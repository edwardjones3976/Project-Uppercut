# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:10 UTC | START ]
"""Is 0.3196 too high, and against what? The contract beside the reference.

The Phase O contract converts 0.3196 of its knockdown-eligible landings and stops
24 of 24 bouts. The reference simulator - the model canon's 0.57 threshold was
actually swept against - reaches the cards in 20 of 24. Until now those two facts
have been quoted side by side without the one number that connects them: the
reference's own conversion rate.

Both are computed the same way, from each model's own published events, with the
same definition of eligible:

    a LANDING, on a region canon lists in `kd_regions`, graded a class the
    pressure formula actually reads (`solid` or `clean`)

  contract    P rows from `analyze_core_round.expected_stream`; K rows count the
              conversions
  reference   `punch_outcome` events carry class and region; `knockdown` events
              count the conversions

NOTHING IS INSTRUMENTED. Both models already say all of this out loud, which is
the property that makes the comparison trustworthy rather than convenient - the
lesson of 2026-08-05, where a day of measurement was taken on a harness because
the harness was the easy thing to hook.

CAVEAT ON THE COMPARISON, stated up front. The two models do not run the same
bout: the reference runs three 120-second rounds and the contract three
180-second rounds, and the contract stops in round one every time. Conversion per
eligible landing is a RATE and survives that, which is the whole reason it is the
metric here rather than any total. Bout-level figures below are reported for
context and must not be compared across the two columns - the confound of
2026-08-05 was exactly that mistake.

Run: python -m tools.engine.measure_conversion_gap
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402

REPO = O.REPO
if REPO not in sys.path:
    sys.path.insert(0, REPO)

SEEDS = list(range(4240, 4264))
PROFILES = ["technician", "rusher", "counterpuncher", "drainer",
            "power_threat", "showman"]


def contract_side(c):
    elig = conv = stopped = 0
    by_move = {}
    for s in SEEDS:
        for l in O.expected_stream(s, 3, with_floats=False).splitlines():
            f = l.split("|")
            if f[0] == "P" and f[4] == "landed" \
                    and f[5] in c["kd_regions"] and f[13] in c["kd_force"]:
                elig += 1
                by_move.setdefault(f[3], [0, 0])[0] += 1
            elif f[0] == "K":
                conv += 1
                if f[3] in by_move:
                    by_move[f[3]][1] += 1
            elif f[0] == "V" and f[1] == "stoppage":
                stopped += 1
    return {"eligible": elig, "converted": conv, "stopped": stopped,
            "bouts": len(SEEDS), "by_move": by_move}


def reference_side(c):
    from tools.uppercut_sim.engine import Bout   # noqa: E402
    elig = conv = stopped = 0
    by_move = {}
    for i, s in enumerate(SEEDS):
        bout = Bout(s, PROFILES[i % len(PROFILES)],
                    PROFILES[(i + 3) % len(PROFILES)], rounds=3,
                    round_seconds=120)
        log = bout.run()
        last_move = None
        for e in log:
            t = e.get("type")
            p = e.get("payload") or {}
            if t == "punch_outcome":
                if p.get("class") in c["kd_force"] \
                        and p.get("region") in c["kd_regions"]:
                    elig += 1
                    by_move.setdefault(p.get("move"), [0, 0])[0] += 1
                    last_move = p.get("move")
            elif t == "knockdown":
                conv += 1
                if last_move in by_move:
                    by_move[last_move][1] += 1
            elif t == "stoppage":
                stopped += 1
    return {"eligible": elig, "converted": conv, "stopped": stopped,
            "bouts": len(SEEDS), "by_move": by_move}


def pct(vals, p):
    v = sorted(vals)
    return v[min(len(v) - 1, max(0, int(round((len(v) - 1) * p / 100.0))))]


def knockdown_terms():
    """The two terms BOTH models publish at a knockdown, and only those.

    The contract's K row carries pressure, accumulated condition, stamina
    fraction, balance and guard. The reference's knockdown payload carries
    pressure and accumulated condition and nothing else. Comparing only the
    intersection is the honest move; inferring the rest would be inventing.
    """
    from tools.uppercut_sim.engine import Bout   # noqa: E402
    con = {"pressure": [], "acc": []}
    ref = {"pressure": [], "acc": []}
    for s in SEEDS:
        for l in O.expected_stream(s, 3, with_floats=False).splitlines():
            if l.startswith("K|"):
                f = l.split("|")
                con["pressure"].append(int(f[4]) / 10000.0)
                con["acc"].append(int(f[6]) / 10000.0)
    for i, s in enumerate(SEEDS):
        bout = Bout(s, PROFILES[i % len(PROFILES)],
                    PROFILES[(i + 3) % len(PROFILES)], rounds=3,
                    round_seconds=120)
        for e in bout.run():
            if e.get("type") == "knockdown":
                p = e.get("payload") or {}
                ref["pressure"].append(float(p.get("pressure", 0.0)))
                ref["acc"].append(float(p.get("accumulated_condition", 0.0)))
    return con, ref


def main() -> int:
    c = O.canon_pack()
    con = contract_side(c)
    try:
        ref = reference_side(c)
    except Exception as exc:                     # pragma: no cover - diagnostic
        print("reference simulator could not be run: %r" % (exc,))
        return 1

    print("ELIGIBLE = a landing, on %s, graded %s"
          % (" or ".join(c["kd_regions"]), " or ".join(sorted(c["kd_force"]))))
    print()
    print("  %-14s %10s %10s %12s %10s"
          % ("", "eligible", "converted", "rate", "stopped"))
    for name, d in (("contract", con), ("reference", ref)):
        print("  %-14s %10d %10d %12.4f %6d/%-3d"
              % (name, d["eligible"], d["converted"],
                 d["converted"] / float(d["eligible"]) if d["eligible"] else 0.0,
                 d["stopped"], d["bouts"]))
    cr = con["converted"] / float(con["eligible"])
    rr = ref["converted"] / float(ref["eligible"]) if ref["eligible"] else 0.0
    print()
    if rr:
        print("  the contract converts %.2fx as often as the reference" % (cr / rr))
    print()

    print("  eligible landings per bout")
    print("  %-14s %10.1f" % ("contract", con["eligible"] / float(con["bouts"])))
    print("  %-14s %10.1f" % ("reference", ref["eligible"] / float(ref["bouts"])))
    print("  (context only - the bouts are different lengths and the contract's")
    print("   all stop in round one. Do not compare these two numbers as if they")
    print("   measured the same thing; that is the 2026-08-05 confound.)")
    print()

    print("  conversion by move")
    print("  %-20s %20s %20s" % ("move", "contract", "reference"))
    moves = sorted(set(con["by_move"]) | set(ref["by_move"]))
    for m in moves:
        a = con["by_move"].get(m, [0, 0])
        b = ref["by_move"].get(m, [0, 0])
        fa = ("%d/%d = %.3f" % (a[1], a[0], a[1] / float(a[0]))) if a[0] else "-"
        fb = ("%d/%d = %.3f" % (b[1], b[0], b[1] / float(b[0]))) if b[0] else "-"
        print("  %-20s %20s %20s" % (m, fa, fb))
    print()

    kc, kr = knockdown_terms()
    print("  what a knockdown looks like in each, on the two terms BOTH publish")
    print("  %-22s %10s %10s %10s" % ("", "min", "median", "max"))
    for label, d in (("contract pressure", kc["pressure"]),
                     ("reference pressure", kr["pressure"]),
                     ("contract accumulated", kc["acc"]),
                     ("reference accumulated", kr["acc"])):
        if d:
            print("  %-22s %10.4f %10.4f %10.4f"
                  % (label, min(d), pct(d, 50), max(d)))
    print("  threshold, shared: %.4f" % (c["kd_threshold"] / 10000.0))
    print()

    print("READ THIS AS:")
    if rr and cr / rr > 1.5:
        print("  The contract converts an eligible landing into a knockdown")
        print("  %.2fx as often as the model canon's threshold was swept" % (cr / rr))
        print("  against. That is the gap, stated as a rate, on the artifact a")
        print("  C++ port has to reproduce - and it is the first version of this")
        print("  number that does not come from a harness.")
    elif rr:
        print("  The two conversion rates are within %.0f%% of each other, which"
              % (abs(cr - rr) / rr * 100.0))
        print("  means conversion is NOT where the contract and the reference")
        print("  part company, and the difference that stops 24 of 24 bouts is")
        print("  elsewhere - most likely in how many eligible landings a bout")
        print("  contains rather than in what each one does.")

    out = {"contract": con, "reference": ref,
           "contract_rate": cr, "reference_rate": rr,
           "ratio": (cr / rr) if rr else None}
    p = os.path.join(REPO, "sandbox", "Saved", "conversion_gap.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:10 UTC | END ]
