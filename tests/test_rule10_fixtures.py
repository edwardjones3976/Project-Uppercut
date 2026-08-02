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
    "illegal_over_budget_cap": "R10.budget_cap",
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


def test_budget_cap_applies_only_to_complete_declarations():
    """A partial sandbox fixture is an instrument, not a fighter; cost scales with how many
    attributes are declared, so one absolute cap cannot span both cases (Decision 0007)."""
    from tools.uppercut_validate import budget
    complete = json.loads((REPO / "fixtures/fighters/legal/reference_complete_shape.json").read_text())
    ev = budget.evaluate(complete["attributes"])
    assert ev["complete_declaration"] and ev["cap_enforced"] and not ev["over_cap"]
    partial = json.loads((REPO / "fixtures/fighters/legal/legal_extremes.json").read_text())
    ev2 = budget.evaluate(partial["attributes"])
    assert not ev2["complete_declaration"] and not ev2["cap_enforced"]


def test_refund_rate_makes_polarised_builds_cost_more_than_moderate_ones():
    """The measurement that drove Decision 0007: at full refund the ordering inverted, which is
    the unrestricted upward stacking Rule 10 forbids."""
    from tools.uppercut_validate import budget
    load_a = lambda n: json.loads((REPO / f"fixtures/fighters/legal/{n}.json").read_text())["attributes"]
    broad, moderate, polarised = (load_a("legal_baseline"), load_a("legal_boundaries"),
                                  load_a("legal_extremes"))
    net = lambda a, r: budget.profile(a, refund_rate=r)["C_tiered_marginal"]["net"]
    assert net(polarised, 1.0) < net(moderate, 1.0), "the loophole this ruling closes"
    assert net(broad, 0.5) < net(moderate, 0.5) < net(polarised, 0.5), "ordering restored at 0.5"


def test_canonical_budget_config_is_internally_consistent():
    from tools.uppercut_validate import budget
    cfg = budget.load_config()
    assert cfg["curve"] in budget.CURVES
    assert 0.0 < cfg["refund_rate"] <= 1.0
    assert cfg["tuning_status"] == "hypothesis", "Rule 18: the cap rests on one modelled build"


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
