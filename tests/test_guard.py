# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:36 UTC | START ]
"""Phase 1A step 7: guard and evasion.

Foundation pattern: the canonical document passes every check, and every checker
proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import guard as gd

CANON = gd.load()


def _mut():
    return copy.deepcopy(CANON)


def _p(doc, pid):
    for p in doc["postures"]:
        if p["id"] == pid:
            return p
    raise KeyError(pid)


def _e(doc, eid):
    for e in doc["evasions"]:
        if e["id"] == eid:
            return e
    raise KeyError(eid)


def test_canonical_model_passes_every_check():
    assert gd.run_all(CANON) == []


def test_all_ten_named_guards_are_authored():
    """Decision 0010 promised the posture set as step 7 content."""
    ids = {p["id"] for p in CANON["postures"]}
    assert len(ids) == 10
    for expected in ("high_guard", "peek_a_boo", "philly_shell", "cross_arm", "long_guard",
                     "low_lead", "tight_elbow", "ear_muff", "forearm_frame", "active_hands"):
        assert expected in ids


def test_this_file_may_not_resolve_contact():
    d = _mut()
    d["authority"]["resolves_contact"] = True
    assert any("sole authority" in e for e in gd.check_authority(d))


def test_pipeline_may_not_read_posture_identity():
    d = _mut()
    d["authority"]["posture_identity_read_by_pipeline"] = True
    assert any("geometry" in e for e in gd.check_authority(d))


def test_no_posture_may_cover_every_lane():
    d = _mut()
    _p(d, "high_guard")["extents"] = {"guard_high": 1.0, "guard_body": 1.0}
    assert any("sell one lane" in e for e in gd.check_postures(d))


def test_no_posture_may_cover_nothing():
    d = _mut()
    _p(d, "low_lead")["extents"] = {"guard_high": 0.42, "guard_body": 0.41}
    assert any("stance, not a guard" in e for e in gd.check_postures(d))


def test_a_survival_posture_must_be_priced():
    """Maximum coverage with no offense has to cost mobility, vision or stamina.
    A free one would never be worth leaving, which is Rule 4's whole concern."""
    d = _mut()
    p = _p(d, "ear_muff")
    p["mobility_multiplier"] = 1.0
    p["visibility"] = 1.0
    p["stamina_per_tick"] = 0.01
    assert any("pays nothing" in e for e in gd.check_postures(d))


def test_extents_must_sit_inside_the_collision_models_bounds():
    d = _mut()
    _p(d, "cross_arm")["extents"]["guard_high"] = 0.2
    assert any("modulation range" in e for e in gd.check_extent_agreement(d))


def test_extents_must_name_exactly_the_declared_volumes():
    d = _mut()
    _p(d, "high_guard")["extents"] = {"guard_high": 0.9, "guard_shoulder": 0.5}
    assert any("exactly the declared guard volumes" in e for e in gd.check_extent_agreement(d))


def test_reconciled_postures_must_use_the_collision_models_state_ids():
    """Drift here would silently break the conditional coverage that the guard
    doc's reconciliation log and Decision 0010 exist to hold in place."""
    d = _mut()
    _p(d, "cross_arm")["alignment_states"] = ["bar_up", "bar_down"]
    assert any("worked examples use" in e for e in gd.check_alignment_states(d))


def test_shell_alignment_states_match_the_overhand_resolution():
    got = set(_p(CANON, "philly_shell")["alignment_states"])
    assert got == {"roll_timed_aligned", "roll_late_or_misaligned"}


def test_evasion_must_outrank_guard():
    d = _mut()
    d["evasion_economy"]["outranks_guard"] = False
    assert any("outrank passive covering" in e for e in gd.check_evasion_economy(d))


def test_a_mistimed_evasion_must_cost_something():
    d = _mut()
    d["evasion_economy"]["mistime_penalty_ticks"] = 0
    assert any("must cost something" in e for e in gd.check_evasion_economy(d))


def test_the_outranks_claim_is_checked_against_the_punch_model():
    """The claim is only worth making if the file that pays out agrees."""
    real = gd.REPO
    rows = {r["class"]: r for r in
            __import__("json").loads((real / "data" / "punch_model.json").read_text())
            ["outcome_recovery"]["rows"]}
    assert rows["dodged"]["counter_window_ticks"] > rows["blocked"]["counter_window_ticks"]


def test_active_window_evasions_are_frame_locked_to_the_move_table():
    d = _mut()
    _e(d, "slip_lead")["active_ticks"] = 99
    assert any("move table authors" in e for e in gd.check_evasion_moves(d))


def test_a_positional_answer_may_not_claim_to_vacate_a_lane():
    d = _mut()
    _e(d, "step_out")["vacates"] = ["head"]
    assert any("removes the fighter from reach" in e for e in gd.check_evasion_moves(d))


def test_every_evasion_must_have_an_answer():
    d = _mut()
    _e(d, "roll_under")["beaten_by"] = []
    assert any("every defence must have one" in e for e in gd.check_evasion_moves(d))


def test_evasions_must_map_to_real_moves():
    d = _mut()
    _e(d, "slip_lead")["move_id"] = "matrix_dodge"
    assert any("absent from the table" in e for e in gd.check_evasion_moves(d))


def test_repetition_alone_may_not_break_a_guard():
    d = _mut()
    d["guard_integrity"]["degrades_from_repetition_alone"] = True
    assert any("spam does not earn a guard break" in e for e in gd.check_guard_integrity(d))


def test_an_opened_guard_may_not_disable_the_fighter():
    d = _mut()
    d["guard_integrity"]["opened_state"] = "fighter is stunned and cannot act"
    assert any("does not disable" in e for e in gd.check_guard_integrity(d))


def test_the_matchup_tables_keep_one_home():
    d = _mut()
    d["authority"]["matchup_reference"] = "docs/design/some_other_file.md"
    assert any("third copy" in e for e in gd.check_matchup_reference(d))


def test_required_prohibitions_and_invariants_are_declared():
    d = _mut()
    d["prohibitions"] = ["nothing relevant"]
    assert gd.check_prohibitions(d)
    d = _mut()
    d["invariants"] = [i for i in d["invariants"] if i["id"] != "every_guard_is_a_trade"]
    assert gd.check_invariants(d)


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 10:52 UTC | START ]
# Appended below the original author's END tag, which is theirs and untouched.
def test_telegraph_must_anchor_on_the_fastest_punch():
    d = _mut()
    d["telegraph"]["reference_startup_frames"] = 7
    assert any("fastest startup" in e for e in gd.check_telegraph(d))


def test_telegraph_must_not_be_inert():
    d = _mut()
    d["telegraph"]["evasion_gain_per_startup_frame"] = 0.001
    assert any("inert" in e for e in gd.check_telegraph(d))


def test_telegraph_may_not_make_a_punch_impossible():
    d = _mut()
    d["telegraph"]["max_multiplier"] = 5.0
    assert any("never impossible" in e for e in gd.check_telegraph(d))


def test_committed_defense_must_exist():
    d = _mut()
    del d["committed_defense"]
    assert any("inert at contact" in e for e in gd.check_committed_defense(d))


def test_commitment_may_not_zero_the_defence():
    """Zero would make being caught committed a guaranteed hit - a stun-lock by
    geometry, which Rule 11 forbids from either side of the exchange."""
    d = _mut()
    d["committed_defense"]["evasion_multiplier_while_committed"] = 0.0
    assert any("strictly inside" in e for e in gd.check_committed_defense(d))


def test_slipping_degrades_at_least_as_hard_as_covering():
    d = _mut()
    d["committed_defense"]["evasion_multiplier_while_committed"] = 0.9
    d["committed_defense"]["guard_extent_multiplier_while_committed"] = 0.5
    assert any("backwards" in e for e in gd.check_committed_defense(d))
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 10:52 UTC | END ]
