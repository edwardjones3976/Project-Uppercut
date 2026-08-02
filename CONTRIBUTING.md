<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ] -->

# Contributing to Project Uppercut

## Read first, in this order

1. `PROJECT_RULES.md` — binding constraints and non-negotiable laws
2. `PROJECT_NOTES.md` — current product identity and operating brief
3. `docs/decisions/` — accepted decisions
4. `ROADMAP.md` — fixed development order, deliverables, quality gates
5. `PROJECT_PLAN.md` — the current execution schedule

When documents conflict, the latest explicit Director correction controls, and the canonical files are
synchronized promptly.

## The rule that governs every claim

Rule 18: design documentation is not implementation evidence. Do not claim a feature, test, asset,
system or playable build exists unless the repository contains verifiable evidence. Prototype numbers
are tuning hypotheses until a validated specification or test promotes them. Status reports cite
commits and artifacts, or say "not started".

## Branches and commits

- `main` is the canonical branch.
- Work branches: `ws<N>/<short-topic>` matching the execution plan's workstreams (`ws1/attribute-schemas`).
- Commit subjects: `<area>: <imperative summary>` — `schemas: add fight event visibility field`.
- A commit that introduces an asset cites its completed compatibility audit.
- A commit that changes a tuning number states whether the number is still a hypothesis.

## Contribution tagging

Required. See `CONTRIBUTION_TAGGING.md`.

## Before you push

```
python3 -m pytest -q
python3 -m tools.uppercut_validate.cli all
```

Both must be clean. CI runs the same two commands.

## Issue labels

One per workstream — `ws0-repo`, `ws1-schemas`, `ws2-validators`, `ws3-acceptance`, `ws4-combat`,
`ws5-evidence`, `ws6-watchability` — plus `gate-phase0`, `gate-phase1a`, `director-decision`.

## Evidence artifacts

Simulation reports, matchup matrices, replay logs and balance evidence are committed under
`evidence/<run-id>/` so a gate review cites a commit rather than a recollection. Never hand-edit a
generated artifact; regenerate it.

## Things that will get a change rejected

- Any forbidden consumer reading official scores (Rule 3)
- A separate combat engine, ruleset or physics for any player tier or mode (Rule 5)
- A single generic health bar replacing per-region condition (Rule 14)
- An Ultimate that ends a match automatically or an ability without counterplay (Rule 11)
- One completed Crowd Bar activating both Ultimate and Full-Crowd Trait (Rule 12)
- A visible miss classified as a clean hit (Rule 13)
- Borrowed names, likenesses, animations, announcer lines, UI motifs or terminology (Rule 1)
- A claim of working software without committed evidence (Rule 18)

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ] -->
