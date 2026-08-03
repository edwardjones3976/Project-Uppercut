# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:24 UTC | START ]
"""ROADMAP Phase 1A step 12 validator: Special / Ultimate / Full-Crowd Trait architecture.

The load-bearing law here is Rule 11: no attack is unblockable by design. An
ability system is exactly where that rule gets quietly broken, because the
temptation is to make the climactic move feel climactic by removing the answer.
This file's job is to make that impossible to author: counterable, no
invulnerability and no commitment bypass are schema constants, and every ability
must define the same nine properties an ordinary punch defines.

Also enforces Rule 12 (two Specials, one Ultimate, one Trait, the full bar
exclusive) and Rule 15 (command entry bypasses nothing).
"""
from __future__ import annotations
import json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

NINE = ("startup_frames", "active_frames", "recovery_frames", "range_band",
        "resource_cost", "guard_interaction", "hit_reaction",
        "counter_vulnerability", "positional_consequence")

EXPECTED_COUNTS = {"special": 2, "ultimate": 1, "full_crowd_trait": 1}

REQUIRED_PROHIBITIONS = ("unblockable by design", "invulnerability", "command entry",
                         "one completed bar", "more than two specials")

REQUIRED_INVARIANTS = (
    "every_ability_is_counterable", "abilities_answer_the_same_questions",
    "ultimates_stay_readable", "input_bypasses_nothing", "two_specials_only",
    "full_bar_exclusivity_holds_here_too", "full_bar_costs_the_whole_bar",
)


def load() -> dict:
    return json.loads((REPO / "data" / "ability_model.json").read_text())


def _crowd() -> dict:
    return json.loads((REPO / "data" / "crowd_model.json").read_text())


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "ability_model.schema.json")


def check_classes(doc: dict) -> list:
    """Rule 11 and Rule 12: stronger options, never safer ones."""
    errs = []
    by = {c["id"]: c for c in doc["ability_classes"]}
    for cid, n in EXPECTED_COUNTS.items():
        c = by.get(cid)
        if c is None:
            errs.append(f"ability class '{cid}' is missing")
            continue
        if c["per_fighter"] != n:
            errs.append(f"Rule 12: each fighter has {n} '{cid}', not {c['per_fighter']}")
        if not c["counterable"]:
            errs.append(f"Rule 11: '{cid}' must be counterable - no attack is unblockable by design")
        if c["grants_invulnerability"]:
            errs.append(f"Rule 13: '{cid}' grants invulnerability, which removes the answer rather "
                        f"than raising the stakes")
        if c["bypasses_commitment"]:
            errs.append(f"Rule 13: '{cid}' bypasses commitment")
    for cid in ("ultimate", "full_crowd_trait"):
        if cid in by and by[cid]["cost_fraction"] != 1.0:
            errs.append(f"Rule 12: '{cid}' must cost the entire Crowd Bar")
        if cid in by and by[cid]["resource"] != "crowd_bar_full":
            errs.append(f"Rule 12: '{cid}' must be a full-bar ability")
    if "special" in by and "ultimate" in by:
        if by["special"]["cost_fraction"] >= by["ultimate"]["cost_fraction"]:
            errs.append("a Special must cost strictly less than a full-bar ability")
    return errs


def check_counterplay(doc: dict) -> list:
    """Rule 22: an ability answers the same questions an ordinary attack answers."""
    r = doc["counterplay_requirements"]
    errs = []
    missing = [p for p in NINE if p not in r["must_define"]]
    if missing:
        errs.append(f"Rule 22: abilities must define {missing} exactly as ordinary attacks do - an "
                    f"ability that skips them has left the combat system rather than extended it")
    if r["min_startup_frames"] <= 0:
        errs.append("Rule 13: abilities need a startup floor; one that arrives faster than a jab is "
                    "not a climax, it is a coin flip")
    if r["min_recovery_frames"] <= r["min_startup_frames"]:
        errs.append("an ability's recovery floor should exceed its startup floor - the whole point "
                    "of a big option is that missing with it costs something")
    if not r["whiff_is_punishable"]:
        errs.append("Rule 13: a whiffed ability must be punishable")
    return errs


def check_activation(doc: dict) -> list:
    """Rule 15: recognition is forgiving; the fight is not."""
    a = doc["activation"]
    errs = []
    if not a["requires_explicit_confirmation"]:
        errs.append("Rule 15: activation requires explicit confirmation")
    for k in ("bypasses_stun", "bypasses_recovery", "bypasses_range",
              "bypasses_resource_cost", "bypasses_startup", "bypasses_whiff_punishment"):
        if a[k]:
            errs.append(f"Rule 15: command entry may not bypass {k.replace('bypasses_', '')} - "
                        f"a motion input is a way to ask, never a way to skip")
    return errs


def check_exclusivity(doc: dict) -> list:
    """Rule 12, cross-checked against the crowd model that owns the bar."""
    e = doc["exclusivity"]
    errs = []
    if e["both_from_one_bar"]:
        errs.append("Rule 12: one completed bar may never yield both an Ultimate and a Trait")
    if set(e["full_bar_choice"]) != {"ultimate", "full_crowd_trait"}:
        errs.append("the full-bar choice must be exactly the Ultimate and the Full-Crowd Trait")
    c = _crowd()["full_bar"]
    if set(c["choice"]) != set(e["full_bar_choice"]):
        errs.append("the ability model and the crowd model disagree about the full-bar choice")
    if not c["exclusive"]:
        errs.append("the crowd model no longer marks the full bar exclusive")
    return errs


def check_prohibitions(doc: dict) -> list:
    blob = " ".join(doc["prohibitions"]).lower()
    return [f"missing required prohibition covering '{p}'"
            for p in REQUIRED_PROHIBITIONS if p not in blob]


def check_invariants(doc: dict) -> list:
    present = {i["id"] for i in doc["invariants"]}
    return [f"missing required invariant '{r}'" for r in REQUIRED_INVARIANTS if r not in present]


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 10:36 UTC | START ]
def check_reference_instruments(doc: dict) -> list:
    """The instrument Ultimate, held to this file's own laws.

    The bar may buy force, never safety: recovery and stamina multipliers at or
    above 1, impact bounded, and the whole thing rides an ordinary punch so the
    nine counterplay properties come from the move table instead of being
    authored twice. A full bar that does nothing is the opposite failure and is
    also refused - that inert state is what made the showman's canon win
    condition unreachable for a full sweep.
    """
    ri = doc.get("reference_instruments")
    if ri is None:
        return ["no reference_instruments block - a full Crowd Bar does nothing in the reference "
                "model, so every win condition phrased as 'converting the bar' is unreachable"]
    u = ri["instrument_ultimate"]
    errs = []
    if u["impact_multiplier"] <= 1.0:
        errs.append("the Ultimate delivers no more than the punch it rides - spending a full bar "
                    "for nothing is authored-but-inert")
    if u["impact_multiplier"] > 2.0:
        errs.append("Ultimate impact above 2.0 approaches a different physics rather than an "
                    "amplified punch (Rule 11's unblockable-by-design, arrived at by force)")
    if u["recovery_multiplier"] < 1.0:
        errs.append("the Ultimate recovers faster than its base punch - the bar is buying "
                    "safety, which is what every prohibition in this file exists to prevent")
    if u["stamina_cost_multiplier"] < 1.0:
        errs.append("Rule 15: the Ultimate discounts its resource cost - a bypass by multiplier")
    return errs
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 10:36 UTC | END ]


ALL_CHECKS = [
    ("schema", check_schema),
    ("classes_rule11_rule12", check_classes),
    ("counterplay_rule22", check_counterplay),
    ("activation_rule15", check_activation),
    ("exclusivity_rule12", check_exclusivity),
    ("reference_instruments_rule15", check_reference_instruments),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:24 UTC | END ]
