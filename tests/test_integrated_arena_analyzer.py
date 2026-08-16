# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 09:55 UTC | START ]
"""Mutation-proving for the integrated arena's coherence checker.

A checker that has never caught anything is a claim, not a check. Every
assertion `analyze_integrated_arena` makes is exercised here by breaking a
stream in exactly that way and requiring the break to be reported. The pinned
streams are used as the healthy body; the mutations are the disease.

This file deliberately does NOT assert anything about whether the fight is good
boxing - not the connect rate, not the knockdown count, not the intent mix.
Those are Director judgements (Decision 0040 R3 holds that neither current
outcome is authentic), and a test that encoded today's numbers as correct would
convert an open question into a passing gate.
"""
import io
import os

import pytest

from tools.engine import analyze_integrated_arena as A
from tools.engine import prove_integrated_arena as P

GOLDEN = P.GOLDEN
PINS = [P.golden_path(seed, ticks) for seed, ticks in P.RUNS]


# --------------------------------------------------------------- the pins --

def test_every_pinned_run_has_a_stream_on_disk():
    missing = [os.path.basename(p) for p in PINS if not os.path.exists(p)]
    assert not missing, (
        "prove_integrated_arena pins these runs but the streams are not "
        "committed: %s" % ", ".join(missing))


@pytest.mark.parametrize("path", PINS, ids=[os.path.basename(p) for p in PINS])
def test_the_pinned_stream_is_a_coherent_fight(path):
    report = A.analyse(path)
    assert not report["errors"], (
        "%s is pinned but contradicts itself:\n  %s"
        % (os.path.basename(path), "\n  ".join(report["errors"])))


@pytest.mark.parametrize("path", PINS, ids=[os.path.basename(p) for p in PINS])
def test_the_pin_carries_no_machine_path(path):
    """A pin with an absolute path in it proves only that the fight was run on
    one laptop. Issue #14's Windows lane checks out somewhere else. Since
    2026-08-16 the authoritative header carries no repo field at all - this
    fails if one ever comes back, normalised or otherwise."""
    head = io.open(path, "r", encoding="utf-8", newline="").read().splitlines()[0]
    assert "repo=" not in head, (
        "%s: the header records its checkout again: %r"
        % (os.path.basename(path), head))
    assert ":\\" not in head and ":/" not in head, (
        "%s carries an absolute path: %r" % (os.path.basename(path), head))


def test_the_pinned_set_covers_a_round_that_ends_mid_flight():
    """The short run earns its place by stopping with a punch unresolved. If
    that stops being true, the trailer's punch accounting is untested."""
    reports = [A.analyse(p) for p in PINS]
    assert any(r["counts"]["unresolved_punches"] > 0 for r in reports), (
        "no pinned run ends with a punch in flight, so the trailer's "
        "`punches` cross-check is never exercised against a nonzero remainder")


# ------------------------------------------------------------- a fixture ---

def minimal(rows=None, trailer=None, verdict=None):
    """The smallest stream the checker calls coherent. Built by hand rather
    than trimmed from a pin so that a mutation test cannot pass because of
    something incidental 9000 rows away."""
    body = rows if rows is not None else [
        "D|0|red_corner|Attack|jab_lead|PUNISH_RECOVERY",
        "A|0|0|jab_lead",
        "D|1|blue_corner|Rest||RECOVER_WIND",
        "A|1|1|rest",
        "P|2|0|jab_lead|landed|force=5000",
    ]
    v = verdict if verdict is not None else "V|decision|0|10|9|0|0"
    body = list(body) + ([v] if v else [])
    s = trailer if trailer is not None else (
        "S|rows=%d|fnv=0000000000000000|ticks=10|punches=1|landed=1|"
        "result=decision|cards=10-9|kd=0-0" % len(body))
    return "\n".join([
        "H|phase=INTEGRATED_1R|contract=uppercut-integrated-v3|seed=1|ticks=10",
        "H|cards=test_alpha,test_beta",
    ] + body + ([s] if s else [])) + "\n"


def errors_of(text):
    return A.analyse(text)["errors"]


def test_the_fixture_itself_is_coherent():
    """Every mutation below is only meaningful because this passes."""
    assert not errors_of(minimal())


def complains_about(text, needle):
    errs = errors_of(text)
    assert any(needle in e for e in errs), (
        "expected a complaint containing %r, got: %s" % (needle, errs or "none"))


# ------------------------------------------------------------- mutations ---

def test_a_foreign_phase_is_caught():
    complains_about(minimal().replace("phase=INTEGRATED_1R", "phase=Q"), "phase")


def test_a_foreign_contract_is_caught():
    complains_about(
        minimal().replace("contract=uppercut-integrated-v3",
                          "contract=uppercut-integrated-v2"), "contract")


def test_two_fighters_on_the_same_card_is_caught():
    complains_about(minimal().replace("cards=test_alpha,test_beta",
                                      "cards=test_alpha,test_alpha"),
                    "same card")


def test_a_tick_running_backwards_is_caught():
    complains_about(minimal(rows=[
        "D|0|red_corner|Rest||RECOVER_WIND",
        "A|0|0|rest",
        "D|5|blue_corner|Rest||RECOVER_WIND",
        "A|5|1|rest",
        "D|3|red_corner|Rest||RECOVER_WIND",
        "A|3|0|rest",
    ], trailer="S|rows=7|fnv=0|ticks=10|punches=0|landed=0|result=decision|"
               "cards=10-9|kd=0-0"), "backwards")


def test_a_punch_that_was_never_thrown_is_caught():
    complains_about(minimal(rows=[
        "D|0|red_corner|Attack|jab_lead|PUNISH_RECOVERY",
        "A|0|0|jab_lead",
        "P|2|0|jab_lead|landed|force=5000",
        "P|3|0|cross_rear|landed|force=5000",
    ], trailer="S|rows=5|fnv=0|ticks=10|punches=2|landed=2|result=decision|"
               "cards=10-9|kd=0-0"), "never thrown")


def test_an_action_with_no_decision_behind_it_is_caught():
    complains_about(minimal(rows=[
        "D|0|red_corner|Attack|jab_lead|PUNISH_RECOVERY",
        "A|4|0|jab_lead",
        "P|6|0|jab_lead|landed|force=5000",
    ], trailer="S|rows=4|fnv=0|ticks=10|punches=1|landed=1|result=decision|"
               "cards=10-9|kd=0-0"), "no decision at that tick")


def test_a_decision_with_no_reason_code_is_caught():
    complains_about(minimal().replace("|PUNISH_RECOVERY", "|"), "no reason code")


def test_a_landed_punch_without_force_is_caught():
    complains_about(minimal().replace("|landed|force=5000", "|landed"), "force")


def test_a_landed_punch_with_no_force_behind_it_is_caught():
    complains_about(minimal().replace("force=5000", "force=0"), "force 0")


def test_an_unknown_outcome_is_caught():
    complains_about(minimal().replace("|landed|force=5000", "|blocked"),
                    "unknown punch outcome")


def test_an_unknown_row_type_is_caught():
    complains_about(minimal().replace("A|0|0|jab_lead", "Z|0|0|jab_lead"),
                    "unknown row type")


def test_a_miscounted_landing_is_caught():
    complains_about(minimal(trailer="S|rows=6|fnv=0|ticks=10|punches=1|landed=2|"
                                    "result=decision|cards=10-9|kd=0-0"),
                    "landed=2")


def test_a_miscounted_punch_is_caught():
    complains_about(minimal(trailer="S|rows=6|fnv=0|ticks=10|punches=9|landed=1|"
                                    "result=decision|cards=10-9|kd=0-0"),
                    "punches=9")


def test_a_miscounted_row_total_is_caught():
    complains_about(minimal(trailer="S|rows=99|fnv=0|ticks=10|punches=1|landed=1|"
                                    "result=decision|cards=10-9|kd=0-0"),
                    "rows=99")


def test_a_stream_that_does_not_end_with_its_trailer_is_caught():
    complains_about(minimal(trailer="") , "does not end with a trailer")


def test_a_decision_with_no_verdict_row_is_caught():
    complains_about(minimal(verdict=""), "no V row")


def test_a_verdict_naming_the_wrong_winner_is_caught():
    complains_about(minimal(verdict="V|decision|1|10|9|0|0"), "names winner 1")


def test_a_verdict_that_disagrees_with_the_trailer_is_caught():
    complains_about(minimal(verdict="V|decision|0|10|8|0|0"), "trailer says")


def test_a_round_winner_who_did_not_score_ten_is_caught():
    """10-point must: the round winner takes 10 unless they were dropped."""
    complains_about(minimal(
        verdict="V|decision|0|9|8|0|0",
        trailer="S|rows=6|fnv=0|ticks=10|punches=1|landed=1|result=decision|"
                "cards=9-8|kd=0-0"), "10-point-must")


def test_a_verdict_whose_knockdowns_are_not_in_the_stream_is_caught():
    complains_about(minimal(
        verdict="V|decision|0|10|8|0|1",
        trailer="S|rows=6|fnv=0|ticks=10|punches=1|landed=1|result=decision|"
                "cards=10-8|kd=0-0"), "knockdowns")


# ------------------------------------------------- the canvas and the count --

def down_and_up(count_rows=None, rise="N|550|rise|fighter=1"):
    counts = count_rows if count_rows is not None else [
        "N|%d|count|%d|fighter=1" % (10 + n * 60, n) for n in range(1, 9)]
    rows = [
        "D|0|red_corner|Attack|cross_rear|PUNISH_RECOVERY",
        "A|0|0|cross_rear",
        "P|2|0|cross_rear|landed|force=9000",
        "K|2|1|pressure=9000|threshold=5700|round_kd=1|bout_kd=1",
    ] + counts + ([rise] if rise else [])
    n = len(rows) + 1  # + the V row appended by minimal()
    return minimal(
        rows=rows,
        verdict="V|decision|0|10|8|0|1",
        trailer="S|rows=%d|fnv=0|ticks=200|punches=1|landed=1|result=decision|"
                "cards=10-8|kd=0-1" % n)


def test_a_clean_knockdown_and_count_is_coherent():
    assert not errors_of(down_and_up())


def test_a_knockdown_below_its_own_threshold_is_caught():
    complains_about(
        down_and_up().replace("pressure=9000|threshold=5700",
                              "pressure=100|threshold=5700"),
        "below its own threshold")


def test_a_count_that_skips_a_number_is_caught():
    complains_about(down_and_up(count_rows=[
        "N|70|count|1|fighter=1", "N|130|count|3|fighter=1",
        "N|190|count|4|fighter=1", "N|250|count|5|fighter=1",
        "N|310|count|6|fighter=1", "N|370|count|7|fighter=1",
        "N|430|count|8|fighter=1",
    ]), "the count goes")


def test_rising_before_the_mandatory_eight_is_caught():
    complains_about(down_and_up(count_rows=[
        "N|70|count|1|fighter=1", "N|130|count|2|fighter=1",
    ]), "before the mandatory")


def test_a_fighter_left_on_the_canvas_is_caught():
    complains_about(down_and_up(rise=""), "on the canvas")


def test_a_count_with_nobody_down_is_caught():
    complains_about(minimal(rows=[
        "D|0|red_corner|Rest||RECOVER_WIND",
        "A|0|0|rest",
        "N|10|count|1|fighter=1",
    ], trailer="S|rows=4|fnv=0|ticks=10|punches=0|landed=0|result=decision|"
               "cards=10-9|kd=0-0"), "nobody down")


def test_a_second_knockdown_during_a_count_is_caught():
    text = down_and_up().replace(
        "N|70|count|1|fighter=1",
        "K|70|1|pressure=9000|threshold=5700|round_kd=2|bout_kd=2")
    complains_about(text, "already being counted")


# ----------------------------------------------------------- the describer --

def test_every_row_type_renders_as_a_sentence():
    """A diff nobody can read is a hash with extra steps, so the describer has
    to cover the grammar - including the rows the pinned fights never reach."""
    for row in ["D|4|red_corner|Attack|jab_lead|PUNISH_RECOVERY",
                "A|4|0|jab_lead",
                "P|6|0|jab_lead|landed|force=5650",
                "P|6|0|jab_lead|evaded",
                "P|6|0|jab_lead|whiff_band",
                "K|6|1|pressure=9000|threshold=5700|round_kd=1|bout_kd=1",
                "N|70|count|1|fighter=1",
                "N|140|rise|fighter=1",
                "V|decision|0|10|9|0|0"]:
        said = A.describe(row)
        assert said != row and said, "describe() passed %r straight through" % row
        assert "|" not in said, "describe() left field separators in %r" % said
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 09:55 UTC | END ]
