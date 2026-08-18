# Isolate Fighter0 and loop orthodox OVERHAND RIGHT (presentation only).
# Orthodox: rear hand = right. Overhand right != lateral rear hook (use -Clip hook_rear for that).
# Does not start a fight; combat authority untouched.
param(
    [string]$Engine = "C:\Program Files\Epic Games\UE_5.8",
    [string]$Project = "C:\Users\edwar\Uppercut\Uppercut.uproject",
    [int]$Fighter = 0,
    [string]$Clip = "overhand_right"
)
$ErrorActionPreference = "Stop"
$Editor = Join-Path $Engine "Engine\Binaries\Win64\UnrealEditor.exe"
$Map = "/Game/ProjectUppercut/Maps/L_UppercutDevArena"
$args = @(
    $Project,
    $Map,
    "-game",
    "-WINDOWED",
    "-ResX=1280",
    "-ResY=720",
    "-UppercutPoseStudio",
    "-UppercutPoseFighter=$Fighter",
    "-UppercutPoseClip=$Clip"
)
Write-Host "Launching pose studio: Fighter$Fighter clip=$Clip (orthodox overhand right)"
Write-Host "$Editor $($args -join ' ')"
Start-Process -FilePath $Editor -ArgumentList $args
