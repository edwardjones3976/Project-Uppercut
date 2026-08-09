# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 07:40 UTC | START ]
"""Phase L marker contract and analyzer - guard and slip.

The defender stops being a static wall (Decision 0012 slice item 7). Three
canon mechanisms enter the C++ core, and each brings an emergence the stream
must demonstrate rather than assert:

  1. POSTURE SWITCHING. Fighters toggle high_guard <-> tight_elbow. The pair
     is chosen by the data itself: at pose_geometry's one interception
     threshold (0.6), high_guard (0.95/0.55) closes the head lane and opens
     the body; tight_elbow (0.55/0.95) is the mirror. Lane coverage becomes
     per-fighter and dynamic - the rock-paper-scissors of lanes goes live.
     Mobility and hold cost follow the current posture (posture_economy,
     hold charged only when not committed, as authored).
  2. THE SLIP. slip_lead: an active-window evasion (guard_evasion_model
     evasions + the move table: cost 0.8, startup 3; window = the evasion
     entry's 5 active ticks; commit = startup+active+recovery = 15). During
     the window an ARRIVING head-height punch resolves 'dodged' - evasion
     outranks guard (evasion_economy.outranks_guard, the pipeline's tier
     order). Body punches ignore it: 'beaten_by body_shot', emergent.
  3. COMMITTED DEFENSE. guard_extent_multiplier_while_committed (0.6) scales
     the defender's extents at evaluation time, so a fighter caught inside
     their own commitment cannot fully cover: 0.95 x 0.6 = 0.57 < 0.6 and the
     normally-closed lane opens. The counterpunch, from canon numbers alone.

Named simplifications, on the record: posture-switch economics are not
authored in canon, so switching commits one decision interval at zero cost
(the contract's number, flagged for canon when guard work deepens);
offense_cheap/offense_expensive pricing and the slip mistime penalty port
with the fuller pipeline; roll_under waits its turn.

Actions (x mod 11): step_in, step_out, step_lateral, jab_lead, cross_rear,
hook_lead, uppercut_rear, body_straight_rear, switch_guard, slip_lead, idle.

Stream (H|phase=L, same eight canon files):
  D|t|i|action|x|pos0|pos1|sep|band|st0|st1|g0|g1|flags   g: h=high_guard t=tight_elbow
  P|t|i|move|result|region|k|tip|plane|surface|dflags     result += dodged;
      dflags: '-' or c (defender committed at evaluation) and/or s (defender
      slip window active) - the WHY of the result, auditable per punch.
  F|k|bits (float probe, reported not judged)
  S|rows=..|punches=..|blocked=..|landed=..|whiffed=..|dodged=..|steps=..|switches=..|slips=..|held=..|idles=..|transitions=..|fnv1a64=..

Usage: python analyze_core_guard.py <markers.txt> [...]
"""
import hashlib
import io
import json
import os
import struct
import sys

from tools.uppercut_guard import core as GUARDCORE  # noqa: E402

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
}

ACTIONS = ("step_in", "step_out", "step_lateral", "jab_lead", "cross_rear",
           "hook_lead", "uppercut_rear", "body_straight_rear", "switch_guard",
           "slip_lead", "idle")
PUNCHES = ("jab_lead", "cross_rear", "hook_lead", "uppercut_rear", "body_straight_rear")
POSTURES = ("high_guard", "tight_elbow")
GCHAR = {"high_guard": "h", "tight_elbow": "t"}


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
    rb = mv["range_bands"]
    st = cm["stamina"]

    postures = {p["id"]: p for p in ge["postures"]}
    vol_by_class = {gv["height_class"]: gv["id"] for gv in col["volumes"]["guard_volumes"]}
    thr = float(pose["guard"]["plane_interception_min_extent"])
    cd_mult = float(ge["committed_defense"]["guard_extent_multiplier_while_committed"])

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 13:50 UTC
    #   | START edit: the guard rule moves out and is CALLED ]
    # This closure was the only implementation of guard interception, which
    # meant the integrated bout could have it by importing a phase analyzer
    # (forbidden) or by copying the formula (the defect this project has
    # deleted three times). It now lives in `tools/uppercut_guard/core.py`
    # and both callers reach the same one. Phase L must re-prove
    # byte-identically or the extraction is wrong - that proof, not this
    # comment, is what says the move was safe.
    _gpack = GUARDCORE.guard_pack()

    def covered(pid: str, committed: bool) -> frozenset:
        return GUARDCORE.covered(_gpack, pid, committed)
    # [ ... | 2026-08-09 13:50 UTC | END edit ]

    slip = next(e for e in ge["evasions"] if e["id"] == "slip_lead")
    slip_mv = moves["slip_lead"]
    hmap = {e["guard_interaction"]: e["height_class"]
            for e in pose["height_by_guard_interaction"]}
    ext_by_move = {e["move_id"]: q(e["extended_ru"])
                   for e in pose["fist"]["extension_by_move"]}

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
        "posture": {pid: {"mobility": q(postures[pid]["mobility_multiplier"]),
                          "hold": q(postures[pid]["stamina_per_tick"]),
                          "covered_free": covered(pid, False),
                          "covered_committed": covered(pid, True)}
                    for pid in POSTURES},
        "slip_cost": q(slip_mv["stamina_cost"]),
        "slip_startup": int(slip_mv["startup_frames"]),
        "slip_active": int(slip["active_ticks"]),
        "slip_frames": int(slip_mv["startup_frames"]) + int(slip["active_ticks"])
                       + int(slip_mv["recovery_frames"]),
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
                     frames=int(a["startup_ticks"]) + int(a["active_ticks"]) + int(a["recovery_ticks"]),
                     ext=ext_by_move[mid],
                     height=hmap[m["guard_interaction"]],
                     region=m["target_regions"][0])
        else:
            d["frames"] = int(m["startup_frames"]) + int(m["recovery_frames"])
        c["moves"][mid] = d

    errs = []
    hg, te = c["posture"]["high_guard"], c["posture"]["tight_elbow"]
    if not (hg["covered_free"] == frozenset({"high"}) and te["covered_free"] == frozenset({"low"})):
        errs.append("the posture pair does not mirror at the interception threshold - "
                    "the lane rock-paper-scissors would be vacuous")
    if hg["covered_committed"] or te["covered_committed"]:
        errs.append("committed defense leaves a lane fully covered - the counter "
                    "window would be inert for that posture")
    c["canon_errors"] = errs
    return c


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


def expected_stream(seed: int, ticks: int, with_floats: bool = True) -> str:
    c = canon_pack()
    lines = ["H|phase=L"]
    lines += [f"H|canon_{k}={c['sha'][k]}" for k in
              ("movement", "condition", "guard", "cpu", "moves", "animation", "collision", "pose")]
    lines += [f"H|seed={seed}", f"H|ticks={ticks}", f"H|interval={c['interval']}"]

    pos = [c["axis"] // 2 - 4500, c["axis"] // 2 + 4500]
    st = [c["st_max"], c["st_max"]]
    committed = [0, 0]
    punch = [None, None]
    posture = ["high_guard", "high_guard"]
    slip_until = [0, 0]           # slip window: ticks (t0+startup, t0+startup+active]
    slip_from = [10 ** 9, 10 ** 9]
    band = 2
    x = seed % LCG_M
    rows = []
    counts = {"punches": 0, "blocked": 0, "landed": 0, "whiffed": 0, "dodged": 0,
              "steps": 0, "switches": 0, "slips": 0, "held": 0, "idles": 0}
    transitions = 0

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
                    cov = c["posture"][posture[opp]][
                        "covered_committed" if d_committed else "covered_free"]
                    dflags = (("c" if d_committed else "") + ("s" if d_slipping else "")
                              + GCHAR[posture[opp]])
                    result = region = None
                    if (arrived_plane or arrived_surface) and d_slipping \
                            and mv["height"] == "high":
                        result, region = "dodged", "-"
                    elif arrived_plane and mv["height"] in cov:
                        result, region = "blocked", "-"
                    elif arrived_surface:
                        result, region = "landed", mv["region"]
                    elif k == mv["startup"] + mv["active"]:
                        result, region = "whiffed", "-"
                    if result:
                        counts[result] += 1
                        rows.append(f"P|{t}|{i}|{mid}|{result}|{region}|{k}"
                                    f"|{tip}|{plane}|{surface}|{dflags}")
                        punch[i] = None
                elif k > mv["startup"] + mv["active"]:
                    punch[i] = None
            if committed[i] > 0:
                committed[i] -= 1
                held = True
            else:
                st[i] = min(c["st_max"], st[i] + c["regen"])
                st[i] = max(0, st[i] - c["posture"][posture[i]]["hold"])
                held = False
            if t % c["interval"] != 0:
                continue
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
                committed[i] = c["interval"]      # contract number, named in the docstring
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
                 f"|transitions={transitions}|fnv1a64={h:016x}")
    return "\n".join(lines) + "\n"


def analyse(path: str) -> dict:
    rep = {"file": os.path.basename(path), "errors": [], "notes": []}
    c = canon_pack()
    rep["errors"] += c["canon_errors"]
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
    for k in CANON:
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
    want_f = float_probe(c)
    if got_f and got_f == want_f:
        rep["notes"].append(f"float probe: all {len(got_f)} checkpoints BIT-IDENTICAL "
                            f"to CPython doubles")
    elif got_f:
        rep["notes"].append("float probe: DIVERGES - a finding, not a failure")
    else:
        rep["notes"].append("float probe absent from stream")

    # The lane laws, now defender-state-aware and checked independently.
    prow = [l.split("|") for l in lines if l.startswith("P|")]
    for r in prow:
        mid, result, k, dflags = r[3], r[4], int(r[6]), r[10]
        mv = c["moves"].get(mid, {})
        if result not in ("blocked", "landed", "whiffed", "dodged"):
            rep["errors"].append(f"unknown punch result {result!r}")
        if not (mv.get("startup", 0) < k <= mv.get("startup", 0) + mv.get("active", 0)):
            rep["errors"].append(f"punch resolved outside its active window ({mid}, k={k})")
        if result == "dodged" and (mv.get("height") != "high" or "s" not in dflags):
            rep["errors"].append("a dodge outside a slip window, or of a body punch - "
                                 "evasion vacates the head, nothing else")
        if result == "blocked" and "s" in dflags and mv.get("height") == "high":
            rep["errors"].append("a head punch blocked through an active slip - evasion "
                                 "outranks guard (evasion_economy.outranks_guard)")
    if len(prow) > 80:
        got_results = {r[4] for r in prow}
        need = {"blocked", "landed", "whiffed", "dodged"} - got_results
        if need:
            rep["errors"].append(f"punch outcome(s) never reached: {sorted(need)}")
        # the counter window must actually fire: a landed punch, defender
        # committed, through the lane that defender's FREE posture covers -
        # a head shot on a committed high_guard, or a body shot on a
        # committed tight_elbow. dflags carries all three facts.
        counter = any(r[4] == "landed" and "c" in r[10]
                      and ((c["moves"][r[3]]["height"] == "high" and "h" in r[10])
                           or (c["moves"][r[3]]["height"] == "low" and "t" in r[10]))
                      for r in prow)
        if not counter:
            rep["errors"].append("no punch ever landed through a committed defender's "
                                 "degraded guard - the counter window is untested")
    drows = [l.split("|") for l in lines if l.startswith("D|")]
    if len(drows) > 200:
        gs = {r[11] for r in drows} | {r[12] for r in drows}
        if not ({"h", "t"} <= gs):
            rep["errors"].append("a posture was never held - the switch is untested")
        acts = {r[3] for r in drows}
        missing = set(ACTIONS) - acts
        if missing:
            rep["errors"].append(f"action(s) never taken: {sorted(missing)}")
    bands = [int(r[8]) for r in drows]
    if any(abs(b - a) > 1 for a, b in zip(bands, bands[1:])):
        rep["errors"].append("band moved more than one step between decisions")
    slines = [l for l in lines if l.startswith("S|")]
    if len(slines) != 1:
        rep["errors"].append(f"{len(slines)} S trailer lines (want exactly 1)")
    else:
        trail = dict(kv.split("=") for kv in slines[0][2:].split("|"))
        blob = "".join(l + "\n" for l in lines
                       if l.startswith("D|") or l.startswith("P|")).encode("utf-8")
        if int(trail["fnv1a64"], 16) != fnv1a64(blob):
            rep["errors"].append("S trailer fnv1a64 does not hash the D and P lines")
    rep["rows"] = len(drows)
    rep["punch_rows"] = len(prow)
    rep["ok"] = not rep["errors"]
    return rep


if __name__ == "__main__":
    all_ok = True
    for p in sys.argv[1:]:
        r = analyse(p)
        all_ok &= r["ok"]
        print(json.dumps(r, indent=1, sort_keys=True))
    sys.exit(0 if all_ok else 1)
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 07:40 UTC | END ]
