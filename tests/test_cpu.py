# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:51 UTC | START ]
"""Phase 1A step 9: CPU decision-making from observable evidence.

Foundation pattern: the canonical document passes every check, and every checker
proves non-vacuous by failing on a mutated copy.

The score-firewall tests matter most. The Phase 1A gate asks that CPU fighters use
no hidden score - an absence, which behaviour testing struggles to demonstrate.
These prove it as a set relation instead.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import cpu

CANON = cpu.load()


def _mut():
    return copy.deepcopy(CANON)


def test_canonical_model_passes_every_check():
    assert cpu.run_all(CANON) == []


def test_the_firewall_is_a_set_relation_not_a_habit():
    """Every sealed judge event named by the score-isolation contract is absent
    from what the CPU can see."""
    sealed = cpu._sealed()["sealed_symbols"]["event_types"]
    assert sealed
    for ev in sealed:
        assert ev not in CANON["observable_inputs"]


def test_a_sealed_judge_event_in_the_input_set_is_caught():
    d = _mut()
    d["observable_inputs"].append("judge_round_card")
    errs = cpu.check_observable_inputs(d)
    assert any("Rule 3 VIOLATION" in e for e in errs)


def test_every_observable_input_is_a_real_event_type():
    d = _mut()
    d["observable_inputs"].append("opponent_intent")
    assert any("not a fight_event type" in e for e in cpu.check_observable_inputs(d))


def test_the_firewall_cannot_be_satisfied_by_blindness():
    """An empty input set would pass every containment check and mean nothing."""
    d = _mut()
    d["observable_inputs"] = ["punch_thrown", "punch_outcome"]
    assert any("satisfied by blindness" in e for e in cpu.check_observable_inputs(d))


def test_opponent_input_reading_must_be_explicitly_forbidden():
    d = _mut()
    d["forbidden_inputs"] = [f for f in d["forbidden_inputs"]
                             if f["id"] != "opponent_input_buffer"]
    assert any("opponent_input_buffer" in e for e in cpu.check_forbidden_inputs(d))


def test_a_ban_without_a_rationale_is_rejected():
    d = _mut()
    d["forbidden_inputs"][0]["why"] = "no"
    assert any("without a rationale" in e for e in cpu.check_forbidden_inputs(d))


def test_the_cpu_may_never_be_certain():
    d = _mut()
    d["estimate_policy"]["max_confidence"] = 1.0
    assert any("stopped estimating" in e for e in cpu.check_estimate_policy(d))


def test_beliefs_must_cite_observed_events():
    d = _mut()
    d["estimate_policy"]["evidence_must_cite_observed_events"] = False
    assert any("cite the observable events" in e for e in cpu.check_estimate_policy(d))


def test_zero_tick_reaction_is_input_reading():
    d = _mut()
    d["reaction"]["floor_ticks"] = 0
    assert any("input reading by another name" in e for e in cpu.check_reaction(d))


def test_no_difficulty_may_dip_below_the_reaction_floor():
    d = _mut()
    d["difficulty_tiers"][-1]["reaction_ticks"] = 1
    assert any("below the floor" in e for e in cpu.check_reaction(d))


def test_the_cpu_may_not_cancel_its_own_commitment():
    d = _mut()
    d["reaction"]["may_cancel_own_commitment"] = True
    assert any("privilege commitment exists to deny" in e for e in cpu.check_reaction(d))


def test_difficulty_may_never_change_damage():
    d = _mut()
    d["difficulty_may_never_change"] = [x for x in d["difficulty_may_never_change"]
                                        if x != "damage_dealt"]
    assert any("hidden advantage" in e for e in cpu.check_difficulty(d))


def test_difficulty_lists_may_not_contradict():
    d = _mut()
    d["difficulty_may_change"].append("damage_dealt")
    assert any("contradict each other" in e for e in cpu.check_difficulty(d))


def test_difficulty_must_order_coherently():
    """A deeper-reading tier that reacts slower is not harder, just noisier."""
    d = _mut()
    d["difficulty_tiers"][-1]["reaction_ticks"] = 30
    assert any("order coherently" in e for e in cpu.check_difficulty(d))


def test_difficulty_may_not_be_inert():
    d = _mut()
    for t in d["difficulty_tiers"]:
        t["reaction_ticks"] = 10
    assert any("inert" in e for e in cpu.check_difficulty(d))


def test_required_prohibitions_and_invariants_are_declared():
    d = _mut()
    d["prohibitions"] = ["nothing relevant"]
    assert cpu.check_prohibitions(d)
    d = _mut()
    d["invariants"] = [i for i in d["invariants"] if i["id"] != "firewall_is_structural"]
    assert cpu.check_invariants(d)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:51 UTC | END ]
