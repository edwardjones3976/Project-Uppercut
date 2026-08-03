# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 00:56 UTC | START ]
"""Phase B scan pass 2: node-creation and pin-wiring surface (the historical wall)."""
import json, os
import unreal

OUT = os.environ["UE_SCAN_OUT"]
report = {"probes": {}}


def probe(name, fn):
    try:
        report["probes"][name] = {"ok": True, "detail": fn()}
    except Exception as e:
        report["probes"][name] = {"ok": False, "detail": repr(e)}


def _all(obj):
    return sorted(m for m in dir(obj) if not m.startswith("_"))


probe("BlueprintGraphEditor_members", lambda: _all(unreal.BlueprintGraphEditor))
probe("BlueprintGraphPinLibrary_members", lambda: _all(unreal.BlueprintGraphPinLibrary))
probe("BlueprintGraphPin_members", lambda: _all(unreal.BlueprintGraphPin))

# End-to-end: build a real graph headlessly and compile it.
BP = "/Game/Probe2/BP_GraphTest"


def build_graph():
    steps = {}
    lib = unreal.BlueprintEditorLibrary
    bp = lib.create_blueprint_asset_with_parent("/Game/Probe2", "BP_GraphTest", unreal.Actor)
    steps["created"] = str(bp)
    dbl = lib.get_basic_type_by_name("double")
    steps["double_type"] = str(dbl)
    steps["var_added"] = lib.add_member_variable(bp, "Acc", dbl)
    ev = lib.find_event_graph(bp)
    steps["event_graph"] = str(ev)
    ge = unreal.BlueprintGraphEditor
    steps["tick_override"] = str(lib.add_event_override(bp, "ReceiveTick"))
    # node creation attempts
    for fname in ("create_node", "add_node", "spawn_node", "create_variable_get_node",
                  "create_variable_set_node", "create_call_function_node", "add_call_function_node"):
        steps["has_" + fname] = hasattr(ge, fname)
    # pin wiring attempts
    for fname in ("connect_pins", "make_link_to", "link_pins", "break_all_pin_links", "set_default_value"):
        steps["pin_has_" + fname] = hasattr(unreal.BlueprintGraphPinLibrary, fname)
    lib.compile_blueprint(bp)
    steps["compiled"] = True
    steps["saved"] = unreal.EditorAssetLibrary.save_asset(BP)
    return steps


probe("build_graph_end_to_end", build_graph)

# Housekeeping: probe assets must not survive into the repo.
def purge():
    out = {}
    for d in ("/Game/Probe", "/Game/Probe2"):
        out[d] = {
            "existed": unreal.EditorAssetLibrary.does_directory_exist(d),
            "deleted": unreal.EditorAssetLibrary.delete_directory(d),
            "still_exists": unreal.EditorAssetLibrary.does_directory_exist(d),
        }
    return out


probe("purge_probe_assets", purge)

with open(OUT, "w") as f:
    json.dump(report, f, indent=2, sort_keys=True)
unreal.log("SCAN2_DONE")
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 00:56 UTC | END ]
