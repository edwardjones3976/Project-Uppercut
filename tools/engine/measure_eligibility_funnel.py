# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 04:50 UTC | START ]
"""How does a decision become a clean head shot, and how often should it?

The conversion measurement left three candidates for Phase O and named this one
as the place I would look: 373 eligible landings across 24 bouts averaging 2,335
ticks is roughly 24 solid-or-clean head shots per minute of fight. Nobody has
ever defended that number, and it sits upstream of every pressure term.

This counts the funnel rather than inferring it, stage by stage:

    decisions -> punches thrown -> reached the plane -> not blocked
              -> landed -> landed on jaw or head -> graded solid or clean

and then puts the result beside what professional boxing actually produces. The
outside benchmark matters here because canon authors NO expected landing rate
anywhere - `movement_model` mentions punches only to say whether a stance permits
them. There is no internal number to check against, which is exactly why this one
has gone unexamined for so long.

BENCHMARK, from CompuBox's published per-fight statistics (see the development-log
entry for sources): a professional fight runs about 55-78 punches thrown per
fighter per round, with power punches connecting at a CompuBox average of 36.9%.
Heavyweights throw far fewer, 30-60. Anthony Joshua against Ngannou threw 37.7
per round and landed 11.7 - and that 11.7 is TOTAL landed, jabs included, not
clean head shots. Roman Gonzalez, a volume outlier, averages 30.1 landed per
round across his career.

The comparison to make is therefore against LANDED POWER PUNCHES per round, which
is the closest real-world analogue to a landing our model grades solid or clean
on the jaw or head. Nothing in this file proposes a number; it measures ours and
prints theirs beside it.

Run: python -m tools.engine.measure_eligibility_funnel
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402

SEEDS = list(range(4240, 4264))
TICKS_PER_MIN = 3600            # 60Hz
ROUND_MINUTES = 3.0


def main() -> int:
    c = O.canon_pack()
    ev = {"thrown": [], "reached": [], "blocked": [], "landed": []}
    elig = []
    ticks = 0
    # A punch is evaluated on every active frame, so `reached` rows are frames
    # and must be deduped to punch instances by (fighter, t0). That key is only
    # unique WITHIN a bout - deduping the pooled rows across 24 seeds collided
    # instances between bouts and reported fewer punches reaching the plane than
    # landed on it. Counted per seed, then summed.
    reached = reached_committed = 0
    for s in SEEDS:
        per = {"thrown": [], "reached": [], "blocked": [], "landed": []}
        r = H.run_with(s, c, 3, None, on_eligible=elig.append,
                       on_event=lambda k, row: per[k].append(row))
        ticks += r["total_ticks"]
        reached += len({(w["by"], w["t0"]) for w in per["reached"]})
        reached_committed += len({(w["by"], w["t0"]) for w in per["reached"]
                                  if w["committed"]})
        for k in ev:
            ev[k].extend(per[k])

    minutes = ticks / float(TICKS_PER_MIN)
    thrown = len(ev["thrown"])
    blocked, landed = len(ev["blocked"]), len(ev["landed"])
    n_elig = len(elig)

    print("%d ticks of fight across %d bouts = %.1f minutes, both fighters"
          % (ticks, len(SEEDS), minutes))
    print()
    print("THE FUNNEL   (per-fighter-round = per minute / 2 x 3)")
    print("  %-28s %8s %10s %12s" % ("stage", "count", "survives", "per f-round"))
    prev = None
    for label, n in (("punches thrown", thrown),
                     ("reached the plane", reached),
                     ("not blocked", reached - blocked),
                     ("landed on the surface", landed),
                     ("landed jaw or head", sum(1 for r in ev["landed"]
                                                if r["region"] in c["kd_regions"])),
                     ("graded solid or clean", n_elig)):
        surv = "-" if prev is None else "%.1f%%" % (100.0 * n / prev)
        print("  %-28s %8d %10s %12.1f"
              % (label, n, surv, n / minutes * ROUND_MINUTES / 2.0))
        prev = n
    print()

    print("WHERE THE PUNCHES GO")
    by_move = {}
    for r in ev["thrown"]:
        by_move.setdefault(r["move"], [0, 0, 0])[0] += 1
    for r in ev["landed"]:
        if r["move"] in by_move:
            by_move[r["move"]][1] += 1
    for r in elig:
        if r["move"] in by_move:
            by_move[r["move"]][2] += 1
    print("  %-14s %8s %8s %8s %9s %9s"
          % ("move", "thrown", "landed", "elig", "land %", "elig %"))
    for mid in sorted(by_move, key=lambda m: -by_move[m][0]):
        t, l, e = by_move[mid]
        print("  %-14s %8d %8d %8d %8.1f%% %8.1f%%"
              % (mid, t, l, e, 100.0 * l / t if t else 0,
                 100.0 * e / t if t else 0))
    print()

    print("GRADE DISTRIBUTION OF LANDINGS")
    grades = {}
    for r in ev["landed"]:
        grades[r["grade"]] = grades.get(r["grade"], 0) + 1
    for g in ("brushed", "grazed", "solid", "clean"):
        n = grades.get(g, 0)
        print("  %-10s %6d  %5.1f%%" % (g, n, 100.0 * n / landed if landed else 0))
    print()

    print("THE BLOCK STAGE")
    print("  %d punches reached the plane; %d (%.1f%%) met a COMMITTED defender"
          % (reached, reached_committed,
             100.0 * reached_committed / reached if reached else 0))
    print("  %d were blocked (%.1f%% of everything that reached)"
          % (blocked, 100.0 * blocked / reached if reached else 0))
    print()

    per_fighter_round = n_elig / minutes * ROUND_MINUTES / 2.0
    print("THE NUMBER, AND WHAT BOXING DOES")
    print("  ours: %.1f solid-or-clean jaw/head landings per fighter per round"
          % per_fighter_round)
    print("  ours: %.1f punches thrown per fighter per round"
          % (thrown / minutes * ROUND_MINUTES / 2.0))
    print()
    print("  CompuBox, professional boxing:")
    print("    55-78 punches thrown per fighter per round (30-60 heavyweight)")
    print("    36.9% power-punch connect rate, the published CompuBox average")
    print("    Joshua-Ngannou: 37.7 thrown, 11.7 landed per round - ALL landings")
    print("    Roman Gonzalez, a volume outlier: 30.1 landed per round, career")
    print()
    tpr = thrown / minutes * ROUND_MINUTES / 2.0
    over = tpr / 78.0
    print("  READ THIS AS: I named eligibility as the suspect and it is not the")
    print("  suspect. The funnel's own percentages are defensible: %.0f%% of what"
          % (100.0 * (reached - blocked) / reached if reached else 0))
    print("  reaches a guard gets past it, %.0f%% of landings are jaw or head, and"
          % (100.0 * sum(1 for r in ev["landed"]
                         if r["region"] in c["kd_regions"]) / landed))
    print("  %.0f%% of landings grade solid or clean. Those are boxing-shaped."
          % (100.0 * n_elig / landed if landed else 0))
    print()
    print("  What is not defensible is the TOP of the funnel. %.0f punches per" % tpr)
    print("  fighter per round against a professional 55-78, and 30-60 for")
    print("  heavyweights: %.1fx the top of the band. Every downstream number is" % over)
    print("  a reasonable fraction of an unreasonable input. %.1f flush head"
          % per_fighter_round)
    print("  shots per round is what %.0f thrown punches buys at honest rates -" % tpr)
    print("  a fighter here absorbs more clean head shots per round than Roman")
    print("  Gonzalez lands punches of any kind.")
    print()
    print("  The volume comes from the decision clock, not from aggression: the")
    print("  core decides every %d ticks (%.1f decisions per second) and punches"
          % (c["interval"], 60.0 / c["interval"]))
    print("  are 5 of its 11 actions. Canon's own slowest tier reacts every 20.")
    print("  That single number was measured earlier tonight as a 1.88x lever on")
    print("  bout length; read against boxing it is not a tuning knob but a")
    print("  wrongly-set constant.")
    dead = [m for m, v in by_move.items() if v[0] and not v[1]]
    reach = {}
    surface = 9000 - c["half_depth"]
    for mid in O.PUNCHES:
        mv = c["moves"][mid]
        peak = max(O.N._ext(c, mid, k) for k in
                   range(mv["startup"] + 1, mv["startup"] + mv["active"] + 1))
        reach[mid] = {"peak": peak, "needs": surface, "reaches": peak >= surface,
                      "cost": mv["cost"], "impact": mv["impact"]}
    if dead:
        print()
        print("  SEPARATE DEFECT, and this one is a modelling finding rather")
        print("  than a tuning value: %s threw %d times and landed ZERO."
              % (", ".join(dead), sum(by_move[m][0] for m in dead)))
        print("  %-20s %8s %8s %10s" % ("move", "peak", "needs", "reaches?"))
        for mid in O.PUNCHES:
            r = reach[mid]
            print("  %-20s %8d %8d %10s"
                  % (mid, r["peak"], r["needs"], "yes" if r["reaches"] else "NO"))
        short = [m for m in reach if not reach[m]["reaches"]]
        gap = min(reach[m]["needs"] - reach[m]["peak"] for m in short)
        print()
        print("  The uppercut peaks %d short of a surface it must touch - about"
              % gap)
        print("  %.0f cm at canon's scale. It is not mis-authored: the uppercut is"
              % (gap / 10000.0 * 130.0))
        print("  an INSIDE punch and this core has no inside. Both fighters stand")
        print("  at a fixed opening distance and never close, so the one punch in")
        print("  the set that requires closing the range can never be used.")
        print()
        spend = sum(by_move[m][0] * c["moves"][m]["cost"] for m in by_move)
        waste = sum(by_move[m][0] * c["moves"][m]["cost"] for m in short
                    if m in by_move)
        print("  AND IT IS NOT FREE. The uppercut is the most expensive move in")
        print("  the set (%d) and the highest impact (%d). Thrown %d times, it"
              % (c["moves"][short[0]]["cost"], c["moves"][short[0]]["impact"],
                 sum(by_move[m][0] for m in short if m in by_move)))
        print("  burned %.1f%% of every point of stamina these fighters spent on"
              % (100.0 * waste / spend))
        print("  punching, for nothing. Stamina is the term that decides every")
        print("  knockdown in this model. A quarter of the punch economy is being")
        print("  paid into a punch that cannot connect, and the fighters arrive")
        print("  at the knockdown threshold that much emptier for it.")

    out = {"ticks": ticks, "minutes": round(minutes, 1), "thrown": thrown,
           "reached": reached, "blocked": blocked, "landed": landed,
           "eligible": n_elig,
           "per_fighter_round": {
               "thrown": round(thrown / minutes * ROUND_MINUTES / 2.0, 2),
               "landed": round(landed / minutes * ROUND_MINUTES / 2.0, 2),
               "eligible": round(per_fighter_round, 2)},
           "grades": grades,
           "reach": reach,
           "by_move": {k: {"thrown": v[0], "landed": v[1], "eligible": v[2]}
                       for k, v in by_move.items()}}
    p = os.path.join(O.REPO, "sandbox", "Saved", "eligibility_funnel.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 04:50 UTC | END ]
