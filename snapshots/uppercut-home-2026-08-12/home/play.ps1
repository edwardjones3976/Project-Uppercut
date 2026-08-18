# Open L_UppercutDevArena in the clean Uppercut UE 5.8 project.
param(
    [string]$Engine = $env:UPPERCUT_ENGINE
)
$ErrorActionPreference = "Stop"
if (-not $Engine) { $Engine = "C:\Program Files\Epic Games\UE_5.8" }
$Editor = Join-Path $Engine "Engine\Binaries\Win64\UnrealEditor.exe"
$Project = "C:\Users\edwar\Uppercut\Uppercut.uproject"
# Correct content path (NOT /Game/Uppercut/...)
$Map = "/Game/ProjectUppercut/Maps/L_UppercutDevArena"
Start-Process -FilePath $Editor -ArgumentList @($Project, $Map)
Write-Host "Launched $Editor $Project $Map"
