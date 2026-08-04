<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 22:45 UTC | START ] -->

# Decision packet — what should being caught mid-punch cost?

Phase O is held because the guard never works: a committed defender's extents are
multiplied by 0.6, high_guard's 0.95 head lane lands at 0.57 under a 0.6
threshold, and fighters are committed on ~740 of every 800 decision ticks. Zero
blocks per round, every bout stopped inside round one.

Two candidate answers were named. Both are now measured
(`tools/engine/experiment_guard_stage.py`, results in
`sandbox/Saved/guard_stage_experiment.json`). One is eliminated outright, the
other is quantified — and together they show the problem has a third layer.

## Candidate A — soften `guard_extent_multiplier_while_committed`: ELIMINATED

Not by a sweep, by arithmetic. Against a hard threshold a lane is closed when
`extent × multiplier ≥ threshold`, so the multiplier at which each lane flips is
exact:

| posture | lane | extent | flips at multiplier | closed at today's 0.6 |
|---|---|---|---|---|
| high_guard | high | 0.95 | **0.6316** | no |
| high_guard | low | 0.55 | 1.091 (unreachable) | no |
| tight_elbow | high | 0.55 | 1.091 (unreachable) | no |
| tight_elbow | low | 0.95 | **0.6316** | no |

Every posture's covering lane flips at the same value, 0.6316, and every exposed
lane would need a multiplier above 1.0 — that is, being committed would have to
*improve* coverage. So the multiplier has exactly two reachable behaviours:

- **below 0.6316** — the guard is entirely absent while committed (today, at 0.6)
- **0.6316 to 1.0** — the guard is exactly as good as a free defender's

**There is no value that produces partial coverage.** It is a switch with the
flip point 5% above where canon currently sits, not a dial. Whatever the answer
is, it is not "pick a softer number", and the near-miss is worth noticing:
canon's 0.6 is close enough to 0.6316 to look like a tuning choice while
behaving like an off switch.

## Candidate B — port the reference's probabilistic guard: WORKS, INSUFFICIENT

`engine.py` resolves a block with `r_guard < extent × 0.55`. The 0.55 is canon's
own, and the draw comes from the LCG the alignment grade already uses, so this is
the same kind of faithful port contact quality was. Over 24 seeds, three rounds:

| | hard threshold (today) | probabilistic port |
|---|---|---|
| blocks | **0** | **868** |
| landings | — | 1,395 |
| knockdowns | — | 106 |
| bouts stopped | 24 of 24 | 24 of 24 |
| decisions reached | 0 | **0** |

The guard starts working — nothing to zero-something is the whole difference —
and a committed defender now catches a share instead of standing open. But the
decision path stays dead: 4.4 knockdowns per bout against a bout limit of 4.

## The third layer, which neither candidate touches

Fixing the guard did not fix the fight, so something else is driving the
knockdown rate. The most likely cause, named here rather than guessed at in code:
**this slice has no decision policy.** Its fighters choose uniformly at random
from eleven actions every decision interval, forever. Canon's 0.57 pressure
threshold was swept against the reference simulator's *policy* — fighters that
pace, reset, and stop throwing when hurt — and its own note records a re-sweep
when work rate fell "from 138 punches per fighter per round to a boxing-plausible
figure." A coin does not pace itself.

That points at the roadmap's own step 9, CPU decision-making from observable
information, as a prerequisite for judging any of these numbers — not as the next
thing to build, necessarily, but as the thing that has to exist before the
knockdown threshold means anything.

## Written default

**Take Candidate B, and do not tune anything yet.**

Porting the probabilistic guard is faithful, restores a mechanism that is
currently inert, and costs one canon coefficient already in the repository. It
should land as its own phase with its own contract, not as an edit to a sealed
one. It will not revive the decision path on its own, and that is fine —
correctness first, then the policy, then tuning against a fight that behaves like
a fight.

**What not to do:** soften the committed multiplier (Candidate A is a switch, and
setting it above 0.6316 makes commitment cost nothing defensively, which deletes
the counter window Phase L exists to prove); or raise the knockdown threshold
until the sweep looks right, which is tuning against an artifact — the same trap
named in the Phase N erosion finding and in the external review's warning about
tuning subsystems before their consequences exist.

**The Director's call is the design question underneath:** should being caught
mid-punch *degrade* defence (a chance to still catch it) or *remove* it (today's
behaviour, honestly stated)? Candidate B is the first; the current model is the
second and merely does not admit it. Both are defensible boxing; only one is
currently reachable through canon's own numbers.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 22:45 UTC | END ] -->
