# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 21:58 UTC | START ]
"""Generate STATUS.md from repository evidence, so no stable document ever needs to
carry a volatile number again.

Why this exists: an external review of 2026-08-03 found the README claiming 402 tests
and nine of eleven checks while the suite stood at 463 and eleven of eleven - and, in
the same breath, claiming all twelve Phase 1A steps defined AND steps 11-12 remaining.
The ROADMAP opened with "Phase 0: in progress" a day after phase0_status.md recorded
the gate as PASSED. None of it was lying when written; all of it was stale when read.
That is documentation's version of the declared-but-inert class this repository keeps
finding in its data: a hand-maintained copy of a value whose source of truth moved.

The fix is the same shape as the data fix: one source of truth, machines carrying it.
STATUS.md is GENERATED - run `python -m tools.gen_status` - and the stable documents
(README, ROADMAP, PROJECT_NOTES, PROJECT_PLAN) point here instead of restating counts.
tests/test_doc_drift.py refuses volatile tallies in the stable documents, so the only
place a number can go stale is a file whose header says it is a snapshot.

The generator RUNS the evidence rather than quoting it: pytest, every validator, and
the eleven required gate checks execute fresh. It is deliberately slow (~3 minutes);
a status file cheap enough to regenerate without thought would be cheap enough to
regenerate without the suite actually passing.
"""
from __future__ import annotations
import datetime
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def run(args: list, timeout: int = 600) -> tuple:
    p = subprocess.run(args, cwd=REPO, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:10 UTC | START edit: --check ]
def check() -> int:
    """Fail if STATUS.md's stated test count is not the tree's actual count.

    The 2026-08-07 state review named this gap: "STATUS.md freshness is not
    enforced by CI". It was half true. `test_status_is_current` runs in the
    suite and so does run in CI, but it allows 5% drift - and it must, because
    that test lives inside the suite this generator RUNS, so an exact check
    there fails during the very run that would fix it.

    CI has no such self-reference. It never regenerates, so it can afford to be
    exact, and exact is what stops STATUS.md drifting a few tests at a time
    until it is wrong by a fifth and nobody noticed the day it started.

    Uses --collect-only rather than a second full run: the suite has already
    executed by the time this step runs, and counting is not re-proving.

    It deliberately does NOT diff the whole file. STATUS.md embeds a generation
    timestamp and the head commit, so a byte comparison would fail on every
    green PR and teach everyone to ignore it - a gate that cries wolf is worse
    than no gate.
    """
    status_path = REPO / "STATUS.md"
    if not status_path.exists():
        print("STATUS.md is missing")
        return 1
    text = status_path.read_text(encoding="utf-8")

    m = re.search(r"Test suite \|\s*\*\*(\d+) passed\*\*", text)
    if not m:
        print("STATUS.md no longer states a test count in the expected form - "
              "either the generator's format changed and this check needs "
              "updating, or the file was hand-edited")
        return 1
    stated = int(m.group(1))

    _, out = run([sys.executable, "-m", "pytest", "-q", "--collect-only",
                  "-p", "no:cacheprovider"])
    c = re.search(r"(\d+) tests? collected", out) or \
        re.search(r"^(\d+) tests? collected", out, re.M)
    if not c:
        print("could not read a collection count from pytest")
        return 1
    actual = int(c.group(1))

    if stated != actual:
        print("STATUS.md says %d tests; the tree collects %d.\n"
              "Regenerate it and commit the result:\n"
              "    python -m tools.gen_status" % (stated, actual))
        return 1
    print("STATUS.md is current: %d tests" % stated)
    return 0
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 08:10 UTC | END edit ]


def main() -> int:
    if "--check" in sys.argv[1:]:
        return check()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    _, head = run(["git", "log", "-1", "--format=%h %s"])
    head = head.strip()

    # Bootstrap: the suite itself asserts STATUS.md exists and is generated, so a
    # first run (or a run after deleting it) must stub the file BEFORE running the
    # evidence, or the generator fails its own drift guard - which is exactly what
    # happened on this tool's first execution. The stub is immediately overwritten
    # with real results below; a crash in between leaves a file that says PENDING
    # rather than one that lies.
    status_path = REPO / "STATUS.md"
    if not status_path.exists():
        status_path.write_text(
            "<!-- GENERATED by tools/gen_status.py - do not hand-edit. -->\n\n"
            "# Status\n\nPENDING - generation in progress.\n",
            encoding="utf-8", newline="\n")

    code, out = run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"])
    m = re.search(r"(\d+) passed", out)
    tests = m.group(1) if m else "UNKNOWN"
    tests_ok = code == 0

    vcode, vout = run([sys.executable, "-m", "tools.uppercut_validate.cli", "all"])
    validators_ok = vcode == 0 and "RESULT: OK" in vout
    fails = [ln.strip() for ln in vout.splitlines() if ln.startswith("FAIL")]

    gcode, gout = run([sys.executable, "-c",
                       "from tools.uppercut_sim import checks;"
                       "e=checks.run_all();"
                       "print('CLEAN' if not e else chr(10).join(e))"])
    gate_ok = gcode == 0 and gout.strip().endswith("CLEAN")
    n_checks = len(__import__("tools.uppercut_sim.checks", fromlist=["ALL_CHECKS"]).ALL_CHECKS)

    probe = (REPO / "docs" / "phase1a" / "determinism_probe_results.md").read_text(
        encoding="utf-8")
    phases = re.findall(r"^## (Phase \w+[^\n]*?): PASS", probe, re.M)
    latest_phase = phases[-1] if phases else "none recorded"

    plan = (REPO / "docs" / "plans" / "next_steps.md")
    next_step = "see docs/plans/next_steps.md"
    if plan.exists():
        txt = plan.read_text(encoding="utf-8")
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 21:05 UTC | edit: Phase N ]
        # The chain is ordered newest-first and must stay that way: an external
        # review on 2026-08-04 found STATUS still naming slice item 8 as next
        # AFTER Phase N had completed it, because the newest marker had no link.
        # Adding a phase means adding its branch HERE, above the previous one.
        if "Phase N is proven" in txt:
            next_step = ("Slice item 9: one rendered round with knockdown, count, "
                         "stoppage and decision (C++)")
        elif "Phase L is proven" in txt:
            next_step = "Slice item 8: visible stamina and condition (C++)"
        elif "Phase K is proven" in txt:
            next_step = "Slice item 7: guard and slip (C++)"
        elif "Phase J is proven" in txt:
            next_step = ("Slice item 6: the four punches animated on generic fighters "
                         "- the first rendered slice")
        elif "Phase I is proven" in txt:
            next_step = "Slice item 5: real movement and swept collision (C++)"
        elif "Phase H is proven" in txt:
            next_step = "Slice item 4: the two-fighter authoritative loop in C++"
        elif "Referee profiles are consumed" in txt:
            next_step = "Phase H: the C++ core scaffold (Decision 0012 slice item 3)"
        elif "The Judge subsystem is extracted" in txt:
            next_step = "B (remaining): consume referee profiles"
        elif "Step A is done" in txt:
            next_step = "B. Extract the Judge subsystem"
        else:
            next_step = "A. Put attributes into the loop"

    ok = tests_ok and validators_ok and gate_ok
    lines = [
        "<!-- GENERATED by tools/gen_status.py - do not hand-edit. Regenerate with:",
        "     python -m tools.gen_status",
        "     Stable documents must not restate these numbers; tests/test_doc_drift.py",
        "     enforces that. -->",
        "",
        "# Status",
        "",
        f"Generated **{now}** at `{head}`.",
        "",
        f"| Evidence | Result |",
        f"|---|---|",
        f"| Test suite | **{tests} passed**" + ("" if tests_ok else " (FAILURES)") + " |",
        f"| Validators (`cli all`) | " + ("**all green**" if validators_ok
                                          else "**FAILING**: " + "; ".join(fails)) + " |",
        f"| Required Phase 1A gate checks | " + (f"**{n_checks} of {n_checks} green**"
                                                 if gate_ok else "**FAILING**") + " |",
        f"| Latest engine phase proven | {latest_phase} |",
        f"| Phase 0 | gate **PASSED** 2026-08-02 (`docs/phase0/phase0_status.md`) |",
        f"| Phase 1A | definitions complete for all twelve steps; the quality gate is "
        f"**not** passed - see `docs/phase1a/phase1a_status.md` |",
        f"| Next step | {next_step} (`docs/plans/next_steps.md`) |",
        "",
        "Open findings, named rather than rounded away:",
        "",
        "- Style balance is an open tuning item: drainer and showman sit below 30% on "
        "both seed bases (`docs/phase1a/attributes_in_the_loop.md`, \"Measured after\").",
        "- Visual readability (gate item 5) is now TESTABLE - the first rendered slice "
        "exists (Phase K) - but not judged: that call is the Director's, on the "
        "screenshots and live runs, not this file's.",
        "",
        "Standing decisions in force this sprint:",
        "",
        "- **Decision 0012** (2026-08-03): the Rule 22 C++ trigger fired for the fight "
        "core - C++ authoritative simulation, Blueprints presentation, Python tooling - "
        "and a document freeze holds for the slice sprint "
        "(`docs/decisions/0012-cpp-fight-core-and-slice-sprint-freeze.md`).",
        "",
    ]
    (REPO / "STATUS.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("\n".join(lines))
    print("WROTE STATUS.md", "OK" if ok else "WITH FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 21:58 UTC | END ]
