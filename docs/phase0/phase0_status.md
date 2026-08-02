<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:57 UTC | START ] -->

# Phase 0 — Deliverable and Gate Status

Traceability from ROADMAP Phase 0 to committed artifacts. Per Rule 18, "complete" here means the
artifact exists; it never means a Director has approved it.

**Canon verified against repository head `ef9299e` on 2026-08-02.**

## Deliverables

| ROADMAP Phase 0 deliverable | Artifact | Status |
|---|---|---|
| Confirm Unreal and tool versions | `docs/phase0/technical_baseline.md` | drafted; **version numbers await Director confirmation** |
| Repository conventions and contribution guidance | `CONTRIBUTING.md`, `CONTRIBUTION_TAGGING.md` | complete |
| Canonical data schemas | `schemas/` (15), `data/` (8 taxonomies and contracts, plus 6 stress profiles, 7 referees, 1 move table) | drafted; attribute vocabulary awaits approval (OQ-5) |
| Define the generic technical sandbox | `docs/phase0/sandbox_acceptance_criteria.md`, `data/moves/generic_sandbox_moves.json` | criteria drafted for approval; 17-move starting table authored |
| Define the Balogun/Givens vertical slice | `docs/phase0/vertical_slice_acceptance_criteria.md` | drafted for approval, separately |
| Automated validators before roster balancing | `tools/uppercut_validate/` (6 modules) | complete — **95 tests passing** |
| Templates | `docs/templates/` (7) | complete |
| Asset compatibility audit | `docs/phase0/asset_compatibility_audit.md` | complete |

## Quality gate

| Gate item | Evidence | Status |
|---|---|---|
| Originality rules documented | Rule 1; `CONTRIBUTING.md` rejection list; audit items 11–13 | met |
| Scorecard access boundaries documented **and testable** | `data/score_isolation_contract.json`, `score_isolation.py`, `tests/test_score_isolation.py` | met — checker proven non-vacuous against a deliberate violation sample |
| One canonical attribute-budget formula chosen | `docs/phase0/attribute_budget_candidates.md` | **DIRECTOR DECISION OUTSTANDING** |
| Legal and illegal fighter-build fixtures specified | `fixtures/fighters/` (3 legal, 13 illegal) | met — every Rule 10 clause fails for its own specific reason |
| Technical sandbox acceptance criteria approved | `docs/phase0/sandbox_acceptance_criteria.md` | **DIRECTOR APPROVAL OUTSTANDING** |
| Character vertical-slice criteria approved separately | `docs/phase0/vertical_slice_acceptance_criteria.md` | **DIRECTOR APPROVAL OUTSTANDING** |
| Game-feel hierarchy and style-viability laws accepted | Rules 19 and 21; `data/stress_profiles/` (all six) | met |

## Rules now enforced by a failing test rather than by code review

| Rule | Enforcement |
|---|---|
| 3 — Score Isolation | sealed-symbol source scan across all nine forbidden consumer categories; event-log leak detection; judge cards sealed by schema |
| 4 — Fair anti-spam | seven-item targeted-abuse list; punishment must come from one of six observable mechanisms; hidden punishment, impossible reaction speed, privileged inputs and score knowledge all rejected; human/CPU symmetry asserted |
| 5 — One unified system | a mode declares which of twelve permitted surfaces it configures; the sixteen prohibited surfaces — physics, damage, scoring, move availability, rubber-banding, hidden tier rules — fail both the validator and the schema |
| 6 — Advice rewards | 3% per-round ceiling, non-stackable, Corner > Commentary > Crowd, never score-driven |
| 8 — Commentary crews | crew-size law parameterised over all ten round/championship combinations |
| 9 — Fight clock | Accelerated Clock ON forces 3:00 display over 1:45 real; OFF permits only 1, 2 or 3 minutes |
| 10 — Attribute economy | every cap, safeguard and compensation rung, with boundary cases proving −30 is not "below −30" |
| 11 — Abilities | an Ultimate declaring an automatic match end fails validation; an ability without counterplay fails validation |
| 12 — Crowd | rewardable-behaviour whitelist; positive gain without risk flagged as farming; one bar cannot activate both Ultimate and Full-Crowd Trait |
| 13 — Contact truth | commitment cost strictly increasing blocked → dodged → whiffed |
| 14 — Condition | all fifteen required regions present; no key named `health` |
| 16 — Referees | seven officials, six mutually distinct enforcement fingerprints, universal minimums binding on every one including the non-Ranked comic-relief official |
| 18 — Evidence honesty | every authored frame and cost value carries `tuning_status: hypothesis` |
| 21 — Style viability | all six stress profiles present with win condition, risk condition, counterplay and readable signals; First Bell Firestorm and Long Drain both bound |
| 22 — Counterplay from the first punch | every move in the generic table defines all nine commitment columns |

## What does not exist yet

No Unreal project, no simulation code, no playable build, no in-engine test. The source-side score
isolation scan has no real tree to police; it is provisioned and proven against samples. The move
table is a *starting* table — no value in it has been validated by play or batch simulation.

## Reproduce

```
python3 -m pytest -q                        # 95 tests
python3 -m tools.uppercut_validate.cli all  # fixtures, isolation, contracts, data laws, budget
```

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:57 UTC | END ] -->
