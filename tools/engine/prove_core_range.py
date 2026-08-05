# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:10 UTC | START ]
"""Phase Q parity: run the C++ commandlet and prove it against the contract.

A phase is proven here when the artifact's marker stream is byte-identical to
the analyzer's - not when the two look similar, and not when their trailers
agree. This runs both and compares the bytes.

WHY PYTHON AND NOT A .ps1 LIKE THE EARLIER PHASES. Phase N's runner is
PowerShell and works when a human runs it. Driven from an agent's spawn context
it silently did nothing twice: a mandatory `param()` that fails to bind prompts
on stdin and hangs forever with no output, and Write-Host goes to the
information stream, which `>` from cmd does not capture. Both failures look
exactly like "the run produced nothing", which is the worst possible failure
mode for evidence tooling. This does the same job with no shell in the middle,
and its output lands on stdout where every caller can see it.

    python -m tools.engine.prove_core_range                     # the pinned set
    python -m tools.engine.prove_core_range 4242:5400 777:5400  # seed:ticks
    python -m tools.engine.prove_core_range --contract-only     # no engine needed
"""
import hashlib
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_range as Q  # noqa: E402

REPO = Q.REPO
ENGINE = os.environ.get("UPPERCUT_ENGINE", r"C:\Program Files\Epic Games\UE_5.8")
CMD = os.path.join(ENGINE, "Engine", "Binaries", "Win64", "UnrealEditor-Cmd.exe")
PROJECT = os.path.join(REPO, "sandbox", "UppercutSandbox.uproject")
OUTDIR = os.path.join(REPO, "sandbox", "Saved", "phaseQ")

# The pinned set. One long run on the seed every phase uses, one on a different
# seed so nothing can be true of 4242 alone, and one short run whose whole point
# is that a port which is wrong late is usually wrong early too.
RUNS = ((4242, 5400), (777, 5400), (4242, 900))


def contract(seed: int, ticks: int) -> str:
    return Q.expected_stream(seed, ticks)


def run_commandlet(seed: int, ticks: int) -> str:
    """Ask the engine for the same stream. Returns the path it wrote."""
    if not os.path.exists(CMD):
        raise SystemExit("no engine at %s - set UPPERCUT_ENGINE" % CMD)
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    out = os.path.join(OUTDIR, "q_%d_%d.stream" % (seed, ticks))
    if os.path.exists(out):
        os.remove(out)
    argv = [CMD, PROJECT, "-run=UppercutCoreRange", "-seed=%d" % seed,
            "-ticks=%d" % ticks, "-repo=%s" % REPO, "-out=%s" % out,
            "-unattended", "-nopause", "-nosplash"]
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if not os.path.exists(out):
        tail = proc.stdout.decode("utf-8", "replace").splitlines()[-20:]
        raise SystemExit("the commandlet wrote no stream:\n  "
                         + "\n  ".join(tail))
    return out


def compare(got: str, want: str) -> tuple:
    """(identical, first differing line number, got line, want line)."""
    if got == want:
        return True, 0, "", ""
    a, b = got.splitlines(), want.splitlines()
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else "<end of file>"
        y = b[i] if i < len(b) else "<end of file>"
        if x != y:
            return False, i + 1, x, y
    return False, 0, "", ""


def main(argv) -> int:
    only = "--contract-only" in argv
    pairs = [tuple(int(v) for v in a.split(":")) for a in argv if ":" in a]
    failed = 0
    for seed, ticks in (pairs or RUNS):
        want = contract(seed, ticks)
        if only:
            print("contract seed=%-5d ticks=%-5d %4d lines sha256=%s"
                  % (seed, ticks, len(want.splitlines()),
                     hashlib.sha256(want.encode("utf-8")).hexdigest()))
            continue
        path = run_commandlet(seed, ticks)
        got = io.open(path, "r", encoding="utf-8", newline="").read()
        same, line, x, y = compare(got, want)
        sha = hashlib.sha256(got.encode("utf-8")).hexdigest()
        if same:
            print("PROVEN seed=%-5d ticks=%-5d sha256=%s" % (seed, ticks, sha))
        else:
            failed = 1
            print("DRIFT  seed=%-5d ticks=%-5d first difference at line %d"
                  % (seed, ticks, line))
            print("   commandlet %s" % x)
            print("   contract   %s" % y)
        # The artifact is also read back cold and re-derived from its own rows,
        # so a pair that agreed for a shared wrong reason still has somewhere
        # left to fail.
        report = Q.analyse(path)
        if report["errors"]:
            failed = 1
            print("   the stream is not internally coherent:")
            for e in report["errors"][:10]:
                print("     %s" % e)
    return failed


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 22:10 UTC | END ]
