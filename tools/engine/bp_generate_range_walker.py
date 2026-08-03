# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:58 UTC | START ]
"""Phase D generator: BP_RangeWalker - canonical range-band resolution WITH HYSTERESIS
and collision quality-band dispatch, executing inside the Blueprint VM.

Why these two and not something easier: the hysteresis rule is *stateful* (the band
you are in decides the thresholds you must cross to leave it), so it cannot be faked
by a pure function and it is the structural anti-magnetic-correction statement of
data/movement_model.json. The quality dispatch is the collision model's tiling of
alignment [0,1] into brushed/grazed/solid/clean. Together they put ROADMAP steps 2
and 5 in the engine, which until now had canon and tests but no engine presence.

Same hard-won discipline as bp_generate_state_walker.py:
  1. Node handles resolved by BEFORE/AFTER delta, never by the returned handle.
  2. Every connection verified from the destination side; strict on value chains.
  3. Every set_pin_value read back.
  4. NO double literals on pins - get_basic_type_by_name lies and promotable DOUBLE
     pins do not retain literals. Every floating constant is a member variable set
     on the CDO, where set_editor_property is proven to stick.

Runtime per tick (all engine-side):
  r      = RandFloat(Stream)
  step   = (r - Half) * StepScale
  Dist   = FClamp(Dist + step, DistMin, DistMax)
  below  = Dist < (BandMin[Band] - Hyst)      <- leaving downward needs the extra Hyst
  above  = Dist > (BandMax[Band] + Hyst)      <- leaving upward likewise
  Band   = Clamp(Band + ToInt(above) - ToInt(below), 0, 4)
  a      = RandFloat(Stream)
  Qual   = ToInt(a>=Q1) + ToInt(a>=Q2) + ToInt(a>=Q3)
  marker R|MyIndex|TickCount|floor(Dist*65536)|Band|floor(a*65536)|Qual
Band and quality tables are read from canon at AUTHORING time and recorded in the report.
"""
import json, os
import unreal

OUT = os.environ["UE_GEN_OUT"]
SEED = int(os.environ.get("UE_GEN_SEED", "56057345"))
MAX_TICKS = 2000
INSTANCES = 3

lib = unreal.BlueprintEditorLibrary
GE = unreal.BlueprintGraphEditor
PL = unreal.BlueprintGraphPinLibrary
EAL = unreal.EditorAssetLibrary

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
rep = {"steps": [], "errors": [], "table": {}}


def step(m, v=None):
    rep["steps"].append(m if v is None else "%s -> %s" % (m, v))


# ---- canon -> flat tables ----
BIG = 99.0     # stands in for the open-ended out_of_range ceiling


def build_tables():
    mv = json.load(open(os.path.join(REPO, "data", "movement_model.json")))
    rb = mv["range_bands"]
    bands = rb["bands"]
    bmin = [float(b["min_ru"]) for b in bands]
    bmax = [BIG if b.get("max_ru") is None else float(b["max_ru"]) for b in bands]
    hyst = float(rb["hysteresis_ru"])

    col = json.load(open(os.path.join(REPO, "data", "collision_model.json")))
    qb = sorted(col["quality_bands"], key=lambda q: q["min_alignment"])
    # Thresholds are the interior boundaries: crossing each one promotes a class.
    qthr = [float(q["min_alignment"]) for q in qb[1:]]
    rep["table"] = {"bands": [b["key"] for b in bands], "band_min": bmin,
                    "band_max": bmax, "hysteresis": hyst,
                    "quality": [q["class"] for q in qb], "quality_thresholds": qthr}
    if len(bmin) != 5 or len(qthr) != 3:
        raise RuntimeError("canon shape changed: %d bands, %d thresholds"
                           % (len(bmin), len(qthr)))
    return bmin, bmax, hyst, qthr


# ---- verified graph authoring (identical discipline to bp_generate_state_walker.py) ----
class G:
    def __init__(self, ge):
        self.ge = ge
        self.seen = set(n.get_name() for n in ge.list_all_nodes())

    def _delta(self, what, klasses):
        now = {n.get_name(): n for n in self.ge.list_all_nodes()}
        new = [now[k] for k in now if k not in self.seen]
        self.seen = set(now)
        cands = [n for n in new if n.get_class().get_name() in klasses]
        if not cands:
            raise RuntimeError("%s: no new node of class %s among %d new"
                               % (what, klasses, len(new)))

        def suffix(n):
            tail = n.get_name().rsplit("_", 1)[-1]
            return int(tail) if tail.isdigit() else -1
        return max(cands, key=suffix)

    def fn(self, path):
        self.ge.add_call_function_node(path)
        return self._delta(path, ("K2Node_CallFunction", "K2Node_PromotableOperator",
                                  "K2Node_CallArrayFunction", "K2Node_GetArrayItem",
                                  "K2Node_CommutativeAssociativeBinaryOperator"))

    def getv(self, name):
        self.ge.add_get_member_variable_node(name)
        return self._delta("get " + name, ("K2Node_VariableGet",))

    def setv(self, name):
        self.ge.add_set_member_variable_node(name)
        return self._delta("set " + name, ("K2Node_VariableSet",))

    def branch(self):
        self.ge.add_branch_node()
        return self._delta("branch", ("K2Node_IfThenElse",))

    def absorb(self, node):
        self.seen.add(node.get_name())
        return node


def _pin_of(node, name, direction):
    finder = lib.find_output_pin if direction == "out" else lib.find_input_pin
    p = finder(node, name)
    if not PL.is_valid(p):
        raise RuntimeError("pin '%s' (%s) missing on %s" % (name, direction, node.get_name()))
    return p


def wire(src_node, src_pin, dst_node, dst_pin, label, strict=False):
    a = _pin_of(src_node, src_pin, "out")
    b = _pin_of(dst_node, dst_pin, "in")
    if not PL.try_create_connection(a, b):
        raise RuntimeError("connect refused: " + label)
    linked = PL.list_connected_pins(b)
    ok = any(PL.get_owning_node(lp).get_name() == src_node.get_name()
             and str(PL.get_pin_name(lp)) == src_pin
             for lp in linked)
    if not ok and strict:
        raise RuntimeError("STRICT wire got a conversion node: " + label)
    if not ok:
        for lp in linked:
            hop = PL.get_owning_node(lp)
            for i in range(6):
                try:
                    hp = lib.find_input_pin_by_index(hop, i)
                except Exception:
                    break
                if not PL.is_valid(hp):
                    break
                if any(PL.get_owning_node(x).get_name() == src_node.get_name()
                       and str(PL.get_pin_name(x)) == src_pin
                       for x in PL.list_connected_pins(hp)):
                    rep["steps"].append("autocast accepted: %s via %s" % (label, hop.get_name()))
                    if GG is not None:
                        GG.seen.add(hop.get_name())
                    return
        raise RuntimeError("connect VERIFY FAILED: " + label)


def wire_exec(src_node, dst_node, label):
    a = lib.find_then_pin(src_node)
    b = lib.find_execute_pin(dst_node)
    if not (PL.is_valid(a) and PL.is_valid(b)):
        raise RuntimeError("exec pins missing: " + label)
    if not PL.try_create_connection(a, b):
        raise RuntimeError("exec connect refused: " + label)
    if not any(PL.get_owning_node(lp).get_name() == src_node.get_name()
               for lp in PL.list_connected_pins(b)):
        raise RuntimeError("exec VERIFY FAILED: " + label)


def setpin(node, pin, value, label):
    p = _pin_of(node, pin, "in")
    if not PL.set_pin_value(p, value):
        raise RuntimeError("set_pin_value refused: " + label)
    back = str(PL.get_pin_value(p))
    if value.rstrip("0").rstrip(".") not in back and value not in back:
        raise RuntimeError("set_pin VERIFY FAILED %s: wrote %r read %r" % (label, value, back))


GG = None

KML = "/Script/Engine.KismetMathLibrary:"
KSL = "/Script/Engine.KismetSystemLibrary:"
KStr = "/Script/Engine.KismetStringLibrary:"
KArr = "/Script/Engine.KismetArrayLibrary:"


def build():
    bmin, bmax, hyst, qthr = build_tables()

    if EAL.does_directory_exist("/Game/RangeWalk"):
        EAL.delete_directory("/Game/RangeWalk")
    bp = lib.create_blueprint_asset_with_parent("/Game/RangeWalk/BP_RangeWalker", unreal.Actor)
    step("bp", bp.get_name())

    global GG
    g = G(GE.get_graph_editor(lib.find_event_graph(bp)))
    GG = g

    # Steal the REAL floating pin type from an engine pin; get_basic_type_by_name
    # returns an int-category "double" and silently truncates everything fed to it.
    tmp_sin = g.fn(KML + "Sin")
    t_double = PL.get_pin_type(_pin_of(tmp_sin, "ReturnValue", "out"))
    tmp_ri = g.fn(KML + "RandomIntegerFromStream")
    t_int = PL.get_pin_type(_pin_of(tmp_ri, "ReturnValue", "out"))
    g.ge.remove_nodes([tmp_sin, tmp_ri])
    g.seen.discard(tmp_sin.get_name()); g.seen.discard(tmp_ri.get_name())
    t_stream = lib.get_struct_type(unreal.RandomStream.static_struct())
    dbl_arr = lib.get_array_type(t_double)

    DVARS = ("Dist", "Hyst", "Half", "StepScale", "DistMin", "DistMax", "Q1", "Q2", "Q3")
    for nm in DVARS:
        if not lib.add_member_variable(bp, nm, t_double):
            raise RuntimeError("add var failed: " + nm)
    for nm in ("Band", "TickCount", "MyIndex"):
        if not lib.add_member_variable(bp, nm, t_int):
            raise RuntimeError("add var failed: " + nm)
    for nm in ("BandMin", "BandMax"):
        if not lib.add_member_variable(bp, nm, dbl_arr):
            raise RuntimeError("add var failed: " + nm)
    if not lib.add_member_variable(bp, "Stream", t_stream):
        raise RuntimeError("add var failed: Stream")
    lib.set_blueprint_variable_instance_editable(bp, "MyIndex", True)
    step("vars", len(DVARS) + 6)

    # BeginPlay: seed the stream engine-side (a Python-side draw would not advance it).
    ev_bp = g.absorb(lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint(-600, -600)))
    gi = g.getv("MyIndex"); mul = g.fn(KML + "Multiply_IntInt"); add = g.fn(KML + "Add_IntInt")
    gs = g.getv("Stream"); seed = g.fn(KML + "SetRandomStreamSeed")
    wire(gi, "MyIndex", mul, "A", "idx->mul"); setpin(mul, "B", "7919", "mul.B")
    wire(mul, "ReturnValue", add, "A", "mul->add"); setpin(add, "B", str(SEED), "add.B")
    wire(add, "ReturnValue", seed, "NewSeed", "add->seed")
    wire(gs, "Stream", seed, "Stream", "stream->seed")
    wire_exec(ev_bp, seed, "beginplay->seed")

    ev_t = g.absorb(lib.add_event_override(bp, "ReceiveTick", unreal.IntPoint(-600, 400)))

    # ---- distance walk: Dist = FClamp(Dist + (r - Half)*StepScale, DistMin, DistMax)
    gs2 = g.getv("Stream"); rf = g.fn(KML + "RandomFloatFromStream")
    wire(gs2, "Stream", rf, "Stream", "stream->randfloat")
    g_half = g.getv("Half"); sub = g.fn(KML + "Subtract_DoubleDouble")
    wire(rf, "ReturnValue", sub, "A", "r->sub.A", strict=True)
    wire(g_half, "Half", sub, "B", "half->sub.B", strict=True)
    g_ss = g.getv("StepScale"); mulf = g.fn(KML + "Multiply_DoubleDouble")
    wire(sub, "ReturnValue", mulf, "A", "sub->mul.A", strict=True)
    wire(g_ss, "StepScale", mulf, "B", "ss->mul.B", strict=True)
    g_d = g.getv("Dist"); addf = g.fn(KML + "Add_DoubleDouble")
    wire(g_d, "Dist", addf, "A", "dist->add.A", strict=True)
    wire(mulf, "ReturnValue", addf, "B", "step->add.B", strict=True)
    clampf = g.fn(KML + "FClamp")
    g_dmin = g.getv("DistMin"); g_dmax = g.getv("DistMax")
    wire(addf, "ReturnValue", clampf, "Value", "add->clamp.Value", strict=True)
    wire(g_dmin, "DistMin", clampf, "Min", "dmin->clamp.Min", strict=True)
    wire(g_dmax, "DistMax", clampf, "Max", "dmax->clamp.Max", strict=True)
    set_d = g.setv("Dist")
    wire(clampf, "ReturnValue", set_d, "Dist", "clamp->setDist", strict=True)
    wire_exec(ev_t, set_d, "tick->setDist")

    # ---- hysteresis band: leaving the current band costs the extra Hyst either way.
    # Pulled AFTER set_d executes, so every Dist read here is the new distance.
    g_bmin = g.getv("BandMin"); get_bmin = g.fn(KArr + "Array_Get")
    g_b1 = g.getv("Band")
    wire(g_bmin, "BandMin", get_bmin, "TargetArray", "bmin->arrget")
    wire(g_b1, "Band", get_bmin, "Index", "band->bmin.Index")
    g_h1 = g.getv("Hyst"); lo = g.fn(KML + "Subtract_DoubleDouble")
    wire(get_bmin, "Item", lo, "A", "bmin->lo.A", strict=True)
    wire(g_h1, "Hyst", lo, "B", "hyst->lo.B", strict=True)

    g_bmax = g.getv("BandMax"); get_bmax = g.fn(KArr + "Array_Get")
    g_b2 = g.getv("Band")
    wire(g_bmax, "BandMax", get_bmax, "TargetArray", "bmax->arrget")
    wire(g_b2, "Band", get_bmax, "Index", "band->bmax.Index")
    g_h2 = g.getv("Hyst"); hi = g.fn(KML + "Add_DoubleDouble")
    wire(get_bmax, "Item", hi, "A", "bmax->hi.A", strict=True)
    wire(g_h2, "Hyst", hi, "B", "hyst->hi.B", strict=True)

    g_d2 = g.getv("Dist"); below = g.fn(KML + "Less_DoubleDouble")
    wire(g_d2, "Dist", below, "A", "dist->below.A", strict=True)
    wire(lo, "ReturnValue", below, "B", "lo->below.B", strict=True)
    g_d3 = g.getv("Dist"); above = g.fn(KML + "Greater_DoubleDouble")
    wire(g_d3, "Dist", above, "A", "dist->above.A", strict=True)
    wire(hi, "ReturnValue", above, "B", "hi->above.B", strict=True)

    ib = g.fn(KML + "Conv_BoolToInt"); ia = g.fn(KML + "Conv_BoolToInt")
    wire(below, "ReturnValue", ib, "InBool", "below->int")
    wire(above, "ReturnValue", ia, "InBool", "above->int")
    delta = g.fn(KML + "Subtract_IntInt")
    wire(ia, "ReturnValue", delta, "A", "above->delta.A")
    wire(ib, "ReturnValue", delta, "B", "below->delta.B")
    g_b3 = g.getv("Band"); nb = g.fn(KML + "Add_IntInt")
    wire(g_b3, "Band", nb, "A", "band->nb.A")
    wire(delta, "ReturnValue", nb, "B", "delta->nb.B")
    clampi = g.fn(KML + "Clamp")
    wire(nb, "ReturnValue", clampi, "Value", "nb->clampi.Value")
    setpin(clampi, "Min", "0", "clampi.Min")
    setpin(clampi, "Max", str(len(bmin) - 1), "clampi.Max")
    set_b = g.setv("Band")
    wire(clampi, "ReturnValue", set_b, "Band", "clampi->setBand")
    wire_exec(set_d, set_b, "setDist->setBand")

    # ---- quality dispatch: branchless tiling of alignment into the four classes.
    gs3 = g.getv("Stream"); align = g.fn(KML + "RandomFloatFromStream")
    wire(gs3, "Stream", align, "Stream", "stream->align")
    qi = []
    for k, qv in enumerate(("Q1", "Q2", "Q3")):
        g_q = g.getv(qv); ge_q = g.fn(KML + "GreaterEqual_DoubleDouble")
        wire(align, "ReturnValue", ge_q, "A", "align->q%d.A" % k, strict=True)
        wire(g_q, qv, ge_q, "B", "%s->q%d.B" % (qv, k), strict=True)
        cv = g.fn(KML + "Conv_BoolToInt")
        wire(ge_q, "ReturnValue", cv, "InBool", "q%d->int" % k)
        qi.append(cv)
    qs1 = g.fn(KML + "Add_IntInt")
    wire(qi[0], "ReturnValue", qs1, "A", "q0->sum.A")
    wire(qi[1], "ReturnValue", qs1, "B", "q1->sum.B")
    qsum = g.fn(KML + "Add_IntInt")
    wire(qs1, "ReturnValue", qsum, "A", "sum1->sum.A")
    wire(qi[2], "ReturnValue", qsum, "B", "q2->sum.B")

    g_tc = g.getv("TickCount"); add_t = g.fn(KML + "Add_IntInt")
    wire(g_tc, "TickCount", add_t, "A", "tc->add.A"); setpin(add_t, "B", "1", "addT.B")
    set_tc = g.setv("TickCount")
    wire(add_t, "ReturnValue", set_tc, "TickCount", "addT->setTc")
    wire_exec(set_b, set_tc, "setBand->setTc")

    # ---- marker R|idx|tick|qDist|band|qAlign|qual
    # Integer quantization because BP float->string truncates; the int literal feeding
    # the multiply is a MakeLiteralInt node, since promotable DOUBLE pins drop literals.
    q_lit = g.fn(KSL + "MakeLiteralInt")
    setpin(q_lit, "Value", "65536", "q.lit")
    g_d4 = g.getv("Dist")
    qd_m = g.fn(KML + "Multiply_DoubleDouble"); qd_f = g.fn(KML + "FFloor")
    wire(g_d4, "Dist", qd_m, "A", "dist->qd.A")
    wire(q_lit, "ReturnValue", qd_m, "B", "lit->qd.B")
    wire(qd_m, "ReturnValue", qd_f, "A", "qd->floor")
    qa_m = g.fn(KML + "Multiply_DoubleDouble"); qa_f = g.fn(KML + "FFloor")
    wire(align, "ReturnValue", qa_m, "A", "align->qa.A")
    wire(q_lit, "ReturnValue", qa_m, "B", "lit->qa.B")
    wire(qa_m, "ReturnValue", qa_f, "A", "qa->floor")

    g_i2 = g.getv("MyIndex"); g_tc2 = g.getv("TickCount"); g_b4 = g.getv("Band")
    parts = [g.fn(KStr + "BuildString_Int") for _ in range(6)]
    setpin(parts[0], "AppendTo", "R|", "s0.prefix")
    wire(g_i2, "MyIndex", parts[0], "InInt", "idx->s0")
    for k in range(5):
        setpin(parts[k], "Suffix", "|", "s%d.suffix" % k)
        wire(parts[k], "ReturnValue", parts[k + 1], "AppendTo", "s%d->s%d" % (k, k + 1))
    wire(g_tc2, "TickCount", parts[1], "InInt", "tc->s1")
    wire(qd_f, "ReturnValue", parts[2], "InInt", "qDist->s2")
    wire(g_b4, "Band", parts[3], "InInt", "band->s3")
    wire(qa_f, "ReturnValue", parts[4], "InInt", "qAlign->s4")
    wire(qsum, "ReturnValue", parts[5], "InInt", "qual->s5")

    pr = g.fn(KSL + "PrintString")
    wire(parts[5], "ReturnValue", pr, "InString", "s5->print")
    setpin(pr, "bPrintToScreen", "false", "pr.screen")
    setpin(pr, "bPrintToLog", "true", "pr.log")
    wire_exec(set_tc, pr, "setTc->print")

    g_tc3 = g.getv("TickCount"); g_i3 = g.getv("MyIndex")
    ge_i = g.fn(KML + "GreaterEqual_IntInt"); eq_i = g.fn(KML + "EqualEqual_IntInt")
    an = g.fn(KML + "BooleanAND"); br = g.branch(); qn = g.fn(KSL + "QuitGame")
    wire(g_tc3, "TickCount", ge_i, "A", "tc->ge.A"); setpin(ge_i, "B", str(MAX_TICKS), "ge.B")
    wire(g_i3, "MyIndex", eq_i, "A", "idx->eq.A"); setpin(eq_i, "B", "0", "eq.B")
    wire(ge_i, "ReturnValue", an, "A", "ge->and.A")
    wire(eq_i, "ReturnValue", an, "B", "eq->and.B")
    cond = lib.find_condition_pin(br)
    if not PL.try_create_connection(_pin_of(an, "ReturnValue", "out"), cond):
        raise RuntimeError("and->branch refused")
    wire_exec(pr, br, "print->branch")
    wire_exec(br, qn, "branch->quit")

    if not lib.compile_blueprint(bp):
        raise RuntimeError("compile failed")
    step("compiled", True)

    # Constants land on the CDO, never on pins: set_editor_property is proven to stick
    # for doubles and arrays, and promotable DOUBLE pins are proven not to.
    cls = EAL.load_blueprint_class("/Game/RangeWalk/BP_RangeWalker")
    cdo = unreal.get_default_object(cls)
    cdo.set_editor_property("BandMin", bmin)
    cdo.set_editor_property("BandMax", bmax)
    cdo.set_editor_property("Hyst", hyst)
    cdo.set_editor_property("Half", 0.5)
    cdo.set_editor_property("StepScale", 0.08)
    cdo.set_editor_property("DistMin", 0.0)
    cdo.set_editor_property("DistMax", 2.0)
    cdo.set_editor_property("Q1", qthr[0])
    cdo.set_editor_property("Q2", qthr[1])
    cdo.set_editor_property("Q3", qthr[2])
    cdo.set_editor_property("Dist", 0.9)      # start in 'mid', mid-band
    cdo.set_editor_property("Band", 2)
    step("cdo", "bands=%s thr=%s hyst=%s" % (bmin, qthr, hyst))
    if not EAL.save_asset("/Game/RangeWalk/BP_RangeWalker"):
        raise RuntimeError("save bp failed")

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not les.new_level_from_template("/Game/RangeWalk/L_RangeWalk",
                                       "/Engine/Maps/Templates/Template_Default"):
        raise RuntimeError("level template failed")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for i in range(INSTANCES):
        a = eas.spawn_actor_from_class(cls, unreal.Vector(i * 300.0, 0.0, 0.0))
        a.set_editor_property("MyIndex", i)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    les.save_current_level()
    les.load_level("/Game/RangeWalk/L_RangeWalk")
    eas2 = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    n = len([a for a in eas2.get_all_level_actors()
             if a.get_class().get_name().startswith("BP_RangeWalker")])
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

with open(OUT, "w") as f:
    json.dump(rep, f, indent=1)
unreal.log("RANGEWALKER_GEN " + rep["result"])
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:58 UTC | END ]
