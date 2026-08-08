<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:40 UTC | START ] -->
# The first round the policy ever ran

`tools/engine/probe_policy_stamina.py`, seed 4242, one 180-second round, both
fighters driven by `tools/uppercut_integrated/policy.py` and charged by the
proven `tools/uppercut_stamina/economy.py`.

**Status of everything below: diagnostic.** Ruling R5 holds. No canon value
changed, no pin written, no hash taken, `values_are_fitted` still false. A
harness may explore; only the contract may conclude.

## What happened

Both fighters fall from a full pool to about 25% Wind inside fifteen seconds
and stay pinned there for the remaining 165. Each throws 33 punches. Neither
enters the declared ordinary band (45-85%) at any point after the twelfth
second, and neither leaves the burst band (15-35%) after the fifteenth.

The Wind ledger for fighter 0, which closes exactly to his reported end state:

| action family | ticks | net Wind | per tick |
|---|---:|---:|---:|
| `move` | 1,004 | -84.34 | -0.08400 |
| `attack` | 33 | -19.64 | -0.59515 |
| `observe` | 429 | +1.46 | +0.00340 |
| `hold_position` | 9,334 | +27.07 | +0.00290 |

`rest` does not appear because it was never chosen.

## F1 - the units error, a third time, and this one was mine

The first version of `stride_ru()` read `locomotion.modes[0].stride_length_ru`
- 0.55, `free_navigation` - and charged the economy that distance every tick.
A stride is the length of a *step*. `locomotion.max_frame_displacement_ru` is
0.14 and its own note calls it "a hard per-tick displacement cap below every
stride", so the probe was moving a fighter 3.9x faster than canon permits per
frame and billing him for all of it.

Fixed before any number was quoted; every figure in this document and on the
readiness board is from the corrected run. The function is now
`displacement_per_tick_ru()`, it names the mode rather than indexing it, and it
refuses rather than guessing if either number is absent.

**The finding that outlives the fix: the repo's units guard is one-sided.**
`economy_pack()` multiplies every *recovery* rate by the round length and fails
if one could refill the pool - the guard that caught this error on 2026-08-03
and again on 2026-08-07. Nothing multiplies a *drain* rate by the round length.
A per-step distance billed per tick therefore passed every gate in the
repository, including the one written specifically to catch this class of
mistake. Both earlier instances were on the recovery side, which is exactly why
the guard grew there and only there.

## F2 - `rest` was chosen zero times in a 180-second round

Recovery was the decision on 9,317 of 10,800 ticks and not one of them was
`rest`. Policy branch 7 rests only at `outside`/`out_of_range` and holds
position otherwise, which is correct boxing - you do not stand and breathe with
a man in front of you.

The gap is that **no branch anywhere converts "I need air" into "make room."**
There is a reason code for leaving a bad range (`EXIT_BAD_RANGE`) and none for
leaving to breathe. Every recovery tick therefore paid `hold_position`'s
0.0030/tick instead of `rest`'s 0.0060 - exactly half - and the fighter spent
165 seconds choosing recovery and receiving the second-best rate for it.

Caveat held open rather than rounded away: this probe's range model is a
declared stand-in in which both fighters share one band value, which makes
separation harder than a real range subsystem would. **The missing branch is
real either way; its magnitude here is not evidence.**

The boxing answer - circle out, tie up, clinch - is also the answer to "what
does a tired fighter do", so this is not a small omission. It is proposed, not
implemented: adding a behaviour branch on the strength of a diagnostic whose
own units defect was fixed the same hour is the mistake this project keeps
writing guards against.

## F3 - movement costs fourteen seconds of rest per second of footwork

At the declared per-tick cap, footwork costs 0.084 Wind/tick against rest's
best 0.0059. A fighter who rested every tick of a round would bank 63.7 Wind;
with a full starting pool that is about 32 seconds of footwork inside a
180-second round. A boxer is on his feet for all three minutes.

Not tuned. R5 forbids stamina tuning until the observable policy produces
plausible cadence, and these are Director values. This is the first evidence
that could inform that call rather than a request to make it.

## The design question this raised

Decision 0022 names RNG substreams by **subsystem**, not by fighter. With two
fighters both drawing from `policy_intent`, fighter A's decision count shifts
fighter B's draws - the same class of coupling 0022 forbids *between*
subsystems, reappearing *within* one. This probe used a fixed
fighter-0-then-fighter-1 order as a declared diagnostic choice.

The integrated bout needs a ruling: per-subsystem streams, or
per-subsystem-per-fighter. Raising it while the only cost is a naming rule is
cheaper than discovering it when a knockdown at tick 8421 moves because the
other man threw one more jab.

## Note on the tags in `probe_policy_stamina.py`

Its first draft carried UTC stamps of 08:40 and 09:40 that were guessed rather
than read, and the real time was 07:35. The file had never been committed, so
they were corrected in place rather than superseded. The convention says to get
the time from `date -u`; that is not decoration, and this is the entry that
says so.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:40 UTC | END ] -->
