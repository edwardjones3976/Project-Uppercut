# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:52 UTC | START ]
"""Phase 1A step 6: what throwing a punch costs.

Foundation pattern: the canonical document passes every check, and every checker
proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import punches as pu

CANON = pu.load()


def _mut():
    return copy.deepcopy(CANON)


def _row(doc, cls):
    for r in doc["outcome_recovery"]["rows"]:
        if r["class"] == cls:
            return r
    raise KeyError(cls)


def test_canonical_model_passes_every_check():
    assert pu.run_all(CANON) == []


def test_commitment_admits_no_thrower_cancel():
    d = _mut()
    d["commitment"]["thrower_cancelable_phases"] = ["recovery"]
    assert any("cancelable" in e for e in pu.check_commitment(d))


def test_only_being_struck_may_interrupt():
    d = _mut()
    d["commitment"]["recovery_interruptible_by"] = ["being_struck", "player_input"]
    assert any("only being struck" in e for e in pu.check_commitment(d))


def test_landing_is_never_punished_for_landing():
    d = _mut()
    _row(d, "clean")["recovery_multiplier"] = 1.2
    assert any("punished for landing" in e for e in pu.check_outcome_recovery(d))


def test_whiff_must_cost_more_than_a_dodge():
    d = _mut()
    _row(d, "whiffed")["recovery_multiplier"] = _row(d, "dodged")["recovery_multiplier"]
    assert any("strictly more recovery" in e for e in pu.check_outcome_recovery(d))


def test_dodge_must_open_a_larger_window_than_a_block():
    d = _mut()
    _row(d, "dodged")["counter_window_ticks"] = _row(d, "blocked")["counter_window_ticks"]
    assert any("strictly larger counter window" in e for e in pu.check_outcome_recovery(d))


def test_every_contact_class_has_a_recovery_row():
    d = _mut()
    d["outcome_recovery"]["rows"] = [r for r in d["outcome_recovery"]["rows"]
                                     if r["class"] != "brushed"]
    assert any("no recovery row" in e for e in pu.check_outcome_recovery(d))


def test_out_of_range_punches_may_not_be_rescued():
    d = _mut()
    d["range_gate"]["auto_advance_on_throw"] = True
    assert any("invisible lunge" in e for e in pu.check_gates(d))


def test_a_tired_fighter_still_throws():
    d = _mut()
    d["stamina_gate"]["input_ever_ignored"] = True
    assert any("never ignored" in e for e in pu.check_gates(d))


def test_repetition_may_not_fire_on_bookkeeping():
    """Rule 4's whole point: the penalty is boxing, not a counter."""
    d = _mut()
    d["repetition_economy"]["mechanisms"][0]["fires_on"] = "the repeat count reaching 3"
    assert any("bookkeeping" in e for e in pu.check_repetition_economy(d))


def test_repetition_must_cost_the_thrower_something():
    d = _mut()
    for m in d["repetition_economy"]["mechanisms"]:
        m["target"] = "defender"
    assert any("repetition would be free" in e for e in pu.check_repetition_economy(d))


def test_repetition_must_give_the_defender_an_answer():
    """Fatigue alone is punishment without counterplay - the spammer gets tired
    but the opponent never gets a better chance to make them pay."""
    d = _mut()
    for m in d["repetition_economy"]["mechanisms"]:
        m["target"] = "thrower"
    assert any("punishment without counterplay" in e
               for e in pu.check_repetition_economy(d))


def test_unanswered_repetition_stays_legitimate():
    d = _mut()
    d["repetition_economy"]["legitimate_repetition"] = "   "
    assert any("stays legitimate" in e for e in pu.check_repetition_economy(d))


def test_chaining_may_not_smuggle_in_a_free_cancel():
    d = _mut()
    d["chaining"]["free_cancel_permitted"] = True
    assert any("back door" in e for e in pu.check_chaining(d))


def test_links_may_not_begin_during_active_contact():
    d = _mut()
    d["chaining"]["link_earliest_recovery_fraction"] = 0.0
    assert pu.check_chaining(d)


def test_same_hand_repeat_costs_at_least_as_much_as_the_other_hand():
    d = _mut()
    d["chaining"]["same_hand_link_startup_multiplier"] = 0.9
    assert any("retract first" in e for e in pu.check_chaining(d))


def test_power_hand_repeat_costs_at_least_a_normal_repeat():
    d = _mut()
    d["chaining"]["power_repeat_same_hand_startup_multiplier"] = 1.0
    d["chaining"]["same_hand_link_startup_multiplier"] = 1.4
    assert any("weight has to come back" in e for e in pu.check_chaining(d))


def test_move_table_range_bands_must_exist_in_the_movement_model():
    """Rule 22 cross-file lock, proven by mutating the checker's view of bands."""
    real = pu._bands
    try:
        pu._bands = lambda: {"nowhere"}
        assert any("movement model does not define" in e
                   for e in pu.check_move_table_agreement(CANON))
    finally:
        pu._bands = real


def test_a_free_punch_is_rejected():
    real = pu._moves
    try:
        pu._moves = lambda: [{"id": "ghost_jab", "category": "jab", "range_band": "mid",
                              "startup_frames": 4, "active_frames": 2, "recovery_frames": 8,
                              "stamina_cost": 0.0}]
        assert any("spam engine" in e for e in pu.check_move_table_agreement(CANON))
    finally:
        pu._moves = real


def test_required_prohibitions_and_invariants_are_declared():
    d = _mut()
    d["prohibitions"] = ["something unrelated"]
    assert pu.check_prohibitions(d)
    d = _mut()
    d["invariants"] = [i for i in d["invariants"] if i["id"] != "repetition_is_observable"]
    assert pu.check_invariants(d)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:52 UTC | END ]
