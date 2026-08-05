<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:30 UTC | START ] -->
# The golden stream

`phase_o_4242_1r.stream` is the exact byte target for a C++ port of Phase O:
seed 4242, 1 round, floats off. A phase is proven when the C++ artifact emits
this file byte for byte. Before this pin existed the target was only ever
"whatever `expected_stream` returns today" - a target that can move silently.

## Working with it

    python -m tools.engine.golden            # --check (default): compare, exit 1 on drift
    python -m tools.engine.golden --diff     # drifted rows rendered in words
    python -m tools.engine.golden --write    # re-bless: overwrite the pin

`--diff` renders each changed row as a sentence rather than a field dump, so a
drift reads as, for example:

    line 621
      was  tick 573: fighter 0 KNOCKED DOWN by cross_rear (pressure 5868 vs 5700)
      now  tick 576: fighter 0 condition snapshot

The guard was verified by nudging `pressure_threshold` from 0.57 to 0.59,
confirming that exact output, then restoring canon and re-verifying by SHA-256.

## When this fails and that is correct

Phase O is HELD. Deciding any of the three open canon quantities - G1 step cost,
G2 rest semantics, G3 aggression - changes the fight and therefore changes this
file. That is the pin doing its job, not a regression.

The re-blessing belongs in the SAME commit as the ruling, so that a canon
decision and its consequence are one reviewable change. A re-bless with no
ruling attached is a silent canon edit and should be rejected in review.

See `docs/decisions/OPEN_GATES.md` for G1-G6.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:30 UTC | END ] -->
