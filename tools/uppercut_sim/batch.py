# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:47 UTC | START ]
"""Batch round-robin telemetry (WS5 / T5.1).

Runs every stress profile against every other across a seed sweep and reports
per-profile outcomes. Rule 21 governs how the numbers are read: lopsided results
are findings to explain, not automatic failures. What the report flags is
*inexplicable* dominance and absent counterplay - a profile that never wins and a
profile that always wins are both worth a look, and the report says which.

Usage: python -m tools.uppercut_sim.batch [--seeds N] [--rounds N] [--json PATH]
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict

from . import canon, policy
from .engine import Bout


def round_robin(seeds: int = 8, rounds: int = 3, round_seconds: int = 120) -> dict:
    names = policy.available_profiles()
    tally = {n: defaultdict(float) for n in names}
    bouts = 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for s in range(seeds):
                bt = Bout(90000 + s, a, b, rounds=rounds, round_seconds=round_seconds)
                bt.run()
                fa, fb = bt.fighters
                bouts += 1
                for f, other in ((fa, fb), (fb, fa)):
                    t = tally[f.profile]
                    t["bouts"] += 1
                    t["thrown"] += f.thrown
                    t["landed"] += f.landed
                    t["knockdowns_scored"] += other.knockdowns
                    t["crowd"] += f.crowd
                    t["end_stamina"] += f.stamina
                    if f.landed > other.landed:
                        t["landed_edge"] += 1
    report = {"bouts": bouts, "seeds": seeds, "rounds": rounds, "profiles": {}, "findings": []}
    for n, t in tally.items():
        b = max(1.0, t["bouts"])
        report["profiles"][n] = {
            "bouts": int(t["bouts"]),
            "landed_edge_rate": round(t["landed_edge"] / b, 4),
            "accuracy": round(t["landed"] / max(1.0, t["thrown"]), 4),
            "avg_thrown": round(t["thrown"] / b, 2),
            "avg_knockdowns_scored": round(t["knockdowns_scored"] / b, 3),
            "avg_end_stamina": round(t["end_stamina"] / b, 2),
            "avg_crowd": round(t["crowd"] / b, 2),
        }
    for n, p in report["profiles"].items():
        if p["landed_edge_rate"] == 0.0:
            report["findings"].append(
                f"{n}: never out-landed an opponent in {p['bouts']} bouts - absent counterplay, "
                f"which Rule 21 treats as a gate failure rather than a tuning note")
        if p["landed_edge_rate"] == 1.0:
            report["findings"].append(
                f"{n}: out-landed every opponent in {p['bouts']} bouts - dominant extreme, "
                f"explain it from observable mechanics or treat it as a gate failure")
        if p["avg_thrown"] < 1.0:
            report["findings"].append(f"{n}: threw almost nothing - the instrument is inert")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--round-seconds", type=int, default=120)
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    rep = round_robin(a.seeds, a.rounds, a.round_seconds)
    print(f"== Stress-profile round robin: {rep['bouts']} bouts, {rep['seeds']} seeds ==")
    hdr = f"{'profile':16}{'edge':>8}{'acc':>8}{'thrown':>9}{'kd':>7}{'stam':>8}{'crowd':>8}"
    print(hdr)
    for n, p in sorted(rep["profiles"].items()):
        print(f"{n:16}{p['landed_edge_rate']:>8.3f}{p['accuracy']:>8.3f}"
              f"{p['avg_thrown']:>9.1f}{p['avg_knockdowns_scored']:>7.2f}"
              f"{p['avg_end_stamina']:>8.1f}{p['avg_crowd']:>8.1f}")
    if rep["findings"]:
        print("\nFINDINGS (Rule 21 - explain or fix, never average away):")
        for f in rep["findings"]:
            print("  " + f)
    else:
        print("\nNo dominant extremes and no absent counterplay in this sweep.")
    print("\nRule 18: reference-model output. Unreal is authoritative; these are "
          "balance instruments, not results.")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(rep, fh, indent=1, sort_keys=True)
        print(f"wrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:47 UTC | END ]
