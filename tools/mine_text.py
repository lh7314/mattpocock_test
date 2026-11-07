#!/usr/bin/env python3
"""Mine Purpose/Explanation (J) + Remark (K) + Status (I) free text for:
   - conditional-increment candidates ("Option:")
   - quantified demand statements
   - ODM-differentiated statements
   - uncertainty / non-normative lexicon
Read-only. Output -> artifacts/extraction/text_signals.md
"""
import io, json, re, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"D:\GAMING_NRE_AGENT")
J = ROOT / "artifacts/extraction/Sample_Requirement_SKU_and_Demand_Baseline_CleanSheet_20261030_V01_FORMAL.json"
p = json.loads(J.read_text(encoding="utf-8"))
ws = p["worksheets"][0]
C = {c["ref"]: c for c in ws["cells"]}

def val(ref):
    if ref not in C: return ""
    c = C[ref]
    return str(c["cached"] if c["cached"] is not None else (c["raw"] or ""))

SUBS = [(3,"RD","HW"),(5,"RD","ME"),(7,"RD","THM"),(9,"RD","Audio"),(11,"RD","RF Test"),
        (13,"RD","EMC Test"),(15,"RD","SED"),(17,"RD","SS"),(19,"RD","PD"),
        (21,"PA","SWPA"),(23,"PA","MEPA"),(25,"PA","HW PA"),
        (27,"Certification","EMC"),(29,"Certification","Green"),(31,"Certification","Safety"),
        (33,"Certification","RF Certification"),(35,"3rd Party","BIOS"),(37,"3rd Party","ITE"),
        (39,"3rd Party","NV"),(41,"3rd Party","INTEL"),(43,"MFG","MFG")]

ODM = ["LCFC", "HQ", "Compal"]
UNCERTAIN = ["case by case","Option","option","to be clarify","to be confirm","TBD","tbd","maybe","suggest",
             "待","待确认","待LCFC update","confirm","If no","是否","gap","refer to","can leverage","Leverage","leverage"]
KEYSRC = ["CPU","GPU","Panel","panel","SSD","memory","Memory","Mem","source","Source","antenna","wlan","WLAN","camera","vendor","battery","connector"]

lines_all = []
for r, cat, sub in SUBS:
    for col, label in (("I","Status"),("J","Purpose"),("K","Remark")):
        t = val(f"{col}{r}")
        if not t.strip(): continue
        for ln in t.split("\n"):
            ln = ln.strip()
            if ln:
                lines_all.append((sub, label, ln))

def has(s, toks): return any(t in s for t in toks)

out = []
out.append("# Free-text signal inventory (Purpose/Explanation, Remark, Status)\n")
out.append(f"Total non-empty text lines mined from columns I/J/K of rows 3-44: **{len(lines_all)}**\n")

blocks = []
cur = None
for sub, label, ln in lines_all:
    if cur != sub:
        out.append(f"\n## {sub}\n")
        cur = sub
    out.append(f"- `[{label}]` {ln}")
out.extend(blocks)

def section(title, pred):
    sel = [x for x in lines_all if pred(x[2])]
    out.append(f"\n\n---\n\n# {title}  — {len(sel)} lines\n")
    for sub, label, ln in sel:
        out.append(f"- **{sub}** `[{label}]` {ln}")

section("A. CONDITIONAL / OPTIONAL increments (non-normative by rule)", lambda s: re.search(r"\bOption\b|option[:：]|Option[:：]", s))
section("B. ODM-differentiated statements (LCFC / HQ / Compal)", lambda s: has(s, ODM))
section("C. UNCERTAINTY / case-by-case / leverage lexicon", lambda s: has(s, UNCERTAIN))
section("D. Source-count driven demand statements (key-factor linkage)", lambda s: has(s, KEYSRC) and re.search(r"\d", s))

# token frequency of key factors
out.append("\n\n---\n\n# E. Key-factor mention frequency across all mined text\n")
for k in ["CPU","GPU","Panel/panel","SSD","Mem/memory","source","antenna","wlan","camera","vendor","battery"]:
    key, *pats = k.split("/")
    n = sum(1 for _,_,ln in lines_all if any(pt in ln for pt in pats) or key in ln)
    out.append(f"- {k}: {n}")

out.append("\n\n# F. PCBA / non-unit demand units observed\n")
units = set()
for _,_,ln in lines_all:
    units |= set(re.findall(r"\b(PCBA|unit|units|台|pcs|PCS|phase|机台)\b", ln))
out.append("- " + ", ".join(sorted(units)))

txt = "\n".join(out)
(ROOT/"artifacts/extraction/text_signals.md").write_text(txt, encoding="utf-8")
print(txt[:6000])
print("\n\n[full -> artifacts/extraction/text_signals.md, %d chars]" % len(txt))
