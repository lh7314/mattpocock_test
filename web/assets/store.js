/* local store + export helpers for the MVP
 *
 * Deliberately browser-local only. There is no server, no user account, no team and no
 * permission model - the task scope excludes all of them. A saved analysis is a complete
 * Input Snapshot plus the full engine payload, so opening it again never recomputes with a
 * newer rule pack and never silently re-decides anything.
 *
 * The three exporters below are byte-for-byte ports of the canonical exporters in
 * prototype/rules_v3.py (export_json_document / export_review_csv /
 * export_trial_feedback_csv). tools/check_python_web_parity.py compares both outputs, so a
 * JSON or CSV file can never say something the Python core did not compute.
 */
(function (global) {
  "use strict";
  var KEY = "gaming-nre.sample-analyses.v1";
  var INDEX = "gaming-nre.recent.v1";

  function readAll() {
    try { return JSON.parse(global.localStorage.getItem(KEY) || "{}"); }
    catch (e) { return {}; }
  }
  function writeAll(m) {
    try { global.localStorage.setItem(KEY, JSON.stringify(m)); return true; }
    catch (e) { global.alert && global.alert("本地存储不可用：" + e.name); return false; }
  }

  var Store = {
    available: function () {
      try { global.localStorage.setItem("__probe", "1"); global.localStorage.removeItem("__probe"); return true; }
      catch (e) { return false; }
    },
    all: function () {
      var m = readAll(), out = [];
      for (var k in m) { out.push(m[k]); }
      out.sort(function (a, b) { return (b.saved_at || "").localeCompare(a.saved_at || ""); });
      return out;
    },
    recent: function (n) { return Store.all().slice(0, n || 8); },
    get: function (id) { return readAll()[id] || null; },
    save: function (rec) {
      var m = readAll();
      rec.saved_at = rec.saved_at || new Date().toISOString();
      m[rec.id] = rec;
      writeAll(m);
      return rec;
    },
    remove: function (id) { var m = readAll(); delete m[id]; writeAll(m); },
    duplicate: function (id, newName) {
      var m = readAll(), src = m[id];
      if (!src) { return null; }
      var copy = JSON.parse(JSON.stringify(src));
      copy.id = "A" + Date.now().toString(36).toUpperCase();
      copy.project_name = newName || ((src.project_name || "未命名项目") + "（副本）");
      copy.saved_at = new Date().toISOString();
      copy.origin_id = src.id;
      copy.draft = true;
      m[copy.id] = copy;
      writeAll(m);
      return copy;
    },
    newId: function () { return "A" + Date.now().toString(36).toUpperCase(); }
  };

  function pad(n) { return n < 10 ? "0" + n : String(n); }
  function stamp() {
    var d = new Date();
    return d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + "-" +
           pad(d.getHours()) + pad(d.getMinutes());
  }

  function download(name, text, mime) {
    var blob = new Blob([text], { type: mime || "application/octet-stream" });
    var url = URL.createObjectURL(blob);
    var a = global.document.createElement("a");
    a.href = url; a.download = name;
    global.document.body.appendChild(a); a.click();
    global.document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(blob); }, 1000);
  }

  /* ---------- display helpers (formatting only, never writes back) ---------- */
  function fmt(v, digits) {
    if (v === null || v === undefined) { return "—"; }
    if (typeof v !== "number") { return String(v); }
    var d = (digits === undefined || digits === null) ? 1 : digits;
    if (Math.abs(v - Math.round(v)) < 1e-9) { return String(Math.round(v)); }
    return String(parseFloat(v.toFixed(d)));
  }
  function fmtRange(min, max, digits) {
    if (min === null || max === null) { return "—"; }
    if (Math.abs(min - max) < 1e-9) { return fmt(min, digits); }
    return fmt(min, digits) + " – " + fmt(max, digits);
  }

  /* ---------- the two formatters the exporters share with the Python core ---------- */
  function jsstr(v) {
    if (v === null || v === undefined) { return ""; }
    if (typeof v === "boolean") { return v ? "true" : "false"; }
    if (typeof v === "number") { return (v % 1 === 0 && isFinite(v)) ? String(Math.round(v)) : String(v); }
    if (typeof v === "string") { return v; }
    return JSON.stringify(v);
  }
  function csvEscape(v) {
    var s = jsstr(v);
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  /* ---------- row status: the eight states a normal user is shown ---------- */
  function rowStatus(x) {
    if (x.base_demand === null || x.base_demand === undefined) { return "暂无法计算"; }
    if (x.value_source === "USER_MANUAL_OVERRIDE") { return "用户输入"; }
    var a = x.main_table_audit || {};
    if (a.verification_status === "MISMATCH") { return "请确认"; }
    if (a.verification_status === "VERIFIED") { return "已验证"; }
    if (x.is_temporary_model) { return "临时采用"; }
    return "已计算";
  }

  function certCells(payload) {
    var out = [];
    (payload.scenarios || []).forEach(function (s) {
      s.results.forEach(function (r) {
        ((r.certification || {}).cells || []).forEach(function (c) {
          out.push({ scenario: s.scope, sku: r.sku_qty, "function": c.function_id,
                     phase: c.phase, adopted_total: c.adopted_total,
                     adopted_value_source: c.adopted_value_source,
                     main_table_per_sku: c.main_table_per_sku_quantity,
                     main_table_derived_total: c.main_table_derived_total,
                     appendix_total: c.appendix_total, delta: c.delta,
                     main_derived_counted_in_project_total: c.main_derived_counted_in_project_total,
                     verification_status: c.verification_status,
                     value_source: c.value_source });
        });
      });
    });
    return out;
  }

  /* ---------- JSON export: adopted value + audit value + difference, ranges stay ranges --- */
  function exportJSONDocument(rec) {
    var p = rec.payload, d = rec.document || {};
    return {
      export_kind: "SAMPLE_REQUIREMENT_ANALYSIS",
      export_version: "4.0",
      analysis_id: rec.id,
      project_name: rec.project_name,
      analysis_engine_version: p.engine_version,
      rule_package_version: p.rule_pack_version,
      schema_version: p.schema_version,
      quantity_model_version: p.quantity_model_version,
      baseline_id: p.baseline_id,
      owner_decision: p.owner_decision,
      input_snapshot: d,
      file_read_value_vs_user_confirmed_value: d.key_factors,
      applied_value: d.key_factors,
      sku_result: (p.scenarios || []).map(function (s) {
        return { scenario: s.scope, state: s.match.state,
                 recommended_sku: s.match.recommended_sku,
                 preferred_sku: s.match.preferred_sku, sku_range: s.match.sku_range,
                 candidates_priced: s.candidates_priced };
      }),
      current_wave: (p.scenarios || []).filter(function (s) { return s.scope === "CURRENT_WAVE"; }),
      full_project: (p.scenarios || []).filter(function (s) { return s.scope === "FULL_PROJECT"; }),
      certification_adopted_and_audit_values: certCells(p),
      certification_cell_audit: rec.certification_grid || null,
      j33_evidence: p.j33_evidence,
      reuse_ledger: (p.scenarios || []).map(function (s) {
        return { scenario: s.scope,
                 ledger: s.results.map(function (r) {
                   return { sku: r.sku_qty, summary: r.reuse_summary,
                            items: r.reuse_ledger.items };
                 }) };
      }),
      review_items: p.owner_review_items,
      panel_annotation_excluded: p.unresolved_comments_excluded,
      policy: p.policy,
      values_full_precision: true,
      range_collapsed_to_single_value_on_export: false,
      payload: p
    };
  }
  function exportJSON(rec) { return JSON.stringify(exportJSONDocument(rec), null, 2); }

  /* ---------- team review report: CSV that opens straight in Excel ---------- */
  function exportReviewCSV(rec) {
    var p = rec.payload, L = [];
    function row() { L.push(Array.prototype.slice.call(arguments).map(csvEscape).join(",")); }
    function blank() { L.push(""); }
    row("样机需求分析 / Sample Requirement Analysis - team review");
    row("Project", rec.project_name || "");
    row("Analysis ID", rec.id);
    row("Engine", p.engine_version);
    row("Rule pack", p.rule_pack_version);
    row("Schema", p.schema_version);
    row("Quantity model", p.quantity_model_version);
    row("Certification adopted", "Appendix total (DEC-10) - counted once");
    row("Certification audit", "Main table per-SKU x SKU - audit only, counted 0 times");
    row("Saved", rec.saved_at);
    row("Rounding", "NONE (D-01) - underlying values keep their decimals");
    blank();
    row("1. SKU result");
    row("Scenario", "State", "Recommended SKU", "Preferred", "Range", "Candidates priced");
    (p.scenarios || []).forEach(function (s) {
      var m = s.match;
      row(s.scope, m.state, m.recommended_sku === null ? "not established" : m.recommended_sku,
          m.preferred_sku, m.sku_range ? m.sku_range[0] + "-" + m.sku_range[1] : "",
          (s.candidates_priced || []).map(jsstr).join(" / "));
    });
    blank();
    row("2. Totals");
    row("Scenario", "SKU", "FVT", "SIT", "Certification", "Non-certification", "Reuse adopted",
        "Risk reserve", "Recommended total", "Single value");
    (p.scenarios || []).forEach(function (s) {
      s.results.forEach(function (r) {
        row(s.scope, r.sku_qty, r.fvt_total, r.sit_total, r.certification_demand,
            r.non_certification_demand, r.confirmed_reuse_adjustment, r.risk_reserve,
            r.recommended_total, r.single_value);
      });
    });
    blank();
    row("3. Function detail");
    row("Scenario", "SKU", "Function", "Phase", "Quantity model", "Adopted", "User status",
        "Main /SKU", "Main derived (audit)", "Delta", "Rule", "Source row");
    (p.scenarios || []).forEach(function (s) {
      s.results.forEach(function (r) {
        (r.rows || []).forEach(function (x) {
          var a = x.main_table_audit || {};
          row(s.scope, r.sku_qty, x.function_name, x.phase, x.quantity_model, x.base_demand,
              rowStatus(x), x.main_table_per_sku_quantity, x.main_table_derived_total,
              a.delta, x.rule_id, x.evidence.row);
        });
      });
    });
    blank();
    row("4. Certification cells - adopted (Appendix) vs audit (Main table)");
    row("Function", "Phase", "SKU", "Adopted (Appendix)", "Main /SKU", "Main derived (audit)",
        "Delta", "Status", "Main row", "Appendix row", "Adopted counted", "Audit counted");
    (p.scenarios || []).forEach(function (s) {
      s.results.forEach(function (r) {
        ((r.certification || {}).cells || []).forEach(function (c) {
          row(c.function_name, c.phase, c.sku_count, c.adopted_total,
              c.main_table_per_sku_quantity, c.main_table_derived_total, c.delta,
              c.verification_status, c.main_table_row, c.appendix_row, 1, 0);
        });
      });
    });
    blank();
    row("5. J33 (explanatory evidence - never added)");
    var j = p.j33_evidence || {};
    row("Role", j.evidence_role);
    row("Disposition", j.disposition);
    row("Added to result", "NO");
    row("Declared reference", JSON.stringify(j.declared_reference_scenario));
    blank();
    row("6. Reuse ledger");
    row("Scenario", "SKU", "Status", "Qty", "Unit", "Applied", "Decision", "Why");
    (p.scenarios || []).forEach(function (s) {
      s.results.forEach(function (r) {
        r.reuse_ledger.items.forEach(function (i) {
          row(s.scope, r.sku_qty, i.reuse_status, i.qty, i.unit, i.applied, i.decision, i.why);
        });
      });
    });
    blank();
    row("7. Review items for the Owner");
    row("Kind", "Blocking level", "Blocks manual MVP", "Function", "Phase", "Why");
    (p.owner_review_items || []).forEach(function (o) {
      row(o.kind, o.blocking_level || "AFFECTS_ACCURACY",
          o.blocks_manual_mvp ? "YES" : "NO", o.function_id || "", o.phase || "", o.why);
    });
    blank();
    row("8. Excluded Panel annotation evidence (DEC-02, never in any calculation)");
    var uc = p.unresolved_comments_excluded || {};
    for (var k in uc) { row("SKU" + k, JSON.stringify(uc[k])); }
    return "\uFEFF" + L.join("\r\n");
  }

  /* ---------- trial feedback form ---------- */
  function exportTrialFeedbackCSV(rec) {
    var p = rec.payload, pack = global.RULEPACK || {}, L = [];
    function row() { L.push(Array.prototype.slice.call(arguments).map(csvEscape).join(",")); }
    function blank() { L.push(""); }
    row("样机需求分析 - 团队试用反馈表 / Trial feedback");
    row("Project", rec.project_name || "");
    row("Analysis ID", rec.id);
    row("Rule pack", p.rule_pack_version);
    row("Engine", p.engine_version);
    row("Reviewer name", "");
    row("Review date", "");
    blank();
    row("1. 请对本次结果逐项回答（同意 / 不同意 / 待确认）+ 说明");
    row("Item", "What the tool produced", "Your answer", "Comment");
    (p.scenarios || []).forEach(function (s) {
      var m = s.match, rng = m.sku_range ? m.sku_range[0] + "-" + m.sku_range[1] : "";
      row("SKU result (" + s.scope + ")",
          m.state + "; recommended=" + jsstr(m.recommended_sku) +
          "; preferred=" + m.preferred_sku + (rng ? "; range=" + rng : ""), "", "");
      s.results.forEach(function (r) {
        row("Totals (" + s.scope + ", " + r.sku_qty + " SKU)",
            "FVT=" + jsstr(r.fvt_total) + "; SIT=" + jsstr(r.sit_total) +
            "; Certification=" + jsstr(r.certification_demand) +
            "; recommended=" + jsstr(r.recommended_total), "", "");
      });
    });
    row("Certification adopted value",
        "Appendix total for that Function, Phase and SKU count (DEC-10); counted once", "", "");
    row("Certification audit value",
        "Main table per-SKU quantity x SKU count, kept for difference analysis; counted 0 times",
        "", "");
    row("J33", "explanatory evidence only - never added", "", "");
    blank();
    row("2. 主表 / 附表仍然不一致的格子（请在真实项目里核对哪一个是业务上正确的数量）");
    row("Function", "Phase", "Adopted (Appendix)", "Main derived (audit)", "Delta",
        "Is the adopted value correct?", "Comment");
    var seen = {};
    (p.scenarios || []).forEach(function (s) {
      s.results.forEach(function (r) {
        (((r.certification || {}).mismatched_cells) || []).forEach(function (c) {
          var k = c.function_id + "|" + c.phase;
          if (seen[k]) { return; }
          seen[k] = 1;
          row(c.function_name, c.phase, c.adopted_total, c.main_table_derived_total, c.delta, "", "");
        });
      });
    });
    blank();
    row("3. 本次分析登记的待确认问题");
    row("Kind", "Blocking level", "Blocks manual MVP", "Your answer", "Comment");
    (p.owner_review_items || []).forEach(function (o) {
      row(o.kind, o.blocking_level || "AFFECTS_ACCURACY", o.blocks_manual_mvp ? "YES" : "NO", "", "");
    });
    blank();
    row("4. 规则包中仍然开放的 Owner 问题（唯一条目，不是影响标签）");
    row("ORI", "Impact tag", "Question", "Your answer", "Comment");
    (pack.open_owner_review_items || []).forEach(function (o) {
      row(o.id, o.blocking_level, o.summary || "", "", "");
    });
    blank();
    row("5. 界面与流程反馈");
    row("Topic", "Your answer", "Comment");
    ["字段是否够用", "结果是否看得懂", "导出文件是否够用", "其它问题"].forEach(function (t) {
      row(t, "", "");
    });
    return "\uFEFF" + L.join("\r\n");
  }

  global.Store = Store;
  global.Export = {
    download: download, fmt: fmt, fmtRange: fmtRange, stamp: stamp,
    jsstr: jsstr, rowStatus: rowStatus,
    jsonDocument: exportJSONDocument,
    json: exportJSON, csv: exportReviewCSV, feedbackCsv: exportTrialFeedbackCSV,
    downloadJSON: function (rec) {
      download("sample-analysis-" + (rec.project_name || rec.id) + "-" + stamp() + ".json",
               exportJSON(rec), "application/json");
    },
    downloadCSV: function (rec) {
      download("sample-review-" + (rec.project_name || rec.id) + "-" + stamp() + ".csv",
               exportReviewCSV(rec), "text/csv;charset=utf-8");
    },
    downloadFeedback: function (rec) {
      download("trial-feedback-" + (rec.project_name || rec.id) + "-" + stamp() + ".csv",
               exportTrialFeedbackCSV(rec), "text/csv;charset=utf-8");
    }
  };
})(window);
