<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 08:00 UTC | START ] -->

# Phase Q — the fight gets a distance, four defects close, and Phase O does not

**2026-08-05.** The reference simulator reaches the cards in 20 of 24 bouts with
canon's own numbers; this core reaches them in 0 of 24, and the 16.7×
knockdowns-per-minute gap factorises into volume 5.8×, accuracy 1.3× and
lethality 2.3×. Two of those three were one omission — the core implements the
reference's *resolution* pipeline and skips its *range* pipeline. This builds the
range pipeline and measures exactly what it does and does not fix.

Every number is read from canon. Nothing here is a tuning proposal.

## What the core had been doing

Both fighters had stood at 0.90 reach units since Phase H. That single fact was
producing four separate defects that nobody had connected:

`step_in`, `step_out` and `step_lateral` sit in the action set, are chosen three
times in eleven, cost stamina, cost commitment — and moved nothing. That is the
declared-but-inert class this repository keeps a checker for, sitting in the
action set the entire time.

`uppercut_rear` is an inside-band punch thrown all night from mid range: 532
thrown, 0 landed, 28.8% of the entire punch stamina budget burned for nothing.

`hook_lead` is *also* an inside-band punch, and it had been **landing** from mid
range — the same defect wearing the opposite sign, and the reason the first one
looked like a reach bug rather than a missing rule.

And nothing missed. 99.9% of thrown punches reached the interception plane,
because with no distance the guard is the only thing between a punch and a body.

## The contract

`analyze_core_range.py`, Phase Q. Canon's five bands (clinch/inside/mid/outside/
out_of_range), its 0.05 ru hysteresis, the `boxing_steps` 0.22 ru stride drained
under the 0.14 ru per-tick displacement cap, the 0.28 ru separation floor, the
ring track with `rope_retreat_multiplier: 0.0`, and Rule 12: *"a punch thrown
from the wrong band travels its full arc into empty air and pays the whiff."*

Four properties are proven rather than asserted: footwork can change a band, the
uppercut becomes reachable by walking, hysteresis holds a band across a boundary,
and **running is finite** — with your back on the ropes a retreat buys nothing,
which is canon's own answer to the excessive-running abuse and turned out to
matter immediately.

Band and geometry are both required and they are different questions. The band is
what a boxer is trying to do from where he stands; the tip-versus-surface test is
the physical check that survived from Phase K. Where they disagreed, the
disagreement was information: the uppercut's 0.72 reach failing at 0.90 separation
was geometry agreeing with a band table nobody had consulted.

The range runner is a **strict superset**: with both switches off it reproduces
the Phase O fight exactly, on every counter, for every seed tested. That control
is a test, not a claim.

## What it does

| configuration | thrown/f-round | whiffs | connect | kd/min | gap | cards |
|---|---|---|---|---|---|---|
| neither (= Phase O) | 236.8 | 0 | 53.0% | 6.36 | 19.1× | 0/24 |
| Rule 12 gate only | 247.9 | 1,317 | 38.5% | 5.18 | 15.5× | 0/24 |
| footwork only | 269.5 | 0 | 20.1% | 3.29 | 9.9× | 0/24 |
| the phase, uniform coin | 274.3 | 7,015 | 8.7% | 2.19 | 6.6× | 0/24 |
| the phase, a band-aware fighter | 187.2 | 0 | 60.1% | 6.70 | 20.1× | 0/24 |
| + a boxer's cadence (20) | 108.9 | 0 | 54.8% | 3.89 | 11.7× | 0/24 |
| + a boxer's cadence (48) | 59.9 | 0 | 57.4% | 2.06 | 6.2× | 0/24 |
| *reference simulator* | *40.7* | — | *42.4%* | *0.38* | — | *20/24* |

The fight is now fought where boxing is fought: 47.9% inside, 46.9% mid, 2.6%
clinch, and **zero** ticks out of range. Every punch is thrown in its own band —
0.0% wasted, against 28.8% of the stamina budget wasted before. The uppercut is
thrown 413 times and is a real punch for the first time.

## What it does not do

**It does not close Phase O.** With a competent fighter the gap is 20.1×, which
is where it started.

That deserves to be said carefully, because the intermediate rows are a trap I
nearly fell into. The gate alone gets 15.5×, footwork alone 9.9×, both with a
uniform coin 6.6× — and all of that improvement is bought by fighters *missing
more*. A coin with a range model drifts out of position and throws 7,015 punches
into empty air. That is not a better model; it is a worse fighter, and reading it
as progress would be the same mistake as measuring bout totals against a bout
that ends on a knockdown count. An improvement that comes from making fighters
worse is not an improvement.

Give the fighter the reference's own policy discipline — throw only what the band
permits, and walk toward a band that permits something — and the gap comes
straight back.

## Where the residual actually is

Against the reference at the closest honest configuration (range, a band-aware
fighter, a boxer's cadence): volume 1.47×, accuracy 1.35×, and knockdowns per
minute 5.4× — leaving a **2.7× lethality residual**, unchanged and unexplained by
anything in this phase. That is the stamina term, for the third independent time
tonight (2.17× floor-to-median, 2.74× median pressure inflation, 2.3× per landed
punch against the reference).

So the factorisation held up exactly. Range was two of the three factors and it
has now delivered two of the three. The remaining accuracy sliver (1.35×) is the
sweep and evasion stages, which this phase deliberately did not take on. The
lethality factor is the stamina economy and it was never a range problem.

## For the Director

Phase Q is worth having on its own terms regardless of Phase O: it closes four
real defects, it makes the CPU policy load-bearing for the first time (with no
distance, no policy could matter — which is why the difficulty tiers measured
flat), and it does it with zero new coefficients.

What it also does is make the remaining question small and specific. Two things
are left between this core and a fight that reaches the cards: the evasion stage
(`slip_lead` and `roll_under` are in the move table; `slip_lead` is in the action
set and is not even loaded into the core's move set), and the stamina economy's
2.7× lethality. Neither is a range problem and neither should be guessed at.

The C++ core reads none of this yet. The contract, its 17 tests and the
measurement are the deliverable here; the implementation follows the same
analyzer-first order every phase has.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 08:00 UTC | END ] -->
