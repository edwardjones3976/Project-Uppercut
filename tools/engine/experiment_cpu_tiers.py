# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 00:10 UTC | START ]
"""Does a fighter who paces himself let the fight reach the cards?

Every phase so far has chosen actions uniformly at random, every
`decision_interval_ticks` (4). Canon does not describe a fighter like that
anywhere. `cpu_decision_model.difficulty_tiers` authors both dials:

    tier        reaction_ticks   aggression_bias   error_rate
    novice                  20              0.35         0.35
    club                    14              0.45         0.22
    contender               10              0.55         0.12
    champion                 6              0.60         0.05

Two gaps, both measurable rather than argued:

  CADENCE. The core acts every 4 ticks. Canon's SLOWEST tier reacts every 20 and
  its fastest every 6. The slice has been deciding five times faster than a
  novice and one and a half times faster than a champion - a work rate no
  authored fighter has.

  AGGRESSION. Uniform choice over eleven actions throws a punch 5/11 = 0.4545 of
  the time, which sits between club and contender. The slice has been punching
  like a mid-tier fighter while reacting faster than a champion.

Nothing here is invented: the cadence and the bias are canon's own numbers, and
the action set is unchanged. `reaction.respects_commitment` and
`may_cancel_own_commitment: false` are honoured - a decision still cannot
interrupt a commitment.

Rule 3/4 boundary: this policy reads range band, its own stamina and its own
commitment. All three are `observable_inputs`. It reads no card, no opponent
input buffer, no RNG state, no hidden attribute and no future tick.

Run: python -m tools.engine.experiment_cpu_tiers
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402

TIERS = json.load(io.open(os.path.join(O.REPO, "data", "cpu_decision_model.json"),
                          encoding="utf-8"))["difficulty_tiers"]
PUNCH_IDX = [O.ACTIONS.index(p) for p in O.PUNCHES]
OTHER_IDX = [i for i in range(len(O.ACTIONS)) if i not in PUNCH_IDX]


def choose(x: int, aggression_q: int):
    """Throw with probability aggression_bias; otherwise do something else.

    The bias is canon's. The choice WITHIN each group stays uniform, because
    canon authors no preference there and this experiment invents nothing."""
    roll = x % 10000
    if roll < aggression_q:
        return O.ACTIONS[PUNCH_IDX[(x // 10000) % len(PUNCH_IDX)]]
    return O.ACTIONS[OTHER_IDX[(x // 10000) % len(OTHER_IDX)]]


def run(seed: int, tier: dict, rounds: int = 3) -> dict:
    """H.run's fight, with the tier's cadence and bias in place of the coin."""
    c = O.canon_pack()
    interval = int(tier["reaction_ticks"])
    aggression_q = O.q(tier["aggression_bias"])
    saved = c["interval"]
    try:
        c["interval"] = interval
        return H.run_with(seed, c, rounds, lambda x: choose(x, aggression_q))
    finally:
        c["interval"] = saved


def main() -> int:
    seeds = list(range(4240, 4264))
    out = {}
    print("Metrics are RATES and TIMES. Totals are reported but must not be")
    print("compared across tiers: every bout ends on the three-knockdown rule,")
    print("so its length is set by the outcome. See the 2026-08-05 confound entry.")
    print()
    print("  %-10s %7s %7s %9s %9s %9s %9s"
          % ("tier", "cadence", "aggr", "kd/elig", "t_1stKD", "t_stop", "stam@r1"))
    for tier in TIERS:
        agg = {"blocked": 0, "landed": 0, "knockdowns": 0, "stopped": 0,
               "rounds": 0, "seeds": len(seeds), "thrown": 0, "end_stamina": 0.0,
               "eligible": 0, "ticks": 0}
        firsts, stops = [], []
        gauge_at = {g: [] for g in (600, 1200, 1800, 2400, 3600)}
        for s in seeds:
            r = run(s, tier)
            for k in ("blocked", "landed", "knockdowns", "rounds", "thrown",
                      "eligible"):
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
        agg["end_stamina"] = round(agg["end_stamina"] / len(seeds), 1)
        agg["decisions"] = agg["seeds"] - agg["stopped"]
        agg["reaction_ticks"] = tier["reaction_ticks"]
        agg["aggression_bias"] = tier["aggression_bias"]
        # The four confound-free readings.
        agg["kd_per_eligible"] = (round(agg["knockdowns"] / float(agg["eligible"]), 4)
                                  if agg["eligible"] else None)
        agg["mean_ticks_to_first_kd"] = (round(sum(firsts) / float(len(firsts)), 1)
                                         if firsts else None)
        agg["mean_ticks_to_stoppage"] = (round(sum(stops) / float(len(stops)), 1)
                                         if stops else None)
        agg["stamina_at"] = {str(g): (round(sum(v) / float(len(v)), 2) if v else None)
                             for g, v in gauge_at.items()}
        agg["seeds_reaching"] = {str(g): len(v) for g, v in gauge_at.items()}
        agg["punches_per_1000_ticks"] = round(
            1000.0 * agg["thrown"] / float(agg["ticks"]), 1) if agg["ticks"] else None
        out[tier["id"]] = agg
        print("  %-10s %7d %7.2f %9s %9s %9s %9s"
              % (tier["id"], agg["reaction_ticks"], agg["aggression_bias"],
                 agg["kd_per_eligible"], agg["mean_ticks_to_first_kd"],
                 agg["mean_ticks_to_stoppage"], agg["stamina_at"]["1200"]))
    print()
    print("  %-10s %9s %9s %9s" % ("tier", "thrown/1k", "eligible", "stopped"))
    for tier in TIERS:
        a = out[tier["id"]]
        print("  %-10s %9.1f %9d %5d/%-3d"
              % (tier["id"], a["punches_per_1000_ticks"], a["eligible"],
                 a["stopped"], a["seeds"]))
    print()
    print("  stamina at fixed ticks (n = seeds still fighting at that tick)")
    print("  %-10s %14s %14s %14s %14s"
          % ("tier", "t=600", "t=1200", "t=1800", "t=2400"))
    for tier in TIERS:
        a = out[tier["id"]]
        cells = []
        for g in ("600", "1200", "1800", "2400"):
            v, n = a["stamina_at"][g], a["seeds_reaching"][g]
            cells.append("--" if v is None else "%.1f (n=%d)" % (v, n))
        print("  %-10s %14s %14s %14s %14s" % (tier["id"], cells[0], cells[1],
                                               cells[2], cells[3]))
    p = os.path.join(O.REPO, "sandbox", "Saved", "cpu_tier_experiment.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 00:10 UTC | END ]
