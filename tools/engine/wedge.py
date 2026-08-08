# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 16:20 UTC | START ]
"""THE TURNKEY WEDGE, killed in one place.

Every editor boot on this machine spawns

    Build.bat -Mode=ValidatePlatforms

which ping-loops and never returns, and the commandlet waits behind it
indefinitely. The log simply stops after `TurnkeySupport`. See
docs/phase1a/engine_setup_runbook.md.

WHY THIS FILE EXISTS. The kill loop had been copied into four runners
(prove_canon_parity, prove_stamina_parity, prove_live_arena, make_dev_arena)
and was MISSING from the two that prove Phase Q and Phase R - which instead
called a blocking `subprocess.run` and simply waited. On 2026-08-07 a Phase Q
proof sat wedged for thirteen minutes and only finished because the wedge was
cleared by hand; Phase R then took under two.

Four copies of a rule and two places that should have had it and did not is the
exact shape this repository spends its discipline avoiding. One home, six
callers.

Killing the wedge is safe: it is Turnkey's own child process, never the
Director's editor. Nothing here touches a running UnrealEditor.exe.
"""
import io
import os
import subprocess
import tempfile
import time

# `$_` survives here because this string is handed to powershell.exe by
# subprocess, not through a tool layer that strips it.
PS_LIST = ("Get-CimInstance Win32_Process | "
           "ForEach-Object { $_.ProcessId.ToString() + '|' + $_.Name + '|' "
           "+ [string]$_.CommandLine }")


def kill_the_wedge():
    """Kill any ValidatePlatforms build and its PING child. Cheap; call often."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LIST],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    killed = 0
    for line in out.stdout.decode("utf-8", "replace").splitlines():
        low = line.lower()
        if "validateplatforms" in low or "|ping.exe|" in low:
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Stop-Process -Id %s -Force -ErrorAction SilentlyContinue"
                            % line.split("|")[0].strip()])
            killed += 1
    return killed


def run_editor(argv, timeout_s=900, label="the editor run"):
    """Run a commandlet to completion, clearing the wedge throughout.

    Returns the process's captured output as text.

    Output goes to a TEMP FILE rather than a pipe. Polling a Popen while its
    stdout pipe fills is a deadlock waiting for a verbose enough run, and the
    editor is verbose - which would reproduce the same symptom this function
    exists to remove ("the run produced nothing") by a different mechanism.
    """
    fd, logpath = tempfile.mkstemp(prefix="uppercut_editor_", suffix=".log")
    os.close(fd)
    try:
        with io.open(logpath, "wb") as log:
            proc = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT)
            deadline = time.time() + timeout_s
            while proc.poll() is None and time.time() < deadline:
                kill_the_wedge()
                time.sleep(2.0)
            if proc.poll() is None:
                proc.kill()
                raise SystemExit(
                    "%s never finished within %ds. The wedge killer was "
                    "running, so this is a different stall - check the tail of "
                    "%s before assuming Turnkey." % (label, timeout_s, logpath))
        with io.open(logpath, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    finally:
        try:
            os.remove(logpath)
        except OSError:
            pass
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 16:20 UTC | END ]
