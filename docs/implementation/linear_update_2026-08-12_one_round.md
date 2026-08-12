<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ] -->

# Linear update note — Unreal 1-round match (2026-08-12)

**Superseded for paste text by**
`docs/implementation/cross_platform_status_2026-08-12.md`
(procedure: `docs/implementation/cross_platform_notes_procedure.md`).

Cloud agent runs still have **no Linear MCP**. Apply board updates from the
Director host (or paste from the status packet):

| Issue | Action |
|---|---|
| PRO-10 | **Done** — Windows A/B/C allowlist probes PASS; see `evidence/2026-08-12-bitdefender-allowlist/` |
| PRO-6 | **In Progress** — FightSubsystem integrated mode + `FUppercutFightSession` + cards/policy/ending on `cursor/unreal-1-round-match-1ce3` |
| PRO-7 | Comment: Phase R already C++ PASS; thin policy in session; full Phase S still open |
| PRO-9 | 1-round ending (count or sealed decision) path in C++; soul proof still deferred |

Follow-up (2026-08-12 03:13+ UTC):

| Issue | Action |
|---|---|
| PRO-6 / Decision 0037 | Comment: `opponent_read` wired; `pressure_threshold` untouched; connect ~43.5% avg seeds 4242–4251 |
| (CI) | LCG copy-count 8; Windows `roles_raw` CRLF fixed; CI green |

Do not invent a Slack todo list. Slack paste lives in the status packet for
`#uppercut-ops`.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ] -->
