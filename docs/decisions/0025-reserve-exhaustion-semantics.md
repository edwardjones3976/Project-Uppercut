# Decision 0025 — Reserve exhaustion semantics

**Status:** accepted  
**Date:** 2026-08-07  
**Authority:** Director  
**Extends:** Decision 0021  
**Evidence:** `docs/implementation/wind_reserve_runtime.md`

## RULING

`Reserve` is a bounded authoritative resource on the closed interval `[0, max]`.

A legal action may spend the fighter's remaining Reserve and request more load than remains. The action is not retroactively cancelled merely because its `reserve_load` exceeds the pre-action balance. Instead:

1. compute the action's declared Reserve expenditure;
2. subtract it from the current Reserve;
3. **saturate the authoritative Reserve value at `0` immediately**;
4. compute every Reserve-derived Wind ceiling, Wind recovery multiplier, balance modifier, and later-round effect from that clamped value.

Reserve-derived formulas may never consume a negative Reserve fraction.

The declared `recovery_from_reserve.floor_multiplier` is therefore a true lower bound. With the current hypothesis values, the multiplier cannot fall below `0.40` merely because one action crossed the zero boundary.

The same rule applies to the Wind ceiling's declared floor: resource underflow may not silently drive a formula below its authored minimum.

## WHY

The first shared C++ Wind/Reserve port exposed one genuine language-boundary disagreement: the implementation calculated the Reserve-derived recovery multiplier before clamping a just-overdrawn Reserve state. That allowed a negative numerator and produced different integer results across the Python and C++ paths for synthetic Reserve values below zero.

More importantly, it contradicted the authored model. Decision 0021 defines Reserve on a 0–100 scale, and `stamina_economy.json` declares an explicit recovery floor. A negative hidden state creates a third exhaustion regime that canon never authorized.

Boxing logic also argues against cancelling the action. A deeply fatigued fighter can still throw the punch that empties the tank. The consequence belongs in what happens **afterward**: reduced Wind ceiling and recovery, degraded balance and posture, poorer later-round work capacity, and increasingly expensive tactical choices. The resource model should represent exhaustion, not invent an invisible energy-credit check that vetoes already legal boxing actions.

## INPUT AND TRANSITION RULES

- Initial state, replay state, fixture state, and externally supplied authoritative state with `Reserve < 0` are invalid and must be rejected rather than silently normalized.
- Arithmetic produced by an authoritative step may cross below zero transiently inside the calculation, but the stored authoritative state must saturate to zero before any downstream state-dependent formula is evaluated.
- Between-round recovery saturates at `reserve.max`.
- No action receives free Reserve because the pool is empty. Its declared load is still recorded in telemetry even when only part of that load can be represented by remaining Reserve.
- A future design may introduce an explicit minimum-Reserve legality requirement for a specific action, but such a rule must be separately authored and may not be inferred from resource underflow.

## REQUIRED IMPLEMENTATION PROOFS

Before the Wind/Reserve runtime integration is accepted:

1. Python and C++ agree when an action spends Reserve from a positive value to exactly zero.
2. Python and C++ agree when an action's declared load exceeds the remaining Reserve.
3. Stored Reserve never becomes negative.
4. `recovery_from_reserve.floor_multiplier` is never violated by underflow.
5. `ceiling_from_reserve.floor_fraction` is never violated by underflow.
6. Externally supplied negative Reserve is rejected.
7. Between-round recovery cannot exceed `reserve.max`.
8. Telemetry preserves the requested `reserve_load` even when the authoritative balance saturates at zero.

## WHAT THIS DOES NOT DECIDE

- It does not tune Reserve loads or recovery values.
- It does not make Reserve a direct knockdown multiplier.
- It does not decide whether a later specific move should have an explicit minimum-Reserve prerequisite.
- It does not authorize broad stamina calibration before observable CPU policy produces boxing-like cadence.

## IMPLEMENTATION ORDER

1. Sync this Decision into `impl/0021-wind-reserve-runtime`.
2. Clamp Reserve before every Reserve-derived state calculation.
3. Add the eight proofs above to the shared Python/C++ stamina vectors.
4. Rerun stamina parity, full tests, validators, Unreal build, canon parity, and the existing Q/R/live proofs.
5. Rebase or merge current `main` into the stacked runtime branch after PR #18's merge.
6. Open the Wind/Reserve runtime PR against `main` only after those gates are green.

This Decision closes the overdraft question raised by the first shared runtime port.