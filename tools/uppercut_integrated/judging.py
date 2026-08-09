# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:00 UTC | START ]
"""Sealed judging for the integrated bout. Three judges, observable evidence,
cards unreadable until the final bell.

THE SEAL IS STRUCTURAL, NOT POLITE. Round scores accumulate inside `_cards`,
on a class whose public surface exposes nothing but a round COUNT until
`verdict()` is called - and `verdict()` refuses to speak before the bout is
declared over. The policy cannot read the cards for a stronger reason than
discipline: `Observation.__slots__` has no field to carry them, which is the
same enforcement the score-isolation contract has used since Phase 1A.

[ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC |
  START edit: the seal, described accurately ]
`_cards` is single-underscore, so it is a CONVENTION and not Python name
mangling; the sentence that said otherwise was wrong and is corrected here
rather than left as a claim an auditor would rely on. What actually holds is
the absent channel plus `verdict()`'s refusal, and that is the enforcement
worth protecting. Making the attribute genuinely private (`__cards`, mangled
in `__slots__` as well) is a one-line change, deferred only because
`export_fight.py` was not visible to this review and may read it.
[ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC |
  END edit: the seal, described accurately ]

THE JUDGES DIFFER ON PURPOSE, AND DETERMINISTICALLY. The round-three review's
one caution on defensive purity: "If all seven scoring models read defence
identically, the game under-scores the master everywhere instead of somewhere
- part of boxing's truth is that Judge A gives Whitaker the round and Judge B
does not." So the three judges weight the same observable evidence
differently - clean punching for all three, effective aggression for one,
defence-that-purchases for another - and no judge consumes randomness. The
`judging_officiating` substream exists per Decision 0022 and is deliberately
unconsumed until canon authors a stochastic term.

WHAT A JUDGE MAY SEE: counts of arrived and dodged punches, knockdowns, and
ground taken - all of it observable from a ringside seat. No Wind, no Reserve,
no reason codes, no internal state. A judge is an audience member with a
pencil, not a debugger.

10-POINT MUST. THE ROUND WINNER RECEIVES TEN - that sentence is what the word
"must" is doing in the name, and `score_round` is built around it rather than
around it being true most of the time. Everything else on the card is
arithmetic hung off that one rule.
"""

# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: D4 legal cards / D5 commensurate units ]
# The q10000 fixed point the rest of the bout already uses.
ONE = 10000

# THE SCORING NUMBERS ARE THE RULESET'S, NOT THIS MODULE'S.
# `data/rulesets/professional.json` authors, verbatim:
#     "scoring": {"system": "ten_point_must", "round_win": 10,
#                 "round_lose": 9, "knockdown_deduction": 1}
# This module deliberately has no imports and no file access - it is the one
# integrated module that can be reasoned about and unit-tested without a repo -
# so the ruleset's own block is INJECTED at construction instead of loaded. The
# table below is canon's professional block restated for the no-ruleset case,
# not a fourth authority: `arcade_three_knockdown.json` authors its own and
# must be passed in. Section 5 flag: hand `ruleset["scoring"]` to the panel
# once ruleset loading exists. No scoring number is chosen here.
DEFAULT_SCORING = {
    "system": "ten_point_must",
    "round_win": 10,
    "round_lose": 9,
    "knockdown_deduction": 1,
}

# The evidence a judge may read, in declared order. These are `bout.py`'s own
# key names and this module does not change the evidence contract:
#   landed   solid punches that arrived                     -> CLEAN PUNCHING
#   denied   opponent punches made to miss while defending  -> DEFENCE
#   pressed  q10000 reach units of ground advanced         -> forward motion
# RING GENERALSHIP, the fourth criterion every commission teaches, has no
# observable in this vector at all. Named as a gap rather than approximated.
CRITERIA = ("landed", "denied", "pressed")

# What each judge weighs, per q10000. Deterministic, declared, and different.
# THE NUMBERS ARE UNCHANGED AND THEIR MEANING IS NOT. A weight now multiplies a
# dimensionless margin in [-ONE, +ONE] rather than a raw magnitude, so 10000
# for clean punching finally outweighs 4000 for aggression the way this file
# always claimed. Before this edit `landed` was a count and `pressed` was
# q10000 reach units, summed as though they were the same kind of number: one
# landed punch was worth 1 to every judge and one capped advancing tick was
# worth 140 to Bello and 560 to Reyes - measured at 116 landed against 4,200
# pressed in one real round, about 90:1 in favour of walking forward.
JUDGE_STYLES = (
    ("aisha_bello", {"landed": 10000, "denied": 2000, "pressed": 1000}),
    ("marta_reyes", {"landed": 10000, "denied": 0, "pressed": 4000}),
    ("tomasz_wojcik", {"landed": 10000, "denied": 5000, "pressed": 0}),
)

# A judge with no non-zero weight cannot separate any round from any other and
# would sit on even rounds for twelve rounds while looking like a judge.
# Refused at import, where it is a typo, rather than at the final bell, where
# it is a scorecard.
for _judge_name, _judge_weights in JUDGE_STYLES:
    _unknown = sorted(set(_judge_weights) - set(CRITERIA))
    if _unknown:
        raise ValueError("judge %r weighs %r, which is not declared evidence"
                         % (_judge_name, _unknown))
    if not any(_judge_weights.get(_k, 0) for _k in CRITERIA):
        raise ValueError("judge %r has no non-zero weight - a judge who "
                         "cannot separate a round is not a judge"
                         % (_judge_name,))
del _judge_name, _judge_weights, _unknown


def _margin(x, y):
    """Two magnitudes of the SAME criterion -> one signed q10000 margin.

    THIS IS THE UNIT FIX. Each criterion is normalised against its own round
    total before any weight touches it, so a punch count and a reach-unit
    distance reach the card on one scale: -ONE the opponent took it outright,
    0 nobody separated it, +ONE this fighter took it outright. There is no
    conversion constant, so there is none to invent, fit or argue about.

    Antisymmetric by construction - the division truncates toward zero instead
    of toward minus infinity - so `_margin(x, y) == -_margin(y, x)` exactly and
    which corner the contract lists first cannot move a card by one unit.
    """
    total = x + y
    if total <= 0:
        return 0                     # nobody contested it; it separates nobody
    d = (x - y) * ONE
    return d // total if d >= 0 else -((-d) // total)


def _criterion_margins(ea, eb):
    """The three margins one round produces, read by every judge alike.

    CLEAN PUNCHING and DEFENCE are counts of one kind and compare directly.

    EFFECTIVE AGGRESSION is the one that needed a ruling. `pressed` is ground
    advanced, and ground advanced is a proxy for walking forward - which is the
    single thing a judging seminar teaches judges to score AGAINST. The
    defining word in effective aggression is EFFECTIVE, so the magnitude here
    is ground advanced THAT BOUGHT CLEAN PUNCHING: `pressed * landed`. A
    fighter who marches forward all round and misses scores zero aggression; a
    fighter who lands going forward scores all of it; two fighters who advance
    and neither lands separate nobody. Clean punching is deliberately counted
    twice - once as itself and once as the thing that makes pressure effective
    - because in the sport it is.

    This is the honest maximum available from today's evidence vector. What a
    seminar would actually want is accuracy - landed over THROWN, while
    advancing - and `thrown` is not emitted per fighter per round. That is a
    Cross-Section Flag to Section 5, not something this module may invent.
    """
    return {
        "landed": _margin(ea["landed"], eb["landed"]),
        "denied": _margin(ea["denied"], eb["denied"]),
        "pressed": _margin(ea["pressed"] * ea["landed"],
                           eb["pressed"] * eb["landed"]),
    }


def _fallback_order(weights):
    """One judge's criteria, most important first, for an exact arithmetic tie.

    Commission practice pushes judges hard off even rounds, and an exact
    integer tie between two weighted sums is usually an arithmetic coincidence
    rather than a dead heat. A tied judge therefore falls through to his own
    criteria in his own order of importance, which is what a judge says out
    loud when a round is close: who landed the cleaner shots.

    Criteria this judge weighs at zero are absent - they are not his to break a
    tie on - so the three judges break ties three different ways. Deterministic
    and consuming no randomness: `judging_officiating` stays unconsumed.
    """
    ranked = [k for k in CRITERIA if weights.get(k, 0)]
    ranked.sort(key=lambda k: (-weights[k], CRITERIA.index(k)))
    return tuple(ranked)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: D4 legal cards / D5 commensurate units ]


class BoutNotOver(RuntimeError):
    """The cards were asked for before the final bell. Refused - the seal is
    the entire point, and an early read is a scoreboard, not a card."""


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: an empty card is not a draw ]
class NoCardToRead(RuntimeError):
    """A verdict was asked for from a panel with no scored round. A bout that
    ends before the first round closes ends by stoppage; answering DRAW off an
    empty card would invent a result out of an absence."""
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: an empty card is not a draw ]


class JudgingPanel(object):
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: ruleset scoring is injected ]
    __slots__ = ("_cards", "_over", "participants", "scoring", "_order",
                 "_last_round")

    def __init__(self, participants, scoring=None):
        if len(participants) != 2:
            raise ValueError("a card has two columns, got %r" % (participants,))
        if participants[0] == participants[1]:
            raise ValueError("a card has two DIFFERENT columns, got %r"
                             % (participants,))
        self.participants = tuple(participants)
        # The ruleset's scoring block, or canon's professional block when no
        # ruleset is handed in. Refused rather than scored anyway if it names a
        # system this panel does not implement: a card produced by ten-point
        # must arithmetic under a ruleset that authors something else is a card
        # nobody agreed to fight under.
        self.scoring = dict(scoring or DEFAULT_SCORING)
        if self.scoring.get("system") != "ten_point_must":
            raise ValueError(
                "this panel implements ten_point_must; the ruleset authors "
                "%r. Refused rather than defaulted."
                % (self.scoring.get("system"),))
        for _key in ("round_win", "round_lose", "knockdown_deduction"):
            if _key not in self.scoring:
                raise ValueError("the ruleset's scoring block authors no "
                                 "%r, and this module will not choose one"
                                 % (_key,))
        self._cards = {name: [] for name, _ in JUDGE_STYLES}
        self._order = {name: _fallback_order(w) for name, w in JUDGE_STYLES}
        self._last_round = None
        self._over = False
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: ruleset scoring is injected ]

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: D4 the ten-point must ]
    def score_round(self, round_no, evidence, knockdowns):
        """One round onto every card. `evidence` is {fighter: {landed, denied,
        pressed}}; `knockdowns` is {fighter: times FLOORED this round}.

        THE TEN-POINT MUST, AS THE RULES ACTUALLY WORK.

        CANON'S PART, read from the injected ruleset and never chosen here:
        `data/rulesets/professional.json` -> `scoring` authors `round_win` 10,
        `round_lose` 9 and `knockdown_deduction` 1 under `ten_point_must`.

        DOMAIN PRINCIPLE, named as mine because no canon file authors it:

          1. THE ROUND WINNER RECEIVES TEN. This is the rule the previous
             implementation broke. It applied the knockdown deduction to BOTH
             fighters, so a man who won a round 20 landed to 1 having been
             dropped twice scored 8 against the loser's 9 and the round
             inverted. A 9-8-to-the-loser round is not a legal card.

          2. A KNOCKDOWN DECIDES THE ROUND. In professional practice a fighter
             who is dropped loses that round barring something exceptional, so
             a knockdown is not a modifier applied after a work-rate verdict -
             it dominates it. Unequal knockdowns therefore pick the round
             winner before any judge weighs anything, which is also why all
             three cards agree on a knockdown round: a knockdown is an
             officially recorded event, not a matter of taste.

          3. KNOCKDOWNS CANCEL ONE FOR ONE. Equal knockdowns leave the round to
             the work; twice against once is a one-knockdown round.

          4. The loser's score is `round_lose - deduction * net`: 10-8 for one,
             10-7 for two, 10-6 for three, which is the sport's own ladder.
             There is NO floor. The `max(7, ...)` this replaces was invented
             and no canon file authors it.

        The only clamp below is at zero and it is ARITHMETIC - a points system
        has no scores beneath nothing - not a boxing rule. It is unreachable
        under any knockdown limit a ruleset can sanely author.
        """
        a, b = self.participants
        if self._last_round is not None and round_no <= self._last_round:
            raise ValueError(
                "round %r is already on the cards (last scored: %r). A round "
                "scored twice is a card nobody can reconstruct."
                % (round_no, self._last_round))
        for who in (a, b):
            if who not in evidence:
                raise KeyError("no evidence for %r - a judge scores what "
                               "he saw, and an absent column is not zero"
                               % (who,))
            missing = [k for k in CRITERIA if k not in evidence[who]]
            if missing:
                raise KeyError("evidence for %r declares no %r"
                               % (who, missing))
            if knockdowns.get(who, 0) < 0:
                raise ValueError("%r is recorded as knocked down %r times"
                                 % (who, knockdowns.get(who)))

        win = int(self.scoring["round_win"])
        lose = int(self.scoring["round_lose"])
        deduct = int(self.scoring["knockdown_deduction"])
        net = knockdowns.get(a, 0) - knockdowns.get(b, 0)
        margins = _criterion_margins(evidence[a], evidence[b])

        for judge, weights in JUDGE_STYLES:
            if net > 0:                     # a was dropped more; b takes it
                pa, pb = max(0, lose - deduct * net), win
            elif net < 0:
                pa, pb = win, max(0, lose - deduct * -net)
            else:
                edge = sum(margins[k] * w for k, w in weights.items())
                if edge == 0:
                    # An exact tie between two weighted sums is an arithmetic
                    # coincidence far more often than it is a dead heat, and
                    # commission practice pushes judges hard off even rounds.
                    # This judge falls through to his own criteria in his own
                    # order. No randomness is consumed anywhere in this file.
                    for k in self._order[judge]:
                        if margins[k]:
                            edge = margins[k]
                            break
                if edge > 0:
                    pa, pb = win, lose
                elif edge < 0:
                    pa, pb = lose, win
                else:
                    # Nothing this judge weighs separated them at all. A
                    # genuinely identical round IS an even round, and inventing
                    # a winner out of nothing would hide the real defect - an
                    # evidence famine - behind a scoreline.
                    pa, pb = win, win
            self._cards[judge].append((round_no, pa, pb))
        self._last_round = round_no
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: D4 the ten-point must ]

    def seal_check(self):
        """What anything mid-bout may know: how many rounds are on the cards.
        Not one point more."""
        return len(next(iter(self._cards.values())))

    def close(self):
        self._over = True

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: an empty card is not a draw, and a draw has a name ]
    def verdict(self):
        """The reveal. Refuses to exist before the bout is over."""
        if not self._over:
            raise BoutNotOver(
                "the cards are sealed until the final bell. Nothing - not the "
                "CPU, not commentary, not a test being helpful - reads them "
                "early.")
        if not self.seal_check():
            raise NoCardToRead(
                "no round has been scored, so there is no card to read. A "
                "bout that ended before the first round closed ended by "
                "stoppage, and DRAW off an empty card invents a result.")
        a, b = self.participants
        totals = {}
        for judge, rounds in self._cards.items():
            totals[judge] = (sum(r[1] for r in rounds),
                             sum(r[2] for r in rounds))
        votes_a = sum(1 for ta, tb in totals.values() if ta > tb)
        votes_b = sum(1 for ta, tb in totals.values() if tb > ta)
        draw_kind = None
        if votes_a == 3:
            result = ("UD", a)
        elif votes_b == 3:
            result = ("UD", b)
        elif votes_a == 2:
            result = ("SD", a) if votes_b == 1 else ("MD", a)
        elif votes_b == 2:
            result = ("SD", b) if votes_a == 1 else ("MD", b)
        else:
            # `method` stays "DRAW" so no existing consumer of it moves, but
            # boxing names three different draws and a card that cannot say
            # which one it is is a card that cannot be read out loud.
            result = ("DRAW", None)
            draw_kind = ("split" if votes_a == 1 and votes_b == 1
                         else "majority" if votes_a or votes_b
                         else "unanimous")
        # The rounds go out as a COPY. The card is read at the final bell and
        # never edited after it, and a live list handed to a consumer is an
        # edit waiting to happen.
        return {"method": result[0], "winner": result[1],
                "draw_kind": draw_kind,
                "cards": {j: {"totals": t, "rounds": list(self._cards[j])}
                          for j, t in totals.items()}}
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: an empty card is not a draw, and a draw has a name ]
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:00 UTC | END ]
