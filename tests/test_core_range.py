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


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:05 UTC | START ]
"""Phase Q marker stream - the tests that make the C++ port provable.

The tests above prove the rules. These prove the ARTIFACT: that the stream is a
function of nothing but seed and ticks, that it is internally coherent when read
back cold, and - the two that would catch a plausible port - that the band gate
and the per-tick displacement cap are both load-bearing, demonstrated by
breaking each one and watching the stream change.
"""
import io as _io

SEED, TICKS = 4242, 900


@pytest.fixture(scope="module")
def qs():
    return Q.expected_stream(SEED, TICKS)


def test_the_stream_is_a_function_of_its_arguments(qs):
    """No clock, no path, no dict ordering: same arguments, same bytes."""
    assert Q.expected_stream(SEED, TICKS) == qs


def test_the_header_names_every_canon_file_the_phase_reads(qs):
    named = {l.split("=")[0][len("H|canon_"):] for l in qs.splitlines()
             if l.startswith("H|canon_")}
    assert named == {"movement", "moves", "animation", "pose"}


def test_a_stream_read_back_cold_is_coherent(qs, tmp_path):
    """`analyse` re-derives the trailer from the rows. It must agree."""
    p = os.path.join(str(tmp_path), "q.stream")
    with _io.open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(qs)
    assert Q.analyse(p)["errors"] == []


def test_a_landing_is_never_recorded_from_an_undeclared_band(qs):
    for line in qs.splitlines():
        if line.startswith("P|") and line.split("|")[4] == "landed":
            assert line.split("|")[10] == "1", line


def test_nothing_ever_moves_further_than_the_cap_in_one_tick(qs):
    cap = Q.stream_pack()["cap"]
    for line in qs.splitlines():
        if line.startswith("X|"):
            assert abs(int(line.split("|")[3])) <= cap, line


def test_separation_never_falls_inside_the_body_floor(qs):
    # The separation field sits in a different column in the two row kinds: an
    # X row carries `applied` ahead of the positions and a D row carries the
    # action and the LCG word. Reading column 6 in both would test pos1 in one
    # of them and pass for the wrong reason.
    floor = Q.stream_pack()["min_sep"]
    for line in qs.splitlines():
        f = line.split("|")
        if f[0] == "X":
            assert int(f[6]) >= floor, line
        elif f[0] == "D":
            assert int(f[7]) >= floor, line


def _trailer(stream: str) -> dict:
    s = next(l for l in stream.splitlines() if l.startswith("S|"))
    return dict(kv.split("=", 1) for kv in s.split("|")[1:])


def test_the_band_gate_is_load_bearing(monkeypatch, qs):
    """Break the gate and the fight must change.

    A port that evaluated geometry first and treated the band as advisory would
    pass every test above. It would not pass this one: with the gate stuck open
    every wrong-band punch that arrives becomes a landing, so `whiff_band` must
    empty and `landed` must rise.
    """
    before = _trailer(qs)
    monkeypatch.setattr(Q, "in_band", lambda c, mid, band: True)
    after = _trailer(Q.expected_stream(SEED, TICKS))
    assert int(before["whiff_band"]) > 0, "the honest stream has no gate to break"
    assert int(after["whiff_band"]) == 0
    assert int(after["landed"]) > int(before["landed"])


def test_the_displacement_cap_is_load_bearing(monkeypatch, qs):
    """A stride delivered in one tick is a teleport, and it is a different fight.

    Canon's cap is per frame and sits below every stride, which is what lets a
    fighter be caught mid-step. Remove it and the stream must differ - if it did
    not, the cap would be decoration.
    """
    monkeypatch.setattr(Q, "drain", lambda c, pending: (pending, 0))
    assert Q.expected_stream(SEED, TICKS) != qs


def test_the_properties_are_carried_inside_the_hash(qs):
    """A port has to prove the properties, not merely append them.

    The V rows sit above the trailer and inside its self-hash, so a port that
    printed `V|running_is_finite|1` without the model that makes it true would
    still have to match every row that model produced.
    """
    rows = [l for l in qs.splitlines()
            if not l.startswith(("H|", "B|", "K|", "M|", "S|"))]
    props = {l.split("|")[1]: l.split("|")[2] for l in rows if l.startswith("V|")}
    assert props == {"footwork_is_not_inert": "1", "uppercut_is_reachable": "1",
                     "hysteresis_kills_flicker": "1", "running_is_finite": "1",
                     "canon_errors": "0"}
    h = Q.fnv1a64("".join(r + "\n" for r in rows).encode("utf-8"))
    assert "%016x" % h == _trailer(qs)["fnv1a64"]
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:05 UTC | END ]
