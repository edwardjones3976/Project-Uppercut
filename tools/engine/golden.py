# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:00 UTC | START ]
"""The golden stream: the exact bytes a C++ port has to produce.

A phase is proven here when the C++ artifact's marker stream is byte-identical
to the analyzer's. Until now that target has only ever existed as "whatever
`expected_stream` returns today" - which is a target that moves silently, and
moved silently once already: on 2026-08-04 a sealed analyzer was edited, Phase
N's recomputation went from 88af6f30 to 974c12ef, and THE WHOLE SUITE STILL
PASSED because every test regenerated from the same edited analyzer. Nothing
compared it to anything.

`test_phase_evidence_pins.py` closed that for the two PROVEN phases by pinning
their hashes. This closes it differently and for the phase about to be ported: it
writes the stream to a file, commits it, and diffs against it. A hash tells you
something moved. A golden file tells you WHAT moved, in fight terms - which
punch, at which tick, with what result.

    python -m tools.engine.golden --check     # compare, exit 1 on drift
    python -m tools.engine.golden --write     # re-bless after a deliberate change
    python -m tools.engine.golden --diff      # show the drift as a fight

ON PHASE O BEING HELD. This pin WILL fail when G1, G2 or G3 is decided, because
a step cost or an aggression bias changes the fight. That is the point: the
decision and the re-blessing belong in the same commit, so a canon ruling and its
consequence are one reviewable change rather than a number edited in one place
and a stream quietly regenerated somewhere else.
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_core_round as O  # noqa: E402

# Seed and rounds chosen once and fixed. 4242 is the seed every phase record in
# this repository quotes, and one round keeps the file reviewable in a diff.
SEED, ROUNDS = 4242, 1
PATH = os.path.join("docs", "phase1a", "golden", "phase_o_%d_%dr.stream" % (SEED, ROUNDS))


def current() -> str:
    """The canonical stream: no floats, no opt-in diagnostics."""
    return O.expected_stream(SEED, ROUNDS, with_floats=False)


def stored() -> str:
    p = os.path.join(O.REPO, PATH)
    if not os.path.exists(p):
        return None
    return io.open(p, encoding="utf-8", newline="\n").read()


def write() -> int:
    p = os.path.join(O.REPO, PATH)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(current())
    print("wrote %s (%d lines)" % (PATH, current().count("\n")))
    return 0


def describe(line: str) -> str:
    """One stream row, in words. A diff nobody can read is a hash with extra
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


def diff(verbose: bool = True) -> int:
    want, got = stored(), current()
    if want is None:
        print("no golden file at %s - run --write first" % PATH)
        return 1
    if want == got:
        print("golden stream matches (%d lines)" % got.count("\n"))
        return 0
    w, g = want.splitlines(), got.splitlines()
    print("GOLDEN STREAM DRIFT")
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
        print("    was  %s" % (describe(a) if a else "(nothing)"))
        print("    now  %s" % (describe(b) if b else "(nothing)"))
        if verbose and a and b:
            print("    raw was: %s" % a)
            print("    raw now: %s" % b)
    print()
    print("If this change was DELIBERATE - a canon ruling, a phase edit - re-bless")
    print("it in the same commit as the change that caused it:")
    print("    python -m tools.engine.golden --write")
    return 1


def main(argv) -> int:
    if "--write" in argv:
        return write()
    if "--diff" in argv:
        return diff(verbose=True)
    return diff(verbose=False)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 21:00 UTC | END ]
