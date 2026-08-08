# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 21:00 UTC | START ]
"""Decision 0029's typed quantities, and the seven adversarial cases it names.

    "If two numbers cannot be legally substituted in boxing, the live runtime
     should not make them trivially substitutable in code."

The seven required mutation cases are numbered below exactly as the decision
numbers them, so coverage can be checked against the ruling without reading the
code.
"""
import copy
import io
import json
import os

import pytest

from tools.uppercut_units import quantities as Q
from tools.uppercut_units import rates as R
from tools.uppercut_integrated.bout import IntegratedBout

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def rates():
    return R.load()


# ============================== the seven required adversarial cases =========

def test_1_a_per_action_value_supplied_to_a_per_tick_input():
    """A punch's price is per commitment. A guard held for a second must not
    pay for a guard sixty times - the 2026-08-08 defect, as a type error."""
    with pytest.raises(Q.BasisError):
        Q.Ticks(60) * Q.WindPerAction(2200)


def test_2_a_per_tick_value_supplied_to_a_per_distance_input():
    """A recovery rate is per tick. Multiplying it by a distance is not a
    smaller mistake for being arithmetically possible."""
    with pytest.raises(Q.BasisError):
        Q.displacement(1400) * Q.WindPerTick(60)


def test_3_a_stride_or_cap_supplied_as_actual_displacement(rates):
    """The defect that cost a 3.9x overcharge.

    A stride and a cap are both integers in reach units, so no type can tell
    them apart from a displacement by inspection - and this test says so
    honestly rather than pretending otherwise. What the type CAN do is force
    the value through one named door, `displacement()`, whose docstring is the
    warning and whose name is the question. The arithmetic difference is what
    the assertion measures.
    """
    stride, cap = 5500, 1400          # free_navigation stride vs the per-tick cap
    as_stride = rates.movement_wind(Q.displacement(stride))
    as_cap = rates.movement_wind(Q.displacement(cap))
    assert as_stride.q > as_cap.q * 3
    # And there is no other route: the rate object exposes no way to charge a
    # distance except through a ReachUnits.
    with pytest.raises(Q.BasisError):
        rates.movement_wind(stride)


def test_4_negative_distance_is_refused():
    with pytest.raises(Q.UnknownBasis):
        Q.displacement(-1)
    Q.displacement(0)                  # zero is legal; negative is not


def test_5_zero_displacement_produces_zero_movement_wind(rates):
    """Standing still is free. A fighter paying breath for ground he was not
    given is the ring doubling as a stamina tax."""
    assert rates.movement_wind(Q.displacement(0)) == Q.Wind(0)
    assert rates.movement_reserve(Q.displacement(0)) == Q.Reserve(0)


def test_6_identical_raw_numbers_on_different_bases_stay_distinguishable():
    """600 wind-per-tick and 600 wind-per-reach-unit are the same integer and
    must never be the same value - in comparison, in a dict, or in telemetry."""
    a, b = Q.WindPerTick(600), Q.WindPerReachUnit(600)
    assert a != b
    assert hash(a) != hash(b)
    assert a.telemetry("rate") != b.telemetry("rate")
    assert {a: "tick"}.get(b) is None
    with pytest.raises(Q.BasisError):
        a + b


def test_7_serialization_cannot_alter_numeric_meaning(rates):
    """No float ever enters the state, so no locale, precision or round-trip
    can move it. The values are integers and the telemetry prints integers."""
    d = Q.displacement(1400)
    w = rates.movement_wind(d)
    assert isinstance(d.q, int) and isinstance(w.q, int)
    # The NUMBER, not the label. The first version of this line scanned the
    # whole string for "e" to rule out scientific notation and tripped on the
    # word "debit" - a test too broad by one word, which is the same mistake as
    # scanning canon prose for the word "engagement".
    text = w.telemetry("movement_wind_debit")
    number = text.split("=", 1)[1].split(" ", 1)[0]
    assert "e" not in number.lower() and "," not in number
    assert json.loads(json.dumps({"q": w.q}))["q"] == w.q


# ============================== the basis is canon's, and it fails closed ====

def test_the_loader_refuses_a_field_canon_has_not_classified(tmp_path,
                                                             monkeypatch):
    econ = json.loads(io.open(os.path.join(REPO, "data",
                                           "stamina_economy.json"),
                              encoding="utf-8").read())
    stripped = copy.deepcopy(econ)
    del stripped["source_basis"]["sources"]["displacement_movement.wind_per_ru"]
    real = R._read

    def fake(rel):
        return stripped if rel == R.ECONOMY else real(rel)

    monkeypatch.setattr(R, "_read", fake)
    # MATCHED ON THE MESSAGE, because the first version of this test passed for
    # the wrong reason. With the missing-field guard disabled by a mutation
    # probe, the code fell through to "not in allowed" and still raised - so
    # the test was green while the guard it names was gone. An assertion that
    # cannot tell which guard fired is not testing that guard.
    with pytest.raises(Q.UnknownBasis, match="canon declares no basis"):
        R.load()


def test_the_loader_refuses_a_basis_that_contradicts_the_runtime(monkeypatch):
    econ = json.loads(io.open(os.path.join(REPO, "data",
                                           "stamina_economy.json"),
                              encoding="utf-8").read())
    lying = copy.deepcopy(econ)
    lying["source_basis"]["sources"]["displacement_movement.wind_per_ru"] = \
        "per_tick"
    real = R._read

    def fake(rel):
        return lying if rel == R.ECONOMY else real(rel)

    monkeypatch.setattr(R, "_read", fake)
    with pytest.raises(Q.UnknownBasis):
        R.load()


def test_the_loader_refuses_a_missing_source_basis_block(monkeypatch):
    econ = json.loads(io.open(os.path.join(REPO, "data",
                                           "stamina_economy.json"),
                              encoding="utf-8").read())
    blind = copy.deepcopy(econ)
    del blind["source_basis"]
    real = R._read

    def fake(rel):
        return blind if rel == R.ECONOMY else real(rel)

    monkeypatch.setattr(R, "_read", fake)
    with pytest.raises(Q.UnknownBasis):
        R.load()


def test_the_tick_rate_comes_from_canon_and_must_be_whole(rates):
    clock = json.loads(io.open(os.path.join(REPO, "data", "clock_model.json"),
                               encoding="utf-8").read())
    assert rates.tick_rate_hz == clock["authority"]["tick_rate_hz"]
    assert Q.ticks_to_seconds(Q.Ticks(180 * 60), rates.tick_rate_hz) \
        == Q.FightSeconds(180)
    assert Q.seconds_to_ticks(Q.FightSeconds(180), rates.tick_rate_hz) \
        == Q.Ticks(10800)


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 22:20 UTC | START edit: Decision 0031 ]
def test_the_per_second_conversion_no_longer_exists():
    """Decision 0031. The helper that stood here took a `WindPerTick` whose
    docstring said the value was actually per-second - a type saying one basis
    and a comment saying another, inside the module built to make that
    impossible. "A conversion may change a quantity's basis. A comment may
    not." Deleted rather than repaired, because no canon source is authored
    per-second; when one is, `WindPerSecond` and its named conversion arrive in
    the same change, and this test is rewritten to demand exactly that."""
    assert not hasattr(Q, "per_second_to_per_tick")
    assert not hasattr(Q, "WindPerSecond"), (
        "WindPerSecond exists but no canon source is authored per-second - "
        "Decision 0031 says the type arrives WITH the first real source, not "
        "ahead of it")


def test_the_legacy_unwrap_has_exactly_one_named_door(rates):
    """Decision 0031's second half: typed ReachUnits is the authority-bound
    displacement input, and the raw-integer unwrap for the proven legacy
    economy is confined to `legacy_economy_travel` - one name, one seam,
    deletable in one edit when the economy itself goes typed."""
    from tools.uppercut_integrated import fighter as F
    assert F.legacy_economy_travel(Q.displacement(1400)) == 1400
    assert F.legacy_economy_travel(None) == 0
    for wrong in (1400, 0.14, Q.Wind(1400), Q.WindPerReachUnit(6000),
                  Q.Ticks(1400)):
        with pytest.raises(Q.BasisError):
            F.legacy_economy_travel(wrong)


def test_the_fighter_refuses_a_raw_integer_travel(rates):
    """The old `travel_ru=<int>` spelling is gone, not deprecated: a caller
    holding a bare number fails today instead of drifting for a month."""
    from tools.uppercut_stamina import economy as E
    from tools.uppercut_integrated import fighter as F
    econ = E.economy_pack()
    f = F.FighterState("red_corner", econ)
    with pytest.raises(TypeError):
        f.step(econ, "move", travel_ru=1400)
    with pytest.raises(Q.BasisError):
        f.step(econ, "move", travel=1400)
    before = f.wind
    f.step(econ, "move", travel=Q.displacement(1400))
    # Against the typed path, not against a hardcoded 6000: the rate is
    # canon's, and a test that memorised it would survive a canon change the
    # fighter did not.
    assert before - f.wind == rates.movement_wind(Q.displacement(1400)).q
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 22:20 UTC | END edit ]


# ============================== the products, and only the products ==========

def test_the_three_products_the_decision_names(rates):
    assert Q.displacement(10000) * Q.WindPerReachUnit(6000) == Q.Wind(6000)
    assert Q.Ticks(100) * Q.WindPerTick(60) == Q.Wind(6000)
    assert Q.Actions(1) * Q.WindPerAction(2200) == Q.Wind(2200)


def test_products_commute_but_nothing_else_does():
    assert (Q.displacement(10000) * Q.WindPerReachUnit(6000)
            == Q.WindPerReachUnit(6000) * Q.displacement(10000))
    for a, b in ((Q.Wind(1), Q.Reserve(1)), (Q.Ticks(1), Q.Actions(1)),
                 (Q.WindPerTick(1), Q.WindPerAction(1)),
                 (Q.ReachUnits(1), Q.ReachUnits(1))):
        with pytest.raises(Q.BasisError):
            a * b


def test_a_bool_is_not_a_quantity():
    for kind in (Q.Ticks, Q.Wind, Q.ReachUnits):
        with pytest.raises(Q.BasisError):
            kind(True)


def test_every_declared_product_lands_on_a_declared_quantity():
    for (a, b), out in Q.PRODUCTS.items():
        assert issubclass(a, Q.Quantity) and issubclass(b, Q.Quantity)
        assert issubclass(out, Q.Quantity)
        assert out.BASIS


# ============================== and it reaches the artifact ==================

def test_the_stream_records_value_and_basis_not_one_opaque_number():
    """Decision 0029's telemetry rule, on the real stream."""
    bout = IntegratedBout(seed=4242).run(120)
    # `E` for energy. The stamina row moved off `W` when Phase R's evasion
    # WINDOW rows arrived and the two collided - one letter, two meanings, in a
    # stream whose entire value is being parseable.
    rows = [r for r in bout.rows if r.startswith("E|")]
    assert rows
    row = rows[0]
    for field in ("movement_displacement=", "movement_wind_rate=",
                  "movement_wind_debit="):
        assert field in row, row
    assert " ru" in row and " wind/ru" in row and " wind" in row
    assert "movement_cost=" not in row


def test_the_typed_debit_and_the_economy_agree_across_a_round():
    """The bout raises if they ever disagree, so running it is the assertion.
    Stated as a test anyway, because a guard nobody exercises is decoration."""
    bout = IntegratedBout(seed=4243).run(900)
    assert bout.moved_ru == bout.charged_ru
    assert bout.moved_ru > 0
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 21:00 UTC | END ]
