<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ] -->

# 2026-08-12 Bitdefender allowlist verification

## Context

PRO-10: Bitdefender had been deleting `tools/engine/build_uppercut_core.ps1`
and blocking `git restore` (2026-08-06). The Director reported the project was
added to the allowlist last week. This packet records what can be proven from
this environment.

## Environment

- Host for this agent run: **Linux cloud** (`uname` Linux x86_64), not the
  Windows Director machine where Bitdefender and UE 5.8 live.
- Repo: `/workspace` at branch `cursor/unreal-1-round-match-1ce3`.

## Results

| Check | Result | Notes |
|---|---|---|
| A. `git restore -- tools/engine/build_uppercut_core.ps1` | **PASS** | exit 0; file present |
| B. `.\tools\engine\build_uppercut_core.ps1` | **NOT RUN** | Requires Windows + UE 5.8 + PowerShell |
| C. Throwaway `tools/engine/_av_probe.cmd` | **NOT RUN** | Windows `.cmd` launch / quarantine signature |
| D. `python -m tools.engine.nightly_verify --no-engine` | deferred | Run on Windows after B/C |

Script inventory at verify time: **13** `.ps1` files under `tools/engine/`,
including `build_uppercut_core.ps1`.

## PRO-10 status

**Do not close PRO-10 from this packet alone.** A passed; B and C remain
Director actions on the Windows box. Close Linear PRO-10 only after B and C
pass there and this README is updated with those command outputs.

### Windows retest (copy/paste)

```powershell
cd C:\Users\edwar\project-uppercut
git restore -- tools/engine/build_uppercut_core.ps1
# Close UnrealEditor first:
.\tools\engine\build_uppercut_core.ps1
Set-Content -Path .\tools\engine\_av_probe.cmd -Value '@echo off & echo AV_PROBE_OK'
.\tools\engine\_av_probe.cmd
Remove-Item .\tools\engine\_av_probe.cmd
python -m tools.engine.nightly_verify --no-engine
```

Allowlist must cover: this clone, `tools\engine\`, `sandbox\`, `UE_5.8`,
host Python, git, `powershell.exe`, `UnrealEditor(-Cmd).exe`, bundled
`dotnet` / UBT.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ] -->
