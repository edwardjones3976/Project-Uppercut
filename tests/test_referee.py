# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START ]
"""Referee-profile consumption (Rule 16, Decision 0012 slice item 2).

Three layers: the semantics laws (each proven non-vacuous by mutation), the
engine actually deriving enforcement from the profile, and the enforcement
actually reaching the fight - warnings, deductions on the card, break
patience, and the referee_judgement stoppage."""
import copy

import pytest

from tools.uppercut_sim import canon
from tools.uppercut_sim.engine import Bout
from tools.uppercut_sim.judge import Judge
from tools.uppercut_validate import referee_semantics as rs


def _doc():
    return copy.deepcopy(rs.load())


# ---- the semantics laws ---------------------------------------------------

def test_the_real_data_passes_every_law():
    doc = rs.load()
    for name, fn in rs.ALL_CHECKS:
        assert fn(doc) == [], name


def test_an_official_mapping_to_nothing_is_caught():
    d = _doc()
    d["referees"]["hana_mori"]["enforcement"]["clinch_tolerance"] = "imaginary"
    assert rs.check_every_official_resolves(d)


def test_words_contradicting_numbers_are_caught():
    d = _doc()
    for r in d["semantics"]["clinch"]["warning_after_entries_by_clinch_tolerance"]:
        if r["level"] == "high":
            r["value"] = 2          # 'high' tolerance warning before 'low'
    assert rs.check_words_order_the_numbers(d)


def test_a_drifted_neutral_is_caught():
    d = _doc()
    for r in d["semantics"]["clinch"]["warning_after_entries_by_clinch_tolerance"]:
        if r["level"] == "moderate":
            r["value"] = 5
    assert rs.check_neutral_is_the_incumbent(d)


def test_identical_officials_are_caught():
    d = _doc()
    for rid in d["referees"]:
        d["referees"][rid]["enforcement"].update(
            clinch_tolerance="moderate", warning_threshold="standard",
            deduction_threshold="standard", stoppage_disposition="standard")
    assert rs.check_officials_differ(d)


def test_an_inert_protective_threshold_is_caught():
    d = _doc()
    for r in d["semantics"]["stoppage"]["unanswered_after_knockdown_by_stoppage_disposition"]:
        if r["level"] == "protective":
            r["value"] = None
    assert rs.check_words_order_the_numbers(d)


# ---- the engine derives from the profile ----------------------------------

def test_the_default_official_is_the_neutral_calibration_point():
    bt = Bout(7, "rusher", "counterpuncher")
    assert bt.referee["id"] == "hana_mori"
    assert bt._ref_warning_entries == 6      # the incumbent constant
    assert bt._ref_break_patience == 90      # the incumbent constant
    assert bt._ref_stop_unanswered is None   # incumbent: count and limits only


def test_officials_derive_different_enforcement():
    strict = Bout(7, "rusher", "counterpuncher", referee="celeste_navarro")
    lax = Bout(7, "rusher", "counterpuncher", referee="elliot_ames")
    assert strict._ref_warning_entries < lax._ref_warning_entries
    assert strict._ref_break_patience < lax._ref_break_patience


def test_the_official_is_disclosed_at_the_opening_bell():
    bt = Bout(7, "rusher", "counterpuncher", rounds=1,
              referee="thomas_baines")
    log = bt.run()
    assert log[0]["type"] == "bout_start"
    assert log[0]["payload"]["referee"] == "thomas_baines"


# ---- enforcement reaches the fight ----------------------------------------

def _clinch_n(bt: Bout, n: int) -> None:
    bt.band = 0                              # in clinch range
    a, b = bt.fighters
    for _ in range(n):
        bt.clinch(a, b)


def test_the_strict_official_walks_the_ladder():
    """celeste: warnings from entry 3, a deduction each 2 past it."""
    bt = Bout(7, "rusher", "counterpuncher", referee="celeste_navarro")
    _clinch_n(bt, 5)
    warns = [e for e in bt.log if e["type"] == "referee_warning"]
    dedns = [e for e in bt.log if e["type"] == "referee_deduction"]
    assert [w["payload"]["entries"] for w in warns] == [3, 4, 5]
    assert [d["payload"]["entries"] for d in dedns] == [5]
    assert dedns[0]["payload"]["official"] == "celeste_navarro"
    assert dedns[0]["explains"], "a deduction must be replay-explainable (Rule 16)"


def test_the_neutral_official_matches_the_incumbent_ladder():
    bt = Bout(7, "rusher", "counterpuncher")
    _clinch_n(bt, 5)
    assert [e for e in bt.log if e["type"] == "referee_warning"] == []
    assert [e for e in bt.log if e["type"] == "referee_deduction"] == []


def test_the_deduction_reaches_the_sealed_card():
    bt = Bout(7, "rusher", "counterpuncher", referee="celeste_navarro")
    _clinch_n(bt, 5)                         # one deduction against A
    bt._score_round()
    bt._final_card()
    assert bt.decision() == "B"
    cards = bt._judge.sealed_cards()         # harness read, after the bell
    assert cards == {"A": 9.0, "B": 10.0}


def test_a_deduction_costs_a_point_in_the_judge_arithmetic():
    j = Judge(("A", "B"))
    j.witness({"type": "deduction", "fighter": "A"})
    j.seal_round()
    j.seal_final()
    assert j.sealed_cards() == {"A": 9.0, "B": 10.0}


def test_the_protective_official_stops_on_observable_evidence():
    """nkiru: a fighter down once, absorbing a sixth unanswered solid punch."""
    bt = Bout(7, "rusher", "counterpuncher", referee="nkiru_okafor")
    a, b = bt.fighters
    b.knockdowns = 1
    bt._unanswered[b.name] = 5
    bt.band = 2
    jab = canon.punches()["jab_lead"]
    bt._apply(a, b, jab, "solid", 0.9, 0)
    assert bt.stopped and bt.stop_reason == "referee_judgement"
    stop = [e for e in bt.log if e["type"] == "stoppage"][-1]
    assert stop["payload"]["official"] == "nkiru_okafor"
    assert stop["payload"]["unanswered"] == 6
    assert stop["explains"], "a stoppage must be replay-explainable (Rule 16)"
    bt._final_card()
    assert bt.decision() == "A"              # the waved-off fighter loses


def test_the_neutral_official_never_stops_on_judgement():
    bt = Bout(7, "rusher", "counterpuncher")
    a, b = bt.fighters
    b.knockdowns = 1
    bt._unanswered[b.name] = 50
    bt.band = 2
    bt._apply(a, b, canon.punches()["jab_lead"], "solid", 0.9, 0)
    assert not bt.stopped


def test_answering_back_resets_the_ledger():
    bt = Bout(7, "rusher", "counterpuncher", referee="nkiru_okafor")
    a, b = bt.fighters
    bt._unanswered[b.name] = 5
    bt.band = 2
    bt._apply(b, a, canon.punches()["jab_lead"], "brushed", 0.1, 0)   # b lands anything
    assert bt._unanswered[b.name] == 0
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | END ]
