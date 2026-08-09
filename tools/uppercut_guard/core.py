# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 13:45 UTC | START ]
"""Phase L's guard rules, extracted so both callers reach ONE implementation.

WHY THIS EXISTS, and it is the same reason `uppercut_evade/core.py` exists.
Phase L proved guard interception in C++ and in `analyze_core_guard.py`, and
the rules lived inside the analyzer - so the integrated bout could only have
them by importing a phase analyzer (forbidden) or by copying the formulas
(the defect this project has deleted three times: eight copies of the LCG
constants, the phase formulas, and `policy.BY_BAND`). Decision 0012's
convergence rule is call, never copy. So the rules move here, the analyzer
calls them, and Phase L re-proves byte-identically or the extraction is wrong.

THE RULE, in canon's own terms and nobody else's. A posture authors an
`extents` map: how far its structure reaches across each guard volume. Canon
authors ONE interception threshold (`pose_geometry.guard.
plane_interception_min_extent`). A lane is covered when the posture's extent
over that lane's volume meets the threshold. That is the whole mechanism, and
everything the design promises falls out of it rather than being written:

  * `high_guard` (head 0.95 / body 0.55) closes the head and sells the body;
    `tight_elbow` is the mirror. Neither is "high defence" or "low defence" -
    each is a body structure that protects some lanes while exposing others,
    which is this project's stated core combat rule, arriving as arithmetic.
  * `guard_extent_multiplier_while_committed` (0.6) scales the extents at
    evaluation time, so 0.95 x 0.6 = 0.57 falls under the 0.6 threshold and
    THE NORMALLY-CLOSED LANE OPENS. The counterpunch is not a feature here.
    It is two authored numbers meeting.

WHAT THIS MODULE REFUSES TO DECIDE. Which posture a fighter holds (policy),
when a guard is consulted relative to an evasion (the bout's ordering, and
`evasion_economy.outranks_guard` already fixes it), and what a blocked punch
costs (`punch_model.outcome_recovery` and `guard_integrity`, read by the
caller). This answers one question: given a posture, a commitment state and a
punch, is the lane that punch travels covered?
"""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GUARD = os.path.join("data", "guard_evasion_model.json")
COLLISION = os.path.join("data", "collision_model.json")
POSE = os.path.join("data", "pose_geometry.json")


def _read(rel):
    with io.open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return json.load(fh)


def q(v):
    """Canon's decimals into the project's q10000 fixed point.

    Rounded rather than truncated, matching `analyze_core_guard.q` exactly:
    an extent of 0.95 must not become 9499 on one side of the extraction and
    9500 on the other, which is the whole point of moving the rule instead of
    rewriting it.
    """
    return int(round(float(v) * 10000))


def guard_pack():
    """Canon's guard structures, q10000, nothing invented.

    `canon_errors` follows the pattern the range and evade packs set: canon is
    checked against its own contract at load, and a bout refuses to start on a
    canon that cannot hold rather than discovering it mid-fight.
    """
    ge = _read(GUARD)
    col = _read(COLLISION)
    pose = _read(POSE)

    postures = {p["id"]: p for p in ge["postures"]}
    # height class -> the guard volume that covers it. The collision model
    # owns this mapping; nothing here re-derives it from a volume's name.
    vol_by_class = {gv["height_class"]: gv["id"]
                    for gv in col["volumes"]["guard_volumes"]}
    thr = q(pose["guard"]["plane_interception_min_extent"])
    cd_mult = q(ge["committed_defense"]["guard_extent_multiplier_while_committed"])
    # Which height class a punch travels through. Canon authors this by GUARD
    # INTERACTION, which is the vocabulary a guard is expressed in - not by
    # target region, which is where a punch ENDS. A guard protects the
    # interception path, not merely the final target.
    hmap = {e["guard_interaction"]: e["height_class"]
            for e in pose["height_by_guard_interaction"]}
    moves = _read(os.path.join("data", "moves",
                               "generic_sandbox_moves.json"))["moves"]
    interaction_by_move = {m["id"]: m["guard_interaction"]
                           for m in moves if "guard_interaction" in m}

    c = {
        "postures": {},
        "vol_by_class": vol_by_class,
        "threshold": thr,
        "committed_multiplier": cd_mult,
        "height_by_interaction": hmap,
        "interaction_by_move": interaction_by_move,
        "canon_errors": [],
    }
    for pid, p in postures.items():
        c["postures"][pid] = {
            "extents": {vid: q(v) for vid, v in p["extents"].items()},
            "mobility": q(p["mobility_multiplier"]),
            "hold_per_tick": q(p["stamina_per_tick"]),
            "alignment_states": tuple(p.get("alignment_states", ())),
            "counter_readiness": q(p.get("counter_readiness", 0)),
        }

    econ = ge.get("posture_economy") or {}
    c["hold_applies_when"] = econ.get("hold_cost_applies_when")
    c["offense_cheap"] = q(econ["offense_cheap_stamina_multiplier"]) \
        if "offense_cheap_stamina_multiplier" in econ else None
    c["offense_expensive"] = q(econ["offense_expensive_stamina_multiplier"]) \
        if "offense_expensive_stamina_multiplier" in econ else None

    if not c["postures"]:
        c["canon_errors"].append("no posture is authored, so no fighter can "
                                 "hold a guard at all")
    if not vol_by_class:
        c["canon_errors"].append("collision_model authors no guard volumes, "
                                 "so no lane can be covered by anything")
    if thr <= 0:
        c["canon_errors"].append(
            "plane_interception_min_extent is %d; a threshold at or below "
            "zero makes every posture cover every lane, which is a wall "
            "rather than a guard" % thr)
    if not (0 < cd_mult < 10000):
        c["canon_errors"].append(
            "guard_extent_multiplier_while_committed is %d and must be "
            "strictly inside (0, 1): at zero commitment is a guaranteed hit, "
            "which Rule 11 forbids, and at one the counterpunch is "
            "unreachable" % cd_mult)
    return c


def outcome_pack():
    """`punch_model.outcome_recovery`, read at last.

    Canon has authored this since step 6 and nothing ever opened it, so a
    punch that hit empty air cost its thrower exactly what a punch that landed
    cost him. Canon's own note is the whole argument: "Empty space is the
    greatest consequence in the model (Rule 13)", and the ordering it encodes
    is `contact_classes.commitment_tier` made real - blocked 1.15 < dodged 1.3
    < whiffed 1.5, because the arm that stops on structure travelled less far
    than the arm that found nothing, and the defender who MOVED earns more
    than the defender who merely covered.

    This is the price on throwing, and its absence is half of why the fight
    throws so much (Decision 0034).
    """
    pm = _read(os.path.join("data", "punch_model.json"))
    rows = {r["class"]: r for r in pm["outcome_recovery"]["rows"]}
    return {
        "recovery_multiplier": {k: q(r["recovery_multiplier"])
                                for k, r in rows.items()},
        "counter_window": {k: int(r["counter_window_ticks"])
                           for k, r in rows.items()},
    }


def covered(pack, posture_id, committed):
    """The height classes this posture closes right now.

    `committed` is the fighter being caught inside his own commitment - mid
    punch, mid evasion, still in recovery. Canon scales the extents rather
    than disabling the guard, which is why a committed fighter still covers
    what he covered MOST strongly and loses only the lanes he was covering
    marginally. Nothing is switched off; the structure is simply worse.
    """
    spec = pack["postures"].get(posture_id)
    if spec is None:
        raise KeyError(
            "%r is not an authored posture (%s). A fighter cannot hold a "
            "structure canon does not describe, and defaulting him to one "
            "would be inventing a defence."
            % (posture_id, ", ".join(sorted(pack["postures"]))))
    mult = pack["committed_multiplier"] if committed else 10000
    thr = pack["threshold"]
    return frozenset(
        hc for hc, vid in pack["vol_by_class"].items()
        if (spec["extents"].get(vid, 0) * mult) // 10000 >= thr)


def lane_of(pack, punches, move_id):
    """The height class a punch travels through, from canon's own mapping.

    PUNCH-NESS IS DECLARED BY THE CALLER and the LANE COMES FROM CANON - the
    same split `uppercut_evade.resolve` uses, and for the same reason. The
    caller passes a membership vocabulary (`contract.PUNCHES`), because
    `guard_high` also authors a guard interaction and is not a punch, and a
    module that inferred punch-ness from the move table would answer for
    moves nobody asked about.
    """
    if move_id not in punches:
        raise KeyError(
            "%r is not in the caller's declared punch vocabulary; guard "
            "interception is a question about punches." % (move_id,))
    interaction = pack["interaction_by_move"].get(move_id)
    if interaction is None:
        raise KeyError(
            "%r authors no guard_interaction, so which lane it travels "
            "through is unknown. Refused rather than assumed - a punch whose "
            "path nobody wrote cannot be blocked or allowed through on "
            "evidence." % (move_id,))
    lane = pack["height_by_interaction"].get(interaction)
    if lane is None:
        raise KeyError(
            "%r travels through guard interaction %r, which "
            "pose_geometry.height_by_guard_interaction does not map to a "
            "height class" % (move_id, interaction))
    return lane


def intercepts(pack, punches, posture_id, committed, move_id):
    """Does this structure, in this state, close the lane this punch takes?

    The whole of guard resolution, and deliberately a pure function of four
    declared things. No dice: the same posture against the same punch answers
    the same way every time, which is the rule evasion already follows and the
    reason a replay can explain a block in boxing's words rather than as a
    number that came up short.
    """
    return lane_of(pack, punches, move_id) in covered(pack, posture_id,
                                                      committed)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 13:45 UTC | END ]
