# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 13:36 UTC | START ]
"""The Phase G analyzer, proven against every defect it claims to catch.

Phase G is where the collision pipeline finally scores something, and that creates a
defect class neither Phase E nor Phase F could see: every stage individually correct
while the chain BETWEEN them is wrong. A run that resolved perfectly and then scored a
blocked punch, or scored a clean punch at a grazed punch's weight, hashes identically to
a correct one and passes every earlier check.

So the synthetic streams here are generated from canon the same way the Blueprint is
meant to compute them, and each test breaks exactly one link.
"""
from __future__ import annotations
import importlib.util
import pathlib
import random

_SPEC = importlib.util.spec_from_file_location(
    "analyze_fight_walker",
    pathlib.Path(__file__).resolve().parents[1] / "tools" / "engine" / "analyze_fight_walker.py")
afw = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(afw)

ROUND_TICKS = 40
ROUNDS = 3
ACTORS = 2
QI, QA = afw.QI, afw.QA
ORDER, QTHR, FORCE = afw.canon()
LANDED = ("clean", "solid", "grazed", "brushed")


def _stream(score_blocked=False, flat_force=False, own_clock=False,
            no_reset=False, leak=False, wrong_card=False, seed=7):
    """A canon-correct stream unless a defect flag says otherwise."""
    rng = random.Random(seed)
    lines = []
    total = ROUND_TICKS * ROUNDS
    acc = {i: 0.0 for i in range(ACTORS)}
    banked = {i: 0.0 for i in range(ACTORS)}
    for tick in range(1, total + 1):
        rnd, tir = divmod(tick - 1, ROUND_TICKS)
        for i in range(ACTORS):
            r1, r2, r3, a = (rng.random() for _ in range(4))
            q1, q2, q3, qa = (int(x * QI) for x in (r1, r2, r3, a))
            r1, r2, r3, a = q1 / QI, q2 / QI, q3 / QI, qa / QI
            cls = afw.expected_class(ORDER, QTHR, r1, r2, r3, a)
            name = ORDER[cls]
            if flat_force:
                gained = 1.0 if name in LANDED else 0.0
            elif score_blocked:
                gained = FORCE.get(name, 0.0) if name in LANDED else (
                    0.5 if name == "blocked" else 0.0)
            else:
                gained = FORCE[name] if name in LANDED else 0.0
            if tir == 0 and tick > 1 and not no_reset:
                banked[i] += acc[i]
                acc[i] = gained
            else:
                acc[i] += gained
            rr, tt = (0, tick - 1) if (own_clock and tick > ROUND_TICKS) else (rnd, tir)
            lines.append(f"F|{i}|{rr}|{tt}|{cls}|{q1}|{q2}|{q3}|{qa}|{round(acc[i]*QA)}")
            if leak and tick == total // 2:
                lines.append(f"S|{i}|{rnd}|{round(acc[i]*QA)}")
    if not leak:
        for i in range(ACTORS):
            total_banked = banked[i] + acc[i]
            if wrong_card:
                total_banked *= 1.5
            lines.append(f"S|{i}|{ROUNDS-1}|{round(total_banked*QA)}")
    return lines


def _errs(**kw):
    return afw.analyse(_stream(**kw), ROUND_TICKS, ROUNDS, "synthetic")["errors"]


def test_a_canon_correct_stream_passes():
    assert _errs() == []


def test_scoring_a_blocked_punch_is_caught():
    """The Phase G defect proper: the pipeline is right, the scoring is not. A blocked
    punch is a resolved outcome and contributes nothing to the card."""
    errs = _errs(score_blocked=True)
    assert any("pipeline and the scoring disagree" in e for e in errs)


def test_scoring_every_landed_punch_at_full_weight_is_caught():
    """A brushed punch scoring like a clean one. Contact quality is the whole point of
    the quality bands, and a flat weight quietly deletes them."""
    errs = _errs(flat_force=True)
    assert any("pipeline and the scoring disagree" in e for e in errs)


def test_a_blueprint_keeping_its_own_clock_is_caught():
    errs = _errs(own_clock=True)
    assert any("keeping its own clock" in e for e in errs)


def test_an_accumulator_that_never_resets_is_caught():
    errs = _errs(no_reset=True)
    assert any("rose across a round boundary" in e or
               "pipeline and the scoring disagree" in e for e in errs)


def test_a_leaked_card_is_caught():
    errs = _errs(leak=True)
    assert any("SEALED LEAK" in e for e in errs)


def test_a_card_that_does_not_follow_from_the_fight_is_caught():
    """The sealed total must be the sum of the banked rounds. A card that is merely
    deterministic and merely late is not thereby correct."""
    errs = _errs(wrong_card=True)
    assert any("does not follow from the fight" in e for e in errs)


def test_a_mislabelled_class_is_caught():
    """The Phase E guarantee, re-asserted here because Phase G depends on it."""
    lines = _stream()
    for n, ln in enumerate(lines):
        if ln.startswith("F|0|"):
            p = ln.split("|")
            p[4] = str((int(p[4]) + 1) % len(ORDER))
            lines[n] = "|".join(p)
            break
    errs = afw.analyse(lines, ROUND_TICKS, ROUNDS, "mislabelled")["errors"]
    assert any("canon gives" in e for e in errs)


def test_an_empty_stream_is_caught():
    assert any("nothing ran" in e
               for e in afw.analyse([], ROUND_TICKS, ROUNDS, "empty")["errors"])


def test_every_contact_class_must_occur():
    """A run that never produced a dodge has not exercised the pipeline, whatever the
    table promises about totality."""
    lines = [ln for ln in _stream()
             if not (ln.startswith("F|") and ln.split("|")[4] == str(ORDER.index("dodged")))]
    errs = afw.analyse(lines, ROUND_TICKS, ROUNDS, "no-dodges")["errors"]
    assert any("classes never produced" in e for e in errs)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 13:36 UTC | END ]
