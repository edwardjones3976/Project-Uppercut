<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:34 UTC | START ] -->

# Decision 0011 — Anatomical Vocabulary Stays Prose; Eight Regions Stay Eight

**Date:** 2026-08-03
**Status:** Accepted under the Director's standing authorization (Decision 0009), issued as
"use your best judgment in solving all of these issues."
**Scope:** the target-region taxonomy question raised by the punch design reference, and the liver
asymmetry question raised by its region-resolution note. Extends ROADMAP Phase 1A step 5.

## Context

`data/condition_regions.json` declares eight physically strikeable regions: `head`, `jaw_chin`,
`eye_left`, `eye_right`, `torso_upper`, `torso_lower`, `arm_left`, `arm_right`. Every one has a
hurtbox, and the collision validator rejects any move targeting a region that does not.

The punch design reference reasons in finer anatomical terms — temple, cheek, nose, forehead, behind
the ear, crown, sternum, solar plexus, liver, floating ribs, collarbone. That vocabulary is good
boxing and it is the reason the document is useful. It is also ten-plus names against eight regions,
with no rule saying which way the mismatch resolves.

A second, sharper version of the same question came with it: the liver shot's defining property is
that it is asymmetric — a lead hook under the opponent's right elbow. But `torso_upper` and
`torso_lower` are declared `side: center`, while the eyes and arms are side-declared. So either the
torso splits, or the liver stays flavour.

## Decision

**The anatomical vocabulary stays design prose and maps down.** It does not become regions, and it
does not become hurtboxes. The mapping is now stated in the design reference itself: temple, cheek,
nose, forehead, behind the ear and crown map to `head`; the point of the chin and jaw hinge to
`jaw_chin`; sternum and solar plexus to `torso_upper`; liver, ribs and floating ribs to
`torso_lower`; guard arm and blocked volume to `arm_left` / `arm_right` plus `guard_integrity`. The
collarbone maps to nothing — a collarbone contact is a mistarget outcome, not a target. Prose names
may not appear in `target_regions` in move data.

**The torso is not side-split. The liver shot is a contact-quality outcome, not a region.** A lead
body hook that enters `torso_lower` from the opponent's open side, at good alignment, produces the
autonomic result; the same punch into the same region from the wrong side does not. Every input that
requires — entry geometry, stance relationship, contact alignment — is already computed by the
collision pipeline. Nothing new is needed.

## Why this way

Adding regions is the obvious move and the wrong one. Each new region needs a hurtbox, a condition
track, validator coverage, and a place in every downstream system that reads condition — and it buys
resolution the simulation cannot honestly use yet, because no fighter model distinguishes a nose from
a cheek in its consequences. Eight regions is not a limitation to route around; it is the level at
which the damage model currently tells the truth.

The liver ruling follows the same reasoning that produced Decision 0010. There, ten guards did not
become ten volumes — postures modulated the extents of two. Here, an asymmetric target does not
become two hurtboxes — geometry qualifies an outcome inside one. Both are the project's
"emergent > hardcoded" rule doing its job: if the liver shot does not fall out of entry side, stance
and alignment, then those values are wrong, and that is a finding rather than a table to hand-edit.

The cost is honest and worth naming: a mechanic keyed on entry geometry is harder to author and
harder to debug than a hurtbox with a name on it, and until step 8 defines condition tracking, the
liver outcome does not exist in any form. This decision fixes where it will live, not that it exists.

## Consequences

- The canonical mapping table lands in `docs/design/boxing-punches-guards-and-target-matchups.md`,
  which was condensed the same day to a link-and-defer structure so the matchup tables live in one
  place only.
- `condition_regions.json` and the collision model are unchanged. No new hurtboxes, no new regions.
- The liver shot is deferred to step 8 (condition and consequence) as a qualified outcome on
  `torso_lower`, with the qualification recorded here so it is not quietly rebuilt as a region.
- If a later phase genuinely needs sub-region resolution — a cut model that distinguishes brow from
  cheek, say — that is a new decision superseding this one, made on evidence that the simulation can
  use the resolution. It is not a schema tweak.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:34 UTC | END ] -->
