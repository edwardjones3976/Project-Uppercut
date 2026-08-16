<!-- [ Codex | GPT-5 | 2026-08-16 03:40 UTC | START: refreshed Director source provenance ] -->

# Director Orchestrator source snapshot

<!-- [ Codex | GPT-5 | 2026-08-16 07:14 UTC | START: post-PR-22 corrective snapshot provenance ] -->

- Canonical repository: `edwardjones3976/director-orchestrator`
- Isolation remediation: [PR #20](https://github.com/edwardjones3976/director-orchestrator/pull/20)
- Live-validation fixes: [PR #22](https://github.com/edwardjones3976/director-orchestrator/pull/22)
- Source commit: `3454e4369857cf9030cbb366d09f7c1b83959871`
- Source tree: `1422c21f52e087e88ffe7d403da932fa1cac8546`
- Transition plan: [director-orchestrator PR #18](https://github.com/edwardjones3976/director-orchestrator/pull/18)
- Project bridge: [Project-Uppercut PR #47](https://github.com/edwardjones3976/Project-Uppercut/pull/47)
- Acceptance tracker: [Project-Uppercut issue #48](https://github.com/edwardjones3976/Project-Uppercut/issues/48)
- Refreshed: 2026-08-16
- Prior snapshot pull request: [Project-Uppercut PR #45](https://github.com/edwardjones3976/Project-Uppercut/pull/45)
- Corrective snapshot: this post-PR-22 pull request

<!-- [ Codex | GPT-5 | 2026-08-16 07:14 UTC | END: post-PR-22 corrective snapshot provenance ] -->

## Creation and exclusions

Every upstream blob at the source tree above was copied under `director-orchestrator/` without source Git history. The snapshot excludes populated `.env` and `.env.uppercut` files, credentials, provider sessions, databases, Compose volumes, caches, logs, runtime artifacts, and local virtual environments. Project Uppercut retains `requirements.lock.txt` as its one declared reproducibility overlay; that file is not part of the upstream tree.

<!-- [ Codex | GPT-5 | 2026-08-16 07:14 UTC | START: corrective snapshot acceptance boundary ] -->

The standalone Director repository is canonical. Orchestration changes originate there and are refreshed here only after they land upstream. This corrective pull request must remain draft until the 46-file comparison and exact-head Linux, Windows, embedded-Director, Compose, and provenance checks pass. The missing formal reviews on merged Director PRs #20 and #22 are historical governance exceptions to record in Issue #48; this snapshot does not represent them as completed reviews.

<!-- [ Codex | GPT-5 | 2026-08-16 07:14 UTC | END: corrective snapshot acceptance boundary ] -->

<!-- [ Codex | GPT-5 | 2026-08-16 03:40 UTC | END: refreshed Director source provenance ] -->
