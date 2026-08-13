<!-- [ Codex | GPT-5 | 2026-08-13 23:33 UTC | START: imported from director-orchestrator@110e403 and specialized for Project Uppercut ] -->
# Project Uppercut Director Orchestrator

A bounded, event-driven control plane for keeping paid specialist AI agents focused on Project Uppercut from a private Slack channel. It is embedded in the Project Uppercut monorepo and hard-scoped to `edwardjones3976/Project-Uppercut`. The first deployment target is an always-on Windows desktop using Docker Desktop. Paid execution is disabled by default.

This directory is derived from [`director-orchestrator`](https://github.com/edwardjones3976/director-orchestrator) commit `110e403`. See [SOURCE_SNAPSHOT.md](SOURCE_SNAPSHOT.md) for provenance and the deliberate Project Uppercut differences.

## What is included

- A Slack Socket Mode gateway, so the desktop does not need a public inbound port.
- A FastAPI orchestration service with idempotent task intake and durable SQLite state.
- Deterministic approval gates and a repository allowlist that model output cannot remove.
- Adapters for Cursor Cloud Agents, Claude Code Routines, Gemini Antigravity Managed Agents, and the Perplexity Agent API.
- An OpenAI Director planner/reviewer using Structured Outputs.
- An optional local n8n deployment and importable authenticated pass-through workflow.
- A reusable Slack app manifest and a Claude routine prompt.
- Dry-run previews for testing without provider spending.

Detailed operations notes live in `docs/always-on-runbook.md`, `docs/provider-setup.md`, `docs/cloud-hosting-later.md`, and `docs/project-uppercut-reiteration.md`.

## Architecture

1. Aesop posts `DIRECTOR` in private `#uppercut-ops`, or uses `/uppercut-director`.
2. The Slack gateway accepts only the configured owner and channel, ignores bot messages, and forwards a stable Slack event ID.
3. By default the gateway calls the constant-time-authenticated orchestrator directly. If enabled, n8n transparently preserves that bearer header instead of granting its own authority.
4. The orchestrator deduplicates it, creates a task record, applies hard limits, and builds a preview or live Director plan.
5. Specialist runs are dispatched sequentially unless the plan explicitly marks independent work.
6. Results are reviewed against acceptance checks. Revision loops are capped.
7. Slack receives the terminal state or a narrowly scoped owner decision request. Approval-gated plans include a confirm button; ambiguity requires a written `/uppercut-director approve DIR-… <clarification>` response.
8. In-progress tasks resume after an orchestrator restart without redispatching an already-recorded provider run.

## Windows desktop quick start

Prerequisites: Docker Desktop with Linux containers and PowerShell 7 or Windows PowerShell 5.1.

```powershell
git clone https://github.com/edwardjones3976/Project-Uppercut.git
cd Project-Uppercut\director-orchestrator
powershell -ExecutionPolicy Bypass -File .\scripts\windows-bootstrap.ps1
```

The bootstrap script creates `.env` with random local secrets and starts the stack. It does not create or store provider credentials.

The orchestrator health endpoint is `http://localhost:18080/health`. Optional n8n is available at `http://localhost:15678`; create its local owner login and import `n8n/workflows/director-intake.json` only if you want that pass-through, then set `N8N_DIRECTOR_WEBHOOK_URL`. Direct authenticated intake remains the safer default. These host ports avoid colliding with the standalone shared Director profile.

For always-on operation, enable Docker Desktop's start-on-sign-in option, disable sleep/hibernation for the host while plugged in, keep Windows and Docker auto-restart behavior enabled, and use a UPS if this desktop is expected to act as infrastructure. Containers use `restart: unless-stopped`; in-progress provider polls resume from durable task state after the orchestrator restarts.

## Slack app setup

1. In Slack app management, create an app from `slack-app-manifest.yaml` in the `Edge_Engine` workspace.
2. Install it to the workspace.
3. Generate an app-level token with `connections:write` for Socket Mode.
4. Put the app token in `SLACK_APP_TOKEN` and the bot token in `SLACK_BOT_TOKEN` inside `.env`.
5. Invite the app to private `#uppercut-ops` (`C0BP62MBFNK`).
6. Restart only the Slack gateway: `docker compose restart slackbot`.

Never paste tokens into Slack, chat, source control, screenshots, or issue bodies.

## Safe smoke test

Keep `ALLOW_PAID_RUNS=false`, then post:

```text
DIRECTOR
Project: Project Uppercut
Outcome: Produce a dry-run plan for reviewing the current Project Uppercut parity HOLD.
Constraints: Do not edit GitHub and do not call paid providers.
```

The expected result is a task ID, a preview plan, and `OWNER_DECISION_REQUIRED` because live execution is disabled. No provider should run.

## Enabling live execution

Add credentials one provider at a time. Verify each adapter independently before setting `ALLOW_PAID_RUNS=true`.

1. `OPENAI_API_KEY` and the configured Director model.
2. At least one specialist credential.
3. Confirm the checked-in repository allowlist and starting branch. The default profile permits only Project Uppercut.
4. Provider-side spending limits.
5. `ALLOW_PAID_RUNS=true`, followed by a low-risk test task.

ChatGPT Plus, Claude Pro, Cursor Pro, Gemini subscriptions, and Perplexity Pro do not necessarily include API usage. Claude Code Routine triggers are the exception represented here: they use the routine-specific URL and token supplied by Claude's routine UI.

## Cloud hosting later

The desktop design intentionally keeps Slack on Socket Mode and stores state locally. For cloud migration:

- Move the orchestrator state from SQLite to managed PostgreSQL.
- Put n8n and the orchestrator behind HTTPS with restricted ingress.
- Replace long-lived cloud credentials with OIDC or narrowly scoped service credentials where supported.
- Use a managed secret store, encrypted backups, centralized logs, uptime monitoring, and provider webhook verification.
- Review and deliberately advance the checked-in container digests; do not replace them with floating tags.
- Keep the Slack channel, task schema, approval policy, and provider adapters unchanged.

Do not expose the local n8n editor or orchestrator port directly to the internet.

## Project Uppercut scope lock

This embedded copy is the separate Project Uppercut deployment profile. It has its own Compose project and volumes, host ports, Slack channel/command, task database, provider budgets, prompt policy, and repository allowlist. Missing repository values are filled with Project Uppercut; any other repository stops in `OWNER_DECISION_REQUIRED` and requires a reviewed configuration change before dispatch. Do not commingle its credentials, task data, or provider sessions with the standalone Director deployment.

The checkout does not contain secrets and this change does not start containers or paid runs. Bootstrap creates a local `.env`; enabling provider credentials and `ALLOW_PAID_RUNS=true` remains an owner operation after the dry-run and one reversible live proof.

<!-- [ Codex | GPT-5 | 2026-08-13 23:45 UTC | START: reproducible isolated Python setup and secret-safe validation ] -->
## Local Python setup and validation

Use Python 3.12 to match the container runtime. The virtual environment is local to this directory and ignored by Git; these commands do not change the global Python installation. `requirements.txt` is the human-maintained compatibility contract, while `requirements.lock.txt` is the exact transitive resolution validated for Python 3.12.

From `director-orchestrator` in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip check

$env:PYTHONPATH = (Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
Remove-Item Env:PYTHONPATH

.\.venv\Scripts\python.exe -m json.tool n8n\workflows\director-intake.json | Out-Null
$env:DIRECTOR_ENV_FILE = '.env.example'
docker compose --env-file .env.example config --quiet
Remove-Item Env:DIRECTOR_ENV_FILE
```

The Compose command validates configuration against placeholders without starting containers, reading a real `.env`, or rendering secret-bearing configuration to the terminal.
<!-- [ Codex | GPT-5 | 2026-08-13 23:45 UTC | END: reproducible isolated Python setup and secret-safe validation ] -->
<!-- [ Codex | GPT-5 | 2026-08-13 23:37 UTC | END: imported from director-orchestrator@110e403 and specialized for Project Uppercut ] -->
