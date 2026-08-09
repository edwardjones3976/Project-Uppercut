# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:30 UTC | START ]
"""Decision 0032 proof tests: evasion is a real commitment.

Decision 0032 (Director, binding) requires that evasion inside the
integrated bout is a committed body movement, not a saving throw:
commit -> startup -> active window -> resolve -> recovery, with a
mistime penalty when the window was never used.  There is no dodge
percentage and no evasion die anywhere in the resolution path, and
evade spam is not free -- every commit is charged its authored
economy cost on the commit tick.

These tests are written to FAIL against the pre-0032 code (where an
evade was an instantaneous, uncharged escape) and to pass only when
the window bookkeeping described in the bout row grammar is actually
implemented.  Wherever possible they parse the public b.rows event
stream instead of reaching into private state.

All tests are deterministic: fixed seeds, no sleeps, no wall clock.
"""

import pytest

from tools.uppercut_evade import core as EVADE
from tools.uppercut_integrated import contract as C
from tools.uppercut_integrated.bout import IntegratedBout


# ---------------------------------------------------------------------------
# Row-grammar helpers.
#
# The bout emits a pipe-separated event stream:
#   D|tick|who|strategic|tactical|execution|reason|initiative
#   W|tick|who|evasion_id|open|until=N
#   W|tick|who|evasion_id|close
#   W|tick|who|evasion_id|mistimed|penalty=6
#   P|tick|who|foe|move|region=X|evasion=Y|arrived-or-dodged|reason
#   E|tick|who|wind=..|reserve=..|movement fields
# ---------------------------------------------------------------------------


def _num(text):
    """Parse an int if possible, else a float (E-row units are unspecified)."""
    try:
        return int(text)
    except ValueError:
        return float(text)


def _kv(field):
    key, _, value = field.partition("=")
    return key, value


def _rows(bout, kind):
    """All rows of one grammar kind, already split into fields."""
    prefix = kind + "|"
    return [row.split("|") for row in bout.rows if row.startswith(prefix)]


def _evade_commits(bout, ec):
    """(tick, who, evasion_id) for every D row that commits an evasion.

    A commit is a D row whose tactical is "Evade" and whose execution
    field names an authored evasion.
    """
    commits = []
    for parts in _rows(bout, "D"):
        tactical, execution = parts[4], parts[5]
        if tactical == "Evade" and execution in ec["evasions"]:
            commits.append((int(parts[1]), parts[2], execution))
    return commits


def _window_rows(bout, state):
    """(tick, who, evasion_id, tail_fields) for W rows in the given state."""
    out = []
    for parts in _rows(bout, "W"):
        if parts[4] == state:
            out.append((int(parts[1]), parts[2], parts[3], parts[5:]))
    return out


def _wind_by_tick(bout):
    """{(tick, who): wind} parsed from the per-tick E stamina rows."""
    wind = {}
    for parts in _rows(bout, "E"):
        tick, who = int(parts[1]), parts[2]
        for field in parts[3:]:
            key, value = _kv(field)
            if key == "wind":
                wind[(tick, who)] = _num(value)
                break
    return wind


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ec():
    return EVADE.evade_pack(C.REGIONS)


@pytest.fixture(scope="module")
def long_bout():
    """One long stretch of integrated fight (3600 ticks = one minute),
    shared read-only by every test that parses the event stream."""
    bout = IntegratedBout(seed=4242)
    bout.run(3600)
    return bout


# ---------------------------------------------------------------------------
# Proofs 1-3: the resolve table is authored geometry, not chance.
# ---------------------------------------------------------------------------


def test_body_shot_finds_the_body_during_a_head_slip(ec):
    """A slip takes the head off the centerline; it does nothing for the
    body.  Digging a rear straight to the body while the opponent slips is
    the classic punishment for slip-happy fighters.

    Canon authors body_straight_rear as a punch that BEATS slip_lead (it
    is in the slip's beaten_by set), so the resolver reports COUNTER --
    the authored answer to the movement -- rather than REGION, which is
    reserved for a punch whose target region merely was not among the
    vacated lanes.  Either way the punch arrives: the slip bought nothing
    against the body.
    """
    arrived, reason, region = EVADE.resolve(
        ec, C.PUNCHES, "body_straight_rear", "slip_lead"
    )
    assert arrived is True, (
        "body_straight_rear must arrive against slip_lead: a head slip "
        "does not move the body"
    )
    assert reason in (EVADE.COUNTER,), (
        "canon authors the body shot as the counter that beats the slip, "
        f"so the reason must be COUNTER, got {reason!r}"
    )
    assert isinstance(region, str) and region


def test_uppercut_defeats_the_authored_roll(ec):
    """Rolling under a hook drops the head down and forward -- directly
    onto the path of a rear uppercut.  That is why the uppercut is the
    authored counter to the roll: the evasion moves the target INTO the
    punch's travel path.  resolve must report an arrival with reason
    COUNTER, not a dodge roll that happened to fail.
    """
    arrived, reason, region = EVADE.resolve(
        ec, C.PUNCHES, "uppercut_rear", "roll_under"
    )
    assert arrived is True, (
        "uppercut_rear must arrive against roll_under: the roll ducks "
        "into the uppercut's rising path"
    )
    assert reason == EVADE.COUNTER, (
        f"the uppercut is the authored counter to the roll, got {reason!r}"
    )
    assert isinstance(region, str) and region


def test_straight_misses_a_correctly_timed_slip(ec):
    """A rear cross travels a straight line to the head.  A slip that is
    live when the cross lands has moved the head lanes off that line, so
    the punch must miss with reason VACATED -- the target was not there.
    No dice, no percentage: the geometry alone decides it.
    """
    arrived, reason, region = EVADE.resolve(ec, C.PUNCHES, "cross_rear", "slip_lead")
    assert arrived is False, (
        "cross_rear must miss a live slip_lead: the head lanes it targets "
        "are vacated"
    )
    assert reason == EVADE.VACATED, (
        f"the miss must be attributed to the vacated lane, got {reason!r}"
    )


# ---------------------------------------------------------------------------
# Commitments: the authored pack itself contains no chance mechanism.
# ---------------------------------------------------------------------------


def test_evasion_pack_authors_commitment_not_chance(ec):
    """Decision 0032 bans dodge percentages and evasion dice.  Every
    authored evasion must therefore be a commitment profile -- startup,
    active window, recovery, and a real economy cost -- and nothing in
    the pack may smell like a probability.  The mistime penalty and the
    evade-outranks-guard precedence are part of the binding contract.
    """
    assert ec["mistime_ticks"] == 6
    assert ec["outranks_guard"] is True

    for name in ("slip_lead", "roll_under"):
        ev = ec["evasions"][name]
        assert ev["kind"] == "active_window", (
            f"{name} must be an active-window commitment, got {ev['kind']!r}"
        )
        assert ev["startup"] > 0, f"{name} must have real startup"
        assert ev["active"] > 0, f"{name} must have a finite live window"
        assert ev["recovery"] > 0, f"{name} must have real recovery"
        assert ev["cost"] > 0, f"{name} must cost resources to throw"
        for key in ev:
            lowered = key.lower()
            for banned in ("percent", "chance", "prob", "dodge", "die", "dice"):
                assert banned not in lowered, (
                    f"{name} carries a chance-like field {key!r}; "
                    "Decision 0032 bans dodge percentages and evasion dice"
                )

    slip = ec["evasions"]["slip_lead"]
    assert slip["vacates"] == ("head", "jaw_chin")
    assert slip["startup"] == 3
    assert slip["active"] == 5
    assert slip["recovery"] == 7
    assert slip["cost"] == 8000
    assert ec["evasions"]["roll_under"]["active"] == 6


# ---------------------------------------------------------------------------
# Proofs 4-8 and the commitment lifecycle, read off the bout's event stream.
# ---------------------------------------------------------------------------


def test_mistimed_window_extends_recovery_with_authored_penalty(ec, long_bout):
    """Slipping a punch that never comes is a real mistake in a real ring:
    the fighter has spent movement and is out of position with nothing to
    show for it.  The bout must therefore emit a W|...|mistimed row when
    an active window expires with no punch having resolved against it,
    and the penalty appended to recovery must be exactly the authored
    ec["mistime_ticks"] -- not a freebie, not an ad-hoc constant.
    """
    mistimed = _window_rows(long_bout, "mistimed")

    if not mistimed:
        # Direct construction fallback: commit an evasion ourselves and let
        # the window expire.  Only attempted when the bout exposes the
        # internal commit hook; the 3600-tick run above is the primary path.
        fallback = IntegratedBout(seed=4242)
        if hasattr(fallback, "_commit_evasion"):
            slip = ec["evasions"]["slip_lead"]
            fallback._commit_evasion(
                fallback.fighters[0], getattr(fallback, "tick", 0), "slip_lead"
            )
            fallback.run(
                slip["startup"]
                + slip["active"]
                + slip["recovery"]
                + ec["mistime_ticks"]
                + 5
            )
            mistimed = _window_rows(fallback, "mistimed")

    assert mistimed, (
        "no W|...|mistimed row appeared in a 3600-tick bout (seed 4242) and "
        "direct construction found none either: under Decision 0032 an "
        "evasion window that expires unused MUST be punished with a mistime "
        "row -- an evade that costs nothing when it whiffs is a dodge "
        "percentage in disguise"
    )
    for tick, who, evasion_id, tail in mistimed:
        fields = dict(_kv(f) for f in tail)
        assert "penalty" in fields, (
            f"mistimed row at tick {tick} for {who}/{evasion_id} carries no "
            f"penalty field: {tail}"
        )
        assert _num(fields["penalty"]) == ec["mistime_ticks"], (
            f"mistime penalty must equal the authored ec['mistime_ticks'] "
            f"({ec['mistime_ticks']}), got {fields['penalty']!r} at tick {tick}"
        )


def test_presentation_rng_cannot_move_evasion_outcomes():
    """Whether a punch lands or is slipped is decided by timing and
    geometry, never by a hidden roll.  Draining the presentation RNG
    stream between every tick must therefore leave every P row -- every
    punch resolution -- byte-for-byte identical to an undisturbed bout
    with the same seed.  If the P rows move, an outcome is secretly
    coupled to presentation randomness.
    """
    bout_a = IntegratedBout(seed=4242)
    bout_a.run(1800)

    bout_b = IntegratedBout(seed=4242)
    for _ in range(1800):
        stream = bout_b.rng.stream("presentation")
        for _ in range(5):
            stream.below(1000)
        bout_b.run(1)

    p_a = [row for row in bout_a.rows if row.startswith("P|")]
    p_b = [row for row in bout_b.rows if row.startswith("P|")]
    assert p_a, "expected at least one punch to resolve in 1800 ticks"
    assert p_a == p_b, (
        "P rows diverged after draining the presentation stream: an "
        "evasion or punch outcome is coupled to presentation RNG"
    )


def test_evade_commit_is_charged_wind_on_the_commit_tick(ec, long_bout):
    """Evade spam is not free.  The moment a fighter commits to an
    evasion, the authored economy cost comes off their Wind -- on the
    commit tick, before any benefit is seen.  For every Evade commit in
    the stream, the committing fighter's E-row wind on the commit tick
    must be strictly below their wind on the previous tick.
    """
    wind = _wind_by_tick(long_bout)
    commits = _evade_commits(long_bout, ec)
    assert commits, (
        "no Evade commit found in a 3600-tick bout (seed 4242); the "
        "economy proof needs at least one committed evasion"
    )

    checked = 0
    for tick, who, evasion_id in commits:
        before = wind.get((tick - 1, who))
        after = wind.get((tick, who))
        if before is None or after is None:
            continue  # commit on the very first tick has no prior E row
        if before <= 0:
            continue  # already floored; a further drop cannot show
        checked += 1
        assert after < before, (
            f"{who} committed {evasion_id} at tick {tick} but wind did not "
            f"drop ({before} -> {after}); the authored cost "
            f"({ec['evasions'][evasion_id]['cost']}) must be charged on the "
            "commit tick"
        )
    assert checked >= 1, (
        "no Evade commit had usable before/after E rows to compare"
    )


def test_window_opens_exactly_startup_ticks_after_commit(ec, long_bout):
    """A slip is not instantaneous: the head has to travel.  During
    startup the fighter is committed but not yet safe.  Every W|open row
    must therefore sit exactly `startup` ticks after the D row that
    committed the evasion -- a too-late slip fails precisely because
    these ticks exist.
    """
    commits = _evade_commits(long_bout, ec)
    opens = _window_rows(long_bout, "open")
    assert opens, (
        "no W|...|open row in a 3600-tick bout (seed 4242); windows must "
        "be part of the public stream"
    )

    for open_tick, who, evasion_id, _tail in opens:
        prior = [
            t
            for t, w, e in commits
            if w == who and e == evasion_id and t <= open_tick
        ]
        assert prior, (
            f"W|open for {who}/{evasion_id} at tick {open_tick} has no "
            "committing D row before it: a window cannot open uncommitted"
        )
        commit_tick = max(prior)
        startup = ec["evasions"][evasion_id]["startup"]
        assert open_tick - commit_tick == startup, (
            f"{who}/{evasion_id}: committed at tick {commit_tick}, window "
            f"opened at tick {open_tick}; expected exactly startup="
            f"{startup} ticks of travel, got {open_tick - commit_tick}"
        )


def test_window_stays_open_exactly_active_ticks(ec, long_bout):
    """The live window is a finite piece of authored timing, not a state
    a fighter sits in.  Every W|open row advertises until=N, and N minus
    the open tick must equal the evasion's authored `active` duration --
    for the slip that is 5 ticks, for the roll 6.
    """
    opens = _window_rows(long_bout, "open")
    assert opens, "no W|...|open row in a 3600-tick bout (seed 4242)"

    for open_tick, who, evasion_id, tail in opens:
        fields = dict(_kv(f) for f in tail)
        assert "until" in fields, (
            f"W|open at tick {open_tick} for {who}/{evasion_id} carries no "
            f"until field: {tail}"
        )
        active = ec["evasions"][evasion_id]["active"]
        assert _num(fields["until"]) - open_tick == active, (
            f"{who}/{evasion_id}: window opened at tick {open_tick} with "
            f"until={fields['until']}; duration must be exactly the "
            f"authored active={active}"
        )


def test_every_opened_window_is_resolved_before_the_next(long_bout):
    """Commitment means the lifecycle always completes: a window that
    opens must be resolved -- closed (used or expired) or flagged
    mistimed -- before that fighter can open another.  Two open rows for
    one fighter with no resolution between them would mean evasions can
    be stacked, which is evade spam by another name.  A window still
    pending at the very end of the run is tolerated only because the
    bout may end mid-window.
    """
    per_fighter = {}
    for parts in _rows(long_bout, "W"):
        per_fighter.setdefault(parts[2], []).append(parts)
    assert per_fighter, "no W rows at all in a 3600-tick bout (seed 4242)"

    saw_open = False
    for who, w_rows in per_fighter.items():
        open_pending = False
        for parts in w_rows:
            state = parts[4]
            if state == "open":
                assert not open_pending, (
                    f"{who} opened a second window before resolving the "
                    f"first: {'|'.join(parts)}"
                )
                open_pending = True
                saw_open = True
            elif state in ("close", "mistimed"):
                open_pending = False
    assert saw_open, "W rows exist but none of them ever opened a window"


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:30 UTC | END ]
