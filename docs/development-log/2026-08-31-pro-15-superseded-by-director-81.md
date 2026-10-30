<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:25 UTC | START ] -->

# PRO-15 — original runtime_active default superseded

Linear PRO-15 asked to set `runtime_active = true` by default. That was
implemented as Director draft PR #60 (proof-lane health boolean, legacy still
sole writer).

On 2026-08-31 the owner closed #60 without merging. Replacement authority is
director-orchestrator issue #81: LangGraph as the complete durable workflow
runtime, including top-level graph, Postgres checkpointer, writer leases, and
writer transfer. No evidence transfers.

This Uppercut slice only records that disposition. It does not refresh the
embedded snapshot and does not start #81 from this repo.

Packet: `docs/implementation/cross_platform_status_2026-08-31.md`.

<!-- [ Cursor Grok 4.6 | cursor-grok-4.6 | 2026-08-31 09:25 UTC | END ] -->
