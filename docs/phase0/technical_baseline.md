<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ] -->

# Phase 0 Deliverable — Technical Baseline (awaiting Director confirmation of versions)

Per Decision 0002 and PROJECT_RULES.md Rule 22, the accepted production strategy is modular,
original and Unreal-first. This document is the pinned-versions record the ROADMAP requires. **The
version numbers are blank on purpose** — pinning a version the Director has not installed would be a
claim without evidence (Rule 18).

| Layer | Accepted role | Version | Status |
|---|---|---|---|
| Unreal Engine | Default engine, subject to technical-sandbox validation | *to be pinned* | awaiting confirmation |
| Blueprints | Early prototyping and rapid iteration | (engine) | accepted |
| Python | Design-data generation, validation, simulation analysis, telemetry, balance reports, asset utilities, automation | 3.11+ (tooling built and tested on 3.11) | in use |
| C++ | Later, where performance, determinism, networking or architecture requires it | (engine toolchain) | accepted, not yet triggered |
| C# | No meaningful role unless the engine changes to Unity | — | excluded |
| GitHub | Version control | — | in use |
| Blender | Content production and modification | *to be pinned* | awaiting confirmation |

## Python tooling dependencies

`jsonschema` (draft 2020-12 validation), `referencing` (local \$ref resolution, no network),
`pytest` (suite). Deliberately minimal so CI stays fast and the toolchain stays auditable.

## The determinism question this baseline has to answer

The load-bearing technical question is whether Blueprint tick behaviour can hold **deterministic
resimulation**: the same seed plus the same authoritative initial state reproducing the same
authoritative event log. That is distinct from **replay**, which reproduces recorded presentation from
a saved log without rerunning uncertain CPU or judging decisions. If Blueprints cannot hold
resimulation, Rule 22's C++ trigger fires early for the simulation core — a finding to be evidenced,
not assumed.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ] -->
