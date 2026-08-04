# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | START ]
"""Phase N analyzer, proven before the C++ that it judges exists.

The discipline every phase has followed: an analyzer that cannot detect a
mutation is not a contract, it is a rubber stamp. Each test below takes the
analyzer's own recomputation, breaks exactly one thing a wrong implementation
would plausibly get wrong, and requires the analyzer to notice.
"""
import io
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "tools", "engine"))
import analyze_core_condition as A  # noqa: E402

SEED, TICKS = 4242, 5400


@pytest.fixture(scope="module")
def stream() -> str:
    return A.expected_stream(SEED, TICKS)


def _write(tmp_path, text: str) -> str:
    p = os.path.join(str(tmp_path), "markers.txt")
    io.open(p, "w", encoding="utf-8", newline="\n").write(text)
    return p


def test_canon_is_coherent():
    """The contract refuses to judge anything if canon itself cannot support the
    phase - an unreachable emergence is a canon defect, not a stream defect."""
    assert A.canon_pack()["canon_errors"] == []


def test_the_honest_stream_passes(tmp_path, stream):
    rep = A.analyse(_write(tmp_path, stream))
    assert rep["ok"], rep["errors"]
    assert rep["punch_rows"] > 50
    assert rep["condition_rows"] > 0


def test_damage_accumulates_on_the_canonical_run(tmp_path, stream):
    rep = A.analyse(_write(tmp_path, stream))
    assert rep["damage"] > 0
    # At the canonical length the erosion has NOT yet reached the threshold, and
    # the analyzer must say so as a note rather than pass in silence.
    assert rep["opened"] == 0
    assert any("guard erosion did not fire" in n for n in rep["notes"])


def test_the_guard_actually_erodes_at_the_reachability_horizon(tmp_path):
    """The phase's claim, tested where canon's own coefficients allow it to be
    true. This is the slow test on purpose: the horizon is the finding."""
    long_stream = A.expected_stream(SEED, A.REACH_TICKS)
    rep = A.analyse(_write(tmp_path, long_stream))
    assert rep["ok"], rep["errors"]
    assert rep["opened"] > 0, "the erosion never fired even past its own horizon"


def test_the_horizon_is_where_the_contract_says_it_is(tmp_path):
    """Guards the finding itself. If a canon edit moves the coefficients, this
    fails and the docstring's arithmetic gets revisited instead of rotting."""
    short = A.expected_stream(SEED, A.REACH_TICKS // 2, with_floats=False)
    trail = [l for l in short.splitlines() if l.startswith("S|")][0]
    opened = int(dict(kv.split("=") for kv in trail[2:].split("|"))["opened"])
    assert opened == 0, ("erosion now fires at half the recorded horizon - canon "
                         "has changed and the finding needs rewriting")


def test_damage_that_runs_backwards_is_caught(tmp_path, stream):
    lines = stream.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("C|") and int(l.split("|")[3]) > 0:
            f = l.split("|")
            f[3] = "0"
            lines[n] = "|".join(f)
            break
    rep = A.analyse(_write(tmp_path, "\n".join(lines) + "\n"))
    assert not rep["ok"]


def test_force_that_the_cost_does_not_justify_is_caught(tmp_path, stream):
    lines = stream.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("P|") and l.split("|")[4] == "landed":
            f = l.split("|")
            f[11] = str(int(f[11]) + 1)
            lines[n] = "|".join(f)
            break
    rep = A.analyse(_write(tmp_path, "\n".join(lines) + "\n"))
    assert not rep["ok"]


def test_landing_through_a_covered_lane_is_caught(tmp_path, stream):
    """A landing whose reported extent still covers the lane is the single most
    dangerous wrong answer: it is the guard model silently not working."""
    lines = stream.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("P|") and l.split("|")[4] == "landed":
            f = l.split("|")
            f[12] = str(A.canon_pack()["thr"] + 1)
            lines[n] = "|".join(f)
            break
    rep = A.analyse(_write(tmp_path, "\n".join(lines) + "\n"))
    assert not rep["ok"]


def test_a_block_that_delivered_force_is_caught(tmp_path, stream):
    lines = stream.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("P|") and l.split("|")[4] == "blocked":
            f = l.split("|")
            f[11] = "1234"
            lines[n] = "|".join(f)
            break
    rep = A.analyse(_write(tmp_path, "\n".join(lines) + "\n"))
    assert not rep["ok"]


def test_capacity_overflow_is_caught(tmp_path, stream):
    lines = stream.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("C|"):
            f = l.split("|")
            f[3] = str(A.canon_pack()["cap"]["head"] + 1)
            lines[n] = "|".join(f)
            break
    rep = A.analyse(_write(tmp_path, "\n".join(lines) + "\n"))
    assert not rep["ok"]


def test_impairment_multiplier_out_of_range_is_caught(tmp_path, stream):
    lines = stream.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("C|"):
            f = l.split("|")
            f[9] = "10001"
            lines[n] = "|".join(f)
            break
    rep = A.analyse(_write(tmp_path, "\n".join(lines) + "\n"))
    assert not rep["ok"]


def test_trailer_hash_covers_the_condition_rows(tmp_path, stream):
    """C rows must be inside the FNV blob. If they are not, a wrong condition
    layer could ride along under a correct-looking hash."""
    lines = [l for l in stream.splitlines() if not l.startswith("C|")]
    rep = A.analyse(_write(tmp_path, "\n".join(lines) + "\n"))
    assert not rep["ok"]


def test_a_shifted_canon_hash_is_caught(tmp_path, stream):
    lines = stream.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("H|canon_punch="):
            lines[n] = "H|canon_punch=" + "0" * 64
            break
    rep = A.analyse(_write(tmp_path, "\n".join(lines) + "\n"))
    assert not rep["ok"]


def test_a_single_flipped_digit_anywhere_is_caught(tmp_path, stream):
    lines = stream.splitlines()
    for n, l in enumerate(lines):
        if l.startswith("D|"):
            f = l.split("|")
            f[9] = str(int(f[9]) + 1)      # one stamina unit
            lines[n] = "|".join(f)
            break
    rep = A.analyse(_write(tmp_path, "\n".join(lines) + "\n"))
    assert not rep["ok"]


def test_impact_is_normalized_over_the_punch_table_only(tmp_path):
    """delivered_impact must rank the punches by what they cost. If a step's
    cost leaked into the normalization the jab would stop being the floor."""
    c = A.canon_pack()
    order = [c["moves"][m]["impact"] for m in
             ("jab_lead", "hook_lead", "cross_rear", "body_straight_rear", "uppercut_rear")]
    assert order == sorted(order), "impact does not rise with stamina cost"
    assert c["moves"]["jab_lead"]["impact"] == c["imp_min"]
    assert c["moves"]["uppercut_rear"]["impact"] < c["imp_max"]
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | END ]
