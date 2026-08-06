# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 07:10 UTC | START ]
"""Decision 0018 (gate G5): no bout runs under an implicit rulebook.

The defect this closes was not a wrong rule. It was an *undeclared* one: the
three-knockdown stoppage was canon, no professional rulebook has it, and it was
the termination condition in every measurement taken the week of 2026-08-03.
Nothing recorded that choice, so nothing could question it.

These tests hold the declaration in place: the default exists and is
professional, the arcade modifier still exists and still bites, every stream
says which rulebook it ran under, and the two rulesets actually produce
different fights — because a ruleset that changes nothing is decoration.
"""
import io
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import analyze_core_round as O  # noqa: E402

RULESETS = os.path.join(ROOT, "data", "rulesets")


def _load(rid):
    return json.load(io.open(os.path.join(RULESETS, rid + ".json"),
                             encoding="utf-8"))


def test_the_default_is_professional_and_has_no_knockdown_count_stoppage():
    """Rule 8 of the unified rules, made executable: there is no three-knockdown
    rule. A professional bout ends because a fighter cannot continue or because
    the cards said so."""
    r = _load("professional")
    assert r["three_knockdown_rule"] is False
    assert r["knockdowns_per_round_stoppage"] is None
    assert r["knockdowns_per_bout_stoppage"] is None
    assert r["standing_eight_count"] is False
    assert r["saved_by_the_bell"] is False
    assert r["mandatory_count_numbers"] == 8


def test_the_arcade_modifier_still_exists_and_still_bites():
    """Decision 0018 kept the rule rather than deleting it. What it may no
    longer do is silently define a professional fight."""
    r = _load("arcade_three_knockdown")
    assert r["three_knockdown_rule"] is True
    assert r["knockdowns_per_round_stoppage"] == 3
    assert r["knockdowns_per_bout_stoppage"] == 4


def test_the_contract_runs_under_the_professional_default():
    c = O.canon_pack()
    assert c["ruleset"]["id"] == "professional"
    assert c["max_per_round"] is None and c["max_per_bout"] is None


def test_every_stream_says_which_rulebook_it_ran_under():
    """A stream that does not name its rules cannot be compared with one that
    ran under different ones, and this project spent a week doing that."""
    head = O.expected_stream(4242, 1, with_floats=False).splitlines()[:16]
    fields = {l.split("=")[0] for l in head if l.startswith("H|")}
    assert "H|ruleset" in fields
    assert "H|ruleset_version" in fields
    assert "H|canon_ruleset" in fields


def test_the_legacy_condition_fields_still_echo_the_arcade_ruleset():
    """Sealed Phases N and K read condition_model's knockdown limits, so those
    fields cannot be removed. They must stay equal to the arcade ruleset, or
    the project is back to two authorities disagreeing silently."""
    cm = json.load(io.open(os.path.join(ROOT, "data", "condition_model.json"),
                           encoding="utf-8"))
    arcade = _load("arcade_three_knockdown")
    assert cm["knockdown"]["max_per_round"] == arcade["knockdowns_per_round_stoppage"]
    assert cm["knockdown"]["max_per_bout"] == arcade["knockdowns_per_bout_stoppage"]


def test_the_two_rulesets_produce_different_fights():
    """A ruleset that changes nothing is decoration.

    Same seed, same contract, different rulebook. Under the arcade rules this
    bout is stopped on the knockdown count; under the professional default the
    same fight keeps going. Restores the module afterwards so the rest of the
    suite runs under the default.
    """
    import importlib
    trailers = {}
    for rid in ("arcade_three_knockdown", "professional"):
        os.environ["UPPERCUT_RULESET"] = rid
        mod = importlib.reload(O)
        s = mod.expected_stream(4242, 3, with_floats=False)
        line = next(l for l in s.splitlines() if l.startswith("S|"))
        trailers[rid] = dict(kv.split("=", 1) for kv in line.split("|")[1:])
    os.environ.pop("UPPERCUT_RULESET", None)
    importlib.reload(O)

    assert trailers["arcade_three_knockdown"]["stopped"] == "1"
    assert trailers["professional"]["stopped"] == "0"
    assert int(trailers["professional"]["rounds"]) > \
        int(trailers["arcade_three_knockdown"]["rounds"])


def test_reaching_the_cards_is_not_mistaken_for_the_fight_being_right():
    """The finding this ruling produced, pinned so it cannot be forgotten.

    Under the professional default the contract reaches the cards. That is the
    invariant `decision_path_must_survive` satisfied for the first time — and it
    is NOT evidence the fight is right. The same measurement shows roughly 23
    knockdowns per round: the three-knockdown rule was not causing the problem,
    it was hiding it, and "0 of 24 reached the cards" and "23 knockdowns a
    round" were always the same fact seen from two sides.

    This test fails if the knockdown rate ever falls below 5 per round, which
    would mean the conversion work has landed and this warning can be retired
    along with the docstring.
    """
    s = O.expected_stream(4242, 3, with_floats=False)
    f = dict(kv.split("=", 1) for kv in
             next(l for l in s.splitlines() if l.startswith("S|")).split("|")[1:])
    per_round = int(f["knockdowns"]) / max(1, int(f["rounds"]))
    assert per_round > 5.0, (
        "knockdowns per round has fallen to %.1f. If that is real, the "
        "conversion problem has been fixed - update this test and the Phase O "
        "record in the same commit, because the warning it carries is no longer "
        "true." % per_round)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 07:10 UTC | END ]
