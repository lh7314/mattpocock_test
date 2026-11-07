#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deliverable D support: what the Quantity Model decision actually changed.

Compares, per SKU tier:
  WORKBOOK_REPLAY  - the raw Main Table totals (must equal the workbook)
  ENGINE MAIN      - the same cells, but MEPA / HW PA read as absolute per-phase
                     allocations instead of pseudo rates, Certification from Main Table
  ENGINE SECONDARY - identical, Certification from the Secondary Table
  ENGINE CONFIRMED - cells nobody disputes (Certification excluded)

Output: artifacts/model/model_delta.md  (+ .json)
"""
from __future__ import annotations

import io
import json
import sys
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

sys.path.insert(0, str(ROOT / "prototype"))
import rules_v2 as R                                          # noqa: E402

SKUS = (2, 3, 4, 5, 6)
GOLDEN = {2: 365.0, 3: 417.0, 4: 443.8, 5: 474.0, 6: 507.0}

rows, cell_changes = [], []
for n in SKUS:
    res = R.finalise(R.AnalysisInput(**{k: R.KeyFactor(k, file_value=v) for k, v in
                                        dict(cpu=3, gpu=2, panel=2, ssd=2, mem=2).items()}), n)
    tm = res["totals_by_model"]
    v = {x["model_source"]: x for x in tm["variants"]}
    rows.append({
        "sku": n,
        "workbook_replay": GOLDEN[n],
        "engine_main": v["MAIN_TABLE"]["TOTAL"],
        "engine_secondary": v["SECONDARY_TABLE"]["TOTAL"],
        "engine_confirmed_only": tm["confirmed_only"]["TOTAL"],
        "delta_engine_minus_workbook": round(v["MAIN_TABLE"]["TOTAL"] - GOLDEN[n], 9),
        "certification_spread": tm["band"]["spread"],
        "band": f"{tm['band']['total_min']:g}-{tm['band']['total_max']:g}",
    })

# which cells caused the ENGINE-vs-WORKBOOK difference
for c in R.QMODEL["cells"]:
    for s in SKUS:
        k = f"SKU{s}"
        adopted, main = c["adopted_absolute"][k], c["main_table_absolute"][k]
        if adopted is not None and main is not None and not R.approx(adopted, main):
            cell_changes.append({
                "function": c["function_name"], "phase": c["phase"], "sku": s,
                "workbook_main_table": main, "engine_adopted": adopted,
                "delta": round(adopted - main, 9),
                "quantity_model": c["quantity_model"],
                "why": "; ".join(c["evidence_basis"]),
            })

out = {
    "model_id": R.QMODEL["model_id"],
    "baseline": R.BASELINE["baseline_id"],
    "status": R.QMODEL["status"],
    "note": "ENGINE MAIN differs from the workbook only where DEC-05 removed a pseudo rate. "
            "No other value moved. DEC-03 leaves Certification unresolved, so the honest "
            "answer is a band, not one number.",
    "totals_by_sku": rows,
    "cells_changed_by_dec05": cell_changes,
}
(ROOT / "artifacts/model/model_delta.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

L = ["# Quantity Model impact on the totals (DEC-05 / DEC-03)", "",
     f"- baseline `{R.BASELINE['baseline_id']}` | quantity model `{R.QMODEL['model_id']}` | "
     f"status **{R.QMODEL['status']}**", "",
     "| SKU | workbook replay | engine (Certification = Main Table) | engine (Certification = "
     "Secondary Table) | engine (undisputed cells only) | engine - workbook | Certification "
     "spread | published answer |",
     "|---:|---:|---:|---:|---:|---:|---:|---|"]
for r in rows:
    L.append(f"| {r['sku']} | {r['workbook_replay']:g} | {r['engine_main']:g} | "
             f"{r['engine_secondary']:g} | {r['engine_confirmed_only']:g} | "
             f"{r['delta_engine_minus_workbook']:+g} | {r['certification_spread']:g} | "
             f"`{r['band']}` |")

L += ["", "## The only cells DEC-05 changed", "",
      "| Function | Phase | SKU | workbook Main Table | engine adopted | delta | model | why |",
      "|---|---|---:|---:|---:|---:|---|---|"]
for c in cell_changes:
    L.append(f"| {c['function']} | {c['phase']} | {c['sku']} | {c['workbook_main_table']:g} | "
             f"{c['engine_adopted']:g} | {c['delta']:+g} | {c['quantity_model']} | {c['why'][:120]} |")

L += ["", "## Reading", "",
      "- `workbook replay` reproduces the source file exactly. It is a regression anchor, not "
      "the answer the MVP publishes.",
      "- `engine (Main Table)` is the workbook total after the pseudo-rate rows are read as "
      "the absolute per-phase allocations they already are. SKU 2 moves because MEPA is 36 "
      "units per phase at every SKU tier, not 32 at 2 SKU.",
      "- The **published answer is the band**. The two Certification models disagree by up to "
      f"{max(r['certification_spread'] for r in rows):g} units and the Agent is not allowed to "
      "choose between them (DEC-03).",
      "- `undisputed cells only` excludes the 8 Certification cells entirely; it is the number "
      "the MVP can state without any Owner decision at all.", ""]

(ROOT / "artifacts/model/model_delta.md").write_text("\n".join(L), encoding="utf-8")
print(f"[ok] {ROOT / 'artifacts/model/model_delta.md'}")
print(json.dumps(out["totals_by_sku"], ensure_ascii=False, indent=1))
print(f"cells changed by DEC-05: {len(cell_changes)}")
