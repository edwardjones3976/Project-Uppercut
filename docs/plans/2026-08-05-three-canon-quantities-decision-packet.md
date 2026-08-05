<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 13:20 UTC | START ] -->

# Decision packet — three canon quantities that cannot work as authored

Phase O has been held since 2026-08-04 on a knockdown rate too high for
`decision_path_must_survive`. Over 2026-08-05 the cause was traced through four
new phases, eight corrected diagnoses, and one confound that invalidated four
earlier conclusions. It is now located, and it is not in the knockdown model.

**Three separate canon quantities each cannot produce a boxer as authored.** All
three were written against systems that did not exist when they were written.
None of them is mine to decide, and picking a number for any of them is the exact
failure mode this investigation kept walking into: a measurement that looks like
progress because it made fighters worse.

Everything below is measured; sources are named per item.

---

## The context, in one table

| | this core | reference sim | professional boxing |
|---|---|---|---|
| punches thrown per fighter-round | 175–219 | 41.4 | 55–78 (30–60 heavyweight) |
| connect rate | 60% | 42.4% | 25–40%, CompuBox power avg 36.9% |
| knockdowns per minute | 7.6–8.1 | 0.38 | — |
| stamina drained per minute | 93–120% | 11.1% | — |
| bouts reaching the cards | 0/24 | 20/24 | — |

The reference simulator satisfies `decision_path_must_survive` with canon's own
numbers and always has. The threshold is not mistuned. Sources:
`measure_reference_gap.py`, `experiment_tiered_policy.py`.

---

## Item 1 — canon prices a step twice, 4.55× apart

    movement_model.locomotion   0.60 per reach unit x 0.22 ru stride = 0.132
    data/moves generic table    0.600 per step, flat

The core reads the move table, so it pays the higher one. Footwork is the largest
single item in the stamina economy — 108.2 per fighter-round against a pool of
100, 46.7% of all spend. At the locomotion price it is 23.8.

**This is a contradiction, not a tuning question.** One of the two is the price of
a step and the other is not.

*Options.* (a) The locomotion model is canon and the move table's flat cost is a
placeholder to be derived from it. (b) The move table is canon and the locomotion
model's per-ru figure describes free navigation rather than a boxing step. (c)
Both are right and describe different acts — in which case the move table's
`step_in` is not a 0.22 ru stride and the range model needs a different stride
source.

*Consequence either way.* Everything downstream of footwork — the stamina economy,
the lethality residual, every Phase Q and R number — is wrong until this is
settled. It is the cheapest of the three to answer.

*Evidence.* `experiment_recovery_models.py`; development log
`2026-08-05-not-recovery-footwork-and-a-canon-contradiction.md`.

---

## Item 2 — `aggression_bias` is roughly 7× too high

Canon's tiers author 0.35 (novice) to 0.60 (champion) as the share of decisions
that throw. Executed at canon's own 4-tick decision interval, that produces
175–219 punches per fighter-round against a professional 55–78.

| aggression | thrown/f-round | bouts reaching cards |
|---|---|---|
| 0.35 (canon's lowest) | 175.0 | 0/24 |
| 0.10 | 79.9 | 0/24 |
| **0.05** | **47.1** | 0/24 |
| 0.025 | 25.6 | 1/24 |
| 0.005 | 5.6 | 20/24 |

Reading each tier's `reaction_ticks` as its decision interval instead gives
108–201 — still two to five times over. **Neither reading of the decision clock
rescues the authored values.**

*Options.* (a) The values are shares of a decision cadence much slower than 4
ticks, and the tier model needs a third number naming it. (b) The values are
correct and the decision interval is wrong. (c) The values are shares of
*offensive intent* rather than of *throws*, with something downstream (range,
guard, commitment) expected to filter most of them — in which case the filter is
missing rather than the number being wrong.

*Note against myself.* Option (c) is the reading I would bet on and I have not
tested it, because testing it means inventing the missing filter, and inventing a
filter to rescue a number is how a model gets tuned to its own assumptions.

*Evidence.* `experiment_tiered_policy.py`; development log
`2026-08-05-phase-s-nobody-can-react-to-a-jab.md`.

---

## Item 3 — nothing in canon authors doing nothing

Of the non-offensive choices available to a fighter, four of six are steps or
slips that charge stamina. `idle` is one option among them, and `movement_model.
threat_compression` changes stride *mode*, not whether a stride happens. So a
fighter takes a full stride at essentially every decision he does not punch on:
well over a thousand strides per round against a real boxer's couple of hundred.

Even at a professional throw rate (aggression 0.05, 47.1 per round) the drain is
93.3% of the pool per minute and 0/24 bouts reach the cards.

**The stamina economy's problem is action COUNT.** Not action price — that is Item
1, and it is a 4.55× correction on one line item. Not recovery — regenerating at
the full authored rate on every single tick, committed or not, moves stamina at
one minute from 4.8 to 7.4.

*Options.* (a) A rest bias beside the aggression bias in the tier model: the share
of decisions that are no action at all. (b) Movement decisions on their own,
slower clock — a fighter re-steps far less often than he re-decides. (c) Stride
cost scales with actual displacement, so a small adjustment costs a fraction of a
full stride; `max_frame_displacement_ru` already implies the machinery.

*Evidence.* `experiment_recovery_models.py`, `experiment_tiered_policy.py`.

---

## What is NOT in question

**`pressure_threshold` (0.57), the pressure terms, and the three-knockdown rule.**
Three separate attempts to blame them were each overturned by the next
measurement. The threshold would have to sit at 1.0268 to let a bout reach the
cards — above the 99th percentile of observed pressure and near the observed
ceiling — which is not a higher bar but knockdowns switched off. The reference
meets the invariant with the same threshold.

**The recovery branch.** Raised on 2026-08-05 as the Director's one question, and
withdrawn the same day: regen is a rounding error next to spend.

**The guard hold.** Called "11% of the story" earlier and asked about directly —
it is 1.2% of spend. It was never the story.

---

## Recommended order

**Item 1 first**, because it is a contradiction rather than a judgement, it is a
five-minute answer, and every number downstream of footwork depends on it.

**Item 3 second**, because it is the largest effect and because Items 2 and 3
interact — a rest bias changes what an aggression bias is a share of, so answering
2 before 3 risks answering it twice.

**Item 2 last**, and possibly not at all: if Item 3's answer is a rest bias, the
aggression values may be correct as shares of the decisions that remain.

Nothing further should be built on the current stamina numbers until Item 1 is
answered. The phase contracts (P, Q, R, S) and their 641 tests are unaffected —
they encode rules, not quantities — and the C++ implementation should wait for all
three.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 13:20 UTC | END ] -->
