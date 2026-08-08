# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 19:05 UTC | START ]
"""A verifier that cannot fail verifies nothing.

`tools/engine/nightly_verify.py` is the one command a scheduled task runs, and
its exit code is the whole answer. If its failure path ever stopped working,
every night would report green and nobody would learn anything until a release
- which is a worse position than having no nightly at all, because the green
would be believed.

So these check the mechanics rather than the gates: that a failing command is
reported FAIL, that a stuck one is cut off instead of waited on, and that a
passing one is reported PASS. They deliberately do NOT run the real gate list -
that would run pytest inside pytest and take minutes to re-prove what the gates
already prove themselves.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.engine import nightly_verify as NV  # noqa: E402


def test_a_failing_gate_is_reported_as_failed():
    status, _, _ = NV.run_gate(
        "tests", [sys.executable, "-c", "import sys; sys.exit(3)"], False, 60)
    assert status == "FAIL", (
        "a gate that exited non-zero was reported as %s - the nightly would "
        "have called a broken tree green" % status)


def test_a_stuck_gate_is_cut_off_rather_than_waited_on():
    """The failure mode that looks exactly like success: nothing ever returns."""
    status, secs, text = NV.run_gate(
        "tests", [sys.executable, "-c", "import time; time.sleep(30)"], False, 3)
    assert status == "FAIL"
    assert secs < 15, "the timeout did not cut the run off (%.1fs)" % secs
    assert "stuck" in text, "a timed-out gate must say so in its output"


def test_a_passing_gate_is_reported_as_passed():
    """The other half. A verifier that always fails is also useless."""
    status, _, _ = NV.run_gate("tests", [sys.executable, "-c", "pass"], False, 60)
    assert status == "PASS"


def test_every_gate_is_a_real_module():
    """A typo in the gate list would silently become a permanent FAIL."""
    for label, cmd, _needs_engine, _t in NV.GATES:
        assert cmd[:2] == [sys.executable, "-m"], (
            "gate %r is not invoked as a module: %s" % (label, cmd))
        mod = cmd[2]
        if mod == "pytest":
            continue
        path = os.path.join(ROOT, *mod.split(".")) + ".py"
        pkg = os.path.join(ROOT, *mod.split("."), "__init__.py")
        assert os.path.exists(path) or os.path.exists(pkg), (
            "gate %r runs %s, which does not exist" % (label, mod))


def test_the_engine_gate_is_marked_as_needing_the_engine():
    """If this flag were lost, a nightly run would fight the Director's editor."""
    engine_gates = [g[0] for g in NV.GATES if g[2]]
    assert engine_gates == ["phase Q"], (
        "the set of engine-dependent gates changed to %s - the skip rule and "
        "the wedge killer are wired to that flag" % engine_gates)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 19:05 UTC | END ]
