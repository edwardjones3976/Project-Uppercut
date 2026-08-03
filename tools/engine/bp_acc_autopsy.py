# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 01:44 UTC | START ]
"""Acc autopsy v2: enumerate every node's pins by index via BlueprintEditorLibrary."""
import json, os
import unreal

OUT = os.environ["UE_SCAN_OUT"]
lib = unreal.BlueprintEditorLibrary
PL = unreal.BlueprintGraphPinLibrary

bp = unreal.EditorAssetLibrary.load_asset(os.environ.get("UE_BP_PATH", "/Game/Determinism/BP_DeterminismActor"))
graph = lib.find_event_graph(bp)
ge = unreal.BlueprintGraphEditor.get_graph_editor(graph)

def pin_info(pin):
    try:
        if not PL.is_valid(pin):
            return None
        links = []
        for lp in PL.list_connected_pins(pin):
            try:
                links.append("%s.%s" % (PL.get_owning_node(lp).get_name(), PL.get_pin_name(lp)))
            except Exception:
                links.append("?")
        val = ""
        try:
            val = str(PL.get_pin_value(pin))[:24]
        except Exception:
            pass
        return {"name": str(PL.get_pin_name(pin)), "dir": str(PL.get_pin_direction(pin)),
                "val": val, "links": links}
    except Exception:
        return None

rep = []
for n in ge.list_all_nodes():
    title = ""
    try:
        title = str(n.get_node_title(unreal.NodeTitleType.FULL_TITLE)).replace(chr(10), " / ")
    except Exception:
        pass
    entry = {"node": n.get_name(), "class": n.get_class().get_name(), "title": title, "in": [], "out": []}
    for i in range(10):
        for side, bucket in (("in", "in"), ("out", "out")):
            try:
                pin = (lib.find_input_pin_by_index if side == "in" else lib.find_output_pin_by_index)(n, i)
                info = pin_info(pin)
                if info:
                    entry[bucket].append(info)
            except Exception:
                pass
    rep.append(entry)

with open(OUT, "w") as f:
    json.dump(rep, f, indent=1)
unreal.log("AUTOPSY2_DONE %d nodes" % len(rep))
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 01:44 UTC | END ]
