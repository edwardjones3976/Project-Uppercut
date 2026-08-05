<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:45 UTC | START ] -->

# Decision 0017 — Ratification of Decision 0013, and its place in the queue

**Status:** accepted (Director ruling, 2026-08-05)
**Closes:** gate **G4**
**Date:** 2026-08-05
**Ratifies:** `docs/decisions/0013-guard-geometry-nuance-in-the-model-simplicity-at-the-controller.md`

## Decision

Decision 0013 is ratified in principle, in both halves:

- **The simulation eventually gains lateral guard geometry.** Coverage becomes
  angular; named guards remain authored postures over shared geometry, so
  Decision 0010 stands and Phase L's emergent results survive.
- **The controller does not gain analog guard steering.** Player controls stay
  discrete and readable. No thumbstick guard aiming.

## Scheduling, which is the part this record adds

Lateral expansion is scheduled **after** the live authoritative round works
end to end. It does not block that work, and the live round does not wait for it.

The reason is the shape of the risk. Angular coverage changes the guard model
underneath a phase (L) that is already proven and pinned; doing that while the
round flow, policy and presentation are all still moving would mean debugging two
unfamiliar things through each other. The live round is also what makes lateral
geometry *judgeable* — whether hooks read correctly is a thing you watch, not a
thing you derive.

## The drift this leaves standing, deliberately

The pinned execution plan flags **ten guards against two guard volumes**. That
remains true and remains open. Ten authored postures currently express themselves
through two height lanes, which is the approximation Decision 0013 exists to
remove. Until it is removed, any statement of the form "these ten guards behave
differently" should be read as "these ten guards behave differently along two
axes," and the guard-expressiveness measurement says how much of that is real.

Ratifying 0013 does not close that drift. It schedules the work that will.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:45 UTC | END ] -->
