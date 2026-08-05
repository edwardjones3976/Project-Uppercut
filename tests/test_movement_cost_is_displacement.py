# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 01:30 UTC | START ]
"""Decision 0014 (gate G1): movement is priced by displacement.

A step was priced twice in canon, 4.55x apart, and the core read the higher one.
These tests hold the ruling in place: one authority, a derived echo that cannot
drift from it, a flat fee that may exist only under a named explosive action, and
the two behavioural consequences the ruling states in words - zero displacement
costs zero, and a shorter stride costs less.

Scope note, because it looks like an omission otherwise: this applies to the
Phase O contract onward. Phases L and N are SEALED evidence of determinism proofs
taken on 2026-08-03 and 2026-08-04, with C++ artifacts proven byte-identical to
them. Retro-fitting a canon ruling into sealed evidence would not update the
proof, it would destroy it. Their pinned hashes are asserted elsewhere and are
expected to stay exactly where they are.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "engine"))
sys.path.insert(0, ROOT)

import analyze_core_round as O  # noqa: E402


def _moves():
    p = os.path.join(ROOT, "data", "moves", "generic_sandbox_moves.json")
    return {m["id"]: m for m in json.load(io.open(p, encoding="utf-8"))["moves"]}


def _locomotion():
    p = os.path.join(ROOT, "data", "movement_model.json")
    mv = json.load(io.open(p, encoding="utf-8"))
    modes = {m["posture_mode"]: m for m in mv["locomotion"]["modes"]}
    return modes["boxing_steps"], mv["locomotion"]["directional"]


def test_the_ordinary_step_costs_what_the_authority_says_it_costs():
    step, _ = _locomotion()
    assert round(step["stride_length_ru"] * step["stamina_cost_per_ru"], 6) == 0.132


def test_the_move_table_echo_matches_the_authority():
    step, d = _locomotion()
    moves = _moves()
    for mid, key in (("step_in", "advance"), ("step_out", "retreat"),
                     ("step_lateral", "lateral")):
        want = round(step["stride_length_ru"]
                     * d[key + "_stride_multiplier"]
                     * step["stamina_cost_per_ru"], 6)
        assert round(moves[mid]["stamina_cost"], 6) == want, mid
        assert moves[mid]["cost_model"] == "displacement", mid


def test_no_ordinary_step_is_priced_flat():
    """The half of Decision 0014 that is enforceable today.

    The ruling permits a flat fee under a separately named explosive action - a
    committed lunge, a rope escape - but does not require one to be authored yet,
    and none is. What it forbids is a flat fee on an ordinary adjustment step,
    which is what 0.600 used to be. That is what this holds.
    """
    for mid, m in _moves().items():
        if m.get("category") == "step":
            assert m.get("cost_model") != "flat", (
                "%s is an ordinary step priced flat, which is the exact defect "
                "G1 closed" % mid)
        if m.get("category") == "explosive_step":
            assert m.get("cost_model") == "flat", (
                "%s is a named explosive action; if it is not priced flat it has "
                "no reason to be a separate move" % mid)


def test_the_contract_reads_the_authority_and_not_the_echo():
    """The pack must carry the per-ru price, or the core is back to two opinions."""
    c = O.canon_pack()
    step, _ = _locomotion()
    assert c["step_per_ru"] == O.q(step["stamina_cost_per_ru"])


def test_a_shorter_stride_costs_less():
    """Displacement pricing, in the one sentence that makes it observable.

    A retreat covers 0.78 of an advance, so it must cost 0.78 of an advance -
    not the same, which is what a flat fee said, and which is why retreating was
    as expensive as pressing forward for three phases.
    """
    c = O.canon_pack()
    def price(mult):
        return ((c["stride"] * mult) // 10000) * c["step_per_ru"] // 10000
    assert price(c["dir"]["retreat"]) < price(c["dir"]["advance"])
    assert price(c["dir"]["lateral"]) < price(c["dir"]["advance"])


def test_zero_displacement_costs_zero():
    """The ropes case, which is where this rule earns its keep.

    `rope_retreat_multiplier` is 0.0: with your back on the ropes a backward step
    buys nothing. If it still charged, the anti-running rule would double as a
    stamina tax on the fighter already in trouble, which is not what canon says
    it is for.
    """
    c = O.canon_pack()
    mul = (c["dir"]["retreat"] * c["rope_retreat"]) // 10000
    travelled = (c["stride"] * mul) // 10000
    assert travelled == 0
    assert (travelled * c["step_per_ru"]) // 10000 == 0


def test_the_stream_still_moves_fighters_after_the_repricing():
    """A cheaper step must not become a step that does nothing.

    The failure mode this guards is a fat-fingered refactor that prices the
    stride correctly and forgets to apply it - which would look like a healthier
    stamina curve and be a fighter standing still.
    """
    s = O.expected_stream(4242, 1, with_floats=False)
    trailer = next(l for l in s.splitlines() if l.startswith("S|"))
    f = dict(kv.split("=", 1) for kv in trailer.split("|")[1:])
    assert int(f["steps"]) > 0
    assert int(f["transitions"]) > 0, "no fighter changed range band all round"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 01:30 UTC | END ]
