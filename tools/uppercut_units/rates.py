# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 20:35 UTC | START ]
"""Canon's rates, typed by the basis canon itself declares. Decision 0029.

    "A loader may normalize authoring representation into typed runtime values;
     it may not infer a basis from a convenient call site."

This is the join between two decisions. Decision 0026 Ruling D made every
stamina source declare its basis in `data/stamina_economy.json`. Decision 0029
makes the loader REFUSE anything that has not. The declaration was worth having
on its own; it is worth much more now that nothing can be loaded around it.

WHAT THIS DELIBERATELY DOES NOT DO. It does not scan, guess, or fall back. There
is a fixed list of the fields First Bell charges, each mapped to the type its
declared basis implies, and a field whose declared basis disagrees with that
mapping is an error rather than a coercion.
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.uppercut_units import quantities as Q     # noqa: E402

ECONOMY = os.path.join("data", "stamina_economy.json")
EFFORT = os.path.join("data", "moves", "generic_sandbox_effort.json")
CLOCK = os.path.join("data", "clock_model.json")

# Which runtime type each declared basis produces, for each field First Bell
# actually charges. The basis string comes from canon; the type comes from here;
# a disagreement is refused rather than reconciled.
EXPECTED = {
    "displacement_movement.wind_per_ru": ("per_reach_unit", Q.WindPerReachUnit),
    "displacement_movement.reserve_per_ru": ("per_reach_unit",
                                             Q.ReserveLoadPerReachUnit),
    "moves[].wind_cost": ("per_action", Q.WindPerAction),
    "moves[].reserve_load": ("per_action", Q.ReserveLoadPerAction),
    "wind.recovery_per_tick_by_action.*": ("per_tick", Q.WindPerTick),
    "reserve.drains.sustained_exertion_per_tick_below_low_wind.value":
        ("per_tick", Q.WindPerTick),
}


def _read(rel):
    with io.open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return json.load(fh)


def _q(v):
    return int(round(float(v) * Q.ONE))


class TypedRates(object):
    """Every rate First Bell charges, carrying its basis in its type."""

    __slots__ = ("wind_per_ru", "reserve_per_ru", "recovery_per_tick",
                 "tick_rate_hz", "declared")

    def __init__(self, wind_per_ru, reserve_per_ru, recovery_per_tick,
                 tick_rate_hz, declared):
        self.wind_per_ru = wind_per_ru
        self.reserve_per_ru = reserve_per_ru
        self.recovery_per_tick = recovery_per_tick
        self.tick_rate_hz = tick_rate_hz
        self.declared = declared

    def movement_wind(self, travelled_ru):
        """The one multiplication that has gone wrong three times.

        `ReachUnits x WindPerReachUnit -> Wind`, and there is no other way to
        get a movement debit out of this object. A stride cannot be passed here
        without first going through `displacement()`, which refuses a negative
        and does not care what the number was called upstream.
        """
        return travelled_ru * self.wind_per_ru

    def movement_reserve(self, travelled_ru):
        return travelled_ru * self.reserve_per_ru


def load(repo=None):
    """Canon's rates, typed. Refuses anything canon has not classified."""
    econ = _read(ECONOMY)
    effort = _read(EFFORT)

    basis = econ.get("source_basis")
    if not basis:
        raise Q.UnknownBasis(
            "stamina_economy declares no source_basis block, so no rate in it "
            "states whether it is charged per tick, per second, per reach-unit, "
            "per action or per round break. Decision 0029: unknown or missing "
            "basis fails closed.")
    sources = basis.get("sources") or {}
    allowed = set(basis.get("allowed") or ())

    declared = {}
    for key, (want, kind) in sorted(EXPECTED.items()):
        got = sources.get(key)
        if got is None:
            raise Q.UnknownBasis(
                "%s is charged by the First Bell runtime and canon declares no "
                "basis for it. A loader that guessed here is how a stride "
                "became a displacement." % key)
        if got not in allowed:
            raise Q.UnknownBasis(
                "%s declares basis %r, which is not one of the allowed bases "
                "%s" % (key, got, ", ".join(sorted(allowed))))
        if got != want:
            raise Q.UnknownBasis(
                "%s declares basis %r but the runtime charges it as %r. One of "
                "the two is wrong and neither may be quietly adapted to the "
                "other." % (key, got, want))
        declared[key] = (got, kind.__name__)

    move = effort["displacement_movement"]
    clock = _read(CLOCK)
    hz = clock["authority"]["tick_rate_hz"]
    if not isinstance(hz, int) or isinstance(hz, bool) or hz <= 0:
        raise Q.UnknownBasis("clock_model declares tick_rate_hz=%r, which is "
                             "not a positive whole number of ticks per second"
                             % (hz,))

    recovery = {a: Q.WindPerTick(_q(v))
                for a, v in econ["wind"]["recovery_per_tick_by_action"].items()
                if not a.startswith("$") and isinstance(v, (int, float))
                and not isinstance(v, bool)}

    return TypedRates(
        wind_per_ru=Q.WindPerReachUnit(_q(move["wind_per_ru"])),
        reserve_per_ru=Q.ReserveLoadPerReachUnit(_q(move["reserve_per_ru"])),
        recovery_per_tick=recovery,
        tick_rate_hz=hz,
        declared=declared,
    )
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 20:35 UTC | END ]
