# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 07:10 UTC | START ]
"""The two-tier stamina economy, tested against the ways it has already failed.

Decision 0021 says what Wind and Reserve ARE. These tests hold the two defects
found in the first hour of implementing them, because both were silent: the
model ran, reported plausible-looking numbers, and said boxing is not tiring.

  1. THE UNITS ERROR, MADE TWICE. Wind recovery was authored at 0.020 per tick
     for Rest. Over a 180-second round that is 216 against a pool of 100, so no
     fighter could tire at any work rate. The project made this exact mistake on
     2026-08-03 and the correction is quoted in condition_model. It was made
     again on 2026-08-07 in a block whose own comment cited that correction.
     Small per-tick decimals look innocent until multiplied by the round.

  2. THE SILENT ZERO. `move_cost` returned (0, 0) for an unrecognised move, and
     the first probe passed the ACTION FAMILY ("attack") where a MOVE ID
     ("cross_rear") belongs. Every punch was free. Nothing raised, nothing
     failed, and a fighter throwing 120 punches a round finished fresh.

Neither would have been caught by a test that only asked "does a punch reduce
Wind". They were caught by asking what a whole round costs.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.uppercut_stamina import economy as E  # noqa: E402

ROUND_TICKS = 180 * 60
PUNCH = "cross_rear"


@pytest.fixture(scope="module")
def c():
    return E.economy_pack()


def test_canon_is_executable(c):
    assert c["errors"] == []


# --- defect 1: the units error ----------------------------------------------

def test_no_recovery_rate_can_refill_the_pool_inside_one_round(c):
    """The guard that would have caught 2026-08-03 and 2026-08-07."""
    for state, rate in c["recover"].items():
        per_round = rate * ROUND_TICKS
        assert per_round <= c["wind_max"], (
            "%s recovers %.1f Wind per round against a pool of %.1f - at that "
            "rate nobody ever tires, whatever they do"
            % (state, per_round / 10000.0, c["wind_max"] / 10000.0))


def test_a_round_of_pure_rest_does_not_fully_refill_from_empty(c):
    """Resting the whole round must be worth a lot and not everything."""
    w, r = 0, c["reserve_start"]
    for _ in range(ROUND_TICKS):
        w, r = E.step(c, w, r, "rest")
    assert 0 < w < c["wind_max"], (
        "a round of rest from empty ends at %.1f; if it reaches the ceiling, "
        "the corner and the round stop meaning anything different"
        % (w / 10000.0))


def test_the_units_guard_actually_fires(c):
    """A test that cannot fail protects nothing."""
    broken = dict(c, recover=dict(c["recover"], rest=200))   # 0.02/tick
    per_round = broken["recover"]["rest"] * ROUND_TICKS
    assert per_round > broken["wind_max"]


# --- defect 2: the silent zero ----------------------------------------------

def test_an_unknown_move_raises_rather_than_costing_nothing(c):
    with pytest.raises(E.UnknownMove):
        E.move_cost(c, "attack")           # an action family, not a move
    with pytest.raises(E.UnknownMove):
        E.move_cost(c, "no_such_move")


def test_an_unknown_action_family_raises(c):
    with pytest.raises(ValueError):
        E.step(c, c["wind_start"], c["reserve_start"], "cross_rear")


def test_a_punch_actually_costs_wind(c):
    w0, r0 = c["wind_start"], c["reserve_start"]
    w1, r1 = E.step(c, w0, r0, "attack", move_id=PUNCH)
    assert w1 < w0, "a punch that costs nothing is not a punch"
    assert r1 < r0, "and it loads conditioning too"


def test_a_busy_round_costs_more_than_a_quiet_one(c):
    def run(every):
        w, r = c["wind_start"], c["reserve_start"]
        for t in range(ROUND_TICKS):
            if t % every == 0:
                w, r = E.step(c, w, r, "attack", move_id=PUNCH)
            else:
                w, r = E.step(c, w, r, "observe")
        return w

    quiet, busy = run(240), run(90)
    assert busy < quiet < c["wind_max"], (
        "work rate does not move the economy: quiet=%.1f busy=%.1f"
        % (quiet / 10000.0, busy / 10000.0))


# --- Decision 0021's structural claims ---------------------------------------

def test_reserve_does_not_meaningfully_recover_inside_a_round(c):
    w, r = c["wind_start"], c["reserve_start"] // 2
    before = r
    for _ in range(ROUND_TICKS):
        w, r = E.step(c, w, r, "rest")
    assert r == before, (
        "Reserve moved during a round of rest. A short pause may restore Wind; "
        "it may not restore the legs.")


def test_the_corner_returns_wind_and_barely_returns_reserve(c):
    w, r = c["wind_max"] // 4, c["reserve_max"] // 2
    w2, r2 = E.between_rounds(c, w, r)
    assert w2 > w, "the corner has to be worth something"
    gained_wind = (w2 - w) / float(c["wind_max"])
    gained_reserve = (r2 - r) / float(c["reserve_max"])
    assert gained_wind > gained_reserve * 5, (
        "between rounds returned %.1f%% of Wind and %.1f%% of Reserve - if "
        "those are comparable there is only one resource wearing two names"
        % (gained_wind * 100, gained_reserve * 100))


def test_later_rounds_start_and_end_worse(c):
    """Round ten must feel different from round one."""
    w, r = c["wind_start"], c["reserve_start"]
    starts = []
    for _ in range(10):
        starts.append(w)
        for t in range(ROUND_TICKS):
            if t % 166 == 0:
                w, r = E.step(c, w, r, "attack", move_id=PUNCH)
            else:
                w, r = E.step(c, w, r, "observe")
        w, r = E.between_rounds(c, w, r)
    assert starts == sorted(starts, reverse=True), \
        "rounds do not begin progressively worse"
    assert starts[-1] < starts[0], (
        "round ten begins at %.1f and round one at %.1f - a fight with no "
        "accumulation is a series of first rounds"
        % (starts[-1] / 10000.0, starts[0] / 10000.0))


def test_reserve_reaches_a_fighter_only_indirectly(c):
    """Decision 0021: through the Wind ceiling and Wind recovery, never as a
    second direct term. Deep fatigue must not be counted twice."""
    fresh = E.wind_ceiling(c, c["reserve_max"])
    spent = E.wind_ceiling(c, 0)
    assert fresh == c["wind_max"], "a fresh fighter must be able to be full"
    assert spent < fresh, "a drained fighter must hold less breath"

    fast = E.recovery_rate(c, "rest", c["reserve_max"])
    slow = E.recovery_rate(c, "rest", 0)
    assert slow < fast, "a drained fighter must get his breath back slower"


def test_working_below_the_low_wind_line_costs_conditioning(c):
    """The mechanism that turns a reckless early pace into a late problem."""
    low = c["wind_low"] - 1
    _, r_working = E.step(c, low, c["reserve_start"], "attack", move_id=PUNCH)
    _, r_resting = E.step(c, low, c["reserve_start"], "rest")
    assert r_working < r_resting


def test_body_work_costs_less_breath_and_more_conditioning(c):
    """The inversion that justifies three numbers instead of one.

    A body hook and a lead hook are authored at equal effort. If they ever cost
    the same in both tiers, `effort` and `wind_cost` have recollapsed and
    Decision 0021's decoupling is decorative.
    """
    head, body = c["moves"]["hook_lead"], c["moves"]["body_hook_lead"]
    assert head["effort"] == body["effort"]
    assert body["wind"] < head["wind"]
    assert body["reserve"] > head["reserve"]


def test_movement_is_priced_by_distance_not_by_a_flat_fee(c):
    """Decision 0014's G1 ruling, carried into the two-tier economy."""
    near, _ = E.move_cost(c, "step_in", displacement_ru=1000)
    far, _ = E.move_cost(c, "step_in", displacement_ru=4000)
    still, _ = E.move_cost(c, "step_in", displacement_ru=0)
    assert still == 0, "standing still must cost nothing"
    assert far > near > 0


def test_nothing_here_claims_to_be_calibrated():
    """Decision 0021 step 7 forbids fitting until an observable policy runs."""
    import io
    import json
    econ = json.load(io.open(os.path.join(ROOT, "data", "stamina_economy.json"),
                             encoding="utf-8"))
    effort = json.load(io.open(os.path.join(
        ROOT, "data", "moves", "generic_sandbox_effort.json"), encoding="utf-8"))
    assert econ["calibration_status"]["values_are_fitted"] is False
    assert effort["calibration_status"]["values_are_fitted"] is False
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 07:10 UTC | END ]
