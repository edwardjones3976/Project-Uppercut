<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 16:20 UTC | START ] -->

# Attributes in the loop

Canon: `data/attribute_effects.json` · Schema: `schemas/attribute_effects.schema.json`
Validator: `tools/uppercut_validate/attribute_effects.py` · Tests: `tests/test_attribute_effects.py`

## The gap this closes

`attribute_families.json` has declared three families of twenty-four attributes on a
−100..+100 scale since Phase 0. Fighter fixtures carry them. `attributes.py` and
`budget.py` police them. **The reference bout read none of them.** It ran on six
hardcoded tuning tuples, so two fighters could not differ in durability, because there
were no fighters.

The sharpest instance was Chin. `condition_model.chin` declares `attribute: "chin"`,
`scales: [knockdown_resistance, stun_duration]` and `max_resistance_confers_immunity:
false` — a bound Rule 14 states explicitly and a validator enforces. Searching the
simulator for `chin` returned ten hits, every one either the *region* `jaw_chin` or the
word "machine". Nothing in the bout knew what a chin was.

The ROADMAP's Phase 1A minimum scope asks for outcomes explainable in terms of
attributes. This is what makes that sentence mechanical.

## The shape

One file declares every way an attribute reaches the fight, as a bounded multiplier band
interpolated linearly across the attribute range:

```
power  → delivered_impact              0.78 … 1.28
chin   → knockdown_pressure_threshold  0.82 … 1.32
hand_speed → punch_startup             1.25 … 0.80   (higher is faster, so the band falls)
```

Fourteen attributes reach the fight; ten are named in `unexpressed_attributes` with a
reason. Every one of the twenty-four is in exactly one of those two places — the
validator refuses the silent third state, which is the same law the coverage checker
applies to canon keys.

Three properties are load-bearing:

**A zeroed attribute multiplies by exactly one.** An empty fighter card fights the
baseline model, so any difference between two cards is attributable to the cards rather
than to the mapping. Rule 10, enforced by `check_curve`.

**No band reaches zero and none is wider than 0.7.** A minimum attribute never makes a
mechanic impossible and a maximum never decides an outcome alone — Rule 11 read from
both sides, enforced by `check_bounds`.

**Chin's ceiling is checked against the file that forbids immunity.**
`condition_model.chin.max_resistance_confers_immunity` is a claim about *data*;
`check_chin_is_not_immunity` is the claim about *arithmetic*, and the two can drift
apart. A chin multiplier without a ceiling would make +100 Chin unfalsifiable no matter
what the other file promises.

Attributes are looked up **by the mechanic being scaled**, not by attribute name, so a
call site says what it is scaling and the data says which attribute does the scaling.
Adding an effect changes behaviour with no engine edit; removing one returns that
mechanic to baseline.

## What the stress profiles became

They were six tuples. They are now attribute loadouts plus a tendency mapping, and every
entry traces to a sentence in `data/stress_profiles/`: the power threat's card says power
and chin because its canon says "contact quality: force, placement and accumulated
condition"; the drainer's says recovery and stamina because its canon says "distance,
composure, created misses, counters, bodywork, recovery".

Exploit policies deliberately carry **no card**, so an abuse fights the baseline model
and its result is attributable to the abuse rather than to a stat line.

## Two things the validator caught immediately

**Three of fourteen effects had inverted bands.** Durability, hand speed and combination
fluency are all `higher_is_weaker` — a better attribute *lowers* the multiplier, because
fast hands shorten startup — and all three were authored rising. `check_effects` refused
them before a single bout ran.

**The coverage registry collided with itself.** `attribute_effects` first used
`reference_model_coverage.not_yet_expressed` to list unexpressed *attributes*, while the
coverage checker reads that same key to mean unread *JSON keys*. Two different questions
under one name, and `registry_is_honest` reported every attribute as a dead entry the
moment the file entered scope. The registries are now separate: `unexpressed_attributes`
for attributes, `reference_model_coverage` for keys.

That check also did something more useful: it **shrank the debt list**. `chin` and
`start_fraction` were listed as unexpressed in `condition_model` and are now read, so the
checker refused to let them keep claiming otherwise.

## Measured after

All-pairs at canonical length, eight seeds, two independent seed bases:

| style | 41000 | 7000 |
|---|---|---|
| technician | 62% | 62% |
| counterpuncher | 45% | 65% |
| rusher | 52% | 35% |
| power_threat | 45% | 38% |
| showman | 30% | 28% |
| drainer | 25% | 28% |

Result states 30% stoppage / 54% decision / 16% draws. Work rate 33 punches per fighter
per round, 43% connect, top landed move 38% against the 60% gate. All eleven required
checks green. Determinism byte-identical, divergent on a different seed.

**Balance did not improve and is still open.** The drainer and the showman sit below 30%
on both bases. Two cards were softened once — the showman was being punished three times
over for the same idea, with a low guard *and* low durability *and* a low chin, when its
canon only asks for exposure; the drainer at −25 power could not score at all, and a style
that cannot score cannot cash the round it just spent three minutes winning. Beyond that
the numbers were left alone deliberately, because tuning cards until a table looks even is
the behaviour this whole rig exists to make unnecessary.

What has changed is that the question is now answerable. A style's win rate is a
consequence of a card whose every entry traces to that style's canon, instead of a
property of six constants nobody could defend.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 16:20 UTC | END ] -->
