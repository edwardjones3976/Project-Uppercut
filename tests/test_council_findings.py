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


def _stream():
    """A legitimate fighter-local policy stream, the only kind decide() takes."""
    from tools.uppercut_integrated import rng as R
    return R.BoutRng(4242, C.CONTRACT, C.DEFAULT_PARTICIPANTS) \
        .stream("policy_intent", C.DEFAULT_PARTICIPANTS[0])


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


def test_the_chooser_and_the_gate_are_one_derivation(rp):
    """THE COUNTDOWN FIRED, 2026-08-09. This test's previous body pinned the
    seven-way disagreement between `policy.BY_BAND` and canon's `range_band`,
    and its docstring said: when this fails, the duplication is being removed -
    delete the test and assert the invariant instead. The duplication was
    removed (`BY_BAND` is deleted; `RANGE.throwable_from` is the single
    authority) and this is that invariant.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-09 09:30 UTC | retired the
      countdown; the pinned disagreement list above it is kept as history. ]

    The invariant is a coherence tautology by construction - the chooser CALLS
    the gate rather than agreeing with it - and this asserts it end to end:
    every punch the authority offers in a band passes the gate in that band,
    nothing outside the declared vocabulary is ever offered, and every punch
    in the vocabulary is reachable from some band.
    """
    seen = set()
    for band in RANGE.band_order(rp):
        legal = RANGE.throwable_from(rp, band, C.PUNCHES)
        for move in legal:
            assert RANGE.in_band(rp, move, band), (move, band)
        assert set(legal) <= set(C.PUNCHES), (band, legal)
        seen.update(legal)
        # And a non-punch canon happens to author a band for is never offered.
        assert "guard_high" not in legal, band
    assert seen == set(C.PUNCHES), (
        "some punch in the bout's vocabulary is throwable from no band at "
        "all: %s" % sorted(set(C.PUNCHES) - seen))
    assert not hasattr(P, "BY_BAND"), "the second authority came back"
    assert not hasattr(P, "BANDS"), "the copied band order came back"


def test_the_punchless_bands_are_pinned_and_no_fighter_may_prefer_one(rp):
    """THE COUNTDOWN FIRED, 2026-08-09, in an unexpected way worth recording:
    not because offence appeared at outside or clinch - canon is unchanged and
    they are still punch-less - but because the body computed the fact through
    `P.BY_BAND`, which no longer exists. The FACT survives; the second
    authority it was measured through does not.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-09 09:30 UTC | retired into
      the two assertions that matter now. Decision 0033 Ruling 3 pins the
      shape: `range_band` stays one band per move and `outside` stays
      punch-less, so this tuple changing is a canon change announcing itself. ]

    And the consequence that made the punch-less bands cost a twelve-round
    fight is now refused at the door: no Profile may PREFER a band it cannot
    punch from. The stalemate is a refused configuration, not a fight.
    """
    assert RANGE.bands_without_offence(rp, C.PUNCHES) == \
        ("clinch", "outside", "out_of_range")
    assert len(RANGE.throwable_from(rp, "mid", C.PUNCHES)) == 3
    assert len(RANGE.throwable_from(rp, "inside", C.PUNCHES)) == 2

    bands = P.Bands(RANGE.band_order(rp),
                    RANGE.bands_without_offence(rp, C.PUNCHES))
    with pytest.raises(P.PolicyError):
        P.decide(  # a plan that cannot produce a punch is refused, not run
            P.Observation(range_band="outside", preferred_band="outside",
                          throwable_here=(), bands=bands),
            _stream())


def test_no_ghost_punches_and_the_gate_refuses_nothing():
    """THE COUNTDOWN FIRED, 2026-08-09. Its docstring said: when this fails,
    the vocabularies were reconciled - retire the test and assert the punch
    ledger closes instead. They were (the policy now chooses only from
    `RANGE.throwable_from(..., C.PUNCHES)`, so a move outside the vocabulary
    is never looked at), and this is that assertion, run on a real fight.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-09 09:30 UTC | retired the
      countdown into the two executable deaths of D1 and D2. ]

    whiff_band == 0 is the death of D1: no punch is ever refused by the range
    gate, because the chooser and the gate are one derivation and the band a
    punch is committed at is the band it resolves against. The closed ledger
    is the death of D2: every punch thrown is accounted for through a named
    exit, so a ghost - charged but never flying - cannot exist silently.
    """
    bout = IntegratedBout(seed=4242)
    bout.run_fight()
    assert bout.whiff_band == 0, (
        "a punch was refused by the range gate; the chooser and the gate "
        "have stopped being one derivation")
    thrown = sum(f.punches_thrown for f in bout.fighters)
    resolved = sum(bout.contact.values())
    in_flight = sum(1 for f in bout.fighters if f.punch)
    assert thrown == resolved + bout.voided + in_flight, (
        "the punch ledger does not close: thrown=%d resolved=%d voided=%d "
        "in_flight=%d" % (thrown, resolved, bout.voided, in_flight))
    assert thrown > 0


# ------------------------------------------------- one punch ends every fight --

def test_knockdown_eligibility_reads_every_authored_region(cp):
    """THE COUNTDOWN'S PREMISE DIED WHILE THE TEST KEPT PASSING - the worst
    way for a countdown to end, and worth recording as a lesson: this test
    measured "one punch can knock anyone down" through the EVADE pack's
    single-region index, which never changed, while the bout switched to
    `RES.knockdown_capable`, which reads every authored region. The test
    stayed green while the fact it pinned stopped being true. A countdown
    must measure through the same door the runtime uses.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-09 10:58 UTC | retired into
      the new shape, measured through the runtime's own door. ]

    The new facts: `jaw_chin` is still the only knockdown-relevant region
    (changing THAT is Decision 0033 Ruling 4's deferred body-knockdown
    question), but four of the five punches now reach it because canon
    authors them to - the hook is ["head", "jaw_chin"] and array position is
    no longer authority. The body straight correctly cannot drop anyone,
    since neither torso region is knockdown-relevant. And the EVADE pack's
    element-zero read remains CORRECT for evasion - a slip vacates one lane -
    which is why it is asserted here rather than "fixed" by analogy.
    """
    relevant = sorted(r for r, spec in cp["regions"].items()
                      if spec["knockdown_relevant"])
    assert relevant == ["jaw_chin"], relevant
    capable = {m: RES.knockdown_capable(cp, m) for m in sorted(C.PUNCHES)}
    assert capable == {"body_straight_rear": False, "cross_rear": True,
                      "hook_lead": True, "jab_lead": True,
                      "uppercut_rear": True}, capable
    # Reordering an authored target list changes nothing (Decision 0026).
    fake = dict(cp)
    fake["move_regions"] = dict(cp["move_regions"],
                                hook_lead=("jaw_chin", "head"))
    assert RES.knockdown_capable(fake, "hook_lead") is True
    # The evasion lane index is a LANE, not a target list, and stays.
    ec = EVADE.evade_pack(C.REGIONS)
    assert ec["region"]["hook_lead"] == "head"


# ---------------------------------------------------- rules nobody is reading --

def test_the_ruleset_rules_the_contest():
    """THE COUNTDOWN'S PREMISE DIED, 2026-08-09 - a ruleset entered the
    contract (v3, Decision 0033 Ruling 2), and the static `C.CANON` tuple this
    test used to inspect was never where it landed: the ruleset is appended
    per bout in `header()`, because WHICH ruleset is a per-fight fact.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-09 10:58 UTC | retired into
      the invariants of the new authority. ]

    What holds now: the header names the ruleset fought under; the integrated
    condition pack no longer carries the knockdown limits at all (they are
    unreachable from the runtime, not merely deprecated - see Decision 0033's
    amendment for why the canon keys themselves survive for Phase O's frozen
    loader); professional's nulls mean NO knockdown count stops a
    professional bout; and the contradiction case is refused at load.
    """
    prof = RES.ruleset_pack("professional")
    assert prof["per_round"] is None and prof["per_bout"] is None
    assert prof["three_knockdown_rule"] is False
    arcade = RES.ruleset_pack("arcade_three_knockdown")
    assert arcade["per_round"] == 3 and arcade["per_bout"] == 4

    assert "max_per_round" not in RES.condition_pack()
    assert "max_per_bout" not in RES.condition_pack()

    header = C.new_bout(REPO, 4242)[2]
    assert "H|ruleset=professional" in header
    assert any(l.startswith("H|canon_ruleset_semantic=") or
               l.startswith("H|canon_ruleset_") for l in header), (
        "the ruleset is named but not hashed - identity without evidence")

    with pytest.raises(SystemExit):
        RES.ruleset_pack("no_such_ruleset")


# ------------------------------------------------------------ the scorecards --

def test_walking_forward_and_missing_scores_nothing():
    """THE COUNTDOWN'S PREMISE DIED, 2026-08-09 - the units were reconciled
    (Section 4's margin normalisation: each criterion against its own round
    total, no conversion constant), so "one advancing tick outscores a landed
    punch 560 to 1" is no longer computable, and the old body's arithmetic on
    the raw weights would have kept passing while describing nothing.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-09 10:58 UTC | retired into
      the referee's surviving ruling, which the fix implemented: effective
      aggression's defining word is EFFECTIVE. ]

    A fighter who marches forward all round and misses everything loses the
    round on every card - including Reyes's, the aggression judge - because
    ground advanced only scores when it bought clean punching.
    """
    panel = J.JudgingPanel(["walker", "boxer"])
    panel.score_round(1,
                      {"walker": {"landed": 0, "denied": 0, "pressed": 9000,
                                  "thrown": 60},
                       "boxer": {"landed": 3, "denied": 2, "pressed": 0,
                                 "thrown": 10}},
                      {})
    panel.close()
    for judge, card in panel.verdict()["cards"].items():
        assert card["rounds"] == [(1, 9, 10)], (judge, card["rounds"])


def test_the_round_winner_always_receives_ten():
    """THE COUNTDOWN FIRED, 2026-08-09. Its docstring said: when this fails,
    the deduction moved to the loser - retire this test and assert the
    ten-point must directly. It moved (Section 4's fix: a knockdown DECIDES
    the round, unequal knockdowns pick the winner before any judge weighs
    anything, and the invented max(7,...) floor is gone), and this is that
    assertion.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-09 10:58 UTC | retired. ]

    The construction that used to invert - a man winning 20 landed to 1,
    dropped twice - now scores 10-7 to the man who dropped him, on all three
    cards, because a fighter who has been down twice has lost the round
    whatever the work rate said. And in every scored round of a real fight,
    someone receives exactly ten.
    """
    panel = J.JudgingPanel(["a", "b"])
    panel.score_round(1,
                      {"a": {"landed": 20, "denied": 0, "pressed": 0},
                       "b": {"landed": 1, "denied": 0, "pressed": 0}},
                      {"a": 2, "b": 0})
    panel.close()
    for judge, card in panel.verdict()["cards"].items():
        assert card["rounds"] == [(1, 7, 10)], (judge, card["rounds"])

    bout = IntegratedBout(seed=4243)
    bout.run_fight()
    if bout.panel.seal_check():
        v = bout.panel.verdict() if bout.result else None
        if v:
            for judge, card in v["cards"].items():
                for _, pa, pb in card["rounds"]:
                    assert max(pa, pb) == 10, (judge, pa, pb)


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
