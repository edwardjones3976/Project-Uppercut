<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:45 UTC | START ] -->

# The contract's own numbers — re-taken, and two of them are new

**2026-08-05.** Everything quantitative published earlier today came from a
harness and was withdrawn. This re-takes the conversion measurement on the Phase
O contract itself, by reading the stream a C++ port has to reproduce rather than
by instrumenting it. No hook was added and no byte of the stream changed.

## What the stream can support, established by failing first

The first version of this measurement reconstructed the defender's condition and
stamina from the nearest earlier `C` and `D` rows. It produced accumulated
condition of 0.0347 where the analyzer's own knockdown row said 0.0545 — stale by
exactly the damage the landing itself had just done.

It was caught by its own self-check, which compared the reconstruction against
the contract's `K` rows and **refused to print a table when 11 of 11 disagreed**.
That check was the only reason this entry is not another plausible wrong table.

The cause is a property of the evidence stream worth recording: **`C` and `D`
rows are emitted on decision ticks only** — 456 of a round's 10,800. Only 15.8%
of eligible landings happen on a tick that carries state. So the terms of a
landing that did *not* convert are simply not in the stream, and recovering them
would mean either changing pinned evidence or building another harness.

What the stream does carry: every eligible landing (a `P` row names move, result,
region and contact class), and the complete pressure decomposition for every
landing that *did* convert, already computed, in the `K` rows.

## The contract's conversion rate

24 seeds × 3 rounds: **291 eligible landings, 93 converted — 0.3196.**

The harness said 0.2654. So the conversion problem is real on the contract too,
and slightly worse. Phase O remains held: 24 of 24 bouts stopped, all in round
one.

## New finding: the punches sort themselves correctly

| move | eligible | converted | rate |
|---|---|---|---|
| jab_lead | 84 | 3 | **0.036** |
| hook_lead | 53 | 16 | 0.302 |
| cross_rear | 80 | 38 | 0.475 |
| uppercut_rear | 74 | 36 | **0.487** |
| body_straight_rear | 0 | 0 | — |

**The jab converts at 3.6% and the uppercut at 48.7%** — a factor of fourteen.
That is boxing: a jab is not a knockdown punch and the uppercut is the most
dangerous thing in the set. Nothing authored that ordering; it falls out of
`impact` running through the pressure product.

It is also the exact opposite of what the harness said. In the harness the jab
was the single largest source of knockdown-eligible landings, because with no
range gate and nothing missing, volume was everything. The contract's ordering is
the one worth trusting, and it is a point in the model's favour that nobody had
looked for.

## New finding: commitment is nearly universal among knockdowns

**90 of 93 knockdowns — 97% — land on a defender caught inside his own
commitment.** Canon's `caught_committed_multiplier` is 1.25 against a balanced
1.0, so this is not a large multiplier doing the work; it is that a fighter is
almost never dropped while his balance is set.

That gives the Director's per-hand mechanic a second justification measured on
the contract rather than the harness: what a fighter does with his own hands
decides almost every knockdown in the model, and the 3 of 93 that landed on a
balanced defender are the exceptions worth looking at when tuning resumes.

## What survives from this morning

The stamina story. **The median knockdown lands on a fighter at 30.5% stamina**,
with the stamina fraction across all 93 running from 0.0 to 0.71. That is the one
quantitative claim from earlier today that re-measures cleanly on the contract —
though note it is now a statement about the knockdowns that happened, not the
comparative decomposition the harness supported.

The condition term spans 12.8× across knockdowns (0.015 to 0.189) while balance
spans 1.25× and guard 1.08×. Two terms carry the variation, three barely move.

## What is still not known

Whether conversion is too high, and against what. The reference simulator reaches
the cards in 20 of 24 bouts; this contract stops 24 of 24. Comparing them
properly needs the reference's eligible-landing count, which its event log does
carry, and that is the next measurement rather than a conclusion here.

Measured by `tools/engine/measure_contract_conversion.py`; figures in
`sandbox/Saved/contract_conversion.json`.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:45 UTC | END ] -->
