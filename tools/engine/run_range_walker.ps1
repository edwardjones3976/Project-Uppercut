# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:05 UTC | START ]
# One determinism leg for BP_RangeWalker: launch L_RangeWalk under -game with a pinned
# fixed timestep, kill the Turnkey wedge while it runs, extract the R| markers and hash.
# The seed is baked into the Blueprint at AUTHORING time, so a different-seed leg means
# regenerating the asset first (see run_range_walker_gen.ps1 -Seed).
param(
    [Parameter(Mandatory=$true)][string]$Tag,
    [string]$Level = 'L_RangeWalk'
)
$ErrorActionPreference = 'Continue'
$editor  = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$project = 'C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject'
$outDir  = 'C:\Users\edwar\project-uppercut\sandbox\Saved\RangeWalk'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$runLog  = Join-Path $outDir "$Tag.runlog"
$outFile = Join-Path $outDir "$Tag.txt"
foreach ($f in @($runLog, $outFile)) { if (Test-Path $f) { Remove-Item $f -Force } }

# -abslog with an unopenable path silently suppresses ALL logging (runbook trap):
# let the editor write its normal log and copy it afterwards instead.
$p = Start-Process -FilePath $editor -PassThru -WindowStyle Hidden -ArgumentList @(
    "`"$project`"", $Level, '-game',
    '-UseFixedTimeStep', '-FPS=60', '-Deterministic',
    '-unattended', '-nopause', '-nosplash', '-nullrhi', '-log', '-NoLogTimes'
)
Write-Output "run pid: $($p.Id) tag=$Tag"

$deadline = (Get-Date).AddMinutes(12)
while (-not $p.HasExited) {
    Start-Sleep -Seconds 3
    Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" |
        Where-Object { $_.CommandLine -match 'Build\.bat.+ValidatePlatforms' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    if ((Get-Date) -gt $deadline) {
        Write-Output 'TIMEOUT - killing game'
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        break
    }
}
Write-Output "exit code: $($p.ExitCode)"

$src = 'C:\Users\edwar\project-uppercut\sandbox\Saved\Logs\UppercutSandbox.log'
if (-not (Test-Path $src)) { Write-Output 'NO LOG'; exit 3 }
Copy-Item $src $runLog -Force

# PrintString prefixes the emitting actor: "LogBlueprintUserMessages: [BP_RangeWalker_C_0] R|..."
# so the marker is anchored at end-of-line rather than after the log category.
$markers = Select-String -Path $runLog -Pattern '(R\|[0-9|\-]+)\s*$' -AllMatches |
    ForEach-Object { $_.Matches[0].Groups[1].Value }
if (-not $markers -or $markers.Count -eq 0) { Write-Output 'NO MARKERS'; exit 4 }
[IO.File]::WriteAllText($outFile, (($markers -join "`n") + "`n"), [Text.UTF8Encoding]::new($false))

Write-Output "OUT: $outFile"
Write-Output "MARKERS: $($markers.Count)"
Write-Output "SHA256: $((Get-FileHash $outFile -Algorithm SHA256).Hash)"
exit 0
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:05 UTC | END ]
