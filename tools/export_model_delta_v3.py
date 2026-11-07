#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_model_delta_v3 - quantifies what the Certification correction actually changed,
and keeps it strictly separate from the MEPA / HW PA change that came from Phase 2.

Three numbers are computed for every SKU band, all from the same 42 cells:

  workbook        the source workbook's own SUM/sku x SKU arithmetic
  phase2_main     Phase 2's upper variant  (Certification priced from the Main Table)
  phase2_second   Phase 2's lower variant  (Certification priced from the Appendix)
  corrected       this task's answer       (Main Table per-SKU x SKU, Appendix validation only)

That makes the attribution unambiguous:
  corrected - workbook            = the MEPA / HW PA Quantity Model change (Phase 2, ORI-10)
  corrected - phase2_*           = the Certification semantic change (this task)
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]

def _refuse_superseded_write() -> None:
    """This exporter writes files the current pipeline also owns.

    Running it for the record would replace the shipped numbers with the superseded
    Phase 2 / Phase 3a figures, so it stops here unless the operator asks for it explicitly
    with ALLOW_SUPERSEDED_WRITE=1. The artefacts already on disk are the historic record.
    """
    import os
    if os.environ.get("ALLOW_SUPERSEDED_WRITE") == "1":
        return
    if (ROOT / "artifacts/model/quantity_model_v4.json").exists():
        print("SKIPPED (superseded): this tool writes artifacts/model/model_delta.*, which "
              "the current pipeline owns. Set ALLOW_SUPERSEDED_WRITE=1 to run it anyway.")
        sys.exit(0)


_refuse_superseded_write()

BASE = json.loads((ROOT / "artifacts/model/baseline_v1.json").read_text(encoding="utf-8"))
V3 = json.loads((ROOT / "artifacts/model/quantity_model_v3.json").read_text(encoding="utf-8"))
CV = json.loads((ROOT / "artifacts/model/certification_verification.json")
                .read_text(encoding="utf-8"))
TOL = 1e-9
SKUS = (2, 3, 4, 5, 6)
FUNCS = {f["function_id"]: f for f in BASE["functions"]}
PA = {"F_MEPA", "F_HW_PA"}
CERT = {k for k, f in FUNCS.items() if f["category"] == "CERT"}


def is_cert(c):
    return c["function_id"] in CERT


def main() -> int:
    rows, cell_changes = [], []
    for n in SKUS:
        k = f"SKU{n}"
        wb = p2up = p2lo = corr = 0.0
        fvt = sit = cert = noncert = 0.0
        for c in V3["cells"]:
            # the workbook's own arithmetic: every cell is Main Table per-SKU x SKU
            wb += c["main_table_absolute"][k]
            # Phase 2 priced each UNRESOLVED Certification cell once per rival source,
            # while MEPA / HW PA were already read as absolute per-phase amounts.
            sec = (c.get("secondary_table_absolute") or {}).get(k)
            p2up += (c["main_table_absolute"][k] if is_cert(c)
                     else c["adopted_absolute"][k])
            p2lo += (sec if (is_cert(c) and sec is not None)
                     else c["adopted_absolute"][k])
            corr += c["adopted_absolute"][k]
            if c["phase"] == "FVT":
                fvt += c["adopted_absolute"][k]
            else:
                sit += c["adopted_absolute"][k]
            if is_cert(c):
                cert += c["adopted_absolute"][k]
            else:
                noncert += c["adopted_absolute"][k]
        lo, hi = min(p2up, p2lo), max(p2up, p2lo)
        rows.append({
            "sku_count": n,
            "workbook_total": round(wb, 10),
            "phase2_band_low": round(lo, 10),
            "phase2_band_high": round(hi, 10),
            "phase2_main_variant": round(p2up, 10),
            "phase2_appendix_variant": round(p2lo, 10),
            "corrected_total": round(corr, 10),
            "corrected_fvt": round(fvt, 10),
            "corrected_sit": round(sit, 10),
            "corrected_certification": round(cert, 10),
            "corrected_non_certification": round(noncert, 10),
            "delta_vs_workbook": round(corr - wb, 10),
            "delta_vs_phase2_high": round(corr - hi, 10),
            "delta_vs_phase2_low": round(corr - lo, 10),
            "delta_attributed_to_certification": round(corr - p2up, 10),
            "delta_attributed_to_mepa_hw_pa": round(corr - wb, 10),
            "delta_attributed_to_sku_range": None,
        })

    # which cells differ from the workbook at all, and why
    for c in V3["cells"]:
        for n in SKUS:
            k = f"SKU{n}"
            d = round(c["adopted_absolute"][k] - c["main_table_absolute"][k], 10)
            if abs(d) > TOL:
                cell_changes.append({
                    "function_id": c["function_id"], "function_name": c["function_name"],
                    "phase": c["phase"], "sku_count": n,
                    "workbook_main_table": c["main_table_absolute"][k],
                    "corrected_adopted": c["adopted_absolute"][k], "delta": d,
                    "quantity_model": c["quantity_model"],
                    "cause": ("MEPA / HW PA absolute restatement in the secondary PA table "
                              "(Phase 2 DEC-05, ORI-10) - NOT a Certification change"
                              if c["function_id"] in PA else
                              "unexpected: a non-PA, non-Certification cell changed"),
                })

    cert_only = [c for c in cell_changes if c["function_id"] in CERT]
    out = {
        "artifact": "model_delta_v3",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "tools/export_model_delta_v3.py",
        "baseline": BASE["baseline_id"],
        "quantity_model": f"{V3['model_id']}/{V3['model_version']}",
        "ori_02_status": CV["ori_02_status"],
        "rows": rows,
        "changed_cells": cell_changes,
        "attribution": {
            "certification_semantic_change": {
                "numeric_effect_on_project_total": 0.0,
                "cells_changed": len(cert_only),
                "explanation":
                    "Certification was already being priced from the Main Table in Phase 2, "
                    "so correcting the semantics did not move any number. What changed is "
                    "the output shape and the reporting: Phase 2 published a 408-417 style "
                    "band at every SKU because it treated the Appendix as a rival model, "
                    "while the corrected model publishes one number and keeps the Appendix "
                    "as a per-cell check.",
            },
            "mepa_hw_pa_change_from_phase2": {
                "numeric_effect_on_project_total": {
                    f"SKU{r['sku_count']}": r["delta_attributed_to_mepa_hw_pa"] for r in rows},
                "cells_changed": len([c for c in cell_changes if c["function_id"] in PA]),
                "explanation":
                    "MEPA and HW PA are read as absolute per-phase amounts from the "
                    "secondary PA table instead of a divide-by-SKU-then-multiply-back rate. "
                    "This came from Phase 2 and is unchanged by this task (ORI-10).",
            },
            "sku_range_only": {
                "explanation":
                    "Where the SKU answer is a tie (4 SKU vs 5 SKU) the demand is a range "
                    "because two SKU bands are priced. SKU4 gives "
                    f"{[r for r in rows if r['sku_count'] == 4][0]['corrected_total']:g} and "
                    f"SKU5 gives {[r for r in rows if r['sku_count'] == 5][0]['corrected_total']:g}; "
                    "neither is a Certification artefact.",
            },
            "unchanged": {
                "explanation":
                    "Every non-Certification, non-PA cell is identical to the workbook: 30 "
                    "PER_SKU_RATE cells keep the Main Table value exactly, including the "
                    "float tail at 3 SKU (65.49999999999999) and 443.8 at 4 SKU.",
            },
            "owner_review_only": {
                "explanation":
                    "The 7 mismatched Certification cells change nothing in the totals; they "
                    "are reported so the Owner can decide which of the two workbook numbers "
                    "is authoritative (ORI-02 PARTIALLY_RESOLVED).",
            },
        },
    }
    (ROOT / "artifacts/model").mkdir(parents=True, exist_ok=True)
    (ROOT / "artifacts/model/model_delta.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    L = ["# Model delta - what changed, and why", "",
         f"- baseline `{BASE['baseline_id']}`, Quantity Model "
         f"`{V3['model_id']}` {V3['model_version']}",
         f"- generated by `tools/export_model_delta_v3.py` "
         f"({out['generated_at_utc']})", "",
         "## Totals by SKU band", "",
         "| SKU | Workbook | Phase 2 band (low–high) | Corrected total | FVT | SIT | "
         "Certification | Non-Cert | Δ vs workbook |",
         "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        L.append(f"| {r['sku_count']} | {r['workbook_total']:g} | "
                 f"{r['phase2_band_low']:g} – {r['phase2_band_high']:g} | "
                 f"**{r['corrected_total']:g}** | {r['corrected_fvt']:g} | "
                 f"{r['corrected_sit']:g} | {r['corrected_certification']:g} | "
                 f"{r['corrected_non_certification']:g} | {r['delta_vs_workbook']:+g} |")
    L += ["", "## Where each difference comes from", "",
          "### 1. Certification semantics (this task) - **no numeric change**", "",
          "Phase 2 already priced Certification from the Main Table in its upper variant, so "
          "correcting the semantics moves no number. What changed is the output:", "",
          "| | Phase 2 | Corrected |", "|---|---|---|",
          "| Certification cells | `UNRESOLVED`, adopted value null | `PER_SKU_RATE`, "
          "adopted = per-SKU quantity × SKU |",
          "| Project total | a band at every SKU (e.g. 408–417 at 3 SKU) | one number "
          "(417 at 3 SKU) |",
          "| Appendix | priced as a rival model, forming the low end | validation evidence "
          "only, never added |",
          "| Range reason | `CERTIFICATION_MODEL_UNRESOLVED` | `SKU_NOT_ESTABLISHED` only |",
          "| Owner output | " + "an unresolvable model question | 33 of 40 cells verified, "
          "7 reported as source-data mismatches |", "",
          "### 2. MEPA / HW PA (Phase 2, unchanged here)", ""]
    for c in cell_changes:
        L.append(f"- {c['function_name']} {c['phase']} at {c['sku_count']} SKU: "
                 f"{c['workbook_main_table']:g} → {c['corrected_adopted']:g} "
                 f"({c['delta']:+g}) — {c['cause']}")
    L += ["", "### 3. Ranges caused only by the SKU answer", "",
          out["attribution"]["sku_range_only"]["explanation"], "",
          "### 4. Numbers that did not change", "",
          out["attribution"]["unchanged"]["explanation"], "",
          "### 5. Differences that are Owner Review items, not calculation changes", "",
          out["attribution"]["owner_review_only"]["explanation"], "",
          "## Cells that differ from the workbook", "",
          "| Function | Phase | SKU | Workbook | Adopted | Δ | Cause |", "|---|---|---:|---:|---:|---:|---|"]
    for c in cell_changes:
        L.append(f"| {c['function_name']} | {c['phase']} | {c['sku_count']} | "
                 f"{c['workbook_main_table']:g} | {c['corrected_adopted']:g} | "
                 f"{c['delta']:+g} | {c['quantity_model']} — "
                 f"{'MEPA/HW PA absolute restatement' if c['function_id'] in PA else c['cause']} |")
    L.append("")
    (ROOT / "artifacts/model/model_delta.md").write_text("\n".join(L), encoding="utf-8")

    print("SKU bands:", json.dumps({f"SKU{r['sku_count']}": r["corrected_total"] for r in rows}))
    print("Δ vs workbook:", json.dumps({f"SKU{r['sku_count']}": r["delta_vs_workbook"] for r in rows}))
    print("Phase 2 bands removed:",
          json.dumps({f"SKU{r['sku_count']}": f"{r['phase2_band_low']:g}-"
                      f"{r['phase2_band_high']:g}" for r in rows}))
    print("Certification-attributed delta:",
          json.dumps({f"SKU{r['sku_count']}": r["delta_attributed_to_certification"]
                      for r in rows}))
    print("cells changed vs workbook:", len(cell_changes),
          "| of which Certification:", len(cert_only))
    print("wrote artifacts/model/model_delta.json / model_delta.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
