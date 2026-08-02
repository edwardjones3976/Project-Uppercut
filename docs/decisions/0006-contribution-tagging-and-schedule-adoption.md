<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ] -->

# Decision 0006 — Contribution Tagging, Schedule and Objectives Adopted

**Date:** 2026-08-02
**Status:** Accepted by explicit Director instruction
**Supersedes:** the "Mandatory contribution tags" and "Premature schedules and objectives" sections of
Decision 0005. Every other part of Decision 0005 stands unchanged.

## Context

Decision 0005 rejected mandatory contribution tags and held dates, objectives, workload, ownership and
acceptance thresholds pending Director approval after the objectives section was authored. During Phase 0
foundation work the Director issued an explicit instruction to the contrary: tags, dates and the
remaining held items are to be implemented.

PROJECT_NOTES.md and Decision 0005 both state that the latest explicit Director correction controls.
This record exists so the repository reflects that correction rather than contradicting it.

## Decision

1. **Contribution tagging is adopted.** Identifying tags are required at the start and end of every
   document, file and code contribution, per `CONTRIBUTION_TAGGING.md`. Data formats that cannot carry
   comments use a `contribution` object; schemas validating tagged data permit that key.
2. **The execution schedule is adopted.** The quarter of Monday 2026-08-03 through Sunday 2026-11-01,
   its five sprints and its milestone targets in `PROJECT_PLAN.md` section 5 are approved as the
   working schedule.
3. **The objectives are adopted.** `PROJECT_PLAN.md` section 3, PO1 through PO5, cease to be candidates
   and become the quarter's objectives.

## What does not change

Quality gates still govern phase boundaries. An adopted date is a commitment to report honestly against
a target, not permission to claim unearned progress: Rule 18 continues to require that status cite
committed evidence, and a gate that has not passed is reported as not passed regardless of the calendar.

Every other rejection in Decision 0005 remains in force — Crowd Bar terminology, score isolation, the
absence of a universal win-rate band, Unreal-first production, generic-fixture-before-character
separation, and the prohibition on importing another project's governance without approval.

## Still open

**Agent ownership and team governance.** Decision 0005 rejected the imported Claude-primary /
Codex-presentation split, and the Director's instruction did not name ownership specifically. Workstream
assignment therefore remains explicit-per-task until the Director rules. This is the one item this
decision deliberately does not adopt on inference.

## Consequences

- `CONTRIBUTION_TAGGING.md` is created and referenced from `CONTRIBUTING.md`.
- All Phase 0 foundation artifacts carry tags from creation.
- `PROJECT_PLAN.md` should be updated to remove the "pending ratification" language from sections 3
  and 5, and to close pending items 1 and 3 in section 9.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ] -->
