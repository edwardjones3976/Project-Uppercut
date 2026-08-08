# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 20:15 UTC | START ]
"""Typed quantities for the First Bell runtime. Decision 0029.

    "If two numbers cannot be legally substituted in boxing, the live runtime
     should not make them trivially substitutable in code."

THREE DEFECTS BUILT THIS FILE, and all three were the same shape: a number that
was numerically valid and semantically wrong.

  - a per-SECOND recovery rate consumed per TICK, twice, which refilled the pool
    inside a round and made fatigue impossible;
  - an authored STRIDE LENGTH billed as per-tick DISPLACEMENT, a 3.9x overcharge;
  - a per-ACTION guard cost charged every TICK the guard was held.

And one more found while fixing the third: suppressing a repeated move id also
suppressed the displacement charge, so movement went free and two fighters
walked for three minutes at 99.7% Wind with nothing raised.

Every one of those passed review because every number involved is a small
decimal. A validator can catch some of them after they are written. A type
makes most of them impossible to write.

SCOPE, DELIBERATELY SMALL. Decision 0029 is explicit: "This is not
authorization to construct a magnificent generic physics-unit framework and
disappear into it for two weeks. Only the types needed by First Bell get
implemented now." So there is no dimensional algebra here, no unit parser, no
inference. There is a fixed list of quantities and a fixed table of the products
that are legal. Anything not in the table raises.

TWO SCALES, AND THE DISTINCTION IS LOAD-BEARING.

  COUNTS      Ticks, Actions, FightSeconds - whole things, not fixed point.
  FIXED       everything else - q10000 on the shared integer contract.

A count times a rate is a plain multiply. A fixed-point value times a
fixed-point rate needs the floor division, because two q10000 values multiplied
carry 10000 twice. Getting that wrong is itself a basis error, so the scale is a
property of the type and the product table applies the right one.

FLOORING, NOT ROUNDING, NOT TRUNCATION. Python's // floors and C++'s / truncates
toward zero. Every division here goes through one named function so the C++ port
has exactly one place to be careful about, which is the same discipline
`UppercutFloorDiv` carries on the other side.
"""

ONE = 10000          # the shared integer contract's scale


def floordiv(a, b):
    """Python's // already floors. Named so the C++ port cannot forget."""
    return a // b


class BasisError(TypeError):
    """Two quantities were combined in a way boxing does not permit.

    A TypeError rather than a ValueError on purpose: the values were fine. The
    meanings were not, and that is a type problem however it is stored.
    """


class UnknownBasis(ValueError):
    """A canon field arrived without a declared basis, and was refused.

    Decision 0029: "Unknown or missing basis fails closed." The alternative is
    a loader that infers a basis from a convenient call site, which is how a
    stride became a displacement.
    """


class Quantity(object):
    """One typed number. Immutable, integer, and unwilling to be another type."""

    __slots__ = ("q",)
    BASIS = None          # human-readable, and what telemetry records
    FIXED = True          # q10000 fixed point, versus a whole count

    def __init__(self, q):
        if isinstance(q, bool) or not isinstance(q, int):
            # bool is an int subclass in Python, and a bout seeded True is a
            # bout nobody meant to run. Same lesson, different file.
            raise BasisError("%s takes an integer, got %r"
                             % (type(self).__name__, q))
        self.q = q

    # ----------------------------------------------------------- arithmetic --

    def _same(self, other, op):
        if type(other) is not type(self):
            raise BasisError(
                "cannot %s %s and %s - they are different bases (%s vs %s). If "
                "this is a real conversion it needs a named function, not an "
                "operator." % (op, type(self).__name__, type(other).__name__,
                               self.BASIS, getattr(other, "BASIS", "?")))

    def __add__(self, other):
        self._same(other, "add")
        return type(self)(self.q + other.q)

    def __sub__(self, other):
        self._same(other, "subtract")
        return type(self)(self.q - other.q)

    def __neg__(self):
        return type(self)(-self.q)

    def __mul__(self, other):
        product = PRODUCTS.get((type(self), type(other)))
        if product is None:
            raise BasisError(
                "%s x %s is not a declared product. Decision 0029 requires "
                "every basis conversion to be explicit and testable; a product "
                "that is not in the table is one nobody has thought about."
                % (type(self).__name__, type(other).__name__))
        if type(self).FIXED and type(other).FIXED:
            return product(floordiv(self.q * other.q, ONE))
        return product(self.q * other.q)

    def __rmul__(self, other):
        raise BasisError(
            "%s cannot be scaled by a bare %s. A dimensionless factor is a "
            "Ratio; anything else is a basis and needs its own type."
            % (type(self).__name__, type(other).__name__))

    # ----------------------------------------------------------- comparison --

    def __eq__(self, other):
        return type(other) is type(self) and other.q == self.q

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        self._same(other, "compare")
        return self.q < other.q

    def __le__(self, other):
        self._same(other, "compare")
        return self.q <= other.q

    def __gt__(self, other):
        self._same(other, "compare")
        return self.q > other.q

    def __ge__(self, other):
        self._same(other, "compare")
        return self.q >= other.q

    def __hash__(self):
        return hash((type(self).__name__, self.q))

    def __bool__(self):
        return self.q != 0

    # ------------------------------------------------------------ reporting --

    def telemetry(self, label):
        """`label=value basis` - Decision 0029's telemetry rule.

        "Integrated event output should record both value and basis where
        ambiguity would otherwise be possible." One opaque `movement_cost` field
        is exactly the ambiguity that hid three defects.
        """
        if self.FIXED:
            return "%s=%d.%04d %s" % (label, self.q // ONE, abs(self.q) % ONE,
                                      self.BASIS)
        return "%s=%d %s" % (label, self.q, self.BASIS)

    def __repr__(self):
        return "%s(%d)" % (type(self).__name__, self.q)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 20:15 UTC | END ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 20:25 UTC | START ]
# ------------------------------------------------------- the counts ---------

class Ticks(Quantity):
    """Whole simulation ticks. 60 to the second, per `clock_model`."""
    BASIS = "ticks"
    FIXED = False


class FightSeconds(Quantity):
    """Whole seconds of fight time. Not real time - the accelerated display
    clock is presentation and reaches nothing here."""
    BASIS = "fight_seconds"
    FIXED = False


class Actions(Quantity):
    """A count of committed actions. One punch is one action, however many
    ticks its animation occupies - which is the whole per-action/per-tick
    distinction that charged a held guard sixty times."""
    BASIS = "actions"
    FIXED = False


# ------------------------------------------------- the fixed-point values ---

class ReachUnits(Quantity):
    """Distance, in reach units. ACTUAL displacement, never a stride and never
    a cap - Decision 0026 Ruling C, and the defect of 2026-08-08."""
    BASIS = "ru"


class Wind(Quantity):
    """Acute breath. Recovers inside a round."""
    BASIS = "wind"


class Reserve(Quantity):
    """Whole-fight conditioning. Does not recover inside a round."""
    BASIS = "reserve"


class Ratio(Quantity):
    """Dimensionless. A fraction, a probability, a multiplier."""
    BASIS = "ratio"


# ------------------------------------------------------------- the rates ----

class ReachUnitsPerTick(Quantity):
    BASIS = "ru/tick"


class WindPerTick(Quantity):
    BASIS = "wind/tick"


class WindPerAction(Quantity):
    BASIS = "wind/action"


class WindPerReachUnit(Quantity):
    BASIS = "wind/ru"


class ReserveLoadPerAction(Quantity):
    BASIS = "reserve/action"


class ReserveLoadPerReachUnit(Quantity):
    """Canon prices locomotion in both tiers, so this exists alongside the
    per-action load Decision 0029 names. Same rule, second resource."""
    BASIS = "reserve/ru"


# --------------------------------------------------- what may multiply what -
#
# THE WHOLE TABLE. If a conversion is not here it raises, and adding a row is a
# reviewable act rather than a line inside a call site. Decision 0029's three
# named products are the first three; the rest are the ones First Bell actually
# performs, and nothing else was added speculatively.
PRODUCTS = {
    (ReachUnits, WindPerReachUnit): Wind,
    (Ticks, WindPerTick): Wind,
    (Actions, WindPerAction): Wind,

    (ReachUnits, ReserveLoadPerReachUnit): Reserve,
    (Actions, ReserveLoadPerAction): Reserve,

    (Ticks, ReachUnitsPerTick): ReachUnits,

    (Wind, Ratio): Wind,
    (Reserve, Ratio): Reserve,
    (ReachUnits, Ratio): ReachUnits,
}
# Both orders, so `rate * distance` reads as naturally as `distance * rate` and
# neither is a trap. Written once and mirrored rather than typed twice.
for (_a, _b), _out in list(PRODUCTS.items()):
    PRODUCTS.setdefault((_b, _a), _out)


# ------------------------------------------------------- named conversions --
#
# Decision 0029: "Conversions between basis types must occur in named functions
# or operators whose dimensional meaning is testable." These are the only ones,
# and each is named for what it means rather than for what it does to the
# number.

def ticks_to_seconds(ticks, tick_rate_hz):
    """Tick count to whole fight seconds, flooring. Partial seconds are not
    seconds; a fighter is not tired for 0.4 of one."""
    if not isinstance(ticks, Ticks):
        raise BasisError("ticks_to_seconds takes Ticks, got %r" % (ticks,))
    if not isinstance(tick_rate_hz, int) or tick_rate_hz <= 0:
        raise UnknownBasis("tick rate must be a positive integer count of "
                           "ticks per second, got %r" % (tick_rate_hz,))
    return FightSeconds(floordiv(ticks.q, tick_rate_hz))


def seconds_to_ticks(seconds, tick_rate_hz):
    if not isinstance(seconds, FightSeconds):
        raise BasisError("seconds_to_ticks takes FightSeconds, got %r"
                         % (seconds,))
    if not isinstance(tick_rate_hz, int) or tick_rate_hz <= 0:
        raise UnknownBasis("tick rate must be a positive integer, got %r"
                           % (tick_rate_hz,))
    return Ticks(seconds.q * tick_rate_hz)


def per_second_to_per_tick(wind_per_second, tick_rate_hz):
    """The 2026-08-03 defect, and the 2026-08-07 defect, as a named function.

    Twice a rate authored per second was consumed per tick, which refilled the
    pool inside a round and meant no fighter could tire at any work rate. There
    is now exactly one way to perform that conversion and it says so in its
    name; anything else raises.
    """
    if not isinstance(wind_per_second, WindPerTick):
        raise BasisError(
            "per_second_to_per_tick takes the per-SECOND rate carried as "
            "WindPerTick's storage, got %r. Author per-second rates as "
            "WindPerTick only after this conversion." % (wind_per_second,))
    if not isinstance(tick_rate_hz, int) or tick_rate_hz <= 0:
        raise UnknownBasis("tick rate must be a positive integer, got %r"
                           % (tick_rate_hz,))
    return WindPerTick(floordiv(wind_per_second.q, tick_rate_hz))


def displacement(travelled_ru):
    """ACTUAL ground covered, refusing a negative and refusing anything else.

    Decision 0029 mutation case 4: "negative distance where the contract
    forbids it". Distance travelled is a magnitude; direction is the range
    runtime's business and it has already had its say by the time this is
    charged.
    """
    if not isinstance(travelled_ru, int) or isinstance(travelled_ru, bool):
        raise BasisError("displacement takes an integer q10000 reach-unit "
                         "count, got %r" % (travelled_ru,))
    if travelled_ru < 0:
        raise UnknownBasis(
            "displacement is a magnitude and %d is negative. A signed step "
            "belongs to the range runtime; by the time a fighter is charged, "
            "the ground is already behind him." % travelled_ru)
    return ReachUnits(travelled_ru)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 20:25 UTC | END ]
