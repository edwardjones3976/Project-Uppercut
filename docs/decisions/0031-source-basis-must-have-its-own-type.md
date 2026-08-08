# Decision 0031 — Source basis must have its own type

**Status:** Accepted  
**Date:** 2026-08-08  
**Authority:** Director

## Decision

Decision 0029 requires semantically different quantities to remain non-substitutable at live-runtime authority boundaries.

The current typed-quantity branch contains a helper named `per_second_to_per_tick()` whose source parameter is typed as `WindPerTick` even though the helper describes the incoming value as per-second. That is rejected.

A conversion source must carry its actual source basis in its type. If the helper remains, introduce `WindPerSecond` and make the legal conversion:

`WindPerSecond -> WindPerTick`

Otherwise remove the helper until a real per-second Wind source exists.

No helper may accept one basis type and reinterpret it as another merely because the numeric representation is compatible.

The same rule applies to future Reserve, movement, time, or other quantity families.

## Runtime normalization

A canon loader may normalize a declared authoring basis into a runtime basis once at an explicit boundary. After conversion, the returned type must truthfully describe the normalized basis. Call sites may not be required to remember a hidden former meaning.

## Merge requirements

Before the Decision 0029 typed seam merges:

1. Per-second Wind cannot be supplied where per-tick Wind is required without an explicit named conversion.
2. `WindPerTick` cannot be accepted as the source of the per-second conversion.
3. Conversion at the authoritative tick rate follows the declared floor semantics.
4. Mutation to the wrong source type fails at the intended type guard.
5. Telemetry never labels a per-second source as per-tick before conversion.

This is an implementation refinement of Decision 0029, not a new research lane.

> **A conversion may change a quantity's basis. A comment may not.**
