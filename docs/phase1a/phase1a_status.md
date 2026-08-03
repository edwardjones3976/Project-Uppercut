<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | START ] -->

# Phase 1A - Status

Phase 0 gate: **PASSED** 2026-08-02 on repository evidence (`docs/phase0/phase0_status.md`).
Phase 1A follows the ROADMAP's required implementation order. Per Rule 18, "defined" means canonical
data plus validator plus tests exist in the repository; it never means engine implementation.

| # | ROADMAP step | Status | Evidence |
|---|---|---|---|
| 1 | Combat-state definitions | **defined + first engine slice** | canon files as before; `sandbox/Content/StateWalk/` executes the machine in the Blueprint VM, byte-reproducibly (`determinism_probe_results.md` Phase C) |
| 2 | Movement and facing | **defined** | `data/movement_model.json`, `schemas/movement_model.schema.json`, `tools/uppercut_validate/movement.py`, `tests/test_movement.py` |
| 3 | Camera behavior | **defined** | `data/camera_model.json`, `schemas/camera_model.schema.json`, `tools/uppercut_validate/camera.py`, `tests/test_camera.py`, `docs/phase1a/camera_behavior.md` |
| 4 | Animation states | not started | - |
| 5 | Hitboxes, hurtboxes, guard regions, collision truth | **defined** (taken ahead of step 4 by Director instruction) | `data/collision_model.json`, `schemas/collision_model.schema.json`, `tools/uppercut_validate/collision.py`, `tests/test_collision.py`, `docs/phase1a/collision_truth.md` |
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
**cleared**. The determinism question's engine-runtime half **passed** 2026-08-03: byte-identical
10,008-line logs across independent editor processes, seed-sensitive, over the canonical
combat-state machine (`docs/phase1a/determinism_probe_results.md`). The **Blueprint actor-tick half
also passed** the same day: five ticking BP actors, byte-identical 10,000-marker logs across
independent `-game` processes, seed-sensitive. Blueprint assets were authored **headlessly** via
editor Python (Route A; no GUI needed). Rule 22's C++ trigger stays armed for scale and for the
one unmeasured case (float accumulation - see the recorded probe defect), not fired for correctness.
Phase C (2026-08-03) then closed that case: float accumulation is deterministic, the dead-accumulator
root cause was a mistyped variable from `get_basic_type_by_name` (recorded), and the canonical
fighter_action machine now executes in the Blueprint VM byte-reproducibly. The trigger is armed for
scale only. Per Director instruction, the next-hardest item - collision truth (step 5) - is
explicitly deferred, behind steps 3-4 in the binding order.
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 02:55 UTC | edit: Phase C ] -->
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 01:28 UTC | edit: Phase B result ] -->
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | edit: step 2 defined, runbook added ] -->

## Quality gate

The Phase 1A quality gate is defined in `ROADMAP.md`. Nothing in it is claimed. Current honest
position: steps 1-3 and 5 defined and validated (step 1 additionally has a first engine slice);
steps 4 and 6-10 not started; steps 11-12 provisioned only. 200 tests.

**Order deviation, recorded honestly.** Step 5 was taken ahead of step 4 on Director instruction
(2026-08-03). This is coherent at the definitions level - collision geometry does not depend on
animation - but NOT at the implementation level, where hitboxes and hurtboxes attach to animated
skeletons. Step 4 therefore remains a prerequisite for building step 5 in the engine, and remains
not started.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | edit: step 5 defined, order deviation ] -->
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | edit: step 3 defined ] -->

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | END ] -->
