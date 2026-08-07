# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 06:30 UTC | START ]
"""The two-tier stamina economy. Decision 0021, Wind over Reserve.

THE CONTRACT COMES FIRST. This is the Python model the C++ runtime must
reproduce, written before the C++ exists so the C++ can be checked against
something rather than discovered by reading it.

    Wind      the acute exchange resource. Movement, guard, evasion, punches.
              Recovers during Observe, HoldPosition and especially Rest.
              A boxer can regain breath, so Wind can come back inside a round.

    Reserve   whole-fight conditioning. Drains slowly, does NOT recover inside a
              round, and reaches a knockdown only INDIRECTLY - through the Wind
              ceiling and the Wind recovery rate. Decision 0021 refuses to make
              it a second direct multiplier until the indirect path is proven
              insufficient, because that would count deep fatigue twice.

A short pause may restore Wind. It may not restore Reserve or erase the history
of the fight.

EVERYTHING IS q10000 INTEGERS. No float ever enters the state, and every
division goes through `floordiv` because Python's // floors and C++'s /
truncates - the seam where a port silently diverges.

NOTHING HERE IS CALIBRATED. `data/stamina_economy.json` declares
`calibration_status.values_are_fitted: false`, and Decision 0021 step 7 forbids
fitting until the integrated policy produces boxing-like cadence. This module
implements the STRUCTURE; the numbers are hypotheses.
"""
import io
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ECONOMY = "data/stamina_economy.json"
EFFORT = "data/moves/generic_sandbox_effort.json"

# Decision 0014's G2 action families. Recovery is a property of the observable
# action state, which is the whole reason those families were named.
ACTIONS = ("observe", "hold_position", "rest", "micro_adjust", "move", "guard",
           "evade", "attack")

# States that buy no Wind back at all (Decision 0021).
NO_RECOVERY = ("move", "guard", "evade", "attack")


def q(v):
    """Canon's decimal into the shared integer contract."""
    return int(round(float(v) * 10000))


def floordiv(a, b):
    """Python's // already floors. Named so the C++ port cannot forget."""
    return a // b


def _read(rel):
    with io.open(os.path.join(REPO, rel.replace("/", os.sep)),
                 encoding="utf-8") as fh:
        return json.load(fh)


def economy_pack():
    """Canon's two-tier economy, in q10000, with nothing invented."""
    e = _read(ECONOMY)
    f = _read(EFFORT)

    wind, reserve = e["wind"], e["reserve"]
    c = {
        "wind_max": q(wind["max"]),
        "wind_start": floordiv(q(wind["max"]) * q(wind["start_fraction"]), 10000),
        "wind_low": floordiv(q(wind["max"]) * q(wind["low_threshold_fraction"]), 10000),
        "wind_exhausted": floordiv(
            q(wind["max"]) * q(wind["exhausted_threshold_fraction"]), 10000),
        "wind_between_rounds": q(wind["between_rounds_recovery_fraction"]),
        # ONLY the eight declared action families, by name. An earlier draft
        # took everything that did not start with "$", which meant a new prose
        # key in this block was fed to float() - a loader that reads whatever it
        # finds will eventually read a sentence as a rate.
        "recover": {a: q(wind["recovery_per_tick_by_action"][a])
                    for a in ACTIONS
                    if a in wind["recovery_per_tick_by_action"]},
        "ceiling_floor": q(wind["ceiling_from_reserve"]["floor_fraction"]),
        "ceiling_span": q(wind["ceiling_from_reserve"]["span_fraction"]),
        "recovery_floor": q(wind["recovery_from_reserve"]["floor_multiplier"]),
        "recovery_span": q(wind["recovery_from_reserve"]["span_multiplier"]),

        "reserve_max": q(reserve["max"]),
        "reserve_start": floordiv(q(reserve["max"]) * q(reserve["start_fraction"]),
                                  10000),
        "reserve_low": floordiv(
            q(reserve["max"]) * q(reserve["low_threshold_fraction"]), 10000),
        "reserve_in_round": q(reserve["in_round_recovery_per_tick"]),
        "reserve_between_rounds": q(reserve["between_rounds_recovery"]),
        "sustained_exertion": q(
            reserve["drains"]["sustained_exertion_per_tick_below_low_wind"]["value"]),
        "body_damage_mult": q(reserve["drains"]["body_damage_multiplier"]["value"]),

        "wind_per_ru": q(f["displacement_movement"]["wind_per_ru"]),
        "reserve_per_ru": q(f["displacement_movement"]["reserve_per_ru"]),
        "moves": {},
        "errors": [],
    }

    for m in f["moves"]:
        mid = m["move_id"]
        c["moves"][mid] = {
            "effort": q(m["effort"]),
            # None means "ask the locomotion model", not "free". Decision 0015.
            "wind": None if m.get("wind_cost") is None else q(m["wind_cost"]),
            "reserve": None if m.get("reserve_load") is None else q(m["reserve_load"]),
            "displacement": m.get("cost_model") == "displacement",
        }

    # Canon this model cannot execute, counted rather than assumed. These are
    # the things that would make the two tiers meaningless if they were true.
    if c["reserve_in_round"] != 0:
        c["errors"].append(
            "reserve recovers during a round, which erases the distinction "
            "between getting your breath back and getting your legs back")
    rest = c["recover"].get("rest", 0)
    for state, rate in c["recover"].items():
        if rate > rest:
            c["errors"].append("%s recovers Wind faster than rest" % state)
    for state in NO_RECOVERY:
        if c["recover"].get(state, 0) != 0:
            c["errors"].append("%s recovers Wind, but Decision 0021 says "
                               "working buys none back" % state)
    for a in ACTIONS:
        if a not in c["recover"]:
            c["errors"].append("no Wind recovery rate declared for %r" % a)

    # THE UNITS GUARD. The 2026-08-03 correction, and again on 2026-08-07: a
    # rate authored as a small per-tick decimal that actually carries per-second
    # magnitude refills the whole pool inside a round, and no fighter can tire
    # at any work rate. The numbers look innocent until multiplied by the round.
    round_ticks = 180 * 60
    for state, rate in c["recover"].items():
        if rate * round_ticks > c["wind_max"]:
            c["errors"].append(
                "%s recovers %.1f Wind per 180s round against a pool of %.1f - "
                "a rate that can refill the pool inside one round means nobody "
                "ever tires. This is the units error, twice made."
                % (state, rate * round_ticks / 10000.0, c["wind_max"] / 10000.0))

    if c["ceiling_floor"] + c["ceiling_span"] != 10000:
        c["errors"].append(
            "the Wind ceiling does not reach a full pool at full Reserve, so a "
            "fresh fighter could never be fresh")

    # The inversion that justifies three separate numbers: body work costs less
    # breath and more conditioning than head work of the same effort. If it ever
    # stops being true, `effort` and `wind_cost` have quietly recollapsed into
    # one number and Decision 0021's decoupling is decorative.
    head = c["moves"].get("hook_lead")
    body = c["moves"].get("body_hook_lead")
    if head and body and head["effort"] == body["effort"]:
        if not (body["wind"] < head["wind"] and body["reserve"] > head["reserve"]):
            c["errors"].append(
                "body and head work of equal effort no longer differ in the "
                "two tiers - the three-value model has collapsed")
    return c


def wind_ceiling(c, reserve):
    """Reserve limits how much Wind a fighter can hold. Indirect path one."""
    frac = floordiv(reserve * 10000, c["reserve_max"]) if c["reserve_max"] else 0
    mult = c["ceiling_floor"] + floordiv(c["ceiling_span"] * frac, 10000)
    return floordiv(c["wind_max"] * mult, 10000)


def recovery_rate(c, action, reserve):
    """What one tick of `action` pays back. Indirect path two.

    A drained fighter gets his breath back more slowly, which is what makes a
    late round feel different from an early one even when Wind reads the same
    number.
    """
    base = c["recover"].get(action, 0)
    if base == 0:
        return 0
    frac = floordiv(reserve * 10000, c["reserve_max"]) if c["reserve_max"] else 0
    mult = c["recovery_floor"] + floordiv(c["recovery_span"] * frac, 10000)
    return floordiv(base * mult, 10000)


class UnknownMove(KeyError):
    """An economy that charges nothing for what it does not recognise is not an
    economy. Raised rather than returning zero - see move_cost."""


def move_cost(c, move_id, displacement_ru=0):
    """(wind, reserve) for committing one authored move.

    A displacement-priced move is charged for the ground it actually covers -
    Decision 0014's G1 ruling - and a zero-displacement step costs nothing,
    which is what stops a fighter paying a fee to stand still.

    AN UNKNOWN MOVE RAISES. The first draft returned (0, 0), and the first
    probe written against it passed the ACTION FAMILY ("attack") where a move id
    ("cross_rear") belongs. Every punch was therefore free, and a fighter
    throwing 120 a round finished with a full pool. Nothing failed; the model
    simply reported that boxing is not tiring.

    A silent zero in a resource system is the most expensive default available:
    it looks like the model working and it is the model absent.
    """
    m = c["moves"].get(move_id)
    if m is None:
        raise UnknownMove(
            "%r is not an authored move. Action FAMILIES (%s) say how a tick "
            "recovers; MOVE IDS say what it costs, and they are not "
            "interchangeable." % (move_id, ", ".join(ACTIONS)))
    if m["displacement"]:
        return (floordiv(displacement_ru * c["wind_per_ru"], 10000),
                floordiv(displacement_ru * c["reserve_per_ru"], 10000))
    return m["wind"] or 0, m["reserve"] or 0


def step(c, wind, reserve, action, move_id=None, displacement_ru=0):
    """One tick. Returns (wind, reserve).

    `action` is one of the eight FAMILIES and decides recovery.
    `move_id` is an authored move and decides cost; None means this tick
    commits nothing. They are separate arguments on purpose - collapsing them
    is what made every punch free in the first draft.

    ORDER MATTERS AND IS DELIBERATE:
      1. pay for the move, if this tick commits one;
      2. pay sustained exertion if working below the low-Wind line;
      3. recover, capped by the Reserve-limited ceiling.

    Recovery last means a fighter who spends and rests in the same tick is not
    quietly refunded before he has paid. Paying first also means the low-Wind
    exertion test sees the Wind he actually has after the spend, which is the
    honest reading of "working while already short of breath".
    """
    if action not in ACTIONS:
        raise ValueError("%r is not one of the declared action families: %s"
                         % (action, ", ".join(ACTIONS)))
    if move_id is not None:
        dw, dr = move_cost(c, move_id, displacement_ru)
        wind -= dw
        reserve -= dr

    working = action in NO_RECOVERY
    if working and wind < c["wind_low"]:
        reserve -= c["sustained_exertion"]

    wind += recovery_rate(c, action, reserve)

    if reserve < 0:
        reserve = 0
    if reserve > c["reserve_max"]:
        reserve = c["reserve_max"]
    ceiling = wind_ceiling(c, reserve)
    if wind > ceiling:
        wind = ceiling
    if wind < 0:
        wind = 0
    return wind, reserve


def between_rounds(c, wind, reserve):
    """The corner. Wind comes back substantially; Reserve barely.

    This is the whole two-tier claim in four lines: a fighter walks out for the
    next round breathing again and still not fresh.
    """
    reserve = min(c["reserve_max"], reserve + c["reserve_between_rounds"])
    ceiling = wind_ceiling(c, reserve)
    wind = min(ceiling,
               wind + floordiv((ceiling - wind) * c["wind_between_rounds"], 10000))
    return wind, reserve
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 06:30 UTC | END ]
