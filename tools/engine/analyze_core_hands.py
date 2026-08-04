# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 23:40 UTC | START ]
"""Phase P marker contract - the hand is the unit, not the fighter.

The Director's mechanic, made a contract. Every phase before this one treated a
fighter as a single defensive object: "committed" was one state, and canon's
`guard_extent_multiplier_while_committed` was applied to the whole body at once.
That is a whole-body dimmer, and it is why the multiplier turned out to be a
switch with exactly one meaningful position (the 0.6316 cliff) rather than a dial.

A boxer is not one object. He has two hands and they are in different places.

  the lane the defender's committed hand VACATED  ->  canon's 0.6 multiplier
  the lane his free hand still covers             ->  full authored extent

Which lane a hand vacated is DERIVED, not invented: the height class of the punch
the defender himself threw, via `move.guard_interaction` ->
`height_by_guard_interaction`, both already canon. Throw upstairs and you are
open upstairs; dig to the body and the head is the lane you left. No new
coefficient enters this phase.

Measured before it was written (`experiment_per_hand_guard.py`, 24 seeds x 3
rounds): blocks 0 -> 853, against 868 for a probabilistic guard stage that costs
one die per arriving punch. Same defensive effectiveness, no dice - which is why
Decision 0013 took this over the port.

SCOPE, deliberately narrow. This phase is the DEFENSIVE half of the principle
only. Canon also authors the offensive half - chaining's opposite-hand link at
1.0, same hand at 1.4, same POWER hand at 1.8, and per-hand arm fatigue - and the
C++ core reads none of it (verified: no `arm_fatigue`, `chaining`, `last_hand` or
`arm_work` anywhere in the module). That is Phase Q, and it is named here rather
than half-done.

KNOWN LIMIT, on the record. Lanes are high/low, not left/right, so this expresses
"open where your hand went" and not yet "open on the side you punched from". The
lateral half needs the 2D geometry `pose_geometry` flags as pending for the hook,
and Decision 0013 sequences it after the CPU policy.

Stream: Phase O's, with the P row gaining the defender's vacated lane so a
blocked-or-landed call can be argued with rather than merely observed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_round as O  # noqa: E402

REPO = O.REPO
canon_pack = O.canon_pack
grade, alignment, pressure = O.grade, O.alignment, O.pressure


def vacated_lane(c: dict, move_id) -> str:
    """The lane a fighter's own punch took his hand out of."""
    return None if move_id is None else c["moves"][move_id]["height"]


# The rule itself lives in analyze_core_round, which is the contract that
# executes it - Phase O was HELD rather than sealed, so the per-hand fix belongs
# in its stream rather than beside it. This module states and proves the rule;
# the dependency runs one way.
coverage = O.coverage


def cliff_is_dissolved(c: dict) -> bool:
    """The property that says this phase did its job.

    Under Phase O every covering lane flipped at one multiplier - 0.6316 - so the
    coefficient was a switch. Under Phase P the surviving coverage in an
    unvacated lane is the free hand's own authored extent, which does not depend
    on the multiplier at all. A committed fighter therefore has DIFFERENT defence
    depending on what he threw, which is the thing a single multiplier could
    never express.
    """
    hg = c["posture"]["high_guard"]["ext"]
    gm = 10000
    high_after_high = coverage(c, "high_guard", "high", "high", gm)
    high_after_low = coverage(c, "high_guard", "high", "low", gm)
    return (high_after_high < c["thr"] <= high_after_low
            and high_after_low == (hg["high"] * gm) // 10000)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 23:40 UTC | END ]
