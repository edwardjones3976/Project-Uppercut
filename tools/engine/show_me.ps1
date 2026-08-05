# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:20 UTC | START ]
# LOOK AT THE GAME. One command, no arguments needed.
#
#   .\tools\engine\show_me.ps1
#
# Runs the rendered slice, drops dated screenshots into docs\visuals\ where they
# are committed and visible on GitHub, and prints the marker-stream hash so the
# run is evidence rather than a picture.
#
# Written because the Director asked, reasonably, where any of this could be
# SEEN - and the honest answer was that it took knowing three scripts, a tag
# convention and where Saved\phaseM lives. A thing you cannot look at without a
# runbook is a thing nobody looks at.
#
# Notes for anyone reading this later:
#   - No rebuild is triggered. The C++ module changes rarely; if you HAVE changed
#     it, run tools\engine\build_uppercut_core.ps1 first, and close the editor,
#     because Live Coding holds the DLL and the build refuses.
#   - This runs happily WITH the editor open. Verified 2026-08-05.
#   - The stream hash should be stable for a given seed and tick count. If it
#     changes and you did not mean it to, something in the sim moved.
param(
    [int]$Seed = 4242,
    [int]$Ticks = 5400,
    [string]$Tag = "",
    [switch]$NoArena,          # bare mannequins on a checker floor, no ring
    [switch]$KeepAll,          # copy every frame, not just the three useful ones
    [string]$Repo = "C:\Users\edwar\project-uppercut"
)

if (-not $Tag) { $Tag = "SHOW" + (Get-Date -Format "MMdd_HHmm") }
$visuals = Join-Path $Repo "docs\visuals"
New-Item -ItemType Directory -Force -Path $visuals | Out-Null

$probe = Join-Path $Repo "tools\engine\run_render_probe.ps1"
$probeArgs = @("-Tag", $Tag, "-Seed", $Seed, "-Ticks", $Ticks, "-Repo", $Repo)
if (-not $NoArena) { $probeArgs += "-Arena" }

Write-Host ""
Write-Host "Running the rendered slice: seed $Seed, $Ticks ticks, arena=$(-not $NoArena)"
Write-Host ""
& powershell -NoProfile -ExecutionPolicy Bypass -File $probe @probeArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "The run failed. Its log is in sandbox\Saved\phaseM\run_$Tag.log"
    exit 1
}

$shots = Join-Path $Repo "sandbox\Saved\phaseM\shots_$Tag"
$stamp = Get-Date -Format "yyyy-MM-dd"
$wanted = if ($KeepAll) { "*.png" } else { @("tick_00900.png", "tick_03000.png", "tick_04200.png") }

$copied = 0
Get-ChildItem $shots -Filter *.png | ForEach-Object {
    $keep = $KeepAll -or ($wanted -contains $_.Name)
    if ($keep) {
        $dest = Join-Path $visuals ("{0}_{1}_{2}" -f $stamp, $Tag, $_.Name)
        Copy-Item $_.FullName $dest -Force
        $copied = $copied + 1
        Write-Host ("  saved  docs\visuals\{0}_{1}_{2}" -f $stamp, $Tag, $_.Name)
    }
}

Write-Host ""
Write-Host "$copied screenshot(s) in docs\visuals\ - commit them and they show on GitHub."
Write-Host "Open the folder:  explorer $visuals"
Write-Host ""
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 20:20 UTC | END ]
