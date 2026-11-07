#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collect_trial_feedback - turn the team's returned trial feedback into a decision list.

Closes step S1 of `docs/42_known_limits_and_next_v4.md`: the MVP exports a feedback form
(`trial-feedback-<project>-<time>.csv`); this tool reads those forms back and answers one
question - **what is still missing before the rule pack may leave DRAFT (S2)?**

Two submission formats are accepted, and they are not equal in weight:

* `trial-submission-*.json` - what `web/trial.html` (trial mode) hands back: one file that
  carries the locked case input, the full analysis, the exercised mismatch cells and the
  answers. Preferred; when one exists for a project, the older CSV/JSON pair for that same
  project is reported as superseded instead of being counted twice.
* `trial-feedback-*.csv` (+ `sample-analysis-*.json`) - the original paper-style flow. Still
  read, still the same standard, nothing dropped.

Reads   : feedback_inbox/**/trial-submission-*.json  (preferred)
          feedback_inbox/**/*.csv                    (legacy feedback forms)
          feedback_inbox/**/*.json                   (legacy analysis exports)
Writes  : artifacts/validation/trial_feedback_report.json / .md

Nothing here decides anything. It counts answers, reports disagreement verbatim, and
refuses to treat silence as agreement: an unanswered question stays open. A submission that
claims its own checks passed is not believed - `submission_gates()` recomputes them from the
embedded analysis, because a browser is not an authority.

  python tools\\collect_trial_feedback.py                 # read the inbox
  python tools\\collect_trial_feedback.py --inbox DIR     # read somewhere else
  python tools\\collect_trial_feedback.py --report-dir DIR # write the roll-up elsewhere
                                                        # (a rehearsal must not overwrite
                                                        #  the real S1 evidence file)
  python tools\\collect_trial_feedback.py --self-test     # parser/aggregator regression

Cross-checks two things a plain count would miss: which of the **five issued cases** came
back (`trial_kit/roster.json`, written by `tools/issue_trial_forms.py`), and whether the
three Function / Phase questions were actually exercised on the SKU count the disagreement
sits on - a group answer from a 2 SKU project says nothing about `Safety / FVT @ SKU6`.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:\GAMING_NRE_AGENT")
CURRENT_PACK = ROOT / "artifacts/model/rule_pack_v4.json"
CERT_VERIFY = ROOT / "artifacts/model/certification_verification.json"
GEN_JSON = ROOT / "artifacts/validation/trial_feedback_report.json"
GEN_MD = ROOT / "artifacts/validation/trial_feedback_report.md"
ROSTER = ROOT / "trial_kit/roster.json"        # what the trial was supposed to cover

OPEN_TOKENS = ("待确认", "待回复", "待业", "待定", "不确定", "无法判断", "tbd", "unknown",
               "pending", "need")
DISAGREE_TOKENS = ("不同意", "不一致", "不对", "不正确", "不准确", "不太对", "有误", "错误",
                   "不应", "no,", "no ", "no.", "disagree", "incorrect", "wrong", "否")
AGREE_TOKENS = ("同意", "正确", "一致", "对的", "可用", "够用", "yes", "agree",
                "correct", "ok", "fine", "match")


# Four explicit choices replace 同意/不同意 on v4.1 cell questions.
ANSWER_OPTIONS = {"附表正确": "AGREE", "主表正确": "DISAGREE",
                  "按条件区分": "OTHER", "无法判断": "OPEN"}


def verdict_of(text: str) -> tuple[str, str]:
    """Classify a free-text answer. Conservative: an ambiguous answer is OTHER, never AGREE."""
    t = (text or "").strip()
    if not t:
        return "UNANSWERED", ""
    low = t.lower()
    for opt in ("主表正确", "无法判断", "按条件区分", "附表正确"):
        # v4.1 cell questions offer four choices instead of 同意/不同意. 主表正确 is a
        # disagreement with the adopted Appendix value; 按条件区分 is a verdict the Owner
        # still has to resolve, so it is OTHER, and 无法判断 stays OPEN - never an agreement.
        if opt in t:
            return ANSWER_OPTIONS[opt], t
    for tok in DISAGREE_TOKENS:                    # negatives first: 不同意 contains 同意
        if tok in low:
            return "DISAGREE", t
    for tok in OPEN_TOKENS:
        if tok in low:
            return "OPEN", t
    for tok in AGREE_TOKENS:
        if tok in low:
            return "AGREE", t
    return "OTHER", t


def read_rows(path: Path) -> list[list[str]]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return [[(c or "").strip() for c in row] for row in csv.reader(fh)]


def parse_feedback(path: Path) -> dict:
    """Parse one trial-feedback CSV into (meta, sections). Unknown layout -> warning, never a guess."""
    rows = read_rows(path)
    warnings: list[str] = []
    if not rows or "Trial feedback" not in ",".join(rows[0]):
        warnings.append("not a trial feedback form (title line missing)")
    meta: dict[str, str] = {}
    sections: dict[str, list[list[str]]] = {"meta": []}
    cur = "meta"
    for r in rows:
        if not r:
            continue
        head = re.match(r"^([1-5])\.\s", r[0])
        if head:
            cur = head.group(1)
            sections[cur] = []
            continue
        sections.setdefault(cur, []).append(r)
    for r in sections.get("meta", []):
        if len(r) >= 2 and r[0]:
            meta[r[0]] = r[1]
    out = {
        "file": path.name,
        "project": meta.get("Project", ""),
        "analysis_id": meta.get("Analysis ID", ""),
        "rule_pack": meta.get("Rule pack", ""),
        "engine": meta.get("Engine", ""),
        "reviewer": meta.get("Reviewer name", ""),
        "review_date": meta.get("Review date", ""),
        "results": [], "cells": [], "items": [], "oris": [], "ui": [],
        "warnings": warnings,
    }
    for key, idx in (("results", "1"), ("cells", "2"), ("items", "3"),
                     ("oris", "4"), ("ui", "5")):
        body = sections.get(idx, [])[1:]          # drop the column header row
        for r in body:
            r = list(r) + [""] * 7
            if key == "cells":
                if not r[0] or not r[1]:
                    continue
                v, note = verdict_of(r[5])
                out["cells"].append({"cell": f"{r[0]} / {r[1]}", "adopted": r[2],
                                     "main_derived": r[3], "delta": r[4],
                                     "verdict": v, "answer": note or r[6],
                                     "comment": r[6]})
            elif key == "oris":
                if not r[0].startswith("ORI-"):
                    continue
                v, note = verdict_of(r[3])
                out["oris"].append({"id": r[0], "impact_tag": r[1], "question": r[2],
                                    "verdict": v, "answer": note, "comment": r[4]})
            elif key == "items":
                if not r[0] or r[0] == "Kind":
                    continue
                v, note = verdict_of(r[3])
                out["items"].append({"kind": r[0], "level": r[1], "blocks_mvp": r[2],
                                     "verdict": v, "answer": note, "comment": r[4]})
            elif key == "ui":
                if not r[0] or r[0] == "Topic":
                    continue
                v, note = verdict_of(r[1])
                out["ui"].append({"topic": r[0], "verdict": v, "answer": note,
                                  "comment": r[2]})
            else:
                if not r[0] or r[0] == "Item":
                    continue
                v, note = verdict_of(r[2])
                out["results"].append({"item": r[0], "produced": r[1], "verdict": v,
                                       "answer": note, "comment": r[3]})
    if not out["cells"] and not out["oris"]:
        warnings.append("no answer rows could be read - the form looks truncated")
    if not out["reviewer"]:
        warnings.append("Reviewer name is blank - the answer cannot be attributed")
    if not out["review_date"]:
        warnings.append("Review date is blank")
    return out


# ORI-02 stays ONE formal Owner question, but it is asked per Function / Phase. Two
# reviewers rejecting RF Certification while accepting Green is not a contradiction; it is
# a function-specific decision the Owner still has to take. The conflict test therefore
# runs inside a sub-decision, never across Functions.
SUB_DECISIONS = {"Green / SIT": "GREEN_SIT", "Safety / FVT": "SAFETY_FVT",
                 "RF Certification / SIT": "RF_CERTIFICATION_SIT"}
SUB_DECISION_LABEL = {"GREEN_SIT": "Green / SIT", "SAFETY_FVT": "Safety / FVT",
                      "RF_CERTIFICATION_SIT": "RF Certification / SIT",
                      "PACK_LEVEL": "整条问题（不针对具体 Function）"}


def sub_decision_of(row: dict) -> str:
    """Which sub-decision of an Owner question an answer belongs to."""
    return SUB_DECISIONS.get(row.get("group") or "", "PACK_LEVEL")


def ori_sub_decisions(rows: list[dict], ids: list[str]) -> dict[str, list[dict]]:
    """Per ORI, one tally bucket per Function / Phase sub-decision (plus a pack-level one)."""
    out: dict[str, list[dict]] = {}
    for i in ids:
        buckets: dict[str, dict] = {}
        for r in rows:
            if r.get("id") != i:
                continue
            key = sub_decision_of(r)
            b = buckets.setdefault(key, {
                "sub_decision": key, "label": SUB_DECISION_LABEL[key],
                **{v: 0 for v in ("AGREE", "DISAGREE", "OPEN", "OTHER", "UNANSWERED")},
                "seen_in": 0, "has_verdict": False, "conflict": False, "verdict": "",
                "answers": []})
            b[r["verdict"]] += 1
            b["seen_in"] += 1
            if r["verdict"] in ("AGREE", "DISAGREE"):
                b["has_verdict"] = True
            if (r.get("answer") or "").strip() or (r.get("comment") or "").strip():
                b["answers"].append({"file": r.get("file", ""),
                                     "project": r.get("project") or "",
                                     "case": r.get("case") or "",
                                     "reviewer": r.get("reviewer") or "",
                                     "verdict": r["verdict"],
                                     "answer": r.get("answer") or "",
                                     "comment": r.get("comment") or ""})
        for b in buckets.values():
            b["conflict"] = b["AGREE"] > 0 and b["DISAGREE"] > 0
            b["verdict"] = ("CONFLICT" if b["conflict"] else
                            "AGREE" if b["AGREE"] and not b["DISAGREE"] else
                            "DISAGREE" if b["DISAGREE"] and not b["AGREE"] else
                            "NO_VERDICT")
        out[i] = sorted(buckets.values(), key=lambda x: x["sub_decision"])
    return out


def tally(rows: list[dict], key: str, ids: list[str]) -> list[dict]:
    led = []
    for i in ids:
        hits = [r for r in rows if r[key] == i]
        c = {v: sum(1 for r in hits if r["verdict"] == v)
             for v in ("AGREE", "DISAGREE", "OPEN", "OTHER", "UNANSWERED")}
        answered = c["AGREE"] + c["DISAGREE"]
        led.append({key: i, "seen_in": len(hits), **c,
                    "has_verdict": answered > 0,
                    "conflict": c["AGREE"] > 0 and c["DISAGREE"] > 0,
                    "evidence": [{"file": r.get("file", r.get("project", "")),
                                  "project": r.get("project") or "",
                                  "case": r.get("case") or "",
                                  "reviewer": r.get("reviewer") or "",
                                  "question": r.get("question") or "",
                                  "sub_decision": sub_decision_of(r),
                                  "verdict": r["verdict"], "answer": r["answer"],
                                  "comment": r.get("comment") or ""}
                                 for r in hits
                                 if (r["verdict"] != "UNANSWERED"
                                     or (r.get("comment") or "").strip())]})
    return led


def canonical_keys() -> tuple[list[str], list[str], str]:
    cv = json.loads(CERT_VERIFY.read_text(encoding="utf-8-sig"))
    cells = sorted({f'{c["function_name"]} / {c["phase"]}' for c in cv["verification_grid"]
                    if c["verification_status"] == "MISMATCH"})
    rp = json.loads(CURRENT_PACK.read_text(encoding="utf-8-sig"))
    return cells, [o["id"] for o in rp["open_owner_review_items"]], rp["pack_version"]


def mismatch_cells() -> list[dict]:
    """The seven underlying Function / Phase / SKU cells that still disagree.

    The feedback form asks one question per Function / Phase group (three questions), but
    a group verdict only proves the SKU counts a trial actually priced. Reporting the
    underlying cells is what shows the difference between "answered" and "looked at".
    """
    cv = json.loads(CERT_VERIFY.read_text(encoding="utf-8-sig"))
    return sorted(
        [{"cell": f'{c["function_name"]} / {c["phase"]} @ SKU{c["sku_count"]}',
          "group": f'{c["function_name"]} / {c["phase"]}', "sku": c["sku_count"],
          "adopted": c["appendix_total"], "main_derived": c["derived_total"],
          "delta": c["delta"]}
         for c in cv["verification_grid"] if c["verification_status"] == "MISMATCH"],
        key=lambda c: (c["group"], c["sku"]))


def load_roster() -> dict:
    """The issued trial roster, if the trial was opened with tools/issue_trial_forms.py."""
    try:
        return json.loads(ROSTER.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}


def parse_analysis(path: Path) -> dict:
    """Read one returned analysis JSON. Only structural facts are taken from it."""
    out = {"file": path.name, "project": "", "analysis_id": "", "rule_pack": "",
           "priced_skus": [], "scenarios": [], "error": ""}
    try:
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    if doc.get("export_kind") != "SAMPLE_REQUIREMENT_ANALYSIS":
        out["error"] = "not an analysis export (export_kind missing)"
        return out
    out["project"] = doc.get("project_name") or ""
    out["analysis_id"] = doc.get("analysis_id") or ""
    out["rule_pack"] = doc.get("rule_package_version") or ""
    for s in doc.get("sku_result") or []:
        skus = [c for c in s.get("candidates_priced") or [] if isinstance(c, int)]
        out["priced_skus"] = sorted(set(out["priced_skus"] + skus))
        out["scenarios"].append({"scope": s.get("scenario"), "state": s.get("state"),
                                 "recommended_sku": s.get("recommended_sku"),
                                 "sku_range": s.get("sku_range")})
    return out


SUBMISSION_KIND = "SAMPLE_REQUIREMENT_TRIAL_SUBMISSION"
SUBMISSION_PREFIX = "trial-submission-"
# What web/assets/trial.js promises to write. Checked against the real file in the self-test,
# because a submission that quietly lost the reviewer name would otherwise read as evidence.
SUBMISSION_FIELDS = ("export_kind", "case_id", "project_name", "analysis_id",
                     "rule_package_version", "reviewer", "analysis_input", "analysis",
                     "covered_mismatch_cells", "exercised_skus", "feedback",
                     "submit_checks", "generated_at_utc")


def roster_case(roster: dict, case_id: str = "", project: str = "") -> dict:
    """The issued case a submission claims to be, looked up by id and by project name."""
    up = lambda s: (s or "").strip().upper()                                  # noqa: E731
    for c in (roster or {}).get("cases", []):
        if case_id and c.get("case") == case_id:
            return c
        if project and up(c.get("project_name")) == up(project):
            return c
    return {}


def submission_gates(sub: dict, issued: dict, pack_version: str) -> list[str]:
    """Re-run the six pre-submission checks from the file itself.

    The page runs the same six checks so the reviewer sees a reason before the export button
    unlocks. That is convenience only: a hand-edited or older file can say anything in
    `submit_checks`, so what counts is what is recomputed here from the embedded analysis.
    """
    findings: list[str] = []
    if not sub["reviewer"]:
        findings.append("REVIEWER_NAME：没有试用者姓名，无法归因，不能作为定稿证据")
    if not sub["review_date"]:
        findings.append("REVIEW_DATE：没有评审日期")
    if not sub["scenarios"]:
        findings.append("CASE_RUN：提交件里没有分析结果，这个案例没有真正跑过")
    if sub["rule_pack"] != pack_version:
        findings.append(f'RULE_PACK：提交件是 {sub["rule_pack"] or "（空）"}，'
                        f'当前规则包是 {pack_version}')
    missing = [q.get("cell") or q.get("id") or "?" for q in sub.get("required_rows") or []
               if q.get("missing")]
    if missing:
        findings.append("REQUIRED_ANSWERED：必答题留空：" + "；".join(missing) + "（空白不算同意）")
    if issued:
        want = issued.get("covers_cells") or []
        ran = {c.get("cell") for c in sub.get("exercised_mismatch_cells") or []}
        absent = [c for c in want if c not in ran]
        if absent:
            findings.append("TARGET_CELLS_EXERCISED：本案例应覆盖的差异格没有全部跑到：" + "；".join(absent))
        asked_ids = [q.get("id") for q in issued.get("questions_required") or []]
        got_ids = [q.get("id") for q in sub.get("required_rows") or []]
        if got_ids and got_ids != asked_ids:
            findings.append("QUESTION_SET：提交件回答的问题与发卷清单不一致"
                            f"（清单 {asked_ids} / 提交 {got_ids}）")
        if issued.get("rule_pack") and sub["rule_pack"] and issued["rule_pack"] != sub["rule_pack"]:
            findings.append(f'CASE_STALE：案例 {issued.get("case")} 是按 {issued["rule_pack"]} '
                            f'发的卷，提交件是 {sub["rule_pack"]}')
    if sub.get("certification_override_used"):
        findings.append("LOCKED_CONFIG：案例配置应为锁定，但提交件里出现了用户覆盖的采用值")
    return findings


def parse_submission(path: Path, pack_version: str, roster: dict) -> dict:
    """Read one in-browser trial submission into the same shape a feedback form parses to.

    A submission also carries the analysis, so the two things the legacy flow needed a second
    file for - which SKU counts were priced, and which mismatch cells the run really produced
    - are read from inside it instead of from a matching `sample-analysis-*.json`.
    """
    out = {"file": path.name, "format": "submission", "project": "", "analysis_id": "",
           "rule_pack": "", "engine": "", "reviewer": "", "review_date": "", "case": "",
           "results": [], "cells": [], "items": [], "oris": [], "ui": [], "warnings": [],
           "priced_skus": [], "scenarios": [], "registered_items": [],
           "exercised_mismatch_cells": [], "answered_cells": [], "required_rows": [],
           "comment": "", "certification_override_used": False, "error": "",
           "submit_checks_claimed": [], "missing_fields": [], "gate_findings": []}
    try:
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        out["error"] = f"{type(e).__name__}: {e}"
        out["warnings"].append(out["error"])
        return out
    if doc.get("export_kind") != SUBMISSION_KIND:
        out["error"] = f"not a trial submission (export_kind={doc.get('export_kind')!r})"
        out["warnings"].append(out["error"])
        return out
    out["missing_fields"] = [f for f in SUBMISSION_FIELDS if f not in doc]
    if out["missing_fields"]:
        out["warnings"].append("submission is missing field(s): "
                               + ", ".join(out["missing_fields"]))
    rev = doc.get("reviewer") or {}
    out["project"] = doc.get("project_name") or ""
    out["analysis_id"] = doc.get("analysis_id") or ""
    out["rule_pack"] = doc.get("rule_package_version") or ""
    out["engine"] = doc.get("engine_version") or ""
    out["reviewer"] = str(rev.get("name") or "").strip()
    out["review_date"] = str(rev.get("date") or "").strip()
    out["case"] = doc.get("case_id") or ""
    out["comment"] = ((doc.get("feedback") or {}).get("comment")) or ""
    out["certification_override_used"] = bool(doc.get("certification_override_used"))
    out["submit_checks_claimed"] = doc.get("submit_checks") or []
    out["exercised_mismatch_cells"] = doc.get("exercised_mismatch_cells") or []
    out["registered_items"] = doc.get("registered_items") or []
    out["priced_skus"] = [s for s in (doc.get("exercised_skus") or []) if isinstance(s, int)]
    out["scenarios"] = doc.get("scenarios") or []
    issued = roster_case(roster, out["case"], out["project"])
    kinds_by_qid = {q.get("id"): (q.get("kinds") or [])
                    for q in issued.get("questions_required") or []}

    for q in (doc.get("feedback") or {}).get("required") or []:
        v, note = verdict_of(q.get("answer") or "")
        row = {"id": q.get("id"), "kind": q.get("kind"), "question": q.get("question") or "",
               "oris": q.get("oris") or [], "missing": v == "UNANSWERED", "answer": note,
               "comment": q.get("comment") or ""}
        out["required_rows"].append(row)
        if q.get("kind") == "cell":
            out["cells"].append({"cell": q.get("group") or q.get("cell") or "",
                                 "underlying_cell": q.get("cell") or "", "sku": q.get("sku"),
                                 "adopted": q.get("adopted"),
                                 "main_derived": q.get("main_derived"),
                                 "delta": q.get("delta"), "verdict": v, "answer": note,
                                 "comment": q.get("comment") or ""})
            if v != "UNANSWERED":
                out["answered_cells"].append({"cell": q.get("cell") or "",
                                              "file": path.name, "verdict": v})
        for oid in q.get("oris") or []:
            out["oris"].append({"id": oid, "impact_tag": "必答（本案例涉及）",
                                "question": q.get("question") or "", "verdict": v,
                                "answer": note, "comment": q.get("comment") or "",
                                "group": q.get("group") or "",
                                "cell": q.get("cell") or ""})
        for k in kinds_by_qid.get(q.get("id"), []):
            out["items"].append({"kind": k, "level": "AFFECTS_ACCURACY", "blocks_mvp": "NO",
                                 "verdict": v, "answer": note,
                                 "comment": q.get("comment") or ""})
    for q in (doc.get("feedback") or {}).get("optional_oris") or []:
        v, note = verdict_of(q.get("answer") or "")
        out["oris"].append({"id": q.get("id"), "impact_tag": q.get("impact_tag") or "可选",
                            "question": q.get("question") or "", "verdict": v,
                            "answer": note, "comment": q.get("comment") or ""})
    for q in out["required_rows"]:
        if q.get("kind") == "ui":
            v, note = verdict_of(q.get("answer") or "")
            out["ui"].append({"topic": q.get("id") or "界面与流程", "verdict": v,
                              "answer": note, "comment": q.get("comment") or ""})
    if out["comment"]:
        out["ui"].append({"topic": "总体 Comment", "verdict": "OTHER",
                          "answer": out["comment"], "comment": ""})
    if not out["reviewer"]:
        out["warnings"].append("Reviewer name is blank - the answer cannot be attributed")
    if not out["review_date"]:
        out["warnings"].append("Review date is blank")
    if not out["scenarios"]:
        out["warnings"].append("no analysis inside the submission - the case was never run")
    out["gate_findings"] = submission_gates(out, issued, pack_version)
    # v4.1 cell questions make the reason mandatory. The page says so; the page is not
    # an authority, so the collector checks the same thing from the file itself.
    need_why = [q for q in issued.get("questions_required") or []
                if q.get("reason_required")]
    why_by_id = {r.get("id"): (r.get("comment") or "").strip()
                 for r in out["required_rows"]}
    blank_why = [q.get("cell") or q.get("id") for q in need_why
                 if q.get("id") in why_by_id and not why_by_id[q.get("id")]]
    if blank_why:
        out["gate_findings"].append(
            "ANSWER_REASON：Trial Form v4.1 要求写明理由，但这些问题只有选择、没有理由："
            + "；".join(blank_why))
    out["warnings"] += out["gate_findings"]
    return out


def analysis_from_submission(sub: dict) -> dict:
    """A submission carries its own analysis; expose it in the shape case coverage expects."""
    return {"file": sub["file"], "project": sub["project"], "analysis_id": sub["analysis_id"],
            "rule_pack": sub["rule_pack"], "priced_skus": list(sub["priced_skus"]),
            "scenarios": sub["scenarios"], "error": sub.get("error", ""),
            "from_submission": True}


def classify_json(path: Path) -> str:
    """submission / analysis / unreadable / unknown - by the file's own export_kind."""
    try:
        kind = json.loads(path.read_text(encoding="utf-8-sig")).get("export_kind")
    except (OSError, ValueError):
        return "unreadable"
    if kind == SUBMISSION_KIND:
        return "submission"
    if kind == "SAMPLE_REQUIREMENT_ANALYSIS":
        return "analysis"
    return "unknown"


def project_coverage(roster: dict, files: list[dict], jsons: list[dict]) -> list[dict]:
    """Case-by-case roll-up: which issued case came back, and which never did."""
    up = lambda s: (s or "").strip().upper()                                # noqa: E731
    by_csv: dict[str, list[dict]] = {}
    for f in files:
        by_csv.setdefault(up(f["project"]), []).append(f)
    by_json: dict[str, list[dict]] = {}
    for j in jsons:
        by_json.setdefault(up(j["project"]), []).append(j)
    rows, known = [], set()
    for c in roster.get("cases", []):
        key = up(c["project_name"])
        known.add(key)
        hits, jhits = by_csv.get(key, []), by_json.get(key, [])
        status = "NOT_RETURNED"
        if hits:
            status = ("STALE_RULE_PACK" if any(h["stale_rule_pack"] for h in hits)
                      else "UNATTRIBUTED" if any(not h["reviewer"] for h in hits)
                      else "RETURNED")
        rows.append({"case": c["case"], "project": c["project_name"],
                     "profile": c.get("profile", ""), "goal": c.get("goal", ""),
                     "expected_cells": c.get("covers_cells", []), "status": status,
                     "feedback_files": [h["file"] for h in hits],
                     "analysis_json": [h["file"] for h in jhits],
                     "missing_json": bool(hits) and not jhits})
    for f in files:
        if up(f["project"]) not in known:
            rows.append({"case": "-", "project": f["project"], "profile": "非清单项（自建配置）",
                         "goal": "", "expected_cells": [], "status": "RETURNED_NOT_IN_ROSTER",
                         "feedback_files": [f["file"]],
                         "analysis_json": [j["file"] for j in by_json.get(up(f["project"]), [])],
                         "missing_json": not by_json.get(up(f["project"]), [])})
    return rows


def cell_level_coverage(led: list[dict], jsons: list[dict],
                        answered_by_cell: dict[str, list[dict]] | None = None) -> tuple[list[dict], bool]:
    """Map each of the seven underlying cells onto its group verdict and the priced SKUs."""
    usable = [j for j in jsons if not j.get("error")]
    known = bool(usable)
    priced: dict[int, list[str]] = {}
    for j in usable:
        for s in j["priced_skus"]:
            priced.setdefault(s, []).append(j["project"] or j["file"])
    verdict = {c["cell"]: c for c in led}
    rows = []
    for c in mismatch_cells():
        g = verdict.get(c["group"], {})
        answered = bool(g.get("has_verdict"))
        projects = sorted(set(priced.get(c["sku"], [])))
        # A submission answers one named cell and proves in the same file that it priced it.
        # That is stronger than "someone answered the group and somebody priced that SKU".
        direct = [a for a in (answered_by_cell or {}).get(c["cell"], [])]
        state = ("EVIDENCED" if answered and projects else
                 "ANSWERED_NOT_EXERCISED" if answered else
                 "EXERCISED_NOT_ANSWERED" if projects else "NOT_COVERED")
        if direct and projects:
            state = "EVIDENCED"
        if not known and answered:      # group answered, but no JSON proves the SKU ran
            state = "ANSWERED_NO_JSON"
        rows.append({**c, "group_verdict": g.get("has_verdict", False),
                     "answered_by": [f'{a.get("project") or a.get("file")}'
                                     f'（{a["verdict"]}）' for a in direct],
                     "exercised_by": projects, "state": state})
    return rows, known


def aggregate(records: list[dict], pack_version: str,
              cell_ids: list[str], ori_ids: list[str],
              analyses: list[dict] | None = None, roster: dict | None = None) -> dict:
    # A submission is the richer record: it holds the input, the analysis and the answers.
    # If a reviewer used the page and also dropped in the older CSV/JSON pair for the same
    # project, counting both would double-weight one person's opinion - so the legacy pair is
    # listed as superseded instead of being merged.
    sub_projects = {(r.get("project") or "").strip().upper() for r in records
                    if r.get("format") == "submission" and r.get("project")}
    superseded = sorted(r["file"] for r in records
                        if r.get("format") != "submission"
                        and (r.get("project") or "").strip().upper() in sub_projects)
    records = [r for r in records
               if r.get("format") == "submission"
               or (r.get("project") or "").strip().upper() not in sub_projects]
    files = []
    all_cells: list[dict] = []
    all_oris: list[dict] = []
    all_items: list[dict] = []
    all_ui: list[dict] = []
    answered_by_cell: dict[str, list[dict]] = {}
    seen_ids: dict[str, int] = {}
    for rec in records:
        stale = bool(rec["rule_pack"]) and rec["rule_pack"] != pack_version
        seen_ids[rec["analysis_id"]] = seen_ids.get(rec["analysis_id"], 0) + 1
        files.append({"file": rec["file"], "project": rec["project"],
                      "analysis_id": rec["analysis_id"], "reviewer": rec["reviewer"],
                      "review_date": rec["review_date"], "rule_pack": rec["rule_pack"],
                      "engine": rec["engine"], "stale_rule_pack": stale,
                      "format": rec.get("format", "csv"), "case": rec.get("case", ""),
                      "priced_skus": rec.get("priced_skus", []),
                      "missing_fields": rec.get("missing_fields", []),
                      "gate_findings": rec.get("gate_findings", []),
                      "warnings": rec["warnings"]})
        for r in rec["cells"]:
            all_cells.append({**r, "file": rec["file"], "project": rec["project"],
                                    "case": rec.get("case", ""), "reviewer": rec.get("reviewer", "")})
        for a in rec.get("answered_cells") or []:
            answered_by_cell.setdefault(a["cell"], []).append(
                {**a, "project": rec["project"]})
        for r in rec["oris"]:
            all_oris.append({**r, "file": rec["file"], "project": rec["project"],
                                    "case": rec.get("case", ""), "reviewer": rec.get("reviewer", "")})
        for r in rec["items"]:
            all_items.append({**r, "file": rec["file"], "project": rec["project"],
                                    "case": rec.get("case", ""), "reviewer": rec.get("reviewer", "")})
        for r in rec["ui"]:
            all_ui.append({**r, "file": rec["file"], "project": rec["project"],
                                    "case": rec.get("case", ""), "reviewer": rec.get("reviewer", "")})

    cell_led = tally(all_cells, "cell", cell_ids)
    ori_led = tally(all_oris, "id", ori_ids)
    # One ORI, several Functions: a different conclusion on a different Function is a
    # decision the Owner still has to take, not a contradiction between reviewers.
    ori_sub = ori_sub_decisions(all_oris, ori_ids)
    for o in ori_led:
        buckets = o["sub_decisions"] = ori_sub.get(o["id"]) or []
        o["conflict"] = any(b["conflict"] for b in buckets)
        o["function_specific"] = (
            len({b["verdict"] for b in buckets if b["has_verdict"] and
                 b["verdict"] != "CONFLICT"}) > 1)
        o["conclusion"] = (
            "FUNCTION_SPECIFIC_DECISION_REQUIRED" if o["function_specific"] else "")
    function_specific = [o["id"] for o in ori_led if o["function_specific"]]
    covered = [c for c in cell_led if c["has_verdict"]]
    ori_answered = [o for o in ori_led if o["has_verdict"]]
    duplicates = sorted(k for k, n in seen_ids.items() if k and n > 1)
    stale = [f["file"] for f in files if f["stale_rule_pack"]]
    # A name and a date are what make an answer traceable. Either one missing and the file is
    # evidence about nothing, whichever format it arrived in.
    unattributed = [f["file"] for f in files if not f["reviewer"] or not f["review_date"]]
    conflicts = ([c["cell"] for c in cell_led if c["conflict"]]
                 + [o["id"] for o in ori_led if o["conflict"]])
    open_threads = ([c["cell"] for c in cell_led if c["seen_in"] and not c["has_verdict"]]
                    + [o["id"] for o in ori_led if o["seen_in"] and not o["has_verdict"]])

    cell_cov, json_known = cell_level_coverage(cell_led, analyses or [], answered_by_cell)
    case_cov = project_coverage(roster or {}, files, analyses or [])
    evidenced = [c for c in cell_cov if c["state"] == "EVIDENCED"]
    returned = [r for r in case_cov if r["feedback_files"]]
    missing_cases = [r["case"] for r in case_cov if r["status"] == "NOT_RETURNED"]
    bad_json = [j["file"] + ": " + j["error"] for j in (analyses or []) if j.get("error")]
    subs = [f for f in files if f["format"] == "submission"]
    legacy = [f for f in files if f["format"] != "submission"]
    findings = [{"file": f["file"], "project": f["project"], "case": f["case"],
                 "findings": f["gate_findings"]} for f in files if f["gate_findings"]]
    missing_fields = [f"{f['file']}: 缺字段 {m}" for f in files
                      for m in f["missing_fields"]]
    json_pack_mismatch = sorted({j["file"] for j in (analyses or [])
                                 if not j.get("error") and j.get("rule_pack")
                                 and j["rule_pack"] != pack_version})

    if not files:
        verdict = "TRIAL_NOT_STARTED"
    elif len(covered) < len(cell_ids) or len(ori_answered) < len(ori_ids):
        verdict = "EVIDENCE_INCOMPLETE"
    elif (conflicts or function_specific or stale or unattributed
          or duplicates or open_threads or findings):
        verdict = "DECISION_REQUIRED"
    else:
        verdict = "READY_FOR_S2"

    missing_cells = [c["cell"] for c in cell_led if not c["has_verdict"]]
    missing_oris = [o["id"] for o in ori_led if not o["has_verdict"]]
    actions = []
    if verdict == "TRIAL_NOT_STARTED":
        actions.append("S1 尚未开始：请试用者打开 web\\index.html →「参加团队试用」，选案例跑完"
                       "并导出 trial-submission-*.json 放进 feedback_inbox\\；"
                       "不用网页的人按 trial_kit\\ROSTER.md 手工跑，把反馈表 + 分析 JSON 一起放进来")
    if missing_cells:
        actions.append(f"仍有 {len(missing_cells)} 个主表/附表差异格没有明确结论（Q-01）："
                       + "、".join(missing_cells))
    if missing_oris:
        actions.append(f"仍有 {len(missing_oris)} 条 Owner 问题没有任何明确回答："
                       + "、".join(missing_oris))
    if missing_cases:
        actions.append("清单里已发卷但没回收反馈的案例：" + "、".join(missing_cases)
                       + "（未回收的案例不能算已试用）")
    if returned and not json_known:
        actions.append("回收到了反馈表但没有任何分析内容（既没有 trial-submission-*.json，"
                       "也没有配套的 `sample-analysis-*.json`），无法核对试用者实际跑的是哪个 "
                       "SKU 数；推荐改用网页试用模式重新提交")
    if superseded:
        actions.append("以下旧格式反馈表与同一个项目名的提交件重复，已按提交件统计，"
                       "旧文件仅登记不重复计入：" + "、".join(superseded))
    if missing_fields:
        actions.append("以下提交件缺少约定字段，按可疑件处理（不采信页面上的自检结论）："
                       + "；".join(missing_fields))
    if findings:
        actions.append("以下提交件在回收端复检时没有通过（回收端只信文件里的事实，"
                       "不信页面自检）：")
        actions += [f'  · `{f["file"]}`（{f["case"] or f["project"]}）：' + "；".join(f["findings"])
                    for f in findings]
    if bad_json:
        actions.append("以下分析 JSON 读不了，按无效件处理：" + "；".join(bad_json))
    if json_pack_mismatch:
        actions.append("以下分析 JSON 不是当前规则包产出的：" + "、".join(sorted(json_pack_mismatch)))
    if case_cov:
        not_cell = [c["cell"] for c in cell_cov if c["state"] != "EVIDENCED"]
        if not_cell:
            actions.append(f"7 个底层差异格中还没有「既被回答、又被真实跑到」的共 "
                           f"{len(not_cell)} 格：" + "、".join(not_cell))
    if function_specific:
        actions.append("这些 Owner 问题在不同 Function 上得到了不同结论，需要按 Function 分别裁决"
                       "（不同 Function 结论不同不算矛盾）：" + "、".join(function_specific))
    if conflicts:
        actions.append("不同反馈互相矛盾的条目需要 Owner 裁决：" + "、".join(conflicts))
    if open_threads:
        actions.append("被登记但只回答成「待确认 / 其它」的条目：" + "、".join(open_threads))
    if duplicates:
        actions.append("同一 Analysis ID 被提交多次（以最后一次为准，请确认）：" + "、".join(duplicates))
    if stale:
        actions.append(f"以下反馈表不是当前规则包 {pack_version} 产出的，其结论不作为定稿证据："
                       + "、".join(stale))
    if unattributed:
        actions.append("以下反馈没有 Reviewer name 或没有 Review date，无法作为可追溯证据："
                       + "、".join(unattributed))
    if verdict == "READY_FOR_S2":
        actions.append("证据齐备：可以进入 S2（规则包 DRAFT -> CONFIRMED），"
                       "本文件与随附 CSV 即定稿证据")

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "current_rule_pack": pack_version,
        "canonical_certification_cells": cell_ids,
        "canonical_owner_review_items": ori_ids,
        "files": files,
        "trial_cases": case_cov,
        "mismatch_cell_coverage": cell_cov,
        "mismatch_cell_exercise_known": json_known,
        "analysis_json": [j for j in (analyses or [])],
        "roster_rule_pack": (roster or {}).get("rule_pack", ""),
        "certification_cell_ledger": cell_led,
        "owner_review_item_ledger": ori_led,
        "analysis_registered_items": all_items,
        "ui_feedback": all_ui,
        "coverage": {
            "feedback_files": len(files),
            "submissions": len(subs),
            "legacy_feedback_files": len(legacy),
            "superseded_legacy_files": superseded,
            "submission_gate_findings": findings,
            "submission_missing_fields": missing_fields,
            "certification_cells_total": len(cell_ids),
            "certification_cells_with_verdict": len(covered),
            "underlying_mismatch_cells_total": len(cell_cov),
            "underlying_mismatch_cells_evidenced": len(evidenced),
            "trial_cases_total": len([r for r in case_cov if r["case"] != "-"]),
            "trial_cases_returned": len([r for r in returned if r["case"] != "-"]),
            "trial_cases_missing": missing_cases,
            "analysis_json_read_ok": len([j for j in (analyses or []) if not j.get("error")]),
            "analysis_json_invalid": bad_json,
            "analysis_json_stale_rule_pack": sorted(json_pack_mismatch),
            "owner_items_total": len(ori_ids),
            "owner_items_with_verdict": len(ori_answered),
            "disagreements": [c["cell"] for c in cell_led if c["DISAGREE"]]
                             + [o["id"] for o in ori_led if o["DISAGREE"]],
            "conflicting": conflicts,
            "function_specific_owner_items": function_specific,
            "stale_rule_pack_files": stale,
            "unattributed_files": unattributed,
            "duplicate_analysis_ids": duplicates,
        },
        "ori_sub_decisions": ori_sub,
        "verdict": verdict,
        "next_actions": actions,
    }


# --------------------------------------------------------------------------- report
def to_markdown(rep: dict) -> str:
    cov = rep["coverage"]
    L = ["# 试用反馈汇总报告（Trial feedback roll-up，交付物：S1 证据）", "",
         f"- 生成时间：{rep['generated_at_utc']}",
         f"- 当前规则包：`{rep['current_rule_pack']}`",
         f"- 回收反馈表：**{cov['feedback_files']}** 份", "",
         "## 1. 结论", "", f"**{rep['verdict']}**", ""]
    if rep["next_actions"]:
        L += ["**下一步（按顺序）：**", ""]
        L += [f"{i}. {a}" for i, a in enumerate(rep["next_actions"], 1)]
        L.append("")
    L += ["## 2. 主表 / 附表差异格（Q-01 的证据）", "",
          "| 差异格 | 被看到 | 同意 | 不同意 | 待确认 | 其它 | 结论 |", "|---|---:|---:|---:|---:|---:|---|"]
    for c in rep["certification_cell_ledger"]:
        state = ("已同意" if c["AGREE"] and not c["DISAGREE"] else
                 "有反对" if c["DISAGREE"] else "矛盾" if c["conflict"] else "未回答")
        L.append(f"| {c['cell']} | {c['seen_in']} | {c['AGREE']} | {c['DISAGREE']} "
                 f"| {c['OPEN']} | {c['OTHER']} | {state} |")
    L += ["", "## 3. Owner 问题回答进度（19 条唯一问题）", "",
          "| ORI | 被看到 | 同意 | 不同意 | 待确认 | 其它 | 结论 |", "|---|---:|---:|---:|---:|---:|---|"]
    for o in rep["owner_review_item_ledger"]:
        state = ("已同意" if o["AGREE"] and not o["DISAGREE"] else
                 "有反对" if o["DISAGREE"] else "矛盾" if o["conflict"] else "未回答" if not o["seen_in"]
                 else "未表态")
        L.append(f"| {o['id']} | {o['seen_in']} | {o['AGREE']} | {o['DISAGREE']} "
                 f"| {o['OPEN']} | {o['OTHER']} | {state} |")
    multi = [(o["id"], o.get("sub_decisions") or [])
             for o in rep["owner_review_item_ledger"]
             if len([b for b in (o.get("sub_decisions") or []) if b["seen_in"]]) > 1]
    if multi:
        L += ["", "## 3A. 同一条 ORI 下的子决策（按 Function / Phase）", "",
              "| ORI | 子决策 | 看到 | 同意 | 不同意 | 待确认 | 其它 | 子结论 | 谁在这一层答了 |",
              "|---|---|---:|---:|---:|---:|---:|---|---|"]
        for oid, buckets in multi:
            for b in buckets:
                if not b["seen_in"]:
                    continue
                who = "、".join(sorted({f"{a['project']}（{a['verdict']}）"
                                        for a in b["answers"] if a.get("project")})) or "-"
                L.append(f"| {oid} | {b['sub_decision']}（{b['label']}） | {b['seen_in']} | "
                         f"{b['AGREE']} | {b['DISAGREE']} | {b['OPEN']} | {b['OTHER']} | "
                         f"`{b['verdict']}` | {who} |")
        L += ["",
              "> 只有同一个子决策里出现相反结论才算冲突。不同 Function 给出不同结论输出"
              "`FUNCTION_SPECIFIC_DECISION_REQUIRED`，交 Owner 在 `docs\\44` 的 ORI-02 "
              "按 Function 确认区逐条裁决；ORI 总数不因拆分子决策而变化。"]
    L += ["", "## 2. 回收情况一览", "",
          "| 指标 | 数值 |", "|---|---|",
          f"| 有效反馈（提交件 + 旧表） | {cov['feedback_files']} |",
          f"| 其中：网页试用提交件（优先采信） | {cov['submissions']} |",
          f"| 其中：旧版反馈表 CSV | {cov['legacy_feedback_files']} |",
          f"| 与提交件同项目、已按提交件统计的旧表 | {len(cov['superseded_legacy_files'])} |",
          f"| 回收端复检未通过的提交件 | {len(cov['submission_gate_findings'])} |",
          f"| 已发卷案例 / 已回收 | {cov['trial_cases_total']} / {cov['trial_cases_returned']} |",
          f"| 规则包不一致的反馈表 | {len(cov['stale_rule_pack_files'])} |",
          f"| 缺试用者姓名或日期的反馈 | {len(cov['unattributed_files'])} |",
          f"| 重复提交的 Analysis ID | {len(cov['duplicate_analysis_ids'])} |",
          f"| Function/Phase 差异组（已回答 / 共） | "
          f"{cov['certification_cells_with_verdict']} / {cov['certification_cells_total']} |",
          f"| 底层差异单元格（已回答且已跑到 / 共 7） | "
          f"{cov['underlying_mismatch_cells_evidenced']} / "
          f"{cov['underlying_mismatch_cells_total']} |",
          f"| Owner 问题（已回答 / 共） | {cov['owner_items_with_verdict']} / "
          f"{cov['owner_items_total']} |",
          f"| 相互冲突的条目 | {len(cov['conflicting'])} |",
          f"| 分析 JSON（可读 / 无效） | {cov['analysis_json_read_ok']} / "
          f"{len(cov['analysis_json_invalid'])} |", ""]
    L += ["## 3. 案例覆盖清单（发卷 vs 回收）", ""]
    if rep["trial_cases"]:
        L += ["| 案例 | 项目名 | 配置画像 | 取证目标 | 应覆盖的差异格 | 状态 | 反馈表 | JSON |",
              "|---|---|---|---|---|---|---|---|"]
        for r in rep["trial_cases"]:
            L.append(f"| {r['case']} | `{r['project']}` | {r['profile']} | {r['goal']} | "
                     f"{'；'.join(r['expected_cells']) or '-'} | **{r['status']}** | "
                     f"{'、'.join(r['feedback_files']) or '（未回收）'} | "
                     f"{'、'.join(r['analysis_json']) or ('（缺）' if r['feedback_files'] else '-')} |")
    else:
        L.append("（尚未发卷：先运行 `python tools\\issue_trial_forms.py`，"
                 "见 `trial_kit\\ROSTER.md`）")
    L += ["", "## 4. 7 个底层差异单元格的取证状态", ""]
    if rep["mismatch_cell_coverage"]:
        L += ["| 差异单元格 | 附表采用值 | 主表推算 | 差 | 该组是否被回答 | 谁在这一点上答了 | "
              "哪些项目跑到过 | 状态 |",
              "|---|---:|---:|---:|---|---|---|---|"]
        for c in rep["mismatch_cell_coverage"]:
            L.append(f"| {c['cell']} | {c['adopted']} | {c['main_derived']} | {c['delta']} | "
                     f"{'是' if c['group_verdict'] else '否'} | "
                     f"{'、'.join(c.get('answered_by') or []) or '（无人就该格作答）'} | "
                     f"{'、'.join(c['exercised_by']) or ('（无分析内容，无法判断）'
                                        if not rep['mismatch_cell_exercise_known'] else '无')} | "
                     f"{c['state']} |")
        L += ["", "状态含义：`EVIDENCED` 该格所属组被明确回答、且有项目实际跑到该 SKU 数；"
              "`ANSWERED_NOT_EXERCISED` 只被泛泛回答、没有项目跑到该 SKU 数；"
              "`EXERCISED_NOT_ANSWERED` 跑到了但没人回答；`NOT_COVERED` 既没跑到也没回答；"
              "`ANSWERED_NO_JSON` 回收了反馈表但没有分析内容，无法核对实际跑到的 SKU 数。",
              "",
              "> 网页试用模式提交的 `trial-submission-*.json` 会同时给出「答的是哪一格」与"
              "「这一格真跑到过」，所以它能把 `ANSWERED_NOT_EXERCISED` 与 `EVIDENCED` 分开；"
              "旧版 CSV 只能回答整个 Function/Phase 组，做不到这一点。"]
    L += ["", "## 5. 无效件 / 旧版本反馈清单", ""]
    bad = ([(f, "规则包不是当前版本") for f in cov["stale_rule_pack_files"]]
           + [(f, "没有 Reviewer name 或没有 Review date，无法归因")
              for f in cov["unattributed_files"]]
           + [(f["file"], "提交件复检未通过：" + "；".join(f["findings"]))
              for f in cov["submission_gate_findings"]]
           + [(_f, m) for _f, m in (x.split(": ", 1) for x in cov["submission_missing_fields"])]
           + [(f, "同一项目已有网页提交件，本文件按旧格式登记、不重复计入")
              for f in cov["superseded_legacy_files"]]
           + [(f, "分析 JSON 读不了：" + e.split(": ", 1)[-1])
              for f, e in ((x.split(": ", 1)[0], x) for x in cov["analysis_json_invalid"])]
           + [(f, "分析 JSON 规则包不是当前版本")
              for f in cov["analysis_json_stale_rule_pack"]])
    L += ([f"- `{f}`：{why}" for f, why in bad] if bad else ["（无）"])
    L += ["", "## 6. 冲突反馈清单（同一问题给出相反结论，需 Owner 裁决）", ""]
    L += ([f"- `{c}`" for c in cov["conflicting"]] if cov["conflicting"] else ["（无）"])
    L += ["", "## 7. 尚未覆盖的问题", "",
          f"- 未回收的案例：{'、'.join(cov['trial_cases_missing']) or '（无）'}",
          f"- 未回答的差异组：{'、'.join(c['cell'] for c in rep['certification_cell_ledger'] if not c['has_verdict']) or '（无）'}",
          f"- 未回答的 Owner 问题：{'、'.join(o['id'] for o in rep['owner_review_item_ledger'] if not o['has_verdict']) or '（无）'}", ""]
    L += ["## 8. 逐份反馈", "",
          "| 文件 | 格式 | 案例 | 项目 | 试用者 | 日期 | 规则包 | 跑到的 SKU | 告警 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for f in rep["files"]:
        warn = "; ".join(f["warnings"]) or ("规则包不是当前版本" if f["stale_rule_pack"] else "-")
        L.append(f"| `{f['file']}` | {'网页提交件' if f['format'] == 'submission' else '旧版 CSV'} "
                 f"| {f['case'] or '-'} | {f['project']} | {f['reviewer'] or '（未填）'} "
                 f"| {f['review_date'] or '（未填）'} | {f['rule_pack']} "
                 f"| {'、'.join('SKU' + str(s) for s in f['priced_skus']) or '-'} | {warn} |")
    dis = [e for c in rep["certification_cell_ledger"] for e in c["evidence"]] \
        + [e for o in rep["owner_review_item_ledger"] for e in o["evidence"]]
    L += ["", "## 5. 全部作答原文（同意也保留；选择与行级理由逐字不改写）", ""]
    L += ([f"- **{e['verdict']}** ｜ 案例 {e.get('case') or '-'} ｜ 项目 "
           f"`{e.get('project') or '-'}` ｜ 试用者 {e.get('reviewer') or '（未署名）'}"
           f" ｜ 子决策 {e.get('sub_decision') or '-'}"
           f" ｜ 问题：{e.get('question') or e['file']}"
           f" ｜ 选择：{e['answer'] or '（只写了理由）'}"
           f" ｜ 理由：{e.get('comment') or '（未填写）'} ｜ 来源 `{e['file']}`"
          for e in dis] if dis else ["（无）"])
    ui = [u for u in rep["ui_feedback"] if u["answer"] or u["comment"]]
    L += ["", "## 6. 界面与流程反馈原文", ""]
    L += ([f"- **{u['topic']}** ｜ 案例 {u.get('case') or '-'} ｜ 项目 "
           f"`{u.get('project') or '-'}` ｜ 试用者 {u.get('reviewer') or '（未署名）'}"
           f" ｜ 选择：{u['answer'] or '（只写了理由）'}"
           f" ｜ 理由：{u.get('comment') or '（未填写）'} ｜ 来源 `{u['file']}`"
          for u in ui] if ui else ["（无）"])
    L += ["", "## 7. 本报告不做什么", "",
          "- 不替 Owner 决定采用哪一列：它只统计谁在什么项目上答了什么；",
          "- 不把「没回答」当成「同意」：未回答的条目一律留在缺口清单里；",
          "- 不修改规则包：`artifacts/model/rule_pack_v4.json` 的状态仍由 Owner 决定改写；",
          "- 规则包版本与当前不一致的反馈表仍然统计，但明确标注为**不作为定稿证据**。", "",
          "> 本文件由 `tools/collect_trial_feedback.py` 生成；反馈表来自 `feedback_inbox\\`。"]
    text = "\n".join(L)

    n = 0

    def _renum(m):
        nonlocal n
        n += 1
        return f"## {n}."

    return re.sub(r"^## \d+\.", _renum, text, flags=re.M)


# --------------------------------------------------------------------------- self test

def self_test() -> int:
    """Feed the parser forms that exercise every branch. Writes nothing into the project."""
    checks, fails = 0, []

    def chk(cond, label, detail=""):
        nonlocal checks
        checks += 1
        if not cond:
            fails.append(f"{label} {detail}")

    def form(project, reviewer, date, pack, cell_ids, ori_ids, cell_ans, ori_ans,
             comment="", aid="A-1"):
        lines = ["样机需求分析 - 团队试用反馈表 / Trial feedback",
                 f"Project,{project}", f"Analysis ID,{aid}", f"Rule pack,{pack}", "Engine,1.0",
                 f"Reviewer name,{reviewer}", f"Review date,{date}", "",
                 "1. 请对本次结果逐项回答（同意 / 不同意 / 待确认）+ 说明",
                 "Item,What the tool produced,Your answer,Comment",
                 "SKU result (FULL_PROJECT),state; recommended=4,,", "",
                 "2. 主表 / 附表仍然不一致的格子",
                 "Function,Phase,Adopted (Appendix),Main derived (audit),Delta,"
                 "Is the adopted value correct?,Comment"]
        for c in cell_ids:
            fname, phase = [p.strip() for p in c.split("/")]
            lines.append(f"{fname},{phase},9.6,6,3.6,{cell_ans},{comment}")
        lines += ["", "3. 本次分析登记的待确认问题", "Kind,Blocking level,Blocks manual MVP,"
                  "Your answer,Comment", "OUT_OF_DOMAIN,AFFECTS_ACCURACY,NO,,", "",
                  "4. 规则包中仍然开放的 Owner 问题", "ORI,Impact tag,Question,Your answer,"
                  "Comment"]
        lines += [f"{oid},BLOCKS_FORMALIZATION,question text,{ori_ans.get(oid, '同意')},"
                  for oid in ori_ids]
        lines += ["", "5. 界面与流程反馈", "Topic,Your answer,Comment", "字段是否够用,够用,加一列"]
        return "\ufeff" + "\r\n".join(lines)

    cells, oris, pack = canonical_keys()
    chk(len(oris) == 19, "the rule pack still carries 19 unique Owner questions", str(len(oris)))
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "f1.csv").write_text(form("P1", "张三", "2026-11-01", pack, cells, oris,
                                       "同意", {}), encoding="utf-8")
        (d / "f2.csv").write_text(form("P2", "李四", "2026-11-02", pack, cells, oris,
                                       "不同意", {"ORI-04": "待确认"}, aid="A-2"),
                                  encoding="utf-8")
        recs = [parse_feedback(p) for p in sorted(d.glob("*.csv"))]
        chk(len(recs) == 2, "two forms parsed")
        chk(recs[0]["project"] == "P1" and recs[0]["reviewer"] == "张三", "meta read back")
        chk(all(o["verdict"] == "AGREE" for o in recs[0]["oris"]), "all-agree form")
        chk(all(c["verdict"] == "AGREE" for c in recs[0]["cells"]), "every cell answered 同意")
        chk(recs[1]["cells"][0]["verdict"] == "DISAGREE", "'不同意' is DISAGREE, not AGREE")
        o4 = [o for o in recs[1]["oris"] if o["id"] == "ORI-04"][0]
        chk(o4["verdict"] == "OPEN", "'待确认' is OPEN, not an agreement")
        chk(recs[0]["ui"][0]["verdict"] == "AGREE", "section 5 answer read")
        rep = aggregate(recs, pack, cells, oris)
        chk(rep["verdict"] == "DECISION_REQUIRED", "disagreement -> DECISION_REQUIRED",
            rep["verdict"])
        rf = [c for c in rep["certification_cell_ledger"]
              if c["cell"].startswith("RF Certification")][0]
        chk(rf["conflict"] is True, "agree + disagree on one cell is a conflict")
        chk(rep["coverage"]["owner_items_with_verdict"] == len(oris),
            "every Owner question has at least one explicit verdict")
        chk(rep["coverage"]["certification_cells_with_verdict"] == len(cells),
            "every disagreeing Certification cell has at least one explicit verdict")
        led4 = [o for o in rep["owner_review_item_ledger"] if o["id"] == "ORI-04"][0]
        chk(led4["AGREE"] == 1 and led4["OPEN"] == 1 and not led4["conflict"],
            "one 同意 plus one 待确认 = answered once, no false conflict")
        rep2 = aggregate(recs[:1], pack, cells, oris)
        chk(rep2["verdict"] == "READY_FOR_S2",
            "a complete, attributed, current-rule-pack form is READY_FOR_S2",
            rep2["verdict"])
        chk("S2" in to_markdown(rep2), "the report names the next step")
        (d / "f3.csv").write_text(
            form("P3", "王五", "2026-11-03", "RP-V3.0", cells, oris, "同意", {}).replace(
                "Analysis ID,A-1", "Analysis ID,A-3"), encoding="utf-8")
        rep3 = aggregate(recs[:1] + [parse_feedback(d / "f3.csv")], pack, cells, oris)
        chk(rep3["coverage"]["stale_rule_pack_files"] == ["f3.csv"],
            "a form built by another rule pack is labelled stale",
            json.dumps(rep3["coverage"]["stale_rule_pack_files"]))
        chk(rep3["verdict"] == "DECISION_REQUIRED", "stale evidence blocks S2", rep3["verdict"])
        chk(aggregate([], pack, cells, oris)["verdict"] == "TRIAL_NOT_STARTED",
            "empty inbox -> TRIAL_NOT_STARTED")
        (d / "f4.csv").write_text(
            form("P4", "赵六", "2026-11-04", pack, cells, oris, "同意",
                 {oris[0]: ""}).replace("Analysis ID,A-1", "Analysis ID,A-4"),
            encoding="utf-8")
        rep4 = aggregate([parse_feedback(d / "f4.csv")], pack, cells, oris)
        chk(rep4["verdict"] == "EVIDENCE_INCOMPLETE",
            "an unanswered Owner question keeps the pack in EVIDENCE_INCOMPLETE",
            rep4["verdict"])
        chk([o for o in rep4["owner_review_item_ledger"] if o["id"] == oris[0]][0]["UNANSWERED"]
            == 1, "unanswered is counted, never treated as agreement")
        (d / "f5.csv").write_text(
            form("P5", "", "2026-11-05", pack, cells, oris, "同意",
                 {oris[0]: "我先问一下业务"}).replace("Analysis ID,A-1", "Analysis ID,A-5"),
            encoding="utf-8")
        rec5 = parse_feedback(d / "f5.csv")
        chk(aggregate([parse_feedback(d / "f1.csv"), parse_feedback(d / "f1.csv")],
                      pack, cells, oris)["coverage"]["duplicate_analysis_ids"] == ["A-1"],
            "the same Analysis ID submitted twice is flagged")
        rep5 = aggregate([rec5], pack, cells, oris)
        chk(rec5["warnings"], "a blank reviewer name is warned about")
        chk([o for o in rep5["owner_review_item_ledger"] if o["id"] == oris[0]][0]["OTHER"] == 1,
            "a non-committal answer is OTHER, not a verdict")
        chk(rep5["verdict"] == "EVIDENCE_INCOMPLETE",
            "an OTHER answer does not close a question", rep5["verdict"])
        bad = d / "bad.csv"
        bad.write_text("hello,world\r\n1,2\r\n", encoding="utf-8")
        chk(parse_feedback(bad)["warnings"], "a non-feedback file is flagged, not guessed")
    # --- the REAL exporter, not only a hand-written lookalike form -----------------
    # If store.js / export_trial_feedback_csv ever changes the form layout, this is what
    # catches it: the parser must read what the kernel actually writes.
    try:
        sys.path.insert(0, str(ROOT / "prototype"))
        import rules_v3 as R                                          # noqa: PLC0415
        doc = {"schema_version": "4.0", "project_name": "SELFTEST",
               "project_type": "CLEAN_SHEET", "phase_scope": ["FVT", "SIT"],
               "key_factors": {n: {"name": n, "file_value": v, "user_edited": False}
                               for n, v in dict(cpu=4, gpu=3, panel=2, ssd=2, mem=2)
                               .items()},
               "risk_reserve": {"percent": 0}}
        res = R.analyse(R.AnalysisInput.from_document(doc))
        payload = json.loads(json.dumps(R.serialise(res, analysis_id="SELFTEST",
                                                    display_precision=2)))
        real = R.export_trial_feedback_csv({"id": "SELFTEST", "project_name": "SELFTEST",
                                            "saved_at": "", "payload": payload})
        with tempfile.TemporaryDirectory() as td2:
            d2 = Path(td2)
            (d2 / "real.csv").write_text(real, encoding="utf-8")
            raw = parse_feedback(d2 / "real.csv")
            chk(raw["project"] == "SELFTEST" and raw["rule_pack"] == pack,
                "the kernel's own feedback form parses (layout has not drifted)",
                f"{raw['project']} / {raw['rule_pack']}")
            chk(len(raw["oris"]) == len(oris),
                "the real form lists all 19 unique Owner questions", str(len(raw["oris"])))
            chk(raw["cells"] and all(c["verdict"] == "UNANSWERED" for c in raw["cells"]),
                "a freshly exported form is unanswered, not pre-agreed",
                json.dumps([c["verdict"] for c in raw["cells"]] if raw["cells"] else []))
            filled = [[("" if c is None else c) for c in r] for r in
                      read_rows(d2 / "real.csv")]
            sec = 0
            for r in filled:
                if r and len(r[0]) > 2 and r[0][1] == "." and r[0][0] in "12345":
                    sec = int(r[0][0])
                if r and r[0] == "Reviewer name":
                    r[1] = "自检"
                if sec == 2 and len(r) >= 7 and r[1] in ("FVT", "SIT"):
                    r[5] = "同意"
                if sec == 4 and r and r[0].startswith("ORI-") and len(r) >= 5:
                    r[3] = "同意"
            with open(d2 / "real-filled.csv", "w", encoding="utf-8-sig", newline="") as fh:
                w = csv.writer(fh, lineterminator="\r\n")
                for r in filled:
                    w.writerow(r)
            done = parse_feedback(d2 / "real-filled.csv")
            chk(done["reviewer"] == "自检", "the reviewer name column parses")
            chk(done["cells"] and all(c["verdict"] == "AGREE" for c in done["cells"]),
                "filling the answer column turns the real form into agreements",
                json.dumps([c["verdict"] for c in done["cells"]]))
            chk(all(o["verdict"] == "AGREE" for o in done["oris"]),
                "section 4 of the real form parses into verdicts")
            aj = R.export_json_document({"id": "SELFTEST", "project_name": "SELFTEST",
                                         "saved_at": "", "payload": payload})
            (d2 / "real.json").write_text(json.dumps(aj, ensure_ascii=False), encoding="utf-8")
            ja = parse_analysis(d2 / "real.json")
            chk(not ja["error"] and ja["rule_pack"] == pack and ja["priced_skus"],
                "the kernel's own analysis JSON parses into case coverage",
                json.dumps(ja, ensure_ascii=False)[:140])
    except ImportError as e:                                       # never pretend a skip passed
        chk(False, "the Python kernel must be importable for the exporter contract check",
            str(e))
    # --- case coverage: what came back vs what the roster asked for ----------------
    fake_roster = {"rule_pack": pack, "cases": [
        {"case": "C2", "project_name": "TRIAL-C2-SKU3", "profile": "3 SKU", "goal": "g",
         "covers_cells": ["Green / SIT @ SKU3", "RF Certification / SIT @ SKU3"]},
        {"case": "C5", "project_name": "TRIAL-C5-SKU6", "profile": "6 SKU", "goal": "g2",
         "covers_cells": ["Safety / FVT @ SKU6"]}]}
    fake_json = [{"file": "a.json", "project": "TRIAL-C2-SKU3", "analysis_id": "x",
                  "rule_pack": pack, "priced_skus": [3], "scenarios": [], "error": ""}]
    repc = aggregate(recs[:1], pack, cells, oris, fake_json, fake_roster)
    chk(repc["coverage"]["trial_cases_total"] == 2
        and repc["coverage"]["trial_cases_returned"] == 0,
        "a case whose project name did not come back counts as not returned",
        json.dumps([r["status"] for r in repc["trial_cases"]]))
    by_case = {r["case"]: r for r in repc["trial_cases"]}
    chk(by_case["C2"]["status"] == "NOT_RETURNED"
        and by_case["C5"]["status"] == "NOT_RETURNED",
        "every issued case without feedback is listed as NOT_RETURNED",
        json.dumps({k: v["status"] for k, v in by_case.items()}))
    chk(repc["coverage"]["underlying_mismatch_cells_evidenced"] == 2,
        "a group verdict plus a project that priced that SKU = 2 cells evidenced",
        str(repc["coverage"]["underlying_mismatch_cells_evidenced"]))
    chk(all(c["state"] == "EVIDENCED" for c in repc["mismatch_cell_coverage"]
            if c["cell"].endswith("SKU3")), "SKU3 cells are evidenced")
    chk(all(c["state"] == "ANSWERED_NOT_EXERCISED" for c in repc["mismatch_cell_coverage"]
            if c["cell"].endswith("SKU6")),
        "group answered but 6 SKU never priced -> ANSWERED_NOT_EXERCISED",
        json.dumps([c["state"] for c in repc["mismatch_cell_coverage"]]))
    chk(len(repc["mismatch_cell_coverage"]) == 7,
        "the roll-up still reports the seven underlying cells, not only the three groups")
    repna = aggregate([], pack, cells, oris, fake_json, fake_roster)
    chk(any(c["state"] == "EXERCISED_NOT_ANSWERED" for c in repna["mismatch_cell_coverage"]
            if c["cell"].endswith("SKU3")), "priced but nobody answered -> EXERCISED_NOT_ANSWERED")
    chk(any(c["state"] == "NOT_COVERED" for c in repna["mismatch_cell_coverage"]
            if c["cell"].endswith("SKU6")), "neither priced nor answered -> NOT_COVERED")
    repnx = aggregate(recs[:1], pack, cells, oris, [], fake_roster)
    chk(repnx["coverage"]["underlying_mismatch_cells_evidenced"] == 0,
        "an answer without a project that ran the SKU is never counted as evidence")
    chk(all(c["state"] == "ANSWERED_NO_JSON" for c in repnx["mismatch_cell_coverage"]
            if c["group_verdict"]),
        "without an analysis JSON the roll-up says so instead of guessing")
    chk(repnx["verdict"] == rep2["verdict"],
        "case coverage is reported, it does not move the S1 verdict")
    chk(repnx["trial_cases"][0]["status"] == "NOT_RETURNED"
        and repnx["trial_cases"][-1]["status"] == "RETURNED_NOT_IN_ROSTER",
        "feedback for a project outside the roster is still counted, and labelled")
    with tempfile.TemporaryDirectory() as td3:
        d3 = Path(td3)
        badj = d3 / "bad.json"
        badj.write_text("{not json", encoding="utf-8")
        chk(parse_analysis(badj)["error"],
            "an unreadable analysis JSON is reported, not skipped")
        otherj = d3 / "other.json"
        otherj.write_text('{"export_kind":"SOMETHING_ELSE"}', encoding="utf-8")
        chk("not an analysis export" in parse_analysis(otherj)["error"],
            "a JSON that is not an analysis export is named")
    verdict_of_checks = [
        ("不同意", "DISAGREE"), ("同意", "AGREE"), ("否，应为 6", "DISAGREE"),
        ("待确认", "OPEN"), ("TBD", "OPEN"), ("够用", "AGREE"), ("", "UNANSWERED"),
        ("不确定，需要核对源表", "OPEN"), ("我看了下不太确定", "OTHER"), ("先这样吧", "OTHER"),
        ("是不是应该用主表", "OTHER"), ("不太对", "DISAGREE"), ("不准确", "DISAGREE"),
    ]
    for text, want in verdict_of_checks:
        chk(verdict_of(text)[0] == want, f"verdict_of({text!r}) == {want}", verdict_of(text)[0])
    # --- the in-browser trial submission (web/trial.html -> trial-submission-*.json) -------
    # Built from the ISSUED roster, not from a hand-typed fixture: if the page and the roster
    # ever disagree about what a case asks, these checks are what notice it.
    roster = load_roster()
    rcases = {c["case"]: c for c in roster.get("cases", [])}
    if not rcases:
        chk(False, "trial_kit/roster.json must exist for the submission contract checks")
    chk(len(rcases) == 5, "the roster issues five controlled cases", str(len(rcases)))
    chk(sorted({c for k in rcases for c in rcases[k]["covers_cells"]})
        == sorted(c["cell"] for c in mismatch_cells()),
        "the five issued cases together cover all seven disagreeing cells",
        str(sorted({c for k in rcases for c in rcases[k]["covers_cells"]})))
    asked = {o for c in rcases.values() for o in c["oris_required"]}
    reachable = {o for c in rcases.values() for o in c["oris_reachable"]}
    chk(len(asked) < len(oris),
        "no reviewer is asked all 19 Owner questions: each case asks only what it exercised",
        f"required per roster union {len(asked)}")
    chk(reachable >= set(oris),
        "every Owner question is still reachable in the trial, asked as optional somewhere",
        str(sorted(set(oris) - reachable)))
    for c in rcases.values():
        chk(set(c["oris_required"]) | {q["id"] for q in c["questions_optional"]} <= set(oris),
            f'{c["case"]} only asks questions the rule pack actually registers')

    def submission_of(cid, answer="同意", reviewer="张三", date="2026-11-05",
                      pack_override=None, drop_answers=(), unrun=False, drop_cells=()):
        """Mirror of what web/assets/trial.js writes, sourced from the roster."""
        c = rcases[cid]
        req = [{"id": q["id"], "kind": q["kind"], "question": q["question"],
                "oris": q["oris"], "cell": q.get("cell"), "group": q.get("group"),
                "sku": q.get("sku"), "adopted": q.get("adopted"),
                "main_derived": q.get("main_derived"), "delta": q.get("delta"),
                "answer": ("" if q["id"] in drop_answers else answer),
                "comment": "真实项目：演练用", "required": True} for q in c["questions_required"]]
        opt = [{"id": q["id"], "kind": "optional", "question": q["question"],
                "oris": q["oris"], "impact_tag": q["impact_tag"], "answer": answer,
                "comment": "", "required": False} for q in c["questions_optional"]]
        cells = [c2 for q in req if q["kind"] == "cell"
                 for c2 in [{"cell": q["cell"], "group": q["group"], "sku": q["sku"],
                             "adopted": q["adopted"], "main_derived": q["main_derived"],
                             "delta": q["delta"]}]]
        cells = [c2 for c2 in cells if c2["cell"] not in drop_cells]
        doc = {"export_kind": SUBMISSION_KIND, "export_version": "4.0",
               "submission_schema": "1.0",
               "generated_at_utc": "2026-11-05T02:00:00+00:00",
               "rule_package_version": pack_override or pack,
               "engine_version": "3.0-port", "case_id": c["case"],
               "project_name": c["project_name"], "analysis_id": "A-" + c["case"],
               "reviewer": {"name": reviewer, "date": date},
               "analysis_input": {"project_name": c["project_name"],
                                  "key_factors": c["key_factors"]},
               "analysis": {"export_kind": "SAMPLE_REQUIREMENT_ANALYSIS",
                            "project_name": c["project_name"]},
               "exercised_skus": ([] if unrun else c["priced_skus"]),
               "scenarios": ([] if unrun else c["scenarios"]),
               "registered_items": c["registered_items"],
               "exercised_mismatch_cells": ([] if unrun else cells),
               "covered_mismatch_cells": [{"cell": x, "exercised": True}
                                          for x in c["covers_cells"]],
               "feedback": {"required": req, "optional_oris": opt, "comment": "ok"},
               "submit_checks": [{"id": "CASE_RUN", "pass": not unrun}],
               "certification_override_used": False}
        return doc

    with tempfile.TemporaryDirectory() as td4:
        d4 = Path(td4)

        def write_sub(cid, **kw):
            p = d4 / f"trial-submission-{rcases[cid]['project_name']}-{cid}.json"
            p.write_text(json.dumps(submission_of(cid, **kw), ensure_ascii=False),
                         encoding="utf-8")
            return p

        # --- v4.1: what the reviewer typed must survive the roll-up (#32), and answers
        # about two different Functions must not be reported as a contradiction (#33).
        MARK = "SELFTEST-REASON-9F3"
        pv = write_sub("C2")
        dv = json.loads(pv.read_text(encoding="utf-8"))
        for q in dv["feedback"]["required"]:
            if q["id"].startswith("CELL:Green"):
                q["answer"], q["comment"] = "附表正确", MARK + " 附表数据正确"
            if q["id"].startswith("CELL:RF"):
                q["answer"], q["comment"] = "主表正确", MARK + " RF Certification 是15"
        pv.write_text(json.dumps(dv, ensure_ascii=False), encoding="utf-8")
        sv = parse_submission(pv, pack, roster)
        chk([c["verdict"] for c in sv["cells"]] == ["AGREE", "DISAGREE"],
            "v4.1 options: 附表正确 counts as agreeing with the Appendix, 主表正确 as disagreeing",
            str([(c["cell"], c["verdict"]) for c in sv["cells"]]))
        chk(not sv["gate_findings"], "a four-option answer still passes the re-check",
            str(sv["gate_findings"]))
        pv2 = write_sub("C2")
        d2 = json.loads(pv2.read_text(encoding="utf-8"))
        for q in d2["feedback"]["required"]:
            if q["id"].startswith("CELL:RF"):
                q["answer"] = "按条件区分"
            if q["id"].startswith("CELL:Green"):
                q["answer"] = "无法判断"
        pv2.write_text(json.dumps(d2, ensure_ascii=False), encoding="utf-8")
        sv2 = parse_submission(pv2, pack, roster)
        chk(sorted(c["verdict"] for c in sv2["cells"]) == ["OPEN", "OTHER"],
            "按条件区分 stays a decision to take, 无法判断 stays OPEN - never an agreement",
            str([(c["cell"], c["verdict"]) for c in sv2["cells"]]))
        rv = aggregate([sv, sv2], pack, cells, oris, [], roster)
        o2 = [o for o in rv["owner_review_item_ledger"] if o["id"] == "ORI-02"][0]
        chk(o2["conflict"] is False,
            "Green accepting the Appendix while RF Certification rejects it is not a conflict",
            str([[b["sub_decision"], b["verdict"]] for b in o2["sub_decisions"]]))
        chk(o2["conclusion"] == "FUNCTION_SPECIFIC_DECISION_REQUIRED",
            "ORI-02 reports a per-Function decision instead of a contradiction",
            o2["conclusion"])
        chk({"GREEN_SIT", "RF_CERTIFICATION_SIT"}
            <= {b["sub_decision"] for b in o2["sub_decisions"]},
            "ORI-02 is tallied inside Function / Phase sub-decisions",
            str([b["sub_decision"] for b in o2["sub_decisions"]]))
        chk("ORI-02" not in rv["coverage"]["conflicting"],
            "ORI-02 is no longer reported as a conflicting item",
            str(rv["coverage"]["conflicting"]))
        chk("ORI-02" in rv["coverage"]["function_specific_owner_items"],
            "ORI-02 is listed where a per-Function Owner decision is owed")
        chk(len(rv["owner_review_item_ledger"]) == len(oris) == 19,
            "sub-decisions did not add a formal ORI: still 19",
            str(len(rv["owner_review_item_ledger"])))
        md = to_markdown(rv)
        chk(MARK in md, "DEFECT #32: the reason typed on a row reaches the report verbatim")
        chk("RF Certification 是15" in md, "the RF Certification dissent is quoted, not dropped")
        chk(json.dumps(rv, ensure_ascii=False).count(MARK) >= 2,
            "the JSON report carries the same verbatim answer and reason")
        chk("案例 C2" in md and "张三" in md,
            "each verbatim line names the case and the reviewer it came from")
        chk("主表正确" in md and "附表正确" in md,
            "the chosen option is shown, not only a verdict token")
        chk("子决策" in md and "GREEN_SIT" in md and "RF_CERTIFICATION_SIT" in md,
            "the report shows the ORI-02 sub-decisions side by side")
        pw = write_sub("C3")
        dw = json.loads(pw.read_text(encoding="utf-8"))
        for q in dw["feedback"]["required"]:
            if q["id"].startswith("CELL:RF"):
                q["answer"] = "附表正确"
        pw.write_text(json.dumps(dw, ensure_ascii=False), encoding="utf-8")
        sw = parse_submission(pw, pack, roster)
        rw = aggregate([sv, sw], pack, cells, oris, [], roster)
        o2w = [o for o in rw["owner_review_item_ledger"] if o["id"] == "ORI-02"][0]
        rfb = [b for b in o2w["sub_decisions"]
               if b["sub_decision"] == "RF_CERTIFICATION_SIT"][0]
        chk(rfb["conflict"] is True and o2w["conflict"] is True,
            "opposite answers inside ONE Function / Phase are still a conflict",
            str([[b["sub_decision"], b["verdict"]] for b in o2w["sub_decisions"]]))
        chk(classify_json(write_sub("C2")) == "submission",
            "a trial submission is classified by its own export_kind, not by file name alone")

        # --- #34: the exact file web/trial.html exports after Trial Form v4.1 ---
        js_src = (ROOT / "web/assets/trial.js").read_text(encoding="utf-8")
        chk("trial_form_version: c.form_version" in js_src
            and "ANSWER_REASON" in js_src and "REQUIRED_ANSWERED" in js_src,
            "the page exports the form version and runs both answer gates under these names")

        def page_v41(cid, option="附表正确", why="真实项目：演练用"):
            p = write_sub(cid)
            d = json.loads(p.read_text(encoding="utf-8"))
            d["trial_form_version"] = rcases[cid].get("form_version", "")
            for q in d["feedback"]["required"]:
                if q.get("kind") == "cell":
                    q["answer"], q["comment"] = option, why
            d["submit_checks"] = [{"id": g, "pass": True} for g in (
                "REVIEWER_NAME", "REVIEW_DATE", "CASE_RUN", "RULE_PACK", "REQUIRED_ANSWERED",
                "ANSWER_REASON", "TARGET_CELLS_EXERCISED")]
            p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            return p

        p41 = page_v41("C3")
        s41 = parse_submission(p41, pack, roster)
        chk(json.loads(p41.read_text(encoding="utf-8"))["trial_form_version"] == "4.1"
            and roster.get("form_version") == "4.1",
            "#34 the submission and the roster agree on Trial Form v4.1",
            str(roster.get("form_version")))
        chk(not s41["gate_findings"],
            "#34 a complete v4.1 submission from the page passes the independent re-check",
            json.dumps(s41["gate_findings"], ensure_ascii=False))
        chk([c["verdict"] for c in s41["cells"]] == ["AGREE"]
            and s41["answered_cells"],
            "#34 the chosen option is read back as the verdict the reviewer chose",
            json.dumps([(c["cell"], c["verdict"]) for c in s41["cells"]], ensure_ascii=False))
        d41 = json.loads(p41.read_text(encoding="utf-8"))
        for q in d41["feedback"]["required"]:
            if q.get("kind") == "cell":
                q["comment"] = "   "
        p41.write_text(json.dumps(d41, ensure_ascii=False), encoding="utf-8")
        s41w = parse_submission(p41, pack, roster)
        chk(any(f.startswith("ANSWER_REASON") for f in s41w["gate_findings"]),
            "#34 an option with a blank reason is caught here too, not only by the page",
            json.dumps(s41w["gate_findings"], ensure_ascii=False))
        chk(s41w["cells"][0]["verdict"] == "AGREE"
            and any(f.startswith("ANSWER_REASON") for f in s41w["gate_findings"]),
            "ANSWER and ANSWER_REASON stay separate: a real choice plus no reason is still "
            "a refused submission, not a lost answer",
            json.dumps([s41w["cells"][0]["verdict"], len(s41w["gate_findings"])]))
        chk(roster_case(roster, "C9", "TRIAL-DOES-NOT-EXIST") == {},
            "an unknown case in a submission is reported as unknown, never guessed")
        unknown = parse_submission(p41, pack, {"cases": []})
        chk(not unknown["gate_findings"] and unknown["case"] == "C3",
            "a submission against a missing roster entry still parses and still reports its case",
            json.dumps(unknown["gate_findings"], ensure_ascii=False))
        s2 = parse_submission(write_sub("C2"), pack, roster)
        chk(not s2["gate_findings"], "a complete case submission passes the re-check",
            json.dumps(s2["gate_findings"], ensure_ascii=False))
        chk(s2["format"] == "submission" and s2["case"] == "C2"
            and s2["reviewer"] == "张三" and s2["priced_skus"] == [3],
            "the submission parses into the same record shape a CSV form produces",
            json.dumps({k: s2[k] for k in ("format", "case", "reviewer", "priced_skus")}))
        chk({c["cell"] for c in s2["cells"]} == {"Green / SIT", "RF Certification / SIT"},
            "cell answers fold onto the canonical Function / Phase groups",
            json.dumps([c["cell"] for c in s2["cells"]]))
        chk({c["underlying_cell"] for c in s2["cells"]}
            == {"Green / SIT @ SKU3", "RF Certification / SIT @ SKU3"},
            "the exact cell each answer refers to is kept, not just the group",
            json.dumps([c["underlying_cell"] for c in s2["cells"]]))
        chk({o["id"] for o in s2["oris"]} == set(oris),
            "one submission carries an answer for every Owner question (required + optional)",
            str(sorted(o["id"] for o in s2["oris"])))

        # blank is still not agreement, and a missing attribution is still not evidence
        sblank = parse_submission(write_sub("C2", drop_answers=("CELL:Green / SIT @ SKU3",),
                                            reviewer="李四"), pack, roster)
        chk(any(f.startswith("REQUIRED_ANSWERED") for f in sblank["gate_findings"]),
            "a blank required answer is caught by the collector, not only by the page",
            json.dumps(sblank["gate_findings"], ensure_ascii=False))
        gblank = [c for c in sblank["cells"] if c["underlying_cell"] == "Green / SIT @ SKU3"][0]
        chk(gblank["verdict"] == "UNANSWERED", "a blank required answer stays UNANSWERED")
        snoname = parse_submission(write_sub("C2", reviewer="  "), pack, roster)
        chk(snoname["gate_findings"] and any("REVIEWER_NAME" in f for f in snoname["gate_findings"]),
            "a submission without a name is refused as evidence")
        snodate = parse_submission(write_sub("C2", date=""), pack, roster)
        chk(any("REVIEW_DATE" in f for f in snodate["gate_findings"]),
            "a submission without a date is refused as evidence")
        rstale = parse_submission(write_sub("C2", pack_override="RP-V3.0"), pack, roster)
        chk(any(f.startswith("RULE_PACK") for f in rstale["gate_findings"])
            and rstale["rule_pack"] == "RP-V3.0",
            "an old rule pack in a submission is caught on the way back in",
            json.dumps(rstale["gate_findings"], ensure_ascii=False))
        sunrun = parse_submission(write_sub("C2", unrun=True), pack, roster)
        chk(any(f.startswith("CASE_RUN") for f in sunrun["gate_findings"])
            and not sunrun["priced_skus"],
            "a submission whose case was never run is named, not counted")
        snocell = parse_submission(write_sub("C2", drop_cells=("Green / SIT @ SKU3",)),
                                   pack, roster)
        chk(any(f.startswith("TARGET_CELL") for f in snocell["gate_findings"]),
            "a submission that did not exercise its target cell is refused",
            json.dumps(snocell["gate_findings"], ensure_ascii=False))

        # old format still readable, and never counted twice next to a submission
        (d4 / "f1.csv").write_text(form(rcases["C2"]["project_name"], "张三", "2026-11-05",
                                        pack, cells, oris, "同意", {}, aid="A-LEGACY"),
                                   encoding="utf-8")
        legacy = parse_feedback(d4 / "f1.csv")
        both = aggregate([legacy, s2], pack, cells, oris,
                         [analysis_from_submission(s2)], roster)
        chk(both["coverage"]["submissions"] == 1
            and both["coverage"]["legacy_feedback_files"] == 0,
            "a submission supersedes the older CSV for the same project instead of doubling it",
            json.dumps({k: both["coverage"][k] for k in ("submissions", "legacy_feedback_files")}))
        chk(both["coverage"]["superseded_legacy_files"] == ["f1.csv"],
            "the superseded legacy file is still listed, never silently dropped",
            json.dumps(both["coverage"]["superseded_legacy_files"]))
        legacy_only = aggregate([legacy], pack, cells, oris, [], roster)
        chk(legacy_only["coverage"]["submissions"] == 0
            and legacy_only["coverage"]["feedback_files"] == 1,
            "the legacy CSV format is still read on its own")

        # two cases together can close the trial: same 19 questions, same 3 groups, same gate
        a2 = analysis_from_submission(parse_submission(write_sub("C2"), pack, roster))
        a5 = analysis_from_submission(parse_submission(write_sub("C5"), pack, roster))
        pair = aggregate([parse_submission(write_sub("C2"), pack, roster),
                          parse_submission(write_sub("C5"), pack, roster)],
                         pack, cells, oris, [a2, a5], roster)
        chk(pair["coverage"]["owner_items_with_verdict"] == len(oris),
            "two case submissions can answer all 19 Owner questions between them",
            str(pair["coverage"]["owner_items_with_verdict"]))
        chk(pair["coverage"]["certification_cells_with_verdict"] == len(cells),
            "C2 + C5 answer all three disagreeing Function / Phase groups",
            str(pair["coverage"]["certification_cells_with_verdict"]))
        chk(pair["verdict"] == "READY_FOR_S2",
            "complete, attributed, current-rule-pack submissions reach READY_FOR_S2",
            pair["verdict"])
        chk(pair["coverage"]["trial_cases_returned"] == 2,
            "returned cases are matched by the roster project name",
            str(pair["coverage"]["trial_cases_returned"]))
        chk(len([c for c in pair["mismatch_cell_coverage"] if c["state"] == "EVIDENCED"]) == 6,
            "C2 + C5 evidence 6 of the 7 cells (SKU2 is C1's job)",
            json.dumps([c["state"] for c in pair["mismatch_cell_coverage"]]))
        three = aggregate([parse_submission(write_sub(k), pack, roster) for k in ("C1", "C2", "C5")],
                          pack, cells, oris,
                          [a2, a5, analysis_from_submission(parse_submission(
                              write_sub("C1"), pack, roster))], roster)
        chk(three["coverage"]["underlying_mismatch_cells_evidenced"] == 7,
            "adding C1 closes the seventh cell: 7/7 evidenced",
            str(three["coverage"]["underlying_mismatch_cells_evidenced"]))

    # the JS builder must keep writing the fields this reader relies on
    try:
        js = (ROOT / "web/assets/trial.js").read_text(encoding="utf-8")
        missing_js = [f for f in SUBMISSION_FIELDS if f + ":" not in js]
        chk(not missing_js,
            "web/assets/trial.js still writes every field the collector reads back",
            json.dumps(missing_js))
        chk("SAMPLE_REQUIREMENT_TRIAL_SUBMISSION" in js,
            "the page still stamps the submission with the export_kind this tool looks for")
        html = (ROOT / "web/trial.html").read_text(encoding="utf-8")
        chk("trialkit.js" in html and "trial.js" in html,
            "trial.html loads the generated roster and the trial logic")
        kit_js = (ROOT / "web/assets/trialkit.js")
        chk(kit_js.exists() and "window.TRIALKIT" in kit_js.read_text(encoding="utf-8"),
            "web/assets/trialkit.js exists - the page cannot invent cases without it")
    except OSError as e:
        chk(False, "the Web trial mode files must be present to check the export contract", str(e))

    md = to_markdown(rep)
    chk("不同意" in md and rep["verdict"] in md, "markdown carries the verdict and evidence")
    print(f"SELF-TEST: {checks} checks | FAIL: {fails or 'none'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", default=str(ROOT / "feedback_inbox"))
    ap.add_argument("--report-dir", default=str(GEN_JSON.parent),
                    help="where to write the roll-up; use a scratch dir for a rehearsal so "
                         "the real S1 evidence file is never overwritten")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    cells, oris, pack = canonical_keys()
    roster = load_roster()
    inbox = Path(args.inbox)
    csvs = sorted(inbox.rglob("*.csv")) if inbox.is_dir() else []
    all_json = sorted(inbox.rglob("*.json")) if inbox.is_dir() else []
    sub_paths = [p for p in all_json if classify_json(p) == "submission"]
    ana_paths = [p for p in all_json if classify_json(p) == "analysis"]
    other_json = [p for p in all_json if classify_json(p) not in ("submission", "analysis")]
    records, errors = [], []
    for p in csvs:
        try:
            rec = parse_feedback(p)
        except Exception as e:                                   # never skip silently
            errors.append(f"{p.name}: {type(e).__name__}: {e}")
            continue
        if any("not a trial feedback form" in w for w in rec["warnings"]):
            errors.append(f"{p.name}: not a trial feedback form - move it out of the inbox")
            continue
        records.append(rec)
    for p in sub_paths:
        try:
            records.append(parse_submission(p, pack, roster))
        except Exception as e:
            errors.append(f"{p.name}: {type(e).__name__}: {e}")
    analyses = [parse_analysis(p) for p in ana_paths]
    analyses += [analysis_from_submission(r) for r in records
                 if r.get("format") == "submission"]
    for j in analyses:
        if j["error"]:
            errors.append(f"{j['file']}: {j['error']} - not an analysis export, move it out")
    for p in other_json:
        errors.append(f"{p.name}: export_kind is neither a trial submission nor an analysis "
                      f"export - move it out of the inbox")
    rep = aggregate(records, pack, cells, oris, analyses, roster)
    rep["inbox"] = str(inbox)
    rep["submission_files"] = [p.name for p in sub_paths]
    rep["analysis_json_files"] = [p.name for p in ana_paths]
    returned = {r["analysis_id"] for r in records}
    rep["coverage"]["analysis_json_without_feedback"] = [
        p.name for p in ana_paths if not any(a in p.name for a in returned) and returned]
    if errors:
        rep["unreadable_files"] = errors
    out_dir = Path(args.report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / GEN_JSON.name).write_text(json.dumps(rep, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
    (out_dir / GEN_MD.name).write_text(to_markdown(rep), encoding="utf-8")

    cov = rep["coverage"]
    print(f"inbox {inbox} | submissions {cov['submissions']} | legacy forms "
          f"{cov['legacy_feedback_files']} | analysis JSON {len(ana_paths)} | superseded "
          f"{len(cov['superseded_legacy_files'])} | cases "
          f"{cov['trial_cases_returned']}/{cov['trial_cases_total']}")
    print(f"certification cells with a verdict: "
          f"{cov['certification_cells_with_verdict']}/{cov['certification_cells_total']} | "
          f"underlying cells evidenced: "
          f"{cov['underlying_mismatch_cells_evidenced']}/"
          f"{cov['underlying_mismatch_cells_total']} | "
          f"Owner items with a verdict: "
          f"{cov['owner_items_with_verdict']}/{cov['owner_items_total']}")
    for a in rep["next_actions"]:
        print("  ->", a)
    if errors:
        for e in errors:
            print("  !! unreadable:", e)
    print(f"VERDICT: {rep['verdict']}"
          + ("" if rep["verdict"] != "TRIAL_NOT_STARTED"
             else "  (not a failure: the trial simply has not delivered anything yet)"))
    jp, mp = out_dir / GEN_JSON.name, out_dir / GEN_MD.name
    print("wrote", jp, "/", mp)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())