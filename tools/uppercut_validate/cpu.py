# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:49 UTC | START ]
"""ROADMAP Phase 1A step 9 validator: CPU decision-making from observable evidence.

The Phase 1A quality gate asks for one thing here that cannot be demonstrated by
playing the game: that CPU fighters use "no hidden score, opponent input, or
privileged state knowledge". Absence is hard to show by testing behaviour, so it
is shown structurally instead - the CPU's declared input set is checked to be a
subset of the observable event vocabulary, and every sealed symbol named by
data/score_isolation_contract.json is checked to be absent from it.

Also enforces Rule 4 (a reaction floor, and difficulty that changes perception
rather than the physics), Rule 13 (commitment binds the CPU too) and Rule 3
(estimates carry confidence and stay below certainty).
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

REQUIRED_FORBIDDEN = ("official_cards", "opponent_input_buffer", "rng_state",
                      "hidden_attributes", "future_ticks")

REQUIRED_PROHIBITIONS = ("official scorecards", "input buffer", "reaction floor",
                         "difficulty alter", "committed action")

REQUIRED_INVARIANTS = (
    "observable_only", "firewall_is_structural", "no_privileged_reads",
    "reaction_floor_holds", "difficulty_never_cheats", "difficulty_is_monotone",
    "estimates_stay_estimates", "commitment_binds_cpu",
)


def load() -> dict:
    return json.loads((REPO / "data" / "cpu_decision_model.json").read_text())


def _event_types() -> set:
    doc = json.loads((REPO / "schemas" / "fight_event.schema.json").read_text())
    return set(doc["properties"]["type"]["enum"])


def _sealed() -> dict:
    return json.loads((REPO / "data" / "score_isolation_contract.json").read_text())


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "cpu_decision_model.schema.json")


def check_observable_inputs(doc: dict) -> list:
    """Rule 3, proven by construction: the firewall is a set relation, not a habit."""
    known = _event_types()
    sealed = _sealed()["sealed_symbols"]
    errs = []
    inputs = doc["observable_inputs"]
    if len(set(inputs)) != len(inputs):
        errs.append("an observable input is declared twice")
    for i in inputs:
        if i not in known:
            errs.append(f"observable input '{i}' is not a fight_event type - the CPU cannot read "
                        f"an event the simulation never emits")
    for ev in sealed.get("event_types", []):
        if ev in inputs:
            errs.append(f"Rule 3 VIOLATION: sealed judge event '{ev}' appears in the CPU's "
                        f"observable inputs - the score firewall is breached at the definition "
                        f"level, before a line of policy has been written")
    blob = " ".join(inputs).lower()
    for ident in sealed.get("identifiers", []):
        if ident.lower() in blob:
            errs.append(f"Rule 3: sealed identifier '{ident}' referenced by the CPU input set")
    # Non-vacuity: an empty-ish input set would pass every check above and mean nothing.
    if len(inputs) < 10:
        errs.append("the observable input set is too small to represent a fighter that can see - "
                    "this check exists so the firewall cannot be satisfied by blindness")
    return errs


def check_forbidden_inputs(doc: dict) -> list:
    """Rule 4: the bans are named, and each says what it protects."""
    errs = []
    ids = {f["id"] for f in doc["forbidden_inputs"]}
    for req in REQUIRED_FORBIDDEN:
        if req not in ids:
            errs.append(f"Rule 4: '{req}' must be explicitly forbidden to CPU policy")
    for f in doc["forbidden_inputs"]:
        if len(f["why"].strip()) < 20:
            errs.append(f"forbidden input '{f['id']}' gives no reason - a ban without a rationale "
                        f"is a ban someone removes later")
    return errs


def check_estimate_policy(doc: dict) -> list:
    """Rule 3: the CPU estimates. It never knows."""
    e = doc["estimate_policy"]
    errs = []
    if not e["confidence_required"]:
        errs.append("Rule 3: every CPU belief must carry a confidence")
    if e["max_confidence"] >= 1.0:
        errs.append("Rule 3: confidence must stay below certainty - a CPU that is ever certain has "
                    "stopped estimating and started knowing")
    if not e["evidence_must_cite_observed_events"]:
        errs.append("Rule 3: a belief must cite the observable events that produced it")
    if e["uncertainty_note_required_below"] > e["max_confidence"]:
        errs.append("the uncertainty-note threshold sits above the confidence ceiling, so it can "
                    "never fire")
    return errs


def check_reaction(doc: dict) -> list:
    """Rule 4: fast is allowed, instant is not. Rule 13: commitment binds the CPU."""
    r = doc["reaction"]
    errs = []
    if r["floor_ticks"] <= 0:
        errs.append("Rule 4: a zero-tick reaction floor is input reading by another name")
    if not r["respects_commitment"]:
        errs.append("Rule 13: CPU policy is bound by commitment exactly as a human is")
    if r["may_cancel_own_commitment"]:
        errs.append("Rule 13: the CPU may not cancel its own committed action when its estimate "
                    "changes - that is the privilege commitment exists to deny")
    for t in doc["difficulty_tiers"]:
        if t["reaction_ticks"] < r["floor_ticks"]:
            errs.append(f"Rule 4: difficulty '{t['id']}' reacts in {t['reaction_ticks']} ticks, "
                        f"below the floor of {r['floor_ticks']}")
    return errs


def check_difficulty(doc: dict) -> list:
    """Rule 4: harder means sharper, never richer."""
    errs = []
    may, never = set(doc["difficulty_may_change"]), set(doc["difficulty_may_never_change"])
    overlap = may & never
    if overlap:
        errs.append(f"difficulty lists contradict each other on {sorted(overlap)}")
    for req in ("damage_dealt", "stamina_cost", "attribute_values",
                "contact_classification", "input_responsiveness"):
        if req not in never:
            errs.append(f"Rule 4: difficulty must never change '{req}' - a CPU that hits harder on "
                        f"a higher setting is a hidden advantage, not a better opponent")
    tiers = doc["difficulty_tiers"]
    ids = [t["id"] for t in tiers]
    if len(set(ids)) != len(ids):
        errs.append("duplicate difficulty tier id")
    ordered = sorted(tiers, key=lambda t: t["read_depth"])
    for a, b in zip(ordered, ordered[1:]):
        if b["reaction_ticks"] > a["reaction_ticks"]:
            errs.append(f"tier '{b['id']}' reads deeper than '{a['id']}' yet reacts slower - "
                        f"difficulty must order coherently")
        if b["error_rate"] > a["error_rate"]:
            errs.append(f"tier '{b['id']}' reads deeper than '{a['id']}' yet errs more often")
    if len({t["reaction_ticks"] for t in tiers}) == 1:
        errs.append("every tier reacts identically - difficulty would be inert")
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
    ("observable_only_rule3", check_observable_inputs),
    ("forbidden_inputs_rule4", check_forbidden_inputs),
    ("estimate_policy_rule3", check_estimate_policy),
    ("reaction_rule4_rule13", check_reaction),
    ("difficulty_rule4", check_difficulty),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:49 UTC | END ]
