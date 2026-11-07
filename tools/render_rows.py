#!/usr/bin/env python3
"""Row-wise readable rendering of the extracted workbook (read-only)."""
import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"D:\GAMING_NRE_AGENT")
J = ROOT / "artifacts/extraction/Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.json"
p = json.loads(J.read_text(encoding="utf-8"))
ws = p["worksheets"][0]
cells = {c["ref"]: c for c in ws["cells"]}

# grid by row
rows = {}
for c in ws["cells"]:
    rows.setdefault(c["row"], {})[c["col_letter"]] = c

def show(v, limit=None):
    if v is None: return ""
    s = str(v).replace("\n", " ⏎ ").strip()
    return s

print(f"SHEET: {ws['title']!r} dims={ws['dimensions']} autofilter={ws['autofilter']}")
print(f"hidden_rows={ws['hidden_rows']} hidden_cols={ws['hidden_cols']}")
print("\n=== MERGED RANGES (91) ===")
for m in ws["merged_detail"]:
    print(f"  {m['range']:<12} = {show(m['topleft_value'])}")

print("\n=== ROW GRID ===")
maxcol = 11
for r in sorted(rows):
    parts = []
    for ci in range(1, maxcol + 1):
        cl = chr(64 + ci)
        c = rows[r].get(cl)
        if not c: continue
        raw, cach = show(c["raw"]), show(c["cached"])
        if c["type"] == "f":
            parts.append(f"{cl}=[{raw}] -> {cach}")
        else:
            parts.append(f"{cl}={raw}")
    print(f"R{r:>3}: " + " | ".join(parts))

print("\n=== COMMENTS ===")
for c in p.get("comments", []):
    print(f"--- {c['ref']} [{c['kind']}]")
    print("   " + c["text"].replace("\n", "\n   "))
