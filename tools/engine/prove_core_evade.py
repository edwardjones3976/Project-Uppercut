# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 13:05 UTC | START ]
"""Phase R parity: run the C++ commandlet and prove it against the contract.

Byte-identical or it is not proven. Same shape as `prove_core_range`, and a
Python entry point for the same reason: a PowerShell runner that silently does
nothing is indistinguishable from a run that found nothing, which is the worst
failure mode available to evidence tooling.

    python -m tools.engine.prove_core_evade
    python -m tools.engine.prove_core_evade 4242:5400 777:5400
    python -m tools.engine.prove_core_evade --contract-only
"""
import hashlib
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_evade as R  # noqa: E402

REPO = R.REPO
ENGINE = os.environ.get("UPPERCUT_ENGINE", r"C:\Program Files\Epic Games\UE_5.8")
CMD = os.path.join(ENGINE, "Engine", "Binaries", "Win64", "UnrealEditor-Cmd.exe")
PROJECT = os.path.join(REPO, "sandbox", "UppercutSandbox.uproject")
OUTDIR = os.path.join(REPO, "sandbox", "Saved", "phaseR")

# One long run on the seed every phase quotes, one on a different seed so
# nothing can be true of 4242 alone, and one short run because a port that is
# wrong late is usually wrong early too.
RUNS = ((4242, 5400), (777, 5400), (4242, 1200))


def run_commandlet(seed: int, ticks: int) -> str:
    if not os.path.exists(CMD):
        raise SystemExit("no engine at %s - set UPPERCUT_ENGINE" % CMD)
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    out = os.path.join(OUTDIR, "r_%d_%d.stream" % (seed, ticks))
    if os.path.exists(out):
        os.remove(out)
    argv = [CMD, PROJECT, "-run=UppercutCoreEvade", "-seed=%d" % seed,
            "-ticks=%d" % ticks, "-repo=%s" % REPO, "-out=%s" % out,
            "-unattended", "-nopause", "-nosplash"]
    proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if not os.path.exists(out):
        tail = proc.stdout.decode("utf-8", "replace").splitlines()[-20:]
        raise SystemExit("the commandlet wrote no stream:\n  " + "\n  ".join(tail))
    return out


def main(argv) -> int:
    only = "--contract-only" in argv
    pairs = [tuple(int(v) for v in a.split(":")) for a in argv if ":" in a]
    failed = 0
    for seed, ticks in (pairs or RUNS):
        want = R.expected_stream(seed, ticks)
        if only:
            print("contract seed=%-5d ticks=%-5d %4d lines sha256=%s"
                  % (seed, ticks, len(want.splitlines()),
                     hashlib.sha256(want.encode("utf-8")).hexdigest()))
            continue
        path = run_commandlet(seed, ticks)
        got = io.open(path, "r", encoding="utf-8", newline="").read()
        sha = hashlib.sha256(got.encode("utf-8")).hexdigest()
        if got == want:
            print("PROVEN seed=%-5d ticks=%-5d sha256=%s" % (seed, ticks, sha))
        else:
            failed = 1
            a, b = got.splitlines(), want.splitlines()
            line = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]),
                        min(len(a), len(b)))
            print("DRIFT  seed=%-5d ticks=%-5d first difference at line %d"
                  % (seed, ticks, line + 1))
            print("   commandlet %s" % (a[line] if line < len(a) else "<eof>"))
            print("   contract   %s" % (b[line] if line < len(b) else "<eof>"))
        report = R.analyse(path)
        if report["errors"]:
            failed = 1
            print("   the stream is not internally coherent:")
            for e in report["errors"][:10]:
                print("     %s" % e)
    return failed


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 13:05 UTC | END ]
