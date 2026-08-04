# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 00:35 UTC | START ]
"""Which term of canon's pressure product actually carries the knockdowns?

Four consecutive wrong diagnoses is enough. This measures instead of predicting,
and it needs no new instrumentation: the K row already carries every term.

    pressure = force x (baseline + accumulated) x (1.4 - stamina_frac)
                     x balance x guard

Each factor is reported as its INFLATION over a fresh, balanced, fully covered
target - the reference fighter for whom the product is smallest:

    condition  (0.55 + accumulated) / 0.55          1.0 when undamaged
    stamina    (1.4 - stamina_frac) / 0.4           1.0 at full stamina
    balance    balance / 1.0                        1.0 when not caught
    guard      guard / 1.0                          1.0 when the lane is covered

Their product is how many times more dangerous the punch was than the same punch
against a fresh, set, covered opponent. Whichever factor's median is largest is
the term carrying the knockdown rate, and it is the only one worth touching.

Run: python -m tools.engine.measure_pressure_terms
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402


def median(v):
    s = sorted(v)
    return s[len(s) // 2] if s else 0.0


def main() -> int:
    c = O.canon_pack()
    base = c["baseline"] / 10000.0          # 0.55
    terms = {"condition": [], "stamina": [], "balance": [], "guard": []}
    total = []
    moves = {}
    for seed in range(4240, 4264):
        for line in O.expected_stream(seed, 3, with_floats=False).splitlines():
            if not line.startswith("K|"):
                continue
            f = line.split("|")
            acc = int(f[6]) / 10000.0
            sf = int(f[7]) / 10000.0
            bal = int(f[8]) / 10000.0
            gd = int(f[9]) / 10000.0
            t = {"condition": (base + acc) / base,
                 "stamina": (1.4 - sf) / 0.4,
                 "balance": bal,
                 "guard": gd}
            for k, v in t.items():
                terms[k].append(v)
            total.append(t["condition"] * t["stamina"] * t["balance"] * t["guard"])
            moves[f[3]] = moves.get(f[3], 0) + 1

    n = len(total)
    print("knockdowns measured: %d" % n)
    print()
    print("  %-11s %8s %8s %8s   %s" % ("term", "median", "min", "max", "reading"))
    order = sorted(terms, key=lambda k: -median(terms[k]))
    for k in order:
        v = terms[k]
        print("  %-11s %8.2f %8.2f %8.2f   %s"
              % (k, median(v), min(v), max(v),
                 "<-- carries it" if k == order[0] else ""))
    print()
    print("  combined median inflation over a fresh, set, covered target: %.2fx"
          % median(total))
    print()
    print("  by move:", dict(sorted(moves.items(), key=lambda kv: -kv[1])))

    out = {"knockdowns": n,
           "median": {k: round(median(v), 4) for k, v in terms.items()},
           "combined_median": round(median(total), 4),
           "by_move": moves}
    p = os.path.join(O.REPO, "sandbox", "Saved", "pressure_terms.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 00:35 UTC | END ]
