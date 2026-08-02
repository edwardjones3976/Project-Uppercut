# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""Canonical data laws that can be checked without a simulation (Rules 8, 9, 11, 13, 14, 21)."""
import json
from pathlib import Path
import pytest
from tools.uppercut_validate import schema_check

REPO = Path(__file__).resolve().parents[1]


def load(p):
    return json.loads((REPO / p).read_text())


def test_contact_commitment_ordering():
    assert schema_check.check_contact_ordering(load("data/contact_classes.json")) == []


def test_condition_regions_complete():
    assert schema_check.check_condition_regions(load("data/condition_regions.json")) == []


def test_no_single_health_bar():
    keys = {r["key"] for r in load("data/condition_regions.json")["regions"]}
    assert "health" not in keys and len(keys) >= 15


@pytest.mark.parametrize("rounds,champ,expected", [
    (4, False, 1), (6, False, 1), (8, False, 2), (10, False, 2), (12, False, 3),
    (4, True, 3), (6, True, 3), (8, True, 3), (10, True, 3), (12, True, 3)])
def test_crew_size_law(rounds, champ, expected):
    ok = {"scheduled_rounds": rounds, "championship": champ, "commentator_count": expected}
    assert schema_check.check_crew_rule(ok) == []
    bad = dict(ok, commentator_count=(expected % 3) + 1)
    assert schema_check.check_crew_rule(bad) != []


@pytest.mark.parametrize("settings,valid", [
    ({"accelerated_clock": True, "round_length": {"display_seconds": 180, "real_seconds": 105},
      "break_seconds": 30, "break_skip": {"in_match_choice_only": True}}, True),
    ({"accelerated_clock": True, "round_length": {"display_seconds": 180, "real_seconds": 180},
      "break_seconds": 30, "break_skip": {"in_match_choice_only": True}}, False),
    ({"accelerated_clock": False, "round_length": {"display_seconds": 120, "real_seconds": 120},
      "break_seconds": 30, "break_skip": {"in_match_choice_only": True}}, True),
    ({"accelerated_clock": False, "round_length": {"display_seconds": 90, "real_seconds": 90},
      "break_seconds": 30, "break_skip": {"in_match_choice_only": True}}, False),
])
def test_clock_law(settings, valid):
    errors = schema_check.validate(settings, "clock_settings.schema.json")
    assert (errors == []) is valid, errors


def test_all_six_stress_profiles_present_and_instrument_only():
    files = sorted((REPO / "data/stress_profiles").glob("*.json"))
    profiles = [json.loads(f.read_text()) for f in files]
    assert {p["id"] for p in profiles} == {
        "rusher", "drainer", "technician", "counterpuncher", "showman", "power_threat"}
    for p in profiles:
        assert p["instrument_only"] is True, "Decision 0005: stress profiles are not roster classes"
        assert schema_check.validate(p, "style_stress_profile.schema.json") == []
        assert p["win_condition"] and p["risk_condition"] and p["counterplay"] and p["readable_signals"]
    gates = {p["gate_test"] for p in profiles}
    assert {"first_bell_firestorm", "long_drain"} <= gates


def test_judge_card_events_must_be_sealed_by_schema():
    bad = {"seq": 1, "tick": 1, "clock": {"round": 1, "display_ms": 0, "real_ms": 0},
           "type": "judge_round_card", "visibility": "observable"}
    assert schema_check.validate(bad, "fight_event.schema.json") != []
    good = dict(bad, visibility="sealed")
    assert schema_check.validate(good, "fight_event.schema.json") == []


def test_ultimate_cannot_be_declared_auto_win():
    ability = {"id": "x", "kind": "ultimate", "name": "X",
               "counterplay": ["slip the loading step"],
               "can_end_match_automatically": True,
               "commitment": {k: "n/a" for k in ["startup", "active_contact", "recovery", "range",
                                                 "stamina_cost", "guard_interaction",
                                                 "counter_vulnerability", "positional_consequence"]}}
    assert schema_check.validate(ability, "ability.schema.json") != []


def test_ability_requires_counterplay():
    ability = {"id": "x", "kind": "special", "name": "X", "counterplay": [],
               "commitment": {k: "n/a" for k in ["startup", "active_contact", "recovery", "range",
                                                 "stamina_cost", "guard_interaction",
                                                 "counter_vulnerability", "positional_consequence"]}}
    assert schema_check.validate(ability, "ability.schema.json") != []
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
