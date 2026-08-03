# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 00:52 UTC | START ]
"""Phase B route-decider: inventory UE 5.8's headless Blueprint-authoring surface.

Runs inside UnrealEditor-Cmd via PythonScriptPlugin (same invocation pattern as the
determinism probe). Answers ONE question with evidence: can Blueprint assets with
variables and graph logic be authored headlessly via editor Python in this build,
or does BP authoring need the editor GUI (computer-use route)?

Writes a JSON report to $UE_SCAN_OUT. Everything is try/except-probed and recorded;
nothing is assumed from documentation (Rule 18 applies to tooling claims too).
Creates its test assets under /Game/Probe/ and deletes them before exiting.
"""
import json
import os

import unreal

OUT = os.environ["UE_SCAN_OUT"]
report = {"engine": str(unreal.SystemLibrary.get_engine_version()), "probes": {}}


def probe(name, fn):
    try:
        report["probes"][name] = {"ok": True, "detail": fn()}
    except Exception as e:
        report["probes"][name] = {"ok": False, "detail": repr(e)}


def _members(obj, prefixes):
    return sorted(m for m in dir(obj) if any(m.startswith(p) for p in prefixes))


probe("blueprint_editor_library_members", lambda: _members(
    unreal.BlueprintEditorLibrary, ("add_", "create_", "compile_", "new_", "set_", "replace_", "find_", "get_", "remove_")))
probe("k2_and_graph_types_exposed", lambda: sorted(
    n for n in dir(unreal) if n.startswith(("K2Node", "EdGraph", "Blueprint"))))
probe("level_editor_subsystem", lambda: _members(
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem), ("new_", "save_", "load_")))
probe("editor_actor_subsystem", lambda: _members(
    unreal.get_editor_subsystem(unreal.EditorActorSubsystem), ("spawn_", "get_all")))

BP_PATH = "/Game/Probe"
BP_NAME = "BP_ScanTest"


def make_bp():
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.Actor)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset = tools.create_asset(BP_NAME, BP_PATH, None, factory)
    return str(asset)


probe("create_blueprint_asset", make_bp)


def add_var():
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH + "/" + BP_NAME)
    lib = unreal.BlueprintEditorLibrary
    attempts = {}
    candidates = []
    try:
        pt = unreal.EdGraphPinType()
        candidates.append(("add_member_variable", (bp, "ProbeAcc", pt)))
    except Exception as e:
        attempts["EdGraphPinType_ctor"] = "RAISED: " + repr(e)
    candidates.append(("add_member_variable_with_type", (bp, "ProbeAcc2", "double")))
    for fname, args in candidates:
        fn = getattr(lib, fname, None)
        if fn is None:
            attempts[fname] = "ABSENT"
            continue
        try:
            attempts[fname] = "OK: " + repr(fn(*args))
        except Exception as e:
            attempts[fname] = "RAISED: " + repr(e)
    return attempts


probe("add_variable_attempts", add_var)


def compile_bp():
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH + "/" + BP_NAME)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    return "compiled"


probe("compile_blueprint", compile_bp)


def level_roundtrip():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    ok = les.new_level("/Game/Probe/L_ScanTest")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 0))
    saved = les.save_current_level()
    return {"new_level": bool(ok), "spawned": str(actor), "saved": bool(saved)}


probe("level_roundtrip", level_roundtrip)

probe("cleanup", lambda: unreal.EditorAssetLibrary.delete_directory(BP_PATH))

with open(OUT, "w") as f:
    json.dump(report, f, indent=2, sort_keys=True)
unreal.log("SCAN_DONE -> " + OUT)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 00:52 UTC | END ]
