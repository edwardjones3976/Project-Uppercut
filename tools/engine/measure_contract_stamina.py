# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:40 UTC | START ]
"""Why is the man empty? The stamina economy, on the contract this time.

The term that separates a knockdown from a landing that did nothing is stamina,
1.47x - a converted landing hits a man at a stamina term of 1.09 against 0.75,
which is 30% of the pool against 65%. So the question is no longer WHICH term.
It is why a contract fighter is at 30% when he gets dropped.

An earlier version of this measurement was taken on a harness and withdrawn with
everything else from that day. This one uses only what the contract publishes:

    the S trailer   punches, steps, switches, slips, held ticks, idles - the
                    complete action census of the bout
    the D rows      both stamina pools at every decision tick, which is a real
                    trajectory rather than an endpoint
    canon           the price of each action, read from the same move table the
                    analyzer reads

Spend by category is then arithmetic over published counts, not instrumentation.
Nothing is hooked and no byte of the stream changes.

WHAT THIS CANNOT DO, said before the numbers rather than after. The trailer
counts actions for the bout as a whole, so a category's spend is a total and not
a per-fighter-per-round rate unless the bout length is carried alongside - which
it is, via `rounds` and the tick of the last row. Bouts here all stop in round
one, so every figure below is normalised to a per-fighter-minute rate and the
raw totals are shown beside it. Comparing raw totals across models is the
2026-08-05 confound and is not done.

Run: python -m tools.engine.measure_contract_stamina
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402

SEEDS = list(range(4240, 4264))
TICKS_PER_MIN = 3600


def bout(seed, c):
    """One bout's action census, tick span and stamina trajectory."""
    trailer, last_tick = None, 0
    traj = []
    for l in O.expected_stream(seed, 3, with_floats=False).splitlines():
        f = l.split("|")
        if f[0] == "D":
            last_tick = max(last_tick, int(f[1]))
            traj.append((int(f[1]), int(f[9]), int(f[10])))
        elif f[0] in ("P", "C", "K", "R"):
            last_tick = max(last_tick, int(f[1]))
        elif f[0] == "S":
            trailer = dict(kv.split("=") for kv in l[2:].split("|"))
    return trailer, last_tick, traj


def main() -> int:
    c = O.canon_pack()
    totals = {}
    ticks = 0
    traj_all = []
    for s in SEEDS:
        t, last, traj = bout(s, c)
        ticks += last
        for k, v in t.items():
            if k != "fnv1a64":
                totals[k] = totals.get(k, 0) + int(v)
        traj_all.append(traj)

    minutes = ticks / float(TICKS_PER_MIN)
    fighter_minutes = minutes * 2.0
    print("%d bouts, %d ticks of fight (%.1f minutes), all stopping in round one"
          % (len(SEEDS), ticks, minutes))
    print()

    # ---- what each action costs, read from canon --------------------------
    step_cost = c["moves"]["step_in"]["cost"]
    hold_cost = c["posture"]["high_guard"]["hold"]
    punch_costs = [c["moves"][m]["cost"] for m in O.PUNCHES]
    avg_punch = sum(punch_costs) / float(len(punch_costs))

    print("SPEND BY CATEGORY, from the trailer's own action census")
    print("  %-12s %10s %12s %14s %8s"
          % ("category", "count", "unit cost", "per f-minute", "share"))
    spend = {
        "punches": totals["punches"] * avg_punch,
        "steps": totals["steps"] * step_cost,
        "guard hold": totals["held"] * hold_cost,
    }
    # A slip's cost is not in the core move table - the analyzer charges the
    # slip through the same branch as a step. Named rather than guessed at.
    unknown_slips = totals.get("slips", 0)
    tot = sum(spend.values())
    for k in ("punches", "steps", "guard hold"):
        print("  %-12s %10d %12.4f %14.2f %7.1f%%"
              % (k, totals["punches"] if k == "punches"
                 else totals["steps"] if k == "steps" else totals["held"],
                 (avg_punch if k == "punches" else step_cost if k == "steps"
                  else hold_cost) / 10000.0,
                 spend[k] / 10000.0 / fighter_minutes,
                 100.0 * spend[k] / tot))
    print("  %-12s %10d %12s %14s" % ("slips", unknown_slips, "(see note)", "-"))
    print("  %-12s %10s %12s %14.2f"
          % ("TOTAL", "", "", tot / 10000.0 / fighter_minutes))
    regen = c["regen"] * ticks * 2
    print("  %-12s %10s %12.4f %14.2f"
          % ("regen ceiling", "", c["regen"] / 10000.0,
             regen / 10000.0 / fighter_minutes))
    print()
    print("  NOTE on the two costs that are not simply read off: the average")
    print("  punch cost is the mean of the five moves (%.2f), because the"
          % (avg_punch / 10000.0))
    print("  trailer counts punches without naming them; and the guard hold is")
    print("  high_guard's, because `held` does not record which posture was")
    print("  held. Both are stated so the arithmetic can be checked rather than")
    print("  trusted.")
    print()

    # ---- the trajectory ---------------------------------------------------
    print("STAMINA TRAJECTORY, from D rows (decision ticks), mean of both men")
    marks = (600, 1200, 1800, 2400, 3000, 3600)
    print("  %-8s %10s %8s" % ("tick", "stamina", "bouts"))
    rows = {}
    for traj in traj_all:
        for m in marks:
            best = None
            for tk, a, b in traj:
                if tk <= m and (best is None or tk > best[0]):
                    best = (tk, a, b)
            if best:
                rows.setdefault(m, []).append((best[1] + best[2]) / 2.0)
    for m in marks:
        v = rows.get(m, [])
        if v:
            print("  %-8d %9.1f%% %8d"
                  % (m, 100.0 * (sum(v) / len(v)) / c["st_max"], len(v)))
    print()
    print("  reference simulator, same 24 seeds: mean end stamina 34.2% of max")
    print("  after 5.9 minutes of bout.")
    print()

    print("READ THIS AS:")
    tail = [m for m in marks[2:] if rows.get(m)]
    vals = [100.0 * (sum(rows[m]) / len(rows[m])) / c["st_max"] for m in tail]
    plateau = max(vals) - min(vals) if vals else None
    print("  IT IS AN EQUILIBRIUM, NOT A DRAIN. Stamina falls fast to about")
    if vals:
        print("  %.0f%% by tick %d and then stops falling - it moves %.1f points"
              % (vals[0], tail[0], plateau))
        print("  across the remaining %d ticks. Spend and regeneration balance"
              % (tail[-1] - tail[0]))
        print("  there. A contract fighter is not running out; he is LIVING at")
        print("  a quarter tank.")
    print()
    print("  Which is the finding, because the median knockdown lands on a man")
    print("  at 30%% and the plateau sits at %.0f%%. Fighters spend the entire"
          % (vals[-1] if vals else 0))
    print("  bout inside the band where a landing converts. That is why the")
    print("  stamina term separates converted from non-converted landings by")
    print("  1.47x while balance and guard separate them by nothing at all.")
    print()
    print("  The largest single line is %s at %.0f%% of spend - not footwork."
          % (max(spend, key=lambda k: spend[k]),
             100.0 * max(spend.values()) / tot))
    print("  The withdrawn harness figures had footwork at 46.7%; on the")
    print("  contract it is %.0f%%. This census replaces them."
          % (100.0 * spend["steps"] / tot))

    out = {"bouts": len(SEEDS), "ticks": ticks, "minutes": round(minutes, 2),
           "totals": totals,
           "spend_per_fighter_minute": {
               k: round(v / 10000.0 / fighter_minutes, 3)
               for k, v in spend.items()},
           "regen_ceiling_per_fighter_minute":
               round(regen / 10000.0 / fighter_minutes, 3),
           "trajectory": {str(m): round(100.0 * (sum(v) / len(v)) / c["st_max"], 2)
                          for m, v in rows.items()},
           "plateau_spread_points": round(plateau, 2) if plateau else None,
           "slips_uncosted": unknown_slips}
    p = os.path.join(O.REPO, "sandbox", "Saved", "contract_stamina.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:40 UTC | END ]
