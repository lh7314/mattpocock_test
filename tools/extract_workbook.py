#!/usr/bin/env python3
"""Read-only deep extractor for the sample-requirement workbook.

Produces structured evidence under artifacts/extraction/.
NEVER writes into original_documents (asserted at runtime).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter, range_boundaries

ROOT = Path(r"D:\GAMING_NRE_AGENT")
SRC_DIR = ROOT / "original_documents"
OUT = ROOT / "artifacts" / "extraction"
INV = ROOT / "artifacts" / "inventory"

FORBIDDEN_WRITE_PREFIX = SRC_DIR.resolve()


def guard_write(path: Path) -> Path:
    rp = path.resolve()
    if str(rp).startswith(str(FORBIDDEN_WRITE_PREFIX)):
        raise RuntimeError(f"Refusing to write inside original_documents: {rp}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def iso(ts) -> str | None:
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts.replace(tzinfo=timezone.utc).isoformat()
    return str(ts)


# ---------------------------------------------------------------- inventory
def build_inventory() -> list[dict]:
    rows = []
    for p in sorted(SRC_DIR.rglob("*")):
        st = p.stat()
        rows.append(
            {
                "file_name": p.name,
                "relative_path": str(p.relative_to(ROOT)),
                "extension": p.suffix.lower(),
                "kind": "file" if p.is_file() else "dir",
                "size_bytes": st.st_size,
                "mtime_local": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                "ctime_local": datetime.fromtimestamp(st.st_ctime).isoformat(timespec="seconds"),
                "sha256": sha256(p) if p.is_file() else None,
            }
        )
    return rows


# ---------------------------------------------------------------- comments
def parse_comment_xml(path: Path, kind: str) -> list[dict]:
    """Parse legacy comments1.xml or threadedComments/*.xml by regex (namespace-safe)."""
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8", errors="replace")
    out = []
    if kind == "legacy":
        for m in re.finditer(r"<comment\b[^>]*\bref=\"([A-Z]+[0-9]+)\"[^>]*>(.*?)</comment>", raw, re.S):
            ref, body = m.group(1), m.group(2)
            text = "".join(re.findall(r"<t[^>]*>(.*?)</t>", body, re.S))
            out.append({"ref": ref, "text": unescape(text).strip(), "kind": "legacy_comment"})
    else:
        for m in re.finditer(r"<threadedComment\b([^>]*)>(.*?)</threadedComment>", raw, re.S):
            attrs, body = m.group(1), m.group(2)
            ref = re.search(r'ref="([A-Z]+[0-9]+)"', attrs)
            pid = re.search(r'personId="([^"]+)"', attrs)
            text = "".join(re.findall(r"<text[^>]*>(.*?)</text>", body, re.S))
            out.append(
                {
                    "ref": ref.group(1) if ref else None,
                    "personId": pid.group(1) if pid else None,
                    "text": unescape(text).strip(),
                    "kind": "threaded_comment",
                }
            )
    return out


def unescape(s: str) -> str:
    return (
        s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
        .replace("&apos;", "'").replace("&#10;", "\n").replace("&#13;", "\n").replace("&amp;", "&")
    )


# ---------------------------------------------------------------- sheets
def cell_state(c) -> str:
    """Best-effort visibility state, incl. white-on-white / hidden row-col."""
    flags = []
    f = c.font
    fill = c.fill
    if c.data_type == "f":
        flags.append("FORMULA")
    try:
        if f and f.color and f.color.rgb and str(f.color.rgb).upper() in ("FFFFFFFF", "FFFFFF") :
            if fill and fill.fgColor and str(fill.fgColor.rgb or "").upper() in ("FFFFFFFF", "FFFFFF"):
                flags.append("WHITE_ON_WHITE")
    except Exception:
        pass
    return "|".join(flags)


def extract(path: Path) -> dict:
    wb_f = openpyxl.load_workbook(path, data_only=False)   # formulas
    wb_v = openpyxl.load_workbook(path, data_only=True)    # cached results
    payload = {
        "source": str(path.relative_to(ROOT)),
        "sha256": sha256(path),
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "properties": {
            "creator": wb_f.properties.creator,
            "last_modified_by": wb_f.properties.lastModifiedBy,
            "created": iso(wb_f.properties.created),
            "modified": iso(wb_f.properties.modified),
        },
        "defined_names": [
            {"name": k, "attr": str(v.attr_text), "hidden": bool(getattr(v, "hidden", False))}
            for k, v in wb_f.defined_names.items()
        ],
        "worksheets": [],
    }
    for ws in wb_f.worksheets:
        wsv = wb_v[ws.title]
        try:
            dims = ws.calculate_dimension(bound_only=True)
        except TypeError:  # older/newer openpyxl signature
            dims = ws.dimensions
        cells = []
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                cached = wsv[c.coordinate].value
                if v is None and cached is None:
                    continue
                cells.append(
                    {
                        "ref": c.coordinate,
                        "row": c.row,
                        "col": c.column,
                        "col_letter": get_column_letter(c.column),
                        "type": c.data_type,
                        "raw": v if not isinstance(v, datetime) else iso(v),
                        "cached": cached if not isinstance(cached, datetime) else iso(cached),
                        "number_format": c.number_format,
                        "state": cell_state(c),
                        "hyperlink": c.hyperlink.target if c.hyperlink else None,
                    }
                )
        merged = [str(r) for r in ws.merged_cells.ranges]
        # map merged -> top-left value for readability
        merged_detail = []
        for r in ws.merged_cells.ranges:
            tl = ws.cell(r.min_row, r.min_col).value
            merged_detail.append({"range": str(r), "topleft_value": tl})
        hidden_rows = [r for r, d in ws.row_dimensions.items() if d.hidden]
        hidden_cols = [c for c, d in ws.column_dimensions.items() if d.hidden]

        comments = []
        legacy = ws.legacy_drawing
        payload["worksheets"].append(
            {
                "title": ws.title,
                "sheet_state": ws.sheet_state,
                "max_row": ws.max_row,
                "max_col": ws.max_col if hasattr(ws, "max_col") else ws.max_column,
                "dimensions": dims,
                "autofilter": str(ws.auto_filter.ref) if ws.auto_filter and ws.auto_filter.ref else None,
                "freeze_panes": str(ws.freeze_panes) if ws.freeze_panes else None,
                "merged_ranges": merged,
                "merged_detail": merged_detail,
                "hidden_rows": sorted(hidden_rows),
                "hidden_cols": sorted(hidden_cols),
                "cells": cells,
                "nonempty_cell_count": len(cells),
            }
        )
        payload.setdefault("_sheet_objs", {})[ws.title] = legacy
    # comment streams from the zip
    import zipfile
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        OUT.mkdir(parents=True, exist_ok=True)
        tmp = OUT / "_zip"
        tmp.mkdir(parents=True, exist_ok=True)
        all_comments = []
        for n in names:
            if re.search(r"(comments\d*|threadedComment\d*)\.xml$", n):
                data = z.read(n)
                fp = guard_write(tmp / Path(n).name)
                fp.write_bytes(data)
                kind = "threaded" if "threaded" in n else "legacy"
                for cm in parse_comment_xml(fp, kind):
                    cm["part"] = n
                    all_comments.append(cm)
        payload["comment_parts"] = [n for n in names if "comment" in n.lower()]
        payload["comments"] = all_comments
        payload["package_parts"] = names
    return payload


# ---------------------------------------------------------------- markdown
def to_markdown(payload: dict) -> str:
    L = [f"# Workbook dump — `{payload['source']}`", ""]
    p = payload["properties"]
    L += [
        f"- SHA-256: `{payload['sha256']}`",
        f"- creator: {p['creator']} | last_modified_by: {p['last_modified_by']}",
        f"- created: {p['created']} | modified: {p['modified']}",
        f"- defined names: {payload['defined_names']}",
        "",
    ]
    for ws in payload["worksheets"]:
        L += [
            f"## Sheet `{ws['title']}`  (state={ws['sheet_state']}, dims={ws['dimensions']}, "
            f"nonempty cells={ws['nonempty_cell_count']})",
            f"- autofilter: {ws['autofilter']} | freeze: {ws['freeze_panes']}",
            f"- hidden rows: {ws['hidden_rows']} | hidden cols: {ws['hidden_cols']}",
            f"- merged ({len(ws['merged_ranges'])}): " + ", ".join(
                f"{m['range']}={m['topleft_value']!r}" for m in ws["merged_detail"]
            ),
            "",
            "| Ref | Raw / Formula | Cached | Fmt | State |",
            "|---|---|---|---|---|",
        ]
        for c in ws["cells"]:
            raw = str(c["raw"]).replace("\n", " ⏎ ").replace("|", "\\|") if c["raw"] is not None else ""
            cach = str(c["cached"]).replace("\n", " ⏎ ").replace("|", "\\|") if c["cached"] is not None else ""
            L.append(f"| {c['ref']} | {raw} | {cach} | {c['number_format']} | {c['state']} |")
        L.append("")
    if payload.get("comments"):
        L += ["## Comments", "", "| Ref | Kind | Text |", "|---|---|---|"]
        for c in payload["comments"]:
            L.append(f"| {c['ref']} | {c['kind']} | {c['text'].strip().replace(chr(10),' ⏎ ')} |")
    return "\n".join(L)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    INV.mkdir(parents=True, exist_ok=True)
    inv = build_inventory()
    guard_write(INV / "file_inventory.json").write_text(
        json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
    import csv
    with guard_write(INV / "file_inventory.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(inv[0].keys()))
        w.writeheader()
        w.writerows(inv)
    for p in SRC_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".xlsx", ".xlsm"):
            payload = extract(p)
            stem = p.stem
            guard_write(OUT / f"{stem}.json").write_text(
                json.dumps(payload, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
            guard_write(OUT / f"{stem}.md").write_text(to_markdown(payload), encoding="utf-8")
            print(f"OK {p.name}: sheets={[w['title'] for w in payload['worksheets']]} "
                  f"cells={sum(w['nonempty_cell_count'] for w in payload['worksheets'])} "
                  f"comments={len(payload.get('comments', []))} merged="
                  f"{sum(len(w['merged_ranges']) for w in payload['worksheets'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
