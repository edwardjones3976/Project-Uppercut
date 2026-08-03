# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 01:52 UTC | START ]
"""Phase C generator: BP_StateWalker - the canonical fighter_action machine executing
inside the Blueprint VM, canon-driven from data/combat_states.json.

Hard-won discipline from the Acc autopsy (see determinism_probe_results.md):
  1. NEVER trust the handle returned by add_call_function_node - promotable operators
     get replaced and handles alias. Every node is resolved by BEFORE/AFTER DELTA of
     the graph's node list.
  2. NEVER trust try_create_connection's True - every connection is VERIFIED from the
     destination side (owning node + pin name) and the build fails loud on mismatch.
  3. Every set_pin_value is read back.

Runtime per tick (all engine-side): count = OutsCount[State]; draw = RandInt(Stream,count);
Next = OutsTarget[OutsOffset[State]+draw]; r = RandFloat(Stream); Acc += r + Sin(Acc);
marker W|MyIndex|TickCount|Next|floor(Acc*65536)|floor(r*65536); State = Next.
Transition tables are flattened from canon at AUTHORING time; the mapping is recorded
in the report JSON. 'stopped' resets to 'idle' (new bout), as in the Python probe.
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
def build_tables():
    doc = json.load(open(os.path.join(REPO, "data", "combat_states.json")))
    fa = doc["machines"]["fighter_action"]
    states = {s["id"]: s for s in fa["states"]}
    walk_states = sorted(sid for sid, s in states.items() if not s.get("provisioned"))
    idx = {sid: i for i, sid in enumerate(walk_states)}
    outs = {sid: [] for sid in walk_states}
    for t in sorted(fa["transitions"], key=lambda x: x["id"]):
        if t.get("provisioned") or t["to"] not in idx:
            continue
        if t["from"] == "*":
            excl = set(t.get("wildcard_excludes", []))
            srcs = [sid for sid in walk_states
                    if not states[sid].get("terminal") and sid not in excl]
        else:
            srcs = [t["from"]] if t["from"] in idx else []
        for s in srcs:
            outs[s].append(idx[t["to"]])
    for sid in walk_states:            # terminal / dead states reset to idle = new bout
        if not outs[sid]:
            outs[sid] = [idx["idle"]]
    offset, count, target = [], [], []
    for sid in walk_states:
        offset.append(len(target)); count.append(len(outs[sid])); target.extend(outs[sid])
    rep["table"] = {"states": walk_states, "offset": offset, "count": count,
                    "target": target, "idle": idx["idle"]}
    return offset, count, target, idx["idle"]


# ---- verified graph authoring ----
class G:
    def __init__(self, ge):
        self.ge = ge
        self.seen = set(n.get_name() for n in ge.list_all_nodes())

    def _delta(self, what, klasses):
        """Return the newest new node of an expected class; absorb everything else
        (e.g. autocast conversion nodes inserted by earlier wires)."""
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

    def absorb(self, node):     # for nodes created outside G (event overrides)
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
        # Strict wires (the Acc accumulation chain) tolerate NO inserted conversion
        # nodes: a conversion here means a type mismatch that can silently destroy
        # the value (the FTrunc-to-int lesson). Fail the build.
        raise RuntimeError("STRICT wire got a conversion node: " + label)
    if not ok:
        # Accept a single-hop autocast: the engine may insert a conversion node
        # between src and dst. Verify the hop genuinely originates at src.
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
                        # Absorb the conversion node immediately so it can never win
                        # a later delta race and alias someone else's handle.
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
    ok = any(PL.get_owning_node(lp).get_name() == src_node.get_name()
             for lp in PL.list_connected_pins(b))
    if not ok:
        raise RuntimeError("exec VERIFY FAILED: " + label)


def setpin(node, pin, value, label):
    p = _pin_of(node, pin, "in")
    if not PL.set_pin_value(p, value):
        raise RuntimeError("set_pin_value refused: " + label)
    back = str(PL.get_pin_value(p))
    if value.rstrip("0").rstrip(".") not in back and value not in back:
        raise RuntimeError("set_pin VERIFY FAILED %s: wrote %r read %r" % (label, value, back))


GG = None  # active G instance; wire() absorbs autocast nodes through it

KML = "/Script/Engine.KismetMathLibrary:"
KSL = "/Script/Engine.KismetSystemLibrary:"
KStr = "/Script/Engine.KismetStringLibrary:"
KArr = "/Script/Engine.KismetArrayLibrary:"


def build():
    offset, count, target, idle_idx = build_tables()

    if EAL.does_directory_exist("/Game/StateWalk"):
        EAL.delete_directory("/Game/StateWalk")
    bp = lib.create_blueprint_asset_with_parent("/Game/StateWalk/BP_StateWalker", unreal.Actor)
    step("bp", bp.get_name())

    global GG
    g = G(GE.get_graph_editor(lib.find_event_graph(bp)))
    GG = g

    # get_basic_type_by_name is a liar (its "double" produced an int-category
    # variable whose feeds got truncated to zero - the root cause of both dead
    # accumulators). Steal the REAL floating type from an actual engine pin.
    tmp_sin = g.fn(KML + "Sin")
    t_double = PL.get_pin_type(_pin_of(tmp_sin, "ReturnValue", "out"))
    tmp_ri = g.fn(KML + "RandomIntegerFromStream")
    t_int = PL.get_pin_type(_pin_of(tmp_ri, "ReturnValue", "out"))
    g.ge.remove_nodes([tmp_sin, tmp_ri])
    g.seen.discard(tmp_sin.get_name()); g.seen.discard(tmp_ri.get_name())
    t_stream = lib.get_struct_type(unreal.RandomStream.static_struct())
    int_arr = lib.get_array_type(t_int)
    for nm, ty in (("Stream", t_stream), ("Acc", t_double), ("MyIndex", t_int),
                   ("TickCount", t_int), ("StateIdx", t_int),
                   ("OutsOffset", int_arr), ("OutsCount", int_arr), ("OutsTarget", int_arr)):
        if not lib.add_member_variable(bp, nm, ty):
            raise RuntimeError("add var failed: " + nm)
    lib.set_blueprint_variable_instance_editable(bp, "MyIndex", True)
    step("vars", 8)

    # BeginPlay: seed
    ev_bp = g.absorb(lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint(-500, -500)))
    gi = g.getv("MyIndex"); mul = g.fn(KML + "Multiply_IntInt"); add = g.fn(KML + "Add_IntInt")
    gs = g.getv("Stream"); seed = g.fn(KML + "SetRandomStreamSeed")
    wire(gi, "MyIndex", mul, "A", "idx->mul"); setpin(mul, "B", "7919", "mul.B")
    wire(mul, "ReturnValue", add, "A", "mul->add"); setpin(add, "B", str(SEED), "add.B")
    wire(add, "ReturnValue", seed, "NewSeed", "add->seed")
    wire(gs, "Stream", seed, "Stream", "stream->seed")
    wire_exec(ev_bp, seed, "beginplay->seed")

    # Tick
    ev_t = g.absorb(lib.add_event_override(bp, "ReceiveTick", unreal.IntPoint(-500, 300)))

    g_state = g.getv("StateIdx")
    g_cnt = g.getv("OutsCount"); get_cnt = g.fn(KArr + "Array_Get")
    wire(g_cnt, "OutsCount", get_cnt, "TargetArray", "cnt->arrget")
    wire(g_state, "StateIdx", get_cnt, "Index", "state->cnt.Index")

    gs2 = g.getv("Stream"); ri = g.fn(KML + "RandomIntegerFromStream")
    wire(gs2, "Stream", ri, "Stream", "stream->randint")
    wire(get_cnt, "Item", ri, "Max", "cnt->randint.Max")

    g_off = g.getv("OutsOffset"); get_off = g.fn(KArr + "Array_Get")
    g_state2 = g.getv("StateIdx")
    wire(g_off, "OutsOffset", get_off, "TargetArray", "off->arrget")
    wire(g_state2, "StateIdx", get_off, "Index", "state->off.Index")
    add_f = g.fn(KML + "Add_IntInt")
    wire(get_off, "Item", add_f, "A", "off->flat.A")
    wire(ri, "ReturnValue", add_f, "B", "draw->flat.B")

    g_tgt = g.getv("OutsTarget"); get_tgt = g.fn(KArr + "Array_Get")
    wire(g_tgt, "OutsTarget", get_tgt, "TargetArray", "tgt->arrget")
    wire(add_f, "ReturnValue", get_tgt, "Index", "flat->tgt.Index")

    gs3 = g.getv("Stream"); rf = g.fn(KML + "RandomFloatFromStream")
    wire(gs3, "Stream", rf, "Stream", "stream->randfloat")

    # Acc = Acc + r + Sin(Acc) - STRICT chain: any conversion node = build failure.
    g_acc = g.getv("Acc"); sin = g.fn(KML + "Sin")
    wire(g_acc, "Acc", sin, "A", "acc->sin", strict=True)
    g_acc2 = g.getv("Acc"); add1 = g.fn(KML + "Add_DoubleDouble")
    wire(g_acc2, "Acc", add1, "A", "acc->add1.A", strict=True)
    wire(rf, "ReturnValue", add1, "B", "r->add1.B", strict=True)
    add2 = g.fn(KML + "Add_DoubleDouble")
    wire(add1, "ReturnValue", add2, "A", "add1->add2.A", strict=True)
    wire(sin, "ReturnValue", add2, "B", "sin->add2.B", strict=True)
    set_acc = g.setv("Acc")
    wire(add2, "ReturnValue", set_acc, "Acc", "add2->setAcc", strict=True)
    wire_exec(ev_t, set_acc, "tick->setAcc")

    g_tc = g.getv("TickCount"); add_t = g.fn(KML + "Add_IntInt")
    wire(g_tc, "TickCount", add_t, "A", "tc->add.A"); setpin(add_t, "B", "1", "addT.B")
    set_tc = g.setv("TickCount")
    wire(add_t, "ReturnValue", set_tc, "TickCount", "addT->setTc")
    wire_exec(set_acc, set_tc, "setAcc->setTc")

    set_st = g.setv("StateIdx")
    wire(get_tgt, "Item", set_st, "StateIdx", "tgt->setState")
    wire_exec(set_tc, set_st, "setTc->setState")

    # marker: W|idx|tick|next|qAcc|qr
    # Literal defaults do not stick on promotable DOUBLE pins (set_pin_value reads
    # back empty). Feed the 65536 quantizer from an int literal node instead - int
    # literals are proven to stick, and the int->double autocast is verified by wire().
    q_lit = g.fn(KSL + "MakeLiteralInt")
    setpin(q_lit, "Value", "65536", "q.lit")
    qa_m = g.fn(KML + "Multiply_DoubleDouble"); qa_f = g.fn(KML + "FFloor")
    g_acc3 = g.getv("Acc")
    wire(g_acc3, "Acc", qa_m, "A", "acc->qa.A")
    wire(q_lit, "ReturnValue", qa_m, "B", "lit->qa.B")
    wire(qa_m, "ReturnValue", qa_f, "A", "qa->floor")
    qr_m = g.fn(KML + "Multiply_DoubleDouble"); qr_f = g.fn(KML + "FFloor")
    wire(rf, "ReturnValue", qr_m, "A", "r->qr.A")
    wire(q_lit, "ReturnValue", qr_m, "B", "lit->qr.B")
    wire(qr_m, "ReturnValue", qr_f, "A", "qr->floor")

    g_i2 = g.getv("MyIndex"); g_tc2 = g.getv("TickCount")
    parts = []
    for k in range(5):
        parts.append(g.fn(KStr + "BuildString_Int"))
    setpin(parts[0], "AppendTo", "W|", "s0.prefix")
    wire(g_i2, "MyIndex", parts[0], "InInt", "idx->s0")
    for k in range(4):
        setpin(parts[k], "Suffix", "|", "s%d.suffix" % k)
        wire(parts[k], "ReturnValue", parts[k + 1], "AppendTo", "s%d->s%d" % (k, k + 1))
    wire(g_tc2, "TickCount", parts[1], "InInt", "tc->s1")
    wire(get_tgt, "Item", parts[2], "InInt", "next->s2")
    wire(qa_f, "ReturnValue", parts[3], "InInt", "qAcc->s3")
    wire(qr_f, "ReturnValue", parts[4], "InInt", "qr->s4")

    pr = g.fn(KSL + "PrintString")
    wire(parts[4], "ReturnValue", pr, "InString", "s4->print")
    setpin(pr, "bPrintToScreen", "false", "pr.screen")
    setpin(pr, "bPrintToLog", "true", "pr.log")
    wire_exec(set_st, pr, "setState->print")

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

    # tables + initial state onto the CDO, then save
    cls = EAL.load_blueprint_class("/Game/StateWalk/BP_StateWalker")
    cdo = unreal.get_default_object(cls)
    cdo.set_editor_property("OutsOffset", offset)
    cdo.set_editor_property("OutsCount", count)
    cdo.set_editor_property("OutsTarget", target)
    cdo.set_editor_property("StateIdx", idle_idx)
    step("cdo tables", "%d/%d/%d idle=%d" % (len(offset), len(count), len(target), idle_idx))
    if not EAL.save_asset("/Game/StateWalk/BP_StateWalker"):
        raise RuntimeError("save bp failed")

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not les.new_level_from_template("/Game/StateWalk/L_StateWalk",
                                       "/Engine/Maps/Templates/Template_Default"):
        raise RuntimeError("level template failed")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for i in range(INSTANCES):
        a = eas.spawn_actor_from_class(cls, unreal.Vector(i * 300.0, 0.0, 0.0))
        a.set_editor_property("MyIndex", i)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    les.save_current_level()
    les.load_level("/Game/StateWalk/L_StateWalk")
    eas2 = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    n = len([a for a in eas2.get_all_level_actors()
             if a.get_class().get_name().startswith("BP_StateWalker")])
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
unreal.log("WALKER_GEN " + rep["result"])
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 01:52 UTC | END ]
