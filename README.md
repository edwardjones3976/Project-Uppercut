# Project Uppercut

**Project shape:** Product — Game / interactive software  
**Closest genre shape:** Competitive character-based arcade-boxing simulation

> **Project Uppercut is a comedy-first, character-based arcade-boxing game for children, beginners, boxing fans, spectators, and experienced competitive players, using one skill-based combat system to simulate CPU-controlled fights, teach boxing mechanics in focused training modules, and support progressively deeper human competition without weakening advanced play.**

Project Uppercut is the working title for an original modern arcade-boxing game inspired by the energy and accessibility of classic arcade boxing. It is a **spiritual successor, not a literal clone**: fighters, commentators, arenas, music, artwork, animations, dialogue, interface, and code will be original.

> **Project Uppercut is arcade boxing with real boxing bones: instantly responsive, visually fast, genuinely funny, competitively fair, and much deeper than it initially appears.**

## Current status

**Preproduction complete; Unreal sandbox established; Phase 1A combat foundations in progress**

Preproduction closed 2026-08-02 with the Phase 0 quality gate passed on repository evidence
([phase0_status](docs/phase0/phase0_status.md)). The repository carries the canonical operating notes,
binding rules and decisions 0001–0009, the validation toolchain (schemas, contracts, validators,
fixtures, 228 tests in CI), Phase 1A definitions for ROADMAP steps 1–5 — combat states,
movement/facing, camera behavior, animation states, and collision truth
([phase1a_status](docs/phase1a/phase1a_status.md)) — a boxing-canon combat reference
([guard and style matchups](docs/design/boxing_guard_matchups.md)), and a verified Unreal Engine
5.8.1 Blueprint sandbox (`sandbox/UppercutSandbox.uproject`, headless editor check: zero errors, zero
warnings; pinned baseline in [technical_baseline](docs/phase0/technical_baseline.md)). Deterministic
fixed-tick resimulation (Decision 0002) is validated at three levels — engine runtime, Blueprint actor
tick, and the canonical state machine executing in the Blueprint VM — byte-identical across same-seed
processes and seed-sensitive ([evidence](docs/phase1a/determinism_probe_results.md)); the C++ trigger
stays armed for scale, not correctness. **No playable boxing match or completed gameplay
implementation is claimed yet** (Rule 18). Next in the fixed order: ROADMAP step 6 — basic punches.
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 06:12 UTC | edit: status sync ] -->

## Core direction

- The production feel order is: impressively responsive, visually fast, fun and funny, boxing-logic accurate, enjoyable, steady-paced, and secretly layered with boxing idioms.
- Comedy is the highest presentation priority, supported by mechanically truthful boxing.
- The first functional and playable priority is a complete **CPU vs. CPU simulation foundation** using the same combat rules as every other mode.
- Human vs. CPU is the second development priority.
- Project Uppercut uses one unified combat system for children, beginners, experienced players, CPU fighters, and competitive play.
- A modular Training Mode teaches concise mechanics in focused chunks without dividing players into artificial experience tiers.
- Beginners receive preparation through training and CPU play, not hidden protection inside competition.
- Head-to-head and online play use the complete combat system. Online matchmaking should provide a fair spread of easier, comparable, and harder challenges rather than permanently isolating skill groups.
- Combat must be responsive, readable, strategic, explainable, and resistant to spam or hidden CPU advantages.
- Effective aggression, patient stamina control, counterpunching, Ringcraft, power, speed, technique, and Showmanship must all retain fair routes to victory when executed skillfully.
- The roster is coed, has no weight divisions, and is balanced through visible attributes, traits, abilities, strengths, and vulnerabilities.
- Official judges’ scores remain isolated from fighters, CPU behavior, corners, referees, commentary, crowd behavior, difficulty logic, and live replay presentation.
- Fighter strengths and weaknesses use a centered give-and-take attribute economy.
- Referees are fair but meaningful matchup conditions whose tendencies are disclosed and explainable.
- Commentary crews scale with fight importance and length while remaining fully original.

## Development order

1. CPU vs. CPU simulation
2. Human vs. CPU
3. Human vs. Human
4. Online mode after local competitive play is stable
5. Version 1 content, presentation, accessibility, and polish

Career Mode, Story Mode, and all career-related systems are deferred to the next version and are its lowest priority.

Every phase must pass a defined quality gate before the next phase begins.

## Documentation

- [Canonical project notes](PROJECT_NOTES.md)
- [Binding project rules](PROJECT_RULES.md)
- [Roadmap](ROADMAP.md)
- [90-day execution plan](PROJECT_PLAN.md)
- [13-response planning review](docs/development-log/2026-07-21-fun-python-coding-ideas-boxing-review.md)
- [Seven-response combat and production consolidation](docs/development-log/2026-07-26-seven-response-design-consolidation.md)
- [Injury, footwork, controls, stances, and referee consolidation](docs/development-log/2026-07-27-injury-footwork-controls-referees.md)
- [Modular production, game feel, and style-balance consolidation](docs/development-log/2026-08-02-modular-production-game-feel-and-style-balance-consolidation.md)
- [Career Growth Journey IV filtered intake](docs/development-log/2026-08-02-career-growth-journey-iv-filtered-intake.md)
- [Decision 0001 — Simulation first and unified training](docs/decisions/0001-simulation-first-unified-training.md)
- [Decision 0002 — Modular Unreal-first production](docs/decisions/0002-modular-unreal-first-production.md)
- [Decision 0003 — Game feel, development, and matchmaking](docs/decisions/0003-game-feel-training-and-competitive-matchmaking.md)
- [Decision 0004 — Style viability and polarity stress testing](docs/decisions/0004-style-viability-and-polar-opposite-stress-testing.md)
- [Decision 0005 — Execution-plan authority and filtered intake](docs/decisions/0005-execution-plan-authority-and-filtered-intake.md)
- [Decision 0006 — Contribution tagging, schedule and objectives adopted](docs/decisions/0006-contribution-tagging-and-schedule-adoption.md)
- [Decision 0007 — Phase 0 gate rulings](docs/decisions/0007-phase0-gate-rulings.md)
- [Decision 0008 — Team governance](docs/decisions/0008-team-governance.md)
- [Decision 0009 — Director standing authorization](docs/decisions/0009-director-standing-authorization.md)
- [Phase 0 gate status](docs/phase0/phase0_status.md) and [pinned technical baseline](docs/phase0/technical_baseline.md)
- [Phase 1A status](docs/phase1a/phase1a_status.md), [determinism evidence](docs/phase1a/determinism_probe_results.md), and [engine setup runbook](docs/phase1a/engine_setup_runbook.md)
- [Design reference — boxing guard and style matchups](docs/design/boxing_guard_matchups.md)
- [Contribution tagging convention](CONTRIBUTION_TAGGING.md)

## Technical foundation

The accepted default production baseline is Unreal Engine with Blueprints for early prototyping, Python for tools and analysis, C++ for later performance-critical or architecture-heavy systems, GitHub for version control, and Blender plus properly licensed assets for content production. The engine baseline is pinned — Unreal Engine 5.8.1 (CL 56057345), recorded with the rest of the toolchain in [technical_baseline](docs/phase0/technical_baseline.md) — and each remaining choice stays subject to validation in the technical sandbox, with no implementation claimed until repository evidence exists.
