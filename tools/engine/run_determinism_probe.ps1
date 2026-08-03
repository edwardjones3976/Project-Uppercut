# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 23:57 UTC | START ]
# Headless determinism-probe runner. Hardened against the known Turnkey Build.bat
# retry-loop wedge (see docs/phase1a/engine_setup_runbook.md): while the editor runs,
# any Build.bat -Mode=ValidatePlatforms child that appears is killed; the editor then
# proceeds normally (verified behavior, exit 0).
param(
    [int]$Seed = 56057345,
    [int]$Ticks = 10000,
    [Parameter(Mandatory=$true)][string]$OutFile
)
$ErrorActionPreference = 'Continue'
$editor = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$project = 'C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject'
$probe = 'C:\Users\edwar\project-uppercut\tools\engine\determinism_probe.py'

$env:UE_PROBE_SEED = "$Seed"
$env:UE_PROBE_TICKS = "$Ticks"
$env:UE_PROBE_OUT = $OutFile
if (Test-Path $OutFile) { Remove-Item $OutFile -Force }
if (Test-Path "$OutFile.failed") { Remove-Item "$OutFile.failed" -Force }

$p = Start-Process -FilePath $editor -ArgumentList @("`"$project`"", '-run=pythonscript', "-script=`"$probe`"", '-unattended', '-nopause', '-nosplash') -PassThru -WindowStyle Hidden
Write-Output "editor pid: $($p.Id) seed=$Seed ticks=$Ticks"

while (-not $p.HasExited) {
    Start-Sleep -Seconds 5
    $wedge = Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" |
        Where-Object { $_.CommandLine -match 'Build\.bat.+ValidatePlatforms' -and $_.ParentProcessId -eq $p.Id }
    foreach ($w in $wedge) {
        Write-Output "killing turnkey wedge pid $($w.ProcessId)"
        Stop-Process -Id $w.ProcessId -Force -ErrorAction SilentlyContinue
    }
}
Write-Output "editor exit code: $($p.ExitCode)"
if (Test-Path "$OutFile.failed") { Write-Output "PROBE FAILED:"; Get-Content "$OutFile.failed"; exit 2 }
if (-not (Test-Path $OutFile)) { Write-Output "NO OUTPUT PRODUCED"; exit 3 }
$h = (Get-FileHash $OutFile -Algorithm SHA256).Hash
$n = (Get-Content $OutFile | Measure-Object -Line).Lines
Write-Output "OUT: $OutFile"
Write-Output "LINES: $n"
Write-Output "SHA256: $h"
exit 0
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 23:57 UTC | END ]
