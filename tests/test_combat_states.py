# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | START ]
"""Phase 1A step 1: combat-state definition laws.

Foundation pattern: the canonical document passes every check, and every
checker proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import combat_states as cs

CANON = cs.load()


def _mut():
    return copy.deepcopy(CANON)


def _fa(doc):
    return doc["machines"]["fighter_action"]


def _t(doc, tid):
    for t in _fa(doc)["transitions"]:
        if t["id"] == tid:
            return t
    raise KeyError(tid)


def test_canonical_document_passes_every_check():
    for name, fn in cs.ALL_CHECKS:
        assert fn(CANON) == [], f"{name} failed on canonical data: {fn(CANON)}"


def test_run_all_clean_on_canon():
    assert cs.run_all() == []


def test_schema_check_not_vacuous():
    doc = _mut()
    del doc["tuning_status"]
    assert cs.check_schema(doc)


def test_reachability_not_vacuous():
    doc = _mut()
    _fa(doc)["states"].append({"id": "orphan_state", "description": "unreachable by construction"})
    assert cs.check_reachability(doc)


def test_liveness_not_vacuous():
    doc = _mut()
    fa = _fa(doc)
    fa["transitions"] = [t for t in fa["transitions"] if t["id"] != "clinch_break"]
    for t in fa["transitions"]:
        if t["from"] == "*":
            t.setdefault("wildcard_excludes", []).append("clinch")
    assert cs.check_liveness(doc)


def test_event_vocabulary_not_vacuous():
    doc = _mut()
    _t(doc, "struck")["emits"] = ["telepathy_burst"]
    assert cs.check_event_vocabulary(doc)


def test_score_isolation_blocks_forbidden_domains():
    doc = _mut()
    _t(doc, "commit_move")["guard_inputs"].append("official_scorecards")
    errs = cs.check_input_domains(doc)
    assert errs and any("Rule 3" in e for e in errs)


def test_score_isolation_blocks_undeclared_domains():
    doc = _mut()
    _t(doc, "commit_move")["guard_inputs"].append("psychic_link")
    assert cs.check_input_domains(doc)


def test_forbidden_list_must_name_scorecards():
    doc = _mut()
    doc["forbidden_input_domains"] = [d for d in doc["forbidden_input_domains"]
                                      if d != "official_scorecards"]
    assert cs.check_input_domains(doc)


def test_counterplay_not_vacuous():
    doc = _mut()
    for s in _fa(doc)["states"]:
        if s["id"] == "move_recovery":
            s["counter_open"] = False
    assert cs.check_counterplay(doc)


def test_recovery_scales_by_commitment_tier():
    doc = _mut()
    for s in _fa(doc)["states"]:
        if s["id"] == "move_recovery":
            s.pop("consequence_scaling", None)
    assert cs.check_counterplay(doc)


def test_condition_refs_not_vacuous():
    doc = _mut()
    for s in _fa(doc)["states"]:
        if s["id"] == "hit_stun":
            s["condition_refs"].append("left_shin")
    assert cs.check_condition_refs(doc)


def test_knockdown_requires_observable_evidence():
    doc = _mut()
    _t(doc, "dropped")["trigger_kind"] = "input_intent"
    assert cs.check_knockdown_flow(doc)


def test_knocked_down_exit_discipline():
    doc = _mut()
    _fa(doc)["transitions"].append(
        {"id": "pop_up", "from": "knocked_down", "to": "idle", "trigger_kind": "input_intent"})
    assert cs.check_knockdown_flow(doc)


def test_rise_governed_by_count_clock():
    doc = _mut()
    _t(doc, "rise_complete")["trigger_kind"] = "input_intent"
    assert cs.check_knockdown_flow(doc)


def test_referee_cannot_alter_combat_truth():
    doc = _mut()
    _t(doc, "referee_stoppage")["emits"] = ["stoppage", "condition_change"]
    assert cs.check_referee_bounds(doc)


def test_posture_zero_delay_not_vacuous():
    doc = _mut()
    doc["machines"]["posture_continuum"]["modes"][0]["transition_delay_frames"] = 5
    assert cs.check_posture(doc)
    assert cs.check_schema(doc)


def test_provisioned_discipline():
    doc = _mut()
    for s in _fa(doc)["states"]:
        if s["id"] == "special_execution":
            s["provisioned"] = False
    assert cs.check_provisioned(doc)


def test_provisioned_transitions_stay_provisioned():
    doc = _mut()
    _t(doc, "ultimate_commit")["trigger_kind"] = "input_intent"
    assert cs.check_provisioned(doc)


def test_crowd_architecture_slots_exist():
    doc = _mut()
    _fa(doc)["states"] = [s for s in _fa(doc)["states"] if s["id"] != "ultimate_execution"]
    assert cs.check_provisioned(doc)


def test_one_unified_machine_set():
    doc = _mut()
    doc["machines"]["beginner_action"] = {"initial": "idle", "states": [], "transitions": []}
    assert cs.check_machine_set(doc)


def test_required_invariants_declared():
    doc = _mut()
    doc["invariants"] = [i for i in doc["invariants"] if i["id"] != "tick_determinism"]
    assert cs.check_invariants(doc)
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | END ]
