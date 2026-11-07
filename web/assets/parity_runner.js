/* parity_runner.js - runs every golden case through the Web core and prints the result for
 * tools/check_python_web_parity.py to read out of the dumped DOM.
 * Present in the repo so the check is reproducible by hand as well.
 *
 * It emits, per case, the same three exported artefacts the MVP produces (JSON document,
 * team review CSV, trial feedback CSV) so the exports are compared, not assumed.
 * saved_at is fixed by the harness so the CSV text can be compared byte for byte. */
(function () {
  "use strict";
  var cases = window.__PARITY_CASES__ || [], out = [];
  for (var i = 0; i < cases.length; i++) {
    var c = cases[i];
    try {
      var inp = NRE.fromDocument(c.document);
      var res = NRE.analyse(inp);
      var payload = NRE.serialise(res, c.document.project_name || null, 2);
      var rec = { id: c.document.project_name || c.id,
                  project_name: c.document.project_name || null,
                  saved_at: c.saved_at || "2026-01-01T00:00:00.000Z",
                  document: c.document, payload: payload,
                  certification_grid: window.RULEPACK.certification_verification.grid };
      out.push({ id: c.id, note: c.note || "",
                 payload: payload,
                 input_snapshot: NRE.inputSnapshot(inp),
                 json_document: Export.jsonDocument(rec),
                 review_csv: Export.csv(rec),
                 feedback_csv: Export.feedbackCsv(rec) });
    } catch (e) {
      out.push({ id: c.id, note: c.note || "", error: String((e && e.message) || e) });
    }
  }
  document.getElementById("out").textContent = "@@PARITY@@" + JSON.stringify({
    engine: NRE.ENGINE_NAME + "/" + NRE.ENGINE_VERSION,
    pack: window.RULEPACK.pack_version, cases: out });
})();
