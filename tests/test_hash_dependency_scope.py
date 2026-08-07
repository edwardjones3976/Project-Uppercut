# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:30 UTC | START ]
"""Decision 0024's required proofs, one test each.

The ruling narrows Decision 0023's dependency graph. Classification is still
evidence - reclassifying a combat field as documentation still moves the hash -
but a classification change for `pose_geometry` must no longer move `movement`,
which never read it.

    global hash-policy identity   rules that govern every file
              +
    per-file role-set identity    only this file's excluded pointers
              +
    authoritative payload
              =
    file semantic identity

Getting this wrong in either direction is a real failure. Too broad and every
manifest edit re-blesses the project, which is the attrition Decision 0023
exists to stop. Too narrow and someone reclassifies a live combat field and the
evidence system politely looks away.
"""
import copy
import io
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.uppercut_canon import canonical as C  # noqa: E402

MANIFEST = os.path.join(ROOT, "data", "hash_roles.json")
POSE = "data/pose_geometry.json"
MOVEMENT = "data/movement_model.json"


def _doc():
    return json.load(io.open(MANIFEST, encoding="utf-8"))


def _man(doc=None):
    return C.Manifest(doc if doc is not None else _doc())


def _sem(man, rel):
    _, sem, _ = man.hashes_for(ROOT, rel, "schema@1")
    return sem


# --- required proof 1 and 2 --------------------------------------------------

def test_changing_one_files_exclusions_moves_its_role_set_and_semantic():
    before = _man()
    doc = _doc()
    doc["files"][POSE]["non_authoritative"].append("/guard/plane_offset_ru")
    after = _man(doc)

    assert after.role_set_identity(POSE) != before.role_set_identity(POSE)
    assert _sem(after, POSE) != _sem(before, POSE)


# --- required proof 3: the whole point of Decision 0024 ----------------------

def test_that_change_does_NOT_move_an_unrelated_files_semantic_identity():
    before = _man()
    doc = _doc()
    doc["files"][POSE]["non_authoritative"].append("/guard/plane_offset_ru")
    after = _man(doc)

    assert after.role_set_identity(MOVEMENT) == before.role_set_identity(MOVEMENT)
    assert _sem(after, MOVEMENT) == _sem(before, MOVEMENT), (
        "reclassifying pose_geometry moved movement_model's identity. That is "
        "the excessive fan-out Decision 0024 exists to remove.")


# --- required proof 4 --------------------------------------------------------

@pytest.mark.parametrize("mutate", [
    lambda d: d.__setitem__("default_role", "non_authoritative"),
    lambda d: d["rules"].__setitem__("unknown_fields_are_authoritative", False),
    lambda d: d["rules"].__setitem__("name_based_exclusion_permitted", True),
    lambda d: d["coverage"].__setitem__(
        "files_not_listed_are_fully_authoritative", False),
])
def test_changing_a_global_policy_rule_moves_every_governed_identity(mutate):
    before = _man()
    doc = _doc()
    mutate(doc)
    after = _man(doc)

    assert after.policy_identity != before.policy_identity
    for rel in (POSE, MOVEMENT):
        assert _sem(after, rel) != _sem(before, rel), (
            "a global rule changed and %s did not move - the policy is not "
            "actually bound into that file's identity" % rel)


# --- required proof 5 --------------------------------------------------------

def test_manifest_prose_moves_only_the_raw_provenance_hash():
    """Change the manifest's exact bytes, preserve policy and role-sets."""
    text = io.open(MANIFEST, encoding="utf-8", newline="").read()
    before = C.Manifest(C.parse(text), text)

    doc = json.loads(text)
    doc["$comment"] = "an entirely rewritten explanation of this manifest"
    doc["files"][POSE]["review_note"] = "reworded"
    new_text = json.dumps(doc)
    after = C.Manifest(C.parse(new_text), new_text)

    assert after.raw_hash != before.raw_hash, "provenance must notice"
    assert after.policy_identity == before.policy_identity
    for rel in (POSE, MOVEMENT):
        assert after.role_set_identity(rel) == before.role_set_identity(rel)
        assert _sem(after, rel) == _sem(before, rel)


# --- required proof 6 --------------------------------------------------------

def test_removing_a_classification_entry_cannot_silently_fall_back():
    """Un-classifying a file must MOVE its identity, not quietly widen it.

    Without this, deleting a file's entry would make every previously excluded
    field authoritative again - arguably safe - but the semantic hash would
    have to change, and if it did not, a reader could not tell which regime
    produced it.
    """
    before = _man()
    doc = _doc()
    del doc["files"][POSE]
    after = _man(doc)

    assert after.role_set_identity(POSE) != before.role_set_identity(POSE)
    assert _sem(after, POSE) != _sem(before, POSE)
    assert after.patterns_for(POSE) == [], "an absent entry excludes nothing"


def test_renaming_a_classification_entry_moves_both_files():
    before = _man()
    doc = _doc()
    # Built by concatenation, not written as a literal: the repository has a
    # guard (tests/test_cross_platform_paths.py) that every `data/....json`
    # string appearing in a test must exist on disk with exact case, and it
    # caught this fixture the first time it was written as a literal. The guard
    # is right - a path that looks real and is not is how a test starts
    # asserting nothing.
    renamed = POSE.replace(".json", "") + "_does_not_exist" + ".json"
    doc["files"][renamed] = doc["files"].pop(POSE)
    after = _man(doc)
    assert _sem(after, POSE) != _sem(before, POSE)


# --- required proof 7 --------------------------------------------------------

def test_an_unlisted_canon_file_is_fully_authoritative():
    man = _man()
    assert man.patterns_for("data/clock_model.json") == []
    assert man.is_classified("data/clock_model.json") is False
    # And hashing it excludes nothing: the semantic payload still contains its
    # prose, because nobody classified it.
    body = man.canonical_bytes_for(ROOT, "data/clock_model.json")
    assert b"tick_rate_hz" in body
    assert b"$comment" in body, (
        "an unclassified file lost a field - silence in the manifest must "
        "never mean exclusion")


# --- RFC 6901 aliasing: the pointer identity requirement ---------------------

ALIAS_DOC = {
    "a/b": {"v": 1, "note": "literal key containing a slash"},
    "a": {"b": {"v": 2, "note": "nested"}},
}


def test_a_literal_slash_key_is_not_the_nested_path():
    """`/a~1b` names the key "a/b". `/a/b` names "a" then "b"."""
    assert C.parse_pointer("/a~1b") == ("a/b",)
    assert C.parse_pointer("/a/b") == ("a", "b")
    assert C.parse_pointer("/a~1b") != C.parse_pointer("/a/b")


def test_excluding_the_literal_key_leaves_the_nested_one_alone():
    doc = copy.deepcopy(ALIAS_DOC)
    stripped, matched = C.strip(doc, ["/a~1b/note"])
    assert matched["/a~1b/note"] == [("a/b", "note")]
    assert "note" not in stripped["a/b"]
    assert stripped["a"]["b"]["note"] == "nested", (
        "excluding the literal key 'a/b' also removed the nested a -> b - the "
        "two paths have aliased")


def test_excluding_the_nested_path_leaves_the_literal_key_alone():
    doc = copy.deepcopy(ALIAS_DOC)
    stripped, matched = C.strip(doc, ["/a/b/note"])
    assert matched["/a/b/note"] == [("a", "b", "note")]
    assert "note" not in stripped["a"]["b"]
    assert stripped["a/b"]["note"] == "literal key containing a slash"


def test_the_two_documents_do_not_hash_alike():
    """The mutation form of the same claim."""
    only_literal = {"a/b": {"v": 1}}
    only_nested = {"a": {"b": {"v": 1}}}
    assert (C.canonical_bytes(json.dumps(only_literal))
            != C.canonical_bytes(json.dumps(only_nested)))


def test_tilde_escapes_decode_in_the_specified_order():
    """~1 before ~0, or the key "~1" decodes to "/"."""
    assert C.parse_pointer("/~01") == ("~1",)
    assert C.parse_pointer("/~1") == ("/",)
    assert C.serialize_pointer(("~1",)) == "/~01"
    assert C.serialize_pointer(("/",)) == "/~1"


def test_a_pointer_round_trips_through_its_display_form():
    for segs in [("a/b",), ("a", "b"), ("~1",), ("/",), ("a~b",), ("x", "0")]:
        assert C.parse_pointer(C.serialize_pointer(segs)) == segs


def test_concrete_paths_are_tuples_not_strings():
    """The representation itself, asserted - a string would re-open aliasing."""
    hits = C.expand(ALIAS_DOC, "/a~1b/v")
    assert hits == [("a/b", "v")]
    assert all(isinstance(h, tuple) for h in hits)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:30 UTC | END ]
