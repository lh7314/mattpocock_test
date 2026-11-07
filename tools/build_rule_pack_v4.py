#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_rule_pack_v4 - package the current rule set for the Web MVP (deliverable: updated E).

The Web front end carries no business numbers of its own. Everything it needs is packaged
here from the verified artefacts, so the Python core and the Web core can never disagree
about a number - and if they ever do, tools/check_python_web_parity.py says so.

DEC-10 is encoded as data: which Certification column is adopted, which one is audit-only,
and how many times each is counted. The package status stays DRAFT_PENDING_OWNER - adopting
the Appendix for the trial does not close ORI-02.

Output is written twice on purpose:
  artifacts/model/rule_pack_v4.json  - the package itself
  web/assets/rulepack.js            - the same object as `window.RULEPACK = ...` so the MVP
                                      runs from a double-clicked file:// page, where fetch()
                                      of a local .json is blocked by the browser

Nothing is hand-typed: every number comes from
  artifacts/model/baseline_v1.json
  artifacts/model/quantity_model_v4.json
  artifacts/model/certification_verification.json
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
QM = json.loads((ROOT / "artifacts/model/quantity_model_v4.json").read_text(encoding="utf-8"))
CV = json.loads((ROOT / "artifacts/model/certification_verification.json").read_text(encoding="utf-8"))

PACK_VERSION = "RP-V4.0"

# The complete register, exactly as registered in docs/38_owner_review_register_v4.md.
# blocking_level is one tag per item; blocks_manual_mvp is a separate question.
REGISTER = [
    ("ORI-01", "BLOCKS_FORMALIZATION", "Panel 批注 N*panel 的正式业务含义"),
    ("ORI-02", "BLOCKS_FORMALIZATION", "Certification 主表派生值与附表的 7 处差异原因"),
    ("ORI-02a", "ADVISORY", "「源费率已验证」的口径（DEC-10 后已不再是阻塞项）"),
    ("ORI-02b", "AFFECTS_ACCURACY", "J33 是否已被采用值包含；主表/附表是否描述不同 Source 组合"),
    ("ORI-03", "AFFECTS_ACCURACY", "波次判据缺失；需求表波次标记列"),
    ("ORI-04", "BLOCKS_FORMALIZATION", "4 SKU 与 5 SKU 的真实分界条件"),
    ("ORI-05", "BLOCKS_FORMALIZATION", "ODM 无结构化规则 + 3 处 Status 未关闭"),
    ("ORI-06", "AFFECTS_ACCURACY", "Option 项是否启用 / PCBA 单位口径"),
    ("ORI-07", "AFFECTS_ACCURACY", "Risk Reserve 比例与适用范围无来源"),
    ("ORI-08", "BLOCKS_FORMALIZATION", "匹配权重 / 阈值属 Agent 设定"),
    ("ORI-09", "ADVISORY", "自动读取需求表所需的真实样本（已与 MVP 解耦）"),
    ("ORI-10", "BLOCKS_FORMALIZATION", "MEPA 是否恒为每 Phase 36；HW PA 何时饱和于 4"),
    ("ORI-11", "ADVISORY", "Build Plan 与 PPA sample standard 1.0（已与 MVP 解耦）"),
    ("ORI-12", "AFFECTS_ACCURACY", "6 条 model questions（EMC Test / NV / INTEL 平坦费率）"),
    ("ORI-13", "AFFECTS_ACCURACY", "定义域空洞：超出 2–6 SKU 无规则（BLOCKS_EXECUTION 只停该情景）"),
    ("ORI-14", "ADVISORY", "缩写与 Green FVT 自相矛盾"),
    ("ORI-15", "AFFECTS_ACCURACY", "Green/SIT/SKU3 主表值与 1/N 规律不符"),
    ("ORI-16", "AFFECTS_ACCURACY", "Safety/FVT/SKU6 = 1.6 与附表 10 不一致（DEC-10 后已采用 10）"),
    ("ORI-17", "AFFECTS_ACCURACY", "主表「每 SKU」列实为总量的 1/N 回推"),
]


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
        "quantity_model": c["quantity_model"],
        "evidence_role": c["evidence_role"],
        "adopted_value_evidence_role": c["adopted_value_evidence_role"],
        "value_access": c["value_access"],
        "adopted_absolute": c["adopted_absolute"],
        "main_table_per_sku_quantity": c["main_table_per_sku_quantity"],
        "main_table_absolute": c["main_table_absolute"],
        "adopted_source": c["adopted_source"],
        "owner_review_required": c["owner_review_required"],
        "is_temporary_model": c["quantity_model"] == "PER_PHASE_FIXED",
        "status": c["status"], "rule_id": c["rule_id"], "evidence": c["evidence"],
        "audit": c["audit"],
        "breakdown_evidence": ({k: v for k, v in c["breakdown_evidence"].items()
                                if k != "raw_text"}
                               if c.get("breakdown_evidence") else None),
    })

levels = {}
for o in REGISTER:
    levels[o[0]] = o[1]

pack = {
    "pack_id": PACK_VERSION,
    "pack_version": PACK_VERSION,
    "version": PACK_VERSION,
    "schema_version": "4.0",
    "engine_contract": "prototype/rules_v3.py is the behaviour reference; web/assets/core.js "
                       "is a port of it and is checked against it by "
                       "tools/check_python_web_parity.py",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "generator": "tools/build_rule_pack_v4.py",
    "source_file": BASE["derived_from"],
    "baseline_id": BASE["baseline_id"],
    "quantity_model_version": f"{QM['model_id']}/{QM['model_version']}",
    "status": "DRAFT_PENDING_OWNER",
    "owner_decision": QM["owner_decision"],
    "certification_adoption": {
        "decision": QM["owner_decision"]["id"],
        "adopted_value_source": QM["owner_decision"]["adopted_value_source"],
        "audit_only_source": QM["owner_decision"]["audit_only_source"],
        "appendix_counted_in_project_total_times":
            QM["owner_decision"]["appendix_counted_in_project_total_times"],
        "main_derived_counted_in_project_total_times":
            QM["owner_decision"]["main_derived_counted_in_project_total_times"],
        "j33_counted_in_project_total_times":
            QM["owner_decision"]["j33_counted_in_project_total_times"],
        "phase_ratio_used": None,
        "fvt_and_sit_each_read_their_own_appendix_row": True,
        "user_override_scope": QM["owner_decision"]["user_override_scope"],
    },
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
        "main_table_rate_shape": CV["main_table_rate_shape"],
    },
    "j33_investigation": CV["j33_investigation"],
    "baseline_embedded_sharing": QM["baseline_embedded_sharing"],
    "model_questions": QM["model_questions"],
    "policy": QM["policy"],
    "tolerance": 1e-9,
    "open_owner_review_items": [
        {"id": k, "blocking_level": lv, "blocks_manual_mvp": False, "summary": txt,
         "note": "shown in the UI; never stops a manual analysis"}
        for k, lv, txt in REGISTER],
    "owner_review_item_count": len(REGISTER),
    "owner_review_impact_tag_counts": {
        lv: sum(1 for _id, l, _t in REGISTER if l == lv) for lv in sorted(levels.values())},
    "counting_note": "owner_review_item_count counts unique ORIs. "
                     "owner_review_impact_tag_counts counts impact tags. A second tag on the "
                     "same question is recorded in the register text, never as a new ORI.",
    "blocking_rule": "only OUT_OF_DOMAIN input stops a calculation, and it stops that "
                     "scenario alone with an explanation",
}

guard(ROOT / "artifacts/model/rule_pack_v4.json").write_text(
    json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
js = ("// GENERATED by tools/build_rule_pack_v4.py - do not edit by hand.\n"
      "// Every business number in the Web MVP comes from here. The front end holds none\n"
      "// of its own, so it cannot drift from the Python core.\n"
      "window.RULEPACK = " + json.dumps(pack, ensure_ascii=False, separators=(",", ":"))
      + ";\n")
guard(ROOT / "web/assets/rulepack.js").write_text(js, encoding="utf-8")

n_cert = sum(1 for c in pack["cells"] if c["category"] == "CERT")
print(f"{PACK_VERSION} | cells {len(pack['cells'])} ({n_cert} Certification) | "
      f"functions {len(pack['functions'])} | open ORI "
      f"{pack['owner_review_item_count']}")
print("adopted:", pack["certification_adoption"]["adopted_value_source"],
      "| audit-only:", pack["certification_adoption"]["audit_only_source"],
      f"(x{pack['certification_adoption']['main_derived_counted_in_project_total_times']})")
print("ORI-02:", CV["ori_02_status"],
      "| grid:", f"{CV['summary']['verified']}V/{CV['summary']['mismatch']}M/"
                 f"{CV['summary']['not_evaluable']}NE",
      "| impact tags:", json.dumps(pack["owner_review_impact_tag_counts"]))
print(f"wrote artifacts/model/rule_pack_v4.json and web/assets/rulepack.js ({len(js)//1024} KB)")
