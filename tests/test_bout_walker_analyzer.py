# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:16 UTC | START ]
"""The Phase F analyzer, proven to fail on every defect it claims to catch.

The engine run this analyzer judges cannot be executed while an interactive editor
holds the sandbox, so the analyzer is built and proven FIRST, against synthetic marker
streams. That ordering is deliberate: the analyzer is the part of an engine phase most
able to fake a pass, because a leak detector that never fires looks exactly like a
clean run. Every test below plants one defect and asserts it is caught.
"""
from __future__ import annotations
import importlib.util
import pathlib

_SPEC = importlib.util.spec_from_file_location(
    "analyze_bout_walker",
    pathlib.Path(__file__).resolve().parents[1] / "tools" / "engine" / "analyze_bout_walker.py")
abw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(abw)

ROUND_TICKS = 8
ROUNDS = 3
ACTORS = 2


def _stream(round_ticks=ROUND_TICKS, rounds=ROUNDS, actors=ACTORS,
            reset_at_boundary=True, leak_sealed=False, own_clock=False,
            frozen=False):
    """A synthetic marker stream shaped exactly like the Blueprint's output."""
    lines = []
    acc = {i: 0 for i in range(actors)}
    total = round_ticks * rounds
    for tick in range(1, total + 1):
        for i in range(actors):
            rnd, tir = divmod(tick - 1, round_ticks)
            if own_clock and tick > round_ticks:
                rnd, tir = 0, tick - 1          # a Blueprint keeping its own count
            if tir == 0 and tick > 1 and reset_at_boundary:
                acc[i] = 0
            if not frozen:
                acc[i] += 1000 + i
            lines.append(f"B|{i}|{rnd}|{tir}|{acc[i]}")
            if leak_sealed and tick == total // 2:
                lines.append(f"S|{i}|{rnd}|{acc[i]}")
    if not leak_sealed:
        for i in range(actors):
            lines.append(f"S|{i}|{rounds - 1}|{acc[i]}")
    return lines


def _errs(**kw):
    rep = abw.analyse(_stream(**kw), ROUND_TICKS, ROUNDS, "synthetic")
    return rep["errors"]


def test_a_clean_stream_passes():
    assert _errs() == []


def test_a_leaked_scorecard_is_caught():
    """The defect a hash cannot see: a sealed card emitted while the fight runs is
    perfectly reproducible and still a Rule 3 violation."""
    errs = _errs(leak_sealed=True)
    assert any("SEALED LEAK" in e for e in errs)


def test_a_stream_with_no_sealed_card_is_caught():
    """The opposite failure. A check that only forbids passes trivially when the
    thing it forbids never happens."""
    lines = [ln for ln in _stream() if not ln.startswith("S|")]
    rep = abw.analyse(lines, ROUND_TICKS, ROUNDS, "no-sealed")
    assert any("sealed path is untested" in e for e in rep["errors"])


def test_a_blueprint_keeping_its_own_clock_is_caught():
    """Rule 8: round boundaries are recomputed from the authoritative tick, never
    trusted from the marker."""
    errs = _errs(own_clock=True)
    assert any("keeping its own clock" in e for e in errs)


def test_an_accumulator_that_never_resets_is_caught():
    """The exact defect the reference model shipped in _score_round: summing the bout
    to date, so an early lead re-wins every later round. It was found by a balance
    sweep rather than by a check, which is why this check exists."""
    errs = _errs(reset_at_boundary=False)
    assert any("rose across a round boundary" in e for e in errs)


def test_a_frozen_accumulator_is_caught():
    """Stuck at zero resets perfectly at every boundary and proves nothing."""
    errs = _errs(frozen=True)
    assert any("vacuous pass" in e for e in errs)


def test_an_empty_stream_is_caught():
    rep = abw.analyse([], ROUND_TICKS, ROUNDS, "empty")
    assert any("nothing ran" in e for e in rep["errors"])


def test_a_short_bout_is_caught():
    """A run that stopped early would otherwise look clean on every other axis."""
    lines = _stream(rounds=2)
    rep = abw.analyse(lines, ROUND_TICKS, ROUNDS, "short")
    assert any("did not run its scheduled length" in e for e in rep["errors"])


def test_the_analyzer_reads_the_tick_rate_from_canon():
    rep = abw.analyse(_stream(), ROUND_TICKS, ROUNDS, "synthetic")
    assert rep["tick_rate_hz"] == 60
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:16 UTC | END ]
