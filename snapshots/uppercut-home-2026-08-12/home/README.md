# Uppercut (UE 5.8)

Clean Unreal home collected from `project-uppercut` on 2026-08-12.

## Layout

- `Uppercut.uproject` — UE 5.8 project (module: `UppercutCore`)
- `Source/UppercutCore` — fight authority (C++)
- `Content/ProjectUppercut` — owned maps/assets (`L_UppercutDevArena`)
- `Content/BoxingAttacks`, `Content/FabImports` — junctions to vendor packs
- `data/`, `fixtures/`, `tools/`, `tests/`, `docs/`, `schemas/` — junctions to the authenticity monorepo

## Build / Play

```powershell
# Close any UnrealEditor that has this project open first.
.\build.ps1
.\play.ps1   # opens /Game/ProjectUppercut/Maps/L_UppercutDevArena
```

Press Play — integrated 1R is the default session (seed 4242).

## Proofs

```powershell
.\prove_integrated.ps1
# or golden-compare both seeds against this project:
$env:UPPERCUT_HOME = "C:\Users\edwar\Uppercut"
python -m tools.engine.prove_integrated_arena
python -m tools.engine.prove_live_arena
```

Canon `-repo=` must be this workspace root (parent of `data/` and `fixtures/`).
Do **not** use the old sandbox path `/Game/Uppercut/Maps/...` — the map lives under `ProjectUppercut`.
