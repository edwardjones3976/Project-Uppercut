# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 23:55 UTC | START ]
"""Phase R's rules moved into a shared module, and nothing else moved with them.

The strongest statement about this extraction is not in this file - it is that
Phase R's marker stream is byte-identical afterwards, through its own prover,
against the C++ artifact. What is here is the part a unit test can carry: that
both callers reach the same objects, that no rule was duplicated on the way,
and that the three phase-analyzer references really did become parameters
rather than copies.
"""
import io
import os

import pytest

from tools.engine import analyze_core_evade as RPH
from tools.uppercut_evade import core as EVADE

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def ec():
    return RPH.evade_pack()


def test_the_analyzer_and_the_shared_core_are_the_same_objects():
    """Not "they agree" - the same function. Agreement can drift; identity
    cannot, and identity is what "one implementation" means."""
    for name in ("beats", "evades", "a_body_shot_beats_the_slip",
                 "the_uppercut_beats_the_roll", "the_slip_evades_a_straight"):
        assert getattr(RPH, name) is getattr(EVADE, name), name


def test_the_two_wrapped_rules_delegate_rather_than_reimplement(ec):
    """`evade_pack` and `no_evasion_is_strictly_better` are wrapped rather than
    re-exported, because each needed a vocabulary the phase owns. The wrapper
    must be a hand-off and nothing more."""
    assert RPH.evade_pack() == EVADE.evade_pack(RPH.O.REGIONS)
    assert (RPH.no_evasion_is_strictly_better(ec)
            is EVADE.no_evasion_is_strictly_better(ec, RPH.O.PUNCHES))


def test_the_two_fixed_point_conversions_agree():
    """The shared core defines its own `q`; the analyzer keeps the one it had.
    Two definitions of a rounding rule is one more than this project lets go
    unwatched, so they are compared rather than assumed."""
    for v in (0, 0.05, 0.1, 0.12, 0.25, 0.5, 0.72, 0.9, 1.0, 2.5, 100.0):
        assert EVADE.q(v) == RPH.O.q(v), v


def test_the_shared_core_imports_no_phase_analyzer():
    """The whole reason the extraction was necessary."""
    src = io.open(os.path.join(REPO, "tools", "uppercut_evade", "core.py"),
                  encoding="utf-8").read()
    body = src.split('"""', 2)[2]
    for forbidden in ("analyze_core_evade", "analyze_core_round",
                      "analyze_core_condition", "analyze_core_range"):
        assert forbidden not in body, forbidden
    assert "O." not in body, "a phase-analyzer reference survived the move"


def test_there_is_no_evasion_die(ec):
    """Director order, and the line worth keeping: "Do not add an evasion die.
    The geometry already answers the question."

    An evasion resolves from timing, trajectory, the vacated region and the
    authored counter relationship. Nothing in the shared core may reach for
    randomness, and this checks the module rather than the intention.
    """
    src = io.open(os.path.join(REPO, "tools", "uppercut_evade", "core.py"),
                  encoding="utf-8").read()
    body = src.split('"""', 2)[2]
    for forbidden in ("random", "rng", "Substream", "seed", "shuffle",
                      "choice", "uniform"):
        assert forbidden not in body.lower(), forbidden


def test_the_four_properties_still_hold(ec):
    """Moved code that stopped being true would be a rewrite wearing a move."""
    assert EVADE.a_body_shot_beats_the_slip(ec)
    assert EVADE.the_uppercut_beats_the_roll(ec)
    assert EVADE.the_slip_evades_a_straight(ec)
    assert EVADE.no_evasion_is_strictly_better(ec, RPH.O.PUNCHES)


def test_a_body_shot_still_finds_the_body_while_the_head_slips(ec):
    """The boxing idea, not the code path. A slip vacates a lane the head was
    in; the body never left."""
    assert not EVADE.evades(ec, "slip_lead", "body_straight_rear",
                            ec["region"]["body_straight_rear"])
    assert EVADE.evades(ec, "slip_lead", "cross_rear",
                        ec["region"]["cross_rear"])


def test_the_uppercut_rises_into_the_roll(ec):
    """An evasion is a structure in motion, so moving into a punch is a real
    thing that can happen to you."""
    assert EVADE.beats(ec, "roll_under", "uppercut_rear")


def test_a_positional_action_is_not_a_lane_vacating_dodge(ec):
    """Director order: "positional actions such as step_out are not magically
    converted into lane-vacating dodges".

    The first version of this test looked for those actions to be ABSENT from
    the evasion table and failed, which was the test being wrong and canon
    being better than it. `step_out` and `pivot_lead` are in the table as
    `kind: positional` with an empty `vacates` tuple - present, so a fighter
    can choose them, and vacating nothing, so they cannot dodge. Canon already
    says the thing the order asks to preserve; what needed asserting is that
    the DISTINCTION survives, not that the entries are missing.
    """
    positional = [k for k, v in ec["evasions"].items()
                  if v["kind"] == "positional"]
    assert positional, "no positional entry left to distinguish from an evasion"
    for k in positional:
        assert ec["evasions"][k]["vacates"] == (), k
        assert ec["evasions"][k]["active"] == 0, k
        # And the consequence, which is the part that matters: vacating nothing
        # means evading nothing, whatever the punch and whatever the region.
        for punch, region in ec["region"].items():
            assert not EVADE.evades(ec, k, punch, region), (k, punch)


def test_evasion_still_outranks_guard(ec):
    """Phase R's own declaration, which the integrated ordering depends on: a
    punch successfully slipped is not also blocked."""
    assert ec["outranks_guard"] is True
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 23:55 UTC | END ]
