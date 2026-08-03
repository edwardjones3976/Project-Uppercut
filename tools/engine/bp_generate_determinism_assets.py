# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 01:05 UTC | START ]
"""Phase B: author the Blueprint actor-tick determinism test articles headlessly.

Route A (confirmed by tools/engine/bp_capability_scan*.py against UE 5.8.1): the
editor Python surface exposes full graph authoring - node creation, pin discovery
and pin connection - so no GUI authoring is required.

Builds:
  /Game/Determinism/BP_DeterminismActor  - ticking actor, RandomStream MEMBER variable
      (engine-side stream, per the probe-v1 architecture lesson), float accumulation,
      quantized integer marker emitted to the log each tick.
  /Game/Determinism/L_DeterminismProbe   - level with 5 instances, MyIndex 0..4.

Marker: P|<MyIndex>|<TickCount>|<floor(Acc * 65536)>
Integer quantization is deliberate: BP float->string truncates; integers are exact.
"""
import json, os
import unreal

OUT = os.environ["UE_GEN_OUT"]
SEED_BASE = int(os.environ.get("UE_GEN_SEED", "56057345"))
INSTANCES = 5
MAX_TICKS = 2000

lib = unreal.BlueprintEditorLibrary
GE = unreal.BlueprintGraphEditor
PL = unreal.BlueprintGraphPinLibrary
EAL = unreal.EditorAssetLibrary

rep = {"steps": [], "errors": []}


def step(msg, val=None):
    rep["steps"].append(msg if val is None else "%s -> %s" % (msg, val))


def basic(name_candidates):
    for n in name_candidates:
        try:
            t = lib.get_basic_type_by_name(n)
            if t:
                return t
        except Exception:
            pass
    raise RuntimeError("no basic type among %r" % (name_candidates,))


def connect(a, b, label):
    ok = PL.try_create_connection(a, b)
    if not ok:
        rep["errors"].append("connect FAILED: " + label)
    return ok


def fn_node(ge, path):
    n = ge.add_call_function_node(path)
    if n is None:
        raise RuntimeError("add_call_function_node failed: " + path)
    return n


def build():
    if EAL.does_directory_exist("/Game/Determinism"):
        EAL.delete_directory("/Game/Determinism")

    bp = lib.create_blueprint_asset_with_parent("/Game/Determinism/BP_DeterminismActor", unreal.Actor)
    step("created blueprint", bp)

    t_double = basic(["double", "float", "real"])
    t_int = basic(["int", "int32", "integer"])
    t_stream = lib.get_struct_type(unreal.RandomStream.static_struct())
    step("types", "double=%s int=%s stream=%s" % (bool(t_double), bool(t_int), bool(t_stream)))

    for nm, ty in (("Stream", t_stream), ("Acc", t_double), ("MyIndex", t_int), ("TickCount", t_int)):
        step("add var " + nm, lib.add_member_variable(bp, nm, ty))
    # MyIndex must be settable per placed instance (it is the actor's identity in the log).
    try:
        step("MyIndex instance-editable",
             lib.set_blueprint_variable_instance_editable(bp, "MyIndex", True))
    except Exception as e:
        rep["errors"].append("instance_editable: " + repr(e))

    graph = lib.find_event_graph(bp)
    ge = GE.get_graph_editor(graph)
    step("graph editor", ge)

    KML = "/Script/Engine.KismetMathLibrary:"
    KSL = "/Script/Engine.KismetSystemLibrary:"
    KStr = "/Script/Engine.KismetStringLibrary:"

    # ---------- BeginPlay: seed the member stream ----------
    ev_bp = lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint(-400, -400))
    step("BeginPlay event", ev_bp)
    g_idx0 = ge.add_get_member_variable_node("MyIndex")
    mul_seed = fn_node(ge, KML + "Multiply_IntInt")
    add_seed = fn_node(ge, KML + "Add_IntInt")
    g_stream0 = ge.add_get_member_variable_node("Stream")
    set_seed = fn_node(ge, KML + "SetRandomStreamSeed")

    connect(lib.find_output_pin(g_idx0, "MyIndex"), lib.find_input_pin(mul_seed, "A"), "idx->mul.A")
    PL.set_pin_value(lib.find_input_pin(mul_seed, "B"), "7919")
    connect(lib.find_output_pin(mul_seed, "ReturnValue"), lib.find_input_pin(add_seed, "A"), "mul->add.A")
    PL.set_pin_value(lib.find_input_pin(add_seed, "B"), str(SEED_BASE))
    connect(lib.find_output_pin(add_seed, "ReturnValue"), lib.find_input_pin(set_seed, "NewSeed"), "add->seed")
    connect(lib.find_output_pin(g_stream0, "Stream"), lib.find_input_pin(set_seed, "Stream"), "stream->seed.Stream")
    connect(lib.find_then_pin(ev_bp), lib.find_execute_pin(set_seed), "beginplay->seed")

    # ---------- Tick ----------
    ev_tick = lib.add_event_override(bp, "ReceiveTick", unreal.IntPoint(-400, 200))
    step("Tick event", ev_tick)

    g_stream = ge.add_get_member_variable_node("Stream")
    rand = fn_node(ge, KML + "RandomFloatFromStream")
    connect(lib.find_output_pin(g_stream, "Stream"), lib.find_input_pin(rand, "Stream"), "stream->rand")

    g_acc = ge.add_get_member_variable_node("Acc")
    add_acc = fn_node(ge, KML + "Add_DoubleDouble")
    set_acc = ge.add_set_member_variable_node("Acc")
    connect(lib.find_output_pin(g_acc, "Acc"), lib.find_input_pin(add_acc, "A"), "acc->add.A")
    connect(lib.find_output_pin(rand, "ReturnValue"), lib.find_input_pin(add_acc, "B"), "rand->add.B")
    connect(lib.find_output_pin(add_acc, "ReturnValue"), lib.find_input_pin(set_acc, "Acc"), "add->setAcc")
    connect(lib.find_then_pin(ev_tick), lib.find_execute_pin(set_acc), "tick->setAcc")

    g_tick = ge.add_get_member_variable_node("TickCount")
    add_tick = fn_node(ge, KML + "Add_IntInt")
    set_tick = ge.add_set_member_variable_node("TickCount")
    connect(lib.find_output_pin(g_tick, "TickCount"), lib.find_input_pin(add_tick, "A"), "tick->add.A")
    PL.set_pin_value(lib.find_input_pin(add_tick, "B"), "1")
    connect(lib.find_output_pin(add_tick, "ReturnValue"), lib.find_input_pin(set_tick, "TickCount"), "add->setTick")
    connect(lib.find_then_pin(set_acc), lib.find_execute_pin(set_tick), "setAcc->setTick")

    # quantize: q = FFloor(Acc * 65536)
    g_acc2 = ge.add_get_member_variable_node("Acc")
    mulq = fn_node(ge, KML + "Multiply_DoubleDouble")
    floorq = fn_node(ge, KML + "FFloor")
    connect(lib.find_output_pin(g_acc2, "Acc"), lib.find_input_pin(mulq, "A"), "acc2->mulq.A")
    PL.set_pin_value(lib.find_input_pin(mulq, "B"), "65536.0")
    connect(lib.find_output_pin(mulq, "ReturnValue"), lib.find_input_pin(floorq, "A"), "mulq->floor")

    # marker string
    g_idx = ge.add_get_member_variable_node("MyIndex")
    g_tick2 = ge.add_get_member_variable_node("TickCount")
    s1 = fn_node(ge, KStr + "BuildString_Int")
    s2 = fn_node(ge, KStr + "BuildString_Int")
    s3 = fn_node(ge, KStr + "BuildString_Int")
    PL.set_pin_value(lib.find_input_pin(s1, "AppendTo"), "P|")
    connect(lib.find_output_pin(g_idx, "MyIndex"), lib.find_input_pin(s1, "InInt"), "idx->s1")
    PL.set_pin_value(lib.find_input_pin(s1, "Suffix"), "|")
    connect(lib.find_output_pin(s1, "ReturnValue"), lib.find_input_pin(s2, "AppendTo"), "s1->s2")
    connect(lib.find_output_pin(g_tick2, "TickCount"), lib.find_input_pin(s2, "InInt"), "tick2->s2")
    PL.set_pin_value(lib.find_input_pin(s2, "Suffix"), "|")
    connect(lib.find_output_pin(s2, "ReturnValue"), lib.find_input_pin(s3, "AppendTo"), "s2->s3")
    connect(lib.find_output_pin(floorq, "ReturnValue"), lib.find_input_pin(s3, "InInt"), "floor->s3")
    PL.set_pin_value(lib.find_input_pin(s3, "Suffix"), "|")

    # Also emit the quantized raw draw, so a dead RNG is distinguishable from a dead
    # accumulator in the log itself rather than by inference.
    mulr = fn_node(ge, KML + "Multiply_DoubleDouble")
    floorr = fn_node(ge, KML + "FFloor")
    s4 = fn_node(ge, KStr + "BuildString_Int")
    connect(lib.find_output_pin(rand, "ReturnValue"), lib.find_input_pin(mulr, "A"), "rand->mulr.A")
    PL.set_pin_value(lib.find_input_pin(mulr, "B"), "65536.0")
    connect(lib.find_output_pin(mulr, "ReturnValue"), lib.find_input_pin(floorr, "A"), "mulr->floorr")
    connect(lib.find_output_pin(s3, "ReturnValue"), lib.find_input_pin(s4, "AppendTo"), "s3->s4")
    connect(lib.find_output_pin(floorr, "ReturnValue"), lib.find_input_pin(s4, "InInt"), "floorr->s4")

    pr = fn_node(ge, KSL + "PrintString")
    connect(lib.find_output_pin(s4, "ReturnValue"), lib.find_input_pin(pr, "InString"), "s4->print")
    PL.set_pin_value(lib.find_input_pin(pr, "bPrintToScreen"), "false")
    PL.set_pin_value(lib.find_input_pin(pr, "bPrintToLog"), "true")
    connect(lib.find_then_pin(set_tick), lib.find_execute_pin(pr), "setTick->print")

    # quit after MAX_TICKS
    g_tick3 = ge.add_get_member_variable_node("TickCount")
    g_idx3 = ge.add_get_member_variable_node("MyIndex")
    ge_int = fn_node(ge, KML + "GreaterEqual_IntInt")
    eq_int = fn_node(ge, KML + "EqualEqual_IntInt")
    and_b = fn_node(ge, KML + "BooleanAND")
    br = ge.add_branch_node()
    quit_n = fn_node(ge, KSL + "QuitGame")
    connect(lib.find_output_pin(g_tick3, "TickCount"), lib.find_input_pin(ge_int, "A"), "tick3->ge.A")
    PL.set_pin_value(lib.find_input_pin(ge_int, "B"), str(MAX_TICKS))
    connect(lib.find_output_pin(g_idx3, "MyIndex"), lib.find_input_pin(eq_int, "A"), "idx3->eq.A")
    PL.set_pin_value(lib.find_input_pin(eq_int, "B"), "0")
    connect(lib.find_output_pin(ge_int, "ReturnValue"), lib.find_input_pin(and_b, "A"), "ge->and.A")
    connect(lib.find_output_pin(eq_int, "ReturnValue"), lib.find_input_pin(and_b, "B"), "eq->and.B")
    connect(lib.find_output_pin(and_b, "ReturnValue"), lib.find_condition_pin(br), "and->branch")
    connect(lib.find_then_pin(pr), lib.find_execute_pin(br), "print->branch")
    connect(lib.find_then_pin(br), lib.find_execute_pin(quit_n), "branch->quit")

    ok = lib.compile_blueprint(bp)
    step("compiled", ok)
    step("saved bp", EAL.save_asset("/Game/Determinism/BP_DeterminismActor"))

    # ---------- level ----------
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    # A plain (non-World-Partition) level: WP stores actors as EXTERNAL packages that
    # save_current_level() does not write, and its streaming is extra nondeterminism we
    # do not want inside a determinism measurement.
    made = False
    for tmpl in ("/Engine/Maps/Templates/Template_Default",
                 "/Engine/Maps/Templates/Template_Default_BuiltData"):
        try:
            made = les.new_level_from_template("/Game/Determinism/L_DeterminismProbe", tmpl)
            if made:
                step("level from template", tmpl)
                break
        except Exception as e:
            rep["errors"].append("template %s: %s" % (tmpl, e))
    if not made:
        les.new_level("/Game/Determinism/L_DeterminismProbe")
        step("level from template", "FALLBACK new_level")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cls = EAL.load_blueprint_class("/Game/Determinism/BP_DeterminismActor")
    for i in range(INSTANCES):
        a = eas.spawn_actor_from_class(cls, unreal.Vector(i * 200.0, 0.0, 0.0))
        a.set_editor_property("MyIndex", i)
        a.set_actor_label("DetActor_%d" % i)
    step("spawned", INSTANCES)
    # Save dirty packages first: on a World Partition level the actors live in EXTERNAL
    # packages that save_current_level() does not write.
    try:
        step("save_dirty_packages",
             unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True))
    except Exception as e:
        rep["errors"].append("save_dirty_packages: " + repr(e))
    saved = les.save_current_level()
    if not saved:
        try:
            saved = les.save_all_dirty_levels()
            step("save_all_dirty_levels", saved)
        except Exception as e:
            rep["errors"].append("save_all_dirty: " + repr(e))
    if not saved:
        try:
            w = unreal.EditorLevelLibrary.get_editor_world()
            saved = unreal.EditorLoadingAndSavingUtils.save_map(w, "/Game/Determinism/L_DeterminismProbe")
            step("save_map", saved)
        except Exception as e:
            rep["errors"].append("save_map: " + repr(e))
    step("level saved", saved)
    rep["node_count"] = len(ge.list_all_nodes())

    # Verify by reloading the level and counting persisted instances.
    try:
        les.load_level("/Game/Determinism/L_DeterminismProbe")
        found = [a for a in eas.get_all_level_actors()
                 if a.get_class().get_name().startswith("BP_DeterminismActor")]
        rep["verify_persisted_actors"] = len(found)
        rep["verify_indices"] = sorted(a.get_editor_property("MyIndex") for a in found)
    except Exception as e:
        rep["errors"].append("verify: " + repr(e))


try:
    build()
    rep["result"] = "OK" if not rep["errors"] else "COMPLETED_WITH_CONNECT_ERRORS"
except Exception as e:
    import traceback
    rep["result"] = "FAILED"
    rep["traceback"] = traceback.format_exc()

with open(OUT, "w") as f:
    json.dump(rep, f, indent=2)
unreal.log("GEN_DONE " + rep.get("result", "?"))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 01:05 UTC | END ]
