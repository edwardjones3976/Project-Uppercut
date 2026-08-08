# Decision 0028 — Crowd, comedy, guard and observation boundaries

**Status:** Accepted  
**Date:** 2026-08-08  
**Authority:** Director  
**Trigger:** Three-lens panel review

## 1. Crowd Bar is retained

The panel recommendation to delete the Crowd Bar is **rejected**.

Project Rules §12 remains authoritative:

- Crowd gain is earned from observable boxing and showmanship.
- Full Crowd creates a choice between an Ultimate and a Full-Crowd Trait.
- One completed bar cannot activate both.
- Crowd cannot alter official scores, judging criteria, hidden combat statistics, contact truth or stamina truth.

The Crowd Bar is a fighter resource mechanic. It is not the same thing as audience presentation intensity.

## 2. Earned presentation is added as a separate layer

The panel correctly identified a second need: the arena should visibly and audibly react to what already happened.

Create a **presentation-only audience state** derived from observable events. It may influence:

- crowd swell and silence;
- camera emphasis;
- replay selection;
- commentary urgency;
- standing/sitting audience animation;
- between-round presentation;
- post-fight highlight selection.

It may not alter:

- scoring;
- damage;
- stamina;
- collision;
- CPU knowledge;
- Crowd resource balance;
- knockdown eligibility.

A fighter does not spend audience noise. Presentation reflects the room; the Crowd Bar remains its own declared mechanic.

## 3. Comedy rule

The panel is right that “comedy-first” cannot remain only a label. The existing respectful-presentation rule is strengthened as follows.

Comedy may arise from:

- personality;
- timing;
- physical consequence;
- overconfidence;
- situational reversals;
- entrances;
- commentary;
- refereeing personality;
- rivalry;
- crowd reaction;
- truthful visual exaggeration.

Comedy must not depend on:

- ethnic, national, racial, gender or demographic caricature;
- treating a culture or origin as the joke;
- dehumanizing humiliation;
- portraying a fighter as inherently stupid or incompetent because of identity;
- falsifying collision, judging, stamina or damage.

A fighter may make a funny mistake or suffer an embarrassing moment. The project does **not** promise that nobody is ever laughed at. The boundary is dignity: the joke should survive if both players are sitting on the same couch.

Before named-fighter vertical-slice work begins, the project must scope at least one repeatable comedy grammar and one original example in each of: fight consequence, commentary, entrance/presentation and referee/crowd timing.

## 4. Ten named guards are not deleted

The panel recommendation to collapse the ten researched guard postures immediately is **rejected as premature**.

Decision 0010 remains authoritative: named guards are authored postures/coverage extents over the shared defensive geometry. The research catalog is not identical to the eventual player control surface.

### First Bell

First Bell continues with the simplest generic defensive controls required to prove the fight. It does not need to expose ten player-selectable guard commands.

### Before Human-vs-CPU

Run a readability/input test to determine how many guard families can be exposed directly to a player without confusion. Candidate named guards that fail the test may remain as:

- fighter-specific posture variants;
- animation/coverage flavor within a family;
- CPU-authored defensive tendencies;
- training/reference material.

No research is discarded merely because the player does not receive ten buttons or ten menu states.

## 5. Readability pilot is accepted after First Bell

After a complete integrated bout exists, run the proposed pilot as a **design test**, not canon evidence.

At minimum measure:

- static silhouette discrimination;
- exposed-lane comprehension (“where would you attack?”);
- real-speed motion over a ring background;
- couch-distance readability;
- compressed-video readability;
- a phone-sized viewport as a stress condition, not a target platform;
- one older participant and at least one participant with reduced visual acuity or corrected-vision challenge.

The panel’s suggested 20% confusion threshold is a starting hypothesis, not a binding canon value until tested.

## 6. Byte identity remains an authoritative merge gate

The panel proposal to demote cross-language byte identity to a release-only gate is **rejected for authoritative integrated simulation work**.

When Python and C++ jointly define an authoritative contract, parity remains required before that contract is promoted or pinned.

However, rapid exploratory work is allowed in explicitly labeled non-authoritative lab tools:

- Python-only experiments may be watched and measured.
- They may not create or move canon pins.
- They may not be represented as Unreal/C++ implementation evidence.
- A result becomes authoritative only after the required cross-language/runtime proof.

This preserves iteration speed without allowing experimental convenience to become combat authority.

## 7. Round-boundary persistence

Round-boundary save/resume is accepted as a future **offline** quality requirement for longer fights, not a First Bell blocker.

- Offline 6- and 12-round modes should eventually support deterministic resume at a sealed round boundary.
- Resume must preserve ruleset, seed/substream state, fighter state, round state, canon/data hashes and event history required for deterministic continuation.
- Ranked/online matches do not gain arbitrary save-and-resume behavior through this decision.

## Summary

The panel correctly identified presentation, accessibility and readability risks. It does not supersede established competitive mechanics merely because it prefers a simpler product.

> **Keep the deep model. Expose only the depth the player can actually read and control.**
