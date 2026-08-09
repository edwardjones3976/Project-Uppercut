# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | START ]
"""ROADMAP Phase 1A step 5 validator: collision truth laws.

Enforces, against data/collision_model.json:
Rule 13 (a visible miss is never a landed class; guard is physical; no magnetic
correction or tunnelling), Rule 14 (per-region hurtboxes, guard costs something,
bounded closing velocity), Rule 22 (the move table and the collision model agree),
criterion A.5 (all seven contact classes, pipeline total, quality bands tile),
and criterion E.19 (swept, snapshotted, fixed-order resolution).
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

SEVEN = ("clean", "solid", "grazed", "brushed", "blocked", "dodged", "whiffed")
LANDED = ("brushed", "grazed", "solid", "clean")   # ascending delivered force

# Condition regions that are physically strikeable. The remainder of
# condition_regions.json are runtime pools and attribute-governed states, which
# are not hurtboxes by nature.
PHYSICAL_REGIONS = ("head", "jaw_chin", "eye_left", "eye_right",
                    "torso_upper", "torso_lower", "arm_left", "arm_right")

FORBIDDEN_KEYS = {"snap_to_target", "hitbox_inflation", "magnetic_correction",
                  "auto_aim", "assist_radius", "knockout_roll"}

REQUIRED_PROHIBITIONS = ("visible miss", "magnetic range correction", "tunnel",
                         "generic health volume", "unblockable", "flat random knockout",
                         "coverage extents")

REQUIRED_INVARIANTS = (
    "pipeline_total", "no_miss_as_hit", "region_lock", "guard_is_physical",
    "guard_costs_something", "commitment_order_holds", "quality_total",
    "move_table_lock", "swept_and_ordered", "closing_velocity_bounded",
    "posture_is_geometry",
)


def load() -> dict:
    return json.loads((REPO / "data" / "collision_model.json").read_text())


def _regions() -> set:
    doc = json.loads((REPO / "data" / "condition_regions.json").read_text())
    return {r["key"] for r in doc["regions"]}


def _moves() -> list:
    return json.loads((REPO / "data" / "moves" / "generic_sandbox_moves.json").read_text())["moves"]


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "collision_model.schema.json")


def check_determinism(doc: dict) -> list:
    d = doc["determinism"]
    errs = []
    if d["swept_volumes"] is not True:
        errs.append("Rule 13: contact must be tested along swept paths; discrete sampling permits tunnelling")
    if d["simultaneity"] != "pre_tick_snapshot":
        errs.append("Criterion E.19: simultaneous attacks must resolve against one pre-tick snapshot")
    if d["pair_ordering"] != "ascending_actor_index_then_move_id":
        errs.append("Criterion E.19: evaluation order must be fixed and declared")
    if d["timing_source"] != "authoritative_tick":
        errs.append("Criterion E.19: collision timing must come from the authoritative tick")
    return errs


def check_pipeline_total(doc: dict) -> list:
    stages = sorted(doc["resolution_pipeline"], key=lambda s: s["order"])
    errs = []
    orders = [s["order"] for s in stages]
    if orders != list(range(len(stages))):
        errs.append(f"Criterion A.5: pipeline order must be contiguous from 0, found {orders}")
    ids = {s["id"] for s in stages}
    for s in stages:
        if s["on_false"] != "terminal" and s["on_false"] not in ids:
            errs.append(f"stage '{s['id']}' falls through to unknown stage '{s['on_false']}'")

    # The first stage must be the non-intersection test terminating in whiffed:
    # nothing may be classified as landed before a miss has been ruled out.
    if not stages or stages[0]["verdict_if_true"] != "whiffed":
        errs.append("Rule 13: the pipeline must rule out non-intersection first, terminating in 'whiffed'")

    # Every one of the seven classes must be reachable.
    emitted = set()
    for s in stages:
        v = s["verdict_if_true"]
        if v == "dispatch_quality_bands":
            emitted.update(b["class"] for b in doc["quality_bands"])
        else:
            emitted.add(v)
    missing = set(SEVEN) - emitted
    if missing:
        errs.append(f"Criterion A.5: contact class(es) unreachable from the pipeline: {sorted(missing)}")
    extra = emitted - set(SEVEN)
    if extra:
        errs.append(f"pipeline emits non-canonical class(es): {sorted(extra)}")

    # Exactly one dispatch into the landed bands, and it must be last.
    dispatchers = [s for s in stages if s["verdict_if_true"] == "dispatch_quality_bands"]
    if len(dispatchers) != 1:
        errs.append(f"Criterion A.5: exactly one quality dispatch stage is required, found {len(dispatchers)}")
    elif dispatchers[0]["order"] != len(stages) - 1:
        errs.append("Criterion A.5: the quality dispatch must be the final stage")

    # Dodged must be decided before blocked (Rule 13 tier order rationale).
    pos = {s["verdict_if_true"]: s["order"] for s in stages}
    if "dodged" in pos and "blocked" in pos and pos["dodged"] > pos["blocked"]:
        errs.append("Rule 13: active evasion must be evaluated before guard interception")
    return errs


def check_region_lock(doc: dict) -> list:
    regions = _regions()
    hurt = doc["volumes"]["hurtboxes"]
    errs = []
    mapped = set()
    for h in hurt:
        r = h["condition_region"]
        if r not in regions:
            errs.append(f"Rule 14: hurtbox '{h['id']}' maps to unknown condition region '{r}'")
        mapped.add(r)
    for r in PHYSICAL_REGIONS:
        if r not in mapped:
            errs.append(f"Rule 14: physical region '{r}' has no hurtbox")
    if len({h["condition_region"] for h in hurt}) != len(hurt):
        errs.append("Rule 14: two hurtboxes map to the same condition region")
    # Side-specific regions must carry a side (eye damage is side-attributable).
    by_region = {h["condition_region"]: h for h in hurt}
    for r in ("eye_left", "arm_left"):
        if r in by_region and by_region[r].get("side") != "left":
            errs.append(f"Rule 14: '{r}' hurtbox must declare side 'left'")
    for r in ("eye_right", "arm_right"):
        if r in by_region and by_region[r].get("side") != "right":
            errs.append(f"Rule 14: '{r}' hurtbox must declare side 'right'")
    return errs


def check_guard_coverage(doc: dict) -> list:
    regions = _regions()
    errs = []
    gv = doc["volumes"]["guard_volumes"]
    covered = set()
    for g in gv:
        for r in g["covers_regions"]:
            if r not in regions:
                errs.append(f"guard volume '{g['id']}' covers unknown region '{r}'")
            covered.add(r)
        for a in g["absorbs_into"]:
            if a not in regions:
                errs.append(f"guard volume '{g['id']}' absorbs into unknown region '{a}'")
        if "guard_integrity" not in g["absorbs_into"]:
            errs.append(f"Rule 14: guard volume '{g['id']}' must absorb into guard_integrity "
                        f"(blocking reduces damage without erasing consequence)")
        if not any(a.startswith("arm_") for a in g["absorbs_into"]):
            errs.append(f"Rule 14: guard volume '{g['id']}' must absorb into the arms")
    # A guard that covers everything would remove the high/low trade-off.
    if covered >= set(PHYSICAL_REGIONS):
        errs.append("Rule 4: no guard configuration may cover every physical region; "
                    "passive blocking must remain counterable")
    heights = {g["height_class"] for g in gv}
    if heights != {"high", "low"}:
        errs.append(f"both a high and a low guard volume are required, found {sorted(heights)}")

    # Interception maps guard_interaction values onto real guard volumes, by the
    # punch's PATH rather than its target region (see the uppercut note in the data).
    ids = {g["id"]: g for g in gv}
    gi = doc["guard_interception"]
    for key, expect_height in (("blockable_high", "high"), ("blockable_low", "low")):
        for vid in gi[key]:
            if vid not in ids:
                errs.append(f"guard_interception.{key} names unknown guard volume '{vid}'")
            elif ids[vid]["height_class"] != expect_height:
                errs.append(f"guard_interception.{key} names '{vid}', whose height_class is "
                            f"'{ids[vid]['height_class']}'")
    either = set(gi["blockable_either"])
    if either != set(ids):
        errs.append(f"guard_interception.blockable_either must name every guard volume "
                    f"{sorted(ids)}, found {sorted(either)}")
    return errs


def check_contact_classes(doc: dict) -> list:
    cc = json.loads((REPO / "data" / "contact_classes.json").read_text())
    errs = list(schema_check.check_contact_ordering(cc))
    keys = {c["key"] for c in cc["classes"]}
    if keys != set(SEVEN):
        errs.append(f"Criterion A.5: contact classes must be exactly {sorted(SEVEN)}, found {sorted(keys)}")
    landed = {c["key"] for c in cc["classes"] if c["landed"]}
    if landed != set(LANDED):
        errs.append(f"landed classes must be {sorted(LANDED)}, found {sorted(landed)}")
    return errs


def check_quality_bands(doc: dict) -> list:
    bands = sorted(doc["quality_bands"], key=lambda b: b["min_alignment"])
    errs = []
    if [b["class"] for b in bands] != list(LANDED):
        errs.append(f"Criterion A.5: quality bands must ascend {list(LANDED)}, "
                    f"found {[b['class'] for b in bands]}")
    if bands[0]["min_alignment"] != 0.0:
        errs.append("quality bands must start at alignment 0.0")
    if bands[-1]["max_alignment"] != 1.0:
        errs.append("quality bands must reach alignment 1.0")
    for a, b in zip(bands, bands[1:]):
        if a["max_alignment"] != b["min_alignment"]:
            errs.append(f"quality bands '{a['class']}' and '{b['class']}' must be contiguous "
                        f"({a['max_alignment']} != {b['min_alignment']})")
    for b in bands:
        if b["max_alignment"] <= b["min_alignment"]:
            errs.append(f"quality band '{b['class']}' has non-positive width")
    forces = [b["delivered_force_fraction"] for b in bands]
    if forces != sorted(forces) or len(set(forces)) != len(forces):
        errs.append(f"Rule 14: delivered force must increase strictly across {list(LANDED)}, found {forces}")
    clean = [b for b in bands if b["class"] == "clean"]
    if clean and clean[0]["delivered_force_fraction"] != 1.0:
        errs.append("a clean landing must deliver full authored force")
    brushed = [b for b in bands if b["class"] == "brushed"]
    if brushed and brushed[0]["delivered_force_fraction"] <= 0:
        errs.append("Rule 14: brushed contact is reduced but meaningful, never zero")
    return errs


def check_move_table_lock(doc: dict) -> list:
    """Rule 22: counterplay must exist from the first punch, and the move table and
    collision model must describe the same world."""
    moves = _moves()
    hurt_regions = {h["condition_region"] for h in doc["volumes"]["hurtboxes"]}
    gi_map = doc["guard_interception"]
    volume_ids = {g["id"] for g in doc["volumes"]["guard_volumes"]}
    errs = []
    offensive = {"jab", "cross", "hook", "uppercut", "overhand", "body_shot"}
    for m in moves:
        if m["category"] not in offensive:
            continue
        for r in m.get("target_regions", []):
            if r == "guard_integrity":
                continue   # a legitimate target that is not a hurtbox
            if r not in hurt_regions:
                errs.append(f"Rule 22: move '{m['id']}' targets region '{r}' with no hurtbox")
        gi = m["guard_interaction"]
        if gi == "unblockable_by_design_prohibited":
            errs.append(f"Rule 11: move '{m['id']}' is unblockable by design, which is prohibited")
            continue
        if gi not in gi_map:
            errs.append(f"Rule 22: move '{m['id']}' uses guard_interaction '{gi}' "
                        f"with no matching guard_interception entry")
            continue
        interceptors = [v for v in gi_map[gi] if v in volume_ids]
        if not interceptors:
            errs.append(f"Rule 22: no guard volume intercepts move '{m['id']}' "
                        f"('{gi}') - counterplay would be absent")
    return errs


def check_closing_velocity(doc: dict) -> list:
    cv = doc["closing_velocity"]
    errs = []
    if cv["into_punch_max_multiplier"] <= 1.0:
        errs.append("Rule 14: movement into a punch must be able to increase consequence")
    if cv["away_from_punch_min_multiplier"] >= 1.0:
        errs.append("Rule 14: movement away from a punch must be able to reduce consequence")
    if cv["neutral_multiplier"] != 1.0:
        errs.append("neutral closing velocity must be the identity multiplier")
    if cv["into_punch_max_multiplier"] > 2.0:
        errs.append("Rule 14: closing-velocity bonus must modulate, not dominate, contact quality")
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
    return [f"Rule 13: forbidden collision-assist key '{k}' has no place in this model" for k in found]


def check_guard_alignment(doc: dict) -> list:
    """Decision 0010: a guard posture is geometry over the two volumes.

    The design reference names ten guards whose coverage changes with sub-state -
    a cross-arm bar riding low or high, a shell roll timed or late. Those are not
    ten volumes and not ten branches: they are extent modulation on the same two
    volumes, so the pipeline stays the single authority and never learns a
    posture's name.
    """
    ga = doc.get("guard_alignment")
    if not ga:
        return ["Decision 0010: guard_alignment block is absent"]
    errs = []
    if ga.get("authority") != "coverage_extent_only":
        errs.append("Decision 0010: postures may influence collision only through coverage extents")
    if ga.get("posture_identity_read_by_pipeline") is not False:
        errs.append("Rule 13: the pipeline must not read posture identity - a guard is an object "
                    "in space, not a status flag the resolver branches on")

    b = ga.get("extent_bounds", {})
    lo, hi = b.get("min"), b.get("max")
    if not isinstance(lo, (int, float)) or lo <= 0:
        errs.append("Decision 0010: extent_bounds.min must exceed 0 - no alignment state may zero "
                    "a guard volume, because a guard that covers nothing is a different posture")
    if hi != 1.0:
        errs.append("Decision 0010: extent_bounds.max must be 1.0 - no alignment state extends a "
                    "volume past its own structure, which is how a guard would stop being a trade")

    vols = {g["id"]: g for g in doc["volumes"]["guard_volumes"]}
    for vid, g in vols.items():
        ce = g.get("coverage_extent")
        if not ce:
            errs.append(f"guard volume '{vid}' declares no coverage_extent")
            continue
        if not ce["min_modulated"] <= ce["baseline"] <= ce["max_modulated"]:
            errs.append(f"guard volume '{vid}': baseline {ce['baseline']} lies outside its own "
                        f"modulation range [{ce['min_modulated']}, {ce['max_modulated']}]")
        if isinstance(lo, (int, float)) and ce["min_modulated"] < lo:
            errs.append(f"guard volume '{vid}': min_modulated {ce['min_modulated']} undercuts "
                        f"extent_bounds.min {lo}")
        if isinstance(hi, (int, float)) and ce["max_modulated"] > hi:
            errs.append(f"guard volume '{vid}': max_modulated {ce['max_modulated']} exceeds "
                        f"extent_bounds.max {hi}")

    seen: dict = {}
    for w in ga.get("worked_examples", []):
        for vid, val in w["extents"].items():
            if vid not in vols:
                errs.append(f"worked example {w['posture']}/{w['state']} sets an extent on unknown "
                            f"guard volume '{vid}'")
                continue
            ce = vols[vid].get("coverage_extent", {})
            if "min_modulated" in ce and not ce["min_modulated"] <= val <= ce["max_modulated"]:
                errs.append(f"worked example {w['posture']}/{w['state']}: extent {val} on '{vid}' "
                            f"falls outside that volume's modulation range")
        seen.setdefault(w["posture"], []).append(w["extents"])

    # Non-vacuity: some posture must actually move its extents between states.
    # Otherwise the mechanism is decoration and the conditional matchups it
    # exists to express are still unrepresentable.
    if not any(len(states) > 1 and any(s != states[0] for s in states[1:])
               for states in seen.values()):
        errs.append("Decision 0010: no posture varies its extents across states - the mechanism "
                    "would be inert and the drift it closes would still be open")

    stage = next((s for s in doc["resolution_pipeline"] if s["id"] == "guard_intercept"), None)
    if stage and "guard_coverage_extent" not in stage.get("reads", []):
        errs.append("the guard_intercept stage must read guard_coverage_extent, or extents cannot "
                    "affect interception and postures become cosmetic")
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
    ("determinism_e19", check_determinism),
    ("pipeline_total_a5", check_pipeline_total),
    ("region_lock_rule14", check_region_lock),
    ("guard_coverage_rule14", check_guard_coverage),
    ("contact_classes_a5", check_contact_classes),
    ("quality_bands_a5", check_quality_bands),
    ("move_table_lock_rule22", check_move_table_lock),
    ("closing_velocity_rule14", check_closing_velocity),
    ("anti_cheat_rule13", check_anti_cheat),
    ("guard_alignment_d0010", check_guard_alignment),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | END ]
