#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_rule_pack_v3 - package the confirmed rule set for the Web MVP (deliverable E).

The Web front end must not carry a second copy of the business numbers. Everything it
needs is packaged here from the verified artefacts, and the package declares which Owner
Review Items are still open so the UI can show them without deciding them.

Output is written twice on purpose:
  artifacts/model/rule_pack_v3.json  - the package itself
  web/assets/rulepack.js             - the same object as `window.RULEPACK = ...` so the
                                       MVP runs from a double-clicked file:// page, where
                                       fetch() of a local .json is blocked by the browser

Nothing is hand-typed: every number comes from
  artifacts/model/baseline_v1.json
  artifacts/model/quantity_model_v3.json
  artifacts/model/certification_verification.json
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "original_documents"
BASE = json.loads((ROOT / "artifacts/model/baseline_v1.json").read_text(encoding="utf-8"))
QM = json.loads((ROOT / "artifacts/model/quantity_model_v3.json").read_text(encoding="utf-8"))
CV = json.loads((ROOT / "artifacts/model/certification_verification.json").read_text(encoding="utf-8"))

def _refuse_superseded_write() -> None:
    """This exporter/package builder targets files the current pipeline also writes.

    Running it for the record would replace the shipped numbers with the superseded Phase 2 /
    Phase 3a figures, so it stops here unless the operator asks for it explicitly with
    ALLOW_SUPERSEDED_WRITE=1. The artefacts already on disk are the historic record.
    """
    import os
    if os.environ.get("ALLOW_SUPERSEDED_WRITE") == "1":
        return
    if (ROOT / "artifacts/model/quantity_model_v4.json").exists():
        print("SKIPPED (superseded): this tool writes files the current pipeline owns "
              "(web/assets/rulepack.js, artifacts/model/model_delta.*). "
              "Set ALLOW_SUPERSEDED_WRITE=1 to run it anyway; the historic artefacts on "
              "disk are already the record.")
        sys.exit(0)


_refuse_superseded_write()

PACK_VERSION = "RP-V3.0"
BLOCKING = {"ORI-02": "BLOCKS_FORMALIZATION", "ORI-04": "BLOCKS_FORMALIZATION",
            "ORI-10": "BLOCKS_FORMALIZATION", "ORI-01": "AFFECTS_ACCURACY",
            "ORI-03": "AFFECTS_ACCURACY", "ORI-07": "AFFECTS_ACCURACY",
            "ORI-09": "ADVISORY", "ORI-11": "ADVISORY", "ORI-12": "ADVISORY",
            "ORI-13": "AFFECTS_ACCURACY", "ORI-14": "ADVISORY"}


def guard(path: Path) -> Path:
    rp = path.resolve()
    if str(rp).startswith(str(SRC_DIR.resolve())):
        raise RuntimeError(f"refusing to write inside original_documents: {rp}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


cells = []
for c in QM["cells"]:
    cells.append({
        "function_id": c["function_id"], "function_name": c["function_name"],
        "category": c["category"], "phase": c["phase"],
        "quantity_model": c["quantity_model"], "evidence_role": c["evidence_role"],
        "value_access": c["value_access"],
        "adopted_absolute": c["adopted_absolute"],
        "main_table_per_sku_quantity": c["main_table_per_sku_quantity"],
        "main_table_absolute": c["main_table_absolute"],
        "adopted_source": c["adopted_source"],
        "owner_review_required": c["owner_review_required"],
        "is_temporary_model": c["quantity_model"] == "PER_PHASE_FIXED",
        "status": c["status"], "rule_id": c["rule_id"], "evidence": c["evidence"],
        "validation": c["validation"],
        "breakdown_evidence": ({k: v for k, v in c["breakdown_evidence"].items()
                                if k != "raw_text"}
                               if c.get("breakdown_evidence") else None),
    })

pack = {
    "pack_id": PACK_VERSION,
    "pack_version": PACK_VERSION,
    "schema_version": "3.0",
    "engine_contract": "prototype/rules_v3.py is the behaviour reference; web/assets/core.js "
                       "is a port of it and is checked against it by "
                       "tools/check_python_web_parity.py",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "generator": "tools/build_rule_pack_v3.py",
    "source_file": BASE["derived_from"],
    "baseline_id": BASE["baseline_id"],
    "quantity_model_version": f"{QM['model_id']}/{QM['model_version']}",
    "status": "DRAFT_PENDING_OWNER",
    "sku_definition": BASE["sku_definition"],
    "sku_definition_header_comments": BASE["sku_definition_header_comments"],
    "functions": [{"function_id": f["function_id"], "name": f["name"],
                   "category": f["category"], "source_rows": f["source_rows"],
                   "purpose_text": f["purpose_text"], "status_text": f["status_text"]}
                  for f in BASE["functions"]],
    "sku_range": [2, 3, 4, 5, 6],
    "phases": ["FVT", "SIT"],
    "dims": ["cpu", "gpu", "panel", "ssd", "mem"],
    "dim_weight": {"cpu": 1.0, "gpu": 1.6, "panel": 1.0, "ssd": 1.4, "mem": 1.4},
    "verdict_weight": {"MATCH": 1.0, "PARTIAL_MATCH": 0.4, "MISMATCH": 0.0, "UNKNOWN": 0.0},
    "weights_note": "ORI-08: agent-set, not Owner-confirmed. Ranking only - DEC-01 forbids "
                    "using them to force a single answer out of a tie.",
    "quantity_model_enum": QM["quantity_model_enum"],
    "evidence_role_enum": QM["evidence_role_enum"],
    "cells": cells,
    "certification_verification": {
        "grid": CV["verification_grid"],
        "summary": CV["summary"],
        "ori_02_status": CV["ori_02_status"],
        "appendix_internally_consistent": CV["appendix_internally_consistent"],
        "owner_semantics": CV["owner_semantics"],
    },
    "j33_investigation": CV["j33_investigation"],
    "baseline_embedded_sharing": QM["baseline_embedded_sharing"],
    "model_questions": QM["model_questions"],
    "policy": QM["policy"],
    "tolerance": 1e-9,
    "open_owner_review_items": [
        {"id": k, "blocking_level": v, "blocks_manual_mvp": False,
         "note": "shown in the UI; never stops a manual analysis (task section 22)"}
        for k, v in sorted(BLOCKING.items())],
    "blocking_rule": "only OUT_OF_DOMAIN input stops a calculation, and it stops that "
                     "scenario alone with an explanation",
}

guard(ROOT / "artifacts/model/rule_pack_v3.json").write_text(
    json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
js = ("// GENERATED by tools/build_rule_pack_v3.py - do not edit by hand.\n"
      "// Every business number in the Web MVP comes from here. The front end holds none\n"
      "// of its own, so it cannot drift from the Python core.\n"
      "window.RULEPACK = " + json.dumps(pack, ensure_ascii=False, separators=(",", ":"))
      + ";\n")
guard(ROOT / "web/assets/rulepack.js").write_text(js, encoding="utf-8")

n_cert = sum(1 for c in pack["cells"] if c["category"] == "CERT")
print(f"{PACK_VERSION} | cells {len(pack['cells'])} ({n_cert} Certification) | "
      f"functions {len(pack['functions'])} | open ORI "
      f"{len(pack['open_owner_review_items'])}")
print("ORI-02:", CV["ori_02_status"],
      "| verification:", f"{CV['summary']['verified']}V/{CV['summary']['mismatch']}M/"
                         f"{CV['summary']['not_evaluable']}NE")
print("wrote artifacts/model/rule_pack_v3.json and web/assets/rulepack.js "
      f"({len(js)//1024} KB)")
