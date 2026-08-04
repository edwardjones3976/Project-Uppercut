# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:40 UTC | START ]
"""Phase O marker contract and analyzer - a round that can END.

Decision 0012 slice item 9. Phase N gave condition somewhere to accumulate and
nowhere to go; this is where it goes. Five canon mechanisms enter the core:

  1. KNOCKDOWN FROM OBSERVABLE STATE (Rule 14, condition_model.knockdown).
     pressure = force x (undamaged_baseline + accumulated) x (1.4 - stamina_frac)
                x balance x guard
     where accumulated is the defender's jaw and head condition (0.6/0.4), balance
     is caught_committed_multiplier when he is inside his own recovery, and guard
     is 1 + unguarded_lane_bonus x (1 - extent). No dice. `flat_random_roll_per_
     punch: false` is not a comment - there is nowhere in this file a random
     number could enter the decision, and the analyzer checks the arithmetic.
     Only jaw_chin and head landings can do it.

  2. THE MANDATORY EIGHT COUNT. count_ticks_per_number x 8 = 480 ticks in which
     the man who was down loses the time as well as the point. Rule 16: the count
     arithmetic is identical for every referee - officiating philosophy never
     touches it.

  3. RELIEF ON RISING. The count is FOR something: jaw and head condition drop by
     count_condition_relief_fraction and stamina recovers count_stamina_relief_
     fraction of its deficit. Partial on purpose - the count buys clarity, never a
     fresh fighter, and the knockdown stays on the card forever.

  4. STOPPAGE. Three knockdowns in a round, or four in the bout, and the referee
     ends it. Both are canon numbers, not thresholds invented here.

  5. ROUNDS AND CARDS. Rounds of round_lengths_seconds x 60 ticks separated by
     between_rounds_break_ticks. Between rounds each region recovers its authored
     fraction and stamina recovers between_rounds_recovery_fraction of its
     deficit. Each round is scored 10-point-must: 10 to the round's winner, 9 to
     the loser, minus a point per knockdown suffered. The cards stay SEALED until
     the bout ends (Rule 3) - the stream carries them only in the final trailer,
     and the analyzer fails if a card value appears before it.

A DELIBERATE DEPARTURE, logged. Every previous phase carried its own frozen copy
of the sim. This one imports Phase N's canon_pack and helpers instead. The
condition layer is now large enough that a third hand-copy is a bigger risk than
the coupling: two copies that must agree, edited by different hands, is exactly
the drift the reconciliation logs exist to catch. The cost is real - a change to
Phase N's canon_pack changes this contract - and is accepted knowingly.

Stream (H|phase=O, Phase N's nine canon files plus clock_model):
  D|... , P|... , C|...   - as Phase N, plus:
  K|t|i|move|pressure|threshold|accumulated|stamina_frac|balance|guard|count
      the knockdown, with every term of the product it was computed from, so a
      wrong knockdown can be argued with rather than just observed
  R|t|round|i|down|stamina|head|jaw   - round boundary snapshot per fighter
  V|verdict|method|rounds|a_card|b_card|a_kd|b_kd   - the FINAL trailer only
  S|... - counts plus knockdowns, stoppages, rounds_completed

Usage: python analyze_core_round.py <markers.txt> [...]
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_condition as N  # noqa: E402  - the departure above

REPO = N.REPO
LCG_A, LCG_C, LCG_M = N.LCG_A, N.LCG_C, N.LCG_M
ACTIONS, PUNCHES, POSTURES, GCHAR = N.ACTIONS, N.PUNCHES, N.POSTURES, N.GCHAR
REGIONS, GRADED = N.REGIONS, N.GRADED
q, fnv1a64 = N.q, N.fnv1a64

CANON = dict(N.CANON, clock="data/clock_model.json")
CANON_ORDER = N.CANON_ORDER + ("clock",)
# Rounds are scored on landings; a knockdown costs the man who suffered it a
# point on top of losing the round. 10-point must, from judge.py.
ROUND_WIN, ROUND_LOSE = 10, 9


def canon_pack() -> dict:
    c = N.canon_pack()
    raw = io.open(os.path.join(REPO, CANON["clock"]), "rb").read()
    import hashlib
    c["sha"]["clock"] = hashlib.sha256(raw).hexdigest()
    clock = json.loads(raw)
    cm = json.loads(io.open(os.path.join(REPO, CANON["condition"]), "rb").read())
    kd = cm["knockdown"]
    pm = kd["pressure_modifiers"]
    st = cm["stamina"]

    c["round_ticks"] = int(max(clock["round_lengths_seconds"])) * int(
        clock["authority"]["tick_rate_hz"])
    c["break_ticks"] = int(cm["recovery"]["between_rounds_break_ticks"])
    c["kd_threshold"] = q(kd["pressure_threshold"])
    c["count_ticks"] = int(kd["count_ticks_per_number"]) * (
        8 if kd.get("mandatory_eight_count") else 3)
    c["cond_relief"] = q(kd["count_condition_relief_fraction"])
    c["stam_relief"] = q(kd["count_stamina_relief_fraction"])
    c["max_per_round"] = int(kd["max_per_round"])
    c["max_per_bout"] = int(kd["max_per_bout"])
    c["baseline"] = q(pm["undamaged_baseline"])
    c["caught"] = q(pm["caught_committed_multiplier"])
    c["balanced"] = q(pm["balanced_multiplier"])
    c["open_lane"] = q(pm["unguarded_lane_bonus"])
    c["solid_force"] = q(0.75)          # retained: the pressure term is per-class below
    # ---- contact quality, which is what unblocks this phase --------------
    # The four bands and the alignment thresholds that dispatch between them.
    col = json.loads(io.open(os.path.join(REPO, CANON["collision"]), "rb").read())
    bands = sorted(col["quality_bands"], key=lambda b: b["min_alignment"])
    c["bands"] = [(b["class"], q(b["min_alignment"]), q(b["delivered_force_fraction"]))
                  for b in bands]
    c["band_thresholds"] = [t for _, t, _ in c["bands"][1:]]   # 0.35, 0.6, 0.85
    pm_ = json.loads(io.open(os.path.join(REPO, CANON["punch"]), "rb").read())
    sg = pm_["stamina_gate"]
    c["align_penalty_max"] = q(sg["low_stamina_alignment_penalty_max"])
    c["low_frac"] = q(st["low_threshold_fraction"])
    c["exh_frac"] = q(st["exhausted_threshold_fraction"])
    # Knockdown force is graded too: canon's pressure formula weights solid at
    # 0.75 and clean at 1.0 and does not fire below solid at all.
    c["kd_force"] = {"solid": q(0.75), "clean": q(1.0)}
    c["between_stam"] = q(st["between_rounds_recovery_fraction"])
    c["region_recovery"] = {d["region"]: q(d["recovers_between_rounds"])
                            for d in cm["damage_regions"]}
    c["kd_regions"] = ("jaw_chin", "head")

    errs = list(c["canon_errors"])
    if c["max_per_round"] > c["max_per_bout"]:
        errs.append("the per-round knockdown limit exceeds the per-bout limit, so "
                    "the round rule could never fire")
    if not kd.get("decision_path_must_survive", False):
        errs.append("canon no longer requires the decision path to survive; this "
                    "contract is written on the assumption that it does")
    if kd.get("flat_random_roll_per_punch"):
        errs.append("canon now permits a flat per-punch knockout roll, which "
                    "Rule 14 forbids and this contract cannot express")
    c["canon_errors"] = errs
    return c


def coverage(c: dict, posture: str, incoming: str, vacated, gmult: int) -> int:
    """Per-hand guard coverage - Phase P's rule, and the whole difference from
    the flat model that held this phase.

        before:  extent x gmult x 0.6   (both lanes, always, when committed)
        now:     extent x gmult x 0.6   ONLY in the lane the hand left

    `vacated` is the height class of the punch the DEFENDER threw and is still
    inside; None when he is free. It lives here rather than in
    analyze_core_hands so the dependency runs one way: the Phase P module reads
    this contract, not the reverse.
    """
    e = c["posture"][posture]["ext"].get(incoming, 0)
    e = (e * gmult) // 10000
    if vacated is not None and vacated == incoming:
        e = (e * c["cd_mult"]) // 10000
    return e


def grade(c: dict, align: int) -> tuple:
    """alignment -> (class, delivered_force_fraction). collision_model's own
    four bands and their thresholds; nothing invented."""
    n = sum(1 for t in c["band_thresholds"] if align >= t)
    return c["bands"][n][0], c["bands"][n][2]


def alignment(c: dict, x: int, stamina: int) -> int:
    """Contact quality, ported from the reference simulator rather than invented.

    Two things are worth stating plainly. First, this is where the fight's one
    genuine die sits: canon's `resolve()` draws alignment at random, and Rule 14
    permits it - what Rule 14 forbids is a random KNOCKOUT roll attached to a
    punch, not stochastic contact quality feeding a deterministic threshold.
    Second, in this core the draw is the ONLY random term in the contact
    pipeline: the reference sim also rolls for sweep, evasion and guard, all
    three of which are geometry here. That is a strictly stronger determinism
    story, and it is worth keeping when the rest of the pipeline ports.

    Exhaustion lands worse (punch_model.stamina_gate): the penalty is subtracted
    before the bands read it, so a tired fighter grades lower without any punch
    being refused.
    """
    align = x % 10001
    frac = (stamina * 10000) // c["st_max"]
    if frac < c["low_frac"]:
        t = 10000 if frac <= c["exh_frac"] else \
            ((c["low_frac"] - frac) * 10000) // (c["low_frac"] - c["exh_frac"])
        align = max(0, align - (c["align_penalty_max"] * t) // 10000)
    return align


def pressure(c: dict, mv: dict, cond: dict, stamina: int, committed: bool,
             extent: int, kd_force: int) -> int:
    """Rule 14 in fixed point. Every term is canon; none of them is a die."""
    force = (kd_force * mv["impact"]) // 10000
    # jaw 0.6 / head 0.4, as a fraction of capacity. One expression, fixed order
    # of operations, so the C++ cannot round it differently.
    accumulated = ((cond["jaw_chin"] * 6000 + cond["head"] * 4000) // 10000) \
        * 10000 // c["cap"]["head"]
    stamina_frac = (stamina * 10000) // c["st_max"]
    balance = c["caught"] if committed else c["balanced"]
    guard = 10000 + (c["open_lane"] * (10000 - max(0, min(10000, extent)))) // 10000
    p = (force * (c["baseline"] + accumulated)) // 10000
    p = (p * (14000 - stamina_frac)) // 10000
    p = (p * balance) // 10000
    p = (p * guard) // 10000
    return p
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:40 UTC | continued ]


def expected_stream(seed: int, rounds: int = 3, with_floats: bool = True) -> str:
    c = canon_pack()
    lines = ["H|phase=O"]
    lines += ["H|canon_%s=%s" % (k, c["sha"][k]) for k in CANON_ORDER]
    lines += ["H|seed=%d" % seed, "H|rounds=%d" % rounds,
              "H|round_ticks=%d" % c["round_ticks"],
              "H|break_ticks=%d" % c["break_ticks"],
              "H|interval=%d" % c["interval"], "H|graded=%s" % GRADED]

    pos = [c["axis"] // 2 - 4500, c["axis"] // 2 + 4500]
    st = [c["st_max"], c["st_max"]]
    cond = [{r: 0 for r in REGIONS}, {r: 0 for r in REGIONS}]
    # Phase P, folded in: the lane each fighter's own punch took his hand out of.
    # None when he is free. Phase O is HELD rather than sealed - it has no
    # recorded hash - so the per-hand rule lands in its contract as the fix that
    # unblocks it, not as an edit to a proven phase.
    vacated = [None, None]
    committed = [0, 0]
    punch = [None, None]
    posture = ["high_guard", "high_guard"]
    slip_until, slip_from = [0, 0], [10 ** 9, 10 ** 9]
    band, x = 2, seed % LCG_M
    rows = []
    counts = {k: 0 for k in ("punches", "blocked", "landed", "whiffed", "dodged",
                             "steps", "switches", "slips", "held", "idles")}
    transitions = damage_total = opened = 0
    kd_total = [0, 0]           # knockdowns suffered, whole bout
    kd_round = [0, 0]
    cards = [0, 0]
    round_landed = [0, 0]
    stopped, stop_reason, stop_loser = False, "-", -1
    rounds_done = 0
    T = 0

    for rnd in range(1, rounds + 1):
        kd_round = [0, 0]
        round_landed = [0, 0]
        round_end = T + c["round_ticks"]
        while T < round_end and not stopped:
            T += 1
            for i in (0, 1):
                if stopped:
                    break
                if punch[i] is not None:
                    mid, t0 = punch[i]
                    mv = c["moves"][mid]
                    k = T - t0
                    if mv["startup"] < k <= mv["startup"] + mv["active"]:
                        tip_ext = N._ext(c, mid, k)
                        opp = 1 - i
                        if i == 0:
                            tip = pos[0] + tip_ext
                            surface = pos[1] - c["half_depth"]
                            plane = surface - c["plane_off"]
                            ap, asf = tip >= plane, tip >= surface
                        else:
                            tip = pos[1] - tip_ext
                            surface = pos[0] + c["half_depth"]
                            plane = surface + c["plane_off"]
                            ap, asf = tip <= plane, tip <= surface
                        d_comm = committed[opp] > 0
                        d_slip = slip_from[opp] < T <= slip_until[opp]
                        gmult = N._guard_mult(cond[opp], c)
                        # Per-hand coverage: canon's committed multiplier applies
                        # ONLY to the lane the defender's own hand vacated. The
                        # lane his free hand still holds keeps its full extent.
                        vac = vacated[opp] if d_comm else None
                        dext = coverage(c, posture[opp], mv["height"], vac, gmult)
                        fresh = coverage(c, posture[opp], mv["height"], vac, 10000)
                        dflags = (("c" if d_comm else "") + ("s" if d_slip else "")
                                  + GCHAR[posture[opp]])
                        result = region = None
                        force = 0
                        if (ap or asf) and d_slip and mv["height"] == "high":
                            result, region = "dodged", "-"
                        elif ap and dext >= c["thr"]:
                            result, region = "blocked", "-"
                            absorbed = (mv["impact"] * c["arm_frac"]) // 10000
                            for arm in ("arm_left", "arm_right"):
                                cond[opp][arm] = min(c["cap"][arm],
                                                     cond[opp][arm] + absorbed)
                        elif asf:
                            # Contact quality. The LCG advances here, once per
                            # landing - the only die in the pipeline.
                            x = (LCG_A * x + LCG_C) % LCG_M
                            align = alignment(c, x, st[i])
                            cls, frac = grade(c, align)
                            result, region = "landed", mv["region"]
                            force = (frac * mv["impact"]) // 10000
                            cond[opp][region] = min(c["cap"][region],
                                                    cond[opp][region] + force * 6)
                            damage_total += force * 6
                            round_landed[i] += 1
                            if fresh >= c["thr"] and dext < c["thr"]:
                                opened += 1
                        elif k == mv["startup"] + mv["active"]:
                            result, region = "whiffed", "-"
                        if result:
                            counts[result] += 1
                            rows.append("P|%d|%d|%s|%s|%s|%d|%d|%d|%d|%s|%d|%d|%s"
                                        % (T, i, mid, result, region, k, tip, plane,
                                           surface, dflags, force, dext,
                                           cls if result == "landed" else "-"))
                            punch[i] = None
                            # ---- the knockdown, decided from state alone ----
                            # Canon's pressure formula grades only solid and clean;
                            # a brushed or grazed shot accumulates and does not drop
                            # anybody, which is the whole point of the bands.
                            if result == "landed" and region in c["kd_regions"] \
                                    and cls in c["kd_force"]:
                                pr = pressure(c, mv, cond[opp], st[opp], d_comm, dext,
                                              c["kd_force"][cls])
                                if pr >= c["kd_threshold"]:
                                    kd_total[opp] += 1
                                    kd_round[opp] += 1
                                    committed[opp] = c["count_ticks"]
                                    acc = ((cond[opp]["jaw_chin"] * 6000
                                            + cond[opp]["head"] * 4000) // 10000) \
                                        * 10000 // c["cap"]["head"]
                                    rows.append(
                                        "K|%d|%d|%s|%d|%d|%d|%d|%d|%d|%d"
                                        % (T, opp, mid, pr, c["kd_threshold"], acc,
                                           (st[opp] * 10000) // c["st_max"],
                                           c["caught"] if d_comm else c["balanced"],
                                           10000 + (c["open_lane"]
                                                    * (10000 - max(0, min(10000, dext))))
                                           // 10000,
                                           kd_total[opp]))
                                    # rising: partial relief, never a fresh fighter
                                    for r in c["kd_regions"]:
                                        cond[opp][r] -= (cond[opp][r]
                                                         * c["cond_relief"]) // 10000
                                    st[opp] += ((c["st_max"] - st[opp])
                                                * c["stam_relief"]) // 10000
                                    if kd_round[opp] >= c["max_per_round"]:
                                        stopped, stop_reason = True, "three_knockdown_rule"
                                        stop_loser = opp
                                    elif kd_total[opp] >= c["max_per_bout"]:
                                        stopped, stop_reason = True, "knockdown_limit"
                                        stop_loser = opp
                    elif k > mv["startup"] + mv["active"]:
                        punch[i] = None
                if committed[i] > 0:
                    committed[i] -= 1
                    if committed[i] == 0:
                        vacated[i] = None       # the hand comes home
                    held = True
                else:
                    st[i] = min(c["st_max"],
                                st[i] + (c["regen"] * N._regen_mult(cond[i], c)) // 10000)
                    st[i] = max(0, st[i] - c["posture"][posture[i]]["hold"])
                    held = False
                if T % c["interval"] != 0:
                    continue
                rows.append("C|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d"
                            % (T, i, cond[i]["head"], cond[i]["jaw_chin"],
                               cond[i]["torso_upper"], cond[i]["torso_lower"],
                               cond[i]["arm_left"], cond[i]["arm_right"],
                               N._regen_mult(cond[i], c), N._guard_mult(cond[i], c)))
                g = "%s|%s" % (GCHAR[posture[0]], GCHAR[posture[1]])
                if held or committed[i] > 0:
                    counts["held"] += 1
                    rows.append("D|%d|%d|held|0|%d|%d|%d|%d|%d|%d|%s|-"
                                % (T, i, pos[0], pos[1], pos[1] - pos[0], band,
                                   st[0], st[1], g))
                    continue
                x = (LCG_A * x + LCG_C) % LCG_M
                action = ACTIONS[x % 11]
                flags = ""
                if action == "idle":
                    counts["idles"] += 1
                elif action == "switch_guard":
                    posture[i] = "tight_elbow" if posture[i] == "high_guard" \
                        else "high_guard"
                    committed[i] = c["interval"]
                    counts["switches"] += 1
                    g = "%s|%s" % (GCHAR[posture[0]], GCHAR[posture[1]])
                elif action == "slip_lead":
                    st[i] = max(0, st[i] - c["slip_cost"])
                    committed[i] = c["slip_frames"]
                    slip_from[i] = T + c["slip_startup"]
                    slip_until[i] = T + c["slip_startup"] + c["slip_active"]
                    counts["slips"] += 1
                elif action in PUNCHES:
                    mv = c["moves"][action]
                    st[i] = max(0, st[i] - mv["cost"])
                    committed[i] = mv["frames"]
                    punch[i] = (action, T)
                    vacated[i] = mv["height"]   # the hand that left, and where
                    counts["punches"] += 1
                else:
                    mv = c["moves"][action]
                    st[i] = max(0, st[i] - mv["cost"])
                    committed[i] = mv["frames"]
                    counts["steps"] += 1
                    mul = {"step_in": c["dir"]["advance"],
                           "step_out": c["dir"]["retreat"],
                           "step_lateral": c["dir"]["lateral"]}[action]
                    mul = (mul * c["posture"][posture[i]]["mobility"]) // 10000
                    if st[i] < c["exhausted_q"]:
                        mul = (mul * c["dir"]["exhausted"]) // 10000
                        flags += "e"
                    if action != "step_lateral":
                        toward = 1 if i == 0 else -1
                        sign = toward if action == "step_in" else -toward
                        on_ropes = min(pos[i], c["axis"] - pos[i]) <= c["ropes"]
                        if on_ropes and action == "step_out":
                            mul = (mul * c["rope_retreat"]) // 10000
                            flags += "r"
                        mag = (c["stride"] * mul) // 10000
                        pos[i] = min(max(pos[i] + sign * mag, 0), c["axis"])
                        if pos[1] - pos[0] < c["min_sep"]:
                            if i == 0:
                                pos[0] = pos[1] - c["min_sep"]
                            else:
                                pos[1] = pos[0] + c["min_sep"]
                            pos[0] = max(0, pos[0])
                            pos[1] = min(c["axis"], pos[1])
                            flags += "m"
                        sep = pos[1] - pos[0]
                        lo = c["bmin"][band] - c["hyst"]
                        hi = c["bmax"][band] + c["hyst"]
                        nxt = band + (1 if sep > hi else 0) - (1 if sep < lo else 0)
                        nxt = max(0, min(len(c["bmin"]) - 1, nxt))
                        if nxt != band:
                            transitions += 1
                        band = nxt
                rows.append("D|%d|%d|%s|%d|%d|%d|%d|%d|%d|%d|%s|%s"
                            % (T, i, action, x, pos[0], pos[1], pos[1] - pos[0],
                               band, st[0], st[1], g, flags or "-"))

        rounds_done += 1
        # ---- the card, sealed: computed now, disclosed only in the trailer ----
        win = None
        if round_landed[0] != round_landed[1]:
            win = 0 if round_landed[0] > round_landed[1] else 1
        for n in (0, 1):
            base = ROUND_WIN if (win is None or n == win) else ROUND_LOSE
            cards[n] += base - kd_round[n]
            rows.append("R|%d|%d|%d|%d|%d|%d|%d"
                        % (T, rnd, n, kd_round[n], st[n], cond[n]["head"],
                           cond[n]["jaw_chin"]))
        if stopped or rnd == rounds:
            break
        # ---- the corner: partial recovery, never a fresh fighter ----
        T += c["break_ticks"]
        for n in (0, 1):
            st[n] += ((c["st_max"] - st[n]) * c["between_stam"]) // 10000
            for r in REGIONS:
                cond[n][r] -= (cond[n][r] * c["region_recovery"][r]) // 10000
        committed = [0, 0]
        punch = [None, None]

    h = fnv1a64("".join(l + "\n" for l in rows).encode("utf-8"))
    lines += rows
    if with_floats:
        lines += N.float_probe(c)
    if stopped:
        verdict = "stoppage"
        winner = "b" if stop_loser == 0 else "a"
        method = stop_reason
    elif cards[0] != cards[1]:
        verdict = "decision"
        winner = "a" if cards[0] > cards[1] else "b"
        method = "unanimous"
    else:
        verdict, winner, method = "decision", "draw", "draw"
    lines.append("V|%s|%s|%s|%d|%d|%d|%d|%d"
                 % (verdict, winner, method, rounds_done, cards[0], cards[1],
                    kd_total[0], kd_total[1]))
    lines.append(
        "S|rows=%d|punches=%d|blocked=%d|landed=%d|whiffed=%d|dodged=%d|steps=%d"
        "|switches=%d|slips=%d|held=%d|idles=%d|transitions=%d|damage=%d|opened=%d"
        "|knockdowns=%d|rounds=%d|stopped=%s|fnv1a64=%016x"
        % (len(rows), counts["punches"], counts["blocked"], counts["landed"],
           counts["whiffed"], counts["dodged"], counts["steps"], counts["switches"],
           counts["slips"], counts["held"], counts["idles"], transitions,
           damage_total, opened, kd_total[0] + kd_total[1], rounds_done,
           "1" if stopped else "0", h))
    return "\n".join(lines) + "\n"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:40 UTC | continued ]


def analyse(path: str) -> dict:
    rep = {"file": os.path.basename(path), "errors": [], "notes": []}
    c = canon_pack()
    rep["errors"].extend(c["canon_errors"])
    lines = [l for l in io.open(path, encoding="utf-8").read().splitlines() if l]
    heads = {l.split("=", 1)[0][2:]: l.split("=", 1)[1]
             for l in lines if l.startswith("H|") and "=" in l}
    for need in ("seed", "rounds"):
        if need not in heads:
            rep["errors"].append("missing header H|%s=" % need)
    if rep["errors"]:
        rep["ok"] = False
        return rep
    seed, rounds = int(heads["seed"]), int(heads["rounds"])
    rep["seed"], rep["rounds_requested"] = seed, rounds
    for k in CANON_ORDER:
        if heads.get("canon_" + k) != c["sha"][k]:
            rep["errors"].append("canon_%s hash does not match the local file" % k)

    got = "\n".join(l for l in lines if not l.startswith("F|")) + "\n"
    want = expected_stream(seed, rounds, with_floats=False)
    if got != want:
        for n, (g, w) in enumerate(zip(got.splitlines(), want.splitlines()), 1):
            if g != w:
                rep["errors"].append("core stream diverges at line %d: got %r, "
                                     "expected %r" % (n, g, w))
                break
        else:
            rep["errors"].append("core stream length differs from recomputation")

    got_f = [l for l in lines if l.startswith("F|")]
    if got_f and got_f == N.float_probe(c):
        rep["notes"].append("float probe: all %d checkpoints BIT-IDENTICAL to "
                            "CPython doubles" % len(got_f))
    elif got_f:
        rep["notes"].append("float probe: DIVERGES - a finding, not a failure")

    # ---- independent properties ------------------------------------------
    krow = [l.split("|") for l in lines if l.startswith("K|")]
    vrow = [l.split("|") for l in lines if l.startswith("V|")]
    rrow = [l.split("|") for l in lines if l.startswith("R|")]
    prow = [l.split("|") for l in lines if l.startswith("P|")]

    for r in krow:
        pr, thr = int(r[4]), int(r[5])
        if pr < thr:
            rep["errors"].append("a knockdown fired below the canon threshold "
                                 "(%d < %d) - Rule 14's line is not a suggestion"
                                 % (pr, thr))
        if thr != c["kd_threshold"]:
            rep["errors"].append("a knockdown used a threshold that is not canon's")
        mid = r[3]
        if c["moves"].get(mid, {}).get("region") not in c["kd_regions"]:
            rep["errors"].append("%s produced a knockdown from a region canon does "
                                 "not make knockdown-relevant" % mid)
    # Every landing to a knockdown region that DID cross the line must have one.
    if len(prow) > 20 and not krow:
        rep["notes"].append("no knockdown occurred in this run")

    if len(vrow) != 1:
        rep["errors"].append("%d V verdict lines (want exactly 1)" % len(vrow))
    else:
        v = vrow[0]
        idx = lines.index("|".join(v))
        # Rule 3: the cards are sealed until the bout ends. Nothing before the
        # verdict line may disclose a card total.
        for l in lines[:idx]:
            if l.startswith(("D|", "P|", "C|", "K|", "R|")) and "card" in l:
                rep["errors"].append("a card value appears before the verdict - "
                                     "the score firewall is open")
        rep["verdict"] = v[1]
        rep["winner"] = v[2]
        rep["method"] = v[3]
        rep["cards"] = [int(v[5]), int(v[6])]
        if v[1] == "decision" and v[2] != "draw":
            hi = 0 if int(v[5]) > int(v[6]) else 1
            if (v[2] == "a") != (hi == 0):
                rep["errors"].append("the decision does not match the cards")
        if v[1] == "stoppage" and int(v[4]) < 1:
            rep["errors"].append("a stoppage is recorded before any round completed")

    if rrow:
        per_round = {}
        for r in rrow:
            per_round.setdefault(int(r[2]), []).append(int(r[3]))
        for rnd, kds in per_round.items():
            for k in kds:
                if k > c["max_per_round"]:
                    rep["errors"].append("round %d records more knockdowns than "
                                         "canon's per-round maximum" % rnd)

    slines = [l for l in lines if l.startswith("S|")]
    if len(slines) != 1:
        rep["errors"].append("%d S trailer lines (want exactly 1)" % len(slines))
    else:
        trail = dict(kv.split("=") for kv in slines[0][2:].split("|"))
        blob = "".join(l + "\n" for l in lines
                       if l[:2] in ("D|", "P|", "C|", "K|", "R|")).encode("utf-8")
        if int(trail["fnv1a64"], 16) != fnv1a64(blob):
            rep["errors"].append("S trailer fnv1a64 does not hash the D/P/C/K/R lines")
        if int(trail["knockdowns"]) != len(krow):
            rep["errors"].append("the trailer's knockdown count disagrees with the "
                                 "K rows")
        if int(trail["knockdowns"]) > 2 * c["max_per_bout"]:
            rep["errors"].append("more knockdowns than both fighters' bout limits "
                                 "allow")
        rep["knockdowns"] = int(trail["knockdowns"])
        rep["rounds_completed"] = int(trail["rounds"])
        rep["stopped"] = trail["stopped"] == "1"
    rep["punch_rows"] = len(prow)
    rep["ok"] = not rep["errors"]
    return rep


def sweep(seeds) -> dict:
    """How often each result path is reached. canon's knockdown block declares
    `decision_path_must_survive: true`, and one stream cannot test that - it is a
    property of the distribution, so it needs a sweep."""
    out = {"stoppage": 0, "decision": 0, "draw": 0, "stopped_in_round_1": 0,
           "seeds": 0}
    for seed in seeds:
        s = expected_stream(seed, 3, with_floats=False)
        v = [l for l in s.splitlines() if l.startswith("V|")][0].split("|")
        t = dict(kv.split("=") for kv in
                 [l for l in s.splitlines() if l.startswith("S|")][0][2:].split("|"))
        out["seeds"] += 1
        if v[1] == "stoppage":
            out["stoppage"] += 1
            if int(t["rounds"]) == 1:
                out["stopped_in_round_1"] += 1
        elif v[2] == "draw":
            out["draw"] += 1
        else:
            out["decision"] += 1
    return out


if __name__ == "__main__":
    all_ok = True
    for p in sys.argv[1:]:
        r = analyse(p)
        all_ok &= r["ok"]
        print(json.dumps(r, indent=1, sort_keys=True))
    sys.exit(0 if all_ok else 1)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:40 UTC | END ]
