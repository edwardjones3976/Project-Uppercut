# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:20 UTC | START ]
"""Phase 1A step 11: Crowd Bar architecture.

Foundation pattern: the canonical document passes every check, and every checker
proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import crowd

CANON = crowd.load()


def _mut():
    return copy.deepcopy(CANON)


def test_canonical_model_passes_every_check():
    assert crowd.run_all(CANON) == []


def test_the_crowd_may_not_read_or_touch_the_cards():
    for key in ("reads_official_scores", "alters_official_scores", "alters_judging_criteria"):
        d = _mut()
        d["authority"][key] = True
        assert crowd.check_authority(d), key


def test_no_hidden_generic_multiplier():
    d = _mut()
    d["authority"]["grants_generic_multipliers"] = True
    assert any("rubber band" in e for e in crowd.check_authority(d))


def test_the_crowd_may_not_override_contact_truth():
    d = _mut()
    d["authority"]["alters_contact_truth"] = True
    assert any("whether a punch landed" in e for e in crowd.check_authority(d))


def test_an_insufficient_behaviour_may_not_become_a_gain_source():
    d = _mut()
    d["gain_sources"].append({"id": "raw_activity", "base_gain": 3.0,
                              "requires_risk": False, "novelty_gated": False})
    assert any("declared insufficient" in e for e in crowd.check_gain_sources(d))


def test_the_mechanism_may_not_invent_rewardable_behaviour():
    d = _mut()
    d["gain_sources"].append({"id": "crowd_pleasing_haircut", "base_gain": 1.0,
                              "requires_risk": False, "novelty_gated": False})
    assert any("may not invent" in e for e in crowd.check_gain_sources(d))


def test_every_contract_rewardable_behaviour_actually_pays():
    d = _mut()
    d["gain_sources"] = [g for g in d["gain_sources"] if g["id"] != "counters"]
    assert any("pays nothing for it" in e for e in crowd.check_gain_sources(d))


def test_farming_an_unopposed_target_must_earn_nothing():
    d = _mut()
    d["risk_gate"]["zero_gain_when_unopposed"] = False
    assert any("most tempting exploit" in e for e in crowd.check_risk_gate(d))


def test_the_best_paying_sources_must_require_risk():
    """If a safe action pays top rate, the risk gate is decorative."""
    d = _mut()
    for g in d["gain_sources"]:
        if g["id"] == "variety":
            g["base_gain"] = 99.0
            g["requires_risk"] = False
    assert any("pay top rates" in e for e in crowd.check_risk_gate(d))


def test_repetition_must_decay_but_never_to_zero():
    """Rule 4 protects legitimate repetition. A meter that zeroes a repeated
    action has prohibited it rather than de-emphasised it."""
    d = _mut()
    d["novelty"]["floor_multiplier"] = 0.0
    errs = crowd.check_novelty(d)
    assert any("strictly above zero" in e for e in errs)


def test_novelty_decay_must_actually_happen():
    d = _mut()
    d["novelty"]["floor_multiplier"] = 0.9
    d["novelty"]["repeat_multiplier"] = 0.55
    assert any("never actually happens" in e for e in crowd.check_novelty(d))


def test_a_full_bar_is_exclusive():
    d = _mut()
    d["full_bar"]["exclusive"] = False
    assert any("never activate both" in e for e in crowd.check_full_bar(d))


def test_the_full_bar_choice_matches_the_contract():
    d = _mut()
    d["full_bar"]["choice"] = ["ultimate", "ultimate"]
    assert crowd.check_full_bar(d)


def test_a_bar_that_never_decays_is_rejected():
    d = _mut()
    d["bar"]["decay_per_tick_idle"] = 0.0
    assert any("bank early and coast" in e for e in crowd.check_bar(d))


def test_required_prohibitions_and_invariants_are_declared():
    d = _mut()
    d["prohibitions"] = ["nothing relevant"]
    assert crowd.check_prohibitions(d)
    d = _mut()
    d["invariants"] = [i for i in d["invariants"] if i["id"] != "full_bar_is_exclusive"]
    assert crowd.check_invariants(d)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:20 UTC | END ]
