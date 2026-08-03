# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:47 UTC | START ]
"""Phase 1A step 4: animation state laws.

Foundation pattern: the canonical document passes every check, and every
checker proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import animation as anim

CANON = anim.load()


def _mut():
    return copy.deepcopy(CANON)


def _move_anim(doc, mid):
    for a in doc["move_animations"]:
        if a["move_id"] == mid:
            return a
    raise KeyError(mid)


def _interrupt(doc, iid):
    for i in doc["interrupts"]:
        if i["id"] == iid:
            return i
    raise KeyError(iid)


def _vis(doc, region):
    for d in doc["damage_visualization"]:
        if d["condition_region"] == region:
            return d
    raise KeyError(region)


def test_canonical_document_passes_every_check():
    for name, fn in anim.ALL_CHECKS:
        assert fn(CANON) == [], f"{name} failed on canonical data: {fn(CANON)}"


def test_run_all_clean_on_canon():
    assert anim.run_all() == []


def test_schema_not_vacuous():
    doc = _mut()
    del doc["tuning_status"]
    assert anim.check_schema(doc)


def test_animation_may_not_write_simulation_state():
    doc = _mut()
    doc["authority"]["writes_simulation_state"] = True
    assert anim.check_authority(doc)
    assert anim.check_schema(doc)


def test_hitbox_transforms_may_not_come_from_blended_playback():
    doc = _mut()
    doc["authority"]["hitbox_transform_source"] = "blended_runtime_playback"
    errs = anim.check_authority(doc)
    assert errs and any("blended" in e for e in errs)


def test_root_motion_may_not_drive_position():
    doc = _mut()
    doc["authority"]["root_motion_drives_position"] = True
    errs = anim.check_authority(doc)
    assert errs and any("movement model owns position" in e for e in errs)


def test_every_combat_state_needs_an_animation():
    doc = _mut()
    doc["state_animations"] = [a for a in doc["state_animations"]
                               if a["combat_state"] != "staggered"]
    errs = anim.check_state_coverage(doc)
    assert errs and any("staggered" in e for e in errs)


def test_unknown_combat_state_rejected():
    doc = _mut()
    doc["state_animations"].append({"combat_state": "showboating",
                                    "clip_id": "anim_showboat", "loops": True})
    assert anim.check_state_coverage(doc)


def test_provisioned_states_must_not_be_animated():
    doc = _mut()
    doc["state_animations"].append({"combat_state": "ultimate_execution",
                                    "clip_id": "anim_ultimate", "loops": False})
    errs = anim.check_state_coverage(doc)
    assert errs and any("Rule 18" in e for e in errs)


def test_move_frames_must_match_move_data():
    doc = _mut()
    _move_anim(doc, "jab_lead")["startup_ticks"] = 6
    errs = anim.check_move_frame_lock(doc)
    assert errs and any("disagree" in e for e in errs)


def test_every_move_needs_an_animation():
    doc = _mut()
    doc["move_animations"] = [a for a in doc["move_animations"]
                              if a["move_id"] != "roll_under"]
    errs = anim.check_move_frame_lock(doc)
    assert errs and any("roll_under" in e for e in errs)


def test_unknown_move_rejected():
    doc = _mut()
    doc["move_animations"].append({"move_id": "spinning_backfist",
                                   "clip_id": "anim_sbf", "startup_ticks": 5,
                                   "active_ticks": 2, "recovery_ticks": 9})
    assert anim.check_move_frame_lock(doc)


def test_hit_reaction_must_outrank_move_commit():
    doc = _mut()
    _interrupt(doc, "hit_reaction")["priority"] = 5
    errs = anim.check_interrupts(doc)
    assert errs and any("finish throwing" in e for e in errs)


def test_knockdown_must_outrank_hit_reaction():
    doc = _mut()
    _interrupt(doc, "knockdown")["priority"] = 55
    assert anim.check_interrupts(doc)


def test_stoppage_must_be_highest_interrupt():
    doc = _mut()
    _interrupt(doc, "stoppage")["priority"] = 30
    assert anim.check_interrupts(doc)


def test_reactive_interrupts_must_interrupt_below():
    doc = _mut()
    _interrupt(doc, "stagger")["interrupts_everything_below"] = False
    assert anim.check_interrupts(doc)


def test_interrupt_priorities_must_be_unique():
    doc = _mut()
    _interrupt(doc, "locomotion")["priority"] = _interrupt(doc, "move_commit")["priority"]
    assert anim.check_interrupts(doc)


def test_blend_may_not_delay_state_change():
    doc = _mut()
    doc["blending"]["blend_may_delay_state_change"] = True
    assert anim.check_blending(doc)
    assert anim.check_schema(doc)


def test_blend_must_stay_below_shortest_offensive_startup():
    doc = _mut()
    doc["blending"]["max_blend_ticks"] = 12
    errs = anim.check_blending(doc)
    assert errs and any("unreadable" in e for e in errs)


def test_blend_bound_is_scoped_to_offensive_windups():
    """The 2-tick guard startup must NOT drive the blend budget: it is a near-instant
    defensive action, not a windup carrying counterplay information. Regression lock on
    the 2026-08-03 scoping correction."""
    moves = anim._moves()
    guard_starts = [m["startup_frames"] for m in moves.values() if m["category"] == "guard"]
    assert min(guard_starts) < CANON["blending"]["max_blend_ticks"], (
        "this lock is meaningless unless a guard startup is shorter than the blend budget")
    assert anim.check_blending(CANON) == []


def test_response_latency_bounded():
    doc = _mut()
    doc["blending"]["input_to_visible_response_ticks"] = 9
    assert anim.check_blending(doc)
    assert anim.check_schema(doc)


def test_tracked_condition_must_be_visible():
    doc = _mut()
    doc["damage_visualization"] = [d for d in doc["damage_visualization"]
                                   if d["condition_region"] != "arm_left"]
    errs = anim.check_damage_visualization(doc)
    assert errs and any("arm_left" in e for e in errs)


def test_eye_damage_must_be_side_specific():
    doc = _mut()
    _vis(doc, "eye_right")["side_specific"] = False
    errs = anim.check_damage_visualization(doc)
    assert errs and any("side-specific" in e for e in errs)


def test_unknown_condition_region_rejected():
    doc = _mut()
    doc["damage_visualization"].append({"condition_region": "left_shin",
                                        "visible": True, "side_specific": True})
    assert anim.check_damage_visualization(doc)


def test_southpaw_must_be_exact_mirror():
    doc = _mut()
    doc["stance"]["southpaw_handling"] = "separate_clip_set"
    assert anim.check_stance(doc)
    assert anim.check_schema(doc)


def test_switch_mechanism_must_name_attribute_penalties():
    doc = _mut()
    doc["stance"]["switch_mechanism"] = "Fighters just turn around."
    assert anim.check_stance(doc)


def test_required_prohibitions_present():
    doc = _mut()
    doc["prohibitions"] = [p for p in doc["prohibitions"] if "root motion" not in p.lower()]
    assert anim.check_prohibitions(doc)


def test_required_invariants_declared():
    doc = _mut()
    doc["invariants"] = [i for i in doc["invariants"] if i["id"] != "pose_not_truth"]
    assert anim.check_invariants(doc)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:47 UTC | END ]
