# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | START ]
"""Import the Director's two Fab exchange-format assets into the sandbox project.

Run inside the editor:
    UnrealEditor-Cmd.exe <uproject> -run=pythonscript
        -script="tools/engine/import_fab_meshes.py" -unattended -nopause

Unlike the PAKPROD pack, which arrived as UE assets and needed no import at all,
these two are raw exchange formats - an FBX from a Unity-origin package and a
Blender-exported OBJ - so the import settings ARE the audit's remediation and
belong in source control rather than in somebody's memory of a dialog box.

Two settings carry the reasoning:
  - combine_meshes False on the arena. The package is six separate rings plus
    stands, fences, lights and monitors; combining them would weld six arenas
    into one mesh and make choosing between them impossible.
  - import_textures True, import_materials True. The textures are diffuse-only
    hand-painted maps (audit item 6). UE will build lit materials from them,
    which is wrong for the intended flat look - rebuilding them unlit is a
    deliberate later step, not something to fix by dropping the textures now.
"""
import os

import unreal

VAULT = r"C:\ProgramData\Epic\EpicGamesLauncher\VaultCache\FabLibrary"
ARENA = os.path.join(
    VAULT, "Cartoon_Boxing_Arena2023-1ab88bac", "fbx",
    "cartoon-boxing-arena2023_extracted", "source",
    "cartoon boxing arena2023_extracted", "cartoon boxing arena2023.FBX")
GLOVE = os.path.join(VAULT, "Boxing_Glove-b9bc411a", "obj", "boxingglove.obj")


def static_mesh_task(src: str, dest: str, combine: bool):
    opts = unreal.FbxImportUI()
    opts.set_editor_property("import_mesh", True)
    opts.set_editor_property("import_as_skeletal", False)
    opts.set_editor_property("import_animations", False)
    opts.set_editor_property("import_materials", True)
    opts.set_editor_property("import_textures", True)
    sm = opts.static_mesh_import_data
    sm.set_editor_property("combine_meshes", combine)
    sm.set_editor_property("generate_lightmap_u_vs", True)
    sm.set_editor_property("auto_generate_collision", True)

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", src)
    task.set_editor_property("destination_path", dest)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    task.set_editor_property("options", opts)
    return task


def main():
    tasks = []
    for src, dest, combine in (
            (ARENA, "/Game/FabImports/CartoonBoxingArena", False),
            (GLOVE, "/Game/FabImports/BoxingGlove", True)):
        if not os.path.isfile(src):
            unreal.log_error("IMPORT: source missing: %s" % src)
            continue
        tasks.append(static_mesh_task(src, dest, combine))

    if not tasks:
        unreal.log_error("IMPORT: nothing to do")
        return

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tools.import_asset_tasks(tasks)

    for task in tasks:
        made = task.get_editor_property("imported_object_paths") or []
        unreal.log("IMPORT: %s -> %d object(s)"
                   % (os.path.basename(task.get_editor_property("filename")), len(made)))
        for p in made:
            unreal.log("IMPORT:   %s" % p)

    unreal.EditorAssetLibrary.save_directory("/Game/FabImports", False, True)
    unreal.log("IMPORT: done")


main()
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | END ]
