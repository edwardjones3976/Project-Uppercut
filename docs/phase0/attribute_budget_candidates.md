<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ] -->

# Phase 0 Gate Item — Attribute Budget Formula (RULED)

> **Ruled in [Decision 0007](../decisions/0007-phase0-gate-rulings.md) (D-1), 2026-08-02, under
> Director delegation:** curve **C, tiered marginal**; **refund rate 0.5**; **cap 1000** applying only
> to complete declarations. Canonical form: `data/attribute_budget.json`, enforced by the Rule 10
> validator. The cap carries `tuning_status: hypothesis` and rests on one modelled build — recalibrate
> when real roster characters exist.

The ROADMAP Phase 0 quality gate requires that **one canonical attribute-budget formula** be chosen.
This document exists so the choice was made against real numbers rather than intuition. All three
candidates remain implemented in `tools/uppercut_validate/budget.py`; the selected one is now enforced,
so the validator polices Rule 10's *economy* as well as its *laws*.

## What Rule 10 demands of any candidate

Advantages require meaningful costs or disadvantages. Extreme values carry **escalating** budget cost.
The model must not permit unrestricted upward stacking. No single overall rating may stand in for the
profile.

## The candidates

| | Formula | +40 | +70 | +100 | Escalating? |
|---|---|---|---|---|---|
| **A — Linear** | `cost = \|v\|` | 40.0 | 70.0 | 100.0 | **No** |
| **B — Quadratic** | `cost = v² / 100` | 16.0 | 49.0 | 100.0 | Yes, smoothly |
| **C — Tiered marginal** | `1× on 0–40, 2× on 41–70, 3× on 71–100` | 40.0 | 100.0 | 190.0 | Yes, sharply |

Candidate A is included only as the baseline the others are measured against. It fails Rule 10's
escalation clause on its own terms and should not be selected without an additional mechanism.

## Measured against the current fixtures

Net cost (`spend − refund`, refund rate 1.0) for the three legal builds:

| Fixture | A — Linear | B — Quadratic | C — Tiered |
|---|---|---|---|
| `legal_baseline` (broad, moderate) | 100.00 | 16.00 | 100.00 |
| `legal_boundaries` (two +70s, two mild negatives) | 85.00 | 74.25 | 145.00 |
| `legal_extremes` (+100, +80, −100, −45) | 65.00 | 47.25 | 110.00 |

**The finding that should drive the ruling:** under every curve at full refund, `legal_extremes` —
the most polarised build in the set — costs *less* than the moderate ones. Severe negatives refund
more than the elite positives cost. That is exactly the "unrestricted upward stacking" Rule 10
forbids, and it is a property of the **refund rate**, not of the curve.

So the ruling has two parts:

1. **Which curve** — recommendation: **C (tiered marginal)**, because its 40/70 tier boundaries are
   the same thresholds Rule 10 already uses for its caps and compensation ladder, so authors reason
   about one set of numbers instead of two, and it punishes extremes hardest.
2. **Refund rate for negatives** — recommendation: **discounted, not full**. A rate around 0.5
   preserves give-and-take while making a polarised build cost more than a rounded one. The exact
   figure is a tuning hypothesis (Rule 18) that should be set, then re-measured against the fixture
   set and adjusted before roster authoring begins.

A third parameter — the **cap** itself — only becomes meaningful once curve and refund rate are fixed.
Recommend setting it after the first pass so it is calibrated to real builds rather than guessed.
*(Set to 1000 in the ruling, calibrated against a modelled complete build at net 869.)*

## Reproducing these numbers

```
python3 -m tools.uppercut_validate.cli budget
```

This document is retained as the reasoning and measurement behind the ruling.

## What the ruling changed in code

`data/attribute_budget.json` holds the canonical curve, refund rate and cap.
`budget.evaluate()` scores a build against them; the Rule 10 validator raises `R10.budget_cap` when a
**complete** build exceeds the cap. Partial sandbox fixtures report cost but are not capped, because
cost scales with declaration count: a 7-attribute fixture nets 230 where a complete 24-attribute build
nets 869, and no single absolute cap spans both.

Two fixtures pin the behaviour: `legal/reference_complete_shape.json` (24 attributes, near several
Rule 10 caps at once, net 869 — legal) and `illegal/illegal_over_budget_cap.json` (net 1446.5 —
rejected for `R10.budget_cap` and nothing else).

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ] -->
