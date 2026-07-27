# Project Uppercut

Project Uppercut is the working title for an original, modern arcade-boxing game inspired by the energy and accessibility of classic arcade boxing. It is a **spiritual successor, not a literal clone**: fighters, commentators, arenas, music, artwork, animations, dialogue, interface, and code will be original.

## Current status

**Preproduction / requirements baseline**

The repository currently documents the design decisions recovered from the “Fun Python Coding Ideas” planning conversation. No playable build or completed gameplay implementation is claimed yet.

## Core direction

- Boxing knowledge should operate as game logic, not decorative flavor.
- The first functional priority is a complete **CPU vs. CPU simulation foundation** using the same combat rules as every other mode.
- Human vs. CPU is the second development priority.
- Project Uppercut uses one unified combat system for beginners, children, experienced players, CPU fighters, and competitive play.
- A modular training mode teaches concise mechanics in focused chunks without dividing players into artificial experience tiers.
- Combat should be readable, strategic, explainable, and resistant to spam or hidden AI advantages.
- Official judges’ scores remain isolated from fighters, CPU behavior, corners, commentary, crowd behavior, difficulty logic, and live replay presentation.
- Fighter strengths and weaknesses use a centered give-and-take attribute economy.
- Commentary crews scale with fight importance and length while remaining fully original.

## Development order

1. CPU vs. CPU simulation
2. Human vs. CPU
3. Human vs. Human
4. Online mode after local competitive play is stable
5. Version 1 content, presentation, accessibility, and polish

Career mode and all career-related systems are deferred to the next version and are its lowest priority.

Every phase must pass a defined quality gate before the next phase begins.

## Documentation

- [Project rules](PROJECT_RULES.md)
- [Roadmap](ROADMAP.md)
- [13-response planning review](docs/development-log/2026-07-21-fun-python-coding-ideas-boxing-review.md)
- [Seven-response combat and production consolidation](docs/development-log/2026-07-26-seven-response-design-consolidation.md)
- [Injury, footwork, controls, stances, and referee consolidation](docs/development-log/2026-07-27-injury-footwork-controls-referees.md)
- [Simulation-first and unified-training decision](docs/decisions/0001-simulation-first-unified-training.md)

## Proposed technical foundation

The planning baseline proposes Unreal Engine, Blueprint/C++, Python tooling, GitHub, and Blender. These remain proposed choices until the initial development environment and vertical-slice requirements are validated.
