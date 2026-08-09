# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | START ]
"""ROADMAP Phase 1A step 3 validator: camera behaviour laws.

Enforces, against data/camera_model.json:
Rule 3 (the camera is named in the score-isolation consumer list), Rules 8/16/17
(officiating framing outranks spectacle), Rule 13 (band lock to the movement model;
presentation may not contradict contact truth), Rule 19 and criterion F.24
(readability guards), criterion A.1 (the framing selector is total and inspectable),
and criteria E.19/E.20 (tick-anchored, camera outside the determinism loop but a pure
function of the log).
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

from . import combat_states, movement, schema_check

REPO = Path(__file__).resolve().parents[2]

# Modes that resolve officiating or safety. None of these may be outranked by spectacle.
OFFICIATING = ("stoppage_hold", "knockdown_read", "count_segment", "doctor_check_segment")
SPECTACLE = ("showmanship_flourish",)

REQUIRED_INVARIANTS = (
    "camera_never_writes", "camera_score_isolated", "framing_selector_total",
    "officiating_outranks_spectacle", "exchange_readability", "band_lock",
    "tick_anchored", "replay_pure",
)

# Substrings that must appear somewhere in the prohibition list. Kept as intent
# fragments rather than exact sentences so wording can improve without silently
# dropping a law.
REQUIRED_PROHIBITIONS = ("scorecard", "simulation state", "clean landed", "wall-clock")


def load() -> dict:
    return json.loads((REPO / "data" / "camera_model.json").read_text())


def _modes(doc: dict) -> dict:
    return {m["id"]: m for m in doc["framing_modes"]}


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "camera_model.schema.json")


def check_authority(doc: dict) -> list:
    a = doc["authority"]
    errs = []
    if a["writes_simulation_state"] is not False:
        errs.append("Criterion E.19: the camera may never write simulation state")
    if a["participates_in_determinism_hash"] is not False:
        errs.append("Criterion E.20: camera output must stay outside the authoritative log hash")
    if a["derivation"] != "pure_function_of_observable_event_log_and_tick":
        errs.append("Criterion E.20: framing must be a pure function of the observable log and tick")
    return errs


def check_input_domains(doc: dict) -> list:
    combat = combat_states.load()
    allowed = set(combat["allowed_input_domains"])
    forbidden = set(combat["forbidden_input_domains"])
    errs = []
    for i in doc["observable_inputs"]:
        if i in forbidden:
            errs.append(f"Rule 3: camera reads forbidden domain '{i}'")
        elif i not in allowed:
            errs.append(f"camera declares undeclared input domain '{i}'")
    return errs


def check_priority_order(doc: dict) -> list:
    modes = doc["framing_modes"]
    errs = []
    prios = [m["priority"] for m in modes]
    if len(set(prios)) != len(prios):
        dupes = sorted({p for p in prios if prios.count(p) > 1})
        errs.append(f"Criterion A.1: framing priorities must be a strict total order; duplicates {dupes}")
    defaults = [m for m in modes if m["trigger"]["kind"] == "default"]
    if len(defaults) != 1:
        errs.append(f"Criterion A.1: exactly one default mode is required, found {len(defaults)}")
    elif defaults[0]["priority"] != min(prios):
        errs.append("Criterion A.1: the default mode must hold the lowest priority (it is the fallback)")
    return errs


def check_officiating_precedence(doc: dict) -> list:
    modes = _modes(doc)
    errs = []
    for name in OFFICIATING + SPECTACLE:
        if name not in modes:
            errs.append(f"Rules 8/16/17: required framing mode '{name}' is missing")
    if errs:
        return errs
    worst_officiating = min(modes[n]["priority"] for n in OFFICIATING)
    for s in SPECTACLE:
        if modes[s]["priority"] >= worst_officiating:
            errs.append(f"Rules 8/16/17: spectacle mode '{s}' outranks officiating framing "
                        f"({modes[s]['priority']} >= {worst_officiating})")
        if modes[s]["max_hold_ticks"] is None:
            errs.append(f"Rule 19: spectacle mode '{s}' must carry a tick cap; the joke may not run forever")
    return errs


def check_band_lock(doc: dict) -> list:
    mv = movement.load()
    bands = {b["key"] for b in mv["range_bands"]["bands"]}
    errs = []
    covered = set()
    for m in doc["framing_modes"]:
        for b in m["distance_bands"]:
            if b not in bands:
                errs.append(f"Rule 13: mode '{m['id']}' references unknown range band '{b}'")
            covered.add(b)
        if m["trigger"]["kind"] == "range_band":
            trig = m["trigger"].get("bands") or []
            if not trig:
                errs.append(f"mode '{m['id']}' triggers on range_band but names no bands")
            for b in trig:
                if b not in bands:
                    errs.append(f"Rule 13: mode '{m['id']}' triggers on unknown range band '{b}'")
                covered.add(b)
            if sorted(trig) != sorted(m["distance_bands"]):
                errs.append(f"mode '{m['id']}': trigger bands and distance_bands must agree")
    missing = bands - covered
    if missing:
        errs.append(f"Criterion A.1: no framing serves range band(s) {sorted(missing)}")
    return errs


def check_event_vocabulary(doc: dict) -> list:
    ev = set(json.loads((REPO / "schemas" / "fight_event.schema.json").read_text())
             ["properties"]["type"]["enum"])
    errs = []
    for m in doc["framing_modes"]:
        if m["trigger"]["kind"] != "fight_event":
            continue
        events = m["trigger"].get("events") or []
        if not events:
            errs.append(f"mode '{m['id']}' triggers on fight_event but names no events")
        for e in events:
            if e not in ev:
                errs.append(f"mode '{m['id']}' triggers on unknown fight_event type '{e}'")
    return errs


def check_readability(doc: dict) -> list:
    r = doc["readability"]
    errs = []
    if r["contact_window_cut_prohibited"] is not True:
        errs.append("Rule 19: cutting inside a contact window must stay prohibited")
    if r["min_ticks_between_cuts"] < 1:
        errs.append("Rule 19: a cut cooldown is required")
    if r["settle_ticks_after_cut"] >= r["min_ticks_between_cuts"]:
        errs.append("Rule 19: settle time must fit inside the cut cooldown, or framing never settles")
    # Anything that can be live during a round has to keep both fighters readable.
    for m in doc["framing_modes"]:
        t = m["trigger"]
        live = (t["kind"] == "range_band"
                or t["kind"] == "default"
                or (t["kind"] == "clock_segment" and t.get("clock_segment") == "round"))
        if live and not m["both_fighters_framed"]:
            errs.append(f"Criterion F.24: mode '{m['id']}' can be live during an exchange "
                        f"but does not keep both fighters framed")
    for m in doc["framing_modes"]:
        h = m["max_hold_ticks"]
        if h is not None and h < 1:
            errs.append(f"Criterion E.19: mode '{m['id']}' has a non-positive tick cap")
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
    ("authority_e19", check_authority),
    ("input_domains_rule3", check_input_domains),
    ("priority_order_a1", check_priority_order),
    ("officiating_precedence", check_officiating_precedence),
    ("band_lock_rule13", check_band_lock),
    ("event_vocabulary", check_event_vocabulary),
    ("readability_f24", check_readability),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | END ]
