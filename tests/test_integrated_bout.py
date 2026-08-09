# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 14:35 UTC | START ]
"""The first integrated bout: a policy decision moves a boxer, and the ground
he covers is what he pays for.

Also the extraction proof. Phase Q's rules were MOVED into a shared module so
the integrated bout could call them rather than copy them, and the strongest
statement about that move is not in this file - it is that Phase Q's golden
stream is byte-identical afterwards. What is here is the part a unit test can
carry: that both callers reach the same objects, and that no rule was quietly
duplicated on the way.
"""
import io
import os

import pytest

from tools.engine import analyze_core_range as Q
from tools.uppercut_range import core as RANGE
from tools.uppercut_integrated.bout import IntegratedBout
from tools.uppercut_stamina import economy as E

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def bout():
    return IntegratedBout(seed=4242).run(600)


# ------------------------------------------------- the extraction, proved ----

def test_the_analyzer_and_the_shared_core_are_the_same_objects():
    """Not "they agree" - the same function. Agreement can drift; identity
    cannot, and identity is what "one implementation" means."""
    for name in ("range_pack", "band_at", "resolve_band", "in_band",
                 "step_delta", "drain", "clamp_separation", "rope_scaled",
                 "running_is_finite", "footwork_is_not_inert",
                 "hysteresis_kills_flicker"):
        assert getattr(Q, name) is getattr(RANGE, name), name


def test_the_two_fixed_point_conversions_agree():
    """The shared core defines its own `q`; the analyzer keeps the one it had.
    Two definitions of a rounding rule is one more than this project allows to
    go unwatched, so they are compared rather than assumed."""
    for v in (0, 0.1, 0.12, 0.14, 0.22, 0.55, 0.9, 1.05, 4.92, 6.4, 100.0):
        assert RANGE.q(v) == Q.q(v), v


def test_the_integrated_bout_imports_no_phase_analyzer():
    """Decision 0022's rule, checked on the file rather than remembered."""
    src = io.open(os.path.join(REPO, "tools", "uppercut_integrated", "bout.py"),
                  encoding="utf-8").read()
    for forbidden in ("analyze_core_range", "analyze_core_evade",
                      "analyze_core_round", "analyze_core_condition"):
        assert forbidden not in src.split('"""', 2)[2], forbidden


def test_the_bout_defines_no_range_rule_of_its_own():
    """The loop may own the ORDER. It may not own a rule."""
    src = io.open(os.path.join(REPO, "tools", "uppercut_integrated", "bout.py"),
                  encoding="utf-8").read()
    for rule in ("def band_at", "def resolve_band", "def drain",
                 "def step_delta", "def rope_scaled", "def clamp_separation"):
        assert rule not in src, rule


# ------------------------------------------- a decision moves a boxer --------

# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:15 UTC | START edit: Phase R changed the cadence ]
@pytest.fixture(scope="module")
def full_round():
    """A whole three-minute round.

    These two tests used the ten-second `bout` fixture and passed until evasion
    entered the loop. They fail on ten seconds now, and that is the finding
    rather than the bug: with commitment lasting the animation canon authors, a
    fighter is throwing, recovering or resting for almost every tick, and the
    first step does not happen inside ten seconds. See
    `test_footwork_is_rare_and_that_is_the_finding` below for the number.
    """
    return IntegratedBout(seed=4242).run(180 * 60)


def test_a_policy_decision_physically_moved_a_boxer(full_round):
    start = RANGE.q(0.90)
    assert full_round.separation() != start
    assert full_round.moved_ru > 0
    assert any(r.startswith("X|") for r in full_round.rows)


def test_footwork_is_rare_and_that_is_the_finding(full_round):
    """A NUMBER ON THE RECORD, asserted so it announces itself when it moves.

    Across a full round these two fighters take footwork on a few dozen ticks
    out of 10,800. Real boxers are on their feet for all three minutes. Nothing
    here is tuned - Decision 0026 Ruling C and R5 both hold - but the shape is
    now measurable for the first time, and a reader should meet it as a finding
    rather than infer it from a small `moved_ru`.

    The mechanism, from the decision log: commitment windows plus recovery plus
    the recovery-space loop consume nearly every tick, so movement only happens
    in the slivers left over.
    """
    steps = len([r for r in full_round.rows if r.startswith("X|")])
    assert 0 < steps < 500, (
        "footwork ticks per round moved to %d - if this is now a plausible "
        "amount of boxing, retire this test and say so in the log" % steps)
# [ ... | 2026-08-09 02:15 UTC | END edit ]


def test_the_movement_came_from_a_decision_and_not_from_nowhere(bout):
    """Every X row must be preceded by a decision that intended movement."""
    intents = {"Advance", "Retreat", "MicroAdjust"}
    decided = set()
    for row in bout.rows:
        f = row.split("|")
        # D|tick|who|strategic|TACTICAL|execution|reason|initiative - the
        # tactic is field 4. The first draft read field 3 and asserted against
        # the strategic intent, which is a different vocabulary and never
        # matches; the test failed for the wrong reason and said so.
        if f[0] == "D" and f[4] in intents:
            decided.add(f[2])
        if f[0] == "X":
            assert f[2] in decided, row


# --------------------------------- the charge is the ground, not the intent --

def test_every_reach_unit_travelled_is_a_reach_unit_billed(full_round):
    """The invariant Decision 0026 Ruling C reduces to, and the one that
    caught this module's own defect on its first run: 3.74 units covered
    against 2.34 billed, because a step taken on a punching tick was free."""
    assert full_round.moved_ru == full_round.charged_ru
    assert full_round.moved_ru > 0


def test_the_bill_matches_the_rate_canon_declares(bout):
    """Travel costs displacement times the authored per-reach-unit rate.

    Asserted against the economy directly rather than scraped off the W rows.
    The first version scraped, and failed on a tick where the fighter was
    resting while a stride owed from earlier was delivered: the net Wind change
    was the travel charge MINUS that tick's recovery, so the row said 446 where
    the travel alone was 480. The row was right and the test was reading a net
    as if it were a charge.
    """
    econ = bout.econ
    for ru in (0, 100, 800, 1400):
        w0, r0 = E.step(econ, econ["wind_start"], econ["reserve_start"],
                        "move", travel_ru=ru)
        expected = E.floordiv(ru * econ["wind_per_ru"], 10000)
        assert econ["wind_start"] - w0 == expected, ru
        assert (econ["reserve_start"] - r0
                == E.floordiv(ru * econ["reserve_per_ru"], 10000)), ru


def test_travel_is_charged_even_on_a_tick_that_also_punches(bout):
    """The defect this module found in itself. `move_id` holds one move, so a
    punch used to displace the travel and the ground came free."""
    econ = bout.econ
    still = E.step(econ, econ["wind_start"], econ["reserve_start"],
                   "attack", move_id="jab_lead")
    moving = E.step(econ, econ["wind_start"], econ["reserve_start"],
                    "attack", move_id="jab_lead", travel_ru=1400)
    assert moving[0] < still[0]
    assert (still[0] - moving[0]
            == E.floordiv(1400 * econ["wind_per_ru"], 10000))


def test_no_travel_means_no_travel_charge(bout):
    """Standing still is free. A fighter paying a fee not to move is a fighter
    the economy is inventing work for."""
    econ = bout.econ
    a = E.step(econ, econ["wind_start"], econ["reserve_start"], "hold_position")
    b = E.step(econ, econ["wind_start"], econ["reserve_start"],
               "hold_position", travel_ru=0)
    assert a == b


# ------------------------------------------------- the rules still hold ------

def test_no_tick_moves_further_than_the_declared_cap(bout):
    cap = bout.range["cap"]
    for row in bout.rows:
        f = row.split("|")
        if f[0] == "X":
            assert abs(int(f[3])) <= cap, row


def test_bodies_never_overlap(bout):
    floor = bout.range["min_sep"]
    for row in bout.rows:
        f = row.split("|")
        if f[0] == "X":
            assert int(f[6]) >= floor, row


def test_a_fighter_never_leaves_the_ring(bout):
    for f in bout.fighters:
        assert 0 <= f.pos <= bout.range["axis"]


# ------------------------------------------------------- the artifact --------

def test_the_same_seed_reproduces_the_same_bout():
    a = IntegratedBout(seed=4242).run(300).stream()
    b = IntegratedBout(seed=4242).run(300).stream()
    assert a == b


def test_a_different_seed_is_a_different_bout():
    a = IntegratedBout(seed=4242).run(300).stream()
    b = IntegratedBout(seed=4243).run(300).stream()
    assert a != b
    # Non-vacuously: the fight moved, not merely the recorded seed line.
    a_rows = [r for r in a.splitlines() if r.startswith("D|")]
    b_rows = [r for r in b.splitlines() if r.startswith("D|")]
    assert a_rows != b_rows


def test_the_stream_carries_its_own_header_and_trailer(bout):
    lines = bout.stream().splitlines()
    assert lines[0].startswith("H|phase=INTEGRATED")
    assert any(l.startswith("H|participants=") for l in lines)
    assert lines[-1].startswith("S|ticks=")
    assert "fnv=" in lines[-1]


def test_the_trailer_hash_covers_the_rows(bout):
    """Change one row and the trailer must move, or the hash is decoration."""
    lines = bout.stream().splitlines()
    trailer = lines[-1]
    from tools.uppercut_integrated import bout as B
    h = B.FNV_OFFSET
    for row in lines[:-1]:
        h = B.fnv1a64(h, row)
    assert ("fnv=%016x" % h) in trailer
    h2 = B.FNV_OFFSET
    for row in lines[:-1]:
        h2 = B.fnv1a64(h2, row.replace("red_corner", "blue_corner", 1))
    assert h2 != h
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 14:35 UTC | END ]
