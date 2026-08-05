# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 04:40 UTC | START ]
"""The research evidence gate, proven by breaking it.

A gate nobody has watched fail is a comment. Each test below feeds the gate a
record that is wrong in one specific way and asserts it is caught - because the
failure this whole pipeline exists to prevent is silent: a scraped paragraph
becoming a gameplay formula, with a citation attached that nobody re-read.

The committed collection is also checked as it stands, so a bad record cannot be
added quietly.
"""
import copy
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.research import gate  # noqa: E402

GOOD = {
    "id": "sample-source-2020",
    "title": "A source",
    "authors": ["Someone"],
    "year": 2020,
    "doi": "10.0000/example",
    "source_url": "https://openalex.org/W1",
    "accessed_at": "2026-08-06T00:00:00Z",
    "document_type": "article",
    "peer_review_status": "likely",
    "tier": 2,
    "research_lane": ["punch_biomechanics"],
    "canon_status": "reviewed",
    "confidence": "moderate",
    "methodology": "force plate",
    "main_findings": ["something measurable"],
}


def _one(**over):
    rec = copy.deepcopy(GOOD)
    rec.update(over)
    return rec


def test_a_clean_record_passes():
    assert gate.check(_one()) == []


def test_the_committed_collection_passes_its_own_gate():
    assert gate.check_all() == []


def test_tier_three_can_never_reach_canon():
    """Inspiration may start a hypothesis and may never end one.

    Without this, the cheapest source in the pile - a coaching blog, a
    retrospective, a forum post - is also the easiest to cite, and the game's
    physics ends up sourced from whatever was most readable.
    """
    errs = gate.check(_one(tier=3, canon_status="accepted",
                           accepted_by_decision="0014-movement-costs-displacement.md"))
    assert any("tier 3" in e for e in errs)


def test_accepting_evidence_requires_a_decision_record_that_exists():
    assert any("accepted_by_decision" in e
               for e in gate.check(_one(canon_status="accepted")))
    assert any("not in docs" in e
               for e in gate.check(_one(canon_status="accepted",
                                        accepted_by_decision="9999-imaginary.md")))
    # and the real thing passes, so the rule is a gate and not a wall
    assert gate.check(_one(
        canon_status="accepted",
        peer_review_status="verified",
        accepted_by_decision="0014-movement-costs-displacement.md")) == []


def test_high_confidence_requires_verified_peer_review():
    """A claim about the evidence, not about the reader's enthusiasm."""
    assert any("confidence 'high'" in e
               for e in gate.check(_one(confidence="high",
                                        peer_review_status="likely")))


def test_a_record_may_not_grow_into_a_copy_of_its_source():
    long_quote = " ".join(["word"] * (gate.QUOTE_WORD_CAP + 1))
    errs = gate.check(_one(quoted_evidence=[{"quote": long_quote,
                                             "locator": "p. 1"}]))
    assert any("the cap is" in e for e in errs)


def test_findings_without_a_method_are_refused():
    """Two findings that disagree cannot be weighed if one has no method."""
    rec = _one()
    del rec["methodology"]
    assert any("no methodology" in e for e in gate.check(rec))


def test_a_source_with_no_doi_must_say_why():
    """Commission rules and engine docs have no DOI. That is a fact to state,
    not a gap to leave: an unfindable source and an unpublished one look
    identical once the tab is closed."""
    rec = _one()
    del rec["doi"]
    assert any("no_doi_reason" in e for e in gate.check(rec))
    rec["no_doi_reason"] = "published by an athletic commission, no DOI issued"
    assert gate.check(rec) == []


def test_a_rejection_must_carry_its_reason():
    assert any("say why" in e
               for e in gate.check(_one(canon_status="rejected")))


def test_a_retracted_source_cannot_be_accepted():
    errs = gate.check(_one(canon_status="accepted",
                           peer_review_status="verified",
                           accepted_by_decision="0014-movement-costs-displacement.md",
                           retraction_or_correction_status="RETRACTED per OpenAlex"))
    assert any("retracted" in e for e in errs)


def test_the_ordinary_no_retraction_note_is_not_read_as_a_retraction():
    """The harvester writes 'no retraction ... recorded', which contains the
    word. A substring check would have failed every clean record in the pile,
    and it did in the first draft of this gate."""
    assert gate.check(_one(
        canon_status="accepted",
        peer_review_status="verified",
        accepted_by_decision="0014-movement-costs-displacement.md",
        retraction_or_correction_status="no retraction or correction recorded "
                                        "in OpenAlex at accessed_at")) == []


@pytest.mark.parametrize("lane", gate.LANES)
def test_every_declared_lane_is_accepted_by_the_gate(lane):
    assert gate.check(_one(research_lane=[lane])) == []


def test_an_invented_lane_is_not():
    assert any("unknown research lane" in e
               for e in gate.check(_one(research_lane=["vibes"])))


def test_nothing_in_the_collection_claims_canon_yet():
    """The honest state of the project, asserted so it cannot drift quietly.

    Update this the day a decision record accepts a source - and the assertion
    below will tell you to, rather than letting 'accepted' appear unnoticed.
    """
    accepted = [r for r in gate.load_all() if r.get("canon_status") == "accepted"]
    assert accepted == [], (
        "a source is marked accepted; if that is real, this test should be "
        "updated in the same commit as the decision record that accepted it")
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 04:40 UTC | END ]
