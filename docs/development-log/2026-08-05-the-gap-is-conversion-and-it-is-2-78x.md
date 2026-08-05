<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:30 UTC | START ] -->

# The gap is conversion, it is 2.78×, and the knockdowns themselves are identical

**2026-08-05.** The last entry ended on the one number nobody had: the reference
simulator's own conversion rate. Here it is, computed the same way as the
contract's, from each model's own published events, with no instrumentation added
to either.

## The number

| | eligible landings | converted | rate | bouts stopped |
|---|---|---|---|---|
| **contract** | 291 | 93 | **0.3196** | 24/24 |
| **reference** | 479 | 55 | **0.1148** | 4/24 |

**The contract converts an eligible landing into a knockdown 2.78× as often as
the model canon's 0.57 threshold was actually swept against.** That is the gap,
stated as a rate, on the artifact a C++ port has to reproduce — and it is the
first version of this number that does not come from a harness.

Note what it is *not*. The reference has **more** eligible landings per bout —
20.0 against 12.1 — and still reaches the cards in 20 of 24. The contract is not
producing more chances. It is converting the ones it has, harder.

Eligible landings per bout are context only and must not be read as a comparison:
the reference runs 120-second rounds, the contract 180-second rounds, and the
contract stops in round one every time. Conversion is a rate and survives that,
which is exactly why it is the metric here. The confound earlier today was making
that mistake.

## The same punch, twice as lethal

| move | contract | reference |
|---|---|---|
| cross_rear | 38/80 = **0.475** | 32/137 = **0.234** |
| jab_lead | 3/84 = 0.036 | 0/259 = 0.000 |
| hook_lead | 16/53 = 0.302 | — |
| uppercut_rear | 36/74 = 0.486 | — |
| overhand_rear | — | 23/83 = 0.277 |

`cross_rear` is the one move both models throw in quantity, and it converts
**2.03×** as often in the contract. The move mixes differ otherwise — the
reference throws an overhand the contract's five-move set does not have, and
never lands a knockdown jab in 259 eligible jabs where the contract manages three.

## And yet a knockdown looks the same in both

The two terms both models publish at the moment of a knockdown:

| | min | median | max |
|---|---|---|---|
| contract pressure | 0.5709 | **0.6863** | 1.3893 |
| reference pressure | 0.5711 | **0.6702** | 1.4420 |
| contract accumulated condition | 0.0148 | **0.0959** | 0.1891 |
| reference accumulated condition | 0.0521 | **0.1215** | 0.2141 |

Pressure at the moment of a knockdown is **almost identical** — medians 0.686
against 0.670 against a shared threshold of 0.570. The formula is not behaving
differently and the threshold is not mistuned. Something has to clear 0.57 in
both, and when it does it clears it by about the same margin.

The accumulated-condition term is the tell. **The contract's knockdowns arrive
with LESS accumulated damage than the reference's** — median 0.096 against 0.122,
and a minimum of 0.015 against 0.052. A contract fighter goes down earlier in his
own beating.

Since both reach the same pressure with *less* of the accumulated term, some
other multiplicand must be making up the difference. The contract publishes all
five in its `K` rows; the reference publishes only these two. From the contract
side alone we already know what those knockdowns look like: **median stamina 30.5%
and 97% landing on a defender caught inside his own commitment.**

So the honest shape of it: the contract's knockdowns are driven by *situational*
terms — how empty the man is, and whether his balance is set — where the
reference's are driven further by *accumulated punishment*. The contract drops
people who are tired and committed; the reference drops people who have been hit
enough.

## Where the evidence runs out, precisely

Confirming that needs the pressure terms of eligible landings that did **not**
convert, and those are not in either stream. The contract emits state on decision
ticks only, so 84% of eligible landings have no state row; the reference's
knockdown payload carries two terms and its non-knockdowns carry none.

That is a statement about the evidence, not a guess about the answer, and it is
the thing to fix before the next claim: **whatever measures this next has to
publish the terms of the landings that did nothing**, and it has to do so without
altering a pinned stream.

## What this does to the open gates

It does not close any of them, and it sharpens two.

**G1 (step cost) and G6 (guard lanes on the threshold)** are unaffected — canon
defects, no simulation involved.

**The stamina economy** is now implicated by contract evidence rather than harness
evidence for the first time: knockdowns cluster at 30.5% stamina, and the
contract converts hardest exactly where the reference does not. Whether the
economy is wrong or the pressure formula leans on it too heavily is still open.

**The three-knockdown rule (G5)** matters more than it did this morning. The
reference converts at 0.1148 and still stops 4 of 24 bouts under the same rule. A
2.78× conversion rate against that rule is what produces 24 of 24 — so G5 and the
conversion rate are the same problem seen from two ends, and deciding G5 changes
what "too high" even means.

Measured by `tools/engine/measure_conversion_gap.py`; figures in
`sandbox/Saved/conversion_gap.json`.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:30 UTC | END ] -->
