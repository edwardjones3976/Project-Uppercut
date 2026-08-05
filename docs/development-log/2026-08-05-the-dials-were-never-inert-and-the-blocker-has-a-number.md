<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 03:10 UTC | START ] -->

# The dials were never inert — and Phase O's blocker finally has a number

**2026-08-05, QA pass over the night's work.** Four entries from tonight concluded
that a dial was inert: CPU cadence, difficulty tiers, commitment frames, and
partly the stamina budget. The last entry of the night found the confound that
put all four in doubt. This is the re-measurement, and it is worse than "in
doubt": three of the four conclusions were artifacts, and correcting them hands
over the number Phase O has been missing since it was raised.

## What was wrong with the instrument

Every sweep compared **totals** — punches thrown, blocks, knockdowns, end
stamina — across bouts that all terminate on the three-knockdown rule. A bout
that ends sooner contains fewer of everything. So a dial that made fighters
slower also made bouts longer, and the total came out flat. The dial looked
disconnected precisely *because* it was connected.

`experiment_per_hand_guard.run_with` now records five things no earlier sweep
had: eligible landings (the knockdown denominator), tick of the first
knockdown, tick of the stoppage, total ticks run, and stamina sampled at fixed
wall-clock ticks rather than at the end. None of them draws from the LCG, so
the fight itself is bit-for-bit the fight it was.

## The tiers, re-measured

| tier | cadence | kd/eligible | ticks to 1st KD | ticks to stoppage | stamina @1200 |
|---|---|---|---|---|---|
| novice | 20 | 0.2905 | 1,696 | 4,734 | 56.7 |
| club | 14 | 0.2746 | 1,259 | 3,310 | 43.3 |
| contender | 10 | 0.2525 | 955 | 2,751 | 37.5 |
| champion | 6 | 0.2966 | 868 | 2,521 | 36.0 |

Time-to-stoppage spans **1.88×** across canon's own four tiers, and the stamina
curves separate cleanly and monotonically at every fixed tick. The earlier entry
said the tiers were "flat — the hypothesis is dead." The tiers were never flat.
What is genuinely flat is `kd/eligible`: the tier changes how *many* landings
happen, not how *dangerous* one is. That distinction was invisible in totals.

## Commitment, re-measured

| commitment | kd/eligible | ticks to 1st KD | ticks to stoppage | thrown/1k ticks | stamina @1200 |
|---|---|---|---|---|---|
| ×1.0 (canon) | 0.2654 | 794 | 2,335 | 43.8 | 33.6 |
| ×1.5 | 0.2837 | 1,220 | 3,132 | 32.6 | 42.5 |
| ×2.0 | 0.3029 | 1,534 | 3,877 | 25.7 | 51.4 |
| ×3.0 | 0.3082 | 2,354 | 5,090 | 18.4 | 66.1 |

Tripling commitment doubles the bout's length, halves throughput, and nearly
doubles stamina at a fixed tick. The earlier entry reported "8.7% fewer punches
thrown — not a connected dial either." It is one of the most connected dials in
the model. Note also that the *only* thing that barely moves, again, is
`kd/eligible`.

## The number Phase O was missing

Both dials move the clock; neither moves conversion. So the arithmetic closes
itself. A bout reaches the cards at 32,400 ticks. Pushed to the far corner —
novice cadence and triple commitment, well past anything canon authors — the
mean bout still ends at 7,049 ticks, **22% of the distance**. The gap is 4.6×,
larger than both dials multiplied together.

Stated as a rate instead of a duration: a full bout at canon's settings would
contain about **216 eligible landings**, and fewer than three of them may
convert if the fight is to be scored. That is a required conversion of **0.0139**
against a measured **0.2654** — a factor of **19.1×**. The most extreme clock
settings only shrink it to 6.6×.

**Phase O's held condition is a conversion problem, not a pacing problem.** Six
hypotheses died getting here — grading, CPU policy, tiers, cadence, commitment,
and the guard's hold cost — and every one of them died on the volume side of the
model, because that is the side I kept looking at. `kd_threshold`, the pressure
terms feeding it, and the condition erosion that inflates them are the surface
where the fix has to live.

## What was corrected in place

- `experiment_per_hand_guard.run_with` — five confound-free recordings added.
- `experiment_cpu_tiers`, `experiment_commitment_frames` — report rates and
  times; totals retained but explicitly marked non-comparable.
- `experiment_decision_path` — new; measures the distance to the cards and the
  conversion arithmetic above.
- Three development-log entries carry a supersession banner rather than an edit.
  The original reasoning stays readable; the correction sits beside it.

The one conclusion from tonight that survives untouched is the pressure
decomposition — stamina 2.74× against condition 1.17× — because it measured
per-event ratios and never compared a total to a total.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 03:10 UTC | END ] -->
