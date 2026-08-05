# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:45 UTC | START ]
"""Is commitment a connected dial, or another inert one?

QA correction, 2026-08-05 02:50 UTC: the sentence this file opened with -
"reaction cadence turned out to be inert, a 3.3x change moved punches thrown by
2.6%" - was measured on a confounded metric and is WITHDRAWN. Punches thrown is
a bout total, and every bout ends on the three-knockdown rule, so the total was
normalised by the very outcome under test. Re-measured against time, cadence is
strongly connected: 1.9x in ticks-to-stoppage across canon's four tiers. The
question below is still worth asking; the premise that motivated it was wrong.

Commitment frames are the other thing setting work rate - authored per move in
`animation_model`, never examined as an economic control.

This is a SENSITIVITY SWEEP, not a tuning proposal. The question is only whether
the dial is connected to anything, measured against time and rate rather than
totals. Canon's authored frames are the 1.0x row; the others show the slope.

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
    print("Rates and times only. Totals across rows are not comparable: every")
    print("bout ends on the three-knockdown rule, so its length is set by the")
    print("outcome. See the 2026-08-05 confound entry.")
    print()
    print("  %-6s %9s %9s %9s %10s %9s" %
          ("commit", "kd/elig", "t_1stKD", "t_stop", "thrown/1k", "stam@1200"))
    for mult in MULTIPLIERS:
        agg = {"thrown": 0, "blocked": 0, "knockdowns": 0, "stopped": 0,
               "end_stamina": 0.0, "eligible": 0, "ticks": 0, "landed": 0}
        firsts, stops = [], []
        gauge_at = {g: [] for g in (600, 1200, 1800, 2400, 3600)}
        for s in seeds:
            r = run_at(s, mult)
            for k in ("thrown", "blocked", "knockdowns", "eligible", "landed"):
                agg[k] += r[k]
            agg["ticks"] += r["total_ticks"]
            agg["end_stamina"] += sum(r["end_stamina"]) / 2.0
            agg["stopped"] += 1 if r["stopped"] else 0
            if r["first_kd_tick"] is not None:
                firsts.append(r["first_kd_tick"])
            if r["stop_tick"] is not None:
                stops.append(r["stop_tick"])
            for g, pair in r["stamina_gauges"].items():
                gauge_at[g].append(sum(pair) / 2.0)
        decisions = len(seeds) - agg["stopped"]
        stam = agg["end_stamina"] / len(seeds)
        conv = (round(agg["knockdowns"] / float(agg["eligible"]), 4)
                if agg["eligible"] else None)
        t1 = round(sum(firsts) / float(len(firsts)), 1) if firsts else None
        ts = round(sum(stops) / float(len(stops)), 1) if stops else None
        rate = round(1000.0 * agg["thrown"] / float(agg["ticks"]), 1)
        stam_at = {str(g): (round(sum(v) / float(len(v)), 2) if v else None)
                   for g, v in gauge_at.items()}
        reaching = {str(g): len(v) for g, v in gauge_at.items()}
        # Blocks per punch thrown, not blocks: a longer commitment changes how
        # many punches exist to block, which is the confound in miniature.
        block_rate = round(agg["blocked"] / float(agg["thrown"]), 4) if agg["thrown"] else None
        print("  %-6.1f %9s %9s %9s %10.1f %9s"
              % (mult, conv, t1, ts, rate, stam_at["1200"]))
        out["%.1f" % mult] = {"thrown": agg["thrown"], "blocked": agg["blocked"],
                              "end_stamina": round(stam, 1),
                              "knockdowns": agg["knockdowns"],
                              "decisions": decisions, "seeds": len(seeds),
                              "eligible": agg["eligible"], "landed": agg["landed"],
                              "kd_per_eligible": conv,
                              "mean_ticks_to_first_kd": t1,
                              "mean_ticks_to_stoppage": ts,
                              "punches_per_1000_ticks": rate,
                              "blocks_per_punch": block_rate,
                              "stamina_at": stam_at, "seeds_reaching": reaching}
    print()
    print("  %-6s %11s %14s %14s %14s" %
          ("commit", "blocks/punch", "t=600", "t=1800", "t=2400"))
    for mult in MULTIPLIERS:
        a = out["%.1f" % mult]
        cells = []
        for g in ("600", "1800", "2400"):
            v, n = a["stamina_at"][g], a["seeds_reaching"][g]
            cells.append("--" if v is None else "%.1f (n=%d)" % (v, n))
        print("  %-6.1f %11.4f %14s %14s %14s"
              % (mult, a["blocks_per_punch"], cells[0], cells[1], cells[2]))
    p = os.path.join(O.REPO, "sandbox", "Saved", "commitment_frames.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:45 UTC | END ]
