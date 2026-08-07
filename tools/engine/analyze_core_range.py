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

sys.path.insert(0, REPO)
from tools.uppercut_canon.header import canon_header_lines  # noqa: E402
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


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:50 UTC | START ]
"""Phase Q marker stream - the artifact a C++ port has to reproduce.

Everything above this line is the RULE SET: canon read into the integer
contract, four properties stated so they can be proven, no clock. That was
enough to mutation-prove the rules and not enough to prove an implementation,
because an implementation is only proven here when its marker stream is
byte-identical to this module's. So this block adds the clock.

WHAT THIS SLICE DELIBERATELY DOES NOT CONTAIN. No stamina, no guard, no
condition, no damage. Two reasons, and the second is the load-bearing one:

  - they belong to phases N, L and O, which are already proven, and a contract
    that re-implements a proven phase is a second place for it to be wrong;
  - the step cost is an OPEN GATE (G1: priced twice, 0.132 against 0.600, a
    factor of 4.55). A stream that spent stamina would have to be re-blessed
    the day that gate is ruled on, for a reason that has nothing to do with
    range. This stream reads only geometry and bands, so the Director's ruling
    on G1 cannot silently invalidate the Phase Q port.

So this phase reads exactly four canon files and the header names all four:
movement (the bands, the stride, the cap, the ring), moves (which band each
move declares), animation (how long a punch occupies its owner) and pose
geometry (how far a fist travels and where a body's surface is).

ROW KINDS, in the order a reader meets them:

  H  header: phase, the four canon hashes, seed, ticks
  B  one per band: index, key, lo, hi (-1 for the unbounded last band)
  K  the scalars, all of them, before any tick
  M  one per move that declares a band, sorted by move id
  X  movement delivered this tick: applied, both positions, separation, what
     is still owed, flags (m = the body clamp stopped the step)
  R  a band transition: which fighter, from, to, at what separation
  P  a punch resolving: result and REASON, the tip and the surface it was
     tested against, the band it was thrown from, whether that band was legal
  D  a decision: action, the LCG word that chose it, the position line
  V  a property, proven rather than asserted
  S  trailer: counts and the FNV-1a 64 self-hash of every row above

THE INFORMATIVE ROW IS `P`. A punch that fails the band gate still runs its
whole animation and still whiffs at the end of its active window - that is
canon's sentence about the full arc into empty air, made executable. It whiffs
with reason `band` even when the geometry says the fist arrived, which is the
one place where a port that "helpfully" checked geometry first would produce a
different fight and be caught in the first hundred rows.
"""

ANIMATION = os.path.join("data", "animation_model.json")
POSE = os.path.join("data", "pose_geometry.json")

# Nine actions, drawn flat. This is not a policy - policy is Phase S, which
# reads cpu_decision_model and is a different contract. A flat draw is the
# right shape here precisely because it exercises every branch of the range
# pipeline at a rate nothing in this phase can bias.
Q_ACTIONS = ("idle", "step_in", "step_out", "step_lateral",
             "jab_lead", "cross_rear", "hook_lead", "uppercut_rear",
             "body_straight_rear")
Q_PUNCHES = frozenset(Q_ACTIONS[4:])

LCG_A, LCG_C, LCG_M = O.LCG_A, O.LCG_C, O.LCG_M
fnv1a64 = O.fnv1a64


def stream_pack() -> dict:
    """`range_pack` plus the two things a clock needs: how long a move lasts
    and how far a fist reaches.

    Movement is re-read rather than threaded out of `range_pack` so that the
    rule set above keeps exactly the surface it was mutation-proven with. The
    duplication is four lines and it is worth more than the coupling.
    """
    import hashlib
    c = range_pack()
    raw_mv = io.open(os.path.join(REPO, MOVEMENT), "rb").read()
    raw_a = io.open(os.path.join(REPO, ANIMATION), "rb").read()
    raw_p = io.open(os.path.join(REPO, POSE), "rb").read()
    raw_m = io.open(os.path.join(REPO, MOVES), "rb").read()
    mv = json.loads(raw_mv)
    anim = {a["move_id"]: a for a in json.loads(raw_a)["move_animations"]}
    pose = json.loads(raw_p)
    moves = {m["id"]: m for m in json.loads(raw_m)["moves"]}
    d = mv["locomotion"]["directional"]
    c["dir_advance"] = q(d["advance_stride_multiplier"])
    c["dir_retreat"] = q(d["retreat_stride_multiplier"])
    c["dir_lateral"] = q(d["lateral_stride_multiplier"])
    c["half_depth"] = q(pose["body"]["half_depth_ru"])
    c["retracted"] = q(pose["fist"]["retracted_ru"])
    ext_by = {e["move_id"]: q(e["extended_ru"])
              for e in pose["fist"]["extension_by_move"]}
    c["mv"] = {}
    for mid in Q_ACTIONS[1:]:
        m = moves[mid]
        if mid in Q_PUNCHES:
            a = anim[mid]
            c["mv"][mid] = {
                "startup": int(a["startup_ticks"]), "active": int(a["active_ticks"]),
                "frames": int(a["startup_ticks"]) + int(a["active_ticks"])
                          + int(a["recovery_ticks"]),
                "ext": ext_by[mid], "region": m["target_regions"][0]}
        else:
            c["mv"][mid] = {"frames": int(m["startup_frames"])
                                      + int(m["recovery_frames"])}
    c["sha"]["animation"] = hashlib.sha256(raw_a).hexdigest()
    c["sha"]["pose"] = hashlib.sha256(raw_p).hexdigest()
    errs = list(c["canon_errors"])
    # A fist that cannot out-reach a body's own half depth could never touch
    # anybody from any distance, and every landing in the stream would be a
    # clamp artefact rather than a punch.
    for mid in Q_PUNCHES:
        if c["mv"][mid]["ext"] <= c["half_depth"]:
            errs.append("%s extends %d, which does not clear a body half depth "
                        "of %d" % (mid, c["mv"][mid]["ext"], c["half_depth"]))
        if c["mv"][mid]["active"] <= 0:
            errs.append("%s has no active window, so it can never arrive" % mid)
        if mid not in c["move_band"]:
            errs.append("%s declares no range band, so the gate cannot be "
                        "evaluated for it" % mid)
    c["canon_errors"] = errs
    return c


def uppercut_is_reachable(c: dict) -> bool:
    """`the_uppercut_becomes_possible`, restated on this pack.

    Same property, no dependency on Phase O's pack - a port has to prove it
    from the four files this phase declares, not from nine.
    """
    mid_sep = q(0.90)
    if in_band(c, "uppercut_rear", band_at(c, mid_sep)):
        return False
    reach = c["mv"]["uppercut_rear"]["ext"]
    sep, cur = mid_sep, band_at(c, mid_sep)
    for _ in range(20):
        sep = clamp_separation(c, sep + step_delta(c, "step_in"))
        cur = resolve_band(c, cur, sep)
        if in_band(c, "uppercut_rear", cur) and reach >= sep - c["half_depth"]:
            return True
    return False


def expected_stream(seed: int, ticks: int) -> str:
    c = stream_pack()
    lines = ["H|phase=Q"]
    # Decision 0023: dual identities. Migrated 2026-08-07; the whole-file hashes
    # this replaced are recorded in the phase evidence, and not one
    # authoritative row moved.
    lines += canon_header_lines(REPO, [
        ("movement", "data/movement_model.json"),
        ("moves", "data/moves/generic_sandbox_moves.json"),
        ("animation", "data/animation_model.json"),
        ("pose", "data/pose_geometry.json"),
    ])
    lines.append("H|seed=%d" % seed)
    lines.append("H|ticks=%d" % ticks)
    for i, (key, lo, hi) in enumerate(c["bands"]):
        lines.append("B|%d|%s|%d|%d" % (i, key, lo, -1 if hi is None else hi))
    lines.append("K|hyst=%d|stride=%d|cap=%d|min_sep=%d|axis=%d|ropes=%d"
                 "|rope_retreat=%d|advance=%d|retreat=%d|lateral=%d"
                 "|half_depth=%d|retracted=%d"
                 % (c["hyst"], c["stride"], c["cap"], c["min_sep"], c["axis"],
                    c["ropes"], c["retreat_mult"], c["dir_advance"],
                    c["dir_retreat"], c["dir_lateral"], c["half_depth"],
                    c["retracted"]))
    for mid in sorted(c["move_band"]):
        lines.append("M|%s|%s" % (mid, c["move_band"][mid]))

    # Both fighters start at the separation every phase before this one was
    # frozen at: 0.90 ru, mid band. The stream is therefore also the record of
    # what the fight looks like once that freeze is lifted.
    half = c["axis"] // 2
    pos = [half - 4500, half + 4500]
    pending = [0, 0]
    busy = [0, 0]
    punch = [None, None]
    band = [band_at(c, pos[1] - pos[0]), band_at(c, pos[1] - pos[0])]
    x = seed % LCG_M
    rows = []
    n = {"decisions": 0, "idles": 0, "steps": 0, "laterals": 0, "punches": 0,
         "landed": 0, "whiff_band": 0, "whiff_reach": 0, "transitions": 0,
         "roped": 0, "clamped": 0, "moves_applied": 0}
    sep_min, sep_max = pos[1] - pos[0], pos[1] - pos[0]

    for t in range(1, ticks + 1):
        for i in (0, 1):
            # ---- 1. deliver movement already owed, at most the cap ---------
            if pending[i] != 0:
                applied, pending[i] = drain(c, pending[i])
                before = pos[i]
                pos[i] = max(0, min(c["axis"], pos[i] + applied))
                flags = ""
                if pos[1] - pos[0] < c["min_sep"]:
                    if i == 0:
                        pos[0] = pos[1] - c["min_sep"]
                    else:
                        pos[1] = pos[0] + c["min_sep"]
                    pos[0] = max(0, pos[0])
                    pos[1] = min(c["axis"], pos[1])
                    # You cannot keep walking into a body. The rest of the
                    # stride is not banked for later; it is refused now.
                    pending[i] = 0
                    flags += "m"
                    n["clamped"] += 1
                applied = pos[i] - before
                if applied != 0:
                    n["moves_applied"] += 1
                sep = pos[1] - pos[0]
                sep_min = min(sep_min, sep)
                sep_max = max(sep_max, sep)
                rows.append("X|%d|%d|%d|%d|%d|%d|%d|%s"
                            % (t, i, applied, pos[0], pos[1], sep, pending[i],
                               flags or "-"))
                for j in (0, 1):
                    nb = resolve_band(c, band[j], sep)
                    if nb != band[j]:
                        rows.append("R|%d|%d|%s|%s|%d" % (t, j, band[j], nb, sep))
                        band[j] = nb
                        n["transitions"] += 1

            # ---- 2. a punch in flight -------------------------------------
            if punch[i] is not None:
                mid, t0, tband, legal = punch[i]
                mv = c["mv"][mid]
                k = t - t0
                span = mv["startup"] + mv["active"]
                if mv["startup"] < k <= span:
                    tip_ext = c["retracted"] + \
                        ((mv["ext"] - c["retracted"]) * k) // span
                    if i == 0:
                        tip = pos[0] + tip_ext
                        surface = pos[1] - c["half_depth"]
                        arrived = tip >= surface
                    else:
                        tip = pos[1] - tip_ext
                        surface = pos[0] + c["half_depth"]
                        arrived = tip <= surface
                    result = reason = None
                    if arrived and legal:
                        result, reason = "landed", "-"
                        n["landed"] += 1
                    elif k == span:
                        result = "whiffed"
                        # Order matters and it is the phase's whole point: a
                        # punch thrown from the wrong band is refused even
                        # when the fist demonstrably arrived.
                        reason = "band" if not legal else "reach"
                        n["whiff_band" if not legal else "whiff_reach"] += 1
                    if result:
                        rows.append("P|%d|%d|%s|%s|%s|%d|%d|%d|%s|%d"
                                    % (t, i, mid, result, reason, k, tip,
                                       surface, tband, 1 if legal else 0))
                        punch[i] = None
                elif k > span:
                    punch[i] = None

            # ---- 3. commitment --------------------------------------------
            # A step keeps draining while its owner is committed: that is what
            # makes "entering is when counters land" true rather than stated.
            if busy[i] > 0:
                busy[i] -= 1
                continue

            # ---- 4. one decision ------------------------------------------
            x = (LCG_A * x + LCG_C) % LCG_M
            action = Q_ACTIONS[x % len(Q_ACTIONS)]
            n["decisions"] += 1
            mark = "-"
            if action == "idle":
                n["idles"] += 1
            elif action in Q_PUNCHES:
                mv = c["mv"][action]
                busy[i] = mv["frames"]
                legal = in_band(c, action, band[i])
                punch[i] = (action, t, band[i], legal)
                n["punches"] += 1
                mark = "1" if legal else "0"
            else:
                busy[i] = c["mv"][action]["frames"]
                n["steps"] += 1
                if action == "step_lateral":
                    # Knowingly inert on one axis. Declared here, in the row,
                    # rather than left for a reader to infer from a zero.
                    n["laterals"] += 1
                    mark = "l"
                else:
                    toward = 1 if i == 0 else -1
                    sign = toward if action == "step_in" else -toward
                    mul = c["dir_advance"] if action == "step_in" \
                        else c["dir_retreat"]
                    delta = sign * ((c["stride"] * mul) // 10000)
                    scaled = rope_scaled(c, pos[i], delta, pos[1 - i])
                    if scaled != delta:
                        n["roped"] += 1
                        mark = "r"
                    pending[i] = scaled
            rows.append("D|%d|%d|%s|%d|%d|%d|%d|%s|%d|%s"
                        % (t, i, action, x, pos[0], pos[1], pos[1] - pos[0],
                           band[i], pending[i], mark))

    # ---- properties, inside the hash so a port has to prove them too -------
    for name, ok in (("footwork_is_not_inert", footwork_is_not_inert(c)),
                     ("uppercut_is_reachable", uppercut_is_reachable(c)),
                     ("hysteresis_kills_flicker", hysteresis_kills_flicker(c)),
                     ("running_is_finite", running_is_finite(c))):
        rows.append("V|%s|%d" % (name, 1 if ok else 0))
    rows.append("V|canon_errors|%d" % len(c["canon_errors"]))

    h = fnv1a64("".join(l + "\n" for l in rows).encode("utf-8"))
    lines += rows
    lines.append("S|rows=%d|decisions=%d|idles=%d|steps=%d|laterals=%d"
                 "|punches=%d|landed=%d|whiff_band=%d|whiff_reach=%d"
                 "|transitions=%d|roped=%d|clamped=%d|applied=%d"
                 "|sep_min=%d|sep_max=%d|fnv1a64=%016x"
                 % (len(rows), n["decisions"], n["idles"], n["steps"],
                    n["laterals"], n["punches"], n["landed"], n["whiff_band"],
                    n["whiff_reach"], n["transitions"], n["roped"],
                    n["clamped"], n["moves_applied"], sep_min, sep_max, h))
    return "\n".join(lines) + "\n"


def analyse(path: str) -> dict:
    """Read a stream back and re-derive its claims from the rows themselves.

    This is deliberately NOT a comparison against `expected_stream`. A port is
    proven by byte equality, which the runner checks; this function asks a
    different question - whether the artifact is internally coherent - so that
    a stream produced by two agreeing but identically wrong implementations
    still has somewhere left to fail.
    """
    c = stream_pack()
    rows = [l.rstrip("\n") for l in io.open(path, "r", encoding="utf-8")
            if l.strip()]
    body = [r for r in rows if not r.startswith(("H|", "B|", "K|", "M|", "S|"))]
    trailer = next(r for r in rows if r.startswith("S|"))
    fields = dict(kv.split("=", 1) for kv in trailer.split("|")[1:])
    errs = []
    if int(fields["rows"]) != len(body):
        errs.append("the trailer counts %s rows and the file carries %d"
                    % (fields["rows"], len(body)))
    h = fnv1a64("".join(r + "\n" for r in body).encode("utf-8"))
    if "%016x" % h != fields["fnv1a64"]:
        errs.append("the self-hash does not cover the rows: %016x vs %s"
                    % (h, fields["fnv1a64"]))
    counts = {"landed": 0, "whiff_band": 0, "whiff_reach": 0, "transitions": 0}
    order = [k for k, _, _ in c["bands"]]
    for r in body:
        f = r.split("|")
        if f[0] == "X":
            if abs(int(f[3])) > c["cap"]:
                errs.append("tick %s moved %s, past the displacement cap %d"
                            % (f[1], f[3], c["cap"]))
            if int(f[6]) < c["min_sep"]:
                errs.append("tick %s left a separation of %s, inside the body "
                            "floor %d" % (f[1], f[6], c["min_sep"]))
        elif f[0] == "R":
            counts["transitions"] += 1
            if abs(order.index(f[3]) - order.index(f[4])) != 1:
                errs.append("tick %s skipped from %s to %s without passing "
                            "through the band between them" % (f[1], f[3], f[4]))
        elif f[0] == "P":
            if f[4] == "landed":
                counts["landed"] += 1
                if f[10] != "1":
                    errs.append("tick %s landed %s from %s, a band it does not "
                                "declare" % (f[1], f[3], f[9]))
            elif f[5] == "band":
                counts["whiff_band"] += 1
            elif f[5] == "reach":
                counts["whiff_reach"] += 1
        elif f[0] == "V" and f[1] != "canon_errors" and f[2] != "1":
            errs.append("the stream reports property %s as unproven" % f[1])
    for k, v in counts.items():
        if int(fields[k]) != v:
            errs.append("the trailer claims %s=%s and the rows show %d"
                        % (k, fields[k], v))
    return {"rows": len(body), "counts": counts, "errors": errs}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:50 UTC | END ]
