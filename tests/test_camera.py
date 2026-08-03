# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | START ]
"""Phase 1A step 3: camera behaviour laws.

Foundation pattern: the canonical document passes every check, and every
checker proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import camera as cam

CANON = cam.load()


def _mut():
    return copy.deepcopy(CANON)


def _mode(doc, mid):
    for m in doc["framing_modes"]:
        if m["id"] == mid:
            return m
    raise KeyError(mid)


def test_canonical_document_passes_every_check():
    for name, fn in cam.ALL_CHECKS:
        assert fn(CANON) == [], f"{name} failed on canonical data: {fn(CANON)}"


def test_run_all_clean_on_canon():
    assert cam.run_all() == []


def test_schema_not_vacuous():
    doc = _mut()
    del doc["tuning_status"]
    assert cam.check_schema(doc)


def test_camera_may_not_write_simulation_state():
    doc = _mut()
    doc["authority"]["writes_simulation_state"] = True
    assert cam.check_authority(doc)
    assert cam.check_schema(doc)


def test_camera_stays_out_of_determinism_hash():
    doc = _mut()
    doc["authority"]["participates_in_determinism_hash"] = True
    assert cam.check_authority(doc)


def test_framing_must_stay_a_pure_function_of_the_log():
    doc = _mut()
    doc["authority"]["derivation"] = "reads_render_thread_state"
    assert cam.check_authority(doc)


def test_score_isolation_blocks_sealed_inputs():
    doc = _mut()
    doc["observable_inputs"].append("official_scorecards")
    errs = cam.check_input_domains(doc)
    assert errs and any("Rule 3" in e for e in errs)


def test_undeclared_input_domain_rejected():
    doc = _mut()
    doc["observable_inputs"].append("director_intuition")
    assert cam.check_input_domains(doc)


def test_priorities_must_be_a_strict_total_order():
    doc = _mut()
    _mode(doc, "exchange_read")["priority"] = _mode(doc, "ring_wide")["priority"]
    assert cam.check_priority_order(doc)


def test_exactly_one_default_mode():
    doc = _mut()
    doc["framing_modes"] = [m for m in doc["framing_modes"] if m["trigger"]["kind"] != "default"]
    assert cam.check_priority_order(doc)


def test_default_mode_must_be_lowest_priority():
    doc = _mut()
    _mode(doc, "bout_default")["priority"] = 999
    assert cam.check_priority_order(doc)


def test_spectacle_may_not_outrank_officiating():
    doc = _mut()
    _mode(doc, "showmanship_flourish")["priority"] = 95
    errs = cam.check_officiating_precedence(doc)
    assert errs and any("outranks officiating" in e for e in errs)


def test_spectacle_needs_a_tick_cap():
    doc = _mut()
    _mode(doc, "showmanship_flourish")["max_hold_ticks"] = None
    assert cam.check_officiating_precedence(doc)


def test_officiating_modes_are_required():
    doc = _mut()
    doc["framing_modes"] = [m for m in doc["framing_modes"] if m["id"] != "knockdown_read"]
    assert cam.check_officiating_precedence(doc)


def test_band_lock_rejects_unknown_band():
    doc = _mut()
    _mode(doc, "exchange_read")["distance_bands"].append("point_blank")
    assert cam.check_band_lock(doc)


def test_every_range_band_has_framing():
    doc = _mut()
    doc["framing_modes"] = [m for m in doc["framing_modes"] if m["id"] != "ring_wide"]
    errs = cam.check_band_lock(doc)
    assert errs and any("out_of_range" in e for e in errs)


def test_trigger_bands_must_match_distance_bands():
    doc = _mut()
    _mode(doc, "clinch_inside")["trigger"]["bands"] = ["clinch"]
    assert cam.check_band_lock(doc)


def test_event_vocabulary_not_vacuous():
    doc = _mut()
    _mode(doc, "knockdown_read")["trigger"]["events"] = ["dramatic_zoom"]
    assert cam.check_event_vocabulary(doc)


def test_live_modes_must_frame_both_fighters():
    doc = _mut()
    _mode(doc, "exchange_read")["both_fighters_framed"] = False
    errs = cam.check_readability(doc)
    assert errs and any("F.24" in e for e in errs)


def test_contact_window_cut_stays_prohibited():
    doc = _mut()
    doc["readability"]["contact_window_cut_prohibited"] = False
    assert cam.check_readability(doc)
    assert cam.check_schema(doc)


def test_settle_must_fit_inside_cut_cooldown():
    doc = _mut()
    doc["readability"]["settle_ticks_after_cut"] = 999
    assert cam.check_readability(doc)


def test_required_prohibitions_present():
    doc = _mut()
    doc["prohibitions"] = [p for p in doc["prohibitions"] if "scorecard" not in p.lower()]
    assert cam.check_prohibitions(doc)


def test_required_invariants_declared():
    doc = _mut()
    doc["invariants"] = [i for i in doc["invariants"] if i["id"] != "camera_never_writes"]
    assert cam.check_invariants(doc)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | END ]
