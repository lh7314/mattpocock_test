#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_python_web_parity - proves the Web MVP core behaves exactly like the Python core.

The Python core (prototype/rules_v3.py) is the behaviour reference. The Web MVP runs a
JavaScript port (web/assets/core.js) because the MVP has to work offline from a double-
clicked file, with no server. This tool runs both over the same cases and compares the
COMPLETE structured output, not a handful of headline numbers:

  SKU state / recommended_sku / preferred_sku / SKU range / priced candidates
  Current Wave and Full Project counts and wave basis
  every Function line, its Quantity Model and its adopted value
  Certification: adopted (Appendix) value, retained Main Table value, derived audit value,
                 delta, verification status, counted-times, J33 role
  Reuse ledger, Review Items, every null field, every underlying decimal
  plus the three exported artefacts: JSON document, team review CSV, trial feedback CSV

Floats are compared with a 1e-9 tolerance (D-01); strings, enums, nulls and the CSV text
must match exactly. Any difference is a delivery blocker and exits non-zero.

The browser is driven headless with no network access (--host-resolver-rules MAP * ~NOTFOUND)
so the check cannot reach the internet even accidentally.
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:\GAMING_NRE_AGENT")
sys.path.insert(0, str(ROOT / "prototype"))
import rules_v3 as R                                              # noqa: E402

TOL = 1e-9
OUT = ROOT / "artifacts" / "validation"
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]
# exports must be byte-identical, so the record carries a fixed timestamp on both sides
FIXED_SAVED_AT = "2026-01-01T00:00:00.000Z"


def doc(cpu=None, gpu=None, panel=None, ssd=None, mem=None, waves=None, cert=None,
        reuse=None, extra=None, risk=None, phase=None, name=None):
    kf = {n: {"name": n, "file_value": v, "user_edited": False}
          for n, v in dict(cpu=cpu, gpu=gpu, panel=panel, ssd=ssd, mem=mem).items()}
    d = {"schema_version": "4.0", "project_name": name, "project_type": "CLEAN_SHEET",
         "phase_scope": phase or ["FVT", "SIT"], "key_factors": kf,
         "risk_reserve": {"percent": risk if risk is not None else 0}}
    if waves:
        d["wave_assignment"] = {"declared_by": "USER_SELECTED", "specs": waves}
    if cert:
        d["certification_input"] = {"mode": "USER_OVERRIDE_FOR_MISMATCH_CELLS",
                                    "override_scope": "THIS_ANALYSIS_ONLY",
                                    "overrides": cert}
    if reuse:
        d["reuse_items"] = reuse
    if extra:
        d["additional_demand"] = extra
    return d


W_LATER_SSD = [{"factor": "ssd", "spec_index": 2, "wave": "LATER_WAVE",
                "wave_source": "USER_SELECTED"},
               {"factor": "mem", "spec_index": 2, "wave": "LATER_WAVE",
                "wave_source": "USER_SELECTED"}]
W_UNK_SSD = [{"factor": "ssd", "spec_index": 2, "wave": "UNKNOWN",
              "wave_source": "USER_SELECTED"}]
W_NONE_SSD = [{"factor": "ssd", "spec_index": 2, "wave": "NO_EXPLICIT_ASSIGNMENT",
               "wave_source": "USER_SELECTED"}]
OVR_RF = lambda qty: [{"function_id": "F_RF_CERTIFICATION", "phase": "SIT", "qty": qty,
                       "reason": "project-specific RF scope"}]
OVR_SAFE = [{"function_id": "F_SAFETY", "phase": "FVT", "qty": 8.5,
             "reason": "battery spec reduced for this project"}]

# Every Certification cell where the Main Table derivation and the adopted Appendix total
# differ is exercised by at least one case below (task section 5 requirement 1):
#   Green/SIT@3        -> W-08, W-26          Safety/FVT@6       -> W-09, W-27
#   RF/SIT@2           -> W-01, W-08, W-37    RF/SIT@3           -> W-08, W-26
#   RF/SIT@4 and @5    -> W-02, W-28          RF/SIT@6           -> W-09, W-27
CASES = [
    ("W-01", "2 SKU single answer; RF/SIT mismatch at SKU2", doc(1, 1, 1, 1, 1, name="W01")),
    ("W-02", "4-5 SKU tie -> RANGE, both priced (RF/SIT@4 and @5)",
     doc(3, 3, 1, 1, 2, name="W02")),
    ("W-03", "missing key factor (panel unanswered)",
     {"schema_version": "4.0", "project_name": "W03",
      "key_factors": {"cpu": {"name": "cpu", "file_value": 3},
                      "gpu": {"name": "gpu", "file_value": 3},
                      "panel": {"name": "panel", "file_value": None},
                      "ssd": {"name": "ssd", "file_value": 2},
                      "mem": {"name": "mem", "file_value": 2}},
      "risk_reserve": {"percent": 0}}),
    ("W-04", "no wave declared anywhere", doc(2, 2, 1, 2, 2, name="W04")),
    ("W-05", "explicit LATER_WAVE specs excluded from the current wave",
     doc(2, 2, 1, 2, 2, waves=W_LATER_SSD, name="W05")),
    ("W-06", "current wave identical to full project", doc(1, 1, 1, 1, 1, name="W06")),
    ("W-07", "current wave differs from full project",
     doc(3, 3, 1, 1, 2, waves=W_LATER_SSD, name="W07")),
    ("W-08", "3 SKU single answer: Green/SIT and RF/SIT mismatches at 3 SKU",
     doc(2, 2, 1, 1, 1, name="W08")),
    ("W-09", "6 SKU: Safety/FVT 9.6 vs adopted 10, RF/SIT 15 vs adopted 10",
     doc(1, 1, 3, 2, 3, name="W09")),
    ("W-10", "certification range comes only from the SKU range",
     doc(3, 3, 1, 1, 2, name="W10")),
    ("W-11", "override equal to the adopted Appendix value",
     doc(2, 2, 1, 1, 1, cert=OVR_RF(9.0), name="W11")),
    ("W-12", "J33 never added on top of the adopted value", doc(3, 2, 2, 2, 2, name="W12")),
    ("W-13", "MEPA / HW PA read as fixed per-phase amounts at 2 SKU",
     doc(1, 2, 1, 1, 1, name="W13")),
    ("W-14", "reuse deduction is allowed",
     doc(3, 2, 2, 2, 2, reuse=[{"qty": 5.0, "unit": "UNIT",
                                "reuse_status": "ADDITIONAL_CONFIRMED_REUSE",
                                "function_id": "F_SED", "proven_not_in_baseline": True,
                                "basis": "spare pool #12"}], name="W14")),
    ("W-15", "reuse without proof is not deducted",
     doc(3, 2, 2, 2, 2, reuse=[{"qty": 5.0, "unit": "UNIT",
                                "reuse_status": "ADDITIONAL_CONFIRMED_REUSE",
                                "function_id": "F_SED"}], name="W15")),
    ("W-16", "single_value=false has no priced result at all (undetermined input)",
     {"schema_version": "4.0", "project_name": "W16",
      "key_factors": {n: {"name": n, "file_value": None} for n in
                      ("cpu", "gpu", "panel", "ssd", "mem")}}),
    ("W-17", "out-of-domain input stops that scenario only",
     doc(9, 3, 2, 2, 2, name="W17")),
    ("W-18", "risk reserve charged on baseline demand", doc(3, 2, 2, 2, 2, risk=0.05, name="W18")),
    ("W-19", "PCBA extra demand is never summed with units",
     doc(3, 2, 2, 2, 2, extra=[{"qty": 12.0, "unit": "PCBA", "label": "PCBA set"},
                               {"qty": 3.0, "unit": "UNIT"}], name="W19")),
    ("W-20", "FVT only phase scope", doc(3, 2, 2, 2, 2, phase=["FVT"], name="W20")),
    ("W-21", "explicitly UNKNOWN wave fans the current wave out",
     doc(2, 2, 1, 2, 2, waves=W_UNK_SSD, name="W21")),
    ("W-22", "NO_EXPLICIT_ASSIGNMENT (UI: 未特别指定) is not UNKNOWN",
     doc(2, 2, 1, 2, 2, waves=W_NONE_SSD, name="W22")),
    ("W-23", "override plus reuse plus risk together",
     doc(3, 3, 1, 1, 2, cert=OVR_SAFE,
         reuse=[{"qty": 2.0, "unit": "UNIT", "reuse_status": "ADDITIONAL_CONFIRMED_REUSE",
                 "function_id": "F_SED", "proven_not_in_baseline": True}],
         risk=0.05, name="W23")),
    ("W-24", "mixed reuse states in one ledger",
     doc(3, 2, 2, 2, 2, reuse=[{"qty": 5.0}, {"qty": 3.0, "reuse_status": "POTENTIAL_REUSE"},
                               {"qty": 2.0, "reuse_status": "ALREADY_EMBEDDED_IN_BASELINE",
                                "function_id": "F_THM"},
                               {"qty": 4.0, "reuse_status": "ADDITIONAL_CONFIRMED_REUSE",
                                "function_id": "F_SED", "proven_not_in_baseline": True}],
         name="W24")),
    ("W-25", "4 SKU single answer: the Appendix total is counted exactly once",
     doc(2, 2, 2, 2, 2, name="W25")),
    ("W-26", "3 SKU: Green/SIT adopts 6.0 while the Main Table 9.0 stays as audit",
     doc(2, 2, 1, 1, 1, phase=["SIT"], name="W26")),
    ("W-27", "6 SKU: Safety/FVT adopts 10.0; the 9.6 audit value keeps its decimal",
     doc(1, 1, 3, 2, 3, phase=["FVT"], name="W27")),
    ("W-28", "4-5 RANGE prices Certification separately for both candidates",
     doc(3, 3, 3, 1, 2, name="W28")),
    ("W-29", "override on a cell whose Main Table already agrees with the Appendix",
     doc(2, 2, 1, 1, 1, cert=[{"function_id": "F_EMC", "phase": "SIT", "qty": 3.0,
                               "reason": "only two EMC machines are free this build"}],
         name="W29")),
    ("W-30", "override that does not match the adopted value is flagged, not hidden",
     doc(2, 2, 1, 1, 1, cert=OVR_RF(12.5), name="W30")),
    ("W-31", "override never escapes into the rule pack: snapshot keeps THIS_ANALYSIS_ONLY",
     doc(2, 2, 1, 1, 1, cert=OVR_RF(7.0), risk=0.05, name="W31")),
    ("W-32", "underlying decimals survive risk and export (D-01)",
     doc(2, 2, 1, 1, 1, risk=0.065, name="W32")),
    ("W-33", "Current Wave versus Full Project with a real later wave and a SKU range",
     doc(3, 3, 1, 1, 2, waves=W_LATER_SSD, risk=0.05, name="W33")),
    ("W-34", "2 SKU: J33 evidence plus MEPA / HW PA fixed amounts together",
     doc(1, 1, 1, 1, 1, phase=["SIT"], name="W34")),
    ("W-35", "integration: reuse + PCBA + extra demand + risk in one analysis",
     doc(2, 2, 2, 2, 2,
         reuse=[{"qty": 3.0, "unit": "UNIT", "reuse_status": "ADDITIONAL_CONFIRMED_REUSE",
                 "function_id": "F_SED", "proven_not_in_baseline": True},
                {"qty": 2.0, "reuse_status": "UNKNOWN_OVERLAP", "function_id": "F_THM"}],
         extra=[{"qty": 4.0, "unit": "UNIT", "label": "extra pilot units"},
                {"qty": 6.0, "unit": "PCBA", "label": "PCBA set"}],
         risk=0.05, name="W35")),
    ("W-36", "SIT only phase scope (FVT excluded, no global phase ratio)",
     doc(3, 3, 1, 1, 2, phase=["SIT"], name="W36")),
    ("W-37", "2 SKU: RF/SIT override to exactly the adopted value plus a risk reserve",
     doc(1, 1, 1, 1, 1, cert=OVR_RF(8.0), risk=0.05, name="W37")),
    ("W-38", "UNKNOWN wave at 3 SKU with Certification mismatches",
     doc(2, 2, 1, 1, 1, waves=[{"factor": "ssd", "spec_index": 1, "wave": "UNKNOWN",
                                "wave_source": "USER_SELECTED"}], name="W38")),
    ("W-39", "6 SKU with a reuse deduction and a risk reserve (decimal chain)",
     doc(1, 1, 3, 2, 3, reuse=[{"qty": 1.5, "unit": "UNIT",
                                "reuse_status": "ADDITIONAL_CONFIRMED_REUSE",
                                "function_id": "F_SED", "proven_not_in_baseline": True}],
         risk=0.075, name="W39")),
    ("W-40", "out-of-domain in the current wave only, full project still priced",
     doc(9, 3, 2, 2, 2, waves=W_LATER_SSD, name="W40")),
]

# Volatile / by-design-different fields: timestamps, ids, and the engine name, which is
# genuinely "rules_v3" on one side and "rules_v3_web" on the other. The version number and
# every business value are still compared exactly.
VOLATILE = {"generated_at_utc", "engine_version", "saved_at", "analysis_id",
            "exported_at_local", "analysis_engine_version"}


def python_record(d: dict) -> dict:
    """The same record object the MVP stores: snapshot + payload + audit grid."""
    res = R.analyse(R.AnalysisInput.from_document(d))
    payload = R.serialise(res, analysis_id=d.get("project_name"), display_precision=2)
    # round-trip through JSON so the Python and Web documents are the same shape:
    # JSON object keys are always strings, and both sides must be compared as they are
    # actually stored and exported (D-01 - this changes no value, only the key type).
    payload = json.loads(json.dumps(payload))
    return {"id": d.get("project_name"), "project_name": d.get("project_name"),
            "saved_at": FIXED_SAVED_AT, "document": json.loads(json.dumps(d)),
            "payload": payload, "_input": res["input"],
            "certification_grid": json.loads(json.dumps(
                json.loads((ROOT / "artifacts/model/certification_verification.json")
                           .read_text(encoding="utf-8"))["verification_grid"]))}


def python_outputs(d: dict) -> dict:
    rec = python_record(d)
    snapshot = json.loads(json.dumps(R.input_document(rec["_input"])))
    doc = R.export_json_document(rec)
    return {"payload": rec["payload"],
            "input_snapshot": snapshot,
            "json_document": json.loads(json.dumps(doc)),
            "review_csv": R.export_review_csv(rec),
            "feedback_csv": R.export_trial_feedback_csv(rec)}


# --------------------------------------------------------------------------- #
# browser
# --------------------------------------------------------------------------- #
def find_browser():
    for b in BROWSERS:
        if Path(b).exists():
            return b
    return None


def run_browser(browser: str, html_path: Path, timeout: int = 300,
                marker: str = "@@PARITY@@", virtual_ms: int = 30000) -> dict:
    """Drive Edge/Chrome headless with no network access and read the dumped DOM.

    Windows notes (all three were real failures, not theoretical):
      * the browser profile must live on an ASCII path - the user profile path here
        contains non-ASCII characters and Edge silently produces nothing;
      * Start-Process is used because launching the exe directly with a redirected
        handle makes Edge discard --dump-dom output;
      * --host-resolver-rules contains spaces, so it needs embedded quotes or Edge
        receives three broken arguments and exits without printing.
    """
    prof = ROOT.parent / "_tmp_edge_profile"       # ASCII path, outside the repository
    prof.mkdir(parents=True, exist_ok=True)
    dom = html_path.with_suffix(".dom.txt")
    args = ["--headless=new", "--disable-gpu", "--no-sandbox",
            f"--user-data-dir={prof}",
            '--host-resolver-rules="MAP * ~NOTFOUND"',      # no DNS at all
            "--allow-file-access-from-files",
            "--disable-background-networking", "--disable-sync",
            "--disable-extensions", "--no-first-run",
            "--virtual-time-budget=%d" % virtual_ms, "--dump-dom", html_path.as_uri()]
    quoted = ",".join("'" + a.replace("'", "''") + "'" for a in args)
    ps = ("$o='{out}';$p=Start-Process -FilePath '{exe}' -ArgumentList {args} -Wait "
          "-NoNewWindow -RedirectStandardOutput $o").format(
              out=str(dom).replace("'", "''"), exe=browser.replace("'", "''"), args=quoted)
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True,
                   text=True, timeout=timeout, encoding="utf-8", errors="replace")
    txt = dom.read_text(encoding="utf-8", errors="replace") if dom.exists() else ""
    dom.unlink(missing_ok=True)
    i = txt.find(marker)
    if i < 0:
        raise RuntimeError(f"no {marker} block in the dumped DOM (length "
                           f"{len(txt)}) - the page did not run. First 400 chars: "
                           + txt[:400].replace("\n", " "))
    j = txt.find("</pre>", i)
    raw = txt[i + len(marker):j if j > 0 else len(txt)]
    return json.loads(raw.strip())


def diff(a, b, path="$", out=None):
    """Structured comparison. Numbers within 1e-9, everything else exactly."""
    if out is None:
        out = []
    if len(out) > 60:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k in VOLATILE:
                continue
            if k not in a:
                out.append({"path": f"{path}.{k}", "kind": "extra_in_web", "web": b[k]})
            elif k not in b:
                out.append({"path": f"{path}.{k}", "kind": "missing_in_web", "python": a[k]})
            else:
                diff(a[k], b[k], f"{path}.{k}", out)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append({"path": path + ".length", "kind": "length",
                        "python": len(a), "web": len(b)})
            return out
        for i in range(len(a)):
            diff(a[i], b[i], f"{path}[{i}]", out)
        return out
    if isinstance(a, bool) or isinstance(b, bool):
        if a != b:
            out.append({"path": path, "kind": "bool", "python": a, "web": b})
        return out
    if isinstance(a, (int, float)) and a is not None and isinstance(b, (int, float)) and b is not None:
        if not (abs(float(a) - float(b)) <= TOL):
            out.append({"path": path, "kind": "number", "python": a, "web": b})
        return out
    if a is None or b is None:
        if a is not None or b is not None:
            out.append({"path": path, "kind": "null", "python": a, "web": b})
        return out
    if a != b:
        out.append({"path": path, "kind": "value", "python": a, "web": b})
    return out


HTML = """<!doctype html><html><head><meta charset="utf-8"><title>parity</title></head>
<body><pre id="out">pending</pre>
<script src="../../web/assets/rulepack.js"></script>
<script src="../../web/assets/core.js"></script>
<script src="../../web/assets/store.js"></script>
<script>window.__PARITY_CASES__ = {cases};</script>
<script src="../../web/assets/parity_runner.js"></script>
</body></html>
"""


def main() -> int:
    browser = find_browser()
    rows, failures = [], []
    py = {cid: python_outputs(d) for cid, note, d in CASES}

    if not browser:
        print("[skip] no Chromium-family browser found - Web parity not executed")
        return 0

    tmp = ROOT / "artifacts" / "validation" / "_parity_run.html"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    cases_js = json.dumps([{"id": c, "note": n, "document": d, "saved_at": FIXED_SAVED_AT}
                           for c, n, d in CASES], ensure_ascii=False)
    tmp.write_text(HTML.format(cases=cases_js), encoding="utf-8")

    web = run_browser(browser, tmp)
    tmp.unlink(missing_ok=True)

    by_id = {c["id"]: c for c in web["cases"]}
    for cid, note, d in CASES:
        w = by_id.get(cid)
        if not w:
            failures.append({"id": cid, "diff": [{"path": "$", "kind": "no_case"}]})
            rows.append({"id": cid, "note": note, "result": "MISSING"})
            continue
        if w.get("error"):
            failures.append({"id": cid, "diff": [{"path": "$", "kind": "js_error",
                                                  "web": w["error"]}]})
            rows.append({"id": cid, "note": note, "result": "JS ERROR"})
            continue
        d_ = diff(py[cid]["payload"], w["payload"])
        d_ += diff(py[cid]["input_snapshot"], w.get("input_snapshot"))
        d_ += diff(py[cid]["json_document"], w.get("json_document"))
        for kind in ("review_csv", "feedback_csv"):
            # the exported header quotes the engine name, which is legitimately different
            # between the two cores (rules_v3 / rules_v3_web). Every other byte must match.
            a = re.sub(r"^Engine,[^\r\n]*", "Engine,<core>", py[cid][kind], flags=re.M)
            b = re.sub(r"^Engine,[^\r\n]*", "Engine,<core>", w.get(kind) or "", flags=re.M)
            if a != b:
                lines_a, lines_b = a.split("\r\n"), b.split("\r\n")
                pyline = next((i for i, (x, y) in enumerate(zip(lines_a, lines_b)) if x != y),
                              len(lines_a) - 1 if len(lines_a) != len(lines_b) else -1)
                d_.append({"path": f"$.{kind}[line {pyline}]", "kind": "export_text",
                           "python": lines_a[pyline] if 0 <= pyline < len(lines_a)
                           else "<length differs>",
                           "web": lines_b[pyline] if 0 <= pyline < len(lines_b)
                           else "<length differs>"})
        rows.append({"id": cid, "note": note,
                     "result": "MATCH" if not d_ else f"DIFF ({len(d_)})",
                     "fields": len(json.dumps(py[cid]["payload"]))})
        if d_:
            failures.append({"id": cid, "diff": d_[:12]})

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python_core": "prototype/rules_v3.py",
        "web_core": "web/assets/core.js",
        "python_engine": f"{R.ENGINE_NAME}/{R.ENGINE_VERSION}",
        "web_engine": web["engine"],
        "rule_pack": web["pack"],
        "browser": browser,
        "network": "disabled (--host-resolver-rules=MAP * ~NOTFOUND)",
        "tolerance": TOL,
        "cases": len(CASES),
        "matching": sum(1 for r in rows if r["result"] == "MATCH"),
        "divergent": [f["id"] for f in failures],
        "exports_compared": ["json_document", "review_csv", "feedback_csv"],
        "certification_mismatch_cells_covered": {
            "Green/SIT@3": ["W-08", "W-26"], "Safety/FVT@6": ["W-09", "W-27"],
            "RF/SIT@2": ["W-01", "W-08", "W-11", "W-30", "W-31", "W-37", "W-38"],
            "RF/SIT@3": ["W-08", "W-11", "W-26", "W-30", "W-31", "W-38"],
            "RF/SIT@4": ["W-02", "W-10", "W-28", "W-33", "W-36"],
            "RF/SIT@5": ["W-02", "W-10", "W-28", "W-33", "W-36"],
            "RF/SIT@6": ["W-09", "W-27"]},
        "status": "MATCH" if not failures else "DIVERGENT",
        "note": "the whole structured payload is compared, including nulls, enums, the "
                "adopted Certification value, the retained Main Table audit value, the reuse "
                "ledger and the review items, plus the JSON and both CSV exports",
    }
    (OUT / "python_web_parity.json").write_text(
        json.dumps({"summary": summary, "rows": rows,
                    "failures": failures}, ensure_ascii=False, indent=1), encoding="utf-8")

    L = ["# Python vs Web consistency report", "",
         f"- Python core: `{summary['python_core']}` ({summary['python_engine']})",
         f"- Web core: `{summary['web_core']}` ({summary['web_engine']})",
         f"- rule pack: `{summary['rule_pack']}` (single source for both)",
         f"- browser: `{os.path.basename(browser)}` headless, {summary['network']}",
         f"- numeric tolerance: `{TOL:g}` (D-01). Enums, strings, nulls and the exported CSV "
         f"text must match exactly.",
         f"- exported artefacts compared per case: `json_document`, `review_csv`, "
         f"`feedback_csv`",
         f"- result: **{summary['status']}** - {summary['matching']}/{summary['cases']} cases "
         f"match on the complete structured payload", "",
         "| case | scenario under test | result |", "|---|---|---|"]
    L += [f"| {r['id']} | {r['note']} | {r['result']} |" for r in rows]
    L += ["", "## Certification mismatch coverage", "",
          "Every cell where the retained Main Table derivation disagrees with the adopted "
          "Appendix total is exercised by the cases below (each case also compares the "
          "exports).", "",
          "| mismatch cell | cases |", "|---|---|"]
    for k, v in summary["certification_mismatch_cells_covered"].items():
        L.append(f"| {k} | {', '.join(v)} |")
    if failures:
        L += ["", "## Divergences", ""]
        for f in failures:
            L.append(f"- **{f['id']}**")
            L += [f"  - `{d['path']}` {d['kind']}: python=`{d.get('python')}` "
                  f"web=`{d.get('web')}`" for d in f["diff"]]
    L += ["", "## What is compared", "",
          "Every field of the serialised output: SKU state, recommended_sku, preferred_sku, "
          "SKU range, priced candidates, Current Wave and Full Project counts and wave basis, "
          "every Function line and its Quantity Model, the adopted Certification value "
          "(Appendix), the retained Main Table value, the derived audit value, the delta, the "
          "verification status, the counted-times flags, the J33 role, the reuse ledger, every "
          "Review Item, every null field and every underlying decimal - plus the JSON export "
          "document and both CSV exports as text.", "",
          "Any divergence blocks delivery (task section 26).", ""]
    (OUT / "python_web_parity.md").write_text("\n".join(L), encoding="utf-8")

    for r in rows:
        print(f"[{r['result']:>10}] {r['id']}  {r['note']}")
    print("-" * 78)
    print(f"{summary['matching']}/{summary['cases']} match | "
          f"divergent: {summary['divergent'] or 'none'} | STATUS: {summary['status']}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
