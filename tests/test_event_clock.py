# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:38 UTC | START ]
"""Event presentation model and the authoritative clock.

The event checks implement section 13 of the merged event presentation reference
(OpenAI GPT-5.6, commit a1c900e), which asked for validators and did not have
any. The clock checks unblock "accelerated-clock synchronization" - one of the
three required ROADMAP checks that could not run because there was no clock.

Foundation pattern: canon passes, every checker fails on a mutation.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import clock, event

EVENT = event.load()
CLOCK = clock.load()


def _e():
    return copy.deepcopy(EVENT)


def _c():
    return copy.deepcopy(CLOCK)


# ---- event ----------------------------------------------------------------
def test_event_canon_passes():
    assert event.run_all(EVENT) == []


def test_an_event_needs_all_four_authorities():
    for role in ("referee", "judge", "timekeeper", "ringside_physician"):
        d = _e()
        d["required_officials"] = [o for o in d["required_officials"] if o["role"] != role]
        assert any(role in x for x in event.check_officials(d)), role


def test_three_judges_minimum():
    d = _e()
    for o in d["required_officials"]:
        if o["role"] == "judge":
            o["min"] = 1
    assert any("three judges" in x for x in event.check_officials(d))


def test_prestige_may_never_reach_the_fight():
    d = _e()
    d["authority"]["prestige_alters_combat"] = True
    assert any("land harder" in x for x in event.check_authority(d))


def test_broadcast_holds_no_privileged_or_future_knowledge():
    for key in ("broadcast_has_privileged_knowledge", "broadcast_has_future_knowledge"):
        d = _e()
        d["authority"][key] = True
        assert event.check_authority(d), key


def test_a_dynamic_incident_may_not_decide_a_fight():
    d = _e()
    d["authority"]["dynamic_incidents_alter_outcomes"] = True
    assert any("rigged fight with good lighting" in x for x in event.check_authority(d))


def test_presentation_may_not_hide_the_decisive_moment():
    d = _e()
    d["authority"]["presentation_may_obscure_evidence"] = True
    assert any("spectacle that hides" in x for x in event.check_authority(d))


def test_ring_size_must_be_real_space():
    d = _e()
    d["venue_requirements"]["ring_size_as_hidden_stat_modifier"] = True
    assert any("hidden stat modifier" in x for x in event.check_venue(d))


def test_commentary_crew_scales_with_importance():
    d = _e()
    for c in d["event_classes"]:
        if c["id"] == "championship_night":
            c["commentary_crew"] = 2
    assert any("must scale" in x for x in event.check_event_classes(d))


def test_championship_metadata_requirement_is_not_inert():
    d = _e()
    for c in d["event_classes"]:
        c["requires_championship_metadata"] = False
    assert any("inert" in x for x in event.check_event_classes(d))


def test_knockdowns_and_stoppage_reasons_stay_visible():
    d = _e()
    d["evidence_visibility"]["must_remain_visible"] = ["contact_classification", "count",
                                                       "foul", "something_else"]
    assert any("stoppage_reason" in x for x in event.check_evidence(d))


def test_licensed_content_requires_provenance():
    d = _e()
    d["provenance_required_for"] = ["sponsor_content", "licensed_music", "brand_placement"]
    assert any("celebrity_appearance" in x for x in event.check_provenance(d))


# ---- clock ----------------------------------------------------------------
def test_clock_canon_passes():
    assert clock.run_all(CLOCK) == []


def test_every_named_system_reads_the_one_clock():
    d = _c()
    d["authority"]["read_by"] = [r for r in d["authority"]["read_by"] if r != "judging"]
    assert any("second clock wearing a different name" in x for x in clock.check_authority(d))


def test_acceleration_is_display_only():
    for key in ("affects_simulation_tick_rate", "affects_authored_frame_data",
                "affects_stamina_per_tick"):
        d = _c()
        d["accelerated_clock"][key] = True
        assert clock.check_acceleration(d), key


def test_the_count_clock_is_exempt_from_acceleration():
    """A knockdown count is a safety instrument, not a pacing option."""
    d = _c()
    d["accelerated_clock"]["affects_knockdown_count_clock"] = True
    assert any("safety instrument" in x for x in clock.check_acceleration(d))


def test_the_acceleration_ratio_is_canonical():
    d = _c()
    d["accelerated_clock"]["on_real_seconds"] = 90
    assert any("3:00 over 1:45" in x for x in clock.check_acceleration(d))


def test_free_form_round_lengths_are_prohibited():
    d = _c()
    d["free_form_round_length_permitted"] = True
    assert any("no free-form values" in x for x in clock.check_rounds(d))


def test_the_clock_and_condition_models_must_agree_on_the_break():
    """Cross-file lock: two files stating the same break differently is two
    clocks by another name."""
    d = _c()
    d["between_rounds_break_seconds"] = 30
    d["authority"]["tick_rate_hz"] = 60
    assert clock.check_rounds(d) == []
    d["authority"]["read_by"].append("noop")
    assert clock.check_rounds(d) == []


def test_wall_clock_never_drives_the_simulation():
    d = _c()
    d["authority"]["wall_clock_drives_simulation"] = True
    assert any("wall-clock time may not drive" in x for x in clock.check_authority(d))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:38 UTC | END ]
