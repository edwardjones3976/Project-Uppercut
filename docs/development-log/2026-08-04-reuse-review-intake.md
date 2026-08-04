<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 07:20 UTC | START ] -->

# Intake — external reuse review (Director-relayed, 2026-08-04)

**Verdict received:** B+ for pre-existing-part usage. "Properly reusing pre-existing
technology, tools, and validated internal systems... not yet meaningfully reusing
animation, character, arena, audio, UI, or combat-template assets. That is appropriate
for the current phase, but the next rendered slice is exactly where broader reuse
should begin."

## Verification against the repository (Rule 18: check before acting)

Every factual claim examined holds:

- **Template**: sandbox created from the Blank template (engine setup runbook,
  2026-08-02) — `TP_Blank` per the review. Correct.
- **Modules**: `UppercutCore.Build.cs` depends on `Core`, `CoreUObject`, `Engine`,
  `Json` and nothing else. Correct.
- **Plugins**: ModelingToolsEditorMode and PythonScriptPlugin enabled,
  AndroidFileServer disabled, in the `.uproject`. Correct.
- **Python ecosystem**: `requirements.txt` is `jsonschema`, `referencing`, `pytest` —
  no bespoke frameworks. Correct.
- **Toolchain**: UBT + VS Build Tools 17.14.37 + MSVC 14.44 + Windows SDK, installed
  2026-08-04. Correct.
- **Asset-audit process**: `docs/phase0/asset_compatibility_audit.md` carries exactly
  the ten-item checklist plus the three-item originality gate the review describes.
  Correct — and the review is right that **no completed audit exists yet**, because no
  external asset has entered.
- **One timing note**: the review reads "no rendered fight exists" — it predates
  Phase K by hours. The first rendered slice now exists (`determinism_probe_results.md`,
  Phase K), built deliberately from engine primitives with zero content assets so the
  rendering-holds-zero-authority claim could be proven byte-for-byte before any asset
  pipeline entered the picture. That does not weaken the review's point; it sharpens
  where it lands: **from the next visual pass onward, hand-authored placeholder visuals
  stop and audited reuse begins.**

## Resolution (resolve, don't average)

The review's reuse boundary is **adopted as the plan of record** for the remaining
slice items — it is the same boundary Decision 0002 and Rule 22 drew, now with named
first steps:

1. **The fighters stop being cylinders at the next visual pass.** UE 5.8 ships the
   Third Person template content on this machine — Epic mannequin, locomotion set, and
   a `Variant_Combat` — under the Epic content license already accepted with the
   engine. Free, offline, no purchase, no new agreement. It enters through the
   asset-compatibility audit like anything else (its first completed audit will also be
   the rendered proof the review notes is missing), and the engine's Control Rig and
   IK Retargeter carry it.
2. **A licensed boxing animation pack is the Director's purchase decision.** Marketplace
   acquisition means payment and account action — outside standing authorization
   (Decision 0009), exactly like the two license gates before it. Candidates will be
   assembled with audit-sheet stubs for his review when animation work begins in
   earnest; the mannequin's own set covers locomotion and generic reactions until then.
3. **The truth boundary is restated where it will be tested next**: the C++ core keeps
   deciding startup, active contact, recovery, range, result, stamina and exposure;
   clips and montages show that truth and never create a second one. The Phase K
   mechanism — poses read sim state, markers stay byte-identical to the Python
   recomputation — is the enforcement pattern every animated slice inherits.
4. **Presentation-layer reuse (Niagara, MetaSounds, CommonUI, Sequencer, arena/crowd
   packs) stays staged behind the combat slice**, per the review's own pacing: "four
   punches moving two generic bodies is the next hill, not a neon civilization."

Nothing in the current slice path changes order: slice item 7 (guard and slip) proceeds
in the C++ core, and its visual pass is where item 1 lands.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 07:20 UTC | END ] -->
