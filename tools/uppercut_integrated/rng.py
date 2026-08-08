# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 06:20 UTC | START ]
"""Named RNG substreams for the integrated bout. Decision 0022.

THE RULE THIS EXISTS TO MAKE ENFORCEABLE:

    "A subsystem may consume only its own authoritative stream. Adding a
     cosmetic draw or changing policy cadence may not silently move knockdown,
     judging, or contact outcomes."

That is unenforceable against a single shared generator. With one stream, every
draw is a side effect on every other subsystem, and the day someone adds a
sparkle to the crowd is the day a knockdown moves - with a green suite, because
nothing compares those two things. Measured 2026-08-08: eight files in
UppercutCore each carry their own copy of the LCG constants, which is the same
problem wearing the opposite hat.

So ownership is by NAME, derivation is stable and versioned, and the streams are
genuinely independent objects rather than views on one cursor.

DERIVATION. A substream's seed is

    sha256( derivation_version | contract_version | bout_seed | name )

over a length-prefixed encoding, first four bytes big-endian. Length prefixes
matter: without them ("ab" + "c") and ("a" + "bc") would derive the same stream,
which is precisely the aliasing bug the canon pointers were bitten by on
2026-08-07. It is hashed rather than, say, seed+index because Decision 0022 says
"iteration order over maps, actors, or containers may not determine random
ownership" - an index is iteration order wearing a number.

The generator is the project's LCG, unchanged, so a substream behaves exactly
like every draw this codebase has already proven.
"""
import hashlib
import struct

# Bump either of these and every substream in every bout moves. That is the
# intent: the derivation is part of the contract, so changing it is a visible,
# versioned act rather than a silent reshuffle of the fight.
DERIVATION_VERSION = "uppercut-rng-substreams-v1"

LCG_A, LCG_C, LCG_M = 1664525, 1013904223, 2 ** 32

# Decision 0022's initial substreams, in the ruling's own order. Order is for
# human reading only - nothing derives from position, and a test enforces that.
AUTHORITATIVE = (
    "policy_intent",
    "movement_range",
    "evasion_defense",
    "contact_condition",
    "knockdown_recovery",
    "judging_officiating",
)

# "presentation-only randomness, isolated from authority". Named here so that
# isolation is a declared property with a test behind it, rather than a habit.
PRESENTATION = ("presentation",)

SUBSTREAMS = AUTHORITATIVE + PRESENTATION


class UnknownSubstream(KeyError):
    """An unnamed stream is refused, never invented.

    Returning a fresh generator for a typo'd name would hand a subsystem a
    private, undeclared source of randomness that no replay metadata records -
    the exact opposite of what "stable, versioned, and recorded" means.
    """


def is_authoritative(name):
    return name in AUTHORITATIVE


def _field(raw):
    """Length-prefixed, so no two different inputs can concatenate alike."""
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return struct.pack(">I", len(raw)) + raw


def derive_seed(bout_seed, name, contract_version):
    """The substream's starting state. Stable, versioned, order-independent."""
    if name not in SUBSTREAMS:
        raise UnknownSubstream(
            "%r is not a declared substream. Declared: %s. Decision 0022 "
            "requires substream derivation to be stable, versioned and "
            "recorded, so an undeclared name is refused rather than given a "
            "private generator nothing can replay." % (name, ", ".join(SUBSTREAMS)))
    # `isinstance(True, int)` is True in Python, so a bool would sail through
    # as seed 1. The canonicalizer's tests already carry this lesson - "Python's
    # bool is an int subclass, which is a real way to get this wrong" - and a
    # bout seeded True is a bout nobody meant to run.
    if isinstance(bout_seed, bool) or not isinstance(bout_seed, int) \
            or bout_seed < 0:
        raise ValueError("bout seed must be a non-negative integer, got %r"
                         % (bout_seed,))
    payload = (_field(DERIVATION_VERSION) + _field(contract_version)
               + _field(struct.pack(">Q", bout_seed)) + _field(name))
    return struct.unpack(">I", hashlib.sha256(payload).digest()[:4])[0]


class Substream(object):
    """One subsystem's private generator.

    Holds its own state. Two substreams of the same bout cannot perturb each
    other because there is nothing shared to perturb - which is the whole
    mechanism behind Decision 0022's isolation rule.
    """

    __slots__ = ("name", "seed", "state", "draws", "authoritative")

    def __init__(self, name, seed):
        self.name = name
        self.seed = seed
        self.state = seed
        self.draws = 0
        self.authoritative = is_authoritative(name)

    def next_u32(self):
        self.state = (LCG_A * self.state + LCG_C) % LCG_M
        self.draws += 1
        return self.state

    def below(self, bound):
        """A draw in [0, bound). Integer-only, like every other draw here."""
        if bound <= 0:
            raise ValueError("bound must be positive, got %r" % (bound,))
        return self.next_u32() % bound

    def __repr__(self):
        return "<Substream %s seed=%d draws=%d%s>" % (
            self.name, self.seed, self.draws,
            "" if self.authoritative else " NON-AUTHORITATIVE")


class BoutRng(object):
    """Every substream for one bout, reachable only by name.

    There is deliberately no "default" stream and no way to ask for the next
    number without saying who is asking. A subsystem that has not been given a
    name cannot draw at all, which is what stops the shared-cursor habit coming
    back one convenience method at a time.
    """

    def __init__(self, bout_seed, contract_version):
        self.bout_seed = bout_seed
        self.contract_version = contract_version
        self._streams = {}
        for name in SUBSTREAMS:
            self._streams[name] = Substream(
                name, derive_seed(bout_seed, name, contract_version))

    def stream(self, name):
        s = self._streams.get(name)
        if s is None:
            raise UnknownSubstream(
                "%r is not a declared substream. Declared: %s"
                % (name, ", ".join(SUBSTREAMS)))
        return s

    def replay_metadata(self):
        """What a replay must record for this bout's randomness to be rerunnable.

        Decision 0022 requires the derivation be "recorded in replay metadata".
        Sorted by name, never by insertion or iteration order.
        """
        return {
            "derivation_version": DERIVATION_VERSION,
            "contract_version": self.contract_version,
            "bout_seed": self.bout_seed,
            "substreams": [
                {"name": n,
                 "seed": self._streams[n].seed,
                 "authoritative": self._streams[n].authoritative}
                for n in sorted(self._streams)
            ],
        }

    def draw_counts(self):
        return {n: self._streams[n].draws for n in sorted(self._streams)}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 06:20 UTC | END ]
