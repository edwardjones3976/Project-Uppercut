# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:02 UTC | START ]
"""Phase 1A step 10: logging and replay guarantees.

Foundation pattern: the canonical document passes every check, and every checker
proves non-vacuous by failing on a mutated copy.
"""
from __future__ import annotations
import copy

from tools.uppercut_validate import replay as rp

CANON = rp.load()


def _mut():
    return copy.deepcopy(CANON)


def test_canonical_model_passes_every_check():
    assert rp.run_all(CANON) == []


def test_resimulation_must_be_byte_identical():
    d = _mut()
    d["resimulation"]["byte_identical_required"] = False
    assert any("weaker claim" in e for e in rp.check_resimulation(d))


def test_wall_clock_may_not_reach_the_log():
    d = _mut()
    d["resimulation"]["wall_clock_may_affect_outcome"] = True
    assert any("wall-clock time may not reach" in e for e in rp.check_resimulation(d))


def test_only_non_authoritative_systems_may_be_excluded_from_the_hash():
    """Excluding something that writes simulation state is how a determinism hash
    stops meaning anything."""
    d = _mut()
    d["resimulation"]["excluded_from_hash"].append("collision")
    assert any("stops meaning anything" in e for e in rp.check_resimulation(d))


def test_the_camera_must_be_excluded():
    d = _mut()
    d["resimulation"]["excluded_from_hash"] = [
        x for x in d["resimulation"]["excluded_from_hash"] if x != "camera"]
    assert any("camera must be excluded" in e for e in rp.check_resimulation(d))


def test_replay_may_not_rerun_cpu_decisions():
    d = _mut()
    d["replay"]["reruns_cpu_decisions"] = True
    assert any("second fight" in e for e in rp.check_replay(d))


def test_replay_may_not_rerun_judging():
    d = _mut()
    d["replay"]["reruns_judging"] = True
    assert any("judging" in e for e in rp.check_replay(d))


def test_replay_may_not_rerun_the_rng():
    d = _mut()
    d["replay"]["reruns_rng"] = True
    assert any("the RNG" in e for e in rp.check_replay(d))


def test_the_log_must_be_ordered_and_clocked():
    for key in ("monotonic_seq", "monotonic_tick", "every_event_carries_clock",
                "explains_references_are_backward"):
        d = _mut()
        d["log_requirements"][key] = False
        assert any(key in e for e in rp.check_log_requirements(d)), key


def test_stoppages_must_be_explainable():
    """The gate asks that the log explain major events; a stoppage nobody can
    trace back is exactly what that guards against."""
    d = _mut()
    d["log_requirements"]["required_explained_types"] = [
        t for t in d["log_requirements"]["required_explained_types"] if t != "stoppage"]
    assert any("stoppage" in e for e in rp.check_log_requirements(d))


def test_required_explained_types_must_be_real_events():
    d = _mut()
    d["log_requirements"]["required_explained_types"].append("vibes_shift")
    assert any("not a fight_event type" in e for e in rp.check_log_requirements(d))


def test_every_sealed_event_needs_a_visibility_rule():
    d = _mut()
    d["visibility_rules"] = [v for v in d["visibility_rules"]
                             if v["event_type"] != "judge_final_card"]
    assert any("no visibility rule" in e for e in rp.check_visibility(d))


def test_a_sealed_event_declared_observable_is_caught():
    d = _mut()
    for v in d["visibility_rules"]:
        if v["event_type"] == "judge_round_card":
            v["visibility"] = "observable"
    assert any("Rule 3 VIOLATION" in e for e in rp.check_visibility(d))


def test_replay_may_not_widen_when_sealed_events_appear():
    d = _mut()
    d["replay"]["sealed_events_visible_during"] = ["archival_reveal", "immediate_result"]
    assert any("stay sealed through the fight" in e for e in rp.check_visibility(d))


def test_the_two_contracts_stay_separate():
    """Resimulation reproduces the log; replay reproduces the presentation. The
    canon must not quietly collapse them into one."""
    assert CANON["resimulation"]["reproduces"] == "authoritative_event_log"
    assert CANON["replay"]["source"] == "saved_event_log"
    assert CANON["replay"]["reruns_cpu_decisions"] is False


def test_required_prohibitions_and_invariants_are_declared():
    d = _mut()
    d["prohibitions"] = ["nothing relevant"]
    assert rp.check_prohibitions(d)
    d = _mut()
    d["invariants"] = [i for i in d["invariants"] if i["id"] != "replay_never_redecides"]
    assert rp.check_invariants(d)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:02 UTC | END ]
