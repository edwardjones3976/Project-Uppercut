# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 20:35 UTC | START ]
"""Measure what the visual scale actually is, against researched real dimensions.

The first arena scaling was eyeballed - "1.7x the fighting axis" - and it was
wrong by about 44%. This measures instead: the mannequins' real height, the ring
parts' real proportions, and what each becomes at a given scale, so the numbers
in BuildArena can be checked rather than trusted.

Reference dimensions (researched 2026-08-04, see docs/design/ring_and_fighter_scale.md):
  ring inside the ropes   16-20 ft (4.88-6.10 m) pro standard, up to 24 ft
  canon's own ring side   6.4 m  (movement_model axis_length_derivation)
  apron beyond the ropes  >= 2 ft (0.61 m)
  ropes                   FOUR, at 18/30/42/54 in = 46/76/107/137 cm above canvas
  corner posts            ~5 ft (1.5 m) above the canvas
  middleweight height     180.6 cm average (top-10); heavyweight 194.3 cm
"""
import json

import unreal

EAL = unreal.EditorAssetLibrary
OUT = r"C:\Users\edwar\project-uppercut\sandbox\Saved\fab_scalecheck.json"
ARENA = "/Game/FabImports/CartoonBoxingArena"
RING = ["cartoon_boxing_arena_511", "cartoon_boxing_arena_5_1",
        "cartoon_boxing_arena_5_2", "cartoon_boxing_arena_5_3",
        "cartoon_boxing_arena_5_4", "cartoon_boxing_arena_5_5",
        "cartoon_boxing_arena_5_6"]

report = {"mannequins": {}, "ring_parts": {}, "derived": {}}

for name in ("SKM_Manny", "SKM_Quinn"):
    p = "/Game/BoxingAttacks/Demo/Mannequins/Meshes/%s" % name
    if EAL.does_asset_exist(p):
        b = unreal.load_asset(p).get_bounds().box_extent
        report["mannequins"][name] = {
            "height_cm": round(b.z * 2, 1),
            "extent": [round(b.x, 1), round(b.y, 1), round(b.z, 1)],
        }

canvas_top = None
for name in RING:
    p = "%s/%s" % (ARENA, name)
    a = unreal.load_asset(p) if EAL.does_asset_exist(p) else None
    if not isinstance(a, unreal.StaticMesh):
        continue
    box = a.get_bounding_box()
    report["ring_parts"][name] = {
        "centre_z": round(box.max.z / 2 + box.min.z / 2, 1),
        "min_z": round(box.min.z, 1),
        "max_z": round(box.max.z, 1),
        "width": round(max(box.max.x - box.min.x, box.max.y - box.min.y), 1),
    }
    if name == "cartoon_boxing_arena_511":
        canvas_top = box.max.z

# Canon's ring side, in cm: axis_length_ru 4.92 x reference_reach_span 1.30 m.
axis_cm = 4.92 * 130.0
ropes = [n for n in report["ring_parts"] if n.endswith(("_3", "_4", "_5", "_6"))]
if ropes and canvas_top is not None:
    span = report["ring_parts"][ropes[0]]["width"]
    scale = axis_cm / span
    report["derived"] = {
        "canon_ring_side_cm": round(axis_cm, 1),
        "rope_rect_units": span,
        "scale_to_make_ropes_the_ring": round(scale, 5),
        "apron_each_side_cm": round(
            (report["ring_parts"]["cartoon_boxing_arena_5_2"]["width"] - span)
            / 2 * scale, 1),
        "rope_heights_cm_at_that_scale": {
            n: round((report["ring_parts"][n]["centre_z"] - canvas_top) * scale, 1)
            for n in sorted(ropes,
                            key=lambda n: -report["ring_parts"][n]["centre_z"])},
        "regulation_rope_heights_cm": [137, 107, 76, 46],
    }

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1)
unreal.log("SCALECHECK: wrote %s" % OUT)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 20:35 UTC | END ]
