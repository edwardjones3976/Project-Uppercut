# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 01:15 UTC | START ]
"""The broadcast fence, held by a test rather than by good intentions.

THE RULE, from the council's elder-commentator brief: the commentator knows
only what a credible ringside observer could know. He may infer "that right
hand looks slower". He may not report "his Reserve has dropped to 26.4%".

`tools/uppercut_integrated/ringside.py` projects an exported fight down to the
observable. These tests hold that projection to its promise, because a fence
nothing patrols is a wish. They are ordinary regression guards - unlike
test_council_findings.py, every assertion here is the CORRECT behaviour.
"""
import re

import pytest

from tools.uppercut_integrated import export_fight as EX
from tools.uppercut_integrated import ringside as RS
from tools.uppercut_integrated.bout import IntegratedBout


@pytest.fixture(scope="module")
def fight():
    bout = IntegratedBout(seed=4242)
    bout.run_fight()
    return EX.export_fight(bout)


@pytest.fixture(scope="module")
def account(fight):
    return RS.transcript(fight) + "\n" + RS.result_paragraph(fight)


def test_the_projection_drops_the_fighters_reasoning(fight):
    """A fighter's intentions are the one thing nobody at ringside can read.

    The `D` rows carry the CPU's strategic aim, tactic and reason code in
    articulate boxing English, which makes them the most seductive material in
    the stream and the most dishonest thing a broadcast could quote. They are
    not exported as events at all; this asserts the projection would refuse
    them even if they were.
    """
    assert "decision" not in RS.OBSERVABLE
    smuggled = dict(fight)
    smuggled["events"] = list(fight["events"]) + [
        {"t": 1, "r": 1, "kind": "decision", "who": "red_corner",
         "reason": "R_SEEK_RECOVERY_SPACE"}]
    assert not [e for e in RS.observable_events(smuggled)
                if e["kind"] == "decision"]


def test_a_new_event_family_is_invisible_until_somebody_declares_it(fight):
    """Fail closed, in the direction the rest of the repository fails closed.

    The projection carries through a NAMED list. An event family nobody has
    ruled observable does not reach the broadcast by default - which is the
    opposite of the usual presentation failure, where anything in the log is
    fair game because it was there.
    """
    invented = dict(fight)
    invented["events"] = list(fight["events"]) + [
        {"t": 1, "r": 1, "kind": "internal_pressure_calculation",
         "who": "red_corner", "value": 6142}]
    assert not [e for e in RS.observable_events(invented)
                if e["kind"] == "internal_pressure_calculation"]


def test_no_internal_quantity_is_ever_printed(account):
    """Wind, Reserve and damage reach the page as words or not at all.

    The condition tables convert q10000 quantities into five coarse phrases,
    which is roughly the resolution a human eye has: two fighters at 41% and
    39% both read "breathing hard", and that is correct rather than lossy.
    This asserts the numbers themselves never survive the projection.
    """
    for banned in ("wind=", "reserve=", "q10000", "fraction",
                   "pressure", "threshold", "seed"):
        assert banned not in account.lower(), banned
    # No bare four- or five-digit fixed-point value anywhere in the prose.
    for token in re.findall(r"\b\d{4,}\b", account):
        pytest.fail("a raw internal quantity reached the broadcast: %s" % token)


def test_what_a_person_could_see_does_survive(account):
    """The fence is not a gag order. Everything a person in the building could
    have seen must still be there - including, after the elder commentator's
    correction, punches actually landing. An account that shows men falling
    down and never shows anybody getting hit is a rumour, not a broadcast.
    """
    assert "is DOWN" in account
    assert "the count reaches" in account
    assert "is up at" in account
    assert "lands" in account or "breaks the lull" in account
    assert "threw" in account and "landed" in account


def test_the_cards_stay_sealed_until_the_fight_is_over():
    """The same seal the bout itself keeps. An unfinished fight has no cards,
    and the projection does not go looking for them."""
    bout = IntegratedBout(seed=4242)
    bout.run(600)
    partial = EX.export_fight(bout)
    assert partial["cards"] == {}
    assert "10-" not in RS.result_paragraph(partial)


def test_a_count_that_outlives_the_round_reads_past_three_minutes(fight):
    """Nobody is saved by the bell, so a count starting at 2:54 finishes after
    the round has expired. The clock must say 3:02 and not wrap to 0:02 - a
    wrapped clock makes a round-one knockdown look like round two, and a person
    in the building sees one unbroken count.
    """
    rt, hz = fight["meta"]["round_ticks"], fight["meta"]["tick_hz"]
    assert RS._clock(rt + 2 * hz, rt, hz, 1) == "3:02"
    assert RS._clock(rt + 2 * hz, rt, hz, 2) == "0:02"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 01:15 UTC | END ]
