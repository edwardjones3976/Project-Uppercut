# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 10:20 UTC | START ]
"""The divergence tracer must not manufacture the divergence it reports.

Decision 0040's second calibration prerequisite is a tick-by-tick trace of where
the C++ and Python rounds first disagree. The failure mode that would make such
a trace worthless is subtle and easy to write by accident: pairing the two
streams by row order. The runtimes decide on different clocks, so row N on one
side is not row N on the other, and an index-paired diff would report a
divergence at the first row of any two runs - including two runs that actually
agreed everywhere they met.

These tests hold the alignment honest. They assert nothing about the size of the
gap, which is a live finding rather than a fixed expectation.
"""
from tools.engine.trace_integrated_divergence import Decision, first_divergence


def d(tick, who, tactic, execution, reason):
    return Decision(tick, who, tactic, execution, reason)


def test_alignment_is_by_tick_and_fighter_not_by_row_order():
    """Same decisions, different cadence: no divergence where they meet."""
    cpp = [d(0, "red", "Rest", "-", "RECOVER_WIND"),
           d(4, "red", "Attack", "jab_lead", "PUNISH_RECOVERY")]
    py = [d(0, "red", "Rest", "-", "RECOVER_WIND"),
          d(1, "red", "Observe", "-", "HOLD_GOOD_RANGE"),
          d(2, "red", "Observe", "-", "HOLD_GOOD_RANGE"),
          d(3, "red", "Observe", "-", "HOLD_GOOD_RANGE"),
          d(4, "red", "Attack", "jab_lead", "PUNISH_RECOVERY")]
    out = first_divergence(cpp, py)
    assert out["alignable"] == 2
    assert out["identical"] == 2
    assert out["tick"] is None, (
        "the tracer found a divergence between two runtimes that agree on "
        "every tick they share - it is pairing by row order")


def test_the_same_tick_for_a_different_fighter_is_not_an_alignment():
    cpp = [d(7, "red", "Attack", "jab_lead", "PUNISH_RECOVERY")]
    py = [d(7, "blue", "Retreat", "step_out", "EXIT_BAD_RANGE")]
    out = first_divergence(cpp, py)
    assert out["alignable"] == 0
    assert out["tick"] is None


def test_a_real_disagreement_is_reported_with_both_sides():
    cpp = [d(0, "red", "Rest", "-", "RECOVER_WIND"),
           d(4, "red", "Attack", "uppercut_rear", "PUNISH_RECOVERY")]
    py = [d(0, "red", "Rest", "-", "RECOVER_WIND"),
          d(4, "red", "Retreat", "step_out", "EXIT_BAD_RANGE")]
    out = first_divergence(cpp, py)
    assert out["tick"] == 4
    assert out["who"] == "red"
    assert out["agreed_before"] == 1
    assert out["cpp"].tactic == "Attack" and out["py"].tactic == "Retreat"


def test_the_reported_totals_cover_the_whole_aligned_set_not_just_the_prefix():
    """`identical` must be scored over every aligned pair. Counting only the
    pairs before the first mismatch would let 'agreed until tick 4' stand in
    for 'agreed once in a thousand chances'."""
    cpp = [d(0, "red", "Rest", "-", "RECOVER_WIND"),
           d(1, "red", "Attack", "jab_lead", "PUNISH_RECOVERY"),
           d(2, "red", "Rest", "-", "RECOVER_WIND")]
    py = [d(0, "red", "Rest", "-", "RECOVER_WIND"),
          d(1, "red", "Retreat", "step_out", "EXIT_BAD_RANGE"),
          d(2, "red", "Rest", "-", "RECOVER_WIND")]
    out = first_divergence(cpp, py)
    assert out["alignable"] == 3
    assert out["identical"] == 2, "pairs after the first mismatch were not scored"
    assert out["tick"] == 1


def test_a_divergence_in_the_reason_alone_still_counts():
    """Two runtimes reaching the same move for different stated reasons have
    not agreed - the reason code is the observable part of the policy."""
    cpp = [d(3, "red", "Rest", "-", "RECOVER_WIND")]
    py = [d(3, "red", "Rest", "-", "REST_WHEN_SAFE")]
    out = first_divergence(cpp, py)
    assert out["tick"] == 3
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 10:20 UTC | END ]
