# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:20 UTC | START ]
"""Phase F generator: BP_BoutWalker - the bout STRUCTURE executing in the Blueprint VM.

Phases B, C, D and E each proved one subsystem reproducible in-engine: actor tick, the
canonical state machine, range bands with hysteresis, and the four-stage collision
pipeline. All four are things that happen *inside* a round. Nothing has executed the
round itself, and `match_flow` is the largest entry in the reference model's coverage
registry - the Phase 1A gate asks for complete matches, and the distance between a
proven exchange and a proven BOUT is this file.

Two claims are under test, and they fail differently:

  Rule 8/9 - one authoritative clock drives the round boundaries. The marker stream
      carries round and tick-within-round so the analyzer recomputes every boundary
      from the tick rather than trusting the Blueprint's own count.

  Rule 3  - the round card is SEALED, which hashing cannot test: a Blueprint printing
      the card every tick would hash perfectly and still leak. Two emission paths
      exist, observable `B|` every tick and sealed `S|` only past the final bell, and
      the analyzer asserts positionally that no S| precedes the last B|.

The accumulator banks and RESETS at each boundary, which is the reference model's
`_score_round` shape - that model once summed the bout to date instead, so an early
lead re-won every later round. Here that defect is a hard analyzer failure.

Markers:
  B|<idx>|<round>|<tickInRound>|<q20 RoundAcc>   observable, every tick
  S|<idx>|<round>|<q20 SealedTotal>              sealed, past the final bell only
"""
import json
import os
import sys

import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bp_authoring as A
from bp_authoring import (G, wire, wire_exec, setpin, pin_of, steal_types,
                          marker_chain, quit_after, KML, KSL, lib, PL, EAL)

OUT = os.environ["UE_GEN_OUT"]
SEED = int(os.environ.get("UE_GEN_SEED", "56057345"))
INSTANCES = 2

# Short rounds: the structure is under test, not endurance. Three rounds of 240 ticks
# crosses two boundaries and one final bell inside the runner's timeout.
ROUND_TICKS = 240
ROUNDS = 3
TOTAL_TICKS = ROUND_TICKS * ROUNDS

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
rep = {"errors": [], "table": {}}


def canon():
    """Refuse to build if the clock, the machine or the event vocabulary has moved. A
    generator that silently keeps working after canon changes is worse than one that
    breaks, because its evidence goes on looking valid."""
    clock = json.load(open(os.path.join(REPO, "data", "clock_model.json")))
    hz = clock["authority"]["tick_rate_hz"]
    if hz != 60:
        raise RuntimeError("clock is no longer 60Hz: %s" % hz)
    cs = json.load(open(os.path.join(REPO, "data", "combat_states.json")))
    ids = [s["id"] for s in cs["machines"]["match_flow"]["states"]]
    for needed in ("round_active", "between_rounds", "bout_complete"):
        if needed not in ids:
            raise RuntimeError("match_flow lost state '%s'" % needed)
    ev = json.load(open(os.path.join(REPO, "schemas", "fight_event.schema.json")))
    types = set(ev["properties"]["type"]["enum"])
    for needed in ("round_start", "round_end", "judge_round_card", "bout_end"):
        if needed not in types:
            raise RuntimeError("fight_event lost type '%s'" % needed)
    rep["table"] = {"tick_rate_hz": hz, "round_ticks": ROUND_TICKS, "rounds": ROUNDS,
                    "total_ticks": TOTAL_TICKS, "match_flow_states": ids}


def build():
    canon()

    if EAL.does_directory_exist("/Game/BoutWalk"):
        EAL.delete_directory("/Game/BoutWalk")
    bp = lib.create_blueprint_asset_with_parent("/Game/BoutWalk/BP_BoutWalker", unreal.Actor)
    A.step("bp", bp.get_name())

    g = A.activate(G(unreal.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(bp))))
    t_double, t_int, _ = steal_types(g)
    t_stream = lib.get_struct_type(unreal.RandomStream.static_struct())

    # Zero is a member variable rather than a pin literal: promotable DOUBLE pins drop
    # floating literals (bp_authoring rule 6), and this one feeds a Select.
    for nm in ("RoundAcc", "SealedTotal", "Zero"):
        if not lib.add_member_variable(bp, nm, t_double):
            raise RuntimeError("add var failed: " + nm)
    for nm in ("TickCount", "MyIndex", "RoundTicks"):
        if not lib.add_member_variable(bp, nm, t_int):
            raise RuntimeError("add var failed: " + nm)
    if not lib.add_member_variable(bp, "Stream", t_stream):
        raise RuntimeError("add var failed: Stream")
    lib.set_blueprint_variable_instance_editable(bp, "MyIndex", True)
    A.step("vars", 7)

    ev_bp = g.absorb(lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint(-700, -900)))
    gi = g.getv("MyIndex")
    mul = g.fn(KML + "Multiply_IntInt")
    add = g.fn(KML + "Add_IntInt")
    gs = g.getv("Stream")
    seed = g.fn(KML + "SetRandomStreamSeed")
    wire(gi, "MyIndex", mul, "A", "idx->mul")
    setpin(mul, "B", "7919", "mul.B")
    wire(mul, "ReturnValue", add, "A", "mul->add")
    setpin(add, "B", str(SEED), "add.B")
    wire(add, "ReturnValue", seed, "NewSeed", "add->seed")
    wire(gs, "Stream", seed, "Stream", "stream->seed")
    wire_exec(ev_bp, seed, "beginplay->seed")

    ev_t = g.absorb(lib.add_event_override(bp, "ReceiveTick", unreal.IntPoint(-700, 500)))

    # TickCount += 1 first, so tick 1 is the first live tick.
    g_tc = g.getv("TickCount")
    add_t = g.fn(KML + "Add_IntInt")
    wire(g_tc, "TickCount", add_t, "A", "tc->add.A")
    setpin(add_t, "B", "1", "addT.B")
    set_tc = g.setv("TickCount")
    wire(add_t, "ReturnValue", set_tc, "TickCount", "addT->setTc")
    wire_exec(ev_t, set_tc, "tick->setTc")

    # round = (TickCount-1)/RoundTicks, tickInRound = (TickCount-1)%RoundTicks.
    # Subtract's A pin refuses set_pin_value on the promotable operator, so the
    # constant arrives from a literal node - proven in Phase E.
    lit1 = g.fn(KSL + "MakeLiteralInt")
    setpin(lit1, "Value", "1", "lit1")
    tc_now = g.getv("TickCount")
    zb = g.fn(KML + "Subtract_IntInt")
    wire(tc_now, "TickCount", zb, "A", "tc->zb.A", strict=True)
    wire(lit1, "ReturnValue", zb, "B", "lit1->zb.B", strict=True)

    g_rt = g.getv("RoundTicks")
    rnd = g.fn(KML + "Divide_IntInt")
    wire(zb, "ReturnValue", rnd, "A", "zb->rnd.A", strict=True)
    wire(g_rt, "RoundTicks", rnd, "B", "rt->rnd.B", strict=True)

    g_rt2 = g.getv("RoundTicks")
    tir = g.fn(KML + "Percent_IntInt")
    wire(zb, "ReturnValue", tir, "A", "zb->tir.A", strict=True)
    wire(g_rt2, "RoundTicks", tir, "B", "rt->tir.B", strict=True)
    A.step("round arithmetic", "round=(tc-1)/rt, tickInRound=(tc-1)%rt")

    # atBoundary = (tickInRound == 0) AND (TickCount > 1). Without the second term the
    # very first tick banks an empty round and shifts every card by one.
    lit0 = g.fn(KSL + "MakeLiteralInt")
    setpin(lit0, "Value", "0", "lit0")
    is_zero = g.fn(KML + "EqualEqual_IntInt")
    wire(tir, "ReturnValue", is_zero, "A", "tir->isZero.A", strict=True)
    wire(lit0, "ReturnValue", is_zero, "B", "lit0->isZero.B", strict=True)

    tc_g2 = g.getv("TickCount")
    lit1b = g.fn(KSL + "MakeLiteralInt")
    setpin(lit1b, "Value", "1", "lit1b")
    past_first = g.fn(KML + "Greater_IntInt")
    wire(tc_g2, "TickCount", past_first, "A", "tc->pf.A", strict=True)
    wire(lit1b, "ReturnValue", past_first, "B", "lit1b->pf.B", strict=True)

    at_boundary = g.fn(KML + "BooleanAND")
    wire(is_zero, "ReturnValue", at_boundary, "A", "isZero->bnd.A")
    wire(past_first, "ReturnValue", at_boundary, "B", "pastFirst->bnd.B")
    A.step("boundary", "tickInRound==0 AND TickCount>1")

    # Bank BEFORE the accumulator is overwritten. Exec order carries the correctness
    # here: set_sealed runs first, so its RoundAcc getter still reads the completed
    # round's total; set_acc then resets it.
    acc_for_bank = g.getv("RoundAcc")
    g_zero = g.getv("Zero")
    bank_sel = g.fn(KML + "SelectFloat")
    wire(acc_for_bank, "RoundAcc", bank_sel, "A", "acc->bank.A", strict=True)
    wire(g_zero, "Zero", bank_sel, "B", "zero->bank.B", strict=True)
    wire(at_boundary, "ReturnValue", bank_sel, "bPickA", "bnd->bank.pick")
    g_sealed = g.getv("SealedTotal")
    sealed_add = g.fn(KML + "Add_DoubleDouble")
    wire(g_sealed, "SealedTotal", sealed_add, "A", "sealed->add.A", strict=True)
    wire(bank_sel, "ReturnValue", sealed_add, "B", "bank->add.B", strict=True)
    set_sealed = g.setv("SealedTotal")
    wire(sealed_add, "ReturnValue", set_sealed, "SealedTotal", "add->setSealed", strict=True)
    wire_exec(set_tc, set_sealed, "setTc->setSealed")

    # RoundAcc := atBoundary ? draw : RoundAcc + draw
    st = g.getv("Stream")
    draw = g.fn(KML + "RandomFloatFromStream")
    wire(st, "Stream", draw, "Stream", "stream->draw")
    g_acc = g.getv("RoundAcc")
    acc_add = g.fn(KML + "Add_DoubleDouble")
    wire(g_acc, "RoundAcc", acc_add, "A", "acc->add.A", strict=True)
    wire(draw, "ReturnValue", acc_add, "B", "draw->add.B", strict=True)
    sel = g.fn(KML + "SelectFloat")
    wire(draw, "ReturnValue", sel, "A", "draw->sel.A", strict=True)
    wire(acc_add, "ReturnValue", sel, "B", "accAdd->sel.B", strict=True)
    wire(at_boundary, "ReturnValue", sel, "bPickA", "bnd->sel.pick")
    set_acc = g.setv("RoundAcc")
    wire(sel, "ReturnValue", set_acc, "RoundAcc", "sel->setAcc", strict=True)
    wire_exec(set_sealed, set_acc, "setSealed->setAcc")
    A.step("banking", "sealed banks the completed round, then RoundAcc resets")

    q_lit = g.fn(KSL + "MakeLiteralInt")
    setpin(q_lit, "Value", "1048576", "q.lit")

    def quant(src, pin, tag):
        m = g.fn(KML + "Multiply_DoubleDouble")
        f = g.fn(KML + "FFloor")
        wire(src, pin, m, "A", tag + ".A", strict=True)
        wire(q_lit, "ReturnValue", m, "B", tag + ".B")
        wire(m, "ReturnValue", f, "A", tag + ".floor")
        return f

    acc_read = g.getv("RoundAcc")
    q_acc = quant(acc_read, "RoundAcc", "qAcc")
    gi2 = g.getv("MyIndex")
    pr_obs = marker_chain(g, "B|", [(gi2, "MyIndex"), (rnd, "ReturnValue"),
                                    (tir, "ReturnValue"), (q_acc, "ReturnValue")],
                          set_acc, "observable")
    A.step("observable marker", "B|idx|round|tickInRound|q20(RoundAcc)")

    # The final bell. Sealed emission hangs off the TRUE branch, so the card is
    # physically unreachable before the last tick - the Rule 3 claim is a property of
    # the graph's shape, and the analyzer then confirms it positionally in the log.
    final_ge = g.fn(KML + "GreaterEqual_IntInt")
    tc_g3 = g.getv("TickCount")
    wire(tc_g3, "TickCount", final_ge, "A", "tc->final.A")
    setpin(final_ge, "B", str(TOTAL_TICKS), "final.B")
    br_final = g.branch()
    cond = lib.find_condition_pin(br_final)
    if not PL.try_create_connection(pin_of(final_ge, "ReturnValue", "out"), cond):
        raise RuntimeError("final bell -> branch refused")
    wire_exec(pr_obs, br_final, "obs->finalBranch")

    sealed_read = g.getv("SealedTotal")
    q_sealed = quant(sealed_read, "SealedTotal", "qSealed")
    gi3 = g.getv("MyIndex")
    rnd2 = g.fn(KML + "Divide_IntInt")
    zb2 = g.fn(KML + "Subtract_IntInt")
    lit1c = g.fn(KSL + "MakeLiteralInt")
    setpin(lit1c, "Value", "1", "lit1c")
    tc_g4 = g.getv("TickCount")
    g_rt3 = g.getv("RoundTicks")
    wire(tc_g4, "TickCount", zb2, "A", "tc->zb2.A", strict=True)
    wire(lit1c, "ReturnValue", zb2, "B", "lit1c->zb2.B", strict=True)
    wire(zb2, "ReturnValue", rnd2, "A", "zb2->rnd2.A", strict=True)
    wire(g_rt3, "RoundTicks", rnd2, "B", "rt->rnd2.B", strict=True)
    pr_sealed = marker_chain(g, "S|", [(gi3, "MyIndex"), (rnd2, "ReturnValue"),
                                       (q_sealed, "ReturnValue")], br_final, "sealed")
    A.step("sealed marker", "S|idx|round|q20(SealedTotal), gated behind the final bell")

    quit_after(g, pr_sealed, g.getv("TickCount"), g.getv("MyIndex"), TOTAL_TICKS)

    if not lib.compile_blueprint(bp):
        raise RuntimeError("compile failed")
    A.step("compiled", True)

    cls_obj = EAL.load_blueprint_class("/Game/BoutWalk/BP_BoutWalker")
    cdo = unreal.get_default_object(cls_obj)
    cdo.set_editor_property("RoundTicks", ROUND_TICKS)
    cdo.set_editor_property("Zero", 0.0)
    A.step("cdo", "RoundTicks=%d Zero=0.0" % ROUND_TICKS)
    if not EAL.save_asset("/Game/BoutWalk/BP_BoutWalker"):
        raise RuntimeError("save bp failed")

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not les.new_level_from_template("/Game/BoutWalk/L_BoutWalk",
                                       "/Engine/Maps/Templates/Template_Default"):
        raise RuntimeError("level template failed")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for i in range(INSTANCES):
        a = eas.spawn_actor_from_class(cls_obj, unreal.Vector(i * 300.0, 0.0, 0.0))
        a.set_editor_property("MyIndex", i)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    les.save_current_level()
    les.load_level("/Game/BoutWalk/L_BoutWalk")
    eas2 = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    n = len([a for a in eas2.get_all_level_actors()
             if a.get_class().get_name().startswith("BP_BoutWalker")])
    rep["persisted_actors"] = n
    if n != INSTANCES:
        raise RuntimeError("level persistence failed: %d/%d" % (n, INSTANCES))


try:
    build()
    rep["result"] = "OK"
except Exception:
    import traceback
    rep["result"] = "FAILED"
    rep["traceback"] = traceback.format_exc()

rep["steps"] = A.steps
with open(OUT, "w") as f:
    json.dump(rep, f, indent=1)
unreal.log("BOUTWALKER_GEN " + rep["result"])
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:20 UTC | END ]
