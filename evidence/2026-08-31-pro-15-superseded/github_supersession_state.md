<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:30 UTC | START ] -->

# GitHub supersession state (authenticated GitHub MCP)

Recorded 2026-08-31 09:30 UTC. The cloud `gh` token cannot read private
`director-orchestrator`; GitHub MCP can.

## director-orchestrator pull/60

- title: Enable runtime_active by default
- state: closed
- merged: false
- closed_at: 2026-08-31T09:21:44Z
- url: https://github.com/edwardjones3976/director-orchestrator/pull/60
- owner comment 5476338824: Closed as superseded. Proof-lane runtime_active
  without a complete top-level graph, Postgres durability, and writer transfer
  is not the current activation model. The replacement is #81; no evidence
  transfers.

## director-orchestrator issues/81

- title: LangGraph primary runtime, Native Long Table canary, and legacy retirement
- state: open
- created_at: 2026-08-31T09:20:25Z
- url: https://github.com/edwardjones3976/director-orchestrator/issues/81

## Project-Uppercut pull/59

- title: docs: PRO-15 superseded by Director issue 81
- state: OPEN
- isDraft: true
- url: https://github.com/edwardjones3976/Project-Uppercut/pull/59

## Local gates (this tracking slice)

- `python3 -m pytest -q` → 1479 passed in 89.36s
- `python3 -m tools.uppercut_validate.cli all` → RESULT: OK
- `python3 -m tools.gen_status --check` → STATUS.md is current: 1479 tests

<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:30 UTC | END ] -->
