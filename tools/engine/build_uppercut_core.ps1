# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | START ]
# Build the UppercutCore module the only way that does not wedge in this spawn
# context: UnrealBuildTool invoked directly through the engine's bundled dotnet,
# with cwd Engine\Source. Build.bat wedges forever in its own lock-file wait loop
# here (docs/phase1a/engine_setup_runbook.md); this sidesteps the wrapper.
# Target note (found 2026-08-04): build UppercutSandboxEditor, not UppercutSandbox.
# Every phase so far runs through the EDITOR binary - commandlets natively, and the
# rendered slice via UnrealEditor.exe with -game. The monolithic game target has
# never been linked here and currently fails with nine unresolved Core externals
# (GInternalProjectName, FMemory_Malloc, ...); packaging it is a later job, not a
# blocker for evidence runs.
param(
    [string]$Target = "UppercutSandboxEditor",
    [string]$Config = "Development",
    [string]$Engine = "C:\Program Files\Epic Games\UE_5.8",
    [string]$Project = "C:\Users\edwar\project-uppercut\sandbox\UppercutSandbox.uproject",
    [string]$Log = "C:\Users\edwar\project-uppercut\sandbox\Saved\build_last.txt"
)

$dotnet = Join-Path $Engine "Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe"
$ubt = Join-Path $Engine "Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll"
$src = Join-Path $Engine "Engine\Source"

New-Item -ItemType Directory -Force -Path (Split-Path $Log) | Out-Null
Push-Location $src
try {
    & $dotnet $ubt $Target Win64 $Config "-project=$Project" -WaitMutex 2>&1 |
        Tee-Object -FilePath $Log
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}
Write-Host "BUILD EXIT: $code"
exit $code
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 17:32 UTC | END ]
