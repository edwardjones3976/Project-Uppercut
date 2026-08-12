# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ]
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:58 UTC | START edit ]
"""The Unreal 1-round test pairing must be unique on expressed attributes.

Adversarial cases ported from feat/matched-pair-and-av-evidence: the check must
refuse pairs that only differ where the fight cannot see them, and the expressed
set must come from canon (including `recovery`), not a drifting hardcoded tuple.
"""
from __future__ import annotations

import copy
from pathlib import Path

from tools.uppercut_validate import attributes, budget
from tools.uppercut_validate import fighter_pair as FP
from tools.uppercut_validate import strict_json as json

REPO = Path(__file__).resolve().parents[1]


def test_default_pair_files_exist():
    for fid in FP.DEFAULT_PAIR:
        path = REPO / "fixtures" / "fighters" / "legal" / f"{fid}.json"
        assert path.is_file(), path


def test_default_pair_each_card_is_rule10_legal_and_budget_complete():
    families = attributes.load_families()
    cfg = budget.load_config()
    tax = budget.taxonomy_keys()
    for fid in FP.DEFAULT_PAIR:
        card = FP.load_fighter(fid)
        rep = attributes.validate_fighter(card, families)
        assert rep.legal, [str(v) for v in rep.violations]
        assert set(card["attributes"]) == tax
        net = budget.profile(card["attributes"], refund_rate=cfg["refund_rate"])[
            cfg["curve"]
        ]["net"]
        assert net <= cfg["cap"], (fid, net, cfg["cap"])


def test_default_pair_is_unique_on_expressed_in_round_attrs():
    errs = FP.validate_default_pair()
    assert errs == [], errs
    a = FP.load_fighter(FP.DEFAULT_PAIR[0])
    b = FP.load_fighter(FP.DEFAULT_PAIR[1])
    diffs = FP.expressed_diffs(a, b)
    assert len(diffs) >= FP.DEFAULT_MIN_KEYS


def test_identical_cards_fail_pair_uniqueness():
    a = FP.load_fighter(FP.DEFAULT_PAIR[0])
    errs = FP.validate_pair(a, a)
    assert errs


def test_a_card_matched_with_itself_is_refused():
    a = FP.load_fighter(FP.DEFAULT_PAIR[0])
    findings = FP.validate_pair(a, copy.deepcopy(a))
    assert findings
    assert any("same fighter id" in f for f in findings)


def test_two_empty_cards_are_refused():
    empty = {"id": "empty_one", "attributes": {}}
    other = {"id": "empty_two", "attributes": {}}
    assert FP.validate_pair(empty, other)


def test_a_pair_differing_only_where_the_fight_cannot_see_is_refused():
    """THE CASE THIS MODULE EXISTS FOR.

    Two cards separated by the full width of the economy on unexpressed
    attributes and identical everywhere the fight can see. A naive 24-key
    comparison calls that maximally differentiated; it produces twins.
    """
    unexpressed = sorted(set(budget.taxonomy_keys()) - FP.expressed_attributes())
    assert len(unexpressed) >= 8, "canon should still name unexpressed attributes"

    a = {"id": "twin_a", "attributes": {k: 60 for k in unexpressed}}
    b = {"id": "twin_b", "attributes": {k: -60 for k in unexpressed}}
    findings = FP.validate_pair(a, b)
    assert findings, (
        "a pair differing only on attributes that scale nothing must be refused"
    )


def test_the_threshold_binds_exactly_where_it_says():
    expressed = sorted(FP.expressed_attributes())

    def built(n_differing, delta):
        a = {"id": "probe_a", "attributes": {k: 0 for k in expressed}}
        b = {"id": "probe_b", "attributes": {k: 0 for k in expressed}}
        for k in expressed[:n_differing]:
            b["attributes"][k] = delta
        return a, b

    assert FP.validate_pair(*built(FP.DEFAULT_MIN_KEYS - 1, FP.DEFAULT_MIN_DELTA))
    assert FP.validate_pair(*built(FP.DEFAULT_MIN_KEYS, FP.DEFAULT_MIN_DELTA - 1))
    assert FP.validate_pair(*built(FP.DEFAULT_MIN_KEYS, FP.DEFAULT_MIN_DELTA)) == []


def test_expressed_attributes_come_from_canon_not_a_hardcoded_tuple():
    doc = json.loads(
        (REPO / "data" / "attribute_effects.json").read_text(encoding="utf-8")
    )
    assert FP.expressed_attributes() == {e["attribute"] for e in doc["effects"]}
    assert "recovery" in FP.expressed_attributes()
    assert "recovery" in FP.EXPRESSED_IN_ROUND


def test_expressed_and_unexpressed_partition_the_taxonomy():
    doc = json.loads(
        (REPO / "data" / "attribute_effects.json").read_text(encoding="utf-8")
    )
    named_absent = set(doc["unexpressed_attributes"]["not_yet_expressed"])
    assert FP.expressed_attributes() | named_absent == budget.taxonomy_keys()
    assert not (FP.expressed_attributes() & named_absent)


def test_default_pair_keeps_unexpressed_attrs_near_baseline():
    """Do not invent Ringcraft/Showmanship as combat drivers on test cards."""
    unexpressed = set(budget.taxonomy_keys()) - FP.expressed_attributes()
    for fid in FP.DEFAULT_PAIR:
        c = FP.load_fighter(fid)
        for k in sorted(unexpressed):
            v = c["attributes"][k]
            assert abs(v) <= 30, (
                "%s sets unexpressed %s to %d; an attribute that scales nothing "
                "must not carry a number that looks like it does" % (fid, k, v)
            )
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:58 UTC | END edit ]
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ]
