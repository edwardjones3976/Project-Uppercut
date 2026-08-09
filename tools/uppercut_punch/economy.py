# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 16:05 UTC | START ]
"""`punch_model.repetition_economy` - Rule 4, and the hardest law in that file.

WHY THIS EXISTS. Decision 0036 measured the fight throwing about four times
too much and named the authored answers that nothing had ever read. Two of
them govern throw rate from the thrower's side, and both are here. The other
two in that block (`opponent_read`, `counter_window_growth`) target the
DEFENDER's reaction and are a different mechanism for a different session.

CANON'S OWN CONSTRAINT, quoted because it decides the shape of everything
below: "Nothing here fires on a repeat count: every mechanism fires on an
observable consequence the opponent could have caused or prevented, so a
punished spammer was punished by boxing rather than by bookkeeping."

So neither mechanism counts repeats. `arm_fatigue` accumulates WORK BY AN ARM
and sheds it whenever that arm rests - a fighter who mixes hands never carries
it, which is the point: the tax is on doing one thing, not on throwing
punches. `position_cost` accumulates only while the feet do not move and
resets the moment they do. Both are things a fighter chose and can stop
choosing, which is what separates a consequence from a penalty.

WHAT THIS MODULE REFUSES. To decide when a fighter throws (policy), to charge
anything itself (the economy owns Wind), or to move anybody (the range core
owns position). It answers two questions and returns numbers: how much more
this arm's next punch costs, and how much ground this throw cedes.
"""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUNCH_MODEL = os.path.join("data", "punch_model.json")
MOVES = os.path.join("data", "moves", "generic_sandbox_moves.json")

ONE = 10000


def _read(rel):
    with io.open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return json.load(fh)


def q(v):
    return int(round(float(v) * ONE))


def repetition_pack():
    """The authored coefficients, q10000, nothing invented.

    Each mechanism is looked up by its canon `id` rather than by position in
    the array, because Decision 0026 says array position is not authority and
    this is a list of four.
    """
    pm = _read(PUNCH_MODEL)["repetition_economy"]
    by_id = {m["id"]: m for m in pm["mechanisms"]}
    moves = _read(MOVES)["moves"]

    c = {"hand_by_move": {m["id"]: m["hand"] for m in moves if "hand" in m},
         "canon_errors": []}

    arm = by_id.get("arm_fatigue")
    if arm is None:
        c["canon_errors"].append("repetition_economy authors no arm_fatigue")
    else:
        k = arm["coefficients"]
        c["per_throw_same_arm"] = q(k["per_throw_same_arm"])
        c["recovery_per_idle_tick"] = q(k["recovery_per_idle_tick"])
        c["max_multiplier"] = q(k["max_multiplier"])
        c["arm_affects"] = tuple(arm.get("affects", ()))

    pos = by_id.get("position_cost")
    if pos is None:
        c["canon_errors"].append("repetition_economy authors no position_cost")
    else:
        k = pos["coefficients"]
        c["ru_ceded_per_throw_without_step"] = \
            q(k["ru_ceded_per_throw_without_step"])
        c["position_resets_on"] = tuple(
            s.strip() for s in str(k["resets_on"]).split(","))

    if arm is not None and c["max_multiplier"] <= ONE:
        c["canon_errors"].append(
            "arm_fatigue max_multiplier is %d; at or below 1.0 the mechanism "
            "cannot make repetition cost anything" % c["max_multiplier"])
    return c


def hand_of(pack, move_id):
    """Which hand throws this. Canon's per-move `hand`, never inferred."""
    hand = pack["hand_by_move"].get(move_id)
    if hand is None:
        raise KeyError(
            "%r authors no hand, so which arm accumulates its work is "
            "unknown. Refused rather than guessed - charging the wrong arm "
            "would tax a fighter for mixing his hands, which is the exact "
            "behaviour canon says must never be taxed." % (move_id,))
    return hand


def arm_multiplier(pack, work):
    """This arm's current cost multiplier, from its accumulated work.

    `work` is q10000 above 1.0 - the amount the arm has earned by working -
    and it is clamped to canon's ceiling here rather than at the accumulation
    site, so a caller cannot accidentally carry an uncapped number.
    """
    return min(pack["max_multiplier"], ONE + max(0, work))


def worked(pack, work):
    """The arm just threw. Canon's per-throw increment, capped."""
    ceiling = pack["max_multiplier"] - ONE
    return min(ceiling, max(0, work) + pack["per_throw_same_arm"])


def rested(pack, work, ticks=1):
    """The arm did not throw for `ticks`. It sheds work at canon's rate.

    This is what makes the mechanism a consequence rather than a counter: a
    fighter who alternates hands is never carrying a tax he cannot shed, and
    the shedding needs no forgiveness rule because resting IS the forgiveness.
    """
    return max(0, work - pack["recovery_per_idle_tick"] * ticks)


def ground_ceded(pack, stepped_since_last_throw):
    """Ring position given up by throwing without resetting the feet.

    Canon's sentence is the whole design: "Punching without moving the feet
    cedes ground. The thrower ends up where the opponent put them." It is not
    a penalty on punching - it is the reason a fighter has to walk his man
    down rather than stand and let his hands go forever.
    """
    if stepped_since_last_throw:
        return 0
    return pack["ru_ceded_per_throw_without_step"]
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 16:05 UTC | END ]
