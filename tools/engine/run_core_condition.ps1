# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | START ]
# Phase N evidence runs. Same countermeasures as run_render_probe.ps1: pre-generate
# TargetInfo.json so the editor never spawns Build.bat -Mode=QueryTargets, and keep
# the widened wedge watchdog alive alongside.
param(
    [string]$Repo = "C:\Users\edwar\project-uppercut",
    [string]$Engine = "C:\Program Files\Epic Games\UE_5.8",
    # ONE comma-separated string, not a string[]. With powershell -File, extra
    # array values bind positionally to the NEXT parameter instead - which
    # silently made $Repo "B1:4243:5400" and produced a wall of drive-not-found.
    [Parameter(Mandatory = $true)][string]$Runs     # "tag:seed:ticks,tag:seed:ticks"
)

$proj = Join-Path $Repo "sandbox\UppercutSandbox.uproject"
$outDir = Join-Path $Repo "sandbox\Saved\phaseN"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$dotnet = Join-Path $Engine "Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe"
$ubt = Join-Path $Engine "Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll"
Push-Location (Join-Path $Engine "Engine\Source")
& $dotnet $ubt -Mode=QueryTargets "-Project=$proj" `
    "-Output=$(Join-Path $Repo 'sandbox\Intermediate\TargetInfo.json')" | Out-Null
Pop-Location

$dog = Start-Process powershell -PassThru -WindowStyle Hidden -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $Repo "tools\engine\wedge_watchdog.ps1"))

$cmd = Join-Path $Engine "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
foreach ($r in $Runs.Split(",")) {
    $parts = $r.Split(":")
    $tag = $parts[0]; $seed = $parts[1]; $ticks = $parts[2]
    $out = Join-Path $outDir "$tag.txt"
    # Args are passed as single pre-quoted strings: an earlier harness bug split
    # "-seed=$($run[1])" into tokens, every run silently used seed 0, and the
    # streams matched for the wrong reason. Evidence that agrees by accident is
    # worse than evidence that disagrees.
    & $cmd $proj "-run=UppercutCoreCondition" "-seed=$seed" "-ticks=$ticks" `
        "-repo=$Repo" "-out=$out" -unattended -nopause -nosplash *>&1 |
        Out-File (Join-Path $outDir "run_$tag.log")
    if (Test-Path $out) {
        $h = (Get-FileHash $out -Algorithm SHA256).Hash.ToLower()
        Write-Host "$tag seed=$seed ticks=$ticks sha256=$h"
    } else {
        Write-Host "$tag FAILED - no stream"
    }
}
Stop-Process -Id $dog.Id -Force -ErrorAction SilentlyContinue
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 18:40 UTC | END ]
