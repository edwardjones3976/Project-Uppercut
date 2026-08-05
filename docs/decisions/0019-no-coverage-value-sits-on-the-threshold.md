<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 01:05 UTC | START ] -->

# Decision 0019 — No coverage value sits on the interception threshold

**Status:** accepted (Director ruling, 2026-08-05)
**Closes:** gate **G6**
**Date:** 2026-08-05
**Extends:** Decision 0010 (guard postures are coverage extents)

## Question

Two of the ten authored guards sat **exactly** on `pose_geometry`'s interception
threshold of 0.60:

    philly_shell   guard_body  0.60
    active_hands   guard_high  0.60

A lane authored exactly at the threshold is decided by the first point of arm
damage, or by whichever way a rounding lands. That is a knife edge, and neither
of these two was authored as one.

## Decision

**No guard coverage value may sit within the authoring margin of the interception
threshold**, unless a knife edge is explicitly intended and explicitly tested.
The margin is canon (`pose_geometry.guard.authoring_margin`), not a convention,
so it can be widened once and checked everywhere.

    authoring_margin = 0.05

    philly_shell  guard_body   0.60 -> 0.55   (moved to the EXPOSED side)
    active_hands  guard_high   0.60 -> 0.65   (moved to the PROTECTED side)

They move in opposite directions, and the direction is the decision:

- **The Philly shell is answered by bodywork.** That is the posture's whole
  identity — a lead shoulder and a low lead hand, beaten downstairs. Its body
  lane belongs on the exposed side of the threshold, and 0.55 is the same value
  `high_guard` already carries there, which is a reasonable statement of "no
  better than an ordinary guard downstairs."
- **Active hands parries.** Its defensive value is in an active behaviour this
  model does not yet represent; the current simplified model can only express it
  as coverage. Authoring it on the *protected* side with a real margin is the
  conservative reading — better that a not-yet-implemented parry reads as slightly
  too safe than that a guard named for its hands is beaten in the head lane by a
  rounding error.

A regression test asserts the invariant for **every** posture and lane, not just
these two, so the next authored guard cannot reintroduce the defect.

## What this is not

It is not a rebalance of the guard table. Eight of ten postures are untouched,
and the two that move do so by 0.05 in the direction their own description
already implied. Any change in guard-versus-punch outcomes larger than those two
lanes would indicate something else is wrong.

It is also not a claim that `active_hands` is now correctly modelled. It is a
placement chosen because the model is simplified; when the parry behaviour is
authoritative, the value is re-derived rather than kept out of habit.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 01:05 UTC | END ] -->
