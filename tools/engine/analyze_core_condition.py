# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | START ]
"""Phase N marker contract and analyzer - visible stamina and condition.

Decision 0012 slice item 8: landing starts to matter. Phase L's guard-and-slip
core gains the condition layer canon has carried since step 8, and the point of
the phase is that ONE mechanism has to emerge rather than be written:

  1. PER-REGION CONDITION (condition_model.damage_regions, Rule 14). A landing
     accumulates into the region the move targets - head, jaw_chin, torso_upper,
     torso_lower - each against its own capacity. There is no generic pool. A
     BLOCKED punch is not free either: arm_damage_fraction_of_blocked_force of
     its impact goes into both guarding arms, which is canon's own answer to the
     passive blocker (Rule 4 - through boxing, not through a rule).
  2. FORCE IS WHAT THE PUNCH COST (punch_model.delivered_impact). Impact is the
     move's stamina_cost normalized over the punch table's own range, so a jab
     accumulates and an uppercut ends nights, and no per-move power field has to
     exist for that to be true.
  3. THE BODY SLOWS THE TANK (impairment.stamina_regen_multiplier_at_full_torso).
     Torso condition scales idle regeneration down toward 0.35. Body work stops
     being cosmetic accumulation and becomes the drainer's win condition.
  4. THE ARMS OPEN THE GUARD - and this is the emergence the stream must show.
     impairment.guard_extent_multiplier_at_full_arms scales coverage extents
     toward 0.55 as the arms take blocked force. Coverage is therefore no longer
     a per-posture constant computable at load: it is evaluated per punch, per
     fighter, per tick, against pose_geometry's one interception threshold. A
     high guard that never drops still opens, because 0.95 x 0.55 = 0.5225 is
     below the 0.6 threshold and punches that were being blocked begin to land.
     Nobody wrote "guards break under pressure" - it falls out of two authored
     coefficients meeting one authored threshold.

     The S trailer counts those landings as `opened`, and the analyzer FAILS if
     the count is zero on a run long enough to reach it: a mechanism that never
     fires is indistinguishable from a mechanism that is not there.

     THE FINDING THIS PHASE PRODUCED (2026-08-04). Building it exposed that the
     erosion is authored but effectively unreachable. Opening high_guard's head
     lane needs the extent below 0.6, and 0.95 x (1 - 0.45f) < 0.6 requires arm
     condition f >= 0.819 of capacity. A blocked punch delivers impact x 0.5 into
     each arm - between 0.225 and 0.412 of a 100-point capacity - so it takes
     roughly 243 blocked punches on one fighter to break his guard. This probe
     blocks about one punch per 430 ticks, so the lane first opens at ~216,000
     ticks: an HOUR of continuous fighting. A twelve-round bout is ~130,000 ticks
     of round time, and damage_regions gives arms 0.15 recovery between rounds,
     which this phase does not yet implement and which would push it further out
     of reach. The mechanism is correct, live and proven at the reachability
     horizon below; whether canon's coefficients put it inside a real fight is a
     tuning question for the Director, and it is on the record rather than
     quietly passing.

Named simplifications, on the record, in the tradition of Phase J's hook and
Phase L's posture economics:
  - Every landing is graded SOLID. Alignment and the quality bands port with the
    fuller collision pipeline; grading a landing needs an alignment the core does
    not compute yet, so the contract names one band rather than inventing four.
  - No attributes. There are no fighter cards in the probes, so every
    attribute-scaled coefficient (condition_accumulation, delivered_impact,
    body_shot_force) is the empty card's 1.0 - which is what makes an empty card
    the baseline (Rule 10).
  - No knockdown, no count, no between-rounds recovery. Condition accumulates and
    impairs; what happens when it crosses a line is slice item 9, with the cards
    and the stoppage paths that make a knockdown mean something.

Actions (x mod 11): unchanged from Phase L.

Stream (H|phase=N, Phase L's eight canon files plus punch_model):
  D|t|i|action|x|pos0|pos1|sep|band|st0|st1|g0|g1|flags     - unchanged from L
  P|t|i|move|result|region|k|tip|plane|surface|dflags|force|dext
      force: delivered force in 1e-4 units (0 unless landed)
      dext:  the defender's EFFECTIVE extent in this punch's lane at evaluation,
             after arm damage and committed defense - the auditable why of a
             blocked-or-landed call
  C|t|i|head|jaw|tup|tlow|aleft|aright|regen_mult|guard_mult  - at each decision
  F|k|bits (float probe, reported not judged)
  S|rows=..|punches=..|blocked=..|landed=..|whiffed=..|dodged=..|steps=..
   |switches=..|slips=..|held=..|idles=..|transitions=..|damage=..|opened=..
   |fnv1a64=..

Usage: python analyze_core_condition.py <markers.txt> [...]
"""
import hashlib
import io
import json
import os
import struct
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

LCG_A, LCG_C, LCG_M = 1664525, 1013904223, 2 ** 32
FNV_OFFSET, FNV_PRIME = 14695981039346656037, 1099511628211

CANON = {
    "movement": "data/movement_model.json",
    "condition": "data/condition_model.json",
    "guard": "data/guard_evasion_model.json",
    "cpu": "data/cpu_decision_model.json",
    "moves": "data/moves/generic_sandbox_moves.json",
    "animation": "data/animation_model.json",
    "collision": "data/collision_model.json",
    "pose": "data/pose_geometry.json",
    "punch": "data/punch_model.json",
}
CANON_ORDER = ("movement", "condition", "guard", "cpu", "moves", "animation",
               "collision", "pose", "punch")

ACTIONS = ("step_in", "step_out", "step_lateral", "jab_lead", "cross_rear",
           "hook_lead", "uppercut_rear", "body_straight_rear", "switch_guard",
           "slip_lead", "idle")
PUNCHES = ("jab_lead", "cross_rear", "hook_lead", "uppercut_rear", "body_straight_rear")
POSTURES = ("high_guard", "tight_elbow")
GCHAR = {"high_guard": "h", "tight_elbow": "t"}
REGIONS = ("head", "jaw_chin", "torso_upper", "torso_lower", "arm_left", "arm_right")
GRADED = "solid"        # the named simplification, in one place
# The reachability horizon: the run length at which arm erosion first opens a
# lane at canon's authored coefficients. Measured, not chosen - see the module
# docstring's finding. A run at or beyond this MUST demonstrate the mechanism;
# a shorter run is not expected to and says so rather than failing.
REACH_TICKS = 216000


def fnv1a64(data: bytes) -> int:
    h = FNV_OFFSET
    for b in data:
        h = ((h ^ b) * FNV_PRIME) % (2 ** 64)
    return h


def q(v) -> int:
    return round(float(v) * 10000)


def canon_pack() -> dict:
    raw = {k: io.open(os.path.join(REPO, p), "rb").read() for k, p in CANON.items()}
    sha = {k: hashlib.sha256(b).hexdigest() for k, b in raw.items()}
    mv = json.loads(raw["movement"])
    cm = json.loads(raw["condition"])
    ge = json.loads(raw["guard"])
    cpu = json.loads(raw["cpu"])
    moves = {m["id"]: m for m in json.loads(raw["moves"])["moves"]}
    anim = {a["move_id"]: a for a in json.loads(raw["animation"])["move_animations"]}
    col = json.loads(raw["collision"])
    pose = json.loads(raw["pose"])
    pm = json.loads(raw["punch"])
    rb = mv["range_bands"]
    st = cm["stamina"]

    postures = {p["id"]: p for p in ge["postures"]}
    vol_by_class = {gv["height_class"]: gv["id"] for gv in col["volumes"]["guard_volumes"]}
    thr = q(pose["guard"]["plane_interception_min_extent"])
    cd_mult = q(ge["committed_defense"]["guard_extent_multiplier_while_committed"])

    slip = next(e for e in ge["evasions"] if e["id"] == "slip_lead")
    slip_mv = moves["slip_lead"]
    hmap = {e["guard_interaction"]: e["height_class"]
            for e in pose["height_by_guard_interaction"]}
    ext_by_move = {e["move_id"]: q(e["extended_ru"])
                   for e in pose["fist"]["extension_by_move"]}

    # delivered_impact: normalized over the PUNCH table's own stamina range, the
    # same set canon.punches() selects - offensive categories only, so a step's
    # cost can never move a punch's power.
    offensive = {"jab", "cross", "hook", "uppercut", "overhand", "body_shot"}
    pcosts = [q(m["stamina_cost"]) for m in moves.values()
              if m.get("category") in offensive]
    di = pm["delivered_impact"]
    imp = cm["impairment"]
    band_force = {b["class"]: q(b["delivered_force_fraction"])
                  for b in col["quality_bands"]}
    caps = {d["region"]: q(d["capacity"]) for d in cm["damage_regions"]}

    c = {
        "sha": sha,
        "bmin": [q(b["min_ru"]) for b in rb["bands"]],
        "bmax": [990000 if b.get("max_ru") is None else q(b["max_ru"]) for b in rb["bands"]],
        "hyst": q(rb["hysteresis_ru"]),
        "axis": q(mv["ring"]["track"]["axis_length_ru"]),
        "ropes": q(mv["ring"]["track"]["back_to_ropes_ru"]),
        "rope_retreat": q(mv["ring"]["track"]["rope_retreat_multiplier"]),
        "min_sep": q(mv["separation"]["min_center_distance_ru"]),
        "stride": q(next(m["stride_length_ru"] for m in mv["locomotion"]["modes"]
                         if m["posture_mode"] == "boxing_steps")),
        "dir": {k: q(mv["locomotion"]["directional"][k + "_stride_multiplier"])
                for k in ("advance", "retreat", "lateral", "exhausted")},
        "st_max": q(st["max"]),
        "regen": q(st["regen_per_tick_idle"]),
        "exhausted_q": round(q(st["max"]) * float(st["exhausted_threshold_fraction"])),
        "interval": int(cpu["reaction"]["decision_interval_ticks"]),
        "half_depth": q(pose["body"]["half_depth_ru"]),
        "plane_off": q(pose["guard"]["plane_offset_ru"]),
        "retracted": q(pose["fist"]["retracted_ru"]),
        "thr": thr,
        "cd_mult": cd_mult,
        "vol_by_class": vol_by_class,
        "posture": {pid: {"mobility": q(postures[pid]["mobility_multiplier"]),
                          "hold": q(postures[pid]["stamina_per_tick"]),
                          "ext": {hc: q(postures[pid]["extents"].get(vid, 0.0))
                                  for hc, vid in vol_by_class.items()}}
                    for pid in POSTURES},
        "slip_cost": q(slip_mv["stamina_cost"]),
        "slip_startup": int(slip_mv["startup_frames"]),
        "slip_active": int(slip["active_ticks"]),
        "slip_frames": int(slip_mv["startup_frames"]) + int(slip["active_ticks"])
                       + int(slip_mv["recovery_frames"]),
        # the condition layer
        "cap": caps,
        "imp_min": q(di["min_impact_scalar"]),
        "imp_max": q(di["max_impact_scalar"]),
        "cost_lo": min(pcosts),
        "cost_hi": max(pcosts),
        "band_force": band_force[GRADED],
        "regen_floor": q(imp["stamina_regen_multiplier_at_full_torso"]),
        "guard_floor": q(imp["guard_extent_multiplier_at_full_arms"]),
        "arm_frac": q(imp["arm_damage_fraction_of_blocked_force"]),
        "moves": {},
        "f_cost": float(moves["jab_lead"]["stamina_cost"]),
        "f_regen": float(st["regen_per_tick_idle"]),
        "f_max": float(st["max"]),
        "f_hold": float(postures["high_guard"]["stamina_per_tick"]),
    }
    for mid in ("jab_lead", "cross_rear", "hook_lead", "uppercut_rear",
                "body_straight_rear", "step_in", "step_out", "step_lateral"):
        m = moves[mid]
        d = {"cost": q(m["stamina_cost"])}
        if mid in PUNCHES:
            a = anim[mid]
            d.update(startup=int(a["startup_ticks"]), active=int(a["active_ticks"]),
                     frames=int(a["startup_ticks"]) + int(a["active_ticks"])
                     + int(a["recovery_ticks"]),
                     ext=ext_by_move[mid],
                     height=hmap[m["guard_interaction"]],
                     region=m["target_regions"][0],
                     impact=impact_q(c, q(m["stamina_cost"])))
        else:
            d["frames"] = int(m["startup_frames"]) + int(m["recovery_frames"])
        c["moves"][mid] = d

    errs = []
    for pid in POSTURES:
        for hc, ext in c["posture"][pid]["ext"].items():
            fresh = ext >= thr
            worn = (ext * c["guard_floor"]) // 10000 >= thr
            if fresh and not worn:
                break
        else:
            continue
        break
    else:
        errs.append("no posture lane can be opened by arm damage alone - the "
                    "impairment coefficient and the interception threshold never "
                    "meet, so the phase's whole emergence is unreachable")
    if c["cost_hi"] <= c["cost_lo"]:
        errs.append("the punch table has no stamina_cost range, so delivered impact "
                    "cannot distinguish a jab from an uppercut")
    if c["regen_floor"] >= 10000:
        errs.append("torso damage does not slow regeneration - body work would be "
                    "cosmetic, which is the defect impairment was authored to fix")
    for r in REGIONS:
        if r not in caps:
            errs.append(f"condition region {r} has no declared capacity")
    c["canon_errors"] = errs
    return c


def impact_q(c: dict, cost_q: int) -> int:
    """punch_model.delivered_impact, in fixed point. Integer throughout so the
    C++ and the Python cannot drift on a rounding mode."""
    t = ((cost_q - c["cost_lo"]) * 10000) // (c["cost_hi"] - c["cost_lo"])
    return c["imp_min"] + (t * (c["imp_max"] - c["imp_min"])) // 10000


def float_probe(c: dict, iters: int = 1000, every: int = 100) -> list:
    out = []
    s = c["f_max"]
    for k in range(1, iters + 1):
        s = s - c["f_cost"] / 4.0
        s = s + c["f_regen"] * 3.0
        s = s * 0.9995
        s = s + c["f_hold"]
        if s > c["f_max"]:
            s = c["f_max"]
        if k % every == 0:
            bits = struct.unpack("<Q", struct.pack("<d", s))[0]
            out.append(f"F|{k}|{bits:016x}")
    return out


def _ext(c: dict, mid: str, m: int) -> int:
    mv = c["moves"][mid]
    return c["retracted"] + ((mv["ext"] - c["retracted"]) * m) // (mv["startup"] + mv["active"])


def _frac(cond: dict, c: dict, a: str, b: str) -> int:
    """Mean of two regions as a 0..10000 fraction of capacity."""
    return ((cond[a] * 10000) // c["cap"][a] + (cond[b] * 10000) // c["cap"][b]) // 2


def _regen_mult(cond: dict, c: dict) -> int:
    torso = _frac(cond, c, "torso_upper", "torso_lower")
    return 10000 - ((10000 - c["regen_floor"]) * torso) // 10000


def _guard_mult(cond: dict, c: dict) -> int:
    arms = _frac(cond, c, "arm_left", "arm_right")
    return 10000 - ((10000 - c["guard_floor"]) * arms) // 10000


def _extent(c: dict, posture: str, height: str, gmult: int, committed: bool) -> int:
    """The defender's effective coverage extent in one lane, at this moment.

    Phase L could precompute coverage per posture. It cannot be precomputed here:
    the arms wear down, so the same guard covers less as the round goes on. This
    is the whole phase in one function."""
    e = c["posture"][posture]["ext"][height]
    e = (e * gmult) // 10000
    if committed:
        e = (e * c["cd_mult"]) // 10000
    return e


def expected_stream(seed: int, ticks: int, with_floats: bool = True) -> str:
    c = canon_pack()
    lines = ["H|phase=N"]
    lines += [f"H|canon_{k}={c['sha'][k]}" for k in CANON_ORDER]
    lines += [f"H|seed={seed}", f"H|ticks={ticks}", f"H|interval={c['interval']}",
              f"H|graded={GRADED}"]

    pos = [c["axis"] // 2 - 4500, c["axis"] // 2 + 4500]
    st = [c["st_max"], c["st_max"]]
    cond = [{r: 0 for r in REGIONS}, {r: 0 for r in REGIONS}]
    committed = [0, 0]
    punch = [None, None]
    posture = ["high_guard", "high_guard"]
    slip_until = [0, 0]
    slip_from = [10 ** 9, 10 ** 9]
    band = 2
    x = seed % LCG_M
    rows = []
    counts = {"punches": 0, "blocked": 0, "landed": 0, "whiffed": 0, "dodged": 0,
              "steps": 0, "switches": 0, "slips": 0, "held": 0, "idles": 0}
    transitions = 0
    damage_total = 0
    opened = 0

    for t in range(1, ticks + 1):
        for i in (0, 1):
            if punch[i] is not None:
                mid, t0 = punch[i]
                mv = c["moves"][mid]
                k = t - t0
                if mv["startup"] < k <= mv["startup"] + mv["active"]:
                    tip_ext = _ext(c, mid, k)
                    opp = 1 - i
                    if i == 0:
                        tip = pos[0] + tip_ext
                        surface = pos[1] - c["half_depth"]
                        plane = surface - c["plane_off"]
                        arrived_plane = tip >= plane
                        arrived_surface = tip >= surface
                    else:
                        tip = pos[1] - tip_ext
                        surface = pos[0] + c["half_depth"]
                        plane = surface + c["plane_off"]
                        arrived_plane = tip <= plane
                        arrived_surface = tip <= surface
                    d_committed = committed[opp] > 0
                    d_slipping = slip_from[opp] < t <= slip_until[opp]
                    gmult = _guard_mult(cond[opp], c)
                    dext = _extent(c, posture[opp], mv["height"], gmult, d_committed)
                    fresh = _extent(c, posture[opp], mv["height"], 10000, d_committed)
                    dflags = (("c" if d_committed else "") + ("s" if d_slipping else "")
                              + GCHAR[posture[opp]])
                    result = region = None
                    force = 0
                    if (arrived_plane or arrived_surface) and d_slipping \
                            and mv["height"] == "high":
                        result, region = "dodged", "-"
                    elif arrived_plane and dext >= c["thr"]:
                        result, region = "blocked", "-"
                        # Blocking is not free: the guarding arms take a share of
                        # the impact, and that is what erodes the extent above.
                        absorbed = (mv["impact"] * c["arm_frac"]) // 10000
                        for arm in ("arm_left", "arm_right"):
                            cond[opp][arm] = min(c["cap"][arm], cond[opp][arm] + absorbed)
                    elif arrived_surface:
                        result, region = "landed", mv["region"]
                        force = (c["band_force"] * mv["impact"]) // 10000
                        cond[opp][region] = min(c["cap"][region],
                                                cond[opp][region] + force * 6)
                        damage_total += force * 6
                        # Did this land only because the arms had worn the guard
                        # below the threshold? That is the phase's claim, counted.
                        if fresh >= c["thr"] and dext < c["thr"]:
                            opened += 1
                    elif k == mv["startup"] + mv["active"]:
                        result, region = "whiffed", "-"
                    if result:
                        counts[result] += 1
                        rows.append(f"P|{t}|{i}|{mid}|{result}|{region}|{k}"
                                    f"|{tip}|{plane}|{surface}|{dflags}|{force}|{dext}")
                        punch[i] = None
                elif k > mv["startup"] + mv["active"]:
                    punch[i] = None
            if committed[i] > 0:
                committed[i] -= 1
                held = True
            else:
                # A worked body refills slower. The multiplier is applied to the
                # regeneration, never to the drain: nothing here can make holding
                # a guard cheaper than it is authored to be.
                st[i] = min(c["st_max"],
                            st[i] + (c["regen"] * _regen_mult(cond[i], c)) // 10000)
                st[i] = max(0, st[i] - c["posture"][posture[i]]["hold"])
                held = False
            if t % c["interval"] != 0:
                continue
            rows.append(f"C|{t}|{i}|{cond[i]['head']}|{cond[i]['jaw_chin']}"
                        f"|{cond[i]['torso_upper']}|{cond[i]['torso_lower']}"
                        f"|{cond[i]['arm_left']}|{cond[i]['arm_right']}"
                        f"|{_regen_mult(cond[i], c)}|{_guard_mult(cond[i], c)}")
            g = f"{GCHAR[posture[0]]}|{GCHAR[posture[1]]}"
            if held or committed[i] > 0:
                counts["held"] += 1
                rows.append(f"D|{t}|{i}|held|0|{pos[0]}|{pos[1]}|{pos[1]-pos[0]}|{band}"
                            f"|{st[0]}|{st[1]}|{g}|-")
                continue
            x = (LCG_A * x + LCG_C) % LCG_M
            action = ACTIONS[x % 11]
            flags = ""
            if action == "idle":
                counts["idles"] += 1
            elif action == "switch_guard":
                posture[i] = "tight_elbow" if posture[i] == "high_guard" else "high_guard"
                committed[i] = c["interval"]
                counts["switches"] += 1
                g = f"{GCHAR[posture[0]]}|{GCHAR[posture[1]]}"
            elif action == "slip_lead":
                st[i] = max(0, st[i] - c["slip_cost"])
                committed[i] = c["slip_frames"]
                slip_from[i] = t + c["slip_startup"]
                slip_until[i] = t + c["slip_startup"] + c["slip_active"]
                counts["slips"] += 1
            elif action in PUNCHES:
                mv = c["moves"][action]
                st[i] = max(0, st[i] - mv["cost"])
                committed[i] = mv["frames"]
                punch[i] = (action, t)
                counts["punches"] += 1
            else:
                mv = c["moves"][action]
                st[i] = max(0, st[i] - mv["cost"])
                committed[i] = mv["frames"]
                counts["steps"] += 1
                mul = {"step_in": c["dir"]["advance"], "step_out": c["dir"]["retreat"],
                       "step_lateral": c["dir"]["lateral"]}[action]
                mul = (mul * c["posture"][posture[i]]["mobility"]) // 10000
                if st[i] < c["exhausted_q"]:
                    mul = (mul * c["dir"]["exhausted"]) // 10000
                    flags += "e"
                if action != "step_lateral":
                    toward = 1 if i == 0 else -1
                    sign = toward if action == "step_in" else -toward
                    on_ropes = min(pos[i], c["axis"] - pos[i]) <= c["ropes"]
                    if on_ropes and action == "step_out":
                        mul = (mul * c["rope_retreat"]) // 10000
                        flags += "r"
                    mag = (c["stride"] * mul) // 10000
                    pos[i] = min(max(pos[i] + sign * mag, 0), c["axis"])
                    if pos[1] - pos[0] < c["min_sep"]:
                        if i == 0:
                            pos[0] = pos[1] - c["min_sep"]
                        else:
                            pos[1] = pos[0] + c["min_sep"]
                        pos[0] = max(0, pos[0])
                        pos[1] = min(c["axis"], pos[1])
                        flags += "m"
                    sep = pos[1] - pos[0]
                    lo = c["bmin"][band] - c["hyst"]
                    hi = c["bmax"][band] + c["hyst"]
                    nxt = band + (1 if sep > hi else 0) - (1 if sep < lo else 0)
                    nxt = max(0, min(len(c["bmin"]) - 1, nxt))
                    if nxt != band:
                        transitions += 1
                    band = nxt
            rows.append(f"D|{t}|{i}|{action}|{x}|{pos[0]}|{pos[1]}|{pos[1]-pos[0]}|{band}"
                        f"|{st[0]}|{st[1]}|{g}|{flags or '-'}")

    h = fnv1a64("".join(l + "\n" for l in rows).encode("utf-8"))
    lines += rows
    if with_floats:
        lines += float_probe(c)
    lines.append(f"S|rows={len(rows)}|punches={counts['punches']}|blocked={counts['blocked']}"
                 f"|landed={counts['landed']}|whiffed={counts['whiffed']}|dodged={counts['dodged']}"
                 f"|steps={counts['steps']}|switches={counts['switches']}|slips={counts['slips']}"
                 f"|held={counts['held']}|idles={counts['idles']}"
                 f"|transitions={transitions}|damage={damage_total}|opened={opened}"
                 f"|fnv1a64={h:016x}")
    return "\n".join(lines) + "\n"


def analyse(path: str) -> dict:
    rep = {"file": os.path.basename(path), "errors": [], "notes": []}
    c = canon_pack()
    rep["errors"].extend(c["canon_errors"])
    text = io.open(path, encoding="utf-8").read()
    lines = [l for l in text.splitlines() if l]
    heads = {l.split("=", 1)[0][2:]: l.split("=", 1)[1]
             for l in lines if l.startswith("H|") and "=" in l}
    for need in ("seed", "ticks"):
        if need not in heads:
            rep["errors"].append(f"missing header H|{need}=")
    if rep["errors"]:
        rep["ok"] = False
        return rep
    seed, ticks = int(heads["seed"]), int(heads["ticks"])
    rep["seed"], rep["ticks"] = seed, ticks
    if heads.get("graded") != GRADED:
        rep["errors"].append("the stream does not declare the graded simplification "
                             "this contract is written against")

    for k in CANON_ORDER:
        if heads.get("canon_" + k) != c["sha"][k]:
            rep["errors"].append(f"canon_{k} hash does not match the local file")

    got_core = "\n".join(l for l in lines if not l.startswith("F|")) + "\n"
    want = expected_stream(seed, ticks, with_floats=False)
    if got_core != want:
        for n, (g, w) in enumerate(zip(got_core.splitlines(), want.splitlines()), 1):
            if g != w:
                rep["errors"].append(f"core stream diverges at line {n}: got {g!r}, "
                                     f"expected {w!r}")
                break
        else:
            rep["errors"].append("core stream length differs from canon recomputation")

    got_f = [l for l in lines if l.startswith("F|")]
    if not got_f:
        rep["notes"].append("float probe absent from stream")
    elif got_f == float_probe(c):
        rep["notes"].append(f"float probe: all {len(got_f)} checkpoints BIT-IDENTICAL "
                            f"to CPython doubles")
    else:
        rep["notes"].append("float probe: DIVERGES - a finding, not a failure")

    # ---- independent properties, checked against canon rather than the recomputation
    prow = [l.split("|") for l in lines if l.startswith("P|")]
    crow = [l.split("|") for l in lines if l.startswith("C|")]
    for r in prow:
        mid, result, region, k = r[3], r[4], r[5], int(r[6])
        force, dext = int(r[11]), int(r[12])
        mv = c["moves"].get(mid, {})
        if not (mv.get("startup", 0) < k <= mv.get("startup", 0) + mv.get("active", 0)):
            rep["errors"].append(f"punch resolved outside its active window ({mid}, k={k})")
        if result == "landed":
            if region != mv.get("region"):
                rep["errors"].append(f"{mid} landed on {region}, not its leading target region")
            if force != (c["band_force"] * mv["impact"]) // 10000:
                rep["errors"].append(f"{mid} delivered a force its cost does not justify")
            if dext >= c["thr"]:
                rep["errors"].append(f"{mid} landed through a lane that was still covered "
                                     f"(extent {dext} >= threshold {c['thr']})")
        if result == "blocked":
            if dext < c["thr"]:
                rep["errors"].append(f"{mid} was blocked by an open lane "
                                     f"(extent {dext} < threshold {c['thr']})")
            if force != 0:
                rep["errors"].append(f"{mid} delivered force through a block")
        if result in ("whiffed", "dodged") and force != 0:
            rep["errors"].append(f"a {result} punch delivered force")
    # condition may never fall, and never exceed capacity: nothing in this phase
    # heals, so a decrease is a bug and a rise past the cap is a broken clamp.
    last = {0: None, 1: None}
    for r in crow:
        i = int(r[2])
        vals = [int(v) for v in r[3:9]]
        names = ("head", "jaw_chin", "torso_upper", "torso_lower", "arm_left", "arm_right")
        for name, v in zip(names, vals):
            if v > c["cap"][name]:
                rep["errors"].append(f"{name} exceeded its declared capacity")
        if last[i] is not None and any(a < b for a, b in zip(vals, last[i])):
            rep["errors"].append(f"fighter {i} condition decreased - nothing in this "
                                 f"phase heals, so this is accumulation running backwards")
        last[i] = vals
        regen, guard = int(r[9]), int(r[10])
        if regen > 10000 or regen < c["regen_floor"]:
            rep["errors"].append("regeneration multiplier left its authored range")
        if guard > 10000 or guard < c["guard_floor"]:
            rep["errors"].append("guard extent multiplier left its authored range")

    slines = [l for l in lines if l.startswith("S|")]
    if len(slines) != 1:
        rep["errors"].append(f"{len(slines)} S trailer lines (want exactly 1)")
    else:
        trail = dict(kv.split("=") for kv in slines[0][2:].split("|"))
        blob = "".join(l + "\n" for l in lines
                       if l[0] in "DPC" and l[1] == "|").encode("utf-8")
        if int(trail["fnv1a64"], 16) != fnv1a64(blob):
            rep["errors"].append("S trailer fnv1a64 does not hash the D, P and C lines")
        if len(prow) > 50:
            if ticks >= REACH_TICKS and int(trail["opened"]) == 0:
                rep["errors"].append(
                    "not one punch landed through a lane that arm damage had opened, "
                    "on a run past the reachability horizon - the guard-erosion "
                    "mechanism is inert, and an inert mechanism is indistinguishable "
                    "from an absent one")
            if ticks < REACH_TICKS and int(trail["opened"]) == 0:
                rep["notes"].append(
                    f"guard erosion did not fire: this run is {ticks} ticks and the "
                    f"mechanism first reaches the interception threshold at about "
                    f"{REACH_TICKS} at canon's coefficients (module docstring). Not a "
                    f"failure at this length - a tuning finding at any length")
            if int(trail["damage"]) == 0:
                rep["errors"].append("no damage accumulated across the whole run")
            resolved = {r[3] for r in prow}
            missing = set(PUNCHES) - resolved
            if missing:
                rep["errors"].append(f"punch(es) never resolved: {sorted(missing)}")
            need = {"blocked", "landed", "whiffed"} - {r[4] for r in prow}
            if need:
                rep["errors"].append(f"punch outcome(s) never reached: {sorted(need)}")
        rep["opened"] = int(trail["opened"])
        rep["damage"] = int(trail["damage"])

    drows = [l.split("|") for l in lines if l.startswith("D|")]
    bands = [int(r[8]) for r in drows]
    if any(abs(b - a) > 1 for a, b in zip(bands, bands[1:])):
        rep["errors"].append("band moved more than one step between decisions")
    rep["rows"] = len(drows)
    rep["punch_rows"] = len(prow)
    rep["condition_rows"] = len(crow)
    rep["ok"] = not rep["errors"]
    return rep


if __name__ == "__main__":
    all_ok = True
    for p in sys.argv[1:]:
        r = analyse(p)
        all_ok &= r["ok"]
        print(json.dumps(r, indent=1, sort_keys=True))
    sys.exit(0 if all_ok else 1)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | END ]
