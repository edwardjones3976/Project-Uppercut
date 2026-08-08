# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 06:30 UTC | START ]
"""Decision 0022's RNG partitioning, made enforceable.

The ruling's central promise is negative: "adding a cosmetic draw or changing
policy cadence may not silently move knockdown, judging, or contact outcomes."
Negative promises are the ones that rot quietly, because nothing fails when they
break - the fight just becomes a different fight, and every existing test still
passes because every existing test regenerates from the same changed thing.

So these are adversarial. Each one tries to move a subsystem's outcomes from
outside it.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.uppercut_integrated import rng as R  # noqa: E402

CONTRACT = "uppercut-integrated-v1"


def bout(seed=4242):
    return R.BoutRng(seed, CONTRACT)


# --- the isolation promise ---------------------------------------------------

def test_a_cosmetic_draw_cannot_move_a_knockdown():
    """THE rule. Presentation randomness is isolated from authority."""
    quiet = bout()
    loud = bout()
    for _ in range(10000):
        loud.stream("presentation").next_u32()

    a = [quiet.stream("knockdown_recovery").next_u32() for _ in range(50)]
    b = [loud.stream("knockdown_recovery").next_u32() for _ in range(50)]
    assert a == b, (
        "ten thousand cosmetic draws moved the knockdown stream. This is the "
        "exact failure Decision 0022's partitioning exists to make impossible")


@pytest.mark.parametrize("noisy", R.SUBSTREAMS)
@pytest.mark.parametrize("watched", ["knockdown_recovery", "judging_officiating",
                                     "contact_condition"])
def test_no_substream_can_move_any_other(noisy, watched):
    """Not just presentation. Policy cadence must not move judging either."""
    if noisy == watched:
        return
    quiet, loud = bout(), bout()
    for _ in range(500):
        loud.stream(noisy).next_u32()
    a = [quiet.stream(watched).next_u32() for _ in range(30)]
    b = [loud.stream(watched).next_u32() for _ in range(30)]
    assert a == b, "%s draws moved %s" % (noisy, watched)


def test_every_substream_starts_somewhere_different():
    """Independence is worthless if two streams are the same stream."""
    seeds = {n: R.derive_seed(4242, n, CONTRACT) for n in R.SUBSTREAMS}
    assert len(set(seeds.values())) == len(seeds), (
        "two substreams derived the same seed and would produce identical "
        "sequences: %s" % seeds)


def test_substreams_do_not_run_in_lockstep():
    """Distinct seeds are necessary, not sufficient - check the sequences."""
    b = bout()
    seqs = {n: [b.stream(n).next_u32() for _ in range(20)] for n in R.SUBSTREAMS}
    as_tuples = {n: tuple(v) for n, v in seqs.items()}
    assert len(set(as_tuples.values())) == len(as_tuples)


# --- determinism and versioning ----------------------------------------------

def test_the_same_seed_reproduces_the_same_bout():
    a, b = bout(777), bout(777)
    for n in R.SUBSTREAMS:
        assert [a.stream(n).next_u32() for _ in range(40)] == \
               [b.stream(n).next_u32() for _ in range(40)]


def test_different_seeds_are_non_vacuously_different():
    """Decision 0022 assertion 2, at the randomness layer."""
    a, b = bout(4242), bout(4243)
    for n in R.SUBSTREAMS:
        assert [a.stream(n).next_u32() for _ in range(40)] != \
               [b.stream(n).next_u32() for _ in range(40)]


def test_the_derivation_version_is_part_of_the_identity():
    """Changing how streams are derived must change what they are."""
    before = R.derive_seed(4242, "policy_intent", CONTRACT)
    original = R.DERIVATION_VERSION
    try:
        R.DERIVATION_VERSION = original + "-experiment"
        after = R.derive_seed(4242, "policy_intent", CONTRACT)
    finally:
        R.DERIVATION_VERSION = original
    assert before != after, (
        "the derivation version does not reach the seed, so the derivation "
        "could change without the contract noticing")


def test_the_contract_version_is_part_of_the_identity():
    a = R.derive_seed(4242, "policy_intent", "uppercut-integrated-v1")
    b = R.derive_seed(4242, "policy_intent", "uppercut-integrated-v2")
    assert a != b


# --- ownership is by name, never by position ---------------------------------

def test_iteration_order_cannot_determine_random_ownership():
    """Decision 0022, verbatim: iteration order may not decide ownership.

    Derivation takes the NAME, so shuffling the declaration order cannot move
    a subsystem onto another's numbers. An index-based scheme would fail this.
    """
    straight = {n: R.derive_seed(4242, n, CONTRACT) for n in R.SUBSTREAMS}
    reversed_order = {n: R.derive_seed(4242, n, CONTRACT)
                      for n in reversed(R.SUBSTREAMS)}
    assert straight == reversed_order

    original = R.SUBSTREAMS
    try:
        R.SUBSTREAMS = tuple(reversed(original))
        shuffled = {n: R.derive_seed(4242, n, CONTRACT) for n in R.SUBSTREAMS}
    finally:
        R.SUBSTREAMS = original
    assert shuffled == straight, (
        "a substream's seed changed when the declaration order changed - "
        "ownership is positional, which Decision 0022 forbids")


def test_names_that_concatenate_alike_do_not_collide():
    """The aliasing bug the canon pointers were bitten by, pre-empted here.

    Without length prefixes, ("ab","c") and ("a","bc") hash identically. Two
    subsystems sharing a generator by accident is the worst version of that.
    """
    a = R._field("ab") + R._field("c")
    b = R._field("a") + R._field("bc")
    assert a != b


# --- fail closed --------------------------------------------------------------

def test_an_undeclared_substream_is_refused():
    with pytest.raises(R.UnknownSubstream):
        bout().stream("crowd_sparkles")
    with pytest.raises(R.UnknownSubstream):
        R.derive_seed(4242, "crowd_sparkles", CONTRACT)


def test_there_is_no_way_to_draw_without_naming_an_owner():
    """The shared-cursor habit cannot come back one convenience method at a time."""
    b = bout()
    for forbidden in ("next_u32", "below", "random", "draw", "next"):
        assert not hasattr(b, forbidden), (
            "BoutRng grew a %r that draws without naming a subsystem" % forbidden)


def test_a_bad_bout_seed_is_refused():
    for bad in (-1, "4242", None, 3.5):
        with pytest.raises((ValueError, TypeError)):
            R.derive_seed(bad, "policy_intent", CONTRACT)


def test_a_boolean_is_not_a_bout_seed():
    """Python's bool is an int subclass; True would otherwise seed bout 1.

    The canonicalizer's tests already carry this exact lesson. A bout seeded
    True is a bout nobody meant to run, and it would reproduce perfectly -
    which is what makes it dangerous rather than obvious.
    """
    for bad in (True, False):
        with pytest.raises(ValueError):
            R.derive_seed(bad, "policy_intent", CONTRACT)


# --- what replay has to carry -------------------------------------------------

def test_replay_metadata_records_the_derivation():
    meta = bout(4242).replay_metadata()
    assert meta["derivation_version"] == R.DERIVATION_VERSION
    assert meta["contract_version"] == CONTRACT
    assert meta["bout_seed"] == 4242
    names = [s["name"] for s in meta["substreams"]]
    assert names == sorted(R.SUBSTREAMS), "replay metadata is not name-ordered"
    assert len(names) == len(R.SUBSTREAMS)


def test_replay_metadata_marks_which_streams_hold_authority():
    meta = bout().replay_metadata()
    auth = {s["name"]: s["authoritative"] for s in meta["substreams"]}
    assert auth["presentation"] is False
    for n in R.AUTHORITATIVE:
        assert auth[n] is True


def test_replay_metadata_is_enough_to_rebuild_the_bout():
    """A recording that cannot reproduce the draws is not a recording."""
    original = bout(999)
    meta = original.replay_metadata()
    rebuilt = R.BoutRng(meta["bout_seed"], meta["contract_version"])
    for s in meta["substreams"]:
        assert rebuilt.stream(s["name"]).seed == s["seed"]
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 06:30 UTC | END ]
