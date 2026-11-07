#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_all - the deterministic pipeline, in dependency order, with one verdict at the end.

  extract_workbook             -> artifacts/extraction/*
  build_baseline_dataset       -> artifacts/model/baseline_v1.json
  derive_quantity_model        -> artifacts/model/quantity_model_v2.json   (Phase 2 record)
  verify_certification         -> artifacts/model/certification_verification.*
  build_quantity_model_v3      -> artifacts/model/quantity_model_v3.*      (Phase 3a record)
  build_quantity_model_v4      -> artifacts/model/quantity_model_v4.*      (DEC-10, current)
  build_rule_pack_v4           -> artifacts/model/rule_pack_v4.json + web/assets/rulepack.js
  validate_rules_v4            -> artifacts/validation/regression_(results|report)_v4.*
  export_model_delta_v4        -> artifacts/model/model_delta.*
  issue_trial_forms            -> trial_kit/* + web/assets/trialkit.js (S1 trial kit)
  lint_sources                 -> structural guard over the repo's own sources
  check_python_web_parity      -> artifacts/validation/python_web_parity.*
  check_web_ui                 -> artifacts/validation/web_ui_*
  collect_trial_feedback       -> artifacts/validation/trial_feedback_report.* (S1 roll-up)
  directory_integrity_report   -> artifacts/validation/directory_integrity_report.*
  verify_integrity             -> artifacts/validation/integrity_report.json  (the gate)

`--history` additionally runs the retained Phase 1 / Phase 2 / Phase 3a suites. They are
kept as stage records and are EXPECTED to report the designed ORI-04 failure (SR-09), plus
in the Phase 3a case the expectations DEC-10 replaced; that is why they are not the gate.
"""
from __future__ import annotations

import io
import subprocess
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

MAIN = ["extract_workbook.py", "build_baseline_dataset.py", "derive_quantity_model.py",
        "verify_certification.py", "build_quantity_model_v3.py",
        "build_quantity_model_v4.py", "build_rule_pack_v4.py",
        "validate_rules_v4.py", "export_model_delta_v4.py", "issue_trial_forms.py",
        "lint_sources.py",
        "check_python_web_parity.py", "check_web_ui.py",
        ("collect_trial_feedback.py", ["--self-test"]),   # parser/aggregator regression
        "collect_trial_feedback.py", "directory_integrity_report.py",
        "verify_integrity.py"]
HISTORY = ["validate_rules.py", "validate_rules_v2.py", "validate_rules_v3.py"]
# The superseded WRITERS (build_rule_pack_v3.py, export_model_delta.py,
# export_model_delta_v3.py) are not part of the history run either: they target the same
# files the current pipeline owns, and they now refuse to run unless ALLOW_SUPERSEDED_WRITE=1.
# retained stage records that exit 1 by design (or are superseded artefact builders)
HIST_REASON = {
    "validate_rules.py": "Phase 1 suite: SR-09 (ORI-04) fails by design - approved Expected "
                         "Failure; 15/16 invariants hold",
    "validate_rules_v2.py": "Phase 2 suite: SR-09 by design; SC-01/SC-02 additionally fail "
                            "because they validate a 2.0 document against the schemas that "
                            "are now at 4.0",
    "validate_rules_v3.py": "Phase 3a suite: RT-02 no longer matches (it pins the Main Table "
                            "totals 373.0/417.0/443.8/474.0/506.6) and CT-V2-02 stops on a "
                            "KeyError because the Appendix counter it asserted is now the "
                            "adopted value. Both are the expectations DEC-10 replaced; the "
                            "report on disk (regression_results_v3.json) stays the Phase 3a "
                            "record and is NOT overwritten by a partial run",
}
EXPECTED_FAIL = set(HIST_REASON)


def last_lines(text: str, n: int = 2) -> str:
    keep = [l.strip() for l in (text or "").splitlines() if l.strip()]
    return " / ".join(keep[-n:]) if keep else "(no output)"


def run(step) -> tuple[str, int, str]:
    script, extra = (step, []) if isinstance(step, str) else step
    t0 = time.time()
    p = subprocess.run([sys.executable, str(TOOLS / script)] + list(extra),
                       cwd=str(ROOT),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    dt = time.time() - t0
    tail = last_lines(p.stdout) or last_lines(p.stderr)
    if p.returncode != 0 and not p.stdout.strip():
        tail = "TRACEBACK: " + last_lines(p.stderr, 1)
    return script, p.returncode, f"{dt:5.1f}s  {tail[:170]}"


def main() -> int:
    want_history = "--history" in sys.argv
    bad = []
    print("=" * 100)
    print("Current pipeline (DEC-10: Certification adopted from the Appendix)"
          + ("   (+ retained history suites)" if want_history else ""))
    print("=" * 100)
    for step in MAIN + (HISTORY if want_history else []):
        s = step if isinstance(step, str) else " ".join([step[0]] + list(step[1]))
        _, rc, info = run(step)
        stage = s in EXPECTED_FAIL
        ok = (rc == 0) if not stage else True
        tag = "HIST" if stage else ("OK  " if ok else "FAIL")
        print(f"[{tag}] {s:32} {info}")
        if stage:
            print(f"        -> {HIST_REASON[s]}")
        if not stage and rc != 0:
            bad.append(s)
    print("=" * 100)
    if want_history:
        print("note: HIST entries are retained stage records, not part of the gate.")
        print("      SR-09 (ORI-04) is an approved Expected Failure and must stay red until")
        print("      the Owner closes ORI-04. The Phase 2 and Phase 3a suites additionally")
        print("      carry expectations that DEC-10 and the 4.0 schemas replaced - each is")
        print("      listed with its reason above, and their reports on disk remain the")
        print("      record of the phase that produced them.")
    if bad:
        print("PIPELINE: FAIL ->", ", ".join(bad))
        return 1
    print("PIPELINE: ALL GREEN   (gate = validate_rules_v4 + parity + web UI + verify_integrity)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
