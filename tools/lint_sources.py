#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lint_sources - cheap structural guard over the repo's own sources.

Python files must compile. JSON files must parse. JS/HTML/MD must not contain the
replacement character (which is what a mis-decoded UTF-8 file looks like) and HTML must
not contain the literal two-character sequence backslash-n (a PowerShell -replace accident
that produced exactly that in one of the tools during this task).
"""
from __future__ import annotations

import glob
import json
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bad: list[str] = []

for f in sorted(glob.glob("tools/*.py") + glob.glob("prototype/*.py")):
    try:
        compile(open(f, encoding="utf-8-sig").read(), f, "exec")
    except SyntaxError as e:
        bad.append(f"{f}: SyntaxError line {e.lineno}: {e.msg}")

for f in sorted(glob.glob("schema/*.json") + glob.glob("artifacts/model/*.json")
                + glob.glob("artifacts/validation/*.json")
                + glob.glob("artifacts/inventory/*.json")):
    try:
        json.load(open(f, encoding="utf-8-sig"))
    except Exception as e:
        bad.append(f"{f}: JSON {str(e)[:120]}")

for f in (sorted(glob.glob("web/*.html") + glob.glob("web/assets/*.js")
                 + glob.glob("docs/*.md") + glob.glob("CHANGES.md"))):
    t = open(f, encoding="utf-8-sig").read()
    if "\ufffd" in t:
        bad.append(f"{f}: contains U+FFFD (mis-decoded UTF-8)")
    if f.endswith(".html") and "\\n" in t:
        bad.append(f"{f}: contains a literal backslash-n (should be a real newline)")

for f in sorted(glob.glob("web/assets/core.js") + glob.glob("web/assets/app.js") + glob.glob("web/assets/store.js")):
    t = open(f, encoding="utf-8-sig").read()
    for brace, label in (("{", "braces"), ("(", "parens")):
        close = ")" if brace == "(" else "}"
        if t.count(brace) != t.count(close):
            bad.append(f"{f}: unbalanced {label} {t.count(brace)}/{t.count(close)}")

# documentation cross-references must resolve
import re
missing = []
for f in sorted(glob.glob("docs/*.md") + ["CHANGES.md"]):
    t = open(f, encoding="utf-8-sig").read()
    for ref in set(re.findall(r"`((?:docs|tools|schema|web|artifacts|prototype)/[\w\-./]+\."
                              r"(?:md|py|json|js|html|sql))`", t)):
        if not os.path.exists(ref) and not ref.endswith(".dom.txt"):
            missing.append(f"{f} -> {ref}")
for m in sorted(set(missing)):
    bad.append(f"broken reference: {m}")

print(f"checked {len(glob.glob('tools/*.py'))} tools, "
      f"{len(glob.glob('prototype/*.py'))} prototypes, "
      f"{len(glob.glob('web/**/*.*', recursive=True))} web files, "
      f"{len(glob.glob('docs/*.md'))} docs")
if bad:
    print("LINT: FAIL")
    for b in bad:
        print("  -", b)
    sys.exit(1)
print("LINT: CLEAN - every source compiles / parses, no mojibake, no broken doc references")
