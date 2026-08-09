# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:00 UTC | START ]
"""Observable CPU policy for the integrated bout. Decision 0022, R4 step 3.

A MEDIOCRE BOXER WHO OBEYS BOXING LOGIC, on purpose. No search, no learning, no
opponent model, no score reading, no prediction. The First Bell instrument has
to be explainable before it is good, because a fight nobody can explain cannot
be tuned - it can only be admired or complained about.

THREE LAYERS, and they are genuinely separate things:

    strategic   slow-changing intention        "I want to be inside"
    tactical    the immediate problem          "he is coming, hold and counter"
    execution   the exact legal action         "lead hook"

DECISION IS NOT ACTION. A fighter may decide he wants offense and execute an
advance, or a hold, or nothing at all. That gap is the whole reason
`aggression_bias` does not become a punch vending machine: aggression moves the
desire to seek initiative, initiative describes the tactical relationship, and
the action is the physical answer to the situation actually in front of him.

WHAT IT MAY SEE. Only `Observation`, which carries observable or legally known
state. There is no field for the scorecard, for the opponent's exact condition,
or for what the opponent is about to do - not because the policy politely
declines to read them, but because there is nothing to read.

WHAT RANDOMNESS IT MAY TOUCH. Exactly one substream, handed in directly. The
policy never receives a `BoutRng`, so contact, defense, knockdown, judging and
presentation draws are not merely off-limits, they are unreachable: a
`Substream` holds no reference to its siblings. Randomness breaks ties between
tactically equivalent options and decides nothing else.
"""

# ---------------------------------------------------------------- strategy ---

SEEK_PREFERRED_RANGE = "SEEK_PREFERRED_RANGE"
PRESSURE = "PRESSURE"
COUNTER = "COUNTER"
RECOVER = "RECOVER"
PROTECT_REGION = "PROTECT_REGION"
ESCAPE_ROPES = "ESCAPE_ROPES"
EXPLOIT_CONDITION = "EXPLOIT_CONDITION"
MANAGE_CLOCK = "MANAGE_CLOCK"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: a man who cannot punch from here ]
# SEEK_PREFERRED_RANGE is "I am not where I like to be". This is a different and
# harder sentence: "there is no punch in the world from where I am standing."
# They were the same intent until a twelve-round fight was decided by the
# difference - two men who preferred a band canon authors no punch from, each
# holding his preference, neither able to land, 3,174 punches into a gate that
# refused every one. A fighter with nothing to throw is not seeking a
# preference; he is looking for the fight.
FIND_WORKING_RANGE = "FIND_WORKING_RANGE"

STRATEGIC = (SEEK_PREFERRED_RANGE, PRESSURE, COUNTER, RECOVER, PROTECT_REGION,
             ESCAPE_ROPES, EXPLOIT_CONDITION, MANAGE_CLOCK, FIND_WORKING_RANGE)
# [ ... | 2026-08-09 02:05 UTC | END edit: a man who cannot punch from here ]

# ---------------------------------------------------------------- tactical ---

OBSERVE = "Observe"
HOLD_POSITION = "HoldPosition"
REST = "Rest"
MICRO_ADJUST = "MicroAdjust"
ADVANCE = "Advance"
RETREAT = "Retreat"
GUARD = "Guard"
EVADE = "Evade"
ATTACK = "Attack"
# Reserved and deliberately NOT implemented. Decision: First Bell does not need
# a feint, and a tactic that exists in the enum but never in the logic is a
# promise the stream would keep making and never keeping.
FEINT_LATER = "FeintLater"

TACTICAL = (OBSERVE, HOLD_POSITION, REST, MICRO_ADJUST, ADVANCE, RETREAT,
            GUARD, EVADE, ATTACK)

# ----------------------------------------------------------------- reasons ---

R_SEEK_PREFERRED_RANGE = "SEEK_PREFERRED_RANGE"
R_NO_LEGAL_ATTACK = "NO_LEGAL_ATTACK"
R_HOLD_GOOD_RANGE = "HOLD_GOOD_RANGE"
R_RECOVER_WIND = "RECOVER_WIND"
R_PROTECT_DAMAGED_BODY = "PROTECT_DAMAGED_BODY"
R_PRESSURE_ROPES = "PRESSURE_ROPES"
R_PUNISH_RECOVERY = "PUNISH_RECOVERY"
R_PUNISH_REPEATED_JAB = "PUNISH_REPEATED_JAB"
R_EXIT_BAD_RANGE = "EXIT_BAD_RANGE"
R_ATTACK_OPEN_LANE = "ATTACK_OPEN_LANE"
R_AVOID_OVERCOMMIT = "AVOID_OVERCOMMIT"
R_ESCAPE_ROPES = "ESCAPE_ROPES"
R_DEFEND_INCOMING = "DEFEND_INCOMING"
R_HAND_UNAVAILABLE = "HAND_UNAVAILABLE"
R_STILL_RECOVERING = "STILL_RECOVERING"
R_MANAGE_CLOCK = "MANAGE_CLOCK"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:10 UTC | START edit: F2 ]
# Added because the first integrated round found its absence. There was a
# reason code for leaving a bad RANGE and none for leaving to BREATHE, so a
# tired fighter with a man in front of him held position - and held it for 165
# seconds, at half the recovery rate, choosing "recover" 9,317 times and never
# once resting. The gap was not in the numbers; it was a sentence boxing knows
# and the policy could not say.
#
# SUPERSEDED THE SAME DAY by Decision 0026 Ruling B, which named the behaviour
# properly and asked for four codes rather than one. MAKE_ROOM_TO_BREATHE is
# kept as the alias of SEEK_RECOVERY_SPACE rather than deleted, because it
# appears in the 2026-08-08 diagnostic write-up and a reader tracing that
# document should land somewhere rather than nowhere.
R_SEEK_RECOVERY_SPACE = "SEEK_RECOVERY_SPACE"
R_REST_WHEN_SAFE = "REST_WHEN_SAFE"
R_RECOVERY_DENIED = "RECOVERY_DENIED"
R_RECOVERY_INTERRUPTED = "RECOVERY_INTERRUPTED"
R_MAKE_ROOM_TO_BREATHE = R_SEEK_RECOVERY_SPACE
# [ ... | 2026-08-08 08:10 UTC | END edit ]

# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: one sentence the policy could not say ]
# A code for "my preferred band has no punch in it" was drafted here and
# deliberately NOT kept. `_refuse_dead_preference` now makes that state
# unconstructable, so the code could never fire, and this module's own rule
# about `FEINT_LATER` applies to reasons as well as tactics: a name in the enum
# that never appears in the logic is a promise the stream keeps making and never
# keeping. The condition is refused at the door instead of narrated in a log.
#
# CONTINUE_COMMITMENT is the tick between decisions. Canon's
# `reaction.decision_interval_ticks` means a CPU reconsiders every fourth tick,
# not that he stands still on the other three: a stride keeps being delivered,
# a punch keeps travelling, and the row in the stream says which of those it is.
R_CONTINUE_COMMITMENT = "CONTINUE_COMMITMENT"
# [ ... | 2026-08-09 02:05 UTC | END edit: one sentence the policy could not say ]

REASONS = (R_SEEK_PREFERRED_RANGE, R_NO_LEGAL_ATTACK, R_HOLD_GOOD_RANGE,
           R_RECOVER_WIND, R_PROTECT_DAMAGED_BODY, R_PRESSURE_ROPES,
           R_PUNISH_RECOVERY, R_PUNISH_REPEATED_JAB, R_EXIT_BAD_RANGE,
           R_ATTACK_OPEN_LANE, R_AVOID_OVERCOMMIT, R_ESCAPE_ROPES,
           R_DEFEND_INCOMING, R_HAND_UNAVAILABLE, R_STILL_RECOVERING,
           R_MANAGE_CLOCK, R_SEEK_RECOVERY_SPACE, R_REST_WHEN_SAFE,
           R_RECOVERY_DENIED, R_RECOVERY_INTERRUPTED, R_CONTINUE_COMMITMENT)

# The DOMAIN this policy is allowed to touch. Decision 0026 made the stream
# fighter-local, so the name a caller hands in is `policy_intent/<participant>`
# and the check below is on the domain, not on the whole string - otherwise the
# guard would reject exactly the streams the ruling requires.
POLICY_STREAM = "policy_intent"
POLICY_DOMAIN = POLICY_STREAM


class PolicyError(ValueError):
    """The policy was asked to decide from something it may not use."""


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: canon's bands, handed in ]
class Bands(object):
    """Canon's range vocabulary, as both fighters know it. Built, never copied.

    THIS REPLACES A HAND-WRITTEN TUPLE. `BANDS = ("clinch", "inside", "mid",
    "outside", "out_of_range")` used to sit in this module as a second opinion
    about `data/movement_model.json`, next to `BY_BAND`, which was a second
    opinion about `data/moves/generic_sandbox_moves.json`. One of those two
    copies cost the project a zero-contact fight; there is no reason to keep the
    other and wait.

    The caller builds exactly one of these per bout, from the single authority:

        P.Bands(RANGE.band_order(range_pack),
                RANGE.bands_without_offence(range_pack, C.PUNCHES))

    `order` is closest first, which is the only thing the policy needs geometry
    for: "closer" and "further" are decisions, distances are the range
    subsystem's business.

    `without_offence` is the fact that had no name until today. A fighter knows
    the ranges he cannot work from - that knowledge is why he stands where he
    stands - and a POLICY that does not know it will happily hold a preference
    that can never produce a punch. Under today's canon that tuple is
    ("clinch", "outside", "out_of_range"); whether `outside` SHOULD be in it is
    an open Director question and nothing here pre-empts the answer.
    """

    __slots__ = ("order", "without_offence")

    def __init__(self, order, without_offence=()):
        order = tuple(order)
        if not order:
            raise PolicyError(
                "a bout with no range bands is not a bout. Canon declares "
                "them; this is built from canon, never written here.")
        if len(set(order)) != len(order):
            raise PolicyError("duplicate band in %r - band order is authority "
                              "and an ambiguous one is not" % (order,))
        for band in order:
            if not isinstance(band, str) or not band:
                raise PolicyError("band names must be non-empty strings, got "
                                  "%r" % (band,))
        without = tuple(without_offence)
        stray = [b for b in without if b not in order]
        if stray:
            raise PolicyError(
                "%s named as having no offence but not declared a band at all. "
                "A typo and a punch-less band are different sentences and only "
                "one of them is a fight." % ", ".join(sorted(stray)))
        if len(without) >= len(order):
            raise PolicyError(
                "every band this vocabulary knows is punch-less, so no fighter "
                "could ever throw anything anywhere. Refused here rather than "
                "discovered after twelve rounds of it.")
        self.order = order
        self.without_offence = without

    def has_offence(self, band):
        return band in self.order and band not in self.without_offence

    def __repr__(self):
        return "<Bands %s, no offence from %s>" % (
            ",".join(self.order), ",".join(self.without_offence) or "-")


# The regions a boxer means by "the body". Canon names no region `body` - it
# names `torso_upper` and `torso_lower` - and the branch below used to test the
# literal string "body", which no contact could ever put in the set. These are
# canon's own ids, grouped under the word the sport uses, so a typo is a name
# error at import rather than a branch that silently never fires.
BODY_REGIONS = ("torso_upper", "torso_lower")
# [ ... | 2026-08-09 02:05 UTC | END edit: canon's bands, handed in ]


class Observation(object):
    """Everything the policy may know, and nothing else.

    `__slots__` is the enforcement, not a micro-optimisation: a field that does
    not exist cannot be read, so "the policy does not consult the scorecard"
    stops being a promise and becomes a property of the type. Adding
    `opponent_wind` here would be a visible, reviewable act rather than a line
    buried in a decision branch.

    Everything about the opponent is what a fighter could actually SEE - where
    he is, what he is doing right now, what he has been throwing. Never his
    exact Wind, never his condition totals, never his next action.
    """

    __slots__ = (
        # own state, legally known to oneself
        "wind_fraction", "reserve_fraction", "wind_is_low", "wind_is_exhausted",
        "hands_available", "in_recovery", "recovery_ticks_left",
        "damaged_regions", "hurt",
        # Decision 0026 Ruling B. `recovery_seeking` is the fighter's own
        # standing intent, which is legally known to himself and is what makes
        # the hysteresis a property of the fighter rather than of the tick.
        # `wind_is_recovered` is the declared EXIT condition, read from canon.
        "recovery_seeking", "wind_is_recovered",
        # position, observable
        "range_band", "preferred_band", "on_ropes", "cornered",
        # the opponent, observable only
        "opponent_band", "opponent_committed", "opponent_recovering",
        "opponent_advancing", "opponent_recent_moves", "incoming_attack",
        "opponent_on_ropes",
        # the clock, which both fighters can see
        "round_number", "ticks_left_in_round",
        # one's own recent history
        "own_recent_moves", "consecutive_failed_attacks",
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
        #   2026-08-09 02:05 UTC | START edit: offence legality arrives by the
        #   front door ]
        # WHAT CANON AUTHORS FROM THIS BAND, and the band vocabulary it belongs
        # to. Both are supplied by the caller from the single authority
        # (`RANGE.throwable_from` / `RANGE.band_order` /
        # `RANGE.bands_without_offence`) rather than derived here, and both
        # arrive THROUGH the observation rather than beside it, because this
        # class is the declared gate through which the policy learns anything
        # about the world. A range pack handed straight to `decide()` would be a
        # second channel of truth, which is the exact defect `BY_BAND` was.
        #
        # `throwable_here` is what canon authors for the band the fighter is
        # standing in, intersected with the bout's own punch vocabulary. It is
        # NOT yet filtered by hand availability - `legal_attacks()` does that,
        # because which hands work is the fighter's business and which punches
        # exist at this distance is canon's.
        "throwable_here", "bands",
        # [ ... | 2026-08-09 02:05 UTC | END edit ]
    )

    # Facts with no sensible default. A missing band vocabulary is not "no
    # bands" and a missing legality answer is not "nothing is legal": both would
    # produce a fighter who never punches, which is precisely the failure this
    # field exists to end, arrived at silently instead of loudly.
    REQUIRED = ("throwable_here", "bands")

    def __init__(self, **kw):
        unknown = set(kw) - set(self.__slots__)
        if unknown:
            raise PolicyError(
                "the policy was handed %s, which it may not see. If this is "
                "genuinely observable, add it to Observation deliberately."
                % ", ".join(sorted(unknown)))
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: required, not defaulted ]
        missing = [k for k in self.REQUIRED if k not in kw]
        if missing:
            raise PolicyError(
                "an Observation must carry %s. These come from canon through "
                "the range authority (RANGE.throwable_from / band_order / "
                "bands_without_offence) and there is no honest default for "
                "them: defaulting to 'nothing is throwable' builds a fighter "
                "who stands still for twelve rounds and never says why."
                % ", ".join(missing))
        if isinstance(kw["throwable_here"], str):
            raise PolicyError(
                "throwable_here is a VOCABULARY of move ids, got the string "
                "%r, which iterates as characters and would answer 'nothing is "
                "legal here'." % (kw["throwable_here"],))
        if not isinstance(kw["bands"], Bands):
            raise PolicyError(
                "bands must be a policy.Bands built from the range authority, "
                "got %r. A bare tuple would lose which bands have no offence, "
                "which is the fact a twelve-round stalemate turned on."
                % type(kw["bands"]))
        # [ ... | 2026-08-09 02:05 UTC | END edit: required, not defaulted ]
        defaults = {
            "wind_fraction": 10000, "reserve_fraction": 10000,
            "wind_is_low": False, "wind_is_exhausted": False,
            "hands_available": ("lead", "rear"), "in_recovery": False,
            "recovery_ticks_left": 0, "damaged_regions": (), "hurt": False,
            "recovery_seeking": False, "wind_is_recovered": True,
            "range_band": "mid", "preferred_band": "mid", "on_ropes": False,
            "cornered": False, "opponent_band": "mid",
            "opponent_committed": False, "opponent_recovering": False,
            "opponent_advancing": False, "opponent_recent_moves": (),
            "opponent_on_ropes": False,
            "incoming_attack": False, "round_number": 1,
            "ticks_left_in_round": 10800, "own_recent_moves": (),
            "consecutive_failed_attacks": 0,
        }
        defaults.update(kw)
        for k, v in defaults.items():
            setattr(self, k, v)


class Decision(object):
    """What was decided, what will be done, and why - always all three."""

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: a decision that renews nothing ]
    # `renews_intent` is FALSE on the ticks between decisions, and it is the
    # whole contract of canon's `reaction.decision_interval_ticks`. A fighter
    # who decided to step forward is still stepping forward three ticks later;
    # he is not deciding to step forward again. Without this flag the caller
    # cannot tell "advance" from "advance AGAIN", and re-owing a whole authored
    # stride on every tick while the displacement cap can deliver a quarter of
    # one is how footwork becomes a slide instead of a step.
    __slots__ = ("strategic", "tactical", "execution", "reason", "initiative",
                 "renews_intent")

    def __init__(self, strategic, tactical, execution, reason, initiative,
                 renews_intent=True):
        if strategic not in STRATEGIC:
            raise PolicyError("unknown strategic intent %r" % (strategic,))
        if tactical not in TACTICAL:
            raise PolicyError("unknown tactical answer %r" % (tactical,))
        if reason not in REASONS:
            raise PolicyError("unknown reason code %r" % (reason,))
        self.strategic = strategic
        self.tactical = tactical
        self.execution = execution
        self.reason = reason
        self.initiative = initiative
        self.renews_intent = bool(renews_intent)
    # [ ... | 2026-08-09 02:05 UTC | END edit: a decision that renews nothing ]

    def as_row(self):
        """The marker-stream shape. Every decision is explainable in the log."""
        return "%s|%s|%s|%s|%d" % (self.strategic, self.tactical,
                                   self.execution or "-", self.reason,
                                   self.initiative)

    def __repr__(self):
        return "<Decision %s>" % self.as_row()


class Profile(object):
    """A fighter's dispositions. Not a skill level and not a difficulty tier.

    `aggression_bias` moves the DESIRE TO SEEK INITIATIVE. It is deliberately
    not a probability of attacking: a tired aggressive fighter still wants
    initiative and may still choose to rest, because attacking now is poor
    boxing. Keeping those separate is what lets judges later score effective
    aggression rather than button-mashing.
    """

    __slots__ = ("aggression_bias", "preferred_band")

    def __init__(self, aggression_bias=5000, preferred_band="mid"):
        if not 0 <= aggression_bias <= 10000:
            raise PolicyError("aggression_bias is q10000, got %r"
                              % (aggression_bias,))
        self.aggression_bias = aggression_bias
        self.preferred_band = preferred_band


# What each hand can throw. An unavailable hand removes its moves entirely -
# a fighter with a damaged lead does not "prefer not to" jab, he cannot.
#
# THIS IS THE ONE TABLE LEFT, and it is not a second opinion about canon: canon
# authors each move's `hand`, and this says which of those a fighter's own body
# can still produce. It answers a question about the man; `throwable_here`
# answers a question about the distance. They are different questions, and the
# reason there used to be a bug is that the second one had two answers.
BY_HAND = {
    "lead": ("jab_lead", "hook_lead", "uppercut_lead", "body_hook_lead"),
    "rear": ("cross_rear", "hook_rear", "uppercut_rear", "overhand_rear",
             "body_straight_rear"),
}

# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: D1/D2 - BY_BAND deleted ]
# `BY_BAND` STOOD HERE and is gone. It was a hand-authored table of which punch
# may be chosen from which band, and `data/moves/generic_sandbox_moves.json`
# already authors exactly that through each move's `range_band`, which
# `punch_model.range_gate.band_source` names as the authority and
# `RANGE.in_band` enforces at the moment a punch resolves. Two authorities, and
# they disagreed in seven places: from `outside` and `clinch` EVERY punch this
# table offered was refused by the gate, 0 legal of 2 and 0 of 3. A fight is
# what happened in between - 3,174 punches thrown, zero contacts, twelve rounds,
# 120-120.
#
# `BANDS` stood here too, a hand-copy of canon's band keys and their order, and
# is likewise gone: `Bands.order` arrives from `RANGE.band_order`.
#
# Nothing replaced either table inside this module. The set of punches available
# from where a fighter stands now arrives on the observation, computed once by
# the caller from `RANGE.throwable_from(range_pack, band, C.PUNCHES)` - which
# iterates the BOUT'S OWN punch vocabulary, so the eight-selectable-versus-five-
# flyable ghost punches (D2) cannot be selected either. A chooser and a gate
# that read one sentence cannot disagree about it.


def _band_index(band, bands):
    try:
        return bands.order.index(band)
    except ValueError:
        raise PolicyError(
            "unknown range band %r - canon declares %s"
            % (band, ", ".join(bands.order)))


def legal_attacks(obs):
    """Every attack this fighter could actually throw right now.

    Intersection of what CANON authors from this distance (supplied on the
    observation by the range authority) and what this fighter's available hands
    can still produce. Returned sorted, so the option set never depends on
    iteration order - the same rule Decision 0022 states for random ownership.

    An empty result is a real answer and a serious one: it means there is no
    punch in the world from where this man is standing, and `decide()` treats it
    as the emergency it is rather than as a shrug.
    """
    from_band = set(obs.throwable_here)
    from_hands = set()
    for hand in obs.hands_available:
        if hand not in BY_HAND:
            raise PolicyError(
                "%r is not a hand this policy knows (%s). An unrecognised hand "
                "would silently contribute no punches, and 'unknown' must "
                "never quietly mean 'nothing'."
                % (hand, ", ".join(sorted(BY_HAND))))
        from_hands.update(BY_HAND[hand])
    return tuple(sorted(from_band & from_hands))
# [ ... | 2026-08-09 02:05 UTC | END edit: D1/D2 - BY_BAND deleted ]


def _tie_break(options, stream):
    """Choose among tactically equivalent options, and ONLY among those.

    The stream is a single Substream. There is no path from it to contact,
    judging or presentation randomness, so this cannot reach a draw it does not
    own even by accident.
    """
    if not options:
        return None
    if stream is None:
        return options[0]
    _require_policy_stream(stream)
    return options[stream.below(len(options))]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 11:35 UTC | START edit: Decision 0026 ]
def _require_policy_stream(stream):
    """The ownership check, in one place and applied before any draw.

    IT USED TO LIVE ONLY IN `_tie_break`, AND THAT WAS A HOLE. Branch 11 draws
    `stream.below(10000)` directly to decide whether to spend, and that call
    never passed through the check - so a caller who handed the policy the
    contact stream would have had it consumed rather than refused, on any tick
    that reached branch 11. Found by a Decision 0026 test that stopped raising
    for the wrong reason: the assertion was right, the coverage was not.

    Domain, not full name: `policy_intent/red_corner` is the shape Ruling A
    requires, and a whole-string comparison would reject exactly the streams
    the ruling mandates.
    """
    if stream is None:
        return
    name = getattr(stream, "name", None)
    domain = name.split(SCOPE_SEP, 1)[0] if isinstance(name, str) else None
    if domain != POLICY_DOMAIN:
        raise PolicyError(
            "the policy was handed the %r stream. It may consume only %r/<owner> "
            "- a policy that can reach contact or judging randomness is a "
            "policy that can be accused of reading them."
            % (name if name is not None else stream, POLICY_DOMAIN))
    if name == POLICY_DOMAIN:
        raise PolicyError(
            "the policy was handed the unscoped %r cursor. Decision 0026 makes "
            "policy randomness fighter-local: one fighter thinking an extra "
            "time must not move the other's tie-break." % POLICY_DOMAIN)


SCOPE_SEP = "/"
# [ ... | 2026-08-08 11:35 UTC | END edit ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: D7 - a CPU may be fast; it may not be instant ]
class Cadence(object):
    """Canon's reaction rules, READ. `data/cpu_decision_model.json`, `reaction`.

    That file has been in `contract.CANON` and hashed into every integrated
    stream header since the contract existed, and nothing ever opened it. It
    authors two numbers and they are not the same number:

        decision_interval_ticks  4   HOW OFTEN a fighter reconsiders.
        floor_ticks              6   HOW OLD the thing he reacts to must be.

    THE INTERVAL is cadence. Between decisions a fighter is not frozen: his
    stride keeps being delivered, his punch keeps travelling, his recovery keeps
    running down. What stops is the renewal of intent - see
    `Decision.renews_intent` and `continue_previous`. Deciding every tick is not
    "more responsive", it is a fighter who re-owes a whole authored stride sixty
    times a second while the authored displacement cap can pay out a quarter of
    one, which is a slide rather than a step. Canon's own numbers say the same
    thing twice: a 0.55 ru stride at a 0.14 ru/frame cap takes four ticks to
    deliver, and the authored decision interval is four ticks.

    THE FLOOR is reaction latency, and it is a different rule with a different
    justification in canon's own words: *"an instant answer is indistinguishable
    from input reading"*. It does not say how often to think; it says that what
    you think ABOUT must already have happened. Six ticks at 60Hz is 100ms.
    `difficulty_tiers[].reaction_ticks` (20 / 14 / 10 / 6) are per-tier
    latencies and the floor is the hard minimum under all of them, which is why
    `latency` is max(floor, tier) rather than either alone.

    The consequence is worth stating because it is a design outcome and not an
    accident: at a 6-tick floor, `jab_lead` (4 startup + 2 active = 6) cannot be
    reacted to at all, and `uppercut_rear` (10 + 3 = 13) can be, with seven
    ticks to spare. A fast punch you must respect positionally and a heavy punch
    you can slip are now different objects, and neither needed a new number.

    WHAT THIS CLASS IS NOT. It is not a scheduler and it holds no state. The
    tick belongs to the bout; the rule belongs here. The bout asks `may_decide`
    and obeys the answer.
    """

    __slots__ = ("interval", "floor", "latency", "respects_commitment")

    def __init__(self, reaction, tier=None):
        """`reaction` is cpu_decision_model["reaction"], parsed by the caller.

        Parsed by the caller on purpose: this module reads no files, imports
        nothing and has no repo path, which is what lets it be tested in
        isolation and ported without dragging a JSON loader into a decision
        grammar.
        """
        try:
            self.interval = int(reaction["decision_interval_ticks"])
            self.floor = int(reaction["floor_ticks"])
        except (KeyError, TypeError):
            raise PolicyError(
                "cpu_decision_model.reaction must author both "
                "decision_interval_ticks and floor_ticks. They are canon's, "
                "and a default invented here would be a second opinion about "
                "the one file that says a CPU may not be instant.")
        if self.interval < 1:
            raise PolicyError("a decision interval below one tick is not an "
                              "interval, got %r" % (self.interval,))
        if self.floor < 1:
            raise PolicyError("a reaction floor of %r is the instant answer "
                              "canon exists to forbid" % (self.floor,))
        tier_ticks = self.floor
        if tier is not None:
            tier_ticks = int(tier["reaction_ticks"])
        self.latency = max(self.floor, tier_ticks)
        self.respects_commitment = bool(reaction.get("respects_commitment",
                                                     True))
        if reaction.get("may_cancel_own_commitment"):
            raise PolicyError(
                "canon now permits a CPU to cancel its own commitment, and "
                "this policy does not implement cancellation - branch 1 "
                "refuses to interrupt a recovery window unconditionally. "
                "Refused rather than silently ignored.")

    def may_decide(self, tick, last_decision_tick, stimulus_ready=False):
        """May this fighter form a NEW intent on this tick?

        Three answers, in order:

          * He has never decided. The first bell is a decision point.
          * Something he can legally react to has just become old enough to
            react to (`stimulus_ready`, an EDGE the caller raises exactly once
            per newly-perceived stimulus). This is the whole reason the answer
            is not `tick % interval`: a fixed lattice makes the same punch
            always answerable at the same phase, so a slip that is possible for
            one move and impossible for another reads to a player as random
            rather than as boxing. Measured from the last decision instead, the
            phase is a consequence of the fight; interrupted by a stimulus, the
            phase stops mattering for reactions at all.
          * Otherwise, the interval has elapsed.

        Commitment is NOT tested here, and deliberately: `reaction`'s
        `respects_commitment` is honoured by branch 1 of `decide()`, which
        refuses to cancel a recovery window whatever the cadence permits. One
        rule, one place.
        """
        if last_decision_tick is None:
            return True
        if stimulus_ready:
            return True
        return (tick - last_decision_tick) >= self.interval

    def phase_for(self, stream):
        """A per-fighter offset for the first decision, drawn once per bout.

        Without it both fighters decide on the same ticks forever, because both
        start with no history and share the interval - lockstep thinking, which
        is an artifact of the implementation and looks like one. Drawn from the
        fighter's OWN `policy_intent/<owner>` substream, so it is deterministic,
        entity-scoped and reproducible, and one fighter's offset can never move
        the other's (Decision 0026).
        """
        if stream is None:
            return 0
        _require_policy_stream(stream)
        return stream.below(self.interval)


def opening_stance():
    """What a fighter is doing before he has been asked anything.

    A staggered cadence means the two men do not think on the same tick, and
    therefore that one of them reaches tick one with no decision behind him.
    That is not an error and it is not "continue what you committed to" either
    - there is nothing yet to continue. He stands, hands up, and renews nothing:
    no stride is owed, no punch is committed, no window opens.

    It exists as a named thing rather than as a `None` the caller has to
    remember to handle, because the alternative is a policy that answers
    `continue_previous(None)` with something invented, and this module refuses
    invented answers on principle.
    """
    return Decision(COUNTER, HOLD_POSITION, None, R_CONTINUE_COMMITMENT, 0,
                    renews_intent=False)


def continue_previous(previous):
    """The tick between decisions. He continues; he does not decide again.

    The TACTIC carries so the economy keeps charging the right action family -
    a man mid-stride is moving, not holding - and `execution` is dropped so no
    second punch is committed and no second evasion window is opened. The
    initiative reported is the one he last read, which is more honest than a
    fresh computation: between decisions he has not looked.
    """
    if previous is None:
        raise PolicyError(
            "there is no previous decision to continue. Seed a fighter with "
            "`opening_stance()` before the first tick: a None here means the "
            "caller has no record of what this man is doing, and inventing one "
            "would be the policy answering a question nobody asked it.")
    return Decision(previous.strategic, previous.tactical, None,
                    R_CONTINUE_COMMITMENT, previous.initiative,
                    renews_intent=False)


def _refuse_dead_preference(profile, bands):
    """A fighter may not intend to fight from a range he cannot punch from.

    THE FIGHT B REFUSAL. Two mirrored `outside` fighters produced twelve rounds,
    3,174 punches, zero contacts and 120-120 on all three cards, and nothing in
    the model could state what was wrong with them. This states it, at the first
    decision, in one sentence: canon authors no punch from that band, so that
    plan has no fight in it.

    It is checked here rather than in `Profile.__init__` because a Profile can
    be built before canon is loaded - `FighterState` builds a default one - and
    a check that can be skipped by construction order is a check that will be.
    Every decision passes through here; there is no way around it.
    """
    if profile.preferred_band not in bands.order:
        raise PolicyError(
            "%r is not a band canon declares (%s). A preference for a band "
            "that does not exist is a typo, and a typo must not read as a "
            "style." % (profile.preferred_band, ", ".join(bands.order)))
    if profile.preferred_band in bands.without_offence:
        raise PolicyError(
            "this fighter prefers to fight at %r, and canon authors no punch "
            "throwable from %r with this bout's punch vocabulary. That is not "
            "a cautious style, it is a plan that cannot produce a punch: it "
            "cost one complete twelve-round fight, 3,174 of them refused by "
            "the range gate, and 120-120 on every card. Choose a band with "
            "offence in it, or change what canon authors - the second is a "
            "Director decision (range_band as a SET per move) and not this "
            "module's to make." % (profile.preferred_band,
                                   profile.preferred_band))
# [ ... | 2026-08-09 02:05 UTC | END edit: D7 - a CPU may be fast; it may not be instant ]


def _initiative(obs):
    """The tactical relationship, not a mood.

    Positive means this fighter is dictating; negative means he is being
    dictated to. A counterpuncher standing his ground against an advancing
    opponent has surrendered initiative and may be about to take it back.
    """
    value = 0
    if obs.opponent_advancing:
        value -= 3000
    if obs.opponent_recovering:
        value += 3000
    if obs.opponent_committed:
        value += 1500
    if obs.on_ropes or obs.cornered:
        value -= 3000
    if obs.hurt:
        value -= 2500
    if obs.wind_is_low:
        value -= 1000
    if obs.range_band == obs.preferred_band:
        value += 1500
    return max(-10000, min(10000, value))


def decide(obs, stream=None, profile=None):
    """One decision. Deterministic given (observation, stream state, profile).

    The order below is a boxing priority list, and it is ordered rather than
    scored on purpose: a weighted sum produces behaviour nobody can explain
    after the fact, and an unexplainable fighter cannot be tuned. Each branch
    commits with a reason.
    """
    if not isinstance(obs, Observation):
        raise PolicyError("decide() takes an Observation, got %r" % type(obs))
    # Decision 0026: refuse a foreign stream BEFORE any branch can draw from
    # it, not only where a tie is broken.
    _require_policy_stream(stream)
    profile = profile or Profile(preferred_band=obs.preferred_band)
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: the plan is checked before the fight ]
    _refuse_dead_preference(profile, obs.bands)
    # [ ... | 2026-08-09 02:05 UTC | END edit: the plan is checked before the fight ]
    init = _initiative(obs)

    # 1. Still recovering. Nothing may cancel a recovery window - a policy that
    #    could would make commitment meaningless.
    if obs.in_recovery and obs.recovery_ticks_left > 0:
        return Decision(RECOVER, OBSERVE, None, R_STILL_RECOVERING, init)

    # 2. An attack is landing. Answer it before doing anything you'd prefer.
    if obs.incoming_attack:
        tactic = EVADE if not obs.wind_is_low else GUARD
        # Decision 0026: a fighter who WAS recovering and has to answer a punch
        # has had his recovery interrupted, and the log should say so rather
        # than reporting a generic defence and losing why it happened.
        return Decision(COUNTER, tactic, "slip_lead" if tactic == EVADE
                        else "guard_high",
                        R_RECOVERY_INTERRUPTED if _wants_recovery(obs)
                        else R_DEFEND_INCOMING, init)

    # 3. Off the ropes. Being trapped outranks every plan that assumes room.
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: D10 - an escape that escapes ]
    # THE ANSWER USED TO BE `MICRO_ADJUST / pivot_lead`, WHICH IS CORRECT BOXING
    # AND MOVES NOBODY. Circling off is the escape canon deliberately protects -
    # `rope_lateral_multiplier: 1.0`, lateral untaxed on the ropes, "circling
    # off is the boxing answer and it remains open" - but the range runtime
    # resolves engagement on ONE axis, so `step_delta("step_lateral")` is zero
    # by construction and always will be until a second coordinate exists. A
    # retreat is worth nothing there either (`rope_retreat_multiplier: 0.0`).
    # That left a fighter whose back reached the ropes with no action that
    # changed his position at all - and this branch outranks almost everything,
    # so he stayed there. A stress run of this policy from a clinch start
    # reached it 2,639 times in one round.
    #
    # Forward is the only direction the geometry can express, and it is not a
    # consolation prize: fighting off the ropes is what a boxer with no angle
    # left actually does. The pivot returns as the first choice on the day the
    # range core has an angle to pivot through - raised to Section 1 as a flag,
    # not silently absorbed here.
    if (obs.on_ropes or obs.cornered) and not obs.opponent_recovering:
        return Decision(ESCAPE_ROPES, ADVANCE, "step_in", R_ESCAPE_ROPES, init)
    # [ ... | 2026-08-09 02:05 UTC | END edit: D10 - an escape that escapes ]

    # 4. Empty. A fighter with nothing left rests, whatever he wants.
    if obs.wind_is_exhausted:
        return Decision(RECOVER, REST, None, R_RECOVER_WIND, init)

    # 5. Hurt, or the body is going. Protect before producing.
    if obs.hurt or "body" in obs.damaged_regions:
        reason = R_PROTECT_DAMAGED_BODY if "body" in obs.damaged_regions \
            else R_DEFEND_INCOMING
        return Decision(PROTECT_REGION, GUARD, "guard_body"
                        if "body" in obs.damaged_regions else "guard_high",
                        reason, init)

    attacks = legal_attacks(obs)

    # 6. He is recovering and you are in range. This is the punish window, and
    #    a fighter who does not take it is not boxing.
    if obs.opponent_recovering and attacks:
        return Decision(EXPLOIT_CONDITION, ATTACK, _tie_break(attacks, stream),
                        R_RECOVERY_INTERRUPTED if _wants_recovery(obs)
                        else R_PUNISH_RECOVERY, init)

    # 7. THE RECOVERY-SPACE LOOP. Decision 0026 Ruling B.
    #
    #        need recovery -> assess threat and range
    #                      -> unsafe? create or defend space
    #                      -> safe?   rest
    #                      -> stay recovery-seeking until recovered or
    #                         interrupted
    #
    # The first version of this branch rested only at outside range and held
    # position otherwise. Holding position is the right answer to "can I rest
    # here?" and no answer at all to "how do I get somewhere I can?" - so in a
    # round where recovery was chosen 9,317 times out of 10,800, `rest` was
    # chosen zero times and every tick paid half rate.
    if _wants_recovery(obs):
        # The opponent can DENY recovery, and this is where that happens. A
        # pressure fighter makes exhaustion harder to escape by walking his man
        # down - not by holding a stamina-drain ability, which is the version
        # of this that would have been easy and wrong.
        if obs.opponent_advancing:
            return Decision(RECOVER, GUARD, "guard_high", R_RECOVERY_DENIED,
                            init)
        # Safe distance and nobody coming: this is what rest is for, and it is
        # the only state that pays well.
        if obs.range_band in ("outside", "out_of_range"):
            return Decision(RECOVER, REST, None, R_REST_WHEN_SAFE, init)
        # Close, but he is not coming forward, so the room is there to be
        # taken. Boxing calls this circling out. Tying up and clinching are the
        # other real answers and both need subsystems that do not exist yet -
        # named here so their absence is a known gap rather than an oversight.
        return Decision(RECOVER, RETREAT, "step_out", R_SEEK_RECOVERY_SPACE,
                        init)

    # 8. He keeps showing you the same thing. Punish the pattern.
    if attacks and _repeats(obs.opponent_recent_moves) >= 3:
        return Decision(COUNTER, ATTACK, _tie_break(attacks, stream),
                        R_PUNISH_REPEATED_JAB, init)

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: a man who cannot punch from here must do something about it ]
    # 9. NOTHING IS LEGAL FROM HERE, AND THAT OUTRANKS A PREFERENCE.
    #
    # This branch used to sit BELOW the preferred-range branch and answer with
    # `MICRO_ADJUST / pivot_lead`, whose step delta is zero - so a fighter
    # standing where he could not punch pivoted on the spot, forever, and the
    # log said `NO_LEGAL_ATTACK` while nothing about the fight changed. Deleting
    # `BY_BAND` on its own would have converted a stalemate of 3,174 refused
    # punches into a stalemate of none, which is more honest and no more
    # watchable.
    #
    # A fighter who cannot reach must close - OR MUST HAVE A REASON NOT TO, and
    # every such reason is already ABOVE this line and stays there: he is
    # committed (1), a punch is on its way (2), he is trapped on the ropes (3),
    # he is empty (4), he is hurt (5), his opponent is open (6), or he needs his
    # breath (7). Past all of those, standing at a distance from which no punch
    # exists is not defensive purity, it is the thing the owner names as the
    # actual abuse: neither hitting nor being hit. Decision 0030 is untouched -
    # nothing here taxes a defensive fighter's movement, stamina or avoidance,
    # and hitting without being hit remains entirely open. What closes is
    # standing still while unable to do either.
    #
    # DIRECTION IS HIS OWN PLAN, WHICH IS WHY THE PLAN IS CHECKED FIRST. He
    # moves toward the band he wants, and `_refuse_dead_preference` has already
    # guaranteed that band has a punch in it, so the walk always terminates. A
    # rule of the form "when in doubt, close" would not: give canon two adjacent
    # punch-less bands and a fighter bounces between them forever, which is the
    # same stalemate wearing a different pair of shoes.
    here, want = (_band_index(obs.range_band, obs.bands),
                  _band_index(profile.preferred_band, obs.bands))

    if not attacks:
        if not obs.hands_available:
            # No hands is not a range problem, and closing would be suicide. A
            # man who cannot punch at any distance covers up. (Unreachable
            # today: `FighterState.observation` hardcodes both hands. It is
            # written to be correct on the day that stops being true.)
            return Decision(PROTECT_REGION, GUARD, "guard_high",
                            R_HAND_UNAVAILABLE, init)
        if here > want:
            return Decision(FIND_WORKING_RANGE, ADVANCE, "step_in",
                            R_NO_LEGAL_ATTACK, init)
        if here < want:
            return Decision(FIND_WORKING_RANGE, RETREAT, "step_out",
                            R_NO_LEGAL_ATTACK, init)
        # He is at the range he chose, that range has offence in it, and he
        # still has nothing: his hands, not his feet. Change what geometry is
        # left to change - back out of the innermost band, close from anywhere
        # else - rather than stand there.
        return Decision(
            FIND_WORKING_RANGE,
            RETREAT if here == 0 else ADVANCE,
            "step_out" if here == 0 else "step_in",
            R_NO_LEGAL_ATTACK, init)

    # 10. There is work here, but it is not the work he wants. Close the
    #     distance or leave it, deliberately.
    if here != want:
        if here > want:
            return Decision(SEEK_PREFERRED_RANGE, ADVANCE, "step_in",
                            R_SEEK_PREFERRED_RANGE, init)
        return Decision(SEEK_PREFERRED_RANGE, RETREAT, "step_out",
                        R_EXIT_BAD_RANGE, init)

    # 11. Good range, hands free, opponent upright. Aggression decides whether
    #     to spend now - and even at full aggression, repeated failure and a
    #     committed opponent argue for waiting.
    #
    # THE BRAKE MUST CHANGE SOMETHING, NOT MERELY BLOCK. It used to answer
    # `HOLD_POSITION`, which is safe only while the counter it reads is broken:
    # `committed_to()` zeroes `failed_attacks` on every throw, so it has never
    # exceeded 1 in 12,000 ticks and this branch has never fired. Repaired (see
    # the cross-section flag - the counter must be zeroed by LANDING, not by
    # THROWING), a hold would be a trap: nothing a holding fighter does can
    # reduce a count of failures, so a man who missed twice would hold for the
    # rest of the fight. Stepping out breaks the exchange, changes the band,
    # changes which punches exist, and lets branch 10 walk him back in - miss,
    # miss, break, re-enter, which is what a corner actually shouts.
    if obs.consecutive_failed_attacks >= 2:
        return Decision(COUNTER, RETREAT, "step_out", R_AVOID_OVERCOMMIT, init)
    # [ ... | 2026-08-09 02:05 UTC | END edit: a man who cannot punch from here must do something about it ]

    want_initiative = profile.aggression_bias + max(0, init) // 2
    roll = stream.below(10000) if stream is not None else 5000
    if roll < want_initiative:
        strategic = PRESSURE if obs.opponent_advancing is False else COUNTER
        return Decision(strategic, ATTACK, _tie_break(attacks, stream),
                        R_PRESSURE_ROPES if obs.opponent_on_ropes
                        else R_ATTACK_OPEN_LANE, init)

    return Decision(MANAGE_CLOCK if obs.ticks_left_in_round < 600 else COUNTER,
                    HOLD_POSITION, None,
                    R_MANAGE_CLOCK if obs.ticks_left_in_round < 600
                    else R_HOLD_GOOD_RANGE, init)


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 10:00 UTC | START edit: Decision 0026 ]
def _wants_recovery(obs):
    """Is this fighter recovery-seeking right now? The hysteresis, in one place.

    Two conditions, not one:

        ENTER   Wind drops below the declared low threshold.
        EXIT    Wind climbs back above a SEPARATE declared recovered threshold.

    Between them the intent persists, which is the whole point. A single
    threshold makes a fighter stop recovering the instant he crosses it, spend,
    fall back under, and recover again - on alternate ticks, forever. The first
    integrated round produced the coarse version of that: a Wind trace that sat
    flat on the entry threshold for 165 seconds.

    Both thresholds come from `data/stamina_economy.json` via the caller, not
    from constants here. Decision 0026 requires them declared and configurable,
    and a policy that carried its own copy would be the second opinion about
    canon this project keeps deleting.
    """
    if obs.wind_is_exhausted:
        return True
    if obs.wind_is_low:
        return True
    return obs.recovery_seeking and not obs.wind_is_recovered
# [ ... | 2026-08-08 10:00 UTC | END edit ]


def _repeats(moves):
    """How many times the most recent move has just been repeated."""
    if not moves:
        return 0
    last, n = moves[-1], 0
    for m in reversed(moves):
        if m != last:
            break
        n += 1
    return n
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:00 UTC | END ]
