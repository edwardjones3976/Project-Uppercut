# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 10:50 UTC | START ]
"""Three answers to the Director's one remaining question, measured not argued.

The question: should a fighter regenerate only while free? Canon's branch says
yes and there is a real argument for it - you are not recovering mid-punch - but
nobody priced its interaction with commitment frames. At authored frames and any
real work rate a fighter is committed 74.9% of the time, so the authored regen
rate is a fiction and the rate he actually receives is a quarter of it: 10.9 per
round against an authored 43.2, a net refill of 8.1 against a pool of 100, while
punching alone spends about 104. He cannot break even at any work rate.

THIS FILE PICKS NOTHING. It measures the three candidate answers against an
OUTSIDE anchor and reports what each does. The anchor is the reference
simulator's stamina trajectory - 8.4% to 11.8% of the pool per minute, ending a
six-minute bout between 29.5 and 49.6 - because that is the model canon's 0.57
threshold was actually swept against, and because tuning to an outcome we want
(bouts reaching the cards) rather than to a trajectory we can check would be
exactly the trap this whole investigation has been about.

    CANDIDATE A   regen accrues always, at a reduced rate while committed.
                  Recovery continues, just worse, which is what conditioning
                  actually is. Precedent exists in canon: `condition_model.
                  impairment.stamina_regen_multiplier_at_full_torso` already
                  scales regen by a state.

    CANDIDATE B   free-only stays, and the authored rate rises to what a fighter
                  actually receives. The same fiction, made honest, and the
                  number becomes checkable against the reference.

    CANDIDATE C   commitment frames come down so "free" is a larger share.
                  Measured last and expected to lose: Phase Q found commitment a
                  genuine 2.18x lever on bout length, so this trades one problem
                  for a different one.

Each is swept, not set. The multipliers below are sweep axes - they are NOT
proposals and none of them is written into canon by this file.

Run: python -m tools.engine.experiment_recovery_models
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_evade as E  # noqa: E402
import analyze_core_range as Q  # noqa: E402
import analyze_core_round as O  # noqa: E402
import experiment_range_model as R  # noqa: E402

SEEDS = R.SEEDS
INTERVAL, AGGRESSION = 6, 3000        # the closest-to-boxing configuration
REF_PER_MIN = (8.4, 11.8)             # the reference simulator's own drain rate
REF_END = (29.5, 49.6)                # ...and where it ends a 6-minute bout


def run(recovery=None, frames_mult=1.0) -> dict:
    c = dict(O.canon_pack())
    c["interval"] = INTERVAL
    if frames_mult != 1.0:
        c["moves"] = {k: dict(v) for k, v in c["moves"].items()}
        for m in c["moves"].values():
            if "frames" in m:
                m["frames"] = max(1, int(m["frames"] * frames_mult))
    rc = Q.range_pack()
    ec = E.evade_pack()
    agg = {"thrown": 0, "landed": 0, "eligible": 0, "kd": 0, "ticks": 0,
           "cards": 0, "busy": 0, "regen": 0}
    spend = {"punch": 0, "step": 0, "evade": 0, "hold": 0}
    stops, gauges = [], {}
    for s in SEEDS:
        ref = [Q.band_at(rc, R.START_SEP), False]
        ch = R.band_aware(rc, ref, ec, True, AGGRESSION)
        r = R.run_range(s, c, rc, 3, ch, gate=True, footwork=True,
                        band_ref=ref, ec=ec, recovery=recovery)
        agg["thrown"] += r["thrown"]
        agg["landed"] += r["landed"]
        agg["eligible"] += r["eligible"]
        agg["kd"] += r["knockdowns"]
        agg["ticks"] += r["total_ticks"]
        agg["busy"] += sum(r["committed_ticks"])
        agg["regen"] += r["regen_paid"]
        for k in spend:
            spend[k] += r["spend"][k]
        if r["stop_tick"] is None:
            agg["cards"] += 1
        else:
            stops.append(r["stop_tick"])
        for g, v in r["stamina_gauges"].items():
            gauges.setdefault(g, []).append(sum(v) / 2.0)
    minutes = agg["ticks"] / float(R.TICKS_PER_MIN)
    full = 3 * O.canon_pack()["round_ticks"]
    elig_full = (agg["eligible"] / float(agg["ticks"])) * full
    conv = agg["kd"] / float(agg["eligible"]) if agg["eligible"] else 0.0
    need = 3.0 / elig_full if elig_full else None
    at = {g: sum(v) / len(v) for g, v in gauges.items()}
    deepest = max(at) if at else None
    per_min = ((100.0 - at[deepest]) / (deepest / 3600.0)) if deepest else None
    return {"thrown_per_fighter_round":
            agg["thrown"] / minutes * R.ROUND_MINUTES / 2.0,
            "connect_pct": 100.0 * agg["landed"] / agg["thrown"]
            if agg["thrown"] else 0.0,
            "kd_per_minute": agg["kd"] / minutes,
            "kd_per_eligible": conv, "gap_x": conv / need if need else None,
            "cards": agg["cards"], "seeds": len(SEEDS),
            "committed_pct": 100.0 * agg["busy"] / (2.0 * agg["ticks"]),
            "drain_per_min": per_min,
            "stamina_at": {str(g): round(v, 1) for g, v in at.items()},
            "mean_ticks_to_stoppage":
                sum(stops) / float(len(stops)) if stops else None,
            # Per fighter per 3-minute round, so it can be read against a pool
            # of 100 without arithmetic.
            "per_round": {k: round(v / 10000.0 / (minutes / 3.0) / 2.0, 1)
                          for k, v in spend.items()},
            "regen_per_round": round(agg["regen"] / 10000.0
                                     / (minutes / 3.0) / 2.0, 1)}


def show(label, r):
    at = r["stamina_at"]
    print("  %-26s %7.1f %6.1f%% %7.1f%% %8.2f %6.1fx %4d/%-2d %7s %7s"
          % (label, r["thrown_per_fighter_round"], r["connect_pct"],
             r["committed_pct"], r["kd_per_minute"], r["gap_x"],
             r["cards"], r["seeds"],
             at.get("1800", "-"), at.get("3600", "-")))


def main() -> int:
    print("Anchor: the reference drains %.1f-%.1f%% of the pool per minute and"
          % REF_PER_MIN)
    print("ends a six-minute bout at %.1f-%.1f. Tuning to the TRAJECTORY, which"
          % REF_END)
    print("can be checked from outside, not to the outcome we happen to want.")
    print()
    print("  %-26s %7s %7s %8s %8s %7s %7s %7s %7s"
          % ("configuration", "thr/f-rd", "connect", "committed", "kd/min",
             "gap", "cards", "st@1800", "st@3600"))

    rows = {}
    base = run()
    rows["as it stands"] = base
    show("as it stands", base)
    print("  %-26s %7s %7s %8s %8s %7s %7s   drain %.1f%%/min"
          % ("", "", "", "", "", "", "", base["drain_per_min"]))
    print()
    pr = base["per_round"]
    total_spend = sum(pr.values())
    print("  WHERE THE POOL GOES, per fighter per 3-minute round, pool = 100")
    for k in ("punch", "step", "evade", "hold"):
        print("    %-10s %7.1f   %5.1f%% of spend" % (k, pr[k],
                                                      100.0 * pr[k] / total_spend))
    print("    %-10s %7.1f" % ("TOTAL OUT", total_spend))
    print("    %-10s %7.1f   received, against %.1f if never committed"
          % ("regen in", base["regen_per_round"],
             O.canon_pack()["regen"] * O.canon_pack()["round_ticks"] / 10000.0))
    print("    %-10s %7.1f" % ("NET", base["regen_per_round"] - total_spend))
    print()

    # FOOTWORK IS THE LARGEST ITEM, and canon prices it twice, differently.
    import io as _io
    import json as _json
    mv = _json.load(_io.open(os.path.join(O.REPO, "data", "movement_model.json"),
                             encoding="utf-8"))
    mt = _json.load(_io.open(os.path.join(O.REPO, "data", "moves",
                                          "generic_sandbox_moves.json"),
                             encoding="utf-8"))
    key = "moves" if "moves" in mt else next(
        k for k, v in mt.items()
        if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0])
    table = {m["id"]: m for m in mt[key]}
    loco = {m["posture_mode"]: m for m in mv["locomotion"]["modes"]}["boxing_steps"]
    per_ru = loco["stamina_cost_per_ru"]
    stride = loco["stride_length_ru"]
    derived = per_ru * stride
    flat = table["step_in"]["stamina_cost"]
    steps = base["per_round"]["step"] / flat
    print("  AND CANON PRICES A STEP TWICE, DIFFERENTLY")
    print("    movement_model.locomotion  %.2f per reach unit x %.2f ru stride"
          % (per_ru, stride))
    print("                               = %.3f per step" % derived)
    print("    the move table             %.3f per step, flat" % flat)
    print("    the move table charges %.2fx the locomotion model for the same"
          % (flat / derived))
    print("    0.22 ru stride. This is a contradiction, not a rounding: one of")
    print("    the two is the price of a step and the other is not.")
    print("    at %.3f, footwork costs %.1f per round instead of %.1f, and total"
          % (derived, steps * derived, base["per_round"]["step"]))
    print("    spend falls from %.1f to %.1f. Still far above the %.1f of regen"
          % (total_spend, total_spend - base["per_round"]["step"] + steps * derived,
             base["regen_per_round"]))
    print("    received, so this is a CORRECTNESS fix and not the whole answer.")
    print()

    print("  CANDIDATE A - regen while committed, as a share of the free rate")
    for pct_ in (10, 25, 50, 75, 100):
        r = run(recovery={"while_committed": pct_ * 100})
        rows["A %d%%" % pct_] = r
        show("A: committed regen %d%%" % pct_, r)
    print()

    print("  CANDIDATE B - free-only, authored rate scaled up")
    for mult in (2, 3, 4, 6, 8):
        r = run(recovery={"free_scale": mult * 10000})
        rows["B x%d" % mult] = r
        show("B: free rate x%d" % mult, r)
    print()

    print("  CANDIDATE C - commitment frames scaled down")
    for fm in (0.75, 0.5, 0.35, 0.25):
        r = run(frames_mult=fm)
        rows["C x%.2f" % fm] = r
        show("C: frames x%.2f" % fm, r)
    print()

    # Which settings land inside the reference's own drain band? That is the
    # only "pass" criterion here, and it is deliberately about the trajectory
    # rather than about knockdowns.
    inband = {k: v for k, v in rows.items()
              if v["drain_per_min"] is not None
              and REF_PER_MIN[0] * 0.6 <= v["drain_per_min"] <= REF_PER_MIN[1] * 1.6}
    print("SETTINGS WHOSE DRAIN RATE LANDS NEAR THE REFERENCE'S")
    if not inband:
        print("  none. Every swept setting still drains far faster than the")
        print("  model canon's threshold was swept against, which would mean the")
        print("  recovery branch is not the whole story after all.")
    else:
        for k in sorted(inband, key=lambda z: rows[z]["drain_per_min"]):
            v = rows[k]
            print("  %-20s drain %5.1f%%/min   cards %2d/%d   gap %5.1fx"
                  % (k, v["drain_per_min"], v["cards"], v["seeds"], v["gap_x"]))
    print()
    print("NOTE, so nobody reads a recommendation into this: every row above is")
    print("a sweep axis. None of these multipliers is written into canon by this")
    print("file, and the fact that a setting produces decisions is NOT the")
    print("argument for it - the argument would be that its drain rate matches a")
    print("model that was independently validated, and the decisions follow.")

    p = os.path.join(O.REPO, "sandbox", "Saved", "recovery_models.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 10:50 UTC | END ]
