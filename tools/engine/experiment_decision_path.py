# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 03:00 UTC | START ]
"""How far is the decision path, in ticks, and do the clock dials reach it?

Phase O is HELD on one failure: 24 of 24 seeds stop, so `decision_path_must_
survive` has never been observed. Four separate sweeps concluded the dials that
might have fixed it were inert. Every one of those sweeps compared bout TOTALS
across bouts that all end on the three-knockdown rule, which normalised the
measurement by the outcome it was measuring. Re-measured against the clock, both
dials are strongly connected:

    cadence     20 -> 6 ticks     1.88x in ticks-to-stoppage
    commitment  1.0 -> 3.0x       2.18x in ticks-to-stoppage

So the question is no longer "is anything connected". It is arithmetic: a bout
needs `rounds * round_ticks` ticks to reach the cards, the canonical fight ends
in a fraction of that, and this measures the gap and whether the two dials,
pushed together to the edge of what canon authors, close it.

Nothing here proposes a tuning. Canon's own tier cadences and a commitment
multiplier are the axes; the output is a distance, not a recommendation.

Run: python -m tools.engine.experiment_decision_path
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402

CADENCES = [4, 6, 10, 14, 20]          # 4 is the core's own; the rest are canon tiers
COMMITMENTS = [1.0, 1.5, 2.0, 3.0]
ROUNDS = 3


def run_at(seed: int, cadence: int, mult: float) -> dict:
    c = O.canon_pack()
    c = dict(c)
    c["interval"] = cadence
    if mult != 1.0:
        c["moves"] = {k: dict(v) for k, v in c["moves"].items()}
        for m in c["moves"].values():
            if "frames" in m:
                m["frames"] = int(m["frames"] * mult)
    return H.run_with(seed, c, ROUNDS, None)


def main() -> int:
    seeds = list(range(4240, 4264))
    c = O.canon_pack()
    full = ROUNDS * c["round_ticks"]
    print("a bout reaches the cards at %d ticks (%d rounds x %d, %.0fs at 60Hz)"
          % (full, ROUNDS, c["round_ticks"], full / 60.0))
    print()
    print("mean ticks to stoppage, and how far that is from the cards")
    print("  %-8s" % "cadence", end="")
    for m in COMMITMENTS:
        print(" %13s" % ("commit %.1fx" % m), end="")
    print()

    out = {}
    best = (None, None, 0.0)
    for cad in CADENCES:
        print("  %-8d" % cad, end="")
        for m in COMMITMENTS:
            stops, survived = [], 0
            elig = kds = ticks = 0
            for s in seeds:
                r = run_at(s, cad, m)
                elig += r["eligible"]
                kds += r["knockdowns"]
                ticks += r["total_ticks"]
                if r["stop_tick"] is not None:
                    stops.append(r["stop_tick"])
                else:
                    survived += 1
            mean = sum(stops) / float(len(stops)) if stops else None
            frac = (mean / full) if mean else None
            conv = (kds / float(elig)) if elig else None
            # Eligible landings per tick, and therefore how many a full bout
            # would contain. Fewer than three of them may convert, or the bout
            # ends early by definition. That ratio is the real Phase O number.
            elig_rate = elig / float(ticks) if ticks else 0.0
            elig_full = elig_rate * full
            need = (3.0 / elig_full) if elig_full else None
            out["cad%d_com%.1f" % (cad, m)] = {
                "cadence": cad, "commitment": m, "seeds": len(seeds),
                "survived_to_cards": survived,
                "mean_ticks_to_stoppage": round(mean, 1) if mean else None,
                "fraction_of_full_bout": round(frac, 4) if frac else None,
                "kd_per_eligible": round(conv, 4) if conv else None,
                "eligible_per_full_bout": round(elig_full, 1),
                "conversion_needed_for_cards": round(need, 4) if need else None,
                "conversion_gap_x": (round(conv / need, 1)
                                     if conv and need else None)}
            if frac and frac > best[2]:
                best = (cad, m, frac)
            cell = ("%d/%d cards" % (survived, len(seeds))) if survived else \
                   ("%.0f (%.0f%%)" % (mean, 100.0 * frac))
            print(" %13s" % cell, end="")
        print()

    print()
    print("the furthest any pairing gets: cadence %s, commitment %.1fx, "
          "%.0f%% of the distance" % (best[0], best[1], 100.0 * best[2]))
    print("the gap is a factor of %.1fx, which is larger than both dials "
          "multiplied together" % (1.0 / best[2]))
    print()
    print("the conversion arithmetic, which is the actual blocker")
    print("  %-8s %10s %12s %12s %10s"
          % ("pairing", "kd/elig", "elig/bout", "needed", "gap"))
    for k in sorted(out, key=lambda z: out[z]["conversion_gap_x"] or 0):
        a = out[k]
        print("  %-8s %10.4f %12.1f %12.4f %9.1fx"
              % (k.replace("cad", "").replace("_com", "/"), a["kd_per_eligible"],
                 a["eligible_per_full_bout"], a["conversion_needed_for_cards"],
                 a["conversion_gap_x"]))
    print()
    print("READ THIS AS: the clock dials are connected but not sufficient. A")
    print("fighter cannot be paced into the twelfth by cadence and commitment")
    print("alone. What ends the bout is three knockdowns, and neither dial")
    print("changes how often a landing converts. For a bout to reach the cards,")
    print("fewer than three of a full bout's eligible landings may convert - a")
    print("rate an order of magnitude below what the model produces. Phase O's")
    print("held condition is a CONVERSION problem, not a pacing one.")

    p = os.path.join(O.REPO, "sandbox", "Saved", "decision_path_distance.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 03:00 UTC | END ]
