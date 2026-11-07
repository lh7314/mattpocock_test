#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 worked examples. Every number is produced by the real engine at run time.

Each case is expressed as a JSON document that validates against
schema/input.schema.json and is fed through AnalysisInput.from_document(), so the
examples also prove the input contract is implementable, not just describe it.

Output: artifacts/validation/worked_examples_v2.md  (+ .json)
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:\GAMING_NRE_AGENT")
sys.path.insert(0, str(ROOT / "prototype"))
import rules_v2 as R                                          # noqa: E402


def doc(counts, **extra) -> dict:
    d = {
        "schema_version": "2.0",
        "key_factors": {n: {"name": n, "file_value": v} if v is not None
                        else {"name": n, "file_value": None, "status_user": "请补充"}
                        for n, v in counts.items()},
        "additional_demand": [],
        "reuse_items": [],
    }
    d.update(extra)
    return d


def g(x, nd=6):
    """display helper only - never used in arithmetic (D-01)"""
    return "–" if x is None else f"{x:.{nd}g}"


CASES = [
    ("EX-A", "clean minimum configuration, one spec per factor", "SINGLE 2 SKU",
     doc(dict(cpu=1, gpu=1, panel=1, ssd=1, mem=1))),

    ("EX-B", "the 4 SKU / 5 SKU tie (ORI-04)",
     "RANGE 4-5, preferred NOT_ESTABLISHED, both priced",
     doc(dict(cpu=3, gpu=3, panel=2, ssd=2, mem=2))),

    ("EX-C", "CPU=3 only, everything else unanswered",
     "no fake single answer, priced candidates limited to the tie",
     doc(dict(cpu=3, gpu=None, panel=None, ssd=None, mem=None))),

    ("EX-D", "declared second wave on the second SSD and Memory spec",
     "CURRENT_WAVE -> 3 SKU, FULL_PROJECT -> 4 SKU",
     doc(dict(cpu=2, gpu=2, panel=1, ssd=2, mem=2),
         wave_assignment={"declared_by": "USER_SELECTED", "specs": [
             {"factor": "ssd", "spec_index": 1, "wave": "CURRENT_WAVE",
              "wave_source": "USER_SELECTED"},
             {"factor": "ssd", "spec_index": 2, "wave": "LATER_WAVE",
              "wave_source": "USER_SELECTED"},
             {"factor": "mem", "spec_index": 1, "wave": "CURRENT_WAVE",
              "wave_source": "USER_SELECTED"},
             {"factor": "mem", "spec_index": 2, "wave": "LATER_WAVE",
              "wave_source": "USER_SELECTED"}]})),

    ("EX-E", "a second SSD/Memory spec exists but nobody declared its wave",
     "the Agent does NOT infer a second wave; an ORI is raised instead",
     doc(dict(cpu=2, gpu=2, panel=1, ssd=2, mem=2))),

    ("EX-F", "an explicitly UNKNOWN second-spec wave",
     "CURRENT_WAVE fans out into several readings",
     doc(dict(cpu=2, gpu=2, panel=1, ssd=2, mem=2),
         wave_assignment={"declared_by": "USER_SELECTED", "specs": [
             {"factor": "ssd", "spec_index": 1, "wave": "CURRENT_WAVE",
              "wave_source": "USER_SELECTED"},
             {"factor": "ssd", "spec_index": 2, "wave": "UNKNOWN",
              "wave_source": "USER_SELECTED"},
             {"factor": "mem", "spec_index": 1, "wave": "CURRENT_WAVE",
              "wave_source": "USER_SELECTED"},
             {"factor": "mem", "spec_index": 2, "wave": "UNKNOWN",
              "wave_source": "USER_SELECTED"}]})),

    ("EX-G", "Certification hand-entered by the user (DEC-03 override interface)",
     "the overridden Function stops contributing to the band, the rest stay UNRESOLVED",
     doc(dict(cpu=3, gpu=3, panel=2, ssd=2, mem=2),
         certification_input={"mode": "MANUAL_OVERRIDE", "overrides": [
             {"function_id": "F_RF_CERTIFICATION", "phase": "SIT", "qty": 10.0,
              "reason": "Owner supplied the RF Certification SIT quantity"}]})),

    ("EX-H", "mixed reuse claims, only the proven one may deduct (DEC-06)",
     "deduction 4.0 out of 14.0 claimed",
     doc(dict(cpu=3, gpu=2, panel=2, ssd=2, mem=2), reuse_items=[
         {"qty": 5.0, "unit": "UNIT", "function_id": "F_THM",
          "reuse_status": "ALREADY_EMBEDDED_IN_BASELINE",
          "basis": "thermal sharing is already inside the rate"},
         {"qty": 3.0, "unit": "UNIT", "reuse_status": "POTENTIAL_REUSE"},
         {"qty": 2.0, "unit": "UNIT", "reuse_status": "UNKNOWN_OVERLAP"},
         {"qty": 4.0, "unit": "UNIT", "function_id": "F_SED",
          "reuse_status": "ADDITIONAL_CONFIRMED_REUSE", "proven_not_in_baseline": True,
          "basis": "confirmed SIT spare pool, not in the baseline rate"}])),

    ("EX-I", "PCBA extra demand must not enter the unit total",
     "unit total unchanged, PCBA listed on its own line",
     doc(dict(cpu=3, gpu=2, panel=2, ssd=2, mem=2),
         additional_demand=[{"qty": 12.0, "unit": "PCBA", "label": "PCBA set for DV"}])),

    ("EX-J", "risk reserve 5 percent (illustrative - the percentage is still ORI-07)",
     "reserve charged on base demand only, full precision preserved",
     doc(dict(cpu=3, gpu=2, panel=2, ssd=2, mem=2), risk_reserve={"percent": 0.05})),

    ("EX-K", "input outside the supported SKU Definition domain",
     "OUT_OF_DOMAIN: refuse rather than extrapolate",
     doc(dict(cpu=9, gpu=3, panel=2, ssd=2, mem=2))),
]

built = []
for cid, note, expect, d in CASES:
    inp = R.AnalysisInput.from_document(d)
    res = R.analyse(inp)
    built.append({"id": cid, "note": note, "expect": expect, "document": d,
                  "payload": R.serialise(res, analysis_id=cid)})

L = ["# Phase 2 worked examples - generated by `prototype/rules_v2.py`", "",
     "Every number below is produced by the engine at run time; nothing is typed in by hand.",
     "Each case is submitted as a JSON document that validates against "
     "`schema/input.schema.json`, so these examples double as contract tests.",
     "D-01: the figures shown are the underlying decimals. No business rounding is applied; "
     "a total written as a range means the underlying model is genuinely unresolved.", "",
     "## Overview", "",
     "| Case | CPU/GPU/Panel/SSD/Mem | What it shows | Scenarios | SKU answer per scope | "
     "Total | ORI |", "|---|---|---|---|---|---|---|"]
for c in built:
    sc = c["payload"]["scenarios"]
    answers, totals = [], []
    for s in sc:
        m = s["match"]
        ans = (m["recommended_sku"] if m["recommended_sku"] is not None
               else "/".join(str(x) for x in (m.get("tie_set") or [])) or m["state"])
        answers.append(f"{'CW' if s['scope'] == 'CURRENT_WAVE' else 'FP'}={ans}")
        for r in s["results"]:
            b = r["recommended_total_band"]
            totals.append(f"{r['sku_qty']}SKU:" + (f"{b['min']:g}" if b["exact"]
                                                  else f"{b['min']:g}-{b['max']:g}"))
    L.append(f"| {c['id']} | "
             + "/".join("-" if c['document']['key_factors'][d].get('file_value') is None
                        else str(c['document']['key_factors'][d]['file_value']) for d in R.DIMS)
             + f" | {c['note']} | {len(sc)} | {'; '.join(dict.fromkeys(answers)) or 'none'} | "
             + ("; ".join(dict.fromkeys(totals)) or "-")
             + f" | {len(c['payload']['owner_review_items'])} |")
L += ["", "> `CW` = CURRENT_WAVE, `FP` = FULL_PROJECT. A hyphen in the input column means the "
      "value was left as 请补充, not defaulted to 0 or 1.", ""]

for c in built:
    p = c["payload"]
    L += ["---", "", f"## {c['id']} - {c['note']}", "",
          f"- **what it should show:** {c['expect']}",
          f"- status `{p['status']}` | rounding `{p['policy']['rounding']}` | "
          f"quantity model `{p['quantity_model_version']}`"]
    for s in p["scenarios"]:
        m = s["match"]
        scope = "CURRENT_WAVE" if s["scope"] == "CURRENT_WAVE" else "FULL_PROJECT"
        L += ["", f"### {c['id']} / {scope}", "",
              f"- counts `{json.dumps(s['counts'], ensure_ascii=False)}` | "
              f"wave basis `{s['wave_basis']}` | identical to full project: "
              f"`{s['identical_to_full_project']}`",
              f"- state **{m['state']}** | recommended_sku **{m['recommended_sku']}** | "
              f"preferred_sku **{m['preferred_sku']}** | tie `{m.get('tie_set', [])}` | "
              f"range `{m.get('sku_range')}`",
              f"- basis: " + " / ".join(m["reasons"])]
        wav = {w["factor"]: w["wave_state"] for w in s["wave_report"]}
        L.append(f"- wave report `{json.dumps(wav, ensure_ascii=False)}`")
        if not s["results"]:
            L.append("- nothing priced")
            continue
        L += ["", "| SKU | exact? | FVT | SIT | base | confirmed reuse | risk reserve | recommended |",
              "|---:|---|---|---|---|---|---|---|"]
        for r in s["results"]:
            b = r["recommended_total_band"]
            L.append("| {} | {} | {} | {} | {} | {:g} | {} | ".format(
                r["sku_qty"], r["single_value"], g(r["fvt_total"]), g(r["sit_total"]),
                g(r["base_demand"]), r["confirmed_reuse_adjustment"],
                g(r["risk_reserve"], 6))
                + ("{} |".format(g(r["recommended_total"])) if r["single_value"]
                   else "**{:.6g} – {:.6g}** (band) |".format(b["min"], b["max"])))

        r0 = s["results"][0]
        tm = r0["totals_by_model"]
        if len(tm["variants"]) > 1 or tm["variants"][0]["model_source"] != "SINGLE_ADOPTED_MODEL":
            L += ["", f"Competing evidence priced separately at {r0['sku_qty']} SKU "
                       f"(DEC-03 - nothing merged, nothing averaged):", "",
                  "| evidence source | FVT | SIT | base TOTAL | recommended total |",
                  "|---|---|---|---|---|"]
            for v in tm["variants"]:
                L.append(f"| {v['model_source']} | {v['FVT']:g} | {v['SIT']:g} | "
                         f"{v['TOTAL']:g} | {v['recommended_total']:g} |")
            if tm["variants_not_evaluable"]:
                L.append(f"| not evaluable: {', '.join(tm['variants_not_evaluable'])} "
                         f"| – | – | – | – |")
            L.append(f"| **band** | | | **{tm['band']['total_min']:g} – "
                     f"{tm['band']['total_max']:g}** (spread {tm['band']['spread']:g}) | |")

        if r0["certification_unresolved"]:
            L += ["", "Certification cells kept UNRESOLVED:", "",
                  "| Function | Phase | Main Table | Secondary Table | J33 formula | models agree? |",
                  "|---|---|---|---|---|---|"]
            for c2 in r0["certification_unresolved"]:
                L.append(f"| {c2['function_name']} | {c2['phase']} | "
                         f"{c2['models'].get('MAIN_TABLE', '–')} | "
                         f"{c2['models'].get('SECONDARY_TABLE', '–')} | "
                         f"{'declared, inputs missing' if 'J33_FORMULA' in c2['models'] else '–'} | "
                         f"{c2['models_agree']} |")

        if r0["reuse_ledger"]["items"]:
            L += ["", "Reuse ledger (DEC-06):", "",
                  "| qty | unit | declared status | applied | decision |", "|---:|---|---|---:|---|"]
            for it in r0["reuse_ledger"]["items"]:
                L.append(f"| {it['qty']:g} | {it['unit']} | {it['reuse_status']} | "
                         f"{it['applied']:g} | {it['decision']} |")
        if r0["pcba_lines_not_summed"]:
            L += ["", f"PCBA lines reported but excluded from the unit total: "
                      f"`{json.dumps(r0['pcba_lines_not_summed'], ensure_ascii=False)}`"]
    if p["owner_review_items"]:
        L += ["", "Owner Review Items raised by this input:", ""]
        for o in p["owner_review_items"]:
            L.append(f"- `{o['kind']}` — {o['why']}")
    else:
        L += ["", "No Owner Review Item raised by this input."]
    L.append("")

out = ROOT / "artifacts" / "validation"
(out / "worked_examples_v2.md").write_text("\n".join(L), encoding="utf-8")
(out / "worked_examples_v2.json").write_text(
    json.dumps(built, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[ok] {out / 'worked_examples_v2.md'}  ({len(L)} lines)")
print(f"[ok] {out / 'worked_examples_v2.json'}")
for c in built:
    sc = c["payload"]["scenarios"]
    tots = ["{}SKU:{}".format(r["sku_qty"],
                              "exact" if r["recommended_total_band"]["exact"]
                              else "{:.6g}-{:.6g}".format(r["recommended_total_band"]["min"],
                                                          r["recommended_total_band"]["max"]))
            for s in sc for r in s["results"]]
    print("{}: {} scenario(s), {} ORI, totals=[{}]".format(
        c["id"], len(sc), len(c["payload"]["owner_review_items"]), ", ".join(tots)))
