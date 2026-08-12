<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:34 UTC | START ] -->
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 04:05 UTC | START edit ] -->

# Cross-platform status — Unreal 1-round + Decision 0037 (2026-08-12)

Canonical packet for **local / Slack / Linear / GitHub / Cursor**. One story,
many channels. Do not invent a second todo list in Slack or STATUS.md.

| Field | Value |
|---|---|
| When | 2026-08-12 (UTC) |
| Branch | `cursor/unreal-1-round-match-1ce3` |
| PR | https://github.com/edwardjones3976/Project-Uppercut/pull/31 |
| Agent run | https://cursor.com/agents/bc-3cb0e490-0afd-44e5-b56d-c08885cd1ce3 |
| CI | phase0-validation + windows-authority **green** |
| Suite | **1425** tests (`STATUS.md` regenerated) |

## What landed

1. Integrated **1-round CPU vs CPU** Play path: `FUppercutFightSession`, thin
   policy (G2/G3), KD/count or sealed decision; Phase Q retained when
   `bIntegratedOneRound=false`.
2. Rule-10 cards `test_pressure_power` / `test_range_timing` + pair uniqueness.
3. Decision **0037**: `opponent_read` in the integrated bout (defender `reads` →
   readiness on evade window + guard extents). **`pressure_threshold` untouched.**
4. CI hardening: LCG copy-count restored to **8** (`UppercutLcgNext` /
   `UppercutMixSeed`); Windows `canon_hash_roles_raw` CRLF fixed
   (`.gitattributes` + Manifest LF normalize).

## Measured (diagnostic, not calibration — Decision 0032 §3)

Seeds **4242–4251**, one-round integrated bout: avg connect **~43.5%**
(was ~55%). Pro band ~30–35%. Next levers: `counter_window_growth`, guard
erosion — not threshold retune.

## Channel disposition (this cloud run)

| Channel | Posted? | Where / why not |
|---|---|---|
| **Local repo** | Yes | This file + procedure + agent routing docs |
| **GitHub PR #31** | Yes | Top-level PR comment + PR body |
| **Cursor agent run** | Yes | Dashboard events (PR created); run URL above |
| **Slack `#uppercut-ops`** | **No — blocked** | Slack MCP discovery/auth fails in cloud; interactive `mcp_auth` is desktop-only. Paste block below. |
| **Linear PRO-6/7/9/10** | **No — blocked** | No Linear MCP server in this environment. Paste blocks below. Host: https://linear.app/project-uppercut/document/agent-tool-routing-beb58abfab20 |
| **Unreal MCP / Perseus** | N/A | Windows host only |

---

## Paste — Slack `#uppercut-ops` (`C0BP62MBFNK`)

```
Uppercut status 2026-08-12 — 1-round path + opponent_read

PR #31 (cursor/unreal-1-round-match-1ce3) CI green (phase0 + windows-authority).
Play: integrated 1-round CPU vs CPU (FUppercutFightSession). Decision 0037:
opponent_read wired in the integrated bout; pressure_threshold untouched.
Connect ~43.5% avg on seeds 4242–4251 (was ~55%).

Needs Ed:
• Linear: mark PRO-10 Done (Windows A/B/C packet in repo); comments on PRO-6/7/9
• Merge PR #31, then land port PR (canon pair + AV evidence + adversarial tests)

Agent: https://cursor.com/agents/bc-3cb0e490-0afd-44e5-b56d-c08885cd1ce3
Packet: docs/implementation/cross_platform_status_2026-08-12.md
```

---

## Paste — Linear comments

### PRO-6 (M2 runtime subsystem)

```
2026-08-12 — progress on cursor/unreal-1-round-match-1ce3 (PR #31, CI green).

FUppercutFightSession + UUppercutFightSubsystem integrated mode (default on).
Thin policy G2/G3. Decision 0037 opponent_read now in the Python integrated bout
(defender reads → readiness on evade + guard). pressure_threshold untouched.
Connect diagnostic ~43.5% avg seeds 4242–4251.

Packet: docs/implementation/cross_platform_status_2026-08-12.md
Agent: https://cursor.com/agents/bc-3cb0e490-0afd-44e5-b56d-c08885cd1ce3
```

### PRO-7 (M3 port R and S)

```
2026-08-12 — Phase R C++ remains PASS. Thin observable policy is in the
integrated session; full Phase S in-session still open. Not claiming S done.
PR #31.
```

### PRO-9 (M5 round flow / soul)

```
2026-08-12 — 1-round ending path started (knockdown/count or sealed decision)
on FUppercutFightSession / prove_one_round. Soul proof still deferred.
PR #31 · docs/implementation/cross_platform_status_2026-08-12.md
```

### PRO-10 (Bitdefender)

```
2026-08-12 — MARK DONE.

Windows blackbox probes A/B/C PASS + nightly_verify --no-engine RC=0.
Evidence: evidence/2026-08-12-bitdefender-allowlist/ (incl. nightly_verify-no-engine.log).
Residual: packet does not claim commandlet/PIE; editor binary path still rests
on the first clean prove_core_range.
```

---

## Related local records

- Procedure: `docs/implementation/cross_platform_notes_procedure.md`
- Prior Linear checklist: `docs/implementation/linear_update_2026-08-12_one_round.md`
- Tooling map: `docs/implementation/agent_tooling.md`, `AGENTS.md`
- Dev log: `docs/development-log/2026-08-12-one-round-and-opponent-read.md`
- Dev log (pose studio): `docs/development-log/2026-08-12-pose-studio-lit-capture.md`

---

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 23:05 UTC | START append: pose-studio slice ] -->

## Append — lit pose studio (PR #42) + gate fix-forward

| Field | Value |
|---|---|
| When | 2026-08-12 (UTC) |
| Substance PR | https://github.com/edwardjones3976/Project-Uppercut/pull/42 (`45762f8`) |
| Director disposition | https://github.com/edwardjones3976/Project-Uppercut/pull/42#issuecomment-5273783768 |
| Failed merge-head | https://github.com/edwardjones3976/Project-Uppercut/actions/runs/31648976805 (`windows-authority` / `check_core_compiles`) |
| Fix-forward | branch `fix/pose-studio-gate-green` (this append) |

### What landed (substance)

Presentation-only `-UppercutPoseStudio`: isolate one fighter, loop authored
overhand-right (or explicit rear hook), spawn key/fill lights + floor, lock
camera, capture via `FScreenshotRequest`. `InferRepoDir` supports clean-home and
sandbox layouts. Combat authority untouched.

### Why `main` was red

`check_core_compiles` rejected bare `#include "EngineUtils.h"` and
`#include "TimerManager.h"` in `UppercutMatchDirector.cpp`. Local UBT compile
had succeeded; the repository gate had not.

### Fix-forward (binding)

1. Replace those includes with whitelist-safe APIs: `GetAllActorsOfClass` +
   Tick-armed capture delay (no whitelist stretch).
2. `tools/engine/pose_fighter0_overhand.ps1` defaults `$Repo` from
   `$PSScriptRoot\..\..`; `-Repo` remains an override; contribution tags added.
3. Capture filenames `fighter{N}_{clipSlug}_orthodox.png`, or refuse unsupported
   `-UppercutPoseClip=` values (fighter + director agree).
4. Dev log: `docs/development-log/2026-08-12-pose-studio-lit-capture.md`.

### Channel disposition (this append)

| Channel | Posted? | Where / why not |
|---|---|---|
| **Local repo** | Yes | This append + development-log entry |
| **GitHub** | Pending | Fix-forward PR comment on merge |
| **Slack / Linear** | No — not required for this gate repair | Paste unused |

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 23:05 UTC | END append ] -->
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 04:05 UTC | END edit ] -->
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 03:34 UTC | END ] -->
