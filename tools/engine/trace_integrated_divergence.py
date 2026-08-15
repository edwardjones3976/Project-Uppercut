# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 10:05 UTC | START ]
"""Where the C++ round and the Python round stop being the same fight.

Decision 0040's calibration prerequisites are ordered, and #2 is this: trace the
FIRST tick where the two runtimes make different decisions from the same seed.
Not the totals. The decision quotes `kd=0-0` against `kd=17` and `kd=21`, and
this repository has already lost a day to reasoning from totals
(`docs/development-log/2026-08-05-i-measured-the-wrong-artifact.md`).

WHAT THIS COMPARES, AND WHY IT CANNOT BE A BYTE DIFF. The two runtimes do not
share a stream grammar. C++ emits D/A/P/K/N/V/S; Python emits D/P/C/W/N/K/U/F/
B/X/R/E, with different field orders and a richer vocabulary. There is no
version of "diff the streams" that means anything here.

What they DO share is the decision: both emit a per-fighter row carrying a
tactic, an execution and a reason code, drawn from vocabularies that use the
same spellings. So the comparison is the projection

    (tick, participant) -> (tactic, execution, reason)

and nothing else. Positions, stamina, damage and windows are deliberately out of
scope: they are expressed differently on the two sides, and a comparison that
had to translate them would be making claims of its own.

WHAT THIS DOES NOT DO. It does not say which side is right. Decision 0040 R2
settles that in advance - C++ is the authority and Python converges to it - so
this file reports the disagreement and stops. It also does not tune anything;
R5 freezes `pressure_threshold` at 0.57 precisely because the two runtimes do
not yet agree on what they are measuring.

    python -m tools.engine.trace_integrated_divergence            # pinned run
    python -m tools.engine.trace_integrated_divergence --seed 777 --ticks 10800

Reads the C++ side from the committed pin, so it needs no engine.
"""
import argparse
import collections
import io
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.engine import prove_integrated_arena as PROVE  # noqa: E402
from tools.uppercut_integrated.bout import IntegratedBout  # noqa: E402

Decision = collections.namedtuple("Decision", "tick who tactic execution reason")


def cpp_decisions(path):
    """C++ D row: D|tick|participant|tactic|execution|reason."""
    out = []
    for line in io.open(path, "r", encoding="utf-8", newline="").read().splitlines():
        if not line.startswith("D|"):
            continue
        f = line.split("|")
        if len(f) < 6:
            continue
        out.append(Decision(int(f[1]), f[2], f[3], f[4] or "-", f[5]))
    return out


def python_decisions(seed, ticks):
    """Python D row: D|tick|who|strategic|tactical|execution|reason|initiative.

    The strategic layer has no C++ counterpart - the thin policy has two layers
    where Python has three - so it is read and dropped here rather than compared
    against nothing.
    """
    bout = IntegratedBout(seed=seed, rounds=1, round_ticks=ticks,
                          fighter_cards="default_pair")
    bout.run(ticks)
    out = []
    for line in bout.rows:
        if not line.startswith("D|"):
            continue
        f = line.split("|")
        if len(f) < 7:
            continue
        out.append(Decision(int(f[1]), f[2], f[4], f[5] or "-", f[6]))
    return out, bout


def cadence(decisions):
    ticks = sorted(set(d.tick for d in decisions))
    per_who = collections.Counter(d.who for d in decisions)
    return {
        "rows": len(decisions),
        "first_tick": ticks[0] if ticks else None,
        "distinct_ticks": len(ticks),
        "per_participant": dict(per_who),
    }


def vocabulary(decisions):
    return {
        "tactics": collections.Counter(d.tactic for d in decisions),
        "reasons": collections.Counter(d.reason for d in decisions),
        "executions": collections.Counter(d.execution for d in decisions),
    }


def first_divergence(cpp, py):
    """The first (tick, participant) both sides decided, where they differ.

    Aligning on (tick, participant) rather than on row order is the only honest
    choice when the two sides decide on different clocks: row N on one side is
    not row N on the other, and pairing them by index would manufacture a
    divergence at row 1 that says nothing.
    """
    py_by_key = {}
    for d in py:
        py_by_key.setdefault((d.tick, d.who), d)

    pairs = [(d, py_by_key[(d.tick, d.who)])
             for d in sorted(cpp, key=lambda x: (x.tick, x.who))
             if (d.tick, d.who) in py_by_key]
    # The whole aligned set is scored before the first mismatch is reported, so
    # "compared" cannot be read as "this is all the alignment there is". Two
    # runtimes that only ever meet once would otherwise look like two runtimes
    # that agreed until they didn't.
    identical = sum(1 for a, b in pairs
                    if (a.tactic, a.execution, a.reason)
                    == (b.tactic, b.execution, b.reason))
    found = {"tick": None, "alignable": len(pairs), "identical": identical,
             "cpp_rows": len(cpp), "py_rows": len(py)}
    for i, (a, b) in enumerate(pairs):
        if (a.tactic, a.execution, a.reason) != (b.tactic, b.execution, b.reason):
            found.update({"tick": a.tick, "who": a.who, "cpp": a, "py": b,
                          "agreed_before": i})
            break
    return found


def report(seed, ticks, pin_path):
    cpp = cpp_decisions(pin_path)
    py, bout = python_decisions(seed, ticks)

    out = []
    add = out.append
    add("== the same seed, two runtimes ==")
    add("   seed %d, %d ticks, cards test_pressure_power vs test_range_timing" % (seed, ticks))
    add("   C++    %s" % os.path.relpath(pin_path, REPO))
    add("   Python tools.uppercut_integrated.bout.IntegratedBout (reference, Decision 0040 R2)")

    cc, pc = cadence(cpp), cadence(py)
    add("")
    add("== cadence: how often anyone decides anything ==")
    add("   %-8s %6s rows over %5s distinct ticks, first at tick %s"
        % ("C++", cc["rows"], cc["distinct_ticks"], cc["first_tick"]))
    add("   %-8s %6s rows over %5s distinct ticks, first at tick %s"
        % ("Python", pc["rows"], pc["distinct_ticks"], pc["first_tick"]))
    if cc["rows"] and pc["rows"]:
        add("   Python decides %.1fx as often." % (float(pc["rows"]) / cc["rows"]))

    cv, pv = vocabulary(cpp), vocabulary(py)
    add("")
    add("== vocabulary: what each side is able to say ==")
    for name, key in (("tactic", "tactics"), ("reason", "reasons")):
        c_set, p_set = set(cv[key]), set(pv[key])
        add("   %ss used by C++    (%d): %s"
            % (name, len(c_set), ", ".join(sorted(c_set))))
        add("   %ss used by Python (%d): %s"
            % (name, len(p_set), ", ".join(sorted(p_set))))
        only_py = sorted(p_set - c_set)
        only_cpp = sorted(c_set - p_set)
        if only_py:
            add("   Python says and C++ never does: %s" % ", ".join(only_py))
        if only_cpp:
            add("   C++ says and Python never does: %s" % ", ".join(only_cpp))
        add("")

    div = first_divergence(cpp, py)
    add("== the first divergence ==")
    add("   Of %d C++ decisions and %d Python decisions, %d land on the same"
        % (div["cpp_rows"], div["py_rows"], div["alignable"]))
    add("   (tick, fighter) and can be compared at all. %d of those are identical."
        % div["identical"])
    if div["alignable"] == 0:
        add("")
        add("   THE TWO RUNTIMES NEVER DECIDE ON THE SAME TICK FOR THE SAME")
        add("   FIGHTER, so there is no aligned pair and no tick-by-tick")
        add("   divergence to find. The disagreement is the clock itself, and")
        add("   it sits upstream of anything a tick diff could report.")
    elif div["tick"] is None:
        add("   No divergence in the aligned set.")
    else:
        add("")
        add("   %d aligned decisions agree, then at tick %d:"
            % (div["agreed_before"], div["tick"]))
        add("      fighter  %s" % div["who"])
        add("      C++      %-14s %-12s %s"
            % (div["cpp"].tactic, div["cpp"].execution, div["cpp"].reason))
        add("      Python   %-14s %-12s %s"
            % (div["py"].tactic, div["py"].execution, div["py"].reason))

    add("")
    add("== what each fight became ==")
    cpp_landed = sum(1 for ln in io.open(pin_path, "r", encoding="utf-8",
                                         newline="").read().splitlines()
                     if ln.startswith("P|") and "|landed" in ln)
    cpp_thrown = sum(1 for ln in io.open(pin_path, "r", encoding="utf-8",
                                         newline="").read().splitlines()
                     if ln.startswith("P|"))
    add("   C++     %d punches resolved, %d landed, %d knockdown rows"
        % (cpp_thrown, cpp_landed,
           sum(1 for ln in io.open(pin_path, "r", encoding="utf-8",
                                   newline="").read().splitlines()
               if ln.startswith("K|"))))
    py_p = [r for r in bout.rows if r.startswith("P|")]
    py_kd = [r for r in bout.rows if r.startswith("N|") and "|down|" in r]
    add("   Python  %d punch rows, %d knockdowns" % (len(py_p), len(py_kd)))
    add("")
    add("   Decision 0040 R2: Python converges to C++, not the reverse. This")
    add("   file reports the disagreement and makes no claim about which fight")
    add("   is the better one - R3 holds that neither is authentic yet.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--ticks", type=int, default=10800)
    args = ap.parse_args(argv)
    pin = PROVE.golden_path(args.seed, args.ticks)
    if not os.path.exists(pin):
        raise SystemExit(
            "no pinned C++ stream for seed %d over %d ticks (%s).\n"
            "Record one with: python -m tools.engine.prove_integrated_arena --write"
            % (args.seed, args.ticks, os.path.basename(pin)))
    print(report(args.seed, args.ticks, pin))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 10:05 UTC | END ]
