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

- `main` is the canonical branch. **Never force-pushed, never rewritten.**
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:20 UTC | edit: document the convention actually in use ]
     This prescribed `ws<N>/<short-topic>` matching the execution plan's
     workstreams. Not one branch in the repository has ever used it - the real
     convention grew into four prefixes and an external audit flagged the gap
     between the rule and the practice. A convention nobody follows is not a
     convention; it is a second source of truth that always loses. Written down
     as it is actually practised. -->
- Work branches carry a prefix that says what kind of change they are:
  `feat/` (new runtime behaviour), `fix/` (a defect with a test that failed
  first), `docs/` (record and reference only), `director/` (a Director ruling
  being recorded), `review/` (a panel or audit record), `impl/` (implementing an
  already-accepted decision), and `wip/` (integration work not yet ready to
  propose). Then a short topic: `feat/phase-r-into-the-bout`.
- **Merge, do not rebase, once a branch has been pushed.** Provenance is
  evidence in this repository; rewriting it destroys the thing the evidence
  discipline exists to protect.
- Commit subjects: `<area>: <imperative summary>` — `schemas: add fight event visibility field`.
- A commit that introduces an asset cites its completed compatibility audit.
- A commit that changes a tuning number states whether the number is still a hypothesis.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 19:45 UTC | edit: measure the contract ] -->
## A harness may explore. Only the contract may conclude.

A finding about a phase must be measured on **that phase's contract** — the
analyzer that emits the marker stream a C++ port has to reproduce. Experiment
harnesses in `tools/engine/experiment_*.py` are for exploring cheaply; they are
simplifications, and a number taken from one describes the harness.

Recorded because it was broken expensively on 2026-08-05: a day of measurement
was taken on `experiment_per_hand_guard.run_with` and written up as though it
described the Phase O contract. The contract already had footwork, slips and
whiffs — 42.5% connect against the reference's 42.4% — and the harness had none
of them, so several headline conclusions were about an artifact nobody ships.
See `docs/development-log/2026-08-05-i-measured-the-wrong-artifact.md`.

Before quoting a number in a document or a commit, state which artifact produced
it. If it was a harness, say so in the same sentence.

## Contribution tagging

Required. See `CONTRIBUTION_TAGGING.md`.

## Before you push

```
python3 -m pytest -q
python3 -m tools.uppercut_validate.cli all
```

Both must be clean. CI runs the same two commands.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 14:10 UTC | edit: push directive ] -->
### Agents push. All of it.

**Director directive, 2026-08-05.** An agent working in a local clone pushes its
own work to `origin` — past, present and future. This replaces the earlier
standing instruction to hand back `git format-patch` output instead of pushing;
that instruction described a sandbox with no access to the remote and does not
apply to an agent working in the Director's own checkout.

What "everything necessary" means in practice, so it does not become an excuse to
push half a thought:

- Both commands above run clean FIRST. A push is not the moment to discover a
  failing validator. (Recorded because the 2026-08-05 push ran the test suite and
  not the validator; it passed on a later check, but the order was wrong.)
- Work is pushed at the point it is coherent — a phase, a finding, a correction —
  not at the end of a session. A local-only commit is a commit nobody else can
  read.
- Nothing is force-pushed and nothing already on `main` is rewritten. A published
  mistake is corrected by a commit that supersedes it, exactly as a superseded
  claim in a document is left in place with the correction beside it.

## Issue labels

One per workstream — `ws0-repo`, `ws1-schemas`, `ws2-validators`, `ws3-acceptance`, `ws4-combat`,
`ws5-evidence`, `ws6-watchability` — plus `gate-phase0`, `gate-phase1a`, `director-decision`.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:34 UTC | START ] -->
Linear is the work tracker (team **Project Uppercut**). Host-tool labels there:
`agent-ops`, `slack`, `github`, `snyk`. Do not invent a parallel todo list in Slack
or in `STATUS.md`. After a lasting slice, follow
`docs/implementation/cross_platform_notes_procedure.md`.
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:34 UTC | END ] -->

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
