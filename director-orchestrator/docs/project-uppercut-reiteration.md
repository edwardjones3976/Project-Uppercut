<!-- [ Codex | GPT-5 | 2026-08-13 23:33 UTC | START: imported from director-orchestrator@110e403 and specialized for Project Uppercut ] -->
# Embedded Project Uppercut Profile

This directory is the Project Uppercut deployment profile copied from the standalone Director runtime. It is not just another prompt: repository, channel, storage, ports, provider budgets, and acceptance context are isolated. Do not enable paid runs until this profile passes its own dry-run and one low-risk end-to-end live test.

## Isolation requirements

- Private repository allowlist limited to `edwardjones3976/Project-Uppercut`; expansion requires a reviewed configuration change.
- Dedicated `#uppercut-ops` channel and `/uppercut-director` command.
- Separate `.env`, task database, Docker project/volume names, host ports, provider budgets, and callback secrets.
- Project-specific acceptance checks and branch protection.
- No shared private documents, genealogy evidence, credentials, or provider sessions unless explicitly approved.
- Separate audit and backup retention.

## Reiteration checklist

1. **Done in source:** deployment configuration copied without runtime secrets.
2. **Done in source:** Compose project and durable volume names use `project-uppercut-director`.
3. **Done in source:** Slack and repository scope default to `#uppercut-ops` and Project Uppercut only.
4. **Done in source:** Project Uppercut instructions and scope tests live beside the runtime.
5. **Owner/operator next:** run the dry-run smoke test with `ALLOW_PAID_RUNS=false`.
6. **Owner/operator next:** add one provider credential and run one reversible task on an isolated branch.
7. **Owner/operator gate:** review the draft PR, logs, spend, and approval behavior before routine use.

No agent may merge, deploy, publish, delete, purchase, expand access, or handle sensitive Project Uppercut data without the matching owner decision gate.
<!-- [ Codex | GPT-5 | 2026-08-13 23:37 UTC | END: imported from director-orchestrator@110e403 and specialized for Project Uppercut ] -->
