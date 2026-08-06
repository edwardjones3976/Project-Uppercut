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

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 04:52 UTC | START ] -->

## Phase H — the C++ core scaffold (UppercutCoreProbe): PASS

**2026-08-04.** Decision 0012 slice item 3: the first C++ slice of the authoritative
fight core, proven by the same discipline as every Blueprint phase — analyzer built and
mutation-proven first (9 tests, committed at `3e08ff7` before a compiler existed on the
machine), implementation judged against it after.

**What ran.** `UppercutCore`, an Unreal C++ Runtime module in the sandbox
(`sandbox/Source/UppercutCore/`), with `UUppercutCoreProbeCommandlet`: canon bytes in
(`data/movement_model.json`, SHA-256 stated in the stream), the Phase D hysteresis walk
in pure integer arithmetic (explicit 32-bit LCG, 1e-4 fixed-point band bounds), and a
self-hashing marker stream out (FNV-1a 64). The same rule's **third independent
implementation** — Python reference, Blueprint VM, now C++ — from the same canon bytes.

**Toolchain.** VS 2022 Build Tools 17.14.37 (July 2026), MSVC 14.44.35207, Windows SDK
10.0.26100.0, .NET Framework SDK 4.8 — installed 2026-08-04 on the Director's explicit
license acceptance (runbook, "C++ toolchain for Phase H"). The staged source compiled
clean on the first build: 71 s, zero errors, zero warnings surfaced by UBT.

**The runs.** Seed 7777 × 400 steps: A1, A2 (independent processes), and A3 after a
**full rebuild** — `sandbox/Binaries` and `sandbox/Intermediate` deleted, module
recompiled from source, rerun. Seed 7778 × 400: B1.

    A1 sha256 0cb2cb647cd2f4e381633d946a33114a6a54a2850f0d19703a976658d9a6e5e0
    A2 sha256 0cb2cb647cd2f4e381633d946a33114a6a54a2850f0d19703a976658d9a6e5e0
    A3 sha256 0cb2cb647cd2f4e381633d946a33114a6a54a2850f0d19703a976658d9a6e5e0   (rebuilt binary)
    B1 sha256 c0f4709f5d65dca6be82d442e11ea6e40a40429487c9dfd7680beab80d0aa77b   (differs, as it must)

Analyzer verdict: **ok on all four** — and "ok" here is the strong claim, because the
analyzer recomputes the entire stream from canon in Python and compares **byte for
byte**, then re-checks the properties independently (band never moves more than one step,
hysteresis obeyed, stream self-hash valid, canon hash matches the local file). 167
transitions on seed 7777, 196 on seed 7778: the rule was exercised, not idled past.
Cross-language determinism is therefore not inferred from matching hashes alone — the
C++ and the Python produced **identical bytes** from identical canon, including
independently computed SHA-256 and FNV-1a values.

**One wedge, already known.** The first commandlet launch stalled in
`TurnkeySupport` spawning `Build.bat -Mode=ValidatePlatforms`, which hits Build.bat's
lock-file wait loop — the exact wedge `tools/engine/wedge_watchdog.ps1` was built for
during the Blueprint phases. The watchdog cleared it; no new rule needed, the old one
held. (Same lock loop bit the first manual build; invoking UnrealBuildTool directly
through the engine's bundled dotnet sidesteps the wrapper entirely and is now the
runbook's documented build path.)

### What this establishes, and what it does not

Established: the C++ pipeline the fight core will live in — canon file to deterministic
arithmetic to auditable evidence stream — reproduces byte-identically across processes
and across a full rebuild, and agrees with the Python reference to the byte. The module,
build path, run path, and analyzer discipline all exist and are proven.

Not established: everything that matters about a fight. This is one rule walking alone —
no fighters, no state, no collision, no cards. Slice item 4 (the two-fighter
authoritative loop in C++) is where the core starts being a core. No gameplay is claimed
(Rule 18).

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 04:52 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:25 UTC | START ] -->

## Phase I — the two-fighter authoritative loop (UppercutCoreLoop): PASS

**2026-08-04.** Decision 0012 slice item 4: where the core starts being a core. Two
fighters with authoritative state, one clock, decisions interleaved in fixed index
order, consuming **five canon files at once** (movement, condition, guard_evasion,
cpu_decision, moves — each SHA-256-stated in the stream). Analyzer first as always:
`tools/engine/analyze_core_loop.py`, mutation-proven by 8 tests before the C++ existed.

**What the loop executes**, in contract-defined integer arithmetic: positions on the
ring track with the rope zone, `rope_retreat_multiplier` zeroing a backward step on the
ropes, and the min-separation snap; footwork as boxing-steps stride × directional ×
high-guard mobility × the exhausted multiplier below the canonical stamina fraction;
band hysteresis driven by real separations rather than synthetic draws; the idle
stamina economy (regen minus guard hold cost) with move costs and clamps; commitment
from the move table's frames, a committed fighter taking no decisions; and Rule 12's
range gate — a jab pays and commits regardless, and is only *delivered* from its
authored band. One simplification is on the record in the contract itself: commitment
is startup+recovery flat; the reference engine's arm/chain/fatigue arithmetic ports
with the collision pipeline, not here.

**The runs.** Seed 4242 × 5,400 ticks (2,700 decision rows: 18 delivered jabs, 202
out-of-band whiffs, 669 steps, 1,578 held, 233 idles, 72 band transitions — every
branch of the decision surface exercised, including rope-blocked retreats and min-sep
snaps). A1, A2, then A3 after a **full rebuild**; B1 at seed 4243.

    A1 = A2 = A3   sha256 1642531f3eb95530…   (A3 from a rebuilt binary)
    B1 differs     sha256 9d36d13b68795b1e…

Analyzer ok on all four — byte-for-byte against the Python recomputation from canon,
plus independent property checks (band steps ≤ 1, separation never below
min_center_distance, stamina within [0, max], full action coverage, valid self-hash).
Second consecutive phase where the C++ compiled clean on the first build and passed on
the first run: the contract-first discipline is doing exactly what it was adopted to do.

**The float-conformance experiment — the finding that matters for everything after
this.** Alongside the integer core, the stream carries an instrumented probe: a fixed
`-`, `+`, `*`, `min` recipe over canon-derived doubles, 1,000 iterations, bit patterns
emitted every 100. Deliberately *not* a pass criterion — an experiment whose answer is
reported either way. The answer: **all 10 checkpoints bit-identical to CPython's
doubles**, through UE's default optimized MSVC codegen, including a multiply-add shape
that FMA contraction could have perturbed. This is evidence — not yet proof for every
expression shape — that the reference simulator's float arithmetic can port to the C++
core byte-comparably. The full port should still guard each new expression shape with
the same probe pattern, but the road is open and the first toll is paid.

### What this establishes, and what it does not

Established: the C++ core's structural skeleton — two actors, shared authoritative
state, fixed resolution order, an authoritative tick, multi-file canon consumption,
auditable per-decision evidence — byte-identical across processes and a full rebuild,
and identical to the Python reference recomputation. Plus the first recorded evidence
of C++/CPython float bit-identity on this machine and toolchain.

Not established: no collision resolution (a delivered jab meets no guard, no evasion,
no outcome), no condition or knockdowns, no judge, no policies — the decision stream is
an LCG schedule, not a mind. Slice item 5 (real movement and swept collision) is next.
No gameplay is claimed (Rule 18).

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:25 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:15 UTC | START ] -->

## Phase J — real movement and swept collision (UppercutCoreSweep): PASS

**2026-08-04.** Decision 0012 slice item 5: punches acquire geometry. The fist is an
authored extension profile (`data/pose_geometry.json`, new canon: schematic reference
pose in reach units, the 2D stand-in until real clips exist), sampled per tick, swept
as an interval, **live only during animation_model's active ticks** — startup is
telegraph, not threat, exactly as collision_model's `active_source` has declared since
step 5 — and evaluated against the defender's position AT THAT TICK, so footwork during
an opponent's startup genuinely changes what the active window meets. Eight canon files
consumed, each SHA-256-stated. Analyzer first: `tools/engine/analyze_core_sweep.py`,
mutation-proven by 10 tests including the lane laws as independent properties.

**The lane demonstration — the design promise as running geometry.** A guard plane
sits `plane_offset_ru` in front of the body and intercepts a height class only when
the posture's authored extent for the covering volume reaches one authored threshold.
high_guard is authored 0.95 over `guard_high`, 0.55 over `guard_body`; the threshold
is 0.6. Nothing anywhere says "body shots beat high guards." The run says it:

    jab_lead            132 thrown into range, 132 blocked   (head lane closed)
    body_straight_rear  114 reached the body,  114 landed    (body lane open)
    whiffed               8 at range                          (Rule 12 as geometry)

The core combat design rule — a guard protects lanes and exposes lanes — and Rule 4's
counterplay against passive high blocking fall out of posture data plus one threshold,
in C++, deterministically, with every contact's tip/plane/surface numbers in the
evidence stream.

**The runs.** Seed 4242 × 5,400 ticks: 2,954 evidence rows (2,700 decisions + 254
resolved punches; one punch in flight at the final tick, counted thrown and honestly
unresolved). A1, A2, A3 after a **full rebuild**; B1 at seed 4243 (269 resolutions).

    A1 = A2 = A3   sha256 b59b6ff35db25b61…   (A3 from a rebuilt binary)
    B1 differs     sha256 62de5ab295ab3ee0…

Analyzer ok on all four — byte-for-byte against the Python recomputation, plus the
independent lane laws (no jab through a closed lane, no body straight blocked by an
extent below threshold, no resolution outside an active window, landed regions equal
the move's leading target). Float probe: bit-identical to CPython again, all
checkpoints. Third consecutive phase passing on the first *correct* run — the one
defect en route was a PowerShell harness slip (an unquoted `-seed=` subexpression fed
seed 0 to all three runs; caught because A1=A2=**B1** is exactly what the discipline
exists to notice), not a C++ or contract error.

### What this establishes, and what it does not

Established: contact in the C++ core is now geometric — authored reach against real
positions decides whether a punch is blocked, lands, or whiffs, with the guard's
structure opening and closing lanes emergently. The animation frame-lock is consumed
(startup/active/recovery ticks from `animation_model`), and the whole thing remains
byte-identical across processes and a full rebuild.

Not established: no damage, condition, knockdowns, or cards flow from a landed punch
yet; one posture, two punches, depth-axis geometry with discrete height classes; no
evasion; decisions are still an LCG schedule. Slice item 6 — the four punches animated
on generic fighters — is where this stops being marker streams and starts being
something a spectator can see. No gameplay is claimed (Rule 18).

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:15 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:55 UTC | START ] -->

## Phase K — the first rendered slice (UppercutBoutDirector): PASS

**2026-08-04.** Decision 0012 slice item 6: the four named punches — jab, cross, lead
hook, rear uppercut — plus the proven body straight, on generic fighters, **on screen**.
A `UppercutRenderGameMode` + `AUppercutBoutDirector` build the whole scene from engine
primitives at runtime (no content assets, nothing to drift): floor, ring posts, two
fighters (cylinder torso, sphere head, sphere gloves), lights, a side-on broadcast
camera, into `/Engine/Maps/Entry`. The authoritative sim — Phase J's, widened to nine
actions — advances exactly one tick per rendered frame; the fighters' poses READ sim
state (the punching glove extends by the sim's own integer extension along its lane's
height); five screenshots per run at fixed ticks.

**The claim, and its proof.** Rendering must hold zero authority over the fight. The
proof is the same proof as every phase: the rendered run's marker stream, R1, is
**byte-identical to the Python recomputation from canon** (`analyze_render_probe.py`,
mutation-proven first, 6 tests), and R2 — a second full rendered run — is byte-identical
to R1:

    R1 = R2   sha256 b6f1c24b62671b8d…
    both analyzer-ok; float probe bit-identical to CPython, again

**The five punches, and the widened lane result.** 315 punches over 5,400 ticks at seed
4242: 112 blocked — every jab, cross and hook that reached the closed high lane; 41
landed — every body straight and **uppercut** that arrived, the uppercut coming up under
the high guard to the jaw exactly as `blockable_low` in the move table says it should
(the classic guard-splitter, emergent from the same one threshold); 161 whiffed at
range. The hook's depth-plane treatment is pose_geometry's NAMED simplification —
around-the-guard hooks arrive with lateral geometry.

**Gate item 5 unblocks.** "Visual speed readable enough for spectators" was untestable
while nothing rendered. Something renders. Screenshots are in
`sandbox/Saved/phaseK/shots_R1` and were delivered to the Director in-session; the
judgment of readability is his, not this record's. What the record can say: two
figures, their spacing, their gloves and their punches are distinguishable at 1280×720
from the broadcast angle, and the render runs the full 5,400-tick bout unattended in
about ninety seconds of wall clock.

**Wedges, again, and the pattern underneath them.** The editor's spawn of
`Build.bat` (this time `-Mode=QueryTargets`, previously `-Mode=ValidatePlatforms`)
wedges in Build.bat's own lock-file wait loop in this launch context. Two fixes are now
standard: pre-generate `Intermediate/TargetInfo.json` by invoking UnrealBuildTool
directly, and run the widened watchdog (kills any Build.bat cmd plus its PING sleeper)
alongside every editor launch. One asset lesson: `/Engine/BasicShapes/Capsule` does not
exist in runtime engine content in 5.8 — its Failed-to-find warning cost one render of
invisible fighters; Cube, Sphere and Cylinder all load.

### What this establishes, and what it does not

Established: the fight core's evidence pipeline survives a real renderer unchanged, on
the record; the slice's four named punches resolve through the swept-geometry contract;
and the project has its first picture — a fight a person can watch, produced by the same
deterministic arithmetic the analyzers judge.

Not established: readability is testable, not passed — that call is the Director's.
Presentation is deliberately crude (primitive shapes, two lights, no color grading, no
hit reactions, no crowd, no comedy). No damage, cards or verdicts flow yet. Slice item
7 is guard and slip; the reference sim's condition/knockdown arithmetic and the Judge
await their C++ port behind it. No gameplay is claimed beyond what renders (Rule 18).

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:55 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 08:05 UTC | START ] -->

## Phase L — guard and slip (UppercutCoreGuard): PASS

**2026-08-04.** Decision 0012 slice item 7: the defender stops being a static wall.
Three canon mechanisms enter the C++ core at once, analyzer-first as always
(`analyze_core_guard.py`, 7 mutation tests, proven before the C++ existed):

1. **Posture switching.** high_guard ⇄ tight_elbow — the mirror pair the DATA picks:
   at the one interception threshold (0.6), high_guard (0.95/0.55) closes the head and
   opens the body; tight_elbow (0.55/0.95) is the inverse. Lane coverage is per-fighter
   and dynamic; mobility and hold cost follow the current posture (posture_economy,
   hold charged only when uncommitted, as authored). The lane rock-paper-scissors is
   live: the punch that beats you is decided by the structure you are holding *now*.
2. **The slip.** `slip_lead` from the evasion table and the move table together: cost
   0.8, startup 3, a five-tick active window, commit 15. An ARRIVING head-height punch
   during the window resolves **dodged** — evasion outranks guard
   (`evasion_economy.outranks_guard`, the pipeline's tier order, now geometric). Body
   punches ignore it entirely: "beaten_by body_shot", emergent.
3. **Committed defense.** `guard_extent_multiplier_while_committed` (0.6) scales the
   defender's extents at evaluation time — 0.95 × 0.6 = 0.57 < 0.6 and the closed lane
   opens. A fighter caught inside their own commitment can be hit through the guard
   they are still nominally holding: **the counterpunch, from canon numbers alone.**
   108 such landings in the canonical run, each carrying its `c` flag in the stream.

Named simplifications, in the contract itself: posture-switch economics are not
authored in canon (the switch commits one decision interval at zero cost — the
contract's number, flagged for canon when guard work deepens); offense pricing per
posture and the slip mistime penalty port with the fuller pipeline; roll_under waits.

**The runs.** Seed 4242 × 5,400 ticks: 2,977 evidence rows — 277 punches (17 blocked,
244 landed, 13 whiffed, 3 dodged), 61 guard switches, 55 slips, both postures held by
both fighters, every action taken. A1, A2, A3 after a **full rebuild**; B1 at 4243.

    A1 = A2 = A3   sha256 cb14f6e35c527451…   (A3 from a rebuilt binary)
    B1 differs     sha256 924a0142f45274a4…

Analyzer ok on all four — byte-for-byte against the Python recomputation plus the
defender-state-aware lane laws (no dodge outside a slip window or of a body punch, no
head punch blocked through an active slip, the counter window proven non-vacuous).
Float probe bit-identical to CPython, again. Fourth consecutive phase: compiled clean
first build, passed first run.

**An emergent worth naming:** landed jumped from Phase K's 41 to 244 — not a bug, a
consequence. Eleven actions mean fighters spend more time committed (a slip commits 15
ticks, a switch 4), and committed defenders' guards degrade, so a bout full of
structure-churn gets hit more. Defence spam is self-punishing by geometry — Rule 4's
philosophy arriving without a single anti-spam rule being written.

### What this establishes, and what it does not

Established: dynamic per-fighter lane coverage, a frame-locked evasion that outranks
guard, and the committed-defense counter window — all from canon data, all
byte-identical across processes and a full rebuild, all identical to the Python
recomputation.

Not established: still no damage, condition, knockdowns or cards from a landed punch;
one evasion of four; no referee or judge in the C++ core yet; decisions remain an LCG
schedule. Slice item 8 — visible stamina and condition — is where landing starts to
matter. No gameplay is claimed (Rule 18).

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 08:05 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | START ] -->

## The mannequin visual pass — real boxing motion under the Phase K proof: PASS

**2026-08-04.** The rendered slice stops being primitives. Two UE5 mannequins now
fight in `AUppercutBoutDirector`, animated by the Director's purchased boxing pack
(PAKPROD *Fighting Animations - Boxing*, audited in
`docs/phase0/asset_audits/2026-08-04-pakprod-fighting-animations-boxing.md`), and the
whole point of the exercise is what did **not** change.

### The claim

Putting real animation on screen is exactly the moment a presentation layer starts
quietly owning the fight: a root-motion step nudges a fighter, an animation's own
duration becomes the punch's timing, a blend eats a frame. So the pass was run as a
falsification test, not a feature. The stream is the same stream:

    mannequin R1  sha256 b6f1c24b62671b8dc81b37057f851f33e075f9280d34b68f5cdcc346c0276bda
    mannequin R2  sha256 b6f1c24b62671b8dc81b37057f851f33e075f9280d34b68f5cdcc346c0276bda
    Phase K R1    sha256 b6f1c24b62671b8dc81b37057f851f33e075f9280d34b68f5cdcc346c0276bda
    Phase K R2    sha256 b6f1c24b62671b8dc81b37057f851f33e075f9280d34b68f5cdcc346c0276bda

Four runs, two of them from before any of this existed, **byte-identical**: 2,700
decision rows, 314 punch rows, analyzer-ok on both new streams, float probe again
bit-identical to CPython at all ten checkpoints. The fight did not notice that it
grew a body. That identity is the whole evidence: *rendering holds zero authority*
stops being a design intention and becomes a measured property that survived
contact with a real animation stack.

### What the two rules were

**In-Place clips only.** The pack ships root-motion variants of every step, and they
are the better-looking option in isolation. They are rejected on principle: a
root-motion step would let an animation move a fighter, and where a fighter stands
is the sim's to own. The pack's `Root/` folder is deliberately unconsumed.

**Clip time is a function of sim state, never of DeltaSeconds.** Nothing here plays.
Each clip is *scrubbed* to the fighter's own progress through the move — his age in
the move over his committed frames — so a twelve-frame jab shows a whole jab
regardless of what duration the vendor authored. Our punch frames are the design;
theirs is a shape to borrow. The idle loop indexes off the sim tick, and its
two-fighter offset is the fighter's *index*, not a random number, because nothing in
presentation may touch the RNG. A dropped frame therefore moves nothing.

### What the picture shows that the primitives could not

The reaction is chosen by **the lane the punch arrived in, not by which punch it
was**: a punch stopped in a closed high lane plays a high block, a punch landing low
plays a body hit. The guard model is now something an audience watches rather than
something a stream reports — the uppercut coming up under a closed high guard and
the body straight going under it are the same fourteen and twenty-seven landings the
analyzer counts, with bodies attached.

Screenshots: `sandbox/Saved/phaseM/shots_R1` (five fixed ticks, as Phase K). Two
mannequins, correct scale and facing, in recognisable boxing stances at the
broadcast angle; delivered to the Director in-session. Readability remains gate item
5 and remains **his** call, not this record's.

### Method notes worth keeping

The visual pass was planned as Mixamo → IK Retargeter → Manny. It was not needed:
reading the pack's asset headers showed every clip already referencing
`SK_Mannequin`, so the retarget step — and its whole error surface — disappeared.
The Mixamo set stays audited and on disk as the fallback library and as the source
of the knockdown motions slice item 9 will need.

One build lesson, now in `tools/engine/build_uppercut_core.ps1`: build the
**editor** target. Every phase so far runs through the editor binary — commandlets
natively, the rendered slice via `UnrealEditor.exe -game` — and the monolithic
`UppercutSandbox` game target has never been linked here; it currently fails with
nine unresolved Core externals. That is a packaging job, not an evidence blocker,
and it is better to know now than at ship. Both the build and the run are scripts
now (`run_render_probe.ps1`), because a run you cannot repeat exactly is not
evidence — and this pass needed the same run repeated four times to say anything.

### What this establishes, and what it does not

Established: the fight core is indifferent to its presentation, measurably, with a
real animation stack attached; the project's first content reuse is done and audited
end to end; the lane model is visible.

Not established: no damage, condition, knockdown or card flows from any of this —
the mannequins take a body hit and are unharmed, because the core has no harm yet.
No stance (SOUTHPAW is bought and unused until stance enters canon). No ring, gloves,
crowd, sound or comedy. Presentation quality is placeholder tier by intent. Slice
item 8 — visible stamina and condition — is next, and it is where landing starts to
matter. No gameplay is claimed (Rule 18).

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | START ] -->

## Phase N — visible stamina and condition (UppercutCoreCondition): PASS, with a finding

**2026-08-04.** Decision 0012 slice item 8: landing starts to matter. Phase L's
guard-and-slip core gains the condition layer canon has carried since step 8, port
run analyzer-first as always (`analyze_core_condition.py`, 15 mutation tests, proven
before the C++ existed).

Four canon mechanisms enter the core at once. Per-region condition accumulates from
delivered force against each region's own capacity — no generic pool, Rule 14.
Delivered impact is derived from what a punch **cost to throw**, normalized over the
punch table's own stamina range, so a jab accumulates and an uppercut ends nights
without any per-move power field existing to be abused. Torso condition scales idle
stamina regeneration down toward 0.35, which is the moment body work stops being
cosmetic and becomes the drainer's win condition. And arm condition — fed by
**blocked** force, because blocking is not free — scales guard coverage extents
toward 0.55.

That last one changes the shape of the code, not just its numbers. Phase L could
compute each posture's covered lanes once at load. Phase N cannot: the arms wear
down, so the same guard covers less as the fight goes on, and coverage becomes a
per-punch, per-fighter, per-tick evaluation against pose_geometry's one interception
threshold.

### The proof

    A1 = A2 = A3 (after a full module rebuild)
        sha256 88af6f3011b93c12540ead0c016062425e20abf9c7cda994322d1a98c14ddc37
    B1 (seed 4243)
        sha256 cf94d6440c79215e87e809be0ec0a58f15b4ed97b319a9ee453f274caae807f7

All four streams analyzer-ok — which is byte-equality with the Python recomputation
from canon, not a similarity score. 2,700 decision rows, 2,700 condition rows, 277
punch rows at seed 4242. The float-conformance probe is again bit-identical to
CPython at all ten checkpoints, through MSVC's optimizer, for the sixth phase
running.

### The finding: an authored mechanism that a real fight cannot reach

Building the guard erosion exposed that it is effectively unreachable at canon's
current coefficients, and the arithmetic is short enough to state in full.

Opening high_guard's head lane needs its effective extent below the 0.6 interception
threshold. The extent is 0.95, and arm damage scales it by 1 − 0.45f where f is arm
condition as a fraction of capacity. So 0.95 × (1 − 0.45f) < 0.6 requires **f ≥
0.819** — the arms must be at 82% of capacity. A blocked punch delivers impact × 0.5
into each arm: between 0.225 and 0.412 against a capacity of 100. That is roughly
**243 blocked punches on one fighter** to break his guard once.

This probe blocks about one punch per 430 ticks. The lane first opens at **216,000
ticks — an hour of continuous fighting.** A twelve-round bout is about 130,000 ticks
of round time, and `damage_regions` gives arms 0.15 recovery between rounds, which
this phase does not yet implement and which would push it further out of reach
still.

So the mechanism is correct, live, and proven — the H1 run at 216,000 ticks opens
lanes 235 times and the analyzer confirms every one of them landed through a lane
that was covered when the arms were fresh. But at these coefficients no player will
ever see it. Canon's own note says this is "how sustained pressure opens a guard
that never drops — the passive blocker's answer arrives through boxing rather than a
rule (Rule 4)". At 243 blocked punches, the passive blocker has no answer arriving.

**This is the Director's tuning call, not the analyzer's.** What the record can say
is that it is now measurable: the horizon is pinned by a test that fails if a canon
edit moves it, so the number cannot rot quietly. The obvious levers are
`arm_damage_fraction_of_blocked_force` (0.5), `guard_extent_multiplier_at_full_arms`
(0.55), and the arms' capacity; the requirement that the mechanism be reachable
inside a bout is not a tuning opinion.

### Two smaller observations from the same runs

**Head and jaw saturate in ninety seconds.** By the end of a 5,400-tick run both
fighters are at capacity in the head, because nothing consumes accumulated condition
yet — no knockdown, no stoppage, no between-rounds recovery. That is slice item 9's
work, and until it lands, "accumulated condition" is a number with nowhere to go.

**torso_lower never takes a hit.** The slice's one body punch,
`body_straight_rear`, names `torso_upper` as its leading target region, and the
probe applies force to the leading region only. Nothing in the slice's move set
reaches the lower body. Not a defect — an observation that the move set, not the
region model, is what is narrow.

### What this establishes, and what it does not

Established: condition is per-region and canon-driven in the C++ core; force is
priced by commitment; body work slows the tank; guard coverage is a live evaluation
rather than a load-time constant; and all of it reproduces byte-for-byte across
processes and a full rebuild.

Not established: no knockdown, no count, no stoppage, no cards, no between-rounds
recovery, no attributes (every attribute-scaled coefficient is the empty card's 1.0,
Rule 10), and every landing is graded `solid` because grading needs an alignment the
core does not compute yet — all four are named simplifications in the contract, not
silent gaps. Slice item 9 is one rendered round with knockdown, decision and
stoppage. No gameplay is claimed (Rule 18).

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:40 UTC | START ] -->

## Phase O — a round that can end: CONTRACT WRITTEN, PHASE HELD

**2026-08-04.** Decision 0012 slice item 9. The contract for knockdowns, the
count, stoppage, rounds and the decision was written first, as every phase is
(`analyze_core_round.py`, 12 tests). It then **refused its own stream**, and the
C++ was not written. This record exists because that is the correct outcome, not
a failure to deliver.

### What the contract covers

Knockdown from observable state alone — canon's pressure product of delivered
force, accumulated jaw and head condition, stamina fraction, whether the defender
was caught inside his own commitment, and how open the lane was. No dice: there is
nowhere in the expression a random number could enter, and the analyzer checks the
arithmetic rather than trusting the claim. The mandatory eight count at canon's
480 ticks. Partial relief on rising — condition and stamina both, because the count
buys clarity and never a fresh fighter. Stoppage on three knockdowns in a round or
four in the bout. Rounds, the corner's partial recovery, 10-point-must cards, and a
verdict — with the cards sealed until the bout ends and the analyzer failing if a
card value appears anywhere before the verdict line (Rule 3).

### The finding that held the phase

    24 seeds swept:  stoppages 24 (100%)  decisions 0 (0%)  stopped in round 1: 24

Canon's knockdown block declares `decision_path_must_survive: true`. Under this
contract it does not survive at all. Every bout ends inside the first round,
typically inside thirty seconds, on the three-knockdown rule.

The cause is not the threshold. It is **Phase N's named simplification becoming
load-bearing**. Every landing in the C++ slice is graded `solid`, because grading
needs an alignment the core does not compute yet. In Phase N that was harmless —
grading only fed accumulation, and accumulation had nowhere to go. In Phase O it
feeds knockdown pressure, and canon's 0.57 threshold was swept against the
reference simulator, where most landings arrive brushed or grazed and carry a
fraction of solid force. Grade everything solid and the threshold stops being a
line and becomes a floor.

The slice's high landing rate compounds it: with defenders committed most of the
time, Phase N already measured far more landings than blocks, so nearly every
punch that arrives is both landing *and* graded at full solid force.

### Why the C++ was not written

Writing it would have produced a faithful implementation of a contract that
provably violates a canon invariant — a phase that passes its own byte-comparison
while every bout it simulates ends in round one. The analyzer-first discipline
exists precisely to make that discovery cost a contract instead of a phase, and
here it did: the finding arrived before a line of C++, from a Python sweep that
took under a second.

**Slice item 9 is held.** The first diagnosis was contact-quality grading, and it
was half right — see the follow-up immediately below, which built it and found the
real blocker underneath.

### Grading built, and the blocker it uncovered

Contact quality is now in the contract, ported from the reference simulator rather
than invented: an alignment draw at contact, reduced by `stamina_gate`'s exhaustion
penalty, dispatched through `collision_model`'s own four bands (brushed 0.15,
grazed 0.40, solid 0.75, clean 1.00). Canon's pressure formula grades only solid
and clean, so brushed and grazed shots now accumulate without dropping anybody —
which is exactly what the bands are for. Landings distribute properly: in the
canonical round, 10 brushed, 14 grazed, 11 solid, 8 clean.

**It did not revive the decision path.** Still 24 of 24 seeds stopped in round one.
And the run says why in one number:

    blocked = 0

Zero blocks in a full round. Phase N managed 17 in half that time; here the guard
never works at all. The cause is structural, not numeric. Our fighters are
committed on roughly 740 of every 800 decision ticks, and `committed_defense`
multiplies a committed defender's extents by 0.6 — which puts high_guard's 0.95
head lane at 0.57, under the 0.6 interception threshold. Against a **hard
geometric threshold**, "committed" therefore means "guard entirely absent," every
time, for almost the whole fight.

The reference simulator does not have this problem because its guard stage is
**probabilistic**: it blocks with chance `extent × 0.55`, so a committed defender
still catches a share of what comes. Our pipeline replaced three of the reference's
four random draws with geometry — sweep, evasion and guard — which is a strictly
better determinism story and, at the guard stage, went one step too far. A
threshold with no tolerance turns a graded defensive state into a binary one.

**So the real next item is the defensive pipeline, not the knockdown numbers.**
The choice is a design question and belongs to the Director rather than to this
contract: either committed defense should degrade coverage rather than erase it
(a softer multiplier, or a threshold with a partial-block band beneath it), or
guard interception needs the tolerance the reference gets from its dice. Both are
expressible without inventing anything; they are different statements about what
being caught mid-punch should cost.

Nothing here says canon's 0.57 knockdown threshold is wrong. It says the threshold
still cannot be judged, because it is being measured against a fighter who is never
defending.

### What this does not say

It does not say canon's threshold is wrong. It says the threshold cannot be judged
against a model that grades every landing at full force, so tuning it now would be
tuning against an artifact — the same trap the external review named in its own
warning about tuning subsystems before their consequences exist. The Director's
call on the guard-erosion horizon has the same shape and should probably be taken
together with this one.

The contract, its tests and the finding are committed and standing. When grading
lands, `test_the_decision_path_is_currently_dead` fails on purpose and forces this
record to be rewritten rather than quietly outgrown.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:40 UTC | END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 03:20 UTC | Phase O status, third revision START ] -->

### Third revision: the guard was fixed, the phase is still held, and the reason is now a number

**2026-08-05.** Two things above are now out of date and are corrected here
rather than edited away.

**The zero-blocks problem is solved.** The Director's per-hand mechanic replaced
the whole-body dimmer: canon's 0.6 `committed_defense` multiplier applies only to
the lane the defender's own hand vacated, derived from the height class of the
punch he himself threw. No new coefficient was invented. Blocks across the
24-seed sweep went from 0 to **853**. The guard works.

**The decision path is still dead, and not for any reason previously named.**
Six hypotheses were tested and buried after this section was written — contact
grading, CPU policy, difficulty tiers, decision cadence, commitment frames, and
the posture hold cost. Four of those were buried on a confounded metric (bout
totals compared across bouts that all end on the three-knockdown rule) and had to
be re-measured; when they were, cadence and commitment turned out to be strongly
connected to the clock, spanning 1.88× and 2.18× in time-to-stoppage.

What no dial moved, in any sweep, is **conversion**: knockdowns per landing
eligible to cause one sits at 0.25–0.31 regardless of tier, cadence or
commitment. That is what holds the phase, and it can now be stated as arithmetic
instead of a hypothesis:

    a bout reaches the cards at            32,400 ticks (3 x 10,800)
    the furthest any dial pairing reaches   7,049 ticks (22% of it)
    eligible landings in a full bout          ~216
    conversion required for a decision      0.0139
    conversion the model produces           0.2654
    the gap                                  19.1x  (6.6x at the extreme corner)

**Phase O is held on a conversion problem, not a pacing one.** The surface where
the fix has to live is `kd_threshold`, the pressure terms feeding it, and the
condition erosion that inflates them — not the volume side of the model, which is
where every one of the six dead hypotheses was looking. Full workings in
`docs/development-log/2026-08-05-the-dials-were-never-inert-and-the-blocker-has-a-number.md`
and `tools/engine/experiment_decision_path.py`.

This does not say canon's 0.57 threshold is wrong either. It says the threshold
is now the only remaining candidate that has not been eliminated, and that it can
finally be judged, because the fighter it is measured against is defending.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 03:20 UTC | Phase O status, third revision END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 13:30 UTC | Phase O status, fourth revision START ] -->

### Fourth revision: it is not the knockdown model, and it is not one number

**2026-08-05, later the same day.** The third revision above named `kd_threshold`,
the pressure terms and condition erosion as "the surface where the fix has to
live." **That is wrong and is withdrawn.** Four more phases were built after it,
and every one of those three was eliminated:

The threshold would have to sit at **1.0268** for a bout to reach the cards —
1.80× canon's 0.57, above the 99th percentile of observed pressure and near the
observed ceiling of 1.1262. That is not a higher bar, it is knockdowns switched
off. And the reference simulator meets `decision_path_must_survive` in **20 of 24
bouts** using the same 0.57. The threshold was never mistuned.

What was actually missing was a *pipeline*, in three parts, each now contracted:

- **Phase Q, range** — `movement_model.range_bands`, footwork, the ring track.
  Closed four defects: inert step actions, `uppercut_rear` landing 0 of 532,
  `hook_lead` landing from the wrong band, and nothing ever missing.
- **Phase R, evasion** — `guard_evasion_model.evasions`, geometric, no dice.
  Closed the accuracy factor: connect rate 60% → 41–46% against the reference's
  42.4%.
- **Phase S, policy** — canon's difficulty tiers, and the distinction between the
  decision interval (4 ticks) and per-tier reaction time (6–20). Nobody can react
  to a 4-frame jab; only a champion answers a cross.

**Phase O remains held**, and the reason is now three canon *quantities* rather
than any model: a step priced twice 4.55× apart, an `aggression_bias` roughly 7×
too high, and nothing anywhere authoring "do nothing." All three are Director
calls and are set out in
`docs/plans/2026-08-05-three-canon-quantities-decision-packet.md`.

Nothing further should be built on the current stamina numbers until the first of
those is answered. The phase contracts and their 641 tests are unaffected: they
encode rules, not quantities.

**SCOPE, stated plainly because the commit subjects invite the wrong reading.**
Phases Q, R and S were, when this paragraph was written, **contracts and
measurements only. No C++ was written for any of them.** Superseded for Q later
the same day: `UppercutCoreRangeCommandlet` was written and proven, and the
section at the end of this file records it. **R and S remain contracts only.** Their commits are labelled `feat(core)` in the repository's usual
style, and that label does NOT mean an engine phase was proven — under this
repository's own discipline a phase is proven when the C++ artifact's marker
stream is byte-identical to the analyzer's across a full rebuild, and at the time
of writing none of Q, R or S had been through that — Q since has, R and S have
not. `STATUS.md` is generated from this file's `PASS` headings and should be read
in preference to any commit subject. Rule 18 governs here — design documentation is not implementation evidence —
and this note exists so nobody has to infer the distinction from a label.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 13:30 UTC | Phase O status, fourth revision END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:50 UTC | Phase Q proof START ] -->

## Phase Q — the fight gets a distance (UppercutCoreRange): PASS

**2026-08-05.** The contract written earlier today became an engine phase.
`UppercutCoreRangeCommandlet` reproduces `analyze_core_range.expected_stream`
byte for byte, which under this repository's discipline is what "proven" means.

Phase Q is the range pipeline the core had been missing while it implemented the
reference simulator's resolution pipeline: five contiguous bands with 0.05 ru
hysteresis, a 0.22 ru stride delivered over several ticks by canon's 0.14 ru
per-frame displacement cap, a 0.28 ru body floor, the ring as a bound with
`rope_retreat_multiplier` 0.0, and Rule 12's range gate tested at **throw** time.

### The proof

    seed 4242, 5400 ticks
        sha256 f040fced729434ce0324f131c804b17fa96258910f0ef10db12e47afb8e508d1
    seed 777, 5400 ticks
        sha256 3fc7092dcff9f9f85460c9f0a6e741b5148de1d5e27c40ce2e2f6a20538e6581
    seed 4242, 900 ticks
        sha256 650bb52c1409861e3c2c509bbe75e24df27bb686773e88985651767f647a6326

Each is byte-equality between the commandlet's stream and the Python
recomputation from canon — not a similarity score, and not a trailer comparison.
Each stream is then read back cold by `analyze_core_range.analyse`, which
re-derives the trailer from the rows and re-checks the invariants (nothing moves
further than the cap in a tick, separation never falls inside the body floor, no
landing is recorded from a band the move does not declare, no band is skipped
without passing through the one between). Zero errors on all three.

Re-run it with `python -m tools.engine.prove_core_range`. The pinned bytes for
the long run are committed at `docs/phase1a/golden/phase_q_4242_5400.stream`, so
a contract edit that would break this parity is caught by the ordinary test
suite, with no engine and no two-minute wait.

### What the proof says about the fight

At seed 4242 over 5400 ticks: 594 decisions, 343 punches, **111 landed, 231
whiffed on the band, 1 whiffed on reach**, 90 band transitions, 16 body clamps,
one rope-blocked retreat, separation ranging from the 0.28 floor out to 2.00 ru.

Two thirds of all punches are thrown from the wrong band and travel their full
arc into empty air. That is not a defect in this phase; it is the defect this
phase makes **visible**, and it is the same thing measured earlier today as
`uppercut_rear`: 532 thrown, 0 landed, from a mid-range stance that had been
frozen since Phase H. A flat nine-way draw has no idea where it is standing. What
happens to that number when a policy that can read the band chooses instead is
Phase S's business, and the two contracts now exist side by side to answer it.

### The finding: the band gate is doing nearly all of the work

The gate and the geometric tip-versus-surface test are both applied, and the
stream says the band is by far the tighter of the two: in 5400 ticks exactly
**one** punch passed its band and still failed geometrically —

    P|1104|1|cross_rear|whiffed|reach|11|19860|19120|mid|1

a rear cross thrown legally from mid, whose fist finished 0.074 ru short of the
opponent's surface. Canon says why in `pose_geometry.fist.profile_note`:
extensions are authored to sit just under each move's band ceiling plus body
reach. So the two tests are meant to agree almost everywhere, and where they part
company the geometry is the stricter one at the top of a band.

Worth stating plainly because it would be easy to conclude the opposite: this is
**not** an argument for deleting the geometric test. A port that checked only the
band would be right 342 times in 343 and wrong in the one case that matters —
the case where a fighter is at the far edge of a legal band, which is exactly
where a boxer's judgement of distance is supposed to be tested.

### Scope, and why this pin will survive the open gates

This phase reads four canon files and no more: movement, moves, animation and
pose geometry. There is deliberately **no stamina, no guard, no condition and no
damage** in it. Those belong to N, L and O, which are already proven, and a
contract that re-implements a proven phase is a second place for it to be wrong.

The load-bearing half of that decision is G1. The step cost is priced twice in
canon, 4.55× apart, and that is a Director call. A Phase Q stream that spent
stamina would have to be re-blessed the day G1 is ruled on, for a reason having
nothing to do with range — and a port proven against a stream that moves for
unrelated reasons is not really proven. This one does not move.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:50 UTC | Phase Q proof END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 02:10 UTC | Decision 0014 re-proof START ] -->

## Re-proof under Decision 0014 — Phases K, N and Q, 2026-08-05

Not a new phase. A **re-run of three proven ones** after a canon ruling moved the
ground under them, recorded here because a pin that is edited rather than
re-earned is worse than no pin at all.

Decision 0014 (gate G1) repriced ordinary movement by displacement. Three step
entries in `data/moves/generic_sandbox_moves.json` changed, and every phase that
hashes that file into its marker stream header therefore produced a different
stream — Phase K, Phase N and Phase Q. **None of their fights changed.** Phase Q
spends no stamina at all; Phases K and N read the table but were re-run against
the same repriced canon on both sides. Only the hashes moved.

Each was re-run and re-compared byte for byte:

    Phase N   UppercutCoreCondition, seed 4242, 5400 ticks     identical
              88af6f3011b93c12540ead0c016062425e20abf9c7cda994322d1a98c14ddc37  (2026-08-04)
           -> 7b2b90001b541b8e145ab4fe501de15e45b3780b3c1e821a866a3b4786cea1ff  (2026-08-05)

    Phase K   UppercutRenderGameMode, seed 4242, 5400 ticks    identical
              b6f1c24b62671b8dc81b37057f851f33e075f9280d34b68f5cdcc346c0276bda  (2026-08-04)
           -> 4826e82c532b98e481080b8603321e2e406c4f706681361b7a1996ff153b36ce  (2026-08-05)

    Phase Q   UppercutCoreRange, three runs                    identical
              4242/5400  32fb81853e8e961525664ecd98fc0f39fae50d2a184769457e6151af66b22faf
               777/5400  02f3832ed95e77e75ff2166cac62baa1bd973aa43f3662041517c159bbd47360
              4242/900   b8acb84ee9c1eaefd1c0575c8794abb9825506e632e13fc39edb438418d9a006

`tests/test_phase_evidence_pins.py` carries the new hashes with the superseded
ones beside them.

### A correction, made where it will be read

When Phase Q was ported earlier the same day, its record claimed the pin "will
survive the open gates" because the slice spends no stamina. **That was too
strong**, and the Phase Q golden failed within hours of being written.

The behaviour claim was right; the bytes claim was not. Phase Q reads the move
table for range bands and hashes it, so a change to a step's *price* — a field
Phase Q never reads — still moved its stream. The distinction that survives is:
a canon ruling on stamina cannot change the Phase Q **fight**, but any edit to a
file Phase Q hashes will change its **stream**.

This is the pin behaving exactly as designed. It failed the moment canon moved,
which is the alarm that says *re-prove the port before re-blessing* — and that is
what happened here rather than a quiet regeneration.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 02:10 UTC | Decision 0014 re-proof END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 13:30 UTC | Phase R proof START ] -->

## Phase R — the head is not where the punch is going (UppercutCoreEvade): PASS

**2026-08-06.** `UppercutCoreEvadeCommandlet` reproduces
`analyze_core_evade.expected_stream` byte for byte.

Canon authors evasion **geometrically**, which is why this phase adds no die.
Each evasion has a kind, an active window in ticks, a set of regions it
**vacates**, and a list of things it is **beaten by**. The whole rule is canon's
sentence rather than the port's:

> During an evasion's active window a punch aimed at a vacated region finds
> nothing there — unless the punch is one the evasion is authored to be beaten
> by, in which case it lands into the movement.

That second clause is the project's core design rule applied one level out. A
guard is a structure that protects some lanes and exposes others; an evasion is
the same object in motion. A roll that beat the uppercut would be a strictly
better guard rather than a different one.

### The proof

    seed 4242, 5400 ticks
        sha256 f450d2f678fb464aca0e59960fcc0c692c213f6fb75de27a9056f53412912523
    seed 777, 5400 ticks
        sha256 4b8d38276da032f71d7577f0ea92c845fe2fd80e420676976c3026e81444aec0
    seed 4242, 1200 ticks
        sha256 4aae2b77657989bab82e39e132a12c5e323ed118127c7b8707fc670235cd8738

Byte-equality against the Python recomputation, not a similarity score. Each
stream is then read back cold by `analyze_core_evade.analyse`, which re-derives
the trailer from the rows and re-checks the invariants — a dodge only ever in a
vacated region, never against a punch the evasion is beaten by, and every
non-dodge recorded as an arrival. Zero errors on all three.

Re-run with `python -m tools.engine.prove_core_evade`. Pinned at
`docs/phase1a/golden/phase_r_4242_5400.stream`.

### The telegraph is free, and that is the interesting part

The reference simulator needs a multiplier —
`telegraph.evasion_gain_per_startup_frame` — to make slow punches more
dodgeable, because its evasion is a die rolled at contact. Here a slip is five
ticks of real time and an 11-frame overhand spends longer in flight than a
4-frame jab, so a slip thrown at the same moment is far likelier to still be
active when the overhand arrives.

**Nothing computes that.** The defender is not buffed and the slow punch is not
nerfed; the slow punch is *seen*, which is exactly what canon says a telegraph
is for. The contract refuses a canon in which every punch spends the same time
in the air, because that is the canon in which the telegraph would stop being
free and would need a coefficient.

### Scope, and why this pin should be stable

Three canon files and no more: guard/evasion, moves, animation. **No separation
and no geometry** — whether a fist reaches is Phase Q's contract, proven on
2026-08-05, and re-implementing it here would be a second place for it to be
wrong. **No guard** — `outranks_guard` is true, so a dodged punch never reaches
the guard stage. **No stamina** — gate G7 is open on the stamina economy, and a
slice that spent stamina would need re-blessing the day it is ruled on for a
reason having nothing to do with evasion.

One caveat learned from Phase Q and stated here rather than discovered later: a
canon ruling on stamina cannot change the Phase R **fight**, but any edit to one
of the three files Phase R hashes will change its **stream**.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 13:30 UTC | Phase R proof END ] -->
