<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:43 UTC | START ] -->

# Condition and Recovery — ROADMAP Phase 1A step 8

Canon: `data/condition_model.json` · Schema: `schemas/condition_model.schema.json` ·
Validator: `tools/uppercut_validate/condition.py` · Tests: `tests/test_condition.py`

**Rule 18.** Definitions only. Nobody has been hurt in this engine, and every number is a tuning
hypothesis.

## What was already settled, and what this adds

`data/condition_regions.json` has declared *which* regions exist since Phase 0 — fifteen of them,
eight physically strikeable and the rest runtime pools and attribute-governed states. What it never
said is what accumulates in them, how much comes back between rounds, or what happens when a fighter
goes down. That is this step.

Step 6 defined what a punch costs to throw and deliberately left the stamina *pool* open. This closes
it: 100 points, regeneration of 0.09 per tick idle, 0.04 moving, and **zero while throwing**.

## Three prohibitions that carry the whole model

Rule 14 is unusually specific about how a damage model stops being boxing, and each failure mode is a
schema constant rather than a convention.

**No generic health pool.** Eight strikeable regions, eight condition tracks, each declaring what it
impairs — the eyes take accuracy and tracking, the torso takes stamina, the arms take guard
integrity, the jaw takes balance and is the knockdown-relevant one. A region that impairs nothing is
rejected, because damage that changes nothing is decoration.

**No flat random knockout roll.** The knockdown reads delivered force, contact quality, target
region, closing velocity, balance, accumulated condition, chin state and guard state. The validator
requires force, quality and accumulated condition specifically: a knockdown decided on less than
those is a dice roll wearing a longer name.

**Chin +100 is not immunity.** It is the most authored resistance available, and it still loses to
enough evidence. `early_stoppage_possible_at_max` is a const `true` the validator enforces, because
the alternative — a Chin value that cannot be stopped early — is immunity arriving by another route.

## Rounds do not erase rounds

Every region recovers *some* fraction between rounds and none recovers fully — the schema bounds the
value strictly below 1 and the validator repeats the check. Arms come back fastest at 0.15, eyes
slowest at 0.05, because swelling does not un-swell in thirty seconds. Stamina recovers 0.35 of its
deficit.

This is the mechanism that makes a late round feel different from an early one, and it is exactly
the mechanism a well-meaning tuning pass would erase by "resetting between rounds." Hence the check.

## Stamina regeneration is monotone

Idle ≥ moving ≥ throwing, and throwing is exactly zero. Inverting that ordering inverts the entire
stamina economy — a fighter would recover faster by working than by breathing, and patient boxing
would stop being a strategy. The validator enforces the ordering rather than the specific numbers,
so tuning stays free and the law stays fixed.

## The count clock belongs to nobody

One number per authoritative second, count to ten, mandatory eight-count, three knockdowns per round
and four per bout, a 480-tick window to rise. Rule 16 gives referees different enforcement
philosophies — clinches, warnings, deductions, stoppage thresholds — but never the arithmetic of the
count or the medical minimums. The validator pins 60 ticks per number so an officiating profile
cannot reach it.

The between-rounds break is 1800 ticks: thirty real seconds at the authoritative 60-tick clock, per
Rule 8, and menus do not pause it. That is why the corner is a resource rather than a loading screen.

## Stoppages are evidenced, and blind to the cards

Five conditions, each naming an authority and an observable trigger: count expired and knockdown
limit and referee judgement belong to the referee, medical minimums to the doctor, retirement to the
corner. The validator scans every trigger for score, card, points, behind and ahead, and fails on any
of them — Rule 3's firewall applies to officiating exactly as it applies to CPU logic. A corner that
retires a fighter because they are behind on the cards is reading something it cannot see.

## What step 8 leaves open

Which fighter chooses to keep pressing while hurt is step 9. The event log that would let a spectator
understand why a stoppage happened is step 10. The referee profiles exist as data for all seven
officials and nothing consumes them yet.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:43 UTC | END ] -->
