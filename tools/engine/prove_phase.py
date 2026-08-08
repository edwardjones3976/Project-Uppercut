# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 05:40 UTC | START ]
"""Re-prove a phase's C++ artifact against its Python contract.

    python -m tools.engine.prove_phase              # every phase
    python -m tools.engine.prove_phase N L          # just these
    python -m tools.engine.prove_phase --list

WHY THIS EXISTS. Phases Q and R had `prove_core_range` / `prove_core_evade`,
which run the C++ artifact and compare its marker stream to the analyzer byte
for byte. Phases H, I, J, K, L and N had nothing of the kind, and the two guards
that look like they cover them do not:

    golden.py                   regenerates from the PYTHON analyzers and never
                                mentions -run=
    test_phase_evidence_pins    likewise recomputes expected_stream in Python

Both answer "does the Python contract still reproduce the record?". Neither
answers "does C++ still reproduce the contract?". That distinction is permanent
and both are needed; neither replaces the other.

The consequence was not hypothetical. On its first run this found Phase N's C++
still emitting the pre-Decision-0023 header while its analyzer had migrated -
1274 event rows identical, header divergent, and nothing in the repository able
to see it.

ONE CONCEPT OF PROOF, SEVERAL LAUNCH MECHANISMS. Phases differ in how they are
invoked, not in what proof means:

    produce the C++ artifact
            v
    derive the Python contract
            v
    compare exact bytes
            v
    cold-read the artifact through the analyzer
            v
    report the FIRST divergence

So the launch mechanism is a strategy and the proof is not.

It does NOT check the historical recorded hash. A phase proven under older canon
legitimately produces different bytes now; what must hold is that the two
implementations still agree. Where they do not, that is a finding to report, not
a number to update.
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
EDITOR = os.path.join(ENGINE, "Engine", "Binaries", "Win64", "UnrealEditor.exe")
PROJECT = os.path.join(REPO, "sandbox", "UppercutSandbox.uproject")
OUTDIR = os.path.join(REPO, "sandbox", "Saved", "prove_phase")


def _out_path(key, seed, n):
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    p = os.path.join(OUTDIR, "%s_%d_%d.stream" % (key, seed, n))
    if os.path.exists(p):
        os.remove(p)
    return p


class CommandletRepoTicksRunner(object):
    """-run=<name> -seed= -ticks= -repo= -out=   (phases I, J, L, N)."""

    needs = "UnrealEditor-Cmd"

    def __init__(self, run):
        self.run = run

    def produce(self, key, seed, n):
        out = _out_path(key, seed, n)
        argv = [CMD, PROJECT, "-run=%s" % self.run, "-seed=%d" % seed,
                "-ticks=%d" % n, "-repo=%s" % REPO, "-out=%s" % out,
                "-unattended", "-nopause", "-nosplash"]
        return out, wedge.run_editor(argv, timeout_s=1800,
                                     label="the phase %s run" % key)


class CommandletCanonStepsRunner(object):
    """-run=<name> -seed= -steps= -canon=<file> -out=   (phase H).

    A different argument shape is an adapter problem, not a reason to leave a
    phase unproven or to spawn a second proof script for it.
    """

    needs = "UnrealEditor-Cmd"

    def __init__(self, run, canon_rel):
        self.run, self.canon_rel = run, canon_rel

    def produce(self, key, seed, n):
        out = _out_path(key, seed, n)
        argv = [CMD, PROJECT, "-run=%s" % self.run, "-seed=%d" % seed,
                "-steps=%d" % n,
                "-canon=%s" % os.path.join(REPO, *self.canon_rel.split("/")),
                "-out=%s" % out, "-unattended", "-nopause", "-nosplash"]
        return out, wedge.run_editor(argv, timeout_s=1800,
                                     label="the phase %s run" % key)


class RenderedPhaseRunner(object):
    """UnrealEditor.exe with -game and a map/gamemode URL   (phase K).

    The rendered slice is not a commandlet: it boots a real game world through
    UppercutRenderGameMode. Arguments mirror tools/engine/run_render_probe.ps1,
    which is the invocation Phase K was originally proven with.
    """

    needs = "UnrealEditor"

    def __init__(self, gamemode):
        self.gamemode = gamemode

    def produce(self, key, seed, n):
        out = _out_path(key, seed, n)
        shots = os.path.join(OUTDIR, "shots_%s_%d_%d" % (key, seed, n))
        argv = [EDITOR, PROJECT,
                "/Engine/Maps/Entry?game=%s" % self.gamemode,
                "-game", "-windowed", "-ResX=1280", "-ResY=720",
                "-benchmark", "-fps=60", "-NoLoadingScreen",
                "-unattended", "-nosplash",
                "-seed=%d" % seed, "-ticks=%d" % n, "-repo=%s" % REPO,
                "-out=%s" % out, "-shots=%s" % shots]
        return out, wedge.run_editor(argv, timeout_s=2400,
                                     label="the phase %s rendered run" % key)


class Phase(object):
    def __init__(self, key, title, runner, analyzer, runs):
        self.key, self.title = key, title
        self.runner, self.analyzer, self.runs = runner, analyzer, runs


# Two seeds each, because nothing may be true of 4242 alone. Phase H quotes
# 7777/7778 in its own record and keeps them.
PHASES = [
    Phase("H", "the C++ core scaffold",
          CommandletCanonStepsRunner("UppercutCoreProbe",
                                     "data/movement_model.json"),
          "analyze_core_scaffold", [(7777, 600), (7778, 600)]),
    Phase("I", "the two-fighter authoritative loop",
          CommandletRepoTicksRunner("UppercutCoreLoop"),
          "analyze_core_loop", [(4242, 1200), (4243, 1200)]),
    Phase("J", "real movement and swept collision",
          CommandletRepoTicksRunner("UppercutCoreSweep"),
          "analyze_core_sweep", [(4242, 1200), (4243, 1200)]),
    # 5400, not the 1200 the commandlet phases use. Phase K's analyzer asserts
    # that the demonstration actually happened - "the uppercut never landed" -
    # and at 1200 ticks it has not yet, so a shorter run fails a coherence
    # check rather than a byte check. The record's own tick count is the only
    # one this phase's contract is meaningful at.
    Phase("K", "the first rendered slice",
          RenderedPhaseRunner("/Script/UppercutCore.UppercutRenderGameMode"),
          "analyze_render_probe", [(4242, 5400)]),
    Phase("L", "guard and slip",
          CommandletRepoTicksRunner("UppercutCoreGuard"),
          "analyze_core_guard", [(4242, 1200), (4243, 1200)]),
    Phase("N", "visible stamina and condition",
          CommandletRepoTicksRunner("UppercutCoreCondition"),
          "analyze_core_condition", [(4242, 1200), (4243, 1200)]),
]

ELSEWHERE = {
    "Q": "tools.engine.prove_core_range",
    "R": "tools.engine.prove_core_evade",
    "live arena": "tools.engine.prove_live_arena",
    "O": "contract only - no C++ artifact exists to re-prove",
}


def pre_generate_target_info():
    """Stop TurnkeySupport spawning Build.bat -Mode=QueryTargets.

    A SECOND wedge, distinct from the ValidatePlatforms one wedge.py kills, and
    the reason the original phase runners pre-generate this file.
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


def header_body(lines):
    return ([l for l in lines if l.startswith("H|")],
            [l for l in lines if not l.startswith("H|")])


def prove(phase):
    mod = __import__(phase.analyzer)
    failed = 0
    for seed, n in phase.runs:
        want = mod.expected_stream(seed, n)
        path, log = phase.runner.produce(phase.key, seed, n)
        if not os.path.exists(path):
            failed = 1
            print("  NO STREAM seed=%d n=%d" % (seed, n))
            for l in log.splitlines()[-12:]:
                print("     %s" % l[:130])
            continue
        got = io.open(path, "r", encoding="utf-8", newline="").read()
        same, line, x, y = compare(got, want)
        sha = hashlib.sha256(got.encode("utf-8")).hexdigest()

        if not same:
            failed = 1
            gh, gb = header_body(got.splitlines())
            wh, wb = header_body(want.splitlines())
            # Say WHICH KIND of divergence immediately. A header difference and
            # a moved fight are the same red line and completely different
            # problems, and the first question anyone asks is which one it is.
            kind = ("HEADER ONLY - every authoritative row matches"
                    if gb == wb else "EVENT ROWS DIFFER - the fight moved")
            print("  DRIFT  seed=%-5d n=%-5d first difference at line %d" %
                  (seed, n, line))
            print("     %s" % kind)
            print("     artifact %s" % x[:120])
            print("     contract %s" % y[:120])
            continue

        # The artifact is also read back cold and re-derived from its own rows,
        # so a pair that agreed for a shared wrong reason still has somewhere
        # left to fail.
        report = mod.analyse(path)
        errs = report.get("errors") if isinstance(report, dict) else None
        if errs:
            failed = 1
            print("  MATCHED-BUT-INCOHERENT seed=%d n=%d" % (seed, n))
            for e in errs[:8]:
                print("     %s" % e)
            continue
        print("  PROVEN seed=%-5d n=%-5d sha256=%s" % (seed, n, sha))
    return failed


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("phases", nargs="*")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        for p in PHASES:
            print("%-3s %-38s %s" % (p.key, p.title,
                                     type(p.runner).__name__))
        for k, where in sorted(ELSEWHERE.items()):
            print("%-3s proven elsewhere - %s" % (k, where))
        return 0

    keys = [a.upper() for a in args.phases]
    wanted = [p for p in PHASES if not keys or p.key in keys]
    if not wanted:
        raise SystemExit("no phase matched %s. Try --list." % args.phases)

    pre_generate_target_info()
    failed = 0
    for p in wanted:
        print("Phase %s - %s (%s)"
              % (p.key, p.title, type(p.runner).__name__))
        failed |= prove(p)
        print()

    if not keys:
        print("Proven by their own runners, not this one: %s"
              % ", ".join("%s (%s)" % (k, v) for k, v in sorted(ELSEWHERE.items())))
        print()
    print("PHASES PROVEN" if not failed else "PHASE DRIFT")
    return failed


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 05:40 UTC | END ]
