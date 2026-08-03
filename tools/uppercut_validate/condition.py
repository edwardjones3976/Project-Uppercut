# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:38 UTC | START ]
"""ROADMAP Phase 1A step 8 validator: condition, knockdowns and recovery.

Rule 14 is unusually specific about what this layer may not become: no single
generic health bar, no flat random knockout roll attached to every punch, and a
Chin of +100 that is maximum authored resistance rather than immunity. Those are
the three ways a damage model quietly stops being boxing, so each is a constant
in the schema and a check here.

Also enforces Rule 16 (the knockdown-count clock is universal - officiating
philosophy changes thresholds, never arithmetic), Rule 8 (the between-rounds
break is authoritative), and Rule 3 (a stoppage is decided on observable
evidence, never on scorecards).
"""
from __future__ import annotations
import json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

PHYSICAL_REGIONS = ("head", "jaw_chin", "eye_left", "eye_right",
                    "torso_upper", "torso_lower", "arm_left", "arm_right")

REQUIRED_PROHIBITIONS = ("generic health pool", "flat random knockout",
                         "absolute knockdown immunity", "knockdown-count clock",
                         "scorecards")

REQUIRED_INVARIANTS = (
    "no_generic_pool", "no_knockout_roll", "chin_is_not_immunity",
    "count_clock_is_universal", "work_never_outpaces_rest",
    "rounds_do_not_erase_damage", "stoppage_is_evidenced", "break_is_authoritative",
)


def load() -> dict:
    return json.loads((REPO / "data" / "condition_model.json").read_text())


def _regions() -> set:
    doc = json.loads((REPO / "data" / "condition_regions.json").read_text())
    return {r["key"] for r in doc["regions"]}


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "condition_model.schema.json")


def check_regions(doc: dict) -> list:
    """Rule 14: damage lands on regions, and a round never erases it."""
    known = _regions()
    errs = []
    if not doc.get("no_generic_health_pool"):
        errs.append("Rule 14: a generic health pool is prohibited - damage is per region")
    seen = [d["region"] for d in doc["damage_regions"]]
    if len(set(seen)) != len(seen):
        errs.append("a region appears twice in damage_regions")
    for d in doc["damage_regions"]:
        if d["region"] not in known:
            errs.append(f"damage region '{d['region']}' is not declared in condition_regions.json")
        if d["recovers_between_rounds"] >= 1.0:
            errs.append(f"Rule 14: region '{d['region']}' fully recovers between rounds, which "
                        f"erases the accumulation that makes late rounds different")
        if not d["impairs"]:
            errs.append(f"region '{d['region']}' impairs nothing, so damage to it is cosmetic")
    for r in PHYSICAL_REGIONS:
        if r not in seen:
            errs.append(f"Rule 14: strikeable region '{r}' has no condition track")
    jaw = [d for d in doc["damage_regions"] if d["region"] == "jaw_chin"]
    if jaw and not jaw[0].get("knockdown_relevant"):
        errs.append("Rule 14: the jaw/chin region must be knockdown-relevant")
    return errs


def check_stamina(doc: dict) -> list:
    """Working may never regenerate faster than resting, and throwing pays in full."""
    s = doc["stamina"]
    errs = []
    if s["regen_per_tick_throwing"] != 0:
        errs.append("throwing must regenerate nothing - a punch that pays for itself is what "
                    "makes volume a decision")
    if not s["regen_per_tick_idle"] >= s["regen_per_tick_moving"] >= s["regen_per_tick_throwing"]:
        errs.append("Rule 14: stamina regeneration must be non-increasing from idle to moving to "
                    "throwing; working faster than resting inverts the whole stamina economy")
    if s["between_rounds_recovery_fraction"] >= 1.0:
        errs.append("Rule 14: a full between-rounds stamina reset would erase pacing as a strategy")
    if not s["exhausted_threshold_fraction"] < s["low_threshold_fraction"]:
        errs.append("the exhausted threshold must sit below the low threshold")
    return errs


def check_knockdown(doc: dict) -> list:
    """Rule 14 (no dice) and Rule 16 (one clock for every official)."""
    k = doc["knockdown"]
    errs = []
    if k["flat_random_roll_per_punch"]:
        errs.append("Rule 14: no flat random knockout chance may be attached to a punch")
    needed = ("delivered_force", "contact_quality", "accumulated_condition")
    for n in needed:
        if n not in k["inputs"]:
            errs.append(f"Rule 14: knockdowns must read '{n}' - a knockdown produced from less than "
                        f"observable force, quality and accumulated condition is a dice roll wearing "
                        f"a longer name")
    if k["count_ticks_per_number"] != 60:
        errs.append("Rule 16: the count advances one number per authoritative second (60 ticks)")
    if k["max_per_round"] > k["max_per_bout"]:
        errs.append("per-round knockdown limit exceeds the per-bout limit")
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:10 UTC | START ]
    # Added with the knockdown-model work. Original author's tags untouched.
    # Every input the model DECLARES has to be one the model USES, or the list
    # above is documentation of an intention rather than a description of a
    # system. balance and guard_state sat in that list unread for a whole step,
    # and the cost was a pressure function with no tail: no threshold existed
    # that stopped some fights and not others.
    if "balance" in k["inputs"] and "pressure_modifiers" not in k:
        errs.append("Rule 14: 'balance' is declared as a knockdown input but nothing in the model "
                    "gives it a coefficient - a declared input that changes no outcome is a claim, "
                    "not a mechanism")
    if "guard_state" in k["inputs"] and "unguarded_lane_bonus" not in k.get(
            "pressure_modifiers", {}):
        errs.append("Rule 14: 'guard_state' is declared as a knockdown input but no term reads it "
                    "- the guard would stop mattering the instant interception failed")
    pm = k.get("pressure_modifiers", {})
    if pm and pm["caught_committed_multiplier"] <= pm["balanced_multiplier"]:
        errs.append("being caught mid-commitment is no worse than being set - the counter-punch "
                    "knockdown, which is how most of them actually happen, could not occur")
    rel = k.get("count_condition_relief_fraction")
    if rel is not None and not 0 < rel < 1:
        errs.append("the count must relieve some accumulated condition and not all of it: at zero "
                    "a hurt fighter never recovers inside a round and knockdowns cluster into an "
                    "automatic stoppage, at one the knockdown erases what caused it")
    if k.get("decision_path_must_survive") is not True:
        errs.append("the model does not require that some bouts reach the cards - a result state "
                    "that never occurs is unimplemented, however green its tests are")
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:10 UTC | END ]
    return errs


def check_chin(doc: dict) -> list:
    """Rule 14: +100 Chin is the most resistance available and still loses to evidence."""
    c = doc["chin"]
    errs = []
    if c["max_resistance_confers_immunity"]:
        errs.append("Rule 14: Chin +100 is maximum authored resistance, never absolute immunity")
    if not c["early_stoppage_possible_at_max"]:
        errs.append("Rule 14: a rare early stoppage must remain possible at maximum Chin, or the "
                    "attribute has become immunity by another route")
    return errs


def check_recovery(doc: dict) -> list:
    r = doc["recovery"]
    errs = []
    if r["between_rounds_break_ticks"] != 1800:
        errs.append("Rule 8: the between-rounds break is thirty real seconds - 1800 authoritative "
                    "ticks - and menus do not pause it")
    if not r["scales"]:
        errs.append("the Recovery attribute must scale something or it is decoration")
    return errs


def check_stoppages(doc: dict) -> list:
    """Rule 3: a stoppage is decided on observable evidence, never on the cards."""
    errs = []
    ids = [s["id"] for s in doc["stoppage_conditions"]]
    if len(set(ids)) != len(ids):
        errs.append("duplicate stoppage condition id")
    auths = {s["authority"] for s in doc["stoppage_conditions"]}
    if "referee" not in auths:
        errs.append("no stoppage condition is owned by the referee")
    for s in doc["stoppage_conditions"]:
        blob = s["trigger"].lower()
        for bad in ("score", "card", "points", "behind", "ahead"):
            if bad in blob:
                errs.append(f"Rule 3: stoppage '{s['id']}' triggers on '{bad}' - the scorecards are "
                            f"unreadable to officiating during the bout")
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
    ("regions_rule14", check_regions),
    ("stamina_rule14", check_stamina),
    ("knockdown_rule14_rule16", check_knockdown),
    ("chin_rule14", check_chin),
    ("recovery_rule8", check_recovery),
    ("stoppages_rule3", check_stoppages),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:38 UTC | END ]
