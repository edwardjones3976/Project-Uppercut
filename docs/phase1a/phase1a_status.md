<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | START ] -->

# Phase 1A - Status

Phase 0 gate: **PASSED** 2026-08-02 on repository evidence (`docs/phase0/phase0_status.md`).
Phase 1A follows the ROADMAP's required implementation order. Per Rule 18, "defined" means canonical
data plus validator plus tests exist in the repository; it never means engine implementation.

| # | ROADMAP step | Status | Evidence |
|---|---|---|---|
| 1 | Combat-state definitions | **defined + first engine slice** | canon files as before; `sandbox/Content/StateWalk/` executes the machine in the Blueprint VM, byte-reproducibly (`determinism_probe_results.md` Phase C) |
| 2 | Movement and facing | **defined + engine slice** | canon files as before; `sandbox/Content/RangeWalk/` resolves range bands with hysteresis in the Blueprint VM, byte-reproducibly and with zero hysteresis violations (`determinism_probe_results.md` Phase D) |
| 3 | Camera behavior | **defined** | `data/camera_model.json`, `schemas/camera_model.schema.json`, `tools/uppercut_validate/camera.py`, `tests/test_camera.py`, `docs/phase1a/camera_behavior.md` |
| 4 | Animation states | **defined** | `data/animation_model.json`, `schemas/animation_model.schema.json`, `tools/uppercut_validate/animation.py`, `tests/test_animation.py`, `docs/phase1a/animation_states.md` |
| 5 | Hitboxes, hurtboxes, guard regions, collision truth | **defined + engine slice** (taken ahead of step 4 by Director instruction) | canon files as before; the quality dispatch (Phase D) and the full four-stage resolution pipeline (Phase E) execute in the Blueprint VM - all seven contact classes reached, zero verdict mismatches against canon over 12,000 rows, zero Rule 13 violations. Stage inputs are still proxied rather than real swept geometry |
| 6 | Basic punches | **defined** | `data/punch_model.json`, `schemas/punch_model.schema.json`, `tools/uppercut_validate/punches.py`, `tests/test_punches.py`, `docs/phase1a/basic_punches.md`; the move table supplies each punch, this supplies what throwing one costs |
| 7 | Guard and evasion | **defined** | `data/guard_evasion_model.json`, `schemas/guard_evasion_model.schema.json`, `tools/uppercut_validate/guard.py`, `tests/test_guard.py`, `docs/phase1a/guard_and_evasion.md`; all ten named guards authored as postures over the two collision volumes, closing Decision 0010's step-7 promise |
| 8 | Stamina, health, condition, knockdowns, recovery | **defined** | `data/condition_model.json`, `schemas/condition_model.schema.json`, `tools/uppercut_validate/condition.py`, `tests/test_condition.py`, `docs/phase1a/condition_and_recovery.md`; closes the stamina pool step 6 left open, eight region tracks, no generic pool, no flat KO roll, Chin is never immunity |
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
position: steps 1-8 defined and validated, with engine slices for steps 1, 2 and 5;
steps 9-10 not started; steps 11-12 provisioned only. 302 tests.

**Structural risk, and the first payment against it (Rule 18).** Definitions had outrun the engine
seven to one: steps 1-7 defined, one engine slice. The Phase 1A gate does not ask for definitions,
it asks for complete CPU-vs-CPU matches, and every further definition step widened a gap only
in-engine work closes.

Phases D and E pay the first instalments. Step 2's range-band resolution **with hysteresis** and
step 5's full four-stage collision pipeline now execute in the Blueprint VM, byte-reproducibly
across independent processes and across full asset regeneration. Zero hysteresis violations, zero
verdict mismatches against canon, all seven contact classes reached in-engine, and zero Rule 13
violations - no visible miss classified as landed, and no case where guard outranked an active
evasion.

Three of seven defined steps now have engine presence rather than one. The honest remaining gap:
steps 3, 4, 6 and 7 have no slice, and the pipeline's stage inputs are still proxied draws rather
than real swept geometry against real hurtboxes. What is proven is the ordering, the inverted sweep
stage, the tier ranking and the class arithmetic - not yet the geometry that feeds them.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:31 UTC | edit: Phase E engine slice ] -->

**Step 6 note.** The move table already carried all nine per-attack properties ROADMAP line 51
requires, so step 6 did not restate them. It defines what *throwing* costs: commitment with no
thrower cancel, the recovery differential that turns `contact_classes.json`'s blocked-dodged-whiffed
ordering into actual frames and counter windows, the range and stamina gates (nothing is rescued,
nothing is eaten), the Rule 4 repetition economy, and chaining. The Rule 4 work is the part worth
flagging for review: the validator requires repetition to cost the thrower **and** to give the
defender a growing answer, because a model that only tires the spammer is punishment without
counterplay, and it rejects any mechanism whose trigger is described in repeat-count language.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:58 UTC | edit: step 6 defined ] -->

**Pinned drift closed: "10 guards vs. 2 guard volumes."** The execution plan has carried this item
since the guard design reference landed. Resolved on mechanism rather than on wording, per
**Decision 0010**: a posture modulates the *coverage extent* of the same two guard volumes, so the
ten named guards need neither ten volumes nor ten branches, and the collision pipeline remains the
sole authority over blocking. Bounded so no alignment can zero a volume or push one past its own
structure, and validated non-inert - a canon where every posture holds identical extents fails.
The authored posture set stays step 7 content; only the architecture lands here. A review pass the
same day also found four locations where the design reference contradicted itself on the shell
versus the overhand; that is resolved conditionally on roll alignment and logged in the document's
reconciliation log as items 4 and 5.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:43 UTC | edit: drift item closed, test count ] -->

**Order deviation, resolved.** Step 5 was taken ahead of step 4 on Director instruction
(2026-08-03), coherent at the definitions level but not at the implementation level, where hitboxes
attach to animated skeletons. Step 4 was completed immediately afterwards and **closes that gap**:
`animation_model.json` fixes hitbox transforms to authored pose sampled at a tick index (never
blended playback), with timing owned by move data and authority retained by the collision pipeline.
The seam between the two layers is now defined rather than assumed. The binding order is restored
from step 6 onward.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:52 UTC | edit: step 4 defined, order deviation resolved ] -->
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | edit: step 5 defined, order deviation ] -->
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | edit: step 3 defined ] -->

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | END ] -->
