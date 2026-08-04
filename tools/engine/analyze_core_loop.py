# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:10 UTC | START ]
"""Phase I marker contract and analyzer - the two-fighter authoritative loop.

Built and mutation-proven before the C++ runs, per the discipline every phase
has run under (Decision 0012). Phase H proved the pipeline with one rule
walking alone; Phase I is where the core starts being a core: two fighters
with authoritative state, one clock, decisions interleaved in fixed index
order, consuming FIVE canon files at once.

What the loop executes, all in contract-defined integer arithmetic
(Q(v) = round(v * 10000); stamina carries the same scale, so 100.0 -> 1000000):

  - Positions on the ring track (movement_model ring.track): axis clamp,
    back-to-ropes zone, rope_retreat_multiplier zeroing a backward step on the
    ropes, min_center_distance separation snap - mover yields.
  - Footwork (locomotion): boxing_steps stride x directional multiplier x
    high_guard mobility, x exhausted multiplier below the exhausted stamina
    fraction. Lateral circling changes no separation, exactly as the track
    model resolves it.
  - Band hysteresis over the separation (range_bands), one band per
    resolution at most - the Phase D/H rule, now driven by real positions.
  - Stamina economy (condition_model): idle regen minus high_guard hold cost
    per uncommitted tick, move costs on action, clamped [0, max].
  - Commitment (moves table): startup + recovery frames, decremented per
    tick; a committed fighter takes no decision. THE CONTRACT'S OWN
    SIMPLIFICATION, on the record: the reference engine's arm/chain/fatigue
    commitment arithmetic ports with the collision pipeline, not here.
  - Decisions every cpu_decision_model reaction interval, from the shared
    32-bit LCG (Phase H spec): x mod 5 -> step_in, step_out, step_lateral,
    jab_lead, idle. A jab pays and commits regardless; it is 'delivered'
    only from its authored band (Rule 12's gate), else counted a whiff.

The stream:

  H|phase=I
  H|canon_movement=<sha256>          (and _condition, _guard, _cpu, _moves)
  H|seed=<uint32>   H|ticks=<T>   H|interval=<from canon>
  D|t|i|action|x|pos0|pos1|sep|band|st0|st1|flags
      one line per decision slot (committed fighters emit action=held).
      flags: '-' or any of r (rope-blocked retreat), m (min-sep snap),
      e (exhausted stride), w (jab out of band).
  F|k|<16-hex double bits>
      the float-conformance probe: a fixed +,-,*,min recipe over canon-derived
      doubles, checkpointed every 100 iterations. NOT part of the pass
      criteria - it is an instrumented experiment in C++/CPython bit
      identity, reported either way, because the full core will eventually
      need floats and the answer should arrive as evidence, not assumption.
  S|rows=..|delivered=..|whiffs=..|steps=..|held=..|idles=..|transitions=..|fnv1a64=<hex over D lines>

Usage: python analyze_core_loop.py <markers.txt> [...]
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
}

ACTIONS = ("step_in", "step_out", "step_lateral", "jab_lead", "idle")


def fnv1a64(data: bytes) -> int:
    h = FNV_OFFSET
    for b in data:
        h = ((h ^ b) * FNV_PRIME) % (2 ** 64)
    return h


def q(v) -> int:
    return round(float(v) * 10000)


def canon_pack() -> dict:
    """Everything the loop consumes, quantized, plus the file hashes."""
    raw = {k: io.open(os.path.join(REPO, p), "rb").read() for k, p in CANON.items()}
    sha = {k: hashlib.sha256(b).hexdigest() for k, b in raw.items()}
    mv = json.loads(raw["movement"])
    cm = json.loads(raw["condition"])
    ge = json.loads(raw["guard"])
    cpu = json.loads(raw["cpu"])
    moves = {m["id"]: m for m in json.loads(raw["moves"])["moves"]}
    rb = mv["range_bands"]
    hg = next(p for p in ge["postures"] if p["id"] == "high_guard")
    st = cm["stamina"]
    return {
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
        "moves": {mid: {"cost": q(moves[mid]["stamina_cost"]),
                        "frames": int(moves[mid]["startup_frames"]) + int(moves[mid]["recovery_frames"])}
                  for mid in ("jab_lead", "step_in", "step_out", "step_lateral")},
        "jab_band": next(i for i, b in enumerate(rb["bands"])
                         if b["key"] == moves["jab_lead"]["range_band"]),
        # canon-derived doubles for the float probe, passed raw
        "f_cost": float(moves["jab_lead"]["stamina_cost"]),
        "f_regen": float(st["regen_per_tick_idle"]),
        "f_max": float(st["max"]),
        "f_hold": float(hg["stamina_per_tick"]),
    }


def float_probe(c: dict, iters: int = 1000, every: int = 100) -> list:
    """The instrumented experiment: identical op order to the C++ side."""
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


def expected_stream(seed: int, ticks: int, with_floats: bool = True) -> str:
    c = canon_pack()
    lines = ["H|phase=I"]
    lines += [f"H|canon_{k}={c['sha'][k]}" for k in ("movement", "condition", "guard", "cpu", "moves")]
    lines += [f"H|seed={seed}", f"H|ticks={ticks}", f"H|interval={c['interval']}"]

    pos = [c["axis"] // 2 - 4500, c["axis"] // 2 + 4500]
    st = [c["st_max"], c["st_max"]]
    committed = [0, 0]
    band = 2
    x = seed % LCG_M
    drows = []
    counts = {"delivered": 0, "whiffs": 0, "steps": 0, "held": 0, "idles": 0}
    transitions = 0

    for t in range(1, ticks + 1):
        for i in (0, 1):
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
                drows.append(f"D|{t}|{i}|held|0|{pos[0]}|{pos[1]}|{pos[1]-pos[0]}|{band}|{st[0]}|{st[1]}|-")
                continue
            x = (LCG_A * x + LCG_C) % LCG_M
            action = ACTIONS[x % 5]
            flags = ""
            if action == "idle":
                counts["idles"] += 1
            elif action == "jab_lead":
                mvd = c["moves"]["jab_lead"]
                st[i] = max(0, st[i] - mvd["cost"])
                committed[i] = mvd["frames"]
                if band == c["jab_band"]:
                    counts["delivered"] += 1
                else:
                    counts["whiffs"] += 1
                    flags += "w"
            else:
                mvd = c["moves"][action]
                st[i] = max(0, st[i] - mvd["cost"])
                committed[i] = mvd["frames"]
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
            drows.append(f"D|{t}|{i}|{action}|{x if action != 'held' else 0}"
                         f"|{pos[0]}|{pos[1]}|{pos[1]-pos[0]}|{band}|{st[0]}|{st[1]}|{flags or '-'}")

    h = fnv1a64("".join(l + "\n" for l in drows).encode("utf-8"))
    lines += drows
    if with_floats:
        lines += float_probe(c)
    lines.append(f"S|rows={len(drows)}|delivered={counts['delivered']}|whiffs={counts['whiffs']}"
                 f"|steps={counts['steps']}|held={counts['held']}|idles={counts['idles']}"
                 f"|transitions={transitions}|fnv1a64={h:016x}")
    return "\n".join(lines) + "\n"


def analyse(path: str) -> dict:
    rep = {"file": os.path.basename(path), "errors": [], "notes": []}
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

    c = canon_pack()
    for k in ("movement", "condition", "guard", "cpu", "moves"):
        if heads.get("canon_" + k) != c["sha"][k]:
            rep["errors"].append(f"canon_{k} hash does not match the local file - "
                                 f"the run consumed different canon")

    # The integer loop, byte for byte against the canon recomputation. The
    # float probe is EXCLUDED here and judged separately below: it is an
    # experiment with a reported answer, not a pass criterion.
    got_core = "\n".join(l for l in lines if not l.startswith("F|")) + "\n"
    want = expected_stream(seed, ticks, with_floats=False)
    if got_core != want:
        for n, (g, w) in enumerate(zip(got_core.splitlines(), want.splitlines()), 1):
            if g != w:
                rep["errors"].append(f"core stream diverges from canon recomputation at "
                                     f"line {n}: got {g!r}, expected {w!r}")
                break
        else:
            rep["errors"].append("core stream length differs from canon recomputation")

    # The experiment's verdict, reported either way.
    got_f = [l for l in lines if l.startswith("F|")]
    want_f = float_probe(c)
    if not got_f:
        rep["notes"].append("float probe absent from stream")
    elif got_f == want_f:
        rep["notes"].append(f"float probe: all {len(got_f)} checkpoints BIT-IDENTICAL "
                            f"to CPython doubles")
    else:
        bad = next(i for i, (g, w) in enumerate(zip(got_f, want_f)) if g != w)
        rep["notes"].append(f"float probe: DIVERGES at checkpoint {bad + 1} "
                            f"(got {got_f[bad]!r}, expected {want_f[bad]!r}) - "
                            f"a finding, not a failure; the integer core is the claim")

    # Independent properties, not derived from expected_stream.
    drows = [l.split("|") for l in lines if l.startswith("D|")]
    bands = [int(r[8]) for r in drows]
    if any(abs(b - a) > 1 for a, b in zip(bands, bands[1:])):
        rep["errors"].append("band moved more than one step between decisions")
    if len(set(bands)) < 2 and len(drows) > 20:
        rep["errors"].append("the band never changed - hysteresis untested by this run")
    seps = [int(r[7]) for r in drows]
    if any(s < c["min_sep"] for s in seps):
        rep["errors"].append("separation below min_center_distance in an emitted state")
    sts = [(int(r[9]), int(r[10])) for r in drows]
    if any(s < 0 or s > c["st_max"] for pair in sts for s in pair):
        rep["errors"].append("stamina outside [0, max] in an emitted state")
    acts = {r[3] for r in drows}
    missing = set(ACTIONS) - acts
    if missing and len(drows) > 100:
        rep["errors"].append(f"action(s) never taken: {sorted(missing)} - the run does "
                             f"not exercise the whole decision surface")
    slines = [l for l in lines if l.startswith("S|")]
    if len(slines) != 1:
        rep["errors"].append(f"{len(slines)} S trailer lines (want exactly 1)")
    else:
        trail = dict(kv.split("=") for kv in slines[0][2:].split("|"))
        blob = "".join(l + "\n" for l in lines if l.startswith("D|")).encode("utf-8")
        if int(trail["fnv1a64"], 16) != fnv1a64(blob):
            rep["errors"].append("S trailer fnv1a64 does not hash the D lines")
        if int(trail["rows"]) != len(drows):
            rep["errors"].append("S trailer row count disagrees with the stream")
    rep["rows"] = len(drows)
    rep["ok"] = not rep["errors"]
    return rep


if __name__ == "__main__":
    all_ok = True
    for p in sys.argv[1:]:
        r = analyse(p)
        all_ok &= r["ok"]
        print(json.dumps(r, indent=1, sort_keys=True))
    sys.exit(0 if all_ok else 1)
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 05:10 UTC | END ]
