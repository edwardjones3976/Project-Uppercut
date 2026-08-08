# Decision 0026 — Entity-scoped RNG ownership and recovery-space behavior

**Status:** Accepted  
**Date:** 2026-08-08  
**Authority:** Director  
**Applies to:** First Bell integrated contract and every later live bout runtime

## Context

The first observable-policy diagnostic produced two architecture findings before the integrated bout was pinned:

1. Decision 0022 partitioned randomness by subsystem, but two fighters still shared the same `policy_intent` cursor. If fighter A makes an additional policy decision, fighter B's later tie-break draw moves. That recreates within one subsystem the same hidden coupling Decision 0022 prohibited between subsystems.
2. The policy recognizes low Wind but, when the fighter is not already at outside or out-of-range distance, it mostly holds position. It has no explicit tactical behavior for **creating safe recovery space**. As a result, `Rest` can remain structurally unreachable in realistic pressure even when recovery is the strategic intent.

The same diagnostic also reported high movement Wind consumption. That finding does **not** authorize a stamina retune because the probe used a stand-in movement model. The authoritative movement rule from Decision 0014 remains displacement-priced and must be measured against the live range runtime before balance coefficients move.

## Ruling A — RNG ownership is hierarchical, not merely subsystem-wide

A single mutable cursor may not be shared by independent authorities whose draw counts can vary independently.

The integrated RNG namespace becomes hierarchical:

```text
<domain>/<owner>
```

where `owner` is a stable authority identity, never declaration order or container index.

### Fighter-local domains

At minimum, these are fighter-scoped:

- `policy_intent/<fighter_slot>`
- `defense_evasion/<fighter_slot>` when fighter-local stochastic choice exists
- `movement_range/<fighter_slot>` when fighter-local stochastic choice exists

The initial two-fighter bout uses stable bout slots such as `red_corner` and `blue_corner`, or an equivalent explicit participant identity authored in initial state. Runtime array position is not authority.

A decision-count change for one fighter may change that fighter's future local draws. It must not change the opponent's local draws merely because both belong to the same subsystem.

### Shared interaction domains

Contact, knockdown, recovery, judging and officiating are not blindly duplicated per fighter. Their randomness must be owned by the authority that actually makes the result:

- interaction/outcome draws should be keyed or scoped to a stable authoritative event/interaction identity;
- judge-specific draws, if any, are scoped to the judge identity;
- referee-specific draws, if any, are scoped to the referee identity;
- presentation randomness remains outside combat authority and may be further split by presentation channel.

The implementation may use child streams or counter/key-derived draws, but it may not reintroduce a single mutable domain cursor when independent consumption would create unrelated coupling.

### Required isolation proofs

Before the first integrated golden bout is minted:

1. Add one extra policy decision for red while holding blue's observation/history fixed; blue's next policy draw and decision must remain unchanged.
2. Add one extra blue decision; red remains unchanged.
3. Reorder participant declaration without changing stable participant identities; both local stream identities remain unchanged.
4. Presentation draws cannot move any fighter-local or authoritative interaction draw.
5. A judge draw cannot move another judge's stream.
6. No caller can obtain an unowned default cursor.

## Ruling B — Recovery is a strategic objective that must create space

`RECOVER` is not synonymous with immediate `Rest`.

A boxer low on Wind should seek a tactically safe recovery opportunity. The policy therefore needs an explicit recovery-space loop:

```text
Need recovery
    -> assess immediate threat and range
    -> if unsafe, create/defend space
    -> if safe, Rest
    -> remain recovery-seeking until a separate exit condition is met or a tactical emergency interrupts it
```

### Required tactical behavior

When recovery is desired:

- at unsafe inside/mid range, prefer a legal escape action such as retreat, pivot/micro-adjust, guard-while-exiting, or evasion as the current shared runtime permits;
- on ropes or in a corner, escape has priority over resting;
- if the opponent is actively advancing or attacking, the fighter may be denied recovery and must defend or move rather than receiving a guaranteed Rest;
- at outside or out-of-range distance with no immediate threat, `Rest` becomes eligible;
- `HoldPosition` may be valid when already safe, but it cannot be the only answer to “I need air” while the opponent remains close;
- entering recovery intent must use hysteresis: one threshold/condition enters recovery-seeking behavior and a separate recovered condition exits it, preventing one-tick oscillation.

Add explicit reason codes such as:

- `SEEK_RECOVERY_SPACE`
- `REST_WHEN_SAFE`
- `RECOVERY_DENIED`
- `RECOVERY_INTERRUPTED`

Exact thresholds remain provisional until the integrated live policy produces complete-bout cadence. They must be declared/configurable, not scattered magic numbers.

## Ruling C — Movement Wind remains priced by actual displacement

Decision 0014 remains binding:

```text
movement_wind_cost = actual_authoritative_displacement_ru * 0.60
```

Therefore:

- `stride_length_ru` is not a per-tick distance;
- `max_frame_displacement_ru` is a hard cap, not the distance a movement action automatically travels every tick;
- zero displacement produces zero locomotion travel debit under the current model;
- synthetic probes may drive at the cap as a stress case, but their resulting depletion rate may not be used to tune the `0.60` coefficient;
- the first tuning evidence must come from the integrated policy driving the real shared range/movement runtime and recording actual displacement.

A later blocked-movement effort cost may be modeled separately if boxing behavior requires it. It may not be smuggled into the displacement coefficient.

## Ruling D — Unit/basis safety becomes an acceptance requirement

The first policy diagnostic exposed a repeated class of unit mistake: a distance authored per step was consumed as though it were per tick.

Every stamina debit/recovery source used by First Bell must have an explicit basis in code/data or a mechanically enforced formula contract, such as:

- per tick;
- per second;
- per reach-unit displaced;
- per action/commitment;
- per round break.

Minimum regression proofs:

1. a movement action cannot debit `stride_length_ru` once per tick;
2. authoritative displacement never exceeds `max_frame_displacement_ru` per tick;
3. movement debit is computed from the observed displacement used by the same tick's range state;
4. zero displacement does not receive the travel debit;
5. a diagnostic that substitutes maximum displacement is labeled stress-only and excluded from fit/tuning evidence.

## Tuning prohibition remains

The diagnostic Wind traces are useful structural evidence, not fitted balance evidence.

Do **not** retune:

- `0.60 stamina/ru`;
- Rest recovery rate;
- HoldPosition recovery rate;
- Wind bands;
- Reserve coupling;

from the current stand-in round alone.

First integrate:

1. entity-scoped policy RNG;
2. recovery-space behavior;
3. the shared live range/movement runtime with actual displacement;
4. Wind/Reserve state;

then measure cadence and depletion again.

If the live integrated round still drives both fighters below intended bands under plausible boxing behavior, that becomes legitimate Director tuning evidence.

## Consequence for PR #23 and First Bell

PR #23 may not merge with the subsystem-wide fighter-local RNG coupling left intact.

Before merge it must:

- absorb this decision;
- make policy RNG fighter-scoped by stable participant identity;
- add the isolation tests above;
- add recovery-space behavior and tests;
- preserve the no-default-stream rule;
- retain the current diagnostic as a non-canon harness;
- rerun full tests, validators and the phase-proof matrix;
- regenerate `STATUS.md`.

No integrated golden bout is minted by this decision. First Bell remains the next product gate.
