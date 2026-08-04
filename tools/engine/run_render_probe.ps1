# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | START ]
# Run the rendered slice (UppercutRenderGameMode + AUppercutBoutDirector) and drop
# its marker stream where analyze_render_probe.py can judge it.
#
# Phase K ran this by hand; it is a script now because the mannequin visual pass
# needs the SAME run repeated and byte-compared, and a run you cannot repeat
# exactly is not evidence.
#
# Two countermeasures are baked in, both learned the hard way (see
# docs/phase1a/engine_setup_runbook.md):
#   - TargetInfo.json is pre-generated, because the editor's TurnkeySupport
#     otherwise spawns Build.bat -Mode=QueryTargets, which wedges in Build.bat's
#     own lock-file wait loop in this spawn context.
#   - The widened wedge watchdog runs alongside, killing any Build.bat cmd and its
#     PING sleeper if one appears anyway.
param(
    [int]$Seed = 4242,
    [int]$Ticks = 5400,
    [string]$Tag = "R1",
    [switch]$Markers,
    [switch]$Arena,
    [string]$Repo = "C:\Users\edwar\project-uppercut",
    [string]$Engine = "C:\Program Files\Epic Games\UE_5.8"
)

$proj = Join-Path $Repo "sandbox\UppercutSandbox.uproject"
$outDir = Join-Path $Repo "sandbox\Saved\phaseM"
$out = Join-Path $outDir "$Tag.txt"
$shots = Join-Path $outDir "shots_$Tag"
$log = Join-Path $outDir "run_$Tag.log"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

# 1. pre-generate TargetInfo.json (kills the QueryTargets wedge before it starts)
$dotnet = Join-Path $Engine "Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe"
$ubt = Join-Path $Engine "Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll"
$targetInfo = Join-Path $Repo "sandbox\Intermediate\TargetInfo.json"
Push-Location (Join-Path $Engine "Engine\Source")
& $dotnet $ubt -Mode=QueryTargets "-Project=$proj" "-Output=$targetInfo" | Out-Null
Pop-Location

# 2. watchdog alongside
$dog = Start-Process powershell -PassThru -WindowStyle Hidden -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $Repo "tools\engine\wedge_watchdog.ps1"))

# 3. the run itself
$editor = Join-Path $Engine "Engine\Binaries\Win64\UnrealEditor.exe"
$args = @(
    $proj,
    "/Engine/Maps/Entry?game=/Script/UppercutCore.UppercutRenderGameMode",
    "-game", "-windowed", "-ResX=1280", "-ResY=720", "-benchmark", "-fps=60",
    "-NoLoadingScreen", "-unattended", "-nosplash",
    "-seed=$Seed", "-ticks=$Ticks", "-repo=$Repo", "-out=$out", "-shots=$shots")
if ($Markers) { $args += "-markers" }
if ($Arena) { $args += "-arena" }

$sw = [System.Diagnostics.Stopwatch]::StartNew()
& $editor $args *>&1 | Tee-Object -FilePath $log | Out-Null
$sw.Stop()

Stop-Process -Id $dog.Id -Force -ErrorAction SilentlyContinue
if (Test-Path $out) {
    $h = (Get-FileHash $out -Algorithm SHA256).Hash.ToLower()
    $n = (Get-Content $out).Count
    Write-Host "RUN $Tag OK  lines=$n  sha256=$h  wall=$([int]$sw.Elapsed.TotalSeconds)s"
} else {
    Write-Host "RUN $Tag FAILED - no stream at $out (see $log)"
    exit 1
}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | END ]
