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
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 23:00 UTC | END ] -->
