<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:35 UTC | START ] -->

# See it. Test it.

Written because the Director asked where any of this could be looked at, and the
honest answer was that it took knowing three scripts, a tag convention, and where
`sandbox\Saved\phaseM` lives. A thing you cannot look at without a runbook is a
thing nobody looks at.

Everything below runs from the repo root on the Windows box with UE 5.8
installed.

---

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ] -->

## Press Play on a 1-round match (integrated)

Open `sandbox\UppercutSandbox.uproject`, open
`/Game/ProjectUppercut/Maps/L_UppercutDevArena`, press Play.

`UUppercutFightSubsystem` defaults to **integrated 1-round** mode:

- Cards: `test_pressure_power` vs `test_range_timing` (complete Rule-10 fixtures)
- Thin observable policy (G2 rest/hold, G3 aggression-as-intent) — not the Phase Q LCG
- Round ends with knockdown/count **or** a sealed 10-point-must decision
- `P` dumps an integrated stream; check with `python -m tools.engine.prove_one_round`

Phase O is **not** held on G7. See `docs/decisions/OPEN_GATES.md`.

To force the old Phase Q distance-only session (for `prove_live_arena`):

set `bIntegratedOneRound = false` on the fight subsystem before StartFight.

Python instrument (CI / Linux):

```
python -m tools.engine.prove_one_round
python -m tools.uppercut_integrated.export_fight --out-dir /tmp/uc1r --rounds 1 --default-cards --round-seconds 180
```

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | START ] -->
Decision 0037 path: the integrated bout now reads `opponent_read` (defender
`reads` → readiness on evade timing and guard extents). Do not retune
`pressure_threshold` to chase connect rate.
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:13 UTC | END ] -->

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ] -->

## Press Play on it (Phase Q distance — historical)

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 22:40 UTC | arena start ] -->

Open `sandbox\UppercutSandbox.uproject`, open
`/Game/ProjectUppercut/Maps/L_UppercutDevArena`, press Play. Two fighters close
and open distance on canon's ring axis, throw punches, and miss when they throw
from the wrong band.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ] -->
**Trap:** if the viewport is an empty landscape / level named `Untitled`, you are
on the engine OpenWorld template — not the arena. Open
`/Game/ProjectUppercut/Maps/L_UppercutDevArena` (also the project default map).
Close Untitled; do not save it over the arena. With Fab + BoxingAttacks present,
Play spawns the cartoon ring and Manny/Quinn on the same FightSubsystem path;
cylinders remain the soft fallback when those packs are missing.
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ] -->

| Key | Does |
|---|---|
| `Space` | pause / resume |
| `.` | one tick |
| `,` | one second |
| `R` | restart, same seed |
| `N` | next seed |
| `[` `]` `\` | slower / faster / 1x |
| `P` | dump the round to `Saved\live\` as a marker stream |

The fight you are watching is the artifact the parity proof is taken against —
same canon reader, same loop, same stream format, not a runtime that agrees with
it. That claim is checkable:

```
python -m tools.engine.prove_live_arena        # ~2 minutes, needs UE
```

It drives the real subsystem inside a real world, through the same single-step
control the `.` key uses, and compares the dump to the contract byte for byte.

Phase Q is a fight about **distance**. With `bIntegratedOneRound=false` there is
no guard, stamina, damage, knockdown or round structure in the arena. The
integrated 1-round path (default) is documented above — Phase O is no longer
held on G7 (`docs/decisions/OPEN_GATES.md`). Full write-up:
`docs\implementation\live_dev_arena.md`.

To rebuild the map after changing the actors:

```
python -m tools.engine.make_dev_arena
```

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 22:40 UTC | arena end ] -->

## Look at it

```
.\tools\engine\show_me.ps1
```

One command, no arguments. It runs the rendered slice, saves dated screenshots
into `docs\visuals\`, and prints the marker-stream hash. Takes about 40 seconds.

```
.\tools\engine\show_me.ps1 -NoArena          # bare mannequins, no ring
.\tools\engine\show_me.ps1 -Seed 4250        # a different fight
.\tools\engine\show_me.ps1 -Ticks 10800      # a longer one
.\tools\engine\show_me.ps1 -KeepAll          # every frame, not just three
```

**It runs with the editor open.** Verified 2026-08-05. It does *not* rebuild —
see "if you changed the C++" below.

The pictures land in `docs\visuals\`, which is committed, so they are visible on
GitHub from any machine.

## What you are actually looking at

The current slice is two Unreal demo mannequins (Manny and Quinn) in a Fab
cartoon ring, playing back a fight the Python contract decided. Known and
unfixed, so you are not seeing them for the first time in a screenshot:

- **The far-left and far-right posts and rope lines are extra geometry** from the
  arena pack, sitting outside the ring proper.
- **The white blotch on the canvas** is the pack's own painted glove emblem, not
  a lighting or z-fighting fault. Diagnosed and confirmed 2026-08-04.
- **The fighters are demo mannequins**, not boxers, and their animation is the
  Fab boxing pack's In-Place clips scrubbed from sim state.
- **The lighting is a probe rig**, not a look. Black background, no crowd, no
  arena beyond the ring.

## Test it

```
python -m pytest -q                            # ~3 minutes
python -m tools.uppercut_validate.cli all      # canon validators, ~10 seconds
python -m tools.gen_status --check             # STATUS.md is not stale
python -m tools.gen_decision_index --check     # the decision index is not stale
```

All four must be clean before anything is pushed. CI runs the same four.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:12 UTC | edit: a hard-coded test count is a lie with a shelf life ]
     This line used to read "811 tests". It said 811 for long enough that an
     external audit named this file as stale documentation. The live count
     lives in STATUS.md, which is generated and CI-checked; a number typed by
     hand into prose has no such protection, so this file no longer carries
     one. -->
The current test count is in [STATUS.md](../STATUS.md), which is generated and
CI-checked. It is deliberately **not** repeated here — the last hand-typed count
in this file went stale and stayed stale.

### Prove the engine still matches the contract

```
python -m tools.engine.prove_core_range        # Phase Q, ~2 minutes, needs UE
python -m tools.engine.prove_core_evade        # Phase R, ~2 minutes, needs UE
python -m tools.engine.prove_live_arena        # the arena itself, ~2 min, needs UE
python -m tools.engine.golden --diff           # every pinned stream, no UE needed
```

The first runs the C++ commandlet three times and compares its marker stream to
the Python contract **byte for byte** — that is what "proven" means here. The
second compares the contracts against their committed golden files and, when
something has moved, prints the drift as a fight: which punch, at which tick,
with what result. Run the second constantly; it costs a second. Run the first
after touching either side of Phase Q.

### Watch the fight as numbers

```
python -m tools.engine.measure_contract_conversion    # what converts, and why
python -m tools.engine.measure_eligible_terms         # knockdown vs near-miss
python -m tools.engine.measure_contract_stamina       # where the pool goes
python -m tools.engine.measure_conversion_gap         # us against the reference
python -m tools.engine.measure_guard_expressiveness   # ten guards, four behaviours
```

Each prints a table and writes JSON into `sandbox\Saved\`. They read the
contract's own marker stream — none of them instruments the simulation.

### Run the reference simulator

```
python -m tools.uppercut_sim.batch
```

The balance instrument the canon numbers were originally swept against.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:14 UTC | edit: this claim is no longer true ]
     This paragraph used to end "the contract currently does not [reach a
     decision], which is the whole of the open Phase O question." That was true
     when written and false by 2026-08-09. Corrected rather than deleted, so
     the record shows the gap closed instead of quietly vanishing. -->
**Correction (2026-08-09):** it used to say the contract could not reach a
decision. It can. Over ten seeds at the shipped configuration, seven of ten
bouts now go to the cards and three end by referee stoppage — see Decisions
0036 and 0037 for the measurement and what remains wrong with it.

## Watch a complete fight

The integrated bout — policy, movement, stamina, evasion, guard, contact,
knockdown, count, referee, sealed judging, verdict — runs in Python and needs no
engine:

```
python -m tools.uppercut_integrated.export_fight --seed 4242
```

It writes a fight JSON plus the authoritative marker stream. The replay viewer
in `docs/fights/` opens the result in a browser. Unlike the Phase Q arena above,
this one *does* have guard, stamina, damage, knockdowns and round structure —
the arena is still the distance-only slice.

## Drive the editor from an agent

UE 5.8 ships Epic's own MCP server plugin, enabled for this project and proven
live on 2026-08-09. Runbook and the four non-obvious client facts:
[`docs/UNREAL_MCP.md`](UNREAL_MCP.md). Loopback only — it is reachable from the
machine running the editor and from nowhere else.

---

## If you changed the C++

```
# close the editor first - Live Coding holds the DLL and the build refuses
.\tools\engine\build_uppercut_core.ps1
```

Target is `UppercutSandboxEditor`, not `UppercutSandbox`; the monolithic game
target has never linked here. The script invokes UnrealBuildTool through the
engine's bundled dotnet rather than `Build.bat`, which wedges in its own
lock-file wait loop in this spawn context.

## Where things are

| | |
|---|---|
| UE project | `sandbox\UppercutSandbox.uproject` |
| C++ module | `sandbox\Source\UppercutCore` — seven commandlets and the render Director |
| Pinned streams | `docs\phase1a\golden\` — the exact bytes a port must reproduce |
| Levels | `sandbox\Content\{BoutWalk,FightWalk,PipeWalk,RangeWalk,StateWalk,Determinism}` |
| Screenshots | `docs\visuals\` |
| Run output | `sandbox\Saved\phaseM\` — marker streams, logs, all frames |
| Measurement JSON | `sandbox\Saved\*.json` |

The six levels are **evidence harnesses**, not a game: each holds one walker
actor that emits a marker stream so a determinism leg can be hashed. There is no
level you open and press play in yet.

The vendor content — `BoxingAttacks` (435 assets) and `FabImports` (131) — is
gitignored on purpose and restored from Fab, so a fresh clone looks empty and
your machine does not.

## What is proven, and what is not

**Phase R is the latest engine phase proven in C++** (2026-08-06:
`UppercutCoreEvadeCommandlet` reproduces its contract byte for byte at 4242/5400,
777/5400 and 4242/1200; Phase Q was proven the day before). Phases O, P and S
exist as Python contracts with tests and no C++ at all — and **Phase O is held
on gate G7**, the stamina economy. A `feat(core)` commit subject does not
mean an engine phase shipped — `STATUS.md` is the authority, it is generated
from the `PASS` headings in `docs/phase1a/determinism_probe_results.md`, and a
test enforces that it cannot name a contract-only phase.

So: the numbers you can run above are real and the pictures are real, and the
range and evasion pipelines now exist on both sides of the line, each agreeing
with itself to the byte. What has not met yet is the round itself — Phase O,
which carries the policy, the scoring and the knockdowns, and which is held on
G7. Closing the gap is the port of S (policy), the Director's ruling on G7, and
then the live runtime
(`docs/implementation/unreal_live_backend_integration.md`).

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:35 UTC | END ] -->
