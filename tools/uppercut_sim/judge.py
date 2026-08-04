# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START ]
"""The Judge subsystem (Rule 3, extracted from Bout per Decision 0012 slice item 1).

Boundary, stated as the contract it is:

  IN  - a stream of witnessed facts, as plain dicts. A fact is something a person
        on the apron can see: a punch landing with a graded quality, a knockdown,
        a bell. Nothing else crosses. No Fighter, no Bout, no stamina, condition,
        attributes, policy state, or RNG - this module cannot even name those
        types, because it imports nothing that defines them.
  OUT - sealed cards. Reading them before the final bell raises, which is Rule 3
        as an exception rather than a comment.

`tools/uppercut_validate/judge_boundary.py` enforces both directions on the
source itself, so the firewall is a checked relation rather than a habit.

The judge witnesses the punch, not the log entry: the `force` in a witnessed
fact is the same unrounded delivered-force fraction the engine computed at the
moment of contact, where the recorded event payload rounds for serialization.
Scoring from the moment rather than the record keeps this extraction
arithmetically identical to the scoring it replaces - proven byte-for-byte over
every profile pairing - and matches the real thing: judges score what they saw,
not the broadcast transcript.

The judge is not the referee. Counts, warnings and stoppages happen in the ring
and stay in the engine; what arrives here is only what the count arithmetic
already made public. Referee-profile consumption (slice item 2) touches the
ring, not this module.
"""
from __future__ import annotations


class SealedCardsError(RuntimeError):
    """Raised when anything tries to read cards before the final bell."""


# The whole vocabulary of what a judge may be shown. The boundary validator
# holds the engine to these exact keys, so widening what the judge sees is a
# visible, reviewable act rather than an extra dict entry.
FACT_TYPES = ("punch_landed", "knockdown", "deduction")
FACT_KEYS = frozenset({"type", "scorer", "fighter", "force"})


class Judge:
    """Ten-point-must over witnessed facts, sealed until the final bell.

    Two corrections are carried in this arithmetic, forced by the
    style-viability and abuse-list checks while it still lived in
    `Bout._score_round`, and logged here so a later edit does not silently
    undo them:

    1. The round is scored on THIS round's work. The previous version summed
       bout-to-date landings, so an early lead re-won every subsequent round.
    2. The round is scored on effective offence - the sum of delivered force
       fractions - not on a raw count of contacts. Counting contacts made a
       brushed jab (0.15 force) worth exactly as much as a clean cross (1.0),
       which is what let a single-jab loop out-point a varied fighter it was
       visibly losing to. Quality already exists in canon as the collision
       model's `delivered_force_fraction`; the card reads it rather than
       inventing a volume proxy beside it. This is the judging analogue of
       Rule 14: what lands, and how well, decides - never a flat tally.

    Knockdowns are deducted the way a real card deducts them: one point per
    knockdown suffered in the round, on top of losing it. A referee deduction
    (2026-08-04, slice item 2) is witnessed the same way a knockdown is - as a
    public ring fact - and costs its point identically. The judge never asks
    why the referee deducted; the reason is the referee's record, the point is
    the card's.
    """

    def __init__(self, corners) -> None:
        self._corners = tuple(corners)
        self._cards = {n: 0.0 for n in self._corners}
        self._round_force = {n: 0.0 for n in self._corners}
        self._round_knockdowns = {n: 0 for n in self._corners}
        self._round_deductions = {n: 0 for n in self._corners}
        self._rounds_sealed = 0
        self._final = False

    # ---- the observation stream in --------------------------------------
    def witness(self, fact: dict) -> None:
        """One observable ring fact. Unknown shapes raise: the vocabulary is a
        contract, and a judge silently ignoring what they were shown would hide
        a harness bug as a scoring opinion."""
        if self._final:
            raise SealedCardsError("the final card is sealed; no fact may be "
                                   "witnessed after the official reading")
        extra = set(fact) - FACT_KEYS
        if extra:
            raise ValueError(f"unknown fact key(s) {sorted(extra)}")
        kind = fact.get("type")
        if kind == "punch_landed":
            self._round_force[fact["scorer"]] += fact["force"]
        elif kind == "knockdown":
            self._round_knockdowns[fact["fighter"]] += 1
        elif kind == "deduction":
            self._round_deductions[fact["fighter"]] += 1
        else:
            raise ValueError(f"unknown fact type {kind!r}")

    # ---- the bells -------------------------------------------------------
    def seal_round(self) -> None:
        """Score the round in front of the judges and seal it into the cards.
        A stopped round is still sealed - the cards simply stop mattering,
        because the official verdict prefers the stoppage (Rule 3: early
        stoppages terminate scoring)."""
        a, b = self._corners
        fa, fb = self._round_force[a], self._round_force[b]
        win = a if fa > fb else b if fb > fa else None
        for n in self._corners:
            base = 10.0 if (win is None or n == win) else 9.0
            self._cards[n] += base - self._round_knockdowns[n] - self._round_deductions[n]
        self._rounds_sealed += 1
        for n in self._corners:
            self._round_force[n] = 0.0
            self._round_knockdowns[n] = 0
            self._round_deductions[n] = 0

    def seal_final(self) -> None:
        self._final = True

    # ---- sealed cards out ------------------------------------------------
    def sealed_cards(self) -> dict:
        """The official totals, after the final bell only. Returns a copy, so
        the caller holds a reading rather than the cards themselves."""
        if not self._final:
            raise SealedCardsError("cards are sealed until the final bell")
        return dict(self._cards)
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | END ]
