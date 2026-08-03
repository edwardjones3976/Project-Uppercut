# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 01:00 UTC | START ]
"""Phase B scan pass 3: exact signatures for the graph-authoring calls, plus purge."""
import json, os
import unreal

OUT = os.environ["UE_SCAN_OUT"]
report = {"sigs": {}, "purge": {}}

lib = unreal.BlueprintEditorLibrary
ge = unreal.BlueprintGraphEditor
pinlib = unreal.BlueprintGraphPinLibrary

targets = [
    ("lib.create_blueprint_asset_with_parent", lib, "create_blueprint_asset_with_parent"),
    ("lib.get_basic_type_by_name", lib, "get_basic_type_by_name"),
    ("lib.get_struct_type", lib, "get_struct_type"),
    ("lib.add_member_variable", lib, "add_member_variable"),
    ("lib.add_event_override", lib, "add_event_override"),
    ("lib.find_event_graph", lib, "find_event_graph"),
    ("lib.find_execute_pin", lib, "find_execute_pin"),
    ("lib.find_then_pin", lib, "find_then_pin"),
    ("lib.find_input_pin", lib, "find_input_pin"),
    ("lib.find_output_pin", lib, "find_output_pin"),
    ("lib.find_self_pin", lib, "find_self_pin"),
    ("lib.compile_blueprint", lib, "compile_blueprint"),
    ("ge.get_graph_editor", ge, "get_graph_editor"),
    ("ge.add_call_function_node", ge, "add_call_function_node"),
    ("ge.add_get_member_variable_node", ge, "add_get_member_variable_node"),
    ("ge.add_set_member_variable_node", ge, "add_set_member_variable_node"),
    ("ge.add_custom_event_node", ge, "add_custom_event_node"),
    ("ge.create_node_from_name", ge, "create_node_from_name"),
    ("ge.find_event_node", ge, "find_event_node"),
    ("ge.list_all_nodes", ge, "list_all_nodes"),
    ("ge.add_member_variable", ge, "add_member_variable"),
    ("pinlib.try_create_connection", pinlib, "try_create_connection"),
    ("pinlib.set_pin_value", pinlib, "set_pin_value"),
    ("pinlib.get_pin_name", pinlib, "get_pin_name"),
]
for label, owner, fname in targets:
    fn = getattr(owner, fname, None)
    report["sigs"][label] = (fn.__doc__ or "").strip().split("\n")[0] if fn else "ABSENT"

# Purge leftovers: switch off the probe level first so it is not the loaded world.
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.new_level("/Game/Scratch/Empty")
    report["purge"]["switched_level"] = True
except Exception as e:
    report["purge"]["switched_level"] = repr(e)
for d in ("/Game/Probe", "/Game/Probe2", "/Game/Scratch"):
    try:
        report["purge"][d] = {
            "existed": unreal.EditorAssetLibrary.does_directory_exist(d),
            "deleted": unreal.EditorAssetLibrary.delete_directory(d),
        }
    except Exception as e:
        report["purge"][d] = repr(e)

with open(OUT, "w") as f:
    json.dump(report, f, indent=2, sort_keys=True)
unreal.log("SCAN3_DONE")
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 01:00 UTC | END ]
