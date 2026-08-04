# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | START ]
"""Where each arena mesh actually sits in the pack's own scene.

The pack lays six rings out side by side in one FBX, and every mesh keeps its
layout offset in its vertices. So 'ring five' is not a name - it is a CLUSTER in
space, and the first attempt to spawn it centred the union of everything called
_5*, which put the visible ring off to one side of the fight. This dumps each
mesh's centre and size so the cluster can be read off the numbers instead of
guessed from the names.
"""
import json

import unreal

EAL = unreal.EditorAssetLibrary
ARENA = "/Game/FabImports/CartoonBoxingArena"
OUT = r"C:\Users\edwar\project-uppercut\sandbox\Saved\fab_bounds.json"

rows = []
for p in EAL.list_assets(ARENA, recursive=False, include_folder=False):
    a = unreal.load_asset(p)
    if not isinstance(a, unreal.StaticMesh):
        continue
    box = a.get_bounds()
    c, e = box.origin, box.box_extent
    rows.append({
        "mesh": a.get_name(),
        "centre": [round(c.x, 1), round(c.y, 1), round(c.z, 1)],
        "size": [round(e.x * 2, 1), round(e.y * 2, 1), round(e.z * 2, 1)],
        "tris": a.get_num_triangles(0),
    })

rows.sort(key=lambda r: (r["centre"][0], r["centre"][1]))
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(rows, fh, indent=1)
unreal.log("BOUNDS: %d meshes -> %s" % (len(rows), OUT))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | END ]
