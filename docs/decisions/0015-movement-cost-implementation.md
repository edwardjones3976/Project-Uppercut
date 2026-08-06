# Decision 0015 — Movement-cost implementation of Decision 0014

**Status:** accepted; implementation evidence present  
**Date:** 2026-08-06  
**Authority:** derives from Decision 0014, G1  
**Supersedes provisional branch numbering:** former local `0014-movement-costs-displacement.md`

## Decision

Ordinary movement is charged by actual displacement:

```text
stamina_cost = distance_travelled_ru × 0.60
```

A normal 0.22-ru advance costs 0.132. Zero displacement costs zero. A flat cost is permitted only for a separately named explosive movement action with its own commitment and recovery.

## Implementation record

The feature branch changes ordinary step moves to `cost_model: displacement`, preserves derived display values for readers, and adds validation tying those values to the locomotion authority. The existing Phase Q behavior is re-proven against the changed canon rather than assumed unchanged.

## Remaining proof

Stamina, cadence, policy, and Phase O evidence affected by the former flat cost must be rerun inside the integrated contract. This record does not claim that the stamina economy is solved.
