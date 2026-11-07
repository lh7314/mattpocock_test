#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""End-of-task integrity gate (DEC-10 round).

1. Re-hash original_documents and compare against the frozen inventory (must be identical).
2. Re-check the derived baseline numbers (unchanged since Phase 1).
3. Re-check the Certification per-cell verification grid (the data facts did not move).
4. Re-check the ADOPTED model: the Appendix total is the adopted value, counted once, and the
   Main Table derivation is retained as audit evidence and counted zero times.
5. Re-check the rule package, the schemas, the regression suite and its probe ledger, the
   model delta and its attribution, the Python<->Web parity report, the Web MVP log and the
   three exported artefacts.
6. Classify every file in the directory. original_documents must show zero changes and there
   must be no file of unknown origin. The report uses Directory Integrity wording: this
   folder has never been under version control.

Read-only apart from its own report under artifacts/validation/.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:\GAMING_NRE_AGENT")
SRC = ROOT / "original_documents"
TOL = 1e-9
EXPECTED = {
    "Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.xlsx":
        "48a360ff2ffd086e41d6b90a916f64fe52d9bc13efba07b8377b2945c846ab5a"
}
GOLDEN_TOTALS = {"SKU2": 365.0, "SKU3": 417.0, "SKU4": 443.8, "SKU5": 474.0, "SKU6": 507.0}
GOLDEN_ADOPTED = {"SKU2": 366.0, "SKU3": 408.0, "SKU4": 438.8, "SKU5": 469.0, "SKU6": 502.0}
GOLDEN_CERT = {"SKU2": 32.0, "SKU3": 33.0, "SKU4": 36.0, "SKU5": 37.0, "SKU6": 38.0}
GOLDEN_QM = {"PER_SKU_RATE": 38, "PER_PHASE_FIXED": 4}
fails: list[str] = []
checks = 0


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def chk(ok: bool, label: str, detail: str = "") -> bool:
    global checks
    checks += 1
    print(f"  [{'OK' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))
    if not ok:
        fails.append(label if not detail else f"{label} :: {detail}")
    return ok


def approx(a, b, tol=TOL) -> bool:
    return abs(float(a) - float(b)) <= tol


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


print("=" * 78)
print("1. original_documents integrity (read-only evidence)")
print("=" * 78)
present = {p.name: sha256(p) for p in sorted(SRC.rglob("*")) if p.is_file()}
chk(set(present) == set(EXPECTED), "original_documents file set unchanged",
    f"{len(present)} file(s)")
for name, want in EXPECTED.items():
    chk(present.get(name) == want, f"SHA-256 unchanged: {name[:52]}...", f"{present.get(name)}")
chk(len(present) == 1, "exactly one file inside original_documents")

print()
print("=" * 78)
print("2. derived baseline (must not have moved since Phase 1)")
print("=" * 78)
base = load("artifacts/model/baseline_v1.json")
for k, v in GOLDEN_TOTALS.items():
    got = base["grand_total_by_sku"][k]
    chk(approx(got, v), f"workbook grand total {k} = {v}", f"got {got}")
chk(base["derived_from"]["sha256"] == EXPECTED[list(EXPECTED)[0]],
    "baseline records the same source SHA-256")
chk(base["status"] == "DRAFT_UNCONFIRMED_BY_OWNER", "baseline stays DRAFT until review")
chk(len(base["functions"]) == 21 and len(base["conflicts"]) == 16,
    "function and conflict counts unchanged",
    f"{len(base['functions'])} functions, {len(base['conflicts'])} conflicts")

print()
print("=" * 78)
print("3. Certification per-cell verification (the data facts)")
print("=" * 78)
cv = load("artifacts/model/certification_verification.json")
grid, s = cv["verification_grid"], cv["summary"]
chk(len(grid) == 40, "grid covers 4 function x 2 phase x 5 SKU = 40 cells", f"{len(grid)}")
chk(s["verified"] + s["mismatch"] + s["not_evaluable"] == len(grid),
    "every cell has exactly one status",
    f"{s['verified']} VERIFIED / {s['mismatch']} MISMATCH / {s['not_evaluable']} NOT_EVALUABLE")
bad = [c for c in grid if c["verification_status"] == "VERIFIED"
       and not approx(c["main_table_per_sku_quantity"] * c["sku_count"], c["appendix_total"])]
chk(not bad, "every VERIFIED cell really satisfies main x SKU == appendix", f"{len(bad)} bad")
bad = [c for c in grid if c["verification_status"] == "MISMATCH"
       and not approx(c["delta"], c["appendix_total"] - c["derived_total"])]
chk(not bad, "every MISMATCH cell keeps its original values and exact delta", f"{len(bad)} bad")
chk(s["verified"] == 33 and s["mismatch"] == 7 and s["not_evaluable"] == 0,
    "verification distribution matches the recorded result",
    f"expected 33/7/0, got {s['verified']}/{s['mismatch']}/{s['not_evaluable']}")
chk(sorted({c["function_name"] for c in grid if c["verification_status"] == "MISMATCH"})
    == ["Green", "RF Certification", "Safety"],
    "the disagreements are confined to Green / RF Certification / Safety",
    json.dumps(s["mismatch_by_function"]))
seven = {(c["function_id"], c["phase"], c["sku_count"]) for c in grid
         if c["verification_status"] == "MISMATCH"}
chk(seven == {("F_RF_CERTIFICATION", "SIT", n) for n in (2, 3, 4, 5, 6)}
    | {("F_GREEN", "SIT", 3), ("F_SAFETY", "FVT", 6)},
    "the seven cells are the same seven cells as before the adoption decision",
    json.dumps(sorted(seven)))
chk(cv["appendix_internally_consistent"] is True,
    "the Appendix block adds up to its own TTL rows (evidence, not a rule)")
chk(cv["ori_02_status"] == "PARTIALLY_RESOLVED", "ORI-02 status follows the evidence",
    f"got {cv['ori_02_status']}")
sem = cv["owner_semantics"]
chk(sem["decision"].startswith("DEC-10")
    and sem["appendix_counted_in_project_total_times"] == 1
    and sem["main_derived_counted_in_project_total_times"] == 0
    and sem["appendix_may_be_added_to_the_main_derived_total"] is False,
    "the verification artefact states the DEC-10 counting rules")
j = cv["j33_investigation"]
chk(j["additive_to_main_table_result"] is False
    and j["mvp_requires_antenna_wlan_input_now"] is False
    and j["disposition"] == "DECLARED_NOT_GENERALIZED",
    "J33 is non-additive evidence and does not force new MVP inputs")
chk(not cv.get("legacy_competing_model_audit", {}).get("hits"),
    "the competing-Certification behaviour is absent from the live Python and Web cores",
    json.dumps(cv.get("legacy_competing_model_audit", {}).get("hits", ["<audit missing>"])))

print()
print("=" * 78)
print("4. ADOPTED model (QMODEL-V4) - Appendix adopted, Main Table retained")
print("=" * 78)
qm = load("artifacts/model/quantity_model_v4.json")
got = qm["summary"]["by_quantity_model"]
chk(got == GOLDEN_QM, f"Quantity Model distribution {GOLDEN_QM}", json.dumps(got))
chk(qm["model_id"] == "QMODEL-V4" and qm["supersedes"].startswith("QMODEL-V3"),
    "the model is V4 and names what it supersedes", qm["supersedes"])
chk(qm["status"] == "DRAFT_PENDING_OWNER", "the Quantity Model stays DRAFT pending Owner")
chk(qm["owner_decision"]["id"] == "DEC-10"
    and qm["owner_decision"]["adopted_value_source"] == "APPENDIX_TABLE_TOTAL"
    and qm["owner_decision"]["appendix_counted_in_project_total_times"] == 1
    and qm["owner_decision"]["main_derived_counted_in_project_total_times"] == 0
    and qm["owner_decision"]["j33_counted_in_project_total_times"] == 0
    and qm["owner_decision"]["phase_ratio_used"] is None,
    "DEC-10 is recorded as data, not only as prose")
cert_cells = [c for c in qm["cells"] if c["category"] == "CERT"]
chk(len(cert_cells) == 8 and all(c["adopted_source"] == "APPENDIX_TABLE_TOTAL"
                                 for c in cert_cells),
    "all 8 Certification cells adopt the Appendix total")
chk(all(c["value_access"] == "APPENDIX_TABLE_READ" for c in cert_cells),
    "the adopted value is an absolute Appendix read, never a re-derived pseudo rate")
skus = [f"SKU{n}" for n in (2, 3, 4, 5, 6)]
chk(all(approx(c["adopted_absolute"][sk], c["audit"]["per_sku"][sk]["appendix_total"])
        for c in cert_cells for sk in skus),
    "adopted == appendix for every Certification cell at every SKU band")
chk(all(c["main_table_absolute"][sk] is not None
        and c["audit"]["per_sku"][sk]["derived_total"] is not None
        and c["audit"]["counted_in_project_total"] is False
        for c in cert_cells for sk in skus),
    "the Main Table value and its derived total are retained, marked as not counted")
tot = {sk: sum(float(c["adopted_absolute"][sk]) for c in qm["cells"]) for sk in skus}
for sk, v in GOLDEN_ADOPTED.items():
    chk(approx(tot[sk], v), f"adopted project total {sk} = {v}", f"got {tot[sk]}")
cert_tot = {sk: sum(float(c["adopted_absolute"][sk]) for c in cert_cells) for sk in skus}
for sk, v in GOLDEN_CERT.items():
    chk(approx(cert_tot[sk], v), f"adopted Certification total {sk} = {v}",
        f"got {cert_tot[sk]}")
chk(qm["summary"]["certification_audit_cells_counted_in_total"] == 0
    and qm["summary"]["main_derived_totals_counted_in_total"] == 0
    and qm["summary"]["j33_added_to_result"] is False,
    "the model summary declares that nothing is counted twice")
_j33 = [c for c in qm["cells"] if c.get("breakdown_evidence")]
chk(_j33 and all(c["breakdown_evidence"]["additive_to_adopted_value"] is False
                 and c["breakdown_evidence"]["additive_to_main_table_result"] is False
                 and c["formula_candidate"] is None
                 and c["function_id"] == "F_RF_CERTIFICATION" for c in _j33),
    "J33 is attached to RF Certification as evidence only, with no formula to add",
    f"{len(_j33)} cell(s)")
p = qm["policy"]
chk(p["certification_appendix_may_be_added_to_total"] is False
    and p["certification_appendix_may_be_added_to_main_derived_total"] is False
    and p["certification_main_table_may_be_added_to_appendix"] is False
    and p["certification_appendix_may_form_a_band"] is False
    and p["certification_appendix_is_a_capping_model"] is False,
    "no column may be added to the other, banded or used as a cap")
chk(p["certification_j33_role"].startswith("BREAKDOWN_EVIDENCE")
    and p["certification_global_phase_ratio"].startswith("PROHIBITED")
    and p["certification_range_reason_allowed"] == "SKU_NOT_ESTABLISHED only",
    "J33 role, the phase-ratio prohibition and the range reason are pinned")
chk(p["user_override"].startswith("allowed per Analysis")
    and "never written back to the rule pack" in p["user_override"],
    "the override scope (this Analysis only) is a policy line, not only a UI promise")
chk({c["function_id"] for c in qm["cells"] if c["quantity_model"] == "PER_PHASE_FIXED"}
    == {"F_MEPA", "F_HW_PA"}, "MEPA / HW PA remain the only temporary models")
chk(len(qm["model_questions"]) == 6, "the 6 model questions are still open questions")
chk("DERIVED_MAIN_TABLE_AUDIT" in qm["evidence_role_enum"]
    and "ADOPTED_ABSOLUTE_TOTAL" in qm["evidence_role_enum"]
    and "DERIVED_MAIN_TABLE_AUDIT" not in qm["quantity_model_enum"],
    "the new evidence roles exist and are never Quantity Models")

print()
print("=" * 78)
print("5. rule package + schemas")
print("=" * 78)
rp = load("artifacts/model/rule_pack_v4.json")
chk(len(rp["cells"]) == 42, "rule pack carries all 42 cells")
chk(rp["pack_version"] == "RP-V4.0" and rp["status"] == "DRAFT_PENDING_OWNER",
    "rule pack is RP-V4.0 and still DRAFT (DEC-10 does not finalise it)")
chk(rp["certification_adoption"]["appendix_counted_in_project_total_times"] == 1
    and rp["certification_adoption"]["main_derived_counted_in_project_total_times"] == 0
    and rp["certification_adoption"]["j33_counted_in_project_total_times"] == 0
    and rp["certification_adoption"]["phase_ratio_used"] is None,
    "the package states the counting rules the engine must follow")
chk(rp["certification_verification"]["ori_02_status"] == "PARTIALLY_RESOLVED",
    "rule pack carries the ORI-02 status")
chk(rp["j33_investigation"]["additive_to_main_table_result"] is False,
    "rule pack states J33 is not additive")
chk(all(o["blocks_manual_mvp"] is False for o in rp["open_owner_review_items"]),
    "no open Owner Review Item blocks the manual MVP")
chk(rp["owner_review_item_count"] == len(rp["open_owner_review_items"]) == 19,
    "19 unique Owner Review Items are published", str(rp["owner_review_item_count"]))
chk(sum(rp["owner_review_impact_tag_counts"].values()) == rp["owner_review_item_count"],
    "impact tags sum back to the unique question count (one tag per question)",
    json.dumps(rp["owner_review_impact_tag_counts"]))
chk(len({o["id"] for o in rp["open_owner_review_items"]}) == rp["owner_review_item_count"],
    "no Owner Review Item id is duplicated in the package")
ins, outs = load("schema/input.schema.json"), load("schema/output.schema.json")
chk(ins["properties"]["schema_version"]["const"] == "4.0"
    and outs["properties"]["schema_version"]["const"] == "4.0", "both schemas are v4")
wv = ins["$defs"]["specWave"]["properties"]["wave"]["enum"]
chk("NO_EXPLICIT_ASSIGNMENT" in wv and "UNKNOWN" in wv,
    "input schema still accepts the UI wording and UNKNOWN", json.dumps(wv))
chk("SYSTEM_APPENDIX_ADOPTED" in ins["properties"]["certification_input"]["properties"]["mode"]["enum"]
    and ins["properties"]["certification_input"]["properties"]["override_scope"]["const"]
    == "THIS_ANALYSIS_ONLY",
    "input schema declares the adopted mode and the override scope")
cp = outs["$defs"]["certification"]["properties"]
chk(cp["counted_in_project_total_times"]["const"] == 1
    and cp["main_derived_counted_in_project_total_times"]["const"] == 0
    and cp["adopted_value_role"]["const"] == "ADOPTED_ABSOLUTE_TOTAL"
    and cp["main_table_role"]["const"] == "DERIVED_MAIN_TABLE_AUDIT"
    and cp["main_table_and_appendix_added_together"]["const"] is False
    and cp["j33_added_to_result"]["const"] is False
    and cp["j33_counted_in_project_total_times"]["const"] == 0
    and cp["phase_ratio_used"]["type"] == "null",
    "output schema structurally pins once-only counting and forbids addition")
cc = outs["$defs"]["certCell"]["properties"]
chk(cc["main_derived_counted_in_project_total"]["const"] is False,
    "per-cell schema states the audit value is never counted")
rs = load("schema/rule.schema.json")
chk("ADOPTED_ABSOLUTE_TOTAL" in json.dumps(rs) and "DERIVED_MAIN_TABLE_AUDIT" in json.dumps(rs),
    "rule schema carries the DEC-10 evidence roles")

print()
print("=" * 78)
print("6. regression suite and probe ledger")
print("=" * 78)
reg_doc = load("artifacts/validation/regression_results_v4.json")
reg = reg_doc["summary"]
chk(reg["status"] == "CLEAN", "regression status", f"{reg['status']}")
chk(reg["expected_failures"] == ["SR-09"],
    "Expected Failure set is exactly ['SR-09']", json.dumps(reg["expected_failures"]))
chk("SR-09" in reg["probes_failing"], "SR-09 (ORI-04) is still failing, not turned green")
chk(not reg["regressions"], "no regressions", json.dumps(reg["regressions"]))
led = reg.get("probe_ledger", {})
chk(led.get("carried_unchanged", 0) + led.get("adapted_in_this_task", 0)
    + led.get("retired_in_this_task", 0) == led.get("previous_total", -1),
    "previous total = carried + adapted + retired",
    f"{led.get('carried_unchanged')}+{led.get('adapted_in_this_task')}+"
    f"{led.get('retired_in_this_task')} vs {led.get('previous_total')}")
chk(led.get("carried_unchanged", 0) + led.get("adapted_in_this_task", 0)
    + led.get("added_in_this_task", 0) == led.get("current_total", -1) == reg["total"],
    "current total = carried + adapted + added = probes executed",
    f"{led.get('current_total')} vs executed {reg['total']}")
chk(led.get("retired_ids") == ["CT-V2-02", "SC-05"],
    "exactly the two probes DEC-10 replaced are retired", json.dumps(led.get("retired_ids")))
chk(not led.get("unexpected_retirements") and not led.get("undocumented_additions"),
    "no probe disappeared or appeared without being recorded",
    json.dumps({"gone": led.get("unexpected_retirements"),
                "new": led.get("undocumented_additions")}))
ids = {r["id"] for r in reg_doc["results"]}
RETIRED = set(led.get("retired_ids", []))
need = ({f"DA-{i:02d}" for i in range(1, 13)} | {f"EX-{i:02d}" for i in range(1, 7)}
        | {"ST-01", "ST-02", "ST-03"}
        | {f"CT-V2-{i:02d}" for i in range(1, 13)}) - RETIRED
chk(need <= ids, "DEC-10, export, statistics and the surviving CT-V2 guards all ran",
    f"missing {sorted(need - ids) or 'none'}")
chk(not ({"CT-V2-02", "SC-05", "CT-01", "CT-02", "CT-03", "CT-08"} & ids),
    "retired probes are absent, not silently still passing")
chk(reg.get("owner_review_item_count") == 19
    and sum(reg.get("owner_review_impact_tag_counts", {}).values()) == 19,
    "the suite reports unique ORIs and impact tags separately",
    f"{reg.get('owner_review_item_count')} / "
    f"{reg.get('owner_review_impact_tag_counts')}")

print()
print("=" * 78)
print("7. model delta and attribution")
print("=" * 78)
d = load("artifacts/model/model_delta.json")
got = {f"SKU{r['sku_count']}": r["current_total_appendix_adopted"] for r in d["rows"]}
chk(all(approx(got[k], v) for k, v in GOLDEN_ADOPTED.items()),
    f"adopted totals {GOLDEN_ADOPTED}", json.dumps(got))
gotc = {f"SKU{r['sku_count']}": r["certification_total"] for r in d["rows"]}
chk(all(approx(gotc[k], v) for k, v in GOLDEN_CERT.items()),
    f"adopted Certification totals {GOLDEN_CERT}", json.dumps(gotc))
chk(d["attribution"]["attribution_closes"], "the delta is fully attributed with no residual",
    json.dumps(d["attribution"]["residual_per_sku"]))
adelta = {f"SKU{r['sku_count']}": r["attributed_to_certification_adoption"] for r in d["rows"]}
chk(all(approx(adelta[k], v) for k, v in {"SKU2": -7.0, "SKU3": -9.0, "SKU4": -5.0,
                                          "SKU5": -5.0, "SKU6": -4.6}.items()),
    "the adoption moved the totals by exactly the seven cell differences",
    json.dumps(adelta))
chk({f"SKU{r['sku_count']}": r["attributed_to_mepa_hw_pa_temporary_model"]
     for r in d["rows"]} == {"SKU2": 8.0, "SKU3": 0.0, "SKU4": 0.0, "SKU5": 0.0,
                             "SKU6": -0.4},
    "MEPA / HW PA contribution is unchanged and separately attributed")
chk(d["sku_range"]["state"] == "RANGE" and d["sku_range"]["reason"] == "SKU_NOT_ESTABLISHED"
    and d["sku_range"]["totals"] == {"4": 438.8, "5": 469.0}
    and d["sku_range"]["certification"] == {"4": 36.0, "5": 37.0},
    "the 4-5 SKU range is still published as a range, both candidates priced",
    json.dumps(d["sku_range"], ensure_ascii=False)[:160])
s6 = d["sku6_review"]
chk(approx(s6["current_total_appendix_adopted"], 502.0)
    and approx(s6["certification_total"], 38.0)
    and approx(s6["certification_total_audit_main_derived"], 42.6)
    and len(s6["disagreeing_cells_at_6_sku"]) == 2,
    "the 6 SKU review reproduces from the cell detail",
    json.dumps({k: s6[k] for k in ("current_total_appendix_adopted", "certification_total",
                                   "certification_total_audit_main_derived")}))
chk(sorted(c["function_id"] for c in s6["disagreeing_cells_at_6_sku"])
    == ["F_RF_CERTIFICATION", "F_SAFETY"], "6 SKU disagreements are Safety FVT and RF SIT")

print()
print("=" * 78)
print("8. Python <-> Web consistency, Web MVP behaviour and exports")
print("=" * 78)
pw = load("artifacts/validation/python_web_parity.json")["summary"]
chk(pw["status"] == "MATCH", "Python and Web cores agree on every case",
    f"{pw['matching']}/{pw['cases']} | divergent {pw['divergent']}")
chk(pw["cases"] >= 40, "the consistency suite covers at least 40 cases", str(pw["cases"]))
chk(pw["tolerance"] == 1e-9, "numeric tolerance is 1e-9")
chk("NOTFOUND" in pw["network"], "the browser ran with DNS disabled")
chk(set(pw["exports_compared"]) == {"json_document", "review_csv", "feedback_csv"},
    "the exports are compared, not assumed", json.dumps(pw["exports_compared"]))
cov = pw.get("certification_mismatch_cells_covered", {})
chk(set(cov) == {"Green/SIT@3", "Safety/FVT@6", "RF/SIT@2", "RF/SIT@3", "RF/SIT@4",
                 "RF/SIT@5", "RF/SIT@6"},
    "every disagreeing Certification cell is covered by at least one parity case",
    json.dumps(sorted(cov)))
ui = load("artifacts/validation/web_ui_results.json")
chk(ui["status"] == "CLEAN", "Web MVP end-to-end probe is clean",
    f"{ui['passed']}/{ui['total']}")
ui_ids = " ".join(r["id"] for r in ui["results"])
for need_id in ("UI-25", "UI-26", "UI-27", "UI-28", "UI-29", "UI-30"):
    chk(need_id in ui_ids, f"DEC-10 UI probe ran: {need_id}")
for rel in ("web/index.html", "web/new.html", "web/result.html", "web/assets/core.js",
            "web/assets/rulepack.js", "web/assets/store.js", "web/assets/app.js",
            "web/assets/app.css", "web/trial.html", "web/assets/trial.js",
            "web/assets/trialkit.js"):
    chk((ROOT / rel).exists(), f"MVP file present: {rel}")
pack_src = (ROOT / "web/assets/rulepack.js").read_text(encoding="utf-8")
core_src = (ROOT / "web/assets/core.js").read_text(encoding="utf-8")
store_src = (ROOT / "web/assets/store.js").read_text(encoding="utf-8")
chk("window.RULEPACK" in pack_src and "373" not in core_src.replace('"', ""),
    "the front end hard-codes no business totals - they come from the rule pack")
for phrase in ("CERTIFICATION_MODEL_UNRESOLVED(", "unresolved_certification",
               "competing_candidates"):
    chk(phrase not in core_src, f"forbidden legacy behaviour absent from the Web core: {phrase}")
chk("APPENDIX_TABLE_TOTAL" in core_src and "DERIVED_MAIN_TABLE_AUDIT" in core_src,
    "the Web core carries the DEC-10 adopted / audit split")
chk("export_review_csv" in (ROOT / "prototype/rules_v3.py").read_text(encoding="utf-8-sig")
    and "exportReviewCSV" in store_src and "exportTrialFeedbackCSV" in store_src,
    "the three exporters exist on both sides (Python is the reference)")
app_src = (ROOT / "web/assets/app.js").read_text(encoding="utf-8-sig")
chk("采用值（附表）" in app_src and "主表口径与差异" in app_src,
    "the result page shows the adopted value first and the Main Table inside details")

print()
print("=" * 78)
print("9. terminology and Register consistency")
print("=" * 78)
ban = ("worktree", "HEAD", "branch", "commit")
for rel in ("artifacts/validation/directory_integrity_report.md",
            "docs/41_directory_integrity_v4.md"):
    txt = (ROOT / rel).read_text(encoding="utf-8-sig")
    chk(not [b for b in ban if b in txt], f"{rel} uses Directory Integrity wording only",
        json.dumps([b for b in ban if b in txt]))
chk((ROOT / "tools/directory_integrity_report.py").exists()
    and not (ROOT / "tools/worktree_report.py").exists(),
    "the report tool is named for what it actually inspects")
reg_md = (ROOT / "docs/38_owner_review_register_v4.md").read_text(encoding="utf-8-sig")
doc_ids = re.findall(r"^### (ORI-\d+[a-z]?) ", reg_md, re.M)
pack_ids = [o["id"] for o in rp["open_owner_review_items"]]
chk(sorted(set(doc_ids)) == sorted(set(pack_ids)) and len(doc_ids) == len(set(doc_ids)),
    "the Register document and the rule package list the same unique ORIs",
    f"doc {len(doc_ids)} unique {len(set(doc_ids))} | pack {len(pack_ids)}")
chk("唯一 Owner 问题" in reg_md and "影响标签" in reg_md,
    "the Register separates unique questions from impact tags in its own counting table")

print()
print("=" * 78)
print("9b. trial feedback roll-up (the S1 evidence S2 depends on)")
print("=" * 78)
tf = load("artifacts/validation/trial_feedback_report.json")
chk(tf["current_rule_pack"] == rp["pack_version"],
    "the roll-up was computed against the current rule pack", tf["current_rule_pack"])
chk(tf["canonical_owner_review_items"] == pack_ids,
    "the roll-up tracks exactly the unique Owner questions the Register lists")
chk(tf["coverage"]["owner_items_total"] == rp["owner_review_item_count"],
    "the roll-up counts the same number of Owner questions as the rule pack")
chk(tf["canonical_certification_cells"] == ["Green / SIT", "RF Certification / SIT",
                                            "Safety / FVT"],
    "the roll-up tracks the three disagreeing Function / Phase cells",
    json.dumps(tf["canonical_certification_cells"]))
VERDICTS = ("TRIAL_NOT_STARTED", "EVIDENCE_INCOMPLETE", "DECISION_REQUIRED", "READY_FOR_S2")
chk(tf["verdict"] in VERDICTS, "the roll-up states a defined S1 verdict", tf["verdict"])
chk(not (rp["status"] == "CONFIRMED" and tf["verdict"] != "READY_FOR_S2"),
    "a CONFIRMED rule pack would require completed trial evidence",
    f"pack {rp['status']} / trial {tf['verdict']}")
chk(not tf.get("unreadable_files"),
    "every file in the trial inbox is a readable feedback form",
    json.dumps(tf.get("unreadable_files", []))[:120])
chk(tf["coverage"]["underlying_mismatch_cells_total"] == 7,
    "the roll-up still reports all seven underlying disagreeing cells",
    str(tf["coverage"]["underlying_mismatch_cells_total"]))

print()
print("=" * 78)
print("9c. issued trial roster (which project proves which disagreement)")
print("=" * 78)
seven = sorted(f'{c["function_name"]} / {c["phase"]} @ SKU{c["sku_count"]}'
               for c in grid if c["verification_status"] == "MISMATCH")
roster = load("trial_kit/roster.json")
chk(roster["rule_pack"] == rp["pack_version"],
    "the issued roster was built from the current rule pack", roster["rule_pack"])
chk(sorted(roster["all_mismatch_cells"]) == seven,
    "the roster lists exactly the seven disagreeing cells the certification grid found",
    json.dumps(roster["all_mismatch_cells"]))
chk(sorted(roster["cells_covered_by_roster"]) == seven,
    "between them the issued cases can exercise every disagreeing cell",
    json.dumps(roster["cells_not_covered_by_roster"]))
chk(len({c["project_name"] for c in roster["cases"]}) == len(roster["cases"]),
    "every issued case has a distinct project name (that name is how feedback is joined back)")
chk(all((ROOT / c["form_file"]).exists() for c in roster["cases"]),
    "every issued case has a blank form on disk")
forms = [c["form_file"] for c in roster["cases"]]
chk(not any("feedback_inbox" in f for f in forms),
    "blank forms are never issued into the inbox, so they cannot be mistaken for answers")
chk(tf["coverage"]["trial_cases_total"] == len(roster["cases"]),
    "the roll-up counts the same cases the roster issued",
    f'{tf["coverage"]["trial_cases_total"]} vs {len(roster["cases"])}')
covered_cases = {c["case"] for c in roster["cases"]}
chk(all(r["case"] in covered_cases or r["case"] == "-" for r in tf["trial_cases"]),
    "the roll-up maps every case it lists back to the roster")

print()
print("=" * 78)
print("9d. in-browser trial mode (what the team actually clicks, and what comes back)")
print("=" * 78)
GATE_IDS = ("REVIEWER_NAME", "REVIEW_DATE", "CASE_RUN", "RULE_PACK", "REQUIRED_ANSWERED",
            "TARGET_CELLS_EXERCISED", "ANSWER_REASON")
trial_js = (ROOT / "web/assets/trial.js").read_text(encoding="utf-8-sig")
trial_html = (ROOT / "web/trial.html").read_text(encoding="utf-8-sig")
kit = json.loads((ROOT / "web/assets/trialkit.js").read_text(encoding="utf-8-sig")
                 .split("window.TRIALKIT = ", 1)[1].rstrip().rstrip(";"))
coll_src = (ROOT / "tools/collect_trial_feedback.py").read_text(encoding="utf-8-sig")
chk(kit["rule_pack"] == rp["pack_version"],
    "the roster the Web trial mode offers is for the current rule pack", kit["rule_pack"])
chk([c["project_name"] for c in kit["cases"]] == [c["project_name"] for c in roster["cases"]],
    "the page cannot invent cases: its case list is the roster this tool issued")
chk(sorted(kit["cells_covered_by_roster"]) == seven,
    "the cases the page offers still cover all seven disagreeing cells",
    json.dumps(kit["cells_not_covered_by_roster"]))
chk(all(c["locked"]["key_factors"] and c["locked"]["project_name"] for c in kit["cases"]),
    "every case is issued locked, so a reviewer cannot quietly change what they are grading")
chk("案例配置不可修改" in trial_js,
    "the trial page says in the reviewer's language that the case config is locked")
for c in kit["cases"]:
    cell_qs = {q["cell"] for q in c["questions_required"] if q["kind"] == "cell"}
    chk(cell_qs == set(c["covers_cells"]),
        f'{c["case"]} asks about exactly the cells it can exercise',
        json.dumps([sorted(cell_qs), c["covers_cells"]]))
chk({o for c in kit["cases"] for o in c["oris_required"]} != set(pack_ids),
    "no single reviewer is asked all 19 Owner questions: each case asks what it exercised",
    str(len({o for c in kit["cases"] for o in c["oris_required"]})))
chk(all({o for o in c["oris_reachable"]} >= set() and
        {q["id"] for q in c["questions_optional"]} | set(c["oris_required"])
        == set(pack_ids) for c in kit["cases"]),
    "every case can still reach all 19 Owner questions (the rest are optional, not deleted)")
for gid in GATE_IDS:
    chk(gid in trial_js, f"the trial page runs check {gid}")
    chk(gid in coll_src, f"the collector re-runs check {gid} instead of trusting the page")
chk("SAMPLE_REQUIREMENT_TRIAL_SUBMISSION" in trial_js
    and "SAMPLE_REQUIREMENT_TRIAL_SUBMISSION" in coll_src,
    "the submission format is agreed on both ends of the trial")
chk("SAMPLE_REQUIREMENT_ANALYSIS" in coll_src,
    "the legacy CSV + analysis-JSON format is still read (old submissions stay valid)")
for need in ("trial-submission-", "superseded"):
    chk(need in coll_src, f"the collector handles its preferred format ({need})")
chk(all(k in tf["coverage"] for k in ("submissions", "legacy_feedback_files",
                                      "superseded_legacy_files", "submission_gate_findings")),
    "the roll-up reports the two formats separately", json.dumps(sorted(tf["coverage"])[:6]))
chk((ROOT / "trial_kit/START_HERE.md").exists()
    and (ROOT / "feedback_inbox/DROP_FILES_HERE.txt").exists(),
    "the two pages a reviewer actually needs exist: START_HERE and the drop-folder note")
start = (ROOT / "trial_kit/START_HERE.md").read_text(encoding="utf-8-sig")
chk(all(c["project_name"] in start for c in roster["cases"]),
    "START_HERE names the same five projects the roster issues")
chk("空白不算同意" in start and "姓名" in start and "日期" in start,
    "START_HERE states the two rules that decide whether a submission counts")
# what the reviewer is told must match what the page actually enforces, or the trial
# produces answers collected under a promise the form never made
# "七件事", not "7件事": count the rows the reviewer is shown and read the numeral back
_cn = "\u96f6\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341"
_gdoc = start.split("## \u63d0\u4ea4\u524d\u4f1a\u6321\u4f60\u7684", 1)
_gdoc = _gdoc[1].split("\n## ", 1)[0] if len(_gdoc) > 1 else ""
_grows = [x for x in _gdoc.split("\n") if x.startswith("| ")][1:]      # minus the header (|---| never matches "| ")
chk(len(_grows) == len(GATE_IDS)
    and f"\u63d0\u4ea4\u524d\u4f1a\u6321\u4f60\u7684{_cn[len(GATE_IDS)]}\u4ef6\u4e8b" in start,
    "START_HERE warns about exactly as many submit gates as the page runs",
    f"doc {_grows and len(_grows)} rows / heading vs page {len(GATE_IDS)} gates")
chk(all(o in start for o in ("\u9644\u8868\u6b63\u786e", "\u4e3b\u8868\u6b63\u786e",
                             "\u6309\u6761\u4ef6\u533a\u5206", "\u65e0\u6cd5\u5224\u65ad")),
    "START_HERE teaches the four v4.1 choices, not the retired agree/disagree wording",
    json.dumps([o for o in ("\u9644\u8868\u6b63\u786e", "\u4e3b\u8868\u6b63\u786e",
                              "\u6309\u6761\u4ef6\u533a\u5206", "\u65e0\u6cd5\u5224\u65ad")
                if o not in start], ensure_ascii=False))
chk("\u5fc5\u987b\u5199\u7406\u7531" in start or "\u5199\u7406\u7531" in start,
    "START_HERE says in the reviewer's language that a cell choice needs a reason")
chk("trial-submission-" in (ROOT / "feedback_inbox/DROP_FILES_HERE.txt")
    .read_text(encoding="utf-8-sig"),
    "the drop-folder note tells reviewers what to put in it")
chk(f"{ui['passed']}/{ui['total']}" == f"{ui['total']}/{ui['total']}",
    "the Web probe (which now drives trial.html end to end) is clean",
    f"{ui['passed']}/{ui['total']}")
for tid in ("UI-40", "UI-41", "UI-42", "UI-43", "UI-44", "UI-45", "UI-46", "UI-47",
            "UI-48", "UI-49"):
    chk(tid in ui_ids, f"trial-mode UI probe ran: {tid}")

print("9d-2. Trial Form v4.1 (the form the team actually answers, #32 / #33 / #34)")
print("=" * 78)
FORM = "4.1"
OPTIONS = ["\u9644\u8868\u6b63\u786e", "\u4e3b\u8868\u6b63\u786e",
           "\u6309\u6761\u4ef6\u533a\u5206", "\u65e0\u6cd5\u5224\u65ad"]
chk(kit.get("form_version") == FORM and roster.get("form_version") == FORM,
    "what is issued is Trial Form v4.1, on the roster and on the page alike",
    f'{kit.get("form_version")} / {roster.get("form_version")}')
chk(kit.get("cell_options") == OPTIONS,
    "the four v4.1 choices are complete and in the issued order",
    json.dumps(kit.get("cell_options"), ensure_ascii=False))
for c in kit["cases"]:
    cellq = [q for q in c["questions_required"] if q["kind"] == "cell"]
    chk(c.get("form_version") == FORM and cellq,
        f'{c["case"]} is issued on the v4.1 form', str(c.get("form_version")))
    chk(all(q.get("options") == OPTIONS and q.get("reason_required") is True
            and q.get("form_version") == FORM for q in cellq),
        f'{c["case"]} asks every mismatch cell as a four-way choice with a mandatory reason',
        json.dumps([[q.get("options"), q.get("reason_required")] for q in cellq],
                   ensure_ascii=False)[:120])
    chk(all((not q.get("options")) or q.get("options") == OPTIONS
            for q in c["questions_required"]),
        f'{c["case"]} never offers a fifth answer nobody agreed on')
status = {c["case"]: c.get("issue_status") for c in roster["cases"]}
chk(status.get("C1") == "RETURNED" and status.get("C2") == "RETURNED",
    "the two cases already handed back are marked returned, not reissuable",
    json.dumps(status, ensure_ascii=False))
chk(all(status.get(k) == "OPEN" for k in ("C3", "C4", "C5")),
    "C3, C4 and C5 are back in an issuable state after the v4.1 fix",
    json.dumps([status.get(k) for k in ("C3", "C4", "C5")]))
chk(sorted(kit.get("returned_cases") or []) == ["C1", "C2"],
    "the page knows which two cases it must not ask for twice",
    json.dumps(kit.get("returned_cases")))
returned_files = {c["case"]: c.get("returned_submission", "") for c in roster["cases"]
                  if c.get("issue_status") == "RETURNED"}
chk(returned_files and all((ROOT / "feedback_inbox" / v).exists()
                           for v in returned_files.values()),
    "the two returned submissions are still in the inbox, unread and unreplaced",
    json.dumps(sorted(returned_files.values())))
inbox_subs = sorted(p.name for p in (ROOT / "feedback_inbox").glob("trial-submission-*.json"))
chk(len(inbox_subs) == len(returned_files),
    "no rehearsal submission ever reached the real inbox",
    json.dumps(inbox_subs))
# one gate name, both ends: what the page calls ANSWER_REASON the collector re-runs
for gid in ("REQUIRED_ANSWERED", "ANSWER_REASON"):
    chk(gid in trial_js and gid in coll_src,
        f"the page and the collector name the {gid} check the same way")
chk('data-k="answer"' in trial_js and "<select" in trial_js,
    "the page renders a real dropdown per mismatch cell instead of a free-text box")
for token in ("GREEN_SIT", "SAFETY_FVT", "RF_CERTIFICATION_SIT"):
    chk(token in coll_src, f"ORI-02 is decided per Function / Phase ({token})")
chk("FUNCTION_SPECIFIC_DECISION_REQUIRED" in coll_src,
    "different Functions reaching different conclusions is a decision, not a contradiction")
for tid in ("UI-50", "UI-51", "UI-54", "UI-55", "UI-56", "UI-57", "UI-58", "UI-59"):
    chk(tid in ui_ids, f"Trial Form v4.1 UI probe ran: {tid}")
# DEFECT #32: an answer and its reason must survive into both report files
md_report = (ROOT / "artifacts/validation/trial_feedback_report.md").read_text(
    encoding="utf-8-sig")
ev = ([e for c in tf["certification_cell_ledger"] for e in c["evidence"]]
      + [e for o in tf["owner_review_item_ledger"] for e in o["evidence"]])
chk(ev and all("answer" in e and "comment" in e and "case" in e and "reviewer" in e
               for e in ev),
    "every evidence row keeps the chosen answer, the typed reason, the case and the reviewer",
    json.dumps(sorted(ev[0].keys()) if ev else []))
typed = [e for e in ev if (e.get("comment") or "").strip()]
chk(typed and all(e["comment"] in md_report for e in typed),
    "DEFECT #32: each typed reason reaches the Markdown report verbatim",
    f"{len(typed)} reasons checked")
chk("RF Certification \u662f15" in md_report,
    "the RF Certification dissent is quoted, not summarised away")
# DEFECT #33: conflicts are judged inside one Function / Phase sub-decision
chk("ori_sub_decisions" in tf, "the roll-up reports ORI answers by sub-decision")
o2 = [o for o in tf["owner_review_item_ledger"] if o["id"] == "ORI-02"][0]
chk(o2["conflict"] is False
    and o2["conclusion"] == "FUNCTION_SPECIFIC_DECISION_REQUIRED",
    "ORI-02 is not reported as a contradiction when Green and RF Certification differ",
    json.dumps({"conflict": o2["conflict"], "conclusion": o2["conclusion"]}))
chk("ORI-02" not in tf["coverage"]["conflicting"]
    and "ORI-02" in tf["coverage"]["function_specific_owner_items"],
    "ORI-02 sits where an Owner decision is owed, not in the conflict list",
    json.dumps({"conflicting": tf["coverage"]["conflicting"],
                "function_specific": tf["coverage"]["function_specific_owner_items"]}))
chk(all(b["sub_decision"] in ("GREEN_SIT", "SAFETY_FVT", "RF_CERTIFICATION_SIT", "PACK_LEVEL")
        for b in tf["ori_sub_decisions"].get("ORI-02", [])),
    "ORI-02 sub-decisions use the three agreed Function / Phase buckets",
    json.dumps([b["sub_decision"] for b in tf["ori_sub_decisions"].get("ORI-02", [])]))
chk(len(tf["owner_review_item_ledger"]) == rp["owner_review_item_count"] == 19,
    "sub-decisions added no formal ORI: the Owner still has 19 items to answer",
    f'{len(tf["owner_review_item_ledger"])} / {rp["owner_review_item_count"]}')

print()
print("=" * 78)
print("9d-3. the wave a case presets (ORI-03 is still unanswered, so cite nothing)")
print("=" * 78)
# ORI-03: the formal requirement sheet has no wave column, and DEC-04 forbids inferring a
# wave from a second SSD / Memory Spec. A case may still PRESET a wave to exercise the
# mechanism - without C5's preset the Current Wave collapses back to 6 SKU and SKU4 / SKU5
# lose their only in-trial evidence - but it must never cite the Owner's sheet as the
# source. A submission carries its locked input, so a false citation there reaches the
# Owner dressed up as evidence.
wave_cases = [c for c in kit["cases"] if (c.get("wave_assignment") or {}).get("specs")]
chk([c["case"] for c in wave_cases] == ["C5"],
    "exactly one issued case presets a wave, so only one reviewer is asked about it",
    json.dumps([c["case"] for c in wave_cases]))
for c in wave_cases:
    wa = c["wave_assignment"]
    chk(wa.get("declared_by") != "FORMAL_REQUIREMENT_SHEET"
        and all(s.get("wave_source") != "FORMAL_REQUIREMENT_SHEET" for s in wa["specs"]),
        f'{c["case"]} cites no requirement-sheet wave source (the sheet has no wave column)',
        json.dumps([wa.get("declared_by"), [s.get("wave_source") for s in wa["specs"]]]))
    chk(wa.get("assumption") is True and (wa.get("assumption_note") or "").strip(),
        f'{c["case"]} marks its preset wave an unconfirmed assumption',
        json.dumps([wa.get("assumption"), wa.get("assumption_note")], ensure_ascii=False))
chk("assumption_note" in trial_js and ".assumption" in trial_js,
    "the trial page prints that assumption under the wave table it shows the reviewer")
# the two returned cases must not be collected twice: a second copy is noise, not evidence
chk("\u5df2\u7ecf\u56de\u6536" in start and "duplicate" in start,
    "START_HERE tells the team not to hand back an already-collected case again")
chk("\u672a\u7ecf Owner \u786e\u8ba4" in start,
    "START_HERE says the preset wave is not an Owner confirmation")
c5 = [c for c in kit["cases"] if c["case"] == "C5"][0]
sc5 = {s["scope"]: s for s in c5["scenarios"]}
chk(sc5["CURRENT_WAVE"]["sku_range"] == "4-6"
    and sc5["FULL_PROJECT"]["sku_range"] == "6-6",
    "C5 still forks Current Wave from Full Project - deleting the preset to dodge ORI-03 "
    "would silently delete the SKU4 / SKU5 evidence as well",
    json.dumps([[k, v["sku_range"]] for k, v in sorted(sc5.items())]))
chk({"RF Certification / SIT @ SKU4", "RF Certification / SIT @ SKU5",
     "RF Certification / SIT @ SKU6", "Safety / FVT @ SKU6"} <= set(c5["covers_cells"]),
    "C5 still exercises the four cells only it can reach",
    json.dumps(c5["covers_cells"], ensure_ascii=False))
chk(not any(s.get("factor") in ("ssd", "mem") for c in wave_cases
            for s in c["wave_assignment"]["specs"]),
    "no wave is inferred from the existence of a second SSD / Memory Spec (DEC-04 / WV-05)")

print()
print("=" * 78)
print("10. file classification (directory integrity)")
print("=" * 78)
BUCKETS = {"SOURCE (read-only, Owner)": [], "DELIVERABLE (review target)": [],
           "EVIDENCE (reproducible)": [], "TOOL / PROTOTYPE": [], "WEB MVP": [],
           "INCOMING (team trial feedback)": [], "TRIAL KIT (issued cases, blank forms)": [],
           "UNEXPECTED": []}
for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    if "__pycache__" in p.parts or p.suffix == ".pyc":
        continue          # interpreter cache, not project content
    rel = p.relative_to(ROOT).as_posix()
    if rel.startswith("original_documents/"):
        b = "SOURCE (read-only, Owner)"
    elif rel.startswith("web/"):
        b = "WEB MVP"
    elif rel.startswith(("docs/", "schema/", "CHANGES.md")):
        b = "DELIVERABLE (review target)"
    elif rel.startswith("feedback_inbox/"):
        b = "INCOMING (team trial feedback)"
    elif rel.startswith("trial_kit/"):
        b = "TRIAL KIT (issued cases, blank forms)"
    elif rel.startswith("artifacts/"):
        b = "EVIDENCE (reproducible)"
    elif rel.startswith(("tools/", "prototype/")):
        b = "TOOL / PROTOTYPE"
    else:
        b = "UNEXPECTED"
    BUCKETS[b].append(rel)
for b, items in BUCKETS.items():
    print(f"  {b}: {len(items)}")
    if b == "UNEXPECTED":
        for i in items:
            print("      ", i)
chk(not BUCKETS["UNEXPECTED"], "zero files of unknown origin")
chk(len(BUCKETS["SOURCE (read-only, Owner)"]) == 1, "original_documents still holds 1 file")

report = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "checks": checks, "failures": fails,
    "result": "PASS" if not fails else "FAIL",
    "owner_decision": qm["owner_decision"]["id"],
    "adopted_value_source": qm["owner_decision"]["adopted_value_source"],
    "original_documents": {k: v for k, v in present.items()},
    "buckets": {k: len(v) for k, v in BUCKETS.items()},
    "regression": {"total": reg["total"], "holding": reg["probes_holding"],
                   "expected_failures": reg["expected_failures"],
                   "regressions": reg["regressions"], "status": reg["status"],
                   "ledger": led},
    "owner_review_items": {"unique": rp["owner_review_item_count"],
                           "impact_tags": rp["owner_review_impact_tag_counts"]},
    "trial_feedback": {"verdict": tf["verdict"],
                       "feedback_files": tf["coverage"]["feedback_files"],
                       "owner_items_with_verdict":
                           tf["coverage"]["owner_items_with_verdict"],
                       "certification_cells_with_verdict":
                           tf["coverage"]["certification_cells_with_verdict"],
                       "underlying_cells_evidenced":
                           f'{tf["coverage"]["underlying_mismatch_cells_evidenced"]}/7',
                       "cases_returned": f'{tf["coverage"]["trial_cases_returned"]}'
                                         f'/{tf["coverage"]["trial_cases_total"]}',
                       "roster_rule_pack": roster["rule_pack"],
              "submissions": tf["coverage"]["submissions"],
              "legacy_forms": tf["coverage"]["legacy_feedback_files"],
              "submissions_rejected_on_recheck":
                  len(tf["coverage"]["submission_gate_findings"]),
              "ori_asked_as_required": len(
                  {o for c in kit["cases"] for o in c["oris_required"]}),
              "ori_total": len(pack_ids)},
    "ori_02_status": cv["ori_02_status"],
    "adopted_totals": got,
    "web_parity": pw["status"], "web_ui": ui["status"],
}
(ROOT / "artifacts/validation").mkdir(parents=True, exist_ok=True)
(ROOT / "artifacts/validation/integrity_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

print()
print("=" * 78)
if fails:
    print("RESULT: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print(f"RESULT: PASS ({checks} checks) - original_documents untouched, DEC-10 adopted values "
      f"reproducible, Python and Web agree, all files accounted for.")
print(f"  regression {reg['probes_holding']}/{reg['total']} hold | "
      f"expected-fail {reg['expected_failures']} | ORI-02 {cv['ori_02_status']} | "
      f"parity {pw['status']} | web UI {ui['status']} | "
      f"trial {tf['verdict']} | "
      f"ORI unique {rp['owner_review_item_count']}")
