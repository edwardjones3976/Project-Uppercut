# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | START ]
# Run import_fab_meshes.py inside the editor. A .ps1 rather than a nested
# -Command string: escaping a path with spaces through two layers of PowerShell
# quoting failed silently and produced no log at all, which is the worst kind of
# failure to debug.
param(
    [string]$Repo = "C:\Users\edwar\project-uppercut",
    [string]$Engine = "C:\Program Files\Epic Games\UE_5.8",
    [string]$Pass = "meshes"        # meshes | materials
)
$cmd = Join-Path $Engine "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$proj = Join-Path $Repo "sandbox\UppercutSandbox.uproject"
$script = (Join-Path $Repo "tools\engine\import_fab_$Pass.py").Replace("\", "/")
$log = Join-Path $Repo "sandbox\Saved\import_fab_$Pass.log"
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null

$dog = Start-Process powershell -PassThru -WindowStyle Hidden -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $Repo "tools\engine\wedge_watchdog.ps1"))

& $cmd $proj "-run=pythonscript" "-script=$script" -unattended -nopause -nosplash *>&1 |
    Out-File $log
Stop-Process -Id $dog.Id -Force -ErrorAction SilentlyContinue
Write-Host "IMPORT EXIT: $LASTEXITCODE"
Select-String -Path $log -Pattern "(IMPORT|MAT):" |
    Select-Object -ExpandProperty Line | Select-Object -Last 25
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 19:30 UTC | END ]
