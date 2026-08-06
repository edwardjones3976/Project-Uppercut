# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:50 UTC | START ]
"""The live arena's parity: what you press Play on is what was proven.

`prove_core_range` proves the C++ RULES reproduce the contract. It says nothing
about the world subsystem, its controls, or its stream writer - and those sit
between the proven rules and the screen. New code in that gap is exactly where a
"runtime version" quietly becomes a second implementation.

This drives UUppercutFightSubsystem inside a real UWorld, through its own
single-step control, and compares the file it dumps to the contract's stream. A
pass means the fight the Director watches is the fight the evidence describes.

    python -m tools.engine.prove_live_arena
    python -m tools.engine.prove_live_arena 777:5400
"""
import hashlib
import io
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze_core_range as Q  # noqa: E402

REPO = Q.REPO
ENGINE = os.environ.get("UPPERCUT_ENGINE", r"C:\Program Files\Epic Games\UE_5.8")
CMD = os.path.join(ENGINE, "Engine", "Binaries", "Win64", "UnrealEditor-Cmd.exe")
PROJECT = os.path.join(REPO, "sandbox", "UppercutSandbox.uproject")
OUTDIR = os.path.join(REPO, "sandbox", "Saved", "liveArena")

# Shorter than the headless set on purpose: this is checking the wiring between
# the subsystem and the proven core, and wiring that is right for 1200 ticks is
# right. The long runs stay where they belong, in prove_core_range.
RUNS = ((4242, 1200), (777, 900))

PS_LIST = ("Get-CimInstance Win32_Process | "
           "ForEach-Object { $_.ProcessId.ToString() + '|' + $_.Name + '|' "
           "+ [string]$_.CommandLine }")


def kill_the_wedge():
    """Turnkey's ValidatePlatforms child ping-loops on every editor boot here."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LIST],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in out.stdout.decode("utf-8", "replace").splitlines():
        low = line.lower()
        if "validateplatforms" in low or "|ping.exe|" in low:
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Stop-Process -Id %s -Force -ErrorAction SilentlyContinue"
                            % line.split("|")[0].strip()])


def run_arena(seed: int, ticks: int) -> str:
    if not os.path.exists(CMD):
        raise SystemExit("no engine at %s - set UPPERCUT_ENGINE" % CMD)
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    out = os.path.join(OUTDIR, "live_%d_%d.stream" % (seed, ticks))
    if os.path.exists(out):
        os.remove(out)
    argv = [CMD, PROJECT, "-run=UppercutLiveArena", "-seed=%d" % seed,
            "-ticks=%d" % ticks, "-repo=%s" % REPO, "-out=%s" % out,
            "-unattended", "-nopause", "-nosplash"]
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    deadline = time.time() + 15 * 60
    while proc.poll() is None and time.time() < deadline:
        kill_the_wedge()
        time.sleep(2.0)
    if proc.poll() is None:
        proc.kill()
        raise SystemExit("the arena run never finished")
    if not os.path.exists(out):
        raise SystemExit("the arena wrote no stream")
    return out


def main(argv) -> int:
    pairs = [tuple(int(v) for v in a.split(":")) for a in argv if ":" in a]
    failed = 0
    for seed, ticks in (pairs or RUNS):
        want = Q.expected_stream(seed, ticks)
        path = run_arena(seed, ticks)
        got = io.open(path, "r", encoding="utf-8", newline="").read()
        sha = hashlib.sha256(got.encode("utf-8")).hexdigest()
        if got == want:
            print("LIVE PROVEN seed=%-5d ticks=%-5d sha256=%s" % (seed, ticks, sha))
        else:
            failed = 1
            a, b = got.splitlines(), want.splitlines()
            for i in range(max(len(a), len(b))):
                x = a[i] if i < len(a) else "<end of file>"
                y = b[i] if i < len(b) else "<end of file>"
                if x != y:
                    print("LIVE DRIFT  seed=%-5d ticks=%-5d first difference at line %d"
                          % (seed, ticks, i + 1))
                    print("   arena    %s" % x)
                    print("   contract %s" % y)
                    break
        # Read back cold and re-derived from its own rows, so a pair that agreed
        # for a shared wrong reason still has somewhere left to fail.
        report = Q.analyse(path)
        if report["errors"]:
            failed = 1
            print("   the stream is not internally coherent:")
            for e in report["errors"][:10]:
                print("     %s" % e)
    return failed


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:50 UTC | END ]
