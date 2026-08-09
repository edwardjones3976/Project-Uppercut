# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 14:25 UTC | START ]
"""The guard, extracted from Phase L and finally inside the fight.

Decision 0035 measured the guard's absence as the largest cause of an
unwatchable fight: nothing stopped a punch except an evasion, and the ten
postures were authored and inert. These tests hold the two claims that
matter - that the extraction moved the rule without changing it, and that the
rule now runs in the bout with canon's own emergences intact.
"""
import pytest

from tools.uppercut_guard import core as GUARD
from tools.uppercut_integrated import contract as C
from tools.uppercut_integrated.bout import IntegratedBout


@pytest.fixture(scope="module")
def gp():
    return GUARD.guard_pack()


@pytest.fixture(scope="module")
def bout():
    b = IntegratedBout(seed=4242)
    b.run(6000)
    return b


def test_canon_holds_its_own_contract(gp):
    assert gp["canon_errors"] == []
    assert gp["postures"], "no posture authored"
    assert 0 < gp["committed_multiplier"] < 10000
    assert gp["threshold"] > 0


def test_a_guard_is_a_structure_and_not_a_defence_rating(gp):
    """The project's core combat rule, arriving as arithmetic rather than as
    a design document.

    `high_guard` (head 0.95 / body 0.55) closes the head lane and sells the
    body; `tight_elbow` (0.55 / 0.95) is the exact mirror. Neither is "more
    defensive" than the other - each protects some lanes while exposing
    others, and canon's single interception threshold is what makes that
    true. Nothing here is written; it all falls out of the extents.
    """
    high = GUARD.covered(gp, "high_guard", False)
    tight = GUARD.covered(gp, "tight_elbow", False)
    assert "high" in high and "low" not in high
    assert "low" in tight and "high" not in tight
    # A shell closes both; a dropped lead closes neither. The spread is the
    # point - if every posture covered the same lanes there would be no trade.
    assert GUARD.covered(gp, "peek_a_boo", False) == frozenset(("high", "low"))
    assert GUARD.covered(gp, "low_lead", False) == frozenset()


def test_commitment_opens_the_lane_the_guard_was_closing(gp):
    """The counterpunch, from two authored numbers meeting and no third.

    0.95 x 0.6 = 0.57, which falls under the 0.6 interception threshold. A
    fighter caught inside his own commitment loses the lane he was covering,
    and no line of code decides that - the multiplier and the threshold do.
    """
    assert "high" in GUARD.covered(gp, "high_guard", False)
    assert "high" not in GUARD.covered(gp, "high_guard", True)
    # And it is a scaling, not a switch: a posture whose extent clears the
    # threshold even after scaling still covers.
    assert "high" in GUARD.covered(gp, "ear_muff", True)


def test_the_lane_is_the_path_not_the_target(gp):
    """A guard protects the interception path, not merely the final target.

    Canon maps a punch to a lane by GUARD INTERACTION - where the punch
    travels through - and the uppercut is authored `blockable_low` even
    though it finishes at the jaw. A high guard therefore does not stop it,
    which is the whole reason the uppercut is the punch for a covered-up
    opponent.
    """
    assert GUARD.lane_of(gp, C.PUNCHES, "jab_lead") == "high"
    assert GUARD.lane_of(gp, C.PUNCHES, "uppercut_rear") == "low"
    assert GUARD.intercepts(gp, C.PUNCHES, "high_guard", False, "jab_lead")
    assert not GUARD.intercepts(gp, C.PUNCHES, "high_guard", False,
                                "uppercut_rear")
    assert GUARD.intercepts(gp, C.PUNCHES, "tight_elbow", False,
                            "uppercut_rear")


def test_it_fails_closed_on_everything_it_does_not_know(gp):
    with pytest.raises(KeyError):
        GUARD.covered(gp, "no_such_posture", False)
    with pytest.raises(KeyError):
        # A guard is not a punch, even though canon authors its interaction.
        GUARD.lane_of(gp, C.PUNCHES, "guard_high")
    with pytest.raises(KeyError):
        GUARD.lane_of(gp, C.PUNCHES, "spinning_backfist")


def test_canon_prices_a_miss_above_a_block():
    """`punch_model.outcome_recovery`, authored since step 6 and unread until
    Decision 0035. The ordering is `contact_classes.commitment_tier` made
    real: the arm that stops on structure travelled less far than the arm
    that found nothing, and the defender who MOVED earns more than the
    defender who merely covered.
    """
    o = GUARD.outcome_pack()
    m = o["recovery_multiplier"]
    assert m["blocked"] < m["dodged"] < m["whiffed"]
    assert m["solid"] == 10000, "landing is never punished for landing"
    assert o["counter_window"]["whiffed"] > o["counter_window"]["blocked"]


# ------------------------------------------------------- inside the fight --

def test_the_guard_actually_stops_punches_in_a_real_bout(bout):
    """The regression that matters. The first wiring read "committed" as any
    recovery tick, which is true on nearly every tick, and the guard blocked
    ONE punch in twelve rounds - authored, wired, and still inert. A
    structure that is never up is not a guard.
    """
    assert bout.blocked > 0
    blocked_rows = [r for r in bout.rows
                    if r.startswith("P|") and r.endswith("|blocked")]
    assert len(blocked_rows) == bout.blocked
    # Every block names the posture that made it, so a replay can say WHY.
    for r in blocked_rows[:20]:
        assert "|guard=" in r


def test_a_dodged_punch_is_never_also_blocked(bout):
    """Phase R's `outranks_guard`, honoured by position: a punch the evasion
    answered never reaches the guard stage at all."""
    for r in bout.rows:
        if r.startswith("P|") and r.endswith("|blocked"):
            # A blocked punch ARRIVED past the movement and was then stopped
            # by structure. The row carries both words because canon prices
            # them differently, and a block recorded as a dodge would say the
            # defender moved when he covered.
            assert "|arrived|" in r, r
    for r in bout.rows:
        if r.startswith("P|") and "|dodged|" in r:
            assert not r.endswith("|blocked"), r


def test_holding_a_structure_costs_what_canon_says(gp):
    """`posture_economy.hold_cost_applies_when: not_committed` - you are not
    holding a guard mid-punch, you are punching. Every posture authors a
    per-tick hold, and the spread between them is what makes carrying a tight
    one a decision rather than a free upgrade."""
    holds = {p: s["hold_per_tick"] for p, s in gp["postures"].items()}
    assert all(h >= 0 for h in holds.values())
    assert len(set(holds.values())) > 1, (
        "every posture costs the same to hold, so the choice is free")
    assert gp["hold_applies_when"] == "not_committed"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 14:25 UTC | END ]
