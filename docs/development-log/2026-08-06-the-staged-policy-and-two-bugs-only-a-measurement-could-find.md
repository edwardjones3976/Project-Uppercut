<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 10:00 UTC | START ] -->
# The staged policy, and two bugs only a measurement could find

**2026-08-06.** Decisions 0015 and 0016 are implemented in the Phase O contract.
The flat eleven-way draw is gone.

## What was there before

Five of eleven outcomes were a punch. Not five of eleven *when a punch was
available* — five of eleven, always, regardless of where the fighter stood, what
he could reach, or how much stamina he had left. It produced 175–219 punches per
fighter-round against a professional 55–78, and it could not miss on range,
because nothing it threw was ever illegal.

## What replaced it

    observe state -> intent -> opportunity -> action -> commit

`aggression_bias` is read at the **intent** stage and nowhere else, which is the
whole of Decision 0016. An intent to attack that finds no legal opportunity
produces an observation, not a punch into a band the move does not declare.

The opportunity stage asks two questions the round contract had never asked:
does a punch exist that declares **this band** (Rule 12), and can he afford it?
The defensive half branches on states canon already defines — below the
low-water mark he recovers, out of position he seeks the band his punches live
in, otherwise he works. Every decision emits a reason code.

Nothing in it is a new number. Tier `club` supplies aggression 0.45 and error
0.22; the bands come from the move table; the low-water mark is canon's
`low_threshold_fraction`.

## The measurement, in the order it happened

| | flat draw | staged v1 | + misjudgement | + Rule 12 at resolution |
|---|---|---|---|---|
| punches / fighter-round | 175–219 | 95.5 | 91.6 | **86.6** |
| connect rate | — | 59.3% | 55.7% | **49.7%** |
| **arrived** (landed or blocked) | — | 99.6% | 97.9% | **86.6%** |
| knockdowns per round | 22.89 | 17.64 | 15.65 | **13.43** |

Reference: professional volume 55–78, reference-simulator connect 42.4%.

## The two bugs, both invisible without the numbers

**Draft one made footwork inert.** The policy only stepped when the band was
*wrong*. Since both fighters start in mid and every mid-band punch keeps them
there, the wrong-band branch essentially never fired: **steps fell from 612 to
36 across three rounds, and band transitions to zero.** The fighters stood at
one separation all night — which is precisely the defect Phase Q was built to
fix, reintroduced by a policy that only moved when it was out of position.

A boxer moves inside his range as much as he moves to reach it. Footwork went
back into the non-offensive set unconditionally, and there is now a regression
test that fails if steps or transitions collapse again.

**Draft two could not miss.** With the band gate at the *opportunity* stage,
every punch thrown was legal, and a legal punch at a static mid separation
always reaches: **99.6% of everything thrown arrived.** That is not an accurate
fighter. It is a fighter with nothing left to miss.

Two things fixed it, and both are readings of canon rather than new numbers:

1. **`error_rate` is a misjudged distance.** The swap draws from every punch,
   not only the legal ones. A fighter who only ever mistakes one legal punch for
   another has not misjudged anything.
2. **Rule 12 applies at resolution, not only at selection.** A punch thrown from
   the wrong band travels its full arc into empty air and pays the whiff, *even
   when the geometry says the fist arrived* — which at mid range it almost
   always does. This is Phase Q's rule, folded into the round contract, and it
   is the first time the round has enforced it.

Arrival fell 99.6% → 86.6% and the connect rate from 59.3% to 49.7%, against the
reference's 42.4%.

## Where this leaves Phase O

Volume was 5.8× the reference and is now roughly 1.4×. Accuracy was the 1.3×
factor and is now about 1.17×. **Knockdowns per round went 22.89 → 13.43.**

What is left is lethality — the 2.3× factor, and the same conversion problem
measured on 2026-08-05 at 2.78×. Roughly 43 landings per fighter-round are
producing 13 knockdowns per round: about one knockdown per six and a half
landings, which no boxing match resembles.

**I have deliberately not touched it.** The pressure formula is Rule 14 canon,
`pressure_threshold` is explicitly "not in question" in the Phase O record, and
three separate attempts to blame the knockdown model have already been
overturned by the next measurement. Lethality is the next thing to investigate
and it should be investigated, not adjusted — and if it turns out to need a
canon change, that is a Director call and a decision record, not an edit.

## Note on what a policy is allowed to know

Every branch reads only observable state: its own stamina, its own band, the
move table. Nothing reads the opponent's private state, a future action, the
scorecards or the die. Decision 0016 says a policy that reads the die is not
difficulty, it is cheating, and it will read as cheating.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 10:00 UTC | END ] -->
