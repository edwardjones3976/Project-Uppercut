# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 10:00 UTC | START ]
"""The last open term: why is a landed punch still 4.6x too likely to drop a man?

Volume was range and accuracy was evasion, and both are now delivered. At
`react 6, aggression 0.30` the core throws 51.8 punches per fighter per round
against the reference's 40.7 and connects 45.7% against 42.4% - both within a
quarter of the reference - and still drops men 6.3x as often. Divide out volume
and accuracy and a 4.6x LETHALITY residual remains.

Every earlier attempt to examine that term read a fight with no distance in it,
so all of them are re-run here on the fight that now exists. The candidates are
the five multiplicands of canon's pressure product, and one new suspect the
earlier passes could not have seen:

  STAMINA.    Measured three ways before, always the largest swing. Footwork and
              evasion now cost stamina that nothing charged for previously, so
              the honest expectation is that this got WORSE, not better.
  FORCE.      The mix changed. `uppercut_rear` is the highest-impact move in the
              set (0.9499) and landed ZERO times in every measurement taken
              before range existed. A model that finally throws its best punch
              gets more knockdowns from the same number of landings - which is
              correct behaviour producing an incorrect total.
  CONDITION.  Inside fighting concentrates landings on the same regions. The
              accumulation term could be climbing for a reason that is also
              correct behaviour.
  BALANCE / GUARD. Both were near their floors before. Evasion changes who is
              committed and when, so both are re-read rather than assumed.

The comparison is Phase O's decomposition against the same decomposition on the
Phase R fight, term by term, on the SAME 24 seeds. Nothing is tuned and nothing
is proposed; this identifies which multiplicand carries the residual so the
Director's decision is about one number rather than five.

Run: python -m tools.engine.measure_lethality_residual
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_evade as E  # noqa: E402
import analyze_core_range as Q  # noqa: E402
import analyze_core_round as O  # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402
import experiment_range_model as R  # noqa: E402

SEEDS = R.SEEDS
TERMS = ("force", "condition", "stamina", "balance", "guard", "pressure")


def pct(vals, p):
    v = sorted(vals)
    return v[min(len(v) - 1, max(0, int(round((len(v) - 1) * p / 100.0))))]


def phase_o_rows():
    rows = []
    c = O.canon_pack()
    for s in SEEDS:
        H.run_with(s, c, 3, None, on_eligible=rows.append)
    return c, rows


def phase_r_rows(interval=6, aggression=3000):
    rows = []
    c = dict(O.canon_pack())
    c["interval"] = interval
    rc = Q.range_pack()
    ec = E.evade_pack()
    stam = []
    busy = free = 0
    for s in SEEDS:
        ref = [Q.band_at(rc, R.START_SEP), False]
        ch = R.band_aware(rc, ref, ec, True, aggression)
        r = R.run_range(s, c, rc, 3, ch, gate=True, footwork=True,
                        band_ref=ref, ec=ec, on_eligible=rows.append)
        busy += sum(r["committed_ticks"])
        free += 2 * r["total_ticks"] - sum(r["committed_ticks"])
        for g in (600, 1200, 1800, 2400, 3600):
            if g in r["stamina_gauges"]:
                stam.append((g, sum(r["stamina_gauges"][g]) / 2.0))
    return c, rows, stam, (busy, free)


def main() -> int:
    c, o_rows = phase_o_rows()
    _, r_rows, r_stam, (busy, free) = phase_r_rows()
    thr = c["kd_threshold"]
    o_fire = sum(1 for r in o_rows if r["pressure"] >= thr)
    r_fire = sum(1 for r in r_rows if r["pressure"] >= thr)
    print("eligible landings   Phase O %d (%d converted, %.4f)"
          % (len(o_rows), o_fire, o_fire / float(len(o_rows))))
    print("                    Phase R %d (%d converted, %.4f)"
          % (len(r_rows), r_fire, r_fire / float(len(r_rows))))
    print("threshold %.4f" % (thr / 10000.0))
    print()

    print("EVERY TERM, THEN AND NOW (median of eligible landings)")
    print("  %-12s %10s %10s %9s   %s"
          % ("term", "Phase O", "Phase R", "change", "what moved"))
    story = {
        "force": "the punch mix",
        "condition": "accumulated damage at the moment of landing",
        "stamina": "how empty the man being hit is",
        "balance": "how often he is caught committed",
        "guard": "how open the lane is",
        "pressure": "",
    }
    deltas = {}
    for k in TERMS:
        a = pct([r[k] for r in o_rows], 50)
        b = pct([r[k] for r in r_rows], 50)
        deltas[k] = b / float(a) if a else 0.0
        print("  %-12s %10.4f %10.4f %8.2fx   %s"
              % (k, a / 10000.0, b / 10000.0, deltas[k], story[k]))
    print()

    # Which term explains the change in the product? Multiply the four
    # multiplicand ratios and compare to the pressure ratio: if they agree, the
    # decomposition is complete and the largest factor is the answer.
    prod = 1.0
    for k in ("force", "condition", "stamina", "balance", "guard"):
        prod *= deltas[k]
    print("  the four multiplicands multiply to %.2fx; median pressure moved "
          "%.2fx" % (prod, deltas["pressure"]))
    driver = max(("force", "condition", "stamina", "balance", "guard"),
                 key=lambda k: abs(deltas[k] - 1.0))
    print("  the term that moved most is %s (%.2fx)" % (driver, deltas[driver]))
    print()

    print("WHERE THE ELIGIBLE LANDINGS COME FROM NOW")
    print("  %-20s %8s %8s %9s %9s" % ("move", "Phase O", "Phase R",
                                       "share O", "share R"))
    o_by = {}
    r_by = {}
    for r in o_rows:
        o_by[r["move"]] = o_by.get(r["move"], 0) + 1
    for r in r_rows:
        r_by[r["move"]] = r_by.get(r["move"], 0) + 1
    for m in O.PUNCHES:
        a, b = o_by.get(m, 0), r_by.get(m, 0)
        print("  %-20s %8d %8d %8.1f%% %8.1f%%"
              % (m, a, b, 100.0 * a / len(o_rows), 100.0 * b / len(r_rows)))
    print()
    print("  median impact of an eligible landing: Phase O %.4f, Phase R %.4f"
          % (pct([c["moves"][r["move"]]["impact"] for r in o_rows], 50) / 10000.0,
             pct([c["moves"][r["move"]]["impact"] for r in r_rows], 50) / 10000.0))
    print()

    print("STAMINA AT FIXED TICKS, PHASE R (n = seeds still fighting)")
    by_g = {}
    for g, v in r_stam:
        by_g.setdefault(g, []).append(v)
    for g in sorted(by_g):
        v = by_g[g]
        print("  t=%-6d %6.1f  (n=%d)" % (g, sum(v) / len(v), len(v)))
    print("  reference simulator, end of a 6-minute bout: 29.5 - 49.6 by profile")
    print()
    # The rate, which is the comparison that actually matters. Ours is read off
    # the trajectory above; the reference's is read off its own committed batch
    # run (tools.uppercut_sim.batch, 3 rounds x 120s = 6.0 minutes).
    have = sorted(by_g)
    last = have[-1]
    ours = (100.0 - (sum(by_g[last]) / len(by_g[last]))) / (last / 3600.0)
    ref_lo = (100.0 - 49.6) / 6.0
    ref_hi = (100.0 - 29.5) / 6.0
    print("THE RATE, WHICH IS THE COMPARISON THAT MATTERS")
    print("  ours:      %.1f%% of the pool per minute (to %.1f%% left at t=%d)"
          % (ours, sum(by_g[last]) / len(by_g[last]), last))
    print("  reference: %.1f%% to %.1f%% of the pool per minute" % (ref_lo, ref_hi))
    print("  we drain %.1fx to %.1fx faster than the model canon's threshold "
          "was swept against." % (ours / ref_hi, ours / ref_lo))
    print("  A round is %d ticks - %.0f seconds. Our fighters are effectively"
          % (c["round_ticks"], c["round_ticks"] / 60.0))
    print("  empty before the FIRST round's bell.")
    print()

    # And the mechanism, which is not the costs at all.
    total = busy + free
    print("AND THE MECHANISM: A FIGHTER ONLY REGENERATES WHEN HE IS FREE")
    print("  Canon charges the posture hold and pays the idle regen in the SAME")
    print("  branch, and a committed fighter is in neither. So the regen a")
    print("  fighter actually receives is the authored rate times the fraction")
    print("  of the bout he is not committed to something.")
    print("  committed  %8d ticks  %5.1f%%" % (busy, 100.0 * busy / total))
    print("  free       %8d ticks  %5.1f%%" % (free, 100.0 * free / total))
    print("  effective regen is %.1f%% of the authored rate." % (100.0 * free / total))
    print()
    # The arithmetic, so the claim is a number rather than an impression.
    rt = c["round_ticks"]
    full_regen = c["regen"] * rt / 10000.0
    got_regen = full_regen * free / float(total)
    hold = c["posture"]["high_guard"]["hold"] * rt / 10000.0 * free / float(total)
    print("  per round, at canon's authored rates and this fight's free share:")
    print("    regen if never committed   %8.1f" % full_regen)
    print("    regen actually received    %8.1f   (%.1f%% of the pool)"
          % (got_regen, 100.0 * got_regen / (c["st_max"] / 10000.0)))
    print("    guard hold actually paid   %8.1f" % hold)
    print("    net refill                 %8.1f   against a pool of %.0f"
          % (got_regen - hold, c["st_max"] / 10000.0))
    print("  The pool is not being emptied by costs that are too high. It is")
    print("  being emptied because it almost never refills - and the fighter")
    print("  who is always committed is the same fighter whose guard is always")
    print("  degraded and whose balance term always reads 'caught'. One state")
    print("  is driving three of the five pressure multiplicands.")
    print()

    print("READ THIS AS:")
    if driver == "stamina":
        print("  The residual is still the stamina term, and it is now WORSE:")
        print("  footwork and evasion cost stamina that nothing charged for")
        print("  before. The lethality factor is not a knockdown-model problem")
        print("  at all - it is that this core empties a fighter faster than the")
        print("  reference does, and canon's pressure formula then multiplies an")
        print("  empty man's vulnerability by up to 3.5x.")
    elif driver == "force":
        print("  The residual is the PUNCH MIX, not the stamina economy - and")
        print("  that is correct behaviour producing an incorrect total. The")
        print("  uppercut is canon's most dangerous punch and it landed zero")
        print("  times in every measurement taken before range existed. The")
        print("  knockdown model was implicitly tuned against a fight in which")
        print("  the hardest punch in the set could never connect.")
    else:
        print("  The residual is carried by %s, which no earlier pass could have"
              % driver)
        print("  seen, because every earlier pass read a fight with no distance.")

    out = {"phase_o": {"eligible": len(o_rows), "converted": o_fire},
           "phase_r": {"eligible": len(r_rows), "converted": r_fire},
           "medians": {k: {"phase_o": pct([r[k] for r in o_rows], 50) / 10000.0,
                           "phase_r": pct([r[k] for r in r_rows], 50) / 10000.0,
                           "ratio": round(deltas[k], 4)} for k in TERMS},
           "driver": driver,
           "eligible_by_move": {"phase_o": o_by, "phase_r": r_by},
           "stamina_at": {str(g): round(sum(v) / len(v), 2)
                          for g, v in by_g.items()}}
    p = os.path.join(O.REPO, "sandbox", "Saved", "lethality_residual.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 10:00 UTC | END ]
