<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 13:10 UTC | Decision 0034 start ] -->
# Decision 0034 — The threshold is not the lever. Volume is.

**Status:** ACCEPTED (delegated).
**Authority:** The owner's standing in-session delegation, 2026-08-09: *"You
rule on them using the logic we have used throughout the project."*
**Gated on:** Decision 0033 Ruling 1, which said: land the knockdown-region
fix, run the sweep, and dispose of `pressure_threshold` as its own numbered
decision informed by the measured distribution. That sequence is complete.

## The ruling

**`pressure_threshold` stays at 0.57 and is NOT re-chosen.** The measurement
that was supposed to justify choosing a new one instead demonstrates that a
threshold cannot fix what is wrong, and choosing one now would encode today's
punch volume into canon — which is exactly the failure canon's own note warns
about, and would guarantee a third re-sweep.

## The evidence

Ten seeds per candidate, professional rules, default profiles, thirty-seed
confirmation population behind it. Threshold injected into the pack, never
written to canon — a harness may explore; only the contract may conclude.

| threshold | kd per capable contact | **kd per round** | stops | decisions | median end round |
|---|---|---|---|---|---|
| 5700 (current) | 0.736 | **21.00** | 2 | 8 | 12 |
| 7200 | 0.482 | **19.48** | 3 | 7 | 12 |
| 8700 | 0.180 | **15.28** | 7 | 3 | 9 |
| 10200 | 0.108 | **13.44** | 5 | 5 | 12 |
| 11700 | 0.070 | **9.90** | 4 | 6 | 12 |
| 13200 | 0.060 | **9.36** | 4 | 6 | 12 |

**A first pass measured knockdowns per FIGHT and was wrong** — that statistic
conflates the rate with the duration, because raising the threshold makes each
contact less likely to drop a man *and* makes fights last longer, and the two
cancel. It produced a flat, non-monotonic curve and would have supported the
conclusion that the threshold does nothing. Recorded here because the corrected
metric reverses the reading, and a measurement that would have misled is worth
keeping visible.

**Read correctly, the threshold works.** Knockdowns per capable contact falls
monotonically and by more than tenfold, 0.736 → 0.060. It is a well-behaved
control over exactly the thing it controls.

**And it cannot reach the problem.** Knockdowns per round only falls 21.0 →
9.4 across a 132% increase, and it plateaus. Even at the extreme, **9.4
knockdowns per round.** A championship fight has nought to three in twelve.

## Why: the arithmetic that ends the argument

At 13200 the per-contact rate is 0.060 — six percent of landed head punches
drop a man, which is not an unreasonable figure for boxing. Nine knockdowns a
round at six percent means **roughly 150 landed knockdown-capable punches per
round.** A real round contains fifteen to twenty-five landed punches in total.

The knockdown count is not a knockdown problem. It is the volume problem
wearing a knockdown's clothes, and it will remain at any threshold anyone
picks.

## What governs volume, all of it authored and none of it running

- **The guard does not exist in the fight.** `GUARD` sets `move_id = None`, so
  guarding costs nothing, and there is no guard stage in `_resolve_punches` at
  all. The ten postures, `posture_economy`, `guard_integrity` and
  `guard_extent_multiplier_while_committed` are authored and inert. **Nothing
  in this game stops a punch except an evasion**, and this is the project's own
  core design rule — *a guard is a body structure that protects some lanes
  while exposing others* — sitting unimplemented.
- **`punch_model.outcome_recovery` is unread**: whiffed ×1.5, dodged ×1.3,
  with counter windows. Missing costs the same as landing, so there is no
  price on throwing.
- **No chain window**, so no combination economy — and equally, no pause.
- **`posture_economy`'s hold costs and mobility multipliers** are unread, so
  no defensive structure costs anything to carry.

## Consequences for sequencing

1. `pressure_threshold` is **frozen at 0.57** until volume is governed. Any
   proposal to move it before then is refused on this record.
2. **The guard stage is promoted from post-First-Bell to the critical path.**
   It was ranked as the largest authored design not in the fight; it is now
   also the largest measured cause of an unwatchable one. It is the next block
   of work.
3. Decision 0033 Ruling 4 (the body knockdown) stays deferred behind the same
   gate, for the same reason: it changes the population, and the population is
   not yet worth measuring against.
4. When volume is governed, this decision's sweep is re-run and the threshold
   is disposed of then, on that population. Canon's criterion is unchanged and
   is canon's own: keep both result paths busy, keep a first-round knockout
   reachable, and let neither path go dead.

## What this decision does not claim

That 0.57 is correct — only that it is not the thing currently wrong, and that
choosing its replacement today would be fitting a number to a fight nobody
wants. Decision 0032 §3 holds: every figure above is a diagnostic.

The one number that did move for the better is worth stating plainly, because
it is the reason this question could be asked at all: under Decision 0033, 24
of 30 fights now reach the cards, with split decisions and draws among them,
and `decision_path_must_survive` survives for the first time.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 13:10 UTC | Decision 0034 end ] -->
