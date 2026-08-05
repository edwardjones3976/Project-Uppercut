<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 11:10 UTC | START ] -->

# Not the recovery branch — footwork, and canon prices a step twice

**2026-08-05.** The previous entry put one question to the Director: should a
fighter regenerate only while free? It reported a fighter committed 74.9% of the
time receiving 10.9 stamina of regen per round against an authored 43.2, and
concluded the pool "is being drained because it almost never refills."

That conclusion is **wrong**, and this is the measurement that overturns it. It is
the eighth time tonight a diagnosis has been corrected by the next measurement,
and the pattern is now the most reliable thing in this log.

## All three candidate answers do nothing

Swept against the reference simulator's own drain trajectory (11.1% of the pool
per minute over the same 24 seeds, ending at a mean 34.2%):

| candidate | stamina @1800 | @3600 | cards |
|---|---|---|---|
| as it stands | 27.7 | 4.8 | 0/24 |
| A: regen while committed, 50% of free rate | 30.1 | 5.8 | 0/24 |
| A: regen while committed, 100% | 32.2 | 7.4 | 0/24 |
| B: free-only, authored rate ×4 | 32.9 | 6.2 | 0/24 |
| B: free-only, authored rate ×8 | 37.4 | 7.2 | 0/24 |
| C: commitment frames ×0.50 | 17.6 | 4.7 | 0/24 |
| C: commitment frames ×0.25 | 12.7 | 2.0 | 0/24 |

Regenerating at the **full** authored rate every single tick, committed or not,
moves stamina at one minute from 4.8 to 7.4. Not one setting reaches the
reference's drain band. The recovery branch is not the lever, and candidate C is
actively worse — shortening commitment lets a fighter act more often, and acting
is what costs.

## Where the pool actually goes

Never measured before, because the earlier stamina budget compared the guard hold
against punching only — in a core that had neither footwork nor evasion:

| item | per fighter per round | share |
|---|---|---|
| **footwork** | **108.2** | **46.7%** |
| punching | 60.7 | 26.2% |
| evasion | 59.9 | 25.9% |
| guard hold | 2.7 | 1.2% |
| **total out** | **231.5** | |
| regen received | 10.6 | |
| **net** | **−220.9** | against a pool of 100 |

The guard hold — the thing an earlier entry called "11% of the story" and the
Director's open question about whether holding a guard for three minutes should
empty a man — is **1.2%**. It was never the story. Footwork is the largest single
item in the stamina economy and nothing had ever priced it, because until Phase Q
footwork did not exist.

## And canon prices a step twice

    movement_model.locomotion   0.60 per reach unit x 0.22 ru stride = 0.132
    data/moves generic table    0.600 per step, flat

**The move table charges 4.55× the locomotion model for the same 0.22 ru stride.**
That is a contradiction, not a rounding: one of the two is the price of a step and
the other is not. The core reads the move table, so it has been paying the higher
one since footwork started working four hours ago.

At the locomotion model's price, footwork costs 23.8 per round instead of 108.2
and total spend falls from 231.5 to 147.1. That is a **correctness** fix — it
resolves a contradiction rather than tuning an outcome — and it is emphatically
not the whole answer, because 147.1 is still fourteen times the regen received.

Per the working style, this is logged rather than silently resolved: the two
numbers disagree, the core follows the move table, and which one is canon is the
Director's call.

## What this actually leaves

The honest position is smaller and more specific than the last entry's.

The stamina economy's problem is **not** the recovery branch, **not** the guard
hold, and **not** any pressure term. It is that a fighter in this core performs
roughly 180 stamina-charging actions per round — a punch, a step, or a slip every
few ticks — against an economy whose regen refills 10.6 per round. Every action is
individually priced somewhere between plausible and contradictory; there are
simply far too many of them.

Which points at the same place the funnel measurement did six hours ago and I
walked past: **the decision clock**. Not because deciding is expensive, but
because in this core every decision that is not `idle` spends stamina, and a
fighter deciding ten times a second will act ten times a second unless something
stops him. The reference's fighters have policies with idle states, threat
compression, and profile-driven pacing. Ours has a uniform draw over a pool that
happens to contain `idle` once.

I am not going to fix that by inventing a policy. It is the CPU model's job, canon
authors it (`cpu_decision_model`, `threat_compression`, the pacing identities in
the stress profiles), and the core reads almost none of it.

## For the Director, revised

**The step-cost contradiction needs a ruling.** Two canon files price the same act
4.55× apart. Everything downstream of footwork is wrong until that is settled, and
it is a five-minute decision.

**The recovery question is withdrawn as urgent.** I raised it three hours ago on an
arithmetic that was correct but not load-bearing. Regen is a rounding error next
to spend. It may still deserve an answer eventually; it should not be the next
thing anyone works on.

**The next real phase is the CPU policy, and it is not a tuning pass.** Canon
authors threat compression, pacing identities and difficulty tiers; the core reads
a uniform coin. Everything measured tonight after Phase R has been measuring a
fighter who acts on nearly every tick he is free, which is not a fighter.

628 tests pass. No canon edited, no coefficient added, no die drawn.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 11:10 UTC | END ] -->
