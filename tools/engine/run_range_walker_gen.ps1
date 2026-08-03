# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:02 UTC | START ]
# Headless generator runner for BP_RangeWalker. Same wedge discipline as the other
# engine runners: the Turnkey Build.bat -Mode=ValidatePlatforms child ping-loops on
# every editor boot and never launches UBT, so it is killed continuously while the
# editor works (see docs/phase1a/engine_setup_runbook.md).
param(
    [string]$OutFile = 'C:\Users\edwar\project-uppercut\sandbox\Saved\rangewalker_gen.json',
    [int]$Seed = 56057345
)
$ErrorActionPreference = 'Continue'
$editor  = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$project = 'C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject'
$script  = 'C:\Users\edwar\project-uppercut\tools\engine\bp_generate_range_walker.py'

if (Test-Path $OutFile) { Remove-Item $OutFile -Force }
$env:UE_GEN_OUT = $OutFile
$env:UE_GEN_SEED = "$Seed"
Write-Output "seed: $Seed"

$p = Start-Process -FilePath $editor -PassThru -WindowStyle Hidden -ArgumentList @(
    "`"$project`"", '-run=pythonscript', "-script=`"$script`"",
    '-unattended', '-nopause', '-nosplash', '-nullrhi', '-NoLogTimes'
)
Write-Output "gen pid: $($p.Id)"

$deadline = (Get-Date).AddMinutes(15)
while (-not $p.HasExited) {
    Start-Sleep -Seconds 3
    Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" |
        Where-Object { $_.CommandLine -match 'Build\.bat.+ValidatePlatforms' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    if ((Get-Date) -gt $deadline) {
        Write-Output 'TIMEOUT - killing editor'
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        break
    }
}
Write-Output "exit code: $($p.ExitCode)"
if (Test-Path $OutFile) {
    Write-Output '--- REPORT ---'
    Get-Content $OutFile -Raw
} else {
    Write-Output 'NO REPORT WRITTEN'
    exit 3
}
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:02 UTC | END ]
