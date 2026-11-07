#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""issue_trial_forms - open the controlled team trial: a fixed case roster, blank forms and
the in-browser trial mode the Web MVP reads from `web/assets/trialkit.js`.

Step S1 asks the team to run 3-5 real projects. Two things make that hard in practice:

* the team has to invent a configuration, and the config decides which of the seven
  disagreeing Certification cells the reviewer ever sees - a trial that only runs simple
  projects can never produce evidence for `Green / SIT` (3 SKU) or `Safety / FVT` (6 SKU);
* a blank form has to be produced by the same kernel that produced the numbers, otherwise
  the reviewer judges something other than what the tool exported.

So this tool fixes the roster and issues everything the trial needs. Every case is a Key
Factor combination taken from the Owner's own SKU definitions (CleanSheet C79:C83), and the
expected result column is computed by `prototype/rules_v3.py` at issue time - never typed
by hand.

`web/assets/trialkit.js` is the same roster in the form a double-clicked `file://` page can
read (fetch() of a local .json is blocked by the browser). `web/trial.html` builds its case
picker from it, so the Web trial mode and this tool can never disagree about what C1-C5 are.

The question scope is computed per case, from what that case actually priced and actually
registered - a reviewer is never asked about a 4/5 tie, a wave or a Panel annotation that
their own case did not produce. Owner questions the case cannot be answered on are still
reachable (asked as optional) so the trial can close all 19 without demanding 19 answers
from one person.

Reads  : artifacts/model/rule_pack_v4.json, artifacts/model/certification_verification.json
Writes : trial_kit/roster.json, trial_kit/ROSTER.md, trial_kit/forms/<project>.csv,
         web/assets/trialkit.js

Rules  : a form is never overwritten (a partially filled form is evidence);
         nothing is written into `feedback_inbox\\`; the rule pack is only read, never touched.

  python tools\\issue_trial_forms.py            # issue what is missing, print the roster
  python tools\\issue_trial_forms.py --check    # drift check only, writes nothing
  python tools\\issue_trial_forms.py --force    # re-issue (deletes nothing, overwrites forms)
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"D:\GAMING_NRE_AGENT")
SRC_DIR = ROOT / "original_documents"
KIT = ROOT / "trial_kit"
FORMS = KIT / "forms"
GEN_JSON = KIT / "roster.json"
GEN_MD = KIT / "ROSTER.md"
GEN_JS = ROOT / "web/assets/trialkit.js"

sys.path.insert(0, str(ROOT / "prototype"))
import rules_v3 as R                                          # noqa: E402

# --------------------------------------------------------------------------- roster
# key_factors are Key Factor counts, i.e. what the reviewer types into web\new.html - or,
# from this round on, what web\trial.html fills in and locks so nothing has to be typed.
# `source` names the CleanSheet cell that publishes the recipe, so a reviewer can check
# the case against the Owner's own sheet instead of trusting this file.
ROSTER = [
    {"case": "C1", "slug": "SKU2", "profile": "简单配置（低配项目）",
     "key_factors": {"cpu": 2, "gpu": 1, "panel": 1, "ssd": 1, "mem": 1},
     "source": "C79 (2SKU: 1-2*CPU +1*GPU +1-2*Panel +SSD*1 +Mem*1)",
     "goal": "最低门槛项目：检查 SKU 判定、总量、界面字段是否够用",
     "wave": None},
    {"case": "C2", "slug": "SKU3", "profile": "Green / SIT 差异取证（必须 3 SKU）",
     "key_factors": {"cpu": 3, "gpu": 2, "panel": 1, "ssd": 1, "mem": 1},
     "source": "C80 (3SKU: 2-3*CPU +2*GPU +1*Panel +SSD*1 +Mem*1)",
     "goal": "唯一能看到 Green / SIT 的 SKU 数（附表 6.0 vs 主表推算 9.0）",
     "wave": None},
    {"case": "C3", "slug": "SKU4", "profile": "中等配置（4 SKU 单值）",
     "key_factors": {"cpu": 2, "gpu": 2, "panel": 2, "ssd": 2, "mem": 2},
     "source": "C81 (4SKU: 2-4*CPU +2-3*GPU +2*Panel +SSD*2 +Mem*2)",
     "goal": "落在 4 SKU 定义内的项目，检查是否给出单值而不是范围",
     "wave": None},
    {"case": "C4", "slug": "RANGE45", "profile": "4-5 SKU 范围项目（SR-09 现场）",
     "key_factors": {"cpu": 3, "gpu": 3, "panel": 2, "ssd": 2, "mem": 2},
     "source": "C81 与 C82 的交集（同时满足 4SKU 与 5SKU 定义）",
     "goal": "工具会给出 RANGE 4-5 并登记 SKU_TIE_NOT_RESOLVABLE；试用者要回答"
             "「这个范围在真实项目里能不能接受」，这是 Q-02 / SR-09 的直接证据",
     "wave": None},
    {"case": "C5", "slug": "SKU6-WAVE", "profile": "复杂配置 + LATER_WAVE（必须 6 SKU）",
     "key_factors": {"cpu": 5, "gpu": 3, "panel": 3, "ssd": 2, "mem": 2},
     "source": "C83 (6SKU: 4-5*CPU +3*GPU +2-3*Panel +SSD*2 +Mem*2-3)；全表唯一的波次"
               "提法是 C80 括号里的「(or SSD/Mem spec *2, arrange 2nd wave)」，"
               "它只提到 SSD / Memory，没有判据，也没有提到 CPU / Panel（ORI-03）",
     "goal": "唯一能看到 Safety / FVT 的 SKU 数（附表 10.0 vs 主表推算 9.6）；"
             "同时把 cpu 第 5 条与 panel 第 3 条标为后续波次，检查 Current Wave 与 "
             "Full Project 是否真的分开。该波次声明只是本案例的试用假设："
             "波次到底按什么条件分，正是 ORI-03 要问试用者的问题",
     # The fork below is the only reason C5 prices SKU4 / SKU5 at all: without it Current
     # Wave collapses back to 6 SKU and RF Certification @ SKU4 / SKU5 lose their only
     # in-trial evidence here. So the fork stays; what changes is its provenance. The
     # formal requirement sheet has no wave column (ORI-03), so labelling the fork
     # FORMAL_REQUIREMENT_SHEET would carry a false citation into every C5 submission the
     # Owner later reads. USER_SELECTED is both the truthful label and the only form
     # DEC-04 accepts: an Agent must never infer a wave from a second SSD / Memory Spec.
     "wave": {"declared_by": "USER_SELECTED",
              "assumption": True,
              "assumption_note": "波次为案例预设的试用假设，未经 Owner 确认；"
                                 "需求表没有波次列（ORI-03），本案不据此下业务结论",
              "specs": [{"factor": "cpu", "spec_index": 5, "wave": "LATER_WAVE",
                         "wave_source": "USER_SELECTED", "spec_label": "cpu5"},
                        {"factor": "panel", "spec_index": 3, "wave": "LATER_WAVE",
                         "wave_source": "USER_SELECTED", "spec_label": "panel3"}]}},
]

# ------------------------------------------------------------------ question scope
# Which Owner questions a reviewer can answer *from this case*. Every entry below is keyed
# on something the case really produced (a priced cell, a registered Review Item, a Panel
# Spec count), because asking about a 4/5 tie the reviewer never saw produces a guess, not
# evidence. Questions the case cannot be answered on stay reachable as optional so the trial
# can still close all 19 without interrogating one person about all 19.
KIND_ORI = {
    "SKU_TIE_NOT_RESOLVABLE": ["ORI-04", "ORI-08"],
    "WAVE_ASSIGNMENT_NOT_PROVIDED": ["ORI-03"],
    "WAVE_ASSIGNMENT_UNKNOWN": ["ORI-03"],
    "OUT_OF_DOMAIN_INPUT": ["ORI-13"],
    "CERTIFICATION_SOURCE_VALIDATION_MISMATCH": ["ORI-02"],
    "CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE": ["ORI-02"],
    "CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED": ["ORI-02b"],
    "REUSE_PROOF_MISSING": [],
    "REUSE_OVERLAP_UNPROVEN": [],
}
# Two cells the Owner register names by name rather than by Function / Phase group.
CELL_ORI = {"Green / SIT @ SKU3": ["ORI-15"], "Safety / FVT @ SKU6": ["ORI-16"]}

# v4.1: 同意 / 不同意 asked the wrong question. A mismatch cell is a choice between two
# candidate quantities, so the form now asks which candidate is right and makes the
# reason mandatory - an unexplained 不同意 cannot be given to the Owner as evidence.
FORM_VERSION = "4.1"
CELL_OPTIONS = ["附表正确", "主表正确", "按条件区分", "无法判断"]
CELL_OPTION_HELP = {
    "附表正确": "附表总量就是业务上正确的数量（维持 DEC-10 的采用值）",
    "主表正确": "主表推算才是正确的，附表需要更正",
    "按条件区分": "要看条件，请把条件写在理由里",
    "无法判断": "现在判断不了（不算同意，也不取消差异）",
}
# C1 / C2 were issued and returned under Trial Form v4.0. Their evidence stays valid and
# is never re-issued; only the still-open cases move to v4.1 wording.
RETURNED_CASES = {
    "C1": "trial-submission-TRIAL-C1-SKU2-20261106-1353.json",
    "C2": "trial-submission-TRIAL-C2-SKU3-20261106-1359.json",
}
RF_FUNCTION = "RF Certification"          # J33 is attached to this function (ORI-02b)

# kind -> one grouped question. Registered items arrive in sets of three on every run;
# asking the same thing three times is noise, so they are asked once, together.
REGISTER_GROUP = [
    ("RANGE", ("SKU_TIE_NOT_RESOLVABLE",),
     "工具给出了 4-5 SKU 的范围、没有替你选一档。这个范围在你的真实项目里能接受吗？"
     "如果不能，你实际靠什么条件判定它是 4 还是 5？",
     "本次结果里确实出现了 RANGE（4 SKU 与 5 SKU 同时成立）"),
    ("WAVE", ("WAVE_ASSIGNMENT_NOT_PROVIDED", "WAVE_ASSIGNMENT_UNKNOWN"),
     "你们项目里「当前波次 / 后续波次」实际按什么条件划分？"
     "（本工具只认「Spec 被明确标为后续波次」这一条判据）",
     "本案例登记了波次相关待确认项"),
    ("CERTVALID", ("CERTIFICATION_SOURCE_VALIDATION_MISMATCH",
                   "CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE",
                   "CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED"),
     "本次 Certification 给出了「与主表不一致 / 附表校验未全部通过 / J33 只适用特定组合」的提示。"
     "这些提示你看得懂吗？会影响你使用这个结果吗？",
     "本案例实际触发了这些认证校验提示"),
    ("REUSE", ("REUSE_PROOF_MISSING", "REUSE_OVERLAP_UNPROVEN"),
     "你手上有「已证明不在基准内含共享中」的可复用样机吗？数量与依据是什么？",
     "本案例登记了复用相关待确认项"),
]
# Questions every case can be answered on because every case prices those rows.
UNIVERSAL_QUESTIONS = [
    {"id": "ORI-10", "kind": "universal", "required": True, "oris": ["ORI-10"],
     "question": "结果里的 MEPA 每 Phase 恒为 36、HW PA 恒为 4：在你的真实项目里成立吗？",
     "why": "本案例的 Function 明细里就有这两行"},
    {"id": "ORI-07", "kind": "universal", "required": True, "oris": ["ORI-07"],
     "question": "本工具默认 Risk Reserve = 0%（源表没有已确认比例）。"
                 "你的项目实际会另加预留吗？比例按什么算？",
     "why": "本案例的合计就是按 0% 算出来的"},
]
UI_QUESTION = {"id": "UI-USE", "kind": "ui", "required": True, "oris": [],
               "question": "这次的输出看得懂吗？字段够你判断吗？（缺什么直接写在下面 Comment）",
               "why": "界面与流程反馈，不影响业务数值"}


def guard(path: Path) -> Path:
    rp = path.resolve()
    if str(rp).startswith(str(SRC_DIR.resolve())):
        raise RuntimeError(f"refusing to write inside original_documents: {rp}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def project_of(case: dict) -> str:
    return f"TRIAL-{case['case']}-{case['slug']}"


def build_document(case: dict) -> dict:
    doc = {"schema_version": "4.0", "project_name": project_of(case),
           "project_type": "CLEAN_SHEET", "phase_scope": ["FVT", "SIT"],
           "key_factors": {n: {"name": n, "file_value": v, "user_edited": False}
                           for n, v in case["key_factors"].items()},
           "risk_reserve": {"percent": 0}}
    if case.get("wave"):
        doc["wave_assignment"] = case["wave"]
    return doc


def run_case(case: dict) -> tuple[dict, str]:
    """Run one roster case through the real kernel. Returns (payload, feedback CSV text)."""
    res = R.analyse(R.AnalysisInput.from_document(build_document(case)))
    payload = json.loads(json.dumps(R.serialise(res, analysis_id=project_of(case),
                                                display_precision=2)))
    record = {"id": project_of(case), "project_name": project_of(case),
              "saved_at": "", "payload": payload, "document": build_document(case)}
    return payload, R.export_trial_feedback_csv(record)


def describe(payload: dict) -> dict:
    """What the case exercises, read back out of the engine output."""
    out = {"scenarios": [], "mismatch_cells": [], "registered": [], "priced_skus": []}
    for s in payload.get("scenarios", []):
        m = s["match"]
        rng = m.get("sku_range")
        out["scenarios"].append({
            "scope": s["scope"], "state": m["state"],
            "recommended_sku": m["recommended_sku"],
            "sku_range": f"{rng[0]}-{rng[1]}" if rng else "",
            "totals": {str(r["sku_qty"]): r["recommended_total"] for r in s["results"]},
            "certification": {str(r["sku_qty"]): r["certification_demand"]
                              for r in s["results"]}})
        for r in s["results"]:
            out["priced_skus"].append(r["sku_qty"])
            for c in (r.get("certification") or {}).get("mismatched_cells", []) or []:
                out["mismatch_cells"].append(
                    {"group": f'{c["function_name"]} / {c["phase"]}',
                     "cell": f'{c["function_name"]} / {c["phase"]} @ SKU{r["sku_qty"]}',
                     "function": c["function_name"], "phase": c["phase"],
                     "sku": r["sku_qty"],
                     "adopted": c.get("adopted_total"),
                     "main_derived": c.get("main_table_derived_total"),
                     "delta": c.get("delta")})
    out["priced_skus"] = sorted(set(out["priced_skus"]))
    out["registered"] = sorted({o["kind"] for o in payload.get("owner_review_items", [])})
    out["mismatch_cells"] = sorted({json.dumps(c, sort_keys=True, ensure_ascii=False): c
                                    for c in out["mismatch_cells"]}.values(),
                                   key=lambda c: c["cell"])
    return out


def questions_for(case: dict, info: dict, ori: dict) -> tuple[list[dict], list[dict]]:
    """The questions this case can be answered on, and the Owner questions it cannot.

    Returned questions are the *contract* for the trial page: `web/trial.html` renders them,
    `tools/collect_trial_feedback.py` re-checks that every required one was answered and
    that the cells they refer to really were priced. Nothing is asked because it seemed
    reasonable to ask.
    """
    asked: list[str] = []
    qs: list[dict] = []

    for c in info["mismatch_cells"]:
        oris = ["ORI-02"] + CELL_ORI.get(c["cell"], [])
        if c.get("function") == RF_FUNCTION:
            oris.append("ORI-02b")
        oris = [o for o in dict.fromkeys(oris) if o in ori]
        asked += oris
        qs.append({"id": f"CELL:{c['cell']}", "kind": "cell", "required": True,
                   "cell": c["cell"], "group": c["group"], "sku": c["sku"],
                   "function": c.get("function", ""), "phase": c.get("phase", ""),
                   "adopted": c["adopted"], "main_derived": c["main_derived"],
                   "delta": c["delta"], "oris": oris,
                   "options": CELL_OPTIONS, "option_help": CELL_OPTION_HELP,
                   "reason_required": True, "form_version": FORM_VERSION,
                   "question": f'{c["cell"]}：本工具采用附表 {c["adopted"]}，'
                               f'主表推算为 {c["main_derived"]}（差 {c["delta"]}）。'
                               f'在你的项目里哪一个才是业务上正确的数量？'
                               f'只能选：{" / ".join(CELL_OPTIONS)}。',
                   "why": "本案例实际跑到了这个 SKU 数，这一格才会出现"})

    for gid, kinds, text, why in REGISTER_GROUP:
        hit = [k for k in kinds if k in info["registered"]]
        if not hit:
            continue
        oris = [o for o in dict.fromkeys(o for k in hit for o in KIND_ORI.get(k, []))
                if o in ori]
        asked += oris
        qs.append({"id": gid, "kind": "group", "required": True, "question": text,
                   "why": why, "oris": oris, "kinds": hit})

    if int((case["key_factors"] or {}).get("panel") or 0) >= 2 and "ORI-01" in ori:
        qs.append({"id": "PANEL", "kind": "group", "required": True, "oris": ["ORI-01"],
                   "question": "本项目有多个 Panel Spec。源表 D2:H2 上的「N*panel」批注，"
                               "在你的业务里到底指什么？（本工具不猜，只做记录）",
                   "why": f'本案例 Panel Spec 数量为 '
                          f'{case["key_factors"]["panel"]}，批注才会被记录进证据'})
        asked.append("ORI-01")

    for q in UNIVERSAL_QUESTIONS:
        if all(o in ori for o in q["oris"]):
            qs.append(dict(q))
            asked += q["oris"]
    qs.append(dict(UI_QUESTION))

    seen = set(asked)
    required = [{"id": q["id"], "kind": q["kind"], "question": q["question"],
                 "why": q.get("why", ""), "oris": q.get("oris", []),
                 **({"cell": q["cell"], "group": q["group"], "sku": q["sku"],
                     "adopted": q["adopted"], "main_derived": q["main_derived"],
                     "delta": q["delta"],
                     # Trial Form v4.1: the four choices, their meaning and the
                     # mandatory reason are part of the issued contract, so they
                     # have to survive into roster.json / trialkit.js.
                     "options": q["options"], "option_help": q["option_help"],
                     "reason_required": q["reason_required"],
                     "form_version": q["form_version"]} if q["kind"] == "cell" else {}),
                 **({"kinds": q["kinds"]} if q.get("kinds") else {})}
                for q in qs]
    optional = [{"id": oid, "kind": "optional", "required": False, "oris": [oid],
                 "question": ori[oid]["summary"], "impact_tag": ori[oid]["blocking_level"]}
                for oid in ori if oid not in seen]
    return required, optional


def raw(path: Path) -> str:
    """Read a form exactly as written - the CSV is CRLF and must stay CRLF for the compare."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return fh.read()


def all_seven_cells() -> list[str]:
    cv = json.loads((ROOT / "artifacts/model/certification_verification.json")
                    .read_text(encoding="utf-8-sig"))
    return sorted(f'{c["function_name"]} / {c["phase"]} @ SKU{c["sku_count"]}'
                  for c in cv["verification_grid"]
                  if c["verification_status"] == "MISMATCH")


def issue(*, force: bool = False, check_only: bool = False) -> int:
    pack_doc = json.loads((ROOT / "artifacts/model/rule_pack_v4.json")
                          .read_text(encoding="utf-8-sig"))
    pack = pack_doc["pack_version"]
    ori = {o["id"]: o for o in pack_doc["open_owner_review_items"]}
    seven = all_seven_cells()
    cases, problems, written = [], [], []

    for case in ROSTER:
        payload, csv_text = run_case(case)
        name = project_of(case)
        form = FORMS / f"trial-feedback-{name}.csv"
        info = describe(payload)
        required, optional = questions_for(case, info, ori)
        entry = {"case": case["case"], "project_name": name, "profile": case["profile"],
                 "key_factors": case["key_factors"], "wave_assignment": case.get("wave"),
                 "source": case["source"], "goal": case["goal"],
                 "rule_pack": pack, "form_file": f"trial_kit/forms/{form.name}",
                 "form_version": FORM_VERSION,
                 "issue_status": ("RETURNED" if case["case"] in RETURNED_CASES
                                    else "OPEN"),
                 "returned_submission": RETURNED_CASES.get(case["case"], ""),
                 "covers_cells": sorted(c["cell"] for c in info["mismatch_cells"]),
                 "covers_groups": sorted({c["group"] for c in info["mismatch_cells"]}),
                 "priced_skus": info["priced_skus"], "scenarios": info["scenarios"],
                 "registered_items": info["registered"],
                 "locked": {"project_name": True, "key_factors": True,
                            "wave_assignment": True, "risk_reserve": True},
                 "questions_required": required, "questions_optional": optional,
                 "oris_required": sorted({o for q in required for o in q["oris"]}),
                 "oris_reachable": sorted({o for q in required + optional
                                           for o in q["oris"]})}
        cases.append(entry)
        if check_only:
            if not form.exists():
                problems.append(f"{form.name}: not issued yet")
            elif raw(form) != csv_text.lstrip("\ufeff"):
                problems.append(f"{form.name}: content differs from what the current kernel "
                                f"exports - the form was edited in place, or the rule pack "
                                f"changed since it was issued")
        else:
            if form.exists() and not force:
                if raw(form) != csv_text.lstrip("\ufeff"):
                    problems.append(f"{form.name}: exists and differs from the current export "
                                    f"- left untouched (a filled form is evidence)")
                continue
            FORMS.mkdir(parents=True, exist_ok=True)
            # utf-8, NOT utf-8-sig: the kernel's export already starts with a BOM, adding a
            # second one here is what made every pristine form look "edited" to --check.
            form.write_text(csv_text, encoding="utf-8", newline="")
            written.append(form.name)

    covered = sorted({c for e in cases for c in e["covers_cells"]})
    uncovered = [c for c in seven if c not in covered]
    req_all = sorted({o for e in cases for o in e["oris_required"]})
    reach_all = sorted({o for e in cases for o in e["oris_reachable"]})
    missing_ori = sorted(set(ori) - set(reach_all))
    roster = {"generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "rule_pack": pack, "join_key": "project_name",
              "cases": cases, "all_mismatch_cells": seven,
              "cells_covered_by_roster": covered,
              "cells_not_covered_by_roster": uncovered,
              "form_version": FORM_VERSION,
              "cell_options": CELL_OPTIONS,
              "returned_cases": sorted(RETURNED_CASES),
              "ori_total": len(ori),
              "ori_required_by_some_case": req_all,
              "ori_reachable_by_some_case": reach_all,
              "ori_not_reachable_in_trial": missing_ori}

    # The Web MVP reads the roster as JS: a double-clicked file:// page cannot fetch() a
    # local .json. `generated_at_utc` is left out on purpose so the file is byte-stable for
    # a given rule pack - that is what makes `--check` able to tell a real edit from noise.
    kit = {k: v for k, v in roster.items() if k != "generated_at_utc"}
    kit["generator"] = "tools/issue_trial_forms.py"
    js = ("// GENERATED by tools/issue_trial_forms.py - do not edit by hand.\n"
          "// The five controlled S1 trial cases: inputs, expected results and the question\n"
          "// scope, all computed from prototype/rules_v3.py and rule_pack_v4.json at issue\n"
          "// time. The Web trial mode holds no case data of its own.\n"
          "window.TRIALKIT = "
          + json.dumps(kit, ensure_ascii=False, separators=(",", ":")) + ";\n")
    if check_only:
        if not GEN_JS.exists():
            problems.append("web/assets/trialkit.js: not issued yet")
        elif GEN_JS.read_text(encoding="utf-8") != js:
            problems.append("web/assets/trialkit.js: content differs from the current roster "
                            "- the Web trial mode would offer cases this tool no longer issues")
    else:
        guard(GEN_JS).write_text(js, encoding="utf-8")

    if not check_only:
        KIT.mkdir(parents=True, exist_ok=True)
        GEN_JSON.write_text(json.dumps(roster, ensure_ascii=False, indent=1), encoding="utf-8")
        GEN_MD.write_text(to_markdown(roster), encoding="utf-8")

    print(f"roster: {len(cases)} cases | rule pack {pack} | "
          f"mismatch cells covered {len(covered)}/{len(seven)} | "
          f"ORI asked as required {len(req_all)}/{len(ori)} | reachable "
          f"{len(reach_all)}/{len(ori)}")
    for e in cases:
        sc = "; ".join(f'{s["scope"]}={s["state"]}'
                       f'{"(" + str(s["recommended_sku"]) + ")" if s["recommended_sku"] else ""}'
                       f'{"/" + s["sku_range"] if s["sku_range"] else ""}'
                       for s in e["scenarios"])
        print(f'  {e["case"]:3s} {e["project_name"]:20s} '
              f'{"/".join(f"{k}{v}" for k, v in e["key_factors"].items()):24s} {sc}')
        print(f'      covers: {", ".join(e["covers_cells"]) or "(none)"} | '
              f'{len(e["questions_required"])} required question(s), '
              f'{len(e["questions_optional"])} optional ORI')
    if uncovered:
        print(f"  !! cells no case in this roster can exercise: {uncovered}")
    if missing_ori:
        print(f"  !! Owner questions no case can even offer: {missing_ori}")
    for p in problems:
        print("  !!", p)
    if written:
        print(f"issued {len(written)} blank form(s) into {FORMS}")
    if check_only:
        print("CHECK:", "DRIFT" if problems else "OK")
    else:
        print(f"wrote {GEN_JSON.relative_to(ROOT)} / {GEN_MD.relative_to(ROOT)} / "
              f"{GEN_JS.relative_to(ROOT)}")
        print("下一步：试用者打开 web\\index.html →「参加团队试用」，或把 trial_kit\\forms "
              "里的表分发给不方便用网页的人；两种方式都填完后放进 feedback_inbox\\。")
    return 1 if (problems and check_only) else 0


def to_markdown(r: dict) -> str:
    L = ["# 试用案例清单（Trial roster，S1 用）", "",
         f"- 规则包：`{r['rule_pack']}`（仍是 DRAFT_PENDING_OWNER，本清单不改状态）",
         f"- 生成时间：{r['generated_at_utc']}",
         f"- 回收关联方式：按 **Project** 列逐字对应（`{r['join_key']}`）",
         f"- 推荐用法：双击 `web\\index.html` →「参加团队试用」，选案例即自动载入本清单里的"
         "项目名、Key Factors 与 Wave（案例配置锁定，不让试用者改）；"
         "本文件同时是给不使用网页的同事的备用清单。", "",
         "## 1. 案例清单", "",
         "| 案例 | 项目名（必须逐字使用） | Key Factors（在 web\\new.html 输入） | 配置画像 | 覆盖的差异格 | 依据 |",
         "|---|---|---|---|---|---|"]
    for e in r["cases"]:
        kf = " / ".join(f"{k}={v}" for k, v in e["key_factors"].items())
        L.append(f"| {e['case']} | `{e['project_name']}` | {kf} | {e['profile']} | "
                 f"{'；'.join(e['covers_cells']) or '（无差异格）'} | {e['source']} |")
    L += ["", "## 2. 每个案例的预期结果（由 prototype/rules_v3.py 实算，不是手写）", "",
          "| 案例 | 场景 | SKU 判定 | 推荐 SKU | 范围 | 总量 | Certification | 登记的待确认项 |",
          "|---|---|---|---|---|---|---|---|"]
    for e in r["cases"]:
        for s in e["scenarios"]:
            tot = "; ".join(f"SKU{k}={v}" for k, v in s["totals"].items()) or "（不出价）"
            cer = "; ".join(f"SKU{k}={v}" for k, v in s["certification"].items()) or "-"
            reg = "、".join(e["registered_items"]) if s["scope"] == "FULL_PROJECT" else ""
            L.append(f"| {e['case']} | {s['scope']} | {s['state']} | "
                     f"{s['recommended_sku'] or '（不给单值）'} | {s['sku_range'] or '-'} | "
                     f"{tot} | {cer} | {reg} |")
    L += ["", "## 3. 每个案例只问它自己涉及的问题", "",
          "试用者不需要回答全部 19 条 Owner 问题：案例没跑到的东西，问了只能换来猜测。",
          f"本清单合计把 {len(r['ori_required_by_some_case'])}/{r['ori_total']} 条问题列为"
          f"必答（按案例），其余 {r['ori_total'] - len(r['ori_required_by_some_case'])} 条"
          "作为可选题仍会出现在每个人的反馈页里，"
          f"可答可不答；本清单保证 {len(r['ori_reachable_by_some_case'])}/{r['ori_total']} "
          "条问题至少被问到一次。", "",
          "| 案例 | 必答问题 | 由该案例引出的 Owner 问题 | 可选（其余 ORI） |",
          "|---|---|---|---|"]
    for e in r["cases"]:
        qs = "<br>".join(f"· {q['question']}" for q in e["questions_required"])
        L.append(f"| {e['case']} | {qs} | {'、'.join(e['oris_required'])} | "
                 f"{'、'.join(q['id'] for q in e['questions_optional'])} |")
    L += ["", "## 4. 为什么是这五个案例", "",
          "7 个主表/附表仍然不一致的格子分布在特定 SKU 数上，试用项目没跑到的 SKU 数，"
          "就永远拿不到那格的证据：", "",
          "| 差异格 | 需要的 SKU 数 | 由哪个案例覆盖 |", "|---|---|---|"]
    for c in r["all_mismatch_cells"]:
        sku = c.split("SKU")[-1]
        who = [e["case"] for e in r["cases"] if c in e["covers_cells"]]
        L.append(f"| {c} | {sku} | {'、'.join(who) or '（本清单未覆盖）'} |")
    L += ["", f"- 本清单覆盖 {len(r['cells_covered_by_roster'])}/{len(r['all_mismatch_cells'])} 格。",
          "", "## 5. 怎么用", "",
          "**推荐（网页内置试用模式）**：",
          "1. 双击 `web\\index.html` →「参加团队试用」；",
          "2. 选一个案例 → 载入（项目名、Key Factors、Wave 自动填好并锁定）；",
          "3. 运行分析 → 看结果 → 只回答本案例涉及的问题 → 填姓名与日期；",
          "4. 点「导出试用提交件」，得到 `trial-submission-<项目>-<时间>.json`；",
          "5. 把这个文件放进 `feedback_inbox\\`，然后 `python tools\\collect_trial_feedback.py`。",
          "",
          "**备用（不用网页）**：",
          "1. 新建分析，Project Name 逐字复制上表，Key Factors 按上表输入；"
          "C5 另外把 cpu 第 5 条、panel 第 3 条的 Wave 选「后续波次」；",
          "2. 运行分析 → 导出 JSON + 试用反馈表；",
          "3. 填好反馈表的署名、日期与每一行答复，"
          "把反馈表和分析 JSON 一起复制到 `feedback_inbox\\`"
          "（`trial_kit\\forms\\` 里的空白表不要就地填写）。",
          "",
          "> 案例配置来自 CleanSheet 自己的 SKU 定义（C79:C83）。如果试用者手上有同类型的真实项目，"
          "请用真实项目的 Key Factors 跑同一条案例，并在 Comment 里写真实项目名——"
          "本清单只保证覆盖面，不替代真实项目。", ""]
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="drift check only, write nothing")
    ap.add_argument("--force", action="store_true", help="re-issue forms (overwrite)")
    a = ap.parse_args()
    sys.exit(issue(force=a.force, check_only=a.check))