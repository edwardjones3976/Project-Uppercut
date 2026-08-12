# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:26 UTC | START ]
"""The matched pair, and proof the check that guards it can fail.

Most of this file is about the SECOND thing. A uniqueness check that passes
whatever it is shown is worse than no check, because it converts an unexamined
assumption into a green tick. So every rule the module enforces gets a
counter-example here that must be refused, and the most important of those is
`test_a_pair_differing_only_where_the_fight_cannot_see_is_refused` - the exact
bug a naive 24-key comparison would ship.
"""
import copy
import json
from pathlib import Path

import pytest

from tools.uppercut_validate import attributes as A
from tools.uppercut_validate import budget as B
from tools.uppercut_validate import pairing as P

REPO = Path(__file__).resolve().parents[1]


def card(fighter_id):
    return P.load_card(fighter_id)


@pytest.fixture
def pair():
    return [card(i) for i in P.MATCH_PAIR]


# --------------------------------------------------------------- the pair --

def test_the_declared_match_pair_is_a_real_matchup(pair):
    assert P.check_pair(*pair) == []


def test_both_cards_are_legal_under_rule_10(pair):
    families = A.load_families()
    for c in pair:
        rep = A.validate_fighter(c, families)
        assert rep.legal, "%s: %s" % (c["id"], [str(v) for v in rep.violations])


def test_both_cards_declare_every_attribute_so_the_budget_cap_applies(pair):
    """A partial card is an instrument whose cost is reported but not capped
    (data/attribute_budget.json, cap_scope). These two are meant to be fought
    with, so they must be complete or the cap is decorative."""
    taxonomy = B.taxonomy_keys()
    for c in pair:
        assert set(c["attributes"]) == taxonomy, (
            "%s declares %d of %d attributes"
            % (c["id"], len(c["attributes"]), len(taxonomy)))
        ev = B.evaluate(c["attributes"])
        assert ev["complete_declaration"] and ev["cap_enforced"]
        assert not ev["over_cap"], "%s nets %s" % (c["id"], ev["net"])


def test_both_cards_are_generic_fixtures_not_roster_characters(pair):
    """Phase 1B owns the roster. A card that quietly acquired Specials, an
    Ultimate or a trait list would be a character arriving through the test
    fixtures door."""
    for c in pair:
        assert c["fixture_kind"] == "generic_test_fixture"
        assert c["specials"] == []
        assert c["ultimate"] is None
        assert c["full_crowd_trait"] is None
        assert c["traits"] == []


def test_neither_card_is_named_after_a_roster_character(pair):
    forbidden = ("adewale", "calvin")
    for c in pair:
        blob = json.dumps(c).lower()
        for name in forbidden:
            assert name not in blob, "%s mentions %s" % (c["id"], name)


# ------------------------------------------------- the check is not vacuous --

def test_a_card_matched_with_itself_is_refused():
    a = card("generic_pressure_a")
    findings = P.check_pair(a, copy.deepcopy(a))
    assert findings, "identical cards must not be a legal matchup"
    assert any("himself" in f for f in findings)


def test_two_empty_cards_are_refused():
    """The state the live C++ fighters were actually in before this work:
    both cards empty, every multiplier 1.0."""
    empty = {"id": "empty_one", "attributes": {}}
    other = {"id": "empty_two", "attributes": {}}
    assert P.check_pair(empty, other)


def test_a_pair_differing_only_where_the_fight_cannot_see_is_refused():
    """THE CASE THIS MODULE EXISTS FOR.

    Two cards separated by the full width of the economy on ten attributes -
    and identical on every attribute that has an effect. A comparison over all
    24 keys would call this the most differentiated pair in the repository. It
    would produce two fighters who fight exactly the same.
    """
    unexpressed = sorted(
        set(B.taxonomy_keys()) - P.expressed_attributes())
    assert len(unexpressed) >= 8, "canon should still name unexpressed attributes"

    a = {"id": "twin_a", "attributes": {k: 60 for k in unexpressed}}
    b = {"id": "twin_b", "attributes": {k: -60 for k in unexpressed}}
    findings = P.check_pair(a, b)
    assert findings, (
        "a pair differing by 120 points on ten attributes that scale nothing "
        "must still be refused")


def test_the_threshold_binds_exactly_where_it_says(pair):
    """One below the bar fails, the bar itself passes. Written because an
    off-by-one in a hygiene check is invisible until it lets something through."""
    expressed = sorted(P.expressed_attributes())

    def built(n_differing, delta):
        a = {"id": "probe_a", "attributes": {k: 0 for k in expressed}}
        b = {"id": "probe_b", "attributes": {k: 0 for k in expressed}}
        for k in expressed[:n_differing]:
            b["attributes"][k] = delta
        return a, b

    assert P.check_pair(*built(P.MIN_DIFFERING - 1, P.MIN_DELTA)), \
        "one attribute short of the bar must be refused"
    assert P.check_pair(*built(P.MIN_DIFFERING, P.MIN_DELTA - 1)) , \
        "one point short of the delta must be refused"
    assert P.check_pair(*built(P.MIN_DIFFERING, P.MIN_DELTA)) == [], \
        "exactly the bar must be accepted"


# ------------------------------------------- the expressed set is canon's ---

def test_expressed_attributes_come_from_canon_not_from_this_module():
    doc = json.loads(
        (REPO / "data" / "attribute_effects.json").read_text(encoding="utf-8"))
    assert P.expressed_attributes() == {e["attribute"] for e in doc["effects"]}


def test_expressed_and_unexpressed_partition_the_taxonomy():
    """Every attribute is either expressed or named as not yet expressed - the
    invariant attribute_effects.json claims for itself. If this ever fails, the
    pair check has been silently comparing over the wrong set."""
    doc = json.loads(
        (REPO / "data" / "attribute_effects.json").read_text(encoding="utf-8"))
    named_absent = set(doc["unexpressed_attributes"]["not_yet_expressed"])
    assert P.expressed_attributes() | named_absent == B.taxonomy_keys()
    assert not (P.expressed_attributes() & named_absent)


def test_unexpressed_attributes_are_not_used_as_combat_drivers(pair):
    """The plan's explicit prohibition: do not invent unexpressed Ringcraft or
    Showmanship as combat drivers. They may be declared - the cap needs a
    complete card - but they must stay near baseline, so that no reader can
    mistake them for the reason a fight went the way it did.
    """
    unexpressed = set(B.taxonomy_keys()) - P.expressed_attributes()
    for c in pair:
        for k in sorted(unexpressed):
            v = c["attributes"][k]
            assert abs(v) <= 30, (
                "%s sets unexpressed attribute %s to %d; an attribute that "
                "scales nothing must not carry a number that looks like it does"
                % (c["id"], k, v))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:26 UTC | END ]
