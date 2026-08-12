<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | START ] -->

# 2026-08-12 Bitdefender allowlist verification

## Context

PRO-10: Bitdefender had been deleting `tools/engine/build_uppercut_core.ps1`
and blocking `git restore` (2026-08-06). The Director reported the project was
added to the allowlist last week. This packet records verification.

## Environment

- Host for the closing Windows retest: **Windows 10** (`win32`), UE 5.8 installed
  at `C:\Program Files\Epic Games\UE_5.8`, branch
  `cursor/unreal-1-round-match-1ce3`.
- Earlier cloud note (Linux-only A pass) is superseded by the Windows table
  below.

## Results (Windows Director host, 2026-08-11 evening local / 2026-08-12 UTC)

| Check | Result | Notes |
|---|---|---|
| A. `git restore -- tools/engine/build_uppercut_core.ps1` | **PASS** | exit 0; `Test-Path` true |
| B. `.\tools\engine\build_uppercut_core.ps1` | **PASS** | `BUILD EXIT: 0` after AttrCore UE 5.8 JSON-key fix; script still present; `UnrealEditor-UppercutCore.dll` linked |
| C. Throwaway `tools/engine/_av_probe.cmd` | **PASS** | wrote, ran (`AV_PROBE_OK`), still present after run; deleted deliberately; never committed |
| D. `python -X utf8 -m tools.engine.nightly_verify --no-engine` | **PASS** | see retest log below / CI green path |

Script inventory at verify time: **13** `.ps1` files under `tools/engine/`,
including `build_uppercut_core.ps1`.

## PRO-10 status

**Close PRO-10.** A–C passed on the Windows box where Bitdefender lives. Linear
issue marked Done with this packet cited. First `prove_live_arena` / PIE after
this remains the live-editor coverage check (not required to close the
quarantine signature that broke restore/build/`.cmd`).

### Retest commands

```powershell
cd C:\Users\edwar\project-uppercut
git restore -- tools/engine/build_uppercut_core.ps1
# Close UnrealEditor first:
.\tools\engine\build_uppercut_core.ps1
Set-Content -Path .\tools\engine\_av_probe.cmd -Value '@echo off & echo AV_PROBE_OK'
.\tools\engine\_av_probe.cmd
Remove-Item .\tools\engine\_av_probe.cmd
python -X utf8 -m tools.engine.nightly_verify --no-engine
```

Allowlist covers: this clone, `tools\engine\`, `sandbox\`, `UE_5.8`,
host Python, git, `powershell.exe`, `UnrealEditor(-Cmd).exe`, bundled
`dotnet` / UBT, and `.cmd` creation/execution inside the tree.

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 02:53 UTC | END ] -->

<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 04:20 UTC | START ] -->
Windows A/B/C closed on this branch after compiling `FUppercutFightSession`
into `UppercutSandboxEditor` (`BUILD EXIT: 0`). AttrCore required an explicit
`FString(Pair.Key)` for UE 5.8 shared JSON key storage — unrelated to AV.
<!-- [ Auto (Cursor Agent) | Auto (Cursor Agent) | 2026-08-12 04:20 UTC | END ] -->
