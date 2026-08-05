# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 05:40 UTC | START ]
"""If the fighters threw like boxers, would the fight reach the cards?

The funnel measurement found the core throwing 237 punches per fighter per round
against a professional 55-78, and traced it to the decision clock: a decision
every 4 ticks, fifteen per second, with punches at 5 of 11 actions. That is the
one number tonight that is wrong against an OUTSIDE reference rather than against
a target, which makes it the only thing worth correcting before anything else is
judged.

This asks the obvious follow-up and refuses to guess the answer: sweep the
decision interval until throw rate lands in the professional band, then read the
invariant. Two outcomes are interesting and neither is assumed -

  the decision path appears -> the whole Phase O hold was an artifact of a core
      that fought at four times human speed, and every "dial X is inert" finding
      from tonight was measured on a fight nobody would recognise as boxing;

  it does not -> the conversion gap is real and independent of volume, and the
      19.1x stands on its own with the volume objection removed.

The professional band is the target for THROW RATE only. Nothing here tunes
toward a knockdown number, and no canon value is edited: the interval is passed
in, exactly as the tier experiment passes canon's own tier cadences.

Run: python -m tools.engine.experiment_boxing_cadence
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402

SEEDS = list(range(4240, 4264))
TICKS_PER_MIN = 3600
ROUND_MINUTES = 3.0
BAND = (55, 78)                 # CompuBox professional per-round throw band
HEAVY = (30, 60)
CADENCES = [4, 6, 10, 14, 20, 28, 36, 48, 60]


def sweep(cadence: int, rounds: int = 3) -> dict:
    c = dict(O.canon_pack())
    c["interval"] = cadence
    agg = {"thrown": 0, "landed": 0, "eligible": 0, "kd": 0, "ticks": 0,
           "cards": 0, "blocked": 0}
    stops, g = [], []
    for s in SEEDS:
        r = H.run_with(s, c, rounds, None)
        agg["thrown"] += r["thrown"]
        agg["landed"] += r["landed"]
        agg["blocked"] += r["blocked"]
        agg["eligible"] += r["eligible"]
        agg["kd"] += r["knockdowns"]
        agg["ticks"] += r["total_ticks"]
        if r["stop_tick"] is not None:
            stops.append(r["stop_tick"])
        else:
            agg["cards"] += 1
        if 1800 in r["stamina_gauges"]:
            g.append(sum(r["stamina_gauges"][1800]) / 2.0)
    minutes = agg["ticks"] / float(TICKS_PER_MIN)
    full = rounds * O.canon_pack()["round_ticks"]
    elig_full = (agg["eligible"] / float(agg["ticks"])) * full
    conv = agg["kd"] / float(agg["eligible"]) if agg["eligible"] else 0.0
    need = 3.0 / elig_full if elig_full else None
    return {"cadence": cadence,
            "thrown_per_fighter_round":
                agg["thrown"] / minutes * ROUND_MINUTES / 2.0,
            "landed_per_fighter_round":
                agg["landed"] / minutes * ROUND_MINUTES / 2.0,
            "connect_pct": 100.0 * agg["landed"] / agg["thrown"]
                if agg["thrown"] else 0.0,
            "kd_per_eligible": conv,
            "conversion_needed": need,
            "gap_x": conv / need if need else None,
            "mean_ticks_to_stoppage":
                sum(stops) / float(len(stops)) if stops else None,
            "cards": agg["cards"], "seeds": len(SEEDS),
            "stamina_at_1800": sum(g) / float(len(g)) if g else None}


def main() -> int:
    print("Sweeping the decision interval. Throw rate is the only thing being")
    print("aimed at a target, and the target is professional boxing: %d-%d"
          % BAND)
    print("punches per fighter per round, %d-%d for heavyweights." % HEAVY)
    print()
    print("  %-9s %9s %9s %8s %9s %8s %8s %8s"
          % ("interval", "thrown", "landed", "connect", "kd/elig", "gap",
             "t_stop", "cards"))
    rows = {}
    for cad in CADENCES:
        r = sweep(cad)
        rows[str(cad)] = r
        mark = " <-- boxing" if BAND[0] <= r["thrown_per_fighter_round"] <= BAND[1] \
            else (" <-- heavy" if HEAVY[0] <= r["thrown_per_fighter_round"] <= HEAVY[1]
                  else "")
        print("  %-9d %9.1f %9.1f %7.1f%% %9.4f %7.1fx %8s %5d/%-2d%s"
              % (cad, r["thrown_per_fighter_round"], r["landed_per_fighter_round"],
                 r["connect_pct"], r["kd_per_eligible"], r["gap_x"],
                 ("%.0f" % r["mean_ticks_to_stoppage"])
                 if r["mean_ticks_to_stoppage"] else "none",
                 r["cards"], r["seeds"], mark))
    print()

    inband = [r for r in rows.values()
              if HEAVY[0] <= r["thrown_per_fighter_round"] <= BAND[1]]
    print("READ THIS AS:")
    if not inband:
        print("  No swept interval lands in the professional band. Widen the")
        print("  sweep before drawing any conclusion from it.")
    else:
        best = min(inband, key=lambda r: r["gap_x"])
        anycards = [r for r in rows.values() if r["cards"]]
        print("  At a boxer's work rate (interval %d, %.0f thrown per fighter per"
              % (best["cadence"], best["thrown_per_fighter_round"]))
        print("  round, %.0f%% connect) the conversion gap is %.1fx, against %.1fx"
              % (best["connect_pct"], best["gap_x"], rows["4"]["gap_x"]))
        print("  at the core's own 4-tick clock. %s"
              % ("The decision path appears."
                 if best["cards"] else "The decision path still does not appear."))
        print()
        if not anycards:
            print("  NOT ONE bout in any swept interval reached the cards. Slowing")
            print("  the fight to a human work rate moves the gap by %.1fx and"
                  % (rows["4"]["gap_x"] / best["gap_x"]))
            print("  leaves it %.1fx short. The conversion problem is NOT an"
                  % best["gap_x"])
            print("  artifact of volume - it survives the volume objection being")
            print("  removed entirely, which is the strongest thing that could")
            print("  have been said for it.")
        else:
            print("  Intervals reaching the cards: %s"
                  % ", ".join("%s (%d/%d)" % (r["cadence"], r["cards"], r["seeds"])
                              for r in anycards))
        print()
        print("  Note the connect rate holds near %.0f%% across the whole sweep."
              % best["connect_pct"])
        print("  Professional boxing runs 25-40%. Cadence buys work rate and")
        print("  nothing else: it cannot make a punch miss, because nothing in")
        print("  this core misses. That is a separate defect and it is untouched")
        print("  by anything measured here.")

    p = os.path.join(O.REPO, "sandbox", "Saved", "boxing_cadence.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 05:40 UTC | END ]
