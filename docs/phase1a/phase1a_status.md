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
| 9 | CPU decision-making (observable info only) | **defined** | `data/cpu_decision_model.json`, `schemas/cpu_decision_model.schema.json`, `tools/uppercut_validate/cpu.py`, `tests/test_cpu.py`, `docs/phase1a/cpu_decision_making.md`; the score firewall is proven as a set relation against the isolation contract, not as a discipline, and difficulty changes perception only |
| 10 | Deterministic logging and replay evidence | **defined** | `data/replay_model.json`, `schemas/replay_model.schema.json`, `tools/uppercut_validate/replay.py`, `tests/test_replay.py`, `docs/phase1a/logging_and_replay.md`; resimulation and replay kept as separate contracts, major events must carry causal explanation, sealed cards stay sealed through replay |
| 11 | Crowd Bar architecture | **defined** | `data/crowd_model.json`, `schemas/crowd_model.schema.json`, `tools/uppercut_validate/crowd.py`, `tests/test_crowd.py`, `docs/phase1a/crowd_bar.md`; gain sources locked to the crowd contract, novelty decays to a floor above zero, risk gate stops farming, full bar exclusive |
| 12 | Special / Full-Crowd Trait / Ultimate architecture | **defined** | `data/ability_model.json`, `schemas/ability_model.schema.json`, `tools/uppercut_validate/ability.py`, `tests/test_ability.py`, `docs/phase1a/ability_architecture.md`; every ability counterable with no invulnerability and no commitment bypass, command entry bypasses nothing (architecture only, no fighter content) |

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
position: **all twelve Phase 1A steps defined and validated**, with engine slices for steps 1, 2
and 5, and a Python reference simulator running complete CPU-vs-CPU bouts. 402 tests.

**Event presentation and the authoritative clock are defined** (`data/event_model.json`,
`data/clock_model.json`, `docs/phase1a/event_and_clock.md`). The event model implements section 13
of the merged event presentation reference, which asked for validators and had none: prestige,
broadcast, crowd and venue now hold provably zero authority over the fight, and evidence cannot be
obscured by spectacle. The clock model unblocked the ninth required check - the Accelerated Clock
is a display mapping that may not reach the tick rate, frame data, stamina, or the knockdown count,
which is a safety instrument rather than a pacing option.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:46 UTC | edit: event, clock, ninth check ] -->

**The evidence rig exists (WS5).** `tools/uppercut_sim/` executes the canonical models end to end -
decisions, collision pipeline, condition, crowd, knockdowns, stoppages, sealed cards - and **all
eleven** of the ROADMAP's required automated checks now run against it: score-access denial,
accelerated-clock synchronization, style viability and dominant-loop detection, the repetition
abuse list, determinism and seeded replay, repetition-versus-spam, large-batch invalid-state and
deadlock, knockdown and stoppage and result states, First Bell Firestorm, Long Drain, and
Crowd-farming prohibition.
Unreal remains authoritative (Decision 0002); the reference model is an instrument, not a result.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:12 UTC | edit: eleven of eleven ] -->

**The last two checks found nine real defects, and that is the point of them.** Playing Rule 4's
named abuses as hard as a policy can play them turned up: judges counting contacts rather than
scoring rounds; an evidence harness with its own opinion about who won; a ring that did not exist,
which made excessive running unanswerable rather than unprofitable; two named abuses that were the
same behaviour; a clean jab hitting exactly as hard as a clean overhand; two knockdown inputs
declared in canon since step 8 and read by nothing; no way back from being hurt inside a round; and
a 60-bout sweep in which **every single bout ended in a stoppage** while the suite stayed green,
because the result-state check asserted that stoppages can happen and never that decisions do. The
ninth was the largest: `punch_model.repetition_economy` declared four mechanisms, gave none of them
a number, and so ran entirely inert - the whole of Rule 4's answer to repetition existed as four
sentences. All nine are resolved in canon rather than in the simulator, with a validator refusing
each regression. Full account with before-and-after figures: `docs/phase1a/exploit_hunt.md`.

Result states over 60 bouts at canonical length now read 45% stoppage, 55% to the cards. **Style
balance is the named open finding** - viability passes, every style can win, but power and pressure
run well ahead of parity (power_threat 72-80%, drainer 12-22%) and the showman's result swings
enough between seed bases to be close to noise. Recorded as evidence rather than as a red test.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:12 UTC | START/END ] -->

**The balance finding was run to ground the same day, and it was not a tuning problem.** Every
lopsided rate traced to a mechanism some losing style's canon win condition names that existed as
declaration and executed as nothing: crowd paid to the wrong fighter with a bar that could neither
drain nor spend (the showman's entire win condition, inert); counter windows that were numbers
rather than windows (the counterpuncher's); a telegraph that existed as prose (power's declared
risk); and every region below the neck cosmetic (bodywork, named in two win conditions). All four
are now canon with coefficients - `crowd` recipients as written plus
`ability_model.reference_instruments`, `guard_evasion_model.committed_defense` and `.telegraph`,
`condition_model.impairment` - each with a validator that refuses the declared-but-inert state,
and mutation-proven tests. After: every style sits inside 30-70% on both independent seed bases
(floor up from 5%, ceiling down from 80%), 44% stoppage / 48% decision / 8% draws, top landed
move at 41% against the 60% gate, determinism byte-identical throughout. Full account:
`docs/phase1a/exploit_hunt.md`, "The balance pass".
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 10:56 UTC | START/END ] -->
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:52 UTC | edit: steps 11-12, evidence rig ] -->

**What "definitions complete" does and does not mean.** Every layer a CPU-vs-CPU match needs is now
specified, cross-locked to its neighbours, and enforced by something that fails loudly. That is not
the gate. The gate wants complete matches running from selection through post-fight flow, and the
distance between a validated definition and a running match remains the largest item on the board.
Steps 11-12 are also still provisioned slots, so Phase 1A's definition work is not finished either -
only the ten steps that a match strictly requires.

**Gate item answered structurally.** The gate asks that CPU fighters use "no hidden score, opponent
input, or privileged state knowledge" - an absence, which behaviour testing struggles to show. Step 9
answers it as a set relation: the CPU's declared observable inputs are checked against the
`fight_event` vocabulary and against every sealed symbol in `score_isolation_contract.json`, so a
firewall breach fails validation rather than surviving until someone reads the code. The blindness
loophole is closed too - an empty input set would satisfy containment and is rejected.

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
