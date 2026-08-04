# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | START ]
"""Third pass: make the material assignment actually stick, and record scale.

The second pass reported success and changed nothing. The cause is a real trap in
the UE Python API and worth writing down: `mesh.get_editor_property(
'static_materials')` returns a COPY of the array, and indexing it returns a COPY
of the struct. So this:

    sms = mesh.get_editor_property('static_materials')
    sms[0].material_interface = mi            # mutates a temporary
    mesh.set_editor_property('static_materials', sms)

writes the untouched array back and reports no error. The element has to be put
back into the array explicitly:

    sm = sms[0]; sm.material_interface = mi; sms[0] = sm

That is why the report pass exists. An import that silently keeps the FBX's own
materials looks exactly like an import that worked, right up until it is on
screen - and this one had already been written up as done.

Scale is recorded here rather than baked in. The pack's rings are ~195 m across
and the glove is ~1 cm: both are authored in their own units, and the fight's
coordinate space is canon's, so the scale factor belongs at the spawn site where
it can be read next to the sim's own numbers.
"""
import json
import re

import unreal

EAL = unreal.EditorAssetLibrary
ARENA = "/Game/FabImports/CartoonBoxingArena"
MATS = ARENA + "/Materials"
GLOVE = "/Game/FabImports/BoxingGlove"
OUT = r"C:\Users\edwar\project-uppercut\sandbox\Saved\fab_fixup_report.json"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def set_slot0(mesh, mat) -> bool:
    """The whole point of this file. Returns whether the write took."""
    sms = mesh.get_editor_property("static_materials")
    if not sms:
        return False
    sm = sms[0]
    sm.set_editor_property("material_interface", mat)
    sms[0] = sm                                   # <- the line pass two was missing
    mesh.set_editor_property("static_materials", sms)
    EAL.save_loaded_asset(mesh)
    check = mesh.get_editor_property("static_materials")[0].material_interface
    return check is not None and check.get_name() == mat.get_name()


instances = []
for p in EAL.list_assets(MATS, recursive=False, include_folder=False):
    a = unreal.load_asset(p)
    if isinstance(a, unreal.MaterialInstanceConstant) and a.get_name().startswith("MI_c"):
        instances.append((a, norm(a.get_name()[3:])))

report = {"assigned": [], "unmatched": [], "failed": [], "scale": {}}

for p in EAL.list_assets(ARENA, recursive=False, include_folder=False):
    mesh = unreal.load_asset(p)
    if not isinstance(mesh, unreal.StaticMesh):
        continue
    n = norm(mesh.get_name())
    best = None
    for mi, key in instances:
        if n.startswith(key) and (best is None or len(key) > len(best[1])):
            best = (mi, key)
    if best is None:
        report["unmatched"].append(mesh.get_name())
        continue
    if set_slot0(mesh, best[0]):
        report["assigned"].append([mesh.get_name(), best[0].get_name()])
    else:
        report["failed"].append(mesh.get_name())

glove_mi = unreal.load_asset(MATS + "/MI_BoxingGlove_Red")
for p in EAL.list_assets(GLOVE, recursive=True, include_folder=False):
    mesh = unreal.load_asset(p)
    if isinstance(mesh, unreal.StaticMesh):
        ok = set_slot0(mesh, glove_mi)
        (report["assigned"] if ok else report["failed"]).append(
            [mesh.get_name(), "MI_BoxingGlove_Red"] if ok else mesh.get_name())

# Scale, measured rather than assumed. A boxing glove is about 30 cm across and a
# ring is about 6 m of canvas; these numbers say how far off the imports are.
for label, path in (("ring_5", ARENA + "/cartoon_boxing_arena_5"),
                    ("stands", ARENA + "/cartoon_boxing_arena__stands1"),
                    ("glove", GLOVE + "/boxingglove")):
    # The FBX import dropped textures and materials into the SAME folder as the
    # meshes, so a name can resolve to a Texture2D. Ask what it is before
    # measuring it.
    asset = unreal.load_asset(path) if EAL.does_asset_exist(path) else None
    if isinstance(asset, unreal.StaticMesh):
        b = asset.get_bounds().box_extent
        report["scale"][label] = {
            "extent_cm": [round(b.x, 1), round(b.y, 1), round(b.z, 1)],
            "width_m": round(max(b.x, b.y) * 2 / 100.0, 2),
        }

report["counts"] = {k: len(report[k]) for k in ("assigned", "unmatched", "failed")}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1)
unreal.log("FIXUP: %s" % report["counts"])
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | END ]
