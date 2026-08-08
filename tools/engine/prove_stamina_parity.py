# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 07:25 UTC | START ]
"""Decision 0021 step 5: Python and C++ must agree about the two-tier economy.

    python -m tools.engine.prove_stamina_parity

Runs the C++ economy over `tests/fixtures/stamina_vectors.json` and requires
every checkpoint and every endpoint to match EXACTLY, in q10000 integers.

Not "close enough at the end". An integer economy that agrees approximately has
already failed: a one-unit-per-tick drift reads correct at tick 1 and is a whole
round wrong by the twelfth, and an end-of-run total can hide a cancelling pair
of errors that a mid-run checkpoint cannot.

This mints NO integrated evidence. It is a unit contract for one subsystem, in
the same shape as the canon-hash parity proof, and it exists so the C++ can be
checked rather than read.
"""
import io
import json
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from tools.uppercut_stamina import economy as E  # noqa: E402
from tools.uppercut_stamina import vectors as V  # noqa: E402

ENGINE = os.environ.get("UPPERCUT_ENGINE", r"C:\Program Files\Epic Games\UE_5.8")
CMD = os.path.join(ENGINE, "Engine", "Binaries", "Win64", "UnrealEditor-Cmd.exe")
PROJECT = os.path.join(REPO, "sandbox", "UppercutSandbox.uproject")
OUT = os.path.join(REPO, "sandbox", "Saved", "stamina", "vectors_report.txt")
FIXTURE = os.path.join(REPO, "tests", "fixtures", "stamina_vectors.json")

from tools.engine.wedge import kill_the_wedge  # noqa: E402


def run_commandlet():
    if not os.path.exists(CMD):
        raise SystemExit("no engine at %s - set UPPERCUT_ENGINE" % CMD)
    if os.path.exists(OUT):
        os.remove(OUT)
    argv = [CMD, PROJECT, "-run=UppercutStaminaVectors", "-repo=%s" % REPO,
            "-out=%s" % OUT, "-unattended", "-nopause", "-nosplash"]
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    deadline = time.time() + 15 * 60
    while proc.poll() is None and time.time() < deadline:
        kill_the_wedge()
        time.sleep(2.0)
    if proc.poll() is None:
        proc.kill()
        raise SystemExit("the stamina-vectors run never finished")
    if not os.path.exists(OUT):
        raise SystemExit("the commandlet wrote no report")
    return io.open(OUT, encoding="utf-8").read()


def python_still_agrees_with_its_own_fixture():
    """Recompute every case from the contract and compare to the file.

    Without this, a fixture hand-edited to match a broken C++ implementation
    would pass: both sides would agree, and neither would be the contract. The
    fixture is a cache of the contract's answers, not a second authority.
    """
    data = json.load(io.open(FIXTURE, encoding="utf-8"))
    c = E.economy_pack()
    if c["errors"]:
        return ["the stamina canon does not satisfy its own contract: %s"
                % "; ".join(c["errors"])]

    problems = []
    fresh = {case["name"]: case for case in V.build()["cases"]}
    for case in data["cases"]:
        name = case["name"]
        again = fresh.get(name)
        if again is None:
            problems.append("%s is in the fixture but the generator no longer "
                            "produces it" % name)
            continue
        if again != case:
            problems.append("%s in the fixture differs from what the contract "
                            "computes now - regenerate it rather than editing "
                            "it" % name)
    for name in fresh:
        if not any(case["name"] == name for case in data["cases"]):
            problems.append("%s is generated but missing from the fixture" % name)
    return problems


def main():
    drift = python_still_agrees_with_its_own_fixture()
    if drift:
        print("THE FIXTURE NO LONGER MATCHES THE CONTRACT")
        for d in drift:
            print("  - %s" % d)
        print("\nPARITY FAILED")
        return 1
    print("fixture agrees with the Python contract")

    report = run_commandlet()
    print()
    print(report.rstrip())

    failed = "failed=0" not in report
    if failed:
        print("\nC++ did not reproduce the trajectories.")

    # A report that checked nothing is not a passing report. "failed=0" is
    # satisfiable by a commandlet that quietly found no cases at all.
    checked = 0
    for line in report.splitlines():
        if line.startswith("SUMMARY"):
            for part in line.split():
                if part.startswith("checked="):
                    checked = int(part.split("=")[1])
    expected = len(json.load(io.open(FIXTURE, encoding="utf-8"))["cases"])
    if checked < expected:
        print("\nthe report checked %d things against %d cases - too few for "
              "the trajectories to have run" % (checked, expected))
        failed = True

    print("\n%s" % ("PARITY FAILED" if failed else "PARITY PROVEN"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 07:25 UTC | END ]
