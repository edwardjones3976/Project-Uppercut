<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ] -->

# Evidence — live arena ring presentation (2026-08-12)

## What changed

- `GameDefaultMap` / `EditorStartupMap` → `/Game/ProjectUppercut/Maps/L_UppercutDevArena`
- `UppercutArenaPresentation` spawns Fab ring (soft-fail) and loads mannequin assets
- `AUppercutMatchDirector` calls ring spawn before `StartRound`
- `AUppercutFighterBase` soft-swaps cylinder → Manny/Quinn + action clips
- `AUppercutBoutDirector::BuildArena` delegates to the same helper

## Authority

Unchanged. Presentation only (Decision 0012). `prove_live_arena` must remain
byte-identical to Phase Q (operator-run on Windows with UE 5.8).

## Operator verify (Windows)

1. Open `sandbox/UppercutSandbox.uproject` (should open L_UppercutDevArena).
2. Confirm Outliner: MatchDirector, Fighter0, Fighter1.
3. Press Play — Fab ring + mannequins when packs present; cylinders otherwise.
4. `python -m tools.engine.prove_live_arena`

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ] -->
