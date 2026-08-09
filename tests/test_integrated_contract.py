# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:00 UTC | START ]
"""The integrated contract's identity and header. Decision 0022.

These cover the parts of the ruling's seven required assertions that exist at
the header layer today. The rest become tests as their subsystems land, and the
ones NOT yet coverable are named at the bottom of this file rather than left to
be assumed - a checklist that quietly loses items is worse than no checklist.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.uppercut_integrated import contract as C  # noqa: E402
from tools.uppercut_integrated import rng as R       # noqa: E402


# --- assertion 1: same seed and initial state reproduce byte-identically ------

def test_the_same_seed_and_state_build_an_identical_header():
    a = C.new_bout(ROOT, 4242)[2]
    b = C.new_bout(ROOT, 4242)[2]
    assert a == b


def test_the_header_order_is_fixed_not_incidental():
    """Two callers emitting the same facts in different orders would produce
    artifacts that are equally true and not byte-identical. Byte-identity is
    the entire currency, so the order is the contract's, not the caller's."""
    lines = C.new_bout(ROOT, 4242)[2]
    assert lines[0] == "H|phase=INTEGRATED"
    assert lines[1] == "H|contract=%s" % C.CONTRACT
    # [ Claude Fable 5 (claude-fable-5) | 2026-08-09 10:58 UTC | resolution:
    #   Decision 0033 Ruling 2 - the ruleset fought under is part of the
    #   fight's identity, named right after the contract that carries it. ]
    assert lines[2] == "H|ruleset=%s" % C.DEFAULT_RULESET
    assert lines[3].startswith("H|canon_hash_contract=")
    seed_at = lines.index("H|seed=4242")
    rng_at = [i for i, l in enumerate(lines)
              if l.startswith("H|rng_derivation=")][0]
    canon_at = [i for i, l in enumerate(lines)
                if l.startswith("H|canon_movement_semantic=")][0]
    assert canon_at < seed_at < rng_at, (
        "canon, then initial state, then randomness - if this order drifts, "
        "every integrated artifact changes for no reason anyone intended")


# --- assertion 2: different seeds create non-vacuous variation ----------------

def test_a_different_seed_changes_the_bout():
    a = C.new_bout(ROOT, 4242)[2]
    b = C.new_bout(ROOT, 4243)[2]
    assert a != b
    # and specifically in the randomness, not merely the recorded seed line
    rng_a = [l for l in a if l.startswith("H|rng_") and "derivation" not in l]
    rng_b = [l for l in b if l.startswith("H|rng_") and "derivation" not in l]
    assert rng_a != rng_b, (
        "the seed line changed but every substream started in the same place - "
        "the bout would be identical and only claim not to be")


# --- assertion 4 (partial): authority is visible in the artifact --------------

def test_the_stream_says_which_randomness_holds_authority():
    lines = C.new_bout(ROOT, 4242)[2]
    declared = [l for l in lines if l.startswith("H|rng_authoritative=")]
    assert len(declared) == 1
    names = declared[0].split("=", 1)[1].split(",")
    # Decision 0026: the fighter-local domains appear once per
    # participant, so the header lists the SCOPED names. Every
    # declared authoritative domain must still be represented.
    assert names == sorted(names)
    for domain in R.AUTHORITATIVE:
        assert any(n == domain or n.startswith(domain + '/')
                   for n in names), domain
    assert all(R.is_authoritative(n) for n in names)
    assert "presentation" not in names, (
        "presentation randomness is declared authoritative - Decision 0022 "
        "requires it isolated from authority")


def test_no_header_row_hides_a_pipe_inside_its_value():
    """Every other header row has exactly two '|' fields; these must too.

    An earlier draft emitted "H|rng_x=<seed>|authoritative", which survives the
    split("=", 1) the analyzers use but gives that row three fields. Nothing
    consumed the integrated stream yet, so it broke nothing - and that is
    precisely why it was worth fixing while the format was still ours alone.
    """
    for l in C.new_bout(ROOT, 4242)[2]:
        assert l.count("|") == 1, (
            "header row has an embedded '|': %r - a reader splitting on '|' "
            "would see a different field count for this row than every other"
            % l)


def test_every_declared_substream_reaches_the_header():
    lines = C.new_bout(ROOT, 4242)[2]
    state, rng, _ = C.new_bout(ROOT, 4242)
    for name in rng.replay_metadata()['substreams']:
        name = name['name']
        assert any(l.startswith("H|rng_%s=" % name) for l in lines), (
            "substream %r exists but no artifact records it, so a replay "
            "could not reproduce its draws" % name)


# --- the canon the bout actually reads ---------------------------------------

def test_every_declared_canon_file_exists():
    """A declared-but-absent canon file is the enforced_by defect again."""
    for label, rel in C.CANON:
        path = os.path.join(ROOT, rel.replace("/", os.sep))
        assert os.path.exists(path), (
            "the integrated contract declares %s (%s) and it is not there"
            % (label, rel))


def test_canon_labels_are_unique():
    labels = [l for l, _ in C.CANON]
    assert len(labels) == len(set(labels)), (
        "two canon files share a header label, so one would overwrite the "
        "other's hashes in any reader that indexes by label")


def test_the_header_carries_the_dual_hash_block():
    """Decision 0023/0024's block, borrowed rather than rebuilt.

    Six C++ artifacts were found on 2026-08-07 emitting a hand-rolled version
    of this. The integrated contract gets exactly one builder.
    """
    lines = C.new_bout(ROOT, 4242)[2]
    for need in ("H|canon_hash_contract=", "H|canon_hash_roles=",
                 "H|canon_hash_policy=", "H|canon_hash_roles_raw="):
        assert any(l.startswith(need) for l in lines), "missing %s" % need
    for label, _rel in C.CANON:
        for suffix in ("_semantic=", "_raw=", "_roles="):
            assert any(l.startswith("H|canon_%s%s" % (label, suffix))
                       for l in lines), "missing canon_%s%s" % (label, suffix)


# --- the initial state is declared, not assumed ------------------------------

def test_the_initial_state_is_in_the_artifact():
    lines = C.new_bout(ROOT, 4242, rounds=3, round_ticks=600)[2]
    assert "H|seed=4242" in lines
    assert "H|rounds=3" in lines
    assert "H|round_ticks=600" in lines


def test_an_impossible_initial_state_is_refused():
    for kwargs in ({"rounds": 0}, {"round_ticks": 0}, {"rounds": -1}):
        with pytest.raises(ValueError):
            C.InitialState(4242, **kwargs)
    for bad in (-1, True, "4242", None):
        with pytest.raises((ValueError, TypeError)):
            C.InitialState(bad)


def test_a_changed_initial_state_changes_the_artifact():
    a = C.new_bout(ROOT, 4242, rounds=12)[2]
    b = C.new_bout(ROOT, 4242, rounds=3)[2]
    assert a != b


# --- the boundary Decision 0022 draws around the old pins ---------------------

def test_the_integrated_package_does_not_reach_into_phase_tooling():
    """Integration adds a contract; it does not reinterpret the old ones.

    If this package ever imports a phase analyzer, an edit here could move a
    unit pin - which is exactly what Decision 0022 forbids.
    """
    import io
    pkg = os.path.join(ROOT, "tools", "uppercut_integrated")
    for name in sorted(os.listdir(pkg)):
        if not name.endswith(".py"):
            continue
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
        #   2026-08-09 02:00 UTC | START edit: narrow the claim ]
        # SCANS IMPORTS, NOT PROSE. The first version searched the whole file
        # text, so it also forbade *naming* a phase analyzer in a comment - and
        # the comment it eventually caught was the one explaining WHY the
        # integrated contract declares its own REGIONS instead of importing
        # `analyze_core_condition`'s. Forbidding the explanation of a rule is
        # not enforcing the rule.
        #
        # This project has now made the too-broad-scan mistake three times: the
        # word "engagement" inside a canon `$comment`, the letter "e" inside
        # the word "debit", and this. The correct move is always to narrow the
        # claim, never to widen an exemption - so the claim is what it always
        # said it was, which is that this package may not IMPORT phase analyzer
        # code.
        text = io.open(os.path.join(pkg, name), encoding="utf-8").read()
        imports = [l for l in text.splitlines()
                   if l.lstrip().startswith(("import ", "from "))]
        for line in imports:
            assert "analyze_core" not in line and "analyze_render" not in line, (
                "%s imports phase analyzer code - integration must not be able "
                "to move a unit pin: %s" % (name, line.strip()))
        # And the runtime consequence, which a text scan could never see: no
        # phase analyzer may end up in this package's module namespace by any
        # route, including one added inside a function tomorrow.
        assert "__import__" not in text and "importlib" not in text, name
        # [ ... | 2026-08-09 02:00 UTC | END edit ]


def test_the_contract_identifier_is_versioned():
    # v3: the ruleset entered the declared canon (Decision 0033 Ruling 2).
    # v2 was Decision 0026's hierarchical substreams. The derivation itself
    # has not changed shape and stays v1.
    assert C.CONTRACT.endswith("-v3")
    assert R.DERIVATION_VERSION.endswith("-v1")


# --- what is NOT covered yet, named on purpose -------------------------------

NOT_YET_COVERABLE = {
    3: "range/evasion/policy/stamina/condition/knockdown/count/scoring events "
       "coexisting in one stream - needs those subsystems to exist",
    5: "pause, speed, rendering and camera not altering authority - needs the "
       "integrated runtime in the live arena",
    6: "one runtime driving commandlet evidence and the live arena - needs the "
       "integrated C++ side",
    7: "a bout ending by stoppage or decision - needs scoring and officiating",
}


def test_the_uncovered_assertions_are_still_named():
    """A checklist that quietly loses items is worse than no checklist.

    Decision 0022 lists seven required assertions. Four cannot be tested until
    their subsystems land. They are named here so that 'the integrated contract
    has tests' never reads as 'the integrated contract is proven'.
    """
    assert set(NOT_YET_COVERABLE) == {3, 5, 6, 7}
    for n, why in NOT_YET_COVERABLE.items():
        assert why and len(why) > 20
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:00 UTC | END ]
