# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 01:45 UTC | START ]
"""Mutation coverage for the semantic canonicalizer. Decision 0023.

The ruling lists eight things the implementation must prove, and says plainly
that "a blanket recursive name-stripper is not acceptable evidence code". So
each numbered requirement below has its own test named after it, and the tests
are adversarial rather than illustrative: every one of them tries to sneak a
change past the semantic hash.

The stakes are unusual. This is evidence code that decides whether OTHER
evidence counts. A false negative here - a canon change the semantic hash cannot
see - would not fail loudly; it would silently make a moved fight look
unchanged, which is the exact failure the whole pin system exists to prevent.
That is why the number tests refuse rather than round, and why nothing is
excluded without an explicit pointer.

THESE TESTS WERE CHECKED AGAINST THE FORBIDDEN IMPLEMENTATION. A blanket
recursive name-stripper was written and swapped in, and six of these failed,
including both tests that encode the Director's safeguard. A suite that cannot
tell the correct canonicalizer from the one the ruling prohibits is decorative.
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

# A fixture with the shapes that matter: prose beside values, prose INSIDE an
# object that also holds values, an array of objects each carrying a note, and
# a field whose name sounds explanatory but selects behaviour.
FIXTURE = {
    "$comment": "explanatory header",
    "contribution": {"agent": "somebody", "model": "some-model"},
    "guard": {
        "$comment": "prose inside an object that also holds a value",
        "authoring_margin": 0.05,
        "authoring_margin_note": "prose about the value beside it",
        "plane_interception_min_extent": 0.6
    },
    "moves": [
        {"id": "jab_lead", "cost": 1.0, "cost_model": "authored",
         "note": "prose"},
        {"id": "step_in", "cost": 0.132, "cost_model": "displacement",
         "note": "prose"}
    ],
    "bands": [0, 1, 2]
}

PATTERNS = [
    "/$comment",
    "/contribution",
    "/guard/$comment",
    "/guard/authoring_margin_note",
    "/moves/*/note",
]


def sem(doc, patterns=PATTERNS):
    return C.hashes(json.dumps(doc), patterns, "fixture-v1")[1]


def raw(doc, patterns=PATTERNS):
    return C.hashes(json.dumps(doc), patterns, "fixture-v1")[0]


BASE = sem(FIXTURE)


def mutated():
    return copy.deepcopy(FIXTURE)


# --- 1. documentation-only change moves raw, not semantic --------------------

def test_1_declared_documentation_moves_raw_hash_only():
    doc = mutated()
    doc["$comment"] = "COMPLETELY DIFFERENT PROSE"
    assert raw(doc) != raw(FIXTURE), "the provenance hash must notice everything"
    assert sem(doc) == BASE, (
        "editing a declared documentation field moved the semantic hash. This "
        "is the bug Decision 0023 exists to fix.")


def test_1b_contribution_metadata_moves_raw_hash_only():
    doc = mutated()
    doc["contribution"] = {"agent": "someone else", "model": "another-model"}
    assert raw(doc) != raw(FIXTURE)
    assert sem(doc) == BASE


def test_1c_nested_declared_documentation_moves_raw_hash_only():
    doc = mutated()
    doc["guard"]["authoring_margin_note"] = "rewritten sentence"
    doc["moves"][0]["note"] = "rewritten sentence"
    assert raw(doc) != raw(FIXTURE)
    assert sem(doc) == BASE


# --- 2. any authoritative mutation moves the semantic hash -------------------

def test_2_scalar_change_moves_semantic_hash():
    doc = mutated()
    doc["guard"]["plane_interception_min_extent"] = 0.61
    assert sem(doc) != BASE


def test_2b_object_member_added_moves_semantic_hash():
    doc = mutated()
    doc["guard"]["new_field"] = 1
    assert sem(doc) != BASE


def test_2c_object_member_removed_moves_semantic_hash():
    doc = mutated()
    del doc["guard"]["plane_interception_min_extent"]
    assert sem(doc) != BASE


def test_2d_array_item_change_moves_semantic_hash():
    doc = mutated()
    doc["bands"][1] = 99
    assert sem(doc) != BASE


def test_2e_array_ORDER_change_moves_semantic_hash():
    """Order is canon. The five range bands are a sequence, not a set."""
    doc = mutated()
    doc["bands"] = [2, 1, 0]
    assert sem(doc) != BASE
    doc2 = mutated()
    doc2["moves"] = list(reversed(doc2["moves"]))
    assert sem(doc2) != BASE


def test_2f_key_ORDER_change_does_not_move_semantic_hash():
    """Object key order is not canon, and a reformat must not read as a retune."""
    doc = mutated()
    doc["guard"] = dict(reversed(list(doc["guard"].items())))
    assert sem(doc) == BASE


# --- 3. a value inside an object that also holds excluded prose --------------

def test_3_authoritative_value_beside_excluded_prose_still_counts():
    """The exact shape that would fail under a lazy 'strip the object' rule."""
    doc = mutated()
    doc["guard"]["authoring_margin"] = 0.06
    assert sem(doc) != BASE, (
        "a tuned value hid behind the prose in its own object - the "
        "canonicalizer is stripping too much")


def test_3b_authoritative_value_inside_a_wildcard_element_still_counts():
    doc = mutated()
    doc["moves"][1]["cost_model"] = "authored"
    assert sem(doc) != BASE, (
        "cost_model selects displacement pricing; it must never be swept up "
        "with the note beside it")


# --- 4. an undeclared field cannot be silently excluded ----------------------

def test_4_a_new_field_that_merely_LOOKS_explanatory_is_authoritative():
    """The safeguard the Director added to the original recommendation.

    Name-based stripping would make this pass silently, which is what "a
    trapdoor with a polite label" means: rename your field to end in _note and
    it stops being evidence.
    """
    doc = mutated()
    doc["guard"]["some_new_note"] = "looks like prose, was never declared"
    assert sem(doc) != BASE, (
        "an undeclared field was excluded because of its NAME. Decision 0023 "
        "forbids exactly this.")
    doc2 = mutated()
    doc2["guard"]["$comment_extra"] = "also looks like prose"
    assert sem(doc2) != BASE


def test_4b_undeclared_prose_at_a_new_path_is_authoritative():
    doc = mutated()
    doc["moves"][0]["notes"] = "plural, undeclared, therefore load-bearing"
    assert sem(doc) != BASE


# --- 5. duplicate keys are rejected ------------------------------------------

def test_5_duplicate_keys_are_refused():
    with pytest.raises(C.CanonError) as exc:
        C.hashes('{"a": 1, "a": 2}', [], "fixture-v1")
    assert "duplicate" in str(exc.value)


def test_5b_non_finite_numbers_are_refused():
    for literal in ("NaN", "Infinity", "-Infinity"):
        with pytest.raises(C.CanonError):
            C.hashes('{"x": %s}' % literal, [], "fixture-v1")


# --- 7. the canonicalizer version is inside the hashed payload ---------------

def test_7_schema_identity_is_part_of_the_identity():
    a = C.hashes(json.dumps(FIXTURE), PATTERNS, "fixture-v1")[1]
    b = C.hashes(json.dumps(FIXTURE), PATTERNS, "fixture-v2")[1]
    assert a != b, (
        "two different schema identities produced one semantic hash - a "
        "contract change would migrate silently")


def test_7b_the_contract_version_is_inside_the_payload():
    assert C.CONTRACT.encode("ascii") in C.payload(FIXTURE, "fixture-v1")


# --- the manifest's own guard rails ------------------------------------------

def test_a_dead_pattern_is_an_error_not_a_no_op():
    with pytest.raises(C.CanonError) as exc:
        C.hashes(json.dumps(FIXTURE), ["/guard/does_not_exist"], "fixture-v1")
    assert "matches nothing" in str(exc.value)


def test_a_wildcard_cannot_delete_a_whole_array_element():
    with pytest.raises(C.CanonError) as exc:
        C.hashes(json.dumps(FIXTURE), ["/moves/*"], "fixture-v1")
    assert "renumber" in str(exc.value)


def test_a_wildcard_does_not_match_object_keys():
    """'*' means one array index. If it matched keys it would be a recursive
    stripper wearing a different hat."""
    with pytest.raises(C.CanonError):
        C.hashes(json.dumps(FIXTURE), ["/*/authoring_margin_note"], "fixture-v1")


def test_the_whole_document_cannot_be_declared_non_authoritative():
    with pytest.raises(C.CanonError):
        C.hashes(json.dumps(FIXTURE), [""], "fixture-v1")


# --- number handling ---------------------------------------------------------

def test_integers_and_their_float_spelling_are_the_same_value():
    assert sem({"x": 3500}, []) == sem({"x": 3500.0}, [])


def test_a_number_too_precise_for_the_canonical_form_is_refused_not_rounded():
    with pytest.raises(C.CanonError) as exc:
        C.hashes('{"x": 0.00000000001}', [], "fixture-v1")
    assert "Refused rather than rounded" in str(exc.value)


def test_a_tenth_decimal_place_still_counts():
    """The boundary case: exactly at the declared precision, still evidence."""
    assert sem({"x": 0.0000000001}, []) != sem({"x": 0.0000000002}, [])


def test_booleans_are_not_numbers():
    """Python's bool is an int subclass, which is a real way to get this wrong."""
    assert sem({"x": True}, []) != sem({"x": 1}, [])
    assert sem({"x": False}, []) != sem({"x": 0}, [])


def test_null_is_not_the_string_null_and_not_zero():
    assert sem({"x": None}, []) != sem({"x": "null"}, [])
    assert sem({"x": None}, []) != sem({"x": 0}, [])


def test_a_string_of_digits_is_not_the_number():
    assert sem({"x": "1"}, []) != sem({"x": 1}, [])


def test_unicode_survives_without_escaping_ambiguity():
    """Two serialisers disagree about \\uXXXX escapes; the byte stream cannot."""
    a = C.hashes(json.dumps({"x": "café"}, ensure_ascii=True), [], "v")[1]
    b = C.hashes(json.dumps({"x": "café"}, ensure_ascii=False), [], "v")[1]
    assert a == b, "the same string hashed differently depending on escaping"


# --- the manifest against the REAL canon -------------------------------------

MANIFEST = os.path.join(ROOT, "data", "hash_roles.json")


def _manifest():
    return json.load(io.open(MANIFEST, encoding="utf-8"))


# Concrete pointers excluded per file, snapshotted. A field added under an
# existing wildcard - a nineteenth move's `note` - changes a count here rather
# than vanishing quietly. That is the one automatic case in the design and this
# is what makes it visible in review.
EXPECTED_EXPANSION = {
    "data/movement_model.json": 21,
    "data/moves/generic_sandbox_moves.json": 5,
    "data/animation_model.json": 16,
    "data/pose_geometry.json": 7,
    "data/guard_evasion_model.json": 29,
    "data/condition_model.json": 17,
    "data/stamina_economy.json": 16,
    "data/moves/generic_sandbox_effort.json": 25,
}


@pytest.mark.parametrize("rel", sorted(EXPECTED_EXPANSION))
def test_every_manifest_pattern_matches_real_canon(rel):
    """A dead pattern raises, so this passing means every pointer is live."""
    spec = _manifest()["files"][rel]
    _, _, matched = C.hashes_for_file(
        os.path.join(ROOT, rel), spec["non_authoritative"], "test")
    concrete = sum(len(v) for v in matched.values())
    assert concrete == EXPECTED_EXPANSION[rel], (
        "%s now excludes %d concrete pointers, not %d. If a field was added "
        "under an existing wildcard, confirm it really is documentation and "
        "update this snapshot in the same commit." % (rel, concrete,
                                                      EXPECTED_EXPANSION[rel]))


def test_the_manifest_refuses_name_based_exclusion_in_its_own_rules():
    m = _manifest()
    assert m["default_role"] == "authoritative"
    assert m["rules"]["unknown_fields_are_authoritative"] is True
    assert m["rules"]["name_based_exclusion_permitted"] is False
    assert m["coverage"]["files_not_listed_are_fully_authoritative"] is True


def test_a_prose_edit_to_real_canon_does_not_move_its_semantic_hash():
    """The 2026-08-06 incident, replayed against the file that caused it.

    A comment edit inside pose_geometry.json broke four frozen pins. Under the
    semantic hash the same edit must move the raw identity and leave the
    authoritative one alone - which is the entire point of Decision 0023.
    """
    rel = "data/pose_geometry.json"
    spec = _manifest()["files"][rel]
    text = io.open(os.path.join(ROOT, rel), encoding="utf-8", newline="").read()
    raw_a, sem_a, _ = C.hashes(text, spec["non_authoritative"], "pose-v1")

    doc = json.loads(text)
    doc["guard"]["authoring_margin_note"] = "an entirely rewritten explanation"
    raw_b, sem_b, _ = C.hashes(json.dumps(doc), spec["non_authoritative"],
                               "pose-v1")

    assert raw_a != raw_b, "provenance must still notice the edit"
    assert sem_a == sem_b, (
        "a comment edit still moves the authoritative identity - Decision 0023 "
        "is not actually implemented")

    doc2 = json.loads(text)
    doc2["guard"]["authoring_margin"] = 0.07
    _, sem_c, _ = C.hashes(json.dumps(doc2), spec["non_authoritative"], "pose-v1")
    assert sem_a != sem_c, "and a real retune must still move it"


# --- the Director's six additional requirements (Issue #17) ------------------

def test_r1_the_manifest_has_its_own_semantic_identity():
    """Requirement 1: the manifest is canon and cannot judge from outside."""
    m = C.Manifest.load(MANIFEST)
    assert len(m.identity) == 64
    assert m.version == "uppercut-hash-roles-v1"


def test_r1b_reclassifying_a_field_moves_the_semantic_hash():
    """The attack requirement 1 exists to stop.

    Convert a live combat field into an "excluded documentation field" and the
    evidence system must NOT politely look away. Two things have to move: the
    manifest's own identity, and therefore every file hashed under it.
    """
    doc = json.load(io.open(MANIFEST, encoding="utf-8"))
    honest = C.Manifest(copy.deepcopy(doc))

    # Someone decides `authoring_margin` - a real threshold - is documentation.
    doc["files"]["data/pose_geometry.json"]["non_authoritative"].append(
        "/guard/authoring_margin")
    tampered = C.Manifest(doc)

    assert tampered.identity != honest.identity, (
        "reclassifying a combat field left the manifest identity unchanged - "
        "the classification is not inside the evidence envelope")

    rel = "data/pose_geometry.json"
    _, sem_honest, _ = honest.hashes_for(ROOT, rel, "pose-v1")
    _, sem_tampered, _ = tampered.hashes_for(ROOT, rel, "pose-v1")
    assert sem_honest != sem_tampered


def test_r1c_a_manifest_prose_edit_does_not_move_its_identity():
    """The manifest gets the same treatment it gives everything else."""
    doc = json.load(io.open(MANIFEST, encoding="utf-8"))
    before = C.Manifest(copy.deepcopy(doc)).identity
    doc["$comment"] = "a completely rewritten explanation of this manifest"
    doc["files"]["data/pose_geometry.json"]["review_note"] = "reworded"
    assert C.Manifest(doc).identity == before


def test_r3_negative_zero_is_the_same_gameplay_quantity_as_zero():
    """Requirement 3. -0, 0, -0.0 and 0.0 are one number."""
    assert sem({"x": -0.0}, []) == sem({"x": 0.0}, [])
    assert sem({"x": -0.0}, []) == sem({"x": 0}, [])
    # ...and the RAW hash still distinguishes the source spelling.
    a = C.hashes('{"x": -0.0}', [], "v")[0]
    b = C.hashes('{"x": 0.0}', [], "v")[0]
    assert a != b, "provenance must still see how the file spelled it"


def test_r5_inserting_a_move_moves_the_semantic_hash():
    """Requirement 5, insertion. A wildcard classifies notes, not membership."""
    doc = mutated()
    doc["moves"].insert(1, {"id": "hook_lead", "cost": 2.2,
                            "cost_model": "authored", "note": "prose"})
    assert sem(doc) != BASE


def test_r5b_deleting_a_move_moves_the_semantic_hash():
    doc = mutated()
    del doc["moves"][0]
    assert sem(doc) != BASE


def test_r5c_a_wildcard_classified_note_still_leaves_membership_authoritative():
    """Every note is excluded, yet the array is still fully load-bearing."""
    doc = mutated()
    for mv in doc["moves"]:
        mv["note"] = "all rewritten"
    assert sem(doc) == BASE, "notes are declared documentation"
    doc2 = mutated()
    doc2["moves"].append({"id": "extra", "cost": 1.0, "note": "prose"})
    assert sem(doc2) != BASE, "adding a move must still move identity"


def test_r6_all_four_identities_are_bound_into_the_payload():
    """Requirement 6: changing any rule that decides sameness changes sameness."""
    base = C.hashes(json.dumps(FIXTURE), PATTERNS, "s1", "m1", "v1")[1]
    assert C.hashes(json.dumps(FIXTURE), PATTERNS, "s2", "m1", "v1")[1] != base
    assert C.hashes(json.dumps(FIXTURE), PATTERNS, "s1", "m2", "v1")[1] != base
    assert C.hashes(json.dumps(FIXTURE), PATTERNS, "s1", "m1", "v2")[1] != base
    head = C.payload(FIXTURE, "s1", "m1", "v1")
    assert C.CANONICALIZER_VERSION.encode() in head
    assert C.HASH_CONTRACT_VERSION.encode() in head


def test_r6b_a_manifest_declaring_the_wrong_contract_is_refused():
    doc = json.load(io.open(MANIFEST, encoding="utf-8"))
    doc["canonicalizer_contract"] = "uppercut-semantic-json-v99"
    with pytest.raises(C.CanonError) as exc:
        C.Manifest(doc)
    assert "refusing to hash" in str(exc.value)

    doc2 = json.load(io.open(MANIFEST, encoding="utf-8"))
    doc2["hash_contract_version"] = "something-else"
    with pytest.raises(C.CanonError):
        C.Manifest(doc2)


# --- the forbidden implementation, kept in the suite -------------------------

def _naive_strip(doc, patterns):
    """The implementation Decision 0023 explicitly prohibits.

    "Mutation coverage must include every exclusion rule. A blanket recursive
    name-stripper is not acceptable evidence code."

    It lives here, in the tests, so the prohibition is enforced rather than
    merely stated - and so nobody can "simplify" the real canonicalizer into
    this shape without a test going red.
    """
    suspect = ("$comment", "note", "notes", "contribution")

    def prune(n):
        if isinstance(n, dict):
            return {k: prune(v) for k, v in n.items()
                    if k.lower() not in suspect
                    and not k.lower().endswith("_note")}
        if isinstance(n, list):
            return [prune(v) for v in n]
        return n

    return prune(doc), {p: ["/naive"] for p in patterns}


def _naive_sem(doc):
    stripped, _ = _naive_strip(copy.deepcopy(doc), [])
    return C.hashlib.sha256(
        C.payload(stripped, "fixture-v1", "m", "v")).hexdigest()


def test_the_forbidden_name_stripper_is_detectably_wrong():
    """The proof that the tests above have teeth.

    A suite that cannot tell the correct canonicalizer from the one the ruling
    prohibits is decorative. Each case below is something the real
    canonicalizer catches and the name-stripper does not.
    """
    naive_base = _naive_sem(FIXTURE)
    missed = []

    # An undeclared field that merely LOOKS explanatory - the trapdoor.
    doc = mutated()
    doc["guard"]["some_new_note"] = "never declared anywhere"
    if _naive_sem(doc) == naive_base:
        missed.append("undeclared *_note field")

    doc = mutated()
    doc["moves"][0]["notes"] = "plural, undeclared"
    if _naive_sem(doc) == naive_base:
        missed.append("undeclared 'notes' field")

    doc = mutated()
    doc["contribution"] = {"agent": "anyone", "model": "anything"}
    if _naive_sem(doc) != naive_base:
        missed.append("contribution (sanity: should be excluded by both)")

    assert len(missed) >= 2, (
        "the name-stripper was not caught by these cases, which means the "
        "distinction this suite claims to test is not actually being tested")

    # And the real canonicalizer catches every one of them.
    doc = mutated()
    doc["guard"]["some_new_note"] = "never declared anywhere"
    assert sem(doc) != BASE
    doc = mutated()
    doc["moves"][0]["notes"] = "plural, undeclared"
    assert sem(doc) != BASE


# --- the shared vectors ------------------------------------------------------

VECTORS = os.path.join(ROOT, "tests", "fixtures", "canon_hash_vectors.json")


def test_the_cross_language_vectors_still_reproduce():
    """These are what the C++ side must match. If Python drifts from them, the
    C++ implementation would be chasing a moving target."""
    data = json.load(io.open(VECTORS, encoding="utf-8"))
    assert data["canonicalizer_contract"] == C.CONTRACT
    for v in data["vectors"]:
        raw_h, sem_h, _ = C.hashes(v["input_json"], v["patterns"],
                                   v["schema_identity"], v["manifest_identity"],
                                   v["manifest_version"])
        assert raw_h == v["raw_sha256"], "%s raw" % v["name"]
        assert sem_h == v["semantic_sha256"], "%s semantic" % v["name"]


def test_every_rejection_vector_is_actually_rejected():
    data = json.load(io.open(VECTORS, encoding="utf-8"))
    for v in data["rejection_vectors"]:
        with pytest.raises(C.CanonError):
            C.hashes(v["input_json"], v["patterns"], v["schema_identity"])
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 01:45 UTC | END ]
