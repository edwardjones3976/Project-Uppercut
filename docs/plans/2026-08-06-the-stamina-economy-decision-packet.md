<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 11:10 UTC | START ] -->

# Decision packet — the stamina economy cannot pay for a round of boxing

**For the Director. Opens gate G7.**
**Date:** 2026-08-06
**Status:** open, evidence complete, no canon changed

## The one-line question

Canon's stamina pool, regeneration rate and punch costs together pay for **19
punches in a round**. A professional round is **55–78**. Which of those three
numbers is wrong?

## Why this is being asked now, and not a week ago

It could not be asked before. Until 2026-08-06 the core threw 175–219 punches a
round from a flat draw and the stoppage rule ended most bouts in round one, so
"the fighters are exhausted" was indistinguishable from "the fighters are doing
something no boxer does." Decisions 0015, 0016 and 0018 removed both confounds:
volume is now 87 per fighter-round and bouts run to the cards.

With those fixed, the residual is measurable and it is not where three previous
investigations looked.

## The arithmetic, which is not an opinion

    stamina pool                        100.0
    idle regeneration                   0.004 per tick
    round length                       10,800 ticks
    a whole round of pure resting        43.2   (43% of the pool)
    mean punch cost                       2.26

    punches a full round of resting pays for    19.1
    professional volume                         55-78
    ------------------------------------------------
    shortfall                                   2.9x  (4.1x at 78)

That is before a single step, guard hold or slip is paid for, and before the
fighter does anything but stand still.

## What it produces, measured on the contract

Eight bouts, three rounds, professional rules, tier club:

**Fighters live on the floor.** Median stamina by minute of round time, both
fighters: 34% in the opening minute, then **1% for the rest of every round**,
recovering to roughly a third at the bell and collapsing again inside a minute.

**Rule 14 then multiplies that.** The pressure product's five terms, compared
between the eligible landings that did NOT fire (233) and those that did (263),
six bouts of three rounds:

| term | median ratio | mean ratio | discriminates? |
|---|---|---|---|
| force | 1.267× | 1.380× | **yes** |
| baseline + accumulated | 1.024× | 1.029× | no |
| 1.4 − stamina fraction | 1.400× | 1.285× | **yes** |
| balance | 1.000× | 0.970× | no |
| guard | 1.003× | 1.002× | no |

**Two terms decide a knockdown and three do not.** A knockdown here is a hard
punch landing on a tired man — force and stamina contribute about equally, and
balance, guard and accumulated damage contribute nothing measurable.

At a fighter on the floor the stamina term reaches 14000 against a fresh
fighter's 4000: a **3.5× multiplier on every punch he takes**, and the fighters
are on the floor for eleven of every twelve minutes.

Conversion is **53.1%** of eligible landings, against the reference simulator's
11.5%.

### A second finding, smaller and worth its own look later

**Accumulated damage moves the pressure by 2%.** `baseline + accumulated` runs
6408 at a landing that does not fire and 6563 at one that does. In boxing, late
knockdowns come from accumulation — a man breaks down because of what he has
already taken. Here he does not: every knockdown is effectively a single-punch
event, because `undamaged_baseline` dominates whatever damage has been done.

That is not part of G7 and should not be bundled into it. It is recorded here so
it is not rediscovered as a surprise.

### A correction, made before anyone quotes the earlier draft

The first version of this packet said **only** stamina discriminates. That was
an artefact: at eight bouts the median force happened to be identical (7124) on
both sides of the threshold, and a test written against the claim failed on a
different sample within the hour. Force discriminates and always did. The
diagnosis below is unaffected — the pathological term is still stamina, because
force at 1.27× is a punch being a harder punch, which is correct behaviour,
while stamina at 1.40× is a fighter who has been on the floor since minute one.

## The conclusion, stated carefully

**The knockdown model is not mistuned. It is faithfully multiplying an
exhaustion the stamina economy makes inevitable.**

This is the fourth time an investigation has arrived at the knockdown model and
the fourth time it has been sent away. `pressure_threshold` at 0.57 is doing
exactly what it is authored to do; a fighter at 1% stamina *should* be easier to
put down, and that is the model working.

What no boxer does is spend eleven of every twelve minutes at 1% stamina.

## Three ways out, with consequences

**1. Regeneration is too low.** `regen_per_tick_idle` 0.004 → about 0.012 would
pay for roughly 57 punches a round.
*Consequence:* the cheapest change and the least defensible on its own — it
makes a resting fighter recover 130% of the pool per round, so stamina stops
being a resource anywhere and patient boxing stops being a strategy. Rule: the
pool exists to make patience pay.

**2. Punch costs are too high.** Mean 2.26 → about 0.78 makes professional
volume affordable on a round's regeneration.
*Consequence:* every impact number in the game moves with it, because
`delivered_impact` is derived from what a punch **cost to throw** — that is how
this project avoids a per-move power field. Changing costs re-tunes damage. The
relationship would need to be re-derived, not just rescaled.

**3. The pool is not a per-round budget and was never meant to be.** If 100 is a
whole-fight reserve, a fighter *should* be depleted by round three, and what is
wrong is the expectation that a round's work is recoverable within a round.
*Consequence:* the most interesting and the most work. It implies a second,
faster resource — wind, or a per-round allowance — with the deep pool draining
slowly beneath it. Two-tier stamina is how boxing actually feels: you get your
breath back between rounds, you do not get your legs back in round ten. It also
explains why `between_rounds_recovery_fraction` is 0.35 rather than 1.0.

## Recommendation

**3, then re-measure, then consider 2.** Option 3 is the only one that explains
all three observations at once — the depletion, the 0.35 between-rounds
fraction, and the fact that stamina is the only term that discriminates at a
knockdown. Options 1 and 2 make the number go away without saying what the
number is.

Whichever is chosen, the consequence is the same shape as Decision 0014's: every
measurement taken before it must be **re-run rather than re-read**, and the
Phase O golden will move.

## What has deliberately not been done

No canon value has been changed. `pressure_threshold`, the pressure terms, the
punch costs and the regeneration rates are exactly as they were. The evidence is
`tools/engine/measure_lethality_after_policy.py` and re-runnable in about forty
seconds.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 11:10 UTC | END ] -->
