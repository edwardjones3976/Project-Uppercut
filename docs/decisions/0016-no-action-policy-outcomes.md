# Decision 0016 — No-action outcomes implement Decision 0014

**Status:** accepted; runtime implementation pending Phase S integration  
**Date:** 2026-08-06  
**Authority:** derives from Decision 0014, G2  
**Supersedes provisional branch numbering:** former local `0015-rest-and-no-action-are-first-class.md`

## Decision

Thinking is not a physical action. The policy may return:

- `Observe`
- `HoldPosition`
- `Rest`
- `MicroAdjust`
- `Move`
- `Guard`
- `Evade`
- `Attack`

`Rest` yields initiative and may concede position. `Observe` receives no special recovery beyond the accepted baseline. `MicroAdjust` pays for actual displacement.

## Implementation boundary

These outcomes must enter the shared policy contract and shared C++ runtime. Adding an `idle` entry to a flat random action table does not implement this decision.

## Acceptance

Decision frequency and physical-action frequency are separately measurable, no-action choices emit reason codes, and a boxer may read the opponent without spending stamina on an invented step.
