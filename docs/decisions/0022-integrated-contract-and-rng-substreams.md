# Decision 0022 — The integrated bout gets a new contract and partitioned RNG

**Status:** accepted  
**Date:** 2026-08-06  
**Authority:** Director  
**Resolves:** how N, Q, R, S, and O become one live simulation without invalidating their historical proof

## Ruling

Integration creates a new, versioned authoritative contract. It does not re-bless the existing phase streams into pretending they were always one fight.

The existing N, Q, R, S, and O pins remain immutable unit-contract evidence for the claims they originally proved. Their hashes may change only when the canon or implementation inside that exact declared scope changes through a numbered Decision.

The live bout receives:

- its own contract identifier and schema version;
- its own marker stream and golden evidence;
- its own initial-state definition;
- its own ruleset and data hashes;
- its own integrated acceptance criteria.

## RNG partitioning

The integrated simulation uses deterministic, named random substreams derived from the bout seed and stable subsystem identifiers.

Initial substreams:

- policy and intent;
- movement and range;
- evasion and defense;
- contact and condition;
- knockdown and recovery;
- judging and officiating;
- presentation-only randomness, isolated from authority.

A subsystem may consume only its own authoritative stream. Adding a cosmetic draw or changing policy cadence may not silently move knockdown, judging, or contact outcomes.

Substream derivation must be stable, versioned, and recorded in replay metadata. Iteration order over maps, actors, or containers may not determine random ownership.

## Integration rule

> No phase after Q is strategically successful unless its implementation is reusable by the shared live simulation without copying its rules.

Commandlets remain evidence clients. Play-in-Editor, standalone builds, replay, batch simulation, and later networking must call the same authoritative runtime.

A phase-specific null harness may remain intentionally separate for stress testing, but it may not be described as integrated product behavior.

## Re-blessing policy

- Unit pins are not re-blessed merely because integration changes global draw order.
- Integrated pins are created as new evidence.
- A changed integrated pin requires either a numbered canon Decision or a documented implementation correction.
- The change record must identify the first divergent authoritative event, not only the final hash.
- Presentation changes may not move authoritative pins.

## Required integrated contract assertions

The first integrated contract must prove at minimum:

1. same seed and initial state reproduce byte-identically;
2. different seeds create non-vacuous variation;
3. range, evasion, policy, stamina, condition, knockdown, count, scoring, and ruleset events coexist in one stream;
4. no CPU or presentation system reads sealed scores, future actions, or another subsystem's private random draw;
5. pause, speed, rendering, and camera changes do not alter authority;
6. the same runtime drives commandlet evidence and the live Unreal arena;
7. a bout can validly end by stoppage or decision.

## What this avoids

This decision avoids two equally bad outcomes:

- destroying historical evidence by reinterpreting old pins as an integrated fight;
- preserving old pins by copying each phase's rules into a separate live implementation.

The project keeps both scientific continuity and one production runtime.
