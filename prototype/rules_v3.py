#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules_v3 - manual-input MVP calculation core. Certification adopted from the Appendix
(Owner decision DEC-10); the Main Table stays on record as audit evidence.

DESIGN VALIDATION + WEB SOURCE OF TRUTH. Not the MVP app itself: the Web front end is a
thin shell over the behaviour defined here, and tools/check_python_web_parity.py proves
the two agree.

Business numbers come from
  artifacts/model/baseline_v1.json                  Function x Phase x SKU, SKU Definition
  artifacts/model/quantity_model_v4.json            per-cell adopted value + evidence roles
  artifacts/model/certification_verification.json   per-cell Main vs Appendix verification
  artifacts/model/rule_pack_v4.json                 the packaged rule version reported out

Owner decisions encoded
  DEC-01 (ORI-04) 4 vs 5 SKU: no forced single answer. RANGE -> preferred_sku =
                  NOT_ESTABLISHED, every candidate in the range is priced. The ORI-04
                  probe stays failing until the Owner supplies real samples.
  DEC-02 (ORI-01) Panel field = Panel Spec Count. D2:H2 "N*panel" comments stay
                  UNRESOLVED_COMMENT and never enter matching or arithmetic.
  DEC-03 (v2, SUPERSEDED) Certification used to be three competing models. Replaced by
                  DEC-09 below; the old behaviour is prohibited and cannot return.
  DEC-04 (ORI-03) Explicit Wave Assignment only. Never inferred from the existence of a
                  second spec. Wave never produces a fixed quantity or a ratio.
  DEC-05 Quantity Model per cell: PER_SKU_RATE / PER_PHASE_FIXED / PER_PROJECT_FIXED /
                  FORMULA_DRIVEN / UNRESOLVED. Absolute values are read straight from the
                  table - no divide-by-SKU-then-multiply-back anywhere.
  DEC-06 Reuse guard: only a proven ADDITIONAL_CONFIRMED_REUSE may reduce demand.
  DEC-09 (ORI-02) Certification is ONE model, not two or three: the Main Table states the
                  quantity needed for one SKU, the Appendix states the total for that SKU
                  count, and FVT and SIT each read their own row (no global phase ratio).
  DEC-10 (ORI-02, THIS TASK) For the MVP and the team-trial phase the ADOPTED Certification
                  quantity is the Appendix total for that Function x Phase x SKU count.
                  The Main Table per-SKU quantity and its derived total stay on the record
                  unchanged, but only as audit and difference-analysis evidence
                  (DERIVED_MAIN_TABLE_AUDIT) - they are never counted in the project total
                  and never added to the Appendix value. The adopted Appendix total is
                  counted exactly once. J33 remains BREAKDOWN_EVIDENCE and is never added.
                  A user override changes one Analysis only and is never written back.
                  DEC-09's prohibitions still hold: no band, no competing models, no global
                  phase ratio, and a Certification range may still only come from a SKU
                  range (SKU_NOT_ESTABLISHED).
  D-01  All underlying arithmetic keeps its original decimal. No business rounding.
        Comparisons use an explicit tolerance; business values are never nudged and
        display formatting never writes back.
"""
from __future__ import annotations

import json
import itertools
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / "artifacts/model/baseline_v1.json").read_text(encoding="utf-8"))
QMODEL = json.loads((ROOT / "artifacts/model/quantity_model_v4.json").read_text(encoding="utf-8"))
CERTV = json.loads((ROOT / "artifacts/model/certification_verification.json")
                   .read_text(encoding="utf-8"))
# The engine reports which rule package it ran on. The pack is generated from the same
# artefacts this module already loads, so the version is read if present and falls back to
# the baseline version when the pack has not been built yet.
_PACK = ROOT / "artifacts/model/rule_pack_v4.json"
_PACK_V3 = ROOT / "artifacts/model/rule_pack_v3.json"


def _pack_version() -> str:
    for p in (_PACK, _PACK_V3):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))["pack_version"]
    return BASELINE["baseline_version"]


RULE_PACK_VERSION = _pack_version()
QCELL = {(c["function_id"], c["phase"]): c for c in QMODEL["cells"]}
EMBEDDED = QMODEL["baseline_embedded_sharing"]
CERT_FUNCS = tuple(f["function_id"] for f in BASELINE["functions"] if f["category"] == "CERT")

ENGINE_NAME = "rules_v3"
ENGINE_VERSION = "4.0"

TOL = 1e-9
SKU_RANGE = (2, 3, 4, 5, 6)
PHASES = ("FVT", "SIT")
DIMS = ("cpu", "gpu", "panel", "ssd", "mem")

# agent-set, NOT Owner-confirmed -> ORI-08. Only ranks candidates; DEC-01 forbids using
# them to manufacture a single answer out of a tie.
DIM_WEIGHT = {"cpu": 1.0, "gpu": 1.6, "panel": 1.0, "ssd": 1.4, "mem": 1.4}
VERDICT_WEIGHT = {"MATCH": 1.0, "PARTIAL_MATCH": 0.4, "MISMATCH": 0.0, "UNKNOWN": 0.0}

MATCH, PARTIAL, MISMATCH, UNKNOWN = "MATCH", "PARTIAL_MATCH", "MISMATCH", "UNKNOWN"

WAVE_CURRENT, WAVE_LATER, WAVE_UNKNOWN = "CURRENT_WAVE", "LATER_WAVE", "UNKNOWN"
WAVE_NONE = "NO_EXPLICIT_ASSIGNMENT"          # what the UI calls 未特别指定
WAVE_SOURCES = ("FORMAL_REQUIREMENT_SHEET", "USER_SELECTED", "IMPLICIT_SINGLE_SPEC",
                "NOT_PROVIDED")

REUSE_EMBEDDED = "ALREADY_EMBEDDED_IN_BASELINE"
REUSE_ADDITIONAL = "ADDITIONAL_CONFIRMED_REUSE"
REUSE_POTENTIAL = "POTENTIAL_REUSE"
REUSE_UNKNOWN = "UNKNOWN_OVERLAP"

QUANTITY_MODELS = tuple(QMODEL["quantity_model_enum"])
EVIDENCE_ROLES = tuple(QMODEL["evidence_role_enum"])

VERIFIED, MISMATCH_CELL, NOT_EVALUABLE = "VERIFIED", "MISMATCH", "NOT_EVALUABLE"
PRIMARY = "PRIMARY_QUANTITY_MODEL"
VALIDATION = "DERIVED_TOTAL_VALIDATION"           # Phase 3a wording, kept for the enum
BREAKDOWN = "BREAKDOWN_EVIDENCE"
# DEC-10: the Appendix total is the adopted quantity, the Main Table derivation is audit
ADOPTED = "ADOPTED_ABSOLUTE_TOTAL"
AUDIT = "DERIVED_MAIN_TABLE_AUDIT"
ADOPTED_SOURCE = "APPENDIX_TABLE_TOTAL"
AUDIT_SOURCE = "MAIN_TABLE_PER_SKU_RATE_TIMES_SKU"
CERT_INPUT_MODE = "SYSTEM_APPENDIX_ADOPTED"

# the only reason a Certification answer may be a range after the correction
RANGE_REASON_SKU = "SKU_NOT_ESTABLISHED"
PROHIBITED_RANGE_REASONS = ("COMPETING_CERTIFICATION_MODELS",
                            "CERTIFICATION_MODEL_UNRESOLVED")

# D2:H2 "N*panel" comments - kept for evidence, excluded from every calculation (DEC-02)
UNRESOLVED_COMMENTS = BASELINE.get("sku_definition_header_comments", {})


def approx(a, b, tol=TOL) -> bool:
    """Explicit tolerance comparison. Modifies neither business value (D-01)."""
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
    wave: str = WAVE_CURRENT
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
        A spec with no marking ("未特别指定" / NO_EXPLICIT_ASSIGNMENT) is CURRENT_WAVE and
        flagged NOT_PROVIDED. It is never pushed into a later wave, because that would be
        the Agent inventing a second wave out of the mere existence of a second spec.
        """
        n = self.effective
        if n is None:
            self.specs = []
            return
        if len(self.specs) != n:
            self.specs = [Spec(label=f"{self.name}{i+1}", wave=WAVE_CURRENT,
                               wave_source="NOT_PROVIDED") for i in range(n)]
        for s in self.specs:
            if s.wave == WAVE_NONE:                 # UI wording: 未特别指定
                s.wave, s.wave_source = WAVE_CURRENT, "NOT_PROVIDED"
            elif s.wave not in (WAVE_CURRENT, WAVE_LATER, WAVE_UNKNOWN):
                s.wave, s.wave_source = WAVE_CURRENT, "NOT_PROVIDED"
        if n == 1:
            # one spec cannot be split across waves. Not a claim about the future, it only
            # means the exclusion set is empty. Recorded so the Owner can overturn it.
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
                "excluded_from_current_wave": [s.label for s in self.specs
                                               if s.wave == WAVE_LATER],
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
            raw = [max(1, v) for v in raw]          # the current wave cannot be empty
        return sorted(set(raw))


@dataclass
class ReuseItem:
    qty: float
    reuse_status: str = REUSE_UNKNOWN
    unit: str = "UNIT"
    function_id: str | None = None
    basis: str = ""
    proven_not_in_baseline: bool = False
    note: str = ""


@dataclass
class AnalysisInput:
    cpu: KeyFactor = field(default_factory=lambda: KeyFactor("cpu"))
    gpu: KeyFactor = field(default_factory=lambda: KeyFactor("gpu"))
    panel: KeyFactor = field(default_factory=lambda: KeyFactor("panel"))
    ssd: KeyFactor = field(default_factory=lambda: KeyFactor("ssd"))
    mem: KeyFactor = field(default_factory=lambda: KeyFactor("mem"))
    odm: str | None = None
    project_name: str | None = None
    project_type: str = "CLEAN_SHEET"
    phase_scope: tuple[str, ...] = ("FVT", "SIT")
    reuse_items: list[ReuseItem] = field(default_factory=list)
    potential_reuse: float = 0.0                 # display only, never subtracted
    risk_reserve_pct: float | None = None
    certification_override: dict | None = None   # {"F_RF_CERTIFICATION": {"SIT": 10.0}}
    extra_demand: list[dict] = field(default_factory=list)

    def factors(self) -> dict:
        return {d: getattr(self, d) for d in DIMS}

    def missing(self) -> list:
        return [n for n, f in self.factors().items() if f.effective is None]

    def normalise(self) -> "AnalysisInput":
        if self.phase_scope:
            self.phase_scope = tuple(p for p in PHASES if p in self.phase_scope) or PHASES
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
                        # The UI's 未特别指定 arrives as NO_EXPLICIT_ASSIGNMENT. It means
                        # "counted in the current wave, nobody said otherwise", so it is
                        # resolved at the contract boundary to CURRENT_WAVE + NOT_PROVIDED.
                        # It is never UNKNOWN: UNKNOWN would fan the answer out into
                        # several scenarios, which is not what the user asked for.
                        wv = w.get("wave", WAVE_CURRENT)
                        if wv == WAVE_NONE:
                            specs[i].wave, specs[i].wave_source = WAVE_CURRENT, "NOT_PROVIDED"
                        else:
                            specs[i].wave = wv
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
        ps = doc.get("phase_scope")
        return cls(
            **{n: factors[n] for n in DIMS},
            odm=doc.get("odm"),
            project_name=doc.get("project_name"),
            project_type=doc.get("project_type", "CLEAN_SHEET"),
            phase_scope=tuple(ps) if ps else PHASES,
            reuse_items=[ReuseItem(qty=float(r.get("qty", 0.0)),
                                   reuse_status=r.get("reuse_status", REUSE_UNKNOWN),
                                   unit=r.get("unit", "UNIT"),
                                   function_id=r.get("function_id"),
                                   basis=r.get("basis") or "",
                                   proven_not_in_baseline=bool(r.get("proven_not_in_baseline")),
                                   note=r.get("note") or "")
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
    The scenarios the engine is allowed to compute.

      FULL_PROJECT  - every spec, nothing excluded, no wave claim needed.
      CURRENT_WAVE  - specs explicitly tagged LATER_WAVE are excluded. Nothing else is.
                      Specs explicitly tagged UNKNOWN fan out into every legal
                      assignment; each becomes its own scenario and, because the SKU
                      answer may differ between them, an Owner Review Item.
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
                    "excluded_specs": [{"factor": n, "label": s.label}
                                       for n, f in inp.factors().items()
                                       for s in f.specs if s.wave == WAVE_LATER],
                    "truncated": truncated})
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
    Score every SKU definition, then decide a STATE. A tie is reported as a RANGE; it is
    never broken by nudging weights (DEC-01).
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
                   f"available evidence (score {best:.6f})"]
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
        partials = [d for d in DIMS if detail[tied[0]][d]["verdict"] == PARTIAL]
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
# demand calculation (DEC-05 / DEC-09)
# --------------------------------------------------------------------------- #
def function_table() -> list:
    return BASELINE["functions"]


FUNCS_CATEGORY = {f["function_id"]: f["category"] for f in BASELINE["functions"]}


def phases_for(inp: AnalysisInput) -> tuple[str, ...]:
    return inp.phase_scope or PHASES


def certification_cell_audit(fid: str, phase: str, sku: int) -> dict:
    """
    The retained Main Table check for one Certification cell at one SKU quantity (DEC-10).

    Under DEC-10 the Appendix total is the ADOPTED quantity and the Main Table per-SKU
    quantity x SKU count is the audit counterpart. This block reports the pair and the
    difference. Nothing in it is a second quantity: the Main Table side is never counted
    in a total and never added to the adopted value.
    """
    c = QCELL[(fid, phase)]
    v = (c.get("audit") or {}).get("per_sku", {}).get(sku_key(sku))
    if not v:
        return {"role": None, "verification_status": None}
    return {"role": AUDIT,
            "adopted_value": v["appendix_total"],
            "adopted_value_source": ADOPTED_SOURCE,
            "appendix_label": v["appendix_label"],
            "appendix_total": v["appendix_total"],
            "appendix_row": v["appendix_row"],
            "main_table_row": v["main_table_row"],
            "main_table_per_sku_quantity": v["main_table_per_sku_quantity"],
            "derived_total": v["derived_total"],
            "delta": v["delta"],
            "verification_status": v["verification_status"],
            "counted_in_project_total": False,
            "may_be_added_to_the_adopted_value": False,
            "relationship": "main_table_per_sku_quantity x sku_count == appendix_total"}


def _cell_value(fid: str, phase: str, sku: int) -> dict:
    """Read the absolute value for one cell according to its Quantity Model (DEC-10)."""
    c = QCELL[(fid, phase)]
    qm = c["quantity_model"]
    sk = sku_key(sku)
    if qm == "UNRESOLVED":
        # still supported by the contract, and no Certification cell uses it any more
        return {"quantity_model": qm, "value": None, "candidates": {},
                "unevaluable_sources": [], "owner_review_required": True,
                "adopted_source": "NONE_UNRESOLVED", "rule_id": c["rule_id"],
                "adopted_value_evidence_role": None,
                "main_table_per_sku_quantity": None, "main_derived_total": None,
                "audit": None, "breakdown_evidence": None}
    is_cert = bool(c.get("audit")) and FUNCS_CATEGORY.get(fid) == "CERT"
    return {"quantity_model": qm, "value": float(c["adopted_absolute"][sk]),
            "candidates": {}, "unevaluable_sources": [],
            "owner_review_required": c["owner_review_required"],
            "adopted_source": c["adopted_source"], "rule_id": c["rule_id"],
            "adopted_value_evidence_role": c.get("adopted_value_evidence_role", PRIMARY),
            "main_table_per_sku_quantity": (c["main_table_per_sku_quantity"].get(sk)
                                            if is_cert else None),
            "main_derived_total": (c["main_table_absolute"].get(sk) if is_cert else None),
            "audit": (certification_cell_audit(fid, phase, sku) if is_cert else None),
            "breakdown_evidence": c.get("breakdown_evidence")}


def demand_rows(inp: AnalysisInput, sku: int) -> list:
    rows = []
    for f in function_table():
        fid = f["function_id"]
        for phase in phases_for(inp):
            cell = _cell_value(fid, phase, sku)
            override = None
            if inp.certification_override and fid in inp.certification_override:
                override = inp.certification_override[fid].get(phase)
            value, src = cell["value"], cell["adopted_source"]
            system_value = value                      # what the model itself publishes
            main_derived = cell["main_derived_total"]
            if override is not None:
                value, src = float(override), "USER_MANUAL_OVERRIDE"
            audit = cell["audit"]
            if override is not None and audit:
                audit = dict(audit)
                audit["user_override_vs_adopted"] = (
                    "NOT_COMPARED" if audit["adopted_value"] is None
                    else ("MATCHES_ADOPTED_APPENDIX_VALUE"
                          if approx(value, audit["adopted_value"])
                          else "DOES_NOT_MATCH_ADOPTED_APPENDIX_VALUE"))
            rows.append({
                "function_id": fid, "function_name": f["name"], "category": f["category"],
                "phase": phase, "sku_qty": sku,
                "quantity_model": cell["quantity_model"],
                "evidence_role": cell["adopted_value_evidence_role"] or PRIMARY,
                "base_demand": value,
                "system_computed_value": system_value,
                "user_input_value": (float(override) if override is not None else None),
                "value_source": src,
                "main_table_per_sku_quantity": cell["main_table_per_sku_quantity"],
                "main_table_derived_total": main_derived,
                "candidate_values": cell["candidates"],
                "models_not_evaluable": cell["unevaluable_sources"],
                "unit": "UNIT",
                "owner_review_required": cell["owner_review_required"] and override is None,
                "main_table_audit": audit,
                "breakdown_evidence_role": (BREAKDOWN if cell["breakdown_evidence"]
                                            else None),
                "is_temporary_model": cell["quantity_model"] == "PER_PHASE_FIXED",
                "override_scope": ("THIS_ANALYSIS_ONLY" if override is not None else None),
                "rule_id": cell["rule_id"],
                "evidence": {"source_file": BASELINE["derived_from"]["file"],
                             "sheet": BASELINE["derived_from"]["sheet"],
                             "row": f["source_rows"][phase.lower()]},
            })
    return rows


# --------------------------------------------------------------------------- #
# Certification block (DEC-09 + DEC-10) - adopted from the Appendix, counted once
# --------------------------------------------------------------------------- #
def certification_result(rows: list) -> dict:
    """
    Certification demand for the applied SKU count (DEC-10):

        demand = the Appendix total of that Function and Phase at the applied SKU count

    read separately for FVT and for SIT (their own rows, no global phase ratio) and summed
    once into the project total. The Main Table per-SKU quantity and the derived total
    (per-SKU quantity x SKU count) are reported alongside as audit evidence only: they are
    never added to the adopted value and never counted a second time.
    """
    cert = [r for r in rows if r["category"] == "CERT"]
    if not cert:
        return {"present": False}
    sku = cert[0]["sku_qty"]
    fvt = sum(r["base_demand"] for r in cert if r["phase"] == "FVT")
    sit = sum(r["base_demand"] for r in cert if r["phase"] == "SIT")
    cells_out, statuses = [], []
    user_overridden = False
    for r in cert:
        v = r["main_table_audit"] or {}
        statuses.append(v.get("verification_status"))
        if r["value_source"] == "USER_MANUAL_OVERRIDE":
            user_overridden = True
        cells_out.append({
            "function_id": r["function_id"], "function_name": r["function_name"],
            "phase": r["phase"], "sku_count": r["sku_qty"],
            "adopted_total": r["base_demand"],
            "adopted_value_source": r["value_source"],
            "applied_total": r["base_demand"],
            "user_input_total": r["user_input_value"],
            "value_source": r["value_source"],
            "main_table_per_sku_quantity": r["main_table_per_sku_quantity"],
            "main_table_derived_total": r["main_table_derived_total"],
            "appendix_total": v.get("appendix_total"),
            "delta_appendix_minus_main_derived": v.get("delta"),
            "delta": v.get("delta"),
            "verification_status": v.get("verification_status"),
            "main_derived_counted_in_project_total": False,
            "user_override_vs_adopted_value": v.get("user_override_vs_adopted"),
            "override_scope": ("THIS_ANALYSIS_ONLY"
                               if r["value_source"] == "USER_MANUAL_OVERRIDE" else None),
            "main_table_row": v.get("main_table_row"),
            "appendix_row": v.get("appendix_row"),
        })
    n_ver = sum(1 for s in statuses if s == VERIFIED)
    n_mis = sum(1 for s in statuses if s == MISMATCH_CELL)
    n_ne = sum(1 for s in statuses if s == NOT_EVALUABLE)
    mismatched = [c for c in cells_out if c["verification_status"] == MISMATCH_CELL]
    # the adopted numbers, re-added from the bottom of the detail for this single check
    recount = {"FVT": sum(c["adopted_total"] for c in cells_out if c["phase"] == "FVT"),
               "SIT": sum(c["adopted_total"] for c in cells_out if c["phase"] == "SIT")}

    j33 = next((r["breakdown_evidence_role"] for r in cert
                if r.get("breakdown_evidence_role")), None)
    j33_detail = None
    for r in cert:
        if QCELL[(r["function_id"], r["phase"])].get("breakdown_evidence"):
            j33_detail = QCELL[(r["function_id"], r["phase"])]["breakdown_evidence"]
            break

    return {
        "present": True,
        "decision": "DEC-10",
        "model": "APPENDIX_ADOPTED_TOTAL",
        "formula": "appendix_total of each Certification Function and Phase at the applied "
                   "SKU count, summed once (no per-SKU multiplication, no phase ratio)",
        "applied_sku_count": sku,
        "fvt_certification_demand": fvt,
        "sit_certification_demand": sit,
        "certification_demand_total": fvt + sit,
        "recounted_from_detail": recount,
        "single_value": True,               # one adopted value, no competition -> one number
        "phase_ratio_used": None,
        "counted_in_project_total_times": 1,
        "adopted_value_role": ADOPTED,
        "adopted_value_source": ADOPTED_SOURCE,
        "main_table_role": AUDIT,
        "main_derived_counted_in_project_total_times": 0,
        "main_table_and_appendix_added_together": False,
        "j33_role": j33,
        "j33_disposition": j33_detail["disposition"] if j33_detail else None,
        "j33_added_to_result": False,
        "j33_counted_in_project_total_times": 0,
        "j33_reference_scenario": (j33_detail or {}).get("declared_reference_scenario"),
        "user_override_used": user_overridden,
        "user_override_scope": "THIS_ANALYSIS_ONLY",
        "main_table_audit": {
            "cells_total": len(cells_out), "verified": n_ver, "mismatch": n_mis,
            "not_evaluable": n_ne,
            "status": ("ALL_MATCHING" if n_ver == len(cells_out) else
                       "PARTIALLY_MATCHING" if n_ver else "NOT_MATCHING"),
            "comparison_tolerance": TOL,
            "counted_in_project_total_times": 0,
            "note": "Main Table per-SKU quantity x SKU count versus the adopted Appendix "
                    "total - audit and difference analysis only",
        },
        # kept as an alias so existing consumers of the old key keep working
        "verification": {"cells_total": len(cells_out), "verified": n_ver,
                         "mismatch": n_mis, "not_evaluable": n_ne,
                         "status": ("ALL_MATCHING" if n_ver == len(cells_out) else
                                    "PARTIALLY_MATCHING" if n_ver else "NOT_MATCHING"),
                         "comparison_tolerance": TOL},
        "cells": cells_out,
        "mismatched_cells": mismatched,
        "range_reason": None,
        "note": "Certification is one adopted number: the Appendix total (DEC-10). The Main "
                "Table per-SKU quantity and its derived total stay on the record for audit "
                "and difference analysis, are counted 0 times and are never added to the "
                "adopted value. J33 explains the RF composition and is never added.",
    }


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
    Prices the demand once per evidence source. After DEC-09 every Certification cell is
    resolved, so there is exactly ONE picture and no band. The machinery is kept because
    the Quantity Model contract still allows UNRESOLVED cells: if one ever appears again
    it must produce a band rather than a silently adopted number.
    """
    unresolved = [r for r in rows if r["base_demand"] is None]
    resolved = [r for r in rows if r["base_demand"] is not None]

    def total(rs):
        return {"FVT": sum(r["base_demand"] for r in rs if r["phase"] == "FVT"),
                "SIT": sum(r["base_demand"] for r in rs if r["phase"] == "SIT"),
                "TOTAL": sum(r["base_demand"] for r in rs)}

    confirmed_only = total(resolved)
    if not unresolved:
        return {"confirmed_only": confirmed_only,
                "variants": [{"model_source": "ADOPTED_MODEL",
                              **confirmed_only}],
                "variants_not_evaluable": [],
                "band": {"total_min": confirmed_only["TOTAL"],
                         "total_max": confirmed_only["TOTAL"], "spread": 0.0},
                "note": "every cell has a resolved Quantity Model - one exact total, "
                        "no competing model and no Certification band (DEC-09)"}

    sources, declared_only = [], []
    for r in unresolved:
        for k, v in r["candidate_values"].items():
            if v is not None and k not in sources:
                sources.append(k)
        for k in r.get("models_not_evaluable", []):
            if k not in declared_only:
                declared_only.append(k)
    usable = [k for k in sources
              if all(r["candidate_values"].get(k) is not None for r in unresolved)]
    dropped = [k for k in sources if k not in usable] + declared_only
    variants = [{"model_source": k,
                 **total(resolved + [dict(r, base_demand=float(r["candidate_values"][k]))
                                     for r in unresolved])} for k in usable]
    if not variants:
        variants = [{"model_source": "ADOPTED_MODEL", **confirmed_only}]
        dropped.append("NO_EVALUABLE_COMPETING_MODEL")
    vals = [v["TOTAL"] for v in variants]
    return {"confirmed_only": confirmed_only, "variants": variants,
            "variants_not_evaluable": dropped,
            "band": {"total_min": min(vals), "total_max": max(vals),
                     "spread": round(max(vals) - min(vals), 9)},
            "note": "each variant is one complete demand picture under one evidence "
                    "source; they are shown side by side and never averaged"}


# --------------------------------------------------------------------------- #
# reuse protection (DEC-06)
# --------------------------------------------------------------------------- #
def reuse_ledger(inp: AnalysisInput, rows: list) -> dict:
    """
    Only ADDITIONAL_CONFIRMED_REUSE with proof that it is not already inside the baseline
    may reduce demand. Everything else becomes an Owner Review Item and is shown without
    being subtracted.
    """
    allowed = 0.0
    items, oris = [], []
    for it in inp.reuse_items:
        base = {"qty": it.qty, "unit": it.unit, "reuse_status": it.reuse_status,
                "function_id": it.function_id, "evidence_note": it.basis or it.note}
        if it.qty is None or it.qty < 0:
            items.append({**base, "index": len(items), "applied": 0.0,
                          "decision": "REJECTED_INVALID_QUANTITY",
                          "why": "reuse quantity must be a valid non-negative number"})
            continue
        if it.unit != "UNIT":                       # PCBA never mixed into unit totals
            items.append({**base, "index": len(items), "applied": 0.0,
                          "decision": "EXCLUDED_UNIT_MISMATCH",
                          "why": "PCBA quantity must never be summed with or deducted "
                                 "from unit demand"})
            continue
        sig = EMBEDDED.get(it.function_id or "", {}).get("overall")
        if it.reuse_status == REUSE_EMBEDDED:
            items.append({**base, "index": len(items), "applied": 0.0,
                          "decision": "NOT_DEDUCTED_ALREADY_EMBEDDED",
                          "why": "the Owner states this sharing is already inside the "
                                 "baseline rate - deducting again would double count"})
            continue
        if it.reuse_status == REUSE_POTENTIAL:
            items.append({**base, "index": len(items), "applied": 0.0,
                          "decision": "DISPLAY_ONLY",
                          "why": "potential reuse is shown, never subtracted"})
            continue
        if it.reuse_status == REUSE_UNKNOWN:
            oris.append({"kind": "REUSE_OVERLAP_UNPROVEN", "index": len(items),
                         "qty": it.qty, "function_id": it.function_id,
                         "why": "cannot rule out double deduction, so nothing is deducted"})
            items.append({**base, "index": len(items), "applied": 0.0,
                          "decision": "BLOCKED_UNTIL_PROVEN",
                          "why": "overlap with the baseline cannot be excluded"})
            continue
        if it.reuse_status != REUSE_ADDITIONAL:
            items.append({**base, "index": len(items), "applied": 0.0,
                          "decision": "REJECTED_UNKNOWN_STATUS",
                          "why": f"{it.reuse_status} is not one of the four supported "
                                 f"reuse states"})
            continue
        if not it.proven_not_in_baseline:
            oris.append({"kind": "REUSE_PROOF_MISSING", "index": len(items),
                         "qty": it.qty, "function_id": it.function_id,
                         "why": "ADDITIONAL_CONFIRMED_REUSE needs proof it is not already "
                                "in the baseline" + (
                                    f"; {it.function_id} shows an already-embedded sharing "
                                    f"signal (spread/growth ~0 across SKU)" if sig == "SUSPECTED"
                                    else "")})
            items.append({**base, "index": len(items), "applied": 0.0,
                          "decision": "BLOCKED_PROOF_MISSING",
                          "why": "proven_not_in_baseline was not asserted"})
            continue
        allowed += abs(it.qty)
        items.append({**base, "index": len(items), "applied": -abs(it.qty),
                      "decision": "DEDUCTED",
                      "why": it.basis or "user confirmed, proven and unit-denominated"})
    requested = sum(float(i.qty or 0.0) for i in inp.reuse_items)
    adopted = allowed
    return {"deduction": -allowed, "items": items, "owner_review_items": oris,
            "requested_reuse_quantity": requested,
            "adopted_reuse_quantity": adopted,
            "rejected_or_deferred_quantity": round(requested - adopted, 10),
            "policy": "only a proven, unit-denominated ADDITIONAL_CONFIRMED_REUSE that is "
                      "confirmed outside the baseline reduces demand (DEC-06)"}


# --------------------------------------------------------------------------- #
# one priced SKU candidate
# --------------------------------------------------------------------------- #
def finalise(inp: AnalysisInput, sku: int, risk_pct: float | None = None) -> dict:
    """
    One demand picture for one SKU quantity. After DEC-09 every cell is resolved, so the
    answer is a single exact number. A range in the final answer can therefore only come
    from the SKU recommendation itself, never from Certification.
    """
    rows = demand_rows(inp, sku)
    s = summarise(rows)
    by_model = totals_by_model(rows)
    cert = certification_result(rows)

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
        "certification_demand": cert["certification_demand_total"] if cert.get("present") else 0.0,
        "non_certification_demand": (first["TOTAL"]
                                     - (cert["certification_demand_total"]
                                        if cert.get("present") else 0.0)) if exact else None,
        "certification": cert,
        "conditional_increment": conditional,
        "confirmed_reuse_adjustment": reuse,
        "reuse_summary": {
            "requested_reuse_quantity": ledger["requested_reuse_quantity"],
            "adopted_reuse_quantity": ledger["adopted_reuse_quantity"],
            "rejected_or_deferred_quantity": ledger["rejected_or_deferred_quantity"],
            "adoption_reason": ("proven ADDITIONAL_CONFIRMED_REUSE, unit-denominated, "
                                "confirmed outside the baseline"
                                if ledger["adopted_reuse_quantity"] else None),
            "non_adoption_reason": (None if not ledger["rejected_or_deferred_quantity"]
                                    else "not proven, not unit-denominated, already "
                                         "embedded, potential only, or an unknown overlap"),
        },
        "risk_reserve": first["risk_reserve"] if exact else None,
        "recommended_total": first["recommended_total"] if exact else None,
        "recommended_total_band": {"min": min(vals), "max": max(vals), "exact": exact},
        "potential_reuse_display_only": float(inp.potential_reuse),
        "by_category": s["by_category"],
        "by_function": s["by_function"],
        "unresolved_functions": s["unresolved_functions"],
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
    One Owner Review Item per (kind, subject), not one per scenario. Repeats fold into a
    `scenario_ids` list so the Owner sees the scope of the question, not a pile of
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


def j33_evidence_block() -> dict:
    """The J33 evidence register entry, taken from the verified artefact."""
    j = CERTV["j33_investigation"]
    return {
        "source_cell": j["cell"],
        "evidence_role": BREAKDOWN,
        "disposition": j["disposition"],
        "attached_to_function": "F_RF_CERTIFICATION",
        "declared_reference_scenario": j["declared_reference_scenario"],
        "reference_total_under_readings": j["reference_total_under_readings"],
        "bracket": j["bracket"],
        "explains_main_table_per_sku_quantity":
            j["findings"]["explains_main_table_quantity"],
        "explains_appendix_total": j["findings"]["explains_appendix_total"],
        "antenna_wlan_are": j["findings"]["antenna_and_wlan_are"],
        "already_inside_main_table_rate": j["findings"]["already_inside_main_table_rate"],
        "double_count_risk_if_added": j["findings"]["double_count_risk_if_added"],
        "added_to_certification_result": False,
        "mvp_requires_antenna_wlan_input_now": j["mvp_requires_antenna_wlan_input_now"],
        "raw_text": j["raw_text"],
        "owner_review_required": True,
    }


def serialise(result: dict, analysis_id: str | None = None,
              display_precision: float | None = 2) -> dict:
    """
    Turn an analyse() result into the shape described by schema/output.schema.json.
    Display precision never touches the stored numbers (D-01): the payload always carries
    the untouched decimal, and the requested display precision is only declared as an
    instruction for the presentation layer.
    """
    scenarios = []
    for s in result["scenarios"]:
        results = []
        for r in s["results"]:
            results.append({k: r[k] for k in (
                "sku_qty", "single_value", "base_demand", "fvt_total", "sit_total",
                "certification_demand", "non_certification_demand", "certification",
                "risk_reserve", "recommended_total", "recommended_total_band",
                "conditional_increment", "confirmed_reuse_adjustment", "reuse_summary",
                "potential_reuse_display_only", "totals_by_model", "by_category",
                "by_function", "unresolved_functions", "reuse_ledger",
                "pcba_lines_not_summed", "rounding", "rows")})
        scenarios.append({
            "scenario_id": s["scenario_id"],
            "scope": s["scope"],
            "wave_basis": s["wave_basis"],
            "unknown_factors": s.get("unknown_factors", []),
            "untagged_factors": s.get("untagged_factors", []),
            "excluded_specs": s.get("excluded_specs", []),
            "truncated": bool(s.get("truncated")),
            "identical_to_full_project": bool(s.get("identical_to_full_project")),
            "counts": s["counts"],
            "wave_report": s["wave_report"],
            "match": s["match"],
            "candidates_priced": s["candidates_priced"],
            "results": results,
        })

    return {
        "schema_version": "4.0",
        "analysis_id": analysis_id,
        "baseline_id": BASELINE["baseline_id"],
        "rule_pack_version": RULE_PACK_VERSION,
        "quantity_model_version": f"{QMODEL['model_id']}/{QMODEL['model_version']}",
        "engine_version": f"{ENGINE_NAME}/{ENGINE_VERSION}",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": result["status"],
        "owner_decision": QMODEL.get("owner_decision", {}),
        "policy": {
            "rounding": "NONE (D-01)",
            "display_precision": display_precision,
            "display_precision_modifies_values": False,
            "comparison_tolerance": TOL,
            "potential_reuse": "DISPLAY_ONLY",
            "pcba_units": "NEVER_SUMMED_WITH_UNIT",
            "product_names": "NOT_A_RULE",
            "conflicting_evidence": "RETAINED_SEPARATELY_NOT_MERGED",
            "panel_annotation_d2_h2": "UNRESOLVED_COMMENT_EXCLUDED",
            "certification_model": "APPENDIX_ADOPTED_TOTAL (DEC-10)",
            "certification_adopted_value_source": ADOPTED_SOURCE,
            "certification_adopted_value_role": ADOPTED,
            "certification_main_table_role": AUDIT,
            "certification_main_derived_added_to_total": False,
            "certification_main_table_and_appendix_added_together": False,
            "certification_j33_role": BREAKDOWN,
            "certification_j33_added_to_result": False,
            "certification_global_phase_ratio": None,
            "certification_range_reason_allowed": RANGE_REASON_SKU,
            "certification_user_override_scope": "THIS_ANALYSIS_ONLY",
            "mepa_hw_pa": "PER_PHASE_FIXED candidate, temporary pending Owner (ORI-10)",
        },
        "unresolved_comments_excluded": result["unresolved_comments_excluded"],
        "j33_evidence": result["j33_evidence"],
        "scenarios": scenarios,
        "owner_review_items": result["owner_review_items"],
        "owner_review_summary": result["owner_review_summary"],
        "export": {
            "csv_rows": sum(len(s["results"]) * (len(s["results"][0]["rows"]) + 1)
                            for s in scenarios if s["results"]),
            "full_precision_present": True,
            "display_precision": display_precision,
            "range_collapsed_to_single_value_on_export": False,
            "certification_adopted_value_source": ADOPTED_SOURCE,
            "main_table_audit_exported_for_review": True,
        },
    }


def analyse(inp: AnalysisInput) -> dict:
    inp.normalise()
    scenarios = wave_scenarios(inp)
    oris: list[dict] = []
    blocked = []

    for s in scenarios:
        s["match"] = match_sku(s["counts"])
        s["candidates_priced"] = candidates_to_price(s["match"])
        s["results"] = [finalise(inp, sku) for sku in s["candidates_priced"]]
        s["wave_report"] = [f.wave_report() for f in inp.factors().values()]

        if s["scope"] == "CURRENT_WAVE" and s.get("unknown_factors"):
            oris.append({"kind": "WAVE_ASSIGNMENT_UNKNOWN", "scenario_id": s["scenario_id"],
                         "factors": s["unknown_factors"],
                         "why": "the wave of these specs is explicitly marked UNKNOWN; "
                                "CURRENT_WAVE is therefore reported as several scenarios. "
                                "The engine will not decide it (DEC-04)."})
        if s["scope"] == "CURRENT_WAVE" and s.get("untagged_factors"):
            oris.append({"kind": "WAVE_ASSIGNMENT_NOT_PROVIDED",
                         "scenario_id": s["scenario_id"],
                         "factors": s["untagged_factors"],
                         "why": "these Factors have more than one spec but nothing says "
                                "which wave each spec belongs to. They are counted as "
                                "CURRENT_WAVE by default, so CURRENT_WAVE equals FULL "
                                "PROJECT for now. The Agent will not infer a second wave "
                                "(DEC-04) - confirm the wave or accept this reading."})
        if s["match"]["state"] == "RANGE":
            oris.append({"kind": "SKU_TIE_NOT_RESOLVABLE", "scenario_id": s["scenario_id"],
                         "tie_set": s["match"]["tie_set"],
                         "why": f"{s['match']['tie_set'][0]} SKU and "
                                f"{s['match']['tie_set'][-1]} SKU cannot be separated by "
                                "the current SKU Definition - ORI-04 stays open. Every "
                                "certification demand is computed for each of them, so "
                                "the range is SKU_NOT_ESTABLISHED, not a Certification "
                                "model conflict."})
        if s["match"]["state"] == "OUT_OF_DOMAIN":
            oris.append({"kind": "OUT_OF_DOMAIN_INPUT", "scenario_id": s["scenario_id"],
                         "detail": s["match"]["out_of_domain"],
                         "why": "input exceeds the supported SKU Definition domain - ORI-13"})
        for c in s["results"]:
            for o in c["reuse_ledger"]["owner_review_items"]:
                oris.append({**o, "scenario_id": s["scenario_id"], "sku_qty": c["sku_qty"]})

    # DEC-10: a Main Table / Appendix disagreement raises a difference item. The adopted
    # number is the Appendix total; this is a source-data question, NOT a model conflict.
    seen_cell = set()
    for s in scenarios:
        for c in s["results"]:
            for m in c["certification"].get("mismatched_cells", []):
                k = (m["function_id"], m["phase"])
                if k in seen_cell:
                    continue
                seen_cell.add(k)
                oris.append({"kind": "CERTIFICATION_SOURCE_VALIDATION_MISMATCH",
                             "function_id": m["function_id"], "phase": m["phase"],
                             "main_table_per_sku_quantity": m["main_table_per_sku_quantity"],
                             "main_table_derived_total": m["main_table_derived_total"],
                             "adopted_total": m["adopted_total"],
                             "appendix_total": m["appendix_total"],
                             "delta": m["delta"],
                             "main_table_row": m["main_table_row"],
                             "appendix_row": m["appendix_row"],
                             "blocking_level": "BLOCKS_FORMALIZATION",
                             "blocks_manual_mvp": False,
                             "why": "the Appendix total - which DEC-10 adopts - does not "
                                    "equal the Main Table per-SKU quantity x SKU count. The "
                                    "engine uses the Appendix total, keeps the Main Table "
                                    "derivation as audit evidence and reports the difference "
                                    "instead of editing the source. The result stays a "
                                    "single value: this is a source-data question, not a "
                                    "competing model, and the two are never added."})
    if any(c["certification"].get("main_table_audit", {}).get("mismatch")
           for s in scenarios for c in s["results"]):
        oris.append({"kind": "CERTIFICATION_APPENDIX_VALIDATION_INCOMPLETE",
                     "blocking_level": "BLOCKS_FORMALIZATION", "blocks_manual_mvp": False,
                     "why": "the Main Table x SKU relationship holds for part of the "
                            "Certification grid only, so ORI-02 is PARTIALLY_RESOLVED and "
                            "the rule pack cannot be finalised. DEC-10 decides WHICH column "
                            "is adopted; it does not explain why the two columns disagree, "
                            "so the difference stays registered for the Owner."})
    if CERTV["j33_investigation"]["disposition"] == "DECLARED_NOT_GENERALIZED":
        oris.append({"kind": "CERTIFICATION_BREAKDOWN_EVIDENCE_NOT_GENERALIZED",
                     "source_cell": "J33",
                     "blocking_level": "ADVISORY", "blocks_manual_mvp": False,
                     "why": "J33 explains the RF Certification composition for one "
                            "declared antenna x WLAN combination and cannot be "
                            "reproduced from the workbook. It is kept as explanatory "
                            "evidence, is never added to the adopted Certification value, "
                            "and does not oblige the MVP to collect antenna / WLAN inputs "
                            "today."})

    # a BLOCKS_EXECUTION condition is the only thing that stops a calculation
    for s in scenarios:
        if s["match"]["state"] == "OUT_OF_DOMAIN":
            blocked.append({"scenario_id": s["scenario_id"],
                            "reason": "OUT_OF_DOMAIN_INPUT",
                            "explanation": "the input is outside the SKU Definition domain "
                                           "covered by the rule pack, so no demand is "
                                           "published for this scenario rather than "
                                           "extrapolating one."})

    n_items = {}
    for o in oris:
        n_items[o["kind"]] = n_items.get(o["kind"], 0) + 1
    summary = {
        "total_items": len(oris),
        "by_kind": n_items,
        "blocking_execution": sum(1 for o in oris
                                  if o.get("blocking_level") == "BLOCKS_EXECUTION"),
        "blocks_manual_mvp": any(o.get("blocks_manual_mvp") for o in oris),
        "note": "Owner Review Items inform the Owner; they do not stop the manual MVP "
                "unless blocks_manual_mvp is true (task section 25 test 22/23).",
    }

    return {"input": inp, "scenarios": scenarios,
            "unresolved_comments_excluded": UNRESOLVED_COMMENTS,
            "j33_evidence": j33_evidence_block(),
            "blocked_scenarios": blocked,
            "owner_review_items": _dedupe_oris(oris),
            "owner_review_summary": summary,
            "status": "DRAFT_UNCONFIRMED_BY_OWNER"}


def analyse_first_results(scenarios: list) -> list:
    out = []
    for s in scenarios:
        out.extend(s.get("results", []))
    return out


def input_document(inp: AnalysisInput) -> dict:
    """The Input Snapshot that travels with every exported result."""
    overrides = [{"function_id": k, "phase": p, "qty": v}
                 for k, d in (inp.certification_override or {}).items()
                 for p, v in d.items()]
    return {
        "schema_version": "4.0",
        "project_name": inp.project_name,
        "project_type": inp.project_type,
        "odm": inp.odm,
        "phase_scope": list(inp.phase_scope),
        "key_factors": {n: {"name": n,
                            "file_value": f.file_value,
                            "user_value": f.user_value,
                            "user_edited": f.user_edited,
                            "effective": f.effective,
                            "value_source": f.source,
                            "user_status": f.status_user}
                        for n, f in inp.factors().items()},
        "wave_assignment": {
            "declared_by": sorted({s.wave_source for f in inp.factors().values()
                                   for s in f.specs}) or ["NOT_PROVIDED"],
            "specs": [{"factor": n, "spec_index": i + 1, "spec_label": s.label,
                       "wave": s.wave, "wave_source": s.wave_source}
                      for n, f in inp.factors().items()
                      for i, s in enumerate(f.specs)]},
        "certification_input": {
            "mode": ("USER_OVERRIDE_FOR_MISMATCH_CELLS" if overrides else CERT_INPUT_MODE),
            "override_scope": "THIS_ANALYSIS_ONLY",
            "overrides": overrides},
        "reuse_items": [asdict(r) for r in inp.reuse_items],
        "additional_demand": list(inp.extra_demand),
        "risk_reserve": {"percent": inp.risk_reserve_pct},
        "panel_annotation_d2_h2": "UNRESOLVED_COMMENT_EXCLUDED",
    }


# --------------------------------------------------------------------------- #
# Exports (deliverables R / S). These are the canonical exporters: the Web MVP
# (web/assets/store.js) produces the same bytes, and the parity check compares the
# two outputs. Formatting never rewrites a stored value (D-01): every number is
# written with its underlying decimal, and a range is exported as a range.
# --------------------------------------------------------------------------- #
def _pack_doc() -> dict:
    if _PACK.exists():
        return json.loads(_PACK.read_text(encoding="utf-8"))
    return {}


def jsstr(v) -> str:
    """String() exactly as the browser renders it, so CSV output can be compared byte-wise."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(int(v)) if float(v).is_integer() else repr(float(v))
    if isinstance(v, str):
        return v
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def csv_escape(v) -> str:
    s = jsstr(v)
    if any(c in s for c in ',"\r\n'):
        return '"' + s.replace('"', '""') + '"'
    return s


def user_row_status(r: dict) -> str:
    """The eight user-facing row states. Internal codes never appear here."""
    if r.get("base_demand") is None:
        return "暂无法计算"
    if r.get("value_source") == "USER_MANUAL_OVERRIDE":
        return "用户输入"
    audit = r.get("main_table_audit") or {}
    if audit.get("verification_status") == MISMATCH_CELL:
        return "请确认"
    if audit.get("verification_status") == VERIFIED:
        return "已验证"
    if r.get("is_temporary_model"):
        return "临时采用"
    return "已计算"


def export_json_document(record: dict) -> dict:
    """The full JSON export: adopted value, audit value and difference all present, and
    a range is still a range - nothing is collapsed to a hidden single value."""
    payload = record["payload"]
    doc = record.get("document") or {}
    cells = []
    for s in payload.get("scenarios", []):
        for r in s.get("results", []):
            for c in (r.get("certification") or {}).get("cells", []) or []:
                cells.append({
                    "scenario": s["scope"], "sku": r["sku_qty"], "function": c["function_id"],
                    "phase": c["phase"],
                    "adopted_total": c.get("adopted_total", c.get("applied_total")),
                    "adopted_value_source": c.get("adopted_value_source"),
                    "main_table_per_sku": c.get("main_table_per_sku_quantity"),
                    "main_table_derived_total": c.get("main_table_derived_total"),
                    "appendix_total": c.get("appendix_total"),
                    "delta": c.get("delta"),
                    "main_derived_counted_in_project_total":
                        c.get("main_derived_counted_in_project_total"),
                    "verification_status": c.get("verification_status"),
                    "value_source": c.get("value_source")})
    return {
        "export_kind": "SAMPLE_REQUIREMENT_ANALYSIS",
        "export_version": "4.0",
        "analysis_id": record.get("id"),
        "project_name": record.get("project_name"),
        "analysis_engine_version": payload.get("engine_version"),
        "rule_package_version": payload.get("rule_pack_version"),
        "schema_version": payload.get("schema_version"),
        "quantity_model_version": payload.get("quantity_model_version"),
        "baseline_id": payload.get("baseline_id"),
        "owner_decision": payload.get("owner_decision"),
        "input_snapshot": doc,
        "file_read_value_vs_user_confirmed_value": doc.get("key_factors"),
        "applied_value": doc.get("key_factors"),
        "sku_result": [{"scenario": s["scope"], "state": s["match"]["state"],
                        "recommended_sku": s["match"]["recommended_sku"],
                        "preferred_sku": s["match"]["preferred_sku"],
                        "sku_range": s["match"]["sku_range"],
                        "candidates_priced": s.get("candidates_priced")}
                       for s in payload.get("scenarios", [])],
        "current_wave": [s for s in payload.get("scenarios", []) if s["scope"] == "CURRENT_WAVE"],
        "full_project": [s for s in payload.get("scenarios", []) if s["scope"] == "FULL_PROJECT"],
        "certification_adopted_and_audit_values": cells,
        "certification_cell_audit": record.get("certification_grid"),
        "j33_evidence": payload.get("j33_evidence"),
        "reuse_ledger": [{"scenario": s["scope"],
                          "ledger": [{"sku": r["sku_qty"], "summary": r.get("reuse_summary"),
                                      "items": r["reuse_ledger"]["items"]}
                                     for r in s.get("results", [])]}
                         for s in payload.get("scenarios", [])],
        "review_items": payload.get("owner_review_items"),
        "panel_annotation_excluded": payload.get("unresolved_comments_excluded"),
        "policy": payload.get("policy"),
        "values_full_precision": True,
        "range_collapsed_to_single_value_on_export": False,
        "payload": payload,
    }


def export_review_csv(record: dict) -> str:
    """The team review report. Eight sections, one per concern, with the adopted value
    first and the retained Main Table audit value next to it."""
    payload = record["payload"]
    lines: list[str] = []

    def row(*vals):
        lines.append(",".join(csv_escape(v) for v in vals))

    def blank():
        lines.append("")

    row("样机需求分析 / Sample Requirement Analysis - team review")
    row("Project", record.get("project_name") or "")
    row("Analysis ID", record.get("id"))
    row("Engine", payload.get("engine_version"))
    row("Rule pack", payload.get("rule_pack_version"))
    row("Schema", payload.get("schema_version"))
    row("Quantity model", payload.get("quantity_model_version"))
    row("Certification adopted", "Appendix total (DEC-10) - counted once")
    row("Certification audit", "Main table per-SKU x SKU - audit only, counted 0 times")
    row("Saved", record.get("saved_at"))
    row("Rounding", "NONE (D-01) - underlying values keep their decimals")
    blank()
    row("1. SKU result")
    row("Scenario", "State", "Recommended SKU", "Preferred", "Range", "Candidates priced")
    for s in payload.get("scenarios", []):
        m = s["match"]
        row(s["scope"], m["state"],
            "not established" if m["recommended_sku"] is None else m["recommended_sku"],
            m["preferred_sku"],
            f"{m['sku_range'][0]}-{m['sku_range'][1]}" if m["sku_range"] else "",
            " / ".join(jsstr(c) for c in (s.get("candidates_priced") or [])))
    blank()
    row("2. Totals")
    row("Scenario", "SKU", "FVT", "SIT", "Certification", "Non-certification",
        "Reuse adopted", "Risk reserve", "Recommended total", "Single value")
    for s in payload.get("scenarios", []):
        for r in s.get("results", []):
            row(s["scope"], r["sku_qty"], r["fvt_total"], r["sit_total"],
                r["certification_demand"], r["non_certification_demand"],
                r["confirmed_reuse_adjustment"], r["risk_reserve"], r["recommended_total"],
                r["single_value"])
    blank()
    row("3. Function detail")
    row("Scenario", "SKU", "Function", "Phase", "Quantity model", "Adopted", "User status",
        "Main /SKU", "Main derived (audit)", "Delta", "Rule", "Source row")
    for s in payload.get("scenarios", []):
        for r in s.get("results", []):
            for x in r.get("rows", []):
                audit = x.get("main_table_audit") or {}
                row(s["scope"], r["sku_qty"], x["function_name"], x["phase"],
                    x["quantity_model"], x["base_demand"], user_row_status(x),
                    x.get("main_table_per_sku_quantity"), x.get("main_table_derived_total"),
                    audit.get("delta"), x["rule_id"], x["evidence"]["row"])
    blank()
    row("4. Certification cells - adopted (Appendix) vs audit (Main table)")
    row("Function", "Phase", "SKU", "Adopted (Appendix)", "Main /SKU", "Main derived (audit)",
        "Delta", "Status", "Main row", "Appendix row", "Adopted counted", "Audit counted")
    for s in payload.get("scenarios", []):
        for r in s.get("results", []):
            for c in (r.get("certification") or {}).get("cells", []) or []:
                row(c["function_name"], c["phase"], c["sku_count"],
                    c.get("adopted_total", c.get("applied_total")),
                    c.get("main_table_per_sku_quantity"), c.get("main_table_derived_total"),
                    c.get("delta"), c.get("verification_status"), c.get("main_table_row"),
                    c.get("appendix_row"), 1, 0)
    blank()
    row("5. J33 (explanatory evidence - never added)")
    j = payload.get("j33_evidence") or {}
    row("Role", j.get("evidence_role"))
    row("Disposition", j.get("disposition"))
    row("Added to result", "NO")
    row("Declared reference", jsstr(j.get("declared_reference_scenario")))
    blank()
    row("6. Reuse ledger")
    row("Scenario", "SKU", "Status", "Qty", "Unit", "Applied", "Decision", "Why")
    for s in payload.get("scenarios", []):
        for r in s.get("results", []):
            for it in r["reuse_ledger"]["items"]:
                row(s["scope"], r["sku_qty"], it.get("reuse_status"), it.get("qty"),
                    it.get("unit"), it.get("applied"), it.get("decision"), it.get("why"))
    blank()
    row("7. Review items for the Owner")
    row("Kind", "Blocking level", "Blocks manual MVP", "Function", "Phase", "Why")
    for o in payload.get("owner_review_items", []):
        row(o.get("kind"), o.get("blocking_level") or "AFFECTS_ACCURACY",
            "YES" if o.get("blocks_manual_mvp") else "NO", o.get("function_id") or "",
            o.get("phase") or "", o.get("why"))
    blank()
    row("8. Excluded Panel annotation evidence (DEC-02, never in any calculation)")
    for k, v in (payload.get("unresolved_comments_excluded") or {}).items():
        row("SKU" + str(k), jsstr(v))
    return "\ufeff" + "\r\n".join(lines)


def export_trial_feedback_csv(record: dict) -> str:
    """Trial feedback form (deliverable: 试用反馈导出). One line per thing the reviewer is
    asked to judge, with empty answer columns. Nothing here decides anything: the questions
    are the ones already registered in the Owner Review Register."""
    payload = record["payload"]
    pack = _pack_doc()
    lines: list[str] = []

    def row(*vals):
        lines.append(",".join(csv_escape(v) for v in vals))

    def blank():
        lines.append("")

    row("样机需求分析 - 团队试用反馈表 / Trial feedback")
    row("Project", record.get("project_name") or "")
    row("Analysis ID", record.get("id"))
    row("Rule pack", payload.get("rule_pack_version"))
    row("Engine", payload.get("engine_version"))
    row("Reviewer name", "")
    row("Review date", "")
    blank()
    row("1. 请对本次结果逐项回答（同意 / 不同意 / 待确认）+ 说明")
    row("Item", "What the tool produced", "Your answer", "Comment")
    for s in payload.get("scenarios", []):
        m = s["match"]
        rng = (f"{m['sku_range'][0]}-{m['sku_range'][1]}" if m["sku_range"] else "")
        row(f"SKU result ({s['scope']})",
            f"{m['state']}; recommended={jsstr(m['recommended_sku'])};"
            f" preferred={jsstr(m['preferred_sku'])}"
            f"{'; range=' + rng if rng else ''}", "", "")
        for r in s.get("results", []):
            row(f"Totals ({s['scope']}, {r['sku_qty']} SKU)",
                f"FVT={jsstr(r['fvt_total'])}; SIT={jsstr(r['sit_total'])}; "
                f"Certification={jsstr(r['certification_demand'])}; "
                f"recommended={jsstr(r['recommended_total'])}", "", "")
    row("Certification adopted value",
        "Appendix total for that Function, Phase and SKU count (DEC-10); counted once", "", "")
    row("Certification audit value",
        "Main table per-SKU quantity x SKU count, kept for difference analysis; counted 0 "
        "times", "", "")
    row("J33", "explanatory evidence only - never added", "", "")
    blank()
    row("2. 主表 / 附表仍然不一致的格子（请在真实项目里核对哪一个是业务上正确的数量）")
    row("Function", "Phase", "Adopted (Appendix)", "Main derived (audit)", "Delta",
        "Is the adopted value correct?", "Comment")
    seen = set()
    for s in payload.get("scenarios", []):
        for r in s.get("results", []):
            for c in (r.get("certification") or {}).get("mismatched_cells", []) or []:
                k = (c["function_id"], c["phase"])
                if k in seen:
                    continue
                seen.add(k)
                row(c["function_name"], c["phase"], c.get("adopted_total"),
                    c.get("main_table_derived_total"), c.get("delta"), "", "")
    blank()
    row("3. 本次分析登记的待确认问题")
    row("Kind", "Blocking level", "Blocks manual MVP", "Your answer", "Comment")
    for o in payload.get("owner_review_items", []):
        row(o.get("kind"), o.get("blocking_level") or "AFFECTS_ACCURACY",
            "YES" if o.get("blocks_manual_mvp") else "NO", "", "")
    blank()
    row("4. 规则包中仍然开放的 Owner 问题（唯一条目，不是影响标签）")
    row("ORI", "Impact tag", "Question", "Your answer", "Comment")
    for o in pack.get("open_owner_review_items", []):
        row(o["id"], o["blocking_level"], o.get("summary", ""), "", "")
    blank()
    row("5. 界面与流程反馈")
    row("Topic", "Your answer", "Comment")
    for topic in ("字段是否够用", "结果是否看得懂", "导出文件是否够用", "其它问题"):
        row(topic, "", "")
    return "\ufeff" + "\r\n".join(lines)
