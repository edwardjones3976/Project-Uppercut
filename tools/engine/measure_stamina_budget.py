# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:00 UTC | START ]
"""Where does a round's stamina actually go — the guard, or the punches?

The last measurement showed fighters are at ~30% stamina when they go down, and
that the per-tick posture hold cost is the suspect because knockdowns were flat
across a 3.3x range of work rate. This decomposes the round's stamina budget so
the Director's question — should holding a guard for three minutes empty a man? —
is answered with the actual split rather than an inference.

Pure measurement. Changes nothing, recommends nothing, invents no number. All
four quantities below are read straight from canon.

Run: python -m tools.engine.measure_stamina_budget
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402


def main() -> int:
    c = O.canon_pack()
    ticks = c["round_ticks"]
    pool = c["st_max"]
    out = {"round_ticks": ticks, "pool": pool / 10000.0}

    print("pool %.1f, round %d ticks (%.0fs at 60Hz)"
          % (pool / 10000.0, ticks, ticks / 60.0))
    print()
    print("  %-34s %10s %10s" % ("per full round, if sustained", "stamina", "x pool"))
    for pid in O.POSTURES:
        hold = c["posture"][pid]["hold"] * ticks
        print("  %-34s %10.1f %10.2f"
              % ("hold %s for the whole round" % pid, hold / 10000.0, hold / pool))
        out["hold_" + pid] = round(hold / 10000.0, 2)

    regen = c["regen"] * ticks
    print("  %-34s %10.1f %10.2f"
          % ("idle regeneration, whole round", regen / 10000.0, regen / pool))
    out["regen_full_round"] = round(regen / 10000.0, 2)

    print()
    print("  %-34s %10s" % ("punch cost", "stamina"))
    for mid in O.PUNCHES:
        print("  %-34s %10.2f" % (mid, c["moves"][mid]["cost"] / 10000.0))

    # What the observed work rate actually spends. Counts come from the contract.
    s = O.expected_stream(4242, 3, with_floats=False)
    trail = dict(kv.split("=") for kv in
                 [l for l in s.splitlines() if l.startswith("S|")][0][2:].split("|"))
    thrown = int(trail["punches"])
    spent = sum(c["moves"][l.split("|")[3]]["cost"]
                for l in s.splitlines() if l.startswith("P|"))
    hold_hg = c["posture"]["high_guard"]["hold"] * ticks
    print()
    print("  observed in the canonical round: %d punches thrown" % thrown)
    print("  punch spend (resolved punches)  : %.1f" % (spent / 10000.0))
    print("  hold spend (high_guard, a round): %.1f" % (hold_hg / 10000.0))
    if spent:
        print()
        print("  THE SPLIT: holding the guard costs %.1fx what the punching costs"
              % (hold_hg / float(spent)))
        out["hold_over_punch_ratio"] = round(hold_hg / float(spent), 2)
    out["punches_thrown"] = thrown

    p = os.path.join(O.REPO, "sandbox", "Saved", "stamina_budget.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:00 UTC | END ]
