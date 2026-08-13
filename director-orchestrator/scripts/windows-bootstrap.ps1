# [ Codex | GPT-5 | 2026-08-13 23:33 UTC | START: imported from director-orchestrator@110e403 and specialized for Project Uppercut ]
$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

function New-RandomSecret {
    $bytes = New-Object byte[] 48
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    return [Convert]::ToBase64String($bytes).Replace("+", "-").Replace("/", "_").TrimEnd("=")
}

$envText = Get-Content ".env" -Raw
$envText = $envText -replace 'ORCHESTRATOR_SHARED_SECRET=REPLACE_WITH_RANDOM_SECRET', ("ORCHESTRATOR_SHARED_SECRET=" + (New-RandomSecret))
$envText = $envText -replace 'N8N_ENCRYPTION_KEY=REPLACE_WITH_RANDOM_SECRET', ("N8N_ENCRYPTION_KEY=" + (New-RandomSecret))
$envText = $envText -replace 'N8N_POSTGRES_PASSWORD=REPLACE_WITH_RANDOM_SECRET', ("N8N_POSTGRES_PASSWORD=" + (New-RandomSecret))
if ($envText -match '(?m)^ALLOW_PAID_RUNS=') {
    $envText = $envText -replace '(?m)^ALLOW_PAID_RUNS=.*$', 'ALLOW_PAID_RUNS=false'
} else {
    $envText += "`r`nALLOW_PAID_RUNS=false`r`n"
}
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path (Get-Location) ".env"), $envText, $utf8NoBom)

docker compose --env-file .env config | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "docker compose config failed with exit code $LASTEXITCODE"
}

docker compose --env-file .env up -d --build
if ($LASTEXITCODE -ne 0) {
    throw "docker compose up failed with exit code $LASTEXITCODE"
}

$n8nPort = if ($envText -match '(?m)^N8N_HOST_PORT=(\d+)\s*$') { $Matches[1] } else { '15678' }

Write-Host "Project Uppercut Director started in dry-run mode."
Write-Host "Open http://localhost:$n8nPort to initialize n8n, then import n8n/workflows/director-intake.json."
Write-Host "Do not enable paid runs until provider credentials and spend limits are configured."
# [ Codex | GPT-5 | 2026-08-13 23:37 UTC | END: imported from director-orchestrator@110e403 and specialized for Project Uppercut ]
