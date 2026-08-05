# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 07:50 UTC | START ]
"""Phase Q - the fight has a distance. Contract tests.

These prove the RULES, not a balance outcome. Whether range closes Phase O is a
measurement and it lives in `experiment_range_model`; what belongs here is that
the model reads canon rather than inventing, that its bands tile the line, that
footwork can actually change a band, that running is finite, and - the control
that matters most - that the range runner with both switches off reproduces the
Phase O fight byte for byte, so the phase is a strict superset of the one it
extends rather than a fork of it.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import analyze_core_range as Q       # noqa: E402
import analyze_core_round as O       # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402
import experiment_range_model as R   # noqa: E402


@pytest.fixture(scope="module")
def rc():
    return Q.range_pack()


def test_canon_is_accepted(rc):
    """The analyzer refuses canon it cannot execute; canon must pass."""
    assert rc["canon_errors"] == []


def test_bands_tile_the_line_with_no_gap(rc):
    for (ka, _, hia), (kb, lob, _) in zip(rc["bands"], rc["bands"][1:]):
        assert hia == lob, "%s and %s do not meet" % (ka, kb)
    assert rc["bands"][0][1] == 0
    assert rc["bands"][-1][2] is None


def test_every_separation_has_exactly_one_band(rc):
    for sep in range(0, 20000, 137):
        hits = [k for k, lo, hi in rc["bands"]
                if sep >= lo and (hi is None or sep < hi)]
        assert len(hits) == 1, "separation %d matched %r" % (sep, hits)


def test_move_bands_come_from_canon_not_from_here(rc):
    """Every punch the core throws must have an authored band."""
    for m in O.PUNCHES:
        assert m in rc["move_band"], "%s has no authored range_band" % m


def test_the_uppercut_is_an_inside_punch(rc):
    """The defect that started this phase, stated as a property."""
    assert rc["move_band"]["uppercut_rear"] == "inside"
    assert not Q.in_band(rc, "uppercut_rear", "mid")


def test_the_hook_was_landing_from_the_wrong_band(rc):
    """The same defect with the opposite sign, and the reason it went unseen."""
    assert rc["move_band"]["hook_lead"] == "inside"
    assert not Q.in_band(rc, "hook_lead", "mid")
    assert Q.band_at(rc, R.START_SEP) == "mid"


def test_an_unauthored_move_is_refused_not_permitted(rc):
    """A missing band must not read as 'legal everywhere'."""
    assert not Q.in_band(rc, "no_such_move", "mid")


def test_hysteresis_holds_the_band_across_a_boundary(rc):
    assert Q.hysteresis_kills_flicker(rc)


def test_hysteresis_is_smaller_than_every_band(rc):
    widths = [hi - lo for _, lo, hi in rc["bands"] if hi is not None]
    assert rc["hyst"] < min(widths)


def test_a_stride_takes_more_than_one_tick(rc):
    """Canon's per-tick cap sits below every stride: no teleports, and a man
    can be caught mid-step."""
    assert rc["cap"] < rc["stride"]
    pending, ticks = rc["stride"], 0
    while pending:
        _, pending = Q.drain(rc, pending)
        ticks += 1
        assert ticks < 50
    assert ticks > 1


def test_footwork_can_change_the_band(rc):
    assert Q.footwork_is_not_inert(rc)


def test_the_uppercut_becomes_reachable_by_walking(rc):
    assert Q.the_uppercut_becomes_possible(rc)


def test_running_is_finite(rc):
    """With his back on the ropes a retreat buys nothing - canon's own
    anti-running rule, and the thing that stops a coin drifting to
    out_of_range and staying there."""
    assert Q.running_is_finite(rc)


def test_bodies_do_not_overlap(rc):
    assert Q.clamp_separation(rc, 0) == rc["min_sep"]
    assert rc["min_sep"] < rc["bands"][0][2], "the clinch would be unreachable"


def test_the_range_runner_is_a_strict_superset_of_phase_o(rc):
    """The control. Both switches off must be the Phase O fight exactly - if it
    is not, every comparison drawn from this runner is against a different
    fight and means nothing."""
    c = O.canon_pack()
    for seed in (4240, 4247, 4255, 4263):
        base = H.run(seed)
        got = R.run_range(seed, c, rc, 3, None, gate=False, footwork=False)
        for k in ("blocked", "landed", "knockdowns", "thrown", "rounds",
                  "stopped", "eligible", "total_ticks", "first_kd_tick",
                  "stop_tick"):
            assert got[k] == base[k], "seed %d diverged on %s" % (seed, k)


def test_every_out_of_band_punch_whiffs_and_only_those(rc):
    """Rule 12 as an exact accounting identity, not as a comparison.

    NOTE, because the first version of this test was wrong in an instructive
    way: it asserted that switching the gate on can only REDUCE landings in a
    given seed, and that is false. A whiffed punch never draws its alignment
    number, so the shared LCG stream diverges from the tick the first punch is
    refused, and a gated bout is a different bout - it also runs longer, because
    it produces fewer knockdowns, and a longer bout contains more of everything.
    That is precisely the confound that invalidated four conclusions on
    2026-08-05, reappearing inside a test. The property that IS true is a
    within-bout identity, so that is what is asserted.
    """
    c = O.canon_pack()
    inside = [m for m in O.PUNCHES if rc["move_band"][m] == "inside"]
    assert inside, "the fixture assumes some punch is an inside-band punch"
    for seed in (4241, 4250):
        # Footwork off pins the band at mid for the whole bout, which makes the
        # expected whiff set exactly the inside-band punches thrown.
        on = R.run_range(seed, c, rc, 3, None, gate=True, footwork=False)
        expected = sum(on["thrown_in_band"].get(m, [0, 0])[0] for m in inside)
        # Exact, up to punches still in the air when the bout ends - at most one
        # per fighter, because a fighter has at most one punch out at a time.
        assert on["whiffed"] <= expected
        assert expected - on["whiffed"] <= 2
        for m in inside:
            assert on["thrown_in_band"].get(m, [0, 0])[1] == 0
        for m in O.PUNCHES:
            if m not in inside:
                t, ok = on["thrown_in_band"].get(m, [0, 0])
                assert ok == t


def test_a_gated_punch_still_costs_its_commitment(rc):
    """'It travels its full arc and pays the whiff.' A doomed punch is still
    thrown, still counted, and still occupies its frames - so throws do not
    collapse when the gate goes on, and every thrown punch is accounted for."""
    c = O.canon_pack()
    on = R.run_range(4243, c, rc, 3, None, gate=True, footwork=False)
    assert on["thrown"] > 0
    assert on["whiffed"] > 0
    # Nothing is lost: every punch either whiffed, was blocked, landed, or is
    # still in the air at the bell.
    assert on["whiffed"] + on["blocked"] + on["landed"] <= on["thrown"]
    assert on["thrown"] - (on["whiffed"] + on["blocked"] + on["landed"]) <= 2
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 07:50 UTC | END ]
