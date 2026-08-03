# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:26 UTC | START ]
"""Phase 1A step 12: Special / Ultimate / Full-Crowd Trait architecture.

Foundation pattern: the canonical document passes every check, and every checker
proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import ability

CANON = ability.load()


def _mut():
    return copy.deepcopy(CANON)


def _c(doc, cid):
    for c in doc["ability_classes"]:
        if c["id"] == cid:
            return c
    raise KeyError(cid)


def test_canonical_model_passes_every_check():
    assert ability.run_all(CANON) == []


def test_no_ability_may_be_unblockable_by_design():
    d = _mut()
    _c(d, "ultimate")["counterable"] = False
    assert any("unblockable by design" in e for e in ability.check_classes(d))


def test_no_ability_grants_invulnerability():
    """The temptation in every ability system: make the big move feel big by
    removing the answer."""
    d = _mut()
    _c(d, "ultimate")["grants_invulnerability"] = True
    assert any("removes the answer" in e for e in ability.check_classes(d))


def test_no_ability_bypasses_commitment():
    d = _mut()
    _c(d, "special")["bypasses_commitment"] = True
    assert any("bypasses commitment" in e for e in ability.check_classes(d))


def test_exactly_two_specials():
    d = _mut()
    _c(d, "special")["per_fighter"] = 1
    assert any("each fighter has 2 'special'" in e for e in ability.check_classes(d))


def test_full_bar_abilities_cost_the_whole_bar():
    d = _mut()
    _c(d, "ultimate")["cost_fraction"] = 0.5
    assert any("entire Crowd Bar" in e for e in ability.check_classes(d))


def test_a_special_costs_less_than_a_full_bar_ability():
    d = _mut()
    _c(d, "special")["cost_fraction"] = 1.0
    assert any("strictly less" in e for e in ability.check_classes(d))


def test_abilities_must_answer_the_same_nine_questions():
    d = _mut()
    d["counterplay_requirements"]["must_define"] = [
        p for p in d["counterplay_requirements"]["must_define"] if p != "counter_vulnerability"]
    assert any("left the combat system" in e for e in ability.check_counterplay(d))


def test_an_ability_faster_than_a_jab_is_rejected():
    d = _mut()
    d["counterplay_requirements"]["min_startup_frames"] = 0
    assert any("coin flip" in e for e in ability.check_counterplay(d))


def test_missing_with_a_big_option_must_cost_something():
    d = _mut()
    d["counterplay_requirements"]["min_recovery_frames"] = 2
    assert any("costs something" in e for e in ability.check_counterplay(d))


def test_command_entry_bypasses_nothing():
    for key in ("bypasses_stun", "bypasses_recovery", "bypasses_range",
                "bypasses_resource_cost", "bypasses_startup", "bypasses_whiff_punishment"):
        d = _mut()
        d["activation"][key] = True
        assert any("way to ask, never a way to skip" in e
                   for e in ability.check_activation(d)), key


def test_activation_requires_explicit_confirmation():
    d = _mut()
    d["activation"]["requires_explicit_confirmation"] = False
    assert any("explicit confirmation" in e for e in ability.check_activation(d))


def test_one_bar_never_yields_both():
    d = _mut()
    d["exclusivity"]["both_from_one_bar"] = True
    assert any("never yield both" in e for e in ability.check_exclusivity(d))


def test_the_two_models_must_agree_about_the_full_bar():
    """Cross-file lock: the crowd model owns the bar, this file spends it."""
    d = _mut()
    d["exclusivity"]["full_bar_choice"] = ["ultimate", "ultimate"]
    assert ability.check_exclusivity(d)


def test_required_prohibitions_and_invariants_are_declared():
    d = _mut()
    d["prohibitions"] = ["nothing relevant"]
    assert ability.check_prohibitions(d)
    d = _mut()
    d["invariants"] = [i for i in d["invariants"] if i["id"] != "every_ability_is_counterable"]
    assert ability.check_invariants(d)


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 10:52 UTC | START ]
# Appended below the original author's END tag, which is theirs and untouched.
def test_the_bar_may_never_buy_safety():
    d = _mut()
    d["reference_instruments"]["instrument_ultimate"]["recovery_multiplier"] = 0.8
    assert any("buying" in e for e in ability.check_reference_instruments(d))


def test_a_full_bar_that_does_nothing_is_refused():
    """The showman's canon win condition is 'converting a full Crowd Bar'; a
    sweep ran with the bar inert and the style won 5 of 40. Both failure
    directions - a bar that buys nothing and a bar that buys safety - are
    refused, not just the flashy one."""
    d = _mut()
    d["reference_instruments"]["instrument_ultimate"]["impact_multiplier"] = 1.0
    assert any("inert" in e for e in ability.check_reference_instruments(d))
    d = _mut()
    del d["reference_instruments"]
    assert any("unreachable" in e for e in ability.check_reference_instruments(d))


def test_the_ultimate_pays_full_resource_cost():
    d = _mut()
    d["reference_instruments"]["instrument_ultimate"]["stamina_cost_multiplier"] = 0.5
    assert any("Rule 15" in e for e in ability.check_reference_instruments(d))
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 10:52 UTC | END ]
