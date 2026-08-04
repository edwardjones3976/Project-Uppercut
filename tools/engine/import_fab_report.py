# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | START ]
"""Verify what the two Fab import passes actually produced, in writing.

unreal.log() does not survive the editor's stdout redirection in this harness, so
the import passes ran blind. This writes the result to a file instead: every
static mesh under /Game/FabImports with its bounds, triangle count and the
material actually bound to slot 0. An import that silently kept the default
material is the failure mode that matters - a grey arena that looks imported.

Run:  run_import_fab.ps1 -Pass report   ->  sandbox/Saved/fab_import_report.json
"""
import json

import unreal

EAL = unreal.EditorAssetLibrary
OUT = r"C:\Users\edwar\project-uppercut\sandbox\Saved\fab_import_report.json"

report = {"meshes": [], "textures": 0, "material_instances": 0, "no_material": []}

for folder in ("/Game/FabImports/CartoonBoxingArena", "/Game/FabImports/BoxingGlove"):
    for path in EAL.list_assets(folder, recursive=True, include_folder=False):
        asset = unreal.load_asset(path)
        if isinstance(asset, unreal.Texture2D):
            report["textures"] += 1
            continue
        if isinstance(asset, unreal.MaterialInstanceConstant):
            report["material_instances"] += 1
            continue
        if not isinstance(asset, unreal.StaticMesh):
            continue
        mats = []
        try:
            for sm in asset.get_editor_property("static_materials"):
                mi = sm.material_interface
                mats.append(mi.get_name() if mi else None)
        except Exception as exc:            # noqa: BLE001
            mats = ["<error: %s>" % exc]
        bounds = asset.get_bounds().box_extent
        entry = {
            "mesh": asset.get_name(),
            "materials": mats,
            "tris": asset.get_num_triangles(0),
            "extent": [round(bounds.x, 1), round(bounds.y, 1), round(bounds.z, 1)],
        }
        report["meshes"].append(entry)
        if not mats or mats[0] is None or str(mats[0]).startswith("WorldGrid"):
            report["no_material"].append(asset.get_name())

report["mesh_count"] = len(report["meshes"])
report["meshes"].sort(key=lambda m: -m["tris"])
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1)
unreal.log("REPORT: wrote %s" % OUT)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | END ]
