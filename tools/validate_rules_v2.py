#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression harness for rules_v2 (manual-input MVP calculation core).

Every invariant carries an Owner-approved EXPECTED outcome. The harness reports:
  * probe result            - did the invariant hold
  * verdict                 - OK, or REGRESSION when the probe disagreed with expectation

A designed-failure probe (ORI-04) is expected="FAIL". It is never deleted, softened
or re-labelled to make the suite green.
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "prototype"))

import rules_v2 as R                                            # noqa: E402

RESULTS: list[dict] = []
RULES_SRC = (ROOT / "prototype" / "rules_v2.py").read_text(encoding="utf-8")


def chk(cid, title, cond, expected="PASS", note="", metric=""):
    actual = "PASS" if cond else "FAIL"
    verdict = "OK" if ((actual == "PASS") == (expected == "PASS")) else "REGRESSION"
    RESULTS.append({"id": cid, "title": title, "expected": expected, "actual": actual,
                    "verdict": verdict, "note": note, "metric": metric})
    print(("[PASS] " if actual == "PASS" else "[FAIL] ") + f"{cid:8} {title}"
          + (f"   {metric}" if metric else "")
          + ("" if verdict == "OK" else f"   <<< REGRESSION (expected {expected})"))


def mk(cpu=None, gpu=None, panel=None, ssd=None, mem=None, **kw):
    """plain manual-input fixture: file_value stands in for a confirmed entered value"""
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
    """first (MAIN_TABLE) variant total of a finalise() result"""
    return res_entry["totals_by_model"]["variants"][0]


def variant(res_entry, source="MAIN_TABLE"):
    for v in res_entry["totals_by_model"]["variants"]:
        if v["model_source"] == source:
            return v
    return None


GOLDEN = {"SKU2": 365.0, "SKU3": 417.0, "SKU4": 443.8, "SKU5": 474.0, "SKU6": 507.0}
CLEAN4 = dict(cpu=3, gpu=3, panel=2, ssd=2, mem=2)      # 4 SKU / 5 SKU tie
SEP4 = dict(cpu=3, gpu=2, panel=2, ssd=2, mem=2)        # 4 SKU only

# --------------------------------------------------------------------------- #
# 1  baseline replay
# --------------------------------------------------------------------------- #
replay = {f"SKU{n}": sum(c["main_table_absolute"][f"SKU{n}"] for c in R.QMODEL["cells"])
          for n in (2, 3, 4, 5, 6)}
chk("RT-01", "workbook grand totals still reproduce from the derived cells",
    all(R.approx(replay[k], GOLDEN[k]) for k in GOLDEN),
    note="raw Main Table read - proves the extraction -> baseline -> quantity model "
         "chain is intact and nothing was hand-edited",
    metric=json.dumps({k: round(v, 4) for k, v in replay.items()}))

# --------------------------------------------------------------------------- #
# 2  Quantity Model (DEC-05)
# --------------------------------------------------------------------------- #
Q = {(c["function_id"], c["phase"]): c for c in R.QMODEL["cells"]}

chk("QM-01", "MEPA and HW PA are PER_PHASE_FIXED candidates, not pseudo rates",
    all(Q[("F_MEPA", p)]["quantity_model"] == "PER_PHASE_FIXED" for p in ("FVT", "SIT"))
    and all(Q[("F_HW_PA", p)]["quantity_model"] == "PER_PHASE_FIXED" for p in ("FVT", "SIT")),
    note="evidence: absolute restatement rows 70/71 are constant across SKU2-6 for MEPA; "
         "rows 72/73 are integer-valued and disagree with rate x SKU for HW PA")

chk("QM-02", "the engine performs no divide-by-SKU-then-multiply-back anywhere",
    "per_sku_rate" not in RULES_SRC and "ttl_per_phase" not in RULES_SRC,
    note="rules_v2 reads adopted_absolute straight from the Quantity Model table",
    metric="no per_sku_rate / ttl_per_phase reference in rules_v2.py")

chk("QM-03", "MEPA absolute is 36.0 at every SKU (Main Table said 32.0 at SKU2)",
    all(R.approx(Q[("F_MEPA", p)]["adopted_absolute"][f"SKU{n}"], 36.0)
        for p in ("FVT", "SIT") for n in (2, 3, 4, 5, 6))
    and R.approx(Q[("F_MEPA", "FVT")]["main_table_absolute"]["SKU2"], 32.0),
    note="the Main Table value is retained as competing evidence, not merged away",
    metric="adopted 36.0 / main 32.0 at SKU2")

chk("QM-04", "HW PA absolute at 6 SKU is 4.0, the pseudo-rate 4.2 is kept as evidence",
    all(R.approx(Q[("F_HW_PA", p)]["adopted_absolute"]["SKU6"], 4.0) for p in ("FVT", "SIT"))
    and all(R.approx(Q[("F_HW_PA", p)]["main_table_absolute"]["SKU6"], 4.2) for p in ("FVT", "SIT")),
    note="D-01: 4.2 is not rounded away, it is reported as the competing Main Table value")

chk("QM-05", "a flat derived total is NOT promoted to PER_PHASE_FIXED on shape alone",
    R.QMODEL["summary"]["by_quantity_model"].get("PER_PHASE_FIXED", 0) == 4
    and len(R.QMODEL["model_questions"]) == 6
    and {q["function_id"] for q in R.QMODEL["model_questions"]} == {"F_EMC_TEST", "F_NV", "F_INTEL"},
    note="EMC Test / NV / INTEL stay PER_SKU_RATE and are raised as model questions "
         "(candidate_models both listed) instead of being silently re-modelled",
    metric=f"{len(R.QMODEL['model_questions'])} model questions")

chk("QM-06", "every demand line states which Quantity Model produced it",
    {r["quantity_model"] for r in R.demand_rows(inp_of(**SEP4), 4)} <= set(R.QUANTITY_MODELS)
    and {r["function_id"]: r["quantity_model"]
         for r in R.demand_rows(inp_of(**SEP4), 4) if r["function_id"] == "F_MEPA"}
    == {"F_MEPA": "PER_PHASE_FIXED"})

chk("QM-07", "the adopted value always carries its provenance",
    all(r["value_source"] == "SECONDARY_ABSOLUTE_TABLE"
        for r in R.demand_rows(inp_of(**SEP4), 4) if r["function_id"] in ("F_MEPA", "F_HW_PA"))
    and all(r["value_source"] == "MAIN_TABLE"
            for r in R.demand_rows(inp_of(**SEP4), 4) if r["function_id"] == "F_HW"))

chk("QM-08", "PER_PROJECT_FIXED and FORMULA_DRIVEN are supported by the contract",
    set(R.QUANTITY_MODELS) == {"PER_SKU_RATE", "PER_PHASE_FIXED", "PER_PROJECT_FIXED",
                               "FORMULA_DRIVEN", "UNRESOLVED"}
    and set(R.QMODEL["quantity_model_enum"]) == set(R.QUANTITY_MODELS),
    note="PER_PROJECT_FIXED currently has no member; FORMULA_DRIVEN appears only as the "
         "non-evaluable J33 candidate on RF Certification")

# --------------------------------------------------------------------------- #
# 3  Certification competing models (DEC-03)
# --------------------------------------------------------------------------- #
r4 = R.finalise(inp_of(**CLEAN4), 4)
cert = r4["certification_unresolved"]

chk("CT-01", "all 8 Certification cells stay UNRESOLVED and OWNER_REVIEW_REQUIRED",
    len(cert) == 8 and all(c["status"].startswith("UNRESOLVED") for c in cert)
    and all(rr["owner_review_required"] for rr in r4["rows"] if rr["category"] == "CERT"),
    metric=f"{len(cert)} cells")

chk("CT-02", "nothing is auto-selected: the whole demand is priced once per model",
    {v["model_source"] for v in r4["totals_by_model"]["variants"]} ==
    {"MAIN_TABLE", "SECONDARY_TABLE"},
    metric=json.dumps({v["model_source"]: round(v["TOTAL"], 3)
                       for v in r4["totals_by_model"]["variants"]}))

chk("CT-03", "the competing models produce a band, never a merged or averaged number",
    not R.approx(r4["totals_by_model"]["band"]["total_min"],
                 r4["totals_by_model"]["band"]["total_max"])
    and "avg" not in json.dumps(r4["totals_by_model"]).lower()
    and r4["recommended_total"] is None and r4["recommended_total_band"]["exact"] is False,
    metric=f"band {r4['totals_by_model']['band']['total_min']:g} .. "
           f"{r4['totals_by_model']['band']['total_max']:g} "
           f"(spread {r4['totals_by_model']['band']['spread']:g})")

chk("CT-04", "J33 formula is kept as evidence but marked not evaluable",
    "J33_FORMULA" in r4["totals_by_model"]["variants_not_evaluable"]
    and any(c["models"].get("J33_FORMULA") is None for c in cert),
    note="required inputs (antenna source / WLAN card counts) are not MVP key factors - "
         "the formula is neither dropped nor silently substituted")

ov = R.finalise(inp_of(certification_override={"F_RF_CERTIFICATION": {"SIT": 10.0}}, **CLEAN4), 4)
chk("CT-05", "manual Certification override is accepted and labelled USER_MANUAL_OVERRIDE",
    any(rr["function_id"] == "F_RF_CERTIFICATION" and rr["phase"] == "SIT"
        and rr["value_source"] == "USER_MANUAL_OVERRIDE" and R.approx(rr["base_demand"], 10.0)
        and not rr["owner_review_required"] for rr in ov["rows"]),
    note="the MVP keeps an entry point for hand-entered Certification quantities")

shares = []
for n in (2, 3, 4, 5, 6):
    t = variant(R.finalise(inp_of(**SEP4), n))
    if t and t["TOTAL"]:
        shares.append(round(t["FVT"] / t["TOTAL"], 6))
chk("CT-06", "FVT / SIT split is a table lookup, never a global ratio",
    len(set(shares)) > 1,
    metric=f"FVT share by SKU = {sorted(set(shares))}")

chk("CT-07", "certification cells where both models agree are still reported UNRESOLVED",
    any(c["models_agree"] for c in cert)
    and all(c["status"].startswith("UNRESOLVED") for c in cert),
    note="agreement is surfaced as information; the model is not promoted to confirmed "
         "without the Owner")

cert_ori = [o for o in R.analyse(inp_of(**CLEAN4))["owner_review_items"]
            if o["kind"] == "CERTIFICATION_MODEL_UNRESOLVED"]
chk("CT-08", "disagreement between the models raises Owner Review Items automatically",
    len(cert_ori) > 0 and all("DEC-03" in o["why"] for o in cert_ori),
    metric=f"{len(cert_ori)} ORI entries")

# --------------------------------------------------------------------------- #
# 4  Panel semantics (DEC-02)
# --------------------------------------------------------------------------- #
chk("PL-01", "Panel is matched as Panel Spec Count taken from the SKU Definition rows",
    R.definitions()["SKU4"]["panel"] == [2, 2]
    and R.match_sku(dict(SEP4))["dimension_detail"][4]["panel"]["range"] == [2, 2])

chk("PL-02", "D2:H2 'N*panel' comments are retained as evidence but excluded from calculation",
    len(R.UNRESOLVED_COMMENTS) == 5
    and R.UNRESOLVED_COMMENTS["3"]["panel"] == 3
    and R.definitions()["SKU3"]["panel"] == [1, 1]
    and R.QMODEL["policy"]["panel_annotation_d2_h2"].startswith("UNRESOLVED_COMMENT"),
    note="comment Panel counts (2/3/4/5/6) never appear as a definition range, so they "
         "cannot reach the matcher or the arithmetic. The same comments also conflict on "
         "CPU at 6 SKU (comment 3*CPU vs definition 4-5*CPU) and are also excluded",
    metric="comment panel = [2,3,4,5,6] vs definition [1-2] [1] [2] [2] [2-3]")

chk("PL-03", "Panel Spec Count stays an independent input dimension (not deleted)",
    "panel" in R.DIMS and R.match_sku({"panel": 2})["state"] != "UNDETERMINED")

chk("PL-04", "proof by counter-example: panel=1 still yields 3 SKU, which the E2 comment forbids",
    R.match_sku(dict(cpu=2, gpu=2, panel=1, ssd=1, mem=1))["recommended_sku"] == 3,
    note="if the E2 comment (3*panel) were in the matching path, panel=1 could not be 3 SKU")

# --------------------------------------------------------------------------- #
# 5  SKU recommendation contract (DEC-01)
# --------------------------------------------------------------------------- #
tie = R.match_sku(dict(CLEAN4))
chk("SR-01", "4 SKU and 5 SKU co-match returns a RANGE, not a forced single SKU",
    tie["state"] == "RANGE" and set(tie["tie_set"]) == {4, 5},
    metric=f"tie={tie['tie_set']} scores={ {k: v for k, v in tie['scores'].items() if k in (4, 5)} }")

chk("SR-02", "recommended_sku is null and preferred_sku is NOT_ESTABLISHED on a range",
    tie["recommended_sku"] is None and tie["preferred_sku"] == "NOT_ESTABLISHED")

both = [R.finalise(inp_of(**CLEAN4), n) for n in R.candidates_to_price(tie)]
chk("SR-03", "a RANGE prices every candidate SKU - 4 SKU and 5 SKU are both calculated",
    {b["sku_qty"] for b in both} == {4, 5},
    metric=" | ".join(f"{b['sku_qty']} SKU total "
                      f"{b['recommended_total_band']['min']:g}-{b['recommended_total_band']['max']:g}"
                      for b in both))

chk("SR-04", "the priced candidate list is never padded beyond the tie set",
    R.candidates_to_price(tie) == [4, 5]
    and R.candidates_to_price(R.match_sku(dict(SEP4))) == [4])

clean2 = R.match_sku(dict(cpu=1, gpu=1, panel=1, ssd=1, mem=1))
chk("SR-05", "a genuine SINGLE is still returned where the evidence separates the tiers",
    clean2["state"] == "SINGLE" and clean2["recommended_sku"] == 2)

chk("SR-06", "partial evidence never produces a fake SINGLE",
    R.match_sku({"cpu": 3, "gpu": 3})["state"] != "SINGLE"
    and R.match_sku({"cpu": 2, "gpu": 2, "panel": 2})["state"] != "SINGLE")

chk("SR-07", "empty input -> UNDETERMINED, nothing recommended, nothing priced",
    (lambda m: m["state"] == "UNDETERMINED" and m["recommended_sku"] is None
     and m["preferred_sku"] == "NOT_ESTABLISHED" and R.candidates_to_price(m) == [])(
        R.match_sku({})))

chk("SR-08", "out-of-domain input is refused and routed to ORI-13, never extrapolated",
    (lambda m: m["state"] == "OUT_OF_DOMAIN" and m["recommended_sku"] is None
     and m["out_of_domain"] and R.candidates_to_price(m) == [])(
        R.match_sku(dict(cpu=9, gpu=3, panel=2, ssd=2, mem=2))))

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
    reachable, expected="FAIL",
    note="UNRESOLVED DESIGN GAP -> ORI-04. The 5 SKU definition is a strict subset of the "
         "4 SKU definition, so 5 SKU can never win alone and only ever appears as the "
         "range 4-5 SKU. Closing this needs real 4-SKU and 5-SKU project samples plus an "
         "official boundary rule from the Owner. This probe is EXPECTED TO FAIL and must "
         "not be weakened, deleted or turned green by re-weighting.",
    metric=f"SKU5 unique winners = {sku5_unique} over 405 realistic combinations")

chk("SR-10", "no weighting trick is used to break a tie (weights unchanged since phase 1)",
    R.DIM_WEIGHT == {"cpu": 1.0, "gpu": 1.6, "panel": 1.0, "ssd": 1.4, "mem": 1.4}
    and R.VERDICT_WEIGHT == {"MATCH": 1.0, "PARTIAL_MATCH": 0.4, "MISMATCH": 0.0, "UNKNOWN": 0.0},
    note="ORI-08: these weights are agent-set, not Owner-confirmed. They rank candidates "
         "but DEC-01 forbids using them to manufacture a single answer.")

# --------------------------------------------------------------------------- #
# 6  Wave assignment contract (DEC-04)
# --------------------------------------------------------------------------- #
w_explicit = mkw(waves={"ssd": ["CURRENT_WAVE", "LATER_WAVE"],
                        "mem": ["CURRENT_WAVE", "LATER_WAVE"]},
                 cpu=2, gpu=2, panel=1, ssd=2, mem=2)
res_w = R.analyse(w_explicit)
cur = next(s for s in res_w["scenarios"] if s["scope"] == "CURRENT_WAVE")
full = next(s for s in res_w["scenarios"] if s["scope"] == "FULL_PROJECT")

chk("WV-01", "explicit LATER_WAVE specs are excluded from CURRENT_WAVE only",
    cur["counts"] == dict(cpu=2, gpu=2, panel=1, ssd=1, mem=1)
    and full["counts"] == dict(cpu=2, gpu=2, panel=1, ssd=2, mem=2))

chk("WV-02", "CURRENT_WAVE and FULL_PROJECT can recommend different SKU counts",
    cur["match"]["recommended_sku"] == 3 and full["match"]["recommended_sku"] == 4,
    metric=f"current wave -> {cur['match']['recommended_sku']} SKU "
           f"({cur['match']['state']}) | full project -> {full['match']['recommended_sku']} SKU "
           f"({full['match']['state']})")

plain = inp_of(cpu=2, gpu=2, panel=1, ssd=2, mem=2)
chk("WV-03", "wave assignment never changes the base rates",
    [totals(x) for x in [R.finalise(w_explicit, 3)]]
    and all(r["base_demand"] == R.QCELL[(r["function_id"], r["phase"])]["adopted_absolute"]["SKU3"]
            for r in R.demand_rows(w_explicit, 3) if r["base_demand"] is not None)
    and all(r["base_demand"] == R.QCELL[(r["function_id"], r["phase"])]["adopted_absolute"]["SKU3"]
            for r in R.demand_rows(plain, 3) if r["base_demand"] is not None),
    note="the same SKU-3 column is read whether or not waves were declared")

nowave = inp_of(cpu=2, gpu=2, panel=1, ssd=2, mem=2)
chk("WV-04", "wave assignment only changes the spec counts - it is not a deduction factor",
    all(a["base_demand"] == b["base_demand"] and a["quantity_model"] == b["quantity_model"]
        for a, b in zip(R.demand_rows(w_explicit, 4), R.demand_rows(nowave, 4)))
    and totals(R.finalise(w_explicit, 4))["TOTAL"] == totals(R.finalise(nowave, 4))["TOTAL"],
    note="declaring a second wave changes which specs are counted, never the arithmetic. "
         "There is no per-wave percentage and no per-wave unit constant in the engine.",
    metric=f"same 4 SKU total {totals(R.finalise(w_explicit, 4))['TOTAL']:g} with or without waves")

chk("WV-05", "the existence of a second spec is never treated as a second wave",
    (lambda r: len([s for s in r["scenarios"] if s["scope"] == "CURRENT_WAVE"]) == 1
     and all(s["identical_to_full_project"] for s in r["scenarios"] if s["scope"] == "CURRENT_WAVE")
     and any(o["kind"] == "WAVE_ASSIGNMENT_NOT_PROVIDED" for o in r["owner_review_items"])
     and not any(o["kind"] == "WAVE_ASSIGNMENT_UNKNOWN" for o in r["owner_review_items"]))(
        R.analyse(inp_of(cpu=2, gpu=2, panel=1, ssd=2, mem=2))),
    note="untagged second specs stay in the current wave by default and raise an ORI asking "
         "the Owner to confirm. The Agent does not guess a second wave and does not drop the "
         "SKU answer from 4 to 3 on its own.")

un = R.analyse(mkw(waves={"ssd": ["CURRENT_WAVE", "UNKNOWN"], "mem": ["CURRENT_WAVE", "UNKNOWN"]},
                   cpu=2, gpu=2, panel=1, ssd=2, mem=2))
unk_scen = [s for s in un["scenarios"] if s["scope"] == "CURRENT_WAVE"]
chk("WV-06", "an explicitly UNKNOWN wave yields a range of scenarios plus an Owner Review Item",
    len(unk_scen) > 1
    and sum(1 for o in un["owner_review_items"] if o["kind"] == "WAVE_ASSIGNMENT_UNKNOWN") == 1,
    metric=f"{len(unk_scen)} current-wave scenarios; "
           f"answers = {sorted({(s['match']['recommended_sku'], tuple(s['match']['tie_set'] or [])) for s in unk_scen})}")

chk("WV-07", "wave source is recorded per spec: user-tagged, implicit single, or not provided",
    {x["factor"]: x["sources"] for x in cur["wave_report"] if x["factor"] in ("ssd", "mem")}
    == {"ssd": ["USER_SELECTED"], "mem": ["USER_SELECTED"]}
    and [x["sources"] for x in cur["wave_report"] if x["factor"] == "panel"] == [["IMPLICIT_SINGLE_SPEC"]]
    and [x["wave_state"] for x in cur["wave_report"] if x["factor"] in ("cpu", "gpu")]
    == ["NOT_PROVIDED", "NOT_PROVIDED"],
    note="cpu and gpu also have two specs here but nobody said which wave they belong to, "
         "so they are reported NOT_PROVIDED rather than being guessed")

chk("WV-07b", "NOT_PROVIDED factors are raised as an Owner Review Item, not resolved silently",
    any(o["kind"] == "WAVE_ASSIGNMENT_NOT_PROVIDED" and set(o["factors"]) == {"cpu", "gpu"}
        for o in res_w["owner_review_items"]),
    metric=str([o.get("factors") for o in res_w["owner_review_items"]
                if o["kind"] == "WAVE_ASSIGNMENT_NOT_PROVIDED"]))

chk("WV-08", "FULL_PROJECT never silently drops a spec because a wave was declared",
    full["counts"]["ssd"] == 2 and full["counts"]["mem"] == 2
    and variant(R.finalise(w_explicit, 4)) is not None)

chk("WV-09", "when no factor has a LATER_WAVE spec, CURRENT_WAVE is flagged identical to FULL_PROJECT",
    (lambda r: len(r["scenarios"]) == 2
     and [s for s in r["scenarios"] if s["scope"] == "CURRENT_WAVE"][0]["identical_to_full_project"])(
        R.analyse(inp_of(cpu=1, gpu=1, panel=1, ssd=1, mem=1))),
    note="both scopes are still shown side by side, but the UI can say 'same as full project'")

chk("WV-10", "a declared second wave does change the SKU answer, so the wave is load-bearing",
    cur["match"]["recommended_sku"] != full["match"]["recommended_sku"]
    and cur["wave_basis"] == "EXPLICIT_ASSIGNMENT")

chk("WV-11", "wave_basis distinguishes 'nobody declared' from 'declared' from 'unknown'",
    (lambda a, b, c: a == "NO_EXPLICIT_ASSIGNMENT" and b == "EXPLICIT_ASSIGNMENT"
     and c == "UNKNOWN_FANOUT")(
        next(s for s in R.analyse(inp_of(cpu=2, gpu=2, panel=1, ssd=2, mem=2))["scenarios"]
             if s["scope"] == "CURRENT_WAVE")["wave_basis"],
        cur["wave_basis"],
        next(s for s in un["scenarios"] if s["scope"] == "CURRENT_WAVE")["wave_basis"]),
    note="the UI needs this to explain why CURRENT_WAVE equals FULL_PROJECT: it is because "
         "nobody declared a second wave, not because a second wave was declared and cancelled")

# --------------------------------------------------------------------------- #
# 7  Reuse protection contract (DEC-06)
# --------------------------------------------------------------------------- #
base = R.finalise(inp_of(**SEP4), 4)
b0 = totals(base)


def with_reuse(items):
    return totals(R.finalise(inp_of(reuse_items=items, **SEP4), 4))


v_emb = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_EMBEDDED, function_id="F_THM",
                                basis="sharing already inside the baseline rate")])
v_ok = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_ADDITIONAL, function_id="F_SED",
                               proven_not_in_baseline=True, basis="confirmed spare pool")])
v_bad = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_ADDITIONAL, function_id="F_SED",
                                basis="no proof supplied")])
v_pot = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_POTENTIAL)])
v_unk = with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_UNKNOWN)])

chk("RS-01", "ALREADY_EMBEDDED_IN_BASELINE is never deducted (double-count guard)",
    R.approx(v_emb["recommended_total"], b0["recommended_total"]),
    metric=f"{v_emb['recommended_total']:g} == base {b0['recommended_total']:g}")

chk("RS-02", "ADDITIONAL_CONFIRMED_REUSE with proof is deducted once",
    R.approx(v_ok["recommended_total"], b0["recommended_total"] - 5.0),
    metric=f"{v_ok['recommended_total']:g} vs base {b0['recommended_total']:g}")

bad_ledger = R.finalise(inp_of(reuse_items=[R.ReuseItem(qty=5.0, reuse_status=R.REUSE_ADDITIONAL,
                                                        function_id="F_SED",
                                                        basis="no proof supplied")], **SEP4), 4)
chk("RS-03", "ADDITIONAL_CONFIRMED_REUSE without proof is not deducted and raises an ORI",
    R.approx(v_bad["recommended_total"], b0["recommended_total"])
    and any(o["kind"] == "REUSE_PROOF_MISSING" for o in bad_ledger["reuse_ledger"]["owner_review_items"])
    and bad_ledger["reuse_ledger"]["items"][0]["decision"] == "BLOCKED_PROOF_MISSING")

chk("RS-04", "POTENTIAL_REUSE stays display only and never reduces demand",
    R.approx(v_pot["recommended_total"], b0["recommended_total"]))

chk("RS-05", "UNKNOWN_OVERLAP is never deducted when double deduction cannot be excluded",
    R.approx(v_unk["recommended_total"], b0["recommended_total"]))

lr = R.finalise(inp_of(reuse_items=[R.ReuseItem(qty=5.0),
                                    R.ReuseItem(qty=3.0, reuse_status=R.REUSE_POTENTIAL),
                                    R.ReuseItem(qty=2.0, reuse_status=R.REUSE_EMBEDDED),
                                    R.ReuseItem(qty=4.0, reuse_status=R.REUSE_ADDITIONAL,
                                                function_id="F_SED",
                                                proven_not_in_baseline=True)], **SEP4), 4)
chk("RS-06", "a mixed reuse ledger applies only the proven item and audits every decision",
    R.approx(totals(lr)["confirmed_reuse_adjustment"], -4.0)
    and {i["decision"] for i in lr["reuse_ledger"]["items"]} ==
    {"BLOCKED_UNTIL_PROVEN", "DISPLAY_ONLY", "NOT_DEDUCTED_ALREADY_EMBEDDED", "DEDUCTED"},
    metric=f"applied {totals(lr)['confirmed_reuse_adjustment']:g} of claimed 14.0")

sus = R.QMODEL["baseline_embedded_sharing"]
chk("RS-07", "flat-total Functions are flagged so reuse needs extra proof",
    sus["F_EMC_TEST"]["reuse_policy"] == "BLOCK_UNLESS_PROVEN"
    and sus["F_SED"]["reuse_policy"] == "PERMIT_WHEN_CONFIRMED",
    metric=f"{len(R.QMODEL['summary']['embedded_sharing_suspected_functions'])} Functions flagged")

chk("RS-08", "a PCBA reuse claim can never reduce unit demand",
    R.approx(with_reuse([R.ReuseItem(qty=5.0, reuse_status=R.REUSE_ADDITIONAL, unit="PCBA",
                                     proven_not_in_baseline=True)])["recommended_total"],
             b0["recommended_total"]),
    note="unit mismatch is an exclusion reason in its own right")

# --------------------------------------------------------------------------- #
# 8  D-01 decimals, unit isolation, provenance
# --------------------------------------------------------------------------- #
chk("D01-01", "the 4 SKU Main Table total stays 443.8, never 444",
    R.approx(replay["SKU4"], 443.8))

res_risk = R.finalise(inp_of(**SEP4), 4, risk_pct=0.05)
chk("D01-02", "fractional risk reserve is kept to full precision",
    R.approx(totals(res_risk)["risk_reserve"], 443.8 * 0.05, 1e-9),
    metric=f"{totals(res_risk)['risk_reserve']!r}")

chk("D01-03", "the engine reports rounding = NONE",
    res_risk["rounding"] == "NONE (D-01)"
    and R.QMODEL["policy"]["rounding"].startswith("NONE (D-01)"))

chk("D01-04", "comparison uses an explicit tolerance, business values stay untouched",
    R.approx(443.8, 443.8000000001) and not R.approx(443.8, 443.9)
    and R.approx(res_risk["totals_by_model"]["variants"][0]["recommended_total"],
                 443.8 + 443.8 * 0.05, 1e-9))

pcba = R.finalise(inp_of(extra_demand=[{"qty": 12.0, "unit": "PCBA", "label": "PCBA set"}],
                         **SEP4), 4)
chk("D01-05", "PCBA extra demand is listed but never summed into unit totals",
    R.approx(totals(pcba)["TOTAL"], b0["TOTAL"]) and len(pcba["pcba_lines_not_summed"]) == 1,
    metric=f"unit total unchanged at {totals(pcba)['TOTAL']:g}; PCBA 12.0 shown separately")

unitx = R.finalise(inp_of(extra_demand=[{"qty": 12.0, "unit": "UNIT"}], **SEP4), 4)
chk("D01-06", "control: extra UNIT demand does enter the total",
    R.approx(totals(unitx)["recommended_total"], b0["recommended_total"] + 12.0))

chk("D01-07", "risk reserve is charged on baseline demand, never on user-added extra demand",
    R.approx(totals(unitx)["risk_reserve"], 0.0)
    and R.approx(R.finalise(inp_of(extra_demand=[{"qty": 12.0, "unit": "UNIT"}], **SEP4), 4,
                            risk_pct=0.05)["totals_by_model"]["variants"][0]["risk_reserve"],
                 443.8 * 0.05, 1e-9))

chk("PR-01", "no product series name is ever used as a judgement basis",
    not any(tok in json.dumps([s["match"]["reasons"] for s in
                               R.analyse(inp_of(**CLEAN4))["scenarios"]], ensure_ascii=False)
            for tok in ("Pro", "LOQ", "Y5", "Y7", "X9", "X11", "N1x", "Y9")))

chk("PR-02", "every demand line carries rule_id, source file, sheet and row",
    all(r["rule_id"].startswith("QM2:") and r["evidence"]["source_file"]
        and r["evidence"]["sheet"] and r["evidence"]["row"]
        for r in R.demand_rows(inp_of(**SEP4), 4)))

chk("PR-03", "missing key factors stay null and are listed as 请补充, never defaulted",
    (lambda a: a.missing() == ["panel", "ssd", "mem"]
     and all(a.factors()[n].effective is None for n in ("panel", "ssd", "mem"))
     and all(a.factors()[n].status_user == "请补充" for n in ("panel", "ssd", "mem")))(
        mk(cpu=3, gpu=2)))

chk("PR-04", "user value overrides the file-read value while the file value is retained",
    (lambda k: k.effective == 4 and k.file_value == 2 and k.source == "USER")(
        R.KeyFactor("cpu", file_value=2, user_value=4, user_edited=True)))

chk("PR-05", "an unedited factor keeps the file value as the effective value",
    (lambda k: k.effective == 2 and k.source == "FILE")(
        R.KeyFactor("cpu", file_value=2, user_value=5)))

# --------------------------------------------------------------------------- #
# 9  schema conformance
# --------------------------------------------------------------------------- #
import importlib.util as _ilu                                                # noqa: E402

if _ilu.find_spec("jsonschema"):
    import jsonschema as _js                                                 # noqa: E402
    IN_SCHEMA = json.loads((ROOT / "schema/input.schema.json").read_text(encoding="utf-8"))
    OUT_SCHEMA = json.loads((ROOT / "schema/output.schema.json").read_text(encoding="utf-8"))

    payload = R.serialise(R.analyse(mk(cpu=2, gpu=2, panel=1, ssd=2, mem=2,
                                       reuse_items=[R.ReuseItem(qty=2.0)],
                                       extra_demand=[{"qty": 3.0, "unit": "PCBA"}])),
                          analysis_id="SMOKE-1")
    errs = sorted(_js.Draft202012Validator(OUT_SCHEMA).iter_errors(payload),
                  key=lambda e: list(e.absolute_path))
    chk("SC-01", "engine output validates against schema/output.schema.json", not errs,
        note="; ".join(f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message[:90]}"
                       for e in errs[:4]))

    doc = {
        "schema_version": "2.0",
        "key_factors": {
            n: {"name": n, "file_value": v, "user_edited": False}
            for n, v in dict(cpu=2, gpu=2, panel=1, ssd=2, mem=2).items()
        },
        "wave_assignment": {"declared_by": "USER_SELECTED", "specs": [
            {"factor": "ssd", "spec_index": 1, "wave": "CURRENT_WAVE",
             "wave_source": "USER_SELECTED"},
            {"factor": "ssd", "spec_index": 2, "wave": "LATER_WAVE",
             "wave_source": "USER_SELECTED"}]},
        "certification_input": {"mode": "UNRESOLVED_SHOW_BAND"},
        "reuse_items": [{"qty": 2.0, "unit": "UNIT",
                         "reuse_status": "ADDITIONAL_CONFIRMED_REUSE",
                         "proven_not_in_baseline": True, "basis": "spare pool"}],
        "additional_demand": [{"qty": 3.0, "unit": "PCBA"}],
        "risk_reserve": {"percent": 0},
    }
    errs_in = sorted(_js.Draft202012Validator(IN_SCHEMA).iter_errors(doc),
                     key=lambda e: list(e.absolute_path))
    chk("SC-02", "a full manual-entry document validates against schema/input.schema.json",
        not errs_in,
        note="; ".join(f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message[:90]}"
                       for e in errs_in[:4]))

    chk("SC-03", "input schema refuses a text sentinel in place of a missing factor",
        bool(list(_js.Draft202012Validator(IN_SCHEMA).iter_errors(
            {**doc, "key_factors": {**doc["key_factors"],
                                    "panel": {"name": "panel", "file_value": "N/A"}}}))),
        note="file_value is number|null, so 'N/A' / 'case by case' cannot be smuggled in; "
             "the UI must leave it null and show 请补充")

    chk("SC-04", "input schema refuses an unknown reuse status",
        bool(list(_js.Draft202012Validator(IN_SCHEMA).iter_errors(
            {**doc, "reuse_items": [{"qty": 1.0, "unit": "UNIT",
                                     "reuse_status": "PROBABLY_SHARED"}]}))))

    bad_payload = json.loads(json.dumps(payload))
    if bad_payload["scenarios"] and bad_payload["scenarios"][0]["results"]:
        rr = bad_payload["scenarios"][0]["results"][0]
        rr["single_value"] = False
        rr["recommended_total"] = 999.0          # a single total hiding an unresolved band
        chk("SC-05", "output schema refuses a single total while cells are UNRESOLVED",
            bool(list(_js.Draft202012Validator(OUT_SCHEMA).iter_errors(bad_payload))),
            note="the if/then rule in output.schema.json makes this a validation error, so a "
                 "front end cannot quietly publish one number out of a band")
    else:
        chk("SC-05", "output schema refuses a single total while cells are UNRESOLVED", False,
            note="smoke fixture produced no priced scenario")

    chk("SC-06", "AnalysisInput.from_document() honours the input contract exactly",
        (lambda a: [a.factors()[n].effective for n in R.DIMS] == [2, 2, 1, 2, 2]
         and a.risk_reserve_pct == 0.0
         and len(a.reuse_items) == 1 and a.reuse_items[0].proven_not_in_baseline
         and [(s.wave, s.wave_source) for s in a.ssd.specs]
         == [("CURRENT_WAVE", "USER_SELECTED"), ("LATER_WAVE", "USER_SELECTED")]
         and [s.wave_source for s in a.cpu.specs] == ["NOT_PROVIDED", "NOT_PROVIDED"])(
            R.AnalysisInput.from_document(doc)))

    chk("SC-07", "a declared LATER_WAVE spec reaches the wave engine through the contract",
        (lambda r: next(s for s in r["scenarios"]
                        if s["scope"] == "CURRENT_WAVE")["counts"]["ssd"] == 1)(
            R.analyse(R.AnalysisInput.from_document(doc))))
else:
    print("[skip] jsonschema not installed - schema conformance probes not run")

# --------------------------------------------------------------------------- #
# 10  report
# --------------------------------------------------------------------------- #
expected_fail = [r["id"] for r in RESULTS if r["expected"] == "FAIL"]
actual_fail = [r["id"] for r in RESULTS if r["actual"] == "FAIL"]
regressions = [r["id"] for r in RESULTS if r["verdict"] != "OK"]
summary = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "core": "prototype/rules_v2.py",
    "quantity_model": R.QMODEL["model_id"],
    "baseline": R.BASELINE["baseline_id"],
    "total": len(RESULTS),
    "probes_holding": sum(1 for r in RESULTS if r["actual"] == "PASS"),
    "probes_failing": actual_fail,
    "expected_failures": expected_fail,
    "regressions": regressions,
    "status": "CLEAN" if not regressions else "REGRESSION",
}

out_dir = ROOT / "artifacts" / "validation"
(out_dir / "regression_results_v2.json").write_text(
    json.dumps({"summary": summary, "results": RESULTS}, ensure_ascii=False, indent=2),
    encoding="utf-8")

L = ["# Phase 2 regression report - manual-input calculation core", "",
     "| item | value |", "|---|---|",
     f"| core | `prototype/rules_v2.py` |",
     f"| quantity model | `{R.QMODEL['model_id']}` {R.QMODEL['model_version']} |",
     f"| baseline | `{R.BASELINE['baseline_id']}` ({R.BASELINE['status']}) |",
     f"| status | **{summary['status']}** |", "",
     "## Expected PASS / FAIL list", "",
     "| ID | Invariant | Expected | Actual | Verdict |", "|---|---|---|---|---|"]
for r in RESULTS:
    v = ("REGRESSION" if r["verdict"] == "REGRESSION"
         else ("as expected" if r["actual"] == "PASS" else "EXPECTED FAIL (open design gap)"))
    L.append(f"| {r['id']} | {r['title']} | {r['expected']} | {r['actual']} | {v} |")
L += ["", "## Probe notes", ""]
for r in RESULTS:
    if r["note"]:
        L.append(f"- **{r['id']}** - {r['note']}" + (f" _({r['metric']})_" if r["metric"] else ""))
L += ["", "## Summary", "", "```json", json.dumps(summary, ensure_ascii=False, indent=1), "```", ""]
(out_dir / "regression_report_v2.md").write_text("\n".join(L), encoding="utf-8")

print("\n" + "=" * 78)
print(f"{summary['probes_holding']}/{summary['total']} probes hold | "
      f"failing: {actual_fail} | expected-fail: {expected_fail}")
print(f"regressions: {regressions or 'none'}")
print(f"STATUS: {summary['status']}")
sys.exit(1 if regressions else 0)
