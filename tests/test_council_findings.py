# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:19 UTC | START ]
"""The specialist council's findings, as executable facts rather than prose.

WHY THESE ASSERT THE DEFECT. Every test here pins a state the council found
WRONG. That is deliberate and it is this repository's established pattern -
`test_region_is_currently_unreachable_from_any_authored_punch` says it best:
"A FINDING, not a gap in the tests, and it is asserted so it announces itself
the day it changes." A finding written only in a review document is a claim
somebody has to remember. A finding written as a test is a claim the suite
defends until someone deliberately retires it.

So each test below fails the day its defect is FIXED, and the docstring says
what to do then: delete the test and assert the correct behaviour in its
place. None of them is a regression guard. All of them are countdowns.

The council report is docs/reviews/2026-08-09-specialist-council-first-bell.md.
Its harness disclaimer applies: the specialists are constructed reviewers, not
evidence. What makes the findings below trustworthy is not that a persona said
them - it is that each one was mechanically re-verified against this code, and
these are those verifications.
"""
import io
import json
import os

import pytest

from tools.uppercut_evade import core as EVADE
from tools.uppercut_integrated import contract as C
from tools.uppercut_integrated import judging as J
from tools.uppercut_integrated import policy as P
from tools.uppercut_integrated import resolution as RES
from tools.uppercut_integrated.bout import IntegratedBout
from tools.uppercut_range import core as RANGE

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def rp():
    return RANGE.range_pack()


@pytest.fixture(scope="module")
def cp():
    return RES.condition_pack()


# ------------------------------------------------ the two range authorities --

# The exact disagreement, pinned move by move. Written out rather than computed
# so that a fix which changes ONE of them is a visible, readable diff instead of
# a count going down.
BAND_DISAGREEMENTS = (
    ("jab_lead", "outside", "mid"),
    ("cross_rear", "outside", "mid"),
    ("hook_lead", "mid", "inside"),
    ("body_straight_rear", "inside", "mid"),
    ("uppercut_lead", "clinch", "inside"),
    ("uppercut_rear", "clinch", "inside"),
    ("body_hook_lead", "clinch", "inside"),
)


def test_the_policy_and_canon_disagree_about_where_a_punch_is_legal(rp):
    """THE council's first finding, and the whole cause of one failure mode.

    `policy.BY_BAND` is a hand-authored Python table of which punches a fighter
    may choose from which band. `data/moves/*.range_band` authors the same rule
    and `RANGE.in_band` gates on it. They disagree seven ways, and canon has
    already named the single authority: `punch_model.range_gate.band_source`
    points at the movement model, so the policy's table is an unauthored second
    opinion about a rule canon says has one source. Same class as the eight
    copies of the LCG constants and the copied phase formulas - both deleted.

    WHEN THIS FAILS: the duplication is being removed. Delete this test and
    assert the invariant instead - every move the policy can offer in a band is
    legal in that band. That invariant is the fix.
    """
    observed = []
    for band, moves in sorted(P.BY_BAND.items()):
        for move in moves:
            canon = rp["move_band"].get(move, "<absent from canon>")
            if canon != band:
                observed.append((move, band, canon))
    assert sorted(observed) == sorted(BAND_DISAGREEMENTS), (
        "the policy/canon band disagreement changed. Expected %r, observed %r. "
        "If it shrank, retire the entries that were fixed; if it grew, a new "
        "second opinion was just written."
        % (sorted(BAND_DISAGREEMENTS), sorted(observed)))


def test_two_of_the_four_bands_cannot_produce_a_legal_punch(rp):
    """The consequence, stated as the fight experiences it.

    From `outside` and from `clinch`, EVERY punch the policy can choose is
    refused by the range gate. That is why two mirrored outside fighters threw
    3,174 punches across twelve rounds and landed none of them: not a decision
    they made, a band in which offence does not exist. The owner's protected
    art - hitting without getting hit - is not currently reachable, and
    Decision 0030 is not what prevents it.

    WHEN THIS FAILS: offence exists at those bands. Retire the test.
    """
    legal = {}
    for band, moves in sorted(P.BY_BAND.items()):
        legal[band] = sum(1 for m in moves if RANGE.in_band(rp, m, band))
    assert legal.get("outside") == 0, legal
    assert legal.get("clinch") == 0, legal
    # And the two that DO work, so a regression in them is also visible.
    assert legal.get("mid") == 3 and legal.get("inside") == 5, legal


def test_three_selectable_punches_never_enter_the_world():
    """A fighter is charged for punches that never fly.

    The policy can select eight punches; `contract.PUNCHES` declares five. The
    other three are charged their stamina and their recovery, increment
    `punches_thrown`, are given a hardcoded 14-tick commitment - and are never
    assigned to `me.punch`, so they never resolve, never whiff, never void. In
    a codebase that fails closed everywhere else, an unknown move id is handed
    an invented window instead of an exception.

    WHEN THIS FAILS: the vocabularies were reconciled. Retire the test and
    assert the punch ledger closes instead.
    """
    selectable = sorted({m for moves in P.BY_BAND.values() for m in moves})
    ghosts = [m for m in selectable if m not in C.PUNCHES]
    assert ghosts == ["body_hook_lead", "hook_rear", "uppercut_lead"], ghosts


# ------------------------------------------------- one punch ends every fight --

def test_exactly_one_punch_in_the_bout_can_cause_a_knockdown(cp):
    """`jaw_chin` is the only knockdown-relevant region and one punch reaches it.

    Every jab, cross, hook and body shot contributes exactly zero accumulated
    knockdown pressure. Roughly 150 knockdowns across thirty measured fights
    all came from one move id.

    The sharper half is WHERE that authority lives: the region is read as
    `target_regions[0]` - the first element of a JSON array - so reordering
    `hook_lead`'s ["head", "jaw_chin"] would change which punches can end a
    fight. Decision 0026 spent a whole ruling removing array order from RNG
    ownership; it is still deciding this.

    WHEN THIS FAILS: the Director authored more knockdown-relevant regions, or
    the region stopped being an array index. Retire and assert the new shape.
    """
    ec = EVADE.evade_pack(C.REGIONS)
    relevant = sorted(r for r, spec in cp["regions"].items()
                      if spec["knockdown_relevant"])
    reaching = [m for m in sorted(C.PUNCHES) if ec["region"].get(m) in relevant]
    assert relevant == ["jaw_chin"], relevant
    assert reaching == ["uppercut_rear"], reaching


# ---------------------------------------------------- rules nobody is reading --

def test_no_ruleset_file_is_in_the_integrated_contract():
    """Every fight so far ended on a rule the declared ruleset switches off.

    `data/rulesets/professional.json` authors `three_knockdown_rule: false` and
    both knockdown-stoppage counts as null. No ruleset file is in `C.CANON`, so
    the bout reads `max_per_round`/`max_per_bout` out of `condition_model.json`
    instead - and thirty of thirty fights ended on exactly that. Decision 0019
    (versioned rulesets) is currently decorative, and
    `condition_model.knockdown.decision_path_must_survive` is contradicted by
    every ending on record.

    WHEN THIS FAILS: a ruleset entered the contract. Retire the test, and note
    that the contract version and the integrated stream hash both move with it.
    """
    assert not [p for p in C.CANON if "ruleset" in p], C.CANON
    prof = json.load(io.open(os.path.join(REPO, "data/rulesets/professional.json"),
                             encoding="utf-8"))
    assert prof["three_knockdown_rule"] is False
    assert prof["knockdowns_per_bout_stoppage"] is None
    assert prof["knockdowns_per_round_stoppage"] is None


# ------------------------------------------------------------ the scorecards --

def test_two_judges_score_walking_forward_far_harder_than_punching():
    """The units are not commensurate, and the docstring says the opposite.

    `evidence["pressed"]` accumulates q10000 reach units; `landed` is a punch
    count; `score_round` weights them as if they were the same kind of number.
    A landed punch is worth 1 to every judge. One capped advancing tick is
    worth 140 to Bello and 560 to Reyes. Measured in one real round of seed
    4245: landed 116 against pressed 4,200.

    The panel therefore has one degree of freedom - two footwork judges and one
    punching judge - rather than three readings of one fight.

    WHEN THIS FAILS: the units were reconciled. Retire the test. Note the
    referee's separate ruling, which survives the fix: a CORRECT `pressed` is
    still the wrong proxy, because effective aggression's defining word is
    effective, and a fighter who walks forward and misses is scored against.
    """
    weights = dict(J.JUDGE_STYLES)
    one_punch = {j: (1 * w["landed"]) // 10000 for j, w in weights.items()}
    one_tick = {j: (1400 * w["pressed"]) // 10000 for j, w in weights.items()}
    assert set(one_punch.values()) == {1}, one_punch
    assert one_tick["marta_reyes"] == 560 and one_tick["aisha_bello"] == 140, \
        one_tick
    assert one_tick["tomasz_wojcik"] == 0, one_tick


def test_the_round_winner_can_be_scored_below_ten():
    """A card this panel can produce is not a legal ten-point-must card.

    The "must" in ten-point must is the rule that the round WINNER must receive
    ten. Here the knockdown deduction is applied to both fighters, so a fighter
    who wins a round 20 landed to 1, having been dropped twice, scores 8 - and
    the man he outlanded twenty to one scores 9. The round inverts.

    It has never fired in a real fight only because no fight has reached the
    cards with a knockdown in it, and First Bell's other half is a valid
    decision. The `max(7, ...)` floor is invented; no canon file authors it.

    WHEN THIS FAILS: the deduction moved to the loser. Retire this test and
    assert the ten-point must directly - every scored round gives the winner 10.
    """
    panel = J.JudgingPanel(["a", "b"])
    panel.score_round(1,
                      {"a": {"landed": 20, "denied": 0, "pressed": 0},
                       "b": {"landed": 1, "denied": 0, "pressed": 0}},
                      {"a": 2, "b": 0})
    panel.close()
    for judge, card in panel.verdict()["cards"].items():
        assert card["rounds"] == [(1, 8, 9)], (judge, card["rounds"])


# ------------------------------------------------- nothing makes a man think --

def test_the_only_brake_in_the_policy_is_unreachable():
    """`consecutive_failed_attacks >= 2` is the sole mechanism by which any
    fighter in this game reconsiders anything, and it cannot happen.

    `committed_to()` zeroes the counter on every throw, and a fighter can hold
    only one punch in the air, so the counter oscillates 0 -> 1 -> 0 forever.
    `R_AVOID_OVERCOMMIT` has never fired in any fight. The fight therefore has
    no negative feedback loop at all - which is worth holding next to the
    twelve-round stalemate, where nothing ever caused either fighter to change
    what he was doing across 129,600 ticks.

    WHEN THIS FAILS: the brake became reachable. Retire and assert it engages.
    """
    bout = IntegratedBout(seed=4243)
    peak = 0
    for _ in range(12000):
        bout.step()
        peak = max(peak, max(f.failed_attacks for f in bout.fighters))
        if bout.result:
            break
    assert peak < 2, peak


def test_a_fighter_never_learns_that_he_is_hurt():
    """Damage lives on the bout; the fighter is never told.

    `_contact` writes into `self.condition[foe.id]` on the bout and never back
    into the fighter, so `FighterState.hurt` and `damaged_regions` keep their
    constructor values through a complete fight. The policy branch that reads
    them is dead code, and so is the `hurt` term in the initiative calculation.
    Doubly dead: the branch tests for the literal string "body", and no canon
    region is named "body".

    WHEN THIS FAILS: condition reached the fighter. Retire the test.
    """
    bout = IntegratedBout(seed=4242)
    bout.run(13000)
    assert all(not f.hurt and not f.damaged_regions for f in bout.fighters), \
        [(f.id, f.hurt, f.damaged_regions) for f in bout.fighters]


def test_the_ropes_are_an_absorbing_state(rp):
    """A fighter whose back reaches the ropes has no action that moves him.

    Retreat is scaled to zero at the ropes (`retreat_mult` is 0), and the
    policy's rope-escape answer is the lateral step, whose step delta is also
    zero. Rope trapping is not a dominant strategy; it is terminal. This is
    confirmed by construction rather than by observation, which is why it is
    asserted against the range pack rather than against a fight.

    WHEN THIS FAILS: either the lateral step acquired a displacement (the axis
    went 2D) or the rope multiplier stopped being zero. Both are good news and
    both retire this test - note that a non-zero retreat multiplier also
    un-masks the one floor-division site that forks Python and C++.
    """
    assert RANGE.step_delta(rp, "step_lateral") == 0
    assert rp["retreat_mult"] == 0
    assert RANGE.step_delta(rp, "step_in") != 0
    assert RANGE.step_delta(rp, "step_out") != 0


# ------------------------------------------------------ what verification killed --

def test_a_stoppage_is_never_overwritten_by_a_second_finish():
    """THE CLAIM THAT DIED, kept because a review that reports only its
    confirmed findings is not a review.

    The architect reasoned that `_resolve_punches` does not break when
    `self.result` is set, so a second punch resolving in the same tick could
    knock a fighter down and call `_stop` again, overwriting the winner. It is
    a good reading of the code and it is wrong: twenty consecutive fights emit
    exactly one F row each. The guard that saves it is the `if self.result:
    return` immediately after `_resolve_punches` in `step()`, plus `_knockdown`
    clearing both fighters' in-flight punches before any second resolution.

    This one IS a regression guard - the only one in this file - because the
    property it asserts is the correct behaviour rather than a defect.
    """
    for seed in range(4242, 4252):
        bout = IntegratedBout(seed=seed)
        bout.run_fight()
        finishes = [r for r in bout.rows if r.startswith("F|")]
        assert len(finishes) == 1, (seed, finishes)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:19 UTC | END ]
