<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:30 UTC | START ] -->

# Phase F — the bout structure in the Blueprint VM

**Status: PASS — executed in the Blueprint VM, byte-reproducible across a full asset
regeneration.** Hashes and the full account are in
`docs/phase1a/determinism_probe_results.md` under "Phase F".

| Leg | Seed | Produced by | Result |
|---|---|---|---|
| A1 | 56057345 | first generation | baseline |
| A2 | 56057345 | replay | identical to A1 |
| B1 | 99001122 | regenerated | diverges |
| A3 | 56057345 | regenerated from scratch | identical to A1 |

A3 is the leg that matters: the asset is deleted and re-authored, and the run returns
byte-identical. All four analyze clean.

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

## Running it

```powershell
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Gen -Seed 56057345
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Tag A1
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Tag A2
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Gen -Seed 99001122
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Tag B1
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Gen -Seed 56057345
powershell -NoProfile -File tools\engine\run_bout_walker.ps1 -Tag A3
```

`-Seed` applies to `-Gen` only: the base seed is compiled into the Blueprint as a literal
on the BeginPlay chain, so passing it to a run leg would silently do nothing and make a
divergence leg look like a failure to diverge. The runner now says so out loud rather
than accepting the argument quietly. Changing seeds means regenerating, which is the
stronger evidence anyway — it puts the generator under test, not just the asset.

The runner **refuses to start while an interactive `UnrealEditor` is open**, with
`-Force` for a session known to be disposable. Two UE processes writing
`sandbox/Intermediate` and `sandbox/Saved` concurrently can corrupt the project, and a
headless generation can be clobbered by the editor's next save. That guard is part of
the deliverable: every other runner in this folder would have happily raced an open
editor. The analyzer runs automatically on each leg.

## The analyzer failed the first clean run, and it was the analyzer that was wrong

A1 reported `SEALED LEAK ... position 1439, before the final observable marker at
position 1440`. Both cards were on the **final tick**; actors tick in sequence inside one
frame, so actor 0's card is legitimately emitted before actor 1's last observable line.

The temptation there is to relax the check until the run passes, which is the same
failure the coverage registry's "flattering direction" check exists to catch one layer
up. Instead the claim was restated precisely — *no card before the final bell*, not *no
card before the last line* — and the check now tests two things: every card is stamped
with the final round, and every observable marker after the first card is itself from the
final tick. A card printed at tick 300 fails both, with hundreds of non-final markers
behind it. The real interleaving is now a regression test taken verbatim from A1.

A second hole surfaced the same way: "every actor emits exactly one card" iterated the
sealed rows, so an actor emitting *no* card had no entry to count and could never be seen
missing. It counts against the observable stream now. Both were found by tests.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:30 UTC | END ] -->
