# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | START ]
"""Second import pass: textures and materials for the Fab exchange-format assets.

The first pass brought geometry in and left the arena grey - the FBX names its
maps, but the textures ship in a SIBLING folder, so nothing resolved. This pass
imports them and builds the materials the audit says the asset wants:

  UNLIT, base colour straight out of the diffuse map, nothing else.

That is not a shortcut. The pack is hand-painted diffuse-only at 256-1024 with
its lighting painted into the albedo (audit item 6). Feeding those maps to a PBR
lit material double-lights them - the painted highlights get lit again - and the
flat cartoon read the style depends on is exactly what gets lost. Unlit is the
faithful choice, and it is also why the arena will not respond to the ring lights
later: that is the trade, taken deliberately.

Meshes are matched to textures by longest normalized-name prefix, because the
author named both systematically ('cartoon boxing arena 3' -> every mesh whose
name starts cartoon_boxing_arena_3...). Every assignment is logged so a wrong
guess is visible rather than silent, and unmatched meshes keep the default
material rather than being given something arbitrary.

Run:  UnrealEditor-Cmd.exe <uproject> -run=pythonscript
          -script=".../import_fab_materials.py" -unattended -nopause
"""
import os
import re

import unreal

VAULT = r"C:\ProgramData\Epic\EpicGamesLauncher\VaultCache\FabLibrary"
TEX_DIR = os.path.join(VAULT, "Cartoon_Boxing_Arena2023-1ab88bac", "fbx",
                       "cartoon-boxing-arena2023_extracted", "textures")
ARENA = "/Game/FabImports/CartoonBoxingArena"
TEXS = ARENA + "/Textures"
MATS = ARENA + "/Materials"
GLOVE = "/Game/FabImports/BoxingGlove"

AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def import_textures():
    if not os.path.isdir(TEX_DIR):
        unreal.log_error("MAT: texture folder missing: %s" % TEX_DIR)
        return []
    files = [os.path.join(TEX_DIR, f) for f in sorted(os.listdir(TEX_DIR))
             if f.lower().endswith((".png", ".tga"))]
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", files[0])
    tasks = []
    for f in files:
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", f)
        t.set_editor_property("destination_path", TEXS)
        t.set_editor_property("automated", True)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("save", True)
        tasks.append(t)
    AT.import_asset_tasks(tasks)
    out = []
    for t in tasks:
        for p in (t.get_editor_property("imported_object_paths") or []):
            out.append(p)
    unreal.log("MAT: imported %d textures" % len(out))
    return out


def make_master(name: str, folder: str):
    path = folder + "/" + name
    if EAL.does_asset_exist(path):
        return unreal.load_asset(path)
    mat = AT.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    tex = MEL.create_material_expression(
        mat, unreal.MaterialExpressionTextureSampleParameter2D, -400, 0)
    tex.set_editor_property("parameter_name", "BaseTex")
    # Unlit takes its colour from emissive - there is no lit base colour to feed.
    MEL.connect_material_property(tex, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.recompile_material(mat)
    EAL.save_asset(path)
    unreal.log("MAT: master material %s" % path)
    return mat


def make_instance(master, tex_path: str):
    tex = unreal.load_asset(tex_path)
    name = "MI_" + tex.get_name()
    path = MATS + "/" + name
    if EAL.does_asset_exist(path):
        mi = unreal.load_asset(path)
    else:
        mi = AT.create_asset(name, MATS, unreal.MaterialInstanceConstant,
                             unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, master)
    MEL.set_material_instance_texture_parameter_value(mi, "BaseTex", tex)
    EAL.save_asset(path)
    return mi, norm(tex.get_name())


def assign(meshes, instances):
    """Longest normalized texture name that prefixes the mesh name wins."""
    assigned = unmatched = failed = 0
    for mp in meshes:
        mesh = unreal.load_asset(mp)
        if not isinstance(mesh, unreal.StaticMesh):
            continue
        n = norm(mesh.get_name())
        best = None
        for mi, key in instances:
            if n.startswith(key) and (best is None or len(key) > len(best[1])):
                best = (mi, key)
        if best is None:
            unmatched += 1
            unreal.log("MAT:   unmatched mesh (default material kept): %s"
                       % mesh.get_name())
            continue
        try:
            sms = mesh.get_editor_property("static_materials")
            if not sms:
                failed += 1
                continue
            sms[0].material_interface = best[0]
            mesh.set_editor_property("static_materials", sms)
            EAL.save_asset(mp)
            assigned += 1
            unreal.log("MAT:   %s -> %s" % (mesh.get_name(), best[0].get_name()))
        except Exception as exc:            # noqa: BLE001 - reported, not swallowed
            failed += 1
            unreal.log_error("MAT:   assign failed on %s: %s" % (mesh.get_name(), exc))
    unreal.log("MAT: assigned=%d unmatched=%d failed=%d" % (assigned, unmatched, failed))


def glove_material():
    """No textures shipped with the OBJ - it is geometry only, straight out of
    Blender with no mtllib. A flat red keeps it in the arena's key rather than
    leaving a grey lump on the end of a fighter's arm; the seller's own maps can
    replace it whenever the Director downloads the listing's extra files."""
    master = make_master("M_UppercutFlat", MATS)
    path = MATS + "/MI_BoxingGlove_Red"
    if not EAL.does_asset_exist(path):
        mi = AT.create_asset("MI_BoxingGlove_Red", MATS,
                             unreal.MaterialInstanceConstant,
                             unreal.MaterialInstanceConstantFactoryNew())
    else:
        mi = unreal.load_asset(path)
    MEL.set_material_instance_parent(mi, master)
    EAL.save_asset(path)
    for mp in EAL.list_assets(GLOVE, recursive=True, include_folder=False):
        mesh = unreal.load_asset(mp)
        if not isinstance(mesh, unreal.StaticMesh):
            continue
        try:
            sms = mesh.get_editor_property("static_materials")
            if sms:
                sms[0].material_interface = mi
                mesh.set_editor_property("static_materials", sms)
                EAL.save_asset(mp)
                unreal.log("MAT:   glove %s -> MI_BoxingGlove_Red" % mesh.get_name())
        except Exception as exc:            # noqa: BLE001
            unreal.log_error("MAT:   glove assign failed: %s" % exc)


def main():
    tex_paths = import_textures()
    master = make_master("M_ArenaUnlit", MATS)
    instances = []
    for tp in tex_paths:
        try:
            instances.append(make_instance(master, tp))
        except Exception as exc:            # noqa: BLE001
            unreal.log_error("MAT: instance failed for %s: %s" % (tp, exc))
    unreal.log("MAT: %d material instances" % len(instances))
    meshes = [p for p in EAL.list_assets(ARENA, recursive=False, include_folder=False)]
    assign(meshes, instances)
    glove_material()
    unreal.log("MAT: done")


main()
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | END ]
