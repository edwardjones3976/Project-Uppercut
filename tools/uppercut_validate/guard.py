# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:36 UTC | START ]
"""ROADMAP Phase 1A step 7 validator: guard and evasion.

This is where Decision 0010 stops being architecture. The ten named guards of
docs/design/boxing_guard_matchups.md land as authored postures that modulate the
coverage extents of the two collision guard volumes, and evasion lands as an
active choice the model must reward above covering.

Enforces Rule 4 (every guard is a trade; a guard break is earned, not counted),
Rule 13 (collision stays authoritative; active evasion outranks passive cover),
Rule 14 (blocking costs something), Rule 22 (the move table agrees), and
Decision 0010 (extents inside the collision model's declared bounds).
"""
from __future__ import annotations
import json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

# The two postures whose conditional coverage the guard doc's reconciliation log
# resolves, and whose states the collision model ships as worked examples.
RECONCILED_STATES = {
    "cross_arm": {"bar_low_aligned", "bar_high_or_split"},
    "philly_shell": {"roll_timed_aligned", "roll_late_or_misaligned"},
}

REQUIRED_INVARIANTS = (
    "every_guard_is_a_trade", "extents_within_volume_bounds",
    "posture_alignment_states_declared", "survival_posture_is_priced",
    "evasion_outranks_guard", "evasion_moves_exist", "guard_break_is_earned",
    "collision_stays_authoritative",
)

REQUIRED_PROHIBITIONS = ("sole authority", "posture's identity", "every guard is a trade",
                         "varied pressure", "indefinitely safe", "active evasion")


def load() -> dict:
    return json.loads((REPO / "data" / "guard_evasion_model.json").read_text())


def _collision() -> dict:
    return json.loads((REPO / "data" / "collision_model.json").read_text())


def _moves() -> dict:
    doc = json.loads((REPO / "data" / "moves" / "generic_sandbox_moves.json").read_text())
    return {m["id"]: m for m in doc["moves"]}


def _regions() -> set:
    doc = json.loads((REPO / "data" / "condition_regions.json").read_text())
    return {r["key"] for r in doc["regions"]}


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "guard_evasion_model.schema.json")


def check_authority(doc: dict) -> list:
    a = doc["authority"]
    errs = []
    if a["resolves_contact"]:
        errs.append("Rule 13: this file may not resolve contact - the collision pipeline is the "
                    "sole authority on whether an attempt was blocked")
    if a["posture_identity_read_by_pipeline"]:
        errs.append("Decision 0010: a posture is geometry, not a flag the resolver branches on")
    if not a["supplies_coverage_extents"]:
        errs.append("Decision 0010: postures influence collision only by supplying coverage extents")
    return errs


def check_postures(doc: dict) -> list:
    """Rule 4: every guard is a trade, and maximum coverage is never free."""
    errs = []
    ids = [p["id"] for p in doc["postures"]]
    if len(set(ids)) != len(ids):
        errs.append("duplicate posture id")
    for p in doc["postures"]:
        ext = p["extents"]
        # A posture that covers everything is not a guard, it is an off switch.
        if all(v >= 0.95 for v in ext.values()):
            errs.append(f"Rule 4: posture '{p['id']}' covers every lane at full extent - every "
                        f"guard must sell one lane to buy another")
        if all(v <= 0.45 for v in ext.values()):
            errs.append(f"posture '{p['id']}' covers nothing meaningful in either lane; that is a "
                        f"stance, not a guard")
        # Maximum coverage has to be paid for somewhere observable.
        if not p["offense_cheap"]:
            priced = (p["mobility_multiplier"] <= 0.8 or p["visibility"] <= 0.45
                      or p["stamina_per_tick"] >= 0.08)
            if not priced:
                errs.append(f"Rule 4: posture '{p['id']}' offers no cheap offense yet pays nothing "
                            f"in mobility, vision or stamina - a free survival posture would never "
                            f"be worth leaving")
        overlap = set(p["offense_cheap"]) & set(p["offense_expensive"])
        if overlap:
            errs.append(f"posture '{p['id']}' lists {sorted(overlap)} as both cheap and expensive")
    return errs


def check_extent_agreement(doc: dict) -> list:
    """Decision 0010: extents live inside the collision model's declared bounds."""
    col = _collision()
    vols = {g["id"]: g for g in col["volumes"]["guard_volumes"]}
    errs = []
    for p in doc["postures"]:
        if set(p["extents"]) != set(vols):
            errs.append(f"posture '{p['id']}' must supply an extent for exactly the declared guard "
                        f"volumes {sorted(vols)}, got {sorted(p['extents'])}")
            continue
        for vid, val in p["extents"].items():
            ce = vols[vid].get("coverage_extent", {})
            lo, hi = ce.get("min_modulated"), ce.get("max_modulated")
            if lo is not None and not lo <= val <= hi:
                errs.append(f"posture '{p['id']}' sets '{vid}' to {val}, outside that volume's "
                            f"modulation range [{lo}, {hi}]")
    return errs


def check_alignment_states(doc: dict) -> list:
    """The reconciled conditionals must use the ids the collision model already ships."""
    errs = []
    by = {p["id"]: p for p in doc["postures"]}
    for pid, expected in RECONCILED_STATES.items():
        p = by.get(pid)
        if p is None:
            errs.append(f"posture '{pid}' is absent, but canon reconciles its coverage conditionally")
            continue
        got = set(p["alignment_states"])
        if got != expected:
            errs.append(f"posture '{pid}' declares alignment states {sorted(got)}; the collision "
                        f"model's worked examples use {sorted(expected)} - drift here would break "
                        f"the conditional coverage the reconciliation log resolved")
    # Non-vacuity: a posture whose states cannot differ expresses nothing.
    for p in doc["postures"]:
        if len(p["alignment_states"]) != len(set(p["alignment_states"])):
            errs.append(f"posture '{p['id']}' repeats an alignment state")
    return errs


def check_evasion_economy(doc: dict) -> list:
    """Rule 13: the defender who moves earns more than the defender who covers."""
    e = doc["evasion_economy"]
    errs = []
    if not e["outranks_guard"]:
        errs.append("Rule 13: active evasion must outrank passive covering, matching the collision "
                    "pipeline's stage order")
    if e["mistime_penalty_ticks"] <= 0:
        errs.append("Rule 13: a mistimed evasion must cost something, or covering becomes pointless")
    # Cross-check the claim against the two files that actually encode it.
    stages = {s["id"]: s["order"] for s in _collision()["resolution_pipeline"]}
    if "active_evasion" in stages and "guard_intercept" in stages:
        if stages["active_evasion"] > stages["guard_intercept"]:
            errs.append("Rule 13: the collision pipeline resolves guard before evasion, which "
                        "contradicts outranks_guard here")
    punch = json.loads((REPO / "data" / "punch_model.json").read_text())
    rows = {r["class"]: r for r in punch["outcome_recovery"]["rows"]}
    if "dodged" in rows and "blocked" in rows:
        if rows["dodged"]["counter_window_ticks"] <= rows["blocked"]["counter_window_ticks"]:
            errs.append("Rule 13: the punch model does not reward a dodge above a block, so this "
                        "file's outranks_guard claim is unbacked")
    return errs


def check_evasion_moves(doc: dict) -> list:
    """Rule 22: evasions are moves, and an active window is frame-locked to the table."""
    moves, regions = _moves(), _regions()
    errs = []
    for ev in doc["evasions"]:
        m = moves.get(ev["move_id"])
        if m is None:
            errs.append(f"evasion '{ev['id']}' names move '{ev['move_id']}', absent from the table")
            continue
        if ev["kind"] == "active_window":
            if ev["active_ticks"] != m.get("active_frames"):
                errs.append(f"evasion '{ev['id']}' declares {ev['active_ticks']} active ticks; the "
                            f"move table authors {m.get('active_frames')} - an evasion window that "
                            f"drifts from its move is a window the collision model cannot trust")
            if not ev["vacates"]:
                errs.append(f"evasion '{ev['id']}' is an active-window evasion that vacates nothing")
        else:
            if ev["vacates"]:
                errs.append(f"positional answer '{ev['id']}' claims to vacate regions; it removes "
                            f"the fighter from reach rather than clearing a lane")
            if ev["active_ticks"] != 0:
                errs.append(f"positional answer '{ev['id']}' carries an active window")
        for r in ev["vacates"]:
            if r not in regions:
                errs.append(f"evasion '{ev['id']}' vacates unknown region '{r}'")
        if not ev["beaten_by"]:
            errs.append(f"Rule 4: evasion '{ev['id']}' has no answer - every defence must have one")
    return errs


def check_guard_integrity(doc: dict) -> list:
    """Rule 14 and Rule 4: a guard break is earned through varied pressure, never counted."""
    g = doc["guard_integrity"]
    errs = []
    if g["degrades_from_repetition_alone"]:
        errs.append("Rule 4: predictable single-action spam does not earn a guard break")
    if not g["degrades_from"]:
        errs.append("Rule 14: blocking must cost something or the guard is free")
    if "disabl" in g["opened_state"].lower() or "stun" in g["opened_state"].lower():
        errs.append("Rule 19: an opened guard reduces coverage; it does not disable the fighter or "
                    "eat their input")
    return errs


def check_matchup_reference(doc: dict) -> list:
    """One table, one home: this file must not restate the design doc's matchups."""
    ref = doc["authority"].get("matchup_reference", "")
    errs = []
    if "boxing_guard_matchups" not in ref:
        errs.append("the authoritative matchup reference must be named, so this file stays a "
                    "coverage model rather than becoming a third copy of the tables")
    if not (REPO / "docs" / "design" / "boxing_guard_matchups.md").exists():
        errs.append(f"matchup reference '{ref}' does not exist in the repository")
    return errs


def check_prohibitions(doc: dict) -> list:
    blob = " ".join(doc["prohibitions"]).lower()
    return [f"missing required prohibition covering '{p}'"
            for p in REQUIRED_PROHIBITIONS if p not in blob]


def check_invariants(doc: dict) -> list:
    present = {i["id"] for i in doc["invariants"]}
    return [f"missing required invariant '{r}'" for r in REQUIRED_INVARIANTS if r not in present]


ALL_CHECKS = [
    ("schema", check_schema),
    ("authority_rule13", check_authority),
    ("postures_rule4", check_postures),
    ("extent_agreement_d0010", check_extent_agreement),
    ("alignment_states_d0010", check_alignment_states),
    ("evasion_economy_rule13", check_evasion_economy),
    ("evasion_moves_rule22", check_evasion_moves),
    ("guard_integrity_rule14", check_guard_integrity),
    ("matchup_reference", check_matchup_reference),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:36 UTC | END ]
