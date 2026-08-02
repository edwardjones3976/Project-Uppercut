<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | START ] -->

# Movement and Facing - Semantics (ROADMAP Phase 1A, step 2)

**Canonical data:** `data/movement_model.json` - **Schema:** `schemas/movement_model.schema.json`
**Validator:** `tools/uppercut_validate/movement.py` (`python -m tools.uppercut_validate.cli movement`)
**Status:** definitions committed and validated. No engine implementation is claimed (Rule 18).

## Range is reach-relative

Range lives in reach units: pairwise center distance divided by the mean of the two fighters'
authored reach. The coed, no-division roster (Rule 11) makes reach a real, visible asymmetry -
reach-relative bands balance it through geometry and counterplay instead of hidden modifiers. The
five bands are exactly move.schema.json's `range_band` values, contiguous from 0 with an unbounded
out_of_range tail.

## Hysteresis is the anti-magnetic-correction statement

A band change registers only after crossing the boundary plus 0.05 ru in the travel direction. That
kills range flicker, and it encodes the deeper Rule 13 law: the simulation never adjusts distance to
make a move fit. A wrong-range attempt whiffs with full commitment consequence. The validator also
walks the whole document for movement-assist vocabulary (`snap_to_range`, `magnetic_correction`,
`auto_face`, `teleport`, `range_assist`) and fails on sight.

## Locomotion locks to the posture continuum

Movement parameters attach to exactly the posture modes `data/combat_states.json` defines - the
validator enforces the cross-file lock, so neither file can drift alone. The compression law is
structural: free_navigation strides must exceed boxing_steps strides (threat-responsive compression
must actually compress), planted means stride zero, every mobile mode declares explicit acceleration
and deceleration frames (no ice skating), and the per-tick displacement cap sits below the longest
stride (no invisible lunges - including hit reactions and separation pushback). Bodies never overlap:
minimum separation resolves by bounded mutual pushback and must stay below the clinch ceiling so the
clinch band remains reachable.

## Facing tiles the circle and mirrors exactly

Four arcs - front (120 deg), lead side (60), rear side (60), back (120) - tile 360 with no gaps.
Punches are permitted only from the front arc. Southpaw geometry is the exact reflection of orthodox
(schema-enforced const): stance familiarity penalties are attribute data, never geometry (Rules 10,
11, 15). Facing away beyond 120 degrees raises the observable `back_exposed` flag for later referee
and judging hooks.

## Ring observables

A 6.4 m ring with rope- and corner-proximity thresholds feeds Ringcraft observables (ropes, corners,
center control) for Crowd rewards and judging evidence at later steps. All sizes are hypotheses.

## Reproduce

```
python -m pytest -q tests/test_movement.py
python -m tools.uppercut_validate.cli movement
```

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | END ] -->
