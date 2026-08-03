<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 00:01 UTC | START ] -->

# Determinism Probe Results - Engine-Runtime Half (Decision 0002)

**Question under test** (from `docs/phase0/technical_baseline.md`): can this engine, on this machine,
reproduce byte-identical authoritative logs from the same seed and initial state?

**Verdict for the engine-runtime half: PASS.** Two independent editor processes with the same seed
produced byte-identical 10,008-line logs; a different seed diverged (non-vacuity). Executed
2026-08-03 00:00 UTC on UE **5.8.1** (CL 56057345), Windows 11, Ryzen 7 5800X.

## What was exercised

`tools/engine/determinism_probe.py`, run inside `UnrealEditor-Cmd` via PythonScriptPlugin by
`tools/engine/run_determinism_probe.ps1`. Per run, over a fixed logical tick (dt = 1/60, no wall
clock, no frame timing): 10,000 distinct engine `FRandomStream` constructions and draws (derived
per-tick seeds), 20,000 chained `KismetMathLibrary` sin/cos accumulations whose trajectory feeds back
into itself, and a deterministic walk over the canonical fighter_action machine from
`data/combat_states.json` - the same canon the validators enforce. Every float serialized as exact
hex bits.

## Evidence

| Run | Seed | Lines | SHA-256 |
|---|---|---|---|
| v2_run1 | 56057345 | 10,008 | `36F31A5668DE722A8C180541C33E5C5FBECE2D443E00B1CA2D48A0CEC9DA1B12` |
| v2_run2 | 56057345 | 10,008 | `36F31A5668DE722A8C180541C33E5C5FBECE2D443E00B1CA2D48A0CEC9DA1B12` |
| v2_run3 | 777 | 10,008 | `6E7BD76EBEA56DA1ADBF5F27DC95DA30A3E97D4E5D4931C76E3135B1789D58D5` |

Logs live under `sandbox/Saved/DeterminismProbe/` (unversioned by design - they are regenerable, which
is the point). Reproduce:

```
tools/engine/run_determinism_probe.ps1 -Seed 56057345 -Ticks 10000 -OutFile <path>
```

All three editor runs exited 0; the known Turnkey wedge was auto-killed by the runner each time (see
the runbook).

## A recorded scripting-semantics finding (probe v1)

KismetMathLibrary stream draws cross the Python bridge **by value**: a single `FRandomStream` held in
Python never advances, so v1's per-tick "draws" were constant per seed. v1's byte-identical result
(SHA `DDFB7E7AE60C0591E759233563BB08280BC72D1C07706546E87B8543DB0BD2BE` twice) remains valid evidence
of chained float-math determinism, but the RNG claim required v2's per-tick derived streams. Lesson
for the simulation core: **authoritative RNG streams must live and advance engine-side**, never
round-tripped through a scripting boundary.

## What this does NOT prove (Rule 18)

This is the necessary half, not the sufficient one. It does not prove **Blueprint actor-tick
determinism**: tick ordering across actors, Blueprint VM evaluation, and engine subsystem interleaving
under `-game` execution. That half needs authored Blueprint assets driving the same log format, and
its own byte-compare evidence, before Decision 0002's Blueprint-can-hold-resimulation question is
answered. Until then, Rule 22's C++ trigger for the simulation core remains neither fired nor
dismissed.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 00:01 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 01:28 UTC | START ] -->

## Phase B - Blueprint Actor-Tick Determinism (the sufficient half)

**Verdict: PASS.** Two independent `-game` processes produced byte-identical 10,000-marker logs;
a different seed diverged. Executed 2026-08-03 on UE 5.8.1 (CL 56057345).

| Run | Seed | Markers | SHA-256 |
|---|---|---|---|
| diagA  | 56057345 | 10,000 | `B8AC4F1C85E4622E84904A1B4F0C4B0ABCA97635D3CEFB954BB1AC647ACEBD6A` |
| diagA2 | 56057345 | 10,000 | `B8AC4F1C85E4622E84904A1B4F0C4B0ABCA97635D3CEFB954BB1AC647ACEBD6A` |
| runB   | 777      | 10,000 | `6DD10F08D5CC39927503260AA4BF15D4302C8ABD0EC9E29BE391FE36C0D973DA` |

### Route decision: headless authoring, no GUI required

`tools/engine/bp_capability_scan{,2,3}.py` inventoried UE 5.8's editor-Python surface against the
real build rather than against documentation. Result: full graph authoring is exposed -
`BlueprintGraphEditor` (`add_call_function_node`, `add_get/set_member_variable_node`,
`add_branch_node`, `create_node_from_name`) and `BlueprintGraphPinLibrary`
(`try_create_connection`, `set_pin_value`). **Route A (headless) was therefore taken; the
computer-use GUI route was not needed.** `tools/engine/bp_generate_determinism_assets.py`
authors the test articles reproducibly - 39 nodes, every pin connected programmatically, compiled
and saved without a human touching the editor.

### Test articles

`/Game/Determinism/BP_DeterminismActor` - ticking Actor with a **RandomStream member variable**
(engine-side state, per the probe-v1 lesson), seeded in BeginPlay as `SEED + MyIndex * 7919`.
Each Tick draws from the stream, increments TickCount, and emits
`P|<MyIndex>|<TickCount>|<q(Acc)>|<q(r)>` to the log, where `q(x) = FFloor(x * 65536)` -
integer quantization because Blueprint float-to-string truncates while integers stringify exactly.
`/Game/Determinism/L_DeterminismProbe` - a plain (non-World-Partition) level holding five
instances, MyIndex 0-4. Run under `-game -UseFixedTimeStep -FPS=60`; actor 0 calls QuitGame at
tick 2000.

### What the log actually proves

**Tick ordering is stable.** Every one of 2,000 ticks emitted its five markers in the order
0,1,2,3,4 - across separate processes. Actor tick order in this configuration is not
frame-timing-dependent.

**The Blueprint VM's RNG is deterministic and genuinely advancing.** Per-actor seeding worked
(tick 1 draws: 2346, 16422, 30498, 44575, 58651 - five distinct streams) and each stream mutates
per tick (actor 0: 2346 then 53811). Unlike the Python bridge in probe v1, a **RandomStream held as
a Blueprint member variable advances correctly** - the stream's internal seed is genuine
path-dependent state carried across 2,000 ticks, and reproducing the log byte-for-byte means
reproducing that entire 2,000-step trajectory per actor.

**Seed sensitivity confirms non-vacuity.** Regenerating with seed 777 changed every draw
(tick 1: 8978, 23054, ...) and the hash.

### A defect in the probe, recorded rather than hidden (Rule 18)

The `Acc` double-accumulator field reads **0 in every marker** - its get/add/set chain is
mis-wired, despite every `try_create_connection` reporting success and the Blueprint compiling
clean. The determinism signal therefore rides entirely on the RandomStream trajectory, which is
sufficient (it is path-dependent state) but the accumulator was meant to add float-math
sensitivity on top. Two consequences, both honest: **(1)** the earlier runA1/runA2 pair, taken
before the raw draw was added to the marker, compared a degenerate constant sequence and is
discarded as evidence - the table above supersedes it; **(2)** float-accumulation determinism in
the Blueprint VM remains *unmeasured*, and a follow-up should fix the wiring and re-run before
anyone claims it. A second lesson also stands: `try_create_connection` returning True is not proof
that a graph computes what was intended - only the emitted values are.

### Consequence for Decision 0002

Blueprints hold deterministic fixed-tick behaviour at sandbox scale across process boundaries, so
the simulation core may proceed **Blueprint-first** as Decision 0002 accepted. Rule 22's C++
trigger stays **armed for scale and for the unmeasured float-accumulation case, not fired for
correctness**. The Phase 1A quality gate's determinism criterion (E.19) has its structural evidence
in the engine; it still needs the real combat simulation behind it before the gate itself closes.

### Reproduce

```
tools/engine/bp_generate_determinism_assets.py   # via UnrealEditor-Cmd -run=pythonscript
tools/engine/bp_tick_orchestrator.ps1 <tagA> <tagB>
```

Both wrap the Turnkey `Build.bat` wedge-killer (see the engine setup runbook). One further trap
recorded there: passing `-abslog=` a path the process cannot open suppresses **all** logging and
the editor appears to hang silently.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 01:28 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 02:55 UTC | START ] -->

## Phase C - The Canonical Machine in the Blueprint VM, and the Float Question Closed

**Both remaining claims now have byte-level evidence.** The canonical `fighter_action` machine from
`data/combat_states.json` executes inside the Blueprint VM under `-game`, and Blueprint float
accumulation is deterministic across processes. Executed 2026-08-03 on UE 5.8.1 (CL 56057345).

| Run | Seed | Markers | SHA-256 |
|---|---|---|---|
| walkA1 | 56057345 | 6,000 | `56B676FA6F1CA53B36E43E6D4E5E1A1E8DA0E8E564854BCEB19A4E126F486035` |
| walkA2 | 56057345 | 6,000 | `56B676FA6F1CA53B36E43E6D4E5E1A1E8DA0E8E564854BCEB19A4E126F486035` |
| walkB  | 777      | 6,000 | `A78C1D8E55DBFC42379078E13A44DF51FADF667ED73BD521564E52DEEA129E75` |

### The test article: a first engine slice of canon

`/Game/StateWalk/BP_StateWalker` (generator: `tools/engine/bp_generate_state_walker.py`) carries the
non-provisioned fighter_action transition table - 12 states, 59 flattened transitions, wildcards
expanded by the same semantics the validators enforce - as flat arrays on the class defaults, written
from `data/combat_states.json` at authoring time. Per tick, entirely engine-side: draw a transition
from the current state's outgoing set (seeded member RandomStream), accumulate
`Acc += r + Sin(Acc)` in genuine floating point, emit
`W|actor|tick|nextState|floor(Acc*65536)|floor(r*65536)`. Three instances in
`/Game/StateWalk/L_StateWalk`, 2,000 ticks. The Acc column is live and path-dependent: **5,742
distinct quantized values across 6,000 markers**, reproduced byte-for-byte across independent
processes. This is not yet combat (no durations, guards, or availability semantics - states and
transition topology only), but it is the first time canon executes in the engine rather than beside
it.

### The dead-accumulator root cause, found and named

The Phase B defect was NOT miswired connections. Graph autopsy (`tools/engine/bp_acc_autopsy.py`)
showed every intended link present - but bridged by engine-inserted conversion nodes, because
**`BlueprintEditorLibrary.get_basic_type_by_name("double")` does not yield a floating-point variable
type in 5.8**. The variable it produced was integer-category; the engine silently wrapped the double
math in int-truncation bridges, so `Acc = trunc(Acc + r)` stayed 0 forever, in both Phase B and the
first walker build. Three defenses now exist in the generator, each of which would have caught it
alone: **(1)** variable types are stolen from real engine pins (`get_pin_type` on a temp node's
ReturnValue) instead of name lookup - with this, the entire 60-node graph wires with **zero**
conversion nodes; **(2)** the accumulation chain uses *strict* wiring where any inserted conversion
node fails the build; **(3)** the evidence extraction asserts the Acc column is non-constant. The
node-handle disciplines from earlier iterations (delta resolution with class filters, absorb-on-
autocast, both-side connection verification) are all retained in the generator.

### Standing for Decision 0002

Blueprint-first is now evidenced on all measured axes at sandbox scale: actor tick ordering,
engine-side RNG streams, float accumulation, and canonical state-machine execution - each
byte-reproducible across processes and seed-sensitive. Rule 22's C++ trigger remains armed **for
scale only**.

### Item 2, deferred by Director instruction (2026-08-03)

The second-most-difficult open item is **collision truth** (ROADMAP step 5): authoritative hitbox /
hurtbox / guard-region geometry, seven-class contact resolution, "a visible miss is never a clean
hit," under the same determinism harness. It is deliberately saved for later and additionally sits
behind steps 3 (camera) and 4 (animation states) in the ROADMAP's binding order. Nothing about it is
started or claimed.

> **Superseded 2026-08-03.** The Director called collision truth forward. Step 3 was completed
> first; step 5 is now **defined** (`docs/phase1a/collision_truth.md`) ahead of step 4, which
> remains not started and remains an implementation-level prerequisite. Definitions only - the
> determinism legs described above still apply to it when it reaches the engine.
> <!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | edit: deferral lifted ] -->

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 02:55 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:16 UTC | START ] -->

## Phase D — range bands with hysteresis, and quality dispatch, in the Blueprint VM — PASS

The first engine slice for ROADMAP steps 2 and 5. Until now those steps had canon, validators and
tests but no engine presence at all; step 1 was the only one with a slice.

**What executes.** `BP_RangeWalker` (`sandbox/Content/RangeWalk/`), three ticking instances under
`-game -UseFixedTimeStep -FPS=60 -Deterministic -nullrhi`, 2000 ticks each:

    r     = RandFloat(Stream)                                  # BP member stream, advances engine-side
    Dist  = FClamp(Dist + (r - 0.5) * 0.08, 0.0, 2.0)
    below = Dist < (BandMin[Band] - Hyst)
    above = Dist > (BandMax[Band] + Hyst)
    Band  = Clamp(Band + ToInt(above) - ToInt(below), 0, 4)
    a     = RandFloat(Stream)
    Qual  = ToInt(a>=0.35) + ToInt(a>=0.6) + ToInt(a>=0.85)
    marker R|MyIndex|TickCount|floor(Dist*65536)|Band|floor(a*65536)|Qual

Band bounds, the 0.05 hysteresis and the three quality thresholds are read from
`data/movement_model.json` and `data/collision_model.json` at authoring time, so the Blueprint is
canon-driven rather than canon-shaped.

The hysteresis rule is the reason this slice is worth building: it is **stateful**. The band you are
in decides the thresholds you must cross to leave it, so it cannot be reproduced by a pure function
of distance, and it is the structural anti-magnetic-correction statement of the movement model.

### Legs

| Leg | Seed | Markers | SHA-256 |
|---|---|---|---|
| A1 | 56057345 | 6000 | `7F7C18246A36F3FF71B6A4099A4CC7E657EEAB3429E102AF4DAEDF2F3CFA7F3B` |
| A2 | 56057345 | 6000 | `7F7C18246A36F3FF71B6A4099A4CC7E657EEAB3429E102AF4DAEDF2F3CFA7F3B` |
| B1 | 99991 | 6000 | `3F5975A424F6D1F0A25DD754325C125AEAB7F4C1C1C4E46935B5F9811D157B47` |
| A3 | 56057345 | 6000 | `7F7C18246A36F3FF71B6A4099A4CC7E657EEAB3429E102AF4DAEDF2F3CFA7F3B` |

Same-seed runs in independent processes are byte-identical; the different-seed run diverges.

**A3 is the result worth noting.** It ran after the Blueprint was **regenerated from scratch** at the
canonical seed, and it reproduced A1 and A2 exactly. So the generator is deterministic too: authoring
the asset again from canon yields byte-identical runtime behaviour, which means the evidence survives
a rebuild rather than depending on one lucky asset.

### Non-vacuity and canon conformance

A byte-identical log proves reproducibility, not execution — a Blueprint emitting a constant would
also be byte-identical. That is precisely how the dead-accumulator defect hid during Phase B. So
`tools/engine/analyze_range_walker.py` checks four things the hash cannot, against canon:

| Check | A1 | B1 |
|---|---|---|
| Distinct quantized distances | 5763 | 5785 |
| Distinct quantized alignments | 5723 | 5727 |
| Bands visited | 5 of 5 | 4 of 5 |
| Quality classes reached | 4 of 4 | 4 of 4 |
| Band changes during the run | 43 | 67 |
| **Hysteresis violations** | **0** | **0** |
| **Quality-dispatch mismatches** | **0** | **0** |

The last two rows are the substantive ones. Every band transition in both runs occurred exactly on
the tick where the distance left `[BandMin[band] - 0.05, BandMax[band] + 0.05]` and on no other
tick — the engine reproduced the canonical hysteresis rule, not an approximation of it. And every one
of the 12,000 emitted quality classes equals the canonical dispatch of its own alignment value.

### What this does and does not establish

It establishes that two more layers of canon execute reproducibly in the Blueprint VM, that the
values are live rather than dead, and that they match canon row by row. It does **not** establish a
fighter, a punch landing, or a match — no gameplay is claimed (Rule 18). The Rule 22 C++ trigger
stays unfired and armed for scale.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:16 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:30 UTC | START ] -->

## Phase E — the collision resolution pipeline in the Blueprint VM — PASS

The layer where a wrong answer is invisible without a harness. The pipeline is a total ordered
function: every attempt resolves to exactly one of seven contact classes, stage 0 is **inverted**
(its verdict fires when the sweep found nothing), and active evasion is ranked deliberately above
guard interception. Each of those could be subtly wrong in an implementation and still look
plausible frame to frame.

`BP_PipelineWalker` (`sandbox/Content/PipeWalk/`), three ticking actors, 2000 ticks each. Four draws
per tick stand in for the pipeline's inputs, and the verdict is computed branchlessly because
exactly one case is true:

    cls = 6*whiffed + 5*dodged + 4*blocked + landed*(3 - quality_count)

Class indices are the canonical order of `data/contact_classes.json`, and the generator refuses to
build if that file is reordered or if the pipeline's stage verdicts change — the Blueprint's
arithmetic encodes those positions, so silent canon drift would silently change what it means.

### Legs

| Leg | Seed | Markers | SHA-256 |
|---|---|---|---|
| A1 | 56057345 | 6000 | `18DB5B9FBCCA867C655B825D328CC27362B064E0356836E760970F00BA411EBE` |
| A2 | 56057345 | 6000 | `18DB5B9FBCCA867C655B825D328CC27362B064E0356836E760970F00BA411EBE` |
| B1 | 99991 | 6000 | `B20F1EF9FD1CEAD7D1FDED35CE068F0DB02D29882052F5397F01A22352A5E886` |
| A3 | 56057345 (regenerated) | 6000 | `18DB5B9FBCCA867C655B825D328CC27362B064E0356836E760970F00BA411EBE` |

Same-seed byte-identical across independent processes and across a full asset regeneration;
different seed diverges.

### Canon conformance — the substantive result

Every marker carries its four pipeline inputs alongside the verdict, precisely so the verdict can be
**re-derived** rather than merely hashed. `tools/engine/analyze_pipeline_walker.py` recomputes the
canonical pipeline from `collision_model.json` and `contact_classes.json` and compares row by row.

| Check | A1 | B1 |
|---|---|---|
| Contact classes reached | **7 of 7** | **7 of 7** |
| Verdict mismatches vs canon | **0** | **0** |
| Visible misses classified as landed (Rule 13) | **0** | **0** |
| Rows where guard outranked an active evasion (Rule 13 tier order) | **0** | **0** |

Class distribution in A1: whiffed 859, dodged 1034, blocked 1399, brushed 935, grazed 703,
solid 668, clean 402.

Criterion A.5 asks that the pipeline be total and every class reachable. That has been enforced by
the validator against the data since step 5 landed; it is now also **demonstrated in the engine**,
with all seven classes actually produced by a running Blueprint rather than argued from a table.

### What this does and does not establish

Three of the four stages are exercised by proxy: the draws stand in for sweep overlap, evasion
windows and guard interception rather than being produced by real swept volumes against real
hurtboxes. What is proven is that the **ordering, the inversion, the tier ranking and the class
arithmetic** execute correctly and reproducibly in the Blueprint VM. Real geometry feeding those
inputs is the next layer, and no gameplay is claimed (Rule 18).

One tooling note: the promotable `Subtract_IntInt` node refuses `set_pin_value` on its **A** pin
while accepting it on **B**. The constant is now fed from a `MakeLiteralInt` node instead. This is
the same family as the earlier promotable-DOUBLE literal defect and is recorded in
`tools/engine/bp_authoring.py`, which now carries the shared authoring discipline.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:30 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:58 UTC | START ] -->

## Phase F — the bout structure (BP_BoutWalker): PASS

Phases B through E each proved something that happens *inside* a round. This one runs the
round itself: three rounds of 240 ticks across two ticking actors, with per-round banking
and a sealed card emitted only past the final bell.

### Determinism

| Leg | Seed | How it was produced | SHA-256 of the marker stream |
|---|---|---|---|
| A1 | 56057345 | first generation | `A79437BED99C71529439FE662CB61E2C94811B03D9E0C45FD3FEBC4D99B734C0` |
| A2 | 56057345 | replay of the same asset | `A79437BED99C71529439FE662CB61E2C94811B03D9E0C45FD3FEBC4D99B734C0` |
| B1 | 99001122 | regenerated | `1486A67719C1D256E5B763F3E2AC93DF930CC2AA62CC828D8ECC7D36E1401273` |
| A3 | 56057345 | **regenerated from scratch** | `A79437BED99C71529439FE662CB61E2C94811B03D9E0C45FD3FEBC4D99B734C0` |

A1 = A2 = A3, and B1 differs. A3 is the leg that matters: the asset is deleted and
re-authored by the generator, and the run comes back byte-identical. The evidence is
therefore about the generator and the model, not about one lucky compile. 1,442 markers
per leg — 1,440 observable (720 ticks × 2 actors) and 2 sealed.

All four legs analyze clean against `tools/engine/analyze_bout_walker.py`, which
recomputes every round boundary from the authoritative tick rather than trusting the
Blueprint's own count.

### The analyzer failed the first clean run, and it was the analyzer that was wrong

Run A1 came back with `SEALED LEAK: an S| card appears at position 1439, before the final
observable marker at position 1440`. The log tail is:

```
B|0|2|239|133244815
S|0|2|253189147
B|1|2|239|121736662
S|1|2|254768311
```

Both cards are on the **final tick**. Actors tick in sequence inside one frame, so actor
0's card is legitimately emitted before actor 1's last observable line, and a check
comparing raw line positions calls that a Rule 3 violation.

This is worth recording because the temptation at that moment is to relax the check until
the run passes, which is exactly the failure the coverage registry's "flattering direction"
check exists to catch one layer up. The log was read first, the claim was restated
precisely — *no card before the final bell*, not *no card before the last line* — and the
check now tests two things instead of one: every card is stamped with the final round, and
every observable marker following the first card is itself from the final tick. A card
printed at tick 300 still fails on both counts with hundreds of non-final markers behind
it. The real interleaving is now a regression test taken verbatim from A1.

A second hole surfaced the same way: the "every actor emits exactly one card" check
iterated the sealed rows, so an actor that emitted *no* card had no entry to count and
could never be seen missing. It now counts against the actors present in the observable
stream. Both were found by tests, not by reading the code.

### What this establishes, and what it does not

Established: round boundaries derive from the authoritative tick and reproduce exactly;
the per-round accumulator banks and **resets** at each boundary, which is the shape the
reference model's `_score_round` was corrected to after it was found summing the bout to
date; and the sealed card is unreachable before the final bell — structurally, because it
hangs off the true branch of the final-bell test, and evidentially, because the log says so.

Not established: no judging arithmetic is claimed. The banked value is a force proxy drawn
from the actor's stream, not scored offence, and `match_flow`'s entrance, break, count,
doctor-check and post-fight segments remain unbuilt — they are named in
`data/combat_states.json` → `reference_model_coverage` rather than implied. No gameplay is
claimed (Rule 18).

Tooling note: the generator compiled and persisted on its first attempt, which is a first
for this project's Blueprint phases. The discipline in `tools/engine/bp_authoring.py` —
node handles by graph delta, connections verified from the destination side, literals kept
off promotable pins — was written down after Phases C, D and E each cost a debugging
session, and Phase F is the evidence that writing it down worked.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:58 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 14:12 UTC | START ] -->

## Phase G — a scored bout (BP_FightWalker): PASS

Phase E proved the four-stage collision pipeline resolves correctly in the Blueprint VM.
Phase F proved the bout structure. Neither connected them: E's verdicts scored nothing,
and F's round card was fed by a raw stream draw standing in for offence. Phase G joins
them, so **the round card is computed from resolved contact**.

### Determinism

| Leg | Seed | How it was produced | SHA-256 of the marker stream |
|---|---|---|---|
| A1 | 56057345 | first generation | `3D54B317817B3C4CE3A40267804DF03AA25CC70616CAF53E2410BF8D6E4CBC96` |
| A2 | 56057345 | replay of the same asset | `3D54B317817B3C4CE3A40267804DF03AA25CC70616CAF53E2410BF8D6E4CBC96` |
| B1 | 99001122 | regenerated | `C0408BD0680BB1B96E0EFE9F703EC9F821446C765DA09F0F8C6C9B19E3D50B9D` |
| A3 | 56057345 | **regenerated from scratch** | `3D54B317817B3C4CE3A40267804DF03AA25CC70616CAF53E2410BF8D6E4CBC96` |

1,442 markers per leg. All four analyze clean, and all seven contact classes occur in a
single run: blocked 343, dodged 249, brushed 223, whiffed 190, grazed 171, solid 159,
clean 105.

The analyzer recomputes the entire chain from canon — `quality_bands` for both the
thresholds and the delivered force fractions, `contact_classes` for the ordering — and
compares the round accumulator tick by tick against what the resolved classes should have
produced. It also checks the sealed card equals the sum of the banked rounds. Nothing the
Blueprint reports is trusted except as a claim to be checked.

### The first run failed, and it found a hazard in the shared authoring discipline

A1 came back with the accumulator disagreeing with canon, and the disagreement had a
shape worth reading rather than patching:

```
actor 0 tick 1: round accumulator reads 0, canon recomputes 1048576
actor 1 tick 2: round accumulator reads 576716, canon recomputes 157286
```

Tick 1's inputs resolve to **clean** under canon, and the Blueprint reported **clean** —
the pipeline was right. It then scored that clean punch as **nothing**. Tick 2 reported
brushed and scored it as grazed. Both halves individually correct, the whole thing
hashing perfectly, and the join between them wrong. This is exactly the defect class
Phase G was built to expose, and it appeared on the first run.

The cause: `RandomFloatFromStream` is a **pure** node that **mutates the stream**. A pure
node's chain can be evaluated more than once when it has multiple consumers, and each
evaluation draws again. Phase E's derived quality counter had exactly one consumer;
Phase G's scoring join added four more, and the class computation and the scoring ended
up reading different draws.

The fix is structural rather than a patch: the tick's four draws are now stored into
member variables on the execution chain, in order, and every consumer reads a variable.
The stream advances exactly four times per tick by construction. This is now **rule 7 in
`tools/engine/bp_authoring.py`**, the seventh entry in a list where every rule was bought
with a debugging session.

Phase E was re-run afterwards and still passes with 6,000 markers, zero verdict
mismatches and zero misses classified as hits. Its analyzer verifies each verdict against
that verdict's own reported inputs, so it remains valid evidence — but it predates rule 7,
and any new consumer added to that graph must materialize its draws first. That caveat is
recorded rather than left for someone to rediscover.

### What this establishes, and what it does not

Established: contact resolved by the canonical pipeline drives per-round scoring, the
accumulator banks and resets at each bell, and the card equals the sum of the banked
rounds — all reproducible across a full asset regeneration, and all recomputed from canon
rather than asserted. A blocked punch cannot score: `landed` is false for it, so the
weight gate returns zero regardless of which quality band its alignment matched.

Not established: this is still one actor resolving against proxy draws rather than two
fighters resolving against each other's real geometry, postures and frame data. No
attributes, no stamina, no knockdowns, no judging beyond a force sum. `match_flow`'s
entrance, break, count, doctor-check and post-fight segments remain unbuilt and named as
such. No gameplay is claimed (Rule 18).

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 14:12 UTC | END ] -->
