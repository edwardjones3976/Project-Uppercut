<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | START ] -->

# Camera Behaviour - Semantics (ROADMAP Phase 1A, step 3)

**Canonical data:** `data/camera_model.json` - **Schema:** `schemas/camera_model.schema.json`
**Validator:** `tools/uppercut_validate/camera.py` (`python -m tools.uppercut_validate.cli camera`)
**Status:** definitions committed and validated. No engine implementation is claimed (Rule 18).

## The camera is downstream of truth

Three properties are fixed by schema constants rather than convention, because each protects
something the project has already paid to establish. The camera **writes no simulation state** - a
camera that could nudge position or timing would make resimulation depend on presentation, undoing
the determinism evidence of Phase B and C. It is **excluded from the authoritative event-log hash**,
because criterion E.20 wants replay to reproduce recorded presentation rather than re-derive it. And
framing is a **pure function of the observable event log and tick**, which is what makes that replay
reproducible at all: same log, same tick, same shot.

That last property also settles a subtler question. The camera appears by name in Rule 3's list of
systems that may not read official scorecards. A camera that framed the fighter ahead on the cards
would leak the scoring through the picture. So camera inputs are declared, and the validator checks
them against the same allowed/forbidden input domains the CPU policy uses.

## Twelve modes, one strict order

CPU vs. CPU is a first-class spectator experience (Rule 7), so the camera is a readability instrument
before it is a spectacle instrument. Framing modes carry integer priorities forming a **strict total
order** - no ties - and exactly one default mode sits at the bottom, so the selector is total: every
tick resolves to exactly one mode, and camera behaviour is inspectable rather than emergent
(criterion A.1).

The order encodes a value judgement worth stating plainly. Stoppages, knockdowns, the count and
doctor checks occupy the top; the Showmanship flourish sits below all of them and carries a hard tick
cap. Comedy is the highest *presentation* priority under Rule 17, but Rule 19 puts responsiveness and
readable cause-and-effect above humour in game feel, and Rule 8 already says event clarity outranks
queued dialogue during knockdowns. The camera inherits that: **the joke never outlasts the boxing, and
never covers the officiating.** The validator fails the build if a spectacle mode ever outranks an
officiating mode or loses its cap.

## Framing follows position; it does not redefine it

Range-driven modes are locked to the movement model's five range bands, and the validator requires
every band to be served by some framing - clinch and inside tighten without losing either fighter's
hands (so legal inside work stays distinguishable from fouling under Rule 16), mid and outside hold
the working exchange shot, out-of-range widens so ropes, corners and centre control make Ringcraft
visible rather than inferred. Trigger bands and declared distance bands must agree, so a mode cannot
claim to serve a band it never activates in.

## Readability guards

Rule 19's warning that visual speed may not destroy readable cause and effect becomes four
structural numbers: a minimum tick cooldown between cuts, a settle window that must fit inside that
cooldown, a maximum angular rate, and an absolute prohibition on cutting between a punch's active
window and its outcome event. Any mode that can be live during an exchange must keep both fighters
framed, which the validator enforces by inspecting trigger kinds rather than trusting a flag.

The prohibition list carries the rest, and the validator requires its four load-bearing intents to
survive rewording: no scorecard access, no writing simulation state, no framing a miss as a clean
landing (Rule 13's presentation half), and no wall-clock dependence.

## Reproduce

```
python -m pytest -q tests/test_camera.py
python -m tools.uppercut_validate.cli camera
```

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | END ] -->
