#!/usr/bin/env python3
"""Baseline numeric model verification + internal conflict detection (read-only analysis).

Evidence source: artifacts/extraction/*.json (extracted from original_documents, untouched).
"""
import io, json, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
J = ROOT / "artifacts/extraction/Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.json"
p = json.loads(J.read_text(encoding="utf-8"))
ws = p["worksheets"][0]
C = {c["ref"]: c for c in ws["cells"]}

def v(ref):
    c = C.get(ref)
    if not c: return None
    return c["cached"] if c["cached"] is not None else c["raw"]

def num(ref):
    x = v(ref)
    return float(x) if isinstance(x, (int, float)) else None

# merge map: for merged ranges, all members inherit top-left
topleft = {}
for m in ws["merged_detail"]:
    r = m["range"]
    import re
    a, b = r.split(":")
    cols = [re.match(r"([A-Z]+)(\d+)", s).groups() for s in (a, b)]
    (c1, r1), (c2, r2) = cols
    rr1, rr2 = int(r1), int(r2)
    for rr in range(rr1, rr2 + 1):
        for cc in range(ord(c1), ord(c2) + 1):
            topleft[f"{chr(cc)}{rr}"] = f"{c1}{r1}"

def fv(ref):
    """value respecting merges"""
    t = topleft.get(ref, ref)
    return v(t)

CATS = ["RD", "PA", "Certification", "3rd Party Vendor", "MFG"]
SUBS = [(3,"RD","HW"),(5,"RD","ME"),(7,"RD","THM"),(9,"RD","Audio"),(11,"RD","RF Test"),
        (13,"RD","EMC Test"),(15,"RD","SED"),(17,"RD","SS"),(19,"RD","PD"),
        (21,"PA","SWPA"),(23,"PA","MEPA"),(25,"PA","HW PA"),
        (27,"Certification","EMC"),(29,"Certification","Green"),(31,"Certification","Safety"),
        (33,"Certification","RF Certification"),
        (35,"3rd Party Vendor","BIOS"),(37,"3rd Party Vendor","ITE"),(39,"3rd Party Vendor","NV"),
        (41,"3rd Party Vendor","INTEL"),(43,"MFG","MFG")]
COLS = {2:"D",3:"E",4:"F",5:"G",6:"H"}

print("="*104)
print("BLOCK 1 — MAIN BASELINE: units per SKU, per phase   (rows 3-44)")
print("="*104)
print(f"{'Cat':<17}{'Sub-function':<17}{'Phase':<5}" + "".join(f"{'SKU'+str(k):>9}" for k in COLS) + "   mono?  status")
matrix = {}
for r, cat, sub in SUBS:
    for phase, pr in (("FVT", r), ("SIT", r + 1)):
        vals = [num(f"{COLS[k]}{pr}") for k in sorted(COLS)]
        matrix[(sub, phase)] = vals
        dec = all(vals[i] is not None and vals[i+1] is not None and vals[i+1] <= vals[i] for i in range(4))
        flat = len(set(vals)) == 1
        tag = "FLAT" if flat else ("nonincr-OK" if dec else "*** NON-MONOTONIC ***")
        st = (fv(f"I{pr}") or "").replace("\n", " / ")[:34]
        print(f"{cat:<17}{sub:<17}{phase:<5}" + "".join(f"{x:>9.2f}" for x in vals) + f"   {tag:<12} {st}")

print()
print("="*104)
print("BLOCK 1 — TOTALS: recomputed vs cached")
print("="*104)
for phase, srow in (("FVT", 45), ("SIT", 46)):
    for k, col in sorted(COLS.items()):
        i = sorted(COLS).index(k)
        mine = sum(matrix[(s, phase)][i] for _, _, s in SUBS)
        cached = num(f"{col}{srow}")
        ttl_cached = num(f"{col}{48 if phase=='FVT' else 49}")
        qty = num(f"{col}47")
        print(f"{phase} SKU={k}: SUM/sku mine={mine:.4f} cached={cached:.4f} diff={abs(mine-cached):.2e} | "
              f"TTL={qty:g}x{cached:.2f}={qty*cached:.4f} cached={ttl_cached:.4f}")

print()
print("="*104)
print("BLOCK 1 — GRAND TOTAL per SKU (FVT+SIT, per phase, per the workbook's own TTL row)")
print("="*104)
for k, col in sorted(COLS.items()):
    f, s = num(f"{col}48"), num(f"{col}49")
    print(f"  SKU={k}: FVT={f:8.2f}  SIT={s:8.2f}  TOTAL={f+s:8.2f}")

print()
print("="*104)
print("BLOCK 2 vs BLOCK 1 — CROSS-TABLE CONSISTENCY (PA block rows 66-75, Cert block rows 51-62)")
print("="*104)
def cmp_block(label, rows_map, phase_row):
    print(f"\n-- {label} --   (block2 = absolute units/phase; block1 = per-SKU rate x SKU qty)")
    for sub, r2 in rows_map:
        for phase in ("FVT","SIT"):
            r1 = dict((s, rr) for rr, _, s in SUBS)[sub]
            pr1 = r1 if phase == "FVT" else r1 + 1
            for k, col in sorted(COLS.items()):
                rate = num(f"{col}{pr1}")
                if rate is None: continue
                derived = rate * k
                actual = num(f"{col}{r2 if phase=='FVT' else r2+1}")
                if actual is None: continue
                flag = "OK " if abs(derived-actual) < 1e-9 else ">>> CONFLICT"
                if flag != "OK ":
                    print(f"  {flag} {sub:<15}{phase:<4}SKU={k}: block2={actual:7.2f}  block1-derived={derived:7.2f}  delta={actual-derived:+.2f}")
    print("   (rows not listed matched exactly)")

cmp_block("PA block (SWPA r68/69, MEPA r70/71, HW PA r72/73)",
          [("SWPA",68),("MEPA",70),("HW PA",72)], None)
cmp_block("Certification block (EMC r53/54, Green r55/56, Safety r57/58, RF r59/60)",
          [("EMC",53),("Green",55),("Safety",57),("RF Certification",59)], None)

print()
print("="*104)
print("BLOCK 2 — Certification block absolute values + TTL (rows 53-62)")
print("="*104)
for name, r in (("EMC",53),("Green",55),("Safety",57),("RF Certification",59)):
    for phase in ("FVT","SIT"):
        rr = r if phase=="FVT" else r+1
        vals = [num(f"{COLS[k]}{rr}") for k in sorted(COLS)]
        print(f"  {name:<17}{phase:<5}" + "".join(f"{x:>8.2f}" for x in vals))
for phase, rr in (("FVT",61),("SIT",62)):
    vals = [num(f"{COLS[k]}{rr}") for k in sorted(COLS)]
    print(f"  {'TTL SUM/phase':<17}{phase:<5}" + "".join(f"{x:>8.2f}" for x in vals))
    print(f"  {'':<17}{'':<5}  vs block1 cert-derived (rate x SKU):")
    for sub, base in (("EMC",27),("Green",29),("Safety",31),("RF Certification",33)):
        r1 = base if phase=="FVT" else base+1
        print(f"  {'':<17}  {sub:<15}" + "".join(f"{num(f'{COLS[k]}{r1}')*k:>8.2f}" for k in sorted(COLS)))

print()
print("="*104)
print("SCALING BEHAVIOUR — implied TTL exponent b in TTL = a*SKU^b  (per function, per phase)")
print("="*104)
import math
for r, cat, sub in SUBS:
    out=[]
    for phase in ("FVT","SIT"):
        vals = matrix[(sub, phase)]
        xs = sorted(COLS); ys = vals
        if ys[0] and ys[-1] and ys[0] > 0:
            b = math.log(ys[-1]/ys[0]) / math.log(xs[-1]/xs[0])
            tot0, totN = ys[0]*xs[0], ys[-1]*xs[-1]
            bt = math.log(totN/tot0)/math.log(xs[-1]/xs[0]) if tot0>0 else float("nan")
            out.append(f"{phase}: rate b={b:+.3f} (per-SKU {ys[0]:g}->{ys[-1]:g}), TTL b={bt:+.3f} ({tot0:g}->{totN:g})")
    print(f"  {sub:<17}" + " | ".join(out))
