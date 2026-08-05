<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:30 UTC | START ] -->

# Decision 0015 — Thinking is free: rest and no-action are first-class outcomes

**Status:** accepted (Director ruling, 2026-08-05)
**Closes:** gate **G2**
**Date:** 2026-08-05
**Packet:** `docs/plans/2026-08-05-three-canon-quantities-decision-packet.md` §Item 3

## Question

Nothing in canon authored *doing nothing*. Four of six non-offensive choices
charged stamina, so a fighter took a full stride at essentially every decision he
did not punch on. Measured on the contract, that is the stamina economy's actual
problem: not the price of an action, and not the recovery rate, but the **count**
of actions.

## Decision

**Deciding must not cost anything physical.** A fighter may reconsider on every
decision tick without stepping, slipping or punching on any of them.

The policy layer emits a first-class outcome, one of:

| Outcome | Displacement | Stamina | Meaning |
|---|---|---|---|
| `Observe` | none | none | read the opponent; commit to nothing |
| `HoldPosition` | none | posture hold only | keep stance and range |
| `Rest` | none | recovers under the physiology rules | deliberately lower activity |
| `MicroAdjust` | small, real | proportional to displacement (0014) | a shift, not a step |
| `Move` | authored stride | proportional to displacement (0014) | a purposeful step |
| `Guard` | none | the posture's declared hold | maintain a posture |
| `Evade` | authored | authored commitment and cost | slip, roll |
| `Attack` | authored | authored commitment and cost | a punch |
| `Feint` | — | — | reserved; arrives with its phase |

`Observe` is the important one and the one that did not exist. It is what a boxer
does most of the time, it is why a real fighter is not exhausted in round three,
and its absence is why this core's fighters were.

## Why this shape rather than "add an idle action"

An idle entry in a flat action table is a fifth of a nine-way draw, which is a
frequency rather than a behaviour. The outcomes above are what a policy *returns*
after deciding, so the policy can hold, observe, and then act — and the cost
follows from what it actually did. `idle` as a table row cannot express "I
considered three things and moved on none of them."

`Rest` is deliberately distinct from `Observe`. Observing is free but neutral;
resting is a choice with a tactical price — a fighter who rests is not
threatening, and canon's physiology decides what he gets back for it.

## Consequences

- The Phase O and Phase S action sets change shape. Contracts change; the pinned
  streams move and are re-blessed with the change.
- Every punches-per-round and stamina-at-minute figure measured before this
  ruling was measured against a fighter who could not stand still. They are
  re-measured, not re-read.
- CPU policy gains a real "do nothing" branch, which is a prerequisite for the
  reason codes in Decision 0016 meaning anything: `HOLD_AND_OBSERVE` cannot be a
  reason code in a model where holding is not an outcome.

## What this does not decide

How *often* each outcome is chosen. That is policy, and it is Decision 0016.
This record says only that the outcomes exist, that thinking is free, and that
zero displacement costs zero.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:30 UTC | END ] -->
