# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:18 UTC | START ]
"""ROADMAP Phase 1A step 11 validator: the Crowd Bar as a mechanism.

data/crowd_contract.json states Rule 12 as law - what the crowd rewards, what it
refuses to reward, and what it may never touch. This checks that the *mechanism*
in data/crowd_model.json obeys that law rather than restating it: every gain
source is a contract-declared rewardable behaviour, no insufficient behaviour
appears as a source, and the two anti-farming devices actually bite.

The subtle one is Rule 4. A meter that drops repeated actions to zero would stop
farming and also break the rule that legitimate repetition stays legitimate. So
the novelty floor must be strictly above zero: a jab that keeps working still
earns, it just stops being a meter engine.
"""
from __future__ import annotations
import json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

REQUIRED_PROHIBITIONS = ("official scorecards", "generic damage", "meter farming",
                         "contact truth", "full-crowd trait from one completed bar",
                         "exactly zero")

REQUIRED_INVARIANTS = (
    "crowd_is_blind_to_scores", "no_generic_multipliers", "gain_sources_are_canonical",
    "risk_gate_stops_farming", "novelty_decays_but_never_to_zero",
    "full_bar_is_exclusive", "banking_is_discouraged",
)


def load() -> dict:
    return json.loads((REPO / "data" / "crowd_model.json").read_text())


def _contract() -> dict:
    return json.loads((REPO / "data" / "crowd_contract.json").read_text())


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "crowd_model.schema.json")


def check_authority(doc: dict) -> list:
    """Rule 3 and Rule 12: the crowd is loud, not powerful."""
    a = doc["authority"]
    errs = []
    for k, why in (
        ("reads_official_scores", "the crowd is not a judge and may not read the cards"),
        ("alters_official_scores", "the crowd may not touch the cards"),
        ("alters_judging_criteria", "the crowd may not change how a round is scored"),
        ("alters_contact_truth", "the crowd may not decide whether a punch landed"),
        ("alters_condition_truth", "the crowd may not decide how hurt a fighter is"),
        ("alters_stamina_truth", "the crowd may not decide how tired a fighter is"),
        ("grants_generic_multipliers", "a hidden generic multiplier is the rubber band Rule 12 bans"),
    ):
        if a[k]:
            errs.append(f"Rule 12: {why}")
    return errs


def check_gain_sources(doc: dict) -> list:
    """Every source is contract-rewardable; no insufficient behaviour sneaks in."""
    c = _contract()
    rewardable = set(c["rewardable_behaviour"])
    insufficient = set(c["insufficient_behaviour"]["keys"])
    errs = []
    ids = [g["id"] for g in doc["gain_sources"]]
    if len(set(ids)) != len(ids):
        errs.append("duplicate gain source id")
    for g in doc["gain_sources"]:
        if g["id"] in insufficient:
            errs.append(f"Rule 12: '{g['id']}' is declared insufficient by the crowd contract and "
                        f"may not be a gain source")
        elif g["id"] not in rewardable:
            errs.append(f"gain source '{g['id']}' is not a behaviour the crowd contract rewards - "
                        f"the mechanism may not invent new rewardable behaviour")
    missing = rewardable - set(ids)
    if missing:
        errs.append(f"the contract rewards {sorted(missing)} and the mechanism pays nothing for it")
    return errs


def check_risk_gate(doc: dict) -> list:
    """Rule 4: farming a target that cannot answer is the tempting exploit."""
    r = doc["risk_gate"]
    errs = []
    if not r["requires_counter_exposure"]:
        errs.append("Rule 12: crowd-paying actions must carry counter exposure")
    if not r["zero_gain_when_unopposed"]:
        errs.append("Rule 12: an action against a target that cannot answer must earn nothing - "
                    "this is the single most tempting exploit in any meter system")
    # The best-paying sources must be the risky ones, or risk is decorative.
    ranked = sorted(doc["gain_sources"], key=lambda g: -g["base_gain"])
    top = ranked[:3]
    if not all(g["requires_risk"] for g in top):
        safe = [g["id"] for g in top if not g["requires_risk"]]
        errs.append(f"the highest-paying crowd sources must all require risk; {safe} pay top rates "
                    f"for free")
    return errs


def check_novelty(doc: dict) -> list:
    """Rule 4: repetition stops paying well without becoming forbidden."""
    n = doc["novelty"]
    errs = []
    if not 0 < n["repeat_multiplier"] < 1:
        errs.append("repeating an action must reduce its crowd value")
    if n["floor_multiplier"] <= 0:
        errs.append("Rule 4: the novelty floor must stay strictly above zero - a repeated action "
                    "that earns literally nothing has been prohibited rather than de-emphasised, "
                    "and legitimate repetition is explicitly protected")
    if n["floor_multiplier"] >= n["repeat_multiplier"]:
        errs.append("the novelty floor sits at or above the first repeat multiplier, so decay "
                    "never actually happens")
    return errs


def check_full_bar(doc: dict) -> list:
    f = doc["full_bar"]
    errs = []
    if set(f["choice"]) != {"ultimate", "full_crowd_trait"}:
        errs.append("Rule 12: a full bar offers exactly the Ultimate and the Full-Crowd Trait")
    if not f["exclusive"]:
        errs.append("Rule 12: one completed bar may never activate both")
    if not f["spend_empties_bar"]:
        errs.append("spending a full bar must empty it")
    c = _contract()["full_bar"]
    if set(c["choice"]) != set(f["choice"]) or not c["exclusive"]:
        errs.append("the mechanism's full-bar choice disagrees with the crowd contract")
    return errs


def check_bar(doc: dict) -> list:
    b = doc["bar"]
    errs = []
    if b["decay_per_tick_idle"] <= 0:
        errs.append("Rule 12: a bar that never decays lets a fighter bank early and coast")
    if b["decay_grace_ticks"] <= 0:
        errs.append("a grace window is required, or decay punishes normal pauses in exchange")
    if b["start"] >= b["max"]:
        errs.append("the bar starts full")
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
    ("authority_rule3_rule12", check_authority),
    ("gain_sources_rule12", check_gain_sources),
    ("risk_gate_rule4", check_risk_gate),
    ("novelty_rule4", check_novelty),
    ("full_bar_rule12", check_full_bar),
    ("bar_rule12", check_bar),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:18 UTC | END ]
