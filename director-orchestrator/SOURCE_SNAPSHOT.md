<!-- [ Codex | GPT-5 | 2026-08-13 23:33 UTC | START ] -->

# Source snapshot and synchronization

This embedded runtime was imported from the private repository
[`edwardjones3976/director-orchestrator`](https://github.com/edwardjones3976/director-orchestrator)
at commit `110e403` (`Merge pull request #1 from edwardjones3976/agent/initial-director-setup`).
The source repository's `.git` directory, history, runtime data, caches, and secrets were not copied.

The import preserves the standalone runtime and then applies a Project Uppercut profile:

- Project and repository defaults are fixed to Project Uppercut.
- A deterministic allowlist prevents dispatch to another repository.
- Direct API intake, Slack intake, the slash command, Compose project, ports, and durable volumes are isolated for Project Uppercut.
- Direct authenticated intake is the default. Optional n8n forwards the caller's bearer header and has no copy of the orchestrator shared secret.
- The Director and Claude prompts require current repository instructions and numbered Decisions, including live C++ combat authority and the current authenticity HOLD.
- Python dependencies are locked for 3.12, Docker excludes local secrets/environments, deployment images are pinned by digest, and bootstrap forces dry-run with checked native exit codes.
- SQLite connections are explicitly closed so restart/idempotency tests and task databases behave correctly on Windows.
- Project Uppercut CI runs the embedded unit tests and validates its n8n and Compose configuration.

Future upstream synchronization should be a reviewed diff from the last recorded source commit. Do
not replace this directory wholesale: retain the scope enforcement, Project Uppercut prompts,
deployment isolation, local contribution tags, and tests unless a new Director ruling deliberately
changes them.

<!-- [ Codex | GPT-5 | 2026-08-13 23:55 UTC | END ] -->
