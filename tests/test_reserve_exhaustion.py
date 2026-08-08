# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 09:30 UTC | START ]
"""Decision 0025 — Reserve exhaustion semantics, in the Python contract.

The ruling's eight proofs are required of the SHARED vectors, which need the
Unreal editor to run. These are the same eight against the contract alone, so a
regression fails in two and a half minutes of pytest rather than waiting for a
commandlet - and so the rules stay checked on a machine with no engine at all.

The failure being guarded against is specific. Before 0025, `step` read the
Reserve-derived recovery multiplier from an unclamped, possibly negative
Reserve. That did two things: it let the declared 0.40 floor be crossed, and it
put a negative numerator into the one division where Python's `//` and C++'s
`/` disagree. Neither was loud. The multiplier was wrong by three parts in four
thousand, and the languages differed by a single unit of Wind per tick.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.uppercut_stamina import economy as E  # noqa: E402

BIG = "overhand_rear"      # the largest authored reserve_load in the table


@pytest.fixture(scope="module")
def c():
    pack = E.economy_pack()
    assert not pack["errors"], pack["errors"]
    return pack


def _load(c, move):
    return c["moves"][move]["reserve"]


# --- 1. exact spend to zero --------------------------------------------------

def test_1_spending_exactly_to_zero_lands_on_zero(c):
    start = _load(c, BIG)
    _, reserve = E.step(c, 100000, start, "rest", move_id=BIG)
    assert reserve == 0, (
        "a fighter holding exactly one punch's worth of Reserve did not land "
        "on zero - the boundary is where an off-by-one in the clamp hides")


# --- 2. overdraw saturates ---------------------------------------------------

def test_2_overdraw_saturates_at_zero_and_the_action_still_happens(c):
    """The Director's worked example: 0.5 in the tank, a 2.0 punch thrown."""
    start = _load(c, BIG) // 4
    wind_before = 100000
    wind, reserve = E.step(c, wind_before, start, "rest", move_id=BIG)
    assert reserve == 0
    # The punch was not cancelled: its Wind cost was still charged.
    assert wind < wind_before, (
        "the action was silently refused. Decision 0025 allows a fighter to "
        "throw the punch that empties the tank; the punishment comes after")


def test_2b_overdrawing_twice_is_not_cumulative_debt(c):
    a = E.step(c, 100000, 100, "rest", move_id=BIG)
    b = E.step(c, 100000, 0, "rest", move_id=BIG)
    assert a[1] == b[1] == 0, (
        "overdraft accumulated. Reserve at zero is one state, not a ledger of "
        "how far past empty a fighter has gone")


# --- 3. stored Reserve is never negative -------------------------------------

@pytest.mark.parametrize("start", [0, 1, 7, 100, 599, 600, 601, 5000])
@pytest.mark.parametrize("action", ["rest", "attack", "observe", "move"])
def test_3_stored_reserve_never_leaves_the_interval(c, start, action):
    move = BIG if action != "move" else "step_in"
    wind, reserve = E.step(c, c["wind_low"] - 1, start, action, move_id=move,
                           displacement_ru=9000)
    assert 0 <= reserve <= c["reserve_max"]
    assert wind >= 0


def test_3b_a_whole_round_of_grinding_never_goes_negative(c):
    wind, reserve = c["wind_exhausted"], 400
    for _ in range(2000):
        wind, reserve = E.step(c, wind, reserve, "attack", move_id=BIG)
        assert reserve >= 0, "Reserve went negative mid-round"
    assert reserve == 0


# --- 4. the recovery floor is a real floor -----------------------------------

@pytest.mark.parametrize("action", ["rest", "observe", "hold_position",
                                    "micro_adjust"])
def test_4_recovery_never_falls_below_the_declared_floor(c, action):
    base = c["recover"][action]
    floor = E.floordiv(base * c["recovery_floor"], 10000)
    assert E.recovery_rate(c, action, 0) == floor, (
        "at zero Reserve the recovery rate must sit exactly on its declared "
        "floor multiplier, not below it")
    for reserve in range(0, 3000, 13):
        assert E.recovery_rate(c, action, reserve) >= floor


def test_4b_the_pre_0025_defect_would_be_caught(c):
    """The multiplier that used to be reachable, computed directly.

    This is the number the old code produced: reserve -150 gave 3997 against a
    declared floor of 4000. Asserting it is still BELOW the floor documents
    what the clamp is preventing - if this ever stops being true, the arithmetic
    changed and the clamp may no longer be load-bearing.
    """
    frac = E.floordiv(-150 * 10000, c["reserve_max"])
    breached = c["recovery_floor"] + E.floordiv(c["recovery_span"] * frac, 10000)
    assert breached < c["recovery_floor"], (
        "the unclamped path no longer breaches the floor, so this test is no "
        "longer describing the defect Decision 0025 was written for")
    # ...and the real path never gets there, because Reserve is clamped first.
    _, reserve = E.step(c, 100000, 450, "rest", move_id=BIG)
    assert reserve == 0


# --- 5. the Wind ceiling floor is a real floor -------------------------------

def test_5_wind_ceiling_never_falls_below_its_declared_floor(c):
    floor = E.floordiv(c["wind_max"] * c["ceiling_floor"], 10000)
    assert E.wind_ceiling(c, 0) == floor
    for reserve in range(0, c["reserve_max"], 7919):
        assert E.wind_ceiling(c, reserve) >= floor
    assert E.wind_ceiling(c, c["reserve_max"]) == c["wind_max"], (
        "a fighter at full Reserve cannot hold a full pool of Wind")


def test_5b_a_fighter_who_empties_the_tank_is_capped_at_the_floor(c):
    wind, reserve = E.step(c, c["wind_max"], 100, "attack", move_id=BIG)
    assert reserve == 0
    assert wind == E.floordiv(c["wind_max"] * c["ceiling_floor"], 10000)


# --- 6. invalid state is refused, not normalised -----------------------------

@pytest.mark.parametrize("reserve", [-1, -600, -1000000])
def test_6_negative_external_reserve_is_rejected(c, reserve):
    with pytest.raises(E.InvalidState):
        E.step(c, c["wind_start"], reserve, "rest")
    with pytest.raises(E.InvalidState):
        E.between_rounds(c, c["wind_start"], reserve)


def test_6b_reserve_above_max_is_rejected(c):
    with pytest.raises(E.InvalidState):
        E.step(c, c["wind_start"], c["reserve_max"] + 1, "rest")


def test_6c_the_endpoints_themselves_are_valid(c):
    """The interval is CLOSED. Rejecting its own endpoints would be the
    mirror-image bug and just as quiet."""
    E.step(c, c["wind_start"], 0, "rest")
    E.step(c, c["wind_start"], c["reserve_max"], "rest")


# --- 7. the corner cannot exceed the maximum ---------------------------------

def test_7_between_rounds_saturates_at_max(c):
    _, reserve = E.between_rounds(c, 0, c["reserve_max"])
    assert reserve == c["reserve_max"]
    _, near = E.between_rounds(c, 0, c["reserve_max"] - 1)
    assert near == c["reserve_max"]


def test_7b_the_corner_restores_reserve_but_not_freshness(c):
    """Decision 0021's whole claim, and 0025 must not have broken it."""
    _, reserve = E.between_rounds(c, 0, 0)
    assert 0 < reserve < c["reserve_max"], (
        "the corner either did nothing or made the fighter fresh; it is meant "
        "to do neither")


# --- 8. telemetry keeps what was requested -----------------------------------

def test_8_telemetry_records_the_requested_load_not_the_affordable_part(c):
    load = _load(c, BIG)
    tel = {}
    _, reserve = E.step(c, 100000, load // 4, "rest", move_id=BIG, telemetry=tel)
    assert reserve == 0
    assert tel["requested_reserve_load"] == load, (
        "the telemetry recorded what the balance could absorb. The fighter ran "
        "out of tank; the model must remember what the action demanded")
    assert tel["reserve_applied"] == load // 4
    assert tel["reserve_unpaid"] == load - load // 4
    assert tel["reserve_saturated"] is True


def test_8b_a_fully_paid_action_is_not_flagged_as_saturated(c):
    tel = {}
    E.step(c, 100000, c["reserve_max"] // 2, "rest", move_id=BIG, telemetry=tel)
    assert tel["reserve_unpaid"] == 0
    assert tel["reserve_saturated"] is False


def test_8c_sustained_exertion_is_reported_separately_from_the_move(c):
    tel = {}
    E.step(c, c["wind_low"] - 1, c["reserve_max"] // 2, "attack",
           move_id="jab_lead", telemetry=tel)
    assert tel["sustained_exertion"] == c["sustained_exertion"]
    assert tel["requested_reserve_load"] == _load(c, "jab_lead")
    assert tel["requested_reserve_total"] == (
        tel["requested_reserve_load"] + tel["sustained_exertion"]), (
        "a fighter grinding below the low-Wind line would look like he was "
        "being charged for the punch alone")


def test_8d_a_tick_that_commits_nothing_requests_nothing(c):
    tel = {}
    E.step(c, 100000, c["reserve_max"] // 2, "rest", telemetry=tel)
    assert tel["requested_reserve_total"] == 0
    assert tel["reserve_saturated"] is False
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 09:30 UTC | END ]
