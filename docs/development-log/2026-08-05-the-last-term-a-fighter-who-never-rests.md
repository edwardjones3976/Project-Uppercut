<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 10:20 UTC | START ] -->

# The last term — a fighter who never rests, and one state driving three of five

**2026-08-05.** Volume was range and accuracy was evasion; both are delivered. At
`react 6, aggression 0.30` the core throws 51.8 punches per fighter per round
against the reference's 40.7 and connects 45.7% against 42.4%, and still drops men
6.3× as often. Dividing out volume and accuracy leaves a 4.6× lethality residual.
This is that residual, measured on the fight that now exists rather than on the
distance-less one every earlier pass was reading.

## Which term

Decomposing canon's pressure product at every eligible landing, Phase O against
Phase R, on the same 24 seeds:

| term | Phase O | Phase R | change | what moved |
|---|---|---|---|---|
| force | 0.5624 | 0.6186 | 1.10× | the punch mix |
| condition | 0.6154 | 0.5967 | 0.97× | damage at the moment of landing |
| **stamina** | **0.8880** | **1.1500** | **1.30×** | how empty the man being hit is |
| balance | 1.2500 | 1.2500 | 1.00× | how often he is caught committed |
| guard | 1.1575 | 1.1575 | 1.00× | how open the lane is |
| pressure | 0.4231 | 0.6078 | 1.44× | |

The four multiplicands multiply to 1.38× against a median pressure move of 1.44×,
so the decomposition is complete. It is stamina, again — for the fourth
independent time tonight, and now *worse*, because footwork and evasion cost
stamina that nothing charged for before.

Conversion per eligible landing went from 0.2654 to **0.5789**: half as many
eligible landings, the same 99 knockdowns. The force term's 1.10× is real and it
is *correct behaviour* — `uppercut_rear` is now 31.6% of all eligible landings,
having been 0.0% in every measurement taken before range existed, and it is the
highest-impact move in the set. The model finally throws its best punch and the
knockdown model cannot absorb it.

## The rate, which is the comparison that matters

| tick | 600 | 1,200 | 1,800 | 2,400 | 3,600 |
|---|---|---|---|---|---|
| stamina | 73.2 | 47.9 | 27.7 | 13.1 | **4.8** |

**Our fighters are at 4.8% after one minute.** The reference simulator ends a
*six*-minute bout between 29.5 and 49.6. As a rate: we spend 95.2% of the pool per
minute against the reference's 8.4–11.8%. **We drain 8.1× to 11.3× faster than the
model canon's threshold was actually swept against.** A round is 180 seconds. Our
fighters are empty before the first bell.

That is the 4.6× lethality residual, and it is not a knockdown-model problem at
all. Canon's pressure formula multiplies an empty man's vulnerability by up to
3.5×, and it is being handed a fighter who is empty essentially always.

## And the mechanism is not the costs

Canon charges the posture hold and pays the idle regen in the *same branch*, and a
committed fighter is in neither. So the regen a fighter actually receives is the
authored rate times the fraction of the bout he is free. Measured:

    committed   223,989 ticks   74.9%
    free         75,203 ticks   25.1%

Per round, at canon's own rates and this fight's free share:

    regen if never committed        43.2
    regen actually received         10.9      (10.9% of the pool)
    guard hold actually paid         2.7
    net refill                       8.1      against a pool of 100

Punching alone spends roughly 104 per round. A fighter cannot break even at any
work rate; he empties in one round regardless. **The pool is not being drained by
costs that are too high — it is being drained because it almost never refills.**

## The structural observation

The fighter who is always committed is the same fighter whose guard is always
degraded (`committed_defense` multiplies his coverage) and whose balance term
always reads "caught" (`caught_committed_multiplier`). **One state variable is
driving three of the five pressure multiplicands**, and it is the one this core
sits in three-quarters of the time.

That is why every dial measured flat all night. Cadence, commitment, tiers, the
hold cost — each was a different handle on the same lever, and the lever was
always "how much of the bout is a fighter committed for."

## For the Director

The question is now one question, and it is a design question rather than a
tuning one: **should a fighter regenerate only while free?**

Canon's branch says yes, and there is a real argument for it — you are not
recovering mid-punch. But it interacts with commitment frames in a way nobody
priced: at authored frame counts and any real work rate, "free" is a quarter of
the bout, so the authored regen rate is a fiction and the real one is a quarter of
it. Three candidate answers, all canon-faithful, none of which I am picking:

Regen accrues always, at a reduced rate while committed — recovery continues, just
worse, which is what conditioning actually is.

Regen stays free-only and the authored rate is raised to what a fighter actually
receives — the same fiction, made honest, and the number becomes tunable against
the reference's 8–12% per minute.

Commitment frames come down so "free" is a larger share — but Phase Q measured
commitment as a genuine 2.18× lever on bout length, so this trades one problem for
a different one and should be the last resort rather than the first.

I would not touch `pressure_threshold`, the pressure terms, or the knockdown rule.
Nothing measured tonight suggests any of them is wrong, and three separate
attempts to blame them were each overturned by the next measurement.

628 tests pass. No canon edited, no coefficient added, no die drawn.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 10:20 UTC | END ] -->
