<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | START ] -->

# Asset Compatibility Audit — Fighting Animations: Boxing (PAKPROD)

**Asset:** *Fighting Animations - Boxing* by PAKPROD, from Fab
**Acquired:** 2026-08-04, **purchased by the Director, $24.99**, added to the
sandbox project through the Epic Games Launcher.
**Location:** `sandbox/Content/BoxingAttacks/` — 458.4 MB, 435 files, **git-ignored**
(see `.gitignore`, which carries the reasoning). The repo keeps the code that
consumes it and this audit, which names every consumed clip path; the content
itself is restored from Fab.
**Contents:** two full stance sets, `TRADITIONAL` (orthodox) and `SOUTHPAW`, each
156 files across Attacks / Defence / Common / Reactions, both **In-Place** and
**Root** variants of most clips; plus `Demo/Mannequins/`, which ships UE5 Manny and
Quinn (`SKM_Manny`, `SKM_Quinn`) on `SK_Mannequin` with their materials, textures,
IK rig and retargeter.

## Audit checklist (all ten answered)

| # | Item | Answer | Evidence |
|---|---|---|---|
| 1 | Commercial license permits this use | **Yes** | Standard Fab license on a paid purchase; use in a commercial game is the licensed use. Honored: content is not redistributed — it is git-ignored, not committed |
| 2 | Modification rights | **Yes** | Standard Fab terms permit modifying the assets within a project |
| 3 | Skeleton compatibility | **Yes, natively** | Every animation references `/Game/BoxingAttacks/Demo/Mannequins/Meshes/SK_Mannequin` — the UE5 Manny skeleton. Verified by reading the asset headers directly, not by assumption |
| 4 | Retargeting behaviour | **Not required** | This is the finding that reshaped the visual pass: no IK Retargeter, no Mixamo→Manny step, no retarget error surface at all. The clips play on Manny as authored |
| 5 | Root motion behaviour | **Both offered; In-Place consumed, Root rejected** | The pack ships `Root/` and `In-Place/` variants. We take In-Place **only** — a root-motion step would let an animation move a fighter, and position is the sim's. The rejection is on principle, recorded in the Director's own comments |
| 6 | Performance cost | **Yes** | Single-node clip evaluation, two characters. The 5,400-tick rendered bout completes in about a minute of wall clock |
| 7 | Network suitability | **Yes** | Presentation only; the C++ core owns truth, proven again below |
| 8 | Visual consistency | **Yes, at placeholder tier** | Mocap-grade boxing on neutral mannequins — a clear step above primitives, still placeholder until original characters. Naming is systematic (`KB_<Move>-<Hand><Body?>_<Stance>`), which made the action→clip map mechanical rather than guesswork |
| 9 | Engine version support | **Yes** | Loads and evaluates in UE 5.8; verified by running, not by the store page |
| 10 | Maintainability | **Acceptable** | Vendor pack, static once purchased. Source folder inside the uassets reads `/Game/KICKBOXING/...` — this is the boxing subset of PAKPROD's kickboxing library, so a future kick-inclusive pack from the same vendor would likely drop in on the same naming |

## Originality gate

| # | Item | Answer |
|---|---|---|
| 11 | Recognisable likeness/name/branding from an existing property? | **No** — generic technique animation on Epic's own mannequins. No character identity, no branding |
| 12 | Would an observer identify a source game/character? | **No** — an observer would recognise *boxing*, which is the point. Manny and Quinn are Epic's placeholder bodies and read as placeholders |
| 13 | Bundled protected audio/announcer/UI motifs? | **No** — animation, meshes, materials and textures only |

## Consumed clips (the exact dependency)

The Bout Director loads these thirteen and no others. If a fresh machine restores
the pack from Fab, these are the paths that must exist:

| sim action / lane event | clip |
|---|---|
| `jab_lead` | `TRADITIONAL/Attacks/In-Place/KB_Jab-L_T_IP` |
| `cross_rear` | `TRADITIONAL/Attacks/In-Place/KB_Cross-R_T_IP` |
| `hook_lead` | `TRADITIONAL/Attacks/In-Place/KB_Hook-L_T_IP` |
| `uppercut_rear` | `TRADITIONAL/Attacks/In-Place/KB_Uppercut-R_T_IP` |
| `body_straight_rear` | `TRADITIONAL/Attacks/In-Place/KB_Cross-RB_T_IP` |
| `step_in` | `TRADITIONAL/Common/In-Place/KB_Walk-F_T` |
| `step_out` | `TRADITIONAL/Common/In-Place/KB_Walk-B_T` |
| `step_lateral` | `TRADITIONAL/Common/In-Place/KB_Walk-L_T` |
| guard hold / idle | `TRADITIONAL/Defence/In-Place/KB_Guard_T` |
| punch stopped in a **closed high** lane | `TRADITIONAL/Reactions/In-Place/KB_Block-H_T_IP` |
| punch stopped in a **closed low** lane | `TRADITIONAL/Reactions/In-Place/KB_Block-B_T_IP` |
| punch landing **high** | `TRADITIONAL/Reactions/In-Place/KB_Hit-H_T_IP` |
| punch landing **low** | `TRADITIONAL/Reactions/In-Place/KB_Hit-B_T_IP` |

Plus `Demo/Mannequins/Meshes/SKM_Manny` and `SKM_Quinn` as the two bodies.

## Outcome

**Accepted.** This is the animation tier for the slice. Three deliberate
non-consumptions, each of which would have been the easy default:

*Root-motion variants* are rejected on principle (item 5). *SOUTHPAW* is untouched
because stance is not in the sim's state model — presentation does not get to
invent a fact the fight does not have; when stance enters canon, the clips are
already bought and waiting. *Parry, roll, evade, overhand and the slip-attacks* are
unconsumed because the Phase K action set has no such actions; they become
available the moment the core grows into them, which is a reason to like this pack
rather than a gap in it.

**Supersedes, in scope:** the Mixamo boxing set
(`2026-08-04-mixamo-boxing-set.md`) for everything this pack covers — it is on the
right skeleton, better authored, and licensed for exactly this. Mixamo remains
audited and on disk as the fallback library and as the source of motions this pack
lacks (knockdowns, taking a knee, defeat/victory), which the slice will need at
item 9.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | END ] -->
