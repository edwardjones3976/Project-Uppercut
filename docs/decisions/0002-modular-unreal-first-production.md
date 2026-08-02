# Decision 0002 — Modular, Original, Unreal-First Production

**Date:** 2026-08-02  
**Status:** Accepted  
**Supersedes:** Any plan that assumes Project Uppercut must build ordinary engine, animation, user-interface, audio, or character technology entirely from scratch

## Decision

Project Uppercut will use a modular, original, Unreal-first production strategy.

The project may combine legally licensed general-purpose templates, animation packs, modular characters, user-interface systems, audio libraries, arena assets, and other reusable production components. Reuse is encouraged when it reduces ordinary implementation cost without weakening originality, readability, performance, competitive integrity, or long-term maintainability.

Project Uppercut remains an original intellectual property. Its fighters, commentators, trainers, referees, arenas, rivalries, writing, mechanics, tuning, branding, finished presentation, and project-specific code must remain original and distinguishable from existing games and real people.

## Accepted technical responsibility split

- **Unreal Engine:** accepted default engine and production baseline, subject to technical validation during the first sandbox.
- **Blueprints:** early prototyping, interaction flow, user interface, basic abilities, presentation, and rapid iteration.
- **Python:** design-data generation, validation, simulation analysis, telemetry processing, balance reports, asset utilities, and development automation.
- **C++:** later use for performance-critical, architecture-heavy, networking, deterministic simulation, or reusable core systems when Blueprints are no longer sufficient.
- **C#:** no meaningful role unless the engine changes to Unity.
- **Blender and licensed content:** permitted for original asset creation, modification, retargeting, and production support.

## Prototype separation

The first technical prototype and the first character-complete prototype are separate milestones.

### Technical combat sandbox

Use generic test fighters to validate:

1. combat-state definitions;
2. movement and facing;
3. camera behavior;
4. animation states;
5. hitboxes, hurtboxes, guard regions, and collision truth;
6. basic punches;
7. guard and evasion;
8. stamina, health, knockdowns, and recovery;
9. CPU decision-making using observable information only;
10. deterministic simulation logging;
11. Crowd Bar behavior;
12. Special, Full-Crowd Trait, and Ultimate architecture.

Counterplay is required from the first punch. Every attack must define startup, active contact, recovery, range, stamina cost, guard interaction, hit reaction, counter vulnerability, and positional consequence before character-specific abilities are layered onto it.

### First character-complete vertical slice

After the generic combat sandbox passes its quality gate, the first named vertical slice will use:

- **Adewale “The Fine Print” Balogun**, testing timing, Ringcraft, range, structure, counters, and pattern recognition;
- **Calvin “The Host” Givens**, testing speed, Combinations, Showmanship, evasive exits, and crowd generation.

Each complete fighter architecture must support two Specials, one Ultimate, one Full-Crowd Trait, base boxing traits and attributes, visible vulnerabilities, and a distinct CPU personality.

## Asset compatibility audit

No asset may be selected only because it looks attractive. Each candidate asset must be reviewed for:

- commercial license and modification rights;
- skeleton and rig compatibility;
- retargeting requirements;
- animation completeness;
- root-motion behavior;
- network and deterministic-simulation suitability;
- performance cost;
- visual consistency with the project;
- engine-version support;
- maintainability and replacement risk.

## Balance and production records

Early authoritative records should include:

- move tables;
- fighter cards;
- matchup matrices;
- CPU simulation reports;
- playtest sheets;
- decision logs;
- attribute-budget sheets.

Patch notes become a priority after builds are distributed to testers; they are not a substitute for early design and simulation records.

## Consequences

- Production should assemble ordinary technology where safe and spend original effort on boxing logic, responsiveness, humor, fighters, balance, crowd strategy, CPU behavior, and presentation.
- Marketplace or licensed content does not become canonical merely because it is available.
- Online play remains deferred until deterministic local combat is stable.
- No document may claim an implemented feature, acquired asset, or playable build without repository evidence.
