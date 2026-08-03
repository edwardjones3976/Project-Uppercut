# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | START ]
"""Phase 1A step 5: collision truth laws.

Foundation pattern: the canonical document passes every check, and every
checker proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import collision as col

CANON = col.load()


def _mut():
    return copy.deepcopy(CANON)


def _stage(doc, sid):
    for s in doc["resolution_pipeline"]:
        if s["id"] == sid:
            return s
    raise KeyError(sid)


def _hurt(doc, region):
    for h in doc["volumes"]["hurtboxes"]:
        if h["condition_region"] == region:
            return h
    raise KeyError(region)


def _guard(doc, gid):
    for g in doc["volumes"]["guard_volumes"]:
        if g["id"] == gid:
            return g
    raise KeyError(gid)


def _band(doc, cls):
    for b in doc["quality_bands"]:
        if b["class"] == cls:
            return b
    raise KeyError(cls)


def test_canonical_document_passes_every_check():
    for name, fn in col.ALL_CHECKS:
        assert fn(CANON) == [], f"{name} failed on canonical data: {fn(CANON)}"


def test_run_all_clean_on_canon():
    assert col.run_all() == []


def test_schema_not_vacuous():
    doc = _mut()
    del doc["tuning_status"]
    assert col.check_schema(doc)


def test_swept_volumes_required():
    doc = _mut()
    doc["determinism"]["swept_volumes"] = False
    assert col.check_determinism(doc)
    assert col.check_schema(doc)


def test_snapshot_simultaneity_required():
    doc = _mut()
    doc["determinism"]["simultaneity"] = "sequential_mutating"
    assert col.check_determinism(doc)


def test_fixed_pair_ordering_required():
    doc = _mut()
    doc["determinism"]["pair_ordering"] = "iteration_order"
    assert col.check_determinism(doc)


def test_miss_must_be_ruled_out_first():
    doc = _mut()
    _stage(doc, "sweep_overlap")["verdict_if_true"] = "brushed"
    errs = col.check_pipeline_total(doc)
    assert errs and any("whiffed" in e for e in errs)


def test_all_seven_classes_reachable():
    doc = _mut()
    _stage(doc, "active_evasion")["verdict_if_true"] = "blocked"
    errs = col.check_pipeline_total(doc)
    assert errs and any("dodged" in e for e in errs)


def test_quality_dispatch_must_be_last():
    doc = _mut()
    _stage(doc, "dispatch_quality")["order"] = 1
    _stage(doc, "active_evasion")["order"] = 3
    assert col.check_pipeline_total(doc)


def test_evasion_ranked_before_guard():
    doc = _mut()
    _stage(doc, "active_evasion")["order"] = 2
    _stage(doc, "guard_intercept")["order"] = 1
    errs = col.check_pipeline_total(doc)
    assert errs and any("evasion" in e for e in errs)


def test_pipeline_fallthrough_targets_must_exist():
    doc = _mut()
    _stage(doc, "active_evasion")["on_false"] = "nowhere"
    assert col.check_pipeline_total(doc)


def test_hurtbox_region_must_exist():
    doc = _mut()
    _hurt(doc, "head")["condition_region"] = "left_shin"
    assert col.check_region_lock(doc)


def test_every_physical_region_needs_a_hurtbox():
    doc = _mut()
    doc["volumes"]["hurtboxes"] = [h for h in doc["volumes"]["hurtboxes"]
                                   if h["condition_region"] != "eye_left"]
    errs = col.check_region_lock(doc)
    assert errs and any("eye_left" in e for e in errs)


def test_side_specific_regions_declare_side():
    doc = _mut()
    _hurt(doc, "eye_right")["side"] = "center"
    assert col.check_region_lock(doc)


def test_guard_must_absorb_into_guard_integrity():
    doc = _mut()
    g = _guard(doc, "guard_high")
    g["absorbs_into"] = [a for a in g["absorbs_into"] if a != "guard_integrity"]
    assert col.check_guard_coverage(doc)


def test_guard_must_absorb_into_arms():
    doc = _mut()
    g = _guard(doc, "guard_body")
    g["absorbs_into"] = ["guard_integrity", "stamina"]
    assert col.check_guard_coverage(doc)


def test_guard_may_not_cover_everything():
    doc = _mut()
    _guard(doc, "guard_high")["covers_regions"] = list(col.PHYSICAL_REGIONS)
    errs = col.check_guard_coverage(doc)
    assert errs and any("counterable" in e for e in errs)


def test_interception_height_must_match_volume():
    doc = _mut()
    doc["guard_interception"]["blockable_low"] = ["guard_high"]
    assert col.check_guard_coverage(doc)


def test_either_must_name_every_guard_volume():
    doc = _mut()
    doc["guard_interception"]["blockable_either"] = ["guard_high", "guard_high"]
    assert col.check_guard_coverage(doc)


def test_interception_must_name_a_real_volume():
    doc = _mut()
    doc["guard_interception"]["blockable_high"] = ["guard_imaginary"]
    assert col.check_guard_coverage(doc)


def test_contact_classes_locked_to_canon():
    doc = _mut()
    assert col.check_contact_classes(doc) == []


def test_quality_bands_must_tile():
    doc = _mut()
    _band(doc, "grazed")["min_alignment"] = 0.4
    assert col.check_quality_bands(doc)


def test_quality_force_must_increase_strictly():
    doc = _mut()
    _band(doc, "solid")["delivered_force_fraction"] = 0.4
    errs = col.check_quality_bands(doc)
    assert errs and any("increase strictly" in e for e in errs)


def test_clean_delivers_full_force():
    doc = _mut()
    _band(doc, "clean")["delivered_force_fraction"] = 0.9
    assert col.check_quality_bands(doc)


def test_bands_must_reach_full_alignment():
    doc = _mut()
    _band(doc, "clean")["max_alignment"] = 0.95
    assert col.check_quality_bands(doc)


def test_move_table_targets_need_hurtboxes():
    doc = _mut()
    doc["volumes"]["hurtboxes"] = [h for h in doc["volumes"]["hurtboxes"]
                                   if h["condition_region"] != "jaw_chin"]
    errs = col.check_move_table_lock(doc)
    assert errs and any("jaw_chin" in e for e in errs)


def test_move_guard_interaction_must_be_covered():
    doc = _mut()
    del doc["guard_interception"]["blockable_high"]
    errs = col.check_move_table_lock(doc)
    assert errs and any("blockable_high" in e for e in errs)


def test_counterplay_required_for_every_offensive_move():
    doc = _mut()
    doc["guard_interception"]["blockable_low"] = []
    errs = col.check_move_table_lock(doc)
    assert errs and any("counterplay" in e for e in errs)


def test_uppercut_is_intercepted_by_the_low_guard_not_the_high():
    """Regression lock on the 2026-08-03 modelling correction: interception follows
    the punch's path, so an uppercut to the jaw is stopped by the dropped forearm."""
    moves = col._moves()
    upper = [m for m in moves if m["category"] == "uppercut"]
    assert upper, "the move table must contain uppercuts for this lock to mean anything"
    for m in upper:
        assert m["guard_interaction"] == "blockable_low"
        assert CANON["guard_interception"][m["guard_interaction"]] == ["guard_body"]
    assert col.check_move_table_lock(CANON) == []


def test_closing_velocity_into_punch_must_increase():
    doc = _mut()
    doc["closing_velocity"]["into_punch_max_multiplier"] = 1.0
    assert col.check_closing_velocity(doc)
    assert col.check_schema(doc)


def test_closing_velocity_must_not_dominate():
    doc = _mut()
    doc["closing_velocity"]["into_punch_max_multiplier"] = 5.0
    errs = col.check_closing_velocity(doc)
    assert errs and any("dominate" in e for e in errs)


def test_anti_cheat_vocabulary():
    doc = _mut()
    doc["volumes"]["assist_radius"] = 0.2
    assert col.check_anti_cheat(doc)


def test_knockout_roll_vocabulary_rejected():
    doc = _mut()
    doc["quality_bands"][0]["knockout_roll"] = 0.01
    assert col.check_anti_cheat(doc)


def test_required_prohibitions_present():
    doc = _mut()
    doc["prohibitions"] = [p for p in doc["prohibitions"] if "visible miss" not in p.lower()]
    assert col.check_prohibitions(doc)


def test_required_invariants_declared():
    doc = _mut()
    doc["invariants"] = [i for i in doc["invariants"] if i["id"] != "no_miss_as_hit"]
    assert col.check_invariants(doc)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | END ]

# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:38 UTC | START
#   Decision 0010: guard postures as coverage-extent modulation. Closes the pinned
#   "10 guards vs 2 guard volumes" drift. ]


def _ga(doc):
    return doc["guard_alignment"]


def test_canonical_guard_alignment_passes():
    assert col.check_guard_alignment(CANON) == []


def test_posture_identity_must_not_reach_the_pipeline():
    d = _mut()
    _ga(d)["posture_identity_read_by_pipeline"] = True
    assert any("posture identity" in e for e in col.check_guard_alignment(d))


def test_authority_must_be_extent_only():
    d = _mut()
    _ga(d)["authority"] = "posture_lookup_table"
    assert col.check_guard_alignment(d)


def test_no_alignment_state_may_zero_a_volume():
    d = _mut()
    _ga(d)["extent_bounds"]["min"] = 0.0
    assert any("zero" in e for e in col.check_guard_alignment(d))


def test_no_alignment_state_may_exceed_its_own_structure():
    d = _mut()
    _ga(d)["extent_bounds"]["max"] = 1.4
    assert any("past its own structure" in e for e in col.check_guard_alignment(d))


def test_volume_extent_range_must_respect_the_global_bounds():
    d = _mut()
    _guard(d, "guard_high")["coverage_extent"]["min_modulated"] = 0.05
    assert any("undercuts" in e for e in col.check_guard_alignment(d))


def test_baseline_must_sit_inside_its_own_modulation_range():
    d = _mut()
    _guard(d, "guard_body")["coverage_extent"]["baseline"] = 0.2
    assert any("outside its own" in e for e in col.check_guard_alignment(d))


def test_worked_example_cannot_name_an_unknown_volume():
    d = _mut()
    _ga(d)["worked_examples"][0]["extents"]["guard_shoulder"] = 0.9
    assert any("unknown" in e for e in col.check_guard_alignment(d))


def test_worked_example_extent_must_stay_in_range():
    d = _mut()
    _ga(d)["worked_examples"][0]["extents"]["guard_high"] = 0.05
    assert any("outside that volume" in e for e in col.check_guard_alignment(d))


def test_mechanism_must_not_be_inert():
    """Every posture holding identical extents across its states would satisfy
    the schema while expressing nothing - the drift would still be open."""
    d = _mut()
    flat = {"guard_high": 0.9, "guard_body": 0.9}
    for w in _ga(d)["worked_examples"]:
        w["extents"] = dict(flat)
    assert any("inert" in e for e in col.check_guard_alignment(d))


def test_intercept_stage_must_read_the_extent():
    d = _mut()
    st = _stage(d, "guard_intercept")
    st["reads"] = [r for r in st["reads"] if r != "guard_coverage_extent"]
    assert any("guard_coverage_extent" in e for e in col.check_guard_alignment(d))


def test_the_two_documented_conditionals_are_actually_expressible():
    """The point of the mechanism: the cross-arm uppercut split and the shell
    overhand turn are the same two volumes at different extents, not two new
    volumes and not a branch on a posture's name."""
    ex = {(w["posture"], w["state"]): w["extents"] for w in _ga(CANON)["worked_examples"]}
    assert ex[("cross_arm", "bar_low_aligned")]["guard_body"] > \
           ex[("cross_arm", "bar_high_or_split")]["guard_body"]
    assert ex[("philly_shell", "roll_timed_aligned")]["guard_high"] > \
           ex[("philly_shell", "roll_late_or_misaligned")]["guard_high"]
    ids = {g["id"] for g in CANON["volumes"]["guard_volumes"]}
    for e in ex.values():
        assert set(e) <= ids, "a posture invented a volume instead of reshaping one"


def test_posture_is_geometry_invariant_is_declared():
    d = _mut()
    d["invariants"] = [i for i in d["invariants"] if i["id"] != "posture_is_geometry"]
    assert col.check_invariants(d)


def test_posture_branching_prohibition_is_declared():
    d = _mut()
    d["prohibitions"] = [p for p in d["prohibitions"] if "coverage extents" not in p]
    assert col.check_prohibitions(d)

# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:38 UTC | END ]

