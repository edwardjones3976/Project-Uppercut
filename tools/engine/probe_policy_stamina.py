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
from tools.uppercut_integrated import fighter as FS   # noqa: E402
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


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:35 UTC | START edit: the observation seam ]
# The hand-rolled `observe()` that used to live here is gone. It built an
# Observation out of this file's own dict of fighter fields, which made a
# HARNESS the author of "what can a fighter see?" - and a harness may explore,
# not define. `FighterState.observation()` is now the single answer and this
# probe consumes it like any other caller will.
#
# The bookkeeping below is the probe's own and stays the probe's own: a trace,
# a reason histogram and the Wind ledger are diagnostics, not fight state, and
# putting them on FighterState would have smuggled them into the runtime.
class Log(object):
    __slots__ = ("trace", "reasons", "family_ticks", "family_wind", "last_tactic")

    def __init__(self):
        self.trace, self.reasons = [], {}
        self.family_ticks, self.family_wind = {}, {}
        self.last_tactic = None


def run(seed=4242, ticks=ROUND_TICKS):
    c = E.economy_pack()
    if c["errors"]:
        raise SystemExit("the stamina canon fails its own contract: %s"
                         % "; ".join(c["errors"]))
    stride = displacement_per_tick_ru(REPO)
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 10:10 UTC | START edit: Decision 0026 ]
    # Fighter-local streams by stable participant identity, not one shared
    # cursor. With the shared version, red thinking one extra time moved blue's
    # next tie-break - the coupling Decision 0022 forbids between subsystems,
    # reappearing inside one.
    red, blue = C.DEFAULT_PARTICIPANTS
    rng = R.BoutRng(seed, C.CONTRACT, C.DEFAULT_PARTICIPANTS)

    fs = [FS.FighterState(red, c, P.Profile(6500, "mid"), band="mid"),
          FS.FighterState(blue, c, P.Profile(4000, "inside"), band="mid")]
    streams = {f.id: rng.stream("policy_intent", f.id) for f in fs}
    # [ ... | 2026-08-08 10:10 UTC | END edit ]
    logs = [Log(), Log()]

    for t in range(ticks):
        left = ticks - t
        for i, me in enumerate(fs):
            foe, log = fs[1 - i], logs[i]
            me.update_recovery_intent(c)
            d = P.decide(me.observation(c, foe, ticks_left_in_round=left),
                         streams[me.id], me.profile)
            log.reasons[d.reason] = log.reasons.get(d.reason, 0) + 1
            previous_tactic, log.last_tactic = log.last_tactic, d.tactical
            me.advancing = d.tactical == P.ADVANCE

            family = FAMILY[d.tactical]
            move = d.execution
            disp = stride if d.tactical in (P.ADVANCE, P.RETREAT) else 0
            # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
            #   2026-08-08 10:25 UTC | START edit: Decision 0026 Ruling D ]
            # A MOVE ID'S COST IS PER ACTION, NOT PER TICK, and the first
            # version of this loop charged it every tick the decision repeated.
            # A guard held for 31 ticks paid `guard_high` thirty-one times. It
            # showed up as a `guard` family bleeding 0.012 Wind a tick, which
            # is the exact shape of the units defect this probe was rewritten
            # to stop making - the same mistake, one layer up, found by the
            # ledger four hours after the ledger was added.
            #
            # An attack is a new commitment every time it is chosen. A guard,
            # an evasion or a pivot is entered once and then held, so it is
            # charged on the tick it is entered and free to sustain. Movement
            # is displacement-priced and is charged continuously, because the
            # ground is covered continuously.
            # AND THE FIRST VERSION OF THIS FIX BROKE MOVEMENT, which is worth
            # keeping on the record because it is the failure this repository
            # fears most. Suppressing the repeated move_id also suppressed the
            # DISPLACEMENT charge, movement became free, and both fighters
            # finished the round at 99.7% Wind having walked for three minutes.
            # Nothing raised. The probe simply reported that boxing is not
            # tiring - the identical symptom the `UnknownMove` docstring
            # describes from 2026-08-07, produced by the opposite cause.
            #
            # So the rule is per-BASIS, not per-tactic, and it is read from the
            # economy rather than restated here: a displacement-priced move is
            # charged every tick because the ground is covered every tick; a
            # flat per-action move is charged once, when it is entered.
            priced_by_distance = bool(move and c["moves"].get(move, {})
                                      .get("displacement"))
            newly_committed = (d.tactical == P.ATTACK
                               or d.tactical != previous_tactic)
            charge = move if (move and (priced_by_distance or newly_committed)) \
                else None
            # [ ... | 2026-08-08 10:25 UTC | END edit ]
            if d.tactical == P.ATTACK:
                me.committed_to(move, 14)    # a committed punch is not free
            me.tick_recovery()

            before = me.wind
            me.step(c, family, move_id=charge, displacement_ru=disp)
            log.family_ticks[family] = log.family_ticks.get(family, 0) + 1
            log.family_wind[family] = (log.family_wind.get(family, 0)
                                       + me.wind - before)

            # Movement actually moves. Bands are the range subsystem's job in
            # the real bout; here they are a stand-in so the policy has
            # something to react to, and this probe claims nothing about range.
            if d.tactical == P.ADVANCE:
                me.band = foe.band = _closer(me.band)
            elif d.tactical == P.RETREAT:
                me.band = foe.band = _further(me.band)

            if t % 60 == 0:
                log.trace.append(round(me.wind_pct(c), 2))
    return c, fs, logs
# [ ... | 2026-08-08 08:35 UTC | END edit ]


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

    c, fs, logs = run(args.seed, args.ticks)
    econ = json.load(io.open(os.path.join(REPO, "data", "stamina_economy.json"),
                             encoding="utf-8"))
    bands = econ["acceptance_bands"]

    report = {
        "diagnostic_only": (
            "Structural diagnostic under Director ruling R5. Not calibration "
            "evidence, not an integrated golden stream. No canon value changed, "
            "no pin written, no hash taken."),
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
        #   2026-08-08 10:15 UTC | START edit: Decision 0026 Ruling C ]
        "stress_only": True,
        "stress_note": (
            "THIS RUN DRIVES MOVEMENT AT max_frame_displacement_ru EVERY "
            "MOVEMENT TICK. Decision 0026 Ruling C: that value is a CEILING, "
            "not the distance a movement action travels, and the real figure "
            "is whatever the authoritative shared range runtime displaces. A "
            "probe may drive at the cap as a stress case; the depletion rate "
            "it produces MAY NOT be cited as evidence for or against the 0.60 "
            "wind-per-reach-unit coefficient, or any other stamina value. The "
            "first legitimate tuning evidence comes from the integrated policy "
            "driving the real range runtime and recording actual displacement, "
            "which does not exist yet."),
        "excluded_from_fit_evidence": True,
        # [ ... | 2026-08-08 10:15 UTC | END edit ]
        "seed": args.seed, "ticks": args.ticks,
        "wind_max": c["wind_max"],
        "acceptance_bands": bands,
        "values_are_fitted": econ["calibration_status"]["values_are_fitted"],
        "fighters": [],
    }
    for i, (f, log) in enumerate(zip(fs, logs)):
        end_pct = f.wind_pct(c)
        report["fighters"].append({
            "id": f.id,
            "preferred_band": f.profile.preferred_band,
            "aggression_bias": f.profile.aggression_bias,
            "punches": f.punches_thrown,
            "end_wind_pct": round(end_pct, 2),
            "end_reserve_pct": round(f.reserve_pct(c), 2),
            "wind_trace_pct": log.trace,
            "reasons": dict(sorted(log.reasons.items(),
                                   key=lambda kv: -kv[1])),
            # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
            #   2026-08-08 07:35 UTC | START edit: the Wind ledger ]
            "wind_ledger": [
                {"family": fam,
                 "ticks": log.family_ticks[fam],
                 "net_wind_pct": round(
                     log.family_wind[fam] * 100.0 / c["wind_max"], 2),
                 "per_tick_wind_pct": round(
                     log.family_wind[fam] * 100.0
                     / c["wind_max"] / log.family_ticks[fam], 5)}
                for fam in sorted(log.family_ticks,
                                  key=lambda k: log.family_wind[k])
            ],
            # [ ... | 2026-08-08 07:35 UTC | END edit ]
            "in_ordinary_band": bool(
                bands["ordinary_round_wind_low"] <= end_pct
                <= bands["ordinary_round_wind_high"]),
        })

    text = json.dumps(report, indent=2)
    if args.out:
        io.open(args.out, "w", encoding="utf-8", newline="\n").write(text + "\n")
    print("STRESS RUN - movement driven at the per-tick displacement CAP. "
          "Decision 0026 Ruling C: not fit evidence for any stamina value.\n")
    for f in report["fighters"]:
        print("fighter %-11s pref=%-8s aggr=%-5d punches=%-4d end_wind=%5.1f%% "
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
