# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 13:42 UTC | START ]
"""Phase G generator: BP_FightWalker - a SCORED bout in the Blueprint VM.

Phase E proved the four-stage collision pipeline resolves correctly in-engine. Phase F
proved the bout structure - rounds off the authoritative clock, per-round banking, a
sealed card past the final bell. Neither connected them: E's verdicts scored nothing,
and F's card was fed by a raw draw standing in for offence.

This joins them, so the round card is computed from RESOLVED CONTACT. That creates a
defect class neither earlier phase could see - every stage individually correct while
the chain between them is wrong - and the analyzer recomputes the whole chain from canon
rather than trusting any number the Blueprint reports.

Per tick, per actor: four draws run the pipeline exactly as Phase E does it, the class
is computed branchlessly, and the delivered force fraction for that class is added to
the round accumulator. Non-landing classes contribute nothing, which is not a special
case in the graph - it falls out of the four equality tests being false.

    force = landed * (Fb*eq(qc,0) + Fg*eq(qc,1) + Fs*eq(qc,2) + Fc*eq(qc,3))

`landed` is already 0 for whiffed, dodged and blocked, so a blocked punch cannot score
even if a quality band matched. The force fractions come from
collision_model.quality_bands and are set on the CDO, so changing canon changes the
scoring without touching this file.

Marker: F|idx|round|tickInRound|cls|q16(r1)|q16(r2)|q16(r3)|q16(align)|q20(RoundAcc)
Sealed: S|idx|round|q20(SealedTotal)
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
ROUND_TICKS = 240
ROUNDS = 3
TOTAL_TICKS = ROUND_TICKS * ROUNDS

WHIFF_RATE, EVADE_RATE, GUARD_RATE = 0.15, 0.20, 0.35

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
rep = {"errors": [], "table": {}}


def canon():
    col = json.load(open(os.path.join(REPO, "data", "collision_model.json")))
    bands = sorted(col["quality_bands"], key=lambda q: q["min_alignment"])
    qthr = [float(b["min_alignment"]) for b in bands[1:]]
    force = [float(b["delivered_force_fraction"]) for b in bands]   # brushed..clean
    cc = json.load(open(os.path.join(REPO, "data", "contact_classes.json")))["classes"]
    order = [c["key"] for c in cc]
    expect = ["clean", "solid", "grazed", "brushed", "blocked", "dodged", "whiffed"]
    if order != expect:
        raise RuntimeError("contact_classes order changed: %s" % order)
    if [b["class"] for b in bands] != ["brushed", "grazed", "solid", "clean"]:
        raise RuntimeError("quality band order changed")
    if len(qthr) != 3:
        raise RuntimeError("expected 3 quality thresholds, got %d" % len(qthr))
    clock = json.load(open(os.path.join(REPO, "data", "clock_model.json")))
    if clock["authority"]["tick_rate_hz"] != 60:
        raise RuntimeError("clock is no longer 60Hz")
    rep["table"] = {"class_order": order, "quality_thresholds": qthr,
                    "delivered_force": force, "round_ticks": ROUND_TICKS,
                    "rounds": ROUNDS, "total_ticks": TOTAL_TICKS,
                    "rates": {"whiff": WHIFF_RATE, "evade": EVADE_RATE,
                              "guard": GUARD_RATE}}
    return qthr, force


def build():
    qthr, force = canon()

    if EAL.does_directory_exist("/Game/FightWalk"):
        EAL.delete_directory("/Game/FightWalk")
    bp = lib.create_blueprint_asset_with_parent("/Game/FightWalk/BP_FightWalker", unreal.Actor)
    A.step("bp", bp.get_name())

    g = A.activate(G(unreal.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(bp))))
    t_double, t_int, _ = steal_types(g)
    t_stream = lib.get_struct_type(unreal.RandomStream.static_struct())

    # R1..AL materialize the tick's four draws. A Blueprint pure node is re-evaluated
    # at every consumption site, and RandomFloatFromStream MUTATES the stream, so a
    # pure draw with N consumers advances the stream N times. Phase E survived that
    # only because its draws had few consumers and its one derived value, qc, had
    # exactly one; Phase G's scoring join adds four more consumers to qc and the
    # latent hazard became a live defect - the first run scored a clean punch as
    # nothing and a brushed punch as a grazed one while reporting both classes
    # correctly, because the class and the score were reading different draws.
    # Storing each draw once, in exec order, removes the whole class of question.
    dvars = ("WhiffRate", "EvadeRate", "GuardRate", "Q1", "Q2", "Q3",
             "Fb", "Fg", "Fs", "Fc", "RoundAcc", "SealedTotal", "Zero",
             "R1", "R2", "R3", "AL")
    for nm in dvars:
        if not lib.add_member_variable(bp, nm, t_double):
            raise RuntimeError("add var failed: " + nm)
    for nm in ("TickCount", "MyIndex", "RoundTicks"):
        if not lib.add_member_variable(bp, nm, t_int):
            raise RuntimeError("add var failed: " + nm)
    if not lib.add_member_variable(bp, "Stream", t_stream):
        raise RuntimeError("add var failed: Stream")
    lib.set_blueprint_variable_instance_editable(bp, "MyIndex", True)
    A.step("vars", len(dvars) + 4)

    ev_bp = g.absorb(lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint(-800, -900)))
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

    ev_t = g.absorb(lib.add_event_override(bp, "ReceiveTick", unreal.IntPoint(-800, 500)))

    g_tc = g.getv("TickCount")
    add_t = g.fn(KML + "Add_IntInt")
    wire(g_tc, "TickCount", add_t, "A", "tc->add.A")
    setpin(add_t, "B", "1", "addT.B")
    set_tc = g.setv("TickCount")
    wire(add_t, "ReturnValue", set_tc, "TickCount", "addT->setTc")
    wire_exec(ev_t, set_tc, "tick->setTc")

    # ---- round arithmetic (Phase F) --------------------------------------
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
    A.step("round arithmetic", "round=(tc-1)/rt, boundary=tir==0 AND tc>1")

    # ---- the four draws, taken ONCE and stored ---------------------------
    # Each Set node sits in the exec chain, so the stream advances exactly four times
    # per tick in a defined order. Everything downstream reads the variables.
    prev_exec = set_tc
    for var in ("R1", "R2", "R3", "AL"):
        s = g.getv("Stream")
        d = g.fn(KML + "RandomFloatFromStream")
        wire(s, "Stream", d, "Stream", "stream->" + var)
        sv = g.setv(var)
        wire(d, "ReturnValue", sv, var, "draw->set" + var, strict=True)
        wire_exec(prev_exec, sv, "exec->set" + var)
        prev_exec = sv
    A.step("draws", "R1,R2,R3,AL stored once per tick in exec order")

    def rd(var):
        """A fresh getter for a stored draw. Variable reads are free of the pure-node
        re-evaluation hazard that made the first Phase G run score the wrong band."""
        return g.getv(var), var

    def cmp_lt(node, pin, var, tag):
        gv = g.getv(var)
        c = g.fn(KML + "Less_DoubleDouble")
        wire(node, pin, c, "A", tag + ".A", strict=True)
        wire(gv, var, c, "B", tag + ".B", strict=True)
        return c

    def cmp_ge(node, pin, var, tag):
        gv = g.getv(var)
        c = g.fn(KML + "GreaterEqual_DoubleDouble")
        wire(node, pin, c, "A", tag + ".A", strict=True)
        wire(gv, var, c, "B", tag + ".B", strict=True)
        return c

    def to_int(node, tag):
        c = g.fn(KML + "Conv_BoolToInt")
        wire(node, "ReturnValue", c, "InBool", tag)
        return c

    def band(a_node, b_node, tag):
        n = g.fn(KML + "BooleanAND")
        wire(a_node, "ReturnValue", n, "A", tag + ".A")
        wire(b_node, "ReturnValue", n, "B", tag + ".B")
        return n

    no_overlap = cmp_lt(*rd("R1"), "WhiffRate", "noOverlap")
    overlap = cmp_ge(*rd("R1"), "WhiffRate", "overlap")
    evading = band(cmp_lt(*rd("R2"), "EvadeRate", "evade"), overlap, "evadeAnd")
    not_evading = cmp_ge(*rd("R2"), "EvadeRate", "notEvade")
    reached = band(overlap, not_evading, "reachedAnd")
    blocked = band(cmp_lt(*rd("R3"), "GuardRate", "guard"), reached, "blockAnd")
    landed = band(cmp_ge(*rd("R3"), "GuardRate", "noGuard"), reached, "landAnd")

    qc_parts = []
    for k, qv in enumerate(("Q1", "Q2", "Q3")):
        qc_parts.append(to_int(cmp_ge(*rd("AL"), qv, "q%d" % k), "q%d->int" % k))
    s1 = g.fn(KML + "Add_IntInt")
    wire(qc_parts[0], "ReturnValue", s1, "A", "qc0->s1.A")
    wire(qc_parts[1], "ReturnValue", s1, "B", "qc1->s1.B")
    qc = g.fn(KML + "Add_IntInt")
    wire(s1, "ReturnValue", qc, "A", "s1->qc.A")
    wire(qc_parts[2], "ReturnValue", qc, "B", "qc2->qc.B")
    lit3 = g.fn(KSL + "MakeLiteralInt")
    setpin(lit3, "Value", "3", "lit3")
    qcls = g.fn(KML + "Subtract_IntInt")
    wire(lit3, "ReturnValue", qcls, "A", "lit3->qcls.A")
    wire(qc, "ReturnValue", qcls, "B", "qc->qcls.B")

    def scaled(bool_node, k, tag):
        i = to_int(bool_node, tag + ".toInt")
        m = g.fn(KML + "Multiply_IntInt")
        wire(i, "ReturnValue", m, "A", tag + ".mul.A")
        setpin(m, "B", str(k), tag + ".mul.B")
        return m

    t_w = scaled(no_overlap, 6, "whiff")
    t_e = scaled(evading, 5, "dodge")
    t_b = scaled(blocked, 4, "block")
    li = to_int(landed, "landed.toInt")
    t_l = g.fn(KML + "Multiply_IntInt")
    wire(li, "ReturnValue", t_l, "A", "landed->tl.A")
    wire(qcls, "ReturnValue", t_l, "B", "qcls->tl.B")
    a1 = g.fn(KML + "Add_IntInt")
    wire(t_w, "ReturnValue", a1, "A", "w->a1.A")
    wire(t_e, "ReturnValue", a1, "B", "e->a1.B")
    a2 = g.fn(KML + "Add_IntInt")
    wire(a1, "ReturnValue", a2, "A", "a1->a2.A")
    wire(t_b, "ReturnValue", a2, "B", "b->a2.B")
    cls = g.fn(KML + "Add_IntInt")
    wire(a2, "ReturnValue", cls, "A", "a2->cls.A")
    wire(t_l, "ReturnValue", cls, "B", "l->cls.B")
    A.step("pipeline", "sweep(inverted) -> evasion -> guard -> quality")

    # ---- the join: class -> delivered force ------------------------------
    # force = landed * (Fb*eq(qc,0) + Fg*eq(qc,1) + Fs*eq(qc,2) + Fc*eq(qc,3))
    # `landed` is already false for whiffed/dodged/blocked, so a blocked punch cannot
    # score even though its alignment still matched a band. That is the whole join
    # Phase E and Phase F each left untested.
    def eq_lit(node, k, tag):
        L = g.fn(KSL + "MakeLiteralInt")
        setpin(L, "Value", str(k), tag + ".lit")
        e = g.fn(KML + "EqualEqual_IntInt")
        wire(node, "ReturnValue", e, "A", tag + ".A", strict=True)
        wire(L, "ReturnValue", e, "B", tag + ".B", strict=True)
        return e

    def weighted(qc_node, k, var, tag):
        """Fx if qc == k else 0, without a branch: SelectFloat on the equality."""
        gv = g.getv(var)
        gz = g.getv("Zero")
        s = g.fn(KML + "SelectFloat")
        wire(gv, var, s, "A", tag + ".A", strict=True)
        wire(gz, "Zero", s, "B", tag + ".B", strict=True)
        wire(eq_lit(qc_node, k, tag), "ReturnValue", s, "bPickA", tag + ".pick")
        return s

    w0 = weighted(qc, 0, "Fb", "wBrushed")
    w1 = weighted(qc, 1, "Fg", "wGrazed")
    w2 = weighted(qc, 2, "Fs", "wSolid")
    w3 = weighted(qc, 3, "Fc", "wClean")
    fa = g.fn(KML + "Add_DoubleDouble")
    wire(w0, "ReturnValue", fa, "A", "w0->fa.A", strict=True)
    wire(w1, "ReturnValue", fa, "B", "w1->fa.B", strict=True)
    fb = g.fn(KML + "Add_DoubleDouble")
    wire(fa, "ReturnValue", fb, "A", "fa->fb.A", strict=True)
    wire(w2, "ReturnValue", fb, "B", "w2->fb.B", strict=True)
    fsum = g.fn(KML + "Add_DoubleDouble")
    wire(fb, "ReturnValue", fsum, "A", "fb->fsum.A", strict=True)
    wire(w3, "ReturnValue", fsum, "B", "w3->fsum.B", strict=True)
    # Gate by `landed`: a non-landing class contributes nothing.
    gz2 = g.getv("Zero")
    gained = g.fn(KML + "SelectFloat")
    wire(fsum, "ReturnValue", gained, "A", "fsum->gained.A", strict=True)
    wire(gz2, "Zero", gained, "B", "zero->gained.B", strict=True)
    wire(landed, "ReturnValue", gained, "bPickA", "landed->gained.pick")
    A.step("scoring join", "force = landed * band weight, gated on the resolved class")

    # ---- banking (Phase F) -----------------------------------------------
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
    wire_exec(prev_exec, set_sealed, "setAL->setSealed")

    g_acc = g.getv("RoundAcc")
    acc_add = g.fn(KML + "Add_DoubleDouble")
    wire(g_acc, "RoundAcc", acc_add, "A", "acc->accAdd.A", strict=True)
    wire(gained, "ReturnValue", acc_add, "B", "gained->accAdd.B", strict=True)
    sel = g.fn(KML + "SelectFloat")
    wire(gained, "ReturnValue", sel, "A", "gained->sel.A", strict=True)
    wire(acc_add, "ReturnValue", sel, "B", "accAdd->sel.B", strict=True)
    wire(at_boundary, "ReturnValue", sel, "bPickA", "bnd->sel.pick")
    set_acc = g.setv("RoundAcc")
    wire(sel, "ReturnValue", set_acc, "RoundAcc", "sel->setAcc", strict=True)
    wire_exec(set_sealed, set_acc, "setSealed->setAcc")

    # ---- markers ----------------------------------------------------------
    qi_lit = g.fn(KSL + "MakeLiteralInt")
    setpin(qi_lit, "Value", "65536", "qi.lit")
    qa_lit = g.fn(KSL + "MakeLiteralInt")
    setpin(qa_lit, "Value", "1048576", "qa.lit")

    def quant(src, pin, lit, tag):
        m = g.fn(KML + "Multiply_DoubleDouble")
        f = g.fn(KML + "FFloor")
        wire(src, pin, m, "A", tag + ".A", strict=True)
        wire(lit, "ReturnValue", m, "B", tag + ".B")
        wire(m, "ReturnValue", f, "A", tag + ".floor")
        return f

    q1n = quant(*rd("R1"), qi_lit, "q1")
    q2n = quant(*rd("R2"), qi_lit, "q2")
    q3n = quant(*rd("R3"), qi_lit, "q3")
    qan = quant(*rd("AL"), qi_lit, "qa")
    acc_read = g.getv("RoundAcc")
    q_acc = quant(acc_read, "RoundAcc", qa_lit, "qAcc")

    gi2 = g.getv("MyIndex")
    pr_obs = marker_chain(g, "F|", [(gi2, "MyIndex"), (rnd, "ReturnValue"),
                                    (tir, "ReturnValue"), (cls, "ReturnValue"),
                                    (q1n, "ReturnValue"), (q2n, "ReturnValue"),
                                    (q3n, "ReturnValue"), (qan, "ReturnValue"),
                                    (q_acc, "ReturnValue")], set_acc, "observable")
    A.step("observable marker", "F|idx|round|tir|cls|q16 x4|q20(RoundAcc)")

    final_ge = g.fn(KML + "GreaterEqual_IntInt")
    tc_g3 = g.getv("TickCount")
    wire(tc_g3, "TickCount", final_ge, "A", "tc->final.A")
    setpin(final_ge, "B", str(TOTAL_TICKS), "final.B")
    br_final = g.branch()
    cond = lib.find_condition_pin(br_final)
    if not PL.try_create_connection(pin_of(final_ge, "ReturnValue", "out"), cond):
        raise RuntimeError("final bell -> branch refused")
    wire_exec(pr_obs, br_final, "obs->finalBranch")

    # The final round is banked into the card at the bell, so the sealed total is the
    # sum of every round including the last - which is what the analyzer recomputes.
    g_sealed2 = g.getv("SealedTotal")
    g_acc2 = g.getv("RoundAcc")
    card = g.fn(KML + "Add_DoubleDouble")
    wire(g_sealed2, "SealedTotal", card, "A", "sealed->card.A", strict=True)
    wire(g_acc2, "RoundAcc", card, "B", "acc->card.B", strict=True)
    q_card = quant(card, "ReturnValue", qa_lit, "qCard")
    gi3 = g.getv("MyIndex")
    zb2 = g.fn(KML + "Subtract_IntInt")
    lit1c = g.fn(KSL + "MakeLiteralInt")
    setpin(lit1c, "Value", "1", "lit1c")
    tc_g4 = g.getv("TickCount")
    wire(tc_g4, "TickCount", zb2, "A", "tc->zb2.A", strict=True)
    wire(lit1c, "ReturnValue", zb2, "B", "lit1c->zb2.B", strict=True)
    rnd2 = g.fn(KML + "Divide_IntInt")
    g_rt3 = g.getv("RoundTicks")
    wire(zb2, "ReturnValue", rnd2, "A", "zb2->rnd2.A", strict=True)
    wire(g_rt3, "RoundTicks", rnd2, "B", "rt->rnd2.B", strict=True)
    pr_sealed = marker_chain(g, "S|", [(gi3, "MyIndex"), (rnd2, "ReturnValue"),
                                       (q_card, "ReturnValue")], br_final, "sealed")
    A.step("sealed marker", "S|idx|round|q20(SealedTotal+RoundAcc), behind the bell")

    quit_after(g, pr_sealed, g.getv("TickCount"), g.getv("MyIndex"), TOTAL_TICKS)

    if not lib.compile_blueprint(bp):
        raise RuntimeError("compile failed")
    A.step("compiled", True)

    cls_obj = EAL.load_blueprint_class("/Game/FightWalk/BP_FightWalker")
    cdo = unreal.get_default_object(cls_obj)
    cdo.set_editor_property("WhiffRate", WHIFF_RATE)
    cdo.set_editor_property("EvadeRate", EVADE_RATE)
    cdo.set_editor_property("GuardRate", GUARD_RATE)
    for k, v in zip(("Q1", "Q2", "Q3"), qthr):
        cdo.set_editor_property(k, v)
    for k, v in zip(("Fb", "Fg", "Fs", "Fc"), force):
        cdo.set_editor_property(k, v)
    cdo.set_editor_property("RoundTicks", ROUND_TICKS)
    cdo.set_editor_property("Zero", 0.0)
    A.step("cdo", "thr=%s force=%s rt=%d" % (qthr, force, ROUND_TICKS))
    if not EAL.save_asset("/Game/FightWalk/BP_FightWalker"):
        raise RuntimeError("save bp failed")

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not les.new_level_from_template("/Game/FightWalk/L_FightWalk",
                                       "/Engine/Maps/Templates/Template_Default"):
        raise RuntimeError("level template failed")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for i in range(INSTANCES):
        a = eas.spawn_actor_from_class(cls_obj, unreal.Vector(i * 300.0, 0.0, 0.0))
        a.set_editor_property("MyIndex", i)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    les.save_current_level()
    les.load_level("/Game/FightWalk/L_FightWalk")
    eas2 = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    n = len([a for a in eas2.get_all_level_actors()
             if a.get_class().get_name().startswith("BP_FightWalker")])
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
unreal.log("FIGHTWALKER_GEN " + rep["result"])
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 13:42 UTC | END ]
