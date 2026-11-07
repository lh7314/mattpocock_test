#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_web_ui - drives the three real MVP pages in a headless browser and asserts what a
user would actually see, then writes the team-facing test log.

This is not a unit test of the arithmetic (tools/check_python_web_parity.py owns that).
It checks the page behaviour the task asks for in section 25: the range is never presented
as a chosen candidate, the Appendix is never shown as a second total, review items never
stop the manual MVP, an out-of-domain input does stop its own scenario with an explanation,
and history save / open / copy / delete work.

Network is disabled. The pages run from file:// with no server, exactly as a user opens them.
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
# check_python_web_parity already re-wraps sys.stdout for UTF-8 output; re-wrapping it here
# would close the first wrapper's buffer and break printing.
from check_python_web_parity import find_browser, run_browser      # noqa: E402

OUT = ROOT / "artifacts" / "validation"


def main() -> int:
    browser = find_browser()
    if not browser:
        print("[skip] no Chromium-family browser found - Web UI probe not executed")
        return 0
    page = ROOT / "web" / "ui_test.html"
    doc = run_browser(browser, page, marker="@@UI@@")
    rows = doc.get("results", [])
    passed = sum(1 for r in rows if r["pass"])
    status = "CLEAN" if passed == len(rows) and rows else "NOT CLEAN"
    L = ["# Web MVP end-to-end test log", "",
         f"- generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
         "- driven headless from `tools/check_web_ui.py`; the pages run from `file://` with "
         "no server and no network", "",
         f"**{passed}/{len(rows)} checks pass - {status}**", "",
         "| check | result | detail |", "|---|---|---|"]
    L += [f"| {r['id']} | {'PASS' if r['pass'] else 'FAIL'} | {r['detail'] or ''} |"
          for r in rows]
    L += ["", "## Mapping to task section 25", "",
          "| required coverage | check id |", "|---|---|",
          "| 1 单一 SKU 结果 | UI-01 |",
          "| 2 4–5 SKU 范围 | UI-02 |",
          "| 6 Current Wave 与 Full Project 一致 | UI-06 |",
          "| 7 Current Wave 与 Full Project 不同 | UI-07 |",
          "| 8 主表与附表验证通过 | UI-08 |",
          "| 9 附表不重复计入 | UI-09 |",
          "| 10 范围只由 SKU 范围产生 | UI-10 |",
          "| 11 用户临时覆盖 | covered by W-11/W-23 in the parity harness |",
          "| 12 J33 不重复叠加 | UI-12, UI-12b |",
          "| 13 MEPA/HW PA 固定量 | UI-13 |",
          "| 14/15 Reuse 扣减与未扣减 | covered by W-14/W-15/W-24 in the parity harness |",
          "| 16 single_value=false 时单值字段为 null | UI-16 |",
          "| 17 显示精度不改变底层值 | UI-17 |",
          "| 18 历史分析保存 | UI-18 |",
          "| 19 历史分析打开 | UI-19 |",
          "| 20 历史分析复制 | UI-20 |",
          "| 21 Review Register 收集新问题 | UI-21 |",
          "| 22 Review Item 不阻断分析 | UI-22 |",
          "| 23 BLOCKS_FORMALIZATION 不阻塞手工 MVP | UI-23 |",
          "| 24 BLOCKS_EXECUTION 停止受影响计算并解释 | UI-24 |", "",
          "## Mapping to the S1 in-browser trial mode (this round)", "",
          "| required behaviour | check id |", "|---|---|",
          "| 首页有「参加团队试用」入口 | UI-42 |",
          "| C1-C5 一键载入、配置锁定、覆盖目标可见 | UI-40, UI-41, UI-43 |",
          "| 五个案例合起来仍覆盖 7/7 差异格 | UI-41 |",
          "| 运行后查看结果 | UI-44 |",
          "| 反馈只显示本案例涉及的问题（不要求 19 条 ORI） | UI-44 |",
          "| 提交前校验：姓名 / 日期 / 已运行 / 规则包 / 必答 / 目标格 | UI-45, UI-47 |",
          "| 单一 Submission JSON 字段齐全 | UI-46, UI-48 |",
          "| 案例确实跑到了目标差异格 | UI-46 |", ""]
    (OUT / "web_ui_report.md").write_text("\n".join(L), encoding="utf-8")
    (OUT / "web_ui_results.json").write_text(
        json.dumps({"status": status, "passed": passed, "total": len(rows),
                    "results": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print(("[PASS] " if r["pass"] else "[FAIL] ") + r["id"]
              + ("   " + r["detail"] if r["detail"] else ""))
    print("-" * 78)
    print(f"{passed}/{len(rows)} | STATUS: {status}")
    return 0 if status == "CLEAN" else 1


if __name__ == "__main__":
    sys.exit(main())
