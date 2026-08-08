# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 18:40 UTC | START ]
"""The nightly verification, as one command that can be run anywhere.

    python -m tools.engine.nightly_verify              # all gates
    python -m tools.engine.nightly_verify --no-engine  # skip the Unreal gate

WHY THIS EXISTS. The nightly verification was a scheduled CLOUD task whose
prompt described five commands for an agent to run on this machine over the
device bridge. It failed every night, and it could not have done otherwise:

  - a scheduled cloud run is not provisioned with the remote-devices bridge,
    so it cannot reach C:\\Users\\edwar\\project-uppercut at all;
  - the repository is private and the cloud sandbox holds no credential for it
    (verified 2026-08-07: a public repo clones, this one returns 401);
  - three of the five gates need UE 5.8, which exists only here.

None of that is a configuration bug that can be fixed by editing the schedule.
The verification has to run where the repository and the engine are.

So the logic moved out of a prompt and into this file. A scheduled task now
only has to run one command, which means the thing being scheduled is version
controlled, reviewable, testable, and identical whether a human or an agent
starts it. A prompt that lists five commands is a sixth implementation of the
gate list; this is the one.

EXIT CODE IS THE ANSWER. 0 only if every gate that ran passed. A gate that was
deliberately skipped is reported as SKIP and does not fail the run - but the
report says so out loud, because a verification that quietly stops checking
something is the failure mode this repository cares most about.
"""
import argparse
import io
import os
import subprocess
import sys
import threading
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

# Gate 5 boots the editor, and on this machine every editor boot spawns the
# Turnkey ValidatePlatforms ping-loop. The runner clears it, but only on
# branches that carry the shared killer - so this clears it too, and a stale
# checkout still finishes instead of hanging for a quarter of an hour.
try:
    from tools.engine.wedge import kill_the_wedge
except Exception:  # pragma: no cover - a checkout predating tools/engine/wedge.py
    kill_the_wedge = None


PS_LIST = ("Get-CimInstance Win32_Process | "
           "ForEach-Object { $_.ProcessId.ToString() + '|' + $_.Name + '|' "
           "+ [string]$_.CommandLine }")


def editor_is_open():
    """Is the Director's interactive editor running?

    UnrealEditor.exe is Ed's; UnrealEditor-Cmd.exe is a headless commandlet and
    is ours. NEVER kill the former, and skip the engine gate while it is up
    rather than competing with it.
    """
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LIST],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in out.stdout.decode("utf-8", "replace").splitlines():
        name = line.split("|")[1].lower() if line.count("|") >= 2 else ""
        if name == "unrealeditor.exe":
            return True
    return False


class WedgeKiller(threading.Thread):
    """Clear the Turnkey wedge for as long as an engine gate is running."""

    daemon = True

    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = threading.Event()

    def run(self):
        while not self.stop.is_set():
            if kill_the_wedge is not None:
                try:
                    kill_the_wedge()
                except Exception:
                    pass
            self.stop.wait(2.0)


def branch():
    try:
        out = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                             cwd=REPO, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        return out.stdout.decode("utf-8", "replace").strip() or "(unknown)"
    except Exception:
        return "(unknown)"


def head():
    try:
        out = subprocess.run(["git", "log", "--oneline", "-1"], cwd=REPO,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        return out.stdout.decode("utf-8", "replace").strip() or "(unknown)"
    except Exception:
        return "(unknown)"


def dirty():
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        lines = [l for l in out.stdout.decode("utf-8", "replace").splitlines()
                 if l.strip() and not l.startswith("??")]
        return len(lines)
    except Exception:
        return -1


# (label, argv, needs_engine, how long before we call it stuck)
GATES = [
    ("tests",      [sys.executable, "-m", "pytest", "-q"], False, 900),
    ("validators", [sys.executable, "-m", "tools.uppercut_validate.cli", "all"],
     False, 600),
    ("golden",     [sys.executable, "-m", "tools.engine.golden", "--diff"],
     False, 600),
    ("research",   [sys.executable, "-m", "tools.research.cli", "validate"],
     False, 300),
    ("phase Q",    [sys.executable, "-m", "tools.engine.prove_core_range"],
     True, 1800),
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:20 UTC | START edit ]
    # Added 2026-08-08. Phase Q above answers "does Q's C++ still reproduce its
    # contract?" for exactly one phase. H, I, J, K, L and N had no such check at
    # all, and that gap is what let Phase N's C++ sit on the pre-Decision-0023
    # header for a day with a fully green suite - the Python side had migrated,
    # every Python-side guard agreed with itself, and nothing compared the two.
    #
    # It is slow, because it boots the editor once per phase and Phase K renders
    # a real world. That is the correct trade for a NIGHTLY: this is precisely
    # the class of drift nobody finds by looking, and the only way it gets found
    # is something running while nobody is looking.
    ("phase matrix", [sys.executable, "-m", "tools.engine.prove_phase"],
     True, 3600),
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:20 UTC | END edit ]
]


def run_gate(label, argv, needs_engine, timeout_s):
    """Returns (status, seconds, output). status is PASS / FAIL / SKIP."""
    killer = None
    if needs_engine:
        killer = WedgeKiller()
        killer.start()
    started = time.time()
    try:
        proc = subprocess.run(argv, cwd=REPO, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=timeout_s)
        text = proc.stdout.decode("utf-8", "replace")
        return ("PASS" if proc.returncode == 0 else "FAIL",
                time.time() - started, text)
    except subprocess.TimeoutExpired as exc:
        got = exc.output.decode("utf-8", "replace") if exc.output else ""
        return ("FAIL", time.time() - started,
                got + "\n[stuck: no result in %ds]" % timeout_s)
    finally:
        if killer is not None:
            killer.stop.set()


def interesting(label, text):
    """The lines worth waking somebody for, not the whole log."""
    lines = text.splitlines()
    if label == "tests":
        keep = [l for l in lines
                if l.startswith("FAILED") or l.startswith("ERROR")
                or " failed" in l or l.strip().startswith("E   ")]
        return keep[-40:]
    if label == "validators":
        return [l for l in lines if l.startswith("FAIL") or "RESULT" in l][-40:]
    if label == "golden":
        # Rendered as the tool renders it - which punch, at which tick - because
        # a drift reported as a changed hash tells nobody what changed.
        return [l for l in lines if l.strip()][-40:]
    if label == "phase Q":
        return [l for l in lines
                if l.startswith("DRIFT") or l.startswith("PROVEN")
                or l.strip().startswith("commandlet")
                or l.strip().startswith("contract")][-40:]
    if label == "phase matrix":
        # Keep the phase headings too, so a drift says WHICH phase without
        # anyone having to re-run it to find out.
        return [l for l in lines
                if l.startswith("Phase ")
                or l.strip().startswith("DRIFT")
                or l.strip().startswith("NO STREAM")
                or l.strip().startswith("MATCHED-BUT-INCOHERENT")
                or l.strip().startswith("HEADER ONLY")
                or l.strip().startswith("EVENT ROWS DIFFER")
                or l.strip().startswith("artifact")
                or l.strip().startswith("contract")][-40:]
    return [l for l in lines if l.strip()][-40:]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-engine", action="store_true",
                    help="skip gates that need Unreal")
    ap.add_argument("--out", default=None, help="also write the report here")
    args = ap.parse_args(argv)

    skip_engine = args.no_engine
    engine_reason = "--no-engine"
    if not skip_engine and editor_is_open():
        # Never compete with the Director's editor, and never kill it.
        skip_engine = True
        engine_reason = "the interactive editor is open"

    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say("Project Uppercut nightly verification")
    say("  branch  %s" % branch())
    say("  head    %s" % head())
    d = dirty()
    if d > 0:
        # Not a failure. But a green run against a dirty tree is a statement
        # about something that is not committed anywhere, and the report should
        # never let that pass unsaid.
        say("  tree    %d uncommitted change(s) - this run describes the "
            "WORKING TREE, not any commit" % d)
    elif d == 0:
        say("  tree    clean")
    say()

    failed, ran, skipped = [], 0, []
    for label, cmd, needs_engine, timeout_s in GATES:
        if needs_engine and skip_engine:
            skipped.append(label)
            say("SKIP %-11s (%s)" % (label, engine_reason))
            continue
        status, secs, text = run_gate(label, cmd, needs_engine, timeout_s)
        ran += 1
        say("%s %-11s %6.1fs" % (status, label, secs))
        if status != "PASS":
            failed.append(label)
            for l in interesting(label, text):
                say("     %s" % l)

    say()
    if failed:
        say("FAILED: %s" % ", ".join(failed))
    else:
        say("all %d gate(s) green%s"
            % (ran, (" - %s skipped" % ", ".join(skipped)) if skipped else ""))

    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 18:40 UTC | END ]
