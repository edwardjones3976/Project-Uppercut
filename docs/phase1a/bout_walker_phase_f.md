<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:30 UTC | START ] -->

# Phase F — the bout structure in the Blueprint VM

**Status: authored and analyzer-proven; the engine leg has not been run.** The reason is
stated plainly below rather than buried, because an engine phase that has not executed
is not evidence, and this project's own Rule 18 says so.

## What this phase is for

Phases B through E each proved one subsystem reproducible inside the Blueprint VM:

| Phase | What executed in-engine |
|---|---|
| B | Actor tick across multiple ticking actors |
| C | The canonical combat state machine |
| D | Range bands with hysteresis |
| E | The four-stage collision pipeline |

Every one of those is something that happens *inside a round*. Nothing has executed the
round itself. `match_flow` is the largest single entry in the reference model's coverage
registry (`data/combat_states.json` → `reference_model_coverage`), and the Phase 1A gate
asks for complete matches from selection through post-fight flow. The distance between a
proven exchange and a proven **bout** is this phase.

## The two claims, and why they fail differently

**Rule 8/9 — one authoritative clock drives the round boundaries.** The Blueprint derives
`round` and `tickInRound` from the authoritative tick each frame and emits both, so the
analyzer recomputes every boundary rather than trusting the Blueprint's own count. A
Blueprint keeping a private round counter that drifted from the clock would hash
perfectly and fail here.

**Rule 3 — the round card is sealed.** This is the claim a hash cannot test. A Blueprint
that printed the scorecard on every tick would be perfectly reproducible and a flat Rule
3 violation. So the graph has two emission paths — observable `B|` every tick, and sealed
`S|` hanging off the *true* branch of the final-bell test, physically unreachable before
the last tick — and the analyzer's check is **positional**: no `S|` line may appear
before the last `B|` line. That makes the seal a fact about the log rather than a claim
about the graph.

Marker formats:

```
B|<idx>|<round>|<tickInRound>|<q20 RoundAcc>    observable, every tick
S|<idx>|<round>|<q20 SealedTotal>               sealed, past the final bell only
```

## The banking shape, and the defect it is guarding against

Each tick draws a force proxy from the actor's stream into `RoundAcc`. At a boundary the
completed round's total is banked into `SealedTotal` and `RoundAcc` **resets**.

That ordering is load-bearing and is why `SealedTotal` is written *before* `RoundAcc` in
the execution chain: the bank's getter must still see the completed round's value. The
reference model shipped a `_score_round` that summed the bout to date instead, so an
early lead re-won every subsequent round — a defect found by a balance sweep rather than
by a check. Here a rising accumulator across a boundary is a hard analyzer failure.

`atBoundary` is `tickInRound == 0 AND TickCount > 1`. Without the second term the very
first tick banks an empty round and shifts every card by one.

## What is proven right now

The **analyzer is built and mutation-proven** (`tools/engine/analyze_bout_walker.py`,
`tests/test_bout_walker_analyzer.py`, nine tests). Each test plants one defect in a
synthetic marker stream and asserts it is caught:

- a scorecard leaked mid-fight — the failure a hash cannot see
- **no** sealed card at all — a check that only forbids passes trivially when the thing
  it forbids never happens
- a Blueprint keeping its own clock
- an accumulator that never resets — the `_score_round` defect, replanted
- an accumulator frozen at zero — resets perfectly at every boundary and proves nothing
- a bout that stopped short of its scheduled rounds
- an empty stream

Building the analyzer first is deliberate. It is the part of an engine phase most able to
fake a pass, because a leak detector that never fires looks exactly like a clean run.

## Why the engine leg has not run

An interactive `UnrealEditor` (pid 13880) has held the sandbox since 08:21 local and
created `sandbox/Content/Untitled.umap`. Two UE processes writing `sandbox/Intermediate`
and `sandbox/Saved` concurrently can corrupt the project, and a headless generation can
be silently clobbered by the editor's next save.

`tools/engine/run_bout_walker.ps1` now **refuses to start** while an editor is open and
says why, with `-Force` available for a session known to be disposable. That guard is
part of the deliverable: every other runner in this folder would have happily raced the
editor.

To complete the phase, with the editor closed:

```powershell
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Gen
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Tag A1 -Seed 56057345
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Tag A2 -Seed 56057345
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Tag B1 -Seed 99001122
```

A1 and A2 must be byte-identical; B1 must differ; all three must analyze clean. The
runner invokes the analyzer automatically on each leg.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:30 UTC | END ] -->
