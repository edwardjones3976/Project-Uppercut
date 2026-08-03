# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:52 UTC | START ]
"""ROADMAP Phase 1A step 6 validator: what throwing a punch costs.

Enforces, against data/punch_model.json:
Rule 13 (commitment is absolute; blocked < dodged < whiffed expressed in frames),
Rule 12 (no magnetic offense), Rule 19 (an input is never eaten), Rule 4 (the
repetition economy is observable boxing rather than a hidden counter), and
Rule 22 (the model and the move table agree).
"""
from __future__ import annotations
import json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

SEVEN = ("clean", "solid", "grazed", "brushed", "blocked", "dodged", "whiffed")
LANDED = ("clean", "solid", "grazed", "brushed")

REQUIRED_PROHIBITIONS = ("cancel a punch", "advance the fighter automatically",
                         "ignore, drop or lock out an input", "hidden counter")

REQUIRED_INVARIANTS = (
    "commitment_is_absolute", "outcome_recovery_total", "commitment_order_in_frames",
    "no_magnetic_offense", "input_is_never_eaten", "repetition_is_observable",
    "chaining_costs_something", "move_table_agreement",
)

# Rule 4: language that would mean the penalty is bookkeeping rather than boxing.
COUNT_WORDS = ("repeat count", "nth", "counter reaches", "after n ", "number of times")


def load() -> dict:
    return json.loads((REPO / "data" / "punch_model.json").read_text())


def _classes() -> list:
    return json.loads((REPO / "data" / "contact_classes.json").read_text())["classes"]


def _moves() -> list:
    return json.loads((REPO / "data" / "moves" / "generic_sandbox_moves.json").read_text())["moves"]


def _bands() -> set:
    doc = json.loads((REPO / "data" / "movement_model.json").read_text())
    return {b["key"] for b in doc["range_bands"]["bands"]}


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "punch_model.schema.json")


def check_commitment(doc: dict) -> list:
    """Rule 13. A thrown punch is a decision the fighter has to live with."""
    c = doc["commitment"]
    errs = []
    if c["thrower_cancelable_phases"]:
        errs.append("Rule 13: no punch phase may be cancelable by the thrower - commitment is the "
                    "reason counterplay exists")
    if c["free_cancel_permitted"]:
        errs.append("Rule 13: free cancels are prohibited")
    for phase in ("startup_interruptible_by", "active_interruptible_by", "recovery_interruptible_by"):
        for src in c.get(phase, []):
            if src != "being_struck":
                errs.append(f"Rule 13: {phase} admits '{src}' - only being struck may interrupt a punch")
    if not 0 <= c["input_buffer_ticks"] <= 4:
        errs.append("Rule 19: the input buffer must stay small enough that a queued punch cannot "
                    "outlive the read that justified it")
    return errs


def check_outcome_recovery(doc: dict) -> list:
    """Rule 13 in frames rather than in prose.

    contact_classes.json declares blocked < dodged < whiffed as an ordering.
    This is where that ordering becomes something a fighter can feel.
    """
    rows = doc["outcome_recovery"]["rows"]
    errs = []
    seen = [r["class"] for r in rows]
    if len(set(seen)) != len(seen):
        errs.append("a contact class appears twice in outcome_recovery")
    canon = {c["key"]: c for c in _classes()}
    missing = set(canon) - set(seen)
    if missing:
        errs.append(f"Criterion A.5: no recovery row for contact class(es) {sorted(missing)}")
    extra = set(seen) - set(canon)
    if extra:
        errs.append(f"outcome_recovery names non-canonical class(es) {sorted(extra)}")

    by = {r["class"]: r for r in rows}
    for cls in LANDED:
        if cls in by and by[cls]["recovery_multiplier"] != 1.0:
            errs.append(f"Rule 13: '{cls}' landed but carries a recovery penalty - landing is never "
                        f"punished for landing")

    # Non-decreasing across the canonical commitment tiers, strictly increasing
    # across the three miss classes (the ordering Rule 13 actually names).
    tiers = sorted(canon.values(), key=lambda c: c["commitment_tier"])
    prev_mult = prev_win = None
    for c in tiers:
        r = by.get(c["key"])
        if r is None:
            continue
        if prev_mult is not None and r["recovery_multiplier"] < prev_mult:
            errs.append(f"Rule 13: '{c['key']}' recovers faster than a lower commitment tier")
        if prev_win is not None and r["counter_window_ticks"] < prev_win:
            errs.append(f"Rule 13: '{c['key']}' offers a smaller counter window than a lower tier")
        prev_mult, prev_win = r["recovery_multiplier"], r["counter_window_ticks"]

    for a, b in (("blocked", "dodged"), ("dodged", "whiffed")):
        if a in by and b in by:
            if by[b]["recovery_multiplier"] <= by[a]["recovery_multiplier"]:
                errs.append(f"Rule 13: '{b}' must cost strictly more recovery than '{a}'")
            if by[b]["counter_window_ticks"] <= by[a]["counter_window_ticks"]:
                errs.append(f"Rule 13: '{b}' must open a strictly larger counter window than '{a}'")
    return errs


def check_gates(doc: dict) -> list:
    """Rule 12 (nothing is edited to make a punch connect) and Rule 19 (nothing is eaten)."""
    r, s = doc["range_gate"], doc["stamina_gate"]
    errs = []
    if r["outside_band_outcome"] != "whiffed":
        errs.append("Rule 12: a punch thrown outside its band must whiff - the simulation never "
                    "adjusts distance to rescue it")
    if r["auto_advance_on_throw"]:
        errs.append("Rule 12: throwing may not advance the fighter automatically (no invisible lunge)")
    if r["band_source"] != "data/movement_model.json":
        errs.append("range bands must come from the movement model, not be restated here")
    if s["input_ever_ignored"]:
        errs.append("Rule 19: an input is never ignored - exhaustion shows as worse boxing, not as "
                    "a dead controller")
    if s["insufficient_stamina_outcome"] != "throw_permitted_at_degraded_quality":
        errs.append("Rule 19: insufficient stamina degrades the punch rather than suppressing it")
    return errs


def check_repetition_economy(doc: dict) -> list:
    """Rule 4, the hardest law here.

    'Punished for spamming' is easy to write and easy to fake. The rule says the
    punishment must arrive through observable pattern recognition, stamina,
    position, commitment, defense and counterplay - not because the game decided
    repetition is illegal. So every mechanism has to name what it fires on and
    how you can see it, and the model has to punish through BOTH sides: the
    thrower paying a cost, and the defender getting a real chance to answer.
    Only the thrower's side is fatigue; only the defender's side is mind-reading.
    """
    r = doc["repetition_economy"]
    errs = []
    ids = [m["id"] for m in r["mechanisms"]]
    if len(set(ids)) != len(ids):
        errs.append("duplicate repetition mechanism id")
    for m in r["mechanisms"]:
        blob = (m["fires_on"] + " " + m["observable_as"]).lower()
        for w in COUNT_WORDS:
            if w in blob:
                errs.append(f"Rule 4: mechanism '{m['id']}' fires on bookkeeping ('{w}') rather than "
                            f"on observable boxing consequence")
        if not m["observable_as"].strip():
            errs.append(f"Rule 4: mechanism '{m['id']}' declares no observable form")
    targets = {m["target"] for m in r["mechanisms"]}
    if "thrower" not in targets:
        errs.append("Rule 4: no mechanism costs the thrower anything - repetition would be free")
    if "defender" not in targets:
        errs.append("Rule 4: no mechanism gives the defender a growing answer - repetition would be "
                    "tiring but not counterable, which is punishment without counterplay")
    blob = " ".join(r["prohibited_mechanisms"]).lower()
    for phrase in ("hidden repetition counter", "lockout", "decay"):
        if phrase not in blob:
            errs.append(f"Rule 4: the prohibition list must rule out '{phrase}' explicitly")
    if not r["legitimate_repetition"].strip():
        errs.append("Rule 4: unanswered repetition stays legitimate and the model must say so")
    return errs


def check_chaining(doc: dict) -> list:
    """Combinations come from overlapping recovery, not from a combo table."""
    c = doc["chaining"]
    errs = []
    if c["free_cancel_permitted"]:
        errs.append("Rule 13: chaining may not introduce free cancels through the back door")
    f = c["link_earliest_recovery_fraction"]
    if not 0 < f <= 1:
        errs.append("a link must begin inside recovery, never during active contact")
    if f < 0.25:
        errs.append(f"link_earliest_recovery_fraction {f} lets a follow-up begin so early that "
                    f"recovery stops being a real cost")
    same = c["same_hand_link_startup_multiplier"]
    opp = c["opposite_hand_link_startup_multiplier"]
    power = c["power_repeat_same_hand_startup_multiplier"]
    if same < opp:
        errs.append("the same hand must cost at least as much to re-throw as the other one - it has "
                    "to retract first")
    if power < same:
        errs.append("repeating the same POWER hand must cost at least an ordinary same-hand repeat; "
                    "the weight has to come back")
    return errs


def check_move_table_agreement(doc: dict) -> list:
    """Rule 22: this model and the move table must be talking about the same punches."""
    errs = []
    bands = _bands()
    offensive = {"jab", "cross", "hook", "uppercut", "overhand", "body_shot"}
    punches = [m for m in _moves() if m.get("category") in offensive]
    if not punches:
        errs.append("Rule 22: the move table declares no offensive moves for step 6 to govern")
    for m in punches:
        if m["range_band"] not in bands:
            errs.append(f"Rule 22: move '{m['id']}' sits in range band '{m['range_band']}', which "
                        f"the movement model does not define")
        for key in ("startup_frames", "active_frames", "recovery_frames"):
            if m.get(key, 0) <= 0:
                errs.append(f"Rule 13: move '{m['id']}' has no {key}; a punch with no {key} has no "
                            f"counterplay")
        if m.get("stamina_cost", 0) <= 0:
            errs.append(f"Rule 14: move '{m['id']}' costs no stamina - a free punch is a spam engine")
    # The recovery multipliers are meaningless if nothing has recovery to scale.
    if punches and doc["outcome_recovery"]["rows"] and all(
            m.get("recovery_frames", 0) == 0 for m in punches):
        errs.append("no punch has recovery frames for the outcome multipliers to act on")
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
    ("commitment_rule13", check_commitment),
    ("outcome_recovery_rule13", check_outcome_recovery),
    ("gates_rule12_rule19", check_gates),
    ("repetition_economy_rule4", check_repetition_economy),
    ("chaining_rule13", check_chaining),
    ("move_table_agreement_rule22", check_move_table_agreement),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:52 UTC | END ]
