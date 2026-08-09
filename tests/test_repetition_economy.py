# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 18:35 UTC | START ]
"""`punch_model.repetition_economy` - Rule 4, read at last and held here.

Decision 0036 named throw rate the critical path and named these as canon's
unread answers. Two of the four mechanisms govern throwing from the thrower's
side and both are now wired.

The load-bearing test in this file is
`test_an_arm_mid_punch_is_not_an_idle_arm`. The first wiring shed an arm's
work on every tick that arm did not *begin* a punch, including the ticks it
spent recovering from one - and canon's own ratio (0.05 gained per throw,
0.004 shed per idle tick, so 12.5 idle ticks undo one throw) against a jab
that occupies its arm for about fourteen made the mechanism structurally
unable to accumulate. It measured bit-identical to being switched off. Canon
does not author dead coefficients, so that was a misreading of "idle".
"""
import pytest

from tools.uppercut_punch import economy as PE
from tools.uppercut_integrated import contract as C
from tools.uppercut_integrated.bout import IntegratedBout

ONE = PE.ONE


@pytest.fixture(scope="module")
def pack():
    return PE.repetition_pack()


@pytest.fixture(scope="module")
def bout():
    b = IntegratedBout(seed=4242)
    b.run(20000)
    return b


def test_canon_holds_its_own_contract(pack):
    assert pack["canon_errors"] == []
    assert pack["max_multiplier"] > ONE
    assert pack["per_throw_same_arm"] > 0
    assert pack["recovery_per_idle_tick"] > 0


def test_every_punch_authors_the_hand_that_throws_it(pack):
    """Fail closed. Charging the wrong arm would tax a fighter for mixing his
    hands, which is the one behaviour canon says must never be taxed."""
    for move in C.PUNCHES:
        assert PE.hand_of(pack, move) in ("lead", "rear")
    with pytest.raises(KeyError):
        PE.hand_of(pack, "no_such_punch")


def test_work_accumulates_and_is_capped_at_canons_ceiling(pack):
    work = 0
    for _ in range(200):
        work = PE.worked(pack, work)
    assert PE.arm_multiplier(pack, work) == pack["max_multiplier"]
    assert work == pack["max_multiplier"] - ONE


def test_resting_forgives_everything_eventually(pack):
    work = PE.worked(pack, 0)
    ticks = 0
    while work > 0 and ticks < 10000:
        work = PE.rested(pack, work)
        ticks += 1
    assert work == 0, "an arm that rests forever must owe nothing"
    assert ticks < 100, "one throw should not take a round to shed"


def test_it_is_not_a_repeat_counter(pack):
    """Canon: "the tax is on doing one thing, not on throwing punches." A
    fighter who alternates hands throws exactly as many punches as one who
    does not, and carries nothing for it."""
    alternating = {"lead": 0, "rear": 0}
    same = {"lead": 0, "rear": 0}
    for i in range(40):
        h = "lead" if i % 2 else "rear"
        alternating[h] = PE.worked(pack, alternating[h])
        for other in alternating:
            if other != h:
                alternating[other] = PE.rested(pack, alternating[other], 14)
        same["lead"] = PE.worked(pack, same["lead"])
        same["rear"] = PE.rested(pack, same["rear"], 14)

    assert max(PE.arm_multiplier(pack, w) for w in alternating.values()) < \
        PE.arm_multiplier(pack, same["lead"]), \
        "mixing hands must cost less than doing one thing"


def test_ground_is_ceded_only_by_the_man_who_does_not_move_his_feet(pack):
    assert PE.ground_ceded(pack, True) == 0
    assert PE.ground_ceded(pack, False) == \
        pack["ru_ceded_per_throw_without_step"]


# --------------------------------------------------- and inside the fight --

def test_an_arm_mid_punch_is_not_an_idle_arm(bout):
    """THE REGRESSION. If the shed runs through a punch's own recovery, no arm
    can ever carry work between punches and the mechanism is inert.

    Measured over ten seeds when it was wrong: throw rate, landed rate and
    round count were identical to the mechanism being stubbed out. So this
    test does not check a coefficient - it checks that the multiplier is ever
    anything other than 1.0, which is the only observable difference between
    a live mechanism and a dead one.
    """
    seen = []
    real = PE.arm_multiplier

    def spy(p, w):
        m = real(p, w)
        seen.append(m)
        return m

    PE.arm_multiplier = spy
    try:
        b = IntegratedBout(seed=4242)
        b.run(40000)
    finally:
        PE.arm_multiplier = real

    assert seen, "no punch was thrown, so nothing was measured"
    taxed = [m for m in seen if m > ONE]
    assert taxed, ("arm_fatigue never charged a single punch - the mechanism "
                   "is inert, which is what the idle-tick misreading did")


def test_a_taxed_arm_is_the_exception_and_never_the_rule(bout):
    """The distribution has to look like boxing rather than like bookkeeping:
    most punches free, a decaying tail of expensive ones, and the ceiling a
    real bound rather than a wall everyone lives against."""
    seen = []
    real = PE.arm_multiplier

    def spy(p, w):
        m = real(p, w)
        seen.append(m)
        return m

    PE.arm_multiplier = spy
    try:
        b = IntegratedBout(seed=4242)
        b.run(40000)
    finally:
        PE.arm_multiplier = real

    taxed = len([m for m in seen if m > ONE])
    assert 0 < taxed < len(seen) // 2, \
        "most punches must cost nothing extra, or this is a punch tax"
    assert max(seen) < PE.repetition_pack()["max_multiplier"], \
        "the ceiling is being pinned, so it is a wall and not a bound"


def test_the_feet_reset_the_position_cost(bout):
    """Canon's `resets_on: step_in, step_out, step_lateral`. If nothing ever
    reset it, position cost would be a flat per-punch tax - the thing canon
    forbids - rather than the reason a fighter walks his man down."""
    assert bout.ceded_ru > 0, "nobody ever ceded ground by standing and firing"
    thrown = sum(1 for r in bout.rows if r.startswith("D|")
                 and r.split("|")[4] == "Attack")
    per_throw = bout.rep["ru_ceded_per_throw_without_step"]
    assert bout.ceded_ru < thrown * per_throw, \
        "every single throw ceded ground, so the feet never reset it"
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 18:35 UTC | END ]
