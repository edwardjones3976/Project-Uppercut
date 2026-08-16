<!-- [ Codex | GPT-5 | 2026-08-16 03:50 UTC | START ] -->

# Director Orchestrator to LangGraph transition bridge

**Status:** Proposed operational bridge; no combat or product authority
**Project baseline:** `main@322930c4e17ac1614499e135a5841ed4c5c6d448`
**Orchestrator baseline:** `director-orchestrator@b54efdb749bda656adf6a8135d828da3165d34f7`
**Binding combat disposition:** Decision 0040

## Purpose

Keep Project Uppercut productive and governable while the Director Orchestrator adopts a LangGraph state engine. This bridge tells every model what remains authoritative, how work is handed off, and what evidence is required during dual operation.

The transition changes orchestration mechanics only. It does not change the game, the development order, the C++ combat authority, the meaning of evidence, or any Director ruling.

## Pre-transition prerequisites

No LangGraph-controlled Uppercut work begins until both original deployment tasks are complete.

### 1. Isolate the Uppercut deployment

Director Orchestrator PR 20 merged the upstream isolation remediation. Acceptance still requires live Windows evidence that the deployment:

- use `.env.uppercut`, never rewrite the shared `.env`;
- run as Compose project `project-uppercut-director`;
- use independent task/n8n/PostgreSQL volumes, ports, secrets, Slack destination, budgets, and audit retention;
- keep paid execution closed until the isolated store is proven empty and healthy;
- add behavioral tests for profile preservation and paid-gate ordering;
- pass a dry-run before any provider check or project task.

### 2. Refresh draft PR 45

PR 45 now vendors merged source commit `b54efdb749bda656adf6a8135d828da3165d34f7`. Its refreshed snapshot, provenance, both repositories' validation, and live Windows deployment evidence must all be accepted on the exact PR head before transition work begins.

The embedded runtime is a pinned compatibility mirror. Development occurs upstream in `edwardjones3976/director-orchestrator`; Project Uppercut must not become a divergent orchestrator fork.

### 3. Close the pre-transition Director checkpoint

Before shadow operation begins, record:

- upstream repaired commit and refreshed PR 45 head;
- current open PRs/issues and their dispositions;
- exact CI and Windows/Unreal evidence status;
- provider readiness booleans;
- isolated volume/port/profile identifiers;
- dry-run outcome and rollback procedure;
- one reversible documentation-only live assignment.

## Project authority during transition

Read in this order:

1. Owner-authored request and explicit Director ruling
2. `PROJECT_RULES.md`
3. `PROJECT_NOTES.md`
4. Numbered decisions and `docs/decisions/OPEN_GATES.md`
5. `ROADMAP.md`
6. Active GitHub issue acceptance criteria
7. This bridge and the upstream transition plan
8. Development logs and model-produced proposals

This bridge is operational guidance. It cannot overrule game canon.

## Current state that every work packet must preserve

- The shared C++ `INTEGRATED_1R` session is combat authority.
- Python `IntegratedBout` is reference/tooling and must not silently become the fight.
- Neither current C++ nor Python outcome is accepted as authentic calibration.
- `pressure_threshold` remains frozen at 0.57.
- `feat/authenticity-program` remains on HOLD under Decision 0040.
- First Bell is not passed.
- Issue 12 remains the integration/convergence board.
- PR 46 supplies important coherence and divergence evidence but requires a Director disposition before overlapping evidence files are chosen or merged.
- PR 38 remains gated on an online self-hosted Windows/UE runner.
- Orchestration work may not tune combat values, move pins, waive authenticity failures, redefine evidence, or claim a product milestone.

## Required work packet

Every model assignment must use the upstream v1 work-packet contract and include:

- repository and starting commit/ref;
- the exact canonical files and SHAs relevant to the assignment;
- objective, non-goals, and prohibited actions;
- dependencies by assignment ID;
- allowed tools and external side effects;
- acceptance checks and required evidence;
- owner/Director approval requirements;
- budget, timeout, hop, and revision limits;
- task, assignment, idempotency, Slack, issue, and PR correlation identifiers.

A conversational summary is not a substitute for this packet.

## Required handoff behavior

- OpenAI, Claude, Cursor, Gemini, and Perplexity have roles, not authority.
- Agents work on isolated branches/worktrees.
- An agent reports unavailable tools or credentials instead of claiming an update.
- Accepted outputs are passed downstream as digested artifacts inside an untrusted-data envelope.
- Parallel work is allowed only for assignments with no dependency edge.
- One writer owns GitHub/Slack side effects for each task.
- The implementing model cannot approve its own work.
- Cross-model disagreement returns to evidence review or the Director.
- Every external write is remotely read back before completion is recorded.
- No provider receives secrets or unrelated personal/project data through a work packet.

## Dual-run policy

### Shadow phase

The LangGraph path may read the same intake and canon snapshot as the legacy engine. It may create comparison artifacts but cannot dispatch providers or write GitHub/Slack.

### Read-only dual run

Both paths may plan. Only the legacy writer may dispatch or write. Differences are classified; wording differences alone are not failures, while different gates, repositories, approvals, budgets, dependencies, or acceptance criteria are failures until resolved.

### Canary phase

LangGraph may schedule explicitly allowlisted, reversible, documentation-only tasks. The legacy writer remains the only external writer until a separate gate transfers that role.

### Single-writer canary

Before LangGraph writes, the matching legacy writer is disabled for the canary task. Owner approval, idempotency ledger, branch isolation, draft PR, exact-head tests, and remote readback are mandatory.

### Uppercut cutover

Cutover applies only to the isolated Uppercut deployment. The shared Director deployment remains unchanged. Legacy recovery stays available for an observation window, but never concurrently as a second writer.

## Evidence requirements

A transition result is valid only when it states:

- graph and legacy versions;
- task/canon snapshot;
- provider and run reference;
- state-transition trace;
- approvals requested and received;
- external effects and idempotency records;
- commands/checks and exact results;
- restart/recovery behavior;
- differences and their disposition;
- rollback readiness.

Model agreement is not evidence. Repository state, deterministic tests, provider receipts, and remote readback are evidence.

## Interaction with active game work

The orchestration transition must not become the new gameplay critical path. Issue 12 continues in its authorized order:

1. coherent integrated C++ evidence and Director disposition;
2. structural diagnosis of implausible fight behavior;
3. complete three-round decision and separate valid stoppage path;
4. refreshed status/evidence;
5. numeric calibration only after parity and structural completeness.

Operational migration work runs beside that sequence and cannot declare First Bell.

## Rollback

If the graph path loses state, widens authority, duplicates a dispatch/write, violates a budget, or disagrees about an approval gate:

1. close paid execution and new intake;
2. stop the graph writer;
3. export checkpoints and the side-effect ledger;
4. reconcile provider runs, branches, PRs, and Slack messages;
5. return the isolated Uppercut deployment to the last accepted legacy engine;
6. preserve all evidence;
7. resume only after owner review.

## Completion

The transition is complete only when the owner accepts:

- isolated Uppercut deployment;
- refreshed and traceable PR 45 snapshot;
- provider-neutral packet contract across configured providers;
- shadow and dual-run comparison evidence;
- restart, callback, approval, budget, and idempotency tests;
- one documentation canary and one reversible repository canary;
- successful rollback drill;
- observation window with no unresolved safety or correctness defect.

Until then, the migration remains reversible and explicitly in transition.

<!-- [ Codex | GPT-5 | 2026-08-16 03:50 UTC | END ] -->
