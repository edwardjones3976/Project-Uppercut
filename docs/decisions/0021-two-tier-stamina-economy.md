# Decision 0021 — Two-tier stamina: Wind over Reserve

**Status:** accepted  
**Date:** 2026-08-06  
**Authority:** Director  
**Closes:** G7  
**Evidence:** `docs/plans/2026-08-06-the-stamina-economy-decision-packet.md`

## Ruling

Project Uppercut uses a two-tier stamina economy.

### Wind

`Wind` is the acute exchange resource. It answers whether a fighter can move, defend, evade, throw, recover position, and sustain the current burst.

- scale: 0–100;
- drained by committed movement, guard maintenance, evasion, attacks, and explosive effort;
- recovers during `Observe`, `HoldPosition`, and especially `Rest`, with recovery limited by tactical state;
- receives little or no recovery during attack, evasion, explosive movement, or active pressure;
- may recover substantially during a round, because a boxer can regain breath;
- directly informs immediate execution quality and knockdown vulnerability.

`Rest` is not safety. It yields initiative, may concede position, and is interruptible.

### Reserve

`Reserve` is whole-fight conditioning. It answers how much deep physical capacity remains after rounds, bodywork, repeated bursts, and accumulated exertion.

- scale: 0–100;
- drains slowly from sustained exertion, repeated high-intensity bursts, and declared body-condition effects;
- does not recover meaningfully during an active round;
- receives only declared partial recovery between rounds;
- limits Wind maximum, Wind recovery, balance recovery, and later-round work capacity;
- must make round ten meaningfully different from round one without making every tired fighter helpless.

A short pause may restore Wind. It may not restore Reserve or erase the history of the fight.

## Decouple effort from resource debit

The current model derives delivered impact from the cost of throwing the punch. That relationship must not force the stamina economy to pay the same number used to describe effort.

Every move therefore distinguishes:

- `effort`: the authored physical commitment used by impact and exertion models;
- `wind_cost`: the immediate acute-resource debit;
- `reserve_load`: the slower conditioning burden.

During migration, the existing authored punch cost may seed `effort`. It is not automatically copied unchanged into `wind_cost`.

## Knockdown interaction

For the first implementation:

- acute Wind participates directly in immediate knockdown vulnerability;
- Reserve affects vulnerability indirectly through Wind ceiling/recovery, balance, posture, and condition;
- Reserve is not added as a second direct multiplier until evidence proves the indirect path insufficient.

This avoids counting deep fatigue twice.

## Initial experience targets

These are acceptance bands, not permanent tuning constants:

- ordinary professional-round activity should usually keep Wind between roughly 45 and 85;
- purposeful bursts may drive Wind into the 15–35 band;
- Wind below 10 should be visible, exceptional, and associated with severe exhaustion, hurt, or reckless output;
- later rounds should begin and recover worse as Reserve falls;
- patient pauses should restore exchange capability without restoring deep freshness;
- body investment and sustained pressure must have consequences that remain after Wind returns.

## Implementation order

1. author Wind and Reserve schemas and migration rules;
2. separate `effort`, `wind_cost`, and `reserve_load`;
3. implement state-dependent Wind recovery;
4. implement slow Reserve expenditure and between-round recovery;
5. integrate both into the shared C++ runtime;
6. rerun stamina equilibrium, work-rate, conversion, and Phase O evidence;
7. calibrate only after the integrated policy produces boxing-like action cadence.

## What this does not decide

It does not tune final costs, recovery rates, or conditioning curves. Those values require integrated live evidence.

It does not solve accumulated-damage influence on knockdown pressure. That remains a separate narrow investigation after the two-tier economy is live.

## Superseding condition

This architecture may be superseded only if an integrated live bout demonstrates that one resource can independently produce both recoverable exchange fatigue and persistent later-round deterioration without hidden exceptions or loss of style viability.
