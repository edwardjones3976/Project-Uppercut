<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 20:47 UTC | START ] -->

# Phase 0 — Deliverable and Gate Status

Traceability from ROADMAP Phase 0 to committed artifacts. Per Rule 18, "complete" means the artifact
exists; "ruled" means a decision record exists; **neither means the gate is closed.**

**Canon merged into `main` at `9e5b4c7` (2026-08-02); canon side previously verified at `ef9299e`.**
**Git:** local `main` and `origin/main` both at **`9e5b4c7`** — pushed and verified 2026-08-02.

## Gate status: PASSED — 2026-08-02, on repository evidence

All seven gate items are answered and the Rule 18 evidence requirement is now met. The foundation was
merged with the canonical history (`8c5861d` + `ef9299e` → merge `9e5b4c7`, zero conflicts, disjoint
paths) and pushed; `git ls-remote` confirms `origin/main` at
`9e5b4c791330ca730fcd6cfd30c2a2e697229769`, identical to local HEAD. GitHub Actions run
**validate #1** on `9e5b4c7` completed successfully (13s) — the 100-test suite and rule validators ran
green in CI. That first green run is also the "validators running in Actions" evidence toward T0.4.

| Gate item | Evidence | Status |
|---|---|---|
| Originality rules documented | Rule 1; `CONTRIBUTING.md` rejection list; audit items 11–13 | met |
| Scorecard access boundaries documented and testable | `data/score_isolation_contract.json`, `score_isolation.py`, `tests/test_score_isolation.py` | met — checker proven non-vacuous |
| One canonical attribute-budget formula chosen | `data/attribute_budget.json`; Decision 0007 D-1 | ruled — in repository at `9e5b4c7` |
| Legal and illegal fighter-build fixtures specified | `fixtures/fighters/` (4 legal, 14 illegal) | met |
| Technical sandbox acceptance criteria approved | `docs/phase0/sandbox_acceptance_criteria.md`; Decision 0007 D-2 | ruled — in repository at `9e5b4c7` |
| Character vertical-slice criteria approved separately | `docs/phase0/vertical_slice_acceptance_criteria.md`; Decision 0007 D-3 | ruled — in repository at `9e5b4c7` |
| Game-feel and style-viability laws accepted | Rules 19 and 21; `data/stress_profiles/` (all six) | met |

## Deliverables

| ROADMAP Phase 0 deliverable | Artifact | Status |
|---|---|---|
| Confirm Unreal and tool versions | `docs/phase0/technical_baseline.md` | procedure ruled (D-7); build numbers filled at first engine install |
| Repository conventions and contribution guidance | `CONTRIBUTING.md`, `CONTRIBUTION_TAGGING.md` | complete |
| Canonical data schemas | `schemas/` (15), `data/` (9 top-level contracts + 6 stress profiles + 7 referees + 1 move table) | complete; taxonomy canonical per D-4 |
| Define the generic technical sandbox | acceptance criteria + `data/moves/generic_sandbox_moves.json` (17 moves) | complete |
| Define the Balogun/Givens vertical slice | `docs/phase0/vertical_slice_acceptance_criteria.md` | complete (bar only; identity stays Director-owned) |
| Automated validators before roster balancing | `tools/uppercut_validate/` (6 modules) | complete — **100 tests passing** |
| Templates | `docs/templates/` (7) | complete |
| Asset compatibility audit | `docs/phase0/asset_compatibility_audit.md` | complete |

## Decisions of record

| Decision | Covers |
|---|---|
| 0006 | Contribution tagging, schedule and objectives adopted; supersedes two sections of 0005 |
| 0007 | Phase 0 gate rulings D-1 to D-7, D-9, D-10 — budget formula, both acceptance-criteria sets, taxonomy, all eight open questions, version-pin procedure, referee depth |
| 0008 | Team governance — Director final authority, explicit per-task assignment, no default file ownership |

Decisions 0007 and 0008 were made under explicit Director delegation. Each ruling is one configuration
line or one data file from being reversed.

## Rules enforced by a failing test rather than by code review

3 (score isolation, all nine consumer categories), 4 (anti-spam mechanisms and symmetry), 5 (mode
configuration whitelist — sixteen prohibited surfaces), 6 (advice ceiling, non-stackable, reliability
order), 8 (crew size across all ten combinations), 9 (clock semantics), 10 (every cap, safeguard,
compensation rung, **and now the budget cap**), 11 (no auto-win Ultimate, no ability without
counterplay), 12 (Crowd whitelist, farming detection, exclusive full-bar choice), 13 (commitment
ordering), 14 (fifteen condition regions, no single health bar), 16 (seven officials, six distinct
philosophies, universal minimums), 18 (every authored number carries `tuning_status: hypothesis`),
21 (six stress profiles with win/risk/counterplay/signals), 22 (nine commitment columns per move).

## What does not exist yet

No Unreal project, no simulation code, no playable build, no in-engine test. The source-side score
isolation scan has no real tree to police — provisioned and proven against samples. The move table and
the budget cap are starting values, not validated ones.

## Reproduce

```
python3 -m pytest -q                        # 100 tests
python3 -m tools.uppercut_validate.cli all  # fixtures, isolation, contracts, data laws, budget
```

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 20:47 UTC | END ] -->
