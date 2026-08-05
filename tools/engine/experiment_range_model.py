# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 07:20 UTC | START ]
"""The same fight, with a distance in it.

This is Phase Q measured before it is contracted, the way the per-hand guard was.
It is a SEPARATE fight function on purpose. `experiment_per_hand_guard.run_with`
is now depended on by six measurement tools whose numbers are quoted in committed
records; changing it in place would silently rewrite every one of them, which is
the "editing the past" hazard this repository already pins phase evidence
against. So the range model gets its own runner and the two can be compared.

WHAT CHANGES, all of it from `analyze_core_range` and none of it invented:

  SEPARATION IS STATE.   One number, q10000 reach units, starting at the 0.90 ru
                         every phase since H has used - so the opening tick is
                         the opening tick it always was.
  FOOTWORK MOVES IT.     `step_in` and `step_out` post a 0.22 ru stride, drained
                         at canon's 0.14 ru per-tick cap, so a stride takes two
                         ticks and a man can be caught mid-step. `step_lateral`
                         still moves nothing and is knowingly inert until the
                         lateral geometry exists.
  RULE 12 GATES THROWS.  A punch whose authored band is not the band the thrower
                         is in travels its full arc into empty air. It is tested
                         at THROW time, keeps its frames, and pays its stamina.
  GEOMETRY STILL RULES.  The tip-versus-surface test survives unchanged; it now
                         reads a separation that moves. Band and geometry are
                         both required and they are different questions.

Run: python -m tools.engine.experiment_range_model
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_range as Q  # noqa: E402
import analyze_core_round as O  # noqa: E402
import experiment_per_hand_guard as H  # noqa: E402

SEEDS = list(range(4240, 4264))
TICKS_PER_MIN = 3600
ROUND_MINUTES = 3.0
START_SEP = 9000                      # 0.90 ru, the fixed separation of Phase H


def run_range(seed: int, c: dict, rc: dict, rounds: int = 3,
              chooser=None, gate: bool = True, footwork: bool = True,
              band_ref: list = None) -> dict:
    """Phase O's fight with separation as state.

    `gate` and `footwork` are switches so the two halves of the phase can be
    attributed separately. Turning both off must reproduce the Phase O numbers
    exactly, and the caller checks that rather than trusting it.
    """
    st = [c["st_max"], c["st_max"]]
    cond = [{r: 0 for r in O.REGIONS}, {r: 0 for r in O.REGIONS}]
    committed = [0, 0]
    punch = [None, None]
    vacated = [None, None]
    posture = ["high_guard", "high_guard"]
    pending = [0, 0]
    # Two positions on canon's ring track, not a bare separation: without a ring
    # a retreating fighter opens distance forever, which is the abuse the track
    # block exists to close. Centred, at the 0.90 ru every phase since H used.
    pos = [rc["axis"] // 2 - START_SEP // 2, rc["axis"] // 2 + START_SEP // 2]
    sep = pos[1] - pos[0]
    band = Q.band_at(rc, sep)
    roped = 0
    x = seed % O.LCG_M
    blocked = landed = kd = thrown = whiffed = 0
    eligible = 0
    band_ticks = {k: 0 for k, _, _ in rc["bands"]}
    thrown_in_band = {}
    kd_round = [0, 0]
    kd_bout = [0, 0]
    stopped = False
    rounds_done = 0
    first_kd_tick = stop_tick = None
    total_ticks = 0
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

            # Footwork resolves first: a punch is judged against the distance
            # that exists when it lands, not the one that existed when the tick
            # began. Both fighters may be moving, so both drain their own
            # pending stride under canon's per-tick cap.
            if footwork:
                for i in (0, 1):
                    applied, pending[i] = Q.drain(rc, pending[i])
                    if applied:
                        # `pending` is signed in SEPARATION; convert it to this
                        # fighter's own direction on the track before the ropes
                        # are consulted, because the rope rule is about which
                        # way HE is going, not about the gap.
                        own = applied if i == 1 else -applied
                        allowed = Q.rope_scaled(rc, pos[i], own, pos[1 - i])
                        if allowed != own:
                            roped += 1
                            pending[i] = 0      # the step is spent, not banked
                        pos[i] = max(0, min(rc["axis"], pos[i] + allowed))
                if pos[1] - pos[0] < rc["min_sep"]:
                    # Bounded mutual pushback, never a repositioning teleport.
                    over = rc["min_sep"] - (pos[1] - pos[0])
                    pos[0] = max(0, pos[0] - over // 2)
                    pos[1] = min(rc["axis"], pos[1] + (over - over // 2))
                sep = max(rc["min_sep"], pos[1] - pos[0])
                band = Q.resolve_band(rc, band, sep)
            band_ticks[band] += 1
            if band_ref is not None:
                band_ref[0] = band      # what a band-aware policy observes

            for i in (0, 1):
                if punch[i] is not None:
                    mid, t0, ok = punch[i]
                    mv = c["moves"][mid]
                    k = T - t0
                    if mv["startup"] < k <= mv["startup"] + mv["active"]:
                        opp = 1 - i
                        if not ok:
                            # Rule 12: it travels its arc and finds empty air.
                            # It is cleared at the END of its active frames so
                            # it keeps occupying them, exactly like a punch that
                            # reached; the commitment is already paid.
                            if k == mv["startup"] + mv["active"]:
                                whiffed += 1
                                punch[i] = None
                            continue
                        tip_ext = O.N._ext(c, mid, k)
                        gap = sep - c["half_depth"]
                        ap = tip_ext >= gap - c["plane_off"]
                        asf = tip_ext >= gap
                        d_comm = committed[opp] > 0
                        gmult = O.N._guard_mult(cond[opp], c)
                        dext = H.per_hand_extent(
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
                        if not ok:
                            whiffed += 1
                        punch[i] = None
                if committed[i] > 0:
                    committed[i] -= 1
                    if committed[i] == 0:
                        vacated[i] = None
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
                    ok = Q.in_band(rc, action, band) if gate else True
                    punch[i] = (action, T, ok)
                    thrown += 1
                    d = thrown_in_band.setdefault(action, [0, 0])
                    d[0] += 1
                    if ok:
                        d[1] += 1
                    vacated[i] = mv["height"]
                elif action == "switch_guard":
                    posture[i] = "tight_elbow" if posture[i] == "high_guard" \
                        else "high_guard"
                    committed[i] = c["interval"]
                elif action != "idle":
                    mv = c["moves"].get(action)
                    if mv:
                        st[i] = max(0, st[i] - mv["cost"])
                        committed[i] = mv["frames"]
                    if footwork:
                        pending[i] += Q.step_delta(rc, action)
        rounds_done += 1
        if stopped:
            break
        for n in (0, 1):
            st[n] += ((c["st_max"] - st[n]) * c["between_stam"]) // 10000
            for rg in O.REGIONS:
                cond[n][rg] -= (cond[n][rg] * c["region_recovery"][rg]) // 10000
    return {"blocked": blocked, "landed": landed, "knockdowns": kd,
            "stopped": stopped, "rounds": rounds_done, "thrown": thrown,
            "whiffed": whiffed, "eligible": eligible,
            "first_kd_tick": first_kd_tick, "stop_tick": stop_tick,
            "total_ticks": total_ticks, "stamina_gauges": stamina_gauges,
            "end_stamina": [st[0] / 10000.0, st[1] / 10000.0],
            "band_ticks": band_ticks, "thrown_in_band": thrown_in_band,
            "end_sep": sep, "roped": roped}


def band_aware(rc: dict, band_ref: list):
    """The reference simulator's policy discipline, in one sentence.

    The reference logs ZERO out-of-range attempts across 24 bouts - not because
    it has no gate but because its policy only throws what the current band
    permits. That is the whole difference between a fighter and a coin, and it
    is legal to read: range band is an `observable_input` under Rule 3/4.

    So: throw only what this band allows; if the band allows nothing, close the
    distance. Choice WITHIN each group stays uniform, because canon authors no
    preference there and this experiment invents none.
    """
    order = [k for k, _, _ in rc["bands"]]
    punch_bands = sorted({order.index(rc["move_band"][a]) for a in O.PUNCHES
                          if a in rc["move_band"]})

    def choose(x: int) -> str:
        band = band_ref[0]
        legal = [a for a in O.PUNCHES if Q.in_band(rc, a, band)]
        if not legal:
            # Walk toward the nearest band that HAS punches in it, in whichever
            # direction that is. Stepping in unconditionally is what a fighter
            # who has never heard of the clinch would do - and the clinch band
            # authors no punches at all, so he would stand there closing a
            # distance that was already closed, forever.
            here = order.index(band)
            return "step_out" if here < punch_bands[0] else "step_in"
        pool = list(legal) + ["step_in", "step_out", "step_lateral",
                              "switch_guard", "idle"]
        return pool[(x // 10000) % len(pool)]
    return choose


def sweep(gate: bool, footwork: bool, policy: bool = False,
          interval: int = None) -> dict:
    c = dict(O.canon_pack())
    if interval:
        c["interval"] = interval
    rc = Q.range_pack()
    agg = {"thrown": 0, "landed": 0, "blocked": 0, "whiffed": 0, "eligible": 0,
           "kd": 0, "ticks": 0, "cards": 0, "roped": 0}
    stops, g18 = [], []
    bands = {k: 0 for k, _, _ in rc["bands"]}
    per_move = {}
    for s in SEEDS:
        ref = [Q.band_at(rc, START_SEP)]
        chooser = band_aware(rc, ref) if policy else None
        r = run_range(s, c, rc, 3, chooser, gate=gate, footwork=footwork,
                      band_ref=ref if policy else None)
        agg["roped"] += r["roped"]
        for a, b in (("thrown", "thrown"), ("landed", "landed"),
                     ("blocked", "blocked"), ("whiffed", "whiffed"),
                     ("eligible", "eligible")):
            agg[a] += r[b]
        agg["kd"] += r["knockdowns"]
        agg["ticks"] += r["total_ticks"]
        if r["stop_tick"] is not None:
            stops.append(r["stop_tick"])
        else:
            agg["cards"] += 1
        if 1800 in r["stamina_gauges"]:
            g18.append(sum(r["stamina_gauges"][1800]) / 2.0)
        for k, v in r["band_ticks"].items():
            bands[k] += v
        for k, v in r["thrown_in_band"].items():
            d = per_move.setdefault(k, [0, 0])
            d[0] += v[0]
            d[1] += v[1]
    minutes = agg["ticks"] / float(TICKS_PER_MIN)
    full = 3 * c["round_ticks"]
    elig_full = (agg["eligible"] / float(agg["ticks"])) * full
    conv = agg["kd"] / float(agg["eligible"]) if agg["eligible"] else 0.0
    need = 3.0 / elig_full if elig_full else None
    return {"gate": gate, "footwork": footwork, "policy": policy,
            "roped": agg["roped"],
            "thrown": agg["thrown"], "landed": agg["landed"],
            "blocked": agg["blocked"], "whiffed": agg["whiffed"],
            "eligible": agg["eligible"], "knockdowns": agg["kd"],
            "cards": agg["cards"], "seeds": len(SEEDS),
            "connect_pct": 100.0 * agg["landed"] / agg["thrown"]
            if agg["thrown"] else 0.0,
            "thrown_per_fighter_round": agg["thrown"] / minutes * ROUND_MINUTES / 2.0,
            "kd_per_minute": agg["kd"] / minutes,
            "kd_per_eligible": conv, "conversion_needed": need,
            "gap_x": conv / need if need else None,
            "mean_ticks_to_stoppage":
                sum(stops) / float(len(stops)) if stops else None,
            "stamina_at_1800": sum(g18) / float(len(g18)) if g18 else None,
            "band_ticks": bands, "per_move": per_move}


def main() -> int:
    rc = Q.range_pack()
    if rc["canon_errors"]:
        print("CANON REFUSED:")
        for e in rc["canon_errors"]:
            print("  -", e)
        return 1
    for name, fn in (("footwork is not inert", Q.footwork_is_not_inert),
                     ("the uppercut becomes possible",
                      Q.the_uppercut_becomes_possible),
                     ("hysteresis kills flicker", Q.hysteresis_kills_flicker),
                     ("running is finite", Q.running_is_finite)):
        print("  %-32s %s" % (name, "yes" if fn(rc) else "NO"))
    print()

    rows = {}
    for label, gate, foot, pol, iv in (
            ("neither (= Phase O)", False, False, False, None),
            ("Rule 12 gate only", True, False, False, None),
            ("footwork only", False, True, False, None),
            ("the phase, coin", True, True, False, None),
            ("the phase, a fighter", True, True, True, None),
            ("+ boxer's cadence 20", True, True, True, 20),
            ("+ boxer's cadence 48", True, True, True, 48)):
        rows[label] = sweep(gate, foot, pol, iv)

    base = H.run(SEEDS[0])
    check = run_range(SEEDS[0], O.canon_pack(), rc, 3, None,
                      gate=False, footwork=False)
    same = all(base[k] == check[k] for k in
               ("blocked", "landed", "knockdowns", "thrown", "rounds"))
    print("  control: both switches off reproduces Phase O exactly ... %s"
          % ("yes" if same else "NO - the runner is not a superset"))
    print()

    print("  %-22s %8s %8s %8s %9s %8s %7s %6s"
          % ("configuration", "thr/f-rd", "whiff", "connect", "kd/min",
             "gap", "cards", "roped"))
    for label in rows:
        r = rows[label]
        print("  %-22s %8.1f %8d %7.1f%% %9.2f %7.1fx %3d/%-2d %6d"
              % (label, r["thrown_per_fighter_round"], r["whiffed"],
                 r["connect_pct"], r["kd_per_minute"], r["gap_x"],
                 r["cards"], r["seeds"], r["roped"]))
    print("  %-22s %8.1f %8s %7.1f%% %9.2f %7s %3d/%-2d"
          % ("REFERENCE SIM", 40.72, "-", 42.41, 0.38, "-", 20, 24))
    print()

    ph = rows["the phase, a fighter"]
    print("  where the fight is fought, with footwork (ticks per band):")
    tot = float(sum(ph["band_ticks"].values())) or 1.0
    for k, v in ph["band_ticks"].items():
        print("    %-14s %8d  %5.1f%%" % (k, v, 100.0 * v / tot))
    print()
    print("  punches by authored band, and how many were thrown in it:")
    print("    %-20s %8s %8s %9s" % ("move", "thrown", "in band", "wasted"))
    for m in O.PUNCHES:
        t, ok = ph["per_move"].get(m, [0, 0])
        print("    %-20s %8d %8d %8.1f%%"
              % (m, t, ok, 100.0 * (t - ok) / t if t else 0.0))

    p = os.path.join(O.REPO, "sandbox", "Saved", "range_model.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 07:20 UTC | END ]
