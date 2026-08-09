# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:00 UTC | START ]
"""ROADMAP Phase 1A step 10 validator: logging and replay guarantees.

Two contracts live in data/replay_model.json and are deliberately kept apart:

  resimulation - the same seed, initial state and authored data reproduce a
                 byte-identical authoritative event log.
  replay       - a SAVED log reproduces the recorded presentation without
                 re-running any uncertain decision.

Conflating them is the standard way a replay system starts quietly re-deciding
fights: it re-runs the CPU, gets a different answer on a different build, and the
"replay" diverges from what the spectator watched. So `reruns_cpu_decisions`,
`reruns_judging` and `reruns_rng` are schema constants and checked here too.

Also enforces the gate's readability item (major events carry causal
explanation), Rule 3 (sealed judge events stay sealed through replay) and
Rule 22 (this file and fight_event.schema.json share one vocabulary).
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

# Systems that may be excluded from the determinism hash only because they are
# forbidden from writing simulation state in the first place.
NON_AUTHORITATIVE = {"camera", "presentation", "audio", "commentary", "crowd_render", "ui"}

REQUIRED_PROHIBITIONS = ("re-run cpu decisions", "wall-clock", "determinism hash",
                         "sealed judge event", "later sequence number")

REQUIRED_INVARIANTS = (
    "resim_is_byte_identical", "presentation_excluded", "replay_never_redecides",
    "sealed_stays_sealed_in_replay", "log_is_ordered", "causality_points_backward",
    "major_events_are_explained", "event_vocabulary_agrees",
)


def load() -> dict:
    return json.loads((REPO / "data" / "replay_model.json").read_text())


def _event_types() -> set:
    doc = json.loads((REPO / "schemas" / "fight_event.schema.json").read_text())
    return set(doc["properties"]["type"]["enum"])


def _sealed_types() -> list:
    doc = json.loads((REPO / "data" / "score_isolation_contract.json").read_text())
    return doc["sealed_symbols"].get("event_types", [])


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "replay_model.schema.json")


def check_resimulation(doc: dict) -> list:
    r = doc["resimulation"]
    errs = []
    if not r["byte_identical_required"]:
        errs.append("Criterion E.19: resimulation must reproduce the log byte-identically, or the "
                    "determinism probes have been testing a weaker claim than the canon makes")
    if r["wall_clock_may_affect_outcome"]:
        errs.append("Criterion E.19: wall-clock time may not reach the authoritative log")
    for need in ("seed", "authoritative_initial_state"):
        if need not in r["inputs"]:
            errs.append(f"resimulation must take '{need}' as an input")
    for ex in r["excluded_from_hash"]:
        if ex not in NON_AUTHORITATIVE:
            errs.append(f"'{ex}' is excluded from the determinism hash but is not a known "
                        f"non-authoritative system - excluding a system that writes simulation "
                        f"state is how a hash stops meaning anything")
    if "camera" not in r["excluded_from_hash"]:
        errs.append("the camera must be excluded from the hash; camera_model.json already declares "
                    "it writes no simulation state")
    return errs


def check_replay(doc: dict) -> list:
    """A replay re-presents. The moment it re-decides, it is a different fight."""
    p = doc["replay"]
    errs = []
    for k, what in (("reruns_cpu_decisions", "CPU decisions"),
                    ("reruns_judging", "judging"),
                    ("reruns_rng", "the RNG")):
        if p[k]:
            errs.append(f"Rule 13: replay may not re-run {what} - a replay that re-decides is not "
                        f"showing what happened, it is holding a second fight")
    if p["source"] != "saved_event_log":
        errs.append("replay must read the saved event log")
    return errs


def check_log_requirements(doc: dict) -> list:
    """Ordering, one clock, and the gate's readability item."""
    lr = doc["log_requirements"]
    known = _event_types()
    errs = []
    for k in ("monotonic_seq", "monotonic_tick", "every_event_carries_clock",
              "explains_references_are_backward", "sealed_events_marked"):
        if not lr[k]:
            errs.append(f"Criterion E.19: '{k}' must hold for the log to be authoritative")
    for t in lr["required_explained_types"]:
        if t not in known:
            errs.append(f"required-explained type '{t}' is not a fight_event type")
    for need in ("knockdown", "stoppage"):
        if need not in lr["required_explained_types"]:
            errs.append(f"ROADMAP gate: '{need}' must carry causal explanation - the gate asks that "
                        f"the log explain major combat and judging events, and a stoppage nobody "
                        f"can trace back is exactly what it is guarding against")
    return errs


def check_visibility(doc: dict) -> list:
    """Rule 3 survives replay: sealed is sealed until the archival reveal."""
    known = _event_types()
    sealed = _sealed_types()
    errs = []
    declared = {v["event_type"]: v for v in doc["visibility_rules"]}
    for t, v in declared.items():
        if t not in known:
            errs.append(f"visibility rule names unknown event type '{t}'")
    for s in sealed:
        if s not in declared:
            errs.append(f"Rule 3: sealed event '{s}' has no visibility rule here")
        elif declared[s]["visibility"] != "sealed":
            errs.append(f"Rule 3 VIOLATION: '{s}' is sealed by the score-isolation contract but "
                        f"declared '{declared[s]['visibility']}' here")
    for t, v in declared.items():
        if v["visibility"] == "sealed" and not v["revealed_at"]:
            errs.append(f"sealed event '{t}' declares no reveal point")
    during = doc["replay"].get("sealed_events_visible_during", [])
    for phase in during:
        if phase != "archival_reveal":
            errs.append(f"Rule 3: sealed events may not become visible during '{phase}' - the cards "
                        f"stay sealed through the fight and the immediate result flow")
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
    ("resimulation_e19", check_resimulation),
    ("replay_rule13", check_replay),
    ("log_requirements_e19", check_log_requirements),
    ("visibility_rule3", check_visibility),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:00 UTC | END ]
