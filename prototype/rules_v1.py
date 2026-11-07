"""SKU / sample-demand rule engine v1 — DESIGN VALIDATION HARNESS (not the MVP app).

Purpose: prove that the designed rules are executable and to quantify ambiguity in the
current SKU Definition. Loads all numbers from artifacts/model/baseline_v1.json which is
itself derived from the Owner workbook. Nothing here is hand-typed business data.

D-01: all intermediate and final values are float; no rounding anywhere in computation.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / "artifacts/model/baseline_v1.json").read_text(encoding="utf-8"))
SKUS = [2, 3, 4, 5, 6]

# ---------------------------------------------------------------- input model
UNKNOWN = "UNKNOWN"
WEIGHTS = {"MATCH": 1.0, "PARTIAL_MATCH": 0.4, "MISMATCH": 0.0}
# dimensions that materially discriminate SKU bands (evidence: see docs/04_sku_model.md §G.4)
DIM_WEIGHT = {"cpu": 1.0, "gpu": 1.6, "panel": 1.0, "ssd": 1.4, "mem": 1.4}


@dataclass
class KeyFactor:
    """One key factor. `file_value` = auto-read, `user_value` = user final choice."""
    name: str
    file_value: int | None = None
    user_value: int | None = None
    user_edited: bool = False
    #: ssd/mem only: the 2nd spec is arranged to a second wave (row 80 clause).
    #: User-declared — the workbook gives no rule to derive it (ORI-03).
    second_wave_deferred: bool = False

    @property
    def effective(self) -> int | None:
        """Priority: user confirmed > file read > None (never default 0/1)."""
        if self.user_edited:
            return self.user_value
        return self.file_value if self.file_value is not None else self.user_value

    @property
    def source(self) -> str:
        if self.user_edited and self.user_value is not None:
            return "USER"
        if self.file_value is not None:
            return "FILE"
        if self.user_value is not None:
            return "USER"
        return UNKNOWN


@dataclass
class AnalysisInput:
    cpu: KeyFactor = field(default_factory=lambda: KeyFactor("cpu"))
    gpu: KeyFactor = field(default_factory=lambda: KeyFactor("gpu"))
    panel: KeyFactor = field(default_factory=lambda: KeyFactor("panel"))
    ssd: KeyFactor = field(default_factory=lambda: KeyFactor("ssd"))
    mem: KeyFactor = field(default_factory=lambda: KeyFactor("mem"))
    odm: str | None = None            # LCFC | HQ | Compal | None
    optional_flags: dict = field(default_factory=dict)
    confirmed_reuse: float = 0.0      # only CONFIRMED reuse enters the calculation
    potential_reuse: float = 0.0      # opportunity only; never subtracted
    risk_reserve_pct: float | None = None

    def factors(self) -> dict:
        return {"cpu": self.cpu, "gpu": self.gpu, "panel": self.panel,
                "ssd": self.ssd, "mem": self.mem}

    def missing(self) -> list:
        return [k for k, f in self.factors().items() if f.effective is None]


# ---------------------------------------------------------------- SKU matching
def _dim_verdict(value: int | None, rng) -> str:
    if value is None or rng is None:
        return UNKNOWN
    lo, hi = rng
    if lo <= value <= hi:
        return "MATCH"
    if value in (lo - 1, hi + 1):
        return "PARTIAL_MATCH"          # one step outside the documented band
    return "MISMATCH"


def match_sku(inp: AnalysisInput, wave: str = "current") -> dict:
    """Score every SKU candidate against the confirmed key factors."""
    cands = []
    for n in SKUS:
        d = BASELINE["sku_definition"][f"SKU{n}"]
        rng = {k: d.get(k) for k in ("cpu", "gpu", "panel", "ssd", "mem")}
        if wave == "current" and d.get("has_second_wave_option"):
            rng = dict(rng)  # current-wave reading: the "or *2 -> 2nd wave" branch stays out
        cpu = inp.factors()["cpu"].effective
        gpu = inp.factors()["gpu"].effective
        panel = inp.factors()["panel"].effective
        ssd = inp.factors()["ssd"].effective
        mem = inp.factors()["mem"].effective
        if wave == "current":
            # Row 80: "(or SSD/Mem spec *2, arrange 2nd wave)". When the user declares that
            # 2nd spec as deferred, the CURRENT wave carries only 1 spec of that kind.
            if ssd == 2 and inp.ssd.second_wave_deferred:
                ssd = 1
            if mem == 2 and inp.mem.second_wave_deferred:
                mem = 1
        vals = {"cpu": cpu, "gpu": gpu, "panel": panel, "ssd": ssd, "mem": mem}
        verdicts, score, wsum, reasons = {}, 0.0, 0.0, []
        for k in ("cpu", "gpu", "panel", "ssd", "mem"):
            v = vals[k]
            verdicts[k] = _dim_verdict(v, rng[k])
            if verdicts[k] == UNKNOWN:
                reasons.append(f"{k}:UNKNOWN(请补充)")
                continue
            w = DIM_WEIGHT[k]
            wsum += w
            score += WEIGHTS[verdicts[k]] * w
            reasons.append(f"{k}={v} vs {rng[k]} -> {verdicts[k]}")
        cands.append({
            "sku": n, "score": round(score, 6), "weight_sum": round(wsum, 6),
            "normalized": round(score / wsum, 6) if wsum else None,
            "verdicts": verdicts, "reasons": reasons,
            "hard_mismatch": [k for k, v in verdicts.items() if v == "MISMATCH"],
            "ranges": rng,
        })
    return _resolve(cands, inp)


def _resolve(cands: list, inp: AnalysisInput) -> dict:
    known = [c for c in cands if c["weight_sum"] > 0]
    if not known:
        return {"state": "UNDETERMINED", "reason": "no key factor supplied", "candidates": cands,
                "recommended": None, "range": None}
    best = max(c["normalized"] for c in known)
    winners = [c for c in known if abs(c["normalized"] - best) < 1e-9]
    losers = [c for c in known if c not in winners]
    missing = inp.missing()
    result = {"candidates": cands, "top_score": best, "missing_key_factors": missing,
              "runner_up_excluded": [
                  {"sku": c["sku"], "normalized": c["normalized"],
                   "why_not": ("hard mismatch on " + "/".join(c["hard_mismatch"]))
                              if c["hard_mismatch"] else "lower weighted match"}
                  for c in sorted(losers, key=lambda x: -x["normalized"])[:2]]}
    if len(winners) == 1:
        w = winners[0]
        ambiguous = best < 1.0 or bool(missing)
        result.update({
            "state": "SINGLE" if not ambiguous else "SINGLE_WITH_RESERVATION",
            "recommended": w["sku"], "range": [w["sku"], w["sku"]],
            "basis": w["reasons"], "score": w["normalized"],
        })
    else:
        skus = sorted(c["sku"] for c in winners)
        result.update({
            "state": "RANGE", "recommended": None, "range": [skus[0], skus[-1]],
            "tie": skus,
            "basis": [f"tie at normalized={best:.2f} among {skus}"],
            "score": best,
        })
    if best <= 0.0:
        result.update({"state": "UNDETERMINED", "recommended": None, "range": None,
                       "reason": "no candidate reaches any match on the confirmed inputs"})
    return result


# ---------------------------------------------------------------- demand calc
def function_table() -> list:
    return BASELINE["functions"]


def demand_rows(inp: AnalysisInput, sku: int) -> list:
    """Base demand per Function x Phase for a given SKU count. D-01: floats, no rounding."""
    rows = []
    for f in function_table():
        for phase in ("FVT", "SIT"):
            base = f["per_sku_rate"][phase].get(f"SKU{sku}")
            if base is None:
                continue
            rows.append({
                "function_id": f["function_id"], "category": f["category"], "function": f["name"],
                "phase": phase, "base_demand": float(base) * sku, "per_sku_rate": float(base),
                "sku_qty": sku, "rule_id": f"{BASELINE['baseline_id']}:{f['function_id']}:{phase}",
                "rule_version": BASELINE["baseline_version"],
                "evidence": {"file": BASELINE["derived_from"]["file"],
                             "row": f["source_rows"]["fvt"] if phase == "FVT" else f["source_rows"]["sit"],
                             "column": {2: "D", 3: "E", 4: "F", 5: "G", 6: "H"}[sku]},
                "status_note": f["status_text"],
            })
    return rows


def summarise(rows: list) -> dict:
    out = {"FVT": 0.0, "SIT": 0.0, "by_category": {}, "by_function": {}}
    for r in rows:
        out[r["phase"]] += r["base_demand"]
        out["by_category"][r["category"]] = out["by_category"].get(r["category"], 0.0) + r["base_demand"]
        out["by_function"][r["function"]] = out["by_function"].get(r["function"], 0.0) + r["base_demand"]
    out["TOTAL"] = out["FVT"] + out["SIT"]
    return {k: (round(v, 10) if isinstance(v, float) else v) for k, v in out.items()}


def finalise(inp: AnalysisInput, sku: int, risk_pct: float = 0.0) -> dict:
    """Base + Conditional + Confirmed Reuse + Risk -> Recommended (D-01, no rounding)."""
    rows = demand_rows(inp, sku)
    s = summarise(rows)
    conditional = float(inp.optional_flags.get("conditional_increment", 0.0))
    reuse = -abs(float(inp.confirmed_reuse))
    reserve = (s["TOTAL"] + conditional + reuse) * float(risk_pct)
    return {
        "sku": sku,
        "base_demand": s["TOTAL"], "fvt": s["FVT"], "sit": s["SIT"],
        "conditional_increment": conditional,
        "confirmed_reuse_adjustment": reuse,
        "potential_reuse_shown_not_applied": float(inp.potential_reuse),
        "risk_reserve": reserve,
        "recommended_total": s["TOTAL"] + conditional + reuse + reserve,
        "by_category": s["by_category"], "by_function": s["by_function"],
        "rows": rows,
        "policy": {"rounding": "NONE (D-01)", "potential_reuse": "DISPLAY_ONLY"},
    }
