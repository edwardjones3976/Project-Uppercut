# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:45 UTC | START ]
"""Is commitment a connected dial, or another inert one?

Reaction cadence turned out to be inert: a 3.3x change moved punches thrown by
2.6%, because commitment already gates a fighter harder than his reaction does.
That left commitment frames as the thing actually setting work rate - authored
per move in `animation_model`, never examined as an economic control.

This is a SENSITIVITY SWEEP, not a tuning proposal. The question is only whether
the dial is connected to anything, which is precisely the test cadence failed.
Canon's authored frames are the 1.0x row; the others exist to show the slope.

A fighter who commits longer throws less, tires less, and is caught inside his
own recovery more often - three consequences pulling in different directions,
which is why guessing the sign of the effect would be unwise and measuring it
is cheap.

Run: python -m tools.engine.experiment_commitment_frames
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402

MULTIPLIERS = [1.0, 1.5, 2.0, 3.0]


def run_at(seed: int, mult: float, rounds: int = 3) -> dict:
    c = O.canon_pack()
    if mult != 1.0:
        c = dict(c)
        c["moves"] = {k: dict(v) for k, v in c["moves"].items()}
        for m in c["moves"].values():
            if "frames" in m:
                m["frames"] = int(m["frames"] * mult)
    return H.run_with(seed, c, rounds, None)


def main() -> int:
    seeds = list(range(4240, 4264))
    out = {}
    print("  %-6s %8s %8s %8s %8s %10s" %
          ("commit", "thrown", "blocks", "end_stam", "kd", "decisions"))
    for mult in MULTIPLIERS:
        agg = {"thrown": 0, "blocked": 0, "knockdowns": 0, "stopped": 0,
               "end_stamina": 0.0}
        for s in seeds:
            r = run_at(s, mult)
            for k in ("thrown", "blocked", "knockdowns"):
                agg[k] += r[k]
            agg["end_stamina"] += sum(r["end_stamina"]) / 2.0
            agg["stopped"] += 1 if r["stopped"] else 0
        decisions = len(seeds) - agg["stopped"]
        stam = agg["end_stamina"] / len(seeds)
        print("  %-6.1f %8d %8d %8.1f %8d %10d"
              % (mult, agg["thrown"], agg["blocked"], stam,
                 agg["knockdowns"], decisions))
        out["%.1f" % mult] = {"thrown": agg["thrown"], "blocked": agg["blocked"],
                              "end_stamina": round(stam, 1),
                              "knockdowns": agg["knockdowns"],
                              "decisions": decisions, "seeds": len(seeds)}
    p = os.path.join(O.REPO, "sandbox", "Saved", "commitment_frames.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:45 UTC | END ]
