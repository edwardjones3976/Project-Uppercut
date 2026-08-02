# Project Uppercut

**Project shape:** Product — Game / interactive software  
**Closest genre shape:** Competitive character-based arcade-boxing simulation

> **Project Uppercut is a comedy-first, character-based arcade-boxing game for children, beginners, boxing fans, spectators, and experienced competitive players, using one skill-based combat system to simulate CPU-controlled fights, teach boxing mechanics in focused training modules, and support progressively deeper human competition without weakening advanced play.**

Project Uppercut is the working title for an original modern arcade-boxing game inspired by the energy and accessibility of classic arcade boxing. It is a **spiritual successor, not a literal clone**: fighters, commentators, arenas, music, artwork, animations, dialogue, interface, and code will be original.

## Current status

**Preproduction / requirements baseline**

The repository currently documents the project’s canonical operating notes, binding rules, accepted decisions, roadmap, and recovered design history. No playable build or completed gameplay implementation is claimed yet.

## Core direction

- Comedy is the highest presentation priority, supported by mechanically truthful boxing.
- The first functional and playable priority is a complete **CPU vs. CPU simulation foundation** using the same combat rules as every other mode.
- Human vs. CPU is the second development priority.
- Project Uppercut uses one unified combat system for children, beginners, experienced players, CPU fighters, and competitive play.
- A modular Training Mode teaches concise mechanics in focused chunks without dividing players into artificial experience tiers.
- Competitive play provides preparation without hidden beginner protection or weakened advanced mechanics.
- Combat must be responsive, readable, strategic, explainable, and resistant to spam or hidden CPU advantages.
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
- [13-response planning review](docs/development-log/2026-07-21-fun-python-coding-ideas-boxing-review.md)
- [Seven-response combat and production consolidation](docs/development-log/2026-07-26-seven-response-design-consolidation.md)
- [Injury, footwork, controls, stances, and referee consolidation](docs/development-log/2026-07-27-injury-footwork-controls-referees.md)
- [Simulation-first and unified-training decision](docs/decisions/0001-simulation-first-unified-training.md)

## Proposed technical foundation

The planning baseline proposes Unreal Engine, Blueprint/C++, Python tooling, GitHub, and Blender. These remain proposed choices until the initial development environment and vertical-slice requirements are validated.
