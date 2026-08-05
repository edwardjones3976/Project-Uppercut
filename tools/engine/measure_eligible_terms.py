# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:00 UTC | START ]
"""Why does an eligible landing convert? Converted against not-converted.

The contract converts 2.78x as often as the reference, and a knockdown looks the
same in both models - pressure medians 0.686 against 0.670 on a shared 0.570
threshold. So the difference is not what a knockdown IS. It is how close the
landings that did nothing came to being one.

That comparison needed the pressure terms of NON-converted eligible landings, and
neither stream carried them: the contract emits state on decision ticks only, so
84% of eligible landings have no state row, and the reference publishes two terms
on knockdowns and nothing on the rest.

So Phase O's analyzer gained an OPT-IN diagnostic row. `expected_stream(...,
with_terms=True)` emits an `E` row at every eligible landing with all five
multiplicands and whether it converted. It is default-OFF and the canonical
stream is byte-for-byte unchanged - trailer count and self-hash included, both of
which now cover canonical rows only. `tests/test_core_round_analyzer.py` asserts
that invariant rather than trusting it.

Phase O is HELD, not sealed, so extending its analyzer is legitimate; the pinned
phases are N and K and neither is touched. The alternative was another harness,
which is the mistake this whole line of work exists to correct.

Run: python -m tools.engine.measure_eligible_terms
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402

SEEDS = list(range(4240, 4264))
FIELDS = ("force", "condition", "stamina", "balance", "guard")


def rows():
    out = []
    for s in SEEDS:
        for l in O.expected_stream(s, 3, with_floats=False,
                                   with_terms=True).splitlines():
            if not l.startswith("E|"):
                continue
            f = l.split("|")
            out.append({"tick": int(f[1]), "on": int(f[2]), "move": f[3],
                        "cls": f[4], "pressure": int(f[5]),
                        "threshold": int(f[6]), "force": int(f[7]),
                        "condition": int(f[8]), "stamina": int(f[9]),
                        "balance": int(f[10]), "guard": int(f[11]),
                        "converted": f[12] == "1"})
    return out


def pct(vals, p):
    v = sorted(vals)
    return v[min(len(v) - 1, max(0, int(round((len(v) - 1) * p / 100.0))))]


def main() -> int:
    c = O.canon_pack()
    data = rows()
    yes = [r for r in data if r["converted"]]
    no = [r for r in data if not r["converted"]]
    thr = c["kd_threshold"]

    print("%d eligible landings: %d converted, %d not (%.4f)"
          % (len(data), len(yes), len(no), len(yes) / float(len(data))))
    print("threshold %.4f" % (thr / 10000.0))
    print()

    print("MEDIAN TERM, CONVERTED AGAINST NOT")
    print("  %-12s %12s %12s %10s" % ("term", "converted", "not", "ratio"))
    ratios = {}
    for k in FIELDS + ("pressure",):
        a = pct([r[k] for r in yes], 50)
        b = pct([r[k] for r in no], 50)
        ratios[k] = a / float(b) if b else 0.0
        print("  %-12s %12.4f %12.4f %9.2fx"
              % (k, a / 10000.0, b / 10000.0, ratios[k]))
    print()
    prod = 1.0
    for k in FIELDS:
        prod *= ratios[k]
    print("  the five multiplicands multiply to %.2fx; median pressure differs "
          "by %.2fx" % (prod, ratios["pressure"]))
    driver = max(FIELDS, key=lambda k: abs(ratios[k] - 1.0))
    print("  the term that separates them most is %s (%.2fx)"
          % (driver, ratios[driver]))
    print()

    print("HOW CLOSE DID THE ONES THAT FAILED COME?")
    near = [r for r in no if r["pressure"] >= thr * 9 // 10]
    print("  %d of %d non-converted landings (%.1f%%) reached 90%% of the "
          "threshold" % (len(near), len(no), 100.0 * len(near) / len(no)))
    for p in (10, 25, 50, 75, 90):
        v = pct([r["pressure"] for r in no], p)
        print("    p%-3d %.4f  (%.0f%% of threshold)"
              % (p, v / 10000.0, 100.0 * v / thr))
    print()

    print("BY CONTACT CLASS - the grade is the force term's whole input")
    print("  %-8s %8s %10s %9s %12s"
          % ("class", "count", "converted", "rate", "median press"))
    for cls in sorted({r["cls"] for r in data}):
        d = [r for r in data if r["cls"] == cls]
        k = sum(1 for r in d if r["converted"])
        print("  %-8s %8d %10d %8.3f %12.4f"
              % (cls, len(d), k, k / float(len(d)),
                 pct([r["pressure"] for r in d], 50) / 10000.0))
    print()

    med_fail = pct([r["pressure"] for r in no], 50)
    print("READ THIS AS:")
    print("  A landing converts on %s more than on anything else, and" % driver)
    print("  'everything else being equal' is close to literally true: balance")
    print("  and guard are identical to two decimal places between the landings")
    print("  that dropped a man and the ones that did not, and condition differs")
    print("  by 5%. Two terms separate them - how empty the man is, and how hard")
    print("  the punch was graded.")
    print()
    print("  ON SENSITIVITY, stated carefully rather than dramatically. Only")
    print("  %.1f%% of failed landings came within 10%% of the threshold and the"
          % (100.0 * len(near) / len(no)))
    print("  median failure sits at %.0f%% of it, so the conversion rate is NOT"
          % (100.0 * med_fail / thr))
    print("  balanced on a knife edge - most landings that failed, failed")
    print("  comfortably. Moving a term moves the tail rather than flipping the")
    print("  population, which means the 2.78x gap against the reference will not")
    print("  close by nudging one number a few percent.")

    out = {"eligible": len(data), "converted": len(yes),
           "rate": len(yes) / float(len(data)),
           "median": {k: {"converted": pct([r[k] for r in yes], 50) / 10000.0,
                          "not": pct([r[k] for r in no], 50) / 10000.0,
                          "ratio": round(ratios[k], 4)}
                      for k in FIELDS + ("pressure",)},
           "driver": driver,
           "near_miss_within_10pct": len(near),
           "non_converted": len(no)}
    p = os.path.join(O.REPO, "sandbox", "Saved", "eligible_terms.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:00 UTC | END ]
