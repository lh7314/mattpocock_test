/* MVP page logic. No business rules live here: every number comes from NRE (the port of
 * prototype/rules_v3.py) and every business number inside NRE comes from rulepack.js.
 * The UI never re-implements SKU matching, Certification, Reuse or Wave behaviour. */
(function () {
  "use strict";
  var P = window.RULEPACK;
  var Q = new URLSearchParams(location.search);
  var CELLS = P.cells, FUNC = {};
  for (var i = 0; i < P.functions.length; i++) { FUNC[P.functions[i].function_id] = P.functions[i]; }
  var CERT_FNS = P.functions.filter(function (f) { return f.category === "CERT"; });

  /* ---------------- shared labels ---------------- */
  var WAVE_LABEL = { "CURRENT_WAVE": "当前波次", "LATER_WAVE": "后续波次",
                     "NO_EXPLICIT_ASSIGNMENT": "未特别指定" };
  var SCOPE_LABEL = { "CURRENT_WAVE": "Current Wave 当前波次",
                      "FULL_PROJECT": "Full Project 全项目" };
  var REUSE_LABEL = { "ALREADY_EMBEDDED_IN_BASELINE": "已含在基准内 (ALREADY_EMBEDDED_IN_BASELINE)",
                      "ADDITIONAL_CONFIRMED_REUSE": "额外且已确认的复用 (ADDITIONAL_CONFIRMED_REUSE)",
                      "POTENTIAL_REUSE": "潜在复用（仅展示） (POTENTIAL_REUSE)",
                      "UNKNOWN_OVERLAP": "重叠情况未知 (UNKNOWN_OVERLAP)" };
  var ORI_LABEL = {
    "SKU_TIE_NOT_RESOLVABLE": ["SKU 档位无法区分", "BLOCKS_FORMALIZATION"],
    "WAVE_ASSIGNMENT_NOT_PROVIDED": ["波次未指定", "AFFECTS_ACCURACY"],
    "WAVE_ASSIGNMENT_UNKNOWN": ["波次标记为未知", "AFFECTS_ACCURACY"],
    "OUT_OF_DOMAIN_INPUT": ["输入超出规则库覆盖范围", "BLOCKS_EXECUTION"],
    "CERTIFICATION_SOURCE_VALIDATION_MISMATCH": ["Certification 附表校验不一致", "BLOCKS_FORMALIZATION"],
    "CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE": ["Certification 逐格验证未全部通过", "BLOCKS_FORMALIZATION"],
    "CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED": ["J33 说明仅适用于特定组合", "ADVISORY"],
    "REUSE_PROOF_MISSING": ["复用缺少证明", "AFFECTS_ACCURACY"],
    "REUSE_OVERLAP_UNPROVEN": ["复用重叠未知", "AFFECTS_ACCURACY"]
  };

  function esc(s) {
    return String(s === null || s === undefined ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function el(id) { return document.getElementById(id); }
  function fmt(v, d) { return Export.fmt(v, d === undefined ? 1 : d); }

  /* 用户可理解状态 - the plain-language column. Internal codes stay in the detail view. */
  function userStatus(r) {
    if (r.base_demand === null) { return ["暂无法计算", "bad"]; }
    if (r.value_source === "USER_MANUAL_OVERRIDE") { return ["用户输入", "info"]; }
    if (r.main_table_audit && r.main_table_audit.verification_status === "MISMATCH") {
      return ["请确认", "warn"]; }
    if (r.owner_review_required) { return ["请确认", "warn"]; }
    if (r.is_temporary_model) { return ["临时采用", "warn"]; }
    if (r.main_table_audit && r.main_table_audit.verification_status === "VERIFIED") {
      return ["已验证", "ok"]; }
    return ["已计算", "ok"];
  }
  function mainReason(r) {
    if (r.quantity_model === "PER_PHASE_FIXED") {
      return "附表按每 Phase 固定量给出，不随 SKU 数量缩放（临时采用，待业务确认）"; }
    if (r.main_table_audit && r.main_table_audit.verification_status === "MISMATCH") {
      return "采用附表值 " + fmt(r.base_demand) + "；主表单 SKU 数量 "
             + fmt(r.main_table_per_sku_quantity) + " × " + r.sku_qty + " 个 SKU = "
             + fmt(r.main_table_audit.derived_total) + "，相差 " + fmt(r.main_table_audit.delta)
             + "（主表值仅用于审计，不计入总量）"; }
    if (r.main_table_audit && r.main_table_audit.verification_status === "VERIFIED") {
      return "采用附表值 " + fmt(r.base_demand) + "，与主表单 SKU 数量 × SKU 数一致"; }
    return "主表单 SKU 数量 " + fmt(r.main_table_per_sku_quantity) + " × " + r.sku_qty + " 个 SKU";
  }

  /* ---------------- SKU / demand summary for one result ---------------- */
  function skuText(m) {
    if (m.state === "RANGE") { return m.sku_range[0] + "–" + m.sku_range[1] + " SKU"; }
    if (m.state === "SINGLE" || m.state === "SINGLE_WITH_RESERVATION") {
      return m.recommended_sku + " SKU"; }
    if (m.state === "OUT_OF_DOMAIN") { return "超出范围"; }
    return "暂无法建议";
  }
  function skuChip(m) {
    if (m.state === "RANGE") { return '<span class="chip range">RANGE 范围</span>'; }
    if (m.state === "SINGLE") { return '<span class="chip ok">单一值</span>'; }
    if (m.state === "SINGLE_WITH_RESERVATION") { return '<span class="chip warn">单一值（有保留）</span>'; }
    if (m.state === "OUT_OF_DOMAIN") { return '<span class="chip bad">超出规则库范围</span>'; }
    return '<span class="chip">信息不足</span>';
  }
  function demandText(res) {
    var v = [];
    for (var i = 0; i < res.length; i++) {
      if (res[i].recommended_total !== null && res[i].recommended_total !== undefined) {
        v.push(res[i].recommended_total); }
    }
    if (!v.length) { return "—"; }
    return Export.fmtRange(Math.min.apply(null, v), Math.max.apply(null, v), 1);
  }

  /* ============================ HOME ============================ */
  function home() {
    var rows = Store.recent(50);
    var box = el("recent");
    if (!rows.length) {
      box.innerHTML = '<p class="muted">还没有分析记录。点击「新建分析」开始。</p>';
    } else {
      var h = "<table><thead><tr><th>Project Name</th><th>分析时间</th><th>SKU 结果</th>" +
              "<th class=r>样机需求</th><th>状态</th><th></th></tr></thead><tbody>";
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i], m = r.summary || {};
        h += "<tr><td><b>" + esc(r.project_name || "未命名项目") + "</b>"
          + (r.draft ? ' <span class="chip">未发布草稿</span>' : "") + "</td>"
          + "<td class=small>" + esc((r.saved_at || "").replace("T", " ").slice(0, 19)) + "</td>"
          + "<td>" + esc(m.sku || "—") + "</td>"
          + "<td class=r>" + esc(m.demand || "—") + "</td>"
          + "<td>" + (m.review ? '<span class="chip warn">' + m.review + " 项待确认</span>"
                               : '<span class="chip ok">无待确认</span>') + "</td>"
          + '<td class=r><button class="small" data-open="' + r.id + '">打开</button> '
          + '<button class="small" data-copy="' + r.id + '">复制</button> '
          + '<button class="small danger" data-del="' + r.id + '">删除</button></td></tr>';
      }
      box.innerHTML = h + "</tbody></table>";
    }
    var all = document.querySelectorAll("[data-open]");
    for (var a = 0; a < all.length; a++) {
      all[a].onclick = function () { location = "result.html?id=" + this.getAttribute("data-open"); };
    }
    var cp = document.querySelectorAll("[data-copy]");
    for (var c = 0; c < cp.length; c++) {
      cp[c].onclick = function () {
        var n = Store.duplicate(this.getAttribute("data-copy"));
        if (n) { location = "new.html?from=" + n.id; }
      };
    }
    var dl = document.querySelectorAll("[data-del]");
    for (var d = 0; d < dl.length; d++) {
      dl[d].onclick = function () {
        if (window.confirm("删除这条本地分析？该操作只影响本机浏览器保存的记录。")) {
          Store.remove(this.getAttribute("data-del")); home();
        }
      };
    }
    el("store-warn").hidden = Store.available();
    el("count").textContent = rows.length ? (rows.length + " 条") : "无";
    // Trial badge: the roster lives in trialkit.js (generated by tools/issue_trial_forms.py).
    // No case data is duplicated here - if the file is absent the card simply says so.
    var tk = document.getElementById("trial-meta");
    if (tk) {
      var seven = (window.TRIALKIT || {}).all_mismatch_cells || [];
      var got = (window.TRIALKIT || {}).cells_covered_by_roster || [];
      tk.textContent = window.TRIALKIT
        ? ((window.TRIALKIT.cases || []).length + " 个案例 · 规则包 "
           + window.TRIALKIT.rule_pack + " · 差异格覆盖 " + got.length + "/" + seven.length)
        : "案例清单未生成：先运行 python tools\issue_trial_forms.py";
    }
  }

  /* ============================ NEW ANALYSIS ============================ */
  var state = { ssd: 1, mem: 1 };

  function specRows(factor, n, existing) {
    var box = el(factor + "-specs"); if (!box) { return; }
    box.innerHTML = "";
    for (var i = 0; i < n; i++) {
      var e = (existing && existing[i]) || {};
      var d = document.createElement("div");
      d.className = "spec-row";
      d.innerHTML =
        '<div><label>Spec Name（可选）</label><input type="text" data-f="' + factor +
        '" data-k="label" value="' + esc(e.label || "") + '" placeholder="spec ' + (i + 1) + '"></div>' +
        '<div><label>Wave Assignment</label><select data-f="' + factor + '" data-k="wave">' +
        opt("NO_EXPLICIT_ASSIGNMENT", e.wave) + opt("CURRENT_WAVE", e.wave) +
        opt("LATER_WAVE", e.wave) + "</select></div>" +
        '<div><label>Wave Source</label><select data-f="' + factor + '" data-k="wave_source">' +
        sopt("NOT_PROVIDED", e.wave_source) + sopt("USER_SELECTED", e.wave_source) +
        sopt("FORMAL_REQUIREMENT_SHEET", e.wave_source) + "</select></div>" +
        '<div></div>';
      box.appendChild(d);
    }
  }
  function opt(v, cur) { return '<option value="' + v + '"' + (v === cur ? " selected" : "") + '>'
    + WAVE_LABEL[v] + "</option>"; }
  function sopt(v, cur) { var l = { "NOT_PROVIDED": "未指定", "USER_SELECTED": "本次手动选择",
    "FORMAL_REQUIREMENT_SHEET": "正式需求表标记" }[v];
    return '<option value="' + v + '"' + (v === cur ? " selected" : "") + ">" + l + "</option>"; }

  function certSummary(skuPreview) {
    var g = P.certification_verification.grid, byFn = {};
    for (var i = 0; i < g.length; i++) {
      var c = g[i];
      if (c.sku_count !== skuPreview) { continue; }
      byFn[c.function_name] = byFn[c.function_name] || { cells: [], ok: true };
      byFn[c.function_name].cells.push(c);
      if (c.verification_status !== "VERIFIED") { byFn[c.function_name].ok = false; }
    }
    return byFn;
  }

  function renderCertPreview(sku) {
    var box = el("cert-preview");
    if (!sku) { box.innerHTML = '<p class="muted small">填写关键配置后显示系统采用值。</p>'; return; }
    var g = P.certification_verification.grid, h = "";
    h += '<div class="note small" style="margin-bottom:10px">'
      + 'Certification 只有一套规则：<b>采用附表中本次 SKU 档位对应的总量</b>（Owner 决定 DEC-10）。'
      + '主表单 SKU 数量与「主表 × SKU 数」继续保留，只用于审计和差异分析，不进入总量。<br>'
      + 'J33 是 RF Certification 的构成说明（'
      + P.j33_investigation.declared_reference_scenario.antenna_source_count
      + ' 天线源 + ' + P.j33_investigation.declared_reference_scenario.wlan_card_count
      + ' WLAN 卡），只用于解释，不叠加。状态：' + P.j33_investigation.disposition + '。</div>';
    h += '<table><thead><tr><th>Function</th><th>Phase</th><th class=r>采用值（附表）</th>'
         + '<th class=r>主表 /SKU</th><th class=r>主表 × ' + sku + '（审计）</th>'
         + '<th class=r>差异</th><th>状态</th><th>本次覆盖（可选）</th></tr></thead><tbody>';
    for (var i = 0; i < g.length; i++) {
      var x = g[i];
      if (x.sku_count !== sku) { continue; }
      var bad = x.verification_status !== "VERIFIED";
      h += "<tr><td>" + esc(x.function_name) + "</td><td>" + x.phase + "</td>"
        + '<td class=r><b>' + fmt(x.appendix_total) + "</b></td>"
        + "<td class=r>" + fmt(x.main_table_per_sku_quantity) + "</td>"
        + "<td class=r>" + fmt(x.derived_total) + "</td>"
        + "<td class=r>" + fmt(x.delta) + "</td>"
        + '<td><span class="chip ' + (bad ? "warn" : "ok") + '">'
        + (bad ? "请确认（与主表不一致）" : "已采用（与主表一致）") + "</span></td>"
        + "<td>"
        + '<input type="number" step="0.1" min="0" style="max-width:110px" '
        + 'data-ovr="' + x.function_id + "|" + x.phase + '" placeholder="'
        + fmt(x.appendix_total) + '"></td></tr>';
    }
    h += "</tbody></table>";
    h += '<p class="hint">此处填写的采用值只对<b>本次分析</b>生效，不会写回规则库，也不会升级成正式规则；'
      + "附表采用值、主表审计值与你填写的值会一起保留在导出文件中。</p>";
    box.innerHTML = h;
  }

  function readForm() {
    var n = function (id) {
      var v = el(id).value;
      return v === "" ? null : parseInt(v, 10);
    };
    var doc = {
      schema_version: "3.0",
      project_name: el("project_name").value || null,
      project_type: el("project_type").value,
      odm: el("odm").value || null,
      phase_scope: Array.prototype.slice.call(document.querySelectorAll("[data-phase]:checked"))
                   .map(function (x) { return x.getAttribute("data-phase"); }),
      key_factors: {
        cpu: { name: "cpu", user_value: n("cpu"), user_edited: el("cpu").value !== "" },
        gpu: { name: "gpu", user_value: n("gpu"), user_edited: el("gpu").value !== "" },
        panel: { name: "panel", user_value: n("panel"), user_edited: el("panel").value !== "" },
        ssd: { name: "ssd", user_value: n("ssd-count"), user_edited: el("ssd-count").value !== "" },
        mem: { name: "mem", user_value: n("mem-count"), user_edited: el("mem-count").value !== "" }
      },
      wave_assignment: { declared_by: "USER_SELECTED", specs: [] },
      certification_input: { mode: "SYSTEM_APPENDIX_ADOPTED", overrides: [] },
      reuse_items: [], additional_demand: [],
      risk_reserve: { percent: el("risk").value === "" ? 0 : Number(el("risk").value) / 100 }
    };
    if (!doc.phase_scope.length) { doc.phase_scope = ["FVT", "SIT"]; }
    ["ssd", "mem"].forEach(function (fac) {
      var rows = document.querySelectorAll('[data-f="' + fac + '"]');
      var byIdx = {};
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i], idx = Math.floor(i / 3) + 1;
        byIdx[idx] = byIdx[idx] || { factor: fac, spec_index: idx };
        var k = r.getAttribute("data-k"), v = r.value;
        if (k === "label") { byIdx[idx].spec_label = v; }
        if (k === "wave") { byIdx[idx].wave = v; }
        if (k === "wave_source") { byIdx[idx].wave_source = v; }
      }
      Object.keys(byIdx).forEach(function (i2) {
        var s = byIdx[i2];
        if (s.wave === "NO_EXPLICIT_ASSIGNMENT") { s.wave_source = "NOT_PROVIDED"; }
        doc.wave_assignment.specs.push(s);
      });
    });
    var ov = document.querySelectorAll("[data-ovr]");
    for (var o = 0; o < ov.length; o++) {
      if (ov[o].value === "") { continue; }
      var parts = ov[o].getAttribute("data-ovr").split("|");
      doc.certification_input.overrides.push({
        function_id: parts[0], phase: parts[1], qty: Number(ov[o].value),
        reason: el("ovr_reason").value || "本次分析按项目实际情况采用" });
    }
    if (doc.certification_input.overrides.length) {
      doc.certification_input.mode = "USER_OVERRIDE_FOR_MISMATCH_CELLS";
    }
    document.querySelectorAll("[data-reuse]").length;
    var rs = el("reuse-rows").querySelectorAll(".reuse-row");
    for (var q = 0; q < rs.length; q++) {
      var row = rs[q], get = function (k) {
        var e = row.querySelector('[data-rk="' + k + '"]'); return e ? e.value : "";
      };
      if (get("qty") === "") { continue; }
      doc.reuse_items.push({
        qty: Number(get("qty")), reuse_status: get("reuse_status"), unit: get("unit"),
        function_id: get("function_id") || null, note: get("note"),
        basis: get("note"), proven_not_in_baseline: get("proven") === "yes" });
    }
    var ad = el("extra-rows").querySelectorAll(".extra-row");
    for (var z = 0; z < ad.length; z++) {
      var r2 = ad[z], g2 = function (k) {
        var e = r2.querySelector('[data-ek="' + k + '"]'); return e ? e.value : "";
      };
      if (g2("qty") === "") { continue; }
      doc.additional_demand.push({ qty: Number(g2("qty")), unit: g2("unit"), label: g2("label") });
    }
    return doc;
  }

  function preview() {
    var doc = readForm();
    var a = NRE.fromDocument(doc); a.normalise();
    var counts = {}; var f = a.factors();
    for (var k in f) { counts[k] = f[k].effective(); }
    var m = NRE.matchSku(counts);
    el("pv-sku").textContent = skuText(m);
    el("pv-chip").innerHTML = skuChip(m);
    el("pv-why").textContent = m.reasons[0] || "";
    var priced = NRE.candidatesToPrice(m);
    renderCertPreview(priced.length ? Math.min.apply(null, priced) : null);
    ["cpu", "gpu", "panel", "ssd-count", "mem-count"].forEach(function (id) {
      el(id).classList.toggle("missing", el(id).value === "");
    });
    el("pv-missing").innerHTML = a.missing().length
      ? '<span class="chip warn">请补充：' + a.missing().join("、") + "</span>" : "";
  }

  function runAnalysis() {
    var doc = readForm();
    var id = Store.newId();
    var inp = NRE.fromDocument(doc); inp.normalise();
    var res = NRE.analyse(inp);
    var payload = NRE.serialise(res, id, 2);
    payload.generated_at_utc = new Date().toISOString();
    payload.certification_grid = P.certification_verification.grid;
    var sc0 = res.scenarios[0];
    var m = sc0 ? sc0.match : { state: "UNDETERMINED", sku_range: null, recommended_sku: null };
    var skuLbl = skuText(m);
    var rec = {
      id: id, document: doc, payload: payload,
      certification_grid: P.certification_verification.grid,
      project_name: doc.project_name || ("未命名 " + new Date().toLocaleDateString()),
      saved_at: new Date().toISOString(), draft: false,
      summary: { sku: skuLbl, demand: demandText(sc0 ? sc0.results : []),
                 review: res.owner_review_items.length }
    };
    Store.save(rec);
    location = "result.html?id=" + id;
  }

  function fillFrom(rec) {
    var d = rec.document || {};
    el("project_name").value = d.project_name || "";
    el("project_type").value = d.project_type || "CLEAN_SHEET";
    el("odm").value = d.odm || "";
    var kf = d.key_factors || {};
    var set = function (id, name) {
      var v = kf[name] && (kf[name].effective !== undefined && kf[name].effective !== null
                           ? kf[name].effective : (kf[name] || {}).user_value);
      el(id).value = (v === null || v === undefined) ? "" : v;
    };
    set("cpu", "cpu"); set("gpu", "gpu"); set("panel", "panel");
    set("ssd-count", "ssd"); set("mem-count", "mem");
    state.ssd = parseInt(el("ssd-count").value || "1", 10);
    state.mem = parseInt(el("mem-count").value || "1", 10);
    specRows("ssd", state.ssd, specsOf(d, "ssd"));
    specRows("mem", state.mem, specsOf(d, "mem"));
    var ov = ((d.certification_input || {}).overrides) || [];
    setTimeout(function () {
      ov.forEach(function (o) {
        var e = document.querySelector('[data-ovr="' + o.function_id + "|" + o.phase + '"]');
        if (e) { e.value = o.qty; }
      });
      preview();
    }, 0);
    el("risk").value = ((d.risk_reserve || {}).percent ? d.risk_reserve.percent * 100 : "");
    return true;
  }
  function specsOf(d, fac) {
    return (((d.wave_assignment || {}).specs) || []).filter(function (s) { return s.factor === fac; })
      .sort(function (a, b) { return a.spec_index - b.spec_index; })
      .map(function (s) { return { label: s.spec_label, wave: s.wave, wave_source: s.wave_source }; });
  }

  function bindNew() {
    var from = Q.get("from");
    if (from) {
      var rec = Store.get(from);
      if (rec) { fillFrom(rec); el("from-note").hidden = false; }
    }
    ["cpu", "gpu", "panel", "ssd-count", "mem-count", "risk"].forEach(function (id) {
      el(id).addEventListener("input", preview);
    });
    el("ssd-count").addEventListener("input", function () {
      state.ssd = parseInt(this.value || "0", 10) || 0;
      specRows("ssd", Math.min(state.ssd, 8)); preview();
    });
    el("mem-count").addEventListener("input", function () {
      state.mem = parseInt(this.value || "0", 10) || 0;
      specRows("mem", Math.min(state.mem, 8)); preview();
    });
    document.addEventListener("change", function (e) {
      if (e.target && (e.target.hasAttribute("data-f") || e.target.hasAttribute("data-ovr")
                       || e.target.hasAttribute("data-phase"))) { preview(); }
    });
    el("add-reuse").onclick = function () { addReuse(); };
    el("add-extra").onclick = function () { addExtra(); };
    el("run").onclick = runAnalysis;
    specRows("ssd", state.ssd); specRows("mem", state.mem);
    addReuse(); addExtra();
    preview();
  }
  function addReuse() {
    var d = document.createElement("div");
    d.className = "spec-row reuse-row";
    d.style.gridTemplateColumns = "1fr 1.6fr .8fr 1.2fr 30px";
    d.innerHTML =
      '<div><label>Quantity</label><input type="number" min="0" step="0.1" data-rk="qty"></div>' +
      '<div><label>Reuse Status</label><select data-rk="reuse_status">'
      + Object.keys(REUSE_LABEL).map(function (k) {
          return '<option value="' + k + '">' + REUSE_LABEL[k] + "</option>"; }).join("")
      + "</select></div>" +
      '<div><label>Unit</label><select data-rk="unit"><option>UNIT</option><option>PCBA</option></select></div>' +
      '<div><label>Evidence Note</label><input type="text" data-rk="note" placeholder="证明 / 依据"></div>' +
      '<div></div>';
    var extra = document.createElement("div");
    extra.className = "row small muted";
    extra.style.marginBottom = "8px";
    extra.innerHTML = '<label style="margin:0">Function（可选）</label>'
      + '<input type="text" data-rk="function_id" style="max-width:180px" placeholder="F_SED">'
      + '<label style="margin:0">已证明不在基准内含共享中</label>'
      + '<select data-rk="proven" style="max-width:110px"><option value="no">否</option>'
      + '<option value="yes">是</option></select>';
    var wrap = document.createElement("div");
    wrap.style.marginBottom = "10px";
    wrap.appendChild(d); wrap.appendChild(extra);
    el("reuse-rows").appendChild(wrap);
  }
  function addExtra() {
    var d = document.createElement("div");
    d.className = "spec-row extra-row";
    d.style.gridTemplateColumns = "1fr .8fr 1.6fr 30px";
    d.innerHTML = '<div><label>Quantity</label><input type="number" min="0" step="0.1" data-ek="qty"></div>'
      + '<div><label>Unit</label><select data-ek="unit"><option>UNIT</option><option>PCBA</option></select></div>'
      + '<div><label>Label</label><input type="text" data-ek="label"></div><div></div>';
    el("extra-rows").appendChild(d);
  }

  /* ============================ RESULT ============================ */
  function resultView(rec) {
    var p = rec.payload;
    el("r-name").textContent = rec.project_name || "未命名项目";
    el("r-meta").innerHTML = '<span class="chip">保存于 '
      + esc((rec.saved_at || "").replace("T", " ").slice(0, 16)) + "</span> "
      + '<span class="chip">ORI-02 ' + esc(P.certification_verification.ori_02_status) + "</span>";
    var sc = p.scenarios, nOpen = (p.owner_review_items || []).length;

    var head = "";
    for (var i = 0; i < sc.length; i++) {
      var s = sc[i], m = s.match;
      head += '<div class="card"><h2>' + SCOPE_LABEL[s.scope]
        + (s.identical_to_full_project ? ' <span class="chip">与 Full Project 相同</span>' : "")
        + "</h2>";
      head += '<div class="row"><div class="kpi"><div class="lab">Recommended SKU</div>'
        + '<div class="big">' + esc(skuText(m)) + "</div>" + skuChip(m) + "</div>";
      head += '<div class="kpi"><div class="lab">Sample Demand 样机需求</div>'
        + '<div class="big">' + esc(demandText(s.results)) + "</div>"
        + '<span class="chip info">FVT / SIT 合计</span></div></div>';
      if (m.state === "RANGE") {
        head += '<div class="note range" style="margin-top:10px"><b>这是一个范围，不是漏填。</b>'
          + m.sku_range[0] + " SKU 与 " + m.sku_range[1] + " SKU 在现有 SKU Definition 下无法区分"
          + "（SKU_NOT_ESTABLISHED）。两档都已完整计算，系统没有、也不会默认替你选一档。"
          + "Certification 的计算规则本身是明确的，这里的范围来自 SKU 档位尚未建立正式分界。</div>";
      }
      if (m.state === "OUT_OF_DOMAIN") {
        head += '<div class="note warn" style="margin-top:10px"><b>本情景已停止计算。</b>'
          + "输入超出规则库覆盖的 SKU Definition 范围，系统不会外推一个数字。请修正输入后重试。</div>";
      }
      if (s.scope === "CURRENT_WAVE" && s.identical_to_full_project) {
        head += '<div class="note" style="margin-top:10px">当前没有明确安排到后续波次的 Spec，'
          + "因此 Current Wave 与 Full Project 使用相同配置范围。</div>";
      }
      if (s.scope === "CURRENT_WAVE" && (s.excluded_specs || []).length) {
        var names = s.excluded_specs.map(function (x) { return x.label; }).join("、");
        head += '<div class="note warn" style="margin-top:10px">已从 Current Wave 排除的 Spec：'
          + "<b>" + esc(names) + "</b>（明确标记为后续波次）。当前波次关键配置："
          + esc(countStr(s.counts)) + "；全项目：" + esc(countStr(fullCounts(sc)))
          + "。差异只来自被排除的 Spec，同一 SKU 档位的 base_demand 不因波次改变。</div>";
      }
      if ((s.unknown_factors || []).length) {
        head += '<div class="note warn" style="margin-top:10px">以下维度的波次被标记为未知：'
          + esc(s.unknown_factors.join("、")) + "，因此当前波次给出多个情景。系统不会替你决定波次。</div>";
      }
      head += renderResultsTable(s) + renderFunctions(s) + renderCert(s) + "</div>";
    }
    el("r-main").innerHTML = head;
    el("r-reopen").onclick = function () { location = "new.html?from=" + rec.id; };
    el("r-json").onclick = function () { Export.downloadJSON(rec); };
    el("r-csv").onclick = function () { Export.downloadCSV(rec); };
    if (el("r-feedback")) {
      el("r-feedback").onclick = function () { Export.downloadFeedback(rec); }; }

    el("r-open-count").textContent = nOpen;
    var byk = {};
    (p.owner_review_items || []).forEach(function (o) {
      byk[o.kind] = (byk[o.kind] || 0) + 1;
    });
    var h2 = "";
    for (var k in byk) {
      var lab = ORI_LABEL[k] || [k, "AFFECTS_ACCURACY"];
      h2 += "<tr><td>" + esc(lab[0]) + '</td><td><span class="chip '
        + (lab[1] === "BLOCKS_EXECUTION" ? "bad" : lab[1] === "BLOCKS_FORMALIZATION" ? "warn" : "")
        + '">' + esc(lab[1]) + "</span></td><td class=r>" + byk[k] + "</td><td class=small muted>"
        + esc(k) + "</td></tr>";
    }
    el("r-open").innerHTML = nOpen
      ? '<table><thead><tr><th>待确认事项</th><th>级别</th><th class=r>条目</th>'
        + "<th>内部标识</th></tr></thead><tbody>" + h2 + "</tbody></table>"
      : '<p class="muted">本次分析没有产生需要确认的问题。</p>';
    el("r-open-full").textContent = JSON.stringify(p.owner_review_items, null, 1);
  }
  function countStr(c) {
    return ["cpu", "gpu", "panel", "ssd", "mem"].map(function (d) {
      return d + "=" + (c[d] === null || c[d] === undefined ? "—" : c[d]); }).join(", ");
  }
  function fullCounts(sc) {
    for (var i = 0; i < sc.length; i++) { if (sc[i].scope === "FULL_PROJECT") { return sc[i].counts; } }
    return {};
  }

  function renderResultsTable(s) {
    if (!s.results.length) { return ""; }
    var h = '<h3>按 SKU 档位的完整计价</h3><table><thead><tr><th>SKU</th><th class=r>FVT</th>'
      + '<th class=r>SIT</th><th class=r>Certification</th><th class=r>非 Certification</th>'
      + '<th class=r>Reuse 采用</th><th class=r>风险预留</th><th class=r>合计</th>'
      + "<th>结果形态</th></tr></thead><tbody>";
    for (var i = 0; i < s.results.length; i++) {
      var r = s.results[i];
      h += "<tr><td><b>" + r.sku_qty + " SKU</b></td>"
        + "<td class=r>" + fmt(r.fvt_total) + "</td><td class=r>" + fmt(r.sit_total) + "</td>"
        + "<td class=r>" + fmt(r.certification_demand) + "</td>"
        + "<td class=r>" + fmt(r.non_certification_demand) + "</td>"
        + "<td class=r>" + fmt(r.confirmed_reuse_adjustment) + "</td>"
        + "<td class=r>" + fmt(r.risk_reserve) + "</td>"
        + "<td class=r><b>" + fmt(r.recommended_total) + "</b></td>"
        + "<td>" + (r.single_value
            ? '<span class="chip ok">单一值</span>'
            : '<span class="chip range">' + fmt(r.recommended_total_band.min) + "–"
              + fmt(r.recommended_total_band.max) + "</span>") + "</td></tr>";
      if (r.pcba_lines_not_summed.length) {
        h += '<tr><td colspan="9" class="small muted">PCBA 行（不计入样机台数）：'
          + esc(JSON.stringify(r.pcba_lines_not_summed)) + "</td></tr>";
      }
    }
    return h + "</tbody></table>";
  }

  function renderFunctions(s) {
    if (!s.results.length) { return ""; }
    var r = s.results[0];
    var h = '<details><summary>Function 明细（' + r.rows.length + ' 行 · 默认取 '
      + r.sku_qty + " SKU 档位）</summary>";
    h += '<table><thead><tr><th>Function</th><th>Phase</th><th>Quantity Model</th>'
      + '<th class=r>建议值</th><th>状态</th><th>主要原因</th></tr></thead><tbody>';
    for (var i = 0; i < r.rows.length; i++) {
      var x = r.rows[i], st = userStatus(x);
      h += "<tr><td>" + esc(x.function_name) + "</td><td>" + x.phase + "</td><td><code>"
        + x.quantity_model + "</code></td><td class=r>" + fmt(x.base_demand)
        + '</td><td><span class="chip ' + st[1] + '">' + st[0] + "</span></td>"
        + '<td class="small">' + esc(mainReason(x)) + "</td></tr>";
    }
    h += "</tbody></table>";
    h += '<details><summary class="small">展开技术详情：源值 / 采用值 / 计算基准 / Source Reference '
      + "/ Verification Status / Reuse 账本</summary>";
    h += '<pre class="mono small" style="max-height:340px;overflow:auto">'
      + esc(JSON.stringify({ rows: r.rows.map(function (x) {
          return { function: x.function_name, phase: x.phase, quantity_model: x.quantity_model,
                   system_computed_value: x.system_computed_value,
                   user_input_value: x.user_input_value, value_source: x.value_source,
                   main_table_derived_total: x.main_table_derived_total,
                   main_table_per_sku_quantity: x.main_table_per_sku_quantity,
                   applied: x.base_demand, unit: x.unit, rule_id: x.rule_id,
                   is_temporary_model: x.is_temporary_model,
                   source_reference: x.evidence, verification: x.main_table_audit,
                   breakdown_evidence_role: x.breakdown_evidence_role }; }),
        reuse_ledger: r.reuse_ledger, reuse_summary: r.reuse_summary }, null, 1))
      + "</pre></details></details>";
    return h;
  }

  function renderCert(s) {
    if (!s.results.length) { return ""; }
    var c = s.results[0].certification;
    if (!c.present) { return ""; }
    var a = c.main_table_audit || {};
    var h = '<h3>Certification</h3>';
    h += '<div class="note small">计算规则：<b>采用附表中本次 SKU 档位（'
      + c.applied_sku_count + '）对应的总量</b>，FVT 与 SIT 各自读自己的附表行，不使用全局比例。'
      + "采用值计入项目总量 <b>" + c.counted_in_project_total_times + "</b> 次；"
      + "主表派生值（主表单 SKU 数量 × SKU 数）计入 <b>"
      + c.main_derived_counted_in_project_total_times
      + "</b> 次，只保留用于审计与差异分析。J33 角色：" + esc(c.j33_role) + "，状态 "
      + esc(c.j33_disposition) + "，未叠加到结果上。"
      + (c.user_override_used ? "<br><b>本次分析包含用户输入的采用值（只影响本次分析）。</b>" : "")
      + "</div>";
    h += '<div class="row" style="margin-top:8px"><span class="chip info">FVT 采用 '
      + fmt(c.fvt_certification_demand) + '</span><span class="chip info">SIT 采用 '
      + fmt(c.sit_certification_demand) + '</span><span class="chip">合计 '
      + fmt(c.certification_demand_total) + "</span>"
      + '<span class="chip ' + (a.mismatch ? "warn" : "ok") + '">主表核对 '
      + a.verified + " 一致 / " + a.mismatch + " 不一致 / " + a.not_evaluable
      + " 无法判定</span></div>";
    h += '<table><thead><tr><th>Function</th><th>Phase</th><th class=r>SKU</th>'
      + '<th class=r>采用值（附表）</th><th>状态</th></tr></thead><tbody>';
    for (var i = 0; i < c.cells.length; i++) {
      var x = c.cells[i];
      h += "<tr><td>" + esc(x.function_name) + "</td><td>" + x.phase + '</td><td class=r>'
        + x.sku_count + '</td><td class=r><b>' + fmt(x.adopted_total) + "</b></td>"
        + '<td><span class="chip '
        + (x.verification_status === "VERIFIED" ? "ok" : "warn") + '">'
        + (x.user_input_total !== null && x.user_input_total !== undefined
            ? "用户输入（本次分析）"
            : (x.verification_status === "VERIFIED" ? "已采用（与主表一致）" : "请确认（与主表不一致）"))
        + "</span></td></tr>";
    }
    h += "</tbody></table>";
    h += '<details><summary>展开：主表口径与差异（审计，不计入总量）</summary><table><thead><tr>'
      + "<th>Function</th><th>Phase</th><th class=r>SKU</th>"
      + '<th class=r>采用值（附表）</th><th class=r>主表 /SKU</th>'
      + "<th class=r>主表 × SKU（审计）</th><th class=r>差值</th><th class=r>用户输入</th>"
      + "<th>来源行</th></tr></thead><tbody>";
    for (var k = 0; k < c.cells.length; k++) {
      var y = c.cells[k];
      h += "<tr><td>" + esc(y.function_name) + "</td><td>" + y.phase + "</td><td class=r>"
        + y.sku_count + '</td><td class=r><b>' + fmt(y.adopted_total) + "</b></td>"
        + "<td class=r>" + fmt(y.main_table_per_sku_quantity) + "</td><td class=r>"
        + fmt(y.main_table_derived_total) + "</td><td class=r>" + fmt(y.delta)
        + "</td><td class=r>" + fmt(y.user_input_total)
        + '</td><td class="small mono">row ' + y.main_table_row + " / " + y.appendix_row
        + "</td></tr>";
    }
    h += "</tbody></table>";
    h += '<p class="hint">主表值与差值只是审计证据：把它们加回到总量里会造成重复计算，'
      + "系统不会这样做。逐格的判断依据与源行号都保留在上面。</p>";
    h += "</details>";
    return h;
  }

  /* ---------------- views exported for web/trial.html ----------------
   * The trial page shows the same numbers with the same wording as the normal result page.
   * It renders through these functions instead of carrying a second copy of the tables -
   * a second copy is a second opinion, and the two would drift. */
  window.AppViews = { skuText: skuText, skuChip: skuChip, demandText: demandText,
                      countStr: countStr, fullCounts: fullCounts, esc: esc,
                      userStatus: userStatus, mainReason: mainReason,
                      renderResultsTable: renderResultsTable,
                      renderFunctions: renderFunctions, renderCert: renderCert };

  /* ---------------- boot ---------------- */
  var page = document.body.getAttribute("data-page");
  if (page === "home") { window.addEventListener("DOMContentLoaded", home); }
  if (page === "new") { window.addEventListener("DOMContentLoaded", bindNew); }
  if (page === "result") {
    window.addEventListener("DOMContentLoaded", function () {
      var rec = Store.get(Q.get("id"));
      if (!rec) {
        el("r-main").innerHTML = '<div class="card"><h2>找不到这条分析</h2>'
          + '<p class="muted">它可能在另一台机器上，或已被删除。<a href="index.html">返回首页</a></p></div>';
        return;
      }
      resultView(rec);
    });
  }
})();
