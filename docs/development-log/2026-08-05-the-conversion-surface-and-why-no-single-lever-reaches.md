<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 04:20 UTC | START ] -->

# The conversion surface — what is actually dropping fighters, and why no single lever reaches

**2026-08-05.** Phase O is held on conversion: a bout needs 0.0139 knockdowns per
eligible landing to reach the cards and the model produces 0.2654. This takes the
pressure product apart term by term to find where that comes from, before anybody
proposes a number.

Canon's Rule 14 is one product of five multiplicands, and each has a floor and a
ceiling canon itself sets, so "which term is doing the work" is answerable exactly:

    p = force x (baseline + accumulated) x (1.4 - stamina_frac) x balance x guard

The decomposition is a deliberate **re-derivation** rather than a refactor of
`analyze_core_round.pressure` — the analyzer's expression is pinned evidence and
must not be reshaped to make a measurement convenient. Every decomposed row is
asserted equal to the analyzer's own result, so a drift between them is a crash
rather than a quietly wrong table.

## What each term actually ranges over

Across 373 eligible landings in the 24-seed sweep:

| term | min | median | max | span |
|---|---|---|---|---|
| force | 0.3375 | 0.5624 | 0.8249 | 2.44× |
| condition | 0.5581 | 0.6154 | 0.7342 | 1.32× |
| **stamina** | **0.4101** | **0.8880** | **1.4000** | **3.41×** |
| balance | 1.0000 | 1.2500 | 1.2500 | 1.25× |
| guard | 1.1505 | 1.1575 | 1.2345 | 1.07× |
| pressure | 0.1110 | 0.4231 | 1.1262 | — |

Three of the five barely move. Balance sits at the caught-committed multiplier
almost always, guard varies by 7% across the whole sweep, and condition — the
term the accumulation model exists to feed — swings only 1.32×. The one that moves is
stamina, and it swings furthest of all.

## The counterfactual

Pin one term at its most favourable observed value and re-decide every landing.
This is a **replay**, not a re-simulation: the landings are the real fight's, so
no bout gets longer or shorter and nothing is normalised by its own outcome — the
mistake that cost four conclusions earlier tonight.

| pinned | converts | rate |
|---|---|---|
| nothing (canon) | 99 | 0.2654 |
| force | 0 | 0.0000 |
| condition | 67 | 0.1796 |
| **stamina** | **0** | **0.0000** |
| balance | 48 | 0.1287 |
| guard | 91 | 0.2440 |

**A fighter who never tires is never knocked down in this sweep.** Not once in 373
eligible landings. Force collapses too, but that pin is degenerate — it makes
every punch the weakest move in the set, which is not a counterfactual anybody
would ship. Stamina's pin is a real design position, and it is the one the
Director's open question is actually about.

So men are not being dropped by punches. They are being dropped because they are
already empty when the punch lands. That converges from a second direction on the
earlier pressure decomposition (stamina 2.74× median inflation against condition's
1.17×), measured a different way and agreeing.

## The threshold cannot fix it

For the decision path to survive, `pressure_threshold` would have to sit at
**1.0268** — 1.80× canon's 0.57, above the 99th percentile of observed pressure
and near the observed ceiling of 1.1262. That is not a higher bar. That is
knockdowns switched off. Canon's 0.57 is not the defect.

## And neither does the economy, alone

If the stamina economy is the surface, how far would it have to move? Punch costs
scaled down, re-simulated, each row carrying its **own** required conversion —
because slowing the fight changes how many eligible landings a full bout would
contain, and a single fixed target would be the confound creeping back in:

| punch cost | kd/eligible | needed | gap | ticks to stop | stamina @1800 |
|---|---|---|---|---|---|
| ×1.00 (canon) | 0.2654 | 0.0139 | 19.1× | 2,335 | 24.9 |
| ×0.75 | 0.2375 | 0.0135 | 17.6× | 2,559 | 33.8 |
| ×0.50 | 0.1897 | 0.0126 | 15.0× | 2,962 | 49.5 |
| ×0.35 | 0.1649 | 0.0120 | 13.8× | 3,624 | 60.4 |
| ×0.25 | 0.1298 | 0.0120 | 10.8× | 4,332 | 68.9 |
| ×0.10 | 0.0855 | 0.0110 | 7.8× | 6,343 | 87.0 |

No row reaches the cards. The economy is a real lever — conversion falls 3.1× and
the gap closes from 19.1× to 7.8× — but a tenth-cost punch is the far end of the
axis, printed precisely so it is visible that the whole axis does not reach.

## What this leaves

Three candidates, and this record deliberately stops short of choosing between
them because the choice is the Director's:

**Two levers together.** Economy plus something else. Nothing measured tonight
rules this out, and the pieces are now instrumented to test it cheaply.

**The eligibility rate.** 373 eligible landings across 24 bouts averaging 2,335
ticks is roughly **24 solid-or-clean head shots per minute of fight**. No real
boxer eats that. This number has never been defended by anyone, it sits upstream
of every term above, and the `needed` column above barely moves across the whole
economy sweep precisely because eligibility does not move with it.

**The stoppage rule itself.** Three knockdowns in a round, four in a bout. Canon
authors it and nothing here questions it, but it is what converts a conversion
rate into a stopped fight, and it has not been examined once.

My own reading, offered as a reading and not a finding: eligibility is where I
would look next. It is the only one of the three that is a *modelling* claim
rather than a tuning value — a claim about how often a punch arrives clean at a
head that is guarded — and it is the term every other lever has to fight against.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 04:20 UTC | END ] -->
