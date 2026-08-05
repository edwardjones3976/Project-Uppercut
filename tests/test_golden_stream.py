# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:10 UTC | START ]
"""The Phase O stream must not move without somebody saying so.

Until now the target a C++ port has to reproduce existed only as "whatever
`expected_stream` returns today". That is a target that moves silently, and it
moved silently once already: on 2026-08-04 a sealed analyzer was edited, Phase
N's recomputation changed hash, and the whole suite still passed because every
test regenerated from the same edited analyzer. Nothing compared it to anything
committed.

`test_phase_evidence_pins.py` fixed that for the two PROVEN phases by pinning
their hashes. This fixes it for the phase about to be ported, by committing the
stream itself. A hash says something moved; the file says what.

WHEN THIS FAILS AND THAT IS CORRECT: Phase O is HELD, and deciding any of the
three canon quantities (G1 step cost, G2 rest semantics, G3 aggression) will
change the fight and therefore this file. The re-blessing belongs in the SAME
commit as the ruling, so a canon decision and its consequence are one reviewable
change:

    python -m tools.engine.golden --diff     # see it as a fight, not a hash
    python -m tools.engine.golden --write    # re-bless
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import golden  # noqa: E402


def test_the_golden_stream_exists_and_is_committed():
    p = os.path.join(ROOT, golden.PATH)
    assert os.path.exists(p), (
        "%s is missing. It is the target a C++ port must reproduce; write it "
        "with `python -m tools.engine.golden --write`." % golden.PATH)


def test_the_analyzer_still_produces_the_golden_stream():
    want, got = golden.stored(), golden.current()
    assert want is not None, "no golden file to compare against"
    if want == got:
        return
    # Give the failure the same shape the tool does, so the message is useful
    # without having to go and run something else.
    w, g = want.splitlines(), got.splitlines()
    first = next((i for i in range(min(len(w), len(g))) if w[i] != g[i]),
                 min(len(w), len(g)))
    raise AssertionError(
        "the Phase O stream has drifted from its committed golden file.\n"
        "  stored  %d lines\n  current %d lines\n"
        "  first difference at line %d:\n    was %s\n    now %s\n"
        "If deliberate, re-bless in the SAME commit as the change:\n"
        "    python -m tools.engine.golden --write"
        % (len(w), len(g), first + 1,
           golden.describe(w[first]) if first < len(w) else "(nothing)",
           golden.describe(g[first]) if first < len(g) else "(nothing)"))


def test_the_golden_file_is_the_canonical_stream_not_a_diagnostic_one():
    """No `E` rows and no float probe: the golden file is what a C++ port has to
    match, and neither of those is part of that."""
    want = golden.stored()
    assert want
    assert not any(l.startswith("E|") for l in want.splitlines()), \
        "the golden stream contains opt-in diagnostic rows"
    assert not any(l.startswith("F|") for l in want.splitlines()), \
        "the golden stream contains float-probe rows"


def test_the_describer_handles_every_row_kind_present():
    """The diff is only useful if it can put every row into words."""
    want = golden.stored()
    kinds = {l.split("|")[0] for l in want.splitlines() if l}
    for k in kinds:
        sample = next(l for l in want.splitlines() if l.startswith(k + "|"))
        text = golden.describe(sample)
        assert text and text != sample, \
            "row kind %r has no human description; the diff would be raw" % k
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:10 UTC | END ]
