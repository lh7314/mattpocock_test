#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules_v2 - manual-input MVP calculation core (DESIGN VALIDATION ONLY, not the MVP app).

Loads business numbers from:
  artifacts/model/baseline_v1.json        (Function x Phase x SKU matrix, SKU Definition)
  artifacts/model/quantity_model_v2.json  (per-cell Quantity Model + competing evidence)

Owner decisions encoded
  DEC-01 (ORI-04) 4 vs 5 SKU: no forced single answer. RANGE -> preferred_sku =
                  NOT_ESTABLISHED, and every candidate in the range is calculated.
                  The ORI-04 probe stays failing until Owner supplies real samples.
  DEC-02 (ORI-01) Panel field = Panel Spec Count. D2:H2 "N*panel" comments are
                  UNRESOLVED_COMMENT and never enter matching or arithmetic.
  DEC-03 (ORI-02) Certification keeps three competing models side by side, marks
                  OWNER_REVIEW_REQUIRED, supports manual override, picks/merges nothing.
  DEC-04 (ORI-03) Explicit Wave Assignment only: CURRENT_WAVE / LATER_WAVE / UNKNOWN.
                  Never inferred from the mere existence of a 2nd SSD/Mem spec.
  DEC-05 Quantity Model is per cell: PER_SKU_RATE / PER_PHASE_FIXED /
                  PER_PROJECT_FIXED / FORMULA_DRIVEN / UNRESOLVED. Absolute values are
                  read straight from the table - no divide-by-SKU-then-multiply-back.
  DEC-06 Reuse guard: ALREADY_EMBEDDED_IN_BASELINE / ADDITIONAL_CONFIRMED_REUSE /
                  POTENTIAL_REUSE / UNKNOWN_OVERLAP. Only a proven
                  ADDITIONAL_CONFIRMED_REUSE may reduce demand.
  D-01  All underlying arithmetic stays decimal. Display formatting only.
        Comparisons use an explicit tolerance; business values are never nudged.
"""
from __future__ import annotations

import json
import itertools
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:\GAMING_NRE_AGENT")
BASELINE = json.loads((ROOT / "artifacts/model/baseline_v1.json").read_text(encoding="utf-8"))
QMODEL = json.loads((ROOT / "artifacts/model/quantity_model_v2.json").read_text(encoding="utf-8"))
QCELL = {(c["function_id"], c["phase"]): c for c in QMODEL["cells"]}
EMBEDDED = QMODEL["baseline_embedded_sharing"]

TOL = 1e-9
SKU_RANGE = (2, 3, 4, 5, 6)
PHASES = ("FVT", "SIT")
DIMS = ("cpu", "gpu", "panel", "ssd", "mem")

# agent-set, NOT Owner-confirmed -> ORI-08. Kept only to rank candidates, never to
# force a single winner out of a tie (DEC-01).
DIM_WEIGHT = {"cpu": 1.0, "gpu": 1.6, "panel": 1.0, "ssd": 1.4, "mem": 1.4}
VERDICT_WEIGHT = {"MATCH": 1.0, "PARTIAL_MATCH": 0.4, "MISMATCH": 0.0, "UNKNOWN": 0.0}

MATCH, PARTIAL, MISMATCH, UNKNOWN = "MATCH", "PARTIAL_MATCH", "MISMATCH", "UNKNOWN"

WAVE_CURRENT, WAVE_LATER, WAVE_UNKNOWN = "CURRENT_WAVE", "LATER_WAVE", "UNKNOWN"
WAVE_SOURCES = ("FORMAL_REQUIREMENT_SHEET", "USER_SELECTED", "IMPLICIT_SINGLE_SPEC",
                "NOT_PROVIDED")

REUSE_EMBEDDED = "ALREADY_EMBEDDED_IN_BASELINE"
REUSE_ADDITIONAL = "ADDITIONAL_CONFIRMED_REUSE"
REUSE_POTENTIAL = "POTENTIAL_REUSE"
REUSE_UNKNOWN = "UNKNOWN_OVERLAP"

QUANTITY_MODELS = ("PER_SKU_RATE", "PER_PHASE_FIXED", "PER_PROJECT_FIXED",
                   "FORMULA_DRIVEN", "UNRESOLVED")

CERT_SOURCES = ("MAIN_TABLE", "SECONDARY_TABLE", "J33_FORMULA")

# D2:H2 "N*panel" comments - kept for evidence, excluded from every calculation (DEC-02)
UNRESOLVED_COMMENTS = BASELINE.get("sku_definition_header_comments", {})


def approx(a, b, tol=TOL) -> bool:
    """Explicit tolerance comparison. Does not modify either business value."""
    if a is None or b is None:
        return a is b
    return abs(float(a) - float(b)) <= tol


def sku_key(n: int) -> str:
    return f"SKU{n}"


# --------------------------------------------------------------------------- #
# input model
# --------------------------------------------------------------------------- #
@dataclass
class Spec:
    """One concrete spec (e.g. one SSD spec) with an explicit wave tag."""
    label: str = ""
    wave: str = WAVE_UNKNOWN
    wave_source: str = "NOT_PROVIDED"


@dataclass
class KeyFactor:
    name: str
    file_value: int | None = None
    user_value: int | None = None
    user_edited: bool = False
    specs: list[Spec] = field(default_factory=list)

    @property
    def effective(self) -> int | None:
        """user final value > file read value > user value if present > None."""
        if self.user_edited:
            return self.user_value
        if self.file_value is not None:
            return self.file_value
        return self.user_value

    @property
    def source(self) -> str:
        if self.user_edited:
            return "USER"
        if self.file_value is not None:
            return "FILE"
        if self.user_value is not None:
            return "USER"
        return "UNKNOWN"

    @property
    def status_user(self) -> str:
        return "请补充" if self.effective is None else ""

    # --- wave handling (DEC-04) -------------------------------------------- #
    def normalise_specs(self) -> None:
        """
        Wave may only come from a formal requirement-sheet marking or from the user.
        A spec with no marking is therefore treated as CURRENT_WAVE and flagged
        NOT_PROVIDED - it is never silently pushed into a later wave, because that
        would be the Agent inventing a second wave from the mere existence of a spec.
        """
        n = self.effective
        if n is None:
            self.specs = []
            return
        if len(self.specs) != n:
            self.specs = [Spec(label=f"{self.name}{i+1}", wave=WAVE_CURRENT,
                               wave_source="NOT_PROVIDED") for i in range(n)]
        for s in self.specs:
            if s.wave not in (WAVE_CURRENT, WAVE_LATER, WAVE_UNKNOWN):
                s.wave, s.wave_source = WAVE_CURRENT, "NOT_PROVIDED"
        if n == 1:
            # a single spec cannot be split across waves. This is not a claim about the
            # future, it just means the exclusion set is empty. Recorded so the Owner can
            # overturn it.
            self.specs[0].wave = WAVE_CURRENT
            if self.specs[0].wave_source == "NOT_PROVIDED":
                self.specs[0].wave_source = "IMPLICIT_SINGLE_SPEC"

    def wave_report(self) -> dict:
        n = self.effective or 0
        cur = sum(1 for s in self.specs if s.wave == WAVE_CURRENT)
        later = sum(1 for s in self.specs if s.wave == WAVE_LATER)
        unk = sum(1 for s in self.specs if s.wave == WAVE_UNKNOWN)
        untagged = sum(1 for s in self.specs
                       if s.wave_source in ("NOT_PROVIDED", "IMPLICIT_SINGLE_SPEC"))
        if n == 0:
            state = "NOT_APPLICABLE"
        elif unk:
            state = WAVE_UNKNOWN
        elif later:
            state = "ASSIGNED"
        elif untagged and n >= 2:
            state = "NOT_PROVIDED"
        else:
            state = "ALL_CURRENT"
        return {"factor": self.name, "count": n, "current": cur, "later": later,
                "unknown": unk, "untagged": untagged, "wave_state": state,
                "sources": sorted({s.wave_source for s in self.specs})}

    def unknown_combinations(self) -> list[int]:
        """Possible CURRENT_WAVE counts. Only specs explicitly tagged UNKNOWN fan out;
        an untagged spec counts as CURRENT_WAVE (DEC-04 - no inference)."""
        base = sum(1 for s in self.specs if s.wave == WAVE_CURRENT)
        unk = sum(1 for s in self.specs if s.wave == WAVE_UNKNOWN)
        if not self.specs:
            return []
        raw = [base + k for k in range(unk + 1)]
        if base == 0 and unk:
            raw = [max(1, v) for v in raw]      # the current wave cannot be empty
        return sorted(set(raw))


@dataclass
class ReuseItem:
    qty: float
    reuse_status: str = REUSE_UNKNOWN
    unit: str = "UNIT"
    function_id: str | None = None
    basis: str = ""
    proven_not_in_baseline: bool = False


@dataclass
class AnalysisInput:
    cpu: KeyFactor = field(default_factory=lambda: KeyFactor("cpu"))
    gpu: KeyFactor = field(default_factory=lambda: KeyFactor("gpu"))
    panel: KeyFactor = field(default_factory=lambda: KeyFactor("panel"))
    ssd: KeyFactor = field(default_factory=lambda: KeyFactor("ssd"))
    mem: KeyFactor = field(default_factory=lambda: KeyFactor("mem"))
    odm: str | None = None
    reuse_items: list[ReuseItem] = field(default_factory=list)
    potential_reuse: float = 0.0                 # display only, never subtracted
    risk_reserve_pct: float | None = None
    certification_override: dict | None = None    # {"F_RF_CERTIFICATION": {"SIT": 10.0}}
    extra_demand: list[dict] = field(default_factory=list)

    def factors(self) -> dict:
        return {d: getattr(self, d) for d in DIMS}

    def missing(self) -> list:
        return [n for n, f in self.factors().items() if f.effective is None]

    def normalise(self) -> "AnalysisInput":
        for f in self.factors().values():
            f.normalise_specs()
        return self

    # ------------------------------------------------------------------ #
    # document boundary: schema/input.schema.json -> this dataclass
    # ------------------------------------------------------------------ #
    @classmethod
    def from_document(cls, doc: dict) -> "AnalysisInput":
        """
        Builds the engine input from a document that validates against
        schema/input.schema.json, so the MVP front end and the core cannot drift.
        Nothing is defaulted: an absent value stays None, an absent wave stays
        NOT_PROVIDED.
        """
        kf = doc.get("key_factors", {})
        waves = (doc.get("wave_assignment") or {}).get("specs") or []
        declared_by = (doc.get("wave_assignment") or {}).get("declared_by", "NOT_PROVIDED")

        factors = {}
        for name in DIMS:
            d = kf.get(name) or {}
            n = d.get("effective")
            if n is None:
                n = d.get("user_value") if d.get("user_edited") else d.get("file_value")
                if n is None:
                    n = d.get("user_value")
            specs = []
            if n:
                specs = [Spec(label=f"{name}{i+1}", wave=WAVE_CURRENT,
                              wave_source="NOT_PROVIDED") for i in range(n)]
                for w in waves:
                    if w.get("factor") != name:
                        continue
                    i = int(w.get("spec_index", 1)) - 1
                    if 0 <= i < n:
                        specs[i].wave = w.get("wave", WAVE_CURRENT)
                        specs[i].wave_source = w.get("wave_source", declared_by)
                        specs[i].label = w.get("spec_label") or specs[i].label
            factors[name] = KeyFactor(
                name=name, file_value=d.get("file_value"), user_value=d.get("user_value"),
                user_edited=bool(d.get("user_edited")), specs=specs)

        cert = doc.get("certification_input") or {}
        override: dict = {}
        for o in cert.get("overrides") or []:
            override.setdefault(o["function_id"], {})[o["phase"]] = float(o["qty"])

        rr = doc.get("risk_reserve") or {}
        return cls(
            **{n: factors[n] for n in DIMS},
            odm=doc.get("odm"),
            reuse_items=[ReuseItem(qty=float(r.get("qty", 0.0)),
                                   reuse_status=r.get("reuse_status", REUSE_UNKNOWN),
                                   unit=r.get("unit", "UNIT"),
                                   function_id=r.get("function_id"),
                                   basis=r.get("basis") or "",
                                   proven_not_in_baseline=bool(r.get("proven_not_in_baseline")))
                         for r in doc.get("reuse_items") or []],
            potential_reuse=float(doc.get("potential_reuse_display_only", 0.0) or 0.0),
            risk_reserve_pct=float(rr.get("percent", 0.0) or 0.0),
            certification_override=override or None,
            extra_demand=list(doc.get("additional_demand") or []),
        )


# --------------------------------------------------------------------------- #
# wave scenarios (DEC-04)
# --------------------------------------------------------------------------- #
MAX_WAVE_COMBOS = 32


def wave_scenarios(inp: AnalysisInput) -> list[dict]:
    """
    Returns the scenarios the engine is allowed to compute.

      FULL_PROJECT  - every spec, nothing excluded, no wave claim needed.
      CURRENT_WAVE  - specs explicitly tagged LATER_WAVE are excluded.
                      Untagged specs (UNKNOWN) fan out into every legal assignment;
                      each fan-out combination becomes its own scenario and, because
                      the SKU answer may differ between them, an Owner Review Item.
    """
    out = [{"scope": "FULL_PROJECT", "counts": {n: f.effective for n, f in inp.factors().items()},
            "wave_basis": "ALL_SPECS"}]

    fanout, unknown_factors, untagged_factors = [], [], []
    for n, f in inp.factors().items():
        if f.effective is None:
            continue
        rep = f.wave_report()
        opts = f.unknown_combinations()
        if rep["wave_state"] == WAVE_UNKNOWN:
            unknown_factors.append(n)
            fanout.append({n: opts})
        else:
            if rep["wave_state"] == "NOT_PROVIDED":
                untagged_factors.append(n)
            fanout.append({n: [sum(1 for s in f.specs if s.wave == WAVE_CURRENT)]})

    keys = [next(iter(d)) for d in fanout]
    combos = list(itertools.product(*[fanout[i][keys[i]] for i in range(len(keys))]))
    truncated = len(combos) > MAX_WAVE_COMBOS
    if truncated:                                   # collapse to the two extremes
        combos = [combos[0], combos[-1]]

    declared_any = any(s.wave_source in ("FORMAL_REQUIREMENT_SHEET", "USER_SELECTED")
                       for f in inp.factors().values() for s in f.specs)

    for combo in combos:
        counts = dict(zip(keys, combo))
        merged = {**{n: f.effective for n, f in inp.factors().items()}, **counts}
        out.append({"scope": "CURRENT_WAVE", "counts": merged,
                    "wave_basis": ("UNKNOWN_FANOUT" if unknown_factors
                                   else "EXPLICIT_ASSIGNMENT" if declared_any
                                   else "NO_EXPLICIT_ASSIGNMENT"),
                    "unknown_factors": list(unknown_factors),
                    "untagged_factors": list(untagged_factors),
                    "truncated": truncated})
    # de-duplicate identical count vectors *within* the same scope, but always keep one
    # CURRENT_WAVE view so the UI can show both scopes side by side even when they match
    seen, uniq = set(), []
    for s in out:
        k = (s["scope"], json.dumps(s["counts"], sort_keys=True, default=str))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(s)
    full_counts = {json.dumps(s["counts"], sort_keys=True, default=str)
                   for s in uniq if s["scope"] == "FULL_PROJECT"}
    for s in uniq:
        s["scenario_id"] = f"{s['scope']}:" + "-".join(
            f"{d}{s['counts'][d] if s['counts'][d] is not None else 'x'}" for d in DIMS)
        s["identical_to_full_project"] = (
            s["scope"] == "CURRENT_WAVE"
            and json.dumps(s["counts"], sort_keys=True, default=str) in full_counts)
    return uniq


# --------------------------------------------------------------------------- #
# SKU recommendation (DEC-01 / DEC-02)
# --------------------------------------------------------------------------- #
def definitions() -> dict:
    return BASELINE["sku_definition"]


def domain_bounds() -> dict:
    hi, lo = {}, {}
    for d in DIMS:
        vals = [v for s in definitions().values() if s.get(d) for v in s[d]]
        lo[d], hi[d] = min(vals), max(vals)
    return {"low": lo, "high": hi}


def _dim_verdict(value, rng) -> str:
    if value is None or rng is None:
        return UNKNOWN
    low, high = rng
    if low <= value <= high:
        return MATCH
    if value in (low - 1, high + 1):
        return PARTIAL
    return MISMATCH


def out_of_domain(counts: dict) -> list:
    b = domain_bounds()
    bad = []
    for d, v in counts.items():
        if v is None:
            continue
        if v > b["high"][d]:
            bad.append({"dimension": d, "value": v, "supported_max": b["high"][d]})
        elif v < b["low"][d]:
            bad.append({"dimension": d, "value": v, "supported_min": b["low"][d]})
    return bad


def match_sku(counts: dict, definitions_map: dict | None = None) -> dict:
    """
    Score every SKU definition, then decide a STATE. A tie is reported as a RANGE;
    it is never broken by nudging weights (DEC-01).
    """
    defs = definitions_map or definitions()
    detail, scores = {}, {}
    for sku in SKU_RANGE:
        d = defs.get(sku_key(sku))
        if not d:
            continue
        per, wsum = {}, 0.0
        for dim in DIMS:
            v = _dim_verdict(counts.get(dim), d.get(dim))
            per[dim] = {"verdict": v, "range": list(d[dim]) if d.get(dim) else None,
                        "weight": DIM_WEIGHT[dim]}
            wsum += VERDICT_WEIGHT[v] * DIM_WEIGHT[dim]
        known_w = sum(DIM_WEIGHT[d_] for d_ in DIMS if counts.get(d_) is not None)
        scores[sku] = round(wsum / known_w, 6) if known_w else 0.0
        detail[sku] = per

    known = [d for d in DIMS if counts.get(d) is not None]
    if not known:
        return {"state": "UNDETERMINED", "recommended_sku": None,
                "preferred_sku": "NOT_ESTABLISHED", "sku_range": None,
                "scores": scores, "dimension_detail": detail,
                "reasons": ["no key factor supplied - nothing can be recommended"],
                "out_of_domain": []}

    bad = out_of_domain(counts)
    if bad:
        return {"state": "OUT_OF_DOMAIN", "recommended_sku": None,
                "preferred_sku": "NOT_ESTABLISHED", "sku_range": None,
                "scores": scores, "dimension_detail": detail, "out_of_domain": bad,
                "reasons": [f"{b['dimension']}={b['value']} is outside the supported "
                            f"SKU Definition domain (max {b.get('supported_max')})"
                            f" - no rule exists yet, see ORI-13" for b in bad]}

    best = max(scores.values())
    tied = sorted(s for s, v in scores.items() if approx(v, best))
    missing = [d for d in DIMS if counts.get(d) is None]

    if len(tied) > 1:
        state, rec, rng = "RANGE", None, [min(tied), max(tied)]
        reasons = [f"SKU {', '.join(map(str, tied))} are indistinguishable on the "
                   f"available evidence (score {best})"]
        if missing:
            reasons.append(f"unanswered key factor(s): {', '.join(missing)}")
        reasons.append("DEC-01: the tie is reported as a range, no weighting is used "
                       "to force a single answer")
    elif len(known) < len(DIMS):
        state, rec, rng = "SINGLE_WITH_RESERVATION", tied[0], [tied[0], tied[0]]
        reasons = [f"best supported answer is {tied[0]} SKU on the answered dimensions"]
        reasons.append(f"unanswered key factor(s): {', '.join(missing)}")
    else:
        state, rec, rng = "SINGLE", tied[0], [tied[0], tied[0]]
        reasons = [f"every answered dimension supports {tied[0]} SKU"]
        partials = [d for d in DIMS
                    if detail[tied[0]][d]["verdict"] == PARTIAL]
        if partials:
            state = "SINGLE_WITH_RESERVATION"
            reasons.append(f"dimension(s) one step outside the definition: "
                           f"{', '.join(partials)}")

    neighbours = {s: scores[s] for s in SKU_RANGE if s not in tied}
    return {"state": state, "recommended_sku": rec,
            "preferred_sku": rec if rec is not None else "NOT_ESTABLISHED",
            "sku_range": rng, "tie_set": tied, "scores": scores,
            "dimension_detail": detail, "neighbour_scores": neighbours,
            "reasons": reasons, "out_of_domain": []}


def candidates_to_price(match: dict) -> list[int]:
    """Every SKU the answer has to be priced for. DEC-01: a range prices every member."""
    if match["state"] in ("UNDETERMINED", "OUT_OF_DOMAIN"):
        return []
    if match["state"] == "RANGE":
        lo, hi = match["sku_range"]
        return [s for s in range(lo, hi + 1) if s in match.get("tie_set", [])]
    return [match["recommended_sku"]]


# --------------------------------------------------------------------------- #
# demand calculation (DEC-05 / DEC-03)
# --------------------------------------------------------------------------- #
def function_table() -> list:
    return BASELINE["functions"]


def _cell_value(fid: str, phase: str, sku: int) -> dict:
    """Read the absolute value for one cell according to its Quantity Model."""
    c = QCELL[(fid, phase)]
    qm = c["quantity_model"]
    sk = sku_key(sku)
    if qm == "UNRESOLVED":
        cands = {}
        unevaluable = []
        for src in ("MAIN_TABLE", "SECONDARY_TABLE"):
            v = (c["competing_candidates"].get(sk) or {}).get(src)
            if v is None and src == "MAIN_TABLE":
                v = c["main_table_absolute"].get(sk)
            if v is None and src == "SECONDARY_TABLE":
                v = (c["secondary_table_absolute"] or {}).get(sk)
            if v is not None:
                cands[src] = float(v)
        if c.get("formula_candidate"):
            # declared as a FORMULA_DRIVEN candidate but cannot be evaluated in the MVP
            unevaluable.append("J33_FORMULA")
            cands["J33_FORMULA"] = None
        return {"quantity_model": qm, "value": None, "candidates": cands,
                "unevaluable_sources": unevaluable,
                "owner_review_required": True, "adopted_source": "NONE_UNRESOLVED",
                "rule_id": c["rule_id"]}
    return {"quantity_model": qm, "value": float(c["adopted_absolute"][sk]),
            "candidates": {}, "unevaluable_sources": [],
            "owner_review_required": c["owner_review_required"],
            "adopted_source": c["adopted_source"], "rule_id": c["rule_id"]}


def demand_rows(inp: AnalysisInput, sku: int) -> list:
    rows = []
    for f in function_table():
        fid = f["function_id"]
        for phase in PHASES:
            cell = _cell_value(fid, phase, sku)
            override = None
            if inp.certification_override and fid in inp.certification_override:
                override = inp.certification_override[fid].get(phase)
            value = cell["value"]
            src = cell["adopted_source"]
            if override is not None:
                value, src = float(override), "USER_MANUAL_OVERRIDE"
            rows.append({
                "function_id": fid, "function_name": f["name"], "category": f["category"],
                "phase": phase, "sku_qty": sku,
                "quantity_model": cell["quantity_model"],
                "base_demand": value,
                "candidate_values": cell["candidates"],
                "models_not_evaluable": cell["unevaluable_sources"],
                "value_source": src,
                "unit": "UNIT",
                "owner_review_required": cell["owner_review_required"] and override is None,
                "rule_id": cell["rule_id"],
                "evidence": {"source_file": BASELINE["derived_from"]["file"],
                             "sheet": BASELINE["derived_from"]["sheet"],
                             "row": f["source_rows"][phase.lower()]},
            })
    return rows


def unresolved_certification(rows: list) -> list:
    out = []
    for r in rows:
        if r["quantity_model"] != "UNRESOLVED":
            continue
        cands = {k: v for k, v in r["candidate_values"].items() if v is not None}
        vals = list(cands.values())
        out.append({
            "function_id": r["function_id"], "function_name": r["function_name"],
            "phase": r["phase"], "sku_qty": r["sku_qty"],
            "models": r["candidate_values"],
            "models_evaluable": [k for k, v in r["candidate_values"].items() if v is not None],
            "models_not_evaluable": r.get("models_not_evaluable", []),
            "models_agree": bool(vals) and all(approx(v, vals[0]) for v in vals),
            "range_min": min(vals) if vals else None,
            "range_max": max(vals) if vals else None,
            "status": "UNRESOLVED / OWNER_REVIEW_REQUIRED",
            "note": "Main Table, Secondary Table and the J33 formula are kept apart. "
                    "Nothing is auto-selected and nothing is merged (DEC-03).",
        })
    return out


def summarise(rows: list) -> dict:
    s = {"FVT": 0.0, "SIT": 0.0, "by_category": {}, "by_function": {},
         "unresolved_functions": set(), "excluded_unresolved": 0.0}
    for r in rows:
        s["by_function"].setdefault(r["function_name"], {"FVT": 0.0, "SIT": 0.0})
        if r["base_demand"] is None:
            s["unresolved_functions"].add(r["function_name"])
            continue
        s[r["phase"]] += r["base_demand"]
        s["by_function"][r["function_name"]][r["phase"]] += r["base_demand"]
        s["by_category"][r["category"]] = s["by_category"].get(r["category"], 0.0) + r["base_demand"]
    s["TOTAL"] = s["FVT"] + s["SIT"]
    s["unresolved_functions"] = sorted(s["unresolved_functions"])
    return s


def totals_by_model(rows: list) -> dict:
    """
    Some cells are UNRESOLVED (Certification, DEC-03). Instead of inventing one
    adopted number, the engine prices the whole demand once per competing model and
    reports the resulting band. Nothing is averaged and nothing is merged.

      confirmed_only  - resolved cells only, no Certification at all
      variants        - one complete total per competing evidence source
      band            - min/max across the variants
    """
    unresolved = [r for r in rows if r["base_demand"] is None]
    resolved = [r for r in rows if r["base_demand"] is not None]

    def total(rs):
        return {"FVT": sum(r["base_demand"] for r in rs if r["phase"] == "FVT"),
                "SIT": sum(r["base_demand"] for r in rs if r["phase"] == "SIT"),
                "TOTAL": sum(r["base_demand"] for r in rs)}

    confirmed_only = total(resolved)

    sources: list[str] = []
    declared_only: list[str] = []
    for r in unresolved:
        for k, v in r["candidate_values"].items():
            if v is None:
                continue
            if k not in sources:
                sources.append(k)
        for k in r.get("models_not_evaluable", []):
            if k not in declared_only:
                declared_only.append(k)
    if not unresolved:
        # every cell is resolved - there is exactly one demand picture, no band
        variants = [{"model_source": "SINGLE_ADOPTED_MODEL",
                     "FVT": confirmed_only["FVT"], "SIT": confirmed_only["SIT"],
                     "TOTAL": confirmed_only["TOTAL"]}]
        return {"confirmed_only": confirmed_only, "variants": variants,
                "variants_not_evaluable": declared_only,
                "band": {"total_min": confirmed_only["TOTAL"],
                         "total_max": confirmed_only["TOTAL"], "spread": 0.0},
                "note": "every cell has a resolved Quantity Model - single exact total"}

    usable = [k for k in sources
              if all(r["candidate_values"].get(k) is not None for r in unresolved)]
    dropped = [k for k in sources if k not in usable] + declared_only

    variants = []
    for k in usable:
        rs = resolved + [dict(r, base_demand=float(r["candidate_values"][k]))
                         for r in unresolved]
        variants.append({"model_source": k, **total(rs)})
    if not variants:                    # no competing source can price every cell
        variants = [{"model_source": "SINGLE_ADOPTED_MODEL", **confirmed_only}]
        dropped.append("NO_EVALUABLE_COMPETING_MODEL")
    vals = [v["TOTAL"] for v in variants]
    return {"confirmed_only": confirmed_only,
            "variants": variants,
            "variants_not_evaluable": dropped,
            "band": {"total_min": min(vals), "total_max": max(vals),
                     "spread": round(max(vals) - min(vals), 9)},
            "note": "each variant is one complete demand picture under one evidence "
                    "source; the MVP shows them side by side and never averages them"}


# --------------------------------------------------------------------------- #
# reuse protection (DEC-06)
# --------------------------------------------------------------------------- #
def reuse_ledger(inp: AnalysisInput, rows: list) -> dict:
    """
    Only ADDITIONAL_CONFIRMED_REUSE with proof that it is not already inside the
    baseline may reduce demand. Everything else becomes an Owner Review Item and is
    shown without being subtracted.
    """
    allowed = blocked = 0.0
    items, oris = [], []
    per_function = {}
    for r in rows:
        if r["base_demand"] is not None:
            per_function[r["function_id"]] = per_function.get(r["function_id"], 0.0) + r["base_demand"]

    for i, it in enumerate(inp.reuse_items):
        if it.unit != "UNIT":                       # PCBA never mixed into unit totals
            blocked += 0.0
            items.append({"index": i, "qty": it.qty, "unit": it.unit,
                          "reuse_status": it.reuse_status, "applied": 0.0,
                          "decision": "EXCLUDED_UNIT_MISMATCH",
                          "why": "PCBA quantity must never be summed with or deducted "
                                 "from unit demand"})
            continue
        sig = EMBEDDED.get(it.function_id or "", {}).get("overall")
        if it.reuse_status == REUSE_EMBEDDED:
            items.append({"index": i, "qty": it.qty, "unit": it.unit,
                          "reuse_status": it.reuse_status, "applied": 0.0,
                          "decision": "NOT_DEDUCTED_ALREADY_EMBEDDED",
                          "why": "the Owner states this sharing is already inside the "
                                 "baseline rate - deducting again would double count"})
            continue
        if it.reuse_status == REUSE_POTENTIAL:
            items.append({"index": i, "qty": it.qty, "unit": it.unit,
                          "reuse_status": it.reuse_status, "applied": 0.0,
                          "decision": "DISPLAY_ONLY",
                          "why": "potential reuse is shown, never subtracted"})
            continue
        if it.reuse_status == REUSE_UNKNOWN:
            blocked += 0.0
            oris.append({"kind": "REUSE_OVERLAP_UNPROVEN", "index": i, "qty": it.qty,
                         "function_id": it.function_id,
                         "why": "cannot rule out double deduction, so nothing is deducted"})
            items.append({"index": i, "qty": it.qty, "unit": it.unit,
                          "reuse_status": it.reuse_status, "applied": 0.0,
                          "decision": "BLOCKED_UNTIL_PROVEN",
                          "why": "overlap with the baseline cannot be excluded"})
            continue
        # ADDITIONAL_CONFIRMED_REUSE
        if not it.proven_not_in_baseline:
            oris.append({"kind": "REUSE_PROOF_MISSING", "index": i, "qty": it.qty,
                         "function_id": it.function_id,
                         "why": "ADDITIONAL_CONFIRMED_REUSE needs proof it is not already "
                                "in the baseline" + (
                                    f"; {it.function_id} shows an already-embedded sharing "
                                    f"signal (spread/growth ~0 across SKU)" if sig == "SUSPECTED"
                                    else "")})
            items.append({"index": i, "qty": it.qty, "unit": it.unit,
                          "reuse_status": it.reuse_status, "applied": 0.0,
                          "decision": "BLOCKED_PROOF_MISSING",
                          "why": "proven_not_in_baseline was not asserted"})
            continue
        allowed += abs(it.qty)
        items.append({"index": i, "qty": it.qty, "unit": it.unit,
                      "reuse_status": it.reuse_status, "applied": -abs(it.qty),
                      "decision": "DEDUCTED", "why": it.basis or "user confirmed and proven"})
    return {"deduction": -allowed, "items": items, "owner_review_items": oris,
            "policy": "only a proven ADDITIONAL_CONFIRMED_REUSE reduces demand (DEC-06)"}


def finalise(inp: AnalysisInput, sku: int, risk_pct: float | None = None) -> dict:
    """
    One demand picture for one SKU quantity.

    If every cell has a resolved Quantity Model the answer is a single exact number.
    If some cells are UNRESOLVED (Certification) the answer is a BAND - one complete
    total per competing evidence source, never an average, never a silently adopted
    model (DEC-03).
    """
    rows = demand_rows(inp, sku)
    s = summarise(rows)
    by_model = totals_by_model(rows)

    conditional = sum(float(e.get("qty", 0.0)) for e in inp.extra_demand
                      if e.get("unit", "UNIT") == "UNIT")
    ledger = reuse_ledger(inp, rows)
    reuse = ledger["deduction"]
    pct = inp.risk_reserve_pct if risk_pct is None else risk_pct
    pct = 0.0 if pct is None else pct

    for v in by_model["variants"]:
        v["conditional_increment"] = conditional
        v["confirmed_reuse_adjustment"] = reuse
        # the reserve is charged on the demand itself; it must never reward added demand
        v["risk_reserve"] = (v["TOTAL"] + reuse) * pct
        v["recommended_total"] = v["TOTAL"] + conditional + reuse + v["risk_reserve"]

    vals = [v["recommended_total"] for v in by_model["variants"]] or [0.0]
    exact = len(by_model["variants"]) == 1
    first = by_model["variants"][0]
    pcba = [{"qty": float(e.get("qty", 0.0)), "label": e.get("label", "")}
            for e in inp.extra_demand if e.get("unit") == "PCBA"]

    return {
        "sku_qty": sku,
        "single_value": exact,
        "base_demand": first["TOTAL"] if exact else None,
        "base_demand_band": by_model["band"],
        "totals_by_model": by_model,
        "fvt_total": first["FVT"] if exact else None,
        "sit_total": first["SIT"] if exact else None,
        "conditional_increment": conditional,
        "confirmed_reuse_adjustment": reuse,
        "risk_reserve": first["risk_reserve"] if exact else None,
        "recommended_total": first["recommended_total"] if exact else None,
        "recommended_total_band": {"min": min(vals), "max": max(vals), "exact": exact},
        "potential_reuse_display_only": float(inp.potential_reuse),
        "by_category": s["by_category"],
        "by_function": s["by_function"],
        "unresolved_functions": s["unresolved_functions"],
        "certification_unresolved": unresolved_certification(rows),
        "reuse_ledger": ledger,
        "pcba_lines_not_summed": pcba,
        "rounding": "NONE (D-01)",
        "rows": rows,
    }


# --------------------------------------------------------------------------- #
# whole analysis
# --------------------------------------------------------------------------- #
def _dedupe_oris(oris: list) -> list:
    """
    One Owner Review Item per (kind, subject), not one per scenario. Repeats are folded
    into a `scenario_ids` list so the Owner sees the scope of the question, not a pile of
    identical questions.
    """
    seen, out = {}, []
    for o in oris:
        key = (o.get("kind"), o.get("factors") or o.get("function_id") or o.get("tie_set")
               or o.get("detail") or o.get("index"), o.get("phase", ""), o.get("sku_qty", ""))
        k = json.dumps(key, sort_keys=True, default=str)
        if k in seen:
            tgt = seen[k]
            sid = o.get("scenario_id")
            if sid and sid not in tgt.setdefault("scenario_ids", tgt.get("scenario_ids", [])):
                tgt.setdefault("scenario_ids", []).append(sid)
            continue
        seen[k] = o
        out.append(o)
    for o in out:
        if "scenario_ids" in o:
            o.pop("scenario_id", None)
    return out


def serialise(result: dict, analysis_id: str | None = None,
              display_precision: float | None = 2) -> dict:
    """
    Turn an analyse() result into the exact shape described by
    schema/output.schema.json. Display precision never touches the stored numbers:
    `values_full_precision` always carries the untouched decimal (D-01).
    """
    scenarios = []
    for s in result["scenarios"]:
        results = []
        for r in s["results"]:
            results.append({
                "sku_qty": r["sku_qty"],
                "single_value": r["single_value"],
                "base_demand": r["base_demand"],
                "fvt_total": r["fvt_total"],
                "sit_total": r["sit_total"],
                "risk_reserve": r["risk_reserve"],
                "recommended_total": r["recommended_total"],
                "recommended_total_band": r["recommended_total_band"],
                "conditional_increment": r["conditional_increment"],
                "confirmed_reuse_adjustment": r["confirmed_reuse_adjustment"],
                "potential_reuse_display_only": r["potential_reuse_display_only"],
                "totals_by_model": r["totals_by_model"],
                "by_category": r["by_category"],
                "by_function": r["by_function"],
                "unresolved_functions": r["unresolved_functions"],
                "certification_unresolved": r["certification_unresolved"],
                "reuse_ledger": r["reuse_ledger"],
                "pcba_lines_not_summed": r["pcba_lines_not_summed"],
                "rounding": r["rounding"],
                "rows": r["rows"],
            })
        scenarios.append({
            "scenario_id": s["scenario_id"],
            "scope": s["scope"],
            "wave_basis": s["wave_basis"],
            "unknown_factors": s.get("unknown_factors", []),
            "untagged_factors": s.get("untagged_factors", []),
            "truncated": bool(s.get("truncated")),
            "identical_to_full_project": bool(s.get("identical_to_full_project")),
            "counts": s["counts"],
            "wave_report": s["wave_report"],
            "match": s["match"],
            "candidates_priced": s["candidates_priced"],
            "results": results,
        })

    return {
        "schema_version": "2.0",
        "analysis_id": analysis_id,
        "baseline_id": BASELINE["baseline_id"],
        "rule_pack_version": BASELINE["baseline_version"],
        "quantity_model_version": QMODEL["model_id"] + "/" + QMODEL["model_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": result["status"],
        "policy": {
            "rounding": "NONE (D-01)",
            "display_precision": display_precision,
            "comparison_tolerance": TOL,
            "potential_reuse": "DISPLAY_ONLY",
            "pcba_units": "NEVER_SUMMED_WITH_UNIT",
            "product_names": "NOT_A_RULE",
            "conflicting_evidence": "RETAINED_SEPARATELY_NOT_MERGED",
            "panel_annotation_d2_h2": "UNRESOLVED_COMMENT_EXCLUDED",
        },
        "unresolved_comments_excluded": result["unresolved_comments_excluded"],
        "scenarios": scenarios,
        "owner_review_items": result["owner_review_items"],
        "export": {
            "csv_rows": sum(len(s["results"]) * len(s["results"][0]["rows"])
                            for s in scenarios if s["results"]),
            "full_precision_present": True,
            "display_precision": display_precision,
        },
    }


def analyse(inp: AnalysisInput) -> dict:
    inp.normalise()
    scenarios = wave_scenarios(inp)
    oris = []

    for s in scenarios:
        s["match"] = match_sku(s["counts"])
        s["candidates_priced"] = candidates_to_price(s["match"])
        s["results"] = [finalise(inp, sku) for sku in s["candidates_priced"]]
        s["wave_report"] = [f.wave_report() for f in inp.factors().values()]
        if s["scope"] == "CURRENT_WAVE" and s.get("unknown_factors"):
            oris.append({
                "kind": "WAVE_ASSIGNMENT_UNKNOWN", "scenario_id": s["scenario_id"],
                "factors": s["unknown_factors"],
                "why": "the wave of these specs is explicitly marked UNKNOWN; CURRENT_WAVE "
                       "is therefore reported as several scenarios. The engine will not "
                       "decide it (DEC-04)."})
        if s["scope"] == "CURRENT_WAVE" and s.get("untagged_factors"):
            oris.append({
                "kind": "WAVE_ASSIGNMENT_NOT_PROVIDED", "scenario_id": s["scenario_id"],
                "factors": s["untagged_factors"],
                "why": "these Factors have more than one spec but the requirement sheet does "
                       "not say which wave each spec belongs to. They are counted as "
                       "CURRENT_WAVE by default and CURRENT_WAVE therefore equals FULL "
                       "PROJECT for now. The Agent will not infer a second wave (DEC-04) - "
                       "confirm the wave or accept the current reading."})
        if s["match"]["state"] == "RANGE":
            oris.append({"kind": "SKU_TIE_NOT_RESOLVABLE", "scenario_id": s["scenario_id"],
                         "tie_set": s["match"]["tie_set"],
                         "why": "4 SKU and 5 SKU (or another tie) cannot be separated by "
                                "the current SKU Definition - ORI-04 stays open"})
        if s["match"]["state"] == "OUT_OF_DOMAIN":
            oris.append({"kind": "OUT_OF_DOMAIN_INPUT", "scenario_id": s["scenario_id"],
                         "detail": s["match"]["out_of_domain"],
                         "why": "input exceeds the supported SKU Definition domain - ORI-13"})
        for c in s["results"]:
            for o in c["reuse_ledger"]["owner_review_items"]:
                oris.append({**o, "scenario_id": s["scenario_id"], "sku_qty": c["sku_qty"]})

    # Certification is always an Owner Review Item while the model is UNRESOLVED
    for r in (analyse_first_results(scenarios)):
        for cu in r["certification_unresolved"]:
            if not cu["models_agree"]:
                oris.append({"kind": "CERTIFICATION_MODEL_UNRESOLVED",
                             "function_id": cu["function_id"], "phase": cu["phase"],
                             "sku_qty": cu["sku_qty"],
                             "models": cu["models"],
                             "why": "three competing Certification models exist and are "
                                    "deliberately not merged - DEC-03"})

    return {"input": inp, "scenarios": scenarios,
            "unresolved_comments_excluded": UNRESOLVED_COMMENTS,
            "owner_review_items": _dedupe_oris(oris),
            "status": "DRAFT_UNCONFIRMED_BY_OWNER"}


def analyse_first_results(scenarios: list) -> list:
    out = []
    for s in scenarios:
        out.extend(s.get("results", []))
    return out
