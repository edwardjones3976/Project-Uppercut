# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 01:20 UTC | START ]
"""Decision 0019 (gate G6): no coverage value sits on the interception threshold.

Two of the ten authored guards used to sit exactly on 0.60 - `philly_shell`'s
body lane and `active_hands`' head lane. A lane authored exactly at the threshold
is decided by the first point of arm damage, or by whichever way a rounding
lands, and neither of those two was authored as a knife edge.

This enforces the invariant for EVERY posture and lane, not the two that were
found, so the next authored guard cannot reintroduce it. The margin is canon
rather than a constant here, so widening it is a canon edit and not a test edit.
"""
import io
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import analyze_core_round as O  # noqa: E402


def _canon():
    pose = json.load(io.open(os.path.join(ROOT, "data", "pose_geometry.json"),
                             encoding="utf-8"))
    guard = json.load(io.open(os.path.join(ROOT, "data",
                                           "guard_evasion_model.json"),
                              encoding="utf-8"))
    return pose["guard"], guard["postures"]


def test_the_margin_is_canon_and_not_a_convention():
    g, _ = _canon()
    assert "authoring_margin" in g, (
        "pose_geometry.guard.authoring_margin is missing. Decision 0019 put the "
        "margin in canon precisely so it could be widened once and checked "
        "everywhere; a margin living in a test is a convention, not a rule.")
    assert g["authoring_margin"] > 0


def test_no_posture_lane_sits_within_the_margin_of_the_threshold():
    """Compared in the shared q10000 integer space, and that is not pedantry.

    In binary floating point 0.6 - 0.55 is 0.04999999999999999, so a margin rule
    written in floats fails a lane sitting exactly on the margin - a rule about
    knife edges, decided by a knife edge. The core reads every one of these
    numbers through `q()` anyway, so this is also simply what the simulation
    sees.
    """
    q = O.q
    g, postures = _canon()
    thr, margin = q(g["plane_interception_min_extent"]), q(g["authoring_margin"])
    offenders = []
    for p in postures:
        for lane, ext in p["extents"].items():
            if abs(q(ext) - thr) < margin:
                offenders.append("%s %s = %s (threshold %s, margin %s)"
                                 % (p["id"], lane, ext, thr, margin))
    assert not offenders, (
        "these lanes are authored on the knife edge of the interception "
        "threshold, so they are decided by the first point of arm damage or by "
        "a rounding:\n  " + "\n  ".join(offenders))


@pytest.mark.parametrize("pid,lane,side", [
    ("philly_shell", "guard_body", "exposed"),
    ("active_hands", "guard_high", "protected"),
])
def test_the_two_moved_lanes_moved_the_way_the_decision_said(pid, lane, side):
    """Direction is the decision, not just distance from the threshold.

    The shell is answered by bodywork, so its body lane belongs on the exposed
    side. Active hands parries with a behaviour this model cannot yet express,
    so its head lane is placed conservatively on the protected side. A future
    edit that satisfies the margin by moving either the wrong way would pass the
    test above and still be wrong.
    """
    g, postures = _canon()
    thr = g["plane_interception_min_extent"]
    ext = {p["id"]: p for p in postures}[pid]["extents"][lane]
    if side == "exposed":
        assert ext < thr, "%s %s must sit below the threshold" % (pid, lane)
    else:
        assert ext > thr, "%s %s must sit above the threshold" % (pid, lane)


def test_the_guard_table_still_answers_the_core_design_rule():
    """A guard protects some lanes and exposes others - still true after 0019.

    The rule this repository is built on says a guard is a body structure, not a
    quality score. If the margin work had accidentally pushed every lane to the
    protected side, the table would encode "more guard is better" instead, and
    every emergent matchup result would quietly become a ranking.
    """
    g, postures = _canon()
    thr = g["plane_interception_min_extent"]
    for p in postures:
        closed = [l for l, e in p["extents"].items() if e >= thr]
        open_ = [l for l, e in p["extents"].items() if e < thr]
        assert closed or open_
    assert any(p["extents"]["guard_body"] < thr for p in postures), \
        "no posture is beatable downstairs; body work has stopped paying"
    assert any(p["extents"]["guard_high"] < thr for p in postures), \
        "no posture is beatable upstairs"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 01:20 UTC | END ]
