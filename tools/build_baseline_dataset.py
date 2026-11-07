#!/usr/bin/env python3
"""Build a machine-readable baseline dataset (baseline_v1.json) from the verified extraction.

Deterministic, derived-only: no hand-typed numbers. original_documents is never written.
"""
import io, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:\GAMING_NRE_AGENT")
SRC_JSON = ROOT / "artifacts/extraction/Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.json"
OUT = ROOT / "artifacts/model"
OUT.mkdir(parents=True, exist_ok=True)

assert not str(OUT.resolve()).startswith(str((ROOT / "original_documents").resolve()))

p = json.loads(SRC_JSON.read_text(encoding="utf-8"))
ws = p["worksheets"][0]
C = {c["ref"]: c for c in ws["cells"]}
SKUS = [2, 3, 4, 5, 6]
COL = {2: "D", 3: "E", 4: "F", 5: "G", 6: "H"}

def raw(ref):
    c = C.get(ref)
    if not c: return None
    return c["cached"] if c["cached"] is not None else c["raw"]

def num(ref):
    x = raw(ref)
    return float(x) if isinstance(x, (int, float)) else None

def text(ref):
    x = raw(ref)
    return str(x).strip() if x is not None else None

FUNC_ROWS = [
    ("RD", "HW", 3), ("RD", "ME", 5), ("RD", "THM", 7), ("RD", "Audio", 9), ("RD", "RF Test", 11),
    ("RD", "EMC Test", 13), ("RD", "SED", 15), ("RD", "SS", 17), ("RD", "PD", 19),
    ("PA", "SWPA", 21), ("PA", "MEPA", 23), ("PA", "HW PA", 25),
    ("CERT", "EMC", 27), ("CERT", "Green", 29), ("CERT", "Safety", 31), ("CERT", "RF Certification", 33),
    ("VENDOR", "BIOS", 35), ("VENDOR", "ITE", 37), ("VENDOR", "NV", 39), ("VENDOR", "INTEL", 41),
    ("MFG", "MFG", 43),
]
ALIASES = {
    "HW": ["HW", "EE", "Power", "HDMI", "TBT", "Battery life", "OC"],
    "ME": ["ME"], "THM": ["THM", "Acoustic", "Fan", "skin"], "Audio": ["Audio", "MIC", "Nahimic"],
    "RF Test": ["RF"], "EMC Test": ["EMC test", "EMI", "ESD", "EMS"],
    "SED": ["SED", "Panel", "X-rite", "HDR", "TP FW"], "SS": ["SS", "BIOS", "EC", "SA", "HLK", "Preload", "OS"],
    "PD": ["PD"], "SWPA": ["SWPA", "SW PA"], "MEPA": ["MEPA", "ME PA"], "HW PA": ["HW PA"],
    "EMC": ["EMC cert"], "Green": ["Green", "EPEAT", "E-Star", "CEL", "BCS", "UL golden"],
    "Safety": ["Safety", "CCC", "BIS", "UL4200A", "CB ", "NOM", "EAC"],
    "RF Certification": ["SRRC", "FCC", "CE", "印尼", "Mexico", "资安"],
    "BIOS": ["3rd BIOS"], "ITE": ["ITE"], "NV": ["NV", "NVIDIA"], "INTEL": ["INTEL"], "MFG": ["MFG", "红丹"],
}

functions = []
for cat, name, r in FUNC_ROWS:
    entry = {
        "function_id": f"F_{re.sub(r'[^A-Za-z0-9]+','_',name).strip('_').upper()}",
        "category": cat, "name": name, "source_rows": {"fvt": r, "sit": r + 1},
        "per_sku_rate": {}, "ttl_per_phase": {}, "marginal_ttl": {},
        "phase_symmetry": None, "status_text": text(f"I{r}") or text(f"I{r+1}"),
        "purpose_text": text(f"J{r}") or text(f"J{r+1}"), "remark_text": text(f"K{r}") or text(f"K{r+1}"),
        "spec_aliases": ALIASES.get(name, []),
    }
    for phase, rr in (("FVT", r), ("SIT", r + 1)):
        entry["per_sku_rate"][phase] = {f"SKU{k}": num(f"{COL[k]}{rr}") for k in SKUS}
    for phase in ("FVT", "SIT"):
        ttl, marg, prev = {}, {}, None
        for k in SKUS:
            rate = entry["per_sku_rate"][phase][f"SKU{k}"]
            t = round(rate * k, 10) if rate is not None else None
            ttl[f"SKU{k}"] = t
            marg[f"SKU{k}"] = None if (t is None or prev is None) else round(t - prev, 10)
            prev = t
        entry["ttl_per_phase"][phase] = ttl
        entry["marginal_ttl"][phase] = marg
    f_fvt = entry["per_sku_rate"]["FVT"]; f_sit = entry["per_sku_rate"]["SIT"]
    entry["phase_symmetry"] = "SYMMETRIC" if f_fvt == f_sit else "ASYMMETRIC"
    entry["all_zero"] = all(v in (0, 0.0) for ph in ("FVT","SIT") for v in entry["per_sku_rate"][ph].values())
    functions.append(entry)

def col_row(label, rr):
    return {"label": label, "row": rr,
            **{f"SKU{k}": num(f"{COL[k]}{rr}") for k in SKUS}}

totals = {"FVT": col_row("SUM/sku FVT", 45), "SIT": col_row("SUM/sku SIT", 46)}
totals_ttl = {"FVT": col_row("TTL SUM/phase FVT", 48), "SIT": col_row("TTL SUM/phase SIT", 49)}

# SKU Definition block rows 79-83
sku_def = {}
SPEC_PATTERNS = {
    "cpu":   r"(\d+)(?:\s*-\s*(\d+))?\s*\*\s*CPU",
    "gpu":   r"(\d+)(?:\s*-\s*(\d+))?\s*\*\s*GPU",
    "panel": r"(\d+)(?:\s*-\s*(\d+))?\s*\*\s*Panel",
    "ssd":   r"SSD\s*SPEC\s*\*\s*(\d+)(?:\s*-\s*(\d+))?",
    "mem":   r"Mem\s*spec\s*\*\s*(\d+)(?:\s*-\s*(\d+))?",
}
for rr, n in ((79,2),(80,3),(81,4),(82,5),(83,6)):
    t = text(f"C{rr}") or ""
    body = t.split(":", 1)[1] if ":" in t else t
    entry = {"row": rr, "raw_text": t}
    spec_end = 0
    for key, pat in SPEC_PATTERNS.items():
        m = re.search(pat, body, re.I)
        if m:
            lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
            entry[key] = [lo, hi]
            spec_end = max(spec_end, m.end())
        else:
            entry[key] = None
    w2 = re.search(r"2nd wave", body, re.I)
    entry["second_wave_clause"] = body[w2.start() - 40:w2.end() + 5].strip() if w2 else None
    entry["has_second_wave_option"] = bool(w2)
    ctx = re.sub(r"\s{2,}", " | ", body[spec_end:].strip())
    entry["context_note"] = ctx or None
    sku_def[f"SKU{n}"] = entry

# header comments on D2:H2 (conflicting panel view)
hdr = {}
col2sku = {v: k for k, v in COL.items()}
comments = [c for c in p.get("comments", []) if c["kind"] == "threaded_comment"]
for cm in comments:
    ref = cm["ref"]
    m = re.match(r"(\d+)\*panel\+(\d+)\*CPU\+(\d+)\*GPU", cm["text"].strip())
    if m and ref[0] in col2sku:
        hdr[col2sku[ref[0]]] = {
            "cell": ref, "panel": int(m.group(1)), "cpu": int(m.group(2)), "gpu": int(m.group(3)),
            "dated": "2026-06-24", "author": "Lingyu LY3 Rong", "raw": cm["text"].strip()}

cert_block2 = {"note": "Rows 51-62: second, independent Certification model (absolute units/phase, not per-SKU rate)",
               "rows": [col_row("EMC FVT",53), col_row("EMC SIT",54), col_row("Green FVT",55), col_row("Green SIT",56),
                        col_row("Safety FVT",57), col_row("Safety SIT",58), col_row("RF Cert FVT",59),
                        col_row("RF Cert SIT",60), col_row("TTL FVT",61), col_row("TTL SIT",62)],
               "explanation_text": text("J52")}
pa_block2 = {"note": "Rows 66-75: PA restated as absolute units/phase",
             "rows": [col_row("SWPA FVT",68), col_row("SWPA SIT",69), col_row("MEPA FVT",70), col_row("MEPA SIT",71),
                      col_row("HW PA FVT",72), col_row("HW PA SIT",73), col_row("TTL FVT",74), col_row("TTL SIT",75)]}

# ---- conflicts
conflicts = []
fn_by_name = {f["name"]: f for f in functions}
for label, r2, fname in [("EMC SIT",54,"EMC"),("Green SIT",56,"Green"),("Safety FVT",57,"Safety"),
                         ("Safety SIT",58,"Safety"),("RF Cert SIT",60,"RF Certification"),
                         ("SWPA FVT",68,"SWPA"),("MEPA FVT",70,"MEPA"),("HW PA FVT",72,"HW PA")]:
    phase = "FVT" if "FVT" in label else "SIT"
    f = fn_by_name[fname]
    for k in SKUS:
        rate = f["per_sku_rate"][phase][f"SKU{k}"]
        b2 = num(f"{COL[k]}{r2}")
        if rate is None or b2 is None: continue
        d = b2 - rate * k
        if abs(d) > 1e-9:
            conflicts.append({"block1_function": fname, "phase": phase, "sku": k,
                              "block1_rate_x_qty": round(rate*k,10), "block2_absolute": b2,
                              "delta": round(d,10), "severity": "MAJOR" if abs(d) >= 1 else "MINOR"})

for n, d in sku_def.items():
    h = hdr.get(int(n[-1]))
    if h and d["panel"] and h["panel"] not in d["panel"]:
        conflicts.append({"type": "SKU_DEFINITION_VS_HEADER_COMMENT", "sku": n,
                          "sku_definition_panel": d["panel"], "header_comment_panel": h["panel"],
                          "severity": "MAJOR",
                          "detail": f"{n}: SKU Definition row {d['row']} says Panel spec {d['panel']}, "
                                    f"but header comment on {h['cell']} says {h['panel']}*panel"})

for f in functions:
    if f["status_text"]:
        s = f["status_text"].lower()
        if any(k in s for k in ("待", "clarify", "gap", "to be")):
            conflicts.append({"type": "UNRESOLVED_STATUS", "function": f["name"],
                              "status_text": f["status_text"], "severity": "OPEN"})

data = {
    "baseline_id": "BASELINE-CS-ODM-001", "baseline_version": "v1.0-draft",
    "derived_from": {"file": p["source"], "sha256": p["sha256"], "sheet": ws["title"],
                     "sheet_dimensions": ws["dimensions"],
                     "workbook_creator": p["properties"]["creator"],
                     "workbook_last_modified_by": p["properties"]["last_modified_by"],
                     "workbook_modified": p["properties"]["modified"],
                     "extraction_sha_source_json": "see artifacts/extraction"},
    "status": "DRAFT_UNCONFIRMED_BY_OWNER",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "generator": "tools/build_baseline_dataset.py",
    "taxonomy": {"FVT": "First validation/prototyping phase", "SIT": "System integration test phase",
                 "categories": {"RD": "Research & Development functions", "PA": "Process/Production Assurance",
                                "CERT": "Certification", "VENDOR": "3rd Party Vendor", "MFG": "Manufacturing"}},
    "functions": functions, "totals": totals, "totals_ttl": totals_ttl,
    "sku_quantity_anchor_row": 47, "sku_definition": sku_def,
    "sku_definition_header_comments": {str(k): v for k, v in hdr.items()},
    "secondary_tables": {"certification_block2": cert_block2, "pa_block2": pa_block2},
    "grand_total_by_sku": {f"SKU{k}": round(num(f"{COL[k]}48") + num(f"{COL[k]}49"), 10) for k in SKUS},
    "conflicts": conflicts,
}
(ROOT/"artifacts/model/baseline_v1.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

print("functions:", len(functions), "| conflicts:", len(conflicts))
print("grand totals:", data["grand_total_by_sku"])
print("\nSKU definitions parsed:")
for k, v in sku_def.items():
    print(f"  {k}: CPU{v['cpu']} GPU{v['gpu']} Panel{v['panel']} SSD{v['ssd']} MEM{v['mem']}  ctx={v['context_note']!r}")
print("\nHeader-comment SKU view:", {k: v for k, v in hdr.items()})
print("\nPhase symmetry:", {f["name"]: f["phase_symmetry"] for f in functions})
print("\nConflicts:")
for c in conflicts:
    print("  ", json.dumps(c, ensure_ascii=False)[:190])
