# Decision 0029 — Typed physical and resource quantities

**Status:** Accepted  
**Date:** 2026-08-08  
**Authority:** Director  
**Trigger:** Repeated movement/stamina basis defects surfaced during First Bell integration and the three-lens review

## Problem

The project has repeatedly produced defects where a numerically valid value is interpreted on the wrong basis:

- per-action cost charged per tick;
- authored stride length treated as actual displacement;
- displacement cap treated as commanded movement;
- values with identical primitive representation but different physical meaning passed through the same interfaces.

More validators around naked numbers would detect some mistakes after they are written. The live runtime instead needs interfaces that make the wrong interpretation difficult to express.

## Decision

All **new First Bell/live-runtime code** must use typed quantities at authority boundaries.

Historical frozen phase artifacts do not need to be retrofitted solely for aesthetic consistency. The rule applies to the shared live runtime and all new post-Q authoritative code.

### Minimum quantity families

The implementation must distinguish at least:

- `Ticks`
- `FightSeconds`
- `ReachUnits`
- `ReachUnitsPerTick`
- `Wind`
- `Reserve`
- `WindPerTick`
- `WindPerAction`
- `WindPerReachUnit`
- `ReserveLoadPerAction`
- dimensionless ratios/probabilities

Equivalent names are acceptable if their meaning is explicit and enforced.

## C++ rule

Do not pass semantically distinct authoritative quantities through generic `float`/`double` parameters when the boundary can reasonably carry a strong wrapper type.

Examples of acceptable shapes:

```cpp
struct FReachUnits { double Value; };
struct FWind { double Value; };
struct FWindPerReachUnit { double Value; };
```

or another strongly typed approach with equivalent compile-time separation.

Operations must be explicit:

```text
ReachUnits × WindPerReachUnit -> Wind
Ticks × WindPerTick -> Wind
One action × WindPerAction -> Wind
```

These must not be interchangeable simply because each contains a decimal number.

## Python/reference rule

Python contract code must preserve the same basis distinction through explicit types, dataclasses, enums plus validated values, or an equivalent representation.

Bare dictionaries containing `value` without a declared basis are not sufficient at integrated authority boundaries.

## Canon/data rule

Canon may remain human-readable JSON, but every cost/rate field entering the integrated runtime must resolve to one declared basis.

Unknown or missing basis fails closed.

A loader may normalize authoring representation into typed runtime values; it may not infer a basis from a convenient call site.

## Conversion rule

Conversions between basis types must occur in named functions or operators whose dimensional meaning is testable.

No implicit conversion may turn:

- stride length into displacement;
- per-second into per-tick;
- per-action into per-tick;
- cap into actual movement;
- requested Reserve load into remaining Reserve balance.

## Cross-language parity

Python and C++ must share fixtures proving the same typed quantity calculations at the integrated boundary.

Required mutation/adversarial cases include:

1. per-action value deliberately supplied to per-tick input;
2. per-tick value supplied to per-distance input;
3. stride/cap value supplied as actual displacement;
4. negative distance where the contract forbids it;
5. zero displacement produces zero distance-priced movement Wind;
6. identical raw numeric values on different bases remain distinguishable in telemetry;
7. locale and serialization cannot alter numeric meaning.

## Telemetry

Integrated event output should record both value and basis where ambiguity would otherwise be possible.

Example:

```text
movement_displacement_ru=0.081
movement_wind_rate_per_ru=0.60
movement_wind_debit=0.0486
```

This is preferable to one opaque field such as `movement_cost=0.0486`.

## Sequencing

Typed quantities are a **First Bell integration requirement**, not a separate research project.

Implement the minimum strong types while assembling integrated movement/stamina state, before the new integrated contract is pinned.

Do not delay the complete bout to retrofit every historical utility or document.

> **If two numbers cannot be legally substituted in boxing, the live runtime should not make them trivially substitutable in code.**
