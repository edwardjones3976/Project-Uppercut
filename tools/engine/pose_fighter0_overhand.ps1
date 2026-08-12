# Isolate Fighter0 and loop orthodox OVERHAND RIGHT (presentation only).
# Orthodox: rear hand = right. Overhand right != lateral rear hook (use -Clip hook_rear).
# Does not start a fight; combat authority untouched.
#
# Capture path (after ~6s): sandbox/Saved/pose_studio/fighter0_overhand_right_orthodox.png
# Uses MatchDirector lights + floor + locked camera + FScreenshotRequest (non-black).
param(
    [string]$Engine = "C:\Program Files\Epic Games\UE_5.8",
    [string]$Repo = "C:\Users\edwar\project-uppercut",
    [int]$Fighter = 0,
    [string]$Clip = "overhand_right"
)
$ErrorActionPreference = "Stop"
$Editor = Join-Path $Engine "Engine\Binaries\Win64\UnrealEditor.exe"
$Project = Join-Path $Repo "sandbox\UppercutSandbox.uproject"
$Map = "/Game/ProjectUppercut/Maps/L_UppercutDevArena"
$launchArgs = @(
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
Write-Host "$Editor $($launchArgs -join ' ')"
Start-Process -FilePath $Editor -ArgumentList $launchArgs
