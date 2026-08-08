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

# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 09:05 UTC | START edit: Decision 0026 ]
# DECISION 0026, RULING A. Decision 0022 partitioned randomness by subsystem
# and stopped one subsystem from moving another's draws. It did not stop two
# fighters inside ONE subsystem from moving each other's: with a single
# `policy_intent` cursor, red thinking one extra time shifts blue's next
# tie-break. That is the coupling 0022 forbids, reappearing one level down.
#
# The namespace is therefore hierarchical - `<domain>/<owner>` - where owner is
# a stable authority identity. Never an array index, never declaration order:
# "an index is iteration order wearing a number" was already the reason
# derivation hashes the name, and a participant's slot in a list is the same
# mistake at the participant level.
SCOPE_SEPARATOR = "/"

# Domains where each fighter draws independently and their draw counts have no
# reason to stay in step. These may ONLY be requested with an owner; asking for
# the bare domain raises, because a bare cursor is the thing being removed.
FIGHTER_LOCAL = (
    "policy_intent",
    "movement_range",
    "evasion_defense",
)

# Domains whose randomness belongs to the authority that actually makes the
# result - an interaction, a judge, a referee - rather than to a fighter.
# 0026 permits child streams or key-derived draws; these are child streams,
# derived on demand because an interaction identity is a runtime fact.
OWNER_SCOPED = (
    "contact_condition",
    "knockdown_recovery",
    "judging_officiating",
    "presentation",
)

SCOPABLE = FIGHTER_LOCAL + OWNER_SCOPED


class UnscopedDraw(KeyError):
    """A fighter-local domain was asked for without saying which fighter.

    Refused rather than served, because the served version is exactly the
    shared mutable cursor Decision 0026 exists to delete. The error names the
    participants so the fix is obvious and nobody is tempted to route around it.
    """


def scoped(domain, owner):
    """The full stream name. One place, so callers cannot spell it two ways."""
    if SCOPE_SEPARATOR in str(owner):
        raise ValueError(
            "owner %r contains %r, which would make two different (domain, "
            "owner) pairs spell the same stream name" % (owner, SCOPE_SEPARATOR))
    return "%s%s%s" % (domain, SCOPE_SEPARATOR, owner)


def split_scope(name):
    """(domain, owner) for a scoped name; (name, None) for a bare one."""
    if SCOPE_SEPARATOR in name:
        domain, owner = name.split(SCOPE_SEPARATOR, 1)
        return domain, owner
    return name, None
# [ ... | 2026-08-08 09:05 UTC | END edit ]


class UnknownSubstream(KeyError):
    """An unnamed stream is refused, never invented.

    Returning a fresh generator for a typo'd name would hand a subsystem a
    private, undeclared source of randomness that no replay metadata records -
    the exact opposite of what "stable, versioned, and recorded" means.
    """


def is_authoritative(name):
    # Scoping does not change authority: `policy_intent/red_corner` is as
    # authoritative as `policy_intent` was, and `presentation/crowd` is as
    # powerless as `presentation`. Authority is a property of the domain.
    return split_scope(name)[0] in AUTHORITATIVE


def _field(raw):
    """Length-prefixed, so no two different inputs can concatenate alike."""
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return struct.pack(">I", len(raw)) + raw


def derive_seed(bout_seed, name, contract_version):
    """The substream's starting state. Stable, versioned, order-independent."""
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 09:10 UTC | START edit: Decision 0026 ]
    # The DOMAIN must be declared; the OWNER need not be, because owners are
    # runtime identities - a participant slot, an interaction, a judge. What is
    # enforced is that the owner is a stable non-empty identity and that the
    # whole name goes into the hash as one length-prefixed field, so
    # ("policy_intent", "red") and ("policy_int", "ent/red") cannot alias.
    domain, owner = split_scope(name)
    if domain not in SUBSTREAMS:
        raise UnknownSubstream(
            "%r is not a declared substream domain. Declared: %s. Decision 0022 "
            "requires substream derivation to be stable, versioned and "
            "recorded, so an undeclared name is refused rather than given a "
            "private generator nothing can replay." % (domain, ", ".join(SUBSTREAMS)))
    if owner is not None and (not owner or domain not in SCOPABLE):
        raise UnknownSubstream(
            "%r cannot be scoped to an owner, or the owner is empty. Scopable "
            "domains: %s" % (domain, ", ".join(SCOPABLE)))
    if owner is None and domain in FIGHTER_LOCAL:
        raise UnscopedDraw(
            "%r is fighter-local under Decision 0026 and has no bare cursor. "
            "Ask for %s instead - a shared cursor is exactly what the ruling "
            "removed, and handing one back on request would remove it in name "
            "only." % (domain, scoped(domain, "<participant>")))
    # [ ... | 2026-08-08 09:10 UTC | END edit ]
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
        """A draw in [0, bound), UNBIASED. Integer-only, deterministic.

        Plain `next_u32() % bound` is biased whenever bound does not divide
        2**32: the low residues occur once more often than the high ones. For
        bound=3 the skew is about one part in 1.4 billion and nobody would ever
        see it; for a bound near 2**31 it approaches 3:2, and "pick one of two
        openings" is exactly the shape of decision a boxing policy makes.

        The frozen phases use plain modulo and MUST keep doing so - their
        proofs are byte-identity against streams already taken. This is a new
        versioned contract, so it starts correct instead of inheriting a bias
        nobody would choose on purpose.

        Rejection is deterministic: same state, same rejections, same result.
        The loop is bounded in expectation by two draws and cannot spin
        forever, since at most one whole `bound`-sized block is ever discarded.
        """
        if not isinstance(bound, int) or isinstance(bound, bool) or bound <= 0:
            raise ValueError("bound must be a positive integer, got %r" % (bound,))
        if bound == 1:
            # Still consumes a draw. A subsystem whose stream advances only
            # sometimes would desynchronise from its own replay.
            self.next_u32()
            return 0
        limit = LCG_M - (LCG_M % bound)      # largest exact multiple of bound
        while True:
            x = self.next_u32()
            if x < limit:
                return x % bound

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

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 09:15 UTC | START edit: Decision 0026 ]
    def __init__(self, bout_seed, contract_version, participants=()):
        """`participants` are the bout's stable authority identities.

        They come from the contract's initial state, not from a runtime array,
        because Decision 0026 says "runtime array position is not authority".
        Declaration ORDER is deliberately not used for anything: the seeds are
        derived from the identity string alone, so shuffling this tuple is a
        no-op, and a test says so.
        """
        self.bout_seed = bout_seed
        self.contract_version = contract_version
        self.participants = tuple(participants)
        if len(set(self.participants)) != len(self.participants):
            raise ValueError(
                "participant identities must be unique, got %r. Two fighters "
                "sharing an identity would share a stream, which is the whole "
                "thing this is here to prevent." % (self.participants,))
        self._streams = {}
        for name in SUBSTREAMS:
            if name in FIGHTER_LOCAL:
                # No bare cursor is ever created, so none can be handed out by
                # accident. The absence is the enforcement.
                for who in self.participants:
                    self._materialise(scoped(name, who))
            else:
                self._materialise(name)

    def _materialise(self, name):
        self._streams[name] = Substream(
            name, derive_seed(self.bout_seed, name, self.contract_version))
        return self._streams[name]

    def stream(self, domain, owner=None):
        """One stream, by domain and - where the domain demands it - by owner.

        An owner-scoped stream for a shared-interaction domain is derived on
        first request, because interaction, judge and referee identities are
        runtime facts rather than bout-setup facts. It is recorded in replay
        metadata from that moment, so nothing draws from a stream a replay
        cannot reconstruct.
        """
        name = domain if owner is None else scoped(domain, owner)
        s = self._streams.get(name)
        if s is not None:
            return s
        # derive_seed carries the refusals; calling it is how they are enforced
        # in one place rather than restated here.
        base, who = split_scope(name)
        if base not in SUBSTREAMS:
            raise UnknownSubstream(
                "%r is not a declared substream domain. Declared: %s"
                % (base, ", ".join(SUBSTREAMS)))
        if who is None and base in FIGHTER_LOCAL:
            raise UnscopedDraw(
                "%r is fighter-local under Decision 0026. Name the owner: "
                "stream(%r, <participant>). Known participants: %s"
                % (base, base, ", ".join(self.participants) or "none declared"))
        if who is not None and base in FIGHTER_LOCAL \
                and self.participants and who not in self.participants:
            raise UnknownSubstream(
                "%r is not a declared participant of this bout (%s). A "
                "fighter-local stream for someone who is not in the bout is a "
                "typo with a private generator behind it."
                % (who, ", ".join(self.participants)))
        return self._materialise(name)
    # [ ... | 2026-08-08 09:15 UTC | END edit ]

    def replay_metadata(self):
        """What a replay must record for this bout's randomness to be rerunnable.

        Decision 0022 requires the derivation be "recorded in replay metadata".
        Sorted by name, never by insertion or iteration order.
        """
        return {
            "derivation_version": DERIVATION_VERSION,
            "contract_version": self.contract_version,
            "bout_seed": self.bout_seed,
            # Sorted, so the recorded participant set is a set and not a
            # transcript of how somebody happened to list them.
            "participants": sorted(self.participants),
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
