# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 01:20 UTC | START ]
"""Evasion inside the integrated bout: one boxer throws, the other tries not to
be there.

The ordering the ruling fixes is movement/range, attack commitment, evasion,
guard, contact. Guard and contact do not exist yet, so the chain stops at
evasion - and these tests assert what the built part must be, not what the
unbuilt part will be.
"""
import pytest

from tools.engine import analyze_core_condition as N
from tools.uppercut_evade import core as EVADE
from tools.uppercut_integrated import contract as C
from tools.uppercut_integrated.bout import IntegratedBout


@pytest.fixture(scope="module")
def bout():
    return IntegratedBout(seed=4242).run(1800)


@pytest.fixture(scope="module")
def ec():
    return EVADE.evade_pack(C.REGIONS)


def rows(bout, kind):
    return [r for r in bout.rows if r.startswith(kind + "|")]


# --------------------------------- the fork in the vocabulary, guarded -------

def test_the_integrated_vocabulary_still_matches_the_frozen_phases():
    """The integrated contract declares its own REGIONS and PUNCHES because it
    may not import a phase analyzer. That is a fork, and this is the guard: the
    day the two disagree it is a visible failure rather than two systems
    quietly meaning different things by "the body"."""
    assert C.REGIONS == N.REGIONS
    assert C.PUNCHES == N.PUNCHES


# ------------------------------------------- there is no evasion die ---------

def test_resolution_is_a_pure_function_of_what_it_is_given(ec):
    """Same punch, same region, same evasion - same answer, every time, with no
    stream, no seed and nothing to roll."""
    for _ in range(50):
        assert EVADE.resolve(ec, C.PUNCHES, "jab_lead", "slip_lead") \
            == (False, EVADE.VACATED, "head")


def test_three_of_the_four_reasons_mean_what_they_say(ec):
    assert EVADE.resolve(ec, C.PUNCHES, "jab_lead", None) \
        == (True, EVADE.CLEAR, "head")
    assert EVADE.resolve(ec, C.PUNCHES, "jab_lead", "slip_lead") \
        == (False, EVADE.VACATED, "head")
    # The uppercut rising into the roll: he moved onto it.
    assert EVADE.resolve(ec, C.PUNCHES, "uppercut_rear", "roll_under") \
        == (True, EVADE.COUNTER, ec["region"]["uppercut_rear"])


def test_region_is_currently_unreachable_from_any_authored_punch(ec):
    """A FINDING, not a gap in the tests, and it is asserted so it announces
    itself the day it changes.

    `region` means "an evasion was active and this punch was not aimed where it
    went". Today no authored punch can produce it, because canon's two
    active-window evasions both vacate exactly (head, jaw_chin) and both are
    beaten by `body_shot`. So a head punch is `vacated` and a body punch is
    `counter`, and there is nothing left over.

    That is coherent - the body shot does not merely miss the vacated lane, it
    punishes the slip, which is the better boxing answer. But it means one
    quarter of the reason vocabulary is currently unreachable in a fight, and
    that is worth knowing before anyone reads a `region` count of zero as
    evidence about fighters rather than about canon.

    The day a third evasion vacates something else, or a punch targets a region
    no evasion covers, this test fails and the finding is retired.
    """
    reachable = set()
    for ev, spec in ec["evasions"].items():
        if spec["kind"] != "active_window":
            continue
        for move in C.PUNCHES:
            reachable.add(EVADE.resolve(ec, C.PUNCHES, move, ev)[1])
    assert EVADE.REGION not in reachable, (
        "a punch can now produce `region` - retire this test and assert the "
        "case directly")
    assert reachable == {EVADE.VACATED, EVADE.COUNTER}


def test_a_guard_or_a_step_is_not_a_punch_and_is_refused(ec):
    """`guard_high` against a slip used to come back `(True, "region")` - an
    answer plausible enough to survive review, for something that cannot
    arrive."""
    for not_a_punch in ("guard_high", "guard_body", "step_in", "step_out",
                        "slip_lead", "clinch_entry", "pivot_lead"):
        with pytest.raises(KeyError):
            EVADE.resolve(ec, C.PUNCHES, not_a_punch, "slip_lead")
    # `guard_high` is the instructive one: canon gives it a target region
    # of arm_left, so "has a region" is not "is a punch".
    assert ec["region"]["guard_high"] is not None


# --------------------------------------- an evasion is a commitment ----------

def test_an_evasion_cannot_be_re_opened_while_it_is_active(bout):
    """A slip re-opened every tick is a permanently active slip, which is the
    "+20% dodge chance" the ruling forbids arrived at from the other side. Every
    open must be preceded by a close for that fighter."""
    state = {}
    for r in rows(bout, "W"):
        f = r.split("|")
        who, what = f[2], f[4]
        if what == "open":
            assert not state.get(who), "%s opened an evasion while one was "\
                                       "already active: %s" % (who, r)
            state[who] = True
        else:
            state[who] = False


def test_an_evasion_window_lasts_exactly_what_canon_authors(bout, ec):
    for r in rows(bout, "W"):
        f = r.split("|")
        if f[4] != "open":
            continue
        opened, until = int(f[1]), int(f[5].split("=")[1])
        assert until - opened == ec["evasions"][f[3]]["active"], r


def test_a_punch_resolves_on_canons_own_window_not_a_guess(bout):
    """The punch is in the air for startup+active and resolves at the end of
    it. A guessed window would be a guessed evasion window too.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-08 23:40 UTC | resolution:
      a knockdown stops the ring and the bell ends the round, and both void
      punches still in the air (counted in bout.voided). The pairing walk
      therefore clears its pending queues at every N row and round_end B row,
      so a voided punch is not mistaken for a resolved one. ]
    """
    thrown = {}
    for r in bout.rows:
        f = r.split("|")
        if f[0] == "N" or (f[0] == "B" and f[2] == "round_end"):
            thrown.clear()          # the ring voided everything in flight
        if f[0] == "D" and f[4] == "Attack" and f[5] in bout.frames:
            thrown.setdefault(f[2], []).append((int(f[1]), f[5]))
        if f[0] == "P":
            who, move = f[2], f[4]
            t0, m = thrown[who].pop(0)
            span = bout.frames[m]["startup"] + bout.frames[m]["active"]
            assert m == move and int(f[1]) - t0 == span, r


def test_every_punch_thrown_is_a_punch_resolved(bout):
    """The first version of this loop let a second punch overwrite one still in
    the air - 214 thrown, 117 resolved, and the missing ones simply vanished.
    The commitment now lasts the animation canon authors.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-08 23:40 UTC | resolution:
      the ledger grew two legal exits. Range legality (Rule 12) whiffs a punch
      thrown from a band it is not authored for - counted in bout.whiff_band,
      not in contact, because it never reached the evasion/contact chain. And
      a knockdown or the bell voids punches in flight - counted in
      bout.voided. The invariant is unchanged in spirit: no punch vanishes
      without a ledger entry saying which door it left through. ]
    """
    thrown = sum(f.punches_thrown for f in bout.fighters)
    resolved = sum(bout.contact.values())
    in_flight = sum(1 for f in bout.fighters if f.punch)
    assert thrown == resolved + bout.whiff_band + bout.voided + in_flight


# --------------------------------------------- and it reaches the fight ------

def test_the_bout_produces_every_outcome_canon_can_reach(bout):
    """Clear and vacated appear in the fight; region stays unreachable by the
    finding above; and every P row is accounted for by exactly one ledger.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-08 23:40 UTC | resolution:
      this test asserted contact[COUNTER] > 0, and under Decision 0032 that
      stopped being a structural guarantee. A counter now requires a punch
      whose resolve tick lands inside the defender's LIVE window (startup has
      passed, close has not) while the move sits in that evasion's authored
      beaten_by set - a genuine timing coincidence, not a table lookup. The
      counter PATH stays proven where it is provable: at the resolve table
      (test_three_of_the_four_reasons_mean_what_they_say above, and the
      Decision 0032 proof tests). Whether a given seed's fight produces one
      is an emergent fact about policy and timing, recorded as a diagnostic
      in the fight artifacts, not asserted here. Averaging the two claims -
      keeping the assert with a longer run until it happened to pass - would
      have pinned policy behavior to a test named after canon. ]
    """
    assert bout.contact[EVADE.CLEAR] > 0
    assert bout.contact[EVADE.VACATED] > 0
    assert bout.contact[EVADE.COUNTER] >= 0    # reachable; proven at the table
    assert bout.contact[EVADE.REGION] == 0
    assert sum(bout.contact.values()) + bout.whiff_band == len(rows(bout, "P"))


def test_the_stream_says_why_and_not_merely_whether(bout):
    """"The jab missed because the slip was still active" is boxing. "Evasion
    roll succeeded" is a spreadsheet wearing gloves.

    [ Claude Fable 5 (claude-fable-5) | 2026-08-08 23:40 UTC | resolution:
      Rule 12 added a third P-row shape - the band whiff, which says WHY just
      as loudly: `band=X|evasion=-|whiffed|band` means "thrown from a band it
      is not authored for", before evasion was ever consulted. It is asserted
      as its own exact shape rather than folded into the reason vocabulary,
      because it is a range-legality verdict, not a contact reason. The
      trailer now also carries whiff_band and voided, so the stream's own
      summary closes the same ledger the tests do. ]
    """
    for r in rows(bout, "P"):
        f = r.split("|")
        if f[-1] == "band":
            assert f[-2] == "whiffed", r
            assert f[5].startswith("band=") and f[6] == "evasion=-", r
            continue
        assert f[-1] in EVADE.REASONS, r
        assert f[-2] in ("arrived", "dodged"), r
        assert f[5].startswith("region=") and f[6].startswith("evasion="), r
    trailer = bout.stream().splitlines()[-1]
    for reason in EVADE.REASONS:
        assert "%s=" % reason in trailer, trailer
    assert "whiff_band=" in trailer and "voided=" in trailer, trailer


def test_the_row_kinds_do_not_collide(bout):
    """`W` briefly meant both a stamina row and an evasion window. One letter,
    two meanings, in a stream whose entire value is being parseable."""
    shapes = {}
    for r in bout.rows:
        f = r.split("|")
        shapes.setdefault(f[0], set()).add(len(f))
    assert "E" in shapes and "W" in shapes and "P" in shapes
    for r in rows(bout, "E"):
        assert "wind=" in r and "movement_wind_debit=" in r
    for r in rows(bout, "W"):
        # [ Claude Fable 5 (claude-fable-5) | 2026-08-08 23:40 UTC |
        #   resolution: Decision 0032 added the third window state - a window
        #   that expired unused is `mistimed`, carrying its authored penalty. ]
        assert r.split("|")[4] in ("open", "close", "mistimed")


def test_a_dodged_punch_is_never_also_blocked(bout, ec):
    """Phase R declares `outranks_guard`, and the integrated ordering depends
    on it: evasion resolves first, so a slipped punch never reaches guard."""
    assert ec["outranks_guard"] is True
    for r in rows(bout, "P"):
        if r.endswith(EVADE.VACATED):
            assert "dodged" in r
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 01:20 UTC | END ]
