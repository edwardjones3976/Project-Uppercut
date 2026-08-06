<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 11:45 UTC | START ] -->
# The fourth time the knockdown model was innocent

**2026-08-06.** With volume and accuracy fixed, lethality was the only factor
left. It was investigated rather than adjusted, and it is not where it looked.

## The arithmetic that ends the argument

    stamina pool                        100.0
    idle regeneration                   0.004 per tick
    round length                       10,800 ticks
    ------------------------------------------------
    a whole round of pure resting        43.2   (43% of the pool)
    mean punch cost                       2.26
    punches a round of resting pays for  19.1
    professional volume                  55-78
    shortfall                             2.9x   (4.1x at 78)

Nineteen punches. That is before a step, a guard hold or a slip, and before the
fighter does anything but stand still.

The measured consequence: fighters hold **1% of the pool for eleven of every
twelve minutes**, starting each round at about a third after the between-rounds
recovery and back on the floor inside a minute.

## What Rule 14 does with that

Comparing the 233 eligible landings that did not fire against the 263 that did,
across six bouts of three rounds:

| term | median ratio | mean ratio | discriminates? |
|---|---|---|---|
| force | 1.267× | 1.380× | **yes** |
| baseline + accumulated | 1.024× | 1.029× | no |
| 1.4 − stamina fraction | 1.400× | 1.285× | **yes** |
| balance | 1.000× | 0.970× | no |
| guard | 1.003× | 1.002× | no |

A knockdown in this core is **a hard punch landing on a tired man**. Force being
a discriminator is a hard punch being a hard punch — correct. Stamina being one
is a fighter who has been exhausted since minute one, and at 1% of the pool the
term hits 14000 against a fresh fighter's 4000: a 3.5× multiplier on every punch
he takes.

**The knockdown model is not mistuned. It is faithfully multiplying an
exhaustion the stamina economy makes inevitable.** Fourth investigation, fourth
time the pressure formula has been cleared. `pressure_threshold` at 0.57 is
doing exactly what it is authored to do.

## Gate G7 is open, and nothing was changed

`docs/plans/2026-08-06-the-stamina-economy-decision-packet.md` sets out three
resolutions — raise regeneration, lower punch costs, or accept that the pool is
a whole-fight reserve and add a faster per-round resource beneath it — each with
its consequence. My recommendation is the third, because it is the only one that
explains the depletion, the 0.35 between-rounds fraction, and why stamina
discriminates, all at once. The other two make the number go away without saying
what the number is.

No canon value was touched. The evidence re-runs in about forty seconds.

## Two things caught by writing the tests

**An overclaim, inside the hour.** The first draft of the packet said *only*
stamina discriminates. At eight bouts the median force was identical on both
sides of the threshold — 7124 against 7124 — and I wrote the claim from it. The
test written to pin that claim failed on a six-bout sample immediately: force
discriminates at 1.27×, and always did. The packet carries the correction rather
than a quiet edit, because a reader who saw the first version deserves to know
which of the two is measured.

**A hundredfold arithmetic error, caught by a sanity check.** The first version
of the budget divided a per-tick rate that was already in fixed point, and
reported that a round of resting regenerates *43 of 1,000,000 units* — a
shortfall of 300×, which would have been a spectacular false alarm. The fix is
one line and the comment explaining it is four, because the next person to touch
that file will be tempted to divide again.

## A smaller finding, recorded so it is not rediscovered

**Accumulated damage moves the pressure by 2%.** 6408 at a landing that does not
fire, 6563 at one that does. In boxing a man breaks down from what he has
already absorbed; here every knockdown is effectively a single-punch event,
because `undamaged_baseline` dominates whatever damage has been done.

That is not part of G7 and should not be bundled into it — but it means the
body-work strategy this project cares about has no mechanical payoff at the
knockdown, whatever it does to stamina.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 11:45 UTC | END ] -->
