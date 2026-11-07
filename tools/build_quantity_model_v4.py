#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_quantity_model_v4 - the same 42 cells with the Certification ADOPTED VALUE switched
to the Appendix total, per the Owner's decision DEC-10 for the MVP / team-trial phase
(TASK-GAMING-NRE-SAMPLE-REQUIREMENT-APPENDIX-ADOPTION-AND-TEAM-TRIAL-01).

QMODEL-V3 (frozen in artifacts/model/quantity_model_v3.json) stays on disk as the record of
Phase 3a, where the Main Table derived total was the adopted number. Nothing in it is
rewritten by this script.

What changes, and only for the 8 Certification cells:

  adopted_absolute            <- the Appendix total for that Function x Phase x SKU
  adopted_source              <- APPENDIX_TABLE_TOTAL
  value_access                <- APPENDIX_TABLE_READ (an absolute read, never a pseudo rate)
  main_table_per_sku_quantity    kept  (audit: the per-SKU rule of record)
  main_table_absolute            kept  (audit: per-SKU quantity x SKU count)
  validation                  -> audit (evidence_role DERIVED_MAIN_TABLE_AUDIT,
                                  counted_in_project_total false)
  evidence_role of the adopted value: ADOPTED_ABSOLUTE_TOTAL

Everything else is carried over untouched: FVT and SIT each keep their own Appendix row (no
global phase ratio), J33 stays BREAKDOWN_EVIDENCE and non-additive, MEPA / HW PA stay
PER_PHASE_FIXED candidates (ORI-10), EMC Test / NV / INTEL keep their model questions, and the
DEC-02 / DEC-04 / DEC-06 / D-01 semantics are unchanged.

No business number is hand-typed: every value is read from
  artifacts/model/quantity_model_v3.json
  artifacts/model/certification_verification.json

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
V3 = json.loads((ROOT / "artifacts/model/quantity_model_v3.json").read_text(encoding="utf-8"))
CERTV = json.loads((ROOT / "artifacts/model/certification_verification.json")
                   .read_text(encoding="utf-8"))

TOL = 1e-9
SKUS = ("SKU2", "SKU3", "SKU4", "SKU5", "SKU6")
FUNCS = {f["function_id"]: f for f in BASELINE["functions"]}
CV = {(c["function_id"], c["phase"], c["sku_count"]): c
      for c in CERTV["verification_grid"]}

EVIDENCE_ROLES = tuple(V3["evidence_role_enum"]) + ("DERIVED_MAIN_TABLE_AUDIT",)
if "ADOPTED_ABSOLUTE_TOTAL" not in EVIDENCE_ROLES:
    EVIDENCE_ROLES = EVIDENCE_ROLES + ("ADOPTED_ABSOLUTE_TOTAL",)

ADOPTED_ROLE = "ADOPTED_ABSOLUTE_TOTAL"
AUDIT_ROLE = "DERIVED_MAIN_TABLE_AUDIT"


def guard(path: Path) -> Path:
    rp = path.resolve()
    if str(rp).startswith(str(SRC_DIR.resolve())):
        raise RuntimeError(f"refusing to write inside original_documents: {rp}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


MQ = {(q["function_id"], q["phase"]) for q in V3["model_questions"]}
cells = []
for v3c in V3["cells"]:
    fid, phase = v3c["function_id"], v3c["phase"]
    f = FUNCS[fid]
    c = dict(v3c)
    v = c.get("validation") or None
    if f["category"] != "CERT" or not v:
        c["audit"] = None                              # nothing to audit: single source
        c.pop("validation", None)
        c["adopted_value_evidence_role"] = ("ABSOLUTE_RESTATEMENT"
                                            if c["quantity_model"] == "PER_PHASE_FIXED"
                                            else "PRIMARY_QUANTITY_MODEL")
        c["rule_id"] = f"QM4:{fid}:{phase}"
        cells.append(c)
        continue

    per_sku = {}
    adopted = {}
    for n in SKUS:
        k = int(n.replace("SKU", ""))
        cell = CV[(fid, phase, k)]
        adopted[n] = cell["appendix_total"]            # DEC-10: the Appendix is adopted
        per_sku[n] = {
            "main_table_per_sku_quantity": cell["main_table_per_sku_quantity"],
            "derived_total": cell["derived_total"],
            "appendix_label": cell["appendix_label"],
            "appendix_total": cell["appendix_total"],
            "delta": cell["delta"],
            "verification_status": cell["verification_status"],
            "appendix_row": cell["source_reference"]["appendix_row"],
            "main_table_row": cell["source_reference"]["main_table_row"],
            "adopted_value": cell["appendix_total"],
            "adopted_value_source": "APPENDIX_TABLE_TOTAL",
            "audit_counted_in_project_total": False,
        }
    statuses = sorted({per_sku[n]["verification_status"] for n in SKUS})
    c.update({
        "scaling_shape": v3c.get("scaling_shape"),
        "value_access": "APPENDIX_TABLE_READ",
        "adopted_absolute": adopted,
        "adopted_source": "APPENDIX_TABLE_TOTAL",
        "adopted_value_evidence_role": ADOPTED_ROLE,
        # the Main Table column and its derived total are kept, untouched, for audit only
        "main_table_per_sku_quantity": {sk: f["per_sku_rate"][phase][sk] for sk in SKUS},
        "main_table_absolute": v3c["main_table_absolute"],
        "audit": {
            "evidence_role": AUDIT_ROLE,
            "what": ("main_table_per_sku_quantity x sku_count, compared with the adopted "
                     "Appendix total"),
            "block": v["block"],
            "appendix_row": v["appendix_row"],
            "relationship": v["relationship"],
            "comparison_tolerance": TOL,
            "per_sku": per_sku,
            "statuses": statuses,
            "fully_verified": statuses == ["VERIFIED"],
            "counted_in_project_total": False,
            "may_be_added_to_the_adopted_value": False,
            "may_form_a_band": False,
        },
        "owner_review_required": True,
        "evidence_basis": [
            "DEC-10 (Owner): during the MVP and team-trial phase the Certification quantity "
            "is the Appendix total for that Function, Phase and SKU count",
            "the Main Table per-SKU quantity and its derived total are retained unchanged "
            "for audit and difference analysis, and are not counted in the project total",
            "FVT and SIT each read their own Appendix row - no global phase ratio",
            "the Appendix total is counted exactly once; it is never added to the Main Table "
            "derived total and never forms a band",
        ],
        "status": "ADOPTED_BY_OWNER_DECISION_APPENDIX_TOTAL",
        "phase3a_superseded": {
            "quantity_model": v3c["quantity_model"],
            "adopted_source": v3c["adopted_source"],
            "value_access": v3c["value_access"],
            "validation_evidence_role": v["evidence_role"],
            "reason": "Phase 3a adopted the Main Table per-SKU quantity x SKU count and "
                      "treated the Appendix as validation only. The Owner has since decided "
                      "that for the MVP and team trial the Appendix total is the adopted "
                      "number, with the Main Table kept as audit evidence.",
        },
    })
    if v3c.get("breakdown_evidence"):
        j = dict(v3c["breakdown_evidence"])
        j["additive_to_adopted_value"] = False
        j["additive_to_main_table_result"] = False
        c["breakdown_evidence"] = j                    # J33: unchanged, still never added
    c["formula_candidate"] = None
    c.pop("validation", None)
    c["rule_id"] = f"QM4:{fid}:{phase}"
    cells.append(c)

by_model: dict[str, int] = {}
by_access: dict[str, int] = {}
by_adopted: dict[str, int] = {}
by_adopted_role: dict[str, int] = {}
for c in cells:
    by_model[c["quantity_model"]] = by_model.get(c["quantity_model"], 0) + 1
    by_access[c["value_access"]] = by_access.get(c["value_access"], 0) + 1
    by_adopted[c["adopted_source"]] = by_adopted.get(c["adopted_source"], 0) + 1
    by_adopted_role[c["adopted_value_evidence_role"]] = \
        by_adopted_role.get(c["adopted_value_evidence_role"], 0) + 1

cert_cells = [c for c in cells if FUNCS[c["function_id"]]["category"] == "CERT"]
model = {
    "model_id": "QMODEL-V4",
    "model_version": "4.0",
    "supersedes": f"{V3['model_id']}/{V3['model_version']}",
    "derived_from_baseline": BASELINE["baseline_id"],
    "derived_from": BASELINE["derived_from"],
    "status": "DRAFT_PENDING_OWNER",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "generator": "tools/build_quantity_model_v4.py",
    "quantity_model_enum": list(V3["quantity_model_enum"]),
    "evidence_role_enum": list(EVIDENCE_ROLES),
    "owner_decision": {
        "id": "DEC-10",
        "decision": ("for the MVP and the team-trial phase the Certification quantity is the "
                     "Appendix total for the corresponding Function, Phase and SKU count"),
        "adopted_value_source": "APPENDIX_TABLE_TOTAL",
        "audit_only_source": "MAIN_TABLE_PER_SKU_RATE_TIMES_SKU",
        "appendix_counted_in_project_total_times": 1,
        "main_derived_counted_in_project_total_times": 0,
        "j33_counted_in_project_total_times": 0,
        "phase_ratio_used": None,
        "fvt_and_sit_each_read_their_own_appendix_row": True,
        "user_override_scope": "this Analysis only - never written back to the rule pack",
        "scope": "MVP + team trial. It does not close ORI-02: the 7 cells where the two "
                 "columns disagree are still registered and still block finalising the "
                 "rule pack.",
    },
    "policy": {
        "rounding": "NONE (D-01) - every underlying value keeps its original decimal",
        "comparison_tolerance": TOL,
        "display_precision_never_modifies_values": True,
        "pseudo_rate_models": "PROHIBITED (no divide-by-SKU-then-multiply-back)",
        "flat_shape_alone_is_not_evidence_for_PER_PHASE_FIXED": True,
        "certification_model": ("APPENDIX_ADOPTED_TOTAL - the Appendix total per Function x "
                                "Phase x SKU is the adopted quantity (DEC-10)"),
        "certification_relationship":
            "appendix_total == main_table_per_sku_quantity x sku_count",
        "certification_appendix_role":
            "ADOPTED_ABSOLUTE_TOTAL - adopted, counted exactly once",
        "certification_main_table_role":
            "DERIVED_MAIN_TABLE_AUDIT - per-SKU rule of record, retained for audit and "
            "difference analysis, not counted",
        "certification_appendix_may_be_added_to_total": False,
        "certification_appendix_may_be_added_to_main_derived_total": False,
        "certification_appendix_may_form_a_band": False,
        "certification_main_table_may_be_added_to_appendix": False,
        "certification_appendix_is_a_capping_model": False,
        "certification_j33_role": "BREAKDOWN_EVIDENCE - explanatory, never additive",
        "certification_global_phase_ratio": "PROHIBITED - FVT and SIT read their own row",
        "certification_range_reason_allowed": "SKU_NOT_ESTABLISHED only",
        "certification_range_reason_prohibited":
            ["COMPETING_CERTIFICATION_MODELS", "CERTIFICATION_MODEL_UNRESOLVED"],
        "user_override": ("allowed per Analysis on Certification cells; affects that "
                          "Analysis only and is never written back to the rule pack"),
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
    "model_questions": V3["model_questions"],
    "baseline_embedded_sharing": V3["baseline_embedded_sharing"],
    "certification_verification_ref": "artifacts/model/certification_verification.json",
    "summary": {
        "cells_total": len(cells),
        "by_quantity_model": by_model,
        "by_value_access": by_access,
        "by_adopted_source": by_adopted,
        "by_adopted_value_evidence_role": by_adopted_role,
        "owner_review_cells": sum(1 for c in cells if c["owner_review_required"]),
        "certification_cells": len(cert_cells),
        "certification_cells_adopted_from_appendix":
            sum(1 for c in cert_cells if c["adopted_source"] == "APPENDIX_TABLE_TOTAL"),
        "certification_fully_verified_cells":
            sum(1 for c in cert_cells if c["audit"]["fully_verified"]),
        "certification_cells_with_mismatch":
            sum(1 for c in cert_cells if not c["audit"]["fully_verified"]),
        "certification_audit_cells_counted_in_total": 0,
        "main_derived_totals_counted_in_total": 0,
        "j33_added_to_result": False,
        "model_questions": len(V3["model_questions"]),
        "embedded_sharing_suspected_functions":
            V3["summary"]["embedded_sharing_suspected_functions"],
        "ori_02_status": CERTV["ori_02_status"],
        "temporary_model_cells": sum(1 for c in cells
                                     if c["quantity_model"] == "PER_PHASE_FIXED"),
    },
}

guard(ROOT / "artifacts/model/quantity_model_v4.json").write_text(
    json.dumps(model, ensure_ascii=False, indent=1), encoding="utf-8")

# --------------------------------------------------------------------------- #
# markdown view
# --------------------------------------------------------------------------- #
j33c = next(c for c in cert_cells if c.get("breakdown_evidence"))
g = lambda v: ("%g" % v) if v is not None else "-"     # noqa: E731  (display only)
L = ["# Quantity Model v4 - Certification adopted from the Appendix (DEC-10)", "",
     f"- supersedes `{model['supersedes']}` (kept on disk unchanged as the Phase 3a record)",
     f"- baseline `{BASELINE['baseline_id']}` from `{BASELINE['derived_from']['file']}`",
     f"- status **{model['status']}** | ORI-02 **{CERTV['ori_02_status']}**",
     "- generated by `tools/build_quantity_model_v4.py`", "",
     "## Owner decision implemented", "",
     f"> {model['owner_decision']['decision']}", "",
     f"- adopted value source: `{model['owner_decision']['adopted_value_source']}` "
     f"(counted {model['owner_decision']['appendix_counted_in_project_total_times']}x)",
     f"- audit-only source: `{model['owner_decision']['audit_only_source']}` "
     f"(counted {model['owner_decision']['main_derived_counted_in_project_total_times']}x)",
     f"- J33 counted: {model['owner_decision']['j33_counted_in_project_total_times']}x "
     f"(explanatory evidence only)",
     f"- global phase ratio: `{model['owner_decision']['phase_ratio_used']}` - FVT and SIT "
     f"each read their own Appendix row",
     f"- scope: {model['owner_decision']['scope']}", "",
     "## What changed against QMODEL-V3", "",
     "| | Phase 3a (QMODEL-V3) | current (QMODEL-V4) |", "|---|---|---|",
     f"| Certification adopted value | Main Table per-SKU quantity x SKU | **Appendix total "
     f"for that Function x Phase x SKU** ({len(cert_cells)}/{len(cert_cells)} cells) |",
     "| Main Table column | adopted source | **retained for audit + difference analysis** |",
     "| Appendix role | `DERIVED_TOTAL_VALIDATION` | **`ADOPTED_ABSOLUTE_TOTAL`, counted "
     "once** |",
     "| Main derived total | counted once | `DERIVED_MAIN_TABLE_AUDIT`, **counted 0 times** |",
     "| Project total | one number, main-based | one number, appendix-based |",
     "| Band / range from Certification | none | **still none** - only `SKU_NOT_ESTABLISHED` |",
     "| J33 | `BREAKDOWN_EVIDENCE`, never added | **unchanged** |",
     "| MEPA / HW PA | `PER_PHASE_FIXED` candidates | **unchanged** (ORI-10) |",
     "| EMC Test / NV / INTEL | `PER_SKU_RATE` + model questions | **unchanged** |",
     "| Reuse / Wave / Panel / D-01 | DEC-06 / DEC-04 / DEC-02 / D-01 | **unchanged** |", "",
     "## Distribution", "", "```json",
     json.dumps(model["summary"], ensure_ascii=False, indent=1), "```", "",
     "## Certification cells - adopted value vs retained audit value", "",
     "| Function | Phase | adopted SKU2..6 (Appendix) | audit SKU2..6 (main x SKU) | "
     "per-SKU rate SKU2..6 | audit status |", "|---|---|---|---|---|---|"]
for c in cert_cells:
    a = c["audit"]["per_sku"]
    L.append(f"| {c['function_name']} | {c['phase']} | "
             f"{', '.join(g(c['adopted_absolute'][s]) for s in SKUS)} | "
             f"{', '.join(g(c['main_table_absolute'][s]) for s in SKUS)} | "
             f"{', '.join(g(c['main_table_per_sku_quantity'][s]) for s in SKUS)} | "
             f"{'/'.join(c['audit']['statuses'])} |")
L += ["", "## Per-cell audit detail (40 cells; nothing in this table is added twice)", "",
      "| Function | Phase | SKU | adopted (Appendix) | main /SKU | main x SKU (audit) | "
      "delta | audit status |", "|---|---|---:|---:|---:|---:|---:|---|"]
for c in cert_cells:
    for n in SKUS:
        v = c["audit"]["per_sku"][n]
        L.append(f"| {c['function_name']} | {c['phase']} | {int(n[3:])} | "
                 f"{g(v['adopted_value'])} | {g(v['main_table_per_sku_quantity'])} | "
                 f"{g(v['derived_total'])} | {g(v['delta'])} | "
                 f"{v['verification_status']} |")
L += ["", "## Non-Certification cells (carried over untouched)", "",
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
             f"{', '.join(g(c['adopted_absolute'][s]) for s in SKUS)} | {why} |")
L += ["", "## J33 (unchanged: explanatory only)", "",
      f"- source cell: `{j33c['breakdown_evidence']['source_cell']}`",
      f"- disposition: **`{j33c['breakdown_evidence']['disposition']}`**",
      f"- additive to the adopted value: "
      f"**{'YES' if j33c['breakdown_evidence']['additive_to_adopted_value'] else 'NO'}**",
      f"- bracket from J33's own wording: "
      f"{g(j33c['breakdown_evidence']['bracket']['min_no_whole_machine_fcc'])} .. "
      f"{g(j33c['breakdown_evidence']['bracket']['max_full_fcc'])}", "",
      "## Model questions still open (never promoted on shape alone)", ""]
L += [f"- {q['function_name']} / {q['phase']} - {q['issue']}" for q in V3["model_questions"]]
L += ["", "## Superseded interpretations (must never return)", ""]
L += [f"- {s}" for s in model["policy"]["superseded_certification_interpretations"]]
L.append("")
guard(ROOT / "artifacts/model/quantity_model_v4.md").write_text("\n".join(L),
                                                                encoding="utf-8")

print("cells", len(cells), "| by model", json.dumps(by_model),
      "| by adopted source", json.dumps(by_adopted))
print("cert adopted from Appendix:",
      model["summary"]["certification_cells_adopted_from_appendix"], "of", len(cert_cells),
      "| audit fully verified", model["summary"]["certification_fully_verified_cells"],
      "| with mismatch", model["summary"]["certification_cells_with_mismatch"])
print("adopted-value evidence roles:", json.dumps(by_adopted_role))
print("owner_review_cells", model["summary"]["owner_review_cells"],
      "| model_questions", len(V3["model_questions"]))
print("J33:", j33c["breakdown_evidence"]["disposition"], "| additive to adopted:",
      j33c["breakdown_evidence"]["additive_to_adopted_value"])
print("ORI-02:", CERTV["ori_02_status"])
print("wrote artifacts/model/quantity_model_v4.json / .md")
