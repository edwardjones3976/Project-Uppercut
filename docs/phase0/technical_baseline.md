<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ] -->

# Phase 0 Deliverable — Technical Baseline

> **Version-pinning procedure ruled in [Decision 0007](../decisions/0007-phase0-gate-rulings.md)
> (D-7), 2026-08-02.** The version fields below stay open deliberately. They are filled from the
> **actual installed build** at first engine setup and recorded in the same commit that creates the
> Unreal project. Until then, no tooling, CI job or document may assume a version. Naming a version
> nobody runs would be exactly the unevidenced claim Rule 18 prohibits.

Per Decision 0002 and PROJECT_RULES.md Rule 22, the accepted production strategy is modular,
original and Unreal-first. This document is the pinned-versions record the ROADMAP requires. **Unfilled
version fields stay blank on purpose** — pinning a version the Director has not installed would be a
claim without evidence (Rule 18). The Unreal Engine and launcher fields were filled 2026-08-02 from the
actual installed build; evidence below.

| Layer | Accepted role | Version | Status |
|---|---|---|---|
| Unreal Engine | Default engine, subject to technical-sandbox validation | **5.8.1** (CL 56057345, `++UE5+Release-5.8`) | **pinned from installed build** 2026-08-02 |
| Epic Games Launcher | Engine distribution and updates | **20.1.7-0+UE5** | installed 2026-08-02 |
| Blueprints | Early prototyping and rapid iteration | (engine) | accepted |
| Python | Design-data generation, validation, simulation analysis, telemetry, balance reports, asset utilities, automation | 3.11 (CI) / 3.14.5 (Windows host); suite green on both 2026-08-02 | in use |
| C++ | Later, where performance, determinism, networking or architecture requires it | (engine toolchain) | accepted, not yet triggered |
| C# | No meaningful role unless the engine changes to Unity | — | excluded |
| GitHub | Version control | — | in use |
| Blender | Content production and modification | *pinned at first install* | procedure ruled (D-7) |

## D-7 evidence — first engine install (2026-08-02)

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 23:10 UTC | edit: D-7 engine stamp ] -->

Read from the machine, not assumed (Rule 18):

- `C:\Program Files\Epic Games\UE_5.8\Engine\Build\Build.version` → **5.8.1**, Changelist **56057345**,
  branch `++UE5+Release-5.8`, promoted build.
- `UnrealEditor.exe` version resource → `++UE5+Release-5.8-CL-56057345`.
- Epic Games Launcher (Portal binary) → `20.1.7-0+UE5`.
- Install size on disk ≈ 29.9 GB; 694 GB free.

D-7's letter couples the stamp to the commit that creates the Unreal project.
`sandbox/UppercutSandbox.uproject` — Blueprint-first, built from the engine's own TP_Blank template
per its TemplateDefs.ini rules — ships in the same commit as this paragraph, created under the
Decision 0009 standing authorization and verified by a headless editor run: ResavePackages
commandlet, result 0, `Success - 0 error(s), 0 warning(s)` (2026-08-02 23:23 UTC). **The D-7
procedure is complete for the engine.** Blender remains unpinned until its own install.

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
