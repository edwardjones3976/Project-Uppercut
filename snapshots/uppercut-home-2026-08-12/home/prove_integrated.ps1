# Headless integrated 1R proof against this project's editor binary.
param(
    [string]$Engine = "C:\Program Files\Epic Games\UE_5.8",
    [int]$Seed = 4242,
    [int]$Ticks = 10800
)
$ErrorActionPreference = "Stop"
$Cmd = Join-Path $Engine "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$Project = "C:\Users\edwar\Uppercut\Uppercut.uproject"
$Repo = "C:\Users\edwar\Uppercut"
$OutDir = Join-Path $Repo "Saved\integratedArena"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$Out = Join-Path $OutDir ("integrated_{0}_{1}.stream" -f $Seed, $Ticks)
if (Test-Path $Out) { Remove-Item $Out -Force }
$argv = @(
    $Project,
    "-run=UppercutLiveArena",
    "-seed=$Seed",
    "-ticks=$Ticks",
    "-repo=$Repo",
    "-out=$Out",
    "-integrated=1",
    "-unattended", "-nopause", "-nosplash"
)
Write-Host "Running: $Cmd $($argv -join ' ')"
& $Cmd @argv
Write-Host "EXIT $LASTEXITCODE"
if (Test-Path $Out) {
    Get-Content $Out -TotalCount 6
    Get-Content $Out -Tail 2
} else {
    Write-Host "NO STREAM WRITTEN"
    exit 1
}
