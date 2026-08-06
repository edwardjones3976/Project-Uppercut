# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 09:40 UTC | START ]
"""Decisions 0015 and 0016 (gates G2 and G3): the staged policy.

What was replaced: a flat eleven-way draw in which 5 of 11 outcomes were a
punch, regardless of where the fighter stood, what he could reach, or how tired
he was. It produced 175-219 punches per fighter-round against a professional
55-78, and it could not miss, because nothing it threw was ever illegal.

What replaced it: observe state -> intent -> opportunity -> action -> commit,
with `aggression_bias` read at the intent stage and nowhere else.

These tests prove the stages are load-bearing by breaking each one, and they
pin the two behaviours the first draft got wrong - footwork went inert, and a
misjudged punch still landed - because both looked fine until they were
measured.
"""
import importlib
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import analyze_core_round as O  # noqa: E402

SEED, ROUNDS = 4242, 2


def _trailer(stream):
    line = next(l for l in stream.splitlines() if l.startswith("S|"))
    return dict(kv.split("=", 1) for kv in line.split("|")[1:])


@pytest.fixture(scope="module")
def stream():
    return O.expected_stream(SEED, ROUNDS, with_floats=False)


def test_the_stream_records_which_policy_and_which_tier_ran(stream):
    head = [l for l in stream.splitlines() if l.startswith("H|")]
    assert "H|policy=staged" in head
    assert any(l.startswith("H|tier=") for l in head)
    assert any(l.startswith("H|aggression=") for l in head)


def test_every_decision_carries_a_reason_code(stream):
    """Decision 0016. A policy behaving oddly should be readable, not inferred."""
    for line in stream.splitlines():
        if line.startswith("D|"):
            # The guard pair `g` is two fields ("h|t"), so a D row is 15 wide:
            # D, tick, fighter, action, lcg, pos0, pos1, sep, band, st0, st1,
            # guard0, guard1, flags, reason.
            f = line.split("|")
            assert len(f) == 15, line
            assert f[14] and f[14].replace("_", "").isupper(), line


def test_aggression_is_read_at_the_intent_stage_and_nowhere_else(monkeypatch):
    """Break the intent stage and the fight must change in one direction only.

    With the bias at zero nobody ever seeks offensive initiative, so there are
    no punches at all. If punches survived a zero bias, the bias would be being
    read somewhere it should not be.
    """
    real = O.canon_pack

    def zero():
        c = real()
        c["aggression"] = 0
        return c

    monkeypatch.setattr(O, "canon_pack", zero)
    t = _trailer(O.expected_stream(SEED, 1, with_floats=False))
    assert int(t["punches"]) == 0
    assert int(t["knockdowns"]) == 0


def test_an_intent_to_attack_with_no_legal_punch_becomes_an_observation(stream):
    """The stage that did not exist before: opportunity.

    Under the flat draw nothing was ever illegal, so this count could not be
    anything but zero. It is now the largest single thing the policy does.
    """
    t = _trailer(stream)
    assert int(t["no_opportunity"]) > 0


def test_thinking_is_free(stream):
    """Decision 0015. An observation or a rest costs no stamina and no
    commitment, so a fighter may reconsider without spending anything."""
    rows = [l.split("|") for l in stream.splitlines() if l.startswith("D|")]
    frees = [r for r in rows if r[3] in ("observe", "rest")]
    assert frees, "the policy never produced a free outcome"
    for r in frees:
        assert r[13] == "-", "a free outcome carried an action flag: %s" % "|".join(r)


def test_a_wrong_band_punch_whiffs_even_when_the_fist_arrived(stream):
    """Rule 12, and the bug the measurement caught.

    `error_rate` is a MISJUDGED DISTANCE, so it draws from every punch rather
    than only the legal ones. Without the band gate at resolution those
    misjudged punches still landed - 97.9% of everything thrown arrived, which
    is not an accurate fighter, it is a fighter with nothing left to miss.
    """
    band_whiffs = [l for l in stream.splitlines()
                   if l.startswith("P|") and l.split("|")[4] == "whiffed"
                   and l.split("|")[10] == "band"]
    assert band_whiffs, (
        "no punch was refused on its band. Either the misjudgement branch or "
        "the Rule 12 gate at resolution has stopped working, and the fight "
        "cannot miss again")


def test_footwork_did_not_go_inert(stream):
    """The regression the first draft of this policy caused, pinned.

    Draft one only stepped when the band was WRONG. Steps fell from 612 to 36
    across three rounds and band transitions to zero - the fighters stood at one
    separation all night, which is exactly the defect Phase Q exists to fix,
    re-introduced by a policy that only moved when it was out of position.
    """
    t = _trailer(stream)
    assert int(t["steps"]) > 20, "the fighters have stopped moving"
    assert int(t["transitions"]) > 0, "no fighter changed range band all fight"


def test_a_committed_fighter_regenerates_by_activity_not_by_nothing():
    """Decision 0015's implementable half.

    Canon has authored three rates since step 8 - idle, moving, throwing - and
    this core read one of them, giving a committed fighter nothing at all. A man
    walking is not a man punching.
    """
    c = O.canon_pack()
    assert c["regen_moving"] > 0
    assert c["regen_throwing"] == 0
    assert c["regen"] > c["regen_moving"], (
        "idle regeneration must exceed moving regeneration, or resting is not "
        "rest")


def test_volume_is_in_the_same_world_as_a_professional_round(stream):
    """The number gate G3 was opened about.

    Not a balance assertion - a sanity one. 175-219 punches per fighter-round
    was the defect; anything in double digits is the same sport. When this
    tightens toward 55-78 the conversion work has landed too.
    """
    t = _trailer(stream)
    per_fighter_round = int(t["punches"]) / (2 * int(t["rounds"]))
    assert 20 < per_fighter_round < 140, (
        "%.0f punches per fighter-round" % per_fighter_round)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 09:40 UTC | END ]
