<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:34 UTC | START ] -->
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 04:05 UTC | START edit ] -->

# Cross-platform notes procedure

Agents leave the **same status story** on every channel that can hold it.
Linear remains work truth; Slack remains humans; GitHub holds code; the repo
holds the durable packet. Never invent a parallel todo list in Slack or
`STATUS.md`.

## When to write a packet

At the end of a lasting slice (or when the Director asks for notes across
platforms), create:

`docs/implementation/cross_platform_status_YYYY-MM-DD.md`

(or append to today's packet if one already exists).

## Required sections

1. **Identity** — branch, PR URL, agent run URL, CI state, test count.
2. **What landed** — facts with paths / Decision ids.
3. **Measured** — numbers named as diagnostic vs calibration (Decision 0032 §3).
4. **Channel disposition** — table: posted / blocked / N/A, with reason.
5. **Paste blocks** — Slack `#uppercut-ops`, each Linear issue comment, optional
   GitHub issue text. Ready to send without rewriting.
6. **Related records** — links to evidence, decisions, prior checklists.

## Channel checklist (do in order)

| # | Channel | How |
|---|---|---|
| 1 | **Local** | Commit the packet + short `docs/development-log/` entry. Update `docs/implementation/agent_tooling.md` if tool reachability changed. |
| 2 | **GitHub** | Update PR body; post a top-level PR comment summarizing the packet. Prefer `ManagePullRequest`. If GitHub MCP is down, `gh` is read-only in cloud — still use ManagePullRequest for PR comments. |
| 3 | **Linear** | Comment on every touched issue (PRO-*). Create issues only for lasting work. MCP preferred; if unavailable, leave paste blocks in the packet and say so in the disposition table. |
| 4 | **Slack** | `#uppercut-ops` (`C0BP62MBFNK`) only. Humans: blockers, Bitdefender, Director asks. No sealed scorecards (Rule 3). Prefer draft send if the user has not reviewed the text; when the user **explicitly** asks to leave Slack notes, post or leave an exact paste block. |
| 5 | **Cursor** | Agent run URL is the durable pointer for cloud work. Do not treat chat as combat authority. |
| 6 | **Unreal MCP / Perseus / Snyk** | Windows host only. Record reachability in `agent_tooling.md`; do not fake posts from cloud. |

## Cloud-agent constraints (record honestly)

- Interactive MCP auth (`mcp_auth`) is **desktop-only**. If Slack/GitHub/Linear
  MCP show `error` / `needsAuth` in cloud, put paste blocks in the packet and
  ask the Director to authenticate in Cursor desktop — do not claim the note
  was posted.
- Linear may be absent from the cloud MCP catalog entirely; that is a host
  wiring gap, not "no Linear project".
- Never hand-edit `STATUS.md`; regenerate with `python -m tools.gen_status`
  after the suite count changes.

## Do not

- Dump a different story per channel.
- Close PRO-10 without Windows AV A/B/C evidence (packet now present under
  `evidence/2026-08-12-bitdefender-allowlist/` — board close is Director/Linear).
- Retune `pressure_threshold` in a status note (Decision 0035–0037).
- Treat Slack reactions as Linear state.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 04:05 UTC | END edit ] -->
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:34 UTC | END ] -->
