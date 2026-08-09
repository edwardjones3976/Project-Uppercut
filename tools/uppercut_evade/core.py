# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 23:40 UTC | START ]
"""Phase R's evasion rules, extracted so the integrated bout can CALL them.

THE PYTHON TWIN OF `UppercutEvadeCore.h`, and the second half of a pattern.
The C++ evasion rules were extracted into `FUppercutEvadeCanon` /
`FUppercutEvadeSession` so a live system and a commandlet could share one
implementation. The Python rules stayed inside a phase analyzer, and the
integrated contract may not import phase analyzers - the same trapdoor Phase Q
had, found by inspection rather than assumed.

Every function below was MOVED, not rewritten: sliced out of
`tools/engine/analyze_core_evade.py` by anchor and written verbatim by a
script. THE PROOF IS THE STREAM. Phase R must re-prove byte-identically through
its own prover afterwards, and the Director's instruction if it does not is
"stop, diagnose" - no re-blessing.

THE ONLY EDITS, and there are exactly three. The rule set reached for three
symbols in a phase analyzer, and each is now a parameter:

    O.q        -> `q` here, the same fixed-point conversion, with a test that
                  compares the two rather than trusting the eye;
    O.REGIONS  -> `regions`, handed to `evade_pack`;
    O.PUNCHES  -> `punches`, handed to `no_evasion_is_strictly_better`.

A vocabulary the caller already owns, passed in explicitly instead of reached
for. `analyze_core_evade` supplies exactly what it supplied before, so nothing
it computes can have changed.

THE BOXING IDEA THIS FILE PROTECTS, stated because it is the thing an
implementation would erode first:

    An evasion is a guard structure in motion.

A slip is not "+20% dodge chance". It is a head that is no longer occupying a
particular lane during an actual window of time. Which is why a body shot still
finds the body while the head slips, why an uppercut rises into a roll, why a
mistimed evasion is a vulnerability rather than a wasted input, and why there is
NO EVASION DIE anywhere in this module. Timing, trajectory, the vacated region
and the authored counter relationship decide the result. The geometry already
answers the question.
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

GUARD_EVASION = os.path.join("data", "guard_evasion_model.json")
MOVES = os.path.join("data", "moves", "generic_sandbox_moves.json")


def q(v):
    """Canon's decimal into the shared integer contract.

    Deliberately identical to the analyzer's own `q`;
    `tests/test_evade_core_extraction.py` compares them across a spread rather
    than trusting that they look alike.
    """
    return int(round(float(v) * 10000))


def evade_pack(regions) -> dict:
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
            "cost": q(mv.get("stamina_cost", 0.0)),
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
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 22:04 UTC | F2 ]
        # The bytes this pack was built from, so a stream header can hash what
        # the fight consumed instead of re-reading the disk.
        "canon_texts": {
            "data/guard_evasion_model.json": raw.decode("utf-8"),
            "data/moves/generic_sandbox_moves.json": raw_m.decode("utf-8")},
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
            if r not in regions:
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


def no_evasion_is_strictly_better(c: dict, punches) -> bool:
    """Every active evasion must be beaten by something the core can throw."""
    for k, v in c["evasions"].items():
        if v["kind"] != "active_window":
            continue
        if not any(beats(c, k, m) for m in punches):
            return False
    return True
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 23:40 UTC | END ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:20 UTC | START ]
ANIMATION = os.path.join("data", "animation_model.json")


def punch_frames(punches):
    """How long each punch is in the air, from canon's animation model.

    ADDED, NOT MOVED, and the distinction matters. Everything above this line
    came out of the Phase R analyzer verbatim; this is new, and it is here
    rather than in the bout because the C++ side already put it here:
    `FUppercutEvadeCanon` carries `FUppercutEvadePunch {Startup, Active,
    Frames}`, populated by `UppercutLoadEvadeCanon`. A live caller needs the
    window to know WHEN a punch resolves, and the two languages should keep
    that fact in the same place.

    Phase R's own `stream_pack` reads the same three fields for its clock. It
    is left exactly as it is: it is frozen evidence, and re-pointing it at this
    function would move a proven stream to save a duplicate nobody is confused
    by. The duplication is named here so the next reader meets it deliberately.

    Returns {move_id: {"startup", "active", "frames"}} and refuses a punch with
    no animation rather than giving it a default window - a punch that resolves
    at a guessed time is a punch whose evasion window was guessed too.
    """
    raw = io.open(os.path.join(REPO, ANIMATION), "rb").read()
    anim = {a["move_id"]: a for a in json.loads(raw)["move_animations"]}
    out = {}
    for mid in punches:
        a = anim.get(mid)
        if a is None:
            raise KeyError(
                "%r has no authored animation, so it has no time in the air "
                "and no window to be evaded during. A default here would be a "
                "guessed evasion window." % mid)
        out[mid] = {"startup": int(a["startup_ticks"]),
                    "active": int(a["active_ticks"]),
                    "frames": int(a["startup_ticks"]) + int(a["active_ticks"])
                              + int(a["recovery_ticks"])}
    return out


# The four reason codes Phase R's `P` row already uses, named here so the
# integrated bout emits the same vocabulary rather than inventing a parallel
# one. The Director's point about why these and not a die:
#
#   "The jab missed because the slip was still active" is boxing.
#   "Evasion roll succeeded" is a spreadsheet wearing gloves.
CLEAR = "clear"          # nothing was active; the punch arrives
VACATED = "vacated"      # the region the punch was aimed at had been left
COUNTER = "counter"      # the evasion is authored to be beaten by this punch
REGION = "region"        # an evasion was active, but not where this punch went
REASONS = (CLEAR, VACATED, COUNTER, REGION)


def resolve(c, punches, move_id, evasion_id):
    """Does this punch arrive, and WHY. Deterministic, and there is no die.

    `punches` is the caller's declared punch vocabulary - the same pattern as
    `no_evasion_is_strictly_better`, and for the same reason: the vocabulary
    belongs to whoever is running the fight, and reaching for a phase
    analyzer's copy is what the extraction exists to stop.

    `evasion_id` is whatever the defender had active at the instant the punch
    resolved, or None. Timing has already been decided by the caller - an
    evasion that had expired is simply not passed in, which is what makes a
    mistimed evasion a vulnerability rather than a wasted input.

    Returns (arrived, reason, region).

    TWO EARLIER VERSIONS OF THIS SIGNATURE WERE WRONG, and the tests caught
    both. The first accepted any move id, so `step_in` against a slip came back
    `(True, "region")` - an answer plausible enough to survive review, for
    something that cannot arrive. The second refused anything without a target
    region, which sounds like "is it a punch" and is not: canon gives
    `guard_high` a region of `arm_left`, so guards sailed through and made the
    `region` reason look reachable when no punch can produce it.

    So punch-ness is declared, not inferred, and the REGION IS READ FROM CANON
    rather than accepted from the caller - which deletes a whole class of
    caller error instead of validating it.
    """
    if move_id not in punches:
        raise KeyError(
            "%r is not in the caller's declared punch vocabulary, so it cannot "
            "arrive and cannot be evaded. Guards, steps and evasions are not "
            "punches - and canon gives some of them a target region, so having "
            "one proves nothing." % (move_id,))
    region = c["region"].get(move_id)
    if region is None:
        raise KeyError(
            "%r is declared a punch but canon gives it no target region, so "
            "there is nothing for an evasion to have vacated." % (move_id,))
    if not evasion_id:
        return True, CLEAR, region
    if beats(c, evasion_id, move_id):
        # He moved into it. An evasion is a structure in motion, so the motion
        # can carry a head onto a punch - the uppercut rising into the roll.
        return True, COUNTER, region
    if evades(c, evasion_id, move_id, region):
        return False, VACATED, region
    # Something was active and it was not where this punch was going. The body
    # is still there while the head slips.
    return True, REGION, region
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:20 UTC | END ]


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:40 UTC | START edit: Decision 0032 correction ]
# A helper named `evasion_frames` stood here for under an hour, reading
# startup/active/recovery from the MOVES table. The Director's correction
# to the round-three review applies to it exactly: the pack above already
# carries startup, recovery, cost and band per evasion, and
# `mistime_ticks` from evasion_economy - canon had authored all of it and
# the analyzer had always read it. A second source is a second opinion,
# so the helper is deleted and the bout consumes the pack.
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:40 UTC | END edit ]

