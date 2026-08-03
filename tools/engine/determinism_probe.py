# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 23:57 UTC | START ]
"""Determinism probe - engine-runtime half of the Decision 0002 question.

Runs INSIDE UnrealEditor-Cmd via PythonScriptPlugin:
    UnrealEditor-Cmd.exe UppercutSandbox.uproject -run=pythonscript -script="...this file..."

Exercises, over a fixed logical tick (dt = 1/60, no wall clock, no frame timing):
  - engine seeded RNG (FRandomStream via KismetMathLibrary),
  - engine float math (sin/cos accumulation),
  - a deterministic walk over the canonical combat-state machine
    (data/combat_states.json - the same canon the validators enforce),
serializing every float as exact hex bits. Two processes with the same seed must
produce byte-identical logs; a different seed must not (non-vacuity).

SCOPE (Rule 18): this is the NECESSARY half - engine runtime primitives across
process boundaries. It does NOT prove Blueprint actor-tick determinism; that
half needs authored Blueprint assets and its own evidence.

Inputs via environment: UE_PROBE_SEED, UE_PROBE_TICKS, UE_PROBE_OUT.
"""
import json
import os
import sys

import unreal

SEED = int(os.environ.get("UE_PROBE_SEED", "56057345"))
TICKS = int(os.environ.get("UE_PROBE_TICKS", "10000"))
OUT = os.environ["UE_PROBE_OUT"]
DT = 1.0 / 60.0

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def make_stream(seed):
    """Resolve the RandomStream API defensively; the resolution is deterministic per build."""
    try:
        rs = unreal.RandomStream(seed)
        return rs, "ctor(seed)"
    except Exception:
        rs = unreal.RandomStream()
        try:
            unreal.MathLibrary.set_random_stream_seed(rs, seed)
            return rs, "set_random_stream_seed"
        except Exception:
            rs.set_editor_property("initial_seed", seed)
            unreal.MathLibrary.reset_random_stream(rs)
            return rs, "initial_seed+reset"


def rand_float(rs):
    return unreal.MathLibrary.random_float_from_stream(rs)


def rand_int(rs, max_exclusive):
    return unreal.MathLibrary.random_integer_from_stream(rs, max_exclusive)


def load_machine():
    with open(os.path.join(REPO, "data", "combat_states.json"), "r") as f:
        doc = json.load(f)
    fa = doc["machines"]["fighter_action"]
    states = {s["id"]: s for s in fa["states"]}
    outgoing = {}
    for t in sorted(fa["transitions"], key=lambda x: x["id"]):
        if t.get("provisioned"):
            continue
        if t["from"] == "*":
            excl = set(t.get("wildcard_excludes", []))
            srcs = [sid for sid, s in sorted(states.items())
                    if not s.get("terminal") and not s.get("provisioned") and sid not in excl]
        else:
            srcs = [t["from"]]
        for s in srcs:
            outgoing.setdefault(s, []).append((t["id"], t["to"]))
    return states, outgoing


def main():
    states, outgoing = load_machine()
    _, api = make_stream(SEED)
    lines = []
    lines.append("# uppercut determinism probe v2")
    lines.append("# v2 note: KismetMathLibrary stream draws cross the Python bridge by value")
    lines.append("#   (const-ref copy), so one stream never advances from Python. Each tick")
    lines.append("#   therefore draws from a fresh engine stream with a derived seed - 10k")
    lines.append("#   distinct FRandomStream constructions and draws, all engine-side.")
    lines.append("# seed=%d ticks=%d dt=%s api=%s" % (SEED, TICKS, DT.hex(), api))
    lines.append("# engine=%s" % unreal.SystemLibrary.get_engine_version())
    state = "idle"
    acc = 0.0
    pos = 0.0
    resets = 0
    for tick in range(TICKS):
        tick_seed = (SEED * 2654435761 + tick * 40503 + 12345) & 0x7FFFFFFF
        rs, _ = make_stream(tick_seed)
        r = rand_float(rs)
        outs = outgoing.get(state)
        if not outs:
            state = "idle"
            resets += 1
            outs = outgoing[state]
        pick = rand_int(rs, len(outs))
        tid, nxt = outs[pick]
        acc += unreal.MathLibrary.sin(r * 6.283185307179586) * DT
        acc += unreal.MathLibrary.cos(acc) * DT
        pos += (r - 0.5) * DT
        lines.append("%d,%s,%s,%s,%s,%s" % (tick, tid, nxt, float(r).hex(), acc.hex(), pos.hex()))
        state = nxt
    lines.append("# end resets=%d final_state=%s" % (resets, state))
    with open(OUT, "wb") as f:
        f.write(("\n".join(lines) + "\n").encode("ascii"))
    unreal.log("PROBE_DONE out=%s lines=%d" % (OUT, len(lines)))


try:
    main()
except Exception as e:
    import traceback
    unreal.log_error("PROBE_FAILED: %r" % (e,))
    unreal.log_error(traceback.format_exc())
    with open(OUT + ".failed", "w") as f:
        f.write(traceback.format_exc())
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 23:57 UTC | END ]
