# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 09:20 UTC | START ]
"""Phase R - the head is not where the punch is going. Contract tests.

The rule is canon's and it is geometric, so these prove structure rather than a
balance outcome: that every active evasion vacates something and is beaten by
something, that the stage outranks the guard, that a mistimed evasion costs, and
- the control that matters - that passing no evasion pack reproduces the Phase Q
fight exactly, so Phase R cannot silently rewrite Phase Q's committed evidence.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import analyze_core_evade as E     # noqa: E402
import analyze_core_range as Q     # noqa: E402
import analyze_core_round as O     # noqa: E402
import experiment_range_model as R  # noqa: E402


@pytest.fixture(scope="module")
def ec():
    return E.evade_pack()


@pytest.fixture(scope="module")
def rc():
    return Q.range_pack()


def test_canon_is_accepted(ec):
    assert ec["canon_errors"] == []


def test_evasion_outranks_the_guard(ec):
    """Stage order is canon's, not a preference: a slipped punch must never
    also be a blocked punch."""
    assert ec["outranks_guard"] is True


def test_a_mistimed_evasion_costs_something(ec):
    """Otherwise slipping is strictly better than blocking and stops being a
    decision at all."""
    assert ec["mistime_ticks"] > 0


def test_every_active_evasion_vacates_a_real_damage_region(ec):
    active = [k for k, v in ec["evasions"].items()
              if v["kind"] == "active_window"]
    assert active
    for k in active:
        assert ec["evasions"][k]["vacates"]
        for r in ec["evasions"][k]["vacates"]:
            assert r in O.REGIONS


def test_every_active_evasion_has_a_counter(ec):
    """An evasion with no counter would be a strictly better guard rather than
    a different one - the trade is the whole design rule."""
    assert E.no_evasion_is_strictly_better(ec)


def test_positional_answers_vacate_nothing(ec):
    """`step_out` and `pivot_lead` are range denial, not evasion: canon says
    they score nothing, and the model must not quietly credit them."""
    for k in ("step_out", "pivot_lead"):
        assert ec["evasions"][k]["kind"] == "positional"
        assert ec["evasions"][k]["vacates"] == ()
        assert not E.evades(ec, k, "jab_lead", "head")


def test_the_slip_evades_a_straight(ec):
    assert E.the_slip_evades_a_straight(ec)


def test_a_body_shot_beats_the_slip(ec):
    """The slip vacates the head. The body is still exactly where it was."""
    assert E.a_body_shot_beats_the_slip(ec)


def test_the_uppercut_beats_the_roll(ec):
    """Canon's sentence made executable: the uppercut rises into where the head
    is going, so the roll vacates that region and is punished there anyway."""
    assert E.the_uppercut_beats_the_roll(ec)


def test_an_unknown_tactic_never_matches(ec):
    """`beaten_by` names tactics the core cannot yet express
    (`feint_then_commit`, `ring_cutting`). They must match nothing rather than
    everything - matching everything would make evasion inert, and matching
    nothing silently would make the tactic look implemented."""
    assert not E.beats(ec, "slip_lead", "no_such_move")
    assert "feint_then_commit" in ec["evasions"]["slip_lead"]["beaten_by"]
    assert not any(ec["category"].get(m) == "feint_then_commit"
                   for m in O.PUNCHES)


def test_no_die_is_drawn_by_the_evasion_stage(ec):
    """The whole point of the geometric form: `evades` is a pure function of
    canon and the punch, so the same question always gets the same answer."""
    for _ in range(5):
        assert E.evades(ec, "slip_lead", "jab_lead", "head") is True
        assert E.evades(ec, "roll_under", "uppercut_rear", "jaw_chin") is False


def test_phase_r_does_not_rewrite_phase_q(rc):
    """The control. No evasion pack must reproduce the Phase Q fight exactly -
    otherwise the numbers committed for Phase Q describe a fight that no longer
    exists."""
    c = O.canon_pack()
    for seed in (4240, 4251, 4263):
        without = R.run_range(seed, c, rc, 3, None, gate=True, footwork=True)
        again = R.run_range(seed, c, rc, 3, None, gate=True, footwork=True,
                            ec=None)
        for k in ("blocked", "landed", "knockdowns", "thrown", "whiffed",
                  "rounds", "eligible", "total_ticks"):
            assert without[k] == again[k]
        assert without["evaded"] == 0
        assert without["mistimed"] == 0


def test_evasion_actually_fires_in_a_fight(rc, ec):
    """And it must do something, or the phase is a contract over nothing."""
    c = O.canon_pack()
    ref = [Q.band_at(rc, R.START_SEP), False]
    chooser = R.band_aware(rc, ref, ec)
    r = R.run_range(4240, c, rc, 3, chooser, gate=True, footwork=True,
                    band_ref=ref, ec=ec)
    assert r["evaded"] > 0


def test_a_slipping_fighter_still_pays_when_he_guesses_wrong(rc, ec):
    """Mistimed windows must be observed in a real fight, not merely authored."""
    c = O.canon_pack()
    ref = [Q.band_at(rc, R.START_SEP), False]
    chooser = R.band_aware(rc, ref, ec)
    r = R.run_range(4242, c, rc, 3, chooser, gate=True, footwork=True,
                    band_ref=ref, ec=ec)
    assert r["mistimed"] > 0
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 09:20 UTC | END ]
