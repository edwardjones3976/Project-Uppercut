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
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
        #   2026-08-08 09:35 UTC | START edit: Decision 0026 hysteresis ]
        # The EXIT from recovery-seeking, distinct from the entry. Read here
        # rather than chosen in the policy, because 0026 requires the
        # thresholds be declared and configurable rather than scattered.
        "wind_recovered": floordiv(
            q(wind["max"]) * q(wind["recovery_exit_fraction"]), 10000),
        # [ ... | 2026-08-08 09:35 UTC | END edit ]
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

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
    #   2026-08-08 09:35 UTC | START edit: Decision 0026 hysteresis ]
    if c["wind_recovered"] <= c["wind_low"]:
        c["errors"].append(
            "the recovery EXIT (%d) is not above the recovery ENTRY (%d), so "
            "recovery intent has no hysteresis and a fighter flickers between "
            "resting and fighting on consecutive ticks - the oscillation "
            "Decision 0026 Ruling B exists to prevent"
            % (c["wind_recovered"], c["wind_low"]))
    if c["wind_recovered"] > c["wind_max"]:
        c["errors"].append(
            "the recovery exit (%d) is above a full pool (%d), so a fighter "
            "could never stop seeking recovery" % (c["wind_recovered"],
                                                   c["wind_max"]))
    # [ ... | 2026-08-08 09:35 UTC | END edit ]

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


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:50 UTC | START edit: Decision 0025 ]
class InvalidState(ValueError):
    """State outside Reserve's authoritative interval, refused not normalised.

    Decision 0025: Reserve is authoritative on the CLOSED interval [0, max].
    Initial, replay, fixture and externally supplied state carrying a Reserve
    outside it is invalid. Quietly clamping such an input would make a corrupt
    save, a bad fixture or a mis-wired caller indistinguishable from an
    exhausted fighter - and the whole point of the ruling is that negative
    Reserve is not "extra tired", it is an invalid hidden state.
    """


def check_state(c, wind, reserve):
    """Decision 0025's input rule. Called on entry to every state transition."""
    if reserve < 0:
        raise InvalidState(
            "Reserve %d is negative. Decision 0025: Reserve is authoritative "
            "on [0, %d], and a negative value is rejected rather than "
            "normalised - it is an invalid state, not a third exhaustion "
            "regime." % (reserve, c["reserve_max"]))
    if reserve > c["reserve_max"]:
        raise InvalidState(
            "Reserve %d exceeds the declared maximum %d. The interval is "
            "closed at both ends; a fighter cannot arrive with more "
            "conditioning than canon declares." % (reserve, c["reserve_max"]))


def saturate_reserve(c, reserve):
    """Clamp to [0, max] IMMEDIATELY after a debit, before anything reads it.

    Decision 0025 step 3. Arithmetic inside a step may cross below zero
    transiently; the stored authoritative value may not, because every
    Reserve-derived formula downstream - the Wind ceiling, the recovery
    multiplier - would then be computed from a fraction canon never authorised
    and would breach its own declared floor.
    """
    if reserve < 0:
        return 0
    if reserve > c["reserve_max"]:
        return c["reserve_max"]
    return reserve
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:50 UTC | END edit ]


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


def step(c, wind, reserve, action, move_id=None, displacement_ru=0,
         telemetry=None, travel_ru=0):
    """One tick. Returns (wind, reserve).

    `telemetry`, if given, is a dict this fills with what the tick REQUESTED as
    opposed to what the balance could absorb (Decision 0025 proof 8). It is an
    out-parameter rather than a second return value or a second function on
    purpose: one implementation of the rule, and callers that do not care are
    unchanged.

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
    check_state(c, wind, reserve)

    reserve_before = reserve
    requested_wind = 0
    requested_reserve = 0

    if move_id is not None:
        dw, dr = move_cost(c, move_id, displacement_ru)
        requested_wind, requested_reserve = dw, dr
        wind -= dw
        reserve -= dr
        # Decision 0025 step 3: saturate IMMEDIATELY, before anything reads it.
        reserve = saturate_reserve(c, reserve)

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
    #   2026-08-08 14:20 UTC | START edit: travel is charged unconditionally ]
    # DECISION 0026 RULING C IS UNCONDITIONAL:
    #
    #     movement_wind_cost = actual_authoritative_displacement_ru * 0.60
    #
    # It does not say "unless he was punching". A tick can both move and commit
    # - a fighter stepping in behind a jab covers ground while he throws - and
    # `move_id` holds exactly one move, so the punch displaced the travel and
    # the ground came free. The first integrated round covered 3.74 reach units
    # and billed 2.34 of them; the missing 1.40 was every step taken on a tick
    # that also threw a punch. Nothing failed. The bout simply reported that
    # walking while punching is free, which is the same silent zero that once
    # made every punch free and is the reason `move_cost` raises.
    #
    # `travel_ru` is therefore charged IN ADDITION, priced by the same
    # per-reach-unit rates, and defaults to zero so every existing caller and
    # every proven parity vector is unchanged.
    if travel_ru:
        tw = floordiv(travel_ru * c["wind_per_ru"], 10000)
        tr = floordiv(travel_ru * c["reserve_per_ru"], 10000)
        requested_wind += tw
        requested_reserve += tr
        wind -= tw
        reserve -= tr
        reserve = saturate_reserve(c, reserve)
    # [ ... | 2026-08-08 14:20 UTC | END edit ]

    working = action in NO_RECOVERY
    exertion = 0
    if working and wind < c["wind_low"]:
        exertion = c["sustained_exertion"]
        reserve -= exertion
        reserve = saturate_reserve(c, reserve)

    # Reserve is now guaranteed inside [0, max], so neither Reserve-derived
    # formula below can see a negative fraction and neither can fall through
    # its authored floor. Decision 0025 makes floor_multiplier and
    # floor_fraction true lower bounds rather than suggestions that disappear
    # when arithmetic underflows.
    wind += recovery_rate(c, action, reserve)

    ceiling = wind_ceiling(c, reserve)
    if wind > ceiling:
        wind = ceiling
    if wind < 0:
        wind = 0

    if telemetry is not None:
        # Decision 0025 proof 8. The fighter ran out of tank; the model should
        # remember what the action DEMANDED. Recording only what the balance
        # could absorb would report a 2.0-load punch as having cost 0.5, and
        # every later analysis of what the fight took out of him would be
        # reading a number the economy invented rather than one it charged.
        requested_total = requested_reserve + exertion
        applied = reserve_before - reserve
        telemetry.update({
            "requested_wind_cost": requested_wind,
            "requested_reserve_load": requested_reserve,
            "sustained_exertion": exertion,
            "requested_reserve_total": requested_total,
            "reserve_applied": applied,
            "reserve_unpaid": requested_total - applied,
            "reserve_saturated": requested_total > applied,
        })
    return wind, reserve


def between_rounds(c, wind, reserve):
    """The corner. Wind comes back substantially; Reserve barely.

    This is the whole two-tier claim in four lines: a fighter walks out for the
    next round breathing again and still not fresh.

    Decision 0025: the incoming state is validated, and the corner's recovery
    saturates at reserve.max rather than carrying a fighter past what canon
    declares he can hold.
    """
    check_state(c, wind, reserve)
    reserve = min(c["reserve_max"], reserve + c["reserve_between_rounds"])
    ceiling = wind_ceiling(c, reserve)
    wind = min(ceiling,
               wind + floordiv((ceiling - wind) * c["wind_between_rounds"], 10000))
    return wind, reserve
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 06:30 UTC | END ]
