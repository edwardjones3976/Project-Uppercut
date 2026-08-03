# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:31 UTC | START ]
"""Canonical data loader. Every number the simulator uses comes from here, so the
reference model can never quietly acquire tuning values of its own."""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data"


@lru_cache(maxsize=None)
def _load(rel: str) -> dict:
    return json.loads((DATA / rel).read_text(encoding="utf-8"))


def moves() -> dict:
    return {m["id"]: m for m in _load("moves/generic_sandbox_moves.json")["moves"]}


def punches() -> dict:
    offensive = {"jab", "cross", "hook", "uppercut", "overhand", "body_shot"}
    return {k: v for k, v in moves().items() if v.get("category") in offensive}


def punch_model() -> dict:
    return _load("punch_model.json")


def collision() -> dict:
    return _load("collision_model.json")


def contact_classes() -> list:
    return _load("contact_classes.json")["classes"]


def condition() -> dict:
    return _load("condition_model.json")


def guard_evasion() -> dict:
    return _load("guard_evasion_model.json")


def crowd() -> dict:
    return _load("crowd_model.json")


def cpu() -> dict:
    return _load("cpu_decision_model.json")


def movement() -> dict:
    return _load("movement_model.json")


def ability() -> dict:
    return _load("ability_model.json")


def combat_states() -> dict:
    return _load("combat_states.json")


def attribute_effects() -> dict:
    return _load("attribute_effects.json")


def attribute_families() -> dict:
    return _load("attribute_families.json")


def stress_profile(name: str) -> dict:
    return json.loads((DATA / "stress_profiles" / f"{name}.json").read_text(encoding="utf-8"))


def stress_profile_names() -> list:
    return sorted(p.stem for p in (DATA / "stress_profiles").glob("*.json"))


def quality_thresholds() -> list:
    qb = sorted(collision()["quality_bands"], key=lambda q: q["min_alignment"])
    return [float(q["min_alignment"]) for q in qb[1:]]


def outcome_recovery() -> dict:
    return {r["class"]: r for r in punch_model()["outcome_recovery"]["rows"]}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:31 UTC | END ]
