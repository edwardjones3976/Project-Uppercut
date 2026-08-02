<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | START ] -->

# Combat-State Definitions - Semantics (ROADMAP Phase 1A, step 1)

**Canonical data:** `data/combat_states.json` - **Schema:** `schemas/combat_state_machine.schema.json`
**Validator:** `tools/uppercut_validate/combat_states.py` (`python -m tools.uppercut_validate.cli states`)
**Status:** definitions committed and validated. No engine implementation, no simulation code, and no
playable behavior is claimed (Rule 18).

## Authority and engine posture

These definitions are engine-neutral canon. Per Decision 0002 / Rule 22, the Unreal sandbox
*implements* this machine; it does not redefine it. If implementation discovers a needed change, the
change lands here first, because sandbox acceptance criterion A.1 requires combat states to exist *and
be inspectable* - this data file and document are the inspectable form.

## The three machines

**match_flow** - owned by the authoritative Match Controller: entrance, live rounds, 30-real-second
breaks that menus do not pause (Rule 9), the knockdown count, doctor checks, and the sealed-card
post-fight flow (Rule 3).

**fighter_action** - one per fighter, identical for human and CPU control (Rule 5). Move commitment is
the spine: `idle -> move_startup -> move_active -> move_recovery -> idle`, every phase duration bound
to authored move data (`startup_frames`, `active_frames`, `recovery_frames`). Reactions (hit_stun,
staggered, knocked_down, rising), guard_hold, clinch and the provisioned ability states hang off that
spine.

**posture_continuum** - Rule 13's continuous, threat-responsive footwork model. Posture modes carry a
schema-enforced zero transition delay: locomotion is a continuum, not a gate. Stance (orthodox /
southpaw) is a dimension switched through believable steps and pivots (Rule 15), never a slow
artificial transition.

## Counterplay from the first punch

Rule 22 demands counterplay before the first punch is implemented, so it is structural: `move_startup`
is interceptable, `move_active` is trade-able, and `move_recovery` is counter-open with consequence
scaled by the commitment tier of the outcome - strictly increasing blocked -> dodged -> whiffed per
`data/contact_classes.json` (Rule 13). The validator fails the build if any of that is removed.

## Score isolation as structure

Transitions declare `guard_inputs` - the input domains their guards may read. The allowed list holds
only observable domains; `official_scorecards` and `sealed_events` are structurally forbidden and the
validator rejects any transition naming them (Rule 3). CPU intent flows through the same `commit_move`
transition as human input, reading the same observable domains, and emits `cpu_decision` records with
cited evidence (sandbox criterion B.11).

## Knockdowns and stoppages

Transitions into `knocked_down` require observable evidence triggers - never a flat per-punch roll
(Rule 14). `knocked_down` exits only to `rising` or `stopped`; a completed rise is governed by the
authoritative count clock plus the referee's mandatory look under universal minimums (Rule 16).
Stoppage reasons: ko, tko_referee_waveoff, tko_failure_to_intelligently_defend, tko_doctor,
corner_retirement, disqualification. Chin +100 is maximum authored resistance, never immunity.

## Provisioned architecture (ROADMAP steps 11-12)

`special_execution`, `ultimate_execution` and `full_crowd_trait_active` exist as provisioned slots so
Crowd Bar and ability work lands inside this machine instead of beside it. Provisioned states and
transitions are marked, use the `provisioned` trigger kind, and claim no implementation (Rule 18). The
full-bar Ultimate-XOR-Trait exclusivity (Rule 12) is declared as an invariant now and becomes a
simulation test at step 12.

## Determinism anchors

Every trigger kind is tick-anchored (`move_phase_end`, `condition_threshold`, `authoritative_clock`,
`count_clock`). Wall-clock triggers do not exist in the vocabulary - the structural half of sandbox
criterion E.19: same seed + same authoritative initial state -> byte-identical event log. Emitted event
names are validated against `schemas/fight_event.schema.json`, so the machine can only speak the
observable-event language the replay and telemetry systems already define.

## Reproduce

```
python -m pytest -q tests/test_combat_states.py
python -m tools.uppercut_validate.cli states
```

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | END ] -->
