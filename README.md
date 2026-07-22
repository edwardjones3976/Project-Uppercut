# Project Uppercut

Project Uppercut is the working title for an original, modern arcade-boxing game inspired by the energy and accessibility of classic arcade boxing. It is a **spiritual successor, not a literal clone**: fighters, commentators, arenas, music, artwork, animations, dialogue, interface, and code will be original.

## Current status

**Preproduction / requirements baseline**

The repository currently documents the design decisions recovered from the “Fun Python Coding Ideas” planning conversation. No playable build or completed gameplay implementation is claimed yet.

## Core direction

- Boxing knowledge should operate as game logic, not decorative flavor.
- The first playable target is a two-fighter **Human vs. CPU vertical slice**.
- Combat should be readable, strategic, explainable, and resistant to spam or hidden AI advantages.
- Official judges’ scores remain isolated from fighters, CPU behavior, corners, commentary, crowd behavior, difficulty logic, and live replay presentation.
- Fighter strengths and weaknesses use a centered give-and-take attribute economy.
- Commentary crews scale with fight importance and length while remaining fully original.

## Development order

1. Human vs. CPU MVP
2. Human vs. Human
3. Complete CPU vs. CPU simulation
4. Career mode
5. Online mode
6. Future updates

Every phase must pass a defined quality gate before the next phase begins.

## Documentation

- [Project rules](PROJECT_RULES.md)
- [Roadmap](ROADMAP.md)
- [13-response planning review](docs/development-log/2026-07-21-fun-python-coding-ideas-boxing-review.md)

## Proposed technical foundation

The planning baseline proposes Unreal Engine, Blueprint/C++, Python tooling, GitHub, and Blender. These remain proposed choices until the initial development environment and vertical-slice requirements are validated.

