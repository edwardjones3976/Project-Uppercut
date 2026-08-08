# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:35 UTC | START ]
"""Run the CPU policy and the Wind/Reserve economy in one loop, and look.

    python -m tools.engine.probe_policy_stamina --out probe.json

A STRUCTURAL DIAGNOSTIC, NOT CALIBRATION. Director ruling R5 is explicit:
no broad stamina tuning until observable integrated policy produces plausible
boxing cadence, and synthetic probes remain structural diagnostics only. This
changes no canon value, writes no pin, and mints no evidence. It answers one
question nobody has asked yet - when the policy decides and the economy charges,
where does Wind actually go? - and renders it against the acceptance bands
`stamina_economy.json` already declares.

WHAT IT IS NOT. Not an integrated golden stream: it writes no marker stream and
takes no hash. The integrated contract owns that, and it does not exist yet.
"""
import argparse
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from tools.uppercut_integrated import policy as P     # noqa: E402
from tools.uppercut_integrated import rng as R        # noqa: E402
from tools.uppercut_integrated import contract as C   # noqa: E402
from tools.uppercut_stamina import economy as E       # noqa: E402

ROUND_TICKS = 180 * 60

# How a tactical answer becomes something the economy can charge for. The
# economy takes an ACTION FAMILY (which decides recovery) and a MOVE ID (which
# decides cost) and Decision 0024 is explicit that they are not interchangeable.
FAMILY = {
    P.OBSERVE: "observe",
    P.HOLD_POSITION: "hold_position",
    P.REST: "rest",
    P.MICRO_ADJUST: "micro_adjust",
    P.ADVANCE: "move",
    P.RETREAT: "move",
    P.GUARD: "guard",
    P.EVADE: "evade",
    P.ATTACK: "attack",
}


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:35 UTC | START edit: units defect ]
# THE FIRST VERSION OF THIS FUNCTION WAS WRONG, and its first run is the reason
# this comment exists. It read `locomotion.modes[0].stride_length_ru` - 0.55,
# free_navigation - and charged the economy that distance EVERY TICK. A stride
# is the length of a STEP. `movement_model.locomotion.max_frame_displacement_ru`
# is 0.14 and its own note calls it "a hard per-tick displacement cap below
# every stride", so the probe was moving a fighter 3.9x faster than canon
# permits per frame and billing him for all of it.
#
# That is the 2026-08-03 units error a third time, and worth naming precisely:
# both earlier instances were caught on the RECOVERY side, and `economy_pack`
# grew a units guard that multiplies every recovery rate by the round length.
# The guard is one-sided. Nothing multiplies a DRAIN rate by the round length,
# so a per-step distance billed per tick sailed through every gate in the repo.
#
# The mode is named, not indexed. `generic_sandbox_effort.json` says wind_per_ru
# is "numerically the same rate movement_model.locomotion.boxing_steps
# .stamina_cost_per_ru carries", so boxing_steps is the mode that price was
# settled against; taking modes[0] priced free_navigation at a boxing step's
# rate as well as at the wrong cadence.
MOVE_MODE = "boxing_steps"


def displacement_per_tick_ru(repo):
    """What one tick of footwork actually covers, in q10000. Read, never invented.

    The authored stride of the priced mode, clamped by the declared hard
    per-tick displacement cap. Both numbers come out of canon; if either is
    missing this refuses rather than guessing a distance.
    """
    doc = json.load(io.open(os.path.join(repo, "data", "movement_model.json"),
                            encoding="utf-8"))
    loco = doc["locomotion"]
    stride = None
    for m in loco["modes"]:
        if m.get("posture_mode") == MOVE_MODE and "stride_length_ru" in m:
            stride = int(round(float(m["stride_length_ru"]) * 10000))
    if stride is None:
        raise SystemExit(
            "locomotion declares no %r mode with a stride_length_ru - refusing "
            "to invent a distance for a displacement-priced move" % MOVE_MODE)
    if "max_frame_displacement_ru" not in loco:
        raise SystemExit(
            "locomotion declares no max_frame_displacement_ru - refusing to "
            "bill a per-step stride as a per-tick displacement, which is "
            "exactly the units error this function was rewritten to stop")
    cap = int(round(float(loco["max_frame_displacement_ru"]) * 10000))
    return min(stride, cap)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:35 UTC | END edit ]


def observe(me, foe, c, stride, tick, ticks_left):
    """Build one fighter's view. Only what a fighter could actually see.

    The opponent contributes his BAND, whether he is committed or recovering,
    whether he is coming forward, and what he has been throwing. Never his Wind,
    never his Reserve - those are not on Observation and could not be passed.
    """
    return P.Observation(
        wind_fraction=E.floordiv(me["wind"] * 10000, c["wind_max"]),
        reserve_fraction=E.floordiv(me["reserve"] * 10000, c["reserve_max"]),
        wind_is_low=me["wind"] < c["wind_low"],
        wind_is_exhausted=me["wind"] < c["wind_exhausted"],
        hands_available=("lead", "rear"),
        in_recovery=me["recovery"] > 0,
        recovery_ticks_left=me["recovery"],
        range_band=me["band"], preferred_band=me["preferred"],
        opponent_band=foe["band"],
        opponent_committed=foe["recovery"] > 0,
        opponent_recovering=foe["recovery"] > 0,
        opponent_advancing=foe["last_tactic"] == P.ADVANCE,
        opponent_recent_moves=tuple(foe["thrown"][-4:]),
        round_number=1, ticks_left_in_round=ticks_left,
        own_recent_moves=tuple(me["thrown"][-4:]),
        consecutive_failed_attacks=me["failed"],
    )


def run(seed=4242, ticks=ROUND_TICKS):
    c = E.economy_pack()
    if c["errors"]:
        raise SystemExit("the stamina canon fails its own contract: %s"
                         % "; ".join(c["errors"]))
    stride = displacement_per_tick_ru(REPO)
    rng = R.BoutRng(seed, C.CONTRACT)
    stream = rng.stream("policy_intent")

    def fighter(preferred, aggression):
        return {"wind": c["wind_start"], "reserve": c["reserve_start"],
                "band": "mid", "preferred": preferred, "recovery": 0,
                "thrown": [], "failed": 0, "last_tactic": None,
                "punches": 0, "profile": P.Profile(aggression, preferred),
                "wind_trace": [], "reasons": {},
                # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
                #   2026-08-08 07:35 UTC | START edit: the Wind ledger ]
                # The first run reported a Wind trace that went flat and gave
                # no way to say WHY, so the only honest reading available was
                # "something cancels out". A resource diagnostic that cannot
                # attribute the resource is a picture, not a diagnostic.
                # Per family: how many ticks chose it, and the signed Wind the
                # economy actually applied on those ticks. Signed, because the
                # net is the thing in question - a family that both charges and
                # repays inside one tick must not be counted twice.
                "family_ticks": {}, "family_wind": {}}
                # [ ... | 2026-08-08 07:35 UTC | END edit ]

    fs = [fighter("mid", 6500), fighter("inside", 4000)]

    for t in range(ticks):
        left = ticks - t
        for i, me in enumerate(fs):
            foe = fs[1 - i]
            d = P.decide(observe(me, foe, c, stride, t, left), stream,
                         me["profile"])
            me["reasons"][d.reason] = me["reasons"].get(d.reason, 0) + 1
            me["last_tactic"] = d.tactical

            family = FAMILY[d.tactical]
            move = d.execution
            disp = stride if d.tactical in (P.ADVANCE, P.RETREAT) else 0
            if d.tactical == P.ATTACK:
                me["punches"] += 1
                me["thrown"].append(move)
                me["recovery"] = 14          # a committed punch is not free
                me["failed"] = 0
            if me["recovery"] > 0:
                me["recovery"] -= 1

            before = me["wind"]
            me["wind"], me["reserve"] = E.step(
                c, me["wind"], me["reserve"], family,
                move_id=move if move else None, displacement_ru=disp)
            me["family_ticks"][family] = me["family_ticks"].get(family, 0) + 1
            me["family_wind"][family] = (me["family_wind"].get(family, 0)
                                         + me["wind"] - before)

            # Movement actually moves. Bands are the range subsystem's job in
            # the real bout; here they are a stand-in so the policy has
            # something to react to, and this probe claims nothing about range.
            if d.tactical == P.ADVANCE:
                me["band"] = foe["band"] = _closer(me["band"])
            elif d.tactical == P.RETREAT:
                me["band"] = foe["band"] = _further(me["band"])

            if t % 60 == 0:
                me["wind_trace"].append(
                    round(me["wind"] * 100.0 / c["wind_max"], 2))
    return c, fs


def _closer(band):
    i = max(0, P.BANDS.index(band) - 1)
    return P.BANDS[i]


def _further(band):
    i = min(len(P.BANDS) - 1, P.BANDS.index(band) + 1)
    return P.BANDS[i]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--ticks", type=int, default=ROUND_TICKS)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    c, fs = run(args.seed, args.ticks)
    econ = json.load(io.open(os.path.join(REPO, "data", "stamina_economy.json"),
                             encoding="utf-8"))
    bands = econ["acceptance_bands"]

    report = {
        "diagnostic_only": (
            "Structural diagnostic under Director ruling R5. Not calibration "
            "evidence, not an integrated golden stream. No canon value changed, "
            "no pin written, no hash taken."),
        "seed": args.seed, "ticks": args.ticks,
        "wind_max": c["wind_max"],
        "acceptance_bands": bands,
        "values_are_fitted": econ["calibration_status"]["values_are_fitted"],
        "fighters": [],
    }
    for i, f in enumerate(fs):
        end_pct = f["wind"] * 100.0 / c["wind_max"]
        report["fighters"].append({
            "id": i,
            "preferred_band": f["preferred"],
            "aggression_bias": f["profile"].aggression_bias,
            "punches": f["punches"],
            "end_wind_pct": round(end_pct, 2),
            "end_reserve_pct": round(f["reserve"] * 100.0 / c["reserve_max"], 2),
            "wind_trace_pct": f["wind_trace"],
            "reasons": dict(sorted(f["reasons"].items(),
                                   key=lambda kv: -kv[1])),
            # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
            #   2026-08-08 07:35 UTC | START edit: the Wind ledger ]
            "wind_ledger": [
                {"family": fam,
                 "ticks": f["family_ticks"][fam],
                 "net_wind_pct": round(
                     f["family_wind"][fam] * 100.0 / c["wind_max"], 2),
                 "per_tick_wind_pct": round(
                     f["family_wind"][fam] * 100.0
                     / c["wind_max"] / f["family_ticks"][fam], 5)}
                for fam in sorted(f["family_ticks"],
                                  key=lambda k: f["family_wind"][k])
            ],
            # [ ... | 2026-08-08 07:35 UTC | END edit ]
            "in_ordinary_band": bool(
                bands["ordinary_round_wind_low"] <= end_pct
                <= bands["ordinary_round_wind_high"]),
        })

    text = json.dumps(report, indent=2)
    if args.out:
        io.open(args.out, "w", encoding="utf-8", newline="\n").write(text + "\n")
    for f in report["fighters"]:
        print("fighter %d  pref=%-8s aggr=%-5d punches=%-4d end_wind=%5.1f%% "
              "end_reserve=%5.1f%%  ordinary_band=%s"
              % (f["id"], f["preferred_band"], f["aggression_bias"],
                 f["punches"], f["end_wind_pct"], f["end_reserve_pct"],
                 f["in_ordinary_band"]))
        top = list(f["reasons"].items())[:5]
        print("   reasons: %s" % ", ".join("%s=%d" % kv for kv in top))
        for row in f["wind_ledger"]:
            print("   %-13s %6d ticks  net %+8.2f Wind  (%+.5f/tick)"
                  % (row["family"], row["ticks"], row["net_wind_pct"],
                     row["per_tick_wind_pct"]))
    print("\nacceptance bands (declared, unfitted): ordinary %s-%s%%, burst "
          "%s-%s%%, exceptional below %s%%"
          % (bands["ordinary_round_wind_low"], bands["ordinary_round_wind_high"],
             bands["burst_wind_low"], bands["burst_wind_high"],
             bands["exceptional_wind_below"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:35 UTC | END ]
