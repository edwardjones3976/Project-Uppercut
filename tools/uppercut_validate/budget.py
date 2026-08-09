# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""Candidate attribute-budget cost curves.

ROADMAP Phase 0 quality gate requires that ONE canonical attribute-budget formula
be chosen. That choice belongs to the Director. This module implements the
candidates so the choice can be made against real numbers instead of intuition,
and deliberately enforces no cap until a curve is selected in
docs/phase0/attribute_budget_candidates.md.

Rule 10 constraints every candidate must honour:
  - give-and-take: advantages require meaningful costs or disadvantages
  - extreme values carry ESCALATING budget cost
  - the model must not permit unrestricted upward stacking
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

CURVES = {}


def curve(name):
    def deco(fn):
        CURVES[name] = fn
        return fn
    return deco


@curve("A_linear")
def cost_linear(v: int) -> float:
    """cost = |v|. Simple, but NOT escalating: fails Rule 10's escalation clause
    on its own and is included only as the baseline the others are measured against."""
    return float(abs(v))


@curve("B_quadratic")
def cost_quadratic(v: int) -> float:
    """cost = v^2 / 100. Smoothly escalating: +100 costs 100.0, +70 costs 49.0,
    +40 costs 16.0. Cheap mid-range breadth, expensive extremes."""
    return (v * v) / 100.0


@curve("C_tiered_marginal")
def cost_tiered(v: int) -> float:
    """Progressive marginal tiers: 1x on 0-40, 2x on 41-70, 3x on 71-100.
    +100 costs 40 + 60 + 90 = 190.0. Sharpest penalty on extremes; most legible
    to authors because the tier boundaries match Rule 10's own thresholds."""
    a = abs(v)
    t1 = min(a, 40) * 1.0
    t2 = max(0, min(a, 70) - 40) * 2.0
    t3 = max(0, a - 70) * 3.0
    return t1 + t2 + t3


def profile(attrs: dict, refund_rate: float = 1.0) -> dict:
    """Return the spend/refund/net for every candidate curve.

    refund_rate < 1.0 means negatives return less than positives cost, which is
    one lever against unrestricted upward stacking; it is itself a Director choice.
    """
    out = {}
    for name, fn in CURVES.items():
        spend = sum(fn(v) for v in attrs.values() if v > 0)
        refund = sum(fn(v) for v in attrs.values() if v < 0) * refund_rate
        out[name] = {"spend": round(spend, 2), "refund": round(refund, 2),
                     "net": round(spend - refund, 2)}
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]


def load_config(path: Path | None = None) -> dict:
    """The canonical formula ruled in Decision 0007."""
    path = path or REPO / "data" / "attribute_budget.json"
    return json.loads(path.read_text())


def taxonomy_keys(path: Path | None = None) -> set:
    path = path or REPO / "data" / "attribute_families.json"
    fam = json.loads(path.read_text())["families"]
    return {a for spec in fam.values() for a in spec["attributes"]}


def evaluate(attrs: dict, config: dict | None = None) -> dict:
    """Score a build against the canonical curve, refund rate and cap.

    The cap applies only to complete declarations; a partial sandbox fixture is an
    instrument, and its cost is reported rather than enforced.
    """
    config = config or load_config()
    fn = CURVES[config["curve"]]
    spend = sum(fn(v) for v in attrs.values() if v > 0)
    refund = sum(fn(v) for v in attrs.values() if v < 0) * config["refund_rate"]
    net = spend - refund
    complete = set(attrs) == taxonomy_keys()
    capped = complete and config.get("cap_scope") == "complete_declaration"
    return {"curve": config["curve"], "refund_rate": config["refund_rate"],
            "spend": round(spend, 2), "refund": round(refund, 2), "net": round(net, 2),
            "complete_declaration": complete, "cap": config["cap"],
            "cap_enforced": capped, "over_cap": bool(capped and net > config["cap"])}
