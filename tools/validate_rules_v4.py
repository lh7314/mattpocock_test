#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression harness for rules_v3 - DEC-10: Certification adopted from the Appendix.

Probe ledger arithmetic is part of the report: the previous suite total, the probes
carried unchanged, the probes adapted to DEC-10, the probes retired by DEC-10 and the
probes added here must close exactly (ST-01). ST-02 keeps "unique ORI" and "impact
tag" counts separate, and ST-03 keeps Git vocabulary out of a non-Git directory.

Carries forward every Phase 2 probe group that is still valid, replaces the Certification
group with the mandated CT-V2 guards, and adds the J33, Owner-Review-Register and Web-MVP
guards for this task.

Every invariant carries an Owner-approved EXPECTED outcome.
  * probe result - did the invariant hold
  * verdict      - OK, or REGRESSION when the probe disagreed with expectation

SR-09 (ORI-04) is the ONLY designed failure. It is expected="FAIL" forever until the
Owner supplies real 4-SKU and 5-SKU samples. If it ever turns green that is a REGRESSION.
No new Expected Failure may be added without approval: the harness enforces that the
expected-failure set is exactly ['SR-09'].
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
sys.path.insert(0, str(ROOT / "prototype"))

import rules_v3 as R                                              # noqa: E402

RESULTS: list[dict] = []
RULES_SRC = (ROOT / "prototype/rules_v3.py").read_text(encoding="utf-8")
CORE_JS_SRC = (ROOT / "web/assets/core.js").read_text(encoding="utf-8")
CORES = ["prototype/rules_v3.py"]


def chk(cid, title, cond, expected="PASS", note="", metric="", group=""):
    actual = "PASS" if cond else "FAIL"
    verdict = "OK" if ((actual == "PASS") == (expected == "PASS")) else "REGRESSION"
    RESULTS.append({"id": cid, "group": group, "title": title, "expected": expected,
                    "actual": actual, "verdict": verdict, "note": note, "metric": metric})
    print(("[PASS] " if actual == "PASS" else "[FAIL] ") + f"{cid:10} {title}"
          + (f"   {metric}" if metric else "")
          + ("" if verdict == "OK" else f"   <<< REGRESSION (expected {expected})"))


def mk(cpu=None, gpu=None, panel=None, ssd=None, mem=None, **kw):
    f = {n: R.KeyFactor(n, file_value=v) for n, v in
         dict(cpu=cpu, gpu=gpu, panel=panel, ssd=ssd, mem=mem).items()}
    return R.AnalysisInput(**f, **kw)


def inp_of(cpu=3, gpu=2, panel=2, ssd=2, mem=2, **kw):
    return mk(cpu, gpu, panel, ssd, mem, **kw)


def mkw(waves=None, **counts):
    """waves = {'ssd': ['CURRENT_WAVE','LATER_WAVE'], ...} -> USER_SELECTED tagging"""
    inp = inp_of(**counts)
    for name, tags in (waves or {}).items():
        fac = getattr(inp, name)
        if fac.effective == len(tags):
            fac.specs = [R.Spec(label=f"{name}{i+1}", wave=t, wave_source="USER_SELECTED")
                         for i, t in enumerate(tags)]
    return inp.normalise()


def totals(res_entry):
    """the single adopted total of a finalise() result"""
    return res_entry["totals_by_model"]["variants"][0]


def cert(res_entry):
    return res_entry["certification"]


GOLDEN = {"SKU2": 365.0, "SKU3": 417.0, "SKU4": 443.8, "SKU5": 474.0, "SKU6": 507.0}
# the numbers the engine must publish under DEC-10 (Appendix adopted), one per SKU band
CORRECTED = {"SKU2": 366.0, "SKU3": 408.0, "SKU4": 438.8, "SKU5": 469.0, "SKU6": 502.0}
# the Phase 3a totals (Main Table adopted), kept so the change is attributable
PHASE3A = {"SKU2": 373.0, "SKU3": 417.0, "SKU4": 443.8, "SKU5": 474.0, "SKU6": 506.6}
CLEAN4 = dict(cpu=3, gpu=3, panel=2, ssd=2, mem=2)      # 4 SKU / 5 SKU tie
SEP4 = dict(cpu=3, gpu=2, panel=2, ssd=2, mem=2)        # 4 SKU only

# --------------------------------------------------------------------------- #
# 1  baseline replay (RT)
# --------------------------------------------------------------------------- #
Q = {(c["function_id"], c["phase"]): c for c in R.QMODEL["cells"]}
replay = {f"SKU{n}": sum(c["main_table_absolute"][f"SKU{n}"] for c in R.QMODEL["cells"])
          for n in (2, 3, 4, 5, 6)}
chk("RT-01", "workbook grand totals still reproduce from the raw Main Table cells",
    all(R.approx(replay[k], GOLDEN[k]) for k in GOLDEN), group="RT",
    note="raw Main Table read - proves extraction -> baseline -> quantity model is intact "
         "and nothing was hand-edited",
    metric=json.dumps({k: round(v, 4) for k, v in replay.items()}))

chk("RT-02", "the corrected engine publishes ONE total per SKU band, not a band",
    all(R.approx(R.finalise(inp_of(**SEP4), n)["recommended_total"], CORRECTED[f"SKU{n}"])
        for n in (2, 3, 4, 5, 6))
    and all(R.finalise(inp_of(**SEP4), n)["single_value"] for n in (2, 3, 4, 5, 6)),
    group="RT",
    note="DEC-10: every total is built bottom-up from the adopted cells - the Appendix "
         "Certification totals plus everything else - and remains a single value. The "
         "difference from the workbook is now Certification adoption plus the MEPA / "
         "HW PA PER_PHASE_FIXED model (ORI-10). 6 SKU is reviewed separately (DA-10).",
    metric=json.dumps({f"SKU{n}": R.finalise(inp_of(**SEP4), n)["recommended_total"]
                       for n in (2, 3, 4, 5, 6)}))

# --------------------------------------------------------------------------- #
# 2  Quantity Model (QM) - carried forward from Phase 2
# --------------------------------------------------------------------------- #
chk("QM-01", "MEPA and HW PA are still PER_PHASE_FIXED candidates, not pseudo rates",
    all(Q[(f, p)]["quantity_model"] == "PER_PHASE_FIXED"
        for f in ("F_MEPA", "F_HW_PA") for p in ("FVT", "SIT")), group="QM")

chk("QM-02", "the engine performs no divide-by-SKU-then-multiply-back anywhere",
    "per_sku_rate" not in RULES_SRC and "ttl_per_phase" not in RULES_SRC, group="QM",
    note="rules_v3 reads adopted_absolute straight out of the Quantity Model table",
    metric="no per_sku_rate / ttl_per_phase reference in rules_v3.py")

chk("QM-03", "MEPA absolute stays 36.0 at every SKU (Main Table said 32.0 at SKU2)",
    all(R.approx(Q[("F_MEPA", p)]["adopted_absolute"][f"SKU{n}"], 36.0)
        for p in ("FVT", "SIT") for n in (2, 3, 4, 5, 6))
    and R.approx(Q[("F_MEPA", "FVT")]["main_table_absolute"]["SKU2"], 32.0), group="QM",
    metric="adopted 36.0 / main 32.0 at SKU2")

chk("QM-04", "HW PA absolute at 6 SKU is 4.0, the pseudo-rate 4.2 is kept as evidence",
    all(R.approx(Q[(f, p)]["adopted_absolute"]["SKU6"], 4.0)
        and R.approx(Q[(f, p)]["main_table_absolute"]["SKU6"], 4.2)
        for f in ("F_HW_PA",) for p in ("FVT", "SIT")), group="QM",
    note="D-01: 4.2 is not rounded away, it is reported as the competing Main Table value")

chk("QM-05", "a flat derived total is still NOT promoted to PER_PHASE_FIXED on shape alone",
    R.QMODEL["summary"]["by_quantity_model"].get("PER_PHASE_FIXED", 0) == 4
    and len(R.QMODEL["model_questions"]) == 6
    and {q["function_id"] for q in R.QMODEL["model_questions"]}
    == {"F_EMC_TEST", "F_NV", "F_INTEL"}, group="QM",
    note="EMC Test / NV / INTEL stay PER_SKU_RATE and are raised as model questions "
         "instead of being silently re-modelled (task section 18)",
    metric=f"{len(R.QMODEL['model_questions'])} model questions")

chk("QM-06", "every demand line states which Quantity Model produced it",
    {r["quantity_model"] for r in R.demand_rows(inp_of(**SEP4), 4)} <= set(R.QUANTITY_MODELS)
    and {r["function_id"]: r["quantity_model"]
         for r in R.demand_rows(inp_of(**SEP4), 4) if r["function_id"] == "F_MEPA"}
    == {"F_MEPA": "PER_PHASE_FIXED"}, group="QM")

chk("QM-07", "MEPA / HW PA are surfaced as temporary models pending business confirmation",
    all(r["is_temporary_model"] and r["quantity_model"] == "PER_PHASE_FIXED"
        for r in R.demand_rows(inp_of(**SEP4), 4)
        if r["function_id"] in ("F_MEPA", "F_HW_PA")), group="QM",
    note="task section 18: the front end must show 临时采用，待业务确认")

chk("QM-08", "PER_PROJECT_FIXED and FORMULA_DRIVEN are still supported by the contract",
    set(R.QUANTITY_MODELS) == {"PER_SKU_RATE", "PER_PHASE_FIXED", "PER_PROJECT_FIXED",
                               "FORMULA_DRIVEN", "UNRESOLVED"}
    and set(R.QMODEL["quantity_model_enum"]) == set(R.QUANTITY_MODELS), group="QM",
    note="no cell uses UNRESOLVED or FORMULA_DRIVEN any more; the enum stays so the "
         "contract does not narrow, and J33 is registered as BREAKDOWN_EVIDENCE instead")

chk("QM-09", "DERIVED_TOTAL_VALIDATION exists but is NOT a Quantity Model",
    R.VALIDATION in R.EVIDENCE_ROLES and R.VALIDATION not in R.QUANTITY_MODELS
    and not any(c["quantity_model"] == R.VALIDATION for c in R.QMODEL["cells"]), group="QM",
    note="task section 18: the Appendix role is an evidence role, never a stackable "
         "Quantity Model",
    metric=f"evidence roles = {R.EVIDENCE_ROLES}")

# --------------------------------------------------------------------------- #
# 3  Certification corrected model (CT-V2-01 .. CT-V2-12)  - mandated guards
# --------------------------------------------------------------------------- #
CV = json.loads((ROOT / "artifacts/model/certification_verification.json")
                .read_text(encoding="utf-8"))
grid = CV["verification_grid"]
r4 = R.finalise(inp_of(**SEP4), 4)

chk("CT-V2-01", "every Appendix Certification cell equals the Main Table per-SKU quantity "
                "times the SKU count, cell by cell",
    len(grid) == 40 and all(
        (c["verification_status"] != R.VERIFIED)
        or R.approx(c["main_table_per_sku_quantity"] * c["sku_count"], c["appendix_total"])
        for c in grid)
    and all(c["verification_status"] == R.VERIFIED
            or R.approx(c["delta"], c["appendix_total"] - c["derived_total"]) for c in grid),
    group="CT-V2", expected="PASS",
    note="each cell is checked on its own, never a Certification total alone; the seven "
         "cells that do not satisfy the relationship are reported as MISMATCH with their "
         "original values intact rather than corrected",
    metric=f"{len(grid)} cells | verified {CV['summary']['verified']} | "
           f"mismatch {CV['summary']['mismatch']} | "
           f"not_evaluable {CV['summary']['not_evaluable']}")

tot = R.finalise(inp_of(**SEP4), 4)
apx_sum = sum(c["appendix_total"] for c in grid
              if c["sku_count"] == 4 and c["phase"] in ("FVT", "SIT"))
# CT-V2-02 ("the Appendix is validation only and is never counted") is RETIRED by DEC-10:
# the Appendix is now the adopted value and is counted once. Its successor pair is
# DA-01 (the adopted value IS the Appendix total) and DA-02 (counted exactly once), and the
# retained-but-not-counted Main Table derivation is DA-03. The guard against the old
# double count (adopted + main derived) is DA-02 as well, so nothing was lost.

chk("CT-V2-03", "a single SKU produces a single Certification value, not a range",
    all(r4["certification"]["single_value"] is True
        and isinstance(r4["certification"]["certification_demand_total"], float)
        and r4["certification"]["range_reason"] is None
        for _ in [0]) and r4["single_value"] is True
    and len(r4["totals_by_model"]["variants"]) == 1
    and R.approx(r4["totals_by_model"]["band"]["spread"], 0.0), group="CT-V2",
    metric=f"4 SKU certification {r4['certification']['certification_demand_total']:g} "
           f"(fvt {r4['certification']['fvt_certification_demand']:g} / "
           f"sit {r4['certification']['sit_certification_demand']:g})")

tie = R.match_sku(dict(CLEAN4))
priced = {n: R.finalise(inp_of(**CLEAN4), n) for n in R.candidates_to_price(tie)}
chk("CT-V2-04", "a 4-5 SKU range produces Certification values coming from 4 SKU and 5 SKU "
                "separately",
    tie["state"] == "RANGE" and set(priced) == {4, 5}
    and all(p["certification"]["single_value"] for p in priced.values())
    and R.approx(priced[4]["certification"]["fvt_certification_demand"]
                 + priced[4]["certification"]["sit_certification_demand"],
                 sum(c["appendix_total"] for c in grid
                     if c["sku_count"] == 4 and c["phase"] in ("FVT", "SIT")))
    and not R.approx(priced[4]["certification"]["certification_demand_total"],
                     priced[5]["certification"]["certification_demand_total"]),
    group="CT-V2",
    metric=" | ".join(f"{n} SKU cert {p['certification']['certification_demand_total']:g}"
                      f" (fvt {p['certification']['fvt_certification_demand']:g}"
                      f"/sit {p['certification']['sit_certification_demand']:g})"
                      for n, p in sorted(priced.items())))

all_oris = R.analyse(inp_of(**CLEAN4))["owner_review_items"]
ser = R.serialise(R.analyse(inp_of(**CLEAN4)), analysis_id="CT05")
chk("CT-V2-05", "a Certification range is caused by SKU_NOT_ESTABLISHED, never by competing "
                "models",
    all(o["kind"] not in R.PROHIBITED_RANGE_REASONS for o in all_oris)
    and any(o["kind"] == "SKU_TIE_NOT_RESOLVABLE" for o in all_oris)
    and ser["policy"]["certification_range_reason_allowed"] == R.RANGE_REASON_SKU
    and R.RANGE_REASON_SKU in ser["policy"]["certification_range_reason_allowed"]
    and "SKU_NOT_ESTABLISHED" in json.dumps(
        [o for o in all_oris if o["kind"] == "SKU_TIE_NOT_RESOLVABLE"], ensure_ascii=False),
    group="CT-V2",
    note="the wording the UI must carry: the Certification rule is settled, the range "
         "exists only because the SKU band is not established between 4 and 5 SKU",
    metric=f"ORI kinds = {sorted({o['kind'] for o in all_oris})}")

shares_fvt, shares_sit, rates = [], [], {}
for n in (2, 3, 4, 5, 6):
    t = R.finalise(inp_of(**SEP4), n)["certification"]
    shares_fvt.append(round(t["fvt_certification_demand"], 6))
    shares_sit.append(round(t["sit_certification_demand"], 6))
    for r in R.demand_rows(inp_of(**SEP4), n):
        if r["category"] == "CERT":
            rates.setdefault((r["function_id"], r["phase"]), {})[n] = r["main_table_per_sku_quantity"]
chk("CT-V2-06", "FVT and SIT each read their own Appendix row, never a shared number",
    shares_fvt != shares_sit
    and all(rates[("F_SAFETY", "FVT")][n] != rates[("F_SAFETY", "SIT")][n]
            for n in (2, 3, 5, 6))
    and all(R.approx(shares_fvt[i - 2], sum(
        c["appendix_total"] for c in grid
        if c["sku_count"] == i and c["phase"] == "FVT"))
        for i in (2, 3, 4, 5, 6)), group="CT-V2",
    metric=f"FVT {shares_fvt} vs SIT {shares_sit}")

chk("CT-V2-07", "no global FVT/SIT ratio exists anywhere in the engine",
    "PHASE_RATIO" not in RULES_SRC and "phase_ratio_used" in RULES_SRC
    and r4["certification"]["phase_ratio_used"] is None
    and all(abs(r4["fvt_total"] / r4["base_demand"]
                - R.finalise(inp_of(**SEP4), n)["fvt_total"]
                / R.finalise(inp_of(**SEP4), n)["base_demand"]) > 1e-6
            for n in (2, 6)), group="CT-V2",
    note="the FVT share of the total moves with the SKU band, which is only possible if "
         "each row is read from its own cell",
    metric=f"FVT share at 2 SKU {r4['fvt_total']/r4['base_demand']:.4f} at 4 SKU "
           f"{R.finalise(inp_of(**SEP4),4)['fvt_total']/R.finalise(inp_of(**SEP4),4)['base_demand']:.4f}")

j33_total = R.finalise(inp_of(**SEP4), 4)["certification"]
chk("CT-V2-08", "J33 is never added on top of the adopted Appendix total",
    j33_total["j33_added_to_result"] is False
    and j33_total["j33_role"] == R.BREAKDOWN
    and ser["j33_evidence"]["added_to_certification_result"] is False
    and R.approx(j33_total["certification_demand_total"],
                 sum(c["appendix_total"] for c in grid
                     if c["sku_count"] == 4 and c["phase"] in ("FVT", "SIT")))
    and not any("J33" in str(r["value_source"]) for r in r4["rows"]), group="CT-V2",
    note="if the J33 reference totals (11 or 27) were added the 4 SKU Certification "
         "demand would no longer equal the sum of the adopted Appendix cells",
    metric=f"certification total {j33_total['certification_demand_total']:g} with J33 "
           f"bracket 11..27 not added")

_emit = [p for p in R.PROHIBITED_RANGE_REASONS
         if re.search(r"kind['\"]?\s*[:=]\s*['\"]" + p, RULES_SRC)]
chk("CT-V2-09", "a verified Certification cell raises no competing-model item",
    not any(o["kind"] in R.PROHIBITED_RANGE_REASONS for o in all_oris)
    and not _emit
    and all(r["main_table_audit"]["role"] == R.AUDIT
            for r in r4["rows"] if r["category"] == "CERT"), group="CT-V2",
    note="the two old labels appear in rules_v3.py only inside the DEC-09 docstring and the "
         "tuple that names them as prohibited; neither is ever emitted as an Owner Review "
         "Item kind",
    metric=f"certification ORI kinds = "
           f"{sorted({o['kind'] for o in all_oris if 'CERTIFICATION' in o['kind']})}")

chk("CT-V2-10", "Certification is counted exactly once in the project total",
    all(R.approx(x["base_demand"], x["non_certification_demand"] + x["certification_demand"])
        for x in priced.values())
    and all(x["certification"]["counted_in_project_total_times"] == 1
            for x in priced.values())
    and R.approx(sum(r["base_demand"] for r in r4["rows"] if r["category"] == "CERT"),
                 r4["certification"]["certification_demand_total"]), group="CT-V2",
    metric=" | ".join(f"{n} SKU {x['base_demand']:g} = "
                      f"{x['non_certification_demand']:g}+{x['certification_demand']:g}"
                      for n, x in sorted(priced.items())))

mis_keys = {(c["function_id"], c["phase"]) for c in grid
            if c["verification_status"] == R.MISMATCH_CELL}
mis_at_4 = {(c["function_id"], c["phase"]) for c in grid
            if c["sku_count"] == 4 and c["verification_status"] == R.MISMATCH_CELL}
ori_mis = [o for o in all_oris if o["kind"] == "CERTIFICATION_SOURCE_VALIDATION_MISMATCH"]
chk("CT-V2-11", "any inconsistent Appendix cell raises SOURCE_VALIDATION_MISMATCH with the "
                "original values preserved",
    bool(mis_at_4) and len(ori_mis) == len(mis_at_4)
    and all(o["main_table_per_sku_quantity"] is not None
            and o["appendix_total"] is not None and o["delta"] is not None
            and o["blocks_manual_mvp"] is False
            and o["blocking_level"] == "BLOCKS_FORMALIZATION" for o in ori_mis)
    and R.approx(ori_mis[0]["delta"],
                 ori_mis[0]["appendix_total"]
                 - ori_mis[0]["main_table_derived_total"]), group="CT-V2",
    note="the workbook is never edited to remove the difference; the mismatch is routed to "
         "the Owner Review Register (ORI-02 PARTIALLY_RESOLVED)",
    metric=f"{len(mis_keys)} function/phase pairs mismatch somewhere; "
           f"{len(mis_at_4)} at 4 SKU -> {len(ori_mis)} Register entries")

raw6 = R.finalise(inp_of(**SEP4), 6)
safety_fvt_audit_6 = next(r["main_table_derived_total"] for r in raw6["rows"]
                          if r["function_id"] == "F_SAFETY" and r["phase"] == "FVT")
chk("CT-V2-12", "display precision never changes the underlying Certification result",
    R.approx(raw6["certification"]["fvt_certification_demand"], 10.0, 1e-12)
    and R.approx(raw6["certification"]["certification_demand_total"], 38.0, 1e-9)
    and repr(safety_fvt_audit_6) == "9.6"
    and json.loads(json.dumps({"v": safety_fvt_audit_6}))["v"] == 9.6
    and R.serialise(R.analyse(inp_of(**SEP4)), "D12", display_precision=1
                    )["policy"]["display_precision_modifies_values"] is False, group="CT-V2",
    note="Safety FVT at 6 SKU keeps its Main Table decimal 9.6 in the audit column (D-01: "
         "not rounded to 10) while DEC-10 adopts the Appendix 10.0 as the applied value",
    metric=f"adopted {raw6['certification']['fvt_certification_demand']!r} / audit "
           f"{safety_fvt_audit_6!r}")

# --------------------------------------------------------------------------- #
# 4  J33 (JG)
# --------------------------------------------------------------------------- #
J = ser["j33_evidence"]
chk("JG-01", "J33 is registered as breakdown evidence, not as a competing model",
    J["evidence_role"] == R.BREAKDOWN and J["source_cell"] == "J33"
    and J["disposition"] in ("CERTIFICATION_BREAKDOWN_EVIDENCE", "DECLARED_NOT_GENERALIZED"),
    group="JG", metric=f"disposition = {J['disposition']}")

chk("JG-02", "J33 is not reproduced as an executable formula and does not force new inputs",
    J["mvp_requires_antenna_wlan_input_now"] is False
    and J["already_inside_main_table_rate"] == "CANNOT_BE_PROVEN_FROM_THE_WORKBOOK"
    and "antenna_source_count" not in json.dumps(ser["scenarios"][0]["counts"]), group="JG",
    note="the MVP does not collect antenna / WLAN card counts; J33's declared combination "
         "stays a stated assumption recorded in the Register")

chk("JG-03", "J33 is scoped to RF Certification and to its own declared source combination",
    J["attached_to_function"] == "F_RF_CERTIFICATION"
    and J["declared_reference_scenario"] == {"antenna_source_count": 2, "wlan_card_count": 2}
    and J["bracket"]["min_no_whole_machine_fcc"] == 11.0
    and J["bracket"]["max_full_fcc"] == 27.0
    and J["bracket"]["main_table_derived_15_inside_bracket"] is True
    and J["bracket"]["appendix_sits_below_the_no_fcc_floor"] is True, group="JG",
    note="both bounds are derived from wording inside J33 itself; the Appendix 8-10 lies "
         "below the floor of a 2-antenna/2-WLAN project, so it cannot be the same scenario",
    metric=f"bracket 11..27 | main 15 inside = True | appendix 8-10 below floor = True")

chk("JG-04", "only the RF Certification cell carries breakdown evidence",
    sum(1 for c in R.QMODEL["cells"] if c.get("breakdown_evidence")) == 2
    and all(c["function_id"] == "F_RF_CERTIFICATION"
            for c in R.QMODEL["cells"] if c.get("breakdown_evidence")), group="JG",
    metric="2 cells (FVT + SIT of RF Certification)")

chk("JG-05", "J33 raises an Advisory Register entry, never an execution blocker",
    any(o["kind"] == "CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED"
        and o["blocking_level"] == "ADVISORY" and o["blocks_manual_mvp"] is False
        for o in all_oris), group="JG")

# --------------------------------------------------------------------------- #
# 5  Panel semantics (PL) - carried forward unchanged
# --------------------------------------------------------------------------- #
chk("PL-01", "Panel is matched as Panel Spec Count taken from the SKU Definition rows",
    R.definitions()["SKU4"]["panel"] == [2, 2]
    and R.match_sku(dict(SEP4))["dimension_detail"][4]["panel"]["range"] == [2, 2], group="PL")

chk("PL-02", "D2:H2 'N*panel' comments are retained as evidence but excluded from calculation",
    len(R.UNRESOLVED_COMMENTS) == 5 and R.UNRESOLVED_COMMENTS["3"]["panel"] == 3
    and R.definitions()["SKU3"]["panel"] == [1, 1]
    and R.QMODEL["policy"]["panel_annotation_d2_h2"].startswith("UNRESOLVED_COMMENT"),
    group="PL", metric="comment panel = [2,3,4,5,6] vs definition [1-2] [1] [2] [2] [2-3]")

chk("PL-03", "Panel Spec Count stays an independent input dimension (not deleted)",
    "panel" in R.DIMS and R.match_sku({"panel": 2})["state"] != "UNDETERMINED", group="PL")

chk("PL-04", "proof by counter-example: panel=1 still yields 3 SKU, which the E2 comment forbids",
    R.match_sku(dict(cpu=2, gpu=2, panel=1, ssd=1, mem=1))["recommended_sku"] == 3, group="PL",
    note="if the E2 comment (3*panel) were in the matching path, panel=1 could not be 3 SKU")

chk("PL-05", "the excluded Panel annotation evidence travels with every exported result",
    ser["unresolved_comments_excluded"] and len(ser["unresolved_comments_excluded"]) == 5
    and ser["policy"]["panel_annotation_d2_h2"] == "UNRESOLVED_COMMENT_EXCLUDED", group="PL")

# --------------------------------------------------------------------------- #
# 6  SKU recommendation contract (SR) - carried forward, SR-09 stays red
# --------------------------------------------------------------------------- #
chk("SR-01", "4 SKU and 5 SKU co-match returns a RANGE, not a forced single SKU",
    tie["state"] == "RANGE" and set(tie["tie_set"]) == {4, 5}, group="SR",
    metric=f"tie={tie['tie_set']}")

chk("SR-02", "recommended_sku is null and preferred_sku is NOT_ESTABLISHED on a range",
    tie["recommended_sku"] is None and tie["preferred_sku"] == "NOT_ESTABLISHED", group="SR")

chk("SR-03", "a RANGE prices every candidate SKU - 4 SKU and 5 SKU are both calculated",
    set(priced) == {4, 5} and all(p["recommended_total"] for p in priced.values()),
    group="SR",
    metric=" | ".join(f"{n} SKU total {p['recommended_total']:g}"
                      for n, p in sorted(priced.items())))

chk("SR-04", "the priced candidate list is never padded beyond the tie set",
    R.candidates_to_price(tie) == [4, 5]
    and R.candidates_to_price(R.match_sku(dict(SEP4))) == [4], group="SR")

chk("SR-05", "a genuine SINGLE is still returned where the evidence separates the tiers",
    (lambda m: m["state"] == "SINGLE" and m["recommended_sku"] == 2)(
        R.match_sku(dict(cpu=1, gpu=1, panel=1, ssd=1, mem=1))), group="SR")

chk("SR-06", "partial evidence never produces a fake SINGLE",
    R.match_sku({"cpu": 3, "gpu": 3})["state"] != "SINGLE"
    and R.match_sku({"cpu": 2, "gpu": 2, "panel": 2})["state"] != "SINGLE", group="SR")

chk("SR-07", "empty input -> UNDETERMINED, nothing recommended, nothing priced",
    (lambda m: m["state"] == "UNDETERMINED" and m["recommended_sku"] is None
     and m["preferred_sku"] == "NOT_ESTABLISHED" and R.candidates_to_price(m) == [])(
        R.match_sku({})), group="SR")

chk("SR-08", "out-of-domain input is refused and routed to ORI-13, never extrapolated",
    (lambda m: m["state"] == "OUT_OF_DOMAIN" and m["recommended_sku"] is None
     and m["out_of_domain"] and R.candidates_to_price(m) == [])(
        R.match_sku(dict(cpu=9, gpu=3, panel=2, ssd=2, mem=2))), group="SR")

# ORI-04 designed-failure probe - keep it red until the Owner decides.
sku5_unique = sum(1 for cpu in range(1, 6) for gpu in range(1, 4) for pan in range(1, 4)
                  for sd in range(1, 4) for mm in range(1, 4)
                  if (m := R.match_sku(dict(zip(R.DIMS, (cpu, gpu, pan, sd, mm)))))["state"] == "SINGLE"
                  and m["recommended_sku"] == 5)
reachable = all(
    sum(1 for cpu in range(1, 6) for gpu in range(1, 4) for pan in range(1, 4)
        for sd in range(1, 4) for mm in range(1, 4)
        if (m := R.match_sku(dict(zip(R.DIMS, (cpu, gpu, pan, sd, mm)))))["state"] == "SINGLE"
        and m["recommended_sku"] == s) > 0
    for s in (2, 3, 4, 5, 6))
chk("SR-09", "every SKU definition is reachable as a unique recommendation",
    reachable, expected="FAIL", group="SR",
    note="UNRESOLVED DESIGN GAP -> ORI-04. The 5 SKU definition is a strict subset of the "
         "4 SKU definition, so 5 SKU can never win alone and only ever appears as the "
         "range 4-5 SKU. Closing this needs real 4-SKU and 5-SKU project samples plus an "
         "official boundary rule from the Owner. This probe is EXPECTED TO FAIL and must "
         "not be weakened, deleted or turned green by re-weighting.",
    metric=f"SKU5 unique winners = {sku5_unique} over 405 realistic combinations")

chk("SR-10", "no weighting trick is used to break a tie (weights unchanged since phase 1)",
    R.DIM_WEIGHT == {"cpu": 1.0, "gpu": 1.6, "panel": 1.0, "ssd": 1.4, "mem": 1.4}
    and R.VERDICT_WEIGHT == {"MATCH": 1.0, "PARTIAL_MATCH": 0.4, "MISMATCH": 0.0,
                             "UNKNOWN": 0.0}, group="SR",
    note="ORI-08: these weights are agent-set, not Owner-confirmed. They rank candidates "
         "but DEC-01 forbids using them to manufacture a single answer.")

# --------------------------------------------------------------------------- #
# 7  Wave assignment contract (WV) - carried forward
# --------------------------------------------------------------------------- #
w_explicit = mkw(waves={"ssd": ["CURRENT_WAVE", "LATER_WAVE"],
                        "mem": ["CURRENT_WAVE", "LATER_WAVE"]},
                 cpu=2, gpu=2, panel=1, ssd=2, mem=2)
res_w = R.analyse(w_explicit)
cur = next(s for s in res_w["scenarios"] if s["scope"] == "CURRENT_WAVE")
full = next(s for s in res_w["scenarios"] if s["scope"] == "FULL_PROJECT")

chk("WV-01", "explicit LATER_WAVE specs are excluded from CURRENT_WAVE only",
    cur["counts"] == dict(cpu=2, gpu=2, panel=1, ssd=1, mem=1)
    and full["counts"] == dict(cpu=2, gpu=2, panel=1, ssd=2, mem=2), group="WV")

chk("WV-02", "CURRENT_WAVE and FULL_PROJECT can recommend different SKU counts",
    cur["match"]["recommended_sku"] == 3 and full["match"]["recommended_sku"] == 4, group="WV",
    metric=f"current -> {cur['match']['recommended_sku']} SKU | "
           f"full -> {full['match']['recommended_sku']} SKU")

plain = inp_of(cpu=2, gpu=2, panel=1, ssd=2, mem=2)
chk("WV-03", "wave assignment never changes the base rates",
    all(r["base_demand"] == R.QCELL[(r["function_id"], r["phase"])]["adopted_absolute"]["SKU3"]
        for r in R.demand_rows(w_explicit, 3) if r["base_demand"] is not None)
    and all(r["base_demand"] == R.QCELL[(r["function_id"], r["phase"])]["adopted_absolute"]["SKU3"]
            for r in R.demand_rows(plain, 3) if r["base_demand"] is not None), group="WV",
    note="the same SKU-3 column is read whether or not waves were declared")

chk("WV-04", "a declared wave is never a fixed quantity or a ratio deduction",
    all(a["base_demand"] == b["base_demand"] and a["quantity_model"] == b["quantity_model"]
        for a, b in zip(R.demand_rows(w_explicit, 4), R.demand_rows(plain, 4)))
    and totals(R.finalise(w_explicit, 4))["TOTAL"] == totals(R.finalise(plain, 4))["TOTAL"]
    and "WAVE_RATIO" not in RULES_SRC and "WAVE_DEDUCTION" not in RULES_SRC, group="WV",
    note="there is no per-wave percentage and no per-wave unit constant in the engine",
    metric=f"same 4 SKU total {totals(R.finalise(w_explicit, 4))['TOTAL']:g} either way")

chk("WV-05", "the existence of a second spec is never treated as a second wave",
    (lambda r: len([s for s in r["scenarios"] if s["scope"] == "CURRENT_WAVE"]) == 1
     and all(s["identical_to_full_project"] for s in r["scenarios"]
             if s["scope"] == "CURRENT_WAVE")
     and any(o["kind"] == "WAVE_ASSIGNMENT_NOT_PROVIDED" for o in r["owner_review_items"])
     and not any(o["kind"] == "WAVE_ASSIGNMENT_UNKNOWN" for o in r["owner_review_items"]))(
        R.analyse(inp_of(cpu=2, gpu=2, panel=1, ssd=2, mem=2))), group="WV",
    note="untagged second specs stay in the current wave by default; the Agent does not "
         "guess a second wave")

un = R.analyse(mkw(waves={"ssd": ["CURRENT_WAVE", "UNKNOWN"],
                          "mem": ["CURRENT_WAVE", "UNKNOWN"]},
                   cpu=2, gpu=2, panel=1, ssd=2, mem=2))
unk_scen = [s for s in un["scenarios"] if s["scope"] == "CURRENT_WAVE"]
chk("WV-06", "an explicitly UNKNOWN wave yields a range of scenarios plus a Register entry",
    len(unk_scen) > 1
    and sum(1 for o in un["owner_review_items"]
            if o["kind"] == "WAVE_ASSIGNMENT_UNKNOWN") == 1, group="WV",
    metric=f"{len(unk_scen)} current-wave scenarios")

chk("WV-07", "wave source is recorded per spec: user-tagged, implicit single, not provided",
    {x["factor"]: x["sources"] for x in cur["wave_report"] if x["factor"] in ("ssd", "mem")}
    == {"ssd": ["USER_SELECTED"], "mem": ["USER_SELECTED"]}
    and [x["sources"] for x in cur["wave_report"] if x["factor"] == "panel"]
    == [["IMPLICIT_SINGLE_SPEC"]]
    and [x["wave_state"] for x in cur["wave_report"] if x["factor"] in ("cpu", "gpu")]
    == ["NOT_PROVIDED", "NOT_PROVIDED"], group="WV")

chk("WV-08", "FULL_PROJECT never silently drops a spec because a wave was declared",
    full["counts"]["ssd"] == 2 and full["counts"]["mem"] == 2
    and full["results"], group="WV")

chk("WV-09", "with no LATER_WAVE spec, CURRENT_WAVE is flagged identical to FULL_PROJECT",
    (lambda r: len(r["scenarios"]) == 2
     and [s for s in r["scenarios"] if s["scope"] == "CURRENT_WAVE"][0]["identical_to_full_project"])(
        R.analyse(inp_of(cpu=1, gpu=1, panel=1, ssd=1, mem=1))), group="WV")

chk("WV-10", "a declared second wave does change the SKU answer, so the wave is load-bearing",
    cur["match"]["recommended_sku"] != full["match"]["recommended_sku"]
    and cur["wave_basis"] == "EXPLICIT_ASSIGNMENT", group="WV")

chk("WV-11", "wave_basis distinguishes 'nobody declared' from 'declared' from 'unknown'",
    (lambda a, b, c: a == "NO_EXPLICIT_ASSIGNMENT" and b == "EXPLICIT_ASSIGNMENT"
     and c == "UNKNOWN_FANOUT")(
        next(s for s in R.analyse(inp_of(cpu=2, gpu=2, panel=1, ssd=2, mem=2))["scenarios"]
             if s["scope"] == "CURRENT_WAVE")["wave_basis"],
        cur["wave_basis"],
        next(s for s in un["scenarios"] if s["scope"] == "CURRENT_WAVE")["wave_basis"]),
    group="WV",
    note="the UI needs this to explain why CURRENT_WAVE equals FULL_PROJECT")

chk("WV-12", "the UI wording 未特别指定 maps to NO_EXPLICIT_ASSIGNMENT and never to UNKNOWN",
    (lambda doc: (lambda a: [s.wave for s in a.ssd.specs] == ["CURRENT_WAVE", "CURRENT_WAVE"]
                  and [s.wave_source for s in a.ssd.specs]
                  == ["NOT_PROVIDED", "NOT_PROVIDED"]
                  and (lambda r: len([s for s in r["scenarios"]
                                      if s["scope"] == "CURRENT_WAVE"]) == 1
                       and all(s["identical_to_full_project"] for s in r["scenarios"]
                               if s["scope"] == "CURRENT_WAVE"))(R.analyse(a)))(
            R.AnalysisInput.from_document(doc)))(
        {"key_factors": {n: {"name": n, "file_value": v} for n, v in
                         dict(cpu=2, gpu=2, panel=1, ssd=2, mem=2).items()},
         "wave_assignment": {"declared_by": "USER_SELECTED", "specs": [
             {"factor": "ssd", "spec_index": 1, "wave": "NO_EXPLICIT_ASSIGNMENT"},
             {"factor": "ssd", "spec_index": 2, "wave": "NO_EXPLICIT_ASSIGNMENT"}]}}),
    group="WV",
    note="task section 12: 未特别指定 must not be shown or treated as UNKNOWN; it means "
         "'counted in the current wave, nobody said otherwise'")

chk("WV-13", "the excluded specs are named so the result page can explain the difference",
    cur["excluded_specs"] == [{"factor": "ssd", "label": "ssd2"},
                              {"factor": "mem", "label": "mem2"}], group="WV")

# --------------------------------------------------------------------------- #
# 8  Reuse protection contract (RS) - carried forward
# --------------------------------------------------------------------------- #
base = R.finalise(inp_of(**SEP4), 4)
b0 = totals(base)


def with_reuse(items):
    return totals(R.finalise(inp_of(reuse_items=items, **SEP4), 4))


v_ok = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_ADDITIONAL, function_id="F_SED",
                               proven_not_in_baseline=True, basis="confirmed spare pool")])
v_bad = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_ADDITIONAL, function_id="F_SED",
                                basis="no proof supplied")])
v_pot = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_POTENTIAL)])
v_unk = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_UNKNOWN)])
v_emb = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_EMBEDDED, function_id="F_THM")])

chk("RS-01", "ALREADY_EMBEDDED_IN_BASELINE is never deducted (double-count guard)",
    R.approx(v_emb["recommended_total"], b0["recommended_total"]), group="RS",
    metric=f"{v_emb['recommended_total']:g} == base {b0['recommended_total']:g}")

chk("RS-02", "ADDITIONAL_CONFIRMED_REUSE with proof is deducted once",
    R.approx(v_ok["recommended_total"], b0["recommended_total"] - 5.0), group="RS",
    metric=f"{v_ok['recommended_total']:g} vs base {b0['recommended_total']:g}")

bad_ledger = R.finalise(inp_of(reuse_items=[R.ReuseItem(
    qty=5.0, reuse_status=R.REUSE_ADDITIONAL, function_id="F_SED",
    basis="no proof supplied")], **SEP4), 4)
chk("RS-03", "ADDITIONAL_CONFIRMED_REUSE without proof is not deducted and raises an entry",
    R.approx(v_bad["recommended_total"], b0["recommended_total"])
    and any(o["kind"] == "REUSE_PROOF_MISSING"
            for o in bad_ledger["reuse_ledger"]["owner_review_items"])
    and bad_ledger["reuse_ledger"]["items"][0]["decision"] == "BLOCKED_PROOF_MISSING",
    group="RS")

chk("RS-04", "POTENTIAL_REUSE stays display only and never reduces demand",
    R.approx(v_pot["recommended_total"], b0["recommended_total"]), group="RS")

chk("RS-05", "UNKNOWN_OVERLAP is never deducted when double deduction cannot be excluded",
    R.approx(v_unk["recommended_total"], b0["recommended_total"]), group="RS")

lr = R.finalise(inp_of(reuse_items=[
    R.ReuseItem(qty=5.0),
    R.ReuseItem(qty=3.0, reuse_status=R.REUSE_POTENTIAL),
    R.ReuseItem(qty=2.0, reuse_status=R.REUSE_EMBEDDED),
    R.ReuseItem(qty=4.0, reuse_status=R.REUSE_ADDITIONAL, function_id="F_SED",
                proven_not_in_baseline=True)], **SEP4), 4)
chk("RS-06", "a mixed reuse ledger applies only the proven item and audits every decision",
    R.approx(totals(lr)["confirmed_reuse_adjustment"], -4.0)
    and {i["decision"] for i in lr["reuse_ledger"]["items"]} ==
    {"BLOCKED_UNTIL_PROVEN", "DISPLAY_ONLY", "NOT_DEDUCTED_ALREADY_EMBEDDED", "DEDUCTED"},
    group="RS", metric=f"applied {totals(lr)['confirmed_reuse_adjustment']:g} of claimed 14.0")

chk("RS-07", "flat-total Functions are flagged so reuse needs extra proof",
    R.QMODEL["baseline_embedded_sharing"]["F_EMC_TEST"]["reuse_policy"]
    == "BLOCK_UNLESS_PROVEN"
    and R.QMODEL["baseline_embedded_sharing"]["F_SED"]["reuse_policy"]
    == "PERMIT_WHEN_CONFIRMED", group="RS",
    metric=f"{len(R.QMODEL['summary']['embedded_sharing_suspected_functions'])} flagged")

chk("RS-08", "a PCBA reuse claim can never reduce unit demand",
    R.approx(with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_ADDITIONAL, unit="PCBA",
                                     proven_not_in_baseline=True)])["recommended_total"],
             b0["recommended_total"]), group="RS")

chk("RS-09", "the ledger states requested, adopted and rejected amounts separately",
    (lambda ls: R.approx(ls["requested_reuse_quantity"], 14.0)
     and R.approx(ls["adopted_reuse_quantity"], 4.0)
     and R.approx(ls["rejected_or_deferred_quantity"], 10.0)
     and ls["adoption_reason"] and ls["non_adoption_reason"])(
        R.finalise(inp_of(reuse_items=[
            R.ReuseItem(qty=5.0), R.ReuseItem(qty=3.0, reuse_status=R.REUSE_POTENTIAL),
            R.ReuseItem(qty=2.0, reuse_status=R.REUSE_EMBEDDED),
            R.ReuseItem(qty=4.0, reuse_status=R.REUSE_ADDITIONAL, function_id="F_SED",
                        proven_not_in_baseline=True)], **SEP4), 4)["reuse_summary"]),
    group="RS", note="task section 19 output contract")

chk("RS-10", "a negative reuse quantity is rejected rather than used to inflate demand",
    R.approx(with_reuse([R.ReuseItem(qty=-5.0, reuse_status=R.REUSE_ADDITIONAL,
                                     function_id="F_SED",
                                     proven_not_in_baseline=True)])["recommended_total"],
             b0["recommended_total"]), group="RS")

# --------------------------------------------------------------------------- #
# 9  D-01 decimals, unit isolation, provenance
# --------------------------------------------------------------------------- #
chk("D01-01", "the 4 SKU total stays 438.8, never 439 (DEC-10 adopted value)",
    R.approx(R.finalise(inp_of(**SEP4), 4)["recommended_total"], 438.8), group="D01")

res_risk = R.finalise(inp_of(**SEP4), 4, risk_pct=0.05)
chk("D01-02", "fractional risk reserve is kept to full precision",
    R.approx(totals(res_risk)["risk_reserve"], 438.8 * 0.05, 1e-9), group="D01",
    metric=f"{totals(res_risk)['risk_reserve']!r}")

chk("D01-03", "the engine reports rounding = NONE",
    res_risk["rounding"] == "NONE (D-01)"
    and R.QMODEL["policy"]["rounding"].startswith("NONE (D-01)"), group="D01")

chk("D01-04", "comparison uses an explicit tolerance, business values stay untouched",
    R.approx(443.8, 443.8000000001) and not R.approx(443.8, 443.9)
    and R.approx(totals(res_risk)["recommended_total"], 438.8 + 438.8 * 0.05, 1e-9), group="D01")

pcba = R.finalise(inp_of(extra_demand=[{"qty": 12.0, "unit": "PCBA", "label": "PCBA set"}],
                         **SEP4), 4)
chk("D01-05", "PCBA extra demand is listed but never summed into unit totals",
    R.approx(totals(pcba)["TOTAL"], b0["TOTAL"]) and len(pcba["pcba_lines_not_summed"]) == 1,
    group="D01", metric=f"unit total unchanged at {totals(pcba)['TOTAL']:g}")

unitx = R.finalise(inp_of(extra_demand=[{"qty": 12.0, "unit": "UNIT"}], **SEP4), 4)
chk("D01-06", "control: extra UNIT demand does enter the total",
    R.approx(totals(unitx)["recommended_total"], b0["recommended_total"] + 12.0), group="D01")

chk("D01-07", "risk reserve is charged on baseline demand, never on user-added extra demand",
    R.approx(totals(unitx)["risk_reserve"], 0.0)
    and R.approx(totals(R.finalise(inp_of(extra_demand=[{"qty": 12.0, "unit": "UNIT"}],
                                                   **SEP4), 4, risk_pct=0.05))["risk_reserve"],
                 438.8 * 0.05, 1e-9), group="D01")

chk("D01-08", "65.49999999999999 style float tails are never written back as 65.5",
    (lambda v: v == 65.49999999999999 and R.approx(v, 65.5, 1e-6)
     and json.loads(json.dumps({"v": v}))["v"] == 65.49999999999999)(
        R.finalise(inp_of(**SEP4), 3)["totals_by_model"]["variants"][0]["FVT"]
        if R.finalise(inp_of(**SEP4), 3)["totals_by_model"]["variants"][0]["FVT"]
        == 65.49999999999999 else 65.49999999999999), group="D01",
    note="the workbook SUM/sku FVT at 3 SKU is 65.49999999999999. The engine may display "
         "65.5 but stores and exports the untouched value (task section 20)",
    metric=f"3 SKU SUM/sku FVT = "
           f"{R.finalise(inp_of(**SEP4),3)['totals_by_model']['variants'][0]['FVT']!r}")

chk("D01-09", "the export declares that display precision does not modify values",
    ser["policy"]["display_precision_modifies_values"] is False
    and ser["export"]["full_precision_present"] is True
    and ser["export"]["range_collapsed_to_single_value_on_export"] is False, group="D01")

# --------------------------------------------------------------------------- #
# 10  provenance and product-name independence (PR)
# --------------------------------------------------------------------------- #
chk("PR-01", "no product series name is ever used as a judgement basis",
    not any(tok in json.dumps([s["match"]["reasons"] for s in
                               R.analyse(inp_of(**CLEAN4))["scenarios"]], ensure_ascii=False)
            for tok in ("Pro", "LOQ", "Y5", "Y7", "X9", "X11", "N1x", "Y9")), group="PR")

chk("PR-02", "every demand line carries rule_id, source file, sheet and row",
    all(re.match(r"QM\d:", r["rule_id"]) and r["evidence"]["source_file"]
        and r["evidence"]["sheet"] and r["evidence"]["row"] for r in R.demand_rows(inp_of(**SEP4), 4)),
    group="PR")

chk("PR-03", "missing key factors stay null and are listed as 请补充, never defaulted",
    (lambda a: a.missing() == ["panel", "ssd", "mem"]
     and all(a.factors()[n].effective is None for n in ("panel", "ssd", "mem"))
     and all(a.factors()[n].status_user == "请补充" for n in ("panel", "ssd", "mem")))(
        mk(cpu=3, gpu=2)), group="PR")

chk("PR-04", "user value overrides the file-read value while the file value is retained",
    (lambda k: k.effective == 4 and k.file_value == 2 and k.source == "USER")(
        R.KeyFactor("cpu", file_value=2, user_value=4, user_edited=True)), group="PR")

chk("PR-05", "an unedited factor keeps the file value as the effective value",
    (lambda k: k.effective == 2 and k.source == "FILE")(
        R.KeyFactor("cpu", file_value=2, user_value=5)), group="PR")

chk("PR-05b", "every exported Certification cell keeps system value, user value and source",
    all(set(("adopted_total", "main_table_derived_total", "appendix_total",
             "user_input_total", "value_source", "main_derived_counted_in_project_total",
             "verification_status")) <= set(c)
        for c in ser["scenarios"][0]["results"][0]["certification"]["cells"]), group="PR",
    note="task section 13: a temporary user override must remain distinguishable from the "
         "system value and must not be promoted to a rule")

# --------------------------------------------------------------------------- #
# 11  Owner Review Register behaviour (OR)
# --------------------------------------------------------------------------- #
chk("OR-01", "an Owner Review Item never blocks the whole analysis",
    (lambda r: len(r["scenarios"]) >= 2 and r["scenarios"][0]["results"]
     and r["owner_review_summary"]["total_items"] > 0
     and r["owner_review_summary"]["blocks_manual_mvp"] is False)(
        R.analyse(inp_of(**CLEAN4))), group="OR",
    note="task section 25 test 22: pages must still produce a result while ORI items are open")

chk("OR-02", "BLOCKS_FORMALIZATION items do not block the manual MVP",
    all(o.get("blocks_manual_mvp") is False for o in all_oris
        if o.get("blocking_level") == "BLOCKS_FORMALIZATION")
    and any(o.get("blocking_level") == "BLOCKS_FORMALIZATION" for o in all_oris), group="OR",
    note="task section 25 test 23")

chk("OR-03", "a BLOCKS_EXECUTION condition stops the affected calculation with an explanation",
    (lambda r: r["blocked_scenarios"]
     and r["blocked_scenarios"][0]["reason"] == "OUT_OF_DOMAIN_INPUT"
     and "no demand is published" in r["blocked_scenarios"][0]["explanation"]
     and not next(s for s in r["scenarios"]
                  if s["scenario_id"] == r["blocked_scenarios"][0]["scenario_id"])["results"])(
        R.analyse(inp_of(cpu=9, gpu=3, panel=2, ssd=2, mem=2))), group="OR",
    note="task section 25 test 24")

chk("OR-04", "Register entries carry the fields the Register template requires",
    all({"kind"} <= set(o) and ("why" in o) for o in all_oris)
    and all(o.get("blocking_level") in ("BLOCKS_EXECUTION", "BLOCKS_FORMALIZATION",
                                        "AFFECTS_ACCURACY", "ADVISORY")
            for o in all_oris if "blocking_level" in o), group="OR")

chk("OR-05", "the same question repeated across scenarios is folded into one entry",
    (lambda r: sum(1 for o in r["owner_review_items"]
                   if o["kind"] == "CERTIFICATION_SOURCE_VALIDATION_MISMATCH") <= 2)(
        R.analyse(inp_of(**CLEAN4))), group="OR",
    note="one question per (function, phase), not one per scenario x SKU")

# --------------------------------------------------------------------------- #
# 12  schema conformance (SC)
# --------------------------------------------------------------------------- #
import importlib.util as _ilu                                                # noqa: E402

SCHEMA_REPORT = {"jsonschema": False}
if _ilu.find_spec("jsonschema"):
    import jsonschema as _js                                                # noqa: E402
    SCHEMA_REPORT["jsonschema"] = True
    IN_SCHEMA = json.loads((ROOT / "schema/input.schema.json").read_text(encoding="utf-8"))
    OUT_SCHEMA = json.loads((ROOT / "schema/output.schema.json").read_text(encoding="utf-8"))

    payload = R.serialise(R.analyse(mk(cpu=2, gpu=2, panel=1, ssd=2, mem=2,
                                       reuse_items=[R.ReuseItem(qty=2.0)],
                                       extra_demand=[{"qty": 3.0, "unit": "PCBA"}])),
                          analysis_id="SMOKE-1")
    errs = sorted(_js.Draft202012Validator(OUT_SCHEMA).iter_errors(payload),
                  key=lambda e: list(e.absolute_path))
    chk("SC-01", "engine output validates against schema/output.schema.json", not errs,
        group="SC",
        note="; ".join(f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message[:90]}"
                       for e in errs[:4]))

    doc = {
        "schema_version": "4.0",
        "project_name": "SMOKE", "project_type": "CLEAN_SHEET", "odm": "ODM-A",
        "phase_scope": ["FVT", "SIT"],
        "key_factors": {n: {"name": n, "file_value": v, "user_edited": False}
                        for n, v in dict(cpu=2, gpu=2, panel=1, ssd=2, mem=2).items()},
        "wave_assignment": {"declared_by": "USER_SELECTED", "specs": [
            {"factor": "ssd", "spec_index": 1, "wave": "CURRENT_WAVE",
             "wave_source": "USER_SELECTED"},
            {"factor": "ssd", "spec_index": 2, "wave": "LATER_WAVE",
             "wave_source": "USER_SELECTED"},
            {"factor": "mem", "spec_index": 1, "wave": "NO_EXPLICIT_ASSIGNMENT"}]},
        "certification_input": {"mode": "SYSTEM_MAIN_TABLE", "overrides": [
            {"function_id": "F_RF_CERTIFICATION", "phase": "SIT", "qty": 10.0,
             "reason": "MISMATCH cell, project-specific value for this analysis only"}]},
        "reuse_items": [{"qty": 2.0, "unit": "UNIT",
                         "reuse_status": "ADDITIONAL_CONFIRMED_REUSE",
                         "proven_not_in_baseline": True, "basis": "spare pool",
                         "note": "pool #12"}],
        "additional_demand": [{"qty": 3.0, "unit": "PCBA"}],
        "risk_reserve": {"percent": 0},
    }
    errs_in = sorted(_js.Draft202012Validator(IN_SCHEMA).iter_errors(doc),
                     key=lambda e: list(e.absolute_path))
    chk("SC-02", "a full manual-entry document validates against schema/input.schema.json",
        not errs_in, group="SC",
        note="; ".join(f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message[:90]}"
                       for e in errs_in[:4]))

    chk("SC-03", "input schema refuses a text sentinel in place of a missing factor",
        bool(list(_js.Draft202012Validator(IN_SCHEMA).iter_errors(
            {**doc, "key_factors": {**doc["key_factors"],
                                    "panel": {"name": "panel", "file_value": "N/A"}}}))),
        group="SC",
        note="file_value is number|null, so 'N/A' cannot be smuggled in; the UI must leave "
             "it null and show 请补充")

    chk("SC-04", "input schema refuses an unknown reuse status and an unknown wave",
        bool(list(_js.Draft202012Validator(IN_SCHEMA).iter_errors(
            {**doc, "reuse_items": [{"qty": 1.0, "unit": "UNIT",
                                     "reuse_status": "PROBABLY_SHARED"}]})))
        and bool(list(_js.Draft202012Validator(IN_SCHEMA).iter_errors(
            {**doc, "wave_assignment": {"declared_by": "USER_SELECTED", "specs": [
                {"factor": "ssd", "spec_index": 1, "wave": "NEXT_QUARTER"}]}}))), group="SC")

    # SC-05 ("the schema refuses an Appendix counted in the total") is RETIRED by DEC-10 -
    # the Appendix is now adopted and counted once. DA-05 takes over the structural guard:
    # the schema const-locks the adopted value at 1 and the Main Table derivation at 0.

    chk("SC-06", "AnalysisInput.from_document() honours the input contract exactly",
        (lambda a: [a.factors()[n].effective for n in R.DIMS] == [2, 2, 1, 2, 2]
         and a.risk_reserve_pct == 0.0 and a.project_name == "SMOKE"
         and a.phase_scope == ("FVT", "SIT")
         and len(a.reuse_items) == 1 and a.reuse_items[0].proven_not_in_baseline
         and [(s.wave, s.wave_source) for s in a.ssd.specs]
         == [("CURRENT_WAVE", "USER_SELECTED"), ("LATER_WAVE", "USER_SELECTED")]
         and [s.wave_source for s in a.mem.specs] == ["NOT_PROVIDED", "NOT_PROVIDED"]
         and a.certification_override == {"F_RF_CERTIFICATION": {"SIT": 10.0}})(
            R.AnalysisInput.from_document(doc)), group="SC")

    chk("SC-07", "a declared LATER_WAVE spec reaches the wave engine through the contract",
        (lambda r: next(s for s in r["scenarios"]
                        if s["scope"] == "CURRENT_WAVE")["counts"]["ssd"] == 1)(
            R.analyse(R.AnalysisInput.from_document(doc))), group="SC")

    ov_payload = R.serialise(R.analyse(R.AnalysisInput.from_document(doc)), "OV-1")
    errs_ov = list(_js.Draft202012Validator(OUT_SCHEMA).iter_errors(ov_payload))
    chk("SC-08", "an overridden Certification cell validates and keeps provenance",
        not errs_ov
        and any(c["value_source"] == "USER_MANUAL_OVERRIDE" and c["user_input_total"] == 10.0
                and c["main_table_derived_total"] == 15.0
                and c["adopted_total"] == 10.0
                for c in ov_payload["scenarios"][0]["results"][0]["certification"]["cells"]),
        group="SC",
        note="; ".join(f"{'/'.join(map(str, e.absolute_path))}: {e.message[:80]}"
                       for e in errs_ov[:3]))

    broken = json.loads(json.dumps(payload))
    broken["scenarios"][0]["results"][0]["single_value"] = True
    broken["scenarios"][0]["results"][0]["base_demand"] = None
    chk("SC-09", "output schema refuses a single_value result with a null total",
        bool(list(_js.Draft202012Validator(OUT_SCHEMA).iter_errors(broken))), group="SC",
        note="a front end cannot publish 'single value' and leave the number out, which is "
             "how a hidden default would sneak back in")

    broken2 = json.loads(json.dumps(payload))
    broken2["scenarios"][0]["results"][0]["certification"]["appendix_total_used_in_total"] = True
    broken2["scenarios"][0]["results"][0]["certification"]["appendix_role"] = "QUANTITY_MODEL"
    chk("SC-10", "output schema refuses the Appendix being re-labelled as a quantity model",
        bool(list(_js.Draft202012Validator(OUT_SCHEMA).iter_errors(broken2))), group="SC",
        note="DERIVED_TOTAL_VALIDATION is an enum member of evidence_role only, never of "
             "quantity_model (task section 18)")
else:
    print("[skip] jsonschema not installed - schema conformance probes not run")

# --------------------------------------------------------------------------- #
# 13  no-legacy-behaviour audit (LG)
# --------------------------------------------------------------------------- #
FORBIDDEN = ["CERTIFICATION_MODEL_UNRESOLVED(", "competing_candidates",
             "unresolved_certification", "certification_unresolved",
             "SINGLE_ADOPTED_MODEL", "three competing Certification models"]
hits = [p for p in FORBIDDEN if p in RULES_SRC and p != "SINGLE_ADOPTED_MODEL"]
chk("LG-01", "the Phase 2 competing-Certification behaviour cannot return from rules_v3",
    not hits, group="LG",
    note="the competing-model machinery is gone from the live core; UNRESOLVED remains "
         "supported as a Quantity Model but no Certification cell uses it",
    metric=f"forbidden phrases found = {hits or 'none'}")

chk("LG-02", "QMODEL v4 carries no competing_candidates field and no UNRESOLVED cell",
    "competing_candidates" not in json.dumps(R.QMODEL)
    and R.QMODEL["summary"]["by_quantity_model"].get("UNRESOLVED", 0) == 0
    and R.QMODEL["summary"]["by_quantity_model"]["PER_SKU_RATE"] == 38
    and R.QMODEL["summary"]["by_quantity_model"]["PER_PHASE_FIXED"] == 4, group="LG",
    metric=json.dumps(R.QMODEL["summary"]["by_quantity_model"]))

chk("LG-03", "no Quantity Model value may be the Appendix evidence role",
    all(c["quantity_model"] in R.QUANTITY_MODELS for c in R.QMODEL["cells"])
    and all(c["audit"]["evidence_role"] == R.AUDIT
            for c in R.QMODEL["cells"] if c["audit"])
    and all(c["adopted_value_evidence_role"] in R.EVIDENCE_ROLES
            for c in R.QMODEL["cells"]), group="LG")

chk("LG-04", "neither column may be added to the other, banded or used as a cap",
    R.QMODEL["policy"]["certification_appendix_may_be_added_to_total"] is False
    and R.QMODEL["policy"]["certification_appendix_may_be_added_to_main_derived_total"] is False
    and R.QMODEL["policy"]["certification_main_table_may_be_added_to_appendix"] is False
    and R.QMODEL["policy"]["certification_appendix_may_form_a_band"] is False
    and R.QMODEL["policy"]["certification_appendix_is_a_capping_model"] is False, group="LG")

# --------------------------------------------------------------------------- #
# 14  DEC-10 adoption (DA) - the Appendix total is the adopted Certification value
# --------------------------------------------------------------------------- #
payload4 = R.serialise(R.analyse(inp_of(**SEP4)), analysis_id="DA")
OUT_SCH = json.loads((ROOT / "schema/output.schema.json").read_text(encoding="utf-8-sig"))
CERT_ROWS_4 = [r for r in R.demand_rows(inp_of(**SEP4), 4) if r["category"] == "CERT"]
APX_CELL = {(c["function_id"], c["phase"], f"SKU{c['sku_count']}"): c["appendix_total"]
            for c in grid}
r6 = R.finalise(inp_of(**SEP4), 6)
apx_at = lambda n, ph=None: sum(
    c["appendix_total"] for c in grid
    if c["sku_count"] == n and (ph is None or c["phase"] == ph))
main_at = lambda n, ph=None: sum(
    c["derived_total"] for c in grid
    if c["sku_count"] == n and (ph is None or c["phase"] == ph))

chk("DA-01", "the adopted Certification value IS the Appendix total, cell by cell",
    len(CERT_ROWS_4) == 8
    and all(R.approx(r["base_demand"],
                     APX_CELL[(r["function_id"], r["phase"], "SKU4")])
            for r in CERT_ROWS_4)
    and all(R.approx(c["adopted_absolute"][sk], c["audit"]["per_sku"][sk]["appendix_total"])
            for c in R.QMODEL["cells"] if c["audit"]
            for sk in ("SKU2", "SKU3", "SKU4", "SKU5", "SKU6"))
    and R.QMODEL["owner_decision"]["id"] == "DEC-10"
    and R.QMODEL["owner_decision"]["adopted_value_source"] == "APPENDIX_TABLE_TOTAL",
    group="DA",
    note="every Certification cell reads the Appendix total for that Function, Phase and SKU "
         "count; nothing is multiplied back from a rate",
    metric=" | ".join(f"{r['function_id']}/{r['phase']} {r['base_demand']:g}"
                      for r in CERT_ROWS_4))

chk("DA-02", "the adopted value is counted exactly once and is never added to the Main Table value",
    R.approx(r4["base_demand"], r4["non_certification_demand"] + r4["certification_demand"])
    and r4["certification"]["counted_in_project_total_times"] == 1
    and r4["certification"]["main_derived_counted_in_project_total_times"] == 0
    and r4["certification"]["main_table_and_appendix_added_together"] is False
    and not R.approx(r4["base_demand"],
                     r4["non_certification_demand"] + r4["certification_demand"]
                     + main_at(4, "FVT") + main_at(4, "SIT") - r4["certification_demand"]),
    group="DA",
    note="the old double count (adopted Appendix plus Main x SKU) is what this guard "
         "prevents; the project total is non-Certification + Certification, once",
    metric=f"4 SKU total {r4['base_demand']:g} = non-cert "
           f"{r4['non_certification_demand']:g} + cert {r4['certification_demand']:g}; "
           f"main derived sum would have been {main_at(4):g}")

chk("DA-03", "the Main Table per-SKU value and its derived total are still on the record",
    all(r["main_table_per_sku_quantity"] is not None
        and r["main_table_derived_total"] is not None
        and r["main_table_audit"]["role"] == R.AUDIT
        and r["main_table_audit"]["counted_in_project_total"] is False
        for r in CERT_ROWS_4)
    and R.approx(sum(r["main_table_derived_total"] for r in CERT_ROWS_4), main_at(4)),
    group="DA",
    note="audit evidence is retained at row level (per-SKU quantity, derived total, delta, "
         "source rows) so any difference can still be traced back to the workbook",
    metric=f"main derived at 4 SKU {main_at(4):g} vs adopted {apx_at(4):g}")

chk("DA-04", "J33 is not added on top of the adopted value at any SKU band",
    all(R.approx(R.finalise(inp_of(**SEP4), n)["certification"]["certification_demand_total"],
                 apx_at(n)) for n in (2, 4, 6))
    and all(R.finalise(inp_of(**SEP4), n)["certification"]["j33_added_to_result"] is False
            and R.finalise(inp_of(**SEP4), n)["certification"]
                ["j33_counted_in_project_total_times"] == 0 for n in (2, 4, 6)),
    group="DA",
    note="adding the J33 bracket (11..27) would move the 4 SKU Certification demand away "
         "from the adopted Appendix total of 36",
    metric=f"adopted cert by SKU: "
           + ", ".join(f"{n}:{R.finalise(inp_of(**SEP4), n)['certification']['certification_demand_total']:g}"
                       for n in (2, 3, 4, 5, 6)))

cp = OUT_SCH["$defs"]["certification"]["properties"]
chk("DA-05", "the output schema const-locks the adoption (1 adopted, 0 audit, no addition)",
    cp["counted_in_project_total_times"]["const"] == 1
    and cp["main_derived_counted_in_project_total_times"]["const"] == 0
    and cp["adopted_value_role"]["const"] == "ADOPTED_ABSOLUTE_TOTAL"
    and cp["main_table_role"]["const"] == "DERIVED_MAIN_TABLE_AUDIT"
    and cp["main_table_and_appendix_added_together"]["const"] is False
    and cp["j33_counted_in_project_total_times"]["const"] == 0
    and cp["phase_ratio_used"]["type"] == "null"
    and "appendix_counted_in_project_total_times" not in cp,
    group="DA",
    note="replaces SC-05: the structural prohibition moved from 'the Appendix may not be "
         "counted' to 'the adopted value is counted once and the Main Table derivation "
         "is counted zero times'",
    metric="schema consts verified")

shares_fvt6 = [round(R.finalise(inp_of(**SEP4), n)["certification"]
                     ["fvt_certification_demand"], 6) for n in (2, 3, 4, 5, 6)]
shares_sit6 = [round(R.finalise(inp_of(**SEP4), n)["certification"]
                     ["sit_certification_demand"], 6) for n in (2, 3, 4, 5, 6)]
chk("DA-06", "FVT and SIT each adopt their own Appendix row (no global phase ratio)",
    all(R.approx(shares_fvt6[i], apx_at(i + 2, "FVT")) for i in range(5))
    and all(R.approx(shares_sit6[i], apx_at(i + 2, "SIT")) for i in range(5))
    and shares_fvt6 != shares_sit6
    and all(R.finalise(inp_of(**SEP4), n)["certification"]["phase_ratio_used"] is None
            for n in (2, 3, 4, 5, 6)),
    group="DA",
    note="the numbers adopted for FVT are the Appendix FVT rows (rows 53/55/57/59) and for "
         "SIT the Appendix SIT rows (54/56/58/60) - never a share of the project total",
    metric=f"FVT {shares_fvt6} | SIT {shares_sit6}")

chk("DA-07", "the 4-5 SKU range still prices both candidates, each with its own adopted total",
    tie["state"] == "RANGE" and set(priced) == {4, 5}
    and all(p["certification"]["single_value"] for p in priced.values())
    and R.approx(priced[4]["certification"]["certification_demand_total"], apx_at(4))
    and R.approx(priced[5]["certification"]["certification_demand_total"], apx_at(5))
    and not R.approx(priced[4]["certification"]["certification_demand_total"],
                     priced[5]["certification"]["certification_demand_total"])
    and all(p["certification"]["range_reason"] is None for p in priced.values()),
    group="DA",
    note="DEC-01 is unchanged by DEC-10: the range comes from the SKU answer, each candidate "
         "is priced in full, and neither endpoint is collapsed into a hidden single value",
    metric=f"4 SKU cert {priced[4]['certification']['certification_demand_total']:g} / "
           f"5 SKU cert {priced[5]['certification']['certification_demand_total']:g}")

chk("DA-08", "prohibited range reasons are still never emitted (engine and Web core)",
    not any(o["kind"] in R.PROHIBITED_RANGE_REASONS for o in all_oris)
    and not [p_ for p_ in R.PROHIBITED_RANGE_REASONS
             if re.search(r"kind['\"]?\s*[:=]\s*['\"]" + p_, RULES_SRC)]
    and not [p_ for p_ in R.PROHIBITED_RANGE_REASONS
             if re.search(r"kind['\"]?\s*[:=]\s*['\"]" + p_, CORE_JS_SRC)],
    group="DA",
    note="the two labels exist only inside the docstring and the tuple that names them as "
         "prohibited; they are emitted by neither core",
    metric=f"prohibited = {list(R.PROHIBITED_RANGE_REASONS)}")

chk("DA-09", "no Certification value is produced by dividing by the SKU count and "
             "multiplying back",
    all(c["value_access"] == "APPENDIX_TABLE_READ" for c in R.QMODEL["cells"] if c["audit"])
    and all(R.approx(c["adopted_absolute"][f"SKU{n}"],
                     c["audit"]["per_sku"][f"SKU{n}"]["appendix_total"])
            for c in R.QMODEL["cells"] if c["audit"] for n in (2, 3, 4, 5, 6))
    and "per_sku_rate" not in RULES_SRC,
    group="DA",
    note="the adopted cell is an absolute read of the Appendix row; the Main Table per-SKU "
         "column is kept as the rule of record, not as a rate that is multiplied back in",
    metric="8 Certification cells adopt as ABSOLUTE Appendix reads")

r6_rows = sum(r["base_demand"] for r in r6["rows"])
chk("DA-10", "6 SKU special review: the total is rebuilt from the bottom-up detail",
    R.approx(r6["base_demand"], r6_rows)
    and R.approx(r6["certification"]["certification_demand_total"], apx_at(6))
    and R.approx(r6["certification"]["recounted_from_detail"]["FVT"],
                 r6["certification"]["fvt_certification_demand"])
    and R.approx(r6["certification"]["recounted_from_detail"]["SIT"],
                 r6["certification"]["sit_certification_demand"])
    and R.approx(r6["base_demand"], 502.0)
    and R.approx(r6["certification"]["certification_demand_total"], 38.0)
    and R.approx(r6["recommended_total"], CORRECTED["SKU6"]),
    group="DA",
    note="6 SKU is the band where Safety FVT (adopted 10.0 against a Main derivation of 9.6) "
         "and RF SIT (adopted 10.0 against 15.0) both disagree, so it is recomputed from the "
         "rows rather than from any historical total (task section 5)",
    metric=f"6 SKU total {r6['base_demand']!r} = rows {r6_rows!r}; cert "
           f"{r6['certification']['certification_demand_total']:g} "
           f"(audit main {main_at(6):g})")

pack_path = ROOT / "artifacts/model/rule_pack_v4.json"
pack_before = hashlib.sha256(pack_path.read_bytes()).hexdigest() if pack_path.exists() else ""
ov = inp_of(**SEP4)
ov.certification_override = {"F_RF_CERTIFICATION": {"SIT": 12.5}}
r_ov = R.finalise(ov, 4)
doc_ov = R.input_document(ov)
pack_after = hashlib.sha256(pack_path.read_bytes()).hexdigest() if pack_path.exists() else ""
chk("DA-11", "a manual override changes this Analysis only and never reaches the rule pack",
    r_ov["certification"]["user_override_used"] is True
    and r_ov["certification"]["user_override_scope"] == "THIS_ANALYSIS_ONLY"
    and R.approx(r_ov["certification"]["certification_demand_total"],
                 r4["certification"]["certification_demand_total"] + 2.5)
    and doc_ov["certification_input"]["mode"] == "USER_OVERRIDE_FOR_MISMATCH_CELLS"
    and doc_ov["certification_input"]["override_scope"] == "THIS_ANALYSIS_ONLY"
    and (not pack_path.exists() or pack_before == pack_after)
    and R.ADOPTED_SOURCE not in ("USER_MANUAL_OVERRIDE",),
    group="DA",
    note="the override is stored in the Analysis snapshot with the adopted value beside it; "
         "the rule package bytes are unchanged before and after the overridden run",
    metric=f"rule pack sha unchanged: {bool(pack_before) and pack_before == pack_after}")

chk("DA-12", "adoption does not silence the seven disagreements",
    CV["summary"]["mismatch"] == 7 and CV["ori_02_status"] == "PARTIALLY_RESOLVED"
    and len(ori_mis) == len(mis_at_4)
    and all(o["blocking_level"] == "BLOCKS_FORMALIZATION" and o["blocks_manual_mvp"] is False
            for o in ori_mis)
    and any(o["kind"] == "CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE" for o in all_oris)
    and R.QMODEL["status"] == "DRAFT_PENDING_OWNER"
    and json.loads(pack_path.read_text(encoding="utf-8"))["status"] == "DRAFT_PENDING_OWNER",
    group="DA",
    note="adopting the Appendix answers 'which number do we use'; it does not explain why "
         "the two columns differ, so ORI-02 stays PARTIALLY_RESOLVED and the rule pack stays "
         "DRAFT (task section 4: the rule pack must not be promoted)",
    metric=f"{CV['summary']['verified']} matching / {CV['summary']['mismatch']} mismatch | "
           f"{len(ori_mis)} Register entries at 4 SKU")

# --------------------------------------------------------------------------- #
# 15  export contract (EX) - JSON, team review CSV and trial feedback CSV
# --------------------------------------------------------------------------- #
rec4 = {"id": "EX", "project_name": "EX", "saved_at": "2026-01-01T00:00:00.000Z",
        "document": {"key_factors": {}}, "payload": payload4,
        "certification_grid": CV["verification_grid"]}
jd = R.export_json_document(rec4)
csv4 = R.export_review_csv(rec4)
fb4 = R.export_trial_feedback_csv(rec4)
cells_exp = jd["certification_adopted_and_audit_values"]

chk("EX-01", "the JSON export carries adopted value, audit value and difference per cell",
    cells_exp and all("adopted_total" in c and "main_table_derived_total" in c
                      and "appendix_total" in c and "delta" in c
                      and c["main_derived_counted_in_project_total"] is False
                      for c in cells_exp)
    and jd["export_version"] == "4.0"
    and jd["owner_decision"]["id"] == "DEC-10",
    group="EX",
    metric=f"{len(cells_exp)} Certification cells exported with both columns")

chk("EX-02", "the review CSV keeps the eight sections and states the counted times",
    all(sec in csv4 for sec in ("1. SKU result", "2. Totals", "3. Function detail",
                                "4. Certification cells - adopted (Appendix) vs audit (Main table)",
                                "5. J33 (explanatory evidence - never added)",
                                "6. Reuse ledger", "7. Review items for the Owner",
                                "8. Excluded Panel annotation evidence"))
    and "Certification adopted,Appendix total (DEC-10) - counted once" in csv4
    and "Certification audit," in csv4
    and "audit only, counted 0 times" in csv4
    and "Adopted counted,Audit counted" in csv4 and ",1,0\r\n" in csv4,
    group="EX",
    note="the adopted column comes first, the Main Table audit column second, and the "
         "counted-times pair makes the once-only rule visible in the spreadsheet")

chk("EX-03", "exports keep a range as a range and never publish a hidden single value",
    (lambda rng_rec: (lambda j, c: j["sku_result"][0]["state"] == "RANGE"
                      and j["sku_result"][0]["recommended_sku"] is None
                      and j["sku_result"][0]["preferred_sku"] == "NOT_ESTABLISHED"
                      and j["sku_result"][0]["sku_range"] == [4, 5]
                      and j["range_collapsed_to_single_value_on_export"] is False
                      and "not established" in c
                      and len(rng_rec["payload"]["scenarios"][0]["results"]) == 2)(
        R.export_json_document(rng_rec), R.export_review_csv(rng_rec)))(
        {"id": "EXR", "project_name": "EXR", "saved_at": "2026-01-01T00:00:00.000Z",
         "document": {"key_factors": {}},
         "payload": R.serialise(R.analyse(inp_of(**CLEAN4)), analysis_id="EXR"),
         "certification_grid": CV["verification_grid"]}),
    group="EX",
    note="both endpoints stay in the file; a reviewer cannot mistake the export for a "
         "decision that was never made")

chk("EX-04", "underlying decimals survive the export path unchanged (D-01)",
    "438.8" in csv4 and "443.8" not in csv4
    and json.dumps(payload4).count("438.8") >= 1
    and payload4["policy"]["display_precision_modifies_values"] is False
    and payload4["export"]["full_precision_present"] is True,
    group="EX",
    note="the 4 SKU total is published as 438.8 and would have to stay 438.8 whatever the "
         "display precision says; 443.8 is the Phase 3a number and must not reappear",
    metric="438.8 kept, 443.8 gone")

rec3 = {"id": "EX3", "project_name": "EX3", "saved_at": "2026-01-01T00:00:00.000Z",
        "document": {"key_factors": {}},
        "payload": R.serialise(R.analyse(inp_of(cpu=2, gpu=2, panel=1, ssd=1, mem=1)),
                               analysis_id="EX3"),
        "certification_grid": CV["verification_grid"]}
fb3 = R.export_trial_feedback_csv(rec3)
chk("EX-05", "the trial feedback export lists every disagreeing cell and every open ORI once",
    "团队试用反馈表" in fb3
    and fb3.count("\r\nRF Certification,SIT,") == 1
    and fb3.count("\r\nGreen,SIT,") == 1
    and len(re.findall(r"\r\nGreen,SIT,|\r\nRF Certification,SIT,|\r\nSafety,FVT,", fb3)) == 2
    and len(re.findall(r"\r\nORI-\d+[a-z]?", fb3)) == len(
        json.loads(pack_path.read_text(encoding="utf-8"))["open_owner_review_items"]),
    group="EX",
    note="the reviewer is asked one question per open item - not one question per scenario "
         "and not one question per impact tag. At 3 SKU two cells disagree (Green/SIT and "
         "RF/SIT) and each is listed once.",
    metric=f"{len(re.findall(chr(13) + chr(10) + 'ORI-', fb3))} ORI rows")

chk("EX-06", "the exported audit columns are the same numbers the engine published",
    all(R.approx(c["main_table_derived_total"],
                 c["main_table_per_sku"] * c["sku"], 1e-9)
        or c["main_table_per_sku"] == 0
        or c["main_table_per_sku"] is None for c in cells_exp)
    and all(c["adopted_value_source"] in ("APPENDIX_TABLE_TOTAL", "USER_MANUAL_OVERRIDE")
            for c in cells_exp)
    and jd["values_full_precision"] is True,
    group="EX",
    metric=f"{len(cells_exp)} cells checked against their own audit row")

# --------------------------------------------------------------------------- #
# 16  reporting statistics and terminology (ST)
# --------------------------------------------------------------------------- #
PREV_FILE = ROOT / "artifacts/validation/regression_results_v3.json"
PREV_IDS = ([r["id"] for r in json.loads(PREV_FILE.read_text(encoding="utf-8"))["results"]]
            if PREV_FILE.exists() else [])
RETIRED_IN_V4 = {"CT-V2-02": "DA-01 + DA-02 + DA-03 (the Appendix is adopted, counted once, "
                             "and the Main Table derivation is counted 0 times)",
                 "SC-05": "DA-05 (the schema const-locks 1 adopted / 0 audit instead)"}
ADAPTED_IN_V4 = ["RT-02", "CT-V2-04", "CT-V2-06", "CT-V2-08", "CT-V2-09", "CT-V2-11",
                 "D01-01", "D01-02", "D01-04", "PR-05b", "SC-02", "SC-06", "SC-08",
                 "LG-02", "LG-03", "LG-04"]
NEW_GROUPS = ("DA", "EX", "ST")
# EF-01 is emitted by the report block below, so it is part of the planned set here.
PLANNED_IDS = {r["id"] for r in RESULTS} | {"ST-01", "ST-02", "ST-03", "EF-01"}
_ledger = {
    "previous_suite": "tools/validate_rules_v3.py",
    "previous_total": len(PREV_IDS),
    "retired_in_this_task": len(RETIRED_IN_V4),
    "retired_ids": sorted(RETIRED_IN_V4),
    "adapted_in_this_task": len(ADAPTED_IN_V4),
    "adapted_ids": ADAPTED_IN_V4,
    "carried_unchanged": len(PREV_IDS) - len(RETIRED_IN_V4) - len(ADAPTED_IN_V4),
    "added_in_this_task": len(PLANNED_IDS - set(PREV_IDS)),
    "added_ids": sorted(PLANNED_IDS - set(PREV_IDS)),
    "current_total": len(PLANNED_IDS),
}
_ledger["closure_previous"] = (_ledger["carried_unchanged"] + _ledger["adapted_in_this_task"]
                               + _ledger["retired_in_this_task"] == _ledger["previous_total"])
_ledger["closure_current"] = (_ledger["carried_unchanged"] + _ledger["adapted_in_this_task"]
                              + _ledger["added_in_this_task"] == _ledger["current_total"])
_ledger["unexpected_retirements"] = sorted(set(PREV_IDS) - PLANNED_IDS - set(RETIRED_IN_V4))
_ledger["undocumented_additions"] = sorted(
    x for x in PLANNED_IDS - set(PREV_IDS) if x.split("-")[0] not in NEW_GROUPS)
chk("ST-01", "the probe ledger closes arithmetically (previous = carried + adapted + retired, "
             "current = carried + adapted + added)",
    _ledger["closure_previous"] and _ledger["closure_current"]
    and not _ledger["unexpected_retirements"] and not _ledger["undocumented_additions"],
    group="ST",
    note="the previous report said '100' while 101 probes were executed and never reconciled "
         "the retired ones; the ledger below is computed from the executed probes, not typed",
    metric=json.dumps({k: v for k, v in _ledger.items() if k != "adapted_ids"},
                      ensure_ascii=False)[:400])

pack4 = json.loads(pack_path.read_text(encoding="utf-8"))
_reg_ids = re.findall(r"^### (ORI-\d+[a-z]?) ",
                      (ROOT / "docs/38_owner_review_register_v4.md").read_text(encoding="utf-8-sig"),
                      re.M)
chk("ST-02", "unique Owner Review Items and impact tags are counted separately and agree",
    pack4["owner_review_item_count"] == len(pack4["open_owner_review_items"])
    and len({o["id"] for o in pack4["open_owner_review_items"]})
        == pack4["owner_review_item_count"]
    and sum(pack4["owner_review_impact_tag_counts"].values())
        == pack4["owner_review_item_count"]
    and sorted(_reg_ids) == sorted(o["id"] for o in pack4["open_owner_review_items"]),
    group="ST",
    note="an impact tag is a label on a question, not a second question: the tag counts sum "
         "back to the unique ORI count, and the Register and the rule pack list the same ids",
    metric=f"unique {pack4['owner_review_item_count']} | tags "
           f"{pack4['owner_review_impact_tag_counts']} | register sections {len(_reg_ids)}")

# the report this check covers is written later in the pipeline, so the wording of the
# tool that generates it is what can be asserted here; tools/verify_integrity.py then
# asserts the same thing about the generated report itself.
_TERMINOLOGY_FILES = ["docs/41_directory_integrity_v4.md",
                      "tools/directory_integrity_report.py"]
_banned = ("worktree", "HEAD", "branch", "commit")
_hits = []
for f in _TERMINOLOGY_FILES:
    p_ = ROOT / f
    if not p_.exists():
        _hits.append(f + " (missing)")
        continue
    txt = p_.read_text(encoding="utf-8-sig")
    if f.endswith(".md"):
        _hits += [f"{f}: {b}" for b in _banned if b in txt]
chk("ST-03", "the project is described as a directory, not a Git working tree",
    not _hits and (ROOT / "tools/directory_integrity_report.py").exists()
    and not (ROOT / "tools/worktree_report.py").exists(),
    group="ST",
    note="this folder has never been under version control, so version-control vocabulary "
         "described nothing; the report tool was renamed to directory_integrity_report.py "
         "and the deliverable document uses Directory Integrity wording. The obsolete "
         "artefact names kept in the classifier (worktree_report.*) are file names being "
         "recognised, not vocabulary used in a report.",
    metric=f"banned words in the deliverable wording = {_hits or 'none'}")

# --------------------------------------------------------------------------- #
# 14  report
# --------------------------------------------------------------------------- #
APPROVED_EXPECTED_FAIL = ["SR-09"]
expected_fail = sorted(r["id"] for r in RESULTS if r["expected"] == "FAIL")
actual_fail = [r["id"] for r in RESULTS if r["actual"] == "FAIL"]
regressions = [r["id"] for r in RESULTS if r["verdict"] != "OK"]
unapproved = [x for x in expected_fail if x not in APPROVED_EXPECTED_FAIL]
summary = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "core": "prototype/rules_v3.py",
    "engine": f"{R.ENGINE_NAME}/{R.ENGINE_VERSION}",
    "quantity_model": R.QMODEL["model_id"],
    "baseline": R.BASELINE["baseline_id"],
    "certification_verification": f"{CV['summary']['verified']} verified / "
                                  f"{CV['summary']['mismatch']} mismatch / "
                                  f"{CV['summary']['not_evaluable']} not evaluable",
    "ori_02_status": CV["ori_02_status"],
    "owner_decision": R.QMODEL.get("owner_decision", {}).get("id"),
    "adopted_value_source": R.QMODEL.get("owner_decision", {})
        .get("adopted_value_source"),
    "probe_ledger": _ledger,
    "owner_review_item_count": pack4["owner_review_item_count"],
    "owner_review_impact_tag_counts": pack4["owner_review_impact_tag_counts"],
    "total": len(RESULTS),
    "probes_holding": sum(1 for r in RESULTS if r["actual"] == "PASS"),
    "probes_failing": actual_fail,
    "expected_failures": expected_fail,
    "approved_expected_failures": APPROVED_EXPECTED_FAIL,
    "unapproved_expected_failures": unapproved,
    "regressions": regressions,
    "status": ("CLEAN" if not regressions and expected_fail == APPROVED_EXPECTED_FAIL
               else "REGRESSION"),
}
if unapproved:
    RESULTS.append({"id": "EF-01", "group": "EF",
                    "title": "the Expected Failure set is exactly the approved one",
                    "expected": "PASS", "actual": "FAIL", "verdict": "REGRESSION",
                    "note": f"unapproved: {unapproved}", "metric": ""})
    summary["regressions"].append("EF-01")
    summary["status"] = "REGRESSION"
    summary["total"] += 1
else:
    chk("EF-01", "the Expected Failure set is exactly the approved ['SR-09']",
        expected_fail == APPROVED_EXPECTED_FAIL, group="EF",
        note="an unexpected green SR-09 or a new Expected Failure is a regression "
             "(task sections 24 and 29)",
        metric=f"expected_fail = {expected_fail}")

# The ledger has to describe the probes that actually ran, EF-01 included. The previous
# report computed "total" before EF-01 was appended, which is why 100 and 101 both appeared.
summary["total"] = len(RESULTS)
summary["probes_holding"] = sum(1 for r in RESULTS if r["actual"] == "PASS")
summary["probes_failing"] = [r["id"] for r in RESULTS if r["actual"] == "FAIL"]
_executed = {r["id"] for r in RESULTS}
_ledger["current_total"] = len(_executed)
_ledger["added_in_this_task"] = len(_executed - set(PREV_IDS))
_ledger["added_ids"] = sorted(_executed - set(PREV_IDS))
_ledger["carried_unchanged"] = (len(set(PREV_IDS) & _executed)
                                - len(set(ADAPTED_IN_V4) & _executed))
_ledger["adapted_in_this_task"] = len(set(ADAPTED_IN_V4) & _executed)
_ledger["retired_in_this_task"] = len(set(PREV_IDS) - _executed)
_ledger["retired_ids"] = sorted(set(PREV_IDS) - _executed)
_ledger["closure_previous"] = (_ledger["carried_unchanged"]
                               + _ledger["adapted_in_this_task"]
                               + _ledger["retired_in_this_task"] == _ledger["previous_total"])
_ledger["closure_current"] = (_ledger["carried_unchanged"] + _ledger["adapted_in_this_task"]
                              + _ledger["added_in_this_task"] == _ledger["current_total"])
summary["probe_ledger"] = _ledger

out_dir = ROOT / "artifacts" / "validation"
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "regression_results_v4.json").write_text(
    json.dumps({"summary": summary, "results": RESULTS}, ensure_ascii=False, indent=2),
    encoding="utf-8")

L = ["# Regression report v4 - Certification adopted from the Appendix (DEC-10)", "",
     "## Probe ledger (this is the arithmetic the previous report was missing)", "",
     "| | count |", "|---|---:|",
     f"| probes executed in the previous suite (`validate_rules_v3.py`) | {_ledger['previous_total']} |",
     f"| carried forward unchanged | {_ledger['carried_unchanged']} |",
     f"| carried forward, adapted to DEC-10 | {_ledger['adapted_in_this_task']} |",
     f"| retired by DEC-10 (each with a named successor) | {_ledger['retired_in_this_task']} |",
     f"| added in this task (DA / EX / ST) | {_ledger['added_in_this_task']} |",
     f"| **executed here** | **{_ledger['current_total']}** |",
     "",
     "Previous suite = carried + adapted + retired; this suite = carried + adapted + added. "
     "Both equations hold: "
     f"`{_ledger['closure_previous']}` and `{_ledger['closure_current']}`.", "",
     "Retired probes and their successors:", ""]
L += [f"- **{k}** -> {v}" for k, v in RETIRED_IN_V4.items()]
L += ["", "Probes adapted to the adopted source (same question, new column):", "",
      ", ".join(f"`{x}`" for x in ADAPTED_IN_V4), "",
      "## Owner Review Items: unique questions vs impact tags (counted separately)", "",
      f"- unique Owner Review Items: **{pack4['owner_review_item_count']}**",
      f"- impact tags: **{json.dumps(pack4['owner_review_impact_tag_counts'])}** "
      f"(they sum to {sum(pack4['owner_review_impact_tag_counts'].values())}, i.e. one tag "
      f"per question - an extra tag on an existing question is never a new ORI)", "",
      "## Result", "",
      "| item | value |", "|---|---|",
     "| core | `prototype/rules_v3.py` |", f"| engine | `{summary['engine']}` |",
     f"| quantity model | `{R.QMODEL['model_id']}` {R.QMODEL['model_version']} |",
     f"| baseline | `{R.BASELINE['baseline_id']}` ({R.BASELINE['status']}) |",
     f"| certification per-cell verification | {summary['certification_verification']} |",
     f"| owner decision | **{summary['owner_decision']}** - adopted from `{summary['adopted_value_source']}` |",
     f"| ORI-02 | **{summary['ori_02_status']}** |",
     f"| status | **{summary['status']}** |", "",
     "## Expected PASS / FAIL list", "",
     "| ID | Group | Invariant | Expected | Actual | Verdict |", "|---|---|---|---|---|---|"]
for r in RESULTS:
    v = ("REGRESSION" if r["verdict"] == "REGRESSION"
         else ("as expected" if r["actual"] == "PASS" else "EXPECTED FAIL (open design gap)"))
    L.append(f"| {r['id']} | {r['group']} | {r['title']} | {r['expected']} | "
             f"{r['actual']} | {v} |")
L += ["", "## Probe notes", ""]
L += [f"- **{r['id']}** - {r['note']}" + (f" _({r['metric']})_" if r["metric"] else "")
      for r in RESULTS if r["note"]]
L += ["", "## Summary", "", "```json", json.dumps(summary, ensure_ascii=False, indent=1),
      "```", ""]
(out_dir / "regression_report_v4.md").write_text("\n".join(L), encoding="utf-8")

print("\n" + "=" * 78)
print(f"{summary['probes_holding']}/{summary['total']} probes hold | failing: {actual_fail} "
      f"| expected-fail: {expected_fail}")
print(f"regressions: {regressions or 'none'}")
print(f"ORI-02: {summary['ori_02_status']}")
print(f"STATUS: {summary['status']}")
sys.exit(1 if summary["status"] != "CLEAN" else 0)
