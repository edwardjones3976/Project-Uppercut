# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 02:22 UTC | START ]
"""What does get_basic_type_by_name actually return, per name? And what type does a
variable created with it end up as? Definitive answer via read-back."""
import json, os
import unreal

OUT = os.environ["UE_SCAN_OUT"]
lib = unreal.BlueprintEditorLibrary
rep = {}

def describe(t):
    out = []
    for prop in ("pin_category", "pin_sub_category", "container_type"):
        try:
            out.append("%s=%s" % (prop, t.get_editor_property(prop)))
        except Exception as e:
            out.append("%s=ERR" % prop)
    return " ".join(out)

for name in ("double", "float", "real", "int", "int64", "bool", "number"):
    try:
        t = lib.get_basic_type_by_name(name)
        rep[name] = describe(t)
    except Exception as e:
        rep[name] = "RAISED " + repr(e)

# and what did the walker's Acc actually become?
bp = unreal.EditorAssetLibrary.load_asset("/Game/StateWalk/BP_StateWalker")
try:
    rep["walker_Acc_type"] = describe(lib.get_member_variable_type(bp, "Acc"))
    rep["walker_TickCount_type"] = describe(lib.get_member_variable_type(bp, "TickCount"))
except Exception as e:
    rep["walker_var_type"] = repr(e)

with open(OUT, "w") as f:
    json.dump(rep, f, indent=1)
unreal.log("TYPEPROBE_DONE")
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 02:22 UTC | END ]
