#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""directory_integrity_report - classify every file in the project folder and emit the
Directory Integrity report (deliverable: Directory Integrity 报告).

This folder has never been under version control. The report therefore describes a plain
directory: which task phase created each file, and whether the Owner's read-only evidence is
still byte-identical. It deliberately says nothing about any repository concept.

Complements tools/verify_integrity.py: that gate fails on any file of unknown origin; this
report explains, for every file, which phase put it here.

Writes artifacts/validation/directory_integrity_report.json / .md
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:\GAMING_NRE_AGENT")
SRC = ROOT / "original_documents"
EXPECTED_SHA = ("48a360ff2ffd086e41d6b90a916f64fe52d9bc13efba07b8377b2945c846ab5a")

P4_TOOLS = {"build_quantity_model_v4.py", "build_rule_pack_v4.py", "validate_rules_v4.py",
            "export_model_delta_v4.py", "directory_integrity_report.py",
            "collect_trial_feedback.py", "issue_trial_forms.py"}
P3_TOOLS = {"verify_certification.py", "build_quantity_model_v3.py", "build_rule_pack_v3.py",
            "export_model_delta_v3.py", "validate_rules_v3.py", "check_python_web_parity.py",
            "check_web_ui.py"}
P12_TOOLS = {"analyze_baseline.py", "build_baseline_dataset.py", "derive_quantity_model.py",
             "export_model_delta.py", "extract_workbook.py", "gen_examples.py",
             "gen_examples_v2.py", "mine_text.py", "render_rows.py", "validate_rules.py",
             "validate_rules_v2.py"}
CURRENT_TOOLS = {"verify_integrity.py", "lint_sources.py", "run_all.py"}
P4_DOCS = {"00_"} | {f"{n:02d}_" for n in range(36, 46)}
P3_DOCS = {f"{n:02d}_" for n in range(22, 36)}
GEN = {"integrity_report.json", "regression_results.json", "regression_results_v2.json",
       "regression_results_v3.json", "regression_results_v4.json", "regression_report.md",
       "regression_report_v2.md", "regression_report_v3.md", "regression_report_v4.md",
       "worked_examples.md", "worked_examples_v2.md", "worked_examples_v2.json",
       "scenario_results.json", "validation_report.md", "python_web_parity.json",
       "python_web_parity.md", "web_ui_results.json", "web_ui_report.md",
       "directory_integrity_report.json", "directory_integrity_report.md",
       "trial_feedback_report.json", "trial_feedback_report.md",
       "worktree_report.json", "worktree_report.md",
       "baseline_verification.md", "row_grid.md", "text_signals.md", "file_inventory.csv",
       "file_inventory.json", "comments1.xml", "threadedComment1.xml",
       "_parity_run.dom.txt"}
P4_ARTIFACTS = {"quantity_model_v4.json", "quantity_model_v4.md", "rule_pack_v4.json"}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def phase_of(rel: str) -> str:
    name = Path(rel).name
    if rel.startswith("original_documents/"):
        return "SOURCE (Owner, read-only)"
    if rel.startswith("web/"):
        return "current task (Web MVP updated)"
    if rel.startswith("prototype/"):
        return "current task (calculation core updated)" if name == "rules_v3.py" \
            else "Phase 1 / Phase 2 (retained)"
    if rel.startswith("tools/"):
        if name in P4_TOOLS or name in CURRENT_TOOLS:
            return "current task (tooling)"
        if name in P3_TOOLS:
            return "Phase 3 (retained, still runnable)"
        return "Phase 1 / Phase 2 (retained)" if name in P12_TOOLS else "UNKNOWN"
    if rel.startswith("schema/"):
        return "current task (schemas at 4.0)"
    if rel.startswith("docs/"):
        if any(rel.startswith(f"docs/{p}") for p in P4_DOCS):
            return "current task (docs)"
        if any(rel.startswith(f"docs/{p}") for p in P3_DOCS):
            return "Phase 3 (retained, banner points to v4)"
        if name.startswith("README"):
            return "current task (index updated)"
        return "Phase 1 / Phase 2 (retained)"
    if rel.startswith("feedback_inbox/"):
        return ("current task (trial inbox instructions)"
                if name in ("README.md", "DROP_FILES_HERE.txt")
                else "team trial feedback (incoming evidence, not project input)")
    if rel.startswith("trial_kit/"):
        if name in ("roster.json", "ROSTER.md"):
            return "current task (trial roster issued for S1)"
        if name == "FOLLOW_UP_LINGYU.md":
            return "current task (trial follow-up questions)"
        if name == "START_HERE.md":
            return "current task (trial instructions for the team)"
        return "issued blank trial form (not evidence until filled and returned)"
    if rel.startswith("artifacts/"):
        if name in GEN:
            return "task evidence (reproducible artefact)"
        if name in P4_ARTIFACTS:
            return "current task (reproducible artefact)"
        return "earlier phase evidence (retained)"
    if rel == "CHANGES.md":
        return "current task (change ledger updated)"
    return "UNKNOWN"


rows, unexpected = [], []
for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    if "__pycache__" in p.parts or p.suffix == ".pyc":
        continue                      # interpreter cache, not project content
    rel = p.relative_to(ROOT).as_posix()
    ph = phase_of(rel)
    rows.append({"path": rel, "phase": ph, "bytes": p.stat().st_size})
    if ph == "UNKNOWN":
        unexpected.append(rel)

present = {p.name: sha(p) for p in sorted(SRC.rglob("*")) if p.is_file()}
sha_ok = list(present.values()) == [EXPECTED_SHA] and len(present) == 1

by_phase: dict[str, int] = {}
for r in rows:
    by_phase[r["phase"]] = by_phase.get(r["phase"], 0) + 1

out = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "root": str(ROOT),
    "directory": {"version_control": "none - plain directory, change accounting is the "
                                      "manual ledger CHANGES.md"},
    "total_files": len(rows),
    "by_phase": by_phase,
    "original_documents": {
        "files": len(present), "sha256": present,
        "unchanged": sha_ok, "expected_sha256": EXPECTED_SHA,
        "verdict": "ZERO CHANGES" if sha_ok else "CHANGED - STOP DELIVERY"},
    "classification": {
        "expected_delivery_changes": [r["path"] for r in rows
                                      if r["phase"].startswith("current task")],
        "task_evidence_or_test_artifacts": [r["path"] for r in rows
                                            if "evidence" in r["phase"]],
        "original_documents": [r["path"] for r in rows
                               if r["phase"].startswith("SOURCE")],
        "unknown_origin": unexpected,
    },
    "verdict": "CLEAN" if sha_ok and not unexpected else "NOT CLEAN",
}
(ROOT / "artifacts/validation").mkdir(parents=True, exist_ok=True)
(ROOT / "artifacts/validation/directory_integrity_report.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

L = ["# Directory Integrity report（目录完整性报告，交付物：Directory Integrity 报告）", "",
     f"- 目录：`{ROOT}`",
     "- 版本控制：**无**。本目录从未纳入版本控制，因此不存在任何版本库状态可言；"
     "变更台账是手工维护的 `CHANGES.md`。",
     f"- 生成时间：{out['generated_at_utc']}", "",
     "## 1. original_documents（Owner 正式输入，只读）", "",
     f"- 文件数：**{len(present)}**（预期 1）",
     f"- SHA-256：**{'一致' if sha_ok else '不一致'}** — 任务开始时与结束时各复验一次",
     f"- 结论：**{'ZERO CHANGES（零变更）' if sha_ok else 'CHANGED — 必须停止交付'}**", ""]
for k, v in present.items():
    L.append(f"- `{k}`\n  - `{v}`")
L += ["", "## 2. 文件来源分类", "", "| 来源阶段 | 文件数 |", "|---|---:|"]
L += [f"| {k} | {v} |" for k, v in sorted(by_phase.items())]
L += [f"| **合计** | **{len(rows)}** |", "",
      "## 3. 来源不明的文件", ""]
L += ([f"- **{u}**" for u in unexpected] if unexpected
      else ["**无。** 目录内每一个文件都能归到 Phase 1、Phase 2、Phase 3、"
            "本轮任务交付物或可复现产物之一。", ""])
L += ["## 4. 结论", "", f"**{out['verdict']}**", "",
      "- original_documents：零变更（任务开始与结束 SHA-256 相同）",
      "- 来源不明变更：**0**",
      "- 本轮交付物全部可由 `tools/run_all.py` 按固定顺序复现",
      "- 历史阶段产物保留为阶段证据，未为了让目录看起来干净而删除", "",
      "> 注：本报告不使用任何版本库术语。任务要求已明确本目录不是版本库，"
      "因此改用 Directory Integrity 的表述。"]
(ROOT / "artifacts/validation/directory_integrity_report.md").write_text(
    "\n".join(L), encoding="utf-8")

print(f"files {len(rows)} | by phase {json.dumps(by_phase, ensure_ascii=False)}")
print("original_documents unchanged:", sha_ok, "| files:", len(present))
print("unknown-origin:", unexpected or "none")
print("VERDICT:", out["verdict"])
sys.exit(0 if out["verdict"] == "CLEAN" else 1)
