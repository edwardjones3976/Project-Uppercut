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
    for tier in TIERS:
        agg = {"blocked": 0, "landed": 0, "knockdowns": 0, "stopped": 0,
               "rounds": 0, "seeds": len(seeds), "thrown": 0, "end_stamina": 0.0}
        for s in seeds:
            r = run(s, tier)
            for k in ("blocked", "landed", "knockdowns", "rounds", "thrown"):
                agg[k] += r[k]
            agg["end_stamina"] += sum(r["end_stamina"]) / 2.0
            agg["stopped"] += 1 if r["stopped"] else 0
        agg["end_stamina"] = round(agg["end_stamina"] / len(seeds), 1)
        agg["decisions"] = agg["seeds"] - agg["stopped"]
        agg["reaction_ticks"] = tier["reaction_ticks"]
        agg["aggression_bias"] = tier["aggression_bias"]
        out[tier["id"]] = agg
        print("%-10s cadence=%-3d aggr=%.2f  thrown=%-6d end_stam=%-6.1f "
              "kd=%-4d stopped=%d/%d"
              % (tier["id"], agg["reaction_ticks"], agg["aggression_bias"],
                 agg["thrown"], agg["end_stamina"], agg["knockdowns"],
                 agg["stopped"], agg["seeds"]))
    p = os.path.join(O.REPO, "sandbox", "Saved", "cpu_tier_experiment.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 00:10 UTC | END ]
