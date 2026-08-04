# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START ]
"""The Judge subsystem and its boundary (Rule 3, Decision 0012 slice item 1).

Two layers: the judge's own behaviour (ten-point-must, sealing, vocabulary),
and the source-relation checks in tools/uppercut_validate/judge_boundary.py -
each proven non-vacuous by a synthetic violation, then proven green on the
real tree."""
import pytest

from tools.uppercut_sim.engine import Bout
from tools.uppercut_sim.judge import Judge, SealedCardsError
from tools.uppercut_validate import judge_boundary as jb


# ---- the judge itself ----------------------------------------------------

def _final(j):
    j.seal_final()
    return j.sealed_cards()


def test_an_even_round_is_ten_ten():
    j = Judge(("A", "B"))
    j.seal_round()
    assert _final(j) == {"A": 10.0, "B": 10.0}


def test_effective_offence_wins_the_round_ten_nine():
    j = Judge(("A", "B"))
    j.witness({"type": "punch_landed", "scorer": "A", "force": 0.8})
    j.witness({"type": "punch_landed", "scorer": "B", "force": 0.3})
    j.witness({"type": "punch_landed", "scorer": "B", "force": 0.3})
    j.seal_round()
    assert _final(j) == {"A": 10.0, "B": 9.0}


def test_a_knockdown_costs_a_point_on_top_of_the_round():
    j = Judge(("A", "B"))
    j.witness({"type": "punch_landed", "scorer": "A", "force": 1.0})
    j.witness({"type": "knockdown", "fighter": "B"})
    j.seal_round()
    assert _final(j) == {"A": 10.0, "B": 8.0}


def test_rounds_are_scored_alone_not_bout_to_date():
    """Correction 1, kept: an early lead must not re-win later rounds."""
    j = Judge(("A", "B"))
    j.witness({"type": "punch_landed", "scorer": "A", "force": 5.0})
    j.seal_round()
    j.witness({"type": "punch_landed", "scorer": "B", "force": 0.1})
    j.seal_round()
    assert _final(j) == {"A": 19.0, "B": 19.0}


def test_cards_are_sealed_until_the_final_bell():
    j = Judge(("A", "B"))
    j.seal_round()
    with pytest.raises(SealedCardsError):
        j.sealed_cards()


def test_no_fact_is_witnessed_after_the_official_reading():
    j = Judge(("A", "B"))
    j.seal_final()
    with pytest.raises(SealedCardsError):
        j.witness({"type": "punch_landed", "scorer": "A", "force": 1.0})


def test_the_reading_is_a_copy_not_the_cards():
    j = Judge(("A", "B"))
    j.seal_final()
    reading = j.sealed_cards()
    reading["A"] = 999.0
    assert j.sealed_cards()["A"] == 0.0


def test_the_fact_vocabulary_is_a_contract():
    j = Judge(("A", "B"))
    with pytest.raises(ValueError):
        j.witness({"type": "bribe", "scorer": "A"})
    with pytest.raises(ValueError):
        j.witness({"type": "punch_landed", "scorer": "A", "force": 1.0,
                   "stamina": 0.2})


def test_the_bout_verdict_raises_before_the_final_bell():
    """Rule 3 at the integration level: even the harness cannot read a card
    from a bout that has not finished."""
    bt = Bout(5, "rusher", "counterpuncher")
    with pytest.raises(SealedCardsError):
        bt.decision()


def test_the_verdict_agrees_with_the_sealed_cards():
    bt = Bout(1234, "rusher", "counterpuncher")
    bt.run()
    cards = bt._judge.sealed_cards()          # test harness, after the bell
    d = bt.decision()
    if not bt.stopped and cards["A"] != cards["B"]:
        assert d == ("A" if cards["A"] > cards["B"] else "B")


# ---- the boundary, as checked relations ----------------------------------

def test_the_real_tree_passes_every_boundary_check():
    doc = jb.load()
    for name, fn in jb.ALL_CHECKS:
        assert fn(doc) == [], name


def test_an_importing_judge_is_caught():
    bad = {"judge_source": "import random\n", "engine_source": ""}
    assert jb.check_judge_imports(bad)
    bad = {"judge_source": "from . import canon\n", "engine_source": ""}
    assert jb.check_judge_imports(bad)


def test_a_judge_naming_ring_state_is_caught():
    bad = {"judge_source": "def peek(f):\n    return f.stamina\n",
           "engine_source": ""}
    assert jb.check_judge_names(bad)


def test_a_fact_outside_the_vocabulary_is_caught():
    bad = {"judge_source": "",
           "engine_source": "self._judge.witness({'type': 'bribe'})\n"}
    assert any("FACT_TYPES" in e for e in jb.check_witness_vocabulary(bad))
    bad = {"judge_source": "",
           "engine_source": "self._judge.witness({'type': 'punch_landed', "
                            "'stamina': f.stamina})\n"}
    assert any("FACT_KEYS" in e for e in jb.check_witness_vocabulary(bad))
    bad = {"judge_source": "", "engine_source": "self._judge.witness(obs)\n"}
    assert any("dict literal" in e for e in jb.check_witness_vocabulary(bad))


def test_an_engine_showing_the_judge_nothing_is_caught():
    bad = {"judge_source": "", "engine_source": "x = 1\n"}
    assert any("vacuously" in e for e in jb.check_witness_vocabulary(bad))


def test_a_card_read_outside_decision_is_caught():
    bad = {"judge_source": "",
           "engine_source": ("def _run_round(self):\n"
                             "    return self._judge.sealed_cards()\n")}
    assert any("_run_round" in e for e in jb.check_sealed_reads(bad))


def test_a_reach_into_the_judge_is_caught():
    bad = {"judge_source": "",
           "engine_source": "def f(self):\n    return self._judge._cards\n"}
    assert jb.check_judge_privacy(bad)


def test_an_aliased_or_travelling_judge_is_caught():
    bad = {"judge_source": "",
           "engine_source": "def f(self):\n    j = self._judge\n"}
    assert any("aliased" in e for e in jb.check_judge_privacy(bad))
    bad = {"judge_source": "",
           "engine_source": "def f(self):\n    leak(self._judge)\n"}
    assert any("argument" in e for e in jb.check_judge_privacy(bad))
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | END ]
