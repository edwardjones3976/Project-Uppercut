# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:20 UTC | START ]
"""Wind and Reserve inside the integrated fighter, and the branch that lets a
tired fighter go and get his breath back.

Every test here was written to fail against the code as it stood before this
change, and each one was run against that code and observed to fail. A test
that passes the moment it is written has proved nothing about the change it
accompanies.
"""
import pytest

from tools.uppercut_stamina import economy as E
from tools.uppercut_integrated import fighter as F
from tools.uppercut_integrated import contract as C
from tools.uppercut_integrated import policy as P


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


RED, BLUE = C.DEFAULT_PARTICIPANTS


@pytest.fixture(scope="module")
def econ():
    c = E.economy_pack()
    assert not c["errors"], c["errors"]
    return c


def low_wind_obs(**kw):
    """A fighter short of breath, with a man in front of him who is not
    coming forward. Branch 7's exact situation."""
    base = dict(wind_fraction=2000, wind_is_low=True, range_band="inside",
                preferred_band="inside", opponent_band="inside",
                opponent_advancing=False)
    base.update(kw)
    base.update(_legality(base["range_band"]))
    base.update(kw)
    return P.Observation(**base)


# ------------------------------------------------------- the missing branch --

def test_low_wind_at_close_range_makes_room_instead_of_standing_there():
    """The whole of F2. He cannot rest here, so he goes where he can."""
    d = P.decide(low_wind_obs(range_band="inside"))
    assert d.tactical == P.RETREAT
    assert d.reason == P.R_MAKE_ROOM_TO_BREATHE
    assert d.strategic == P.RECOVER


def test_making_room_is_reached_from_every_band_that_denies_rest():
    # [ Claude Fable 5 (claude-fable-5) | 2026-08-09 09:20 UTC | resolution:
    #   preferring clinch is now refused (canon authors no punch there). The
    #   claim is about the band he is IN, so the preference stays the
    #   helper's default and only range_band varies. ]
    for band in ("clinch", "inside", "mid"):
        d = P.decide(low_wind_obs(range_band=band))
        assert d.reason == P.R_MAKE_ROOM_TO_BREATHE, band
        assert d.tactical == P.RETREAT, band


def test_with_room_already_he_actually_rests():
    """The branch must not have turned every recovery into footwork."""
    # [ Claude Fable 5 (claude-fable-5) | 2026-08-09 09:20 UTC | resolution:
    #   same as above - he stands far away; he does not have to PREFER far
    #   away, and preferring a punchless band is now a refused plan. ]
    for band in ("outside", "out_of_range"):
        d = P.decide(low_wind_obs(range_band=band))
        assert d.tactical == P.REST, band
        assert d.reason == P.R_REST_WHEN_SAFE, band


def test_he_does_not_turn_his_back_on_a_man_coming_forward():
    """Branch 7 is guarded on `not opponent_advancing` and must stay guarded.

    Retreating from an advancing opponent while short of breath is how a
    fighter gets walked onto the ropes, and the guard is the only thing
    stopping this branch from teaching that.
    """
    d = P.decide(low_wind_obs(range_band="inside", opponent_advancing=True))
    assert d.reason != P.R_MAKE_ROOM_TO_BREATHE
    assert d.tactical != P.RETREAT


def test_empty_outranks_making_room():
    """Branch 4 comes first: a fighter with nothing left rests where he
    stands, because moving costs what he does not have."""
    d = P.decide(low_wind_obs(range_band="inside", wind_is_exhausted=True))
    assert d.tactical == P.REST
    assert d.reason == P.R_RECOVER_WIND


def test_the_ropes_outrank_making_room():
    """Branch 3 comes first. 'Step out' into the ropes is not room."""
    d = P.decide(low_wind_obs(range_band="inside", on_ropes=True))
    assert d.reason == P.R_ESCAPE_ROPES


def test_an_open_punish_window_outranks_making_room():
    """Branch 6 comes first: a tired fighter still takes a free shot at a man
    who is recovering. Wanting air does not mean declining the opening."""
    d = P.decide(low_wind_obs(range_band="inside", opponent_recovering=True))
    assert d.tactical == P.ATTACK
    # Decision 0026: the log says the recovery was interrupted, which is
    # strictly more information than 'he punished a recovery'.
    assert d.reason == P.R_RECOVERY_INTERRUPTED


def test_the_new_reason_is_declared_and_accepted():
    assert P.R_MAKE_ROOM_TO_BREATHE in P.REASONS
    P.Decision(P.RECOVER, P.RETREAT, "step_out", P.R_MAKE_ROOM_TO_BREATHE, 0)


def test_every_declared_reason_is_unique():
    assert len(set(P.REASONS)) == len(P.REASONS)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:20 UTC | END ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:25 UTC | START ]
# ------------------------------------------------- the state, and its seams --

def test_the_fighter_owns_no_economy_rules(econ):
    """A step through FighterState must equal a step through the economy.

    This is the runtime convergence rule applied to a resource. If these two
    ever disagree it is because someone reimplemented a rule here, and the
    disagreement is the only warning that would arrive.
    """
    f = F.FighterState(RED, econ)
    direct = E.step(econ, econ["wind_start"], econ["reserve_start"],
                    "attack", move_id="cross_rear")
    assert f.step(econ, "attack", move_id="cross_rear") == direct


def test_the_corner_is_delegated_too(econ):
    f = F.FighterState(RED, econ)
    for _ in range(400):
        f.step(econ, "attack", move_id="jab_lead")
    w, r = f.wind, f.reserve
    assert f.between_rounds(econ) == E.between_rounds(econ, w, r)


def test_displacement_is_charged_for_the_ground_covered(econ):
    f = F.FighterState(RED, econ)
    before = f.wind
    f.step(econ, "move", move_id="step_out", displacement_ru=1400)
    assert f.wind < before


def test_an_unknown_move_still_fails_closed(econ):
    """The fail-closed rule must survive the extra layer. A wrapper that
    swallowed UnknownMove would restore the silent zero that once made every
    punch in a 120-punch round free."""
    f = F.FighterState(RED, econ)
    with pytest.raises(E.UnknownMove):
        f.step(econ, "attack", move_id="superman_punch")


def test_reserve_outside_its_interval_is_refused(econ):
    """Decision 0025 reaches constructed state, not only stepped state."""
    f = F.FighterState(RED, econ)
    f.reserve = -1
    with pytest.raises(E.InvalidState):
        f.step(econ, "observe")


# --------------------------------------------------- what an opponent sees --

def test_an_opponent_is_seen_through_a_declared_list(econ):
    seen = F.FighterState(BLUE, econ).observable()
    assert set(F.Observable.__slots__) == {
        "band", "committed", "recovering", "advancing", "recent_moves",
        "on_ropes"}
    for hidden in ("wind", "reserve", "profile", "damaged_regions", "hurt",
                   "failed_attacks", "punches_thrown"):
        assert not hasattr(seen, hidden), hidden


def test_the_observation_cannot_be_built_from_raw_opponent_state(econ):
    """Narrowing is the mechanism. Handing the whole fighter over would make
    the leak a matter of who remembers, which is the thing the Director asked
    to be made awkward or impossible."""
    me = F.FighterState(RED, econ)
    with pytest.raises(TypeError):
        me.observation(econ, {"band": "mid"})


def test_the_observation_carries_own_wind_and_never_the_opponents(econ):
    me, foe = F.FighterState(RED, econ), F.FighterState(BLUE, econ)
    for _ in range(600):
        foe.step(econ, "attack", move_id="cross_rear")
    assert foe.wind < me.wind
    obs = me.observation(econ, foe, **_legality("mid"))
    assert obs.wind_fraction == 10000
    assert not hasattr(obs, "opponent_wind")
    assert not hasattr(obs, "opponent_wind_fraction")


def test_the_thresholds_sit_exactly_where_canon_puts_them(econ):
    me, foe = F.FighterState(RED, econ), F.FighterState(BLUE, econ)
    me.wind = econ["wind_low"]
    assert me.observation(econ, foe, **_legality("mid")).wind_is_low is False
    me.wind = econ["wind_low"] - 1
    assert me.observation(econ, foe, **_legality("mid")).wind_is_low is True
    me.wind = econ["wind_exhausted"] - 1
    assert me.observation(econ, foe,
                          **_legality("mid")).wind_is_exhausted is True


def test_the_thresholds_are_read_and_not_remembered(econ):
    """The test above would pass against a hardcoded 250000, because that is
    what canon says today. It was written, run under mutation, and found to be
    decorative - so it is kept for the boundary and this one carries the claim.

    Moving the threshold in a copy of the pack must move the answer. A reader
    that had memorised the number would sail through the test above and fail
    here, which is the only difference that matters.
    """
    moved = dict(econ)
    moved["wind_low"] = econ["wind_max"] // 2
    moved["wind_exhausted"] = econ["wind_max"] // 4
    me, foe = F.FighterState(RED, moved), F.FighterState(BLUE, moved)
    me.wind = econ["wind_max"] * 3 // 8          # below the moved low line,
    obs = me.observation(moved, foe,             # far above canon's
                         **_legality("mid"))
    assert obs.wind_is_low is True
    assert obs.wind_is_exhausted is False
    me.wind = econ["wind_max"] // 8
    assert me.observation(moved, foe,
                          **_legality("mid")).wind_is_exhausted is True


def test_a_thrown_punch_is_visible_and_a_recovery_window_opens(econ):
    f = F.FighterState(RED, econ)
    f.committed_to("jab_lead", 14)
    assert f.observable().recovering is True
    assert f.observable().recent_moves == ("jab_lead",)
    for _ in range(14):
        f.tick_recovery()
    assert f.observable().recovering is False
    assert f.observable().committed is False


def test_the_decision_the_state_produces_is_the_one_boxing_expects(econ):
    """End to end through the seam this file exists to close: real economy,
    real state, real observation, real policy."""
    me = F.FighterState(RED, econ, P.Profile(5000, "inside"), band="inside")
    foe = F.FighterState(BLUE, econ, P.Profile(5000, "inside"), band="inside")
    me.wind = econ["wind_low"] - 1
    d = P.decide(me.observation(econ, foe, **_legality("inside")))
    assert d.reason == P.R_MAKE_ROOM_TO_BREATHE
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:25 UTC | END ]
