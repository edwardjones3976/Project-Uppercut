# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:35 UTC | START ]
"""A pinned stream must not move without somebody saying so.

Until these pins existed, the target a C++ port has to reproduce was only ever
"whatever `expected_stream` returns today". That is a target that moves
silently, and it moved silently once already: on 2026-08-04 a sealed analyzer
was edited, Phase N's recomputation changed hash, and the whole suite still
passed because every test regenerated from the same edited analyzer. Nothing
compared it to anything committed.

TWO PINS, TWO REASONS.

  O is HELD with no C++ yet. Its pin WILL fail when G1 (step cost), G2 (rest
    semantics) or G3 (aggression) is decided, and that failure is correct. The
    re-blessing belongs in the SAME commit as the ruling, so a canon decision
    and its consequence are one reviewable change.

  Q is PROVEN: the commandlet reproduces the contract byte for byte. Its pin is
    what keeps that proof meaningful without an engine - parity needs Unreal and
    two minutes, but noticing that somebody moved the contract out from under a
    proven port needs only this test. If it fails, the port is not proven any
    more until `python -m tools.engine.prove_core_range` says otherwise.

    python -m tools.engine.golden --diff     # see it as a fight, not a hash
    python -m tools.engine.golden --write    # re-bless
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import golden  # noqa: E402

PHASES = sorted(golden.PINS)


@pytest.mark.parametrize("phase", PHASES)
def test_the_golden_stream_exists_and_is_committed(phase):
    p = os.path.join(ROOT, golden.PINS[phase]["path"])
    assert os.path.exists(p), (
        "%s is missing. It is the target a C++ port must reproduce; write it "
        "with `python -m tools.engine.golden --phase=%s --write`."
        % (golden.PINS[phase]["path"], phase))


@pytest.mark.parametrize("phase", PHASES)
def test_the_analyzer_still_produces_the_golden_stream(phase):
    want, got = golden.stored(phase), golden.current(phase)
    assert want is not None, "no golden file to compare against"
    if want == got:
        return
    # Give the failure the same shape the tool does, so the message is useful
    # without having to go and run something else.
    w, g = want.splitlines(), got.splitlines()
    first = next((i for i in range(min(len(w), len(g))) if w[i] != g[i]),
                 min(len(w), len(g)))
    extra = ("\nPhase Q has a C++ port proven against these exact bytes. Re-run\n"
             "    python -m tools.engine.prove_core_range\n"
             "before re-blessing." if phase == "Q" else "")
    raise AssertionError(
        "the Phase %s stream has drifted from its committed golden file.\n"
        "  stored  %d lines\n  current %d lines\n"
        "  first difference at line %d:\n    was %s\n    now %s%s\n"
        "If deliberate, re-bless in the SAME commit as the change:\n"
        "    python -m tools.engine.golden --phase=%s --write"
        % (phase, len(w), len(g), first + 1,
           golden.describe(phase, w[first]) if first < len(w) else "(nothing)",
           golden.describe(phase, g[first]) if first < len(g) else "(nothing)",
           extra, phase))


def test_the_phase_o_file_is_the_canonical_stream_not_a_diagnostic_one():
    """No `E` rows and no float probe: the golden file is what a C++ port has to
    match, and neither of those is part of that."""
    want = golden.stored("O")
    assert want
    assert not any(l.startswith("E|") for l in want.splitlines()), \
        "the golden stream contains opt-in diagnostic rows"
    assert not any(l.startswith("F|") for l in want.splitlines()), \
        "the golden stream contains float-probe rows"


@pytest.mark.parametrize("phase", PHASES)
def test_the_describer_handles_every_row_kind_present(phase):
    """The diff is only useful if it can put every row into words."""
    want = golden.stored(phase)
    kinds = {l.split("|")[0] for l in want.splitlines() if l}
    for k in kinds:
        sample = next(l for l in want.splitlines() if l.startswith(k + "|"))
        text = golden.describe(phase, sample)
        assert text and text != sample, \
            "row kind %r has no human description; the diff would be raw" % k


def test_each_phase_has_its_own_describer():
    """`R` means end-of-round in Phase O and a band transition in Phase Q.

    One shared describer would have rendered one of them as a lie, which is
    worse than rendering it raw - so this asserts the split stays.
    """
    row = "R|100|0|inside|mid|7600"
    assert golden.describe("O", row) != golden.describe("Q", row)
    assert "passed from inside into mid" in golden.describe("Q", row)
    assert "end of round" in golden.describe("O", row)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:35 UTC | END ]
