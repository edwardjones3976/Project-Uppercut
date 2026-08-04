<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 09:30 UTC | START ] -->

# Asset Compatibility Audit — Epic Game Animation Sample

**The first completed audit** under `docs/phase0/asset_compatibility_audit.md` — the
gap the 2026-08-04 reuse review named ("no rendered proof that the asset-audit
workflow is actually being used") closes here.

**Asset:** Game Animation Sample (Epic Games official sample project)
**Acquired:** 2026-08-04, by the Director, through the Epic Games Launcher (Samples)
**Location:** `GameAnimationSample/` beside the repo content — **deliberately
git-ignored** (5.9 GB, 3,128 uassets). It is a local library, not repo content:
selected assets migrate into `sandbox/Content` only when the mannequin visual pass
consumes them, each migration cited against this audit in its own commit.
**Contents surveyed:** UE 5.8 project; hundreds of AAA locomotion animations built
for Motion Matching (AnimationWarping, PoseSearch stack); UE5 Mannequins (Manny/
Quinn), UE4 Mannequin, UEFN Mannequin, Echo, Paragon characters; Locomotor system,
input setup, demo level.

## Audit checklist (all ten answered)

| # | Item | Answer | Evidence |
|---|---|---|---|
| 1 | Commercial license permits this use | **Yes** | Epic Content License: content distributed by Epic through the Launcher/Fab for use in Unreal Engine projects; same agreement family as the engine, accepted by the Director 2026-08-02. UE-only use — Project Uppercut is UE-only by Decision 0002 |
| 2 | Modification rights | **Yes** | Sample content is provided to be modified and shipped in UE products |
| 3 | Skeleton compatibility | **Yes** | UE5 Manny/Quinn native — the exact skeleton the 2026-08-04 reuse plan standardizes on |
| 4 | Retargeting behaviour | **Yes** | None needed for UE5 mannequins; IK Retargeter available for Mixamo/pack imports onto the same skeleton |
| 5 | Root motion behaviour | **Yes** | Motion-Matching database with root-motion-aware locomotion; usable both as MM database and as individual clips |
| 6 | Performance cost | **Acceptable** | AAA sample tuned by Epic; MM stack heavier than clip playback — fine for a two-fighter scene; measured when integrated |
| 7 | Network suitability | **Acceptable** | Animation is presentation; the C++ core owns truth (Phase K proof), so netcode never depends on these assets |
| 8 | Visual consistency | **Yes** | Neutral generic mannequins — ideal placeholder tier before original characters |
| 9 | Engine version support | **Yes** | Published for 5.8; `EngineAssociation: 5.8` in its uproject |
| 10 | Maintainability | **Yes** | Epic-maintained official sample, updated with engine releases |

## Originality gate

| # | Item | Answer |
|---|---|---|
| 11 | Recognisable likeness/name/branding from an existing property? | **No** for the mannequins and locomotion set (the usable scope). **Paragon and Echo characters are Epic-branded identities — excluded from use**; they stay in the library folder and never migrate |
| 12 | Would an observer identify a source game/character? | **No** within the approved scope (mannequins + animations) |
| 13 | Bundled protected audio/announcer/UI motifs? | **No** in the approved scope; sample UI/audio stays behind |

## Outcome

**Accepted with modification** — approved scope is the UE5 mannequins (Manny/Quinn),
the locomotion animation set, and the Motion Matching machinery; Paragon/Echo/UEFN
characters and sample-branded presentation are excluded. No boxing punches exist in
this set: it supplies stance, footwork, idles and weight — the four named punches
come from Mixamo (free, audited on import) and later a licensed boxing pack
(Director's purchase). Migrations into `sandbox/Content` cite this audit per the
process doc.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 09:30 UTC | END ] -->
