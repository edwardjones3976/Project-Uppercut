<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | START ] -->

# Asset Compatibility Audit — Boxing Glove (Pedro Perin)

**Asset:** *Boxing Glove* by Pedro Perin, from Fab (free). Listing category
Weapons & Combat; single real-time model advertised as game-engine optimized.
**Acquired:** 2026-08-04 by the Director.
**Location:** Epic Launcher Vault cache only —
`VaultCache/FabLibrary/Boxing_Glove-b9bc411a/obj/`, which contains exactly three
files: `boxingglove.obj` (251 KB), `metadata`, `thumbnail.jpg`.
**Status: NOT YET USABLE — wrong format variant downloaded.** See below.

## The finding that matters

This is **not a UE asset pack**. Unlike the PAKPROD animations, which arrived as
a UE project and dropped straight in, this listing publishes a raw **OBJ**
exchange mesh, and the OBJ variant is what the Vault holds. Two consequences:

1. **No textures.** The listing declares two formats — `obj` and an *Additional
   files* `zip`. Only the OBJ came down, and an OBJ carries geometry plus a
   material reference, not the maps themselves. Imported as-is, the glove is
   untextured grey. The `zip` variant is where the texture set will be; it needs
   downloading from Fab separately.
2. **Manual import, manual attachment.** There is no skeleton, no socket and no
   Blueprint. The path is: import the OBJ as a Static Mesh, then attach one
   instance per hand to the mannequin's hand sockets (`hand_l` / `hand_r` on
   `SK_Mannequin`), with a per-hand transform tuned by eye once.

Neither is a defect in the asset — it is a 3D model listing, and it is a good
one. It is a note that the *acquisition* is half done.

## Audit checklist

| # | Item | Answer | Evidence |
|---|---|---|---|
| 1 | Commercial license permits this use | **Yes** | Standard Fab license, free tier; commercial game use is the licensed use. Metadata carries `isAiForbidden: true` — the seller prohibits the asset being used as AI training/generation input. Recorded because it is a real term: it constrains what may be done *to* the asset, not our shipping it in a game |
| 2 | Modification rights | **Yes** | Standard Fab terms; a static mesh we rescale and re-material is ordinary use |
| 3 | Skeleton compatibility | **N/A — prop** | No skeleton. Attaches to hand sockets; skinning is not involved |
| 4 | Retargeting behaviour | **N/A** | |
| 5 | Root motion behaviour | **N/A** | |
| 6 | Performance cost | **Unmeasured, expected trivial** | 251 KB OBJ; two instances. Poly count to be read at import — the listing says real-time optimized and the geometry size supports that |
| 7 | Network suitability | **Yes** | Prop; presentation only |
| 8 | Visual consistency | **Mismatch flagged** | The thumbnail is a photoreal-leaning leather glove. Project direction is comedy-first and the arena candidate is cartoon. A photoreal glove on a cartoon mannequin in a cartoon ring is the kind of tonal split that reads as unfinished rather than stylised. Usable as placeholder; a style call is owed before it ships |
| 9 | Engine version support | **N/A — format, not version** | OBJ imports into any UE version; nothing is version-bound |
| 10 | Maintainability | **Static** | Free single-model listing, published 2024-10-27, no updates expected |

## Originality gate

| # | Item | Answer |
|---|---|---|
| 11 | Recognisable likeness/name/branding? | **No** — a generic red boxing glove, no marks or logos visible in the thumbnail. Confirm on import that the texture set carries no brand text |
| 12 | Would an observer identify a source game/character? | **No** |
| 13 | Bundled protected audio/announcer/UI motifs? | **No** — geometry only |

## Outcome

**Accepted in principle, blocked on acquisition.** Nothing here disqualifies the
asset; it simply is not yet in a usable state. To finish: download the
*Additional files* (zip) variant from Fab for the textures, import OBJ + textures
as a Static Mesh, attach to `hand_l` / `hand_r`. The tonal question in item 8 is
the Director's call and is worth answering before the gloves become the thing
everyone sees.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | END ] -->
