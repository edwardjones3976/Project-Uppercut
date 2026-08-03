<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:47 UTC | START ] -->

# Animation States - Semantics (ROADMAP Phase 1A, step 4)

**Canonical data:** `data/animation_model.json` - **Schema:** `schemas/animation_model.schema.json`
**Validator:** `tools/uppercut_validate/animation.py` (`python -m tools.uppercut_validate.cli animation`)
**Status:** definitions committed and validated. No engine implementation is claimed (Rule 18).

## Animation supplies pose; it never supplies truth

This is the layer that can most easily turn the entire simulation into a lie. Rule 13 promises that
visible action and authoritative result agree, and animation is the *visible* half of that promise.
Everything below follows from taking that seriously.

Three properties are fixed by schema constants. Animation **writes no simulation state** and is
**excluded from the determinism hash**, exactly as the camera is. The third is the one specific to
this layer and the easiest to get wrong: **hitbox transforms are sampled from authored pose at a tick
index, never from blended runtime playback.** Blending is a presentation concern. If collision read
the blended pose, contact classification would depend on frame timing and interpolation, and the
byte-identical determinism proven in Phases B and C would quietly stop being true. Pose data can be
authored per-frame against the skeleton; the *timing* comes from move data and the *authority* stays
with the collision pipeline.

A fourth constant closes a related hole: **root motion does not drive position.** Feet establish
position through the movement model (Rule 13). Root motion driving position would let an animation
clip overrule the locomotion contract, including its no-invisible-lunges displacement cap.

## This step closes the dependency step 5 was taken ahead of

When collision truth was defined ahead of this step by Director instruction, the recorded caveat was
that hitboxes ultimately attach to animated skeletons, making step 4 an implementation-level
prerequisite. That dependency now has an answer rather than a promise: hitboxes attach to authored
pose, sampled at tick indices, with timing owned by move data. The two layers meet at a defined seam
instead of an assumed one.

## The frame lock

Every one of the seventeen moves has an animation whose startup, active and recovery tick counts must
**equal the move table exactly**. The validator fails the build on any mismatch.

The duplication is deliberate. An animator authors to explicit counts, so the counts have to exist in
the animation data; the validator is the anti-drift mechanism that makes that duplication safe rather
than dangerous. A jab whose animation says 5 startup ticks while the move table says 4 is precisely
the disagreement between picture and timing that Rule 13 exists to forbid, and it is exactly the kind
of drift that creeps in silently over months of tuning.

Every non-provisioned combat state likewise has an animation, and the validator refuses animations for
the three *provisioned* states (Special, Ultimate, Full-Crowd Trait) — animating them would claim
architecture that is not implemented (Rule 18).

## Interrupts: a struck fighter never finishes throwing

Eight interrupt tiers in a strict total order. Stoppage sits highest, then knockdown, stagger, hit
reaction — all four must outrank `move_commit`, and the validator enforces that ordering directly.

The reason is not cosmetic. If a landed clean shot did not interrupt the struck fighter's in-flight
punch animation, a spectator would watch a fighter absorb a knockout blow while still visibly
throwing. That is the Rule 13 lie in its most obvious form, and the ordering makes it structurally
impossible. Below the reactive tiers, `move_commit` plays through its authored phases — because
commitment is real, and a committed punch that could be cancelled on reaction would delete the counter
windows the whole combat model is built on.

## Responsiveness, and a distinction the validator forced

Rule 19 puts *impressively responsive* first in the game-feel order, so visible response must begin
within one tick of the authoritative state change, and blending may never delay that change: the state
flips on its tick and the picture catches up.

The blend budget also has to stay shorter than a punch's windup, or the windup smears and the
interception window stops being readable (Rule 22). The first version of that rule checked the blend
against the shortest startup of *any* move — and immediately failed the build, because the guard's
2-tick startup is shorter than the 3-tick blend budget.

The rule was wrong, not the value. A 2-tick guard startup is not a windup carrying counterplay
information; it is a near-instant defensive action whose requirement is responsiveness, and
responsiveness is already bounded separately by when the visible response *begins*. Beginning a
response and completing a blend are different guarantees. Conflating them would have forced a 1-tick
blend budget across the entire game to satisfy a constraint the guard never actually imposed. The
check is now scoped to offensive windups, and a regression test pins the scoping so it cannot be
quietly re-broadened.

## Condition must be visible, and side-specific where it matters

Eleven condition regions are declared visually attributable, with the eyes and arms side-specific.
Rule 14 requires eye damage to be visible and side-specific without resorting to extreme visual blur;
the arms matter just as much for a different reason — arm attrition is the counterplay to passive
blocking, and counterplay a spectator cannot see is counterplay that appears not to exist (Rule 4).
Stamina and balance are carried in posture and guard height rather than a bar. Attribute-governed
states (Chin, Durability, Recovery, Composure) are deliberately excluded: their expression is
behavioural rather than a visible surface.

## Stance

Southpaw is the exact mirror, matching the movement model's own const — never a separate clip set with
divergent timing, which would smuggle a mechanical asymmetry into presentation. Stance changes emerge
from steps, pivots and pullbacks driven by the authoritative `stance_change` event, never from a slow
dedicated transition clip (Rule 15), and familiarity penalties live in attribute data.

## Reproduce

```
python -m pytest -q tests/test_animation.py
python -m tools.uppercut_validate.cli animation
```

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:47 UTC | END ] -->
