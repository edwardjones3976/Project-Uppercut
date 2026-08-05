# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 12:10 UTC | START ]
"""Phase S measured - canon's difficulty tiers, executed instead of read.

The core has never had a policy. It draws uniformly from a pool that contains
`idle` once, so it acts on nearly every tick it is free: ~180 stamina-charging
actions per round against an economy that refills 10.6. Every stamina finding
after Phase R was measuring that, not a stamina model.

Canon authors the policy in full. This executes it and adds nothing:

    decision_interval_ticks 4   how often the policy runs
    floor_ticks             6   the fastest any tier may respond, ever
    aggression_bias             the share of decisions that throw
    error_rate                  the share that choose the wrong thing
    reaction_ticks              how long a tier needs to respond to what it saw

THE FOUR RULES OF THIS POLICY, each a canon line rather than a design choice:

  1. RANGE FIRST. Throw only what the band permits; if the band permits nothing,
     walk toward one that does. (Phase Q; the reference logs zero out-of-range
     attempts for exactly this reason.)
  2. REACT ONLY IF YOU COULD HAVE. A slip in response to a punch requires that
     the punch has been visible for at least max(floor, tier reaction). A jab
     has 4 startup frames against a 6-tick floor, so NO tier can react to a jab
     - it is anticipated or eaten.
  3. AGGRESSION GATES OFFENCE. A decision that is not offensive is footwork, a
     guard change, an anticipatory slip, or nothing at all.
  4. ERROR CHANGES THE CHOICE AND NOTHING ELSE. Rule 4 forbids difficulty from
     touching damage, stamina, contact classification or anything else; an error
     may only be a different action.

AND `idle` IS A REAL ANSWER. That is the whole difference from the uniform coin.
A fighter who is not throwing, not moving and not slipping is resting, and
resting is the only thing in this model that refills the pool. The coin picked
`idle` one time in eleven; a novice at 0.35 aggression picks something other than
a punch two decisions in three, and most of those are not actions at all.

Run: python -m tools.engine.experiment_tiered_policy
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_evade as E  # noqa: E402
import analyze_core_policy as P  # noqa: E402
import analyze_core_range as Q  # noqa: E402
import analyze_core_round as O  # noqa: E402
import experiment_range_model as R  # noqa: E402

SEEDS = R.SEEDS
REF = {"thrown": 41.4, "connect": 42.4, "kd_per_min": 0.38, "drain": 11.1,
       "cards": 20, "seeds": 24}


def tiered(pc: dict, rc: dict, ec: dict, tier: str, obs: list):
    """Canon's tier, as a chooser. Nothing here is invented; see the four rules
    in the module docstring, each of which is a canon line."""
    order = [k for k, _, _ in rc["bands"]]
    punch_bands = sorted({order.index(rc["move_band"][a]) for a in O.PUNCHES
                          if a in rc["move_band"]})
    passive = ("idle", "step_in", "step_out", "step_lateral", "switch_guard")

    def choose(x: int) -> str:
        band = obs[0]
        legal = [a for a in O.PUNCHES if Q.in_band(rc, a, band)]
        slips = [k for k, v in ec["evasions"].items()
                 if v["kind"] == "active_window" and v["band"] == band] \
            if ec else []
        if not legal:
            here = order.index(band)
            return "step_out" if here < punch_bands[0] else "step_in"

        # Rule 2: a reaction the tier could not have made is not available.
        if slips and obs[1] and P.may_react(pc, tier, obs[1]):
            pick = slips[(x // 100000000) % len(slips)]
        elif P.is_offensive(pc, tier, x):
            pick = legal[(x // 100000000) % len(legal)]
        else:
            # Rule 3's other half, and the reason this is a fighter: most of
            # what a boxer does is not a punch, and some of it is nothing.
            pool = list(passive) + slips
            pick = pool[(x // 100000000) % len(pool)]

        # Rule 4: the error is a different CHOICE, never a worse outcome.
        #
        # And it swaps WITHIN THE CLASS the fighter had already chosen: an
        # intended punch becomes a different punch, an intended non-punch
        # becomes a different non-punch. The first version of this drew the
        # replacement from every action at once, and the measurement caught it
        # immediately - at the club tier's 0.22 error rate that put ~10% of ALL
        # decisions into a punch no matter what the aggression bias said, so
        # dropping aggression from 0.35 to 0.005 moved the throw rate only from
        # 218 to 148. An error that can override the fighter's own aggression is
        # not an error, it is a second aggression dial wearing the wrong name.
        if P.errs(pc, tier, x):
            same = list(legal) if pick in legal else list(passive) + slips
            same = [a for a in same if a != pick] or [pick]
            pick = same[(x // 1000000000000) % len(same)]
        return pick
    return choose


def run(tier: str, interval: int = None, aggression: int = None) -> dict:
    c = dict(O.canon_pack())
    pc = P.policy_pack()
    c["interval"] = interval or pc["interval"]
    if aggression is not None:
        pc = dict(pc)
        pc["tiers"] = {k: dict(v) for k, v in pc["tiers"].items()}
        pc["tiers"][tier]["aggression"] = aggression
    rc = Q.range_pack()
    ec = E.evade_pack()
    agg = {"thrown": 0, "landed": 0, "eligible": 0, "kd": 0, "ticks": 0,
           "cards": 0, "busy": 0, "regen": 0, "evaded": 0}
    spend = {"punch": 0, "step": 0, "evade": 0, "hold": 0}
    stops, gauges = [], {}
    for s in SEEDS:
        obs = [Q.band_at(rc, R.START_SEP), 0]
        ch = tiered(pc, rc, ec, tier, obs)
        r = R.run_range(s, c, rc, 3, ch, gate=True, footwork=True,
                        band_ref=obs, ec=ec)
        for k in ("thrown", "landed", "eligible", "evaded"):
            agg[k] += r[k]
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
    drain = ((100.0 - at[deepest]) / (deepest / 3600.0)) if deepest else None
    per = lambda v: round(v / 10000.0 / (minutes / 3.0) / 2.0, 1)  # noqa: E731
    return {"tier": tier,
            "thrown": agg["thrown"] / minutes * R.ROUND_MINUTES / 2.0,
            "connect": 100.0 * agg["landed"] / agg["thrown"] if agg["thrown"] else 0,
            "kd_per_min": agg["kd"] / minutes,
            "gap_x": conv / need if need else None,
            "cards": agg["cards"], "seeds": len(SEEDS),
            "evaded": agg["evaded"],
            "committed_pct": 100.0 * agg["busy"] / (2.0 * agg["ticks"]),
            "drain": drain,
            "stamina_at": {str(g): round(v, 1) for g, v in at.items()},
            "spend": {k: per(v) for k, v in spend.items()},
            "regen": per(agg["regen"])}


def main() -> int:
    pc = P.policy_pack()
    if pc["canon_errors"]:
        print("CANON REFUSED:")
        for e in pc["canon_errors"]:
            print("  -", e)
        return 1
    for name, fn in (("nobody can react to a jab", P.nobody_can_react_to_a_jab),
                     ("something IS reactable",
                      P.the_slowest_punch_is_readable_by_someone),
                     ("difficulty is a ladder", P.difficulty_is_a_ladder),
                     ("reaction is not the decision clock",
                      P.reaction_is_not_the_decision_clock)):
        print("  %-36s %s" % (name, "yes" if fn(pc) else "NO"))
    print()
    core = O.canon_pack()
    print("  who can react to what, from two authored numbers and a move table:")
    for m in O.PUNCHES:
        s = core["moves"][m]["startup"]
        who = [t for t in pc["order"] if P.may_react(pc, t, s)]
        print("    %-20s startup %2d   %s" % (m, s, ", ".join(who) or "NOBODY"))
    print()

    rows = {}
    print("  %-10s %8s %8s %8s %8s %7s %7s %8s"
          % ("tier", "thr/f-rd", "connect", "kd/min", "drain%/m", "gap",
             "cards", "st@3600"))
    for t in pc["order"]:
        r = run(t)
        rows[t] = r
        print("  %-10s %8.1f %7.1f%% %8.2f %8.1f %6.1fx %3d/%-2d %8s"
              % (t, r["thrown"], r["connect"], r["kd_per_min"], r["drain"],
                 r["gap_x"], r["cards"], r["seeds"],
                 r["stamina_at"].get("3600", "-")))
    print("  %-10s %8.1f %7.1f%% %8.2f %8.1f %6s %3d/%-2d"
          % ("REFERENCE", REF["thrown"], REF["connect"], REF["kd_per_min"],
             REF["drain"], "-", REF["cards"], REF["seeds"]))
    print()

    print("  WHERE THE POOL GOES NOW, per fighter per round (pool = 100)")
    print("    %-10s %8s %8s %8s %8s %8s %8s"
          % ("tier", "punch", "step", "evade", "hold", "OUT", "regen"))
    for t in pc["order"]:
        s = rows[t]["spend"]
        print("    %-10s %8.1f %8.1f %8.1f %8.1f %8.1f %8.1f"
              % (t, s["punch"], s["step"], s["evade"], s["hold"],
                 sum(s.values()), rows[t]["regen"]))
    print()
    print("  for comparison, the coin with a range model spent 231.5 and")
    print("  received 10.6 - punch 60.7, step 108.2, evade 59.9, hold 2.7.")
    print()

    # The tiers produce 5x boxing's work rate under the reading above. Canon is
    # ambiguous about which clock aggression_bias is a share OF, so both
    # readings are measured rather than argued.
    print("  READING (a): a tier DECIDES every reaction_ticks")
    print("    %-10s %8s %8s %8s" % ("tier", "interval", "thr/f-rd", "drain%/m"))
    alt = {}
    for t in pc["order"]:
        iv = pc["tiers"][t]["reaction"]
        r = run(t, interval=iv)
        alt["a:" + t] = r
        print("    %-10s %8d %8.1f %8.1f" % (t, iv, r["thrown"], r["drain"]))
    print()
    print("  and the aggression that WOULD produce a professional work rate,")
    print("  at canon's own 4-tick decision interval:")
    print("    %-10s %10s %10s %10s" % ("aggression", "thr/f-rd", "drain%/m",
                                        "cards"))
    for a in (3500, 1000, 500, 250, 100, 50):
        r = run("club", aggression=a)
        alt["agg:%d" % a] = r
        print("    %-10.4f %10.1f %10.1f %8d/%-2d"
              % (a / 10000.0, r["thrown"], r["drain"], r["cards"], r["seeds"]))
    rows.update(alt)
    print()

    print("READ THIS AS:")
    print("  The reaction table is right and it is the win here: two authored")
    print("  numbers and a move table produce a fact of real boxing - the jab")
    print("  cannot be reacted to by anybody, and only a champion answers a")
    print("  cross. Nobody wrote that. Difficulty was never inert; it simply")
    print("  had nothing to be a difficulty OF until distance and evasion")
    print("  existed.")
    print()
    print("  THE VOLUME IS STILL WRONG, and it is canon's number this time.")
    print("  Under BOTH readings of the decision clock, canon's aggression_bias")
    print("  produces 3-6x a professional work rate. The lowest authored value")
    print("  is the novice's 0.35; the sweep above shows what is actually")
    print("  needed. That is not a tuning gap I should close by picking a")
    print("  number - it is a third canon quantity that was authored against a")
    print("  decision model nobody had built yet, and it belongs beside the")
    print("  step-cost contradiction on the Director's desk.")

    p = os.path.join(O.REPO, "sandbox", "Saved", "tiered_policy.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 12:10 UTC | END ]
