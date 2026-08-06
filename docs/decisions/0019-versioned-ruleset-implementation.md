# Decision 0019 — Versioned ruleset implementation of Decision 0014

**Status:** accepted; data implementation present, complete bout enforcement pending  
**Date:** 2026-08-06  
**Authority:** derives from Decision 0014, G5  
**Supersedes provisional branch numbering:** former local `0018-versioned-rulesets-and-the-professional-default.md`

## Decision

Every bout names and versions its ruleset.

The default is `Project Uppercut Professional Rules v1`:

- mandatory knockdown count;
- no standing eight count;
- no automatic three-knockdown stoppage;
- no saved-by-the-bell rescue;
- sealed scoring until reveal.

`Project Uppercut Arcade Three-Knockdown Rule` remains an explicit optional modifier.

## Implementation record

The feature branch adds versioned professional and arcade ruleset data, schema checks, and contract measurements. Those measurements show that removing the arcade stoppage reveals the unresolved knockdown-conversion problem rather than solving it.

## Remaining proof

The shared live bout must record and enforce the selected ruleset through count, stoppage, scoring, replay metadata, and verdict.
