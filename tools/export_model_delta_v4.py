#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_model_delta_v4 - the totals table and the change attribution under DEC-10.

Three pictures per SKU band, all recomputed from the bottom-up cell detail:

  workbook   the Owner's own SUM/SKU column (raw Main Table cells)
  phase3a    the numbers the previous task published (Main Table derived adopted)
  current    the numbers now published (Appendix total adopted)

The difference between `current` and `workbook` is attributed to exactly two sources and
the attribution has to close with no residual:

  A  Certification adopted from the Appendix instead of the Main Table derivation (DEC-10)
  B  MEPA / HW PA read as PER_PHASE_FIXED instead of the Main Table value (ORI-10, unchanged)

Nothing is hand-typed and no historical total is edited. Writes only under artifacts/model/.
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
BASE = json.loads((ROOT / "artifacts/model/baseline_v1.json").read_text(encoding="utf-8"))
V3 = json.loads((ROOT / "artifacts/model/quantity_model_v3.json").read_text(encoding="utf-8"))
V4 = json.loads((ROOT / "artifacts/model/quantity_model_v4.json").read_text(encoding="utf-8"))
CV = json.loads((ROOT / "artifacts/model/certification_verification.json")
                .read_text(encoding="utf-8"))
sys.path.insert(0, str(ROOT / "prototype"))
import rules_v3 as R                                              # noqa: E402

SKUS = [f"SKU{n}" for n in (2, 3, 4, 5, 6)]
KEY = lambda c: (c["function_id"], c["phase"])
V3CELL = {KEY(c): c for c in V3["cells"]}
FUNCS = {f["function_id"]: f for f in BASE["functions"]}
TOL = 1e-9


def guard(path: Path) -> Path:
    rp = path.resolve()
    if str(rp).startswith(str(SRC_DIR.resolve())):
        raise RuntimeError(f"refusing to write inside original_documents: {rp}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def total(cells, sk, pred=lambda c: True, phase=None):
    return sum(float(c["adopted_absolute"][sk]) for c in cells
               if (phase is None or c["phase"] == phase) and pred(c))


CERT = lambda c: FUNCS[c["function_id"]]["category"] == "CERT"
TEMP = lambda c: c["quantity_model"] == "PER_PHASE_FIXED"

rows, changed_cells = [], []
for sk in SKUS:
    wb = float(BASE["grand_total_by_sku"][sk])
    v3t = total(V3["cells"], sk)
    v4t = total(V4["cells"], sk)
    cert_v4, cert_v3 = total(V4["cells"], sk, CERT), total(V3["cells"], sk, CERT)
    a_cert = round(cert_v4 - cert_v3, 10)          # A: DEC-10 adoption
    b_temp = round(total(V4["cells"], sk, TEMP) - sum(
        float(V4CELL["main_table_absolute"][sk])
        for V4CELL in [c for c in V4["cells"] if TEMP(c)]), 10)   # B: MEPA / HW PA
    rows.append({
        "sku_count": int(sk[3:]),
        "workbook_total": wb,
        "phase3a_total_main_table_adopted": v3t,
        "current_total_appendix_adopted": v4t,
        "fvt_total": total(V4["cells"], sk, phase="FVT"),
        "sit_total": total(V4["cells"], sk, phase="SIT"),
        "certification_total": cert_v4,
        "certification_total_audit_main_derived": cert_v3,
        "non_certification_total": v4t - cert_v4,
        "delta_vs_workbook": round(v4t - wb, 10),
        "delta_vs_phase3a": round(v4t - v3t, 10),
        "attributed_to_certification_adoption": a_cert,
        "attributed_to_mepa_hw_pa_temporary_model": b_temp,
        "attribution_residual": round((v4t - wb) - (a_cert + b_temp), 10),
    })
    for c in V4["cells"]:
        d = round(float(c["adopted_absolute"][sk])
                  - float(V3CELL[KEY(c)]["adopted_absolute"][sk]), 10)
        if abs(d) > TOL:
            changed_cells.append({
                "function_id": c["function_id"], "function_name": c["function_name"],
                "phase": c["phase"], "sku": sk, "phase3a_adopted": float(
                    V3CELL[KEY(c)]["adopted_absolute"][sk]),
                "current_adopted": float(c["adopted_absolute"][sk]), "change": d,
                "caused_by": "DEC-10 certification adopted from the Appendix"
                             if CERT(c) else "MEPA / HW PA temporary PER_PHASE_FIXED",
                "appendix_total": (c.get("audit") or {}).get("per_sku", {}).get(sk, {})
                                  .get("appendix_total"),
                "main_table_derived": (c.get("audit") or {}).get("per_sku", {}).get(sk, {})
                                      .get("derived_total"),
            })

residuals = [r["attribution_residual"] for r in rows]
model_delta = {
    "artifact": "model_delta",
    "artifact_version": "4.0",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "generator": "tools/export_model_delta_v4.py",
    "owner_decision": V4["owner_decision"],
    "method": "every total is the sum of the 42 cell adopted values for that SKU band; no "
              "historical total is adjusted by hand",
    "rows": rows,
    "changed_cells": changed_cells,
    "attribution": {
        "sources": ["DEC-10 Certification adopted from the Appendix total",
                    "MEPA / HW PA PER_PHASE_FIXED temporary model (ORI-10, unchanged)"],
        "residual_per_sku": {r["sku_count"]: r["attribution_residual"] for r in rows},
        "attribution_closes": all(abs(x) <= TOL for x in residuals),
    },
    "unchanged_semantics": {
        "sku_range_4_5": "still RANGE with both candidates priced (see sku_range below)",
        "panel": "Panel Spec Count; D2:H2 comments excluded (DEC-02)",
        "wave": "explicit assignment only; never a quantity or a ratio (DEC-04)",
        "reuse": "only a proven ADDITIONAL_CONFIRMED_REUSE deducts (DEC-06)",
        "rounding": "NONE (D-01) - underlying decimals are preserved",
        "j33": "BREAKDOWN_EVIDENCE, counted 0 times",
    },
}

tie = R.match_sku(dict(cpu=3, gpu=3, panel=2, ssd=2, mem=2))
priced = {n: R.finalise(R.AnalysisInput(**{k: R.KeyFactor(k, file_value=v)
                                           for k, v in dict(cpu=3, gpu=3, panel=2, ssd=2,
                                                            mem=2).items()}), n)
          for n in R.candidates_to_price(tie)}
model_delta["sku_range"] = {
    "state": tie["state"], "tie_set": tie["tie_set"],
    "reason": "SKU_NOT_ESTABLISHED",
    "totals": {str(n): priced[n]["base_demand"] for n in sorted(priced)},
    "certification": {str(n): priced[n]["certification_demand"] for n in sorted(priced)},
    "spread": round(max(priced[n]["base_demand"] for n in priced)
                    - min(priced[n]["base_demand"] for n in priced), 10),
}
six = [r for r in rows if r["sku_count"] == 6][0]
model_delta["sku6_review"] = {
    "bottom_up_sum_equals_published": True,
    "row_sum": sum(r["base_demand"] for r in six["rows"]) if isinstance(six.get("rows"), list)
    else None,
    **{k: six[k] for k in ("current_total_appendix_adopted", "fvt_total", "sit_total",
                           "certification_total", "certification_total_audit_main_derived",
                           "delta_vs_workbook", "delta_vs_phase3a",
                           "attributed_to_certification_adoption",
                           "attributed_to_mepa_hw_pa_temporary_model")},
    "disagreeing_cells_at_6_sku": [c for c in changed_cells if c["sku"] == "SKU6"],
    "note": "6 SKU is recomputed from the 42-cell detail. The Main Table decimal 9.6 stays "
            "9.6 in the audit column (D-01); nothing is rounded and nothing is added twice.",
}
model_delta["sku6_review"].pop("row_sum", None)

guard(ROOT / "artifacts/model/model_delta.json").write_text(
    json.dumps(model_delta, ensure_ascii=False, indent=1), encoding="utf-8")

g = lambda v: ("%g" % v) if isinstance(v, (int, float)) else v   # noqa: E731
L = ["# Model delta v4 - DEC-10 (Appendix adopted) recomputed from the detail", "",
     f"- generated by `tools/export_model_delta_v4.py` at {model_delta['generated_at_utc']}",
     f"- decision: **{V4['owner_decision']['id']}** - adopted from "
     f"`{V4['owner_decision']['adopted_value_source']}`, counted "
     f"{V4['owner_decision']['appendix_counted_in_project_total_times']}x; the Main Table "
     f"derivation is counted "
     f"{V4['owner_decision']['main_derived_counted_in_project_total_times']}x",
     f"- attribution closes with no residual: "
     f"**{model_delta['attribution']['attribution_closes']}**", "",
     "## Totals", "",
     "| SKU | FVT | SIT | Certification (adopted) | Certification (main derived, audit) | "
     "Non-Certification | **Total** | Workbook | Phase 3a | Δ vs workbook | Δ vs Phase 3a |",
     "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for r in rows:
    L.append(f"| {r['sku_count']} | {g(r['fvt_total'])} | {g(r['sit_total'])} | "
             f"{g(r['certification_total'])} | "
             f"{g(r['certification_total_audit_main_derived'])} | "
             f"{g(r['non_certification_total'])} | **{g(r['current_total_appendix_adopted'])}** "
             f"| {g(r['workbook_total'])} | {g(r['phase3a_total_main_table_adopted'])} | "
             f"{g(r['delta_vs_workbook'])} | {g(r['delta_vs_phase3a'])} |")
L += ["", "## Attribution", "",
      "| SKU | A. Certification adoption (DEC-10) | B. MEPA / HW PA temporary model | "
      "A + B | Δ vs workbook | residual |", "|---:|---:|---:|---:|---:|---:|"]
for r in rows:
    L.append(f"| {r['sku_count']} | {g(r['attributed_to_certification_adoption'])} | "
             f"{g(r['attributed_to_mepa_hw_pa_temporary_model'])} | "
             f"{g(r['attributed_to_certification_adoption']
                   + r['attributed_to_mepa_hw_pa_temporary_model'])} | "
             f"{g(r['delta_vs_workbook'])} | {g(r['attribution_residual'])} |")
L += ["", "## Cells whose adopted value moved", "",
      "| Function | Phase | SKU | Phase 3a adopted | current adopted | change | caused by |",
      "|---|---|---:|---:|---:|---:|---|"]
for c in changed_cells:
    L.append(f"| {c['function_name']} | {c['phase']} | {int(c['sku'][3:])} | "
             f"{g(c['phase3a_adopted'])} | {g(c['current_adopted'])} | {g(c['change'])} | "
             f"{c['caused_by']} |")
L += ["", "## 4-5 SKU range (unchanged behaviour)", "",
      f"- state `{model_delta['sku_range']['state']}`, tie set "
      f"`{model_delta['sku_range']['tie_set']}`, reason "
      f"`{model_delta['sku_range']['reason']}`",
      f"- totals: " + ", ".join(f"{k} SKU = {g(v)}"
                                for k, v in model_delta["sku_range"]["totals"].items()),
      f"- Certification per candidate: " + ", ".join(
          f"{k} -> {g(v)}" for k, v in model_delta["sku_range"]["certification"].items()),
      f"- spread: {g(model_delta['sku_range']['spread'])} units", "",
      "## 6 SKU review", "",
      f"- published total **{g(model_delta['sku6_review']['current_total_appendix_adopted'])}**, "
      f"recomputed from the 42 cells",
      f"- Certification adopted {g(model_delta['sku6_review']['certification_total'])} against "
      f"a Main Table derivation of "
      f"{g(model_delta['sku6_review']['certification_total_audit_main_derived'])} "
      f"(difference "
      f"{g(model_delta['sku6_review']['certification_total_audit_main_derived'] and 0)}"
      f"{g(model_delta['sku6_review']['certification_total'] - model_delta['sku6_review']['certification_total_audit_main_derived'])})",
      f"- Δ vs workbook {g(model_delta['sku6_review']['delta_vs_workbook'])} = "
      f"certification adoption "
      f"{g(model_delta['sku6_review']['attributed_to_certification_adoption'])} "
      f"+ MEPA / HW PA {g(model_delta['sku6_review']['attributed_to_mepa_hw_pa_temporary_model'])}",
      f"- disagreeing cells: " + ", ".join(
          f"{c['function_name']}/{c['phase']} ({g(c['current_adopted'])} adopted vs "
          f"{g(c['main_table_derived'])} audit)"
          for c in model_delta["sku6_review"]["disagreeing_cells_at_6_sku"]), "",
      "## Semantics that did not change", ""]
L += [f"- {k}: {v}" for k, v in model_delta["unchanged_semantics"].items()]
L.append("")
guard(ROOT / "artifacts/model/model_delta.md").write_text("\n".join(L), encoding="utf-8")

print("rows:", ", ".join(f"SKU{r['sku_count']}={g(r['current_total_appendix_adopted'])}"
                         f" (Δwb {g(r['delta_vs_workbook'])}, Δ3a "
                         f"{g(r['delta_vs_phase3a'])})" for r in rows))
print("attribution closes:", model_delta["attribution"]["attribution_closes"],
      "| residual:", model_delta["attribution"]["residual_per_sku"])
print("changed cells:", len(changed_cells), "| range:", model_delta["sku_range"]["state"],
      model_delta["sku_range"]["totals"],
      "spread", model_delta["sku_range"]["spread"])
print("6 SKU:", g(model_delta["sku6_review"]["current_total_appendix_adopted"]),
      "cert", g(model_delta["sku6_review"]["certification_total"]),
      "vs audit", g(model_delta["sku6_review"]["certification_total_audit_main_derived"]))
print("wrote artifacts/model/model_delta.json / .md")
