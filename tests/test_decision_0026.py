# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 10:40 UTC | START ]
"""Decision 0026, proved rather than asserted.

Ruling A gives six required isolation proofs, Ruling B a required tactical
grammar with hysteresis, Ruling D five behavioural regression proofs. They are
grouped below in the ruling's own order so a reader can check coverage against
the decision record without reading the code.
"""
import pytest

from tools.uppercut_integrated import contract as C
from tools.uppercut_integrated import fighter as F
from tools.uppercut_integrated import policy as P
from tools.uppercut_integrated import rng as R
from tools.uppercut_stamina import economy as E

RED, BLUE = C.DEFAULT_PARTICIPANTS


@pytest.fixture(scope="module")
def econ():
    c = E.economy_pack()
    assert not c["errors"], c["errors"]
    return c


def bout(seed=4242, participants=C.DEFAULT_PARTICIPANTS):
    return R.BoutRng(seed, C.CONTRACT, participants)


# ================================================ Ruling A: isolation proofs ==

def test_a1_extra_red_draws_cannot_move_blue():
    """One extra policy decision for red; blue's next draw is unchanged.

    This is the whole ruling in one test. Under the shared cursor it fails,
    because red's draw advanced the object blue was about to read.
    """
    a, b = bout(), bout()
    baseline = [b.stream("policy_intent", BLUE).below(1000) for _ in range(3)]
    a.stream("policy_intent", RED).below(1000)          # red thinks once more
    after = [a.stream("policy_intent", BLUE).below(1000) for _ in range(3)]
    assert after == baseline


def test_a2_extra_blue_draws_cannot_move_red():
    a, b = bout(), bout()
    baseline = [b.stream("policy_intent", RED).below(1000) for _ in range(3)]
    for _ in range(17):
        a.stream("policy_intent", BLUE).below(1000)
    after = [a.stream("policy_intent", RED).below(1000) for _ in range(3)]
    assert after == baseline


def test_a3_reordering_participants_changes_nothing():
    """Declaration order is not authority. Identity is."""
    forward = bout(participants=(RED, BLUE))
    backward = bout(participants=(BLUE, RED))
    for who in (RED, BLUE):
        assert (forward.stream("policy_intent", who).seed
                == backward.stream("policy_intent", who).seed)
    assert (forward.replay_metadata()["participants"]
            == backward.replay_metadata()["participants"])


def test_a4_presentation_cannot_move_authority():
    a, b = bout(), bout()
    baseline = [b.stream("policy_intent", RED).below(1000) for _ in range(3)]
    for _ in range(500):                                 # a very busy crowd
        a.stream("presentation").below(1000)
    after = [a.stream("policy_intent", RED).below(1000) for _ in range(3)]
    assert after == baseline
    assert a.stream("presentation").authoritative is False


def test_a5_one_judge_cannot_move_another():
    a = bout()
    b = bout()
    baseline = [b.stream("judging_officiating", "judge_2").below(1000)
                for _ in range(3)]
    for _ in range(9):
        a.stream("judging_officiating", "judge_1").below(1000)
    after = [a.stream("judging_officiating", "judge_2").below(1000)
             for _ in range(3)]
    assert after == baseline


def test_a6_no_caller_can_obtain_an_unowned_cursor():
    r = bout()
    for domain in R.FIGHTER_LOCAL:
        with pytest.raises(R.UnscopedDraw):
            r.stream(domain)
    for missing in ("next", "random", "draw", "default"):
        assert not hasattr(r, missing)


def test_a_unknown_participant_is_refused():
    with pytest.raises(R.UnknownSubstream):
        bout().stream("policy_intent", "green_corner")


def test_a_scoped_names_cannot_alias():
    """Two different owners are two different streams, and the ambiguity that
    could make them one is refused at the door rather than hashed away.

    A separator inside an owner would let ("presentation", "a/b") and a
    hypothetical ("presentation/a", "b") spell one name. `scoped` refuses it,
    so the aliasing case cannot be constructed - which is why this asserts the
    refusal and the distinctness rather than hashing two colliding spellings.
    """
    seeds = {R.derive_seed(1, R.scoped("presentation", who), "v")
             for who in ("ab", "a", "b", "crowd")}
    assert len(seeds) == 4
    assert R.split_scope("presentation/crowd") == ("presentation", "crowd")
    assert R.split_scope("presentation") == ("presentation", None)


def test_a_an_owner_containing_the_separator_is_refused():
    with pytest.raises(ValueError):
        R.scoped("presentation", "crowd/left")


def test_a_participants_are_declared_in_the_contract_initial_state():
    state = C.InitialState(4242)
    assert state.participants == C.DEFAULT_PARTICIPANTS
    assert "H|participants=blue_corner,red_corner" in state.header_lines()
    with pytest.raises(ValueError):
        C.InitialState(4242, participants=(RED, RED))
    with pytest.raises(ValueError):
        C.InitialState(4242, participants=(RED,))
    with pytest.raises(ValueError):
        C.InitialState(4242, participants=(RED, "blue|corner"))


def test_a_the_policy_refuses_the_unscoped_cursor(econ):
    """Even if one were somehow produced, the policy will not consume it."""
    fake = R.Substream("policy_intent", 1)
    with pytest.raises(P.PolicyError):
        P._tie_break(("jab_lead", "cross_rear"), fake)
    with pytest.raises(P.PolicyError):
        P._tie_break(("jab_lead",), R.Substream("contact_condition", 1))
    assert P._tie_break(("jab_lead", "cross_rear"),
                        bout().stream("policy_intent", RED)) is not None
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 10:40 UTC | END ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 10:50 UTC | START ]
# =========================================== Ruling B: recovery makes space ==

def tired(**kw):
    base = dict(wind_is_low=True, range_band="inside", preferred_band="inside",
                opponent_band="inside")
    base.update(kw)
    base.update(_legality(base["range_band"]))
    base.update(kw)
    return P.Observation(**base)


def test_b_unsafe_and_close_seeks_space():
    d = P.decide(tired())
    assert (d.strategic, d.tactical, d.reason) == (
        P.RECOVER, P.RETREAT, P.R_SEEK_RECOVERY_SPACE)


def test_b_safe_and_far_rests():
    # [ Claude Fable 5 (claude-fable-5) | 2026-08-09 09:20 UTC | resolution:
    #   he stands at outside; preferring it is now a refused plan. The
    #   ruling's claim - safe and far means Rest - is unchanged. ]
    d = P.decide(tired(range_band="outside"))
    assert (d.tactical, d.reason) == (P.REST, P.R_REST_WHEN_SAFE)


def test_b_an_advancing_opponent_denies_recovery():
    """The pressure fighter's reward, and it is not a stamina-drain ability.
    He makes exhaustion harder to escape by walking his man down."""
    d = P.decide(tired(opponent_advancing=True))
    assert (d.strategic, d.tactical, d.reason) == (
        P.RECOVER, P.GUARD, P.R_RECOVERY_DENIED)


def test_b_a_punch_interrupts_recovery_and_says_so():
    d = P.decide(tired(incoming_attack=True))
    assert d.reason == P.R_RECOVERY_INTERRUPTED
    d = P.decide(tired(opponent_recovering=True))
    assert d.reason == P.R_RECOVERY_INTERRUPTED
    assert d.tactical == P.ATTACK


def test_b_escape_outranks_resting():
    """Ruling B: "on ropes or in a corner, escape has priority over resting"."""
    assert P.decide(tired(on_ropes=True)).reason == P.R_ESCAPE_ROPES
    assert P.decide(tired(cornered=True)).reason == P.R_ESCAPE_ROPES


def test_b_hold_position_is_not_the_only_answer_to_needing_air():
    """The sentence in the ruling, as a test. Across every close band and both
    threat states, the answer is never merely to stand there."""
    for band in ("clinch", "inside", "mid"):
        for advancing in (False, True):
            # [ Claude Fable 5 (claude-fable-5) | 2026-08-09 09:20 UTC |
            #   resolution: preferred_band stays the helper's default -
            #   preferring clinch is now a refused plan. ]
            d = P.decide(tired(range_band=band,
                               opponent_advancing=advancing))
            assert d.tactical != P.HOLD_POSITION, (band, advancing)


def test_b_recovery_intent_persists_between_the_two_thresholds(econ):
    """Hysteresis. Above the entry line but below the exit line, a fighter who
    was recovering is still recovering - which is the difference between a
    boxer catching his breath and a light switch."""
    f = F.FighterState(RED, econ)
    f.wind = econ["wind_low"] - 1
    assert f.update_recovery_intent(econ) is True
    f.wind = (econ["wind_low"] + econ["wind_recovered"]) // 2
    assert f.update_recovery_intent(econ) is True          # still seeking
    f.wind = econ["wind_recovered"]
    assert f.update_recovery_intent(econ) is False         # and now done


def test_b_the_thresholds_are_two_different_numbers(econ):
    assert econ["wind_recovered"] > econ["wind_low"]


def test_b_a_single_threshold_would_be_refused(econ):
    """Collapse the exit onto the entry and the economy must reject its own
    canon rather than run with a policy that oscillates every tick."""
    import copy
    import tools.uppercut_stamina.economy as EE
    doc = copy.deepcopy(EE._read(EE.ECONOMY))
    doc["wind"]["recovery_exit_fraction"] = doc["wind"]["low_threshold_fraction"]
    real_read = EE._read

    def fake(rel):
        return doc if rel == EE.ECONOMY else real_read(rel)

    EE._read = fake
    try:
        errs = EE.economy_pack()["errors"]
    finally:
        EE._read = real_read
    assert any("hysteresis" in e for e in errs), errs


def test_b_a_recovering_fighter_still_seeks_space_above_the_low_line(econ):
    """The state carries the intent, and the policy honours it: no longer
    'low', not yet 'recovered', still going for room."""
    obs = P.Observation(wind_is_low=False, recovery_seeking=True,
                        wind_is_recovered=False, range_band="inside",
                        preferred_band="inside", **_legality("inside"))
    assert P.decide(obs).reason == P.R_SEEK_RECOVERY_SPACE
    obs = P.Observation(wind_is_low=False, recovery_seeking=True,
                        wind_is_recovered=True, range_band="inside",
                        preferred_band="inside", **_legality("inside"))
    assert P.decide(obs).reason != P.R_SEEK_RECOVERY_SPACE


def test_b_every_new_reason_is_declared():
    for r in (P.R_SEEK_RECOVERY_SPACE, P.R_REST_WHEN_SAFE,
              P.R_RECOVERY_DENIED, P.R_RECOVERY_INTERRUPTED):
        assert r in P.REASONS
    assert len(set(P.REASONS)) == len(P.REASONS)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 10:50 UTC | END ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 11:00 UTC | START ]
# ================================================ Ruling D: units and basis ==
import io
import json
import os

from tools.engine import probe_policy_stamina as PROBE


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 03:15 UTC | START edit: legality reaches the unit tests ]
# `Observation` requires offence legality, and these tests build Observations
# by hand. The defaults come from the SAME authority the bout reads - canon,
# through `uppercut_range.core` - so a test never asserts against a legality
# table written in a test file. `mid` is the band `Observation` itself
# defaults to, so these two lines say "the fighter is where the default says
# he is, and canon says this is what he may throw from there".
from tools.uppercut_range import core as _RANGE          # noqa: E402
from tools.uppercut_integrated import contract as _CONTRACT  # noqa: E402

_RANGE_PACK = _RANGE.range_pack()
_BANDS = P.Bands(_RANGE.band_order(_RANGE_PACK),
                 _RANGE.bands_without_offence(_RANGE_PACK, _CONTRACT.PUNCHES))


def _legality(band="mid"):
    return {"throwable_here": _RANGE.throwable_from(_RANGE_PACK, band,
                                                    _CONTRACT.PUNCHES),
            "bands": _BANDS}
# [ ... | 2026-08-09 03:15 UTC | END edit ]


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def canon(rel):
    return json.load(io.open(os.path.join(REPO, *rel.split("/")),
                             encoding="utf-8"))


def test_d1_a_movement_action_cannot_debit_a_stride_once_per_tick(econ):
    """The 2026-08-08 defect, as a regression.

    Charging `stride_length_ru` per tick empties a full pool in about four
    seconds. The test states the consequence rather than the line of code,
    because the line of code will move and the consequence will not.
    """
    loco = canon("data/movement_model.json")["locomotion"]
    stride = int(round(loco["modes"][0]["stride_length_ru"] * 10000))
    f = F.FighterState(RED, econ)
    for _ in range(240):                     # four seconds at 60 Hz
        f.step(econ, "move", move_id="step_out", displacement_ru=stride)

    g = F.FighterState(RED, econ)
    per_tick = PROBE.displacement_per_tick_ru(REPO)
    for _ in range(240):
        g.step(econ, "move", move_id="step_out", displacement_ru=per_tick)

    assert f.wind < econ["wind_low"], (
        "billing a per-step stride every tick no longer puts a fighter under "
        "the low-Wind line inside four seconds of walking, so this test has "
        "stopped discriminating and needs rewriting rather than deleting")
    assert g.wind > econ["wind_low"], (
        "the per-tick reader is billing a per-step distance: four seconds of "
        "footwork should not cross the low-Wind line")
    assert g.wind > f.wind * 3


def test_d2_displacement_never_exceeds_the_declared_cap():
    loco = canon("data/movement_model.json")["locomotion"]
    cap = int(round(loco["max_frame_displacement_ru"] * 10000))
    assert PROBE.displacement_per_tick_ru(REPO) <= cap


def test_d3_the_debit_comes_from_the_displacement_of_the_same_tick(econ):
    """Halve the ground covered and the bill halves. A debit computed from
    anything other than this tick's displacement would not track."""
    costs = []
    for ru in (2000, 1000, 500):
        f = F.FighterState(RED, econ)
        before = f.wind
        f.step(econ, "move", move_id="step_out", displacement_ru=ru)
        costs.append(before - f.wind)
    assert costs[0] == 2 * costs[1] == 4 * costs[2]


def test_d4_zero_displacement_receives_no_travel_debit(econ):
    """Standing still is free. A fighter paying a fee not to move is a fighter
    the economy is inventing work for."""
    f = F.FighterState(RED, econ)
    before = f.wind
    f.step(econ, "move", move_id="step_out", displacement_ru=0)
    assert f.wind == before


def test_d5_the_max_displacement_probe_labels_itself_stress_only(tmp_path):
    out = tmp_path / "probe.json"
    PROBE.main(["--ticks", "120", "--out", str(out)])
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["stress_only"] is True
    assert report["excluded_from_fit_evidence"] is True
    assert "may not be cited" in report["stress_note"].lower()
    assert report["values_are_fitted"] is False


def test_d_a_per_action_cost_is_not_charged_per_tick(econ):
    """A guard held for a second must not pay for a guard sixty times.

    Found by the Wind ledger four hours after the ledger was written: a `guard`
    family quietly bleeding 0.012 Wind a tick, which is a per-action price
    being charged on a per-tick basis - the same class of error as the stride,
    one layer up.
    """
    f = F.FighterState(RED, econ)
    before = f.wind
    f.step(econ, "guard", move_id="guard_high")          # entered
    entry_cost = before - f.wind
    held = f.wind
    for _ in range(60):
        f.step(econ, "guard", move_id=None)              # held
    assert entry_cost > 0
    assert f.wind == held, "holding a guard is being charged as re-entering it"


def test_d_every_declared_source_basis_is_one_of_the_allowed_units():
    basis = canon("data/stamina_economy.json")["source_basis"]
    allowed = set(basis["allowed"])
    assert allowed
    for key, unit in basis["sources"].items():
        assert unit in allowed, (key, unit)


def test_d_the_step_length_is_declared_not_to_be_a_stamina_source():
    basis = canon("data/stamina_economy.json")["source_basis"]
    text = basis["not_a_stamina_source"][
        "movement_model.locomotion.modes[].stride_length_ru"]
    assert "not per-tick" in text.lower()
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 11:00 UTC | END ]
