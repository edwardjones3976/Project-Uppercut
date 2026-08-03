<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:41 UTC | START ] -->

# Decision 0010 — Guard Postures Are Coverage Extents, Not Volumes or Branches

**Date:** 2026-08-03
**Status:** Accepted under the Director's standing authorization (Decision 0009), issued as
"use your best judgment in your solutions."
**Scope:** the pinned execution-plan drift item "10 guards vs. 2 guard volumes need reconciling."
Closes it on mechanism. Amends nothing in Decision 0002; extends ROADMAP Phase 1A step 5.

## Context

`docs/design/boxing_guard_matchups.md` describes ten named guards. `data/collision_model.json`
declares two guard volumes, `guard_high` and `guard_body`. The two documents have been carrying an
unreconciled count since the design reference landed.

The framing added at landing — the ten structures are *postures* over the same two volumes, and
`guard_interception` stays authoritative — was the right shape but was written too tightly. It said
any entry contradicting `guard_interception` is "wrong by construction." A review pass on
2026-08-03 showed that clause condemned the document's most boxing-truthful content: the conditional
rows. A cross-arm bar riding low intercepts a chin-line uppercut and the same bar riding high does
not. A shell roll that is timed turns an overhand and the same roll arriving late does not. Those are
state-dependent *geometry*, and a fixed `guard_interaction` → volume map has no vocabulary for them.

Two exits were available: make the interception map posture-aware, or let posture states modulate the
volumes' coverage.

## Decision

**A guard posture influences collision only by modulating the coverage extent of the two declared
guard volumes.** Each volume carries a `coverage_extent` — the fraction of its nominal structure
actually presented on a tick — and an alignment state moves that number inside declared bounds.
`guard_interception` keeps deciding which volume is *permitted* to intercept a given punch path; the
extent decides whether it actually reaches. The resolution pipeline reads the resulting number and
never a posture's name.

Three bounds make the mechanism honest rather than a free parameter:

- **No state may zero a volume.** A guard covering nothing is a different posture, not a misaligned
  one. `extent_bounds.min` is greater than zero and the validator enforces it.
- **No state may exceed 1.0.** Nothing an alignment does extends a volume past its own structure.
  That ceiling is what keeps every guard a trade rather than a strictly-better option, which is the
  design principle the whole guard model rests on.
- **The mechanism may not be inert.** At least one posture must vary its extents across its states,
  or the drift is not closed — it is merely documented. `check_guard_alignment` fails a canon where
  every posture holds identical extents.

The alternative — a posture-aware interception map — is rejected. It would move design data into the
collision layer, create a second authority over blocking, and turn ten guards into ten hand-maintained
table rows. Extents keep the conditional matchups *emergent from geometry*, which is the project's
"emergent > hardcoded" rule doing its job: if a matchup does not fall out of the extents, the extents
are wrong, and that is a finding rather than a lookup entry to edit.

## Consequences

- `data/collision_model.json` gains a `guard_alignment` block, a `coverage_extent` on each guard
  volume, one prohibition (no branching on posture identity), and the `posture_is_geometry`
  invariant. The `guard_intercept` stage now reads `guard_coverage_extent`.
- Four worked examples ship with the model — the cross-arm and shell conditionals — labelled
  illustrative under Rule 18. They exist to prove the mechanism expresses the design reference's
  contested rows. The authored posture set remains **ROADMAP step 7** content; this decision builds
  the architecture, not the roster of guards.
- `tools/uppercut_validate/collision.py::check_guard_alignment` and fourteen tests in
  `tests/test_collision.py` enforce all of the above, each proven non-vacuous by mutation.
- The over-tight clause in `docs/design/boxing_guard_matchups.md` is amended in place, with the
  original author's tags untouched.
- Every extent number here is a tuning hypothesis (Rule 18). No engine implementation is claimed.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:41 UTC | END ] -->
