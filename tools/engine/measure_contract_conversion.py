# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:30 UTC | START ]
"""The conversion rate, measured on the CONTRACT, and the limit that stops there.

A day of measurement was taken on `experiment_per_hand_guard.run_with` and
written up as though it described Phase O. It did not. Everything quantitative
from that day is withdrawn and has to be re-taken here, on the artifact a C++
port is proven against.

THE CONSTRAINT: the Phase O stream is pinned evidence, so measuring it may not
mean editing it. No hook is added; this file reads what the stream already says.

WHAT THE STREAM CAN AND CANNOT SUPPORT, established by trying and failing first.

  IT CAN give the conversion rate. A P row names the move, the result, the target
  region and the contact class, so an ELIGIBLE landing - canon's kd_regions and
  a class the pressure formula grades - is identifiable without any state at all.
  K rows count the ones that converted.

  IT CAN give the full pressure decomposition FOR KNOCKDOWNS. Every K row already
  publishes pressure, threshold, accumulated condition, stamina fraction, balance
  multiplier and guard multiplier. Nothing needs recomputing.

  IT CANNOT give the terms for eligible landings that did NOT convert, and this
  was worth discovering properly. C and D rows are emitted on DECISION ticks only
  - 456 of a round's 10,800 - so the defender's condition and stamina at an
  arbitrary landing tick are simply not in the stream. A first version of this
  file reconstructed them from the nearest earlier rows and got accumulated
  condition of 347 against the analyzer's own 545: stale by exactly the damage
  the landing itself had just done.

  That version was caught by its own self-check - it compared its reconstruction
  against the K rows and refused to print a table when 11 of 11 disagreed. The
  check is kept below, now trivially satisfied because the K rows ARE the source
  rather than a thing to verify against.

So this file reports the rate, and the anatomy of the knockdowns that happened.
Comparing converted against non-converted landings needs state the stream does
not carry, and getting it would mean either changing pinned evidence or building
another harness - which is the mistake this file exists to correct.

Run: python -m tools.engine.measure_contract_conversion
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402

SEEDS = list(range(4240, 4264))


def parse(stream: str):
    punches, kds, trailer = [], [], None
    ticks_with_state = set()
    for l in stream.splitlines():
        f = l.split("|")
        if f[0] == "C":
            ticks_with_state.add(int(f[1]))
        elif f[0] == "P":
            punches.append({"tick": int(f[1]), "by": int(f[2]), "move": f[3],
                            "result": f[4], "region": f[5], "flags": f[10],
                            "force": int(f[11]), "dext": int(f[12]),
                            "cls": f[13]})
        elif f[0] == "K":
            kds.append({"tick": int(f[1]), "on": int(f[2]), "move": f[3],
                        "pressure": int(f[4]), "threshold": int(f[5]),
                        "acc": int(f[6]), "stam_frac": int(f[7]),
                        "balance": int(f[8]), "guard": int(f[9])})
        elif f[0] == "S":
            trailer = dict(kv.split("=") for kv in l[2:].split("|"))
    return punches, kds, trailer, ticks_with_state


def pct(vals, p):
    v = sorted(vals)
    return v[min(len(v) - 1, max(0, int(round((len(v) - 1) * p / 100.0))))]


def main() -> int:
    c = O.canon_pack()
    elig, kd_rows, trailers = [], [], []
    state_ticks = punch_ticks = 0
    for s in SEEDS:
        stream = O.expected_stream(s, 3, with_floats=False)
        punches, kds, trailer, ticks = parse(stream)
        for p in punches:
            if p["result"] == "landed" and p["region"] in c["kd_regions"] \
                    and p["cls"] in c["kd_force"]:
                elig.append(p)
                punch_ticks += 1
                if p["tick"] in ticks:
                    state_ticks += 1
        kd_rows.extend(kds)
        trailers.append(trailer)

    print("SELF-CHECK: is the stream's own accounting consistent?")
    agg = {}
    for t in trailers:
        for k, v in t.items():
            if k != "fnv1a64":
                agg[k] = agg.get(k, 0) + int(v)
    ok = (len(kd_rows) == agg["knockdowns"])
    print("  K rows %d against the trailers' knockdown total %d ... %s"
          % (len(kd_rows), agg["knockdowns"], "agree" if ok else "DISAGREE"))
    if not ok:
        print("  the stream disagrees with itself; stopping.")
        return 1
    print("  eligible landings whose tick also carries a state row: %d of %d "
          "(%.1f%%)" % (state_ticks, punch_ticks,
                        100.0 * state_ticks / punch_ticks if punch_ticks else 0))
    print("  - which is why the terms of NON-converted landings are not")
    print("    recoverable from this stream, and are not reported below.")
    print()

    conv = len(kd_rows)
    print("THE CONTRACT'S CONVERSION RATE, %d seeds x 3 rounds" % len(SEEDS))
    print("  %d eligible landings, %d converted -> %.4f"
          % (len(elig), conv, conv / float(len(elig))))
    print("  threshold %.4f" % (c["kd_threshold"] / 10000.0))
    print()

    print("  eligible landings by move, and how often each converted")
    print("  %-20s %9s %10s %8s" % ("move", "eligible", "converted", "rate"))
    by_move = {}
    for p in elig:
        by_move.setdefault(p["move"], [0, 0])[0] += 1
    for k in kd_rows:
        if k["move"] in by_move:
            by_move[k["move"]][1] += 1
    for m in O.PUNCHES:
        e, k = by_move.get(m, [0, 0])
        print("  %-20s %9d %10d %8.4f"
              % (m, e, k, (k / float(e)) if e else 0.0))
    print()

    print("  by contact class")
    by_cls = {}
    for p in elig:
        by_cls.setdefault(p["cls"], 0)
        by_cls[p["cls"]] += 1
    for cls in sorted(by_cls):
        print("    %-8s %6d eligible" % (cls, by_cls[cls]))
    print()

    print("WHAT A KNOCKDOWN LOOKS LIKE, from the K rows themselves")
    print("  %-14s %9s %9s %9s %9s" % ("term", "min", "median", "max", "span"))
    for key, label, scale in (("pressure", "pressure", 10000.0),
                              ("acc", "accumulated", 10000.0),
                              ("stam_frac", "stamina frac", 10000.0),
                              ("balance", "balance", 10000.0),
                              ("guard", "guard", 10000.0)):
        v = [k[key] for k in kd_rows]
        print("  %-14s %9.4f %9.4f %9.4f %8.2fx"
              % (label, min(v) / scale, pct(v, 50) / scale, max(v) / scale,
                 max(v) / float(min(v)) if min(v) else 0.0))
    print()
    print("  the median knockdown lands on a fighter at %.1f%% stamina"
          % (pct([k["stam_frac"] for k in kd_rows], 50) / 100.0))
    caught = sum(1 for k in kd_rows if k["balance"] == c["caught"])
    print("  %d of %d (%.0f%%) land on a defender caught inside his own "
          "commitment" % (caught, len(kd_rows), 100.0 * caught / len(kd_rows)))
    print()

    print("  contract trailer totals: punches %d, landed %d (%.1f%% connect),"
          % (agg["punches"], agg["landed"],
             100.0 * agg["landed"] / agg["punches"]))
    print("  whiffed %d, dodged %d, blocked %d, steps %d, slips %d,"
          % (agg["whiffed"], agg["dodged"], agg["blocked"], agg["steps"],
             agg["slips"]))
    print("  knockdowns %d, bouts stopped %d of %d"
          % (agg["knockdowns"], agg["stopped"], len(SEEDS)))

    out = {"eligible": len(elig), "converted": conv,
           "rate": conv / float(len(elig)),
           "by_move": {k: {"eligible": v[0], "converted": v[1]}
                       for k, v in by_move.items()},
           "by_class": by_cls,
           "knockdown_terms": {
               k: {"min": min(x[k] for x in kd_rows) / 10000.0,
                   "median": pct([x[k] for x in kd_rows], 50) / 10000.0,
                   "max": max(x[k] for x in kd_rows) / 10000.0}
               for k in ("pressure", "acc", "stam_frac", "balance", "guard")},
           "trailer_totals": agg,
           "state_row_coverage": {"eligible": punch_ticks,
                                  "with_state_row": state_ticks}}
    p = os.path.join(O.REPO, "sandbox", "Saved", "contract_conversion.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:30 UTC | END ]
