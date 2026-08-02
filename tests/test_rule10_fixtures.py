# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""Phase 0 gate item: legal and illegal fighter-build fixtures (PROJECT_RULES.md Rule 10)."""
import json
from pathlib import Path
import pytest
from tools.uppercut_validate import attributes, schema_check

REPO = Path(__file__).resolve().parents[1]
LEGAL = sorted((REPO / "fixtures/fighters/legal").glob("*.json"))
ILLEGAL = sorted((REPO / "fixtures/fighters/illegal").glob("*.json"))

RULE_FOR_FIXTURE = {
    "illegal_two_at_plus_100": "R10.pos.one_max",
    "illegal_three_over_70": "R10.pos.two_over_70",
    "illegal_two_at_minus_100": "R10.neg.one_max",
    "illegal_three_related_under_30": "R10.neg.two_related_under_30",
    "illegal_four_under_40": "R10.neg.three_under_40",
    "illegal_all_physical_negative": "R10.neg.family_all_negative",
    "illegal_all_technical_negative": "R10.neg.family_all_negative",
    "illegal_uncompensated_severe": "R10.compensation",
    "illegal_insufficient_compensation": "R10.compensation",
    "illegal_shared_compensation": "R10.compensation.exclusive",
    "illegal_missing_severe_consequence": "R10.severe_consequence",
    "illegal_unknown_attribute": "R10.families",
    "illegal_overall_rating": "R10.no_overall",
}


@pytest.mark.parametrize("path", LEGAL, ids=lambda p: p.stem)
def test_legal_fixture_passes(path):
    data = json.loads(path.read_text())
    assert schema_check.validate(data, "fighter.schema.json") == []
    rep = attributes.validate_fighter(data)
    assert rep.legal, [str(v) for v in rep.violations]


@pytest.mark.parametrize("path", ILLEGAL, ids=lambda p: p.stem)
def test_illegal_fixture_rejected_for_the_right_reason(path):
    data = json.loads(path.read_text())
    rep = attributes.validate_fighter(data)
    assert not rep.legal, "illegal fixture was accepted"
    expected = RULE_FOR_FIXTURE[path.stem]
    assert any(v.rule.startswith(expected) for v in rep.violations), \
        f"expected {expected}, got {[v.rule for v in rep.violations]}"


def test_every_illegal_fixture_is_mapped():
    assert {p.stem for p in ILLEGAL} == set(RULE_FOR_FIXTURE), "unmapped illegal fixture"


def test_boundaries_are_inclusive_exclusive_as_written():
    """-30 is not 'below -30'; -40 is not 'below -40'; +70 is not 'exceeding +70'."""
    f = {"id": "b", "attributes": {"power": 70, "accuracy": 70, "hand_speed": -30,
                                   "foot_speed": -40, "composure": 0}, "compensations": []}
    assert attributes.validate_fighter(f).legal


def test_compensation_binding_is_configurable():
    shared = attributes.Interpretation(compensation_binding="shared")
    data = json.loads((REPO / "fixtures/fighters/illegal/illegal_shared_compensation.json").read_text())
    assert not attributes.validate_fighter(data).legal
    assert attributes.validate_fighter(data, interp=shared).legal, \
        "under the 'shared' reading this build is legal; OQ-1 is a real Director choice"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
