# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:45 UTC | START ]
"""WS5: the reference simulator and the ROADMAP's required automated checks.

These are the first tests in the repository that exercise a running fight rather
than a definition. The reference model is not authoritative - Unreal is
(Decision 0002) - but it is what lets the gate's balance and exploit checks run
at all before the engine can host them.
"""
from __future__ import annotations
import hashlib
import json

import pytest

from tools.uppercut_sim import canon, checks, policy
from tools.uppercut_sim.engine import Bout


def _hash(log):
    return hashlib.sha256(json.dumps(log, sort_keys=True).encode()).hexdigest()


def test_a_complete_bout_runs_end_to_end():
    bt = Bout(1234, "rusher", "counterpuncher")
    log = bt.run()
    assert log[0]["type"] == "bout_start"
    assert log[-1]["type"] == "judge_final_card"
    assert any(e["type"] == "punch_outcome" for e in log)
    assert bt.result()["fighters"][0]["thrown"] > 0


def test_same_seed_reproduces_the_log_byte_for_byte():
    a = Bout(99, "technician", "showman").run()
    b = Bout(99, "technician", "showman").run()
    assert _hash(a) == _hash(b)


def test_different_seeds_diverge():
    a = Bout(99, "technician", "showman").run()
    b = Bout(100, "technician", "showman").run()
    assert _hash(a) != _hash(b)


def test_every_stress_profile_has_a_policy_mapping():
    """A canon profile with no mapping must be a loud failure, not a silent gap."""
    assert set(policy.available_profiles()) == set(canon.stress_profile_names())


def test_the_observation_has_no_path_to_the_cards():
    """Rule 3 as a property of the call signature: a policy is handed a plain
    dict of observable state and no reference to the bout."""
    bt = Bout(7, "drainer", "power_threat")
    bt.run()
    obs = bt.observe(bt.fighters[0], bt.fighters[1])
    assert isinstance(obs, dict)
    assert not any(isinstance(v, Bout) for v in obs.values())
    for key in obs:
        assert "card" not in key.lower() and "score" not in key.lower()


def test_judge_events_are_emitted_and_sealed():
    bt = Bout(11, "rusher", "drainer")
    log = bt.run()
    judge = [e for e in log if e["type"].startswith("judge_")]
    assert judge, "no judge events at all would make the sealing test vacuous"
    assert all(e["visibility"] == "sealed" for e in judge)


def test_no_observable_event_leaks_card_data():
    bt = Bout(12, "showman", "technician")
    for ev in bt.run():
        if ev["visibility"] == "observable":
            blob = json.dumps(ev.get("payload", {})).lower()
            assert "card" not in blob and "scorecard" not in blob


def test_causality_points_backward():
    bt = Bout(13, "rusher", "technician")
    for ev in bt.run():
        for ref in ev.get("explains", []):
            assert ref < ev["seq"]


@pytest.mark.parametrize("name,fn", checks.ALL_CHECKS, ids=[n for n, _ in checks.ALL_CHECKS])
def test_required_roadmap_check(name, fn):
    """The ROADMAP's required automated checks, each reported by name."""
    findings = fn()
    assert findings == [], f"{name}: {findings}"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:45 UTC | END ]
