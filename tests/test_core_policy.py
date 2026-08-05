# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 12:40 UTC | START ]
"""Phase S - canon's difficulty tiers, executed instead of read. Contract tests.

These prove the rules and the prohibitions, not a balance outcome. The most
valuable one is `test_nobody_can_react_to_a_jab`: it is a fact of real boxing
that nobody authored, falling out of a 6-tick reaction floor meeting a 4-frame
jab, and if a later edit ever makes the jab reactable this test says so.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import analyze_core_policy as P   # noqa: E402
import analyze_core_round as O    # noqa: E402


@pytest.fixture(scope="module")
def pc():
    return P.policy_pack()


def test_canon_is_accepted(pc):
    assert pc["canon_errors"] == []


def test_no_tier_may_react_below_the_floor(pc):
    """Canon's prohibition is absolute and has no difficulty exemption."""
    for t in pc["order"]:
        assert not P.may_react(pc, t, pc["floor"] - 1)
        assert pc["tiers"][t]["reaction"] >= pc["floor"]


def test_nobody_can_react_to_a_jab(pc):
    """4 startup frames against a 6-tick floor. The jab is anticipated or eaten,
    which is what a jab IS - and nobody wrote that rule."""
    assert P.nobody_can_react_to_a_jab(pc)
    startup = O.canon_pack()["moves"]["jab_lead"]["startup"]
    assert startup < pc["floor"]


def test_something_is_reactable(pc):
    """...or reaction is decoration."""
    assert P.the_slowest_punch_is_readable_by_someone(pc)


def test_only_the_faster_tiers_answer_the_slower_punches(pc):
    """The ladder must show up in what each tier can actually respond to."""
    core = O.canon_pack()
    counts = []
    for t in pc["order"]:
        counts.append(sum(1 for m in O.PUNCHES
                          if P.may_react(pc, t, core["moves"][m]["startup"])))
    assert counts == sorted(counts), "a harder tier answers fewer punches"
    assert counts[-1] > counts[0]


def test_difficulty_is_a_ladder(pc):
    assert P.difficulty_is_a_ladder(pc)


def test_reaction_is_not_the_decision_clock(pc):
    """The distinction this phase exists to make."""
    assert P.reaction_is_not_the_decision_clock(pc)
    assert pc["interval"] != pc["floor"]


def test_commitment_may_not_be_cancelled(pc):
    """Commitment is the currency; a policy that can cancel it makes it free."""
    assert pc["respects_commitment"]
    assert not pc["may_cancel"]


def test_the_forbidden_inputs_are_all_named(pc):
    """Rule 3 and Rule 4's list, present so a later edit cannot quietly drop
    one."""
    for f in ("official_cards", "opponent_input_buffer", "rng_state",
              "hidden_attributes", "future_ticks"):
        assert f in pc["forbidden"]


def test_aggression_and_error_are_pure_functions_of_the_draw(pc):
    """No hidden state, no die of their own: same draw, same answer."""
    for t in pc["order"]:
        for x in (0, 1234, 9999, 123456789):
            assert P.is_offensive(pc, t, x) == P.is_offensive(pc, t, x)
            assert P.errs(pc, t, x) == P.errs(pc, t, x)


def test_aggression_and_error_read_different_digits(pc):
    """They must not be the same roll wearing two names, or a tier's error rate
    would be a deterministic function of whether it decided to punch."""
    t = pc["order"][0]
    offensive = {P.is_offensive(pc, t, x) for x in range(0, 10000, 7)}
    assert offensive == {True, False}
    # holding the low digits fixed, the error answer must still vary
    errs = {P.errs(pc, t, 500 + 10000 * k) for k in range(0, 10000, 7)}
    assert errs == {True, False}


def test_error_rate_never_reaches_certainty(pc):
    """A tier that always errs can never choose what it meant to, which is not
    a difficulty setting but a broken fighter."""
    for t in pc["order"]:
        assert 0 <= pc["tiers"][t]["error"] < 10000


def test_every_tier_can_both_punch_and_not(pc):
    for t in pc["order"]:
        assert 0 < pc["tiers"][t]["aggression"] < 10000
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 12:40 UTC | END ]
