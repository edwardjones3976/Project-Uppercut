<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:50 UTC | START ] -->

# Evidence Rig — WS5 (T5.1, T5.2, T5.3)

Code: `tools/uppercut_sim/` · Checks: `tools/uppercut_sim/checks.py` ·
Batch: `python -m tools.uppercut_sim.batch` · Tests: `tests/test_sim.py`

## Authority, stated first

**Unreal is the authoritative simulation** (Decision 0002). `tools/uppercut_sim` is a *reference
model*: it executes the canonical JSON in `data/` so balance evidence, exploit hunts and the
ROADMAP's required automated checks have something to run against before the engine can host them.
Where the two ever disagree, the engine is right and the reference model has a bug — and that
disagreement is itself a finding worth having.

Decision 0002 assigns Python to tools, analysis, simulation analysis and telemetry. This is that. It
holds no tuning values of its own; every number it uses is loaded from `data/`, which is what stops
a reference model turning into a second combat system.

## What now runs

A complete CPU-vs-CPU bout, end to end: bout start, rounds, per-tick decisions at the canonical
interval, punches resolved through the collision pipeline's stage order, outcome recovery applied,
condition accumulated per region, crowd earned with novelty decay, knockdowns produced from
observable force and accumulated condition, stoppages, between-rounds recovery, and a sealed final
card. Roughly 660 events for a three-round bout.

That is the first complete bout this project has produced. It is not the gate — the gate wants it in
the engine, with a spectator able to follow it — but it is the first time the canon has been executed
rather than validated.

## The eight required checks that could honestly be built

The ROADMAP lists eleven required automated checks. Until now exactly one existed — the attribute
fixtures — because the other ten need something to run. Nine now run:

| Check | What it asserts |
|---|---|
| Accelerated-clock synchronization | One clock at 60Hz read by every named system; acceleration is a display mapping that reaches neither the tick rate, the frame data, the stamina economy, nor the knockdown count |
| Score-access denial | Judge events are sealed, no observable payload leaks card data, and the Observation handed to a policy contains no path to the cards |
| Determinism and seeded replay | Same seed reproduces the log byte for byte; different seeds diverge |
| Repetition versus spam | Novelty decays with repetition **and** never reaches zero |
| Large-batch invalid state and deadlock | 40 bouts with no out-of-range stamina or condition, strictly ordered sequences, monotonic ticks, backward causality, and no bout where nothing resolved |
| Knockdown, stoppage and result states | Stoppages occur, each explained by a knockdown, every bout ends on a final card |
| First Bell Firestorm | Effective pressure **can** win, and does **not** win everything |
| Long Drain | Patience pays in stamina, and the patient instrument still throws |
| Crowd-farming prohibition | Repeated actions are reduced by novelty; unopposed targets pay nothing |

Several are deliberately two-sided. First Bell Firestorm fails if the aggressive profile never wins
*and* fails if it always wins, because "aggression can win" and "volume alone is not enough" are both
canon. Long Drain fails if the patient instrument throws nothing, because that is empty avoidance
rather than stamina control. A check that only forbids can be satisfied by a simulation where
nothing happens, so most of these assert that something *can* happen too.

Two remain unbuilt and are named rather than quietly skipped: style-viability and dominant-loop
detection at scale, and the full repetition abuse list (safe-animation abuse, stun loops, clinch
abuse, excessive running, passive blocking).

## Balance instruments

The six canon stress profiles are mapped to numeric policies in `policy.py`. The profiles are canon
and unedited; the mapping from their declared win and risk conditions to biases is a tuning
hypothesis. A canon profile with no mapping raises rather than being silently skipped.

A 90-bout round robin at six seeds produced no dominant extreme and no absent counterplay. Rule 21
governs how that is read: lopsided results are findings to explain, not automatic failures, and the
report flags only the two conditions the rule calls gate failures — a profile that never wins, and a
profile that always does.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:50 UTC | END ] -->
