<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 23:00 UTC | START ] -->
# The golden streams

The exact byte targets a C++ port has to produce. A phase is proven when the
engine's marker stream is byte-identical to the analyzer's; before these files
existed, that target was only ever "whatever `expected_stream` returns today" —
a target that can move silently, and did once.

| File | Phase | Arguments | State |
|---|---|---|---|
| `phase_o_4242_1r.stream` | O — a round that can end | seed 4242, 1 round, floats off | **HELD**, no C++ yet |
| `phase_q_4242_5400.stream` | Q — the fight gets a distance | seed 4242, 5400 ticks | **PROVEN** by `UppercutCoreRangeCommandlet` |

## Working with them

    python -m tools.engine.golden                    # check every pin
    python -m tools.engine.golden --diff             # drift rendered in words
    python -m tools.engine.golden --phase=Q --write  # re-bless one pin

`--diff` renders each changed row as a sentence rather than a field dump, so a
drift reads as:

    line 621
      was  tick 573: fighter 0 KNOCKED DOWN by cross_rear (pressure 5868 vs 5700)
      now  tick 576: fighter 0 condition snapshot

The describer is per phase on purpose: `R` means the end of a round in Phase O
and a band transition in Phase Q, and one shared describer would have rendered
one of them as a lie. The guard itself was verified rather than assumed — by
nudging `pressure_threshold` from 0.57 to 0.59, confirming that exact output,
then restoring canon and re-verifying by SHA-256.

## When a pin fails, and whether that is correct

**Phase O.** It is HELD. Deciding any of the three open canon quantities — G1
step cost, G2 rest semantics, G3 aggression — changes the fight and therefore
changes this file. That is the pin doing its job. The re-blessing belongs in the
SAME commit as the ruling, so a canon decision and its consequence are one
reviewable change; a re-bless with no ruling attached is a silent canon edit and
should be rejected in review.

**Phase Q.** It is PROVEN, and this pin is what keeps that proof meaningful
without an engine. Parity needs Unreal and about two minutes; noticing that
somebody moved the contract out from under a proven port needs only this file. If
it fails, **the port is not proven any more** until

    python -m tools.engine.prove_core_range

says otherwise. Re-run that first, then re-bless in the same commit as the change
that caused the drift.

See `docs/decisions/OPEN_GATES.md` for G1–G6.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 10:30 UTC | START ] -->
## The integrated round — a different kind of pin

| File | Run | State |
|---|---|---|
| `integrated_1r_4242_10800.stream` | seed 4242, full round | **AUTHORITY**, recorded from C++ |
| `integrated_1r_777_10800.stream` | seed 777, full round | **AUTHORITY**, recorded from C++ |
| `integrated_1r_4242_1200.stream` | seed 4242, 1200 ticks | **AUTHORITY**, ends mid-round |

    python -m tools.engine.prove_integrated_arena           # needs UE, ~1 min
    python -m tools.engine.prove_integrated_arena --write   # re-bless

**These three are pinned in the opposite direction from the ones above, and the
difference matters.** O, Q and R are pins on an *analyzer*: a Python contract
predicts the bytes and the C++ port must reproduce them, so `golden.py` can
regenerate and check them with no engine at all. Decision 0040 R1 makes the
shared C++ `INTEGRATED_1R` session the combat authority and R2 makes Python
reference-only. There is therefore nothing that can predict these bytes, and
writing something that could would BE the second implementation of the rules
that the convergence rule exists to prevent.

So these files are **recordings, not predictions**. Checking them needs Unreal,
because the only thing that can produce them is the authority itself. What the
committed bytes still buy without an engine is the readable diff — a drift shows
up as `tick 1195: fighter 0 LANDS hook_lead` against `... and it is slipped`,
not as a changed hash.

**Why they were recorded on 2026-08-14.** Until then the combat authority was
the one artifact in this repository with nothing watching it: `prove_live_arena`
asks for `-integrated=0` because it pins Phase Q, `golden.py` covers O/Q/R, and
the two tests that appeared to cover the integrated arena existed on `main` only
as orphaned `.pyc` files with no `.py` beside them — their sources sit on
`feat/authenticity-program`, which Decision 0040 R6 holds as not merge-ready,
together with that branch's own `analyze_integrated_arena.py`,
`prove_integrated_arena.py` and streams under
`tools/engine/golden_integrated_arena/`. **That name collision is unresolved and
is a Director call**, compared in
`docs/development-log/2026-08-14-the-combat-authority-had-nothing-watching-it.md`.
The cost was already on the
record — Decision 0040 quotes the C++ round at `punches=123 landed=51` for seed
4242 over 10800 ticks, and the same configuration on `86d3ef1` produces
`punches=153 landed=153`. No gate could have reported that, because no gate was
looking.

**The normalisation is gone (2026-08-16).** The C++ header used to carry
`repo=<absolute path>`, so the same fight produced different bytes in a
different checkout — including on the self-hosted Windows runner Issue #14 is
building — and `prove_integrated_arena` normalised that single field as a
declared stopgap. The durable fix landed in the artifact: the header no longer
records where it was run, the prover compares raw bytes, the pins are stored
exactly as the engine wrote them (re-blessed in the same commit as the header
change), and `tests/test_integrated_arena_analyzer.py` fails if a `repo=`
field or machine path ever reaches a pin again.

**When one of these fails, it is not automatically wrong.** A pin on an
authority moves whenever the authority is deliberately improved — and the
integrated round has a great deal of deliberate improvement still owed to it
(Issue #12). Re-bless with `--write`, in the same commit as the change that
caused it, and say in the message what about the fight changed. A re-bless with
no explanation attached is how `123 landed=51` became `153 landed=153` with
nobody noticing.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 10:30 UTC | END ] -->
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 23:00 UTC | END ] -->
