# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:05 UTC | START ]
"""Semantic drift: a DECIDED decision must not still read as pending.

test_doc_drift.py already stops stable documents restating volatile numbers -
test counts, check tallies. It cannot catch the other kind of staleness, the one
an external review found on 2026-08-04: the README said the Rule 22 C++ decision
"is with the Director" while Decision 0012 had already fired, the C++ module was
compiled, and six engine phases had passed inside it. Numbers were guarded; a
sentence about the state of the world was not.

The rule these tests encode: **when a decision record exists, no stable document
may describe that decision as open.** Adding a decision file is what arms each
check, so a future Decision 0013 gets the same protection by existing.
"""
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DECISIONS = REPO / "docs" / "decisions"
# Documents that describe the project's state to a reader arriving cold.
STABLE_DOCS = ["README.md", "PROJECT_PLAN.md", "ROADMAP.md"]
# Phrasings that mean "nobody has decided this yet".
PENDING = re.compile(
    r"(is|remains|stays|sits)\s+(with the Director|open|undecided|pending|unresolved)"
    r"|awaiting (a )?(Director|decision)"
    r"|(decision|call) (is )?(still )?(to be made|outstanding|not yet made)",
    re.I)


def _decided(number: int) -> bool:
    return any(p.name.startswith("%04d-" % number) for p in DECISIONS.glob("*.md"))


def _text(name: str) -> str:
    p = REPO / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


def test_decisions_are_numbered_contiguously_from_one():
    """A gap means a record was lost, and a lost record is how 'already decided'
    turns back into 'still open' in somebody's summary."""
    nums = sorted(int(p.name[:4]) for p in DECISIONS.glob("[0-9][0-9][0-9][0-9]-*.md"))
    assert nums, "no decision records found"
    assert nums == list(range(1, len(nums) + 1)), \
        "decision numbers are not contiguous from 0001: %s" % nums


@pytest.mark.parametrize("doc", STABLE_DOCS)
def test_no_stable_doc_calls_the_cpp_decision_open(doc: str):
    """Decision 0012 fired 2026-08-03. Nothing may still say it is the Director's
    to make."""
    if not _decided(12):
        pytest.skip("Decision 0012 does not exist yet")
    text = _text(doc)
    for para in text.split("\n\n"):
        if re.search(r"Rule 22|C\+\+ (fight )?core|authoritative simulation", para, re.I) \
                and PENDING.search(para):
            raise AssertionError(
                "%s still describes the C++ core decision as open, but Decision 0012 "
                "exists:\n  %s" % (doc, " ".join(para.split())[:200]))


@pytest.mark.parametrize("doc", STABLE_DOCS)
def test_no_stable_doc_calls_the_phase0_gate_open(doc: str):
    """Decision 0007 recorded the Phase 0 gate rulings."""
    if not _decided(7):
        pytest.skip("Decision 0007 does not exist yet")
    text = _text(doc)
    for para in text.split("\n\n"):
        if re.search(r"Phase 0 (quality )?gate", para, re.I) and PENDING.search(para):
            raise AssertionError(
                "%s describes the Phase 0 gate as open, but Decision 0007 exists:\n  %s"
                % (doc, " ".join(para.split())[:200]))


# ---- the guard proven non-vacuous, per house rule ---------------------------

def test_the_pending_pattern_actually_matches_the_phrasing_that_slipped():
    """The exact sentence the review caught, and its neighbours."""
    assert PENDING.search("the Rule 22 C++ decision for the fight core is with the Director")
    assert PENDING.search("that call remains open")
    assert PENDING.search("awaiting a Director decision")
    assert PENDING.search("the decision is still to be made")


def test_the_pending_pattern_permits_settled_prose():
    assert not PENDING.search("the Rule 22 C++ trigger fired for the fight core")
    assert not PENDING.search("Decision 0012 records the C++ core as authoritative")
    assert not PENDING.search("Blueprints carry presentation, Python keeps tooling")
    # A decision doc may narrate the question it answered without re-opening it.
    assert not PENDING.search("the question was whether to move the core to C++")
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:05 UTC | END ]
