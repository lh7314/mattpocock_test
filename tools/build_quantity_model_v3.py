#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_quantity_model_v3 - Quantity Model rebuilt under the Owner's corrected
Certification semantics (deliverable D of
TASK-GAMING-NRE-SAMPLE-REQUIREMENT-CERTIFICATION-CORRECTION-AND-WEB-MVP-01).

Everything Phase 2 established and this task does not correct is carried over
verbatim: MEPA / HW PA stay PER_PHASE_FIXED candidates, EMC Test / NV / INTEL stay
PER_SKU_RATE with their open model questions, and the DEC-06 embedded-reuse signal is
carried over unchanged.

What changes, and only for the Certification Functions:

  Main Table -> quantity_model = PER_SKU_RATE,
                adopted_absolute = per-SKU quantity x sku_count,
                evidence_role    = PRIMARY_QUANTITY_MODEL
  Appendix   -> evidence_role = DERIVED_TOTAL_VALIDATION. It validates the
                multiplication relationship. It is never a second rule, never forms a
                band, never overrides the rate, is not a capping model and is never
                added to a project total a second time.
  J33        -> evidence_role = BREAKDOWN_EVIDENCE, additive = false.

No business number is hand-typed. Every value is read from
  artifacts/model/baseline_v1.json
  artifacts/model/quantity_model_v2.json           (carry-over of the PA decisions)
  artifacts/model/certification_verification.json  (per-cell verification)

Writes only under artifacts/model/. Never original_documents.
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:\GAMING_NRE_AGENT")
SRC_DIR = ROOT / "original_documents"
BASELINE = json.loads((ROOT / "artifacts/model/baseline_v1.json").read_text(encoding="utf-8"))
V2 = json.loads((ROOT / "artifacts/model/quantity_model_v2.json").read_text(encoding="utf-8"))
CERTV = json.loads((ROOT / "artifacts/model/certification_verification.json")
                   .read_text(encoding="utf-8"))

TOL = 1e-9
SKUS = ("SKU2", "SKU3", "SKU4", "SKU5", "SKU6")
FUNCS = {f["function_id"]: f for f in BASELINE["functions"]}
V2CELL = {(c["function_id"], c["phase"]): c for c in V2["cells"]}
CV = {(c["function_id"], c["phase"], c["sku_count"]): c
      for c in CERTV["verification_grid"]}
SHAPE = {(s["function_id"], s["phase"]): s for s in CERTV["main_table_rate_shape"]}

QUANTITY_MODELS = ("PER_SKU_RATE", "PER_PHASE_FIXED", "PER_PROJECT_FIXED",
                   "FORMULA_DRIVEN", "UNRESOLVED")
EVIDENCE_ROLES = ("PRIMARY_QUANTITY_MODEL", "DERIVED_TOTAL_VALIDATION",
                  "BREAKDOWN_EVIDENCE", "ABSOLUTE_RESTATEMENT", "UNRESOLVED_COMMENT")


def guard(path: Path) -> Path:
    rp = path.resolve()
    if str(rp).startswith(str(SRC_DIR.resolve())):
        raise RuntimeError(f"refusing to write inside original_documents: {rp}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# --------------------------------------------------------------------------- #
# cell table
# --------------------------------------------------------------------------- #
MQ = {(q["function_id"], q["phase"]) for q in V2["model_questions"]}
cells = []
for v2c in V2["cells"]:
    fid, phase = v2c["function_id"], v2c["phase"]
    f = FUNCS[fid]
    c = dict(v2c)                                     # carry Phase 2 over untouched
    c.pop("competing_sources", None)
    c.pop("competing_candidates", None)
    c["evidence_role"] = "PRIMARY_QUANTITY_MODEL"
    c["validation"] = None
    c["breakdown_evidence"] = None
    c["main_table_per_sku_quantity"] = {
        sk: f["per_sku_rate"][phase][sk] for sk in SKUS}

    if f["category"] == "CERT":
        adopted, verif = {}, {}
        for n in SKUS:
            k = int(n.replace("SKU", ""))
            cell = CV[(fid, phase, k)]
            adopted[n] = cell["derived_total"]
            verif[n] = {"main_table_per_sku_quantity": cell["main_table_per_sku_quantity"],
                        "derived_total": cell["derived_total"],
                        "appendix_label": cell["appendix_label"],
                        "appendix_total": cell["appendix_total"],
                        "delta": cell["delta"],
                        "verification_status": cell["verification_status"],
                        "appendix_row": cell["source_reference"]["appendix_row"],
                        "main_table_row": cell["source_reference"]["main_table_row"]}
        statuses = sorted({verif[n]["verification_status"] for n in SKUS})
        c.update({
            "quantity_model": "PER_SKU_RATE",
            "scaling_shape": SHAPE[(fid, phase)]["rate_shape"],
            "value_access": "MAIN_TABLE_DERIVED",
            "adopted_absolute": adopted,
            "adopted_source": "MAIN_TABLE_PER_SKU_RATE_TIMES_SKU",
            "validation": {
                "evidence_role": "DERIVED_TOTAL_VALIDATION",
                "block": "certification_block2",
                "appendix_row": verif["SKU2"]["appendix_row"],
                "relationship": "appendix_total == main_table_per_sku_quantity x sku_count",
                "comparison_tolerance": TOL,
                "per_sku": verif,
                "statuses": statuses,
                "fully_verified": statuses == ["VERIFIED"],
                "counted_in_project_total": False,
                "may_form_a_band": False,
            },
            "owner_review_required": statuses != ["VERIFIED"],
            "evidence_basis": [
                "Owner semantics: the Main Table states the quantity needed for ONE SKU; "
                "the Appendix states the resulting total for that SKU count",
                "Appendix is validation evidence only (DERIVED_TOTAL_VALIDATION): never a "
                "second model, never merged, never re-added to the total",
            ],
            "status": ("CONFIRMED_BY_SOURCE_VALIDATION" if statuses == ["VERIFIED"]
                       else "DRAFT_PENDING_OWNER"),
            "phase2_superseded": {
                "quantity_model": v2c["quantity_model"],
                "adopted_source": v2c["adopted_source"],
                "competing_sources": v2c.get("competing_sources", []),
                "formula_candidate_retired": bool(v2c.get("formula_candidate")),
                "reason": "Phase 2 treated the Main Table, the Appendix and J33 as three "
                          "competing models and left the cell UNRESOLVED. The Owner has "
                          "since stated they are one model plus its own validation.",
            },
        })
        if fid == "F_RF_CERTIFICATION":
            j = CERTV["j33_investigation"]
            c["breakdown_evidence"] = {
                "evidence_role": "BREAKDOWN_EVIDENCE",
                "source_cell": j["cell"],
                "disposition": j["disposition"],
                "additive_to_main_table_result": False,
                "explains_main_table_quantity":
                    j["findings"]["explains_main_table_quantity"],
                "explains_appendix_total": j["findings"]["explains_appendix_total"],
                "declared_reference_scenario": j["declared_reference_scenario"],
                "bracket": j["bracket"],
                "antenna_wlan_are": j["findings"]["antenna_and_wlan_are"],
                "already_inside_main_table_rate":
                    j["findings"]["already_inside_main_table_rate"],
                "double_count_risk_if_added": j["findings"]["double_count_risk_if_added"],
                "mvp_requires_antenna_wlan_input_now":
                    j["mvp_requires_antenna_wlan_input_now"],
                "raw_text": j["raw_text"],
                "reference_total_under_readings": j["reference_total_under_readings"],
            }
        c["formula_candidate"] = None                 # J33 is evidence, never a candidate
    c["rule_id"] = f"QM3:{fid}:{phase}"
    cells.append(c)

by_model: dict[str, int] = {}
by_access: dict[str, int] = {}
by_role: dict[str, int] = {}
for c in cells:
    by_model[c["quantity_model"]] = by_model.get(c["quantity_model"], 0) + 1
    by_access[c["value_access"]] = by_access.get(c["value_access"], 0) + 1
    by_role[c["evidence_role"]] = by_role.get(c["evidence_role"], 0) + 1

cert_cells = [c for c in cells if FUNCS[c["function_id"]]["category"] == "CERT"]
model = {
    "model_id": "QMODEL-V3",
    "model_version": "3.0",
    "supersedes": f"{V2['model_id']}/{V2['model_version']}",
    "derived_from_baseline": BASELINE["baseline_id"],
    "derived_from": BASELINE["derived_from"],
    "status": "DRAFT_PENDING_OWNER",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "generator": "tools/build_quantity_model_v3.py",
    "quantity_model_enum": list(QUANTITY_MODELS),
    "evidence_role_enum": list(EVIDENCE_ROLES),
    "policy": {
        "rounding": "NONE (D-01) - every underlying value keeps its original decimal",
        "comparison_tolerance": TOL,
        "display_precision_never_modifies_values": True,
        "pseudo_rate_models": "PROHIBITED (no divide-by-SKU-then-multiply-back)",
        "flat_shape_alone_is_not_evidence_for_PER_PHASE_FIXED": True,
        "certification_model": "PER_SKU_RATE from the Main Table",
        "certification_relationship":
            "appendix_total == main_table_per_sku_quantity x sku_count",
        "certification_appendix_role": "DERIVED_TOTAL_VALIDATION - validation only",
        "certification_appendix_may_be_added_to_total": False,
        "certification_appendix_may_form_a_band": False,
        "certification_appendix_may_override_main_table": False,
        "certification_appendix_is_a_capping_model": False,
        "certification_j33_role": "BREAKDOWN_EVIDENCE - explanatory, never additive",
        "certification_global_phase_ratio": "PROHIBITED - FVT and SIT read their own row",
        "certification_band_origin_after_correction": "SKU_NOT_ESTABLISHED only",
        "superseded_certification_interpretations":
            CERTV["owner_semantics"]["superseded_interpretations"],
        "panel_annotation_d2_h2": "UNRESOLVED_COMMENT - excluded from calculation (DEC-02)",
        "wave": "explicit per-spec assignment only; never a fixed quantity or ratio (DEC-04)",
        "reuse": "only a proven ADDITIONAL_CONFIRMED_REUSE deducts (DEC-06)",
        "mepa_hw_pa": "PER_PHASE_FIXED candidate model retained from Phase 2, shown as "
                      "temporary pending business confirmation (ORI-10)",
    },
    "cells": cells,
    "contested_cells": [c["rule_id"] for c in cells if c.get("conflicting_skus")],
    "model_questions": V2["model_questions"],
    "baseline_embedded_sharing": V2["baseline_embedded_sharing"],
    "certification_verification_ref": "artifacts/model/certification_verification.json",
    "summary": {
        "cells_total": len(cells),
        "by_quantity_model": by_model,
        "by_value_access": by_access,
        "by_evidence_role": by_role,
        "owner_review_cells": sum(1 for c in cells if c["owner_review_required"]),
        "certification_cells": len(cert_cells),
        "certification_fully_verified_cells":
            sum(1 for c in cert_cells if c["validation"]["fully_verified"]),
        "certification_cells_with_mismatch":
            sum(1 for c in cert_cells if not c["validation"]["fully_verified"]),
        "model_questions": len(V2["model_questions"]),
        "embedded_sharing_suspected_functions":
            V2["summary"]["embedded_sharing_suspected_functions"],
        "ori_02_status": CERTV["ori_02_status"],
        "temporary_model_cells": sum(1 for c in cells
                                     if c["quantity_model"] == "PER_PHASE_FIXED"),
    },
}

guard(ROOT / "artifacts/model/quantity_model_v3.json").write_text(
    json.dumps(model, ensure_ascii=False, indent=1), encoding="utf-8")

# --------------------------------------------------------------------------- #
# markdown view
# --------------------------------------------------------------------------- #
j33c = next(c for c in cert_cells if c["breakdown_evidence"])
L = ["# Quantity Model v3 - Certification corrected", "",
     f"- supersedes `{model['supersedes']}`",
     f"- baseline `{BASELINE['baseline_id']}` from `{BASELINE['derived_from']['file']}`",
     f"- status **{model['status']}** | ORI-02 **{CERTV['ori_02_status']}**",
     "- generated by `tools/build_quantity_model_v3.py`", "",
     "## What changed against Phase 2", "",
     "| | Phase 2 (QMODEL-V2) | Phase 3 (QMODEL-V3) |", "|---|---|---|",
     f"| Certification Quantity Model | `UNRESOLVED` on all {len(cert_cells)} cells | "
     f"`PER_SKU_RATE` on all {len(cert_cells)} cells |",
     "| Main Table vs Appendix | two competing models, band published | one model plus "
     "its own validation |",
     "| adopted_absolute | null because of the competition | per-SKU quantity x SKU |",
     "| Appendix role | competing evidence priced as its own variant | "
     "`DERIVED_TOTAL_VALIDATION`, never added to a total |",
     "| J33 | third competing model, non-evaluable candidate | `BREAKDOWN_EVIDENCE`, "
     "never additive |",
     "| Certification demand output | always a band | single value; a range only when the "
     "SKU answer itself is a range |",
     "| Range reason | `CERTIFICATION_MODEL_UNRESOLVED` | `SKU_NOT_ESTABLISHED` only |",
     "| MEPA / HW PA | `PER_PHASE_FIXED` candidates | **unchanged** |",
     "| EMC Test / NV / INTEL | `PER_SKU_RATE` + model questions | **unchanged** |",
     "| Reuse / Wave / Panel semantics | DEC-06 / DEC-04 / DEC-02 | **unchanged** |", "",
     "## Distribution", "", "```json",
     json.dumps(model["summary"], ensure_ascii=False, indent=1), "```", "",
     "## Certification cells", "",
     "| Function | Phase | model | per-SKU qty SKU2..6 | adopted total SKU2..6 | "
     "appendix verification | review |", "|---|---|---|---|---|---|---|"]
for c in cert_cells:
    L.append(f"| {c['function_name']} | {c['phase']} | `{c['quantity_model']}` | "
             f"{', '.join(str(c['main_table_per_sku_quantity'][s]) for s in SKUS)} | "
             f"{', '.join(str(c['adopted_absolute'][s]) for s in SKUS)} | "
             f"{'/'.join(c['validation']['statuses'])} | "
             f"{'YES' if c['owner_review_required'] else 'no'} |")
L += ["", "## Appendix validation detail (every cell, never a total alone)", "",
      "| Function | Phase | SKU | main /SKU | x SKU = derived | appendix | delta | status |",
      "|---|---|---:|---:|---:|---:|---:|---|"]
for c in cert_cells:
    for n in SKUS:
        v = c["validation"]["per_sku"][n]
        L.append(f"| {c['function_name']} | {c['phase']} | {int(n[3:])} | "
                 f"{v['main_table_per_sku_quantity']} | {v['derived_total']} | "
                 f"{v['appendix_total']} | {v['delta']} | {v['verification_status']} |")
L += ["", "## Non-Certification cells (carried over from Phase 2)", "",
      "| Function | Phase | model | adopted SKU2..6 | why |", "|---|---|---|---|---|"]
for c in cells:
    if FUNCS[c["function_id"]]["category"] == "CERT":
        continue
    why = ("absolute restatement in the secondary PA table - read as an absolute, "
           "never as a pseudo rate (temporary, ORI-10)"
           if c["quantity_model"] == "PER_PHASE_FIXED" else
           ("flat total but no independent evidence - model question open"
            if (c["function_id"], c["phase"]) in MQ else "main table per-SKU rate"))
    L.append(f"| {c['function_name']} | {c['phase']} | `{c['quantity_model']}` | "
             f"{', '.join(str(c['adopted_absolute'][s]) for s in SKUS)} | {why} |")
L += ["", "## J33", "",
      f"- source cell: `{j33c['breakdown_evidence']['source_cell']}` "
      f"(merged `J33:J34`, RF Certification)",
      f"- disposition: **`{j33c['breakdown_evidence']['disposition']}`**",
      f"- additive to the Main Table result: "
      f"**{'YES' if j33c['breakdown_evidence']['additive_to_main_table_result'] else 'NO'}**",
      f"- explains the Main Table per-SKU quantity: "
      f"**{j33c['breakdown_evidence']['explains_main_table_quantity']}**",
      f"- explains the Appendix total: "
      f"**{j33c['breakdown_evidence']['explains_appendix_total']}**",
      f"- bracket from J33's own wording: "
      f"{j33c['breakdown_evidence']['bracket']['min_no_whole_machine_fcc']:g} .. "
      f"{j33c['breakdown_evidence']['bracket']['max_full_fcc']:g}",
      f"- {j33c['breakdown_evidence']['double_count_risk_if_added']}", "",
      "## Model questions still open (never promoted on shape alone)", ""]
L += [f"- {q['function_name']} / {q['phase']} - {q['issue']}" for q in V2["model_questions"]]
L += ["", "## Superseded interpretations (must never return)", ""]
L += [f"- {s}" for s in model["policy"]["superseded_certification_interpretations"]]
L.append("")
guard(ROOT / "artifacts/model/quantity_model_v3.md").write_text("\n".join(L),
                                                                encoding="utf-8")

print("cells", len(cells), "| by model", json.dumps(by_model),
      "| by role", json.dumps(by_role))
print("cert fully verified", model["summary"]["certification_fully_verified_cells"],
      "of", len(cert_cells), "| with mismatch",
      model["summary"]["certification_cells_with_mismatch"])
print("owner_review_cells", model["summary"]["owner_review_cells"],
      "| model_questions", len(V2["model_questions"]),
      "| embedded_sharing functions",
      len(model["summary"]["embedded_sharing_suspected_functions"]))
print("J33:", j33c["breakdown_evidence"]["disposition"], "| bracket",
      json.dumps(j33c["breakdown_evidence"]["bracket"], ensure_ascii=False)[:120])
print("ORI-02:", CERTV["ori_02_status"])
print("wrote artifacts/model/quantity_model_v3.json / .md")
