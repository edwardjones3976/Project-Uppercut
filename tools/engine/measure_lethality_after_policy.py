# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 10:40 UTC | START ]
"""Where the knockdowns come from, now that volume and accuracy are fixed.

WHY THIS RE-RUN EXISTS. The lethality decomposition taken on 2026-08-05 -
stamina 1.47x, force 1.27x, condition 1.05x, balance 1.00x, guard 1.00x - was
measured against a fighter who threw 200 punches a round and could not rest.
Decisions 0015 and 0016 replaced that fighter. Every one of those numbers is
now a measurement of something that no longer exists, and re-reading them
instead of re-running them is the exact error this repository keeps a rule
about.

WHAT IT MEASURES, and nothing it measures is adjusted. Rule 14's pressure is a
product of five terms:

    p = force x (baseline + accumulated) x (1.4 - stamina_frac) x balance x guard

and it fires at `pressure_threshold`. This reads the E rows the contract emits
at every eligible landing, reports the distribution of each multiplicand, and
answers one question: WHICH TERM IS CARRYING THE KNOCKDOWNS.

It also computes the stamina BUDGET, because the term most likely to be
carrying them is the one that rewards exhaustion, and exhaustion is an
arithmetic consequence of spend against regeneration rather than an opinion.

    python -m tools.engine.measure_lethality_after_policy [--bouts 8] [--rounds 3]
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_round as O  # noqa: E402


def pct(v, n):
    return 100.0 * v / n if n else 0.0


def median(xs):
    if not xs:
        return 0
    s = sorted(xs)
    return s[len(s) // 2]


def main(argv) -> int:
    bouts = int(argv[argv.index("--bouts") + 1]) if "--bouts" in argv else 8
    rounds = int(argv[argv.index("--rounds") + 1]) if "--rounds" in argv else 3
    c = O.canon_pack()
    thr = c["kd_threshold"]

    terms = {k: [] for k in ("force", "cond", "stam", "bal", "guard", "p")}
    fired = {k: [] for k in terms}
    stam_at_kd, stam_trace, kd_count, eligible = [], {}, 0, 0

    for b in range(bouts):
        s = O.expected_stream(4242 + b, rounds, with_floats=False, with_terms=True)
        for line in s.splitlines():
            f = line.split("|")
            if f[0] == "E":
                # E|tick|defender|move|class|pressure|threshold|force|
                #   baseline+acc|1.4-stamina|balance|guard|...
                eligible += 1
                vals = {"p": int(f[5]), "force": int(f[7]), "cond": int(f[8]),
                        "stam": int(f[9]), "bal": int(f[10]),
                        "guard": int(f[11])}
                for k, v in vals.items():
                    terms[k].append(v)
                if vals["p"] >= thr:
                    for k, v in vals.items():
                        fired[k].append(v)
            elif f[0] == "K":
                # K|tick|defender|move|pressure|threshold|accumulated|
                #   stamina_fraction|balance|guard|total. Field 7 is already a
                # fraction of the pool, not an absolute.
                kd_count += 1
                stam_at_kd.append(int(f[7]))
            elif f[0] == "D" and f[3] != "held":
                # Both fighters' stamina, by minute of round time.
                minute = int(f[1]) // 3600
                stam_trace.setdefault(minute, []).extend(
                    (int(f[9]), int(f[10])))

    print("\n%d bouts x %d rounds, tier %s, ruleset %s"
          % (bouts, rounds, c["tier"], c["ruleset"]["id"]))
    print("%d eligible landings, %d knockdowns, conversion %.1f%%\n"
          % (eligible, kd_count, pct(kd_count, eligible)))

    print("  the five multiplicands, q10000, at every eligible landing")
    print("  %-10s %9s %9s %9s" % ("term", "median", "median@KD", "ratio"))
    for k, label in (("force", "force"), ("cond", "baseline+acc"),
                     ("stam", "1.4-stamina"), ("bal", "balance"),
                     ("guard", "guard")):
        m, mf = median(terms[k]), median(fired[k])
        print("  %-10s %9d %9d %9.2fx"
              % (label, m, mf, (mf / m) if m else 0))
    print("  %-10s %9d %9d" % ("pressure", median(terms["p"]), median(fired["p"])))
    print("  threshold  %9d" % thr)

    print("\n  stamina at the moment of a knockdown: median %.1f%% of the pool"
          % (median(stam_at_kd) / 100.0))
    print("\n  stamina by minute of round time (median of both fighters)")
    for minute in sorted(stam_trace)[:12]:
        xs = stam_trace[minute]
        print("    minute %-2d  %6d  (%.0f%% of max)"
              % (minute, median(xs), pct(median(xs), c["st_max"])))

    # ---- the budget, which is arithmetic rather than opinion ---------------
    # `regen` is per TICK and already in q10000, so a round's worth is a
    # multiplication and nothing else. Dividing by 10000 here once produced
    # "43 of 1,000,000" and made the shortfall look a hundred times worse than
    # it is - which would have been a false alarm dressed as a finding.
    per_round = c["round_ticks"]
    regen_round = c["regen"] * per_round
    punch_costs = [c["moves"][p]["cost"] for p in O.PUNCHES]
    mean_punch = sum(punch_costs) // len(punch_costs)
    print("\n  the stamina budget for ONE round, q10000 units")
    print("    maximum pool                       %9d" % c["st_max"])
    print("    idle regeneration, a whole round   %9d  (%.0f%% of the pool)"
          % (regen_round, pct(regen_round, c["st_max"])))
    print("    mean punch                         %9d" % mean_punch)
    print("    punches a full round of resting pays for  %6.1f"
          % (regen_round / mean_punch if mean_punch else 0))
    print("    professional volume is 55-78 punches per round.")
    print("    shortfall  %.1fx" % ((55.0 * mean_punch) / regen_round
                                    if regen_round else 0))

    out = os.path.join(O.REPO, "sandbox", "Saved", "lethality_after_policy.json")
    if os.path.isdir(os.path.dirname(out)):
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"bouts": bouts, "rounds": rounds, "eligible": eligible,
                       "knockdowns": kd_count,
                       "conversion_pct": round(pct(kd_count, eligible), 2),
                       "median_terms": {k: median(v) for k, v in terms.items()},
                       "median_terms_at_knockdown": {k: median(v)
                                                     for k, v in fired.items()},
                       "threshold": thr,
                       "median_stamina_at_knockdown": median(stam_at_kd),
                       "regen_per_round": regen_round,
                       "mean_punch_cost": mean_punch}, fh, indent=2)
        print("\nwrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 10:40 UTC | END ]
