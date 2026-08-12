# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:26 UTC | START ]
"""The authored pair actually reaches the reference simulator.

A card that validates but never arrives in a fight is a document, not a
fighter. These tests assert the whole path: fixture on disk -> `cards=` ->
`Fighter.attrs` -> the multiplier `_attr` hands to a call site.

The last link is the one that matters and the one a naive test skips. Two
fighters can hold different `attrs` dicts and still fight identically if the
attributes they differ on scale nothing, so the assertions below are written
against MULTIPLIERS the engine will actually apply, not against the numbers on
the card.
"""
import pytest

from tools.uppercut_sim.engine import Bout
from tools.uppercut_validate import pairing as P

# Mechanic names as data/attribute_effects.json spells them, paired with the
# side expected to come out ahead. Each row is a sentence about the matchup that
# a coach would recognise, made checkable.
MECHANICS = [
    ("delivered_impact", "A"),              # A punches harder
    ("knockdown_pressure_threshold", "A"),  # A is harder to drop (chin)
    ("range_band_offset", "B"),             # B fights from further out
    ("evasion_chance", "B"),                # B actually evades
    ("counter_window_exploitation", "B"),   # B punishes commitment
    ("body_shot_force", "A"),               # A invests downstairs
    ("alignment", "B"),                     # B is the accurate one
    ("punch_startup", "B"),                 # lower is faster - B's hands
]


def bout_with_pair(**kw):
    opts = dict(seed=4242, profile_a="rusher", profile_b="technician",
                rounds=1, round_seconds=60, cards=P.MATCH_PAIR)
    opts.update(kw)
    return Bout(**opts)


def test_cards_load_by_id_and_are_recorded_on_the_fighter():
    b = bout_with_pair()
    assert [f.card_id for f in b.fighters] == list(P.MATCH_PAIR)


def test_the_card_replaces_the_stress_profile_loadout():
    """A card and a profile must not both contribute. Profile 'rusher' carries
    stamina_pool +35 and defensive_technique -25; the card must be the only
    voice once it is supplied."""
    b = bout_with_pair()
    card = P.load_card("generic_pressure_a")
    assert b.fighters[0].attrs == card["attributes"]


def test_no_card_still_means_the_stress_profile_loadout():
    """The default path is untouched - which is what keeps every pinned
    measurement taken before this seam existed still true."""
    from tools.uppercut_sim import policy as _policy
    b = Bout(seed=4242, profile_a="rusher", profile_b="technician",
             rounds=1, round_seconds=60)
    assert b.fighters[0].attrs == _policy.attributes_for("rusher")
    assert b.fighters[0].card_id == ""


@pytest.mark.parametrize("mechanic,favoured", MECHANICS)
def test_the_pair_differs_where_the_engine_will_read_it(mechanic, favoured):
    """The multipliers, not the card values. This is the assertion that would
    catch a pair differing only on attributes that scale nothing."""
    b = bout_with_pair()
    a_mul = b._attr(b.fighters[0], mechanic)
    b_mul = b._attr(b.fighters[1], mechanic)
    assert a_mul != b_mul, "%s is identical for both fighters" % mechanic

    # punch_startup is the one mechanic where lower is better (higher hand
    # speed shortens the telegraph), so the comparison inverts.
    ahead = (a_mul < b_mul) if mechanic == "punch_startup" else (a_mul > b_mul)
    expected_a = favoured == "A"
    assert ahead == expected_a, (
        "%s favours the wrong fighter: A=%.4f B=%.4f" % (mechanic, a_mul, b_mul))


def test_two_baseline_fighters_would_be_indistinguishable():
    """The state this work was undoing, asserted rather than remembered: with
    no cards and the same profile, every mechanic multiplier matches - which is
    what 'the live C++ fighters are identical empty cards' meant in practice."""
    b = Bout(seed=4242, profile_a="rusher", profile_b="rusher",
             rounds=1, round_seconds=60)
    for mechanic, _ in MECHANICS:
        assert b._attr(b.fighters[0], mechanic) == b._attr(b.fighters[1], mechanic)


def test_a_card_without_attributes_is_refused_loudly():
    with pytest.raises(ValueError, match="attributes"):
        Bout(seed=1, profile_a="rusher", profile_b="technician", rounds=1,
             round_seconds=60, cards=({"id": "hollow"}, "generic_range_b"))


def test_cards_argument_demands_exactly_two():
    with pytest.raises(ValueError, match="exactly two"):
        Bout(seed=1, profile_a="rusher", profile_b="technician", rounds=1,
             round_seconds=60, cards=("generic_pressure_a",))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:26 UTC | END ]
