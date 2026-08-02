# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | START ]
"""ROADMAP Phase 1A step 2 validator: movement, facing and range-band geometry laws.

Enforces, against data/movement_model.json:
Rule 11 (reach-relative range), Rule 13 (band contiguity and hysteresis, compression
law, explicit accel/decel, displacement caps, no overlap, anti-cheat vocabulary),
Rule 15 (exact stance mirroring), plus cross-file locks to combat_states posture
modes and allowed input domains, and the fight_event vocabulary.
"""
from __future__ import annotations
import json
from pathlib import Path

from . import combat_states, schema_check

REPO = Path(__file__).resolve().parents[2]

BAND_ORDER = ("clinch", "inside", "mid", "outside", "out_of_range")

FORBIDDEN_KEYS = {"snap_to_range", "magnetic_correction", "auto_face", "teleport", "range_assist"}

REQUIRED_INVARIANTS = (
    "feet_establish_position", "no_magnetic_correction", "no_overlap", "no_invisible_lunges",
    "threat_responsive_compression", "explicit_accel_decel", "reach_relative_range",
    "stance_mirror_exact",
)


def load() -> dict:
    return json.loads((REPO / "data" / "movement_model.json").read_text())


def _modes(doc: dict) -> dict:
    return {m["posture_mode"]: m for m in doc["locomotion"]["modes"]}


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "movement_model.schema.json")


def check_bands(doc: dict) -> list:
    rb = doc["range_bands"]
    bands = rb["bands"]
    errs = []
    keys = tuple(b["key"] for b in bands)
    if keys != BAND_ORDER:
        errs.append(f"Rule 13: bands must appear in canonical order {BAND_ORDER}, found {keys}")
        return errs
    if bands[0]["min_ru"] != 0:
        errs.append("Rule 13: clinch band must start at 0")
    if bands[-1]["max_ru"] is not None:
        errs.append("Rule 13: out_of_range must be unbounded (max_ru null)")
    widths = []
    for prev, cur in zip(bands, bands[1:]):
        if prev["max_ru"] != cur["min_ru"]:
            errs.append(f"Rule 13: bands '{prev['key']}' and '{cur['key']}' must be contiguous "
                        f"({prev['max_ru']} != {cur['min_ru']})")
    for b in bands:
        if b["max_ru"] is not None:
            if b["max_ru"] <= b["min_ru"]:
                errs.append(f"Rule 13: band '{b['key']}' has non-positive width")
            else:
                widths.append(b["max_ru"] - b["min_ru"])
    h = rb["hysteresis_ru"]
    if widths and h >= min(widths):
        errs.append(f"Rule 13: hysteresis {h} must be smaller than the narrowest band width {min(widths)}")
    if h <= 0:
        errs.append("Rule 13: hysteresis must be positive (band flicker is magnetic correction's cousin)")
    return errs


def check_posture_lock(doc: dict) -> list:
    combat = combat_states.load()
    combat_ids = {m["id"] for m in combat["machines"]["posture_continuum"]["modes"]}
    move_ids = set(_modes(doc))
    errs = []
    if move_ids != combat_ids:
        errs.append(f"cross-file lock: movement modes {sorted(move_ids)} must equal "
                    f"combat_states posture modes {sorted(combat_ids)}")
    return errs


def check_compression_law(doc: dict) -> list:
    modes = _modes(doc)
    errs = []
    free = modes.get("free_navigation")
    boxing = modes.get("boxing_steps")
    planted = modes.get("planted")
    if free and boxing and free["stride_length_ru"] <= boxing["stride_length_ru"]:
        errs.append("Rule 13: free_navigation stride must exceed boxing_steps stride "
                    "(threat-responsive compression must compress)")
    if planted and planted["stride_length_ru"] != 0:
        errs.append("Rule 13: planted stride must be zero (planted means planted)")
    for mid, m in modes.items():
        if m["stride_length_ru"] > 0:
            if m["acceleration_frames"] < 1 or m["deceleration_frames"] < 1:
                errs.append(f"Rule 13: mobile mode '{mid}' must declare explicit acceleration "
                            f"and deceleration frames (no ice skating)")
    return errs


def check_displacement(doc: dict) -> list:
    modes = _modes(doc)
    cap = doc["locomotion"]["max_frame_displacement_ru"]
    errs = []
    free = modes.get("free_navigation")
    if free and cap >= free["stride_length_ru"]:
        errs.append(f"Rule 13: displacement cap {cap} must stay below the longest stride "
                    f"{free['stride_length_ru']} (no invisible lunges)")
    sep = doc["separation"]["min_center_distance_ru"]
    clinch_max = doc["range_bands"]["bands"][0]["max_ru"]
    if clinch_max is not None and sep >= clinch_max:
        errs.append(f"Rule 13: min separation {sep} must stay below the clinch ceiling "
                    f"{clinch_max}, or the clinch band is unreachable")
    return errs


def check_facing(doc: dict) -> list:
    facing = doc["facing"]
    errs = []
    total = sum(2 * a["half_width_deg"] for a in facing["arcs"])
    if total != 360:
        errs.append(f"facing arcs must tile exactly 360 degrees, found {total}")
    fronts = [a for a in facing["arcs"] if a["key"] == "front"]
    if not fronts:
        errs.append("facing must define a 'front' arc")
    else:
        if fronts[0]["center_deg"] != 0:
            errs.append("front arc must center on the opponent (0 degrees)")
    for a in facing["arcs"]:
        if a["punches_permitted"] and a["key"] != "front":
            errs.append(f"Rule 13: punches are permitted only from the front arc, not '{a['key']}'")
    if facing["back_exposed_threshold_deg"] < (fronts[0]["half_width_deg"] if fronts else 0):
        errs.append("back_exposed threshold cannot sit inside the front arc")
    return errs


def _walk_keys(node, found):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in FORBIDDEN_KEYS:
                found.append(k)
            _walk_keys(v, found)
    elif isinstance(node, list):
        for v in node:
            _walk_keys(v, found)


def check_anti_cheat(doc: dict) -> list:
    found = []
    _walk_keys(doc, found)
    return [f"Rule 13: forbidden movement-assist key '{k}' has no place in this model" for k in found]


def check_threat_compression(doc: dict) -> list:
    tc = doc["locomotion"]["threat_compression"]
    band_keys = {b["key"] for b in doc["range_bands"]["bands"]}
    mode_ids = set(_modes(doc))
    combat = combat_states.load()
    allowed = set(combat["allowed_input_domains"])
    errs = []
    for group in ("threat_bands", "release_bands"):
        for b in tc[group]:
            if b not in band_keys:
                errs.append(f"threat_compression.{group}: unknown band '{b}'")
    if tc["compressed_mode"] not in mode_ids:
        errs.append(f"threat_compression: unknown compressed_mode '{tc['compressed_mode']}'")
    for i in tc["observable_inputs"]:
        if i not in allowed:
            errs.append(f"Rule 3: threat compression may read only allowed observable domains, not '{i}'")
    return errs


def check_events(doc: dict) -> list:
    ev = set(json.loads((REPO / "schemas" / "fight_event.schema.json").read_text())
             ["properties"]["type"]["enum"])
    errs = []
    for e in list(doc["emits"]) + list(doc["range_bands"]["band_change_emits"]):
        if e not in ev:
            errs.append(f"emits unknown fight_event type '{e}'")
    return errs


def check_invariants(doc: dict) -> list:
    present = {i["id"] for i in doc["invariants"]}
    return [f"missing required invariant '{r}'" for r in REQUIRED_INVARIANTS if r not in present]


ALL_CHECKS = [
    ("schema", check_schema),
    ("bands_rule13", check_bands),
    ("posture_lock", check_posture_lock),
    ("compression_rule13", check_compression_law),
    ("displacement_rule13", check_displacement),
    ("facing_rule15", check_facing),
    ("anti_cheat_rule13", check_anti_cheat),
    ("threat_compression", check_threat_compression),
    ("event_vocabulary", check_events),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | END ]
