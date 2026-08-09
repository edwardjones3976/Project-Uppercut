# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 13:10 UTC | START ]
"""Phase Q's range rules, extracted so the integrated bout can CALL them.

THIS IS THE PYTHON TWIN OF `UppercutRangeCore.h`, and it exists for the same
reason that file does. The C++ rules were extracted out of a commandlet's
`Main()` on 2026-08-06 so a live subsystem could run them instead of
re-implementing them; the Python rules stayed inside a phase analyzer, and the
integrated contract is forbidden to import phase analyzers. So integrating
range meant either importing an analyzer or copying its formulas, and Decision
0026's successor order names that exact situation:

    "If integrating Phase Q or R requires copying their authoritative formulas
     rather than calling reusable shared code, stop. In that case, extract the
     missing reusable seam first."

This is that extraction. Every function below was MOVED, not rewritten - sliced
out of `tools/engine/analyze_core_range.py` by anchor and written verbatim, so
no transcription could alter a rule. `analyze_core_range` now imports them and
remains the Phase Q contract; the integrated runtime imports the same names.

THE SAFETY NET IS THE PARITY PROOF, exactly as it was for the C++ extraction:
after this move Phase Q must still emit a byte-identical marker stream against
its pinned hash. Passing tests would say the code still does what the tests
describe. An identical stream says the fight is the same fight.

WHAT DID NOT MOVE. `the_uppercut_becomes_possible` stays in the analyzer: it
reads Phase Q's own round canon to compare reach against a body surface, which
is a property OF THAT PHASE rather than a rule of range. Moving it would have
dragged a phase analyzer's canon pack into shared code and quietly recreated
the coupling this file removes.

DESIGN RULES, so it stays usable from both sides - the same list
`UppercutRangeCore.h` carries:
  - no clock, no IO in the rules themselves (`range_pack` is the loader);
  - fixed-point integers only (q10000), never float;
  - every division floors, because Python's // floors and C++ / truncates and
    that is the seam where a port silently diverges;
  - canon arrives as a dict, loaded by whoever has a file system.
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def q(v):
    """Canon's decimal into the shared integer contract.

    Deliberately identical to the analyzer's own `q`, and
    `tests/test_range_core_extraction.py` asserts they agree across a spread of
    values rather than trusting the eye. If they ever disagree the band table
    moves and Phase Q stops re-proving, which is the loudest available failure.
    """
    return int(round(float(v) * 10000))


def floordiv(a, b):
    """Python's // already floors. Named so the C++ port cannot forget."""
    return a // b


# The two canon files the range rules read. Moved with the loader they belong
# to; `analyze_core_range` re-exports them so the Phase Q header, which names
# every file the phase reads, still names the same two.
MOVEMENT = os.path.join("data", "movement_model.json")
MOVES = os.path.join("data", "moves", "generic_sandbox_moves.json")


def range_pack() -> dict:
    """Canon's range model in the shared integer contract.

    Everything is q10000 reach units, which is the unit Phase K's positions were
    already in - `axis` 49200 is canon's 6.4 m ring over a 1.3 m reach span, and
    a jab's 10500 tip extension is 1.05 reach units. The band table and the
    geometry have been in the same space all along; only the table was unread.
    """
    import hashlib
    raw = io.open(os.path.join(REPO, MOVEMENT), "rb").read()
    mv = json.loads(raw)
    rb = mv["range_bands"]
    bands = []
    for b in rb["bands"]:
        lo = q(b["min_ru"])
        hi = None if b["max_ru"] is None else q(b["max_ru"])
        bands.append((b["key"], lo, hi))
    loco = {m["posture_mode"]: m for m in mv["locomotion"]["modes"]}
    raw_m = io.open(os.path.join(REPO, MOVES), "rb").read()
    moves = json.loads(raw_m)
    key = "moves" if "moves" in moves else next(
        k for k, v in moves.items()
        if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0])
    band_of_move = {m["id"]: m["range_band"] for m in moves[key]
                    if m.get("range_band")}
    c = {
        "bands": bands,
        "hyst": q(rb["hysteresis_ru"]),
        "stride": q(loco["boxing_steps"]["stride_length_ru"]),
        "cap": q(mv["locomotion"]["max_frame_displacement_ru"]),
        "min_sep": q(mv["separation"]["min_center_distance_ru"]),
        # The ring as a BOUND on movement, not only as Ringcraft flavour. Canon
        # added this block when the excessive-running abuse showed a retreating
        # fighter opening distance forever: separation had no ring to run out of.
        #
        # THERE IS NO ANTI-RUNNING RULE. An earlier version of this comment
        # called `rope_retreat_multiplier: 0.0` exactly that, and the phrase was
        # never canon's - it was invented here and spread to six files. What
        # canon has is a ring that ends, and what Rule 4 names is an abuse:
        # NEITHER hitting NOR being hit for long periods. Hitting WITHOUT being
        # hit is the opposite of an abuse; it is the thing the sport most
        # admires, and nothing in this model may charge a fighter for it.
        # Lateral stays at full rate on the ropes for that reason: circling off
        # is the boxing answer and it remains open. See
        # docs/design/defensive_purity_and_non_engagement.md.
        "axis": q(mv["ring"]["track"]["axis_length_ru"]),
        "ropes": q(mv["ring"]["track"]["back_to_ropes_ru"]),
        "retreat_mult": q(mv["ring"]["track"]["rope_retreat_multiplier"]),
        "move_band": band_of_move,
        "sha": {"movement": hashlib.sha256(raw).hexdigest(),
                "moves": hashlib.sha256(raw_m).hexdigest()},
    }
    errs = []
    # Contiguity: the bands must tile the line with no gap and no overlap, or a
    # separation exists that belongs to no band and the gate cannot be evaluated.
    for (ka, _, hia), (kb, lob, _) in zip(bands, bands[1:]):
        if hia != lob:
            errs.append("bands %s and %s do not meet: %s vs %s"
                        % (ka, kb, hia, lob))
    if bands[0][1] != 0:
        errs.append("the first band does not start at zero separation")
    if bands[-1][2] is not None:
        errs.append("the last band is bounded, so a far enough fighter has no band")
    # The hysteresis must be smaller than the narrowest band, or a fighter could
    # cross a band entirely without ever registering it.
    widths = [hi - lo for _, lo, hi in bands if hi is not None]
    if c["hyst"] >= min(widths):
        errs.append("hysteresis %d is not smaller than the narrowest band %d"
                    % (c["hyst"], min(widths)))
    # A stride the cap cannot deliver would silently truncate every step.
    if c["stride"] <= 0 or c["cap"] <= 0:
        errs.append("a zero stride or displacement cap makes footwork inert")
    # The floor must sit inside the innermost band or the clinch is unreachable -
    # canon says this in prose in `separation.note`; here it is executable.
    if c["min_sep"] >= bands[0][2]:
        errs.append("the separation floor is at or above the clinch ceiling, so "
                    "the clinch band could never be entered")
    c["canon_errors"] = errs
    return c


def band_at(c: dict, sep: int) -> str:
    """Which band a separation sits in, ignoring history."""
    for key, lo, hi in c["bands"]:
        if sep >= lo and (hi is None or sep < hi):
            return key
    return c["bands"][-1][0]


def resolve_band(c: dict, current: str, sep: int) -> str:
    """The band a fighter is IN, which is not always the band he is AT.

    Hysteresis, canon's own anti-flicker rule: leaving the current band costs the
    boundary plus `hysteresis_ru` in the direction of travel. A fighter hovering
    on a boundary therefore keeps the band he had, and the band a punch is judged
    against does not chatter tick by tick.
    """
    idx = {k: i for i, (k, _, _) in enumerate(c["bands"])}
    if current not in idx:
        return band_at(c, sep)
    _, lo, hi = c["bands"][idx[current]]
    if sep < lo - c["hyst"]:
        return band_at(c, sep)
    if hi is not None and sep >= hi + c["hyst"]:
        return band_at(c, sep)
    return current


def in_band(c: dict, move_id: str, band: str) -> bool:
    """Rule 12. A move declares one band; anywhere else it hits empty air.

    A move with no authored band is not silently permitted - that would make the
    gate optional exactly where the move table is incomplete, which is the defect
    class this repository refuses. It is refused instead.

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: the one membership test ]
    THIS IS THE ONE MEMBERSHIP TEST, and `throwable_from` below asks the same
    question of a whole vocabulary at once. It CALLS this rather than
    re-deriving it, so the set a chooser picks from and the gate the resolver
    applies cannot disagree - not because two derivations were checked against
    each other, but because there is only one derivation.

    SHAPE-TOLERANT ON PURPOSE. Whether canon's `range_band` becomes a SET per
    move is an open Director decision, so the authored value is read as one
    band or as a collection of bands, and the day that decision lands the
    loader changes and this rule does not. The previous body was
    `c["move_band"].get(move_id) == band`, identical for every authored move
    and different on exactly one input: an UNAUTHORED move id compared against
    a `band` of None, where `None == None` made an unknown move legal. Nothing
    in the bout can produce that band, but "unknown ids never mean free" is a
    rule here, not a hope.
    # [ ... | 2026-08-09 02:05 UTC | END edit: the one membership test ]
    """
    authored = c["move_band"].get(move_id)
    if authored is None:
        return False
    if isinstance(authored, str):
        return authored == band
    return band in authored


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: one legality authority ]
def band_order(c: dict) -> tuple:
    """Canon's bands, closest first, in the order canon declares them.

    Ordering is authority, not convenience. "Closer" and "further" is how any
    chooser reasons about range, and a hand-written copy of this tuple is a
    second opinion about a rule canon already owns - the same defect class as a
    hand-written table of which punch is legal where, one field along.
    """
    return tuple(k for k, _, _ in c["bands"])


def throwable_from(c: dict, band: str, punches) -> tuple:
    """Every punch in `punches` that canon authors for `band`, sorted.

    THE SINGLE AUTHORITY ON OFFENCE LEGALITY, which is a question that had two.
    `punch_model.range_gate.band_source` names `data/movement_model.json` as the
    source of the band a punch is judged against, and the move table authors
    each move's band. This returns the set that follows from that; `in_band`
    gates the individual punch with the same test. A chooser that calls this can
    no longer offer a punch the resolver will refuse, because both are reading
    one sentence rather than agreeing about two.

    THE VOCABULARY IS REQUIRED, AND THAT IS THE WHOLE POINT. Canon authors a
    `range_band` for GUARDS and EVASIONS as well as punches - `guard_high` is
    authored `mid` - so "everything canon authors here" is not an offence
    answer at all; it would hand a chooser a guard as something to throw. And
    a caller that forgets to intersect gets a punch its own world cannot fly,
    which is not hypothetical: it is the live ghost-punch defect. Iterating the
    VOCABULARY rather than filtering canon is what makes a ghost structurally
    impossible - a move the caller did not declare is never looked at.

    SORTED BY MOVE ID, because a chooser breaking a tie indexes this result
    with a seeded stream, so the ORDER is part of the simulation's determinism
    and may not depend on dict iteration or canon's array order (Decision 0026).

    AN EMPTY RESULT IS A REAL ANSWER, not a failure. Under today's canon
    `clinch` and `outside` author no punch at all. Whether `outside` SHOULD be
    punch-less is an open Director decision and this function does not
    pre-empt it. An unknown band is a different thing entirely and is refused,
    so a typo can never be mistaken for a band with no offence in it.
    """
    order = band_order(c)
    if band not in order:
        raise KeyError(
            "%r is not a band canon declares (%s). Refused rather than "
            "answered with an empty set, because 'that band has no offence' "
            "and 'that is not a band' are different sentences and only one of "
            "them is a fight." % (band, ", ".join(order)))
    if isinstance(punches, str):
        raise TypeError(
            "throwable_from takes a VOCABULARY of punches, got the string %r. "
            "One move id iterates as characters, so this would have answered "
            "'nothing is legal here' rather than refusing." % (punches,))
    return tuple(sorted(m for m in set(punches) if in_band(c, m, band)))


def bands_without_offence(c: dict, punches) -> tuple:
    """The bands this vocabulary can throw nothing from, closest first.

    The structural fact that cost a twelve-round fight. Two fighters who
    preferred a band with no authored punch threw 3,174 of them into a gate
    that refused every one, and scored 120-120 with no contact in thirty-six
    minutes. Nothing in the model could state the condition that produced it.

    It is a REPORT AND NOT A VERDICT. `out_of_range` belongs by definition;
    whether `clinch` and `outside` belong is canon's business and the
    Director's. What it gives a test is an exact tuple to pin, so the day canon
    changes shape the change is a visible failure rather than a fight that
    quietly stops landing.
    """
    return tuple(b for b in band_order(c)
                 if not throwable_from(c, b, punches))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: one legality authority ]


def step_delta(c: dict, action: str) -> int:
    """Signed change in SEPARATION a step intends, before the per-tick cap.

    `step_lateral` returns zero and that is a knowing simplification, not an
    oversight: separation is one number on one axis here, and the angle a lateral
    step changes has no coordinate to change. It is named in the module docstring
    and in Decision 0013's sequencing rather than left to be discovered.
    """
    if action == "step_in":
        return -c["stride"]
    if action == "step_out":
        return c["stride"]
    return 0


def drain(c: dict, pending: int) -> tuple:
    """One tick of movement: at most the displacement cap, no teleports.

    Returns (applied_this_tick, still_pending). Canon's cap is per FRAME and
    below every stride, so a stride is delivered over more than one tick and a
    fighter can be caught mid-step - which is the whole point of `counter
    vulnerability: moderate; entering is when counters land`.
    """
    if pending == 0:
        return 0, 0
    step = max(-c["cap"], min(c["cap"], pending))
    return step, pending - step


def clamp_separation(c: dict, sep: int) -> int:
    """Bodies do not overlap (Rule 13)."""
    return max(c["min_sep"], sep)


def rope_scaled(c: dict, pos: int, delta: int, opponent: int) -> int:
    """A retreat with your back on the ropes buys nothing.

    Canon's `rope_retreat_multiplier: 0.0`, stated as movement rather than as
    flavour. This is what makes running FINITE: without it a uniform-random
    fighter drifts to out_of_range and stays there, which is not a fighter, and
    it is the exact abuse the ring track block was added to close.

    The rule reads only the retreating fighter's own distance to the edge he is
    backing toward, so it is observable and symmetric. Lateral movement is
    untouched at full rate, which is the boxing answer and stays open.
    """
    if delta == 0:
        return 0
    retreating = (delta < 0) if pos < opponent else (delta > 0)
    if not retreating:
        return delta
    edge = pos if delta < 0 else c["axis"] - pos
    if edge <= c["ropes"]:
        return (delta * c["retreat_mult"]) // 10000
    return delta


def running_is_finite(c: dict) -> bool:
    """A fighter who only ever retreats must stop retreating."""
    pos, opp = c["axis"] // 2 - 4500, c["axis"] // 2 + 4500
    last = None
    for _ in range(200):
        d = rope_scaled(c, pos, -c["cap"], opp)
        pos = max(0, min(c["axis"], pos + d))
        if d == 0:
            return True
        if pos == last:
            return True
        last = pos
    return False


# ---- properties this phase must have, stated so they can be proven ----------

def footwork_is_not_inert(c: dict) -> bool:
    """A step must be able to change the band, or the phase changed nothing."""
    start = q(0.90)                       # the fixed separation every phase used
    band0 = band_at(c, start)
    sep = start
    cur = band0
    for _ in range(20):                   # walk inward, one stride at a time
        sep = clamp_separation(c, sep + step_delta(c, "step_in"))
        cur = resolve_band(c, cur, sep)
        if cur != band0:
            return True
    return False


def hysteresis_kills_flicker(c: dict) -> bool:
    """Sitting exactly on a boundary must not change the band every tick."""
    for _, lo, hi in c["bands"]:
        if hi is None:
            continue
        here = band_at(c, hi - 1)
        # step just over the boundary, but by less than the hysteresis
        if resolve_band(c, here, hi + c["hyst"] // 2) != here:
            return False
    return True
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 13:10 UTC | END ]
