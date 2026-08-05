# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 08:40 UTC | START ]
"""Phase R marker contract - the head is not where the punch is going.

The last factor in the reference gap that is not the stamina economy. The
reference simulator dodges 15.6% of everything thrown, on top of 14.8% swept;
this core dodges nothing, because the evasion stage was dropped when geometry
replaced the probabilistic guard. `slip_lead` has sat in the action set since
Phase H costing nothing and doing nothing - it is not even loaded into the core's
move table - and `roll_under` is authored and unreachable.

THE HAPPY DISCOVERY: canon authors evasion GEOMETRICALLY already, so no die is
needed and none is added. `guard_evasion_model.evasions` gives each evasion a
`kind`, a set of regions it VACATES, an active window in ticks, and the things it
is BEATEN BY:

    slip_lead    active_window  vacates head, jaw_chin  5 ticks
                 beaten_by feint_then_commit, body_shot
    roll_under   active_window  vacates head, jaw_chin  6 ticks
                 beaten_by uppercut, body_shot
    step_out     positional     vacates nothing         "range denial rather
    pivot_lead   positional     vacates nothing          than evasion... scores
                                                         nothing"

So the whole rule is one sentence and it is canon's, not mine:

    During an evasion's active window a punch aimed at a vacated region finds
    nothing there - UNLESS the punch is one the evasion is authored to be beaten
    by, in which case it lands into the movement.

That second clause is not an exception bolted on to save a model. It is the
design rule this project already runs on, applied one level out: a guard is not
"high defence" or "low defence" but a structure that protects some lanes and
exposes others. An evasion is the same object in motion. Canon says it plainly -
"the uppercut is the punishment because it rises into where the head is going" -
and a roll that beat the uppercut would be a strictly better guard rather than a
different one.

THE TELEGRAPH FALLS OUT, unpriced. The reference needs a multiplier to make slow
punches more dodgeable (`telegraph.evasion_gain_per_startup_frame`), because its
evasion is a die rolled at contact. Here a slip is five ticks of real time: an
11-frame overhand spends longer in flight than a 4-frame jab, so a slip thrown at
the same moment is far likelier to still be active when the overhand arrives. The
defender is not buffed and the slow punch is not nerfed - the slow punch is SEEN,
which is exactly what canon says the telegraph is for. Nothing computes it.

THE PRICE IS AUTHORED TOO. `evasion_economy.mistime_penalty_ticks: 6` - a
committed evasion that catches nothing leaves the defender in recovery with no
structure up. "Slipping is better than blocking when it works and worse when it
does not, which is what makes it a decision." And `outranks_guard: true` fixes
the stage order: evasion resolves BEFORE the guard, so a slipped punch is never
also a blocked punch.

SCOPE. `step_out` and `pivot_lead` are `positional` and vacate nothing; Phase Q
already gives step_out its real effect (distance) and pivot needs the lateral
geometry that is still pending. They are named here so their absence is a stated
scope boundary rather than a silent one.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_round as O  # noqa: E402

REPO = O.REPO
GUARD_EVASION = os.path.join("data", "guard_evasion_model.json")
MOVES = os.path.join("data", "moves", "generic_sandbox_moves.json")


def evade_pack() -> dict:
    """Canon's evasion model, loaded without touching a sealed phase.

    Phase N's `canon_pack` never loaded the evasions and Phase N is SEALED - its
    recomputation is pinned evidence and editing it would change the past. So
    this phase reads the same canon files itself, exactly as Phase Q reads the
    range bands, and the two packs sit side by side rather than one mutating the
    other.
    """
    import hashlib
    raw = io.open(os.path.join(REPO, GUARD_EVASION), "rb").read()
    ge = json.loads(raw)
    raw_m = io.open(os.path.join(REPO, MOVES), "rb").read()
    mt = json.loads(raw_m)
    key = "moves" if "moves" in mt else next(
        k for k, v in mt.items()
        if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0])
    table = {m["id"]: m for m in mt[key]}

    evasions = {}
    for e in ge["evasions"]:
        mv = table.get(e["move_id"], {})
        evasions[e["id"]] = {
            "kind": e["kind"],
            "vacates": tuple(e.get("vacates", ())),
            "active": int(e.get("active_ticks", 0)),
            "beaten_by": tuple(e.get("beaten_by", ())),
            "startup": int(mv.get("startup_frames", 0)),
            "recovery": int(mv.get("recovery_frames", 0)),
            "cost": O.q(mv.get("stamina_cost", 0.0)),
            "band": mv.get("range_band"),
        }
    econ = ge["evasion_economy"]
    c = {
        "evasions": evasions,
        "outranks_guard": bool(econ["outranks_guard"]),
        "mistime_ticks": int(econ["mistime_penalty_ticks"]),
        "category": {m["id"]: m.get("category") for m in mt[key]},
        "region": {m["id"]: (m.get("target_regions") or [None])[0]
                   for m in mt[key]},
        "sha": {"guard_evasion": hashlib.sha256(raw).hexdigest(),
                "moves": hashlib.sha256(raw_m).hexdigest()},
    }

    errs = []
    active = [k for k, v in evasions.items() if v["kind"] == "active_window"]
    if not active:
        errs.append("no evasion has an active window, so the stage is inert")
    for k in active:
        v = evasions[k]
        if v["active"] <= 0:
            errs.append("%s is an active_window evasion with no window" % k)
        if not v["vacates"]:
            errs.append("%s vacates nothing, so it can never evade anything" % k)
        if not v["beaten_by"]:
            errs.append("%s has no counter, which would make it a strictly "
                        "better guard rather than a different one" % k)
        if v["band"] is None:
            errs.append("%s has no authored range band" % k)
    for k, v in evasions.items():
        if v["kind"] == "positional" and v["vacates"]:
            errs.append("%s is positional yet vacates a lane" % k)
    if not c["outranks_guard"]:
        errs.append("evasion does not outrank the guard, so a slipped punch "
                    "could also be a blocked punch and the stage order is "
                    "undefined")
    if c["mistime_ticks"] <= 0:
        errs.append("a mistimed evasion costs nothing, so slipping is strictly "
                    "better than blocking and stops being a decision")
    # Every region an evasion claims to vacate must be a region the condition
    # model actually damages, or the vacating is decorative.
    for k in active:
        for r in evasions[k]["vacates"]:
            if r not in O.REGIONS:
                errs.append("%s vacates '%s', which is not a damage region"
                            % (k, r))
    c["canon_errors"] = errs
    return c


def beats(c: dict, evasion: str, move_id: str) -> bool:
    """Is this punch the authored punishment for this evasion?

    `beaten_by` names categories ('uppercut', 'body_shot') and tactics
    ('feint_then_commit', 'ring_cutting'). Only the categories can be matched to
    a move; a tactic that the core cannot yet express simply never matches, which
    is the honest behaviour - it must not silently match everything or nothing
    would ever be evaded, and it must not silently match nothing or the tactic
    would look implemented.
    """
    cat = c["category"].get(move_id)
    return cat is not None and cat in c["evasions"][evasion]["beaten_by"]


def evades(c: dict, evasion: str, move_id: str, region: str) -> bool:
    """The whole rule.

    True means the punch finds empty air. False means the punch continues to the
    guard stage exactly as before - evasion outranks the guard but does not
    replace it.
    """
    e = c["evasions"].get(evasion)
    if e is None or e["kind"] != "active_window":
        return False
    if region not in e["vacates"]:
        return False
    return not beats(c, evasion, move_id)


# ---- properties, stated so they can be proven -------------------------------

def a_body_shot_beats_the_slip(c: dict) -> bool:
    """The slip vacates the head; the body is still there to be hit."""
    body = [m for m, r in c["region"].items()
            if r in ("torso_upper", "torso_lower")]
    if not body:
        return False
    return all(not evades(c, "slip_lead", m, c["region"][m]) for m in body)


def the_uppercut_beats_the_roll(c: dict) -> bool:
    """Canon's own sentence, executable: the uppercut rises into where the head
    is going, so a roll does not evade it even though it vacates that region."""
    ups = [m for m, cat in c["category"].items() if cat == "uppercut"]
    if not ups:
        return False
    return all(c["region"][m] in c["evasions"]["roll_under"]["vacates"]
               and not evades(c, "roll_under", m, c["region"][m]) for m in ups)


def the_slip_evades_a_straight(c: dict) -> bool:
    """And it must actually evade something, or the phase changed nothing."""
    straights = [m for m, cat in c["category"].items()
                 if cat in ("jab", "cross")]
    return bool(straights) and all(
        evades(c, "slip_lead", m, c["region"][m]) for m in straights)


def no_evasion_is_strictly_better(c: dict) -> bool:
    """Every active evasion must be beaten by something the core can throw."""
    for k, v in c["evasions"].items():
        if v["kind"] != "active_window":
            continue
        if not any(beats(c, k, m) for m in O.PUNCHES):
            return False
    return True
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 08:40 UTC | END ]
