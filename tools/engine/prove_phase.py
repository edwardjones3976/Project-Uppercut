# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 04:05 UTC | START ]
"""Re-prove a phase's C++ artifact against its Python contract.

    python -m tools.engine.prove_phase              # every covered phase
    python -m tools.engine.prove_phase N L          # just these
    python -m tools.engine.prove_phase --list

WHY THIS EXISTS, AND WHY IT IS URGENT RATHER THAN TIDY.

Phases Q and R have `prove_core_range` / `prove_core_evade`, which run the C++
commandlet and compare its marker stream to the analyzer byte for byte. Phases
H, I, J, K, L and N have nothing of the kind. Checked 2026-08-08:

    prove_canon_parity   -> UppercutCanonVectors
    prove_core_evade     -> UppercutCoreEvade      (Phase R)
    prove_core_range     -> UppercutCoreRange      (Phase Q)
    prove_live_arena     -> UppercutLiveArena

`golden.py` does not close the gap. It regenerates from the PYTHON analyzers
(`analyze_core_evade`, `analyze_core_range`, `analyze_core_round`) and invokes
no commandlet at all - it never mentions `-run=`. `test_phase_evidence_pins`
likewise recomputes `expected_stream(...)` in Python. Both are real guards
against the analyzer changing. Neither can see the C++ move.

The consequence is precise and was the reason this file got written: the six
commandlets that parse movement canon inline could be edited today and NOTHING
in the repository would notice. That makes the loader unification the
integrated schema needs - one reader replacing six - an unfalsifiable change,
which is the one kind this project refuses to make.

So this is the safety net that has to exist BEFORE that refactor, not after.

WHAT IT PROVES. For each phase: run the commandlet, read the stream it wrote,
and require it to be byte-identical to `expected_stream(seed, ticks)`. Then
hand the artifact back to the analyzer's own `analyse()` so a pair that agreed
for a shared wrong reason still has somewhere left to fail. Two seeds each,
because nothing may be true of 4242 alone.

It does NOT check the historical recorded hash. A phase proven months ago under
older canon legitimately produces different bytes now; what must hold is that
the two implementations still agree with each other. Where a run disagrees,
that is a finding to report, not a number to update.
"""
import argparse
import hashlib
import io
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "tools", "engine"))

from tools.engine import wedge  # noqa: E402

ENGINE = os.environ.get("UPPERCUT_ENGINE", r"C:\Program Files\Epic Games\UE_5.8")
CMD = os.path.join(ENGINE, "Engine", "Binaries", "Win64", "UnrealEditor-Cmd.exe")
PROJECT = os.path.join(REPO, "sandbox", "UppercutSandbox.uproject")
OUTDIR = os.path.join(REPO, "sandbox", "Saved", "prove_phase")


class Phase(object):
    def __init__(self, key, title, run, analyzer, runs):
        self.key, self.title = key, title
        self.run, self.analyzer, self.runs = run, analyzer, runs


# The four commandlets that take the same -seed/-ticks/-repo/-out shape. Two
# seeds each: 4242 is the seed every phase quotes, and a second one exists so
# that nothing here can be true of 4242 alone.
COVERED = [
    Phase("I", "the two-fighter authoritative loop", "UppercutCoreLoop",
          "analyze_core_loop", [(4242, 1200), (4243, 1200)]),
    Phase("J", "real movement and swept collision", "UppercutCoreSweep",
          "analyze_core_sweep", [(4242, 1200), (4243, 1200)]),
    Phase("L", "guard and slip", "UppercutCoreGuard",
          "analyze_core_guard", [(4242, 1200), (4243, 1200)]),
    Phase("N", "visible stamina and condition", "UppercutCoreCondition",
          "analyze_core_condition", [(4242, 1200), (4243, 1200)]),
]

# Named rather than omitted. A safety net that quietly covers four of six while
# reading as though it covers the set is the failure this file exists to stop.
NOT_COVERED = {
    "H": ("UppercutCoreProbe takes -canon=<file> and -steps= instead of "
          "-repo=/-ticks=, so it needs its own entry rather than this shape"),
    "K": ("the rendered slice runs UnrealEditor.exe with -game and a map/"
          "gamemode URL, not a commandlet - see tools/engine/run_render_probe.ps1"),
    "Q": "already covered by tools.engine.prove_core_range",
    "R": "already covered by tools.engine.prove_core_evade",
}


def pre_generate_target_info():
    """Stop TurnkeySupport spawning Build.bat -Mode=QueryTargets.

    A SECOND wedge, distinct from the ValidatePlatforms one wedge.py kills, and
    the reason the phase runners pre-generate this file. Cheap; do it once.
    """
    dotnet = os.path.join(ENGINE, "Engine", "Binaries", "ThirdParty", "DotNet",
                          "10.0", "win-x64", "dotnet.exe")
    ubt = os.path.join(ENGINE, "Engine", "Binaries", "DotNET",
                       "UnrealBuildTool", "UnrealBuildTool.dll")
    target = os.path.join(REPO, "sandbox", "Intermediate", "TargetInfo.json")
    if not (os.path.exists(dotnet) and os.path.exists(ubt)):
        return
    try:
        subprocess.run([dotnet, ubt, "-Mode=QueryTargets",
                        "-Project=%s" % PROJECT, "-Output=%s" % target],
                       cwd=os.path.join(ENGINE, "Engine", "Source"),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=180)
    except Exception:
        pass


def run_commandlet(phase, seed, ticks):
    if not os.path.exists(CMD):
        raise SystemExit("no engine at %s - set UPPERCUT_ENGINE" % CMD)
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    out = os.path.join(OUTDIR, "%s_%d_%d.stream" % (phase.key, seed, ticks))
    if os.path.exists(out):
        os.remove(out)
    argv = [CMD, PROJECT, "-run=%s" % phase.run, "-seed=%d" % seed,
            "-ticks=%d" % ticks, "-repo=%s" % REPO, "-out=%s" % out,
            "-unattended", "-nopause", "-nosplash"]
    log = wedge.run_editor(argv, timeout_s=1800,
                           label="the phase %s run" % phase.key)
    if not os.path.exists(out):
        tail = "\n  ".join(log.splitlines()[-20:])
        raise SystemExit("phase %s wrote no stream:\n  %s" % (phase.key, tail))
    return out


def compare(got, want):
    """(identical, first differing line, got line, want line)."""
    if got == want:
        return True, 0, "", ""
    a, b = got.splitlines(), want.splitlines()
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else "<end of file>"
        y = b[i] if i < len(b) else "<end of file>"
        if x != y:
            return False, i + 1, x, y
    return False, 0, "", ""


def prove(phase):
    mod = __import__(phase.analyzer)
    failed = 0
    for seed, ticks in phase.runs:
        want = mod.expected_stream(seed, ticks)
        path = run_commandlet(phase, seed, ticks)
        got = io.open(path, "r", encoding="utf-8", newline="").read()
        same, line, x, y = compare(got, want)
        sha = hashlib.sha256(got.encode("utf-8")).hexdigest()
        if not same:
            failed = 1
            print("  DRIFT  seed=%-5d ticks=%-5d first difference at line %d"
                  % (seed, ticks, line))
            print("     commandlet %s" % x[:140])
            print("     contract   %s" % y[:140])
            continue

        # The artifact is also read back cold and re-derived from its own rows,
        # so a pair that agreed for a shared wrong reason still has somewhere
        # left to fail.
        report = mod.analyse(path)
        errs = report.get("errors") if isinstance(report, dict) else None
        if errs:
            failed = 1
            print("  PROVEN-BUT-INCOHERENT seed=%d ticks=%d" % (seed, ticks))
            for e in errs[:8]:
                print("     %s" % e)
            continue
        print("  PROVEN seed=%-5d ticks=%-5d sha256=%s" % (seed, ticks, sha))
    return failed


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("phases", nargs="*", help="phase keys, e.g. N L")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        for p in COVERED:
            print("%-3s %-40s %s" % (p.key, p.title, p.run))
        for k, why in sorted(NOT_COVERED.items()):
            print("%-3s NOT COVERED - %s" % (k, why))
        return 0

    wanted = [p for p in COVERED
              if not args.phases or p.key in [a.upper() for a in args.phases]]
    if not wanted:
        raise SystemExit("no covered phase matched %s. Try --list." % args.phases)

    pre_generate_target_info()

    failed = 0
    for p in wanted:
        print("Phase %s - %s (%s)" % (p.key, p.title, p.run))
        failed |= prove(p)
        print()

    uncovered = sorted(k for k in NOT_COVERED
                       if k in ("H", "K") and not args.phases)
    if uncovered:
        # Said out loud every run. A net that covers four of six while reading
        # as though it covers the set is worse than one that admits the hole.
        print("NOT COVERED by this runner: %s" % ", ".join(uncovered))
        for k in uncovered:
            print("   %s - %s" % (k, NOT_COVERED[k]))
        print()

    print("PHASES PROVEN" if not failed else "PHASE DRIFT")
    return failed


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 04:05 UTC | END ]
