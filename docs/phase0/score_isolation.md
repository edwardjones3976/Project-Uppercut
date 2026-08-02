<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ] -->

# Phase 0 Gate Item — Scorecard Access Boundaries (documented and testable)

Rule 3, the Score Isolation Principle, is the rule most likely to be broken by convenience rather than
intent. A programmer wiring commentary needs "who is winning", the nearest correct answer sits in the
Judge subsystem, and one import later the firewall is gone. This document makes the boundary
executable so the failure is caught by a test rather than by a playtester.

## The boundary, as data

`data/score_isolation_contract.json` is the machine-readable form of Rule 3. It names:

- **sealed symbols** — identifiers that constitute official-score access
- **sealed event types** — `judge_round_card`, `judge_final_card`
- **authorized holders** — the Judge subsystem and the authoritative Match Controller, only
- **forbidden consumers** — all nine categories Rule 3 lists: human-facing fighter logic, CPU fighter
  logic, referees, trainers and corners, commentary, crowd systems, difficulty and adaptive systems,
  live replay presentation, and advice or bonus systems
- **the permitted substitute** — an observable-evidence estimate carrying explicit confidence

## Enforced in two directions

**1. Source.** `scan_source()` flags any sealed-symbol reference inside a forbidden-consumer path.

**2. Evidence.** `check_event_log()` reads a recorded bout and flags three failures: an official card
event not marked sealed; a CPU decision citing a sealed event as observed evidence; and a CPU decision
missing its forbidden-inputs assertion.

The event schema closes the loop structurally — `schemas/fight_event.schema.json` makes
`visibility: "sealed"` a schema requirement for judge card events, so an unsealed card fails
validation before it ever reaches the checker.

## Honesty note (Rule 18)

No simulation source exists yet, so the source scan currently has nothing real to police. A check that
passes because the tree is empty proves nothing. Its non-vacuity is therefore proved separately:
`tests/isolation_samples/violation_sample/` contains deliberate leaks in CPU policy and commentary,
and the suite **fails if the checker does not flag them**. When engine code lands under the contract's
paths, the same check becomes load-bearing with no changes.

## What the CPU is allowed instead

`schemas/cpu_decision_reason.schema.json` requires every decision to cite observable event sequence
numbers, state a belief phrased from observable evidence, carry a confidence between 0 and 1, and
assert `no_official_score_no_opponent_input_no_privileged_state`. Rule 3's "imperfect estimates with
explicit confidence and uncertainty" becomes a data requirement rather than a coding habit.

## Run it

```
python3 -m tools.uppercut_validate.cli isolation
python3 -m pytest tests/test_score_isolation.py
```

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ] -->
