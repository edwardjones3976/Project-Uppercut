<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-23 07:46 UTC | START ] -->
<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:25 UTC | START ] -->

**SUPERSEDED 2026-08-31.** Director PR #60 was closed without merge. Proof-lane
`runtime_active` without a complete top-level graph, Postgres durability, and
writer transfer is not the current activation model. Replacement:
[director-orchestrator#81](https://github.com/edwardjones3976/director-orchestrator/issues/81).
No evidence transfers. Current packet:
`docs/implementation/cross_platform_status_2026-08-31.md`.

<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:25 UTC | END ] -->

# Cross-platform status — PRO-15 runtime_active default (2026-08-23)

Canonical packet for **local / Slack / Linear / GitHub / Cursor**. One story,
many channels. Do not invent a second todo list in Slack or STATUS.md.

## Identity

| Field | Value |
|---|---|
| When | 2026-08-23 (UTC) |
| Linear | PRO-15 — Enable runtime_active by default |
| Assigned repo | `edwardjones3976/Project-Uppercut` |
| Canonical code | `edwardjones3976/director-orchestrator` (SOURCE_SNAPSHOT: orchestration changes originate upstream) |
| Upstream branch | `cursor/runtime-active-default-d5ae` |
| Upstream PR | https://github.com/edwardjones3976/director-orchestrator/pull/60 |
| Uppercut branch | `cursor/runtime-active-default-d5ae` |
| Agent run | https://cursor.com/agents/bc-749e77a2-3996-4754-b44c-904a21aad5ae |
| Embedded snapshot | unchanged at `3454e4369857cf9030cbb366d09f7c1b83959871` |

## What landed

`runtime_active` did not exist in the pinned Uppercut Director snapshot. After
Director PR #59, upstream health hard-coded `runtime_active=false` even though
the isolated proof lanes default on.

PRO-15 is implemented **upstream**, not as an Uppercut fork:

- `LANGGRAPH_RUNTIME_ACTIVE` defaults to `true`
- `/health` `langgraph.runtime_active` is true only when the setting is on, a
  proof lane is enabled, and checkpoint isolation is valid
- `legacy_sole_writer` stays `true` — this is not a writer cutover
- requested runtime + invalid isolation fails closed
- example profiles and `docs/langgraph-shadow-operations.md` updated
- tests cover default-on, explicit off, disabled lanes, and fail-closed isolation

No combat canon, C++ authority, Decision 0040, Issue 12 ordering, frozen
values, or evidence pins changed.

## Measured

This is control-plane work, not combat calibration.

```
PYTHONPATH=src python3 -m unittest tests.test_runtime_active_local -v
Ran 4 tests in 0.001s
OK
```

Artifact: `evidence/2026-08-23-pro-15-runtime-active/runtime_active_tests.txt`

## Channel disposition

| Channel | Status | Evidence |
|---|---|---|
| Local repo | Done | This packet + development log + evidence |
| GitHub (Director) | Posted | Draft PR #60 |
| GitHub (Uppercut) | This tracking PR | Embedded snapshot not refreshed |
| Linear PRO-15 | Paste block only | Linear MCP absent in this cloud run |
| Slack `#uppercut-ops` | Paste block only | Slack MCP `needsAuth` |
| Unreal / Snyk / Perseus | N/A | No engine or vuln work |

## Paste blocks

### Linear PRO-15

PRO-15 implemented upstream, not by forking the pinned Uppercut snapshot.

Director draft PR: https://github.com/edwardjones3976/director-orchestrator/pull/60

`LANGGRAPH_RUNTIME_ACTIVE` now defaults true. Health `runtime_active` is true
only when a proof lane is enabled and isolated. `legacy_sole_writer` remains
true. No writer cutover, no LangGraph import from `main.py`, no combat change.

Embedded snapshot stays at `3454e436` until #60 lands and a later snapshot
refresh is accepted.

### Slack `#uppercut-ops`

PRO-15: `runtime_active` now defaults on in Director (draft PR #60). Isolated
proof-lane config only — legacy engine remains the sole writer. No combat
change. Uppercut snapshot refresh waits for that PR to land.

## Related records

- `director-orchestrator/SOURCE_SNAPSHOT.md`
- `docs/implementation/orchestrator-transition-bridge.md`
- Director PR #59 (proof lanes default-on)
- Director PR #60 (this slice)
- Project-Uppercut issue #48 (transition tracker; no Gate 0 status change)

<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-23 07:46 UTC | END ] -->
