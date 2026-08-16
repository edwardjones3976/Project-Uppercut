<!-- [ Codex | GPT-5 | 2026-08-16 03:40 UTC | START: refreshed Director source provenance ] -->

# Director Orchestrator source snapshot

- Canonical repository: `edwardjones3976/director-orchestrator`
- Isolation remediation: [PR #20](https://github.com/edwardjones3976/director-orchestrator/pull/20)
- Source commit: `b54efdb749bda656adf6a8135d828da3165d34f7`
- Source tree: `959982dacf39be625207574098d60a52ebbfadcf`
- Transition plan: [director-orchestrator PR #18](https://github.com/edwardjones3976/director-orchestrator/pull/18)
- Project bridge: [Project-Uppercut PR #47](https://github.com/edwardjones3976/Project-Uppercut/pull/47)
- Acceptance tracker: [Project-Uppercut issue #48](https://github.com/edwardjones3976/Project-Uppercut/issues/48)
- Refreshed: 2026-08-15
- Snapshot pull request: [Project-Uppercut PR #45](https://github.com/edwardjones3976/Project-Uppercut/pull/45)

## Creation and exclusions

Every upstream blob at the source tree above was copied under `director-orchestrator/` without source Git history. The snapshot excludes populated `.env` and `.env.uppercut` files, credentials, provider sessions, databases, Compose volumes, caches, logs, runtime artifacts, and local virtual environments. Project Uppercut retains `requirements.lock.txt` as its one declared reproducibility overlay; that file is not part of the upstream tree.

The standalone Director repository is canonical. Orchestration changes originate there and are refreshed here only after review. This PR must remain draft until PR #20 merges, the source commit is updated to its merge commit, both exact heads pass CI, and the Windows operator dry-run succeeds.

<!-- [ Codex | GPT-5 | 2026-08-16 03:40 UTC | END: refreshed Director source provenance ] -->
