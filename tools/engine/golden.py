# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:30 UTC | START ]
"""The golden streams: the exact bytes a C++ port has to produce.

A phase is proven here when the C++ artifact's marker stream is byte-identical
to the analyzer's. Until this file existed that target was only ever "whatever
`expected_stream` returns today" - a target that moves silently, and one that
moved silently once already: on 2026-08-04 a sealed analyzer was edited, Phase
N's recomputation went from 88af6f30 to 974c12ef, and THE WHOLE SUITE STILL
PASSED because every test regenerated from the same edited analyzer. Nothing
compared it to anything.

`test_phase_evidence_pins.py` closed that for the PROVEN phases by pinning their
hashes. This closes it differently: it writes each stream to a file, commits it,
and diffs against it. A hash tells you something moved. A golden file tells you
WHAT moved, in fight terms - which punch, at which tick, with what result.

    python -m tools.engine.golden                # check every pin
    python -m tools.engine.golden --diff         # show the drift as a fight
    python -m tools.engine.golden --write        # re-bless after a real change
    python -m tools.engine.golden --phase=Q ...  # one pin only

THE TWO PINS ARE HERE FOR DIFFERENT REASONS.

  O is HELD and has no C++ yet. Its pin WILL fail when G1, G2 or G3 is decided,
    because a step cost or an aggression bias changes the fight. That is the
    point: the ruling and the re-blessing belong in the same commit, so a canon
    decision and its consequence are one reviewable change rather than a number
    edited in one place and a stream quietly regenerated somewhere else.

  Q is PROVEN: `UppercutCoreRangeCommandlet` reproduces this contract byte for
    byte at 4242/5400, 777/5400 and 4242/900. Its pin is what makes that proof
    keep meaning something WITHOUT an engine. Proving parity needs Unreal and
    two minutes; noticing that somebody moved the contract out from under a
    proven port needs only this file and a diff. If Q's pin fails, the port is
    no longer proven - re-run `prove_core_range` before re-blessing, and if the
    change was deliberate, say so in the commit that carries it.
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_evade as R  # noqa: E402
import analyze_core_range as Q  # noqa: E402
import analyze_core_round as O  # noqa: E402

REPO = O.REPO


def _describe_o(line: str) -> str:
    """One Phase O row, in words. A diff nobody can read is a hash with extra
    steps."""
    f = line.split("|")
    k = f[0]
    if k == "P":
        return ("tick %s: fighter %s threw %s -> %s%s"
                % (f[1], f[2], f[3], f[4],
                   "" if f[5] == "-" else " on the " + f[5]))
    if k == "K":
        return ("tick %s: fighter %s KNOCKED DOWN by %s (pressure %s vs %s)"
                % (f[1], f[2], f[3], f[4], f[5]))
    if k == "D":
        return ("tick %s: fighter %s decided %s (separation %s, band %s)"
                % (f[1], f[2], f[3], f[7], f[8]))
    if k == "R":
        return "tick %s: end of round %s for fighter %s" % (f[1], f[2], f[3])
    if k == "V":
        return "VERDICT %s to %s by %s after %s round(s)" % (f[1], f[2], f[3], f[4])
    if k == "S":
        return "TRAILER " + line[2:]
    if k == "H":
        return "header " + line[2:]
    if k == "C":
        return "tick %s: fighter %s condition snapshot" % (f[1], f[2])
    return line


def _describe_q(line: str) -> str:
    """One Phase Q row, in words.

    Note that `R` means something different here than it does in Phase O - a
    band transition rather than the end of a round - which is exactly why the
    describer is per phase rather than shared.
    """
    f = line.split("|")
    k = f[0]
    if k == "X":
        return ("tick %s: fighter %s moved %s to separation %s%s"
                % (f[1], f[2], f[3], f[6],
                   " (stopped by the body clamp)" if "m" in f[8] else ""))
    if k == "R":
        return ("tick %s: fighter %s passed from %s into %s at separation %s"
                % (f[1], f[2], f[3], f[4], f[5]))
    if k == "P":
        if f[4] == "landed":
            return "tick %s: fighter %s LANDED %s from %s" % (f[1], f[2], f[3], f[9])
        if f[5] == "band":
            return ("tick %s: fighter %s threw %s from %s, the wrong band - "
                    "full arc into empty air" % (f[1], f[2], f[3], f[9]))
        return ("tick %s: fighter %s threw %s from %s and fell short (tip %s, "
                "surface %s)" % (f[1], f[2], f[3], f[9], f[7], f[8]))
    if k == "D":
        return ("tick %s: fighter %s decided %s (separation %s, band %s)"
                % (f[1], f[2], f[3], f[7], f[8]))
    if k == "V":
        return "property %s proven=%s" % (f[1], f[2])
    if k == "B":
        return "band %s: %s covers %s to %s" % (f[1], f[2], f[3], f[4])
    if k == "M":
        return "%s is a %s-band move" % (f[1], f[2])
    if k == "K":
        return "scalars " + line[2:]
    if k == "S":
        return "TRAILER " + line[2:]
    if k == "H":
        return "header " + line[2:]
    return line


def _describe_r(line: str) -> str:
    """One Phase R row, in words.

    `P` means a punch resolving here as it does in Q, but the interesting field
    is WHY: clear, vacated, counter or region. Those four words are the phase.
    """
    f = line.split("|")
    k = f[0]
    if k == "P":
        if f[5] == "vacated":
            return ("tick %s: fighter %s threw %s and found nothing there - %s "
                    "had vacated the %s" % (f[1], f[2], f[3], f[7], f[6]))
        if f[5] == "counter":
            return ("tick %s: fighter %s landed %s INTO the %s - it is authored "
                    "to beat that evasion" % (f[1], f[2], f[3], f[7]))
        if f[5] == "region":
            return ("tick %s: fighter %s landed %s on the %s; %s was active but "
                    "went somewhere else" % (f[1], f[2], f[3], f[6], f[7]))
        return ("tick %s: fighter %s landed %s on the %s, nobody evading"
                % (f[1], f[2], f[3], f[6]))
    if k == "W":
        return ("tick %s: fighter %s %s a %s"
                % (f[1], f[2], "began" if f[4] == "open" else "came out of", f[3]))
    if k == "A":
        return "tick %s: fighter %s committed to %s" % (f[1], f[2], f[3])
    if k == "Y":
        return ("%s is %s, %s ticks, vacates %s, beaten by %s"
                % (f[1], f[2], f[4], f[5], f[6]))
    if k == "M":
        return "%s is a %s aimed at the %s" % (f[1], f[2], f[3])
    if k == "V":
        return "property %s proven=%s" % (f[1], f[2])
    if k == "K":
        return "economy " + line[2:]
    if k == "S":
        return "TRAILER " + line[2:]
    if k == "H":
        return "header " + line[2:]
    return line


# Seeds and lengths chosen once and fixed. 4242 is the seed every phase record
# in this repository quotes. Phase O pins one round to keep the file reviewable
# in a diff; Phase Q pins the long run its port was proven at, because that is
# the run whose meaning the pin is protecting.
PINS = {
    "O": {
        "path": os.path.join("docs", "phase1a", "golden",
                             "phase_o_4242_1r.stream"),
        # The canonical stream: no floats, no opt-in diagnostics.
        "current": lambda: O.expected_stream(4242, 1, with_floats=False),
        "describe": _describe_o,
        # G1 and G5 have landed and moved it twice. G2 and G3 will move it
        # again, and so will the conversion work the 2026-08-06 measurement
        # points at. The file grew from ~2,000 lines to ~11,000 when Decision
        # 0018 removed the three-knockdown stoppage: the round now runs to the
        # bell instead of ending early, which is the pin recording a real change
        # in what a bout IS rather than getting bigger for no reason.
        "state": "HELD - moves on any canon ruling that changes the fight",
    },
    "Q": {
        "path": os.path.join("docs", "phase1a", "golden",
                             "phase_q_4242_5400.stream"),
        "current": lambda: Q.expected_stream(4242, 5400),
        "describe": _describe_q,
        "state": "PROVEN - UppercutCoreRangeCommandlet reproduces this exactly",
    },
    "R": {
        "path": os.path.join("docs", "phase1a", "golden",
                             "phase_r_4242_5400.stream"),
        "current": lambda: R.expected_stream(4242, 5400),
        "describe": _describe_r,
        "state": "PROVEN - UppercutCoreEvadeCommandlet reproduces this exactly",
    },
}


def current(phase: str) -> str:
    return PINS[phase]["current"]()


def stored(phase: str):
    p = os.path.join(REPO, PINS[phase]["path"])
    if not os.path.exists(p):
        return None
    return io.open(p, encoding="utf-8", newline="\n").read()


def describe(phase: str, line: str) -> str:
    return PINS[phase]["describe"](line)


def write(phase: str) -> int:
    p = os.path.join(REPO, PINS[phase]["path"])
    text = current(phase)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(text)
    print("wrote %s (%d lines)" % (PINS[phase]["path"], text.count("\n")))
    return 0


def diff(phase: str, verbose: bool = True) -> int:
    want, got = stored(phase), current(phase)
    path = PINS[phase]["path"]
    if want is None:
        print("phase %s: no golden file at %s - run --write first" % (phase, path))
        return 1
    if want == got:
        print("phase %s: golden stream matches (%d lines)"
              % (phase, got.count("\n")))
        return 0
    d = PINS[phase]["describe"]
    w, g = want.splitlines(), got.splitlines()
    print("PHASE %s GOLDEN STREAM DRIFT  [%s]" % (phase, PINS[phase]["state"]))
    print("  stored  %d lines" % len(w))
    print("  current %d lines" % len(g))
    print()
    shown = 0
    for i in range(max(len(w), len(g))):
        a = w[i] if i < len(w) else None
        b = g[i] if i < len(g) else None
        if a == b:
            continue
        shown += 1
        if shown > 25:
            print("  ... and more; the first 25 differences are shown")
            break
        print("  line %d" % (i + 1))
        print("    was  %s" % (d(a) if a else "(nothing)"))
        print("    now  %s" % (d(b) if b else "(nothing)"))
        if verbose and a and b:
            print("    raw was: %s" % a)
            print("    raw now: %s" % b)
    print()
    if phase == "Q":
        print("Phase Q has a C++ port that was proven against these exact bytes.")
        print("Re-run the parity proof BEFORE re-blessing:")
        print("    python -m tools.engine.prove_core_range")
    print("If this change was DELIBERATE - a canon ruling, a phase edit - re-bless")
    print("it in the same commit as the change that caused it:")
    print("    python -m tools.engine.golden --phase=%s --write" % phase)
    return 1


def main(argv) -> int:
    phases = [a.split("=", 1)[1] for a in argv if a.startswith("--phase=")]
    for p in phases:
        if p not in PINS:
            print("unknown phase %r; pinned phases are %s"
                  % (p, ", ".join(sorted(PINS))))
            return 1
    selected = phases or sorted(PINS)
    rc = 0
    for phase in selected:
        if "--write" in argv:
            rc |= write(phase)
        else:
            rc |= diff(phase, verbose="--diff" in argv)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:30 UTC | END ]
