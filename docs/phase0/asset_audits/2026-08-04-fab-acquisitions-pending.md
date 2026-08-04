<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 17:32 UTC | START ] -->

# Fab Acquisitions — Audit Stubs (content not yet landed)

Three items entered the Director's Fab library on 2026-08-04. **None are audited
yet** — the audit checklist runs against actual content, and none of these have
been added to a UE project on disk. This file records the acquisitions and holds
one stub each so the pending state is visible; each stub becomes a full audit
(like the Game Animation Sample and Mixamo set audits beside this file) when its
content lands.

**To land them:** in the Epic Games Launcher → Library → Fab Library, use
**"Add to project"** (or download to Vault, then add) targeting the sandbox
project. That is a Director click — the launcher runs under the Director's
Epic account.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | edit: item 1 landed ] -->
> **Item 1 is no longer pending.** The PAKPROD pack was already added to the
> sandbox project when this file was written, and it is now fully audited and in
> use: `2026-08-04-pakprod-fighting-animations-boxing.md`. Its skeleton question
> resolved the best possible way — the clips are authored on UE5 Manny, so the
> planned Mixamo retarget was not needed at all. Items 2 and 3 remain pending.
<!-- [ edit end ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | edit: items 2 and 3 inspected ] -->
> **Items 2 and 3 are inspected and audited — and both need re-downloading.**
> The Director connected their Vault cache folders on 2026-08-04. Both hold the
> **wrong format variant**: the glove came down as a bare OBJ with no textures
> (its texture set is in the listing's separate *Additional files* zip), and the
> arena came down as the **USDZ conversion** rather than the author's FBX. Both
> are otherwise fine and both are now audited in their own files
> (`2026-08-04-boxing-glove-pedro-perin.md`,
> `2026-08-04-cartoon-boxing-arena-2023.md`), each with its remediation and, for
> the arena, one originality-gate item: baked lettering on the meshes.
>
> Neither is a UE-native pack — unlike PAKPROD, both need manual import and
> UE-side materials. This file's own guidance above ("Add to project") only
> applies to UE packs; a 3D-model listing has to be downloaded in a chosen format
> and imported by hand.
<!-- [ edit end ] -->

## 1. Fighting Animations - Boxing — PAKPROD (**purchased, $24.99**)

Role: primary boxing animation tier, superseding Mixamo clips per-move where its
quality wins. Expected contents per store page: boxing punch/defense/reaction
set authored for UE skeletons.
Audit expectations to check on landing: which skeleton it targets (UE4 vs UE5
Manny — determines whether it retargets or drops in), root motion policy, clip
inventory vs our named punch families, license tier purchased (standard Fab
license assumed — confirm seat/project terms on the receipt).

## 2. Boxing Glove — Pedro Perin (free)

Role: first prop/equipment mesh — gloves on the mannequins are the cheapest
"this is a boxing game" read at the visual pass.
Audit expectations: poly budget, whether it comes skinned/socketed or as a static
mesh needing socket attachment to the hand bones, texture set size, Fab free-tier
license terms.

## 3. Cartoon Boxing Arena2023 — vustudios (free/acquired)

Role: candidate ring + arena environment, replacing the primitive floor from
Phase K. Style is cartoon — matches the comedy-first art direction better than a
photoreal ring.
Audit expectations: scale sanity vs our ring dimensions (sim law: min_sep 0.28
world units between fighters — ring must be authored or scaled to the sim's
coordinate space, not the other way around), draw cost, whether ropes/canvas are
separate meshes (ropes matter later for cornering), license tier.

## Already landed and audited (for completeness)

**Game Animation Sample** — on disk (5.90 GB), audited 2026-08-04
(`2026-08-04-game-animation-sample.md`), accepted with modification.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 17:32 UTC | END ] -->
