# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:47 UTC | START ]
"""ROADMAP Phase 1A step 4 validator: animation state laws.

Enforces, against data/animation_model.json:
Rule 13 (animation supplies pose, never truth; phase ticks equal authored move
frames; reactions interrupt offence), Rule 14 (tracked condition is visually
attributable, eyes and arms side-specific), Rule 15 (southpaw is the exact
mirror), Rule 19 (bounded responsiveness; blending never delays a state change),
criterion A.1 (every combat state has an animation and is inspectable), and
criterion E.19 (tick-anchored, outside the determinism loop).
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

from . import combat_states, schema_check

REPO = Path(__file__).resolve().parents[2]

# Interrupts that must override an in-flight attack, worst-priority-first order
# is asserted against move_commit below.
REACTIVE = ("stoppage", "knockdown", "stagger", "hit_reaction")

# Condition regions that must be visually attributable. The remaining entries in
# condition_regions.json are attribute-governed states (chin, durability,
# recovery, composure) whose expression is behavioural rather than a visible
# surface, so they are deliberately not required here.
MUST_BE_VISIBLE = ("head", "jaw_chin", "eye_left", "eye_right", "torso_upper",
                   "torso_lower", "arm_left", "arm_right", "guard_integrity")
SIDE_SPECIFIC = ("eye_left", "eye_right", "arm_left", "arm_right")

REQUIRED_PROHIBITIONS = ("root motion", "blended runtime playback", "contact class",
                         "wall-clock", "southpaw")

REQUIRED_INVARIANTS = (
    "animation_never_writes", "pose_not_truth", "position_belongs_to_movement",
    "state_coverage", "frames_match_move_data", "reaction_interrupts_offence",
    "responsiveness_bounded", "condition_is_visible", "stance_mirror_exact",
)


def load() -> dict:
    return json.loads((REPO / "data" / "animation_model.json").read_text())


def _moves() -> dict:
    doc = json.loads((REPO / "data" / "moves" / "generic_sandbox_moves.json").read_text())
    return {m["id"]: m for m in doc["moves"]}


def _regions() -> set:
    doc = json.loads((REPO / "data" / "condition_regions.json").read_text())
    return {r["key"] for r in doc["regions"]}


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "animation_model.schema.json")


def check_authority(doc: dict) -> list:
    a = doc["authority"]
    errs = []
    if a["writes_simulation_state"] is not False:
        errs.append("Criterion E.19: animation may never write simulation state")
    if a["participates_in_determinism_hash"] is not False:
        errs.append("Criterion E.20: animation must stay outside the authoritative log hash")
    if a["derivation"] != "pure_function_of_authoritative_state_and_tick":
        errs.append("Criterion E.20: animation must be a pure function of authoritative state and tick")
    if a["hitbox_transform_source"] != "authored_pose_sampled_at_tick_index":
        errs.append("Rule 13: hitbox transforms must come from authored pose sampled at a tick "
                    "index, not from blended playback")
    if a["root_motion_drives_position"] is not False:
        errs.append("Rule 13: root motion must not drive authoritative position; the movement "
                    "model owns position")
    return errs


def check_state_coverage(doc: dict) -> list:
    combat = combat_states.load()
    fa = combat["machines"]["fighter_action"]
    required = {s["id"] for s in fa["states"] if not s.get("provisioned")}
    provisioned = {s["id"] for s in fa["states"] if s.get("provisioned")}
    covered = {a["combat_state"] for a in doc["state_animations"]}
    errs = []
    for missing in sorted(required - covered):
        errs.append(f"Criterion A.1: combat state '{missing}' has no animation")
    for extra in sorted(covered - required - provisioned):
        errs.append(f"animation references unknown combat state '{extra}'")
    for p in sorted(covered & provisioned):
        errs.append(f"Rule 18: '{p}' is a provisioned state; animating it would claim "
                    f"architecture that is not implemented")
    ids = [a["combat_state"] for a in doc["state_animations"]]
    if len(set(ids)) != len(ids):
        errs.append("each combat state must map to exactly one animation entry")
    clips = [a["clip_id"] for a in doc["state_animations"]]
    if len(set(clips)) != len(clips):
        errs.append("state animation clip ids must be unique")
    return errs


def check_move_frame_lock(doc: dict) -> list:
    """Rule 13: the picture and the timing must be the same numbers.

    The duplication between move data and animation data is deliberate - an
    animator authors to explicit counts - and this check is the anti-drift
    mechanism that makes the duplication safe.
    """
    moves = _moves()
    errs = []
    animated = set()
    for a in doc["move_animations"]:
        mid = a["move_id"]
        animated.add(mid)
        m = moves.get(mid)
        if m is None:
            errs.append(f"animation references unknown move '{mid}'")
            continue
        for field, src in (("startup_ticks", "startup_frames"),
                           ("active_ticks", "active_frames"),
                           ("recovery_ticks", "recovery_frames")):
            if a[field] != m[src]:
                errs.append(f"Rule 13: move '{mid}' {field}={a[field]} but move data "
                            f"{src}={m[src]} - visible action and authoritative timing disagree")
    for missing in sorted(set(moves) - animated):
        errs.append(f"Criterion A.1: move '{missing}' has no animation")
    clips = [a["clip_id"] for a in doc["move_animations"]]
    if len(set(clips)) != len(clips):
        errs.append("move animation clip ids must be unique")
    return errs


def check_interrupts(doc: dict) -> list:
    errs = []
    by_id = {i["id"]: i for i in doc["interrupts"]}
    prios = [i["priority"] for i in doc["interrupts"]]
    if len(set(prios)) != len(prios):
        errs.append("interrupt priorities must form a strict total order")
    for name in REACTIVE + ("move_commit",):
        if name not in by_id:
            errs.append(f"Rule 13: required interrupt '{name}' is missing")
    if errs:
        return errs
    commit = by_id["move_commit"]["priority"]
    for name in REACTIVE:
        if by_id[name]["priority"] <= commit:
            errs.append(f"Rule 13: '{name}' must outrank move_commit, or a struck fighter "
                        f"would finish throwing")
        if not by_id[name]["interrupts_everything_below"]:
            errs.append(f"Rule 13: '{name}' must interrupt everything below it")
    if by_id["knockdown"]["priority"] <= by_id["hit_reaction"]["priority"]:
        errs.append("Rule 13: knockdown must outrank ordinary hit reaction")
    if by_id["stoppage"]["priority"] != max(prios):
        errs.append("Rules 16/13: stoppage must be the highest interrupt")
    return errs


def check_blending(doc: dict) -> list:
    b = doc["blending"]
    errs = []
    if b["blend_may_delay_state_change"] is not False:
        errs.append("Rules 13/19: blending must never delay an authoritative state change")
    if b["input_to_visible_response_ticks"] > 2:
        errs.append("Rule 19: 'impressively responsive' leads the game-feel order; visible "
                    "response must begin within 2 ticks")
    # A blend longer than the shortest OFFENSIVE startup would smear the windup that
    # counterplay depends on reading (Rule 22).
    #
    # Scoped to offensive moves deliberately. A 2-tick guard "startup" is not a windup
    # carrying counterplay information - it is a near-instant defensive action, and its
    # requirement is responsiveness rather than readability. That requirement is already
    # carried by input_to_visible_response_ticks above, which bounds when the visible
    # response BEGINS. Beginning a response and completing a blend are different
    # guarantees, and conflating them would force a blend budget of 1 tick across the
    # whole game to satisfy a constraint the guard never actually imposed.
    moves = _moves()
    offensive = {"jab", "cross", "hook", "uppercut", "overhand", "body_shot"}
    starts = [a["startup_ticks"] for a in doc["move_animations"]
              if moves.get(a["move_id"], {}).get("category") in offensive
              and a["startup_ticks"] > 0]
    if starts and b["max_blend_ticks"] >= min(starts):
        errs.append(f"Rule 22: max_blend_ticks {b['max_blend_ticks']} must stay below the "
                    f"shortest offensive startup {min(starts)}, or the windup becomes unreadable")
    return errs


def check_damage_visualization(doc: dict) -> list:
    regions = _regions()
    errs = []
    by_region = {}
    for d in doc["damage_visualization"]:
        r = d["condition_region"]
        if r not in regions:
            errs.append(f"Rule 14: visualization references unknown condition region '{r}'")
        if d["visible"] is not True:
            errs.append(f"Rule 14: condition region '{r}' must be visually attributable")
        by_region[r] = d
    for r in MUST_BE_VISIBLE:
        if r not in by_region:
            errs.append(f"Rule 14: condition region '{r}' has no visualization")
    for r in SIDE_SPECIFIC:
        if r in by_region and not by_region[r]["side_specific"]:
            errs.append(f"Rule 14: '{r}' damage must be side-specific")
    return errs


def check_stance(doc: dict) -> list:
    s = doc["stance"]
    errs = []
    if s["southpaw_handling"] != "exact_mirror":
        errs.append("Rule 15: southpaw animation must be the exact mirror of orthodox")
    if "attribute" not in s["switch_mechanism"].lower():
        errs.append("Rule 15: the switch mechanism must state that familiarity penalties are "
                    "attribute data, not animation timing")
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
    ("state_coverage_a1", check_state_coverage),
    ("move_frame_lock_rule13", check_move_frame_lock),
    ("interrupts_rule13", check_interrupts),
    ("blending_rule19", check_blending),
    ("damage_visible_rule14", check_damage_visualization),
    ("stance_rule15", check_stance),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:47 UTC | END ]
