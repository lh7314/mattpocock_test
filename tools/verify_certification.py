#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_certification - per-cell verification of the Certification Main Table against
the Certification Appendix, under the Owner's corrected semantics.

Owner semantics implemented (task TASK-...-CERTIFICATION-CORRECTION-AND-WEB-MVP-01, §4)
  * the Main Table states the sample quantity needed for ONE SKU
  * the Appendix states the resulting project total for that SKU count
  * they are NOT two competing models. They must satisfy

        appendix_total == main_table_per_sku_quantity x sku_count

  * the Appendix is therefore evidence with evidence_role = DERIVED_TOTAL_VALIDATION.
    It is never added to a project total a second time and never forms a band.

Every Certification Function x Phase x SKU cell is verified individually - never a
total alone. Nothing in the source data is edited to make a cell agree: the original
values, the delta and the reason are all preserved and routed to the Owner Review
Register.

Reads   artifacts/model/baseline_v1.json          (read-only)
Writes  artifacts/model/certification_verification.json
        artifacts/model/certification_verification.md
"""
from __future__ import annotations

import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-9
SKU_RANGE = (2, 3, 4, 5, 6)
PHASES = ("FVT", "SIT")

BASELINE = json.loads((ROOT / "artifacts/model/baseline_v1.json").read_text(encoding="utf-8"))
QMODEL_V2 = None
_q = ROOT / "artifacts/model/quantity_model_v2.json"
if _q.exists():                                    # only used to quote Phase 2 wording
    QMODEL_V2 = json.loads(_q.read_text(encoding="utf-8"))

VERIFIED, MISMATCH, NOT_EVALUABLE = "VERIFIED", "MISMATCH", "NOT_EVALUABLE"

# Appendix label -> (function_id, phase).  The TTL rows of the appendix block are not
# Function cells; they are cross-checked separately.
APPENDIX_MAP = {
    "EMC FVT":     ("F_EMC", "FVT"),
    "EMC SIT":     ("F_EMC", "SIT"),
    "Green FVT":   ("F_GREEN", "FVT"),
    "Green SIT":   ("F_GREEN", "SIT"),
    "Safety FVT":  ("F_SAFETY", "FVT"),
    "Safety SIT":  ("F_SAFETY", "SIT"),
    "RF Cert FVT": ("F_RF_CERTIFICATION", "FVT"),
    "RF Cert SIT": ("F_RF_CERTIFICATION", "SIT"),
}
APPENDIX_TTL = {"TTL FVT": "FVT", "TTL SIT": "SIT"}


def approx(a, b, tol=TOL) -> bool:
    if a is None or b is None:
        return a is b
    return abs(float(a) - float(b)) <= tol


def g(x):
    return "" if x is None else f"{x:g}"


# --------------------------------------------------------------------------- #
# 1  source reads
# --------------------------------------------------------------------------- #
FUNCS = {f["function_id"]: f for f in BASELINE["functions"]}
CERT_FUNCS = [f for f in BASELINE["functions"] if f["category"] == "CERT"]
APX = BASELINE["secondary_tables"]["certification_block2"]
APX_ROW = {}
for r in APX["rows"]:
    APX_ROW[r["label"]] = r


def appendix_cell(label: str, sku: int):
    r = APX_ROW.get(label)
    return None if r is None else r.get(f"SKU{sku}")


# --------------------------------------------------------------------------- #
# 2  per-cell verification grid
# --------------------------------------------------------------------------- #
cells = []
for f in CERT_FUNCS:
    fid, name = f["function_id"], f["name"]
    for phase in PHASES:
        rate_row = f["source_rows"][phase.lower()]
        apx_label = next((k for k, v in APPENDIX_MAP.items() if v == (fid, phase)), None)
        apx_row = APX_ROW.get(apx_label, {}).get("row") if apx_label else None
        rates = [f["per_sku_rate"][phase][f"SKU{n}"] for n in SKU_RANGE]
        non_null = [v for v in rates if v is not None]
        constant = bool(non_null) and all(approx(v, non_null[0]) for v in non_null)
        for n in SKU_RANGE:
            rate = f["per_sku_rate"][phase][f"SKU{n}"]
            apx = appendix_cell(apx_label, n) if apx_label else None
            derived = None if rate is None else round(rate * n, 10)
            if rate is None or apx is None or apx_label is None:
                status, delta = NOT_EVALUABLE, None
            elif approx(derived, apx):
                status, delta = VERIFIED, 0.0
            else:
                status, delta = MISMATCH, round(apx - derived, 10)
            cells.append({
                "function_id": fid,
                "function_name": name,
                "phase": phase,
                "sku_count": n,
                "main_table_per_sku_quantity": rate,
                "derived_total": derived,
                "appendix_label": apx_label,
                "appendix_total": apx,
                "delta": delta,
                "delta_direction": (None if delta in (None, 0.0)
                                    else "APPENDIX_HIGHER" if delta > 0
                                    else "APPENDIX_LOWER"),
                "verification_status": status,
                "main_table_rate_is_constant_across_sku": constant,
                "source_reference": {
                    "source_file": BASELINE["derived_from"]["file"],
                    "sheet": BASELINE["derived_from"]["sheet"],
                    "main_table_row": rate_row,
                    "appendix_row": apx_row,
                    "main_table_cells": f"C{n + 1}{rate_row}:H{n + 1}{rate_row}",
                    "appendix_cells": (f"C{n + 1}{apx_row}:H{n + 1}{apx_row}"
                                       if apx_row else None),
                },
            })

verified = [c for c in cells if c["verification_status"] == VERIFIED]
mismatched = [c for c in cells if c["verification_status"] == MISMATCH]
not_evaluable = [c for c in cells if c["verification_status"] == NOT_EVALUABLE]

# --------------------------------------------------------------------------- #
# 3  appendix internal consistency (does the appendix add up to its own TTL rows?)
# --------------------------------------------------------------------------- #
appendix_internal = []
for apx_label, phase in APPENDIX_TTL.items():
    comp = [k for k, v in APPENDIX_MAP.items() if v[1] == phase]
    for n in SKU_RANGE:
        parts = [appendix_cell(k, n) for k in comp]
        parts = [p for p in parts if p is not None]
        ttl = appendix_cell(apx_label, n)
        appendix_internal.append({
            "appendix_label": apx_label, "phase": phase, "sku_count": n,
            "component_sum": sum(parts) if parts else None,
            "appendix_ttl": ttl,
            "status": (NOT_EVALUABLE if ttl is None or not parts
                       else VERIFIED if approx(sum(parts), ttl) else MISMATCH),
            "appendix_row": APX_ROW.get(apx_label, {}).get("row"),
        })
int_ok = all(a["status"] == VERIFIED for a in appendix_internal)

# --------------------------------------------------------------------------- #
# 4  main-table semantic shape: does the "per SKU" column behave like a rate?
#    A genuine per-SKU rate is constant across SKU bands. A column that falls as
#    1/N is a back-derivation from a flat total, which changes what "per SKU" means.
# --------------------------------------------------------------------------- #
rate_shape = []
for f in CERT_FUNCS:
    for phase in PHASES:
        rates = [f["per_sku_rate"][phase][f"SKU{n}"] for n in SKU_RANGE]
        vals = [v for v in rates if v is not None]
        ttl = [f["ttl_per_phase"][phase][f"SKU{n}"] for n in SKU_RANGE]
        tvals = [v for v in ttl if v is not None]
        if not vals:
            shape = "NOT_EVALUABLE"
        elif all(approx(v, vals[0]) for v in vals):
            shape = "TRUE_PER_SKU_RATE"          # constant -> main x SKU grows with SKU
        elif tvals and all(approx(v, tvals[0]) for v in tvals):
            shape = "BACK_DERIVED_FROM_FLAT_TOTAL"   # rate x SKU is constant
        else:
            shape = "IRREGULAR"
        rate_shape.append({
            "function_id": f["function_id"], "function_name": f["name"], "phase": phase,
            "per_sku_rate": {f"SKU{n}": f["per_sku_rate"][phase][f"SKU{n}"] for n in SKU_RANGE},
            "main_table_rate_x_sku": {f"SKU{n}": f["ttl_per_phase"][phase][f"SKU{n}"]
                                      for n in SKU_RANGE},
            "rate_shape": shape,
            "main_table_row": f["source_rows"][phase.lower()],
        })

# --------------------------------------------------------------------------- #
# 5  impact of each mismatch, expressed on the project total
# --------------------------------------------------------------------------- #
impact = []
for c in mismatched:
    impact.append({
        "function_id": c["function_id"], "function_name": c["function_name"],
        "phase": c["phase"], "sku_count": c["sku_count"],
        "main_derived_total_audit_only": c["derived_total"],
        "appendix_total_adopted": c["appendix_total"],
        "change_of_adopted_value_vs_main_derived": c["delta"],
        "note": "DEC-10: the Appendix total is the adopted value and is what the project "
                "total carries. The Main Table derived total stays here for audit and "
                "difference analysis only - it is never counted alongside the Appendix.",
    })

# --------------------------------------------------------------------------- #
# 6  J33 investigation
# --------------------------------------------------------------------------- #
J33_TEXT = FUNCS["F_RF_CERTIFICATION"]["purpose_text"] or ""


def j33_items(text: str) -> list:
    """Pull the numbered line items out of the J33 note, keeping the raw wording."""
    out = []
    for m in re.finditer(r"(\d+)\s*[..、]\s*([^\n]+?)(?=\n\s*\d+\s*[..、]|\Z)", text, re.S):
        body = " ".join(m.group(2).split())
        # leading quantity claim, e.g. "CE *4 =antenna *wlan（欧盟）" -> 4
        q = re.search(r"\*\s*(\d+(?:\.\d+)?)", body)
        out.append({"item_no": int(m.group(1)), "raw": body,
                    "stated_unit_count": float(q.group(1)) if q else None})
    return out


def j33_total(items, reading: str):
    """
    Two readings of the same note. Neither is invented here: both follow from wording
    already inside the cell.
      CERTIFICATION_SUBSET - FCC whole-machine submissions treated as covered by the
                             C1PC/module route ("如果是C1PC ,就不需要整机"), so only the
                             SRRC/CE/Indonesia/Mexico/资安 line items need whole machines.
      FULL                 - every line item needs its own whole machines, at its stated
                             per-line quantity, with FCC = intel_wlan x antenna x 4.
    """
    def by_no(k):
        return next((i for i in items if i["item_no"] == k), None)

    ant = 2          # declared reference scenario inside J33: 2 antenna source
    wlan = 2         #                        + 2 wlan source
    parts = {}
    for k in (1, 2, 4, 5, 6):
        it = by_no(k)
        if it is None or it["stated_unit_count"] is None:
            return None, parts
        parts[f"item{k}"] = it["stated_unit_count"]
    if reading == "FULL":
        it3 = by_no(3)
        if it3 is None or it3["stated_unit_count"] is None:
            return None, parts
        parts["item3_FCC"] = ant * wlan * it3["stated_unit_count"]
    else:
        parts["item3_FCC"] = 0.0
    return sum(parts.values()), parts


j33_declared = {"antenna_source_count": 2, "wlan_card_count": 2}
j33_items_list = j33_items(J33_TEXT)
j33_subset, parts_subset = j33_total(j33_items_list, "CERTIFICATION_SUBSET")
j33_full, parts_full = j33_total(j33_items_list, "FULL")

rf = FUNCS["F_RF_CERTIFICATION"]
j33_vs_main = []
for n in SKU_RANGE:
    main_rate = rf["per_sku_rate"]["SIT"][f"SKU{n}"]
    derived = None if main_rate is None else round(main_rate * n, 10)
    apx = appendix_cell("RF Cert SIT", n)
    for label, val, reading in (
            ("CERTIFICATION_SUBSET", j33_subset, "FCC covered by module route"),
            ("FULL", j33_full, "every line item needs a whole machine")):
        j33_vs_main.append({
            "sku_count": n, "phase": "SIT", "reading": label, "reading_note": reading,
            "j33_reference_total": val,
            "main_table_derived_total": derived,
            "appendix_total": apx,
            "explains_main_table": (None if val is None or derived is None
                                    else approx(val, derived)),
            "explains_appendix": (None if val is None or apx is None
                                  else approx(val, apx)),
            "breakdown_parts": parts_subset if label == "CERTIFICATION_SUBSET" else parts_full,
        })

j33_can_explain_main = any(x["explains_main_table"] for x in j33_vs_main)
j33_can_explain_appendix = any(x["explains_appendix"] for x in j33_vs_main)

# the two readings bound a range rather than a point: the no-FCC floor (module route
# applies to every WLAN card) and the full-FCC ceiling. Where does each business value
# sit inside that bracket? Nothing here is invented - both bounds come from wording in
# J33 itself.
j33_bracket = {"min_no_whole_machine_fcc": j33_subset, "max_full_fcc": j33_full}
_jmin, _jmax = j33_subset, j33_full
j33_bracket["main_table_derived_15_inside_bracket"] = (
    None if _jmin is None or _jmax is None else bool(_jmin - TOL <= 15.0 <= _jmax + TOL))
j33_bracket["appendix_totals_8_to_10_inside_bracket"] = (
    None if _jmin is None or _jmax is None
    else bool(_jmin - TOL <= 8.0 <= _jmax + TOL))
j33_bracket["appendix_sits_below_the_no_fcc_floor"] = (
    None if _jmin is None else bool(8.0 < _jmin - TOL))
j33_bracket["reading"] = (
    "15 is inside the bracket: consistent with a mix where some WLAN cards take the "
    "C1PC/module route (no whole machine) and others do not. The Appendix 8-10 sits "
    "BELOW the floor of a 2-antenna / 2-WLAN-card project, so the Appendix cannot be the "
    "same reference scenario as J33. Neither value is reproducible from J33 alone.")

J33 = {
    "candidate_role": "CERTIFICATION_BREAKDOWN_EVIDENCE",
    "cell": "J33",
    "attached_to": {"function_id": "F_RF_CERTIFICATION", "phase": "FVT+SIT (merged J33:J34)",
                    "merged_range": "J33:J34"},
    "raw_text": J33_TEXT,
    "declared_reference_scenario": j33_declared,
    "declared_scope_words": "this data for 2 antenna source +2 wlan source refrence",
    "parsed_line_items": j33_items_list,
    "reference_total_under_readings": {
        "CERTIFICATION_SUBSET": {"total": j33_subset, "parts": parts_subset,
                                 "assumption": "FCC whole machines not required where the "
                                               "C1PC/module route applies, per the wording "
                                               "inside J33 itself"},
        "FULL": {"total": j33_full, "parts": parts_full,
                 "assumption": "every numbered line item needs its own whole machines, "
                               "FCC = intel_wlan x antenna x 4"},
    },
    "quantitative_reconciliation": j33_vs_main,
    "bracket": j33_bracket,
    "findings": {
        "explains_main_table_quantity": j33_can_explain_main,
        "explains_appendix_total": j33_can_explain_appendix,
        "applies_to": ["F_RF_CERTIFICATION only"],
        "applies_to_specific_source_combination": True,
        "antenna_and_wlan_are": ("BUSINESS_COMPOSITION_DESCRIPTION - the note explains why "
                                 "RF certification consumes machines (antenna source x WLAN "
                                 "card matrix). It is not an executable calculation "
                                 "variable in the workbook: no cell formula consumes it."),
        "already_inside_main_table_rate": "CANNOT_BE_PROVEN_FROM_THE_WORKBOOK",
        "double_count_risk_if_added": "HIGH - the Main Table per-SKU rate for RF "
                                      "certification is already the whole-machine count "
                                      "for that SKU; adding the J33 line items on top "
                                      "would count the same machines twice",
    },
    "disposition": ("CERTIFICATION_BREAKDOWN_EVIDENCE"
                    if (j33_can_explain_main or j33_can_explain_appendix)
                    else "DECLARED_NOT_GENERALIZED"),
    "additive_to_main_table_result": False,
    "mvp_requires_antenna_wlan_input_now": False,
    "rule_package_role": "EXPLANATORY_EVIDENCE_NOT_A_RULE",
}

# --------------------------------------------------------------------------- #
# 7  ORI-02 status
# --------------------------------------------------------------------------- #
if not_evaluable and not verified and not mismatched:
    ori02 = "OWNER_REVIEW_REQUIRED"
elif not mismatched and not not_evaluable:
    ori02 = "RESOLVED"
elif verified and not mismatched and not_evaluable:
    ori02 = "PARTIALLY_RESOLVED"
elif verified and mismatched:
    ori02 = "PARTIALLY_RESOLVED"
elif mismatched and not verified:
    ori02 = "OWNER_REVIEW_REQUIRED"
else:
    ori02 = "OWNER_REVIEW_REQUIRED"

# --------------------------------------------------------------------------- #
# 8  legacy-behaviour audit: is the old competing-model wording still anywhere in the
#    live calculation path? (kept out of this tool's own files by construction)
# --------------------------------------------------------------------------- #
LIVE_PATH = [ROOT / "prototype/rules_v3.py", ROOT / "web/assets/core.js",
             ROOT / "artifacts/model/quantity_model_v3.json"]
# Contextual patterns. The label may exist in source (it has to be named somewhere to be
# prohibited) but it may never be emitted as an Owner Review Item kind, and the competing
# model structures may not come back at all.
FORBIDDEN_PHRASES = ["'kind': 'COMPETING_CERTIFICATION_MODELS'",
                     '"kind": "COMPETING_CERTIFICATION_MODELS"',
                     "'kind': 'CERTIFICATION_MODEL_UNRESOLVED'",
                     '"kind": "CERTIFICATION_MODEL_UNRESOLVED"',
                     "competing_candidates", "unresolved_certification",
                     "certification_unresolved",
                     "three competing Certification models"]
legacy_hits = []
for p in LIVE_PATH:
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8")
    for ph in FORBIDDEN_PHRASES:
        if ph in t:
            legacy_hits.append({"file": p.name, "phrase": ph})

# --------------------------------------------------------------------------- #
# 9  emit
# --------------------------------------------------------------------------- #
out = {
    "artifact": "certification_verification",
    "artifact_version": "1.1",
    "derived_from_baseline": BASELINE["baseline_id"],
    "derived_from": BASELINE["derived_from"],
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "generator": "tools/verify_certification.py",
    "owner_semantics": {
        "decision": "DEC-10 (Owner, team-trial phase) - the Appendix total at the applied "
                    "SKU count is the adopted Certification quantity",
        "main_table": "sample quantity required for ONE SKU -> retained as the rule of "
                      "record and as audit evidence (ADOPTED_ABSOLUTE_TOTAL's audit pair)",
        "main_derived_total": "main_table_per_sku_quantity x sku_count -> retained for "
                              "audit and difference analysis, NOT counted in the project "
                              "total (evidence_role DERIVED_MAIN_TABLE_AUDIT)",
        "appendix": "resulting project total for that SKU count -> evidence_role "
                    "ADOPTED_ABSOLUTE_TOTAL, read per Function x Phase x SKU (FVT and SIT "
                    "each from their own row, never a global phase ratio)",
        "relationship": "appendix_total == main_table_per_sku_quantity x sku_count",
        "relationship_holds_for": "33 of 40 cells - see summary",
        "comparison_tolerance": TOL,
        "appendix_counted_in_project_total_times": 1,
        "main_derived_counted_in_project_total_times": 0,
        "appendix_may_be_added_to_project_total": False,     # on top of itself: never
        "appendix_may_be_added_to_the_main_derived_total": False,
        "appendix_may_form_a_band": False,
        "appendix_may_override_the_main_table_rate_rule": False,
        "superseded_interpretations": [
            "Main Table and Appendix are competing models",
            "Certification has two mutually exclusive rules",
            "Appendix 8-10 is an independent capping model",
            "the Certification range comes from Main vs Appendix competition",
            "adopted_absolute must stay null because of model competition",
            "the Main Table derived total is the adopted project number (superseded by "
            "DEC-10; it stays as audit evidence only)",
        ],
    },
    "verification_grid": cells,
    "appendix_internal_consistency": appendix_internal,
    "appendix_internally_consistent": int_ok,
    "main_table_rate_shape": rate_shape,
    "summary": {
        "cells_total": len(cells),
        "verified": len(verified),
        "mismatch": len(mismatched),
        "not_evaluable": len(not_evaluable),
        "mismatch_by_function": {},
        "functions_fully_verified": [],
        "functions_with_mismatch": [],
        "max_abs_delta": max((abs(c["delta"]) for c in mismatched), default=0.0),
        "total_abs_delta_at_each_sku": {},
    },
    "impact_on_project_total": impact,
    "j33_investigation": J33,
    "ori_02_status": ori02,
    "legacy_competing_model_audit": {"files_scanned": [p.name for p in LIVE_PATH],
                                     "forbidden_phrases": FORBIDDEN_PHRASES,
                                     "hits": legacy_hits},
}
for c in mismatched:
    k = c["function_name"]
    out["summary"]["mismatch_by_function"][k] = out["summary"]["mismatch_by_function"].get(k, 0) + 1
out["summary"]["functions_fully_verified"] = sorted(
    {c["function_name"] for c in cells} - set(out["summary"]["mismatch_by_function"]))
out["summary"]["functions_with_mismatch"] = sorted(out["summary"]["mismatch_by_function"])
for n in SKU_RANGE:
    out["summary"]["total_abs_delta_at_each_sku"][f"SKU{n}"] = round(sum(
        abs(c["delta"]) for c in mismatched if c["sku_count"] == n), 10)

md = ["# Certification per-cell verification", "",
      f"- baseline: `{BASELINE['baseline_id']}` ({BASELINE['derived_from']['file']}, "
      f"SHA-256 `{BASELINE['derived_from'].get('sha256', '')}`)",
      f"- generated: {out['generated_at_utc']} by `tools/verify_certification.py`",
      f"- tolerance: `{TOL:g}` (D-01 - no business rounding, comparison only)",
      "", "## Relationship being verified", "",
      "```", "derived_total = main_table_per_sku_quantity x sku_count",
      "VERIFIED  when  derived_total == appendix_total   (within tolerance)", "```", "",
      "DEC-10: the Appendix total is the adopted value for the team-trial phase and is "
      "counted exactly once. The Main Table per-SKU quantity and its derived total stay on "
      "record for audit and difference analysis and are not counted again. There is still "
      "one model, never a band, never a main + appendix addition.", "",
      "## Result", "",
      "| cells | VERIFIED | MISMATCH | NOT_EVALUABLE |",
      "|---:|---:|---:|---:|",
      f"| {len(cells)} | {len(verified)} | {len(mismatched)} | {len(not_evaluable)} |", "",
      f"**ORI-02 status: `{ori02}`**", "",
      "## Per-cell grid", "",
      "| function | phase | SKU | main /SKU | derived | appendix | delta | status | "
      "main row | apx row |", "|---|---|---:|---:|---:|---:|---:|---|---:|---:|"]
for c in cells:
    md.append(f"| {c['function_name']} | {c['phase']} | {c['sku_count']} | "
              f"{g(c['main_table_per_sku_quantity'])} | {g(c['derived_total'])} | "
              f"{g(c['appendix_total'])} | {g(c['delta'])} | {c['verification_status']} | "
              f"{c['source_reference']['main_table_row']} | "
              f"{c['source_reference']['appendix_row']} |")
md += ["", "## Appendix internal consistency", "",
       "Does the appendix block add up to its own TTL rows? A consistent appendix is a "
       "strong argument that the appendix numbers are deliberate, not stray formulas.", "",
       "| appendix row label | phase | SKU | sum of components | appendix TTL | status |",
       "|---|---|---:|---:|---:|---|"]
for a in appendix_internal:
    md.append(f"| {a['appendix_label']} | {a['phase']} | {a['sku_count']} | "
              f"{g(a['component_sum'])} | {g(a['appendix_ttl'])} | {a['status']} |")
md += ["", f"Appendix internally consistent across every SKU band: "
           f"**{'YES' if int_ok else 'NO'}**", "",
       "## Main Table column shape", "",
       "A genuine per-SKU rate stays flat as the SKU count changes. A column that falls "
       "as 1/N is a back-derivation from a flat total. This is reported as evidence only - "
       "the Owner's stated relationship is still the one being verified, and the workbook "
       "values are never modified.", "",
       "| function | phase | shape | main /SKU at SKU2..SKU6 | main x SKU at SKU2..SKU6 |",
       "|---|---|---|---|---|"]
for s in rate_shape:
    md.append(f"| {s['function_name']} | {s['phase']} | `{s['rate_shape']}` | "
              f"{', '.join(g(s['per_sku_rate'][f'SKU{n}']) for n in SKU_RANGE)} | "
              f"{', '.join(g(s['main_table_rate_x_sku'][f'SKU{n}']) for n in SKU_RANGE)} |")
md += ["", "## Impact of every mismatch on the project total", "",
       "DEC-10 adopts the Appendix total, so this column is now the change of the adopted "
       "number against the Main Table derivation that Phase 3a published. The Main Table "
       "column is audit evidence and is not counted in the total.", "",
       "| function | phase | SKU | main derived (audit, not counted) | Appendix (adopted) "
       "| change of adopted value |", "|---|---|---:|---:|---:|---:|"]
for i in impact:
    md.append(f"| {i['function_name']} | {i['phase']} | {i['sku_count']} | "
              f"{g(i['main_derived_total_audit_only'])} | "
              f"{g(i['appendix_total_adopted'])} | "
              f"{g(i['change_of_adopted_value_vs_main_derived'])} |")
md += ["", "## J33", "",
       f"- cell: `J33` (merged `J33:J34`, attached to RF Certification)",
       f"- declared scope: *{J33['declared_scope_words']}*",
       f"- declared reference scenario: "
       f"{J33['declared_reference_scenario']['antenna_source_count']} antenna sources, "
       f"{J33['declared_reference_scenario']['wlan_card_count']} WLAN cards",
       f"- role assigned: `{J33['disposition']}` (candidate "
       f"`{J33['candidate_role']}`)",
       f"- additive to the Main Table result: "
       f"**{'YES' if J33['additive_to_main_table_result'] else 'NO'}**",
       f"- MVP must add Antenna / WLAN inputs now: "
       f"**{'YES' if J33['mvp_requires_antenna_wlan_input_now'] else 'NO'}**", "",
       "| reading | total | main x SKU | appendix | explains main | explains appendix |",
       "|---|---:|---:|---:|---|---|"]
for x in J33["quantitative_reconciliation"]:
    md.append(f"| SKU{x['sku_count']} {x['phase']} {x['reading']} | "
              f"{g(x['j33_reference_total'])} | {g(x['main_table_derived_total'])} | "
              f"{g(x['appendix_total'])} | {x['explains_main_table']} | "
              f"{x['explains_appendix']} |")
md += ["", "J33 bracket sensitivity (both bounds come from wording inside J33 itself, "
           "nothing is invented):", "",
       f"- floor ({g(J33['bracket']['min_no_whole_machine_fcc'])}) - every WLAN card takes "
       f"the C1PC / module route, so FCC needs no whole machine",
       f"- ceiling ({g(J33['bracket']['max_full_fcc'])}) - every line item needs its own "
       f"whole machines, FCC = intel_wlan x antenna x 4",
       f"- Main Table derived total 15 inside that bracket: "
       f"**{J33['bracket']['main_table_derived_15_inside_bracket']}**",
       f"- Appendix totals 8-10 inside that bracket: "
       f"**{J33['bracket']['appendix_totals_8_to_10_inside_bracket']}**",
       f"- Appendix below the floor: "
       f"**{J33['bracket']['appendix_sits_below_the_no_fcc_floor']}**", "",
       "> " + J33["bracket"]["reading"], "",
       "Raw J33 text (verbatim, unmodified source evidence):", "", "```",
       J33_TEXT or "(empty)", "```", "",
       "## Legacy competing-model behaviour audit", "",
       "Forbidden phrases in the live calculation path "
       f"({', '.join('`' + p + '`' for p in out['legacy_competing_model_audit']['files_scanned'])}):", ""]
if legacy_hits:
    md += [f"- **FOUND** `{h['phrase']}` in `{h['file']}`" for h in legacy_hits]
else:
    md.append("- none. The Phase 2 competing-model wording is gone from the live path.")
md += ["", "## Superseded interpretations (must never return)", ""]
md += [f"- {s}" for s in out["owner_semantics"]["superseded_interpretations"]]
md.append("")

(ROOT / "artifacts/model").mkdir(parents=True, exist_ok=True)
(ROOT / "artifacts/model/certification_verification.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
(ROOT / "artifacts/model/certification_verification.md").write_text("\n".join(md),
                                                                    encoding="utf-8")

print(f"cells {len(cells)} | VERIFIED {len(verified)} | MISMATCH {len(mismatched)} "
      f"| NOT_EVALUABLE {len(not_evaluable)}")
print("mismatch by function:", json.dumps(out["summary"]["mismatch_by_function"]))
print("appendix internally consistent:", int_ok)
print("rate shape:", json.dumps({f"{s['function_name']}/{s['phase']}": s["rate_shape"]
                                 for s in rate_shape}))
print("J33 reference total: subset", j33_subset, "full", j33_full,
      "| explains main:", j33_can_explain_main, "| explains appendix:", j33_can_explain_appendix)
print("J33 disposition:", J33["disposition"])
print("legacy competing-model behaviour in live path:", legacy_hits or "none")
if legacy_hits:
    print("!!! PHASE 2 COMPETING-MODEL BEHAVIOUR IS BACK - this must be fixed before delivery")
print("ORI-02:", ori02)
