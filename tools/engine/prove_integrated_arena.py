# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 09:45 UTC | START ]
"""The integrated round's pin: the fight the Director watches, in bytes.

WHY THIS FILE EXISTS. Decision 0040 R1 named the shared C++ `INTEGRATED_1R`
session the combat authority. On 2026-08-14 it was the one artifact in this
repository with nothing watching it: `prove_live_arena` deliberately asks for
`-integrated=0` (it pins Phase Q), `tools/engine/golden.py` covers O, Q and R,
and the two tests that looked like they covered the integrated arena existed on
`main` only as orphaned `.pyc` files with no `.py` beside them.

Their sources are real, on `feat/authenticity-program` - the branch Decision
0040 R6 holds as not merge-ready - which carries its own
`analyze_integrated_arena.py` and `prove_integrated_arena.py` under these exact
names. That collision was found after this file was written, it is not resolved
here, and it is a Director call rather than a race between whichever version
lands first. The comparison is in
`docs/development-log/2026-08-14-the-combat-authority-had-nothing-watching-it.md`.

The cost of that was already on the record and nobody had been told. Decision
0040 quotes the C++ round at `punches=123 landed=51` for seed 4242 over 10800
ticks. The same configuration on `86d3ef1` produces `punches=153 landed=153`.
Whether that is a build difference or a behaviour change, no gate could have
reported it, because no gate was looking.

WHAT IS AND IS NOT PROVEN HERE. Every other phase proves parity: a Python
contract predicts the bytes and the C++ port reproduces them. That is
impossible here by construction - Decision 0040 R2 makes Python reference-only,
so a Python module that predicted these bytes would be the second implementation
the convergence rule exists to prevent. So this pin is weaker and says so:

    the authority still produces the fight it produced when this was blessed,
    and that fight is internally coherent.

It cannot tell you the fight is correct. `analyze_integrated_arena` cannot
either. Whether 153 landed punches out of 153 thrown is boxing is a Director
judgement, and this file deliberately does not encode an opinion about it.

    python -m tools.engine.prove_integrated_arena          # needs UE, ~1 min
    python -m tools.engine.prove_integrated_arena --write  # re-bless, deliberately

THE NORMALISED FIELD, DECLARED. The C++ header carries `repo=<absolute path>`,
so the same fight produces different bytes in a different checkout - including
on the self-hosted runner Issue #14 is building, which checks out somewhere
else entirely. This file therefore normalises that ONE field to `repo=<repo>`
before comparing, and the pins are stored normalised. Nothing else is touched.
The real fix is for the header to stop carrying an environment path at all;
that is a change to the authoritative artifact's bytes and belongs to whoever
owns the header, not to its checker.
"""
import argparse
import hashlib
import io
import os
import re
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.engine import analyze_integrated_arena as A  # noqa: E402
from tools.engine.wedge import kill_the_wedge  # noqa: E402

ENGINE = os.environ.get("UPPERCUT_ENGINE", r"C:\Program Files\Epic Games\UE_5.8")
CMD = os.path.join(ENGINE, "Engine", "Binaries", "Win64", "UnrealEditor-Cmd.exe")
PROJECT = os.path.join(REPO, "sandbox", "UppercutSandbox.uproject")
OUTDIR = os.path.join(REPO, "sandbox", "Saved", "liveArena")
GOLDEN = os.path.join(REPO, "docs", "phase1a", "golden")

# Two full rounds and one short one. The full rounds are the seeds Decision 0040
# and `prove_one_round` already argue about, so a drift here lands in a
# conversation that already exists. The short run is not a prefix of the long
# one - the tick budget is an input to the policy's observation - and it earns
# its place by ending mid-round, which is the only configuration in the set that
# exercises a punch still in flight when the stream stops.
RUNS = ((4242, 10800), (777, 10800), (4242, 1200))

REPO_FIELD = re.compile(r"^(H\|phase=[^|]*\|contract=[^|]*\|seed=\d+\|ticks=\d+\|repo=).*$",
                        re.MULTILINE)


def normalise(text):
    """Replace the header's absolute repo path with a fixed token. See the
    module docstring: this is the only normalisation, and it is declared."""
    return REPO_FIELD.sub(r"\1<repo>", text)


def golden_path(seed, ticks):
    return os.path.join(GOLDEN, "integrated_1r_%d_%d.stream" % (seed, ticks))


def run_arena(seed, ticks):
    """Drive the authoritative session headless and return its bytes."""
    if not os.path.exists(CMD):
        raise SystemExit("no engine at %s - set UPPERCUT_ENGINE" % CMD)
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    out = os.path.join(OUTDIR, "integrated_%d_%d.stream" % (seed, ticks))
    if os.path.exists(out):
        os.remove(out)
    argv = [CMD, PROJECT, "-run=UppercutLiveArena", "-seed=%d" % seed,
            "-ticks=%d" % ticks, "-repo=%s" % REPO, "-out=%s" % out,
            "-integrated=1", "-unattended", "-nopause", "-nosplash"]
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    deadline = time.time() + 15 * 60
    while proc.poll() is None and time.time() < deadline:
        kill_the_wedge()
        time.sleep(2.0)
    if proc.poll() is None:
        proc.kill()
        raise SystemExit("the integrated round never finished (seed %d)" % seed)
    if not os.path.exists(out):
        raise SystemExit("the arena wrote no stream (seed %d)" % seed)
    return normalise(io.open(out, "r", encoding="utf-8", newline="").read())


def first_difference(got, want):
    a, b = got.splitlines(), want.splitlines()
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else "<end of file>"
        y = b[i] if i < len(b) else "<end of file>"
        if x != y:
            return i + 1, x, y
    return None, None, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true",
                    help="re-bless the pins from this run (say why in the commit)")
    ap.add_argument("--runs", default="",
                    help="seed:ticks[,seed:ticks] instead of the pinned set")
    args = ap.parse_args(argv)

    runs = RUNS
    if args.runs:
        runs = tuple(tuple(int(v) for v in part.split(":"))
                     for part in args.runs.split(",") if ":" in part)

    failed = 0
    for seed, ticks in runs:
        got = run_arena(seed, ticks)
        sha = hashlib.sha256(got.encode("utf-8")).hexdigest()
        path = golden_path(seed, ticks)
        label = "seed=%-5d ticks=%-6d" % (seed, ticks)

        report = A.analyse(got)
        if report["errors"]:
            failed = 1
            print("INCOHERENT  %s - the stream contradicts itself:" % label)
            for e in report["errors"][:10]:
                print("    %s" % e)

        if args.write:
            if not os.path.isdir(GOLDEN):
                os.makedirs(GOLDEN)
            io.open(path, "w", encoding="utf-8", newline="").write(got)
            print("BLESSED     %s sha256=%s" % (label, sha))
            print(A.summary(report))
            continue

        if not os.path.exists(path):
            failed = 1
            print("NO PIN      %s - %s does not exist; --write to bless it"
                  % (label, os.path.basename(path)))
            continue
        want = io.open(path, "r", encoding="utf-8", newline="").read()
        if got == want:
            print("PROVEN      %s sha256=%s" % (label, sha))
        else:
            failed = 1
            n, x, y = first_difference(got, want)
            print("DRIFT       %s first difference at line %d" % (label, n))
            print("    arena  %s" % A.describe(x))
            print("    pin    %s" % A.describe(y))
            print("  the arena's fight:")
            print(A.summary(report))
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 09:45 UTC | END ]
