# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | START ]
"""ROADMAP Phase 1A step 1 validator: structural laws of the combat-state definitions.

Enforces, against data/combat_states.json:
Rule 3 (score isolation of state inputs), Rule 5 (one unified machine set),
Rule 13 (commitment ordering, posture zero delay), Rule 14 (knockdown evidence,
condition-region references), Rule 16 (referee bounds), Rule 18 (provisioned
discipline), Rule 22 (counterplay from the first punch), and sandbox criterion
E.19 (tick-anchored trigger vocabulary).
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

REQUIRED_INVARIANTS = (
    "score_isolation_structural", "commitment_ordering", "counterplay_from_first_punch",
    "no_flat_knockout_roll", "posture_zero_delay", "tick_determinism", "chin_no_immunity",
    "crowd_exclusive_choice", "referee_bounded", "one_unified_machine",
)

CROWD_SLOTS = ("special_execution", "ultimate_execution", "full_crowd_trait_active")


def load() -> dict:
    return json.loads((REPO / "data" / "combat_states.json").read_text())


def _event_types() -> set:
    doc = json.loads((REPO / "schemas" / "fight_event.schema.json").read_text())
    return set(doc["properties"]["type"]["enum"])


def _region_keys() -> set:
    doc = json.loads((REPO / "data" / "condition_regions.json").read_text())
    return {r["key"] for r in doc["regions"]}


def _states(machine: dict) -> dict:
    return {s["id"]: s for s in machine["states"]}


def _expand_from(t: dict, states: dict) -> list:
    """'*' covers every non-terminal, non-provisioned state minus wildcard_excludes.
    Wildcards never implicitly touch provisioned architecture (Rule 18)."""
    if t["from"] == "*":
        excluded = set(t.get("wildcard_excludes", []))
        return [sid for sid, s in states.items()
                if not s.get("terminal") and not s.get("provisioned") and sid not in excluded]
    return [t["from"]]


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "combat_state_machine.schema.json")


def check_endpoints(doc: dict) -> list:
    errs = []
    for name in ("match_flow", "fighter_action"):
        m = doc["machines"][name]
        ids = set(_states(m))
        if m["initial"] not in ids:
            errs.append(f"{name}: initial state '{m['initial']}' is not defined")
        for t in m["transitions"]:
            if t["from"] != "*" and t["from"] not in ids:
                errs.append(f"{name}/{t['id']}: unknown from-state '{t['from']}'")
            if t["to"] not in ids:
                errs.append(f"{name}/{t['id']}: unknown to-state '{t['to']}'")
            for x in t.get("wildcard_excludes", []):
                if x not in ids:
                    errs.append(f"{name}/{t['id']}: wildcard_excludes names unknown state '{x}'")
    return errs


def check_reachability(doc: dict) -> list:
    errs = []
    for name in ("match_flow", "fighter_action"):
        m = doc["machines"][name]
        states = _states(m)
        reached = {m["initial"]}
        changed = True
        while changed:
            changed = False
            for t in m["transitions"]:
                if t["to"] in reached:
                    continue
                if any(src in reached for src in _expand_from(t, states)):
                    reached.add(t["to"])
                    changed = True
        for sid in states:
            if sid not in reached:
                errs.append(f"{name}: state '{sid}' is unreachable from '{m['initial']}'")
    return errs


def check_liveness(doc: dict) -> list:
    errs = []
    for name in ("match_flow", "fighter_action"):
        m = doc["machines"][name]
        states = _states(m)
        with_exit = set()
        for t in m["transitions"]:
            with_exit.update(_expand_from(t, states))
        for sid, s in states.items():
            if not s.get("terminal") and sid not in with_exit:
                errs.append(f"{name}: non-terminal state '{sid}' has no exit")
    return errs


def check_event_vocabulary(doc: dict) -> list:
    ev = _event_types()
    errs = []
    for name in ("match_flow", "fighter_action"):
        for t in doc["machines"][name]["transitions"]:
            for e in t.get("emits", []):
                if e not in ev:
                    errs.append(f"{name}/{t['id']}: emits unknown fight_event type '{e}'")
    return errs


def check_input_domains(doc: dict) -> list:
    allowed = set(doc["allowed_input_domains"])
    forbidden = set(doc["forbidden_input_domains"])
    errs = []
    overlap = allowed & forbidden
    if overlap:
        errs.append(f"Rule 3: domains listed as both allowed and forbidden: {sorted(overlap)}")
    for required in ("official_scorecards", "sealed_events"):
        if required not in forbidden:
            errs.append(f"Rule 3: forbidden_input_domains must name '{required}'")
    for name in ("match_flow", "fighter_action"):
        for t in doc["machines"][name]["transitions"]:
            for g in t.get("guard_inputs", []):
                if g in forbidden:
                    errs.append(f"Rule 3: {name}/{t['id']} reads forbidden domain '{g}'")
                elif g not in allowed:
                    errs.append(f"{name}/{t['id']}: undeclared input domain '{g}'")
    return errs


def check_counterplay(doc: dict) -> list:
    st = _states(doc["machines"]["fighter_action"])
    errs = []
    for phase in ("move_startup", "move_active", "move_recovery"):
        if phase not in st:
            errs.append(f"Rule 22: offensive commitment state '{phase}' is missing")
    startup = st.get("move_startup", {})
    if startup and not startup.get("counter_open"):
        errs.append("Rule 22: move_startup must be interceptable (counter_open)")
    rec = st.get("move_recovery", {})
    if rec and not rec.get("counter_open"):
        errs.append("Rule 22: move_recovery must be counter_open")
    if rec and rec.get("consequence_scaling") != "contact_class_commitment_tier":
        errs.append("Rule 13: move_recovery consequence must scale by contact_class_commitment_tier")
    return errs


def check_commitment_scaling(doc: dict) -> list:
    contact = json.loads((REPO / "data" / "contact_classes.json").read_text())
    errs = list(schema_check.check_contact_ordering(contact))
    present = {c["key"] for c in contact["classes"]}
    for k in ("clean", "solid", "grazed", "brushed", "blocked", "dodged", "whiffed"):
        if k not in present:
            errs.append(f"sandbox criterion A.5: contact class '{k}' missing from data/contact_classes.json")
    return errs


def check_condition_refs(doc: dict) -> list:
    keys = _region_keys()
    errs = []
    for name in ("match_flow", "fighter_action"):
        for s in doc["machines"][name]["states"]:
            for r in s.get("condition_refs", []):
                if r not in keys:
                    errs.append(f"Rule 14: {name}/{s['id']} references unknown condition region '{r}'")
    return errs


def check_knockdown_flow(doc: dict) -> list:
    errs = []
    for t in doc["machines"]["fighter_action"]["transitions"]:
        if t["from"] == "knocked_down" and t["to"] not in ("rising", "stopped"):
            errs.append(f"Rule 14/16: knocked_down may exit only to rising or stopped, not '{t['to']}' ({t['id']})")
        if t["from"] == "rising" and t["to"] == "idle" and t["trigger_kind"] != "count_clock":
            errs.append(f"Rule 16: rising resolves on the authoritative count clock, not '{t['trigger_kind']}' ({t['id']})")
        if t["to"] == "knocked_down" and t["trigger_kind"] not in ("condition_threshold", "incoming_contact"):
            errs.append(f"Rule 14: knockdown requires an observable evidence trigger, not '{t['trigger_kind']}' ({t['id']})")
    return errs


def check_referee_bounds(doc: dict) -> list:
    banned = {"condition_change", "stamina_change", "balance_change", "composure_change", "crowd_gain"}
    errs = []
    for name in ("match_flow", "fighter_action"):
        for t in doc["machines"][name]["transitions"]:
            if t["trigger_kind"] == "referee" and set(t.get("emits", [])) & banned:
                errs.append(f"Rule 16: referee transition {name}/{t['id']} may not alter combat truth "
                            f"(emits {sorted(set(t['emits']) & banned)})")
    return errs


def check_posture(doc: dict) -> list:
    errs = []
    for mode in doc["machines"]["posture_continuum"]["modes"]:
        if mode.get("transition_delay_frames") != 0:
            errs.append(f"Rule 13: posture mode '{mode['id']}' must have zero transition delay")
    return errs


def check_provisioned(doc: dict) -> list:
    st = _states(doc["machines"]["fighter_action"])
    errs = []
    for t in doc["machines"]["fighter_action"]["transitions"]:
        endpoints = [t["to"]] + ([t["from"]] if t["from"] != "*" else [])
        touches = any(st.get(x, {}).get("provisioned") for x in endpoints)
        if touches and not t.get("provisioned"):
            errs.append(f"Rule 18: transition '{t['id']}' touches a provisioned state but is not marked provisioned")
        if t.get("provisioned") and t["trigger_kind"] != "provisioned":
            errs.append(f"Rule 18: provisioned transition '{t['id']}' must keep trigger_kind 'provisioned' until implemented")
    for sid in CROWD_SLOTS:
        if sid not in st:
            errs.append(f"sandbox criterion D.18: architecture slot '{sid}' is missing")
        elif not st[sid].get("provisioned"):
            errs.append(f"Rule 18: '{sid}' must stay provisioned until ROADMAP step 12")
    return errs


def check_machine_set(doc: dict) -> list:
    keys = set(doc["machines"].keys())
    expected = {"match_flow", "fighter_action", "posture_continuum"}
    if keys != expected:
        return [f"Rule 5: exactly one unified machine set is required; found {sorted(keys)}"]
    return []


def check_invariants(doc: dict) -> list:
    present = {i["id"] for i in doc["invariants"]}
    return [f"missing required invariant '{r}'" for r in REQUIRED_INVARIANTS if r not in present]


ALL_CHECKS = [
    ("schema", check_schema),
    ("endpoints", check_endpoints),
    ("reachability", check_reachability),
    ("liveness", check_liveness),
    ("event_vocabulary", check_event_vocabulary),
    ("input_domains_rule3", check_input_domains),
    ("counterplay_rule22", check_counterplay),
    ("commitment_rule13", check_commitment_scaling),
    ("condition_refs_rule14", check_condition_refs),
    ("knockdown_flow_rule14", check_knockdown_flow),
    ("referee_bounds_rule16", check_referee_bounds),
    ("posture_rule13", check_posture),
    ("provisioned_rule18", check_provisioned),
    ("machine_set_rule5", check_machine_set),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | END ]
