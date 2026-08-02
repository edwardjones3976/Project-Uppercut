<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | START ] -->

# Phase 1A - Status

Phase 0 gate: **PASSED** 2026-08-02 on repository evidence (`docs/phase0/phase0_status.md`).
Phase 1A follows the ROADMAP's required implementation order. Per Rule 18, "defined" means canonical
data plus validator plus tests exist in the repository; it never means engine implementation.

| # | ROADMAP step | Status | Evidence |
|---|---|---|---|
| 1 | Combat-state definitions | **defined** | `data/combat_states.json`, `schemas/combat_state_machine.schema.json`, `tools/uppercut_validate/combat_states.py`, `tests/test_combat_states.py` |
| 2 | Movement and facing | **defined** | `data/movement_model.json`, `schemas/movement_model.schema.json`, `tools/uppercut_validate/movement.py`, `tests/test_movement.py` |
| 3 | Camera behavior | not started | - |
| 4 | Animation states | not started | - |
| 5 | Hitboxes, hurtboxes, guard regions, collision truth | not started | - |
| 6 | Basic punches | not started | move data exists (`data/moves/generic_sandbox_moves.json`); behavior does not |
| 7 | Guard and evasion | not started | - |
| 8 | Stamina, health, condition, knockdowns, recovery | not started | condition regions defined (`data/condition_regions.json`) |
| 9 | CPU decision-making (observable info only) | not started | decision-reason schema exists |
| 10 | Deterministic logging and replay evidence | not started | fight-event schema exists |
| 11 | Crowd Bar architecture | provisioned slots only | provisioned states in `data/combat_states.json` |
| 12 | Special / Full-Crowd Trait / Ultimate architecture | provisioned slots only | same |

## Engine prerequisite

Steps 2 and later increasingly require the Unreal sandbox project. Per Decision 0007 (D-7), engine and
tool versions are pinned from the actual installed build at first engine setup - a Director action.
Definitions-level work (schemas, contracts, validators) may continue ahead of it where honest.
The Director click-path for first engine setup is `docs/phase1a/engine_setup_runbook.md`; the
2026-08-02 machine audit found no Epic Games Launcher or Unreal Engine installed. Later that day the
install completed: **UE 5.8.1** (CL 56057345) is on the machine and pinned in
`docs/phase0/technical_baseline.md`. Runbook step 5 was then executed by agent under
Decision 0009: `sandbox/UppercutSandbox.uproject` exists and a headless editor run accepted it
(commandlet result 0, zero errors, zero warnings, 2026-08-02 23:23 UTC). The engine prerequisite is
**cleared**. Next in-engine task per Decision 0002: deterministic fixed-tick resimulation validation.
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | edit: step 2 defined, runbook added ] -->

## Quality gate

The Phase 1A quality gate is defined in `ROADMAP.md`. Nothing in it is claimed. Current honest
position: steps 1-2 defined and validated; steps 3-10 not started; steps 11-12 provisioned only.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | END ] -->
