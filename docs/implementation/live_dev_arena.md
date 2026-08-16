<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 22:20 UTC | START ] -->
# The live development arena

Open `sandbox/UppercutSandbox.uproject`, open
`/Game/ProjectUppercut/Maps/L_UppercutDevArena`, press Play. Two fighters move
on canon's ring axis, close and open distance, throw punches, and miss when they
throw from the wrong band. The round ends when the tick budget runs out.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ] -->
**Update 2026-08-12.** MatchDirector defaults `bIntegratedOneRound=true` on
`UUppercutFightSubsystem`. That path loads `FUppercutFightSession`: unique
fighter cards, thin policy, and a round ending (count or sealed decision).
Phase Q `FUppercutRangeSession` remains for `prove_live_arena` when the flag
is false. Phase O is not held on G7 — see `docs/decisions/OPEN_GATES.md`.
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ] -->

The point of this document is the sentence that makes the arena worth having:

> **What you press Play on is the artifact the parity proof is taken against —
> not a runtime that agrees with it.**

That is a claim, so it is checked:

    python -m tools.engine.prove_live_arena

which drives the real `UUppercutFightSubsystem` inside a real `UWorld`, through
the same single-step control the Director's keyboard uses, and compares the file
it dumps to `tools/engine/analyze_core_range.expected_stream` byte for byte.

## What was extracted, and why the extraction is the work

Before this, every proven phase lived inside a commandlet's `Main()` —
monolithic, file-scoped, reachable only by running the editor headless. A
runtime could not call a line of it. An arena would therefore have had to
re-implement the rules, and two implementations of one rule is the defect this
repository spends most of its discipline avoiding.

So Phase Q was taken apart into four pieces, each with exactly one home:

| Piece | File | Who calls it |
|---|---|---|
| The rules | `UppercutRangeCore.cpp` | both |
| The canon reader | `UppercutRangeCanonLoader.cpp` | both |
| The loop | `UppercutRangeCore.cpp` (`FUppercutRangeSession::Step`) | both |
| The stream's shape | `UppercutRangeStream.cpp` | both |
| Arguments, tick count, file | `UppercutCoreRangeCommandlet.cpp` | headless only |
| Clock, controls, snapshots | `UppercutFightSubsystem.cpp` | live only |

Phase R was taken apart the same way (`UppercutEvadeCore`,
`UppercutEvadeCanonLoader`, `UppercutEvadeSession`).

The safety net for every step was the parity proof itself: after each
extraction the commandlet had to emit a **byte-identical** stream. That is a
stronger statement about a refactor than a test suite can make — the fight is
provably unchanged. All six pinned hashes survived every move:

    Q  4242/5400  32fb81853e8e961525664ecd98fc0f39fae50d2a184769457e6151af66b22faf
    Q  777/5400   02f3832ed95e77e75ff2166cac62baa1bd973aa43f3662041517c159bbd47360
    Q  4242/900   b8acb84ee9c1eaefd1c0575c8794abb9825506e632e13fc39edb438418d9a006
    R  4242/5400  f450d2f678fb464aca0e59960fcc0c692c213f6fb75de27a9056f53412912523
    R  777/5400   4b8d38276da032f71d7577f0ea92c845fe2fd80e420676976c3026e81444aec0
    R  4242/1200  4aae2b77657989bab82e39e132a12c5e323ed118127c7b8707fc670235cd8738

## The controls

Bound directly to keys by `AUppercutMatchDirector`, with no project input
configuration, because a development control that needs a settings file edited
before it works is a control that is missing at the moment somebody wants it.

| Key | Does |
|---|---|
| `Space` | pause / resume |
| `.` | advance exactly one tick |
| `,` | advance exactly one second |
| `R` | restart on the same seed |
| `N` | next seed (a stride of 7919, not +1) |
| `[` `]` | halve / double speed, clamped to 0.05×–8× |
| `\` | back to 1× |
| `P` | dump the round to `Saved/live/` as a marker stream |

`N` strides rather than increments because adjacent seeds in a linear
congruential generator open with correlated draws, and a "different fight" that
opens the same way is not much of a second opinion.

## Wall-clock time never drives the simulation

Criterion E.19, and the one rule most easily broken by a speed slider.

Real time decides **when** a tick runs, never how big one is. Delta seconds
accumulate; whole ticks are spent out of the accumulator; a frame worth four
ticks runs four identical ticks. The speed control changes how fast the
accumulator fills and nothing else.

This is why a fight watched at 0.25× and the same fight watched at 4× produce
the same marker stream, and it is the difference between a development control
and a lie. A pause drops the fractional remainder rather than banking it, so a
resume cannot depend on the moment somebody happened to press the key.

The tick rate is read from `data/clock_model.json` rather than assumed, because
Rule 9 says one clock read by everything and a hardcoded 60 here would be a
second one.

## The presentation boundary is testable, not decorative

`AUppercutFighterBase` reads one index out of a snapshot and places itself. It
holds no state the simulation cares about and cannot write back. Delete a
fighter actor mid-round and the fight is unaffected — that is the test of
whether Decision 0012's separation is real, and
`tests/test_live_arena_is_one_implementation.py` asserts the actor never calls a
control.

Animation hooks fire on **edges of the snapshot**, not on parsed marker rows. A
presentation layer that parsed the evidence stream would be a second reader of
it, and the second reader is always the one that drifts. Two identical actions
in a row are distinguished by the decision tick rather than the action string,
so a jab-jab plays two animations.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ] -->
## Ring and mannequins on Press Play

`AUppercutMatchDirector::BeginPlay` calls `UppercutSpawnFabRing` before
`StartRound`. Each `AUppercutFighterBase` soft-loads Manny/Quinn and action clips
from BoxingAttacks when present, otherwise keeps the engine cylinder. Shared
helpers live in `UppercutArenaPresentation` (also used by
`AUppercutBoutDirector::BuildArena`). Vendor packs stay gitignored; nothing is
baked into `L_UppercutDevArena.umap`.

Default maps in `sandbox/Config/DefaultEngine.ini` point at
`/Game/ProjectUppercut/Maps/L_UppercutDevArena` — if you see Untitled landscape,
you opened the wrong level.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-15 17:40 UTC | START ] -->
### How the mannequins are driven (2026-08-15)

Three defects fixed on 2026-08-15 define the current playback rules:

- **Being hit is visible.** It is not an action a fighter commits, so it can
  never appear in `LastAction` — the four reaction clips were loaded and
  unreachable. The session now stamps view-facing impact telemetry
  (`LastImpactTick`, `LastImpactMove`) on the defender when a punch lands; the
  view carries it; the actor edge-detects it exactly as it does
  `LastActionTick`, plays `hit_high`/`hit_body` (by the move's own `body_`
  prefix), and fires `OnHitTaken`. The stream is untouched — the P row already
  recorded the landing, and the parity proofs were re-run to hold that claim.
- **Every commitment restarts its clip, and one-shots do not loop.** Punches
  and reactions play once and hand the body back to a looping guard when they
  finish (checked in real time, so a paused fight does not freeze a fist
  mid-air forever). Guard and steps loop. The old code resumed the running
  clip on identical actions and looped everything, which is where the missing
  second jab and the self-repeating punches came from.
- **The mesh counter-rotation exists.** Mannequin-family meshes are authored
  facing +Y; the component now carries the standard −90° relative yaw, so the
  fighters face each other along the axis instead of both facing a side wall.
  The actor-facing maths was always right; the mesh under it was not.
- A hit reaction briefly owns the body: sustained actions do not stomp it, a
  new punch commitment always does. `block_high`/`block_body` remain loaded
  and unused — the simulation has no blocking yet, and playing one would be
  presentation inventing a defence that never happened.

### Look-at (2026-08-16)

A boxer never takes his eyes off the other one; a clip does not know that, so
every punch and hit reaction turned the head wherever the animator put it.
`AUppercutFighterBase::ApplyLookAt` bends the head — and `LookAtSpineShare` of
the turn through `spine_03` — back onto the opponent's eye line **after** the
clip has been evaluated, every frame, guarded by `LookAtMaxDegrees` so a neck
still has limits.

Three things about it are deliberate:

- **The face axis is measured, not assumed.** Calibration asks the reference
  skeleton which bone-local direction points out of the face, because a
  hard-coded axis is a guess about an asset and the asset may change. It runs
  once and logs `look-at ON (head 'head' +N children …)`.
- **Descendants are carried.** Turning a bone in component space turns only
  that bone's skinning; its children keep their old transforms and the mesh
  tears at the neck. Every descendant gets the same delta about the same pivot.
- **It writes bones and nothing else.** It runs at `TG_PostPhysics`, after
  animation has been evaluated, reads the fight snapshot, and touches only
  `GetEditableComponentSpaceTransforms`. The three integrated pins re-proved
  byte-identical with it on, which is that claim made checkable.

Its effect is real but modest today, and worth saying plainly: the fight is
one-dimensional, so the fighters already face each other exactly and the
correction is only ever undoing what a clip did to the head. It will matter far
more when Decision 0013's lateral axis lands and "facing" stops being binary.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-15 17:40 UTC | END ] -->
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ] -->

## What this arena does not do yet

Phase Q is a fight about **distance**. There is no guard, no stamina, no damage,
no knockdown and no round structure in it. Those layers belong to the integrated
session work (see `docs/SEE_AND_TEST.md`); this arena shows exactly what Phase
Q's contract describes and no more, which is the only honest thing it could show.

The map is authored offline by `tools/engine/build_dev_arena.py` (Decision 0012:
Python offline only, never in the runtime path) and regenerated rather than
patched, so the committed map is always exactly what that file says.

## A finding this work surfaced

Six other phases' commandlets each parse `data/movement_model.json` inline, with
their own opinion about which field means what. That is not a defect today —
each is proven against its own contract, so each is right about the phase it
describes. It becomes one the moment a live runtime wants to run those phases
too, which is precisely what Phase O will want. The count is pinned in
`tests/test_live_arena_is_one_implementation.py` so a seventh is a decision
somebody makes on purpose.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 22:20 UTC | END ] -->
