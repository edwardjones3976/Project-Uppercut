<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 17:32 UTC | START ] -->

# Asset Compatibility Audit — Mixamo Boxing Set (28 FBX)

**Asset:** 28 animation clips exported from Adobe Mixamo (mixamo.com)
**Acquired:** 2026-08-04, by the Director, from a signed-in Adobe account; three
gap-fillers (both uppercut throws and the guard idle) delivered through the session
and landed the same day.
**Location:** `mixamo_boxing/` beside the repo content — treated like
`GameAnimationSample/`: a local source library. Files import into the UE project
during the mannequin visual pass, then retarget onto the UE5 Manny skeleton; each
import cites this audit.
**Export settings used (recorded for reproducibility):** FBX Binary, With Skin on
the first download (carries the Mixamo skeleton for retarget setup) / Without Skin
after, 60 FPS, no keyframe reduction, Mirror where a lead/rear variant was needed,
In Place for locomotion-adjacent clips.

## Inventory (28 files)

**Offense (7):** `jab.fbx`, `cross.fbx`, `Lead_Upper_Hook.fbx`,
`Rear_Lower_Hook_to_Body.fbx`, `Lead_Upper_Uppercut.fbx`,
`Rear_Lower_Uppercut_to_Body.fbx`, `Punching.fbx` (combo filler).
This completes one clip per named punch family in `data/pose_geometry.json`:
jab_lead, cross_rear, hook_lead (+ body hook), uppercut_rear (+ lead), body work.

**Defense (5):** `Idle_with_guard.fbx`, `Left Block.fbx`, `Right Block.fbx`,
`Upper_Center_Block.fbx`, `Dodging.fbx` (slip source).

**Hit reactions (12):** `Big Hit To Center of Head.fbx`, `Big Hit To Left of
Head.fbx`, `Big Hit To Right of Head.fbx`, `Light Hit To Head.fbx`, `Medium Hit To
Head.fbx`, `Head Hit Reaction.fbx`, `Receive Punch To The Face Reaction.fbx`,
`Hit To Body Reaction.fbx`, `Stomach Hit Reaction.fbx`, `Big Stomach Hit
Reaction.fbx`, `Receive Stomach Uppercut.fbx`, `Receiving A Big Uppercut
Reaction.fbx`.

**Knockdown / round-state (4):** `Livershot Knockdown.fbx`, `Taking_a_knee.fbx`,
`Defeat.fbx`, `Victory.fbx`.

## Audit checklist (all ten answered)

| # | Item | Answer | Evidence |
|---|---|---|---|
| 1 | Commercial license permits this use | **Yes** | Mixamo assets are royalty-free for use in commercial projects, including games, under the Adobe General Terms of Use / Mixamo FAQ ("You can use both characters and animations royalty free for personal, commercial, and non-profit projects"). Restriction honored: clips ship **embedded in the game**, never redistributed as standalone animation files. *Verification note: license text as published at audit date; re-verify at ship if Adobe revises terms.* |
| 2 | Modification rights | **Yes** | Modification/retarget explicitly within permitted use; retargeting onto Manny is the plan |
| 3 | Skeleton compatibility | **Via retarget** | Mixamo skeleton ≠ UE5 skeleton; UE IK Retargeter (Game Animation Sample provides the target skeleton and retarget tooling) is the designed path |
| 4 | Retargeting behaviour | **Expected clean, verified on import** | Mixamo→Manny is the single most-travelled retarget path in UE; each clip eyeballed after retarget, failures logged here |
| 5 | Root motion behaviour | **In-place by export choice** | In Place selected where offered; punches are effectively in-place. Sim owns all positioning (Phase K truth boundary), so root motion is unwanted anyway |
| 6 | Performance cost | **Yes** | Plain clip playback; trivial for a two-fighter scene |
| 7 | Network suitability | **Yes** | Presentation only; C++ core owns truth |
| 8 | Visual consistency | **Acceptable** | Mocap-derived generic boxing; livelier than primitives, below licensed-pack quality — placeholder tier until the PAKPROD pack (and later the animo Collection, wishlisted) supersedes per-clip |
| 9 | Engine version support | **Yes** | FBX 2019-era binary imports fine into UE 5.8 |
| 10 | Maintainability | **Static snapshot** | Mixamo clips don't update; acceptable for a frozen source library |

## Originality gate

| # | Item | Answer |
|---|---|---|
| 11 | Recognisable likeness/name/branding from an existing property? | **No** — generic mocap boxing motions, no character identity attached (skinned mannequin discarded at retarget) |
| 12 | Would an observer identify a source game/character? | **No** — these are stock motions used across thousands of projects; our identity comes from original characters, timing, and the comedy layer |
| 13 | Bundled protected audio/announcer/UI motifs? | **No** — animation-only FBX, no audio or UI |

## Outcome

**Accepted.** Full 28-file set approved for import + retarget onto UE5 Manny in the
mannequin visual pass. Known gaps, deliberately deferred: no clinch animations
(clinch is currently unreachable in natural play — step C problem, animate when it
becomes reachable), no referee motions (referee is not yet rendered), and lead/rear
mirrors beyond the exported set are produced with Mirror at retarget time rather
than as extra downloads.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 17:32 UTC | END ] -->
