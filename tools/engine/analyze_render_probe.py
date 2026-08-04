# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | START ]
"""Phase K marker contract and analyzer - the first rendered slice.

Phase J proved swept collision headless. Phase K's claim is different and
sharper: the SAME contract runs under a real renderer - generic fighters
built from primitives, lights, a camera, sixty fixed ticks a second on
screen - and the marker stream comes out BYTE-IDENTICAL to this file's
recomputation. Presentation holds zero authority (Rule 13, Decision 0002's
Blueprint/presentation boundary, now demonstrated for the C++ core):
rendering a fight must not be able to change it, and the proof is the same
proof every phase has used - bytes.

The sim is Phase J's, widened to the slice's four named punches plus the
proven body straight (Decision 0012 slice item 6):

    x mod 9 -> step_in, step_out, step_lateral, jab_lead, cross_rear,
               hook_lead, uppercut_rear, body_straight_rear, idle

Same eight canon files, same D/P/F/S stream shapes as Phase J, H|phase=K.
The lane laws widen with the moves: jab and cross are blockable_high;
the hook maps to the high plane as pose_geometry's NAMED simplification;
the uppercut is blockable_low in the move table, so against high_guard it
comes up under the closed head lane to the jaw - the guard-splitter,
emergent. The analyzer requires every punch to resolve at least once and
the uppercut to land at least once, or the demonstration is vacuous.

Usage: python analyze_render_probe.py <markers.txt> [...]
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
}

ACTIONS = ("step_in", "step_out", "step_lateral", "jab_lead", "cross_rear",
           "hook_lead", "uppercut_rear", "body_straight_rear", "idle")
PUNCHES = ("jab_lead", "cross_rear", "hook_lead", "uppercut_rear", "body_straight_rear")


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
    hg = next(p for p in ge["postures"] if p["id"] == "high_guard")
    st = cm["stamina"]

    vol_by_class = {gv["height_class"]: gv["id"] for gv in col["volumes"]["guard_volumes"]}
    thr = float(pose["guard"]["plane_interception_min_extent"])
    covered = {hc for hc, vid in vol_by_class.items()
               if float(hg["extents"].get(vid, 0.0)) >= thr}
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
        "mobility": q(hg["mobility_multiplier"]),
        "hold": q(hg["stamina_per_tick"]),
        "st_max": q(st["max"]),
        "regen": q(st["regen_per_tick_idle"]),
        "exhausted_q": round(q(st["max"]) * float(st["exhausted_threshold_fraction"])),
        "interval": int(cpu["reaction"]["decision_interval_ticks"]),
        "half_depth": q(pose["body"]["half_depth_ru"]),
        "plane_off": q(pose["guard"]["plane_offset_ru"]),
        "retracted": q(pose["fist"]["retracted_ru"]),
        "covered": covered,
        "moves": {},
        "f_cost": float(moves["jab_lead"]["stamina_cost"]),
        "f_regen": float(st["regen_per_tick_idle"]),
        "f_max": float(st["max"]),
        "f_hold": float(hg["stamina_per_tick"]),
    }
    for mid in ACTIONS:
        if mid == "idle":
            continue
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
    total = mv["startup"] + mv["active"]
    return c["retracted"] + ((mv["ext"] - c["retracted"]) * m) // total


def expected_stream(seed: int, ticks: int, with_floats: bool = True) -> str:
    c = canon_pack()
    lines = ["H|phase=K"]
    lines += [f"H|canon_{k}={c['sha'][k]}" for k in
              ("movement", "condition", "guard", "cpu", "moves", "animation", "collision", "pose")]
    lines += [f"H|seed={seed}", f"H|ticks={ticks}", f"H|interval={c['interval']}"]

    pos = [c["axis"] // 2 - 4500, c["axis"] // 2 + 4500]
    st = [c["st_max"], c["st_max"]]
    committed = [0, 0]
    punch = [None, None]
    band = 2
    x = seed % LCG_M
    rows = []
    counts = {"punches": 0, "blocked": 0, "landed": 0, "whiffed": 0,
              "steps": 0, "held": 0, "idles": 0}
    transitions = 0

    for t in range(1, ticks + 1):
        for i in (0, 1):
            if punch[i] is not None:
                mid, t0 = punch[i]
                mv = c["moves"][mid]
                k = t - t0
                if mv["startup"] < k <= mv["startup"] + mv["active"]:
                    tip_ext = _ext(c, mid, k)
                    if i == 0:
                        tip = pos[0] + tip_ext
                        surface = pos[1] - c["half_depth"]
                        plane = surface - c["plane_off"]
                        crossed_plane = tip >= plane
                        crossed_surface = tip >= surface
                    else:
                        tip = pos[1] - tip_ext
                        surface = pos[0] + c["half_depth"]
                        plane = surface + c["plane_off"]
                        crossed_plane = tip <= plane
                        crossed_surface = tip <= surface
                    result = region = None
                    if crossed_plane and mv["height"] in c["covered"]:
                        result, region = "blocked", "-"
                    elif crossed_surface:
                        result, region = "landed", mv["region"]
                    elif k == mv["startup"] + mv["active"]:
                        result, region = "whiffed", "-"
                    if result:
                        counts[result] += 1
                        rows.append(f"P|{t}|{i}|{mid}|{result}|{region}|{k}"
                                    f"|{tip}|{plane}|{surface}")
                        punch[i] = None
                elif k > mv["startup"] + mv["active"]:
                    punch[i] = None
            if committed[i] > 0:
                committed[i] -= 1
                held = True
            else:
                st[i] = min(c["st_max"], st[i] + c["regen"])
                st[i] = max(0, st[i] - c["hold"])
                held = False
            if t % c["interval"] != 0:
                continue
            if held or committed[i] > 0:
                counts["held"] += 1
                rows.append(f"D|{t}|{i}|held|0|{pos[0]}|{pos[1]}|{pos[1]-pos[0]}|{band}|{st[0]}|{st[1]}|-")
                continue
            x = (LCG_A * x + LCG_C) % LCG_M
            action = ACTIONS[x % 9]
            flags = ""
            if action == "idle":
                counts["idles"] += 1
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
                mul = (mul * c["mobility"]) // 10000
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
            rows.append(f"D|{t}|{i}|{action}|{x}"
                        f"|{pos[0]}|{pos[1]}|{pos[1]-pos[0]}|{band}|{st[0]}|{st[1]}|{flags or '-'}")

    h = fnv1a64("".join(l + "\n" for l in rows).encode("utf-8"))
    lines += rows
    if with_floats:
        lines += float_probe(c)
    lines.append(f"S|rows={len(rows)}|punches={counts['punches']}|blocked={counts['blocked']}"
                 f"|landed={counts['landed']}|whiffed={counts['whiffed']}|steps={counts['steps']}"
                 f"|held={counts['held']}|idles={counts['idles']}"
                 f"|transitions={transitions}|fnv1a64={h:016x}")
    return "\n".join(lines) + "\n"


def analyse(path: str) -> dict:
    rep = {"file": os.path.basename(path), "errors": [], "notes": []}
    c = canon_pack()
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
    if not got_f:
        rep["notes"].append("float probe absent from stream")
    elif got_f == want_f:
        rep["notes"].append(f"float probe: all {len(got_f)} checkpoints BIT-IDENTICAL "
                            f"to CPython doubles")
    else:
        rep["notes"].append("float probe: DIVERGES - a finding, not a failure")

    prow = [l.split("|") for l in lines if l.startswith("P|")]
    for r in prow:
        mid, result, region, k = r[3], r[4], r[5], int(r[6])
        mv = c["moves"].get(mid, {})
        if not (mv.get("startup", 0) < k <= mv.get("startup", 0) + mv.get("active", 0)):
            rep["errors"].append(f"punch resolved outside its active window ({mid}, k={k})")
        if result == "landed" and region != mv.get("region"):
            rep["errors"].append(f"{mid} landed on {region}, not its leading target region")
        if result == "blocked" and mv.get("height") not in c["covered"]:
            rep["errors"].append(f"{mid} blocked in an open lane")
        if result == "landed" and mv.get("height") in c["covered"]:
            rep["errors"].append(f"{mid} landed through a closed lane")
    if len(prow) > 50:
        resolved = {r[3] for r in prow}
        missing = set(PUNCHES) - resolved
        if missing:
            rep["errors"].append(f"punch(es) never resolved: {sorted(missing)}")
        upp = {r[4] for r in prow if r[3] == "uppercut_rear"}
        if "landed" not in upp:
            rep["errors"].append("the uppercut never landed - the guard-splitter is "
                                 "untested and the lane demonstration is half missing")
        need = {"blocked", "landed", "whiffed"} - {r[4] for r in prow}
        if need:
            rep["errors"].append(f"punch outcome(s) never reached: {sorted(need)}")
    drows = [l.split("|") for l in lines if l.startswith("D|")]
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
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 06:25 UTC | END ]
