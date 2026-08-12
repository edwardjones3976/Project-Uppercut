# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 22:10 UTC | START ]
"""The arena must not become a second implementation.

The whole argument for the live arena is that it RUNS the proven code rather
than agreeing with it. That argument is a property of the source layout, and
source layout is exactly the kind of thing that decays quietly: someone adds one
convenient JSON read to the subsystem, or reimplements one rule inline "just for
the HUD", and the arena stops being evidence without a single test failing.

These tests are cheap and need no engine. They do not prove the arena correct -
`tools/engine/prove_live_arena.py` does that, byte for byte. They stop the
arrangement that makes that proof meaningful from being dismantled by accident.
"""
import io
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "sandbox", "Source", "UppercutCore")
PRIVATE = os.path.join(SRC, "Private")
PUBLIC = os.path.join(SRC, "Public")


def read(*parts):
    path = os.path.join(*parts)
    assert os.path.exists(path), "%s is missing" % path
    return io.open(path, encoding="utf-8", errors="replace").read()


# The files that make up the shared core: rules, canon reader, loop, stream
# shape. Everything else in the module is a caller.
CORE_FILES = (
    "UppercutRangeCore.cpp",
    "UppercutRangeCanonLoader.cpp",
    "UppercutRangeStream.cpp",
)

# The callers. Two of them, which is the point - the commandlet that writes the
# evidence and the subsystem the Director presses Play on.
CALLERS = (
    "UppercutCoreRangeCommandlet.cpp",
    "UppercutFightSubsystem.cpp",
)


# Phase Q's chain: the shared core, the commandlet that writes the evidence, and
# the subsystem the Director presses Play on. Other phases' commandlets read
# canon for themselves and are none of this test's business - see
# `test_the_canon_reader_sprawl_is_on_the_record` for that, which is a finding
# rather than a rule.
PHASE_Q_CHAIN = CORE_FILES + (
    "UppercutCoreRangeCommandlet.cpp",
    "UppercutFightSubsystem.cpp",
    "UppercutLiveArenaCommandlet.cpp",
)


def test_only_the_loader_reads_canon_in_phase_qs_chain():
    """A second JSON reader is a second chance to read canon differently.

    The claim is about Phase Q's chain, not the module. An earlier draft of this
    test asserted the wider thing and failed immediately on six other phases'
    commandlets - which read canon legitimately, for their own contracts. The
    narrow claim is the one that is true and the one that matters: the fight the
    Director watches and the fight in the evidence are parsed by one function.
    """
    readers = []
    for name in PHASE_Q_CHAIN:
        text = read(PRIVATE, name)
        if "range_bands" in text or "max_frame_displacement_ru" in text:
            readers.append(name)
    assert readers == ["UppercutRangeCanonLoader.cpp"], (
        "Phase Q canon is parsed in %s - it must be parsed only by the loader, "
        "which both the commandlet and the subsystem call" % readers
    )


def test_the_canon_reader_sprawl_is_on_the_record():
    """Six other phases parse canon inline. Counted, not fixed, not forgotten.

    This is drift, and it is the same drift the Phase Q extraction just undid:
    every one of these commandlets holds its own opinion about which JSON field
    means what, and nothing makes them agree. It is NOT a defect today - each is
    proven against its own contract, so each is right about the phase it
    describes. It becomes a defect the moment a live runtime wants to run any of
    those phases too, which is precisely what Phase O will want.

    The number is asserted so that adding a seventh is a decision somebody makes
    on purpose, and removing one shows up as progress.
    """
    inline = []
    for name in sorted(os.listdir(PRIVATE)):
        if not name.endswith(".cpp") or name in PHASE_Q_CHAIN:
            continue
        if "range_bands" in read(PRIVATE, name):
            inline.append(name)
    assert len(inline) == 6, (
        "%d phases parse movement canon inline (was 6): %s. If this went up, a "
        "new phase copied the pattern the Phase Q extraction exists to end; if "
        "it went down, say so in the phase record." % (len(inline), inline)
    )


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 18:05 UTC | START edit: unbounded-band sentinel ]
def test_the_two_unbounded_band_sentinels_still_agree():
    """The one place the six inline readers and Phase Q's loader DISAGREE.

    The top range band (`out_of_range`) authors no `max_ru`, meaning unbounded.
    The two implementations represent that differently:

        the six inline readers     (int64)990000        i.e. a ceiling at 99.0 ru
        UppercutRangeCanonLoader   Unbounded == -1      i.e. no ceiling at all

    Those are not the same statement. They agree on every fight only because
    separation is capped by the ring, and the ring is far smaller than 99 ru -
    so `Sep < 990000` is always true and both resolve the top band identically.

    That equivalence is currently an ACCIDENT of the ring being small. This
    test makes it a checked invariant, so a canon edit that grew the ring (or
    shrank the reference reach span, which is the same thing in reach units)
    would fail here rather than silently making five phases disagree with Phase
    Q about which band a fighter is in.

    The real fix is one loader with one representation - see
    docs/plans/2026-08-07-what-the-integrated-schema-has-to-absorb.md. Until
    then the coupling is at least on the record.
    """
    import json
    doc = json.loads(io.open(os.path.join(REPO, "data", "movement_model.json"),
                             encoding="utf-8").read())

    bands = doc["range_bands"]["bands"]
    unbounded = [b for b in bands if b.get("max_ru") is None]
    assert len(unbounded) == 1, (
        "%d bands are unbounded (was 1). The sentinel divergence below was "
        "reasoned about for exactly one top band." % len(unbounded)
    )

    SENTINEL_RU = 99.0          # (int64)990000 in q10000, in the six readers
    axis = doc["ring"]["track"]["axis_length_ru"]
    assert axis < SENTINEL_RU, (
        "the ring axis is %s reach units and the inline readers treat %s as "
        "the top band's ceiling. Separation can now reach the sentinel, so the "
        "six inline readers and UppercutRangeCanonLoader would resolve the top "
        "band DIFFERENTLY - five phases would disagree with Phase Q about "
        "which band a fighter is in." % (axis, SENTINEL_RU)
    )

    lowest_unbounded = unbounded[0]["min_ru"]
    assert lowest_unbounded < axis < SENTINEL_RU, (
        "the ring no longer spans into the unbounded band (min_ru=%s, "
        "axis=%s); either the ring shrank below the top band or the bands "
        "moved, and the sentinel reasoning needs redoing"
        % (lowest_unbounded, axis)
    )
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 18:05 UTC | END edit ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 17:20 UTC | START edit: RNG copy count ]
def test_the_decision_draw_copy_count_is_on_the_record():
    """Eight files carry their own LCG. Counted, so a ninth is deliberate.

    `test_the_subsystem_does_not_reimplement_the_loop` below asserts these
    constants are absent from the SUBSYSTEM, which is a real guard covering one
    file. Nothing counted the rest, so the sprawl could grow silently - the same
    hole the reader-sprawl test was written to close for canon parsing.

    This is not a defect today: each phase is proven against its own contract,
    so each is right about the fight it describes. It is the blocker for
    Decision 0022's named RNG substreams, which require one seeded derivation
    per subsystem and cannot be enforced while eight files each advance their
    own generator. Surveyed in
    docs/plans/2026-08-07-what-the-integrated-schema-has-to-absorb.md.

    When the substream layer lands this number should FALL. If it rises, a new
    phase copied the pattern that work exists to end.
    """
    for const, what, expected in (
        ("1664525", "the LCG multiplier", 8),
        ("1013904223", "the LCG increment", 8),
        ("1099511628211", "the FNV-1a prime", 8),
    ):
        owners = [n for n in sorted(os.listdir(PRIVATE))
                  if n.endswith(".cpp") and const in read(PRIVATE, n)]
        assert len(owners) == expected, (
            "%d files define %s (was %d): %s. If this went up, the decision "
            "draw was copied again; if it went down, say so in the phase "
            "record." % (len(owners), what, expected, owners)
        )
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 17:20 UTC | END edit ]


def test_the_subsystem_does_not_reimplement_the_loop():
    """The arena must call Step(), never grow its own copy of the rules."""
    text = read(PRIVATE, "UppercutFightSubsystem.cpp")
    assert "Session.Step(" in text, "the subsystem no longer drives the session"
    for forbidden in ("1664525", "1013904223"):
        assert forbidden not in text, (
            "the subsystem contains the LCG constant %s - the decision draw "
            "belongs to the core, and a copy here would be a second fight"
            % forbidden
        )


def test_the_marker_hash_has_one_definition():
    """FNV-1a folds the rows. Two definitions is two hashes that agree for now."""
    definers = []
    for name in sorted(os.listdir(PRIVATE)):
        if name.endswith(".cpp") and "1099511628211" in read(PRIVATE, name):
            definers.append(name)
    # Other phases still carry their own copies; Phase Q's chain must not.
    for name in CORE_FILES + CALLERS:
        if name != "UppercutRangeStream.cpp":
            assert name not in definers, (
                "%s defines the FNV prime itself - it should fold rows through "
                "UppercutFnv1a64 so the arena and the commandlet hash "
                "identically" % name
            )
    assert "UppercutRangeStream.cpp" in definers


def test_the_stream_shape_is_not_duplicated():
    """A header written twice is two artifacts that look like one."""
    writers = []
    for name in sorted(os.listdir(PRIVATE)):
        if name.endswith(".cpp") and "H|phase=Q" in read(PRIVATE, name):
            writers.append(name)
    assert writers == ["UppercutRangeStream.cpp"], (
        "the Phase Q stream header is written in %s - one writer, or a dumped "
        "fight is only a lookalike of the proven one" % writers
    )


def test_wall_clock_does_not_scale_a_tick():
    """Criterion E.19, checked where it is easy to break."""
    text = read(PRIVATE, "UppercutFightSubsystem.cpp")
    assert "Accumulator +=" in text, "the fixed-step accumulator is gone"
    assert re.search(r"Accumulator -= TickSeconds", text), (
        "ticks are no longer spent whole - wall-clock time has started scaling "
        "the simulation, which Criterion E.19 prohibits"
    )
    assert "DeltaSeconds *" not in text.replace(
        "(double)DeltaSeconds * (double)Speed", ""), (
        "delta seconds are being applied to something other than the accumulator"
    )


@pytest.mark.parametrize("name", CORE_FILES + CALLERS + (
    "UppercutFighterBase.cpp",
    "UppercutMatchDirector.cpp",
    "UppercutLiveArenaCommandlet.cpp",
    # [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
    "UppercutArenaPresentation.cpp",
    # [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]
))
def test_every_arena_file_is_tagged(name):
    """The owner's identifying-tag procedure, on the files this work added."""
    text = read(PRIVATE, name)
    assert "START ]" in text and "END ]" in text, (
        "%s is missing its start/end identifying tags" % name
    )


def test_the_fighter_actor_cannot_write_to_the_fight():
    """Decision 0012's boundary, tested rather than trusted.

    Presentation reads snapshots. If this actor ever calls a control, deleting it
    mid-round would change the fight - and the separation would be decorative.
    """
    text = read(PRIVATE, "UppercutFighterBase.cpp")
    for forbidden in ("StartFight", "SingleStep", "Restart(", "Reseed",
                      "SetSpeed", "Session"):
        assert forbidden not in text, (
            "the fighter actor calls %s - a presentation actor that can drive "
            "the fight is not a presentation actor" % forbidden
        )


# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | START ]
def test_arena_presentation_cannot_drive_the_fight():
    """Fab ring / mannequin helpers are presentation-only."""
    text = read(PRIVATE, "UppercutArenaPresentation.cpp")
    for forbidden in ("StartFight", "SingleStep", "Restart(", "Reseed",
                      "SetSpeed", "Session", "1664525", "1013904223"):
        assert forbidden not in text, (
            "arena presentation contains %s - presentation must not own the fight"
            % forbidden
        )
# [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:53 UTC | END ]
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 22:10 UTC | END ]
