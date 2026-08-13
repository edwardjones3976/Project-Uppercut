<!-- [ Codex | GPT-5 | 2026-08-13 23:33 UTC | START ] -->

# Embedded Project Uppercut Director Orchestrator — 2026-08-13

## Outcome

The standalone private `director-orchestrator` repository was imported into
`director-orchestrator/` from source commit `110e403`. Repository metadata, runtime state, caches,
and secrets were not copied. The embedded copy is a Project Uppercut deployment profile rather than
a second generic Director.

## Project-specific controls

- Project and default repository are fixed to Project Uppercut.
- A deterministic repository allowlist rejects off-project assignments before provider dispatch.
- Every provider receives project, repository, starting-ref, task, and Slack-thread context.
- Direct API intake and Slack intake enforce the configured owner and `#uppercut-ops` channel.
- The dedicated `/uppercut-director` command, Compose project, host ports, database, and volumes do
  not collide with the standalone Director profile.
- Direct Slack-to-orchestrator intake is the default. The optional n8n workflow preserves the
  caller's bearer header, so the orchestrator's constant-time comparison remains authoritative;
  n8n does not receive the shared secret or manufacture authority for anonymous webhook traffic.
- The Director and Claude prompts require current repository instructions and numbered Decisions.
  C++ combat authority, Python's reference-only role, the threshold freeze, and the current
  authenticity HOLD are preserved; this slice changes no combat value or ruling.
- Paid execution remains disabled in `.env.example`; no credential, container, provider run, Slack
  post, deployment, or merge occurred in this slice.
- Python dependencies have an exact Python 3.12 lock, Docker excludes local environments/secrets,
  and the Python, Postgres, and n8n images are pinned by digest.
- Bootstrap forces dry-run mode before startup and fails on native Docker command errors instead of
  printing a false success message.

## Windows defect found and repaired

The imported SQLite store used connection context managers that commit or roll back but do not close
the connection. Linux commonly tolerates removal of an open temporary database; Windows does not.
The embedded store now closes every connection in a `finally` block, and its existing temporary-
database tests pass on Windows.

## Validation

- Canonical isolated environment: Python 3.12.10; `pydantic 2.13.4` and `pydantic-core 2.46.4`;
  `pip check` passed.
- Embedded orchestration unit suite: 13 passed on Python 3.12.
- n8n workflow JSON: valid.
- Docker Compose configuration: valid using `.env.example` without starting services.
- Bootstrap PowerShell syntax: valid.
- Locked Linux Docker image build: passed without warnings; no service started.
- Project Uppercut suite: 1,437 passed.
- Rule validators: `RESULT: OK`; generated status and decision index are current; C++ source-integrity
  checker passed (this is not an Unreal compile or runtime proof).

## Source relationship

`director-orchestrator/SOURCE_SNAPSHOT.md` records the source commit and the deliberate divergence.
Future upstream changes must be reviewed against that record instead of overwriting the embedded
scope locks.

<!-- [ Codex | GPT-5 | 2026-08-13 23:55 UTC | END ] -->
