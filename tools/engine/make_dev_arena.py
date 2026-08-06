# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:30 UTC | START ]
"""Run the editor headless to author L_UppercutDevArena, and report honestly.

    python -m tools.engine.make_dev_arena

WHY PYTHON AND NOT A .ps1. Every PowerShell runner in this repository has the
same two failure modes when driven from an agent's spawn context: a mandatory
`param()` that fails to bind prompts on stdin and hangs forever, and Write-Host
goes to the information stream which `>` does not capture. Both look exactly
like "the run produced nothing", which is the worst failure mode available to
tooling that produces evidence.

THE TURNKEY WEDGE. Every editor boot on this machine spawns
`Build.bat -Mode=ValidatePlatforms`, which ping-loops and never returns; the
editor waits behind it indefinitely. It is killed continuously while the editor
works. See docs/phase1a/engine_setup_runbook.md.
"""
import io
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENGINE = os.environ.get("UPPERCUT_ENGINE", r"C:\Program Files\Epic Games\UE_5.8")
CMD = os.path.join(ENGINE, "Engine", "Binaries", "Win64", "UnrealEditor-Cmd.exe")
PROJECT = os.path.join(REPO, "sandbox", "UppercutSandbox.uproject")
SCRIPT = os.path.join(REPO, "tools", "engine", "build_dev_arena.py")
OUT = os.path.join(REPO, "sandbox", "Saved", "dev_arena.json")

PS_LIST = ("Get-CimInstance Win32_Process | "
           "ForEach-Object { $_.ProcessId.ToString() + '|' + $_.Name + '|' "
           "+ [string]$_.CommandLine }")


def kill_the_wedge():
    out = subprocess.run(["powershell", "-NoProfile", "-Command", PS_LIST],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in out.stdout.decode("utf-8", "replace").splitlines():
        low = line.lower()
        if "validateplatforms" in low or "|ping.exe|" in low:
            pid = line.split("|")[0].strip()
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Stop-Process -Id %s -Force -ErrorAction SilentlyContinue"
                            % pid])


def main() -> int:
    if not os.path.exists(CMD):
        print("no engine at %s - set UPPERCUT_ENGINE" % CMD)
        return 2
    if os.path.exists(OUT):
        os.remove(OUT)

    env = dict(os.environ)
    env["UE_ARENA_OUT"] = OUT
    argv = [CMD, PROJECT, "-run=pythonscript", "-script=%s" % SCRIPT,
            "-unattended", "-nopause", "-nosplash", "-NoLogTimes"]
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, env=env)

    deadline = time.time() + 15 * 60
    while proc.poll() is None and time.time() < deadline:
        kill_the_wedge()
        time.sleep(2.0)
    if proc.poll() is None:
        proc.kill()
        print("TIMEOUT - the editor never finished")
        return 3

    if not os.path.exists(OUT):
        print("NO REPORT WRITTEN - the run produced nothing")
        return 3
    report = json.load(io.open(OUT, encoding="utf-8"))
    for e in report.get("errors", []):
        print("ERROR %s" % e)
    for a in report.get("actors", []):
        print("  %-10s %s" % (a["kind"], a["name"]))
    print("%s saved=%s" % (report["map"], report.get("saved")))
    return 0 if (report.get("saved") and not report.get("errors")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:30 UTC | END ]
