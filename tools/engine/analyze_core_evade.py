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

sys.path.insert(0, REPO)
from tools.uppercut_canon.header import canon_header_lines  # noqa: E402
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


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 12:10 UTC | START ]
"""Phase R marker stream - the artifact a C++ port has to reproduce.

Everything above is the RULE SET: canon read, four properties stated so they can
be mutation-proven, no clock. Enough to prove the rules and not enough to prove
an implementation, because an implementation is proven here only when its marker
stream is byte-identical to this module's.

WHAT THIS SLICE DELIBERATELY DOES NOT CONTAIN, and the reasoning is the same one
that kept Phase Q's port stable through two canon rulings:

  - **No separation and no geometry.** Whether a fist reaches is Phase Q's
    contract, proven byte-for-byte on 2026-08-05. Re-implementing it here would
    be a second place for it to be wrong. A punch in this slice arrives at the
    end of its active window; what this phase decides is whether anything is
    THERE when it does.
  - **No guard.** `outranks_guard` is true, so evasion resolves first and a
    dodged punch never reaches the guard stage at all. Phases L and O own what
    happens to a punch that is not dodged.
  - **No stamina.** Gate G7 is open on the stamina economy. A slice that spent
    stamina would have to be re-blessed the day it is ruled on, for a reason
    having nothing to do with evasion.

So this phase reads three canon files and the header names all three: guard and
evasion (the windows, the vacated regions, the counters, the economy), moves
(category and target region) and animation (how long a punch is in the air).

ROW KINDS:

  H  header: phase, three canon hashes, seed, ticks
  Y  one per evasion, sorted: kind, active window, what it vacates, what beats it
  M  one per punch, sorted: category and target region
  K  the two economy scalars, before any tick
  A  a commitment: which fighter, what he threw or slipped, the LCG word
  W  an evasion window opening or closing
  P  a punch resolving: dodged or arrived, the evasion in force, and WHY
  V  a property, proven rather than asserted
  S  trailer: counts and the FNV-1a 64 self-hash

THE INFORMATIVE ROW IS `P`, and its reason field is the phase in one column:
`clear` (no evasion active), `vacated` (dodged), `counter` (the evasion is
authored to be beaten by this punch, so it lands into the movement), or `region`
(an evasion was active but this punch was not aimed where it went).
"""
ANIMATION_R = os.path.join("data", "animation_model.json")

R_PUNCHES = ("jab_lead", "cross_rear", "hook_lead", "uppercut_rear",
             "body_straight_rear", "body_hook_lead")
R_EVASIONS = ("slip_lead", "roll_under")
R_ACTIONS = R_PUNCHES + R_EVASIONS + ("wait",)

LCG_A, LCG_C, LCG_M = O.LCG_A, O.LCG_C, O.LCG_M
fnv1a64 = O.fnv1a64


def stream_pack() -> dict:
    """`evade_pack` plus the one thing a clock needs: how long a punch is up."""
    import hashlib
    c = evade_pack()
    raw_a = io.open(os.path.join(REPO, ANIMATION_R), "rb").read()
    anim = {a["move_id"]: a for a in json.loads(raw_a)["move_animations"]}
    c["sha"]["animation"] = hashlib.sha256(raw_a).hexdigest()
    c["anim"] = {}
    errs = list(c["canon_errors"])
    for mid in R_PUNCHES:
        a = anim.get(mid)
        if a is None:
            errs.append("%s has no animation, so it has no time in the air" % mid)
            continue
        c["anim"][mid] = {
            "startup": int(a["startup_ticks"]), "active": int(a["active_ticks"]),
            "frames": int(a["startup_ticks"]) + int(a["active_ticks"])
                      + int(a["recovery_ticks"])}
    # The telegraph, unpriced and asserted: if every punch were in the air for
    # the same time, a five-tick slip would be equally good against all of them
    # and canon's telegraph would need a multiplier to exist. It does not.
    spans = {mid: c["anim"][mid]["startup"] + c["anim"][mid]["active"]
             for mid in c["anim"]}
    if spans and max(spans.values()) == min(spans.values()):
        errs.append("every punch spends the same time in the air, so a fixed "
                    "evasion window cannot distinguish a slow punch from a fast "
                    "one and the telegraph stops being free")
    c["canon_errors"] = errs
    return c


def expected_stream(seed: int, ticks: int) -> str:
    c = stream_pack()
    lines = ["H|phase=R"]
    # Decision 0023: dual identities. Migrated 2026-08-07 with no authoritative
    # row moved; the superseded whole-file hashes are in the phase evidence.
    lines += canon_header_lines(REPO, [
        ("guard_evasion", "data/guard_evasion_model.json"),
        ("moves", "data/moves/generic_sandbox_moves.json"),
        ("animation", "data/animation_model.json"),
    ])
    lines.append("H|seed=%d" % seed)
    lines.append("H|ticks=%d" % ticks)
    for eid in sorted(c["evasions"]):
        e = c["evasions"][eid]
        lines.append("Y|%s|%s|%d|%d|%s|%s"
                     % (eid, e["kind"], e["startup"], e["active"],
                        ",".join(sorted(e["vacates"])) or "-",
                        ",".join(sorted(e["beaten_by"])) or "-"))
    for mid in R_PUNCHES:
        lines.append("M|%s|%s|%s|%d|%d"
                     % (mid, c["category"].get(mid) or "-",
                        c["region"].get(mid) or "-",
                        c["anim"][mid]["startup"], c["anim"][mid]["active"]))
    lines.append("K|outranks_guard=%d|mistime_ticks=%d"
                 % (1 if c["outranks_guard"] else 0, c["mistime_ticks"]))

    busy = [0, 0]                       # commitment frames remaining
    punch = [None, None]                # (move, thrown_at)
    ev = [None, None]                   # (evasion, from_tick, until_tick)
    x = seed % LCG_M
    rows = []
    n = {k: 0 for k in ("commits", "punches", "evasions", "waits", "arrived",
                        "dodged", "countered", "wrong_region", "mistimed",
                        "clear")}

    for t in range(1, ticks + 1):
        for i in (0, 1):
            opp = 1 - i
            # ---- 1. a punch already in the air --------------------------
            if punch[i] is not None:
                mid, t0 = punch[i]
                a = c["anim"][mid]
                if t - t0 == a["startup"] + a["active"]:
                    region = c["region"].get(mid) or "-"
                    active = ev[opp] is not None and \
                        ev[opp][1] < t <= ev[opp][2]
                    if not active:
                        result, why, name = "arrived", "clear", "-"
                        n["clear"] += 1
                    else:
                        name = ev[opp][0]
                        if region not in c["evasions"][name]["vacates"]:
                            result, why = "arrived", "region"
                            n["wrong_region"] += 1
                        elif beats(c, name, mid):
                            # Canon's own sentence: the uppercut rises into
                            # where the head is going. A roll that beat it
                            # would be a strictly better guard, not a
                            # different one.
                            result, why = "arrived", "counter"
                            n["countered"] += 1
                        else:
                            result, why = "dodged", "vacated"
                            n["dodged"] += 1
                    if result == "arrived":
                        n["arrived"] += 1
                    rows.append("P|%d|%d|%s|%s|%s|%s|%s"
                                % (t, i, mid, result, why, region, name))
                    punch[i] = None
                elif t - t0 > a["startup"] + a["active"]:
                    punch[i] = None

            # ---- 2. an evasion window closing ---------------------------
            if ev[i] is not None and t == ev[i][2]:
                rows.append("W|%d|%d|%s|close" % (t, i, ev[i][0]))
                ev[i] = None

            # ---- 3. commitment ------------------------------------------
            if busy[i] > 0:
                busy[i] -= 1
                continue

            # ---- 4. one commitment --------------------------------------
            x = (LCG_A * x + LCG_C) % LCG_M
            action = R_ACTIONS[x % len(R_ACTIONS)]
            n["commits"] += 1
            if action == "wait":
                n["waits"] += 1
            elif action in R_PUNCHES:
                busy[i] = c["anim"][action]["frames"]
                punch[i] = (action, t)
                n["punches"] += 1
            else:
                e = c["evasions"][action]
                # A committed evasion that catches nothing leaves the defender
                # in recovery with no structure up. That price is authored -
                # `mistime_penalty_ticks` - and it is what makes slipping a
                # decision rather than a strictly better block.
                busy[i] = e["startup"] + e["active"] + e["recovery"] \
                    + c["mistime_ticks"]
                ev[i] = (action, t + e["startup"],
                         t + e["startup"] + e["active"])
                rows.append("W|%d|%d|%s|open" % (t, i, action))
                n["evasions"] += 1
            rows.append("A|%d|%d|%s|%d" % (t, i, action, x))

    # ---- properties, inside the hash so a port has to prove them too -------
    for name, ok in (("a_body_shot_beats_the_slip",
                      a_body_shot_beats_the_slip(c)),
                     ("the_uppercut_beats_the_roll",
                      the_uppercut_beats_the_roll(c)),
                     ("the_slip_evades_a_straight",
                      the_slip_evades_a_straight(c)),
                     ("no_evasion_is_strictly_better",
                      no_evasion_is_strictly_better(c))):
        rows.append("V|%s|%d" % (name, 1 if ok else 0))
    rows.append("V|canon_errors|%d" % len(c["canon_errors"]))

    h = fnv1a64("".join(l + "\n" for l in rows).encode("utf-8"))
    lines += rows
    lines.append("S|rows=%d|commits=%d|punches=%d|evasions=%d|waits=%d"
                 "|arrived=%d|dodged=%d|countered=%d|wrong_region=%d|clear=%d"
                 "|fnv1a64=%016x"
                 % (len(rows), n["commits"], n["punches"], n["evasions"],
                    n["waits"], n["arrived"], n["dodged"], n["countered"],
                    n["wrong_region"], n["clear"], h))
    return "\n".join(lines) + "\n"


def analyse(path: str) -> dict:
    """Read a stream back and re-derive its claims from the rows themselves.

    Not a comparison against `expected_stream` - the runner does that, byte for
    byte. This asks the different question of whether the artifact is internally
    coherent, so a stream produced by two agreeing but identically wrong
    implementations still has somewhere left to fail.
    """
    c = stream_pack()
    rows = [l.rstrip("\n") for l in io.open(path, encoding="utf-8") if l.strip()]
    body = [r for r in rows
            if not r.startswith(("H|", "Y|", "M|", "K|", "S|"))]
    trailer = next(r for r in rows if r.startswith("S|"))
    fields = dict(kv.split("=", 1) for kv in trailer.split("|")[1:])
    errs = []
    if int(fields["rows"]) != len(body):
        errs.append("the trailer counts %s rows and the file carries %d"
                    % (fields["rows"], len(body)))
    h = fnv1a64("".join(r + "\n" for r in body).encode("utf-8"))
    if "%016x" % h != fields["fnv1a64"]:
        errs.append("the self-hash does not cover the rows")
    seen = {"dodged": 0, "countered": 0, "wrong_region": 0, "clear": 0}
    for r in body:
        f = r.split("|")
        if f[0] != "P":
            continue
        result, why, region, name = f[4], f[5], f[6], f[7]
        if why == "vacated":
            seen["dodged"] += 1
            if result != "dodged":
                errs.append("tick %s vacated the region and the punch still "
                            "arrived" % f[1])
            if region not in c["evasions"][name]["vacates"]:
                errs.append("tick %s dodged a punch aimed at %s, which %s does "
                            "not vacate" % (f[1], region, name))
            if beats(c, name, f[3]):
                errs.append("tick %s dodged %s, which %s is authored to be "
                            "beaten by" % (f[1], f[3], name))
        elif why == "counter":
            seen["countered"] += 1
            if not beats(c, name, f[3]):
                errs.append("tick %s recorded a counter for %s against %s, "
                            "which does not beat it" % (f[1], f[3], name))
        elif why == "region":
            seen["wrong_region"] += 1
        elif why == "clear":
            seen["clear"] += 1
        if why != "vacated" and result != "arrived":
            errs.append("tick %s recorded %s with reason %s" % (f[1], result, why))
    for k, v in seen.items():
        if int(fields[k]) != v:
            errs.append("the trailer claims %s=%s and the rows show %d"
                        % (k, fields[k], v))
    return {"rows": len(body), "counts": seen, "errors": errs}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 12:10 UTC | END ]
