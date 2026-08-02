# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:52 UTC | START ]
"""Contract tests for Rules 4, 5, 6, 12 and 16."""
import json
from pathlib import Path
import pytest
from tools.uppercut_validate import contracts, schema_check

REPO = Path(__file__).resolve().parents[1]


def load(p):
    return json.loads((REPO / p).read_text())


# ------------------------------------------------------------------ Rule 12 Crowd
def test_crowd_rewardable_list_matches_rule_12():
    c = load("data/crowd_contract.json")
    assert set(c["rewardable_behaviour"]) == {
        "clean_offense", "defense", "evasions", "counters", "reversals", "combinations",
        "variety", "ringcraft", "appropriate_showmanship", "high_risk_success",
        "momentum_changing_sequences"}
    assert c["full_bar"]["exclusive"] is True


def test_crowd_cannot_touch_scores_or_grant_hidden_multipliers():
    p = set(load("data/crowd_contract.json")["prohibitions"])
    for forbidden in ("read_official_scores", "change_judging_criteria",
                      "hidden_generic_damage_multiplier", "hidden_generic_comeback_multiplier",
                      "reward_low_risk_meter_farming", "override_stamina_truth"):
        assert forbidden in p


def test_low_risk_farming_is_rejected():
    farm = {"seq": 1, "fighter": "red", "delta": 5, "earned_by": "appropriate_showmanship",
            "observed_evidence": [0], "risk_taken": False}
    assert any("farming" in e for e in contracts.check_crowd_event(farm))
    earned = dict(farm, risk_taken=True)
    assert contracts.check_crowd_event(earned) == []


def test_crowd_event_schema_rejects_unrewardable_behaviour():
    bad = {"seq": 1, "fighter": "red", "delta": 3, "earned_by": "raw_activity",
           "observed_evidence": [0], "risk_taken": True}
    assert schema_check.validate(bad, "crowd_event.schema.json") != []


def test_full_bar_cannot_activate_both():
    assert contracts.check_full_crowd_spend({"ultimate": True, "full_crowd_trait": True})
    assert contracts.check_full_crowd_spend({"ultimate": True}) == []
    assert contracts.check_full_crowd_spend({"full_crowd_trait": True}) == []


# ------------------------------------------------------------------- Rule 5 modes
@pytest.mark.parametrize("mode", load("data/mode_configurations.json")["modes"], ids=lambda m: m["id"])
def test_declared_modes_configure_only_permitted_surfaces(mode):
    assert contracts.check_mode_configuration(mode) == []
    assert schema_check.validate({k: v for k, v in mode.items() if k != "notes"} | (
        {"notes": mode["notes"]} if "notes" in mode else {}), "mode_configuration.schema.json") == []


@pytest.mark.parametrize("surface", [
    "physics", "damage", "scoring", "move_availability", "rubber_banding",
    "hidden_beginner_damage_reduction", "restricted_advanced_mechanics",
    "named_experience_tier_system"])
def test_a_mode_may_never_configure_combat(surface):
    bad = {"id": "beginner_league", "phase": 3, "configures": [surface]}
    assert contracts.check_mode_configuration(bad), f"'{surface}' must be rejected"
    assert schema_check.validate(bad, "mode_configuration.schema.json") != []


def test_training_configures_instruction_not_rules():
    training = next(m for m in load("data/mode_configurations.json")["modes"] if m["id"] == "training")
    assert "instruction" in training["configures"]
    for banned in ("damage", "scoring", "physics", "move_availability"):
        assert banned not in training["configures"]


def test_training_module_requirements_match_rule_5():
    reqs = load("data/mode_configurations.json")["training_module_requirements"]
    assert len(reqs) == 9 and "allow_repetition_without_record_penalties" in reqs


# ------------------------------------------------------------------ Rule 6 advice
def test_advice_reliability_order():
    assert load("data/advice_contract.json")["reliability_order"] == ["corner", "commentary", "crowd"]


@pytest.mark.parametrize("award,ok", [
    ({"sources": ["corner"], "benefit_pct": 2.5}, True),
    ({"sources": ["corner"], "benefit_pct": 6.0}, False),
    ({"sources": ["corner", "commentary"], "benefit_pct": 2.0}, False),
    ({"sources": ["corner"], "benefit_pct": 2.0, "used_official_score": True}, False),
])
def test_advice_bounds(award, ok):
    assert (contracts.check_advice_award(award) == []) is ok


# ---------------------------------------------------------------- Rule 4 anti-spam
def test_targeted_abuse_list_matches_rule_4():
    assert set(load("data/anti_spam_contract.json")["targeted_abuse"]) == {
        "one_move_loops", "safe_animation_abuse", "stun_loops", "clinch_abuse",
        "excessive_running", "passive_blocking_abuse", "meter_farming"}


@pytest.mark.parametrize("mech,ok", [
    ("observable_pattern_recognition", True), ("stamina", True), ("counterplay", True),
    ("hidden_punishment", False), ("impossible_reaction_speed", False),
    ("privileged_inputs", False), ("official_score_knowledge", False)])
def test_spam_punishment_mechanism(mech, ok):
    assert (contracts.check_spam_ruling({"mechanism": mech, "applies_to": "both"}) == []) is ok


def test_spam_rules_apply_symmetrically():
    assert contracts.check_spam_ruling({"mechanism": "stamina", "applies_to": "cpu_only"})


# ------------------------------------------------------------------ Rule 16 referee
REFS = sorted((REPO / "data/referees").glob("*.json"))


def test_all_seven_officials_present():
    ids = {json.loads(f.read_text())["id"] for f in REFS}
    assert ids == {"raymond_whitaker", "celeste_navarro", "hana_mori", "darius_cole",
                   "nkiru_okafor", "thomas_baines", "elliot_ames"}


@pytest.mark.parametrize("path", REFS, ids=lambda p: p.stem)
def test_referee_profile_valid_and_bound(path):
    p = json.loads(path.read_text())
    assert schema_check.validate(p, "referee_profile.schema.json") == []
    assert contracts.check_referee_profile(p) == []


def test_comic_relief_official_is_non_ranked_but_still_bound():
    ames = json.loads((REPO / "data/referees/elliot_ames.json").read_text())
    assert ames["competitive"] is False and ames["ranked_eligible"] is False
    assert all(v is True for v in ames["universal_minimums"].values()), \
        "lax ordinary enforcement never relaxes medical, foul or knockdown-count minimums"


def test_six_serious_officials_are_ranked_eligible_and_distinct():
    serious = [json.loads(f.read_text()) for f in REFS if json.loads(f.read_text())["competitive"]]
    assert len(serious) == 6
    assert all(r["ranked_eligible"] and r["disclosed_before_match"] for r in serious)
    fingerprints = {tuple(sorted(r["enforcement"].items())) for r in serious}
    assert len(fingerprints) == 6, "each official must apply a meaningfully different philosophy"


def test_referee_decision_requires_observable_evidence_and_profile_clause():
    bad = {"seq": 5, "referee": "hana_mori", "decision": "deduction", "observed_evidence": [],
           "profile_clause": ""}
    assert schema_check.validate(bad, "referee_decision.schema.json") != []
    good = {"seq": 5, "referee": "hana_mori", "decision": "deduction", "against": "red",
            "observed_evidence": [3, 4], "profile_clause": "deduction_threshold=standard",
            "applies_equally_to_both": True,
            "forbidden_inputs_assertion": "no_official_score_no_privileged_state"}
    assert schema_check.validate(good, "referee_decision.schema.json") == []


# -------------------------------------------------------------- generic move table
def test_generic_move_table_is_complete_and_valid():
    doc = load("data/moves/generic_sandbox_moves.json")
    assert len(doc["moves"]) >= 15
    for m in doc["moves"]:
        assert schema_check.validate(m, "move.schema.json") == []
        assert m["tuning_status"] == "hypothesis", "Rule 18: prototype numbers are hypotheses"
        assert m["counter_vulnerability"] and m["positional_consequence"], \
            "Rule 22: counterplay exists from the first punch"


def test_move_table_covers_the_required_basics():
    cats = {m["category"] for m in load("data/moves/generic_sandbox_moves.json")["moves"]}
    assert {"jab", "cross", "hook", "uppercut", "body_shot", "guard", "evasion",
            "step", "pivot", "clinch"} <= cats


def test_no_move_is_unblockable_by_design():
    for m in load("data/moves/generic_sandbox_moves.json")["moves"]:
        assert m["guard_interaction"] != "unblockable_by_design_prohibited"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:52 UTC | END ]

# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:55 UTC | START — added after schema fix ]
def test_offensive_moves_must_name_a_target_but_movement_need_not():
    """An attack that hits nowhere is not an attack; a pivot that hits nowhere is a pivot."""
    base = {"id": "x", "startup_frames": 5, "active_frames": 2, "recovery_frames": 8,
            "range_band": "mid", "stamina_cost": 1.0, "guard_interaction": "blockable_high",
            "hit_reaction": "n/a", "counter_vulnerability": "n/a",
            "positional_consequence": "n/a", "target_regions": []}
    assert schema_check.validate(dict(base, category="jab"), "move.schema.json") != []
    assert schema_check.validate(dict(base, category="step"), "move.schema.json") == []
    assert schema_check.validate(dict(base, category="jab", target_regions=["head"]),
                                 "move.schema.json") == []
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:55 UTC | END — added after schema fix ]
