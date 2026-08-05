# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 11:50 UTC | START ]
"""Phase S marker contract - a fighter, instead of a coin with a range model.

Everything measured after Phase R has been measuring a fighter who acts on nearly
every tick he is free: ~180 stamina-charging actions per round against an economy
that refills 10.6. That is not a stamina problem and it is not a knockdown
problem. It is that the core has never had a policy - it draws uniformly from a
pool that happens to contain `idle` once - while canon authors one in full and the
core reads none of it.

WHAT CANON AUTHORS, and this phase executes without adding to it:

    reaction.decision_interval_ticks   4    how often the policy RUNS
    reaction.floor_ticks               6    the fastest any tier may RESPOND
    reaction.respects_commitment    true
    reaction.may_cancel_own_commitment false

    tier        reaction_ticks  read_depth  aggression_bias  error_rate
    novice                  20           1             0.35        0.35
    club                    14           2             0.45        0.22
    contender               10           3             0.55        0.12
    champion                 6           4             0.60        0.05

THE DISTINCTION THAT MATTERS, and that this core has never made: the decision
interval is how often a fighter THINKS, and `reaction_ticks` is how long it takes
him to respond to something he has seen. They are different numbers in canon - 4
and 6-to-20 - and the core has been treating the first as if it were both.

That distinction produces a piece of real boxing for free. A jab has 4 startup
frames. The FASTEST tier canon permits reacts in 6. So no fighter at any
difficulty can react to a jab - it must be anticipated, or eaten. An 11-frame
overhand can be reacted to by a champion and a contender and not by a novice.
Nobody wrote that rule; it falls out of two authored numbers meeting a move table,
which is the same shape as the telegraph falling out of Phase R.

IT ALSO MAKES PHASE R'S MEASUREMENT ILLEGAL, and this phase says so plainly. The
reactive slip in `experiment_range_model.band_aware` fires on the tick the punch
enters startup - an instant response, which canon's own prohibition list forbids
outright: "React faster than the reaction floor at any difficulty, at any time."
Phase R's evasion numbers are therefore an upper bound on what a legal fighter
could achieve, not a measurement of one. The correction lives here rather than as
an edit to Phase R, so the mistake stays visible.

WHAT ERROR_RATE IS AND IS NOT. Canon's prohibition is explicit: difficulty may
never "alter damage, stamina, attributes, contact classification, crowd gain,
input responsiveness, judging or refereeing". So `error_rate` cannot make a punch
weaker or a guard worse. It can only change WHICH ACTION IS CHOSEN - a novice
picks the wrong answer more often. That is the only implementation of it that
Rule 4 permits, and it is the one below.

READ_DEPTH is loaded and NOT executed here, and is named rather than quietly
dropped: it feeds the opponent read (`repetition_economy.opponent_read` in the
reference, which our core has never had), and a read model is its own phase.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_round as O  # noqa: E402

REPO = O.REPO
CPU = os.path.join("data", "cpu_decision_model.json")


def policy_pack() -> dict:
    import hashlib
    raw = io.open(os.path.join(REPO, CPU), "rb").read()
    d = json.loads(raw)
    r = d["reaction"]
    tiers = {}
    for t in d["difficulty_tiers"]:
        tiers[t["id"]] = {
            "reaction": int(t["reaction_ticks"]),
            "read_depth": int(t["read_depth"]),
            "aggression": O.q(t["aggression_bias"]),
            "error": O.q(t["error_rate"]),
        }
    c = {
        "tiers": tiers,
        "order": [t["id"] for t in d["difficulty_tiers"]],
        "interval": int(r["decision_interval_ticks"]),
        "floor": int(r["floor_ticks"]),
        "respects_commitment": bool(r["respects_commitment"]),
        "may_cancel": bool(r["may_cancel_own_commitment"]),
        "observable": tuple(d["observable_inputs"]),
        "forbidden": tuple(f["id"] for f in d["forbidden_inputs"]),
        "sha": hashlib.sha256(raw).hexdigest(),
    }

    errs = []
    if not c["respects_commitment"] or c["may_cancel"]:
        errs.append("a policy that can cancel its own commitment makes "
                    "commitment free, and commitment is the currency")
    fastest = min(t["reaction"] for t in tiers.values())
    if fastest < c["floor"]:
        errs.append("tier reacts in %d ticks, below the %d-tick floor"
                    % (fastest, c["floor"]))
    if len({t["reaction"] for t in tiers.values()}) == 1:
        errs.append("every tier reacts identically, so difficulty is inert")
    # Monotonicity: a harder tier must be at least as fast, at least as
    # aggressive and no more error-prone, or the ladder is not a ladder.
    seq = [tiers[k] for k in c["order"]]
    for a, b in zip(seq, seq[1:]):
        if b["reaction"] > a["reaction"]:
            errs.append("a harder tier reacts more slowly")
        if b["aggression"] < a["aggression"]:
            errs.append("a harder tier is less aggressive")
        if b["error"] > a["error"]:
            errs.append("a harder tier makes more errors")
    for t in tiers.values():
        if not 0 <= t["error"] < 10000:
            errs.append("an error rate at or above certainty makes a tier "
                        "incapable of ever choosing what it meant to")
        if not 0 < t["aggression"] < 10000:
            errs.append("an aggression bias at a boundary is a fighter who "
                        "either never punches or does nothing else")
    if c["interval"] <= 0:
        errs.append("a non-positive decision interval is not a clock")
    c["canon_errors"] = errs
    return c


def may_react(c: dict, tier: str, ticks_visible: int) -> bool:
    """Has this fighter had time to respond to something he has seen?

    `ticks_visible` is how long the thing has been observable. The tier's own
    reaction time gates the response, and the floor gates the tier - canon's
    prohibition is absolute: "React faster than the reaction floor at any
    difficulty, at any time."
    """
    need = max(c["floor"], c["tiers"][tier]["reaction"])
    return ticks_visible >= need


def is_offensive(c: dict, tier: str, x: int) -> bool:
    """Canon's `aggression_bias`, as the share of decisions that throw."""
    return (x % 10000) < c["tiers"][tier]["aggression"]


def errs(c: dict, tier: str, x: int) -> bool:
    """Canon's `error_rate`: the chance this decision is the wrong one.

    It changes WHICH ACTION IS CHOSEN and nothing else. Rule 4 forbids difficulty
    from touching damage, stamina, attributes, contact classification, crowd
    gain, input responsiveness, judging or refereeing - so an error may not be
    implemented as a weaker punch or a worse guard, only as a different choice.
    """
    return ((x // 10000) % 10000) < c["tiers"][tier]["error"]


# ---- properties, stated so they can be proven -------------------------------

def nobody_can_react_to_a_jab(c: dict) -> bool:
    """Four startup frames against a six-tick floor. The jab must be anticipated
    or eaten - which is what a jab is."""
    core = O.canon_pack()
    startup = core["moves"]["jab_lead"]["startup"]
    return all(not may_react(c, t, startup) for t in c["tiers"])


def the_slowest_punch_is_readable_by_someone(c: dict) -> bool:
    """And something must be reactable, or reaction is decoration."""
    core = O.canon_pack()
    slowest = max(core["moves"][m]["startup"] for m in O.PUNCHES)
    return any(may_react(c, t, slowest) for t in c["tiers"])


def difficulty_is_a_ladder(c: dict) -> bool:
    seq = [c["tiers"][k] for k in c["order"]]
    return all(b["reaction"] <= a["reaction"]
               and b["aggression"] >= a["aggression"]
               and b["error"] <= a["error"]
               for a, b in zip(seq, seq[1:]))


def reaction_is_not_the_decision_clock(c: dict) -> bool:
    """The distinction this phase exists to make. If every tier reacted in
    exactly the decision interval, the two would be the same number and the
    core's conflation would have been harmless."""
    return any(t["reaction"] != c["interval"] for t in c["tiers"].values())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 11:50 UTC | END ]
