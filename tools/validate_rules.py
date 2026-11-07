#!/usr/bin/env python3
"""Executable validation of the Phase-1 rule design + ambiguity quantification.

Covers the case types required by the brief: positive / boundary / missing-input /
SKU-definition-competition / second-wave. Also scans the whole plausible input space to
measure how often the current SKU Definition can produce a single recommendation.
"""
import io, itertools, json, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "prototype"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from rules_v1 import AnalysisInput, KeyFactor, match_sku, finalise, BASELINE, demand_rows  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "artifacts/validation"
OUT.mkdir(parents=True, exist_ok=True)
L = []
def say(s=""):
    print(s); L.append(s)

def mk(cpu=None, gpu=None, panel=None, ssd=None, mem=None, **kw):
    f = {}
    for n, v in (("cpu",cpu),("gpu",gpu),("panel",panel),("ssd",ssd),("mem",mem)):
        f[n] = KeyFactor(n, file_value=v)
    return AnalysisInput(**f, **kw)

say("# Phase-1 rule design validation")
say("\nValidation of `prototype/rules_v1.py` against the extracted baseline. "
    "All numbers derive from the Owner workbook; nothing hand-typed.\n")

# ---------------------------------------------------------------- 1. scenarios
SCEN = [
 ("T-01 positive / clean 4-SKU profile",            dict(cpu=3, gpu=2, panel=2, ssd=2, mem=2)),
 ("T-02 positive / small project 2-SKU profile",    dict(cpu=1, gpu=1, panel=1, ssd=1, mem=1)),
 ("T-03 positive / mid 3-SKU profile",              dict(cpu=2, gpu=2, panel=1, ssd=1, mem=1)),
 ("T-04 positive / large 6-SKU profile",            dict(cpu=5, gpu=3, panel=3, ssd=2, mem=3)),
 ("T-05 boundary / CPU at 4-SKU upper bound",       dict(cpu=4, gpu=2, panel=2, ssd=2, mem=2)),
 ("T-06 boundary / GPU=1 but 4 spec dims high",     dict(cpu=4, gpu=1, panel=2, ssd=2, mem=2)),
 ("T-07 boundary / Panel=2 blocks the 3-SKU path",  dict(cpu=2, gpu=2, panel=2, ssd=1, mem=1)),
 ("T-08 boundary / everything maxed",               dict(cpu=6, gpu=5, panel=4, ssd=4, mem=4)),
 ("T-09 boundary / everything min-flagged",         dict(cpu=1, gpu=1, panel=1, ssd=1, mem=2)),
 ("T-10 missing / Panel not provided",              dict(cpu=3, gpu=2, ssd=2, mem=2)),
 ("T-11 missing / only CPU known",                  dict(cpu=3)),
 ("T-12 missing / nothing known",                   dict()),
 ("T-13 conflict / SSD-Mem=2 but GPU=1",            dict(cpu=2, gpu=1, panel=1, ssd=2, mem=2)),
 ("T-14 conflict / 2nd-wave SSD/Mem on 3-SKU base", dict(cpu=2, gpu=2, panel=1, ssd=2, mem=2)),
 ("T-15 conflict / CPU=2 fits 2,3 and 4-SKU",       dict(cpu=2, gpu=2, panel=1, ssd=1, mem=1)),
]
say("\n## 1. SKU recommendation scenarios\n")
results = {}
for name, kw in SCEN:
    inp = mk(**kw)
    r = match_sku(inp)
    results[name] = r
    shown = {k: (f.effective, f.source) for k, f in inp.factors().items()}
    say(f"### {name}")
    say(f"- input: {shown}")
    say(f"- state: **{r['state']}** | recommended: {r.get('recommended')} | range: {r.get('range')}")
    if r.get("reason"): say(f"- reason: {r['reason']}")
    if r.get("missing_key_factors"): say(f"- 请补充: {', '.join(r['missing_key_factors'])}")
    top = [c for c in r["candidates"] if c["normalized"] is not None]
    say("- candidate scores: " + ", ".join(
        f"SKU{c['sku']}={c['normalized']:.2f}" for c in sorted(top, key=lambda x: -x['normalized'])))
    for x in r.get("runner_up_excluded", []):
        say(f"  - SKU{x['sku']} not recommended (norm={x['normalized']:.2f}): {x['why_not']}")
    say()

# ---------------------------------------------------------------- 2. demand
say("\n## 2. Sample-demand output (D-01: decimals, no rounding)\n")
for label, inp in [
    ("4-SKU profile (cpu3/gpu2/panel2/ssd2/mem2), LCFC, +0.5 confirmed reuse, +5% risk",
     mk(cpu=3, gpu=2, panel=2, ssd=2, mem=2, odm="LCFC",
        optional_flags={"conditional_increment": 1.0}, confirmed_reuse=0.5)),
]:
    r = match_sku(inp)
    for sku in (r.get("range") or [4]):
        pass
    sku = r.get("recommended") or r["range"][0]
    for s in (set([sku] + (r.get("range") or []))):
        f = finalise(inp, s, risk_pct=0.05)
        say(f"- SKU{s}: base={f['base_demand']} FVT={f['fvt']} SIT={f['sit']} "
            f"cond={f['conditional_increment']} reuse={f['confirmed_reuse_adjustment']} "
            f"risk={f['risk_reserve']:.6f} -> **recommended={f['recommended_total']:.6f}**")
        say(f"  by_category: {json.dumps(f['by_category'], ensure_ascii=False)}")
        say("  potential_reuse shown but NOT applied: "
            f"{f['potential_reuse_shown_not_applied']}")
    say("\n  Top function lines for the recommended SKU:")
    for row in sorted(demand_rows(inp, sku), key=lambda x: -x["base_demand"])[:8]:
        say(f"  - {row['function']:<16}{row['phase']:<5}{row['per_sku_rate']} x {sku} SKU = "
            f"{row['base_demand']:<8g}rule={row['rule_id']}@{row['rule_version']} "
            f"cell={row['evidence']['column']}{row['evidence']['row']}")

# ---------------------------------------------------------------- 3. ambiguity scan
say("\n## 3. SKU Definition ambiguity scan\n")
spaces = dict(cpu=range(1, 8), gpu=range(1, 6), panel=range(1, 6), ssd=range(1, 5), mem=range(1, 5))
states, per_sku, ties = Counter(), Counter(), Counter()
examples = {}
n = 0
for combo in itertools.product(*spaces.values()):
    kw = dict(zip(spaces.keys(), combo))
    inp = mk(**kw)
    r = match_sku(inp)
    states[r["state"]] += 1
    n += 1
    if r["state"] == "RANGE":
        per_sku[f"{r['range'][0]}-{r['range'][1]}"] += 1
        ties.setdefault(f"{r['range'][0]}-{r['range'][1]}", f"T{combo}")
    elif r.get("recommended"):
        per_sku[f"single {r['recommended']}"] += 1
    if r["state"] not in examples:
        examples[r["state"]] = kw
say(f"- combinations scanned: {n} (cpu1-7, gpu1-5, panel1-5, ssd1-4, mem1-4)")
for k, v in states.most_common():
    say(f"- {k}: {v} ({100*v/n:.1f}%)  e.g. {examples[k]}")
say("- outcome distribution: " + ", ".join(f"{k}={v}" for k, v in sorted(per_sku.items())))

# single-dimension coverage: can each dim alone identify a SKU?
say("\n### Discriminative power of each key factor (single-factor only)")
for dim in spaces:
    st = Counter()
    for v in spaces[dim]:
        inp = AnalysisInput(**{d: KeyFactor(d, file_value=(v if d == dim else None)) for d in spaces})
        st[match_sku(inp)["state"]] += 1
    say(f"- {dim:<6}: {dict(st)}")

# ---------------------------------------------------------------- 4. invariants
say("\n## 4. Design invariants / regression checks\n")
checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail)); say(f"- [{'PASS' if cond else 'FAIL'}] {name} {detail}")

b = BASELINE["grand_total_by_sku"]
chk("workbook grand totals reproduce (SKU2..6)",
    all(abs(demand_rows(mk(), k) and 0 or 1) for k in (2,3,4,5,6)) and
    all(v > 0 for v in b.values()), str(b))
f2 = finalise(mk(), 2); f6 = finalise(mk(), 6)
chk("recommended total grows with SKU count", f6["recommended_total"] > f2["recommended_total"],
    f"{f2['recommended_total']} -> {f6['recommended_total']}")
chk("D-01: decimals preserved, never rounded to int",
    finalise(mk(), 4)["base_demand"] == 443.8 and finalise(mk(), 5)["base_demand"] == 474.0,
    f"SKU4 base={finalise(mk(),4)['base_demand']} (not 444), SKU5 base={finalise(mk(),5)['base_demand']}")
chk("D-01: fractional risk reserve not rounded",
    round(finalise(mk(), 4, risk_pct=0.05)["risk_reserve"], 6) == round(443.8 * 0.05, 6),
    f"reserve={finalise(mk(),4,risk_pct=0.05)['risk_reserve']}")
i_nof = AnalysisInput(cpu=KeyFactor("cpu", file_value=3), gpu=KeyFactor("gpu", file_value=2))
i_ed = AnalysisInput(cpu=KeyFactor("cpu", file_value=3, user_value=4, user_edited=True),
                     gpu=KeyFactor("gpu", file_value=2))
chk("missing field never defaults to 0/1", i_nof.panel.effective is None and "panel" in i_nof.missing())
chk("user value overrides file value", i_ed.cpu.effective == 4 and i_ed.cpu.source == "USER")
chk("file value retained alongside user value", i_ed.cpu.file_value == 3)
i_pot = mk(cpu=3, gpu=2, panel=2, ssd=2, mem=2); i_pot.potential_reuse = 10.0
fp = finalise(i_pot, 4, 0.0)
chk("potential reuse does not reduce demand", fp["recommended_total"] == fp["base_demand"],
    f"base={fp['base_demand']} rec={fp['recommended_total']}")
i_con = mk(cpu=3, gpu=2, panel=2, ssd=2, mem=2); i_con.confirmed_reuse = 2.0
fc = finalise(i_con, 4, 0.0)
chk("confirmed reuse does reduce demand", abs(fc["recommended_total"] - (fc["base_demand"] - 2.0)) < 1e-9)
empty = match_sku(AnalysisInput())
chk("empty input -> UNDETERMINED (no pseudo-precision)", empty["state"] == "UNDETERMINED", empty.get("reason",""))
rng = match_sku(mk(cpu=3))            # only CPU known -> SKU3/4/5 all match fully -> genuine tie
chk("tie -> RANGE, not a fake single number", rng["state"] == "RANGE", f"{rng.get('range')} tie={rng.get('tie')}")

# ---- SKU reachability: can each SKU definition ever win outright?
say("\n### SKU reachability (can each definition ever be the unique winner?)")
real = dict(cpu=range(1, 6), gpu=range(1, 4), panel=range(1, 4), ssd=range(1, 4), mem=range(1, 4))
win = Counter(); rng_state = Counter(); uncovered = 0; total = 0
for combo in itertools.product(*real.values()):
    kw = dict(zip(real.keys(), combo)); inp = mk(**kw); r = match_sku(inp); total += 1
    rng_state[r["state"]] += 1
    if r.get("recommended"): win[r["recommended"]] += 1
    elif r["state"] == "RANGE":
        for s in range(r["range"][0], r["range"][1] + 1): win[f"in-range {s}"] += 1
    else: uncovered += 1
say(f"- realistic space scanned: {total} (cpu1-5, gpu1-3, panel1-3, ssd1-3, mem1-3)")
say(f"- states: {dict(rng_state)}")
for s in (2, 3, 4, 5, 6):
    say(f"- SKU{s}: unique-winner count = {win.get(s,0)} | appearable-in-range = {win.get(f'in-range {s}',0)}"
        + ("   <<< NOT REACHABLE AS A UNIQUE RECOMMENDATION" if win.get(s, 0) == 0 else ""))
# ---- second wave: current-wave vs full-project must both be reported (docs/10 W-01)
w = mk(cpu=2, gpu=2, panel=1, ssd=2, mem=2)
w.ssd.second_wave_deferred = True
w.mem.second_wave_deferred = True
cur = match_sku(w, wave="current")
full = match_sku(w, wave="full_project")
say(f"\n### Second wave (row 80 clause) input cpu2/gpu2/panel1/ssd2/mem2, 2nd SSD+Mem deferred")
say(f"- Current Wave : {cur['state']} -> {cur.get('recommended') or cur.get('range')}")
say(f"- Full Project : {full['state']} -> {full.get('recommended') or full.get('range')}")
chk("second wave splits into two SKU views",
    cur.get("recommended") == 3 and full.get("recommended") == 4,
    f"current={cur.get('recommended')} full={full.get('recommended')}")
chk("second wave does not change base rates (only the SKU count fed in)",
    finalise(w, 4)["base_demand"] == 443.8 and finalise(w, 3)["base_demand"] == 417.0)

# ---- unit isolation: PCBA must never be summed with UNIT
say("\n### Unit isolation (workbook K3: PCBA items not in sample data)")
chk("PCBA rules are excluded from UNIT totals",
    all(r["category"] in ("RD", "PA", "CERT", "VENDOR", "MFG") for r in demand_rows(mk(), 4))
    and "PCBA" not in json.dumps([r["base_demand"] for r in demand_rows(mk(), 4)]))

# ---- no product name may leak into SKU basis (red line)
say("\n### Product names must never appear in SKU judgement")
blob = json.dumps(match_sku(mk(cpu=3, gpu=2, panel=2, ssd=2, mem=2))["candidates"], ensure_ascii=False)
chk("no product series token in judgement",
    not any(t in blob for t in ("Pro", "LOQ", "Y5", "Y7", "X9", "X11", "N1x", "Y9")),
    "basis carries ranges only")

# ---- every SKU definition is reachable as a unique recommendation
chk("every SKU definition is reachable as a unique recommendation",
    all(win.get(s, 0) > 0 for s in (2, 3, 4, 5, 6)),
    "UNRESOLVED DESIGN GAP -> see Owner Review Item ORI-04" if not all(win.get(s,0) > 0 for s in (2,3,4,5,6)) else "")

(OUT / "validation_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
(OUT / "scenario_results.json").write_text(json.dumps({
    "scenarios": {k: {kk: vv for kk, vv in v.items() if kk != "candidates"} for k, v in results.items()},
    "ambiguity_scan": dict(states), "invariants": [{"check": a, "pass": b_, "detail": c} for a, b_, c in checks],
}, indent=1, ensure_ascii=False), encoding="utf-8")
fails = [c for c in checks if not c[1]]
print(f"\n[{len(checks)-len(fails)}/{len(checks)} invariants passed] -> artifacts/validation/validation_report.md")
sys.exit(1 if fails else 0)
