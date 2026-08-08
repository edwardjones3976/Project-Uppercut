# Decision 0027 — Primary platform and input/accessibility floor

**Status:** Accepted  
**Date:** 2026-08-08  
**Authority:** Director  
**Trigger:** Three-lens panel review after First Bell foundation merge

## Decision

Project Uppercut is **PC-first, controller-first, television/monitor-framed, and console-ready**.

The current Windows/Unreal build is not merely an accidental development default anymore. It is the primary development and first shipping target unless a later explicit product decision changes it.

### Primary presentation target

Design the complete fight so that it reads correctly on a conventional 16:9 television or monitor at normal couch/desk viewing distances.

- Ring geography, ropes, corners, exits, pressure and footwork must remain spatially legible.
- Broadcast-style CPU-vs-CPU viewing is a first-class requirement.
- The UI must remain readable at 1080p without depending on tiny text, color-only state, or close phone viewing.
- Console compatibility should be preserved architecturally, but console certification, platform SDKs and release commitments are later production work.

### Mobile ruling

Mobile is **not a Version 1 primary gameplay target**.

The project may later support companion, streaming, spectating, replay, or deliberately redesigned mobile experiences, but the core game will not be framed around a phone-sized viewport if doing so sacrifices ring geography, analog movement fidelity, local multiplayer ergonomics, or readable boxing distance.

Phone-sized and compressed-video views remain useful **readability stress tests**, not target authority.

## Input surface

The baseline human input device is a modern gamepad, with keyboard and other devices supported through remapping.

The input layer must distinguish **intent acquisition** from **authoritative action execution**.

### Required accessibility/input behavior

- Full remapping.
- Guard may be configured as latched/toggle or hold behavior where the resulting authoritative guard state is identical.
- Input buffering is allowed and should be deliberate, bounded and visible in tests.
- Slightly imperfect physical input may resolve to the intended legal command when the mapping is unambiguous.
- Alternative devices and one-handed layouts should be supportable through remapping/adaptive-device compatibility.
- Important guard and condition states must remain readable without color alone.
- Camera shake, motion blur, flashes and related presentation intensity must later be adjustable without changing combat authority.

### Competitive integrity boundary

Accessibility may change **how an intent is entered**. It may not secretly change **what the resulting action is allowed to do** in head-to-head competitive play.

Therefore competitive modes do not receive accessibility-specific:

- shortened startup;
- shortened active/recovery frames;
- enlarged counter windows that alter combat outcomes;
- hidden stamina assistance;
- auto-combos;
- aim or guard automation that makes decisions for the player;
- damage or score adjustments.

Training and practice modes may slow time, pause, replay, demonstrate, constrain exercises, or otherwise teach mechanics, but the underlying move data remains the same.

> **Forgive the hand where possible; do not falsify the punch.**

## Why

The game’s design depends on ring geography, visible pressure, counterplay, footwork and a broadcast-readable CPU experience. A phone-first framing would force the core product to sacrifice those strengths before evidence says that trade is worthwhile.

At the same time, accessibility is cheapest before the human input layer hardens. The project therefore commits now to flexible input acquisition while protecting one unified competitive combat system.

## Acceptance requirements before Human-vs-CPU quality gate

1. One controller mapping works without three-point chord dependence for ordinary defense and offense.
2. Guard hold and guard toggle produce identical authoritative states.
3. Buffered and unbuffered input paths produce the same legal move timing after intent acceptance.
4. Full remapping exists.
5. At least one reduced-dexterity/adaptive-device layout is demonstrated.
6. Key fight information remains readable without color-only cues.
7. No accessibility setting changes authoritative move frame data in competitive play.

## Not authorized by this decision

- Mobile-first redesign.
- Console launch commitment.
- Human combat implementation before First Bell.
- Any competitive assist that changes outcome rules.
