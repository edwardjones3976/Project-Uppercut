<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 02:40 UTC | START ] -->

# Unreal live backend integration

**Status: in progress. This document is written as work lands, not after, so it
is trustworthy about what does NOT exist yet.** Every section is marked DONE, IN
PROGRESS or NOT STARTED, and nothing is described in the present tense unless it
runs today.

**Branch:** `feat/unreal-live-backend-integration`
**Starting commit:** `926fafc` — *feat(core): Phase Q proven in C++ — the fight
gets a distance*
**Working tree at start:** clean, except one file deleted by something outside
git (see "Blockers").

## The gap this closes

The project has a deterministic C++ core through the latest proven phase, Python
contracts and measurements, mannequins, licensed boxing animation, an imported
arena, and a one-command screenshot harness. What it does not have is an ordinary
Unreal level the Director can open, press Play in, and watch a fight.

That is the whole assignment: one persistent development arena, authoritative
C++ simulation, live controls, real inspection, and a thin proof of the project's
personality — with Python demoted to offline validation and never in the runtime
path.

## Milestone 1 — decision gates. DONE

All six open gates were ruled on by the Director and are now closed by accepted
decision records. `docs/decisions/OPEN_GATES.md` carries the closure table.

| Gate | Decision | What it settles |
|---|---|---|
| G1 | 0014 | movement is priced by displacement; the flat 0.600 is not the price of an ordinary step |
| G2 | 0015 | thinking is free; Observe, HoldPosition and Rest are first-class outcomes |
| G3 | 0016 | `aggression_bias` is intent at the intent stage, not throw rate |
| G4 | 0017 | Decision 0013 ratified; lateral guard geometry scheduled after the live round |
| G5 | 0018 | versioned rulesets; professional default, three-knockdown becomes an arcade modifier |
| G6 | 0019 | a canon authoring margin; no coverage value sits on the interception threshold |

### What was implemented with the rulings, and what was only recorded

**Implemented (G1, G6).**

- `movement_model.locomotion.<mode>.stamina_cost_per_ru` is now the single
  authority for what movement costs. The Phase O contract prices a step by the
  distance actually travelled, including the directional, posture and exhausted
  multipliers, and including the rope-retreat multiplier — so a retreat that
  buys nothing on the ropes now costs nothing, and circling is not free.
- The move table's three ordinary step entries became a **derived echo**
  (`cost_model: "displacement"`), and `movement.check_step_cost_authority`
  recomputes them from the authority and fails on drift. Two authorities
  disagreeing by 4.55x with nothing checking either was the defect; one
  authority plus a checked echo is the fix.
- `pose_geometry.guard.authoring_margin` (0.05) is canon.
  `philly_shell.guard_body` moved to 0.55 (exposed side — the shell is answered
  downstairs) and `active_hands.guard_high` to 0.65 (protected side — its parry
  is not yet authoritative, so the conservative placement is correct).
  `tests/test_guard_threshold_margin.py` enforces the margin for **every**
  posture and lane, in the shared q10000 integer space, because a margin rule
  written in floats is itself a knife edge.

**Recorded, not yet implemented (G2, G3, G5).** These change the shape of the
policy layer and the round-termination rules rather than a number, and they land
with the runtime subsystem rather than ahead of it. Nothing in the repository
currently claims otherwise.

### The ripple, and how it was handled

Repricing three steps changed `data/moves/generic_sandbox_moves.json`, and three
already-proven phases hash that file into their marker streams. Their pins
failed — correctly.

Every one was **re-run and re-proven byte-for-byte against the new canon**, not
edited to match: Phase N (`UppercutCoreCondition`), Phase K (the render slice)
and Phase Q (`UppercutCoreRange`, three runs). New hashes and the superseded ones
are recorded together in `docs/phase1a/determinism_probe_results.md` and in
`tests/test_phase_evidence_pins.py`. Both golden streams were re-blessed in the
same commit as the ruling that moved them, which is the rule those pins exist to
enforce.

One claim was corrected rather than left standing: Phase Q's record said its pin
"will survive the open gates." The fight survived; the bytes did not, because
Phase Q hashes a file it does not otherwise read.

## Milestone 2 — authoritative runtime subsystem. GROUNDWORK DONE

**2026-08-06: the rules are now callable at runtime.** `UppercutRangeCore`
(`Public/UppercutRangeCore.h`, `Private/UppercutRangeCore.cpp`) holds Phase Q's
rules as plain fixed-point functions — no UObject, no ticking, no logging, no
file IO. `UppercutCoreRangeCommandlet` is now a *caller*: it loads canon, drives
the clock and writes rows.

This had to happen before anything else in this milestone. The proven C++ lived
inside commandlet `Main()` functions, monolithic and file-scoped and reachable
only by running the editor headless. A runtime subsystem could not call any of
it, so a live arena would have had to re-implement the rules — and two
implementations of one rule is the defect this repository spends most of its
discipline avoiding.

**The refactor's safety net is the parity proof itself.** After the extraction
the commandlet still emits byte-identical streams:

    seed 4242, 5400 ticks  32fb8185...   unchanged
    seed  777, 5400 ticks  02f3832e...   unchanged
    seed 4242,  900 ticks  b8acb84e...   unchanged

That is a stronger statement about a refactor than a test suite can make: the
fight is provably the same fight.

Design rules for anything else extracted this way, so it stays usable from both
sides: no UObject, fixed-point integers only, every division through
`UppercutFloorDiv` (Python's `//` floors and C++ `/` truncates, and that is the
seam where a port silently diverges), and canon arrives as **data** — loaded by
whoever has a file system, the commandlet from disk and the subsystem from a
data asset.

**Still to do in M2:** the same extraction for Phase R, then the subsystem,
match director and fighter classes.

## Milestone 2 (continued) — the subsystem itself. NOT STARTED

Planned shape, recorded so the next session does not re-derive it:

- `UUppercutFightSubsystem` — owns one fight session, advances the fixed
  authoritative tick, accepts seed / ruleset / profiles / rounds / clock mode,
  exposes read-only snapshots and events, supports start, pause, resume,
  single-step, restart, reseed and playback speed. No rendering decisions.
- `AUppercutMatchDirector` — creates the session, binds fighters and presentation,
  translates authoritative events into animation, audio, camera and UI. Never
  changes an outcome.
- `AUppercutFighterBase` — presents one authoritative fighter. Owns meshes,
  animation, hit-reaction presentation, nameplates, debug draw. Calculates no
  damage and no collision truth.
- Data assets: fighter profile, CPU profile, strike definition, guard posture,
  ruleset, referee profile, event class, presentation mapping.
- `WBP_UppercutDevHUD` — controls, telemetry, reason codes, event stream, debug
  toggles.

The existing commandlets stay. They are evidence harnesses and the parity proof
runs through them; the subsystem is a second consumer of the same rules, not a
replacement.

## Milestone 3 — the live arena, controls, HUD, presentation. NOT STARTED

`/Game/ProjectUppercut/Maps/L_UppercutDevArena`, the control set, the debug
visualisation, and the soul proof. Nothing exists yet.

## Parity boundary

Stated now because it is the thing most easily lost later.

The C++ runtime is proven against the Python contract at the **marker stream**,
for a fixed seed and configuration, byte for byte. That is what "proven" means in
this repository and it does not soften. The runtime subsystem carries the same
obligation as the commandlets: for every ported subsystem, run the contract, run
the C++, compare streams, and reconcile genuine implementation errors without
changing canon to force agreement.

Python is not in the runtime path and must never be. It validates, measures,
references and reports.

## Test commands

    python -m pytest -q                            # 745 tests
    python -m tools.uppercut_validate.cli all      # canon validators
    python -m tools.engine.golden --diff           # both pinned streams, no engine
    python -m tools.engine.prove_core_range        # Phase Q parity, needs UE
    .\tools\engine\show_me.ps1                     # the rendered slice

## Blockers, recorded rather than worked around

**`tools/engine/build_uppercut_core.ps1` was deleted from the working tree by
something outside git, and git cannot restore it** — `git checkout` fails with
`unable to create file ... Permission denied`. A `.cmd` file written during the
same session also vanished between being written and being run. The signature
fits an endpoint security product quarantining scripts that launch executables
(Bitdefender is installed). The file is intact in the repository and the
deletion is deliberately **not** committed.

Until the folder is whitelisted, the build runs through UnrealBuildTool directly:

    cd "C:\Program Files\Epic Games\UE_5.8\Engine\Source"
    dotnet "...\UnrealBuildTool.dll" UppercutSandboxEditor Win64 Development
        -project=C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject -WaitMutex

Also observed: UnrealBuildTool refused one build with *"Unable to build while
Live Coding is active"* with no editor running and no live-coding mutex present.
It cleared on retry. If it recurs, `-NoHotReloadFromIDE` skips the check.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 02:40 UTC | END ] -->
