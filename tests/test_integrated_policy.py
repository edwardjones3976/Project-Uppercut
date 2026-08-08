# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:20 UTC | START ]
"""The Director's seventeen required CPU-policy tests, plus the ones they imply.

Numbered to the order they were given, so a reader can check the list off
against the ruling rather than trusting that it was covered.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.uppercut_integrated import policy as P   # noqa: E402
from tools.uppercut_integrated import rng as R      # noqa: E402

CONTRACT = "uppercut-integrated-v1"


def streams(seed=4242):
    return R.BoutRng(seed, CONTRACT)


def policy_stream(seed=4242):
    return streams(seed).stream("policy_intent")


def obs(**kw):
    return P.Observation(**kw)


# --- 1. same state + same seed -> same decision ------------------------------

def test_1_same_state_and_seed_decide_identically():
    a = [P.decide(obs(), policy_stream()).as_row() for _ in range(1)]
    b = [P.decide(obs(), policy_stream()).as_row() for _ in range(1)]
    assert a == b

    sa, sb = policy_stream(), policy_stream()
    rows_a = [P.decide(obs(range_band="mid"), sa).as_row() for _ in range(60)]
    rows_b = [P.decide(obs(range_band="mid"), sb).as_row() for _ in range(60)]
    assert rows_a == rows_b


# --- 2. a different policy seed can alter tie-breaking -----------------------

def test_2_a_different_policy_seed_changes_tie_breaking():
    sa, sb = policy_stream(4242), policy_stream(999)
    rows_a = [P.decide(obs(), sa).as_row() for _ in range(80)]
    rows_b = [P.decide(obs(), sb).as_row() for _ in range(80)]
    assert rows_a != rows_b, (
        "two different policy seeds produced identical decision sequences - "
        "the stream is not reaching the tie-break")


# --- 3 & 4. other subsystems' randomness cannot alter policy -----------------

@pytest.mark.parametrize("other", ["presentation", "contact_condition",
                                   "knockdown_recovery", "judging_officiating",
                                   "evasion_defense", "movement_range"])
def test_3_and_4_other_streams_cannot_move_the_policy(other):
    quiet, loud = streams(), streams()
    for _ in range(5000):
        loud.stream(other).next_u32()
    a = [P.decide(obs(), quiet.stream("policy_intent")).as_row()
         for _ in range(40)]
    b = [P.decide(obs(), loud.stream("policy_intent")).as_row()
         for _ in range(40)]
    assert a == b, "draws on %s moved the policy" % other


def test_the_policy_cannot_even_reach_another_stream():
    """Not 'did not read' - could not. The interface makes it impossible.

    decide() takes a Substream, and a Substream holds no reference to its
    siblings, so there is no path from inside the policy to contact or judging
    randomness. The BoutRng is never handed over.
    """
    s = policy_stream()
    assert not hasattr(s, "stream")
    assert not hasattr(s, "_streams")
    for attr in vars(R.Substream).get("__slots__", R.Substream.__slots__):
        assert attr in ("name", "seed", "state", "draws", "authoritative")


def test_the_policy_refuses_a_stream_that_is_not_its_own():
    with pytest.raises(P.PolicyError):
        P.decide(obs(), streams().stream("contact_condition"))


# --- 5, 6, 7. what the policy is not allowed to know -------------------------

@pytest.mark.parametrize("forbidden", [
    "official_score", "scorecard", "judge_totals",
    "opponent_next_action", "opponent_intent",
    "opponent_wind", "opponent_reserve", "opponent_condition",
])
def test_5_6_7_forbidden_inputs_do_not_exist_on_the_observation(forbidden):
    assert forbidden not in P.Observation.__slots__
    with pytest.raises(P.PolicyError):
        P.Observation(**{forbidden: 1})


def test_no_decision_path_needs_a_score():
    """17, checked as a property of the type rather than by inspection."""
    assert not any("score" in s or "judge" in s
                   for s in P.Observation.__slots__)


# --- 8 & 9. aggression is a bias, not a switch -------------------------------

def test_8_high_aggression_does_not_attack_every_decision():
    s = policy_stream()
    hot = P.Profile(aggression_bias=10000)
    rows = [P.decide(obs(consecutive_failed_attacks=2), s, hot).tactical
            for _ in range(20)]
    assert all(t != P.ATTACK for t in rows), (
        "a maximally aggressive fighter attacked straight through a "
        "two-failure streak - aggression has become a vending machine")

    s2 = policy_stream()
    mixed = [P.decide(obs(wind_is_low=True), s2, hot).tactical
             for _ in range(20)]
    assert all(t != P.ATTACK for t in mixed), (
        "aggression overrode low Wind; a tired fighter must still be able to "
        "want initiative and choose to rest")


def test_9_low_aggression_does_not_forbid_attacks():
    s = policy_stream()
    cold = P.Profile(aggression_bias=200)
    rows = [P.decide(obs(opponent_recovering=True), s, cold).tactical
            for _ in range(10)]
    assert all(t == P.ATTACK for t in rows), (
        "a cautious fighter refused a free punish window - low aggression is "
        "not pacifism")


# --- 10. low Wind produces recovery when tactically possible ------------------

def test_10_low_wind_seeks_recovery_when_it_can():
    d = P.decide(obs(wind_is_low=True, range_band="outside",
                     preferred_band="outside"), policy_stream())
    assert d.strategic == P.RECOVER and d.tactical == P.REST
    assert d.reason == P.R_RECOVER_WIND


def test_10b_low_wind_does_not_rest_while_being_walked_down():
    """Recovery is a decision, not a reflex. Resting with a man on top of you
    is not recovery, it is being hit."""
    d = P.decide(obs(wind_is_low=True, opponent_advancing=True),
                 policy_stream())
    assert d.tactical != P.REST


def test_10c_an_empty_fighter_rests_regardless_of_wanting_not_to():
    d = P.decide(obs(wind_is_exhausted=True), policy_stream(),
                 P.Profile(aggression_bias=10000))
    assert d.tactical == P.REST and d.reason == P.R_RECOVER_WIND


# --- 11 & 12. range produces purposeful behaviour ----------------------------

def test_11_good_range_can_yield_hold_position():
    s = policy_stream()
    cold = P.Profile(aggression_bias=0)
    d = P.decide(obs(range_band="mid", preferred_band="mid"), s, cold)
    assert d.tactical == P.HOLD_POSITION
    assert d.reason in (P.R_HOLD_GOOD_RANGE, P.R_MANAGE_CLOCK)


def test_12_bad_range_yields_purposeful_movement():
    far = P.decide(obs(range_band="out_of_range", preferred_band="inside"),
                   policy_stream())
    assert far.tactical == P.ADVANCE
    assert far.reason == P.R_SEEK_PREFERRED_RANGE

    close = P.decide(obs(range_band="clinch", preferred_band="outside"),
                     policy_stream())
    assert close.tactical == P.RETREAT
    assert close.reason == P.R_EXIT_BAD_RANGE


# --- 13. an unavailable hand cannot be selected ------------------------------

def test_13_an_unavailable_hand_is_never_thrown():
    s = policy_stream()
    for _ in range(200):
        d = P.decide(obs(hands_available=("lead",), range_band="mid",
                         opponent_recovering=True), s)
        if d.execution:
            assert d.execution not in P.BY_HAND["rear"], (
                "threw %s with no rear hand available" % d.execution)


def test_13b_no_hands_means_no_attack_at_all():
    s = policy_stream()
    for _ in range(50):
        d = P.decide(obs(hands_available=(), opponent_recovering=True), s)
        assert d.tactical != P.ATTACK
        assert d.reason == P.R_HAND_UNAVAILABLE


def test_13c_attacks_are_legal_for_the_band():
    s = policy_stream()
    for band in P.BANDS:
        for _ in range(40):
            d = P.decide(obs(range_band=band, preferred_band=band,
                             opponent_recovering=True), s)
            if d.tactical == P.ATTACK:
                assert d.execution in P.BY_BAND[band], (
                    "%s is not throwable from %s" % (d.execution, band))


# --- 14. recovery cannot be illegally cancelled ------------------------------

def test_14_recovery_cannot_be_cancelled():
    s = policy_stream()
    for _ in range(50):
        d = P.decide(obs(in_recovery=True, recovery_ticks_left=9,
                         opponent_recovering=True, incoming_attack=True), s,
                     P.Profile(aggression_bias=10000))
        assert d.tactical == P.OBSERVE
        assert d.reason == P.R_STILL_RECOVERING


# --- 15. repeated failure changes the next tactical choice -------------------

def test_15_repeated_failure_changes_the_choice():
    s = policy_stream()
    fresh = P.decide(obs(consecutive_failed_attacks=0), s,
                     P.Profile(aggression_bias=10000))
    burned = P.decide(obs(consecutive_failed_attacks=2), s,
                      P.Profile(aggression_bias=10000))
    assert burned.tactical == P.HOLD_POSITION
    assert burned.reason == P.R_AVOID_OVERCOMMIT
    assert fresh.tactical != burned.tactical or fresh.reason != burned.reason


def test_15b_a_repeated_opponent_pattern_is_punished():
    d = P.decide(obs(opponent_recent_moves=("jab_lead",) * 4,
                     range_band="mid", preferred_band="mid"),
                 policy_stream())
    assert d.reason == P.R_PUNISH_REPEATED_JAB
    assert d.tactical == P.ATTACK


# --- 16. every decision carries a reason -------------------------------------

def test_16_every_decision_committed_or_deferred_has_a_reason():
    s = policy_stream()
    seen = set()
    cases = [
        {}, {"wind_is_low": True}, {"wind_is_exhausted": True},
        {"in_recovery": True, "recovery_ticks_left": 5},
        {"incoming_attack": True}, {"on_ropes": True}, {"cornered": True},
        {"hurt": True}, {"damaged_regions": ("body",)},
        {"opponent_recovering": True}, {"hands_available": ()},
        {"range_band": "out_of_range"}, {"range_band": "clinch"},
        {"consecutive_failed_attacks": 3},
        {"opponent_recent_moves": ("jab_lead",) * 4},
        {"ticks_left_in_round": 100},
        {"range_band": "out_of_range", "preferred_band": "out_of_range"},
    ]
    for kw in cases:
        for _ in range(12):
            d = P.decide(obs(**kw), s)
            assert d.reason in P.REASONS
            assert d.strategic in P.STRATEGIC
            assert d.tactical in P.TACTICAL
            assert "|" not in (d.execution or "")
            seen.add(d.reason)
    assert len(seen) >= 10, (
        "only %d distinct reasons across every situation - the policy is "
        "explaining less than it is doing: %s" % (len(seen), sorted(seen)))


# --- initiative is not aggression --------------------------------------------

def test_initiative_is_a_relationship_not_a_mood():
    walked_down = P.decide(obs(opponent_advancing=True), policy_stream())
    dictating = P.decide(obs(opponent_recovering=True), policy_stream())
    assert walked_down.initiative < dictating.initiative


def test_a_tired_fighter_can_still_want_initiative_while_resting():
    """The Director's distinction, checked rather than described."""
    d = P.decide(obs(wind_is_low=True, range_band="outside",
                     preferred_band="outside", opponent_recovering=False),
                 policy_stream(), P.Profile(aggression_bias=10000))
    assert d.tactical == P.REST
    assert d.strategic == P.RECOVER


def test_feint_is_reserved_but_never_produced():
    """A tactic in the enum but never in the logic is a promise the stream
    keeps making and never keeping."""
    assert P.FEINT_LATER not in P.TACTICAL
    s = policy_stream()
    for kw in ({}, {"wind_is_low": True}, {"opponent_recovering": True}):
        for _ in range(30):
            assert P.decide(obs(**kw), s).tactical != P.FEINT_LATER


def test_the_option_set_never_depends_on_iteration_order():
    a = P.legal_attacks(obs(range_band="inside"))
    b = P.legal_attacks(obs(range_band="inside",
                            hands_available=("rear", "lead")))
    assert a == b == tuple(sorted(a))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:20 UTC | END ]
