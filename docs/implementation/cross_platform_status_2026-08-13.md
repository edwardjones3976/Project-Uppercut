<!-- [ Codex | GPT-5 | 2026-08-13 23:33 UTC | START ] -->

# Cross-platform status — embedded Project Uppercut Director (2026-08-13)

## Identity

| Field | Value |
|---|---|
| Branch | `codex/embed-director-orchestrator` |
| Source | `edwardjones3976/director-orchestrator@110e403` |
| Pull request | https://github.com/edwardjones3976/Project-Uppercut/pull/45 (draft) |
| Paid provider calls | **0** |
| Deployment | **Not started** |
| Project suite | **1,437 passed** |
| Embedded suite | **13 passed** |

## What landed

1. The 29-file Director runtime is embedded under `director-orchestrator/` without its Git history,
   runtime state, caches, or secrets.
2. Deterministic Project Uppercut project/repository defaults and an off-project allowlist block are
   enforced before provider dispatch.
3. Slack/API intake, Compose resources, host ports, prompts, provenance, and operating docs are
   specialized for Project Uppercut.
4. A Windows SQLite connection-lifecycle defect found during validation is repaired.
5. Direct constant-time-authenticated intake is the default; optional n8n preserves caller auth and
   holds no orchestrator shared secret.
6. Python dependencies are exactly locked; Docker build context excludes secrets/environments; all
   deployment images are digest-pinned; bootstrap forces dry-run and checks native exit codes.
7. GitHub CI has a separate embedded-Director job for its unit suite, n8n JSON, and Compose config.

## Measured

This is operations/control-plane work, not combat calibration. It changes no combat value, C++/Python
authority, authenticity band, waiver, or `pressure_threshold`.

- Canonical `.venv`: Python 3.12.10; `pydantic 2.13.4` + `pydantic-core 2.46.4`;
  `pip check` passed.
- Embedded unit suite: 13 passed on Windows / Python 3.12.
- n8n JSON parse: pass.
- Docker Compose configuration: pass; no container started.
- Bootstrap AST parse: pass.
- Locked Linux Docker image build: pass without warnings; no service started.
- Main Project Uppercut suite: 1,437 passed.
- Validators: `RESULT: OK`; status, decision index, and C++ source-integrity checks passed.

## Channel disposition

| Channel | Status | Evidence |
|---|---|---|
| Local repo | Done | Embedded runtime, source record, dev log, this packet |
| GitHub | Posted | Draft PR #45 carries this status; Actions pending at packet update |
| Linear | N/A | No existing PRO issue was changed or closed |
| Slack `#uppercut-ops` | N/A | User requested repository duplication, not an external post |
| Provider dashboards | N/A | Paid execution remains disabled; no provider dispatched |

## Related records

- `director-orchestrator/README.md`
- `director-orchestrator/SOURCE_SNAPSHOT.md`
- `director-orchestrator/docs/project-uppercut-reiteration.md`
- `docs/development-log/2026-08-13-embedded-director-orchestrator.md`
- `docs/governance/DIRECTOR_OPERATING_CHARTER.md`
- Decision 0040 (C++ authority and authenticity HOLD)

<!-- [ Codex | GPT-5 | 2026-08-13 23:57 UTC | END ] -->
