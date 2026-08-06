# Decision 0020 — Guard-threshold authoring margin

**Status:** accepted; values and regression test present, validator pending  
**Date:** 2026-08-06  
**Authority:** derives from Decision 0014, G6  
**Supersedes provisional branch numbering:** former local `0019-no-coverage-value-sits-on-the-threshold.md`

## Decision

No guard coverage value may sit exactly on, or inside the declared authoring margin around, the interception threshold unless a numbered Decision explicitly authorizes the knife edge.

For the current two-lane model:

```text
interception threshold = 0.60
authoring margin = 0.05
philly_shell.guard_body = 0.55
active_hands.guard_high = 0.65
```

The Philly shell remains exposed to bodywork. Active Hands remains protected against predictable head singles in the simplified model.

## Implementation record

The feature branch changes the values and adds a regression test. That test is not the requested canon validator.

## Remaining proof

Add the same invariant to `tools/uppercut_validate`, with any exception requiring an explicit numbered Decision. The gate is decided; this engineering obligation remains open in Issue #9.
