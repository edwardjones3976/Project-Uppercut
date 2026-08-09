# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | START ]
"""ROADMAP Phase 1A step 2 validator: movement, facing and range-band geometry laws.

Enforces, against data/movement_model.json:
Rule 11 (reach-relative range), Rule 13 (band contiguity and hysteresis, compression
law, explicit accel/decel, displacement caps, no overlap, anti-cheat vocabulary),
Rule 15 (exact stance mirroring), plus cross-file locks to combat_states posture
modes and allowed input domains, and the fight_event vocabulary.
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

from . import combat_states, schema_check

REPO = Path(__file__).resolve().parents[2]

BAND_ORDER = ("clinch", "inside", "mid", "outside", "out_of_range")

FORBIDDEN_KEYS = {"snap_to_range", "magnetic_correction", "auto_face", "teleport", "range_assist"}

REQUIRED_INVARIANTS = (
    "feet_establish_position", "no_magnetic_correction", "no_overlap", "no_invisible_lunges",
    "threat_responsive_compression", "explicit_accel_decel", "reach_relative_range",
    "stance_mirror_exact",
    # Added 2026-08-03 by Claude Opus 5 with the ring-track work: an invariant the
    # data declares but nothing requires can be dropped in a later edit without
    # anything noticing, which is exactly how the running gap got in.
    "retreat_slower_than_advance", "separation_is_ring_bounded",
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


def check_step_cost_authority(doc: dict) -> list:
    """Decision 0014 (gate G1): one authority for what movement costs.

    `stamina_cost_per_ru` is the authority; the move table's ordinary step
    entries are a derived echo of it. This recomputes the echo and fails on
    drift, because the defect this ruling closed was exactly two authorities
    disagreeing by 4.55x with nothing checking either.
    """
    moves_path = Path(__file__).resolve().parents[2] / "data" / "moves" / \
        "generic_sandbox_moves.json"
    if not moves_path.exists():
        return []
    modes = _modes(doc)
    step = modes.get("boxing_steps")
    if step is None:
        return ["Decision 0014: no boxing_steps mode to price movement from"]
    per_ru = step["stamina_cost_per_ru"]
    stride = step["stride_length_ru"]
    d = doc["locomotion"]["directional"]
    expect = {"step_in": d["advance_stride_multiplier"],
              "step_out": d["retreat_stride_multiplier"],
              "step_lateral": d["lateral_stride_multiplier"]}
    table = {m["id"]: m for m in
             json.loads(moves_path.read_text(encoding="utf-8"))["moves"]}
    errs = []
    for mid, mult in expect.items():
        m = table.get(mid)
        if m is None:
            errs.append(f"Decision 0014: ordinary step {mid} is missing from the "
                        f"move table")
            continue
        if m.get("cost_model") != "displacement":
            errs.append(f"Decision 0014: {mid} must declare cost_model "
                        f"'displacement'; it declares {m.get('cost_model')!r}")
        want = round(stride * mult * per_ru, 6)
        if round(float(m["stamina_cost"]), 6) != want:
            errs.append(f"Decision 0014: {mid} echoes stamina_cost "
                        f"{m['stamina_cost']} but displacement pricing gives "
                        f"{want} ({stride} ru x {mult} x {per_ru}/ru). The echo "
                        f"drifted from its authority - fix the echo, not the rule")
    for mid, m in table.items():
        if m.get("category") == "step" and m.get("cost_model") == "flat":
            errs.append(f"Decision 0014: {mid} is categorised as an ordinary step "
                        f"but priced flat; a flat fee belongs to a separately "
                        f"named explosive action")
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


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:52 UTC | START ]
# Added inside the original author's file; their tags above and below are theirs
# and are left exactly as written.
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 19:20 UTC | START edit: Director correction ]
def check_defensive_purity_is_not_penalised(doc: dict) -> list:
    """Nothing may charge a fighter for hitting without being hit.

    DIRECTOR CORRECTION, 2026-08-08. There is no anti-running rule and there
    never was one; the phrase was invented in this repository's comments and
    spread to six files. What Rule 4 names is an ABUSE - neither hitting nor
    being hit, for long periods - and what canon has is a RING that ends.

    Hitting without being hit is the opposite of that abuse. "Swim without
    getting wet." It is the most admired thing in the sport and the model may
    never make it expensive.

    The concrete failure this guards against is the easy fix somebody will
    eventually propose: tax movement, or tax the fighter who is not being hit,
    and call it anti-running. Every clause below is a place that fix would land.
    """
    errs = []
    loco = doc["locomotion"]
    d = loco["directional"]
    track = doc["ring"]["track"]

    # Circling off the ropes is the boxing answer to being backed up, and canon
    # says so in its own notes. If lateral is ever scaled at the ropes, a
    # cornered fighter is being charged for the correct response.
    if track.get("rope_lateral_multiplier") != 1.0:
        errs.append(
            "rope_lateral_multiplier is %r, not 1.0 - circling off the ropes is "
            "being taxed, which charges a fighter for the one answer canon says "
            "remains open to him" % (track.get("rope_lateral_multiplier"),))

    # The ring is a bound on RETREAT IN A STRAIGHT LINE ONTO THE ROPES, and
    # nothing else. In open ring a retreating step must still buy ground, or the
    # out-boxer has been deleted rather than answered.
    if d["retreat_stride_multiplier"] <= 0:
        errs.append(
            "retreat covers no ground at all, so a fighter cannot box on the "
            "back foot - that answers non-engagement by removing a legitimate "
            "style rather than by letting the ring close")

    # Lateral must remain a real option, not a token one.
    if d["lateral_stride_multiplier"] <= 0:
        errs.append("lateral movement covers no ground, so there is no circling "
                    "and the ropes become a trap rather than a bound")

    # The tell that somebody has built the thing this check exists to stop: a
    # movement or stamina term keyed on output, on being hit, or on not being
    # hit. Movement is priced by DISTANCE (Decision 0014) and by nothing else.
    #
    # THE FIRST VERSION OF THIS SCAN FAILED ON ARRIVAL, and correctly. It read
    # the whole block as text and tripped on the word "engagement" inside a
    # `$comment` explaining that the reference model resolves engagement along
    # one axis - prose, not a term. A test written too broadly tempts you to
    # widen its exemption; the right move is to narrow the claim. So it reads
    # KEY NAMES only. A penalty has to be a field before it can be a penalty.
    forbidden = ("punches_landed", "punches_thrown", "output", "engagement",
                 "inactivity", "passivity", "damage_taken", "unhit",
                 "not_hit", "avoidance", "evasion_penalty")

    def key_names(node, out):
        if isinstance(node, dict):
            for k, v in node.items():
                out.add(str(k).lower())
                key_names(v, out)
        elif isinstance(node, list):
            for v in node:
                key_names(v, out)
        return out

    names = key_names(loco, set()) | key_names(track, set())
    blob = " ".join(n for n in names if not n.startswith("$")
                    and not n.endswith(("note", "notes", "comment")))
    for token in forbidden:
        if token in blob:
            errs.append(
                "the movement model references %r. Movement is priced by "
                "distance travelled and by nothing else; a movement or stamina "
                "term keyed on output or on being hit would charge a fighter "
                "for defensive success. Non-engagement is answered by the "
                "scorecard, not by the locomotion table." % token)
    return errs
# [ ... | 2026-08-08 19:20 UTC | END edit ]


def check_directional_footwork(doc: dict) -> list:
    """Rule 4: excessive running must lose to boxing, not to a prohibition.

    The mechanism is the stride asymmetry, so the ordering is load-bearing: if
    retreat ever covers as much ground as advance, a pressure fighter can never
    close and running stops being a losing strategy - it becomes an unanswerable
    one. Checked here rather than trusted to stay sorted by hand.
    """
    d = doc["locomotion"]["directional"]
    errs = []
    if d["retreat_stride_multiplier"] >= d["advance_stride_multiplier"]:
        errs.append("retreat covers at least as much ground as advance - pressure could never "
                    "close, and Rule 4's 'excessive running' would be unanswerable rather than "
                    "unprofitable")
    if d["lateral_stride_multiplier"] > d["advance_stride_multiplier"]:
        errs.append("circling outruns advancing - lateral movement would dominate both other "
                    "directions")
    if d["exhausted_stride_multiplier"] >= 1.0:
        errs.append("exhaustion does not shorten the stride, so stamina buys no ground and the "
                    "pool has no positional meaning")
    if set(d["exhausted_applies_to"]) != {"advance", "retreat", "lateral"}:
        errs.append("exhaustion is applied to some directions and not others - that is a penalty "
                    "aimed at a playstyle, which Rule 4 forbids; being out of gas slows everything")
    return errs


def check_ring_track(doc: dict) -> list:
    """Rule 13 / Rule 4: the ring bounds separation, and it does so without ever
    taking movement away."""
    t = doc["ring"]["track"]
    ring, su = doc["ring"], doc["spatial_units"]
    errs = []
    expected = ring["side_m"] / su["reference_reach_span_m"]
    if abs(t["axis_length_ru"] - expected) > 0.01:
        errs.append(f"axis_length_ru {t['axis_length_ru']} does not follow from side_m "
                    f"{ring['side_m']} and reference reach {su['reference_reach_span_m']} "
                    f"(expected {expected:.2f}) - two coordinate systems by another name")
    if abs(t["back_to_ropes_ru"] - ring["rope_proximity_m"] / su["reference_reach_span_m"]) > 0.01:
        errs.append("back_to_ropes_ru does not follow from rope_proximity_m")
    if abs(t["cornered_ru"] - ring["corner_proximity_m"] / su["reference_reach_span_m"]) > 0.01:
        errs.append("cornered_ru does not follow from corner_proximity_m")
    if t["cornered_ru"] <= t["back_to_ropes_ru"]:
        errs.append("the corner is not deeper than the ropes - cornering would be indistinguishable "
                    "from having your back to a rope")
    if t["rope_lateral_multiplier"] != 1.0:
        errs.append("lateral movement is reduced on the ropes - the ropes may end free retreat, "
                    "never the ability to circle off them (Rule 4)")
    # The bound must actually bind: the widest band must fit inside the ring, or
    # the ropes would never be reached and the mechanism would be inert.
    widest = max(b["min_ru"] for b in doc["range_bands"]["bands"])
    if widest >= t["axis_length_ru"]:
        errs.append("the ring is not wider than the outermost band boundary - fighters would be "
                    "on the ropes permanently and the bound would be indistinguishable from a wall")
    return errs
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:52 UTC | END ]


ALL_CHECKS = [
    ("schema", check_schema),
    ("bands_rule13", check_bands),
    ("posture_lock", check_posture_lock),
    ("compression_rule13", check_compression_law),
    ("displacement_rule13", check_displacement),
    ("step_cost_authority_0014", check_step_cost_authority),
    ("facing_rule15", check_facing),
    ("anti_cheat_rule13", check_anti_cheat),
    ("threat_compression", check_threat_compression),
    ("directional_footwork_rule4", check_directional_footwork),
    ("defensive purity is not penalised",
     check_defensive_purity_is_not_penalised),
    ("ring_track_rule13", check_ring_track),
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
