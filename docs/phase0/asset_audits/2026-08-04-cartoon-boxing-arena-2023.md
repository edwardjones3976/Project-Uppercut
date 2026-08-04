<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | START ] -->

# Asset Compatibility Audit — Cartoon Boxing Arena2023 (vustudios)

**Asset:** *Cartoon Boxing Arena2023* by vustudios, from Fab.
**Acquired:** 2026-08-04 by the Director.
**Location:** Epic Launcher Vault cache,
`VaultCache/FabLibrary/Cartoon_Boxing_Arena2023-1ab88bac/`, in all four published
formats (`fbx/`, `glb/`, `gltf/`, `usdz/`). The FBX is the one that matters and it
is complete with textures.
**Status: complete and imported** — see the correction and the outcome below.

## Correction (2026-08-04, later the same day)

**The paragraph below was wrong, and it is left standing rather than deleted so
the mistake is legible.** It concluded from a single connected folder that the
wrong format had been downloaded. In fact every format is present in the Vault —
`fbx/`, `glb/`, `gltf/` and `usdz/` all exist under
`VaultCache/FabLibrary/Cartoon_Boxing_Arena2023-1ab88bac/`, and the FBX arrived
complete with its texture set:

    fbx/cartoon-boxing-arena2023_extracted/
        source/cartoon boxing arena2023_extracted/cartoon boxing arena2023.FBX
        textures/  (15 PNG + 1 TGA, diffuse and light maps)

What was wrong was the folder connected to this session — `usdz/converted` — not
what the Director downloaded. The lesson is the ordinary one: a directory listing
scoped to one subfolder is evidence about that subfolder, and a claim about the
whole acquisition needed the whole acquisition in view. No remediation is
required; the asset is complete and ready to import.

## ~~The finding that matters~~ (superseded by the correction above)

The listing publishes three format groups: **FBX**, *Additional files* (zip), and
*Converted Files* (gltf / glb / usdz). What came down is the **USDZ conversion** —
Apple's AR container, and the least convenient of the three for Unreal. UE 5.8 can
import USD through the USD Importer plugin, but the path is fiddlier, material
translation is lossier, and a converted file is a derivative of the author's FBX
rather than the author's FBX.

**Re-download the FBX variant.** That is the whole remediation; the asset itself
is fine.

## What the listing contains (per its own description, to verify on import)

Six boxing arenas, crowd seating/stands, fences, light systems, electronic
monitors. Everything between 40 and 1,000 polygons, mobile-optimised, prefabs
included, hand-painted **diffuse-only** textures at 256 / 512 / 1024.

Two of those facts are worth pausing on. *Diffuse-only* means no normal, roughness
or metallic maps — the models carry their shading in the albedo, which is exactly
right for a flat cartoon look and exactly wrong if anyone later expects PBR
response from them. And *prefabs* is Unity vocabulary: this is a Unity-origin
package published to Fab, which is consistent with the FBX-plus-textures shape and
means no UE Blueprints, materials or collision come with it. Materials get rebuilt
UE-side (unlit or a simple base-colour-only material), which is a small, one-time
job and preserves the intended look.

## Audit checklist

| # | Item | Answer | Evidence |
|---|---|---|---|
| 1 | Commercial license permits this use | **Yes** | Standard Fab license; commercial game use is the licensed use. `isAiForbidden: true` in the metadata — the seller prohibits use of the asset as AI training/generation input; recorded as a real constraint on what may be done to the asset |
| 2 | Modification rights | **Yes** | Rebuilding materials UE-side and scaling the ring is ordinary permitted use |
| 3 | Skeleton compatibility | **N/A — environment** | |
| 4 | Retargeting behaviour | **N/A** | |
| 5 | Root motion behaviour | **N/A** | |
| 6 | Performance cost | **Very low** | 40–1,000 polys per model, textures ≤1024, diffuse only. A cheap environment is the correct trade for a two-fighter scene where the fighters carry the frame |
| 7 | Network suitability | **Yes** | Static environment |
| 8 | Visual consistency | **Good fit, on direction** | Cartoon styling matches a comedy-first game far better than a photoreal ring, and it resolves the tonal question the glove audit raises: the ring is the larger surface, so it should set the style and the props should follow it |
| 9 | Engine version support | **Format-bound, not version-bound** | FBX imports cleanly into 5.8; the USDZ variant on disk needs the USD Importer plugin and is not the recommended path |
| 10 | Maintainability | **Static** | Published 2024-10-05, no review history, no updates expected |

## Originality gate — one item to check on import

| # | Item | Answer |
|---|---|---|
| 11 | Recognisable likeness/name/branding? | **Check required.** The thumbnail shows **baked-in text on the meshes** — a jumbotron reading "welc…" and a cage floor reading "Big Show". These are the author's placeholder dressing, not a protected mark as far as can be told, but *any* baked text in our ring is text an audience will read as ours. Read the diffuse maps at import and repaint or blank any lettering |
| 12 | Would an observer identify a source game/character? | **No** — generic cartoon arenas |
| 13 | Bundled protected audio/announcer/UI motifs? | **No** — meshes and diffuse textures only |

## Imported, materialled and rendered (2026-08-04)

Done, in three scripted passes kept in `tools/engine/` so the settings are source
control rather than somebody's memory of a dialog:

`import_fab_meshes.py` brought in 68 static meshes, `combine_meshes` off so the
six rings stay separable. `import_fab_materials.py` imported the 15 textures the
FBX names but does not carry (they ship in a sibling folder, so nothing resolved
on the first pass) and built an **unlit** master material plus one instance per
map. Unlit is the faithful choice for a diffuse-only hand-painted pack: a lit PBR
material lights the painted highlights a second time and the flat cartoon read is
exactly what gets lost. The trade, taken deliberately: the ring will not respond
to the ring lights later.

`import_fab_fixup.py` exists because the second pass **reported success and
changed nothing**. `get_editor_property('static_materials')` returns a copy of the
array, and indexing it returns a copy of the struct, so mutating `sms[0]
.material_interface` writes to a temporary and the assignment is silently lost.
The element has to be put back: `sm = sms[0]; sm.material_interface = mi; sms[0] =
sm`. Final state: **56 meshes assigned, 0 failures, 12 unmatched** (chairs, table,
stairs, two fences, one high-light) which keep their FBX materials rather than
being given something arbitrary.

**Scale, measured.** The pack is authored at showroom scale: ring five is 195 m
across and the crowd stands are 727 m. Nothing was rescaled on disk — the scale
factor is computed at the spawn site from canon's own track length, where it can
be read next to the sim's numbers.

**One trap worth the note.** "Ring five" is a cluster in space, not a naming
convention, and the two facts disagree: `cartoon_boxing_arena_5_Led_` and
`_5_light_systems1` carry a 5 but sit 40 m away among arena one's fixtures.
Selecting the ring by name put it *beside* the fight instead of around it. The
Bout Director now spawns the seven meshes whose bounds actually cluster together,
found by measuring (`import_fab_bounds.py`) rather than by reading names.

**Rendered, and the truth boundary re-proved.** `-arena` on the render probe puts
the ring in the scene. The marker stream from a full 5,400-tick run with the ring
present is `b6f1c24b62671b8dc81b37057f851f33e075f9280d34b68f5cdcc346c0276bda` —
**byte-identical to the primitives run and to the mannequin runs**. Five runs,
three completely different presentations, one fight.

**Gate item 11, closed for ring five.** No baked lettering appears on the ring as
rendered. The "Big Show" cage floor and the jumbotron text in the store thumbnail
belong to other pieces in the pack; they remain a live check for anything else
imported from it, and are recorded as such rather than declared clean wholesale.

**Open, cosmetic:** light irregular patches on the canvas under the fighters,
consistent with two near-coplanar ring surfaces fighting for depth. Cosmetic only,
and it does not touch the sim. Worth a pass when the ring gets its polish.

## Outcome

**Accepted and in use.** The style fit is the best of the three Fab items and it
leads the project's look. Ring five is in the rendered slice, sized from canon's
track rather than from boxing's own dimensions — the sim's numbers win that
argument, and a ring the fighters could walk out of would be worse. The remaining
work is polish (the canvas depth artifact, framing, the other five rings) and one
standing check: any further piece imported from this pack gets item 11 read
again, because the pack does carry baked lettering elsewhere.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | END ] -->
