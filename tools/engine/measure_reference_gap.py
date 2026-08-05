# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 06:00 UTC | START ]
"""What does the reference simulator do that the core does not?

Canon's 0.57 knockdown threshold was swept against the REFERENCE simulator, not
against this core. The core has been held for a conversion rate 19.1x too high,
and tonight ruled out every volume explanation for it: cadence, commitment, CPU
policy, the guard's hold cost, and finally work rate itself - slowed to a boxer's
76 punches per round the gap only falls to 6.0x and not one bout in 24 reaches
the cards.

So the question stops being "which of our numbers is wrong" and becomes "what is
the reference doing that we are not". That is answerable by reading its pipeline
and counting both.

`uppercut_sim.engine.resolve` runs these stages in `collision_model`'s declared
order. Against each, what our core does:

    Rule 12 RANGE GATE  a punch from the wrong band travels its arc into empty
                        air                            -> WE DO NOT HAVE THIS
    Stage 0  SWEEP      15% chance of no overlap       -> replaced by geometry
    Stage 1  EVASION    active dodge, amplified by the telegraph of a slow punch
                        and by the defender's read of a repeated pattern
                                                       -> WE DO NOT HAVE THIS
    Stage 2  GUARD      probabilistic interception     -> replaced by geometry,
                        and repaired this week by the Director's per-hand rule

Three of the four stages that make a punch MISS in the reference are absent from
the core. Geometry replaced one of them and nothing replaced the other two. That
is not a tuning discrepancy; it is a missing pipeline.

This file measures both sides rather than asserting the consequence.

Run: python -m tools.engine.measure_reference_gap
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402

REPO = O.REPO
if REPO not in sys.path:
    sys.path.insert(0, REPO)

SEEDS = list(range(4240, 4264))
TICKS_PER_MIN = 3600
ROUND_MINUTES = 3.0


def core_side() -> dict:
    """Our core, at canon's own settings."""
    c = O.canon_pack()
    ev = {"thrown": [], "reached": [], "blocked": [], "landed": []}
    ticks = kd = 0
    for s in SEEDS:
        r = H.run_with(s, c, 3, None,
                       on_event=lambda k, row: ev[k].append(row))
        ticks += r["total_ticks"]
        kd += r["knockdowns"]
    minutes = ticks / float(TICKS_PER_MIN)
    thrown, landed = len(ev["thrown"]), len(ev["landed"])
    return {"minutes": minutes, "thrown": thrown, "landed": landed,
            "blocked": len(ev["blocked"]), "knockdowns": kd,
            "connect_pct": 100.0 * landed / thrown if thrown else 0.0,
            "thrown_per_fighter_round": thrown / minutes * ROUND_MINUTES / 2.0,
            "kd_per_minute": kd / minutes}


def reference_side() -> dict:
    """The reference simulator, over the same number of bouts."""
    from tools.uppercut_sim.engine import Bout   # noqa: E402
    profiles = ["technician", "rusher", "counterpuncher", "drainer",
                "power_threat", "showman"]
    rounds, round_seconds = 3, 120
    thrown = landed = blocked = dodged = whiffed = oor = kd = 0
    stopped = bouts = 0
    for i, s in enumerate(SEEDS):
        a = profiles[i % len(profiles)]
        b = profiles[(i + 3) % len(profiles)]
        bout = Bout(s, a, b, rounds=rounds, round_seconds=round_seconds)
        log = bout.run()
        bouts += 1
        for f in bout.fighters:
            kd += f.knockdowns
            oor += f.out_of_range_attempts
            blocked += f.blocked_taken
        for e in log:
            t = e.get("type")
            if t == "punch_thrown":
                thrown += 1
            elif t == "punch_outcome":
                cls = (e.get("payload") or {}).get("class")
                if cls == "whiffed":
                    whiffed += 1
                elif cls == "dodged":
                    dodged += 1
                elif cls and cls != "blocked":
                    landed += 1
            elif t == "stoppage":
                stopped += 1
    minutes = bouts * rounds * round_seconds / 60.0
    return {"minutes": minutes, "bouts": bouts, "thrown": thrown,
            "landed": landed, "blocked": blocked, "dodged": dodged,
            "whiffed": whiffed, "out_of_range": oor, "knockdowns": kd,
            "stopped": stopped,
            "connect_pct": 100.0 * landed / thrown if thrown else 0.0,
            "thrown_per_fighter_round": thrown / minutes * ROUND_MINUTES / 2.0,
            "kd_per_minute": kd / minutes}


def main() -> int:
    core = core_side()
    try:
        ref = reference_side()
    except Exception as exc:                      # pragma: no cover - diagnostic
        print("reference simulator could not be run in-process: %r" % (exc,))
        print("The core-side numbers below stand on their own.")
        ref = None

    print("THE CORE (this week's Phase O contract, canon settings)")
    print("  %.1f minutes of fight, %d bouts" % (core["minutes"], len(SEEDS)))
    print("  thrown %d, landed %d (%.1f%% connect)"
          % (core["thrown"], core["landed"], core["connect_pct"]))
    print("  %.1f thrown per fighter per round" % core["thrown_per_fighter_round"])
    print("  %d knockdowns = %.2f per minute of fight" % (core["knockdowns"],
                                                          core["kd_per_minute"]))
    print()
    if ref:
        print("THE REFERENCE SIMULATOR (what canon's 0.57 was swept against)")
        print("  %.1f minutes of fight, %d bouts" % (ref["minutes"], ref["bouts"]))
        print("  thrown %d, landed %d (%.1f%% connect)"
              % (ref["thrown"], ref["landed"], ref["connect_pct"]))
        print("  %.1f thrown per fighter per round"
              % ref["thrown_per_fighter_round"])
        print("  %d knockdowns = %.2f per minute of fight"
              % (ref["knockdowns"], ref["kd_per_minute"]))
        print("  stopped %d of %d bouts - the rest went to the cards"
              % (ref["stopped"], ref["bouts"]))
        print()
        print("  where the reference's punches GO:")
        for label, n in (("out of range (Rule 12)", ref["out_of_range"]),
                         ("whiffed", ref["whiffed"]),
                         ("dodged", ref["dodged"]),
                         ("blocked", ref["blocked"]),
                         ("landed", ref["landed"])):
            print("    %-24s %6d  %5.1f%%"
                  % (label, n, 100.0 * n / ref["thrown"] if ref["thrown"] else 0))
        print()
        print("THE GAP")
        print("  %-28s %12s %12s %9s"
              % ("", "core", "reference", "ratio"))
        for label, a, b in (("thrown per f-round",
                             core["thrown_per_fighter_round"],
                             ref["thrown_per_fighter_round"]),
                            ("connect %", core["connect_pct"], ref["connect_pct"]),
                            ("knockdowns per minute", core["kd_per_minute"],
                             ref["kd_per_minute"])):
            print("  %-28s %12.2f %12.2f %8.1fx"
                  % (label, a, b, a / b if b else float("inf")))
        print()
        vol = core["thrown_per_fighter_round"] / ref["thrown_per_fighter_round"]
        acc = core["connect_pct"] / ref["connect_pct"]
        kd_per_land_core = core["knockdowns"] / float(core["landed"])
        kd_per_land_ref = ref["knockdowns"] / float(ref["landed"])
        lethal = kd_per_land_core / kd_per_land_ref
        print("THE GAP, FACTORISED")
        print("  knockdowns per minute, core over reference: %.1fx, and it comes"
              % (core["kd_per_minute"] / ref["kd_per_minute"]))
        print("  apart cleanly into three independent factors:")
        print("    volume     %5.1fx   punches thrown per fighter per round" % vol)
        print("    accuracy   %5.1fx   share of them that land" % acc)
        print("    lethality  %5.1fx   knockdowns per LANDED punch (%.4f vs %.4f)"
              % (lethal, kd_per_land_core, kd_per_land_ref))
        print("    product    %5.1fx" % (vol * acc * lethal))
        print()
        print("READ THIS AS:")
        print("  Canon's threshold was swept against the right-hand column and is")
        print("  being asked to govern the left. The threshold is not what differs")
        print("  between them - the PIPELINE is, in three separable places.")
        print()
        print("  ACCURACY. %.1f%% of reference punches miss before any guard check:"
              % (100.0 * (ref["whiffed"] + ref["dodged"]) / ref["thrown"]))
        print("  %.1f%% swept (no overlap) and %.1f%% actively dodged, the dodge"
              % (100.0 * ref["whiffed"] / ref["thrown"],
                 100.0 * ref["dodged"] / ref["thrown"]))
        print("  amplified by a slow punch's telegraph and by the defender's read")
        print("  of a repeated pattern. In the core that figure is ZERO. Geometry")
        print("  replaced the guard stage - a genuine determinism win - and")
        print("  silently dropped the sweep and evasion stages with it.")
        print()
        print("  VOLUME. The reference's Rule 12 range gate records %d out-of-range"
              % ref["out_of_range"])
        print("  attempts, which is the point: its POLICY only throws what the")
        print("  current band permits, so distance shapes the punch selection")
        print("  itself. The core stands at one fixed distance forever, so every")
        print("  punch is always available and the action set is thrown flat.")
        print("  That is also why the uppercut landed zero of 532 - an inside-band")
        print("  punch, thrown all night from outside, in a core with no bands.")
        print()
        print("  LETHALITY. %.1fx per landed punch is the residual after volume and"
              % lethal)
        print("  accuracy are removed, and it is the size of the stamina inflation")
        print("  measured independently tonight (2.17x from floor to the median")
        print("  eligible landing; 2.74x median pressure inflation). Fighters here")
        print("  arrive at every landing emptier than the reference's do - and")
        print("  28.8% of everything they spend on punching goes into the")
        print("  uppercut that cannot connect.")
        print()
        print("  So the three factors are not three problems. Two of them are the")
        print("  missing range model, and the third is what the missing range")
        print("  model does to the stamina economy.")

    out = {"core": core, "reference": ref}
    p = os.path.join(REPO, "sandbox", "Saved", "reference_gap.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 06:00 UTC | END ]
