<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 22:20 UTC | START ] -->

# Decision 0012 — The C++ Fight Core, and a Document Freeze for the Slice Sprint

**Date:** 2026-08-03
**Status:** Accepted (Director, 2026-08-03, on the concurring recommendations of the
project's own next-steps analysis and an independent external review)
**Refines:** Decision 0002's technical responsibility split — the C++ "later" clause
fires now, for the authoritative fight core only
**Supersedes:** nothing; Decision 0002 stands in full

## Decision

Rule 22's C++ trigger **fires for the authoritative fight core**. The responsibility
split becomes:

- **C++:** the authoritative simulation core — fighter and match state, the
  authoritative clock and tick, collision resolution, the stamina/condition/knockdown
  arithmetic, attribute effects, scoring boundaries and sealed cards, replay
  serialization, and the foundations networking will later require.
- **Blueprints:** presentation and orchestration — cameras, entrances, effects, menus,
  the visual orchestration of Specials and Ultimates, audio hooks, and content glue.
  Blueprints never hold fight-deciding state.
- **Python:** validators, the reference simulator, telemetry, balance sweeps, asset
  utilities, reporting, and development automation — unchanged.

This is the split Decision 0002 described from the beginning; what changes is only the
tense of its C++ clause.

## Why now, on evidence rather than preference

Decision 0002 left the trigger "armed for scale, not correctness," and the record shows
exactly that shape:

1. **Correctness never fired it.** Seven engine phases (B through G) executed in the
   Blueprint VM byte-identically across same-seed processes and — for the later phases —
   across full asset regeneration, with zero mismatches against canon
   (`docs/phase1a/determinism_probe_results.md`). Blueprint determinism is proven, and
   nothing in this decision unproves it.
2. **Scale did.** Phase G's first run produced a defect that exists *only* because
   Blueprint's evaluation model differs from an imperative one: `RandomFloatFromStream`
   is a pure node that mutates the stream, so a pure chain with several consumers draws
   several times — the pipeline reported the correct contact class while the scoring
   read different draws, and the run hashed perfectly. It is now rule 7 of
   `tools/engine/bp_authoring.py`, the seventh entry in a list where every rule cost a
   debugging session. A full fight core — attributes, stamina, guard postures,
   knockdowns, referee, judges, match flow — is roughly an order of magnitude more
   graph than Phase G, and every one of those systems already exists as readable,
   tested Python executing canonical JSON.
3. **Two independent analyses converged.** `docs/plans/next_steps.md` ("The one
   decision that is yours") and an external review of 2026-08-03 recommended the same
   split for the same reasons, without sight of each other.

## What this does and does not change

- **Unreal remains authoritative** (Decision 0002). The C++ core is an Unreal module,
  not a departure from the engine.
- **The Python reference simulator remains non-authoritative** — it is the instrument
  the C++ core will be checked against, exactly as the Blueprint walkers were.
- **The Blueprint walkers (Phases B–G) are evidence, not production code.** They stay
  in the repository as the record that the canonical models are implementable
  deterministically in-engine; they are not extended further.
- **The conformance discipline carries over unchanged:** the C++ core must emit the
  same style of marker streams, be analyzed against canon by the same
  analyzer-first pattern (analyzer built and mutation-proven before the implementation
  runs), and reproduce byte-identically across same-seed runs and full rebuilds before
  any phase is called a PASS.
- **Canon stays the single source of truth.** The C++ core consumes the same
  `data/*.json` the validators enforce and the reference simulator executes. A number
  that exists only in C++ is the same defect as a number that existed only in the
  Python engine, and the coverage checker's laws apply to it identically.

## The document freeze (this sprint)

For the duration of the slice sprint, **no new major conceptual system enters the
repository as design surface** — no new schema, design document, contract, or
subsystem model — unless it is required to unblock an item on the slice path:

1. the Judge subsystem (extraction from `Bout`, sealed-card boundary);
2. referee-profile consumption (observable enforcement differences only);
3. the C++ core scaffold under this decision;
4. the two-fighter authoritative loop;
5. real movement and swept collision;
6. jab / cross / lead hook / rear uppercut animations on generic fighters;
7. guard and slip;
8. visible stamina and condition;
9. one rendered round with knockdown, decision or stoppage;
10. result and replay explanation.

**Exempt from the freeze,** because stopping them would rot the evidence culture the
freeze exists to protect: corrections to existing canon surfaced by validators or
checks; coverage-registry updates; evidence records for work performed;
synchronization of stable documents with STATUS.md; and this decision log itself.

The freeze's test is one question: *does this document move a rendered, responsive,
funny fight closer?* If the answer requires a paragraph, the answer is no.

## Consequences

- The next engine phase (Phase H) is a C++ scaffold proven by the established
  discipline, not a further Blueprint graph.
- `docs/plans/next_steps.md` step D resolves: engine work proceeds in C++.
- The open finding "the Rule 22 C++/Blueprint decision is with the Director" is
  closed and leaves STATUS.md's findings list.
- Rule 22's text in PROJECT_RULES.md remains accurate as written — "C++ enters later
  where performance, determinism, networking, or architecture requires it" — with
  "later" now dated: 2026-08-03, for the fight core, by this decision.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 22:20 UTC | END ] -->
