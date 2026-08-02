# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | START ]
"""Phase 1A step 2: movement, facing and range-band geometry laws.

Foundation pattern: the canonical document passes every check, and every
checker proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import movement as mv

CANON = mv.load()


def _mut():
    return copy.deepcopy(CANON)


def test_canonical_document_passes_every_check():
    for name, fn in mv.ALL_CHECKS:
        assert fn(CANON) == [], f"{name} failed on canonical data: {fn(CANON)}"


def test_run_all_clean_on_canon():
    assert mv.run_all() == []


def test_schema_not_vacuous():
    doc = _mut()
    del doc["tuning_status"]
    assert mv.check_schema(doc)


def test_band_order_enforced():
    doc = _mut()
    b = doc["range_bands"]["bands"]
    b[1], b[2] = b[2], b[1]
    assert mv.check_bands(doc)


def test_band_contiguity_enforced():
    doc = _mut()
    doc["range_bands"]["bands"][1]["min_ru"] = 0.4
    assert mv.check_bands(doc)


def test_hysteresis_must_be_positive():
    doc = _mut()
    doc["range_bands"]["hysteresis_ru"] = 0
    assert mv.check_bands(doc)


def test_hysteresis_below_narrowest_band():
    doc = _mut()
    doc["range_bands"]["hysteresis_ru"] = 0.5
    assert mv.check_bands(doc)


def test_posture_lock_to_combat_states():
    doc = _mut()
    doc["locomotion"]["modes"][0]["posture_mode"] = "sprint"
    assert mv.check_posture_lock(doc)


def test_compression_must_compress():
    doc = _mut()
    for m in doc["locomotion"]["modes"]:
        if m["posture_mode"] == "boxing_steps":
            m["stride_length_ru"] = 0.9
    assert mv.check_compression_law(doc)


def test_planted_means_planted():
    doc = _mut()
    for m in doc["locomotion"]["modes"]:
        if m["posture_mode"] == "planted":
            m["stride_length_ru"] = 0.2
    assert mv.check_compression_law(doc)


def test_mobile_modes_declare_accel():
    doc = _mut()
    for m in doc["locomotion"]["modes"]:
        if m["posture_mode"] == "free_navigation":
            m["acceleration_frames"] = 0
    assert mv.check_compression_law(doc)


def test_displacement_cap_below_stride():
    doc = _mut()
    doc["locomotion"]["max_frame_displacement_ru"] = 0.9
    assert mv.check_displacement(doc)


def test_separation_below_clinch_ceiling():
    doc = _mut()
    doc["separation"]["min_center_distance_ru"] = 0.4
    assert mv.check_displacement(doc)


def test_facing_must_tile_the_circle():
    doc = _mut()
    doc["facing"]["arcs"][0]["half_width_deg"] = 50
    assert mv.check_facing(doc)


def test_punches_only_from_front():
    doc = _mut()
    for a in doc["facing"]["arcs"]:
        if a["key"] == "back":
            a["punches_permitted"] = True
    assert mv.check_facing(doc)


def test_anti_cheat_vocabulary():
    doc = _mut()
    doc["locomotion"]["snap_to_range"] = True
    assert mv.check_anti_cheat(doc)


def test_threat_compression_bands_exist():
    doc = _mut()
    doc["locomotion"]["threat_compression"]["threat_bands"] = ["narnia"]
    assert mv.check_threat_compression(doc)


def test_threat_compression_observables_only():
    doc = _mut()
    doc["locomotion"]["threat_compression"]["observable_inputs"].append("official_scorecards")
    errs = mv.check_threat_compression(doc)
    assert errs and any("Rule 3" in e for e in errs)


def test_event_vocabulary_not_vacuous():
    doc = _mut()
    doc["emits"] = ["moonwalk"]
    assert mv.check_events(doc)


def test_required_invariants_declared():
    doc = _mut()
    doc["invariants"] = [i for i in doc["invariants"] if i["id"] != "no_magnetic_correction"]
    assert mv.check_invariants(doc)
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | END ]
