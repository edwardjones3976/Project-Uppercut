# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 23:10 UTC | START ]
"""The hand is the unit, not the fighter — measured before it becomes a phase.

The Director's mechanic: whether being caught mid-punch degrades your defence or
removes it depends on WHERE THE OTHER HAND IS. A fighter mid-jab still has his
rear hand home, and that hand can catch. A fighter who has committed the hand
that was covering the incoming lane has nothing there. Same commitment,
different defence.

The nuance is already authored; only our core flattened it. `move.hand` is
lead/rear on every punch, and `committed_defense` already answers "how much
coverage survives commitment" with 0.6. What the current model does is apply that
0.6 to BOTH lanes at once — a whole-body dimmer — which is exactly why it turned
out to be a switch with a single meaningful position (the 0.6316 cliff).

Per hand, with no new coefficient at all:

    the lane the defender's committed hand VACATED   -> canon's 0.6 multiplier
    the lane his free hand still covers              -> full authored extent

Which lane a hand vacated is derived, not invented: the height class of the punch
the defender himself threw. Throw upstairs and you are open upstairs; dig to the
body and the head is the lane you left. That is the same sentence a coach says,
and it falls out of `move.guard_interaction` -> `height_by_guard_interaction`,
both already canon.

KNOWN LIMIT, stated up front: our lanes are high/low, not left/right, so this
expresses "open where your hand went" and not yet "open on the side you punched
from". The lateral half needs the 2D geometry that `pose_geometry` already flags
as pending for the hook. This is the vertical half of the Director's mechanic,
reachable today.

Run: python -m tools.engine.experiment_per_hand_guard
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402


def per_hand_extent(c, posture, incoming_height, vacated_height, gmult):
    """The whole idea, in five lines.

    `vacated_height` is the height class of the punch the DEFENDER threw and is
    still inside; None when he is free. Coverage in the incoming lane is
    degraded only if that is the lane his own hand left.
    """
    e = c["posture"][posture]["ext"].get(incoming_height, 0)
    e = (e * gmult) // 10000
    if vacated_height is not None and vacated_height == incoming_height:
        e = (e * c["cd_mult"]) // 10000
    return e


def _terms(c, mv, cond, stamina, committed, extent, kd_force, pr, tick) -> dict:
    """`O.pressure` taken apart into the four multiplicands it applies, in the
    same order and with the same integer arithmetic.

    This is deliberately a re-derivation and not a refactor of `O.pressure`:
    the analyzer's expression is pinned evidence and must not be reshaped to
    make a measurement convenient. `product` below is checked against the
    analyzer's own `pr` on every call, so a drift between the two is a crash
    rather than a quietly wrong table.
    """
    force = (kd_force * mv["impact"]) // 10000
    accumulated = ((cond["jaw_chin"] * 6000 + cond["head"] * 4000) // 10000) \
        * 10000 // c["cap"]["head"]
    stamina_frac = (stamina * 10000) // c["st_max"]
    balance = c["caught"] if committed else c["balanced"]
    guard = 10000 + (c["open_lane"]
                     * (10000 - max(0, min(10000, extent)))) // 10000
    p = (force * (c["baseline"] + accumulated)) // 10000
    p = (p * (14000 - stamina_frac)) // 10000
    p = (p * balance) // 10000
    p = (p * guard) // 10000
    assert p == pr, "term decomposition drifted from the analyzer's pressure"
    return {"tick": tick, "move": mv.get("id", "?"), "pressure": pr,
            "force": force, "condition": c["baseline"] + accumulated,
            "accumulated": accumulated, "stamina": 14000 - stamina_frac,
            "stamina_frac": stamina_frac, "balance": balance, "guard": guard,
            "extent": extent, "committed": committed}


def run(seed: int, rounds: int = 3) -> dict:
    return run_with(seed, O.canon_pack(), rounds, None)


def run_with(seed: int, c: dict, rounds: int = 3, chooser=None,
             on_eligible=None) -> dict:
    """`chooser(x) -> action` replaces the uniform coin when supplied, so a CPU
    policy can be measured against the same fight without forking it.

    `on_eligible(row)` is a read-only hook called at every landing eligible to
    cause a knockdown, with that landing's pressure terms already decomposed.
    It cannot draw from the LCG and cannot alter state, so a measurement taken
    through it is a measurement of this exact fight and not of a fork of it.
    """
    st = [c["st_max"], c["st_max"]]
    cond = [{r: 0 for r in O.REGIONS}, {r: 0 for r in O.REGIONS}]
    committed = [0, 0]
    punch = [None, None]
    vacated = [None, None]          # the height class each fighter's hand left
    posture = ["high_guard", "high_guard"]
    pos = [c["axis"] // 2 - 4500, c["axis"] // 2 + 4500]
    x = seed % O.LCG_M
    blocked = landed = kd = thrown = 0
    kd_round = [0, 0]
    kd_bout = [0, 0]
    stopped = False
    rounds_done = 0

    # Confound-free instrumentation, added 2026-08-05 02:40 UTC. Every sweep
    # before this compared TOTALS across bouts that all terminate on the
    # three-knockdown rule, so bout length was set by the outcome being
    # measured. These five record RATES and TIMES instead, and none of them
    # draws from the LCG, so the fight itself is bit-for-bit unchanged.
    eligible = 0          # landings that could have knocked a man down
    first_kd_tick = None  # when the fight first turned
    stop_tick = None      # when it ended, if it ended
    total_ticks = 0       # how long it actually ran
    # Stamina read at fixed wall-clock ticks, NOT at the end. "End stamina" is
    # stamina at the moment the fight happened to stop, which is the confound
    # again wearing a different hat. A gauge is only recorded if the fight was
    # still running when it passed, so a missing gauge is itself a reading.
    gauges = (600, 1200, 1800, 2400, 3600)
    stamina_gauges = {}

    for _r in range(rounds):
        kd_round = [0, 0]
        for t in range(1, c["round_ticks"] + 1):
            if stopped:
                break
            T = _r * c["round_ticks"] + t
            total_ticks = T
            if T in gauges:
                stamina_gauges[T] = [st[0] / 10000.0, st[1] / 10000.0]
            for i in (0, 1):
                if punch[i] is not None:
                    mid, t0 = punch[i]
                    mv = c["moves"][mid]
                    k = T - t0
                    if mv["startup"] < k <= mv["startup"] + mv["active"]:
                        opp = 1 - i
                        tip_ext = O.N._ext(c, mid, k)
                        if i == 0:
                            tip, surf = pos[0] + tip_ext, pos[1] - c["half_depth"]
                            ap, asf = tip >= surf - c["plane_off"], tip >= surf
                        else:
                            tip, surf = pos[1] - tip_ext, pos[0] + c["half_depth"]
                            ap, asf = tip <= surf + c["plane_off"], tip <= surf
                        d_comm = committed[opp] > 0
                        gmult = O.N._guard_mult(cond[opp], c)
                        dext = per_hand_extent(
                            c, posture[opp], mv["height"],
                            vacated[opp] if d_comm else None, gmult)
                        if ap and dext >= c["thr"]:
                            blocked += 1
                            punch[i] = None
                            continue
                        if asf:
                            x = (O.LCG_A * x + O.LCG_C) % O.LCG_M
                            cls, frac = O.grade(c, O.alignment(c, x, st[i]))
                            force = (frac * mv["impact"]) // 10000
                            region = mv["region"]
                            cond[opp][region] = min(c["cap"][region],
                                                    cond[opp][region] + force * 6)
                            landed += 1
                            punch[i] = None
                            if region in c["kd_regions"] and cls in c["kd_force"]:
                                eligible += 1
                                pr = O.pressure(c, mv, cond[opp], st[opp], d_comm,
                                                dext, c["kd_force"][cls])
                                if on_eligible is not None:
                                    on_eligible(_terms(c, mv, cond[opp], st[opp],
                                                       d_comm, dext,
                                                       c["kd_force"][cls], pr, T))
                                if pr >= c["kd_threshold"]:
                                    kd += 1
                                    if first_kd_tick is None:
                                        first_kd_tick = T
                                    kd_round[opp] += 1
                                    kd_bout[opp] += 1
                                    committed[opp] = c["count_ticks"]
                                    vacated[opp] = None
                                    for rg in c["kd_regions"]:
                                        cond[opp][rg] -= (cond[opp][rg]
                                                          * c["cond_relief"]) // 10000
                                    st[opp] += ((c["st_max"] - st[opp])
                                                * c["stam_relief"]) // 10000
                                    if kd_round[opp] >= c["max_per_round"] \
                                            or kd_bout[opp] >= c["max_per_bout"]:
                                        stopped = True
                                        stop_tick = T
                    elif k > mv["startup"] + mv["active"]:
                        punch[i] = None
                if committed[i] > 0:
                    committed[i] -= 1
                    if committed[i] == 0:
                        vacated[i] = None       # the hand comes home
                else:
                    st[i] = min(c["st_max"], st[i]
                                + (c["regen"] * O.N._regen_mult(cond[i], c)) // 10000)
                    st[i] = max(0, st[i] - c["posture"][posture[i]]["hold"])
                if T % c["interval"] or committed[i] > 0:
                    continue
                x = (O.LCG_A * x + O.LCG_C) % O.LCG_M
                action = chooser(x) if chooser else O.ACTIONS[x % 11]
                if action in O.PUNCHES:
                    mv = c["moves"][action]
                    st[i] = max(0, st[i] - mv["cost"])
                    committed[i] = mv["frames"]
                    punch[i] = (action, T)
                    thrown += 1
                    vacated[i] = mv["height"]   # <- the hand that left, and where
                elif action == "switch_guard":
                    posture[i] = "tight_elbow" if posture[i] == "high_guard" \
                        else "high_guard"
                    committed[i] = c["interval"]
                elif action != "idle":
                    mv = c["moves"].get(action)
                    if mv:
                        st[i] = max(0, st[i] - mv["cost"])
                        committed[i] = mv["frames"]
        rounds_done += 1
        if stopped:
            break
        for n in (0, 1):
            st[n] += ((c["st_max"] - st[n]) * c["between_stam"]) // 10000
            for rg in O.REGIONS:
                cond[n][rg] -= (cond[n][rg] * c["region_recovery"][rg]) // 10000
    return {"blocked": blocked, "landed": landed, "knockdowns": kd,
            "stopped": stopped, "rounds": rounds_done, "thrown": thrown,
            "end_stamina": [st[0] / 10000.0, st[1] / 10000.0],
            # Rates and times. Safe to compare across sweeps; the totals above
            # are not, because every bout ends where the outcome puts it.
            "eligible": eligible, "first_kd_tick": first_kd_tick,
            "stop_tick": stop_tick, "total_ticks": total_ticks,
            "stamina_gauges": stamina_gauges}


def main() -> int:
    seeds = list(range(4240, 4264))
    agg = {"blocked": 0, "landed": 0, "knockdowns": 0, "stopped": 0, "rounds": 0,
           "seeds": len(seeds)}
    for s in seeds:
        r = run(s)
        for k in ("blocked", "landed", "knockdowns", "rounds"):
            agg[k] += r[k]
        agg["stopped"] += 1 if r["stopped"] else 0
    agg["decisions"] = agg["seeds"] - agg["stopped"]
    out = os.path.join(O.REPO, "sandbox", "Saved", "per_hand_guard_experiment.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    io.open(out, "w", encoding="utf-8").write(json.dumps(agg, indent=1))
    print(json.dumps(agg, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 23:10 UTC | END ]
