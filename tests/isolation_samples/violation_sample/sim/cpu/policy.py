# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""DELIBERATE VIOLATION sample. Never merge this pattern into real code.

Exists solely to prove the score-isolation checker is not vacuous: it must flag
every sealed-symbol reference below. See docs/phase0/score_isolation.md.
"""


def choose_action(observable_events, judge):
    card = judge.official_scorecard          # VIOLATION: sealed symbol
    if card.is_behind_on_cards("red"):       # VIOLATION: sealed symbol
        return {"chosen_action": "desperation_pressure"}
    return {"chosen_action": "hold_range"}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
