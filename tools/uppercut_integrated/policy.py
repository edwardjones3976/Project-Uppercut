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

STRATEGIC = (SEEK_PREFERRED_RANGE, PRESSURE, COUNTER, RECOVER, PROTECT_REGION,
             ESCAPE_ROPES, EXPLOIT_CONDITION, MANAGE_CLOCK)

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

REASONS = (R_SEEK_PREFERRED_RANGE, R_NO_LEGAL_ATTACK, R_HOLD_GOOD_RANGE,
           R_RECOVER_WIND, R_PROTECT_DAMAGED_BODY, R_PRESSURE_ROPES,
           R_PUNISH_RECOVERY, R_PUNISH_REPEATED_JAB, R_EXIT_BAD_RANGE,
           R_ATTACK_OPEN_LANE, R_AVOID_OVERCOMMIT, R_ESCAPE_ROPES,
           R_DEFEND_INCOMING, R_HAND_UNAVAILABLE, R_STILL_RECOVERING,
           R_MANAGE_CLOCK)

# The stream this policy is allowed to touch, by name.
POLICY_STREAM = "policy_intent"


class PolicyError(ValueError):
    """The policy was asked to decide from something it may not use."""


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
    )

    def __init__(self, **kw):
        unknown = set(kw) - set(self.__slots__)
        if unknown:
            raise PolicyError(
                "the policy was handed %s, which it may not see. If this is "
                "genuinely observable, add it to Observation deliberately."
                % ", ".join(sorted(unknown)))
        defaults = {
            "wind_fraction": 10000, "reserve_fraction": 10000,
            "wind_is_low": False, "wind_is_exhausted": False,
            "hands_available": ("lead", "rear"), "in_recovery": False,
            "recovery_ticks_left": 0, "damaged_regions": (), "hurt": False,
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

    __slots__ = ("strategic", "tactical", "execution", "reason", "initiative")

    def __init__(self, strategic, tactical, execution, reason, initiative):
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


# Band ordering, closest first. The policy reasons about "closer" and "further"
# rather than about distances, because distance is the range subsystem's job.
BANDS = ("clinch", "inside", "mid", "outside", "out_of_range")

# What each hand can throw. An unavailable hand removes its moves entirely -
# a fighter with a damaged lead does not "prefer not to" jab, he cannot.
BY_HAND = {
    "lead": ("jab_lead", "hook_lead", "uppercut_lead", "body_hook_lead"),
    "rear": ("cross_rear", "hook_rear", "uppercut_rear", "overhand_rear",
             "body_straight_rear"),
}

# What is throwable from each band. Boxing, not taste: you cannot land a jab
# from out of range, and an uppercut belongs inside.
BY_BAND = {
    "clinch": ("uppercut_lead", "uppercut_rear", "body_hook_lead"),
    "inside": ("hook_lead", "hook_rear", "uppercut_lead", "uppercut_rear",
               "body_hook_lead", "body_straight_rear"),
    "mid": ("jab_lead", "cross_rear", "hook_lead", "body_straight_rear"),
    "outside": ("jab_lead", "cross_rear"),
    "out_of_range": (),
}


def _band_index(band):
    try:
        return BANDS.index(band)
    except ValueError:
        raise PolicyError("unknown range band %r" % (band,))


def legal_attacks(obs):
    """Every attack this fighter could actually throw right now.

    Intersection of what the band allows and what the available hands can do.
    Returned sorted, so the option set never depends on iteration order - the
    same rule Decision 0022 states for random ownership.
    """
    from_band = set(BY_BAND.get(obs.range_band, ()))
    from_hands = set()
    for hand in obs.hands_available:
        from_hands.update(BY_HAND.get(hand, ()))
    return tuple(sorted(from_band & from_hands))


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
    if getattr(stream, "name", None) != POLICY_STREAM:
        raise PolicyError(
            "the policy was handed the %r stream. It may consume only %r - a "
            "policy that can reach contact or judging randomness is a policy "
            "that can be accused of reading them."
            % (getattr(stream, "name", stream), POLICY_STREAM))
    return options[stream.below(len(options))]


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
    profile = profile or Profile(preferred_band=obs.preferred_band)
    init = _initiative(obs)

    # 1. Still recovering. Nothing may cancel a recovery window - a policy that
    #    could would make commitment meaningless.
    if obs.in_recovery and obs.recovery_ticks_left > 0:
        return Decision(RECOVER, OBSERVE, None, R_STILL_RECOVERING, init)

    # 2. An attack is landing. Answer it before doing anything you'd prefer.
    if obs.incoming_attack:
        tactic = EVADE if not obs.wind_is_low else GUARD
        return Decision(COUNTER, tactic, "slip_lead" if tactic == EVADE
                        else "guard_high", R_DEFEND_INCOMING, init)

    # 3. Off the ropes. Being trapped outranks every plan that assumes room.
    if (obs.on_ropes or obs.cornered) and not obs.opponent_recovering:
        return Decision(ESCAPE_ROPES, MICRO_ADJUST, "pivot_lead",
                        R_ESCAPE_ROPES, init)

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
                        R_PUNISH_RECOVERY, init)

    # 7. Low on Wind. Recover when the situation permits it - which is what
    #    makes this a decision rather than a reflex.
    if obs.wind_is_low and not obs.opponent_advancing:
        tactic = REST if obs.range_band in ("outside", "out_of_range") \
            else HOLD_POSITION
        return Decision(RECOVER, tactic, None, R_RECOVER_WIND, init)

    # 8. He keeps showing you the same thing. Punish the pattern.
    if attacks and _repeats(obs.opponent_recent_moves) >= 3:
        return Decision(COUNTER, ATTACK, _tie_break(attacks, stream),
                        R_PUNISH_REPEATED_JAB, init)

    # 9. Wrong distance. Close it or leave, deliberately.
    here, want = _band_index(obs.range_band), _band_index(profile.preferred_band)
    if here != want:
        if here > want:
            return Decision(SEEK_PREFERRED_RANGE, ADVANCE, "step_in",
                            R_SEEK_PREFERRED_RANGE, init)
        return Decision(SEEK_PREFERRED_RANGE, RETREAT, "step_out",
                        R_EXIT_BAD_RANGE, init)

    # 10. In range with nothing legal to throw. Say so rather than inventing.
    if not attacks:
        return Decision(SEEK_PREFERRED_RANGE, MICRO_ADJUST, "pivot_lead",
                        R_NO_LEGAL_ATTACK if obs.hands_available
                        else R_HAND_UNAVAILABLE, init)

    # 11. Good range, hands free, opponent upright. Aggression decides whether
    #     to spend now - and even at full aggression, repeated failure and a
    #     committed opponent argue for waiting.
    if obs.consecutive_failed_attacks >= 2:
        return Decision(COUNTER, HOLD_POSITION, None, R_AVOID_OVERCOMMIT, init)

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
