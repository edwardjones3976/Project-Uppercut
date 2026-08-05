<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:35 UTC | START ] -->

# See it. Test it.

Written because the Director asked where any of this could be looked at, and the
honest answer was that it took knowing three scripts, a tag convention, and where
`sandbox\Saved\phaseM` lives. A thing you cannot look at without a runbook is a
thing nobody looks at.

Everything below runs from the repo root on the Windows box with UE 5.8
installed.

---

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
python -m pytest -q                            # 716 tests, ~2 minutes
python -m tools.uppercut_validate.cli all      # canon validators, ~10 seconds
```

Both must be clean before anything is pushed. CI runs the same two.

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

The balance instrument the canon numbers were originally swept against. It
reaches a decision in most bouts; the contract currently does not, which is the
whole of the open Phase O question.

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
| C++ module | `sandbox\Source\UppercutCore` — six commandlets and the render Director |
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

**Phase N is the latest engine phase proven in C++.** Phases O, P, Q, R and S
exist as Python contracts with tests and no C++ at all. A `feat(core)` commit
subject does not mean an engine phase shipped — `STATUS.md` is the authority and
a test enforces that it cannot name a contract-only phase.

So: the numbers you can run above are real and the pictures are real, but they
are two different things that have not met yet. Closing that gap is the port of
Q, R and S into the module.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:35 UTC | END ] -->
