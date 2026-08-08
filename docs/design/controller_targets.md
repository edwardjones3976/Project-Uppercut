<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 21:20 UTC | START ] -->
# Controller targets — the Director's named devices

**Director statement, 2026-08-08, recorded verbatim:**

> "This should be compatible with gaming controllers (e.g., PlayStation 5,
> Xbox, and Steam-compliant)."

## Why this file exists

Decision 0027 already rules the project **PC-first, controller-first,
television/monitor-framed, and console-ready**, and names "a modern gamepad" as
the baseline human input device. It does not name the devices. This does, so the
statement lives somewhere a build engineer will find it rather than only in a
conversation.

This is a **record, not a decision.** Decision 0027 is the authority; nothing
here overrides or extends it. If the device list needs to become binding it
belongs in a numbered Decision, and that is the Director's call.

## The targets, as stated

| Family | What it implies in practice |
|---|---|
| **PlayStation 5** | DualSense over USB and Bluetooth. Face/shoulder/trigger/stick layout with two analogue triggers. Haptics and adaptive triggers exist and are presentation, never authority — see below. |
| **Xbox** | Xbox Wireless Controller, the de-facto layout most PC middleware assumes. Impulse triggers are again presentation. |
| **Steam-compliant** | Steam Input, which is the practical umbrella: it normalises the two above plus Switch Pro, third-party pads, and the Steam Deck's built-in controls, and it gives players their own remapping layer whether or not the game ships one. |

Steam Input is the one that carries the most weight for the least work, because
supporting it well means the other two are largely handled and a large tail of
third-party and adaptive hardware comes with it.

## What this must not become

Decision 0027's rule governs, and it is the one sentence to keep:

> **Forgive the hand where possible; do not falsify the punch.**

So haptics, adaptive trigger resistance, rumble and LED state are all
**presentation**. They may report what the simulation did; they may never be
inputs to it, and a pad that cannot produce them must not play a different
fight. That is the same boundary Decision 0028 draws between the Crowd Bar and
the Audience Presentation State, applied to hardware: the building may erupt,
and the erupting may not move a scorecard.

The corollary matters for the accessibility floor 0027 sets. If adaptive trigger
resistance ever became a way to *time* a punch, then a player on a pad without
it — or a player who cannot press hard — would be playing a different game, and
"full remapping" would be a promise the hardware quietly broke.

## What is deliberately not being built yet

Nothing. Decision 0027's own sequencing puts human input proof **after** First
Bell, and the current critical path is Decision 0029 and the complete fight. The
one thing worth doing early is negative: **do not author an input scheme that
assumes a three-point chord**, because 0027 already requires that ordinary
offence and defence work without one, and because the panel's accessibility
consultant could not make that shape with his left hand.

A ten-posture guard selector is the obvious way to end up needing one. Decision
0028 has already separated the research catalogue from the number of player-
facing commands and deferred the count to a post-First-Bell readability test —
which is the same answer arriving from the other direction.

## Where this connects

- `docs/decisions/0027-primary-platform-and-input-accessibility-floor.md` — the authority
- `docs/decisions/0028-crowd-comedy-guard-and-observation-boundaries.md` — presentation may not touch authority
- `docs/plans/2026-08-08-post-first-bell-readability-pilot.md` — where the guard-count question is answered
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 21:20 UTC | END ] -->
