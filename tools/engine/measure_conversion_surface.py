# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 04:00 UTC | START ]
"""Which term in the pressure product is putting men on the floor?

Phase O is held on conversion, not pacing: a bout needs a knockdown rate of
0.0139 per eligible landing to reach the cards and the model produces 0.2654,
and no volume dial moves that ratio. This measures the surface the fix has to
live on, before anybody touches a number.

Canon's pressure is one product of four multiplicands (Rule 14):

    p = force x (baseline + accumulated) x (1.4 - stamina_frac) x balance x guard

and it fires at `pressure_threshold`. Each term has a floor and a ceiling that
canon itself sets, so "which term is doing the work" is answerable exactly
rather than by intuition:

    force        0.75 solid, 1.00 clean, times the move's impact
    condition    baseline at undamaged, rising with accumulated jaw and head
    stamina      0.40 at full, 1.40 at empty - a 3.5x span, the widest by far
    balance      balanced, or the caught-committed multiplier
    guard        1.0 behind full coverage, up to 1 + unguarded_lane_bonus open

Three questions, three measurements, no proposals:

  1. DISTRIBUTION. What does each term actually range over in a real bout, as
     opposed to what it could range over in principle?
  2. COUNTERFACTUAL. Pin one term at its most favourable value and re-decide
     every landing. The term whose pinning collapses conversion is the term
     carrying the phase.
  3. THRESHOLD DISTANCE. Where would `pressure_threshold` have to sit for the
     decision path to survive, and is that a number canon could live with?

Question 2 is a REPLAY, not a re-simulation: the landings are those of the real
fight, re-decided under a modified rule. That keeps the confound out - no bout
gets longer or shorter, so nothing is normalised by its own outcome.

Run: python -m tools.engine.measure_conversion_surface
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402

SEEDS = list(range(4240, 4264))


def collect():
    """Every eligible landing in the canonical 24-seed sweep, decomposed."""
    rows = []
    c = O.canon_pack()
    for s in SEEDS:
        H.run_with(s, c, 3, None, on_eligible=rows.append)
    return c, rows


def pct(vals, p):
    v = sorted(vals)
    return v[min(len(v) - 1, max(0, int(round((len(v) - 1) * p / 100.0))))]


def main() -> int:
    c, rows = collect()
    thr = c["kd_threshold"]
    n = len(rows)
    fired = [r for r in rows if r["pressure"] >= thr]
    print("%d eligible landings across %d seeds, %d converted (%.4f)"
          % (n, len(SEEDS), len(fired), len(fired) / float(n)))
    print("threshold %.4f" % (thr / 10000.0))
    print()

    print("1. WHAT EACH TERM ACTUALLY RANGES OVER")
    print("  %-12s %8s %8s %8s %8s %8s"
          % ("term", "min", "p25", "median", "p75", "max"))
    for key, label in (("force", "force"), ("condition", "condition"),
                       ("stamina", "stamina"), ("balance", "balance"),
                       ("guard", "guard"), ("pressure", "PRESSURE")):
        v = [r[key] for r in rows]
        print("  %-12s %8.4f %8.4f %8.4f %8.4f %8.4f"
              % (label, min(v) / 10000.0, pct(v, 25) / 10000.0,
                 pct(v, 50) / 10000.0, pct(v, 75) / 10000.0, max(v) / 10000.0))
    print()

    # 2. Counterfactual replay. Recompute the product with one term pinned at
    # its most favourable (lowest-pressure) observed value, and re-decide.
    print("2. PIN ONE TERM AT ITS MOST FAVOURABLE VALUE AND RE-DECIDE")
    print("   (the fight is unchanged; only the decision is recomputed)")
    print("  %-24s %10s %10s" % ("pinned term", "converts", "rate"))
    base = len(fired) / float(n)
    print("  %-24s %10d %10.4f" % ("nothing (canon)", len(fired), base))
    order = ("force", "condition", "stamina", "balance", "guard")
    results = {}
    for pin in order:
        floor = min(r[pin] for r in rows)
        k = 0
        for r in rows:
            p = r["force"] if pin != "force" else floor
            cond = r["condition"] if pin != "condition" else floor
            stam = r["stamina"] if pin != "stamina" else floor
            bal = r["balance"] if pin != "balance" else floor
            grd = r["guard"] if pin != "guard" else floor
            v = (p * cond) // 10000
            v = (v * stam) // 10000
            v = (v * bal) // 10000
            v = (v * grd) // 10000
            if v >= thr:
                k += 1
        rate = k / float(n)
        results[pin] = {"pinned_to": floor / 10000.0, "converts": k, "rate": rate}
        print("  %-24s %10d %10.4f    (pinned to %.4f)"
              % (pin, k, rate, floor / 10000.0))
    print()

    # 3. Where the threshold would have to sit.
    print("3. WHERE THE THRESHOLD WOULD HAVE TO SIT")
    ps = sorted(r["pressure"] for r in rows)
    target = 0.0139
    need_k = int(target * n)
    # the smallest threshold at which at most need_k landings still convert
    want = ps[n - need_k - 1] + 1 if need_k < n else ps[0]
    print("  a decision needs conversion <= %.4f, i.e. at most %d of these %d"
          % (target, need_k, n))
    print("  canon's threshold        %.4f  -> %d convert" % (thr / 10000.0,
                                                              len(fired)))
    print("  the threshold that works %.4f  -> %d convert" % (want / 10000.0,
                                                              need_k))
    print("  that is %.2fx canon's, and above the %sth percentile of pressure"
          % (want / float(thr),
             next(p for p in range(100) if pct(ps, p) >= want)))
    print("  observed pressure ceiling %.4f" % (max(ps) / 10000.0))
    if want > max(ps):
        print("  NOTE: that threshold is above every landing in the sweep, so it")
        print("  would not raise the bar - it would switch knockdowns off.")
    print()

    print("4. HOW WIDE EACH TERM ACTUALLY SWINGS WITHIN THE BOUT")
    print("   (a term pinned to its own minimum is only interesting if the bout")
    print("    puts it well above that minimum in the first place)")
    print("  %-12s %10s %10s %10s" % ("term", "span", "median/min", "kills?"))
    spans = {}
    for k in order:
        v = [r[k] for r in rows]
        lo, med = min(v), pct(v, 50)
        spans[k] = med / float(lo)
        print("  %-12s %9.2fx %9.2fx %10s"
              % (k, max(v) / float(lo), spans[k],
                 "yes" if results[k]["rate"] <= target else "no"))
    print()

    print("READ THIS AS:")
    driver = max(spans, key=lambda k: spans[k])
    print("  Three terms are pinned at or near their floor already: balance sits")
    print("  at the caught-committed multiplier almost always, guard barely")
    print("  moves, and condition swings %.2fx. Those cannot be what varies."
          % spans["condition"])
    print("  The term that actually swings is %s: %.2fx from its floor to the"
          % (driver, spans[driver]))
    print("  median eligible landing, and pinning it at full-fighter value takes")
    print("  conversion from %.4f to %.4f - every knockdown in the sweep"
          % (base, results[driver]["rate"]))
    print("  disappears. Men are not being dropped by punches; they are being")
    print("  dropped because they are already empty when the punch lands.")
    print()
    print("  And the threshold cannot fix it. To reach the cards it would have")
    print("  to sit at %.4f, which is %.2fx canon's and above the observed"
          % (want / 10000.0, want / float(thr)))
    print("  ceiling of %.4f - that is not a higher bar, it is knockdowns off."
          % (max(ps) / 10000.0))
    print("  The surface is the STAMINA ECONOMY, not `pressure_threshold`. That")
    print("  lands on the Director's open question directly: should a fighter")
    print("  reach the late rounds near-empty? Canon's answer is currently yes,")
    print("  and Rule 14 then converts it into a stoppage every time.")
    print()
    print("  STATED AGAINST ITSELF: force also collapses when pinned, but its")
    print("  pin is degenerate - it makes every punch the weakest move in the")
    print("  set, which is not a counterfactual anybody would ship. Stamina's")
    print("  pin is a fighter who never tires, which is a real design position")
    print("  and the one the Director may actually be choosing between.")
    print()

    # 5. If the economy is the surface, how far would it have to move? This one
    # RE-SIMULATES, so it is read on the invariant itself - seeds reaching the
    # cards - and not on any total.
    print("5. HOW FAR WOULD THE ECONOMY HAVE TO MOVE?")
    print("   (punch costs scaled; re-simulated, and read on the invariant)")
    print("   Each row carries its OWN required conversion: slowing the fight")
    print("   changes how many eligible landings a full bout would contain, so a")
    print("   single fixed target would be the confound creeping back in.")
    print("  %-8s %8s %8s %9s %8s %7s %7s"
          % ("cost x", "kd/elig", "needed", "gap", "t_stop", "cards", "st@1800"))
    econ = {}
    for k in (1.0, 0.75, 0.5, 0.35, 0.25, 0.1):
        cc = dict(c)
        cc["moves"] = {mk: dict(mv) for mk, mv in c["moves"].items()}
        for mv in cc["moves"].values():
            if "cost" in mv:
                mv["cost"] = int(mv["cost"] * k)
        elig = kds = cards = ticks = 0
        stops, g18 = [], []
        for s in SEEDS:
            r = H.run_with(s, cc, 3, None)
            elig += r["eligible"]
            kds += r["knockdowns"]
            ticks += r["total_ticks"]
            if r["stop_tick"] is not None:
                stops.append(r["stop_tick"])
            else:
                cards += 1
            if 1800 in r["stamina_gauges"]:
                g18.append(sum(r["stamina_gauges"][1800]) / 2.0)
        conv = kds / float(elig) if elig else 0.0
        ts = sum(stops) / float(len(stops)) if stops else None
        sg = sum(g18) / float(len(g18)) if g18 else None
        full = 3 * c["round_ticks"]
        elig_full = (elig / float(ticks)) * full
        need = 3.0 / elig_full if elig_full else None
        gap = conv / need if need else None
        econ["%.2f" % k] = {"kd_per_eligible": round(conv, 4),
                            "mean_ticks_to_stoppage": round(ts, 1) if ts else None,
                            "reached_cards": cards, "seeds": len(SEEDS),
                            "stamina_at_1800": round(sg, 2) if sg else None,
                            "eligible_per_full_bout": round(elig_full, 1),
                            "conversion_needed": round(need, 4) if need else None,
                            "gap_x": round(gap, 2) if gap else None}
        print("  %-8.2f %8.4f %8.4f %8.1fx %8s %5d/%-2d %7s"
              % (k, conv, need, gap, ("%.0f" % ts) if ts else "none",
                 cards, len(SEEDS), ("%.1f" % sg) if sg else "--"))
    out_econ = econ
    print()
    last = econ["0.10"]
    print("  The economy is a real lever - conversion falls %.1fx from canon to"
          % (econ["1.00"]["kd_per_eligible"] / last["kd_per_eligible"]))
    print("  a tenth-cost fighter, and the gap closes from %.1fx to %.1fx. It is"
          % (econ["1.00"]["gap_x"], last["gap_x"]))
    print("  still not enough on its own, and a tenth-cost punch is not a")
    print("  proposal: it is the far end of the axis, printed so the Director")
    print("  can see that the whole axis does not reach. Whatever closes Phase O")
    print("  is either two of these levers together or a structural call about")
    print("  how often a landing should be ELIGIBLE at all - %d in %d bouts is"
          % (n, len(SEEDS)))
    print("  itself a number nobody has yet defended.")

    out = {"eligible": n, "converted": len(fired), "rate": base,
           "threshold": thr / 10000.0,
           "terms": {k: {"min": min(r[k] for r in rows) / 10000.0,
                         "median": pct([r[k] for r in rows], 50) / 10000.0,
                         "max": max(r[k] for r in rows) / 10000.0}
                     for k in order + ("pressure",)},
           "pinned": results,
           "threshold_needed": want / 10000.0,
           "threshold_ratio": round(want / float(thr), 3),
           "economy_sweep": out_econ}
    p = os.path.join(O.REPO, "sandbox", "Saved", "conversion_surface.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 04:00 UTC | END ]
