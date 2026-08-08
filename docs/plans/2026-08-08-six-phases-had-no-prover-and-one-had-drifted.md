<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 04:40 UTC | START ] -->

# Six phases had no prover, and one of them had drifted

Written before starting the loader unification the integrated schema needs, to
check the thing that would falsify the plan: that a phase can be re-proven after
its canon reading changes.

It could not be, for six of six. And building the runner that fixes that found a
real divergence on its first run.

## The gap

Phases Q and R have `prove_core_range` and `prove_core_evade`, which run the C++
commandlet and compare its marker stream to the analyzer byte for byte. Checked
2026-08-08, that is the entire set:

```text
prove_canon_parity  -> UppercutCanonVectors
prove_core_evade    -> UppercutCoreEvade    (Phase R)
prove_core_range    -> UppercutCoreRange    (Phase Q)
prove_live_arena    -> UppercutLiveArena
```

Phases H, I, J, K, L and N had nothing. And the two guards that look like they
cover the gap do not:

- `golden.py` regenerates from the **Python analyzers** and invokes no
  commandlet at all — it never mentions `-run=`.
- `test_phase_evidence_pins.py` likewise recomputes `expected_stream(...)` in
  Python.

Both are real protection against an *analyzer* changing. Neither can see the C++
move. So the six commandlets that parse movement canon inline — the exact six
the loader unification has to replace — could have been edited with nothing in
the repository noticing.

`tools/engine/prove_phase.py` closes four of the six. H and K are named in its
own output every run rather than quietly omitted: H takes `-canon=`/`-steps=`
instead of `-repo=`/`-ticks=`, and K runs through the renderer rather than a
commandlet.

## What the first run found

| phase | result |
|---|---|
| I — the two-fighter authoritative loop | **PROVEN**, both seeds |
| J — real movement and swept collision | **PROVEN**, both seeds |
| L — guard and slip | **PROVEN**, both seeds |
| N — visible stamina and condition | **DRIFT** |

Phase N's C++ artifact emits the pre-Decision-0023 header:

```text
commandlet   H|canon_movement=1ea96fe4...
contract     H|canon_hash_contract=uppercut-hash-contract-v1
```

**No fight moved.** All 1274 event rows are identical, and every old
`H|canon_X=` value equals the contract's new `H|canon_X_raw=` exactly as
Decision 0023 promised it would. This is a header-identity divergence and
nothing more.

## Why N and not I, J, L

Decision 0023's migration covered five phases — N, K, O, Q, R. The **analyzers**
for all five were migrated to the dual-hash header. On the C++ side, only two
commandlets route through `UppercutCanonHeaderLines`:

```text
UppercutRangeStream.cpp            (Phase Q's chain)
UppercutCoreEvadeCommandlet.cpp    (Phase R)
```

Six still build the old header inline: `CoreSweep`, `CoreProbe`, `CoreLoop`,
`CoreGuard`, `CoreCondition`, `BoutDirector` — the same six as the inline canon
readers, which is not a coincidence: they are the six that never went through
the Phase Q extraction.

So the phases split three ways:

- **I, J, L** — neither side migrated, so both agree. Proven, and they are.
- **Q, R** — both sides migrated. Proven, and they are.
- **N** — analyzer migrated, C++ not. This is the drift.
- **K** — same mechanism as N (`analyze_render_probe` was migrated,
  `UppercutBoutDirector.cpp` was not), but **not verified here**, because the
  render path needs a runner this file does not yet provide. Stated as an
  expectation, not a result.
- **O** — contract-only, no C++ artifact, unaffected.

## The claim that turns out to be too strong

`test_phase_evidence_pins.py` records, of the 0023 migration:

> Every phase also re-proved against its C++ artifact after the change, which is
> why this is a migration and not a re-bless.

That holds for Q and R. It does not hold for N, and by the same mechanism almost
certainly not for K — and those two are precisely the phases the pin file pins.
The pins recompute from the migrated analyzer, so they pass while the C++ they
describe no longer produces those bytes. The pin mechanism cannot see it. That
is not a criticism of the pins; it is the hole `prove_phase.py` exists to fill.

## What this implies for the repair, and for the refactor

The repair is smaller than it sounds. The pinned streams are generated from the
analyzers, which already carry the new header, so routing the six commandlets
through `UppercutCanonHeaderLines` brings the C++ **into** agreement with the
pins rather than moving them. **No pin moves.** It is finishing an ordered
migration, not a re-bless — but it does touch six proven artifacts, so it wants
doing deliberately and with `prove_phase` run before and after.

And the loader unification should not start until that repair lands. Changing
canon parsing in a commandlet whose header is already out of step would mix two
divergences in one diff, and the first rule here is that a change to proven code
must be falsifiable on its own.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 04:40 UTC | END ] -->
