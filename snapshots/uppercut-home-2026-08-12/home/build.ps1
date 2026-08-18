# Build UppercutEditor (UE 5.8) for the clean Uppercut home.
param(
    [string]$Target = "UppercutEditor",
    [string]$Config = "Development",
    [string]$Engine = "C:\Program Files\Epic Games\UE_5.8",
    [string]$Project = "C:\Users\edwar\Uppercut\Uppercut.uproject",
    [string]$Log = "C:\Users\edwar\Uppercut\Saved\build_last.txt"
)

$ErrorActionPreference = "Stop"
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
