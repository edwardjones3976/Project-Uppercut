# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:24 UTC | START ]
# Generator + determinism-leg runner for BP_BoutWalker (Phase F: the bout structure).
# -Gen authors the asset; otherwise a leg runs and its B|/S| markers are extracted and
# hashed. Same Turnkey wedge discipline as every other runner here (engine_setup_runbook.md).
#
# Refuses to start while an interactive UnrealEditor holds the sandbox. Two UE processes
# writing sandbox/Intermediate and sandbox/Saved at once can corrupt the project, and a
# headless generation can be clobbered by the editor's next save. Pass -Force only if
# you know the open editor is disposable.
# -Seed applies to -Gen ONLY. The base seed is compiled into the Blueprint as a literal
# on the BeginPlay chain, so a run leg cannot change it - passing -Seed to a run leg
# would silently do nothing and make a divergence leg look like a failure to diverge.
# Changing seeds means regenerating, which is the stronger evidence anyway: it proves
# the ASSET regenerates identically, not merely that a fixed asset replays.
param(
    [switch]$Gen,
    [switch]$Force,
    [string]$Tag = 'A1',
    [int]$Seed = 56057345
)
if (-not $Gen -and $PSBoundParameters.ContainsKey('Seed')) {
    Write-Output "NOTE: -Seed is ignored on a run leg; the seed is compiled in. Regenerate to change it."
}
$ErrorActionPreference = 'Continue'
$editor  = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$project = 'C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject'
$script  = 'C:\Users\edwar\project-uppercut\tools\engine\bp_generate_bout_walker.py'
$outDir  = 'C:\Users\edwar\project-uppercut\sandbox\Saved\BoutWalk'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$open = Get-Process -Name 'UnrealEditor' -ErrorAction SilentlyContinue
if ($open -and -not $Force) {
    Write-Output "REFUSING: UnrealEditor is open (pid $($open.Id -join ', '))."
    Write-Output "Close it, or re-run with -Force if that session is disposable."
    exit 5
}

if ($Gen) {
    $genOut = Join-Path $outDir 'gen.json'
    if (Test-Path $genOut) { Remove-Item $genOut -Force }
    $env:UE_GEN_OUT = $genOut
    $env:UE_GEN_SEED = "$Seed"
    $args = @("`"$project`"", '-run=pythonscript', "-script=`"$script`"",
              '-unattended', '-nopause', '-nosplash', '-nullrhi', '-NoLogTimes')
} else {
    $args = @("`"$project`"", 'L_BoutWalk', '-game',
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
# Both marker kinds are captured IN LOG ORDER - the sealed check is positional, so
# splitting them into separate files here would destroy the evidence it needs.
$markers = Select-String -Path $runLog -Pattern '((?:B|S)\|[0-9|\-]+)\s*$' -AllMatches |
    ForEach-Object { $_.Matches[0].Groups[1].Value }
if (-not $markers -or $markers.Count -eq 0) { Write-Output 'NO MARKERS'; exit 4 }
[IO.File]::WriteAllText($outFile, (($markers -join "`n") + "`n"), [Text.UTF8Encoding]::new($false))
Write-Output "OUT: $outFile"
Write-Output "MARKERS: $($markers.Count)"
Write-Output "SHA256: $((Get-FileHash $outFile -Algorithm SHA256).Hash)"
python 'C:\Users\edwar\project-uppercut\tools\engine\analyze_bout_walker.py' $outFile
exit 0
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 12:24 UTC | END ]
