# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 07:00 UTC | START ]
"""Phase Q marker contract - the fight gets a distance.

WHY THIS PHASE EXISTS, measured rather than argued. The reference simulator
reaches the cards in 20 of 24 bouts with canon's own numbers; this core reaches
them in 0 of 24, and the 16.7x knockdowns-per-minute gap between them factorises
exactly into volume 5.8x, accuracy 1.3x and lethality 2.3x. Two of those three
are one omission: the core implements the reference's RESOLUTION pipeline and
skips its RANGE pipeline. Both fighters have stood at one fixed separation since
Phase H, so:

  - every punch is always available, and the action set is thrown flat;
  - `step_in`, `step_out` and `step_lateral` are chosen 3 times in 11, cost
    stamina, cost commitment, and MOVE NOTHING - the declared-but-inert class
    this repository keeps a checker for, sitting in the action set the whole time;
  - `uppercut_rear` is an inside-band punch thrown all night from mid range: 532
    thrown, 0 landed, 28.8% of the entire punch stamina budget burned for nothing;
  - `hook_lead`, also an inside-band punch, has been LANDING from mid range,
    which is the same defect wearing the opposite sign.

Nothing in this phase is invented. Every number below is read from canon:

    movement_model.range_bands      clinch/inside/mid/outside/out_of_range
    movement_model.range_bands      hysteresis_ru 0.05
    movement_model.locomotion       boxing_steps stride 0.22 ru
    movement_model.max_frame_displacement_ru   0.14, the per-tick cap
    movement_model.separation       min_center_distance_ru 0.28
    punch_model.range_gate          wrong band -> whiffed, full commitment
    data/moves/*.range_band         which band each move belongs to

THE ONE RULE, and it is canon's sentence not mine: "A punch thrown from the wrong
band travels its full arc into empty air and pays the whiff. No invisible lunge
closes the gap, and no magnetic correction shortens it." So the band is tested at
THROW time, when the fighter commits, and a doomed punch still occupies its
frames and still costs its stamina. That is what makes range a decision rather
than a filter.

GEOMETRY AND BAND ARE BOTH REQUIRED, and they are not the same test. The band is
the authored intent - what a boxer is trying to do from where he stands. The
geometric tip-versus-surface test is the physical check that survived from Phase
K. A punch must pass both, and where they disagree the disagreement is
information: the uppercut's 0.72 reach failing at 0.90 separation was geometry
agreeing with a band table nobody had consulted.

SCOPE. Separation is one number on one axis, which is the same simplification
Phase K's lanes make. `step_lateral` therefore still changes nothing, and is
recorded here as knowingly inert rather than quietly so - the angle it changes
needs the 2D geometry `pose_geometry` flags as pending and Decision 0013
sequences after this. Evasion (`slip_lead`, `roll_under`) is likewise NOT in this
phase: it is the third factor in the reference gap and it deserves its own
contract rather than being bolted to this one.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_round as O  # noqa: E402

REPO = O.REPO
q = O.q

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
        # `rope_retreat_multiplier: 0.0` is the whole anti-running rule - with
        # your back on the ropes a backward step buys nothing, while lateral
        # movement stays fully available at full rate.
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
    """
    return c["move_band"].get(move_id) == band


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


def the_uppercut_becomes_possible(c: dict) -> bool:
    """The defect that started this phase must be reachable, not merely named.

    `uppercut_rear` is an inside-band punch. At the separation every phase has
    used it is illegal AND out of geometric reach; there must exist a separation
    a fighter can walk to where it is both legal and reaches.
    """
    mid = q(0.90)
    if in_band(c, "uppercut_rear", band_at(c, mid)):
        return False                      # it should NOT be legal at mid
    core = O.canon_pack()
    reach = core["moves"]["uppercut_rear"]["ext"]
    sep = mid
    cur = band_at(c, mid)
    for _ in range(20):
        sep = clamp_separation(c, sep + step_delta(c, "step_in"))
        cur = resolve_band(c, cur, sep)
        if in_band(c, "uppercut_rear", cur) and reach >= sep - core["half_depth"]:
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
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 07:00 UTC | END ]
