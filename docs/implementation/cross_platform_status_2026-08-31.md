<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:25 UTC | START ] -->

# Cross-platform status — PRO-15 superseded by Director issue #81 (2026-08-31)

Canonical packet for **local / Slack / Linear / GitHub / Cursor**. One story,
many channels. Do not invent a second todo list in Slack or STATUS.md.

## Identity

| Field | Value |
|---|---|
| When | 2026-08-31 09:25 UTC |
| Linear | PRO-15 — Enable runtime_active by default (original scope superseded) |
| Assigned repo | `edwardjones3976/Project-Uppercut` |
| Canonical code | `edwardjones3976/director-orchestrator` |
| Superseded upstream PR | https://github.com/edwardjones3976/director-orchestrator/pull/60 (closed, not merged) |
| Replacement authority | https://github.com/edwardjones3976/director-orchestrator/issues/81 |
| Uppercut branch | `cursor/runtime-active-default-d5ae` |
| Uppercut tracking PR | https://github.com/edwardjones3976/Project-Uppercut/pull/59 |
| Agent run | https://cursor.com/agents/bc-749e77a2-3996-4754-b44c-904a21aad5ae |
| Embedded snapshot | unchanged; not refreshed from #60 |

## What landed

Owner closed Director draft PR #60 as superseded. Quote (PR comment
5476338824):

> Proof-lane runtime_active without a complete top-level graph, Postgres
> durability, and writer transfer is not the current activation model. The
> replacement is #81; no evidence transfers.

This agent will **not**:

- revive `LANGGRAPH_RUNTIME_ACTIVE` default-on without the #81 graph
- treat 2026-08-23 Settings-contract tests as activation evidence
- fork Uppercut's pinned Director snapshot
- start #81 implementation from this Uppercut cloud run

Issue #81 is the sole live LangGraph-primary authority. It requires a typed
top-level graph, Postgres checkpointer, durable writer leases, and writer
transfer so LangGraph owns new Default Director tasks. First required landings
are Director PR #77 then #80; those are upstream, not this repo.

No combat canon, C++ authority, Decision 0040, Issue 12 ordering, frozen
values, or evidence pins changed.

## Measured

Control-plane disposition only. No new combat or Director runtime measurement.
2026-08-23 local Settings tests are historical and **do not transfer**.

Director issue #81 is open. Director PR #60 is `state=closed`, `merged=false`.

<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:28 UTC | START edit ] -->

## Channel disposition

| Channel | Status | Evidence |
|---|---|---|
| Local repo | Done | development log + superseded banners on 2026-08-23 files |
| GitHub (Director) | Posted | owner close on #60; tracking comment `5476388501` |
| GitHub (Uppercut) | Posted | PR #59 retitled; top-level comment on this packet |
| Linear PRO-15 | Posted | comment `6539540d-8da8-4622-8643-954dcb7f5682` |
| Slack `#uppercut-ops` | Draft | draft `Dr0BUN873JAC` in `C0BP62MBFNK` (not sent) |
| Unreal / Snyk / Perseus | N/A | No engine or vuln work |

<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:28 UTC | END edit ] -->

## Paste blocks

### Linear PRO-15

Director draft PR #60 was closed as superseded. Proof-lane `runtime_active`
without a complete top-level graph, Postgres durability, and writer transfer is
not the current activation model.

Replacement: https://github.com/edwardjones3976/director-orchestrator/issues/81

No evidence transfers from #60 or from Uppercut tracking PR
https://github.com/edwardjones3976/Project-Uppercut/pull/59

This cloud run recorded the supersession in Uppercut docs. It did not implement
#81 (wrong repo; #81 first requires landing Director PRs #77 and #80). PRO-15's
original "flip the health boolean" scope should be canceled or retargeted by
the Director; this agent is not closing the Linear issue.

### Slack `#uppercut-ops`

PRO-15 update: Director PR #60 (`runtime_active` default-on, legacy still sole
writer) was closed as superseded. Replacement is director-orchestrator issue
#81 (LangGraph primary runtime + Postgres durability + writer transfer). No
evidence transfers. Uppercut snapshot was not refreshed. No combat change.

## Related records

- `docs/implementation/cross_platform_status_2026-08-23.md` (historical, bannered)
- `docs/development-log/2026-08-31-pro-15-superseded-by-director-81.md`
- Director issue #81 comment preserving exact-SHA / reviewer / security rules
- Director PRs #77 and #80 (required landings before #81 implementation)
- `docs/implementation/orchestrator-transition-bridge.md`

<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:25 UTC | END ] -->
