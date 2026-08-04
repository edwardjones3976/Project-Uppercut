<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | START ] -->

# Asset Compatibility Audit — Cartoon Boxing Arena2023 (vustudios)

**Asset:** *Cartoon Boxing Arena2023* by vustudios, from Fab.
**Acquired:** 2026-08-04 by the Director.
**Location:** Epic Launcher Vault cache only —
`VaultCache/FabLibrary/Cartoon_Boxing_Arena2023-1ab88bac/usdz/converted/`,
containing `cartoon_boxing_arena2023.usdz` (2.6 MB), `metadata`, `thumbnail.jpeg`.
**Status: NOT YET USABLE — wrong format variant downloaded.** See below.

## The finding that matters

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

## Outcome

**Accepted, blocked on acquisition, with one gate item to close on import.** The
style fit is the best of the three Fab items and it should lead the project's
look. To finish: download the **FBX** variant (not USDZ), import, rebuild
materials as unlit/base-colour, scale the chosen ring to the sim's coordinate
space — the sim's `min_center_distance_ru` and track axis are authoritative, so
the ring is fitted to the fight rather than the fight to the ring — and repaint
the baked lettering flagged at item 11.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | END ] -->
