# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:00 UTC | START ]
"""Sealed judging for the integrated bout. Three judges, observable evidence,
cards unreadable until the final bell.

THE SEAL IS STRUCTURAL, NOT POLITE. Round scores accumulate inside `_cards`,
a name-mangled attribute on a class whose public surface exposes nothing until
`verdict()` is called - and `verdict()` refuses to speak before the bout is
declared over. The policy cannot read the cards for a stronger reason than
discipline: `Observation.__slots__` has no field to carry them, which is the
same enforcement the score-isolation contract has used since Phase 1A.

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

10-POINT MUST, canonically shaped: round winner 10, loser 9; each knockdown
suffered turns the loser's 9 into an 8, floor 7. A draw round is 10-10.
"""

# What each judge weighs, per q10000. Deterministic, declared, and different.
# The evidence vector per fighter per round:
#   landed      solid punches that arrived
#   denied      opponent punches made to miss (vacated) while this fighter defended
#   pressed     reach units of ground this fighter advanced
JUDGE_STYLES = (
    ("aisha_bello", {"landed": 10000, "denied": 2000, "pressed": 1000}),
    ("marta_reyes", {"landed": 10000, "denied": 0, "pressed": 4000}),
    ("tomasz_wojcik", {"landed": 10000, "denied": 5000, "pressed": 0}),
)


class BoutNotOver(RuntimeError):
    """The cards were asked for before the final bell. Refused - the seal is
    the entire point, and an early read is a scoreboard, not a card."""


class JudgingPanel(object):
    __slots__ = ("_cards", "_over", "participants")

    def __init__(self, participants):
        if len(participants) != 2:
            raise ValueError("a card has two columns, got %r" % (participants,))
        self.participants = tuple(participants)
        self._cards = {name: [] for name, _ in JUDGE_STYLES}
        self._over = False

    def score_round(self, round_no, evidence, knockdowns):
        """One round onto every card. `evidence` is {fighter: {landed, denied,
        pressed}}; `knockdowns` is {fighter: times FLOORED this round}."""
        a, b = self.participants
        for judge, weights in JUDGE_STYLES:
            score_a = sum(evidence[a][k] * w for k, w in weights.items()) // 10000
            score_b = sum(evidence[b][k] * w for k, w in weights.items()) // 10000
            if score_a == score_b:
                pa, pb = 10, 10
            elif score_a > score_b:
                pa, pb = 10, 9
            else:
                pa, pb = 9, 10
            # A knockdown moves the card whatever the work rate said.
            pa = max(7, pa - knockdowns.get(a, 0))
            pb = max(7, pb - knockdowns.get(b, 0))
            self._cards[judge].append((round_no, pa, pb))

    def seal_check(self):
        """What anything mid-bout may know: how many rounds are on the cards.
        Not one point more."""
        return len(next(iter(self._cards.values())))

    def close(self):
        self._over = True

    def verdict(self):
        """The reveal. Refuses to exist before the bout is over."""
        if not self._over:
            raise BoutNotOver(
                "the cards are sealed until the final bell. Nothing - not the "
                "CPU, not commentary, not a test being helpful - reads them "
                "early.")
        a, b = self.participants
        totals = {}
        for judge, rounds in self._cards.items():
            totals[judge] = (sum(r[1] for r in rounds),
                             sum(r[2] for r in rounds))
        votes_a = sum(1 for ta, tb in totals.values() if ta > tb)
        votes_b = sum(1 for ta, tb in totals.values() if tb > ta)
        if votes_a == 3:
            result = ("UD", a)
        elif votes_b == 3:
            result = ("UD", b)
        elif votes_a == 2:
            result = ("SD", a) if votes_b == 1 else ("MD", a)
        elif votes_b == 2:
            result = ("SD", b) if votes_a == 1 else ("MD", b)
        else:
            result = ("DRAW", None)
        return {"method": result[0], "winner": result[1],
                "cards": {j: {"totals": t, "rounds": self._cards[j]}
                          for j, t in totals.items()}}
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:00 UTC | END ]
