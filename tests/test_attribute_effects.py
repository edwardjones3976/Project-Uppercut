# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 16:10 UTC | START ]
"""How attributes reach the fight, held to the laws the file claims.

Foundation pattern: the canonical document passes every check, and every checker proves
non-vacuous by failing on a mutated copy. The mutations are chosen from the failure
modes that actually threaten this file - an attribute declared and scaled by nothing, a
maximum that decides an outcome by itself, and a Chin that quietly becomes immunity.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import attribute_effects as ae

CANON = ae.load()


def _mut():
    return copy.deepcopy(CANON)


def _eff(doc, attr):
    for e in doc["effects"]:
        if e["attribute"] == attr:
            return e
    raise KeyError(attr)


def test_canonical_model_passes_every_check():
    assert ae.run_all(CANON) == []


def test_every_attribute_is_expressed_or_named():
    """The whole reason this file exists: twenty-four attributes were declared in
    Phase 0 and the bout read none of them."""
    declared = set(ae._families())
    scaled = {e["attribute"] for e in CANON["effects"]}
    named = set(CANON["unexpressed_attributes"]["not_yet_expressed"])
    assert declared == scaled | named
    assert not (scaled & named)


def test_a_zeroed_attribute_must_be_the_baseline():
    d = _mut()
    d["curve"]["centre_multiplier"] = 1.2
    assert any("multiply by exactly one" in e for e in ae.check_curve(d))


def test_an_attribute_scaled_by_nothing_is_caught():
    d = _mut()
    e = _eff(d, "power")
    e["multiplier_at_plus_100"] = e["multiplier_at_minus_100"]
    assert any("still decorative" in x for x in ae.check_effects(d))


def test_an_unnamed_unscaled_attribute_is_caught():
    """The silent third state - declared, no effect, not named as unexpressed."""
    d = _mut()
    d["unexpressed_attributes"]["not_yet_expressed"] = [
        a for a in d["unexpressed_attributes"]["not_yet_expressed"] if a != "composure"]
    assert any("silent third state" in x for x in ae.check_effects(d))


def test_claiming_an_expressed_attribute_is_unexpressed_is_caught():
    d = _mut()
    d["unexpressed_attributes"]["not_yet_expressed"].append("power")
    assert any("flattering direction" in x for x in ae.check_effects(d))


def test_a_direction_that_contradicts_its_band_is_caught():
    """higher_is_weaker means the multiplier FALLS as the attribute rises - fast hands
    shorten startup. Authoring it the other way is a sign error the data caught on its
    first run, when three of fourteen effects had rising bands."""
    d = _mut()
    e = _eff(d, "hand_speed")
    e["multiplier_at_minus_100"], e["multiplier_at_plus_100"] = (
        e["multiplier_at_plus_100"], e["multiplier_at_minus_100"])
    assert any("higher_is_weaker" in x for x in ae.check_effects(d))


def test_an_attribute_reaching_several_mechanics_is_caught():
    d = _mut()
    d["effects"].append(dict(_eff(d, "power"), scales="evasion_chance"))
    assert any("impossible to read off a single row" in x for x in ae.check_effects(d))


def test_a_maximum_that_decides_an_outcome_alone_is_caught():
    d = _mut()
    _eff(d, "power")["multiplier_at_plus_100"] = 3.0
    errs = ae.check_bounds(d)
    assert any("decide" in e or "dominate" in e for e in errs)


def test_a_minimum_that_makes_a_mechanic_impossible_is_caught():
    d = _mut()
    _eff(d, "evasion_chance" and "defensive_technique")["multiplier_at_minus_100"] = 0.05
    errs = ae.check_bounds(d)
    assert any("impossible" in e or "dominate" in e for e in errs)


def test_a_band_too_narrow_to_matter_is_caught():
    d = _mut()
    e = _eff(d, "accuracy")
    e["multiplier_at_minus_100"] = 0.99
    e["multiplier_at_plus_100"] = 1.01
    assert any("inert by another name" in x for x in ae.check_bounds(d))


def test_chin_may_not_become_immunity():
    """Rule 14 states it, condition_model asserts it about DATA, and this asserts it
    about ARITHMETIC - the two can drift apart, and a chin multiplier without a ceiling
    would make +100 Chin unfalsifiable whatever the other file promises."""
    d = _mut()
    _eff(d, "chin")["multiplier_at_plus_100"] = 5.0
    assert any("immunity" in e for e in ae.check_chin_is_not_immunity(d))


def test_chin_must_scale_knockdown_resistance():
    d = _mut()
    _eff(d, "chin")["scales"] = "stride_length"
    assert any("knockdown resistance" in e for e in ae.check_chin_is_not_immunity(d))


def test_required_prohibitions_and_invariants_are_declared():
    d = _mut()
    d["prohibitions"] = ["nothing relevant"]
    assert ae.check_prohibitions(d)
    d = _mut()
    d["invariants"] = [i for i in d["invariants"] if i["id"] != "no_attribute_is_inert"]
    assert ae.check_invariants(d)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 16:10 UTC | END ]
