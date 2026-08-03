# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:40 UTC | START ]
"""Phase 1A step 8: condition, knockdowns and recovery.

Foundation pattern: the canonical document passes every check, and every checker
proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import condition as cd

CANON = cd.load()


def _mut():
    return copy.deepcopy(CANON)


def _r(doc, region):
    for d in doc["damage_regions"]:
        if d["region"] == region:
            return d
    raise KeyError(region)


def test_canonical_model_passes_every_check():
    assert cd.run_all(CANON) == []


def test_all_eight_strikeable_regions_have_condition_tracks():
    tracked = {d["region"] for d in CANON["damage_regions"]}
    for r in cd.PHYSICAL_REGIONS:
        assert r in tracked


def test_generic_health_pool_is_rejected():
    d = _mut()
    d["no_generic_health_pool"] = False
    assert any("per region" in e for e in cd.check_regions(d))


def test_a_round_may_not_erase_accumulated_damage():
    d = _mut()
    _r(d, "head")["recovers_between_rounds"] = 1.0
    assert any("erases the accumulation" in e for e in cd.check_regions(d))


def test_damage_to_a_region_must_impair_something():
    d = _mut()
    _r(d, "torso_upper")["impairs"] = []
    assert any("cosmetic" in e for e in cd.check_regions(d))


def test_jaw_must_be_knockdown_relevant():
    d = _mut()
    _r(d, "jaw_chin")["knockdown_relevant"] = False
    assert any("knockdown-relevant" in e for e in cd.check_regions(d))


def test_working_may_not_outpace_resting():
    """Inverting this inverts the entire stamina economy - a fighter would be
    better off throwing than breathing."""
    d = _mut()
    d["stamina"]["regen_per_tick_moving"] = 0.5
    assert any("non-increasing" in e for e in cd.check_stamina(d))


def test_throwing_regenerates_nothing():
    d = _mut()
    d["stamina"]["regen_per_tick_throwing"] = 0.01
    assert any("regenerate nothing" in e for e in cd.check_stamina(d))


def test_between_rounds_may_not_fully_restore_stamina():
    d = _mut()
    d["stamina"]["between_rounds_recovery_fraction"] = 1.0
    assert any("pacing as a strategy" in e for e in cd.check_stamina(d))


def test_no_flat_knockout_roll():
    d = _mut()
    d["knockdown"]["flat_random_roll_per_punch"] = True
    assert any("flat random knockout" in e for e in cd.check_knockdown(d))


def test_knockdowns_must_read_accumulated_condition():
    """A knockdown decided without accumulated condition is a dice roll with a
    longer name - the exact failure Rule 14 names."""
    d = _mut()
    d["knockdown"]["inputs"] = [i for i in d["knockdown"]["inputs"]
                                if i != "accumulated_condition"]
    assert any("accumulated_condition" in e for e in cd.check_knockdown(d))


def test_count_clock_is_one_number_per_authoritative_second():
    d = _mut()
    d["knockdown"]["count_ticks_per_number"] = 30
    assert any("one number per authoritative second" in e for e in cd.check_knockdown(d))


def test_chin_may_never_confer_immunity():
    d = _mut()
    d["chin"]["max_resistance_confers_immunity"] = True
    assert any("never absolute immunity" in e for e in cd.check_chin(d))


def test_early_stoppage_stays_possible_at_maximum_chin():
    d = _mut()
    d["chin"]["early_stoppage_possible_at_max"] = False
    assert any("immunity by another route" in e for e in cd.check_chin(d))


def test_between_rounds_break_is_thirty_authoritative_seconds():
    d = _mut()
    d["recovery"]["between_rounds_break_ticks"] = 900
    assert any("thirty real seconds" in e for e in cd.check_recovery(d))


def test_a_stoppage_may_not_read_the_scorecards():
    d = _mut()
    d["stoppage_conditions"].append({
        "id": "behind_on_cards",
        "trigger": "the fighter is far behind on the official scorecards",
        "authority": "corner"})
    assert any("unreadable to officiating" in e for e in cd.check_stoppages(d))


def test_the_referee_owns_at_least_one_stoppage():
    d = _mut()
    for s in d["stoppage_conditions"]:
        s["authority"] = "corner"
    assert any("owned by the referee" in e for e in cd.check_stoppages(d))


def test_required_prohibitions_and_invariants_are_declared():
    d = _mut()
    d["prohibitions"] = ["nothing relevant"]
    assert cd.check_prohibitions(d)
    d = _mut()
    d["invariants"] = [i for i in d["invariants"] if i["id"] != "chin_is_not_immunity"]
    assert cd.check_invariants(d)


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 10:52 UTC | START ]
# Appended below the original author's END tag, which is theirs and untouched.
def test_a_declared_impairs_target_may_not_sit_in_a_silent_third_state():
    """Every impairs target is expressed or named as unexpressed - the torso
    spent a whole step in the unnamed middle, accumulating numbers that changed
    no outcome, and two canon win conditions name bodywork."""
    d = _mut()
    d["impairment"]["not_yet_expressed"] = []
    assert any("silent third state" in e for e in cd.check_impairment(d))


def test_stamina_impairment_must_be_expressed():
    d = _mut()
    d["impairment"]["expressed"] = ["guard_integrity"]
    assert any("decorative" in e for e in cd.check_impairment(d))


def test_guard_integrity_impairment_must_be_expressed():
    d = _mut()
    d["impairment"]["expressed"] = ["stamina"]
    d["impairment"]["not_yet_expressed"].append("guard_integrity")
    assert any("unlimited force" in e for e in cd.check_impairment(d))


def test_missing_impairment_block_is_refused():
    d = _mut()
    del d["impairment"]
    assert any("cosmetic" in e for e in cd.check_impairment(d))
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 10:52 UTC | END ]
