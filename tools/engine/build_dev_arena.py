# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:30 UTC | START ]
"""Author L_UppercutDevArena. RUNS INSIDE THE EDITOR, never in the runtime.

Decision 0012 puts Python offline only, and this is what offline means: the map
is a build artifact produced once and committed, not something generated when
somebody presses Play. Nothing this file writes is read by the simulation.

    UnrealEditor-Cmd.exe <project> -run=pythonscript -script=build_dev_arena.py

Launch it through tools/engine/make_dev_arena.py, which handles the Turnkey
wedge that stalls every editor boot on this machine.
"""
import json
import os

import unreal

MAP = "/Game/ProjectUppercut/Maps/L_UppercutDevArena"
OUT = os.environ.get("UE_ARENA_OUT",
                     r"C:\Users\edwar\project-uppercut\sandbox\Saved\dev_arena.json")

report = {"map": MAP, "actors": [], "errors": []}


def note(kind, name):
    report["actors"].append({"kind": kind, "name": name})


def main():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    # A brand new empty level every time. Regenerating rather than patching
    # means the map in the repository is always exactly what this file says,
    # and a hand edit that someone forgot to describe here does not survive.
    les.new_level(MAP)

    # ---- the floor --------------------------------------------------------
    # 24 ring units of axis at 100 cm each; the plane is 100 cm, so 40x12 covers
    # the track with room to see the ropes being reached.
    plane = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    floor = eas.spawn_actor_from_class(unreal.StaticMeshActor,
                                       unreal.Vector(1200, 0, 0))
    floor.set_actor_label("Floor")
    floor.static_mesh_component.set_static_mesh(plane)
    floor.set_actor_scale3d(unreal.Vector(40, 12, 1))
    note("floor", "Floor")

    # ---- light ------------------------------------------------------------
    sun = eas.spawn_actor_from_class(unreal.DirectionalLight,
                                     unreal.Vector(0, 0, 900),
                                     unreal.Rotator(-50, -35, 0))
    sun.set_actor_label("Sun")
    note("light", "Sun")

    sky = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 600))
    sky.set_actor_label("SkyLight")
    note("light", "SkyLight")

    # ---- the fight --------------------------------------------------------
    director = eas.spawn_actor_from_class(unreal.UppercutMatchDirector,
                                          unreal.Vector(0, 0, 0))
    director.set_actor_label("MatchDirector")
    director.set_editor_property("seed", 4242)
    director.set_editor_property("round_length_seconds", 180)
    director.set_editor_property("auto_start", True)
    director.set_editor_property("capture_rows", True)
    director.set_editor_property("bind_default_keys", True)
    note("director", "MatchDirector")

    for index in (0, 1):
        f = eas.spawn_actor_from_class(unreal.UppercutFighterBase,
                                       unreal.Vector(0, 0, 0))
        f.set_actor_label("Fighter%d" % index)
        f.set_editor_property("fighter_index", index)
        f.set_editor_property("world_units_per_ring_unit", 100.0)
        f.set_editor_property("axis_direction", unreal.Vector(1, 0, 0))
        f.set_editor_property("axis_origin", unreal.Vector(0, 0, 0))
        f.set_editor_property("face_opponent", True)
        note("fighter", "Fighter%d" % index)

    # ---- the camera -------------------------------------------------------
    # Side on, because Phase Q is a fight about DISTANCE and a camera behind a
    # shoulder is the one angle that hides it.
    cam = eas.spawn_actor_from_class(unreal.CameraActor,
                                     unreal.Vector(600, -1400, 320),
                                     unreal.Rotator(-6, 90, 0))
    cam.set_actor_label("ArenaCamera")
    cam.set_editor_property("auto_activate_for_player",
                            unreal.AutoReceiveInput.PLAYER0)
    note("camera", "ArenaCamera")

    start = eas.spawn_actor_from_class(unreal.PlayerStart,
                                       unreal.Vector(600, -900, 100))
    start.set_actor_label("PlayerStart")
    note("start", "PlayerStart")

    les.save_current_level()
    report["saved"] = unreal.EditorAssetLibrary.does_asset_exist(MAP)


try:
    main()
except Exception as exc:                                   # noqa: BLE001
    # Written to the report rather than only raised: an editor run that dies
    # silently is indistinguishable from one that never started, which is the
    # failure mode this project has already been bitten by twice.
    report["errors"].append("%s: %s" % (type(exc).__name__, exc))

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=2)
unreal.log("dev arena report -> %s" % OUT)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 21:30 UTC | END ]
