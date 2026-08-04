# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 22:45 UTC | START ]
"""Decision packet: what should being caught mid-punch cost?

Phase O is held because the guard never works. A committed defender's extents are
multiplied by 0.6, which puts high_guard's 0.95 head lane at 0.57 - under the 0.6
interception threshold - so "committed" means "guard entirely absent", and the
fighters are committed on roughly 740 of every 800 decision ticks. Result: zero
blocks per round and every bout stopped inside round one.

This is an EXPERIMENT, not a contract. It does not touch Phase O's analyzer. It
measures the candidate answers so the Director's call arrives with numbers, per
PROJECT_PLAN R8: every request for decision comes with a written default.

Run: python -m tools.engine.experiment_guard_stage
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402

REPO = O.REPO


def cliff_analysis() -> list:
    """Candidate A: soften committed_defense's multiplier.

    The point of this function is that it settles the question with arithmetic
    rather than a sweep. Against a HARD threshold, a lane is closed when
    extent x multiplier >= threshold. Solving for the multiplier gives the exact
    value at which each lane flips - and because every posture's extents are far
    from the threshold, the flip is a CLIFF, not a dial.
    """
    c = O.canon_pack()
    thr = c["thr"]
    out = []
    for pid in O.POSTURES:
        for lane, ext in sorted(c["posture"][pid]["ext"].items()):
            flip = (thr * 10000 + ext - 1) // ext if ext else None
            out.append({
                "posture": pid,
                "lane": lane,
                "extent": ext / 10000.0,
                "closed_when_free": ext >= thr,
                "multiplier_that_flips_it": None if flip is None else flip / 10000.0,
                "closed_at_current_0_6": (ext * c["cd_mult"]) // 10000 >= thr,
            })
    return out


def probabilistic_guard(seed: int, rounds: int = 3) -> dict:
    """Candidate B: port the reference simulator's own guard stage.

    engine.py resolves a block with `r_guard < extent * 0.55 * (1 + read)`. The
    0.55 is canon's, not invented here, and the draw comes from the same LCG the
    alignment grade already uses - so this is the same kind of faithful port that
    contact quality was, not a new mechanic.

    Implemented as a lightweight re-simulation rather than a fork of the Phase O
    analyzer: it counts outcomes, not stream bytes, because the question is
    "does the guard ever work" and not "do two languages agree".
    """
    c = O.canon_pack()
    st = [c["st_max"], c["st_max"]]
    cond = [{r: 0 for r in O.REGIONS}, {r: 0 for r in O.REGIONS}]
    committed = [0, 0]
    punch = [None, None]
    posture = ["high_guard", "high_guard"]
    pos = [c["axis"] // 2 - 4500, c["axis"] // 2 + 4500]
    x = seed % O.LCG_M
    blocked = landed = kd = 0
    kd_round = [0, 0]
    kd_bout = [0, 0]
    stopped = False
    rounds_done = 0

    for _rnd in range(rounds):
        kd_round = [0, 0]
        for t in range(1, c["round_ticks"] + 1):
            if stopped:
                break
            T = _rnd * c["round_ticks"] + t
            for i in (0, 1):
                if punch[i] is not None:
                    mid, t0 = punch[i]
                    mv = c["moves"][mid]
                    k = T - t0
                    if mv["startup"] < k <= mv["startup"] + mv["active"]:
                        opp = 1 - i
                        tip_ext = O.N._ext(c, mid, k)
                        if i == 0:
                            tip, surface = pos[0] + tip_ext, pos[1] - c["half_depth"]
                            ap, asf = tip >= surface - c["plane_off"], tip >= surface
                        else:
                            tip, surface = pos[1] - tip_ext, pos[0] + c["half_depth"]
                            ap, asf = tip <= surface + c["plane_off"], tip <= surface
                        d_comm = committed[opp] > 0
                        gmult = O.N._guard_mult(cond[opp], c)
                        dext = O.N._extent(c, posture[opp], mv["height"], gmult, d_comm)
                        if ap or asf:
                            # the ported stage: a chance, not a threshold
                            x = (O.LCG_A * x + O.LCG_C) % O.LCG_M
                            roll = x % 10000
                            if roll < (dext * 5500) // 10000:
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
                                pr = O.pressure(c, mv, cond[opp], st[opp], d_comm,
                                                dext, c["kd_force"][cls])
                                if pr >= c["kd_threshold"]:
                                    kd += 1
                                    kd_round[opp] += 1
                                    kd_bout[opp] += 1
                                    committed[opp] = c["count_ticks"]
                                    for r in c["kd_regions"]:
                                        cond[opp][r] -= (cond[opp][r]
                                                         * c["cond_relief"]) // 10000
                                    st[opp] += ((c["st_max"] - st[opp])
                                                * c["stam_relief"]) // 10000
                                    if kd_round[opp] >= c["max_per_round"] \
                                            or kd_bout[opp] >= c["max_per_bout"]:
                                        stopped = True
                    elif k > mv["startup"] + mv["active"]:
                        punch[i] = None
                if committed[i] > 0:
                    committed[i] -= 1
                else:
                    st[i] = min(c["st_max"], st[i]
                                + (c["regen"] * O.N._regen_mult(cond[i], c)) // 10000)
                    st[i] = max(0, st[i] - c["posture"][posture[i]]["hold"])
                if T % c["interval"] or committed[i] > 0:
                    continue
                x = (O.LCG_A * x + O.LCG_C) % O.LCG_M
                action = O.ACTIONS[x % 11]
                if action in O.PUNCHES:
                    mv = c["moves"][action]
                    st[i] = max(0, st[i] - mv["cost"])
                    committed[i] = mv["frames"]
                    punch[i] = (action, T)
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
            for r in O.REGIONS:
                cond[n][r] -= (cond[n][r] * c["region_recovery"][r]) // 10000
    return {"blocked": blocked, "landed": landed, "knockdowns": kd,
            "stopped": stopped, "rounds": rounds_done}


def main() -> int:
    report = {"cliff": cliff_analysis(), "probabilistic": {}}
    seeds = list(range(4240, 4264))
    agg = {"blocked": 0, "landed": 0, "knockdowns": 0, "stopped": 0,
           "rounds": 0, "seeds": len(seeds)}
    for s in seeds:
        r = probabilistic_guard(s)
        for k in ("blocked", "landed", "knockdowns", "rounds"):
            agg[k] += r[k]
        agg["stopped"] += 1 if r["stopped"] else 0
    agg["decisions"] = agg["seeds"] - agg["stopped"]
    report["probabilistic"] = agg
    report["hard_threshold"] = O.sweep(seeds)

    out = os.path.join(REPO, "sandbox", "Saved", "guard_stage_experiment.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    io.open(out, "w", encoding="utf-8").write(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 22:45 UTC | END ]
