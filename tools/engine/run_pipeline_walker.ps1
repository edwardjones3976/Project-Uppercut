# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:20 UTC | START ]
# Generator + determinism-leg runner for BP_PipelineWalker. -Gen authors the asset,
# otherwise a leg is run and its C| markers hashed. Same Turnkey wedge discipline as
# every other engine runner in this folder (see engine_setup_runbook.md).
param(
    [switch]$Gen,
    [string]$Tag = 'A1',
    [int]$Seed = 56057345
)
$ErrorActionPreference = 'Continue'
$editor  = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$project = 'C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject'
$script  = 'C:\Users\edwar\project-uppercut\tools\engine\bp_generate_pipeline_walker.py'
$outDir  = 'C:\Users\edwar\project-uppercut\sandbox\Saved\PipeWalk'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

if ($Gen) {
    $genOut = Join-Path $outDir 'gen.json'
    if (Test-Path $genOut) { Remove-Item $genOut -Force }
    $env:UE_GEN_OUT = $genOut
    $env:UE_GEN_SEED = "$Seed"
    $args = @("`"$project`"", '-run=pythonscript', "-script=`"$script`"",
              '-unattended', '-nopause', '-nosplash', '-nullrhi', '-NoLogTimes')
} else {
    $args = @("`"$project`"", 'L_PipeWalk', '-game',
              '-UseFixedTimeStep', '-FPS=60', '-Deterministic',
              '-unattended', '-nopause', '-nosplash', '-nullrhi', '-log', '-NoLogTimes')
}

$p = Start-Process -FilePath $editor -PassThru -WindowStyle Hidden -ArgumentList $args
Write-Output "pid: $($p.Id) gen=$Gen tag=$Tag seed=$Seed"
$deadline = (Get-Date).AddMinutes(15)
while (-not $p.HasExited) {
    Start-Sleep -Seconds 3
    Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" |
        Where-Object { $_.CommandLine -match 'Build\.bat.+ValidatePlatforms' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    if ((Get-Date) -gt $deadline) {
        Write-Output 'TIMEOUT'; Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; break
    }
}
Write-Output "exit code: $($p.ExitCode)"

if ($Gen) {
    if (Test-Path $genOut) { Get-Content $genOut -Raw } else { Write-Output 'NO REPORT'; exit 3 }
    exit 0
}

$src = 'C:\Users\edwar\project-uppercut\sandbox\Saved\Logs\UppercutSandbox.log'
if (-not (Test-Path $src)) { Write-Output 'NO LOG'; exit 3 }
$runLog = Join-Path $outDir "$Tag.runlog"
$outFile = Join-Path $outDir "$Tag.txt"
Copy-Item $src $runLog -Force
# PrintString prefixes the emitting actor, so the marker is anchored at end-of-line.
$markers = Select-String -Path $runLog -Pattern '(C\|[0-9|\-]+)\s*$' -AllMatches |
    ForEach-Object { $_.Matches[0].Groups[1].Value }
if (-not $markers -or $markers.Count -eq 0) { Write-Output 'NO MARKERS'; exit 4 }
[IO.File]::WriteAllText($outFile, (($markers -join "`n") + "`n"), [Text.UTF8Encoding]::new($false))
Write-Output "OUT: $outFile"
Write-Output "MARKERS: $($markers.Count)"
Write-Output "SHA256: $((Get-FileHash $outFile -Algorithm SHA256).Hash)"
exit 0
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:20 UTC | END ]
