# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:14 UTC | START ]
"""Phase E generator: BP_PipelineWalker - the collision model's four-stage resolution
pipeline executing inside the Blueprint VM.

This is the layer where a wrong answer is invisible without a harness. The pipeline is
a total ordered function: every attempt lands on exactly one of seven contact classes,
the sweep stage is INVERTED (its verdict fires when the answer is no), and active
evasion is ranked deliberately above guard interception. Any of those could be subtly
wrong in an implementation and still look plausible frame to frame.

Per tick, four draws from the actor's Blueprint stream stand in for the pipeline's
inputs, and the verdict is computed branchlessly, because exactly one case is true:

    r1 -> overlap    = r1 >= WhiffRate        (stage 0, inverted: no overlap -> whiffed)
    r2 -> evading    = r2 <  EvadeRate        (stage 1, ranked above guard)
    r3 -> intercept  = r3 <  GuardRate        (stage 2)
    a  -> alignment                            (stage 3, quality dispatch)

    qc  = ToInt(a>=Q1) + ToInt(a>=Q2) + ToInt(a>=Q3)
    cls = 6*whiffed + 5*dodged + 4*blocked + landed*(3 - qc)

Class indices are the canonical order of data/contact_classes.json
(clean 0, solid 1, grazed 2, brushed 3, blocked 4, dodged 5, whiffed 6), so the
analyzer can recompute every row against canon rather than against this file.

Marker: C|MyIndex|TickCount|cls|q(r1)|q(r2)|q(r3)|q(a) - the inputs travel with the
verdict precisely so the verdict can be re-derived and checked, not just hashed.
"""
import json, os, sys
import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bp_authoring as A
from bp_authoring import (G, wire, wire_exec, setpin, pin_of, steal_types,
                          marker_chain, quit_after, KML, KSL, lib, PL, EAL)

OUT = os.environ["UE_GEN_OUT"]
SEED = int(os.environ.get("UE_GEN_SEED", "56057345"))
MAX_TICKS = 2000
INSTANCES = 3

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
rep = {"errors": [], "table": {}}

WHIFF_RATE = 0.15
EVADE_RATE = 0.20
GUARD_RATE = 0.35


def canon():
    col = json.load(open(os.path.join(REPO, "data", "collision_model.json")))
    qb = sorted(col["quality_bands"], key=lambda q: q["min_alignment"])
    qthr = [float(q["min_alignment"]) for q in qb[1:]]
    cc = json.load(open(os.path.join(REPO, "data", "contact_classes.json")))["classes"]
    order = [c["key"] for c in cc]
    stages = [(s["order"], s["id"], s["verdict_if_true"]) for s in col["resolution_pipeline"]]
    stages.sort()
    rep["table"] = {"class_order": order, "quality_thresholds": qthr,
                    "pipeline": stages,
                    "rates": {"whiff": WHIFF_RATE, "evade": EVADE_RATE, "guard": GUARD_RATE}}
    # The generator encodes indices by position in contact_classes.json; if that file
    # is reordered, the Blueprint's arithmetic would silently mean something else.
    expect = ["clean", "solid", "grazed", "brushed", "blocked", "dodged", "whiffed"]
    if order != expect:
        raise RuntimeError("contact_classes order changed: %s" % order)
    if [s[2] for s in stages] != ["whiffed", "dodged", "blocked", "dispatch_quality_bands"]:
        raise RuntimeError("pipeline stage verdicts changed: %s" % stages)
    if len(qthr) != 3:
        raise RuntimeError("expected 3 quality thresholds, got %d" % len(qthr))
    return qthr


def build():
    qthr = canon()

    if EAL.does_directory_exist("/Game/PipeWalk"):
        EAL.delete_directory("/Game/PipeWalk")
    bp = lib.create_blueprint_asset_with_parent("/Game/PipeWalk/BP_PipelineWalker", unreal.Actor)
    A.step("bp", bp.get_name())

    g = A.activate(G(unreal.BlueprintGraphEditor.get_graph_editor(lib.find_event_graph(bp))))
    t_double, t_int, _ = steal_types(g)
    t_stream = lib.get_struct_type(unreal.RandomStream.static_struct())

    for nm in ("WhiffRate", "EvadeRate", "GuardRate", "Q1", "Q2", "Q3"):
        if not lib.add_member_variable(bp, nm, t_double):
            raise RuntimeError("add var failed: " + nm)
    for nm in ("TickCount", "MyIndex"):
        if not lib.add_member_variable(bp, nm, t_int):
            raise RuntimeError("add var failed: " + nm)
    if not lib.add_member_variable(bp, "Stream", t_stream):
        raise RuntimeError("add var failed: Stream")
    lib.set_blueprint_variable_instance_editable(bp, "MyIndex", True)
    A.step("vars", 9)

    ev_bp = g.absorb(lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint(-700, -700)))
    gi = g.getv("MyIndex"); mul = g.fn(KML + "Multiply_IntInt"); add = g.fn(KML + "Add_IntInt")
    gs = g.getv("Stream"); seed = g.fn(KML + "SetRandomStreamSeed")
    wire(gi, "MyIndex", mul, "A", "idx->mul"); setpin(mul, "B", "7919", "mul.B")
    wire(mul, "ReturnValue", add, "A", "mul->add"); setpin(add, "B", str(SEED), "add.B")
    wire(add, "ReturnValue", seed, "NewSeed", "add->seed")
    wire(gs, "Stream", seed, "Stream", "stream->seed")
    wire_exec(ev_bp, seed, "beginplay->seed")

    ev_t = g.absorb(lib.add_event_override(bp, "ReceiveTick", unreal.IntPoint(-700, 500)))

    def draw(tag):
        s = g.getv("Stream"); d = g.fn(KML + "RandomFloatFromStream")
        wire(s, "Stream", d, "Stream", "stream->" + tag)
        return d

    r1, r2, r3, al = draw("r1"), draw("r2"), draw("r3"), draw("align")

    def cmp_lt(a_node, a_pin, var, tag):
        gv = g.getv(var); c = g.fn(KML + "Less_DoubleDouble")
        wire(a_node, a_pin, c, "A", tag + ".A", strict=True)
        wire(gv, var, c, "B", tag + ".B", strict=True)
        return c

    def cmp_ge(a_node, a_pin, var, tag):
        gv = g.getv(var); c = g.fn(KML + "GreaterEqual_DoubleDouble")
        wire(a_node, a_pin, c, "A", tag + ".A", strict=True)
        wire(gv, var, c, "B", tag + ".B", strict=True)
        return c

    def to_int(b_node, tag):
        c = g.fn(KML + "Conv_BoolToInt")
        wire(b_node, "ReturnValue", c, "InBool", tag)
        return c

    def band(a_node, b_node, tag):
        n = g.fn(KML + "BooleanAND")
        wire(a_node, "ReturnValue", n, "A", tag + ".A")
        wire(b_node, "ReturnValue", n, "B", tag + ".B")
        return n

    # Stage 0 is INVERTED: the verdict fires when the sweep found nothing.
    no_overlap = cmp_lt(r1, "ReturnValue", "WhiffRate", "noOverlap")
    overlap = cmp_ge(r1, "ReturnValue", "WhiffRate", "overlap")
    # Stage 1 outranks stage 2 by construction: 'evading' consumes the attempt first.
    evading = band(cmp_lt(r2, "ReturnValue", "EvadeRate", "evade"), overlap, "evadeAnd")
    not_evading = cmp_ge(r2, "ReturnValue", "EvadeRate", "notEvade")
    reached = band(overlap, not_evading, "reachedAnd")
    blocked = band(cmp_lt(r3, "ReturnValue", "GuardRate", "guard"), reached, "blockAnd")
    landed = band(cmp_ge(r3, "ReturnValue", "GuardRate", "noGuard"), reached, "landAnd")
    A.step("stages", "sweep(inverted) -> evasion -> guard -> quality")

    # Stage 3: quality tiling, then class = 3 - qc so clean is 0 in canonical order.
    qc_parts = []
    for k, qv in enumerate(("Q1", "Q2", "Q3")):
        qc_parts.append(to_int(cmp_ge(al, "ReturnValue", qv, "q%d" % k), "q%d->int" % k))
    s1 = g.fn(KML + "Add_IntInt")
    wire(qc_parts[0], "ReturnValue", s1, "A", "qc0->s1.A")
    wire(qc_parts[1], "ReturnValue", s1, "B", "qc1->s1.B")
    qc = g.fn(KML + "Add_IntInt")
    wire(s1, "ReturnValue", qc, "A", "s1->qc.A")
    wire(qc_parts[2], "ReturnValue", qc, "B", "qc2->qc.B")
    # The A pin of a promotable Subtract refuses set_pin_value (B pins accept it).
    # Feed the constant from a literal node instead - proven to stick.
    lit3 = g.fn(KSL + "MakeLiteralInt")
    setpin(lit3, "Value", "3", "lit3")
    qcls = g.fn(KML + "Subtract_IntInt")
    wire(lit3, "ReturnValue", qcls, "A", "lit3->qcls.A")
    wire(qc, "ReturnValue", qcls, "B", "qc->qcls.B")

    # cls = 6*w + 5*e + 4*b + landed*(3 - qc). Exactly one term is non-zero.
    def scaled(bool_node, k, tag):
        i = to_int(bool_node, tag + ".toInt"); m = g.fn(KML + "Multiply_IntInt")
        wire(i, "ReturnValue", m, "A", tag + ".mul.A"); setpin(m, "B", str(k), tag + ".mul.B")
        return m

    t_w = scaled(no_overlap, 6, "whiff")
    t_e = scaled(evading, 5, "dodge")
    t_b = scaled(blocked, 4, "block")
    li = to_int(landed, "landed.toInt")
    t_l = g.fn(KML + "Multiply_IntInt")
    wire(li, "ReturnValue", t_l, "A", "landed->tl.A")
    wire(qcls, "ReturnValue", t_l, "B", "qcls->tl.B")

    a1 = g.fn(KML + "Add_IntInt")
    wire(t_w, "ReturnValue", a1, "A", "w->a1.A"); wire(t_e, "ReturnValue", a1, "B", "e->a1.B")
    a2 = g.fn(KML + "Add_IntInt")
    wire(a1, "ReturnValue", a2, "A", "a1->a2.A"); wire(t_b, "ReturnValue", a2, "B", "b->a2.B")
    cls = g.fn(KML + "Add_IntInt")
    wire(a2, "ReturnValue", cls, "A", "a2->cls.A"); wire(t_l, "ReturnValue", cls, "B", "l->cls.B")

    g_tc = g.getv("TickCount"); add_t = g.fn(KML + "Add_IntInt")
    wire(g_tc, "TickCount", add_t, "A", "tc->add.A"); setpin(add_t, "B", "1", "addT.B")
    set_tc = g.setv("TickCount")
    wire(add_t, "ReturnValue", set_tc, "TickCount", "addT->setTc")
    wire_exec(ev_t, set_tc, "tick->setTc")

    q_lit = g.fn(KSL + "MakeLiteralInt")
    setpin(q_lit, "Value", "65536", "q.lit")

    def quant(src, tag):
        m = g.fn(KML + "Multiply_DoubleDouble"); f = g.fn(KML + "FFloor")
        wire(src, "ReturnValue", m, "A", tag + ".A")
        wire(q_lit, "ReturnValue", m, "B", tag + ".B")
        wire(m, "ReturnValue", f, "A", tag + ".floor")
        return f

    q1n, q2n, q3n, qan = quant(r1, "q1"), quant(r2, "q2"), quant(r3, "q3"), quant(al, "qa")

    g_i2 = g.getv("MyIndex"); g_tc2 = g.getv("TickCount")
    pr = marker_chain(g, "C|", [(g_i2, "MyIndex"), (g_tc2, "TickCount"),
                                (cls, "ReturnValue"), (q1n, "ReturnValue"),
                                (q2n, "ReturnValue"), (q3n, "ReturnValue"),
                                (qan, "ReturnValue")], set_tc)
    quit_after(g, pr, g.getv("TickCount"), g.getv("MyIndex"), MAX_TICKS)

    if not lib.compile_blueprint(bp):
        raise RuntimeError("compile failed")
    A.step("compiled", True)

    cls_obj = EAL.load_blueprint_class("/Game/PipeWalk/BP_PipelineWalker")
    cdo = unreal.get_default_object(cls_obj)
    cdo.set_editor_property("WhiffRate", WHIFF_RATE)
    cdo.set_editor_property("EvadeRate", EVADE_RATE)
    cdo.set_editor_property("GuardRate", GUARD_RATE)
    cdo.set_editor_property("Q1", qthr[0])
    cdo.set_editor_property("Q2", qthr[1])
    cdo.set_editor_property("Q3", qthr[2])
    A.step("cdo", "thr=%s rates=%s" % (qthr, [WHIFF_RATE, EVADE_RATE, GUARD_RATE]))
    if not EAL.save_asset("/Game/PipeWalk/BP_PipelineWalker"):
        raise RuntimeError("save bp failed")

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not les.new_level_from_template("/Game/PipeWalk/L_PipeWalk",
                                       "/Engine/Maps/Templates/Template_Default"):
        raise RuntimeError("level template failed")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for i in range(INSTANCES):
        a = eas.spawn_actor_from_class(cls_obj, unreal.Vector(i * 300.0, 0.0, 0.0))
        a.set_editor_property("MyIndex", i)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    les.save_current_level()
    les.load_level("/Game/PipeWalk/L_PipeWalk")
    eas2 = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    n = len([a for a in eas2.get_all_level_actors()
             if a.get_class().get_name().startswith("BP_PipelineWalker")])
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
unreal.log("PIPEWALKER_GEN " + rep["result"])
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:14 UTC | END ]
