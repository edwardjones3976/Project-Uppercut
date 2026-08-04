# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 23:40 UTC | START ]
"""Phase P - the hand is the unit. Proven before the C++, as every phase is.

These tests are about ONE claim: a committed fighter's defence depends on what he
threw. Under every earlier phase it did not - a single multiplier dimmed both
lanes together - and that is why the coefficient behaved as a switch rather than
a dial.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__))), "tools", "engine"))
import analyze_core_hands as P  # noqa: E402


def c():
    return P.canon_pack()


def test_no_new_coefficient_enters_this_phase():
    """Phase P uses committed_defense's authored 0.6 and posture extents. If a
    number appears here that canon did not author, this phase has stopped being
    a port and become an invention."""
    k = c()
    assert k["cd_mult"] == 6000, "canon's committed multiplier, 0.6"
    assert k["thr"] == 6000, "canon's interception threshold, 0.6"
    assert k["posture"]["high_guard"]["ext"]["high"] == 9500


def test_a_free_fighter_is_unchanged_from_earlier_phases():
    """Phase P must not alter a fighter who is not committed - otherwise it is
    not an extension, it is a rewrite."""
    k = c()
    for lane in ("high", "low"):
        assert P.coverage(k, "high_guard", lane, None, 10000) == \
            k["posture"]["high_guard"]["ext"][lane]


def test_the_lane_you_left_is_the_lane_that_opens():
    """Throw upstairs, be open upstairs."""
    k = c()
    after_head_punch = P.coverage(k, "high_guard", "high", "high", 10000)
    assert after_head_punch < k["thr"], "the vacated head lane must open"


def test_the_lane_your_free_hand_holds_stays_shut():
    """Dig to the body and your head lane is still covered - the difference the
    whole phase exists to express."""
    k = c()
    after_body_punch = P.coverage(k, "high_guard", "high", "low", 10000)
    assert after_body_punch >= k["thr"], "the unvacated head lane must stay closed"


def test_commitment_now_means_two_different_things():
    """The claim in one assertion: same posture, same commitment, opposite
    outcome, decided only by which punch the defender threw."""
    k = c()
    assert (P.coverage(k, "high_guard", "high", "high", 10000) <
            P.coverage(k, "high_guard", "high", "low", 10000))


def test_the_0_6316_cliff_is_dissolved():
    k = c()
    assert P.cliff_is_dissolved(k)


def test_arm_damage_still_erodes_coverage_underneath():
    """Phase N's impairment must survive Phase P: a worn guard covers less
    whichever hand is home."""
    k = c()
    fresh = P.coverage(k, "high_guard", "high", "low", 10000)
    worn = P.coverage(k, "high_guard", "high", "low", 6000)
    assert worn < fresh


def test_the_mirror_posture_mirrors():
    """tight_elbow is high_guard's mirror in canon; the per-hand rule must not
    quietly privilege one posture."""
    k = c()
    assert (P.coverage(k, "tight_elbow", "low", "low", 10000) <
            P.coverage(k, "tight_elbow", "low", "high", 10000))


def test_vacated_lane_is_derived_from_canon_not_hardcoded():
    k = c()
    assert P.vacated_lane(k, "jab_lead") == k["moves"]["jab_lead"]["height"]
    assert P.vacated_lane(k, "body_straight_rear") == \
        k["moves"]["body_straight_rear"]["height"]
    assert P.vacated_lane(k, None) is None


def test_the_guard_is_not_vacuously_always_open():
    """A rule that opens every lane would 'work' and mean nothing."""
    k = c()
    opens = [P.coverage(k, p, lane, vac, 10000) < k["thr"]
             for p in ("high_guard", "tight_elbow")
             for lane in ("high", "low")
             for vac in (None, "high", "low")]
    assert any(opens) and not all(opens)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 23:40 UTC | END ]
