#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 / Deliverable D  -  Quantity Model derivation (evidence driven).

Reads artifacts/model/baseline_v1.json only. No hand-typed business numbers.

Owner decisions implemented
  DEC-05  every cell is no longer a "per-SKU rate". Supported models:
          PER_SKU_RATE / PER_PHASE_FIXED / PER_PROJECT_FIXED /
          FORMULA_DRIVEN / UNRESOLVED.
          MEPA and HW PA become PER_PHASE_FIXED *candidates* on the strength of
          the secondary PA table + the remark text, and the engine must read the
          absolute value straight out of the table (never rate -> /SKU -> *SKU).
  DEC-03  Certification: Main Table, Secondary Table and the J33 formula are
          kept as three independent competing evidence items. Nothing is
          auto-selected and nothing is merged; the cell is marked UNRESOLVED and
          OWNER_REVIEW_REQUIRED.

A flat derived total is NOT, by itself, promoted to PER_PHASE_FIXED - it is only
recorded as an "embedded sharing" signal used by the Reuse Protection Contract
(DEC-06) and as an open model question.

Writes only under artifacts/. Never original_documents.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "artifacts" / "model" / "baseline_v1.json"
OUT_JSON = ROOT / "artifacts" / "model" / "quantity_model_v2.json"
OUT_MD = ROOT / "artifacts" / "model" / "quantity_model_v2.md"
SRC_DIR = ROOT / "original_documents"

TOL = 1e-9
SKUS = ("SKU2", "SKU3", "SKU4", "SKU5", "SKU6")
PHASES = ("FVT", "SIT")

CERT_CATEGORY = "CERT"

# function_id -> (secondary block, label used inside that block)
SECONDARY_MAP = {
    "F_EMC":              ("certification_block2", "EMC"),
    "F_GREEN":            ("certification_block2", "Green"),
    "F_SAFETY":           ("certification_block2", "Safety"),
    "F_RF_CERTIFICATION": ("certification_block2", "RF Cert"),
    "F_SWPA":             ("pa_block2", "SWPA"),
    "F_MEPA":             ("pa_block2", "MEPA"),
    "F_HW_PA":            ("pa_block2", "HW PA"),
}

# text in Status/Purpose/Remark that states an absolute per-phase allocation
FIXED_PHASE_PATTERNS = [
    r"phase\s*(\d+)\s*unit",          # "CS: 1 phase 36 units"
    r"(\d+)\s*-\s*(\d+)\s*unit\s*one\s*phase",   # "TTL3-4unit one phase"
    r"one\s*phase\s*(\d+)\s*unit",
]

FORMULA_DECLARATIONS = {
    "F_RF_CERTIFICATION": {
        "source_cell": "J33",
        "declared_inputs": ["antenna_source_count", "wlan_card_count", "intel_wlan_count"],
        "status": "INPUTS_UNAVAILABLE_IN_MVP",
        "note": "J33 states an antenna x WLAN driven demand; MVP key factors do not "
                "carry antenna / WLAN card counts, so the formula cannot be evaluated.",
    }
}


def guard(path: Path) -> Path:
    rp = path.resolve()
    if str(rp).startswith(str(SRC_DIR.resolve())):
        raise RuntimeError(f"refusing to write inside original_documents: {rp}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def feq(a, b, tol=TOL) -> bool:
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tol


def is_constant(vals) -> bool:
    known = [v for v in vals if v is not None]
    return bool(known) and all(feq(v, known[0]) for v in known)


def classify_shape(vals):
    known = [v for v in vals if v is not None]
    if len(known) < 2:
        return "INSUFFICIENT"
    if is_constant(vals):
        return "CONSTANT"
    lo, hi = min(known), max(known)
    diffs = [known[i + 1] - known[i] for i in range(len(known) - 1)]
    monotonic_up = all(d >= -TOL for d in diffs)
    if hi - lo <= 1.0 + TOL:
        return "NEAR_FLAT_WITH_DIP" if not monotonic_up else "NEAR_FLAT"
    return "RAMP" if monotonic_up else "IRREGULAR"


def fixed_phase_text_hits(*texts):
    hits = []
    for t in texts:
        if not t:
            continue
        for pat in FIXED_PHASE_PATTERNS:
            hits += re.findall(pat, str(t), re.I)
    return hits


def main() -> int:
    b = json.loads(SRC.read_text(encoding="utf-8"))
    sec = b["secondary_tables"]

    sec_abs, sec_rows = {}, {}
    for block, body in sec.items():
        for r in body["rows"]:
            label = r["label"]
            if label.startswith("TTL"):
                continue
            func, phase = label.rsplit(" ", 1)
            key = (block, func, phase)
            sec_abs[key] = {s: r.get(s) for s in SKUS}
            sec_rows[key] = r["row"]

    cells, contested, model_questions = [], [], []

    for f in b["functions"]:
        fid, name, cat = f["function_id"], f["name"], f["category"]
        mapping = SECONDARY_MAP.get(fid)
        for phase in PHASES:
            main_abs = {s: f["ttl_per_phase"][phase].get(s) for s in SKUS}
            skey = (mapping[0], mapping[1], phase) if mapping else None
            sec_a = sec_abs.get(skey) if skey else None

            adopted = dict(main_abs)
            deltas, conflict_skus, near_round = {}, [], []
            raw_disagreement = False
            if sec_a:
                for s in SKUS:
                    m, a = main_abs[s], sec_a[s]
                    d = None if (m is None or a is None) else round(float(a) - float(m), 9)
                    deltas[s] = d
                    if d is None or abs(d) <= TOL:
                        continue
                    raw_disagreement = True
                    # integer restatement of the same quantity (|d| < 0.5): adopt the
                    # stated absolute, model is unchanged, still recorded as evidence
                    if abs(d) < 0.5 and feq(round(float(m)), float(a)):
                        adopted[s] = float(a)
                        near_round.append(s)
                    else:
                        conflict_skus.append(s)

            shape = classify_shape(list(adopted.values()))
            txt_hits = fixed_phase_text_hits(f.get("remark_text"), f.get("status_text"),
                                             f.get("purpose_text"))
            formula = FORMULA_DECLARATIONS.get(fid) if phase == "SIT" else None

            # ---------- evidence-driven Quantity Model ----------------------
            # A flat derived total is NOT enough to claim a fixed allocation.
            # Promotion requires an independent absolute restatement or remark text.
            evidence = []
            all_int_sec = bool(sec_a) and all(
                v is not None and feq(round(float(v)), float(v)) for v in sec_a.values())

            if cat == CERT_CATEGORY:
                qm = "UNRESOLVED"
                evidence.append("DEC-03: Main Table / Secondary Table / J33 formula are "
                                "three competing evidence items - no auto-selection, no merge")
            elif sec_a and is_constant(list(sec_a.values())):
                qm = "PER_PHASE_FIXED"
                evidence.append(f"absolute restatement row {sec_rows[skey]} is the same for "
                                f"SKU2-6 -> allocation is per phase, not per SKU")
            elif sec_a and all_int_sec and raw_disagreement:
                qm = "PER_PHASE_FIXED"
                evidence.append(f"absolute restatement row {sec_rows[skey]} is integer-valued "
                                f"and disagrees with rate x SKU -> the main-table value is a "
                                f"derived pseudo-rate (divide by SKU, multiply back)")
            elif txt_hits:
                qm = "PER_PHASE_FIXED"
                evidence.append(f"Status/Purpose/Remark states an absolute per-phase "
                                f"quantity {txt_hits}")
            elif shape == "CONSTANT":
                qm = "PER_SKU_RATE"
                model_questions.append({
                    "function_id": fid, "function_name": name, "phase": phase,
                    "issue": "derived total is constant across SKU2-6, but there is no "
                             "independent evidence that the allocation is fixed per phase",
                    "candidate_models": ["PER_SKU_RATE", "PER_PHASE_FIXED"],
                    "note": "NOT promoted to PER_PHASE_FIXED on shape alone; "
                            "also feeds the DEC-06 embedded-reuse signal",
                })
            else:
                qm = "PER_SKU_RATE"

            if formula:
                qm = "UNRESOLVED"
                evidence.append("FORMULA_DRIVEN candidate declared in J33 but its required "
                                "inputs (antenna / WLAN card counts) are not MVP key factors")

            # ---------- adopted value / competing candidates -----------------
            if qm == "UNRESOLVED":
                adopted = {s: None for s in SKUS}          # nothing is auto-selected
                adopted_source = "NONE_UNRESOLVED"
                competing = {k: v for k, v in (("MAIN_TABLE", main_abs),
                                               ("SECONDARY_TABLE", sec_a)) if v}
                if formula:
                    competing["J33_FORMULA"] = {"evaluable": False,
                                                "declared_inputs": formula["declared_inputs"]}
            elif qm == "PER_PHASE_FIXED" and sec_a:
                adopted = dict(sec_a)
                adopted_source = "SECONDARY_ABSOLUTE_TABLE"
                competing = {"MAIN_TABLE": main_abs} if raw_disagreement else {}
            else:
                adopted = dict(main_abs)
                adopted_source = "MAIN_TABLE"
                competing = {"SECONDARY_TABLE": sec_a} if (sec_a and raw_disagreement) else {}

            candidates = {s: {k: (v.get(s) if isinstance(v, dict) else None)
                              for k, v in competing.items()} for s in SKUS}

            # values the engine is allowed to read directly (no rate round-trip)
            read_direct = qm in ("PER_PHASE_FIXED", "PER_PROJECT_FIXED", "UNRESOLVED")

            owner_review = bool(conflict_skus) or cat == CERT_CATEGORY or bool(formula) \
                or qm == "PER_PHASE_FIXED" or bool(near_round)

            cell = {
                "function_id": fid,
                "function_name": name,
                "category": cat,
                "phase": phase,
                "quantity_model": qm,
                "scaling_shape": shape,
                "value_access": "ABSOLUTE_TABLE_READ" if read_direct else "MAIN_TABLE_DERIVED",
                "adopted_absolute": adopted,
                "adopted_source": adopted_source,
                "competing_sources": [k for k in competing],
                "competing_candidates": candidates,
                "main_table_absolute": main_abs,
                "secondary_table_absolute": sec_a,
                "delta_secondary_minus_main": deltas,
                "conflicting_skus": conflict_skus,
                "integer_restatement_adopted_for": near_round,
                "owner_review_required": owner_review,
                "evidence_basis": evidence,
                "formula_candidate": formula,
                "rule_id": f"QM2:{fid}:{phase}",
                "status": "DRAFT_PENDING_OWNER" if owner_review else "DERIVED_CONSISTENT",
                "evidence": {
                    "source_file": b["derived_from"]["file"],
                    "sheet": b["derived_from"]["sheet"],
                    "main_row": f["source_rows"][phase.lower()],
                    "secondary_row": sec_rows.get(skey) if skey else None,
                    "status_text": f.get("status_text"),
                    "remark_text": f.get("remark_text"),
                },
            }
            cells.append(cell)

            if conflict_skus:
                contested.append({
                    "function_id": fid, "function_name": name, "phase": phase,
                    "quantity_model": qm,
                    "conflicting_skus": conflict_skus,
                    "main_table_absolute": main_abs,
                    "secondary_table_absolute": sec_a,
                    "delta": {s: deltas[s] for s in conflict_skus},
                    "note": "competing evidence - retained separately, NOT auto-selected, "
                            "NOT merged (DEC-03 / DEC-05)",
                })

    # ---------- DEC-06: sharing possibly already inside the baseline ---------
    embedded = {}
    for f in b["functions"]:
        fid = f["function_id"]
        per_phase, overall = {}, "NONE"
        for phase in PHASES:
            known = [f["ttl_per_phase"][phase].get(s) for s in SKUS]
            known = [v for v in known if v is not None]
            if not known:
                continue
            spread = round(max(known) - min(known), 9)
            growth = round(known[-1] - known[0], 9)
            sig = "SUSPECTED" if (spread <= 1.0 + TOL or growth <= TOL) else "NONE"
            per_phase[phase] = {"signal": sig, "spread": spread, "growth": growth}
            if sig == "SUSPECTED":
                overall = "SUSPECTED"
        embedded[fid] = {
            "function_name": f["name"],
            "overall": overall,
            "phases": per_phase,
            "reuse_policy": ("BLOCK_UNLESS_PROVEN" if overall == "SUSPECTED"
                             else "PERMIT_WHEN_CONFIRMED"),
            "reason": ("baseline total does not grow with SKU count -> sharing or scale "
                       "effect is probably already inside the number"
                       if overall == "SUSPECTED" else "baseline total grows with SKU count"),
        }

    out = {
        "model_id": "QMODEL-CS-ODM-002",
        "model_version": "v2.0-draft",
        "derived_from_baseline": b["baseline_id"],
        "derived_from": b["derived_from"],
        "status": "DRAFT_UNCONFIRMED_BY_OWNER",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "tools/derive_quantity_model.py",
        "quantity_model_enum": ["PER_SKU_RATE", "PER_PHASE_FIXED", "PER_PROJECT_FIXED",
                                "FORMULA_DRIVEN", "UNRESOLVED"],
        "policy": {
            "tolerance": TOL,
            "rounding": "NONE (D-01); tolerance used only for comparison, never to alter a business value",
            "flat_shape_alone_promotes_model": False,
            "conflicting_evidence": "RETAINED_SEPARATELY_NOT_MERGED",
            "certification": "UNRESOLVED + OWNER_REVIEW_REQUIRED (Main / Secondary / J33 formula kept apart)",
            "panel_annotation_d2_h2": "UNRESOLVED_COMMENT - excluded from recommendation and from quantity calculation",
            "no_pseudo_rate": "PER_PHASE_FIXED values are read straight from the table; "
                              "the engine must never divide by SKU and multiply back",
        },
        "cells": cells,
        "contested_cells": contested,
        "model_questions": model_questions,
        "baseline_embedded_sharing": embedded,
        "summary": {
            "cells_total": len(cells),
            "by_quantity_model": {},
            "by_value_access": {},
            "owner_review_cells": 0,
            "contested_cells": len(contested),
            "model_questions": len(model_questions),
            "embedded_sharing_suspected_functions": [],
        },
    }
    s = out["summary"]
    for c in cells:
        s["by_quantity_model"][c["quantity_model"]] = s["by_quantity_model"].get(c["quantity_model"], 0) + 1
        s["by_value_access"][c["value_access"]] = s["by_value_access"].get(c["value_access"], 0) + 1
        if c["owner_review_required"]:
            s["owner_review_cells"] += 1
    s["embedded_sharing_suspected_functions"] = sorted(
        v["function_name"] for v in embedded.values() if v["overall"] == "SUSPECTED")

    guard(OUT_JSON).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    L = ["# Quantity Model v2 (evidence driven, machine derived)", "",
         f"- baseline: `{b['baseline_id']}` ({b['status']})",
         f"- source: `{b['derived_from']['file']}` / sheet `{b['derived_from']['sheet']}`",
         f"- status: **{out['status']}**",
         f"- tolerance `{TOL}` - comparison only, D-01 rounding is NONE", "",
         "## Summary", "", "| key | value |", "|---|---|"]
    for k, v in s.items():
        L.append(f"| {k} | {v if not isinstance(v, dict) else json.dumps(v, ensure_ascii=False)} |")

    L += ["", "## Quantity model per (Function, Phase)", "",
          "| Function | Phase | Model | Shape | Value access | Conflicting SKU | Owner Review |",
          "|---|---|---|---|---|---|---|"]
    for c in cells:
        L.append(f"| {c['function_name']} | {c['phase']} | {c['quantity_model']} | "
                 f"{c['scaling_shape']} | {c['value_access']} | "
                 f"{','.join(c['conflicting_skus']) or '-'} | "
                 f"{'YES' if c['owner_review_required'] else ''} |")

    L += ["", "## Adopted absolute values (what the engine reads)", "",
          "Adopted source is shown so every number carries its provenance and interim state.", "",
          "| Function | Phase | Model | Adopted from | SKU2 | SKU3 | SKU4 | SKU5 | SKU6 | Competing |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for c in cells:
        a = c["adopted_absolute"]
        L.append(f"| {c['function_name']} | {c['phase']} | {c['quantity_model']} | "
                 f"{c['adopted_source']} | " +
                 " | ".join(f"{a[k]:g}" if a[k] is not None else "UNRESOLVED" for k in SKUS) +
                 f" | {','.join(c['competing_sources']) or '-'} |")

    L += ["", "## Contested cells - competing evidence kept apart", "",
          "| Function | Phase | SKU | Main Table | Secondary Table | Delta |", "|---|---|---|---|---|---|"]
    for c in contested:
        for sk in c["conflicting_skus"]:
            L.append(f"| {c['function_name']} | {c['phase']} | {sk} | "
                     f"{c['main_table_absolute'][sk]:g} | {c['secondary_table_absolute'][sk]:g} | "
                     f"{c['delta'][sk]:+g} |")

    L += ["", "## Model questions raised (not promoted on shape alone)", "",
          "| Function | Phase | Candidate models | Issue |", "|---|---|---|---|"]
    for q in model_questions:
        L.append(f"| {q['function_name']} | {q['phase']} | {', '.join(q['candidate_models'])} | "
                 f"{q['issue']} |")

    L += ["", "## DEC-06 baseline-embedded sharing signal", "",
          "| Function | signal | FVT spread | FVT growth | SIT spread | SIT growth | reuse policy |",
          "|---|---|---|---|---|---|---|"]
    for fid in sorted(embedded):
        e = embedded[fid]
        if e["overall"] != "SUSPECTED":
            continue
        p = e["phases"]
        L.append(f"| {e['function_name']} | {e['overall']} | {p['FVT']['spread']:g} | "
                 f"{p['FVT']['growth']:+g} | {p['SIT']['spread']:g} | {p['SIT']['growth']:+g} | "
                 f"{e['reuse_policy']} |")
    L += ["", "> SUSPECTED = the baseline total does not grow when SKU count grows, so sharing "
          "or a scale effect is very likely already inside the number. Under DEC-06 a further "
          "manual reuse claim on these Functions is blocked unless the user proves it is not "
          "already in the baseline.", ""]

    guard(OUT_MD).write_text("\n".join(L), encoding="utf-8")
    print(f"[ok] {OUT_JSON}")
    print(f"[ok] {OUT_MD}")
    print(json.dumps(out["summary"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
