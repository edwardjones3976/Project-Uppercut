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

**Those balance figures are superseded.** They were correct when measured and the paragraph
above is left as written, but the units correction later the same day changed what they were
measured against: work rate fell from 138 punches per fighter per round to 31, which made the
old `pressure_threshold` of 1.50 unreachable and forced a re-sweep to 0.57. Current, all-pairs,
eight seeds, two independent bases: technician 50/60, counterpuncher 45/60, power_threat 45/50,
rusher 45/42, showman 45/32, drainer 32/**22**. Result states 32% stoppage / 58% decision / 9%
draws; top landed move 37% against the 60% gate; determinism byte-identical. **The 30-70% band
no longer holds** - the drainer is below the floor on one base, so style balance is an open
item again rather than a closed one. Viability still passes, which is the gate Rule 21 actually
sets. Full account: `docs/phase1a/exploit_hunt.md`, "Superseded".
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 14:44 UTC | START/END ] -->
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:52 UTC | edit: steps 11-12, evidence rig ] -->

**The bout structure now executes in the engine (Phase F).** Phases B through E each proved
one subsystem reproducible in the Blueprint VM - actor tick, the canonical state machine,
range bands with hysteresis, the four-stage collision pipeline - and every one of them is
something that happens INSIDE a round. `BP_BoutWalker` runs the round itself: three rounds
across two ticking actors, boundaries derived from the authoritative tick, a per-round
accumulator that banks and resets at each bell, and a sealed card that is structurally
unreachable before the final tick. Four legs, byte-identical across a full asset
regeneration and divergent on a different seed, all analyzing clean. That closes the
largest single entry in the reference model's coverage registry and is the first time a
BOUT rather than an exchange has executed in-engine. Judging arithmetic is not claimed -
the banked value is a force proxy - and `match_flow`'s entrance, break, count, doctor-check
and post-fight segments remain named-as-unbuilt rather than implied. Evidence:
`docs/phase1a/determinism_probe_results.md` (Phase F) and `bout_walker_phase_f.md`.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 13:04 UTC | START/END ] -->

**The bout is now scored in the engine (Phase G).** `BP_FightWalker` joins the Phase E
collision pipeline to the Phase F round structure, so the round card is computed from
resolved contact rather than a proxy: each resolved class contributes its authored
delivered force fraction, a blocked punch contributes nothing, the accumulator banks and
resets at each bell, and the card equals the sum of the banked rounds. Four legs,
byte-identical across a full asset regeneration, all seven contact classes occurring in a
single run, and the analyzer recomputing the whole chain from canon tick by tick.

Its first run failed in the most useful way available: the pipeline reported the right
class and then scored it wrong - a clean punch as nothing, a brushed punch as a grazed
one - which hashed perfectly and would have passed every Phase E and F check. The cause
was `RandomFloatFromStream` being a pure node that mutates the stream, so a pure chain
with several consumers draws several times. Draws are now materialized into variables
before anything reads them, and that is rule 7 in `tools/engine/bp_authoring.py`. Phase E
was re-run and still passes, so it stands as evidence, with the caveat recorded rather
than left to be rediscovered.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 14:16 UTC | START/END ] -->

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

**The Judge subsystem exists** (2026-08-04, Decision 0012 slice item 1). Minimum scope's "deterministic
Judge subsystem behind the score firewall" stops being `Bout._score_round` computed inline and becomes
`tools/uppercut_sim/judge.py`: witnessed facts in, sealed cards out, cards unreadable before the final
bell by exception rather than by comment. Five source-relation checks in `cli all` hold the boundary in
both directions, each proven non-vacuous by a synthetic violation, and the extraction was held to byte
identity - 72 bouts across every profile pairing, unchanged grand hash
(`docs/phase1a/judge_subsystem.md`). The contract's live source scan is load-bearing as of the same
change, with `tools/uppercut_sim/policy.py` named as the real CPU consumer. The referee did not move:
counts and stoppages are ring facts, and referee-profile consumption is the next slice item.
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START/END ] -->

**Referee profiles officiate** (2026-08-04, Decision 0012 slice item 2). The seven philosophies stop
being inert data: `data/referee_semantics.json` maps their categorical levels to executed numbers,
and each official now differs in the clinch warning/deduction ladder (deductions reach the sealed
card as witnessed facts, one point, exactly like a knockdown), break patience, and the
`referee_judgement` stoppage — a stoppage condition canon declared at step 8 and nothing executed.
The count arithmetic stays one code path for every official (Rule 16). Calibration proven: the
default official reproduces the pre-consumption engine byte-for-byte over the 72-bout matrix, so
every recorded balance figure still describes the current build; the protective official stops two
of those 72 fights on observable evidence. Named finding carried to step C: no stress policy ever
clinches, so clinch-side tendencies are unreachable in natural play until the CPU gets the clinch
(`docs/phase1a/referee_consumption.md`).
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START/END edit: referees consumed ] -->

**The fight core has a C++ home, and it is proven (Phase H)** (2026-08-04, Decision 0012 slice
item 3). `UppercutCore` is a real Unreal C++ Runtime module in the sandbox, compiled by a toolchain
installed the same day on the Director's license acceptance, and its probe — the Phase D hysteresis
walk, the same rule's third independent implementation — reproduced byte-identically across
processes and a **full rebuild**, with bytes identical to the Python reference recomputation.
Analyzer-first as every phase before it: the contract was mutation-proven and committed before the
machine could compile. The claim is deliberately narrow — one rule walking alone, no fighters, no
cards — and the next slice item, the two-fighter authoritative loop, is where the core starts being
a core (`docs/phase1a/determinism_probe_results.md`, "Phase H").
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 04:52 UTC | START/END edit: Phase H proven ] -->

**The core is a core (Phase I)** (2026-08-04, Decision 0012 slice item 4). The two-fighter
authoritative loop runs in C++: real ring positions with ropes and the min-separation snap,
directional footwork with the exhausted multiplier, band hysteresis from real separations, the
stamina economy, move-table commitment, Rule 12's range gate — five canon files consumed at once,
byte-identical across a full rebuild and identical to the Python recomputation, every branch of the
decision surface exercised. Second consecutive phase compiling clean and passing on the first run.
The instrumented float probe returned **bit-identical to CPython on every checkpoint**, putting the
reference simulator's float arithmetic on an evidenced road into the C++ core — each new expression
shape still gets its own probe as it ports. No collision, no condition, no judge, no policies yet;
the decision stream is a schedule, not a mind (`determinism_probe_results.md`, "Phase I").
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:25 UTC | START/END edit: Phase I proven ] -->

**Punches have geometry (Phase J)** (2026-08-04, Decision 0012 slice item 5). The fist is an
authored extension profile (`data/pose_geometry.json` — schematic reference pose, the 2D stand-in
until real clips exist), swept per tick, live only during animation active ticks, against the
defender's position at that tick. The lane result the whole design stands on is now emergent in
engine evidence: with high_guard's authored extents against one interception threshold, 132 of 132
jabs were blocked and 114 of 114 reachable body straights landed — "body shots pay off against a
high guard" written as a rule nowhere, produced by structure everywhere. Eight canon files, animation
frame-lock consumed, byte-identical across a full rebuild, float probe bit-identical to CPython
again. No damage flows from a landed punch yet; slice item 6 (the four punches animated on generic
fighters) is where evidence becomes something a spectator can see (`determinism_probe_results.md`,
"Phase J").
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:15 UTC | START/END edit: Phase J proven ] -->

**The game renders (Phase K)** (2026-08-04, Decision 0012 slice item 6). Jab, cross, lead hook,
rear uppercut and the body straight on primitive-built generic fighters, in a scene spawned entirely
at runtime — no content assets — one authoritative tick per rendered frame, screenshots on the
record and delivered to the Director. The claim that matters is proven the house way: the rendered
run's marker stream is byte-identical to the Python recomputation and to a second rendered run, so
**rendering holds zero authority over the fight**. The uppercut splits the high guard on screen
because the move table says blockable_low and the geometry obeys. Gate item 5 flips from untestable
to testable; the readability judgment is the Director's. Presentation is deliberately crude — the
comedy, the reactions, the crowd all await real content — and no damage or cards flow yet
(`determinism_probe_results.md`, "Phase K").
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:55 UTC | START/END edit: Phase K proven ] -->

**The defender fights back structurally (Phase L)** (2026-08-04, Decision 0012 slice item 7). Guard
and slip in the C++ core: posture switching makes lane coverage per-fighter and dynamic (high_guard
⇄ tight_elbow, the mirror pair the data itself picks at the one interception threshold), the slip is
a frame-locked evasion that outranks guard and loses to the body shot, and committed defense scales
a mid-action defender's extents so the counter window opens from canon numbers alone — 108 counters
through degraded guards in the canonical run, each flagged in the evidence stream. An emergent worth
keeping: defence spam is self-punishing by geometry (structure-churn spends commitment, commitment
degrades cover), Rule 4's philosophy without an anti-spam rule anywhere. Byte-identical across a
full rebuild, identical to the Python recomputation, fourth consecutive phase passing on the first
run. Still no damage or cards from a landed punch — slice item 8 is where landing starts to matter
(`determinism_probe_results.md`, "Phase L").
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 08:05 UTC | START/END edit: Phase L proven ] -->

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
