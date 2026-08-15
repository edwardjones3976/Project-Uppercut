<!-- [ Codex | GPT-5 | 2026-08-15 21:00 UTC | START: Project Uppercut Director framework transition plan ] -->

# Project Uppercut Director framework transition

## Decision

Use a hybrid architecture with **LangGraph as the future orchestration kernel** while retaining the existing FastAPI/Slack boundary, Pydantic contracts, deterministic policy checks, persistent evidence, and provider adapters.

LangGraph is the best fit for Project Uppercut because the project needs cyclic implementation-review-repair loops, durable checkpoints, explicit human gates, replayable state transitions, and a clean separation between Python reference evidence and authoritative Windows/Unreal evidence. This is not approval for a wholesale rewrite.

PydanticAI may be used inside graph nodes for typed model calls. Provider SDKs remain adapters. CrewAI and AutoGen may be evaluated in isolated experiments, but neither becomes the execution authority: CrewAI hides too much routing behavior for this audit-sensitive workflow, and AutoGen's chat-first topology adds token use without improving deterministic project state.

## Canonical source

- Director source: [edwardjones3976/director-orchestrator](https://github.com/edwardjones3976/director-orchestrator)
- Isolation and transition change: [director-orchestrator PR #20](https://github.com/edwardjones3976/director-orchestrator/pull/20)
- Embedded Project Uppercut snapshot: [Project-Uppercut PR #45](https://github.com/edwardjones3976/Project-Uppercut/pull/45)
- Snapshot source commit: `eaaa1a90dad684c9810ce8e83287f348d3bd02ce`

The standalone Director repository is canonical. The embedded copy is a reviewed transitional deployment artifact, not a second development line. Changes originate in the source repository, pass its CI, and are then refreshed here with provenance.

## Gate 0 — complete the original task first

No framework transition starts until all items are evidenced:

- [ ] A fresh bounded availability check reports OpenAI, Claude, and Cursor ready.
- [ ] One owner-authored Slack analysis task completes OpenAI plan → Claude evidence → Cursor independent review → OpenAI acceptance.
- [ ] One isolated coding smoke test creates only a feature branch and draft pull request.
- [ ] Claude callback authentication proves exact-run matching, replay idempotency, and conflict rejection.
- [ ] Each gated assignment requires its own owner approval; approval does not leak to later assignments.
- [ ] A restart during an in-flight task resumes from persisted state without duplicate provider dispatch.
- [ ] At least four scheduled recovery probes across one workday complete, including one restart-recovery probe.
- [ ] SQLite and n8n backup/restore procedures are proved against disposable copies.
- [ ] The evidence bundle records provider run IDs, state transitions, approvals, terminal acceptance, and token/cost data where providers expose it.
- [ ] Project and repository allowlists remain fail-closed for every new and resumed run.

Pause/cancel/resume UX, generalized parallel fan-out, provider-specific rate-limit backoff, hard daily/monthly budget enforcement, richer metrics, and cloud hosting are production-hardening work. They do not excuse or replace Gate 0.

## Stable three-model roles

| Role | Primary model | Required output |
|---|---|---|
| Director | OpenAI | Bounded plan, assignment contracts, routing decisions, acceptance or explicit owner decision |
| Workhorse | Claude | Primary implementation/repository reasoning with tests and structured evidence |
| Independent review | Cursor | Adversarial review or independent implementation on an isolated branch, with evidence |

A model may cover another role only through an explicit assignment. No model self-approves, merges, deploys, releases, expands allowlists, or edits protected branches.

## Transition phases

### Phase 1 — freeze contracts

Version the task, assignment, callback, approval, evidence, and terminal-result schemas. Add captured, redacted traces for the successful Gate 0 analysis and coding runs. Treat deterministic policy decisions as externally observable contracts.

### Phase 2 — introduce a shadow graph

Implement LangGraph behind an `ORCHESTRATION_ENGINE=legacy|shadow|langgraph` switch. In `shadow`, replay captured events without provider, Slack, GitHub, filesystem, or deployment writes. Compare node order, policy decisions, budgets, approvals, evidence, and terminal state to the legacy engine.

### Phase 3 — bounded canary

Enable LangGraph only for one allowlisted analysis-only workflow. Keep the legacy engine as an immediate rollback. Require exact callback correlation, restart recovery, no duplicate dispatch, and equivalent or lower token/cost use.

### Phase 4 — Uppercut coding pilot

Run one feature-branch/draft-PR workflow. Claude performs the primary coding work, Cursor independently reviews, and OpenAI accepts against explicit checks. Windows/Unreal steps pause for the designated runner and cannot be inferred from Linux evidence.

### Phase 5 — cutover and retirement

Make LangGraph the default only after parity and recovery criteria pass. Keep legacy rollback for at least two stable release cycles. Remove legacy code only through a separate reviewed decision.

## CI and coordination contract

Both repositories must validate Python 3.12, dependency health, all Director unit tests, n8n workflow JSON, generic Compose configuration, the isolated `.env.uppercut.example` configuration, and PowerShell syntax for the Windows live-validation script. A populated `.env` or `.env.uppercut` must never enter Git history.

Every model must leave a bounded handoff containing: task/run ID, repository and starting ref, role, inputs used, files changed, checks executed, exact result, remaining risks, and next owner/model. Free-form chat is supporting context, not the source of truth.

## Completion criteria

The transition is complete when the LangGraph path passes captured-trace parity, restart/replay and duplicate-dispatch tests, one analysis canary, one isolated coding pilot, Windows/Unreal authority gates where relevant, a rollback drill, and owner acceptance. “Agents talked to each other” is not completion; durable, reviewable evidence is.

<!-- [ Codex | GPT-5 | 2026-08-15 21:00 UTC | END: Project Uppercut Director framework transition plan ] -->
