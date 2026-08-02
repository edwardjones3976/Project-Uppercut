# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""Phase 0 gate item: scorecard access boundaries documented and TESTABLE (Rule 3)."""
import json
from pathlib import Path
from tools.uppercut_validate import score_isolation as si

REPO = Path(__file__).resolve().parents[1]
SAMPLES = REPO / "tests/isolation_samples"


def test_checker_flags_source_violations():
    """Non-vacuity: the checker must catch a deliberate leak, or it proves nothing."""
    v = si.scan_source(SAMPLES / "violation_sample")
    assert len(v) >= 3
    assert {x.kind for x in v} == {"score_access"}
    assert any("cpu_fighter_logic" in x.detail for x in v)
    assert any("commentary" in x.detail for x in v)


def test_compliant_source_is_clean():
    assert si.scan_source(SAMPLES / "compliant_sample") == []


def test_compliant_event_log_is_clean():
    events = json.loads((SAMPLES / "compliant_log.json").read_text())
    assert si.check_event_log(events) == []


def test_leaking_event_log_is_caught():
    events = json.loads((SAMPLES / "leaking_log.json").read_text())
    kinds = {v.kind for v in si.check_event_log(events)}
    assert {"unsealed_card", "evidence_leak", "missing_assertion"} <= kinds


def test_every_forbidden_consumer_in_rule_3_is_covered():
    """Rule 3 names nine consumer categories; the contract must list all nine."""
    contract = si.load_contract()
    assert {c["id"] for c in contract["forbidden_consumers"]} == {
        "human_facing_fighter_logic", "cpu_fighter_logic", "referees",
        "trainers_and_corners", "commentary", "crowd_systems",
        "difficulty_or_adaptive", "live_replay_presentation", "advice_or_bonus_systems"}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
