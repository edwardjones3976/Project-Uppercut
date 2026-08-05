<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 12:50 UTC | START ] -->

# Phase S — nobody can react to a jab, and a third canon quantity that cannot work

**2026-08-05.** Everything measured after Phase R was measuring a fighter who acts
on nearly every tick he is free: ~180 stamina-charging actions per round against
an economy that refills 10.6. That was never a stamina model. The core has never
had a policy — it draws uniformly from a pool containing `idle` once — while canon
authors one in full and the core reads none of it. This executes canon's policy.

## The win: a fact of boxing nobody wrote

Canon authors a decision interval of 4 ticks, a hard reaction floor of 6 ticks at
every difficulty, and per-tier reaction times of 6 to 20. **The decision interval
is how often a fighter thinks; `reaction_ticks` is how long he needs to respond to
something he has seen.** They are different numbers in canon and the core had been
treating the first as if it were both.

Put that distinction against the move table and this falls out:

| punch | startup | who can react |
|---|---|---|
| jab_lead | 4 | **nobody** |
| hook_lead | 7 | champion |
| cross_rear | 8 | champion |
| body_straight_rear | 9 | champion |
| uppercut_rear | 10 | contender, champion |

**No fighter at any difficulty can react to a jab.** It has to be anticipated or
eaten — which is what a jab *is*. Only a champion answers a cross. Nobody authored
that; it is two numbers meeting a move table, the same shape as Phase R's
telegraph falling out of timing. There is a test on it now, so if a later edit
ever makes the jab reactable, the test says so.

It also means **Phase R's evasion measurement was illegal**. Its reactive slip
fired on the tick a punch entered startup — an instant response, which canon's
prohibition list forbids outright: *react faster than the reaction floor at any
difficulty, at any time*. Phase R's evasion numbers are an upper bound on what a
legal fighter could achieve, not a measurement of one. The correction is recorded
here rather than edited into Phase R, so the mistake stays visible.

And difficulty is finally a difficulty *of* something. It was never inert — with
no distance, no evasion and no policy, a reaction time and an aggression bias had
nothing to change.

## The loss: canon's aggression cannot produce a boxer

Executing the tiers at canon's own numbers:

| tier | thrown/f-round | connect | drain %/min | cards |
|---|---|---|---|---|
| novice | 174.7 | 60.0% | 115.6 | 0/24 |
| club | 196.2 | 59.3% | 100.0 | 0/24 |
| contender | 219.2 | 60.2% | 120.7 | 0/24 |
| champion | 217.7 | 59.8% | 117.4 | 0/24 |
| *reference* | *41.4* | *42.4%* | *11.1* | *20/24* |

Four to five times a professional work rate. Reading the tier's `reaction_ticks`
as its decision interval instead gives 108–201 — still two to five times over. And
sweeping aggression at canon's 4-tick interval shows what would actually be
needed: **0.05 gives 47.1 thrown per round**, inside the professional band, against
canon's lowest authored value of **0.35**. A factor of seven.

That is the third canon quantity tonight that cannot work as authored, and like
the other two it was written against a system nobody had built yet. It goes beside
them rather than being quietly fixed here.

## One implementation bug, caught by the measurement

The first version implemented `error_rate` by redrawing from every action at once.
At the club tier's 0.22 that put roughly a tenth of *all* decisions into a punch
regardless of aggression, so dropping aggression from 0.35 to 0.005 moved the
throw rate only from 218 to 148. An error that overrides the fighter's own
aggression is not an error; it is a second aggression dial wearing the wrong name.
Corrected to swap within the chosen class — an intended punch becomes a different
punch, an intended non-punch a different non-punch — after which the sweep is
monotone. Rule 4 constrains this: difficulty may never touch damage, stamina,
contact classification or anything else, so an error can only ever be a different
*choice*.

## What is actually left, and it is not what I thought

Even at a professional throw rate (aggression 0.05, 47.1 per round) the drain is
93.3%/min and 0/24 reach the cards. The spend is not the punches. In this action
model **almost every action costs stamina and there is no authored weighting for
doing nothing**: of the non-offensive choices, four of six are steps or slips that
charge, and `idle` is one option among them. A fighter takes a full 0.22 ru stride
at essentially every decision he does not punch on — well over a thousand strides
per round, against a real boxer's couple of hundred.

So the stamina economy's problem, finally stated correctly, is **action count**,
not action price and not recovery. Three separate canon quantities feed it and
each is now a Director call.

## The three, together, for the Director

**The step-cost contradiction.** `movement_model.locomotion` prices a step at
0.132; the move table prices it at 0.600. 4.55× apart for the same 0.22 ru stride,
and the core reads the higher one.

**`aggression_bias` is roughly 7× too high** to produce a professional work rate
under either reading of the decision clock.

**Nothing authors "do nothing."** `threat_compression` changes stride *mode*, not
whether a stride happens. The reference's fighters have profile pacing and idle
behaviour; canon's tier model has an aggression bias and no rest bias, so a
fighter who is not punching is always doing something else that costs.

I have not picked a number for any of the three. Each is a quantity authored
against a model that did not exist when it was written, and the pattern tonight
has been that guessing at one of those produces a measurement that looks like
progress and is not.

641 tests pass. No canon edited, no coefficient added, no die drawn.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 12:50 UTC | END ] -->
