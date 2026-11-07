/* Trial mode for the S1 controlled team trial (web/trial.html).
 *
 * The case data is not here: it comes from `web/assets/trialkit.js`, which
 * tools/issue_trial_forms.py generates from the same roster that produced the printed forms.
 * The arithmetic is not here either: every number is produced by web/assets/core.js (the port
 * of prototype/rules_v3.py). What this file owns is only the trial *flow*:
 *
 *   pick a case -> run it with locked inputs -> read the result -> answer only the questions
 *   this case actually produced -> export ONE submission JSON.
 *
 * The six pre-submission checks are deliberately written as pure functions so
 * web/ui_test.html can drive them headlessly, and so tools/collect_trial_feedback.py can
 * recompute the same six checks on its own when the file comes back. A submission that says
 * it passed is not believed; the collector re-checks it from the embedded analysis.
 */
(function (global) {
  "use strict";
  var SKEY = "gaming-nre.trial-session.v1";
  var Export = global.Export, Store = global.Store, NRE = global.NRE;
  function kit() { return global.TRIALKIT || null; }
  function pack() { return (global.RULEPACK || {}).pack_version || ""; }
  function el(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s === null || s === undefined ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function today() { return new Date().toISOString().slice(0, 10); }

  /* ---------------- cases ---------------- */
  function cases() { return (kit() || {}).cases || []; }
  function byId(id) {
    var all = cases();
    for (var i = 0; i < all.length; i++) { if (all[i].case === id) { return all[i]; } }
    return null;
  }
  function rosterPack() { return (kit() || {}).rule_pack || ""; }

  /* The exact input the roster issued. Same shape tools/issue_trial_forms.py builds. */
  function documentFor(c) {
    var kf = {};
    for (var n in c.key_factors) {
      kf[n] = { name: n, file_value: c.key_factors[n], user_edited: false };
    }
    var doc = { schema_version: "4.0", project_name: c.project_name,
                project_type: "CLEAN_SHEET", phase_scope: ["FVT", "SIT"],
                key_factors: kf, risk_reserve: { percent: 0 } };
    if (c.wave_assignment) { doc.wave_assignment = c.wave_assignment; }
    return doc;
  }

  /* ---------------- run ---------------- */
  function run(c) {
    var doc = documentFor(c);
    var id = Store.newId();
    var inp = NRE.fromDocument(doc); inp.normalise();
    var res = NRE.analyse(inp);
    var payload = NRE.serialise(res, id, 2);
    payload.generated_at_utc = new Date().toISOString();
    payload.certification_grid = global.RULEPACK.certification_verification.grid;
    var sc0 = res.scenarios[0];
    var m = sc0 ? sc0.match : { state: "UNDETERMINED", sku_range: null, recommended_sku: null };
    var rec = { id: id, document: doc, payload: payload,
                certification_grid: global.RULEPACK.certification_verification.grid,
                project_name: c.project_name, saved_at: new Date().toISOString(), draft: false,
                trial_case: c.case,
                summary: { sku: window.AppViews ? window.AppViews.skuText(m) : m.state,
                           demand: Export.fmtRange(0, 0, 1), review: res.owner_review_items.length } };
    var vals = [];
    (res.scenarios || []).forEach(function (s) {
      (s.results || []).forEach(function (r) {
        if (r.recommended_total !== null && r.recommended_total !== undefined) {
          vals.push(r.recommended_total); }
      });
    });
    rec.summary.demand = vals.length
      ? Export.fmtRange(Math.min.apply(null, vals), Math.max.apply(null, vals), 1) : "—";
    Store.save(rec);
    return rec;
  }

  /* ---------------- what the run actually produced ---------------- */
  function certCells(payload) {
    var out = [], seen = {};
    ((payload || {}).scenarios || []).forEach(function (s) {
      (s.results || []).forEach(function (r) {
        var cert = r.certification || {};
        (cert.cells || []).forEach(function (x) {
          if (x.verification_status !== "MISMATCH") { return; }
          var sku = x.sku_count || r.sku_qty;
          var cell = x.function_name + " / " + x.phase + " @ SKU" + sku;
          if (seen[cell]) { return; }
          seen[cell] = 1;
          out.push({ cell: cell, group: x.function_name + " / " + x.phase, sku: sku,
                     function: x.function_name, phase: x.phase,
                     adopted: x.adopted_total, main_derived: x.main_table_derived_total,
                     delta: x.delta });
        });
      });
    });
    return out.sort(function (a, b) { return a.cell < b.cell ? -1 : 1; });
  }
  function exercisedSkus(payload) {
    var set = {};
    ((payload || {}).scenarios || []).forEach(function (s) {
      (s.candidates_priced || []).forEach(function (n) { set[n] = 1; });
      (s.results || []).forEach(function (r) { set[r.sku_qty] = 1; });
    });
    return Object.keys(set).map(Number).sort(function (a, b) { return a - b; });
  }
  function scenariosOf(payload) {
    return ((payload || {}).scenarios || []).map(function (s) {
      return { scope: s.scope, state: s.match.state,
               recommended_sku: s.match.recommended_sku,
               sku_range: s.match.sku_range ? s.match.sku_range.join("-") : "",
               candidates_priced: s.candidates_priced || [] };
    });
  }
  function registeredOf(payload) {
    var set = {};
    (((payload || {}).owner_review_items) || []).forEach(function (o) { set[o.kind] = 1; });
    return Object.keys(set).sort();
  }

  /* ---------------- session (so a refresh does not lose the draft answers) ---------------- */
  function allSessions() {
    try { return JSON.parse(global.localStorage.getItem(SKEY) || "{}"); }
    catch (e) { return {}; }
  }
  function session(c) { return allSessions()[c.case] || {}; }
  function saveSession(c, patch) {
    var m = allSessions();
    m[c.case] = Object.assign({}, m[c.case], patch);
    try { global.localStorage.setItem(SKEY, JSON.stringify(m)); return true; }
    catch (e) { return false; }
  }

  /* ---------------- a draft saved under the previous form version ----------------
   * Trial Form v4.1 replaced the free-text answer on a mismatch cell with four fixed
   * choices and made the reason mandatory. A draft written by v4.0 holds a sentence
   * where a choice is now expected, plus a reason that explains that sentence and not a
   * choice. Keeping either silently would put words in the reviewer's mouth, so the
   * draft is migrated loudly: the old wording stays on screen for reference, the answer
   * and its reason go back to blank, and the reviewer has to answer again before the
   * export unlocks. No gate is relaxed and no answer is filled in on anyone's behalf.
   */
  function formVersion(c) { return (c || {}).form_version || ""; }
  function migrateDraft(c) {
    var s = session(c);
    var want = formVersion(c);
    if (!Object.keys(s || {}).length || s.form_version === want) { return { stale: [] }; }
    var answers = Object.assign({}, s.answers || {}), legacy = {}, stale = [];
    (c.questions_required || []).forEach(function (q) {
      var opts = q.options || [];
      if (!opts.length) { return; }                 // still a free-text question
      var a = answers[q.id] || {};
      var v = String(a.answer || "").trim();
      if (!v || opts.indexOf(v) >= 0) { return; }   // blank, or a real v4.1 choice
      legacy[q.id] = { answer: a.answer || "", comment: a.comment || "" };
      answers[q.id] = { answer: "", comment: "" };
      stale.push(q.id);
    });
    var patch = { form_version: want, answers: answers, needs_reanswer: stale };
    if (Object.keys(legacy).length) { patch.legacy_v40 = legacy; }
    saveSession(c, patch);
    return { stale: stale, legacy: legacy };
  }

  /* ---------------- the six checks a submission has to pass ----------------
   * These are the task's gates, stated in the order a person hits them. Each one fails
   * loudly and says what to do; none of them is allowed to treat a blank as an agreement. */
  function gates(c, rec, answers, reviewer) {
    var name = String((reviewer || {}).name || "").trim();
    var date = String((reviewer || {}).date || "").trim();
    var payload = rec && rec.payload;
    var g = [];
    g.push({ id: "REVIEWER_NAME", label: "试用者姓名已填写",
             pass: !!name, detail: name ? name : "姓名留空的反馈无法归因，不能当证据" });
    g.push({ id: "REVIEW_DATE", label: "评审日期已填写",
             pass: /^\d{4}-\d{2}-\d{2}$/.test(date),
             detail: date || "请填写 YYYY-MM-DD" });
    var ran = !!(payload && (payload.scenarios || []).length
                 && (payload.scenarios[0].results || []).length);
    g.push({ id: "CASE_RUN", label: "本案例已实际运行",
             pass: ran, detail: ran ? (rec.project_name + " / " + rec.id)
                                    : "还没有算过这个案例：先点「运行分析」" });
    var got = (payload || {}).rule_pack_version || "";
    g.push({ id: "RULE_PACK", label: "规则包版本正确",
             pass: !!got && got === pack() && got === c.rule_pack,
             detail: got + "（当前规则包 " + pack() + "，案例发卷时是 " + c.rule_pack + "）" });
    var required = c.questions_required || [];
    var missing = required.filter(function (q) {
      // answers are {answer, comment} pairs; comparing the pair to "" would make every
      // blank look answered, which is the one mistake this gate exists to prevent.
      var a = (answers || {})[q.id];
      var v = (a && typeof a === "object") ? a.answer : a;
      return !String(v === null || v === undefined ? "" : v).trim();
    });
    g.push({ id: "REQUIRED_ANSWERED",
             label: "本案例的必答问题已全部作答（" + (required.length - missing.length)
                    + "/" + required.length + "）",
             pass: !missing.length,
             detail: missing.length ? "仍未作答：" + missing.map(function (q) {
               return q.cell || q.id; }).join("；") : "" });
    var need = required.filter(function (q) { return q.reason_required; });
    var noWhy = need.filter(function (q) {
      var a = (answers || {})[q.id] || {};
      return !String(a.comment || "").trim();
    });
    g.push({ id: "ANSWER_REASON",
             label: "需要理由的问题都写了理由（" + (need.length - noWhy.length)
                    + "/" + need.length + "）",
             pass: !noWhy.length,
             detail: noWhy.length ? "缺理由：" + noWhy.map(function (q) {
               return q.cell || q.id; }).join("；") : "" });
    var cells = certCells(payload), want = c.covers_cells || [];
    var absent = want.filter(function (cell) {
      return !cells.some(function (x) { return x.cell === cell; });
    });
    var priced = exercisedSkus(payload);
    var needSku = [];
    want.forEach(function (cell) {
      var n = Number(String(cell).split("SKU").pop());
      if (n && priced.indexOf(n) < 0 && needSku.indexOf(n) < 0) { needSku.push(n); }
    });
    g.push({ id: "TARGET_CELLS_EXERCISED",
             label: "案例目标差异格已实际跑到（" + (want.length - absent.length) + "/"
                    + want.length + "）",
             pass: !!ran && !absent.length && !needSku.length,
             detail: absent.length ? "本次没有产出：" + absent.join("；")
                   : (needSku.length ? "本次没有给这些 SKU 数出价：SKU" + needSku.join("、SKU")
                                     : want.join("；")) });
    return g;
  }
  function canSubmit(g) { return (g || []).every(function (x) { return x.pass; }); }

  /* ---------------- the one file the reviewer has to hand back ---------------- */
  function buildSubmission(c, rec, answers, reviewer, comment, checks) {
    var payload = (rec || {}).payload || {};
    var required = (c.questions_required || []).map(function (q) {
      var a = answers[q.id] || {};
      return { id: q.id, kind: q.kind, question: q.question, oris: q.oris || [],
               cell: q.cell || null, group: q.group || null, sku: q.sku || null,
               adopted: q.adopted === undefined ? null : q.adopted,
               main_derived: q.main_derived === undefined ? null : q.main_derived,
               delta: q.delta === undefined ? null : q.delta,
               answer: String(a.answer || "").trim(),
               comment: String(a.comment || "").trim(),
               required: true };
    });
    var optional = (c.questions_optional || []).map(function (q) {
      var a = answers[q.id] || {};
      return { id: q.id, kind: "optional", question: q.question, oris: q.oris || [],
               impact_tag: q.impact_tag || "", answer: String(a.answer || "").trim(),
               comment: String(a.comment || "").trim(), required: false };
    });
    var doc = Export.jsonDocument(rec);
    return {
      export_kind: "SAMPLE_REQUIREMENT_TRIAL_SUBMISSION",
      export_version: "4.0",
      submission_schema: "1.0",
      generated_at_utc: new Date().toISOString(),
      generator: "web/trial.html + web/assets/trial.js",
      rule_package_version: payload.rule_pack_version || "",
      engine_version: payload.engine_version || "",
      case_id: c.case,
      case_profile: c.profile,
      case_goal: c.goal,
      case_source: c.source,
      roster_rule_pack: c.rule_pack,
      project_name: c.project_name,
      analysis_id: (rec || {}).id || "",
      reviewer: { name: String((reviewer || {}).name || "").trim(),
                  date: String((reviewer || {}).date || "").trim() },
      config_locked: c.locked,
        trial_form_version: c.form_version || "",
      analysis_input: documentFor(c),
      analysis: doc,
      exercised_skus: exercisedSkus(payload),
      scenarios: scenariosOf(payload),
      registered_items: registeredOf(payload),
      exercised_mismatch_cells: certCells(payload),
      covered_mismatch_cells: (c.covers_cells || []).map(function (cell) {
        var hit = certCells(payload).filter(function (x) { return x.cell === cell; })[0] || {};
        return { cell: cell, group: hit.group || cell.split(" @ ")[0],
                 sku: hit.sku || Number(String(cell).split("SKU").pop()) || null,
                 adopted: hit.adopted === undefined ? null : hit.adopted,
                 main_derived: hit.main_derived === undefined ? null : hit.main_derived,
                 delta: hit.delta === undefined ? null : hit.delta,
                 exercised: !!hit.cell };
      }),
      feedback: { required: required, optional_oris: optional,
                  comment: String(comment || "").trim() },
      submit_checks: checks || [],
      /* The trial mode never lets anyone edit an input, so an override here would mean the
       * page was bypassed. Recorded, never assumed. */
      certification_override_used: !!((payload.scenarios || [])
        .some(function (s) { return (s.results || [])
          .some(function (r) { return (r.certification || {}).user_override_used; }); }))
    };
  }
  function submissionName(c) {
    return "trial-submission-" + c.project_name + "-" + Export.stamp() + ".json";
  }

  /* ================= the page ================= */
  var cur = null, rec = null;

  function caseTable() {
    var rows = cases(), h = "";
    if (!rows.length) {
      return '<p class="bad">没有读到案例清单（web/assets/trialkit.js 缺失或过期）。'
           + '请先运行 <code>python tools\\issue_trial_forms.py</code>。</p>';
    }
    h = '<table><thead><tr><th>案例</th><th>项目名（自动填写并锁定）</th><th>配置画像</th>'
      + '<th>这个案例要取证什么</th><th>覆盖的差异格</th><th></th></tr></thead><tbody>';
    rows.forEach(function (c) {
      var s = session(c);
      h += "<tr><td><b>" + esc(c.case) + "</b></td><td class=mono small>"
        + esc(c.project_name) + "</td><td class=small>" + esc(c.profile) + "</td>"
        + "<td class=small>" + esc(c.goal) + "</td><td class=small>"
        + c.covers_cells.map(function (x) { return esc(x); }).join("<br>") + "</td>"
        + "<td><button data-case=\"" + esc(c.case) + '">'
        + (s.analysis_id ? "重新载入" : "载入并运行") + "</button>"
        + (s.submitted_at ? '<div class="small muted" style="margin-top:4px">已提交</div>' : "")
        + "</td></tr>";
    });
    return h + "</tbody></table>";
  }

  function showCase(c) {
    cur = c; rec = null; migrateDraft(c);
    el("case-pick").innerHTML = caseTable();
    bindPick();
    el("case-input").hidden = false;
    el("case-run").hidden = false;
    el("result-box").hidden = true;
    el("feedback").hidden = true;
    var kf = Object.keys(c.key_factors).map(function (k) {
      return "<tr><td>" + esc(k) + "</td><td class=r><b>" + esc(c.key_factors[k])
           + "</b></td></tr>"; }).join("");
    var waves = ((c.wave_assignment || {}).specs || []).map(function (s) {
      return "<tr><td>" + esc(s.factor) + " #" + esc(s.spec_index) + "</td><td>"
           + esc(s.spec_label || "") + "</td><td><b>"
           + esc(s.wave === "LATER_WAVE" ? "后续波次" : s.wave) + "</b></td></tr>"; }).join("");
    el("case-input").innerHTML =
      '<div class="row spread"><h2 style="margin:0">案例 ' + esc(c.case) + ' 的输入（锁定）</h2>'
      + '<span class="chip warn">案例配置不可修改</span></div>'
      + '<p class="hint" style="margin-top:6px">' + esc(c.goal) + '</p>'
      + '<div class="grid g2"><div><h3>输入</h3><table><tbody>'
      + '<tr><td>Project Name</td><td class=r><b class=mono>' + esc(c.project_name)
      + '</b></td></tr>' + kf
      + '<tr><td>Risk Reserve</td><td class=r>0%（源表无已确认比例，ORI-07）</td></tr>'
      + '<tr><td>Phase Scope</td><td class=r>FVT + SIT</td></tr>'
      + '</tbody></table>'
       + (waves ? '<h3>Wave Assignment（案例预设）</h3><table><thead><tr><th>Spec</th>'
                + '<th>名称</th><th>波次</th></tr></thead><tbody>' + waves
                + '</tbody></table>'
                // ORI-03: a requirement sheet has no wave column yet, so a preset wave
                // is a test fixture, never a confirmed business fact. Say so where shown.
                + (c.wave_assignment && c.wave_assignment.assumption
                   ? '<p class="small bad">'
                     + esc(c.wave_assignment.assumption_note
                           || "波次为案例预设的试用假设，未经 Owner 确认")
                     + '</p>' : "")
                : "")
      + '</div><div><h3>预期结果（发卷时由 prototype/rules_v3.py 实算）</h3>'
      + '<table><thead><tr><th>场景</th><th>SKU 判定</th><th>范围</th>'
      + '<th class=r>总量</th></tr></thead><tbody>'
      + c.scenarios.map(function (s) {
          var tot = Object.keys(s.totals).map(function (k) {
            return "SKU" + k + "=" + Export.fmt(s.totals[k], 1); }).join("<br>") || "（不出价）";
          return "<tr><td>" + esc(s.scope) + "</td><td>" + esc(s.state) + "</td><td>"
               + esc(s.sku_range || "-") + '</td><td class=r small>' + tot + "</td></tr>";
        }).join("")
      + '</tbody></table><p class="hint">依据：' + esc(c.source) + '</p>'
      + '</div></div>';
    el("run-btn").onclick = function () { doRun(); };
    el("case-run").scrollIntoView ? el("case-run").scrollIntoView({ block: "nearest" }) : 0;
  }

  function doRun() {
    try {
      rec = run(cur);
    } catch (e) {
      el("result-box").hidden = false;
      el("result-box").innerHTML = '<div class="note bad">运行失败：' + esc(e && e.message)
                                 + '</div>';
      return;
    }
    saveSession(cur, { analysis_id: rec.id, ran_at: new Date().toISOString(),
                       rule_pack: rec.payload.rule_pack_version });
    renderResult();
    renderFeedback();
    el("case-pick").innerHTML = caseTable();
    bindPick();
  }

  function renderResult() {
    var V = global.AppViews, p = rec.payload;
    var h = '<div class="row spread"><h2 style="margin:0">分析结果</h2>'
          + '<span class="small muted">Project <b class=mono>' + esc(rec.project_name)
          + '</b> · 规则包 ' + esc(p.rule_pack_version) + ' · <a href="result.html?id='
          + esc(rec.id) + '">打开完整结果页</a></span></div>';
    (p.scenarios || []).forEach(function (s) {
      h += '<h3 style="margin-top:14px">' + (s.scope === "CURRENT_WAVE"
           ? "Current Wave 当前波次" : "Full Project 全项目")
         + (s.identical_to_full_project
             ? ' <span class="chip">与 Full Project 相同</span>' : "") + "</h3>";
      h += '<div class="row"><div class="kpi"><div class="lab">Recommended SKU</div>'
         + '<div class="big">' + esc(V.skuText(s.match)) + "</div>" + V.skuChip(s.match)
         + "</div>";
      h += '<div class="kpi"><div class="lab">Sample Demand 样机需求</div>'
         + '<div class="big">' + esc(V.demandText(s.results)) + "</div>"
         + '<span class="chip info">FVT / SIT 合计</span></div></div>';
      if (s.match.state === "RANGE") {
        h += '<div class="note range small">这是范围，不是漏填：'
           + s.match.sku_range[0] + " 与 " + s.match.sku_range[1]
           + " 档在现有 SKU Definition 下无法区分，两档都已完整计算。</div>";
      }
      h += V.renderResultsTable(s) + V.renderCert(s);
    });
    el("result-box").innerHTML = h;
    el("result-box").hidden = false;
  }

  function qBlock(q) {
    var head = q.kind === "cell"
      ? '<b>' + esc(q.cell) + '</b> <span class="chip warn">附表 '
        + esc(Export.fmt(q.adopted, 1)) + ' · 主表推算 '
        + esc(Export.fmt(q.main_derived, 1)) + ' · 差 ' + esc(Export.fmt(q.delta, 1))
        + "</span>"
      : '<b>' + esc(q.id) + "</b>";
    var oris = (q.oris || []).length
      ? '<div class="small muted">对应 Owner 问题：' + esc(q.oris.join("、")) + "</div>" : "";
    var a = (session(cur).answers || {})[q.id] || {};
    // a v4.0 draft kept free text where v4.1 now asks for one of four choices
    var old = (session(cur).legacy_v40 || {})[q.id] || {};
    var stale = (q.options || []).length && old.answer
      ? '<div class="small bad" style="margin-top:6px">表单已升级到 Trial Form v4.1：'
        + '先前保存的回答「' + esc(old.answer) + '」不是四个选项之一，'
        + '已作废，请重新选择'
        + (old.comment ? '（旧理由：' + esc(old.comment) + '）' : "")
        + '。</div>'
      : "";
    var ctl;
    if ((q.options || []).length) {
      // Trial Form v4.1: four choices replace 同意/不同意, both candidate quantities are
      // spelled out, and the reason is mandatory - a bare 不同意 is not evidence.
      var opts = '<option value="">（请选择）</option>'
               + q.options.map(function (o) {
             return '<option value="' + esc(o) + '"'
                  + (a.answer === o ? " selected" : "") + '>' + esc(o)
                  + (q.option_help && q.option_help[o]
                     ? " - " + esc(q.option_help[o]) : "") + "</option>";
           }).join("");
      ctl = '<div class="row" style="margin-top:6px;align-items:flex-start">'
          + '<select data-q="' + esc(q.id) + '" data-k="answer" '
          + 'style="flex:1;min-width:220px">' + opts + "</select>"
          + '<textarea data-q="' + esc(q.id) + '" data-k="comment" rows="2" '
          + 'style="flex:1;min-width:220px" placeholder="理由（必填）：真实项目、源文件单元格、备注…">'
          + esc(a.comment || "") + "</textarea></div>"
          + '<div class="small muted">两个候选数量：附表 '
          + esc(Export.fmt(q.adopted, 1)) + ' ／ 主表推算 '
          + esc(Export.fmt(q.main_derived, 1)) + (q.reason_required
             ? ' · 选了之后必须写理由' : "") + "</div>";
    }
    else {
      ctl = '<div class="row" style="margin-top:6px;align-items:flex-start">'
          + '<textarea data-q="' + esc(q.id) + '" data-k="answer" rows="2" '
          + 'style="flex:1;min-width:260px" placeholder="你的回答：同意 / 不同意 / 待确认 + 说明">'
          + esc(a.answer || "") + "</textarea>"
          + '<textarea data-q="' + esc(q.id) + '" data-k="comment" rows="2" '
          + 'style="flex:1;min-width:220px" placeholder="Comment（真实项目名、源文件、备注…）">'
          + esc(a.comment || "") + "</textarea></div>";
    }
    return '<div class="q" style="margin:12px 0;padding-bottom:8px;'
         + 'border-bottom:1px dashed var(--line,#ddd)">'
         + head + '<div class="small" style="margin:4px 0">' + esc(q.question) + "</div>"
         + '<div class="small muted">为什么问你这一条：' + esc(q.why || "本案例涉及") + "</div>"
         + oris + ctl + stale + "</div>";
  }

  function renderFeedback() {
    var s = session(cur);
    el("fb-name").value = s.name || el("fb-name").value || "";
    el("fb-date").value = s.date || el("fb-date").value || today();
    var req = (cur.questions_required || []).map(qBlock).join("");
    var opt = (cur.questions_optional || []).map(function (q) {
      var a = (s.answers || {})[q.id] || {};
      return '<div class="q" style="margin:10px 0"><div class="small"><b>' + esc(q.id)
           + '</b> <span class="chip">' + esc(q.impact_tag || "ADVISORY") + "</span> "
           + esc(q.question) + "</div>"
           + '<div class="row" style="margin-top:4px">'
           + '<input type="text" data-q="' + esc(q.id) + '" data-k="answer" '
           + 'style="flex:1" placeholder="可空；回答：同意 / 不同意 / 待确认" value="'
           + esc(a.answer || "") + '">'
           + '<input type="text" data-q="' + esc(q.id) + '" data-k="comment" '
           + 'style="flex:1" placeholder="Comment（可选）" value="'
           + esc(a.comment || "") + '"></div></div>'; }).join("");
    var back = (s.needs_reanswer || []).length
      ? '<div class="note bad">表单版本已升级到 Trial Form v4.1：'
        + s.needs_reanswer.length
        + ' 道题原来保存的自由文本回答不再算作答（原题下方'
        + '保留了旧文字），必须重新从四个选项里选择'
        + '并写明理由，才能导出。</div>'
      : "";
    el("fb-questions").innerHTML = back + req;
    el("fb-optional-list").innerHTML = opt;
    el("fb-comment").value = s.comment || "";
    el("feedback").hidden = false;
    Array.prototype.forEach.call(document.querySelectorAll("[data-q]"), function (e) {
      e.addEventListener("input", refreshChecks);
      e.addEventListener("change", refreshChecks);
    });
    refreshChecks();
  }

  function readAnswers() {
    var out = {};
    Array.prototype.forEach.call(document.querySelectorAll("[data-q]"), function (e) {
      var id = e.getAttribute("data-q"), k = e.getAttribute("data-k");
      out[id] = out[id] || {};
      out[id][k] = e.value;
    });
    return out;
  }
  function reviewer() {
    return { name: (el("fb-name") || {}).value || "", date: (el("fb-date") || {}).value || "" };
  }

  function refreshChecks() {
    if (!cur) { return; }
    var g = gates(cur, rec, readAnswers(), reviewer());
    // what the reviewer can see, published for the automated probe: gate id, pass and
    // the reason shown on screen. Reading it proves the page ran the gate; it is not a
    // second authority - the collector still recomputes everything from the file.
    global.Trial.lastChecks = { case: cur.case, analysis_id: (rec || {}).id || "",
                                gates: g, can_submit: canSubmit(g) };
    el("checks").innerHTML = '<table><tbody>' + g.map(function (x) {
      return '<tr><td style="width:26px">' + (x.pass ? "✅" : "❌") + "</td><td>"
           + esc(x.label) + "</td><td class=\"small muted\">" + esc(x.detail || "")
           + "</td></tr>"; }).join("") + "</tbody></table>";
    var ok = canSubmit(g);
    el("submit-btn").disabled = !ok;
    el("submit-note").innerHTML = ok
      ? '可以提交了：导出 <b class="mono">' + esc(submissionName(cur))
        + '</b>，然后把这一个文件放进 <b class="mono">feedback_inbox\\</b>。'
      : "还有检查没通过，导出按钮保持不可用。空白不算回答，姓名与日期不能省。";
    saveSession(cur, { answers: readAnswers(), name: reviewer().name,
                       date: reviewer().date, comment: el("fb-comment").value });
  }

  function submit() {
    var g = gates(cur, rec, readAnswers(), reviewer());
    if (!canSubmit(g)) { refreshChecks(); return; }
    var sub = buildSubmission(cur, rec, readAnswers(), reviewer(),
                              el("fb-comment").value, g);
    saveSession(cur, { submitted_at: new Date().toISOString(),
                       submission_id: sub.analysis_id });
    Export.download(submissionName(cur), JSON.stringify(sub, null, 2), "application/json");
    el("submit-note").innerHTML = "已导出 <b class=mono>" + esc(submissionName(cur))
      + "</b>。请把它（只有这一个文件）复制到 <b class=mono>feedback_inbox\\</b>，"
      + "然后运行 <code>python tools\\collect_trial_feedback.py</code>。";
    el("case-pick").innerHTML = caseTable();
    bindPick();
  }

  function bindPick() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-case]"), function (b) {
      b.onclick = function () {
        var c = byId(this.getAttribute("data-case"));
        if (c) { showCase(c); }
      };
    });
  }

  function boot() {
    if (!el("case-pick")) { return; }
    el("roster-pack").textContent = rosterPack();
    el("live-pack").textContent = pack();
    var all = cases();
    el("case-count").textContent = all.length + " 个";
    el("cell-count").textContent = ((kit() || {}).cells_covered_by_roster || []).length
                                  + "/" + ((kit() || {}).all_mismatch_cells || []).length;
    var ori = {};
    all.forEach(function (c) {
      (c.oris_required || []).forEach(function (o) { ori[o] = 1; });
    });
    el("ori-count").textContent = Object.keys(ori).length + " / "
                                + ((kit() || {}).ori_total || "?");
    el("case-pick").innerHTML = caseTable();
    bindPick();
    el("fb-name").addEventListener("input", refreshChecks);
    el("fb-date").addEventListener("input", refreshChecks);
    el("fb-comment").addEventListener("input", refreshChecks);
    el("submit-btn").onclick = submit;
    var want = new URLSearchParams(location.search).get("case");
    if (want && byId(want)) { showCase(byId(want)); }
  }

  global.Trial = {
    cases: cases, byId: byId, documentFor: documentFor, run: run,
    certCells: certCells, exercisedSkus: exercisedSkus, scenariosOf: scenariosOf,
    registeredOf: registeredOf, gates: gates, canSubmit: canSubmit,
    buildSubmission: buildSubmission, submissionName: submissionName,
    session: session, saveSession: saveSession, rosterPack: rosterPack, pack: pack,
    migrateDraft: migrateDraft, formVersion: formVersion, readAnswers: readAnswers,
    sessionKey: SKEY
  };
  if (document.body && document.body.getAttribute("data-page") === "trial") {
    global.addEventListener("DOMContentLoaded", boot);
  }
})(window);