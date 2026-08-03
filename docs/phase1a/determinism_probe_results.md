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
