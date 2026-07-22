# Decision 0001 — Simulation First and One Unified Training System

**Date:** 2026-07-22  
**Status:** Accepted  
**Supersedes:** The earlier Human-vs.-CPU-first roadmap and any proposed named beginner-to-advanced player tiers

## Decision

Project Uppercut will prioritize a complete CPU vs. CPU simulation foundation first. Human vs. CPU becomes the second development priority.

The project will use one unified combat system for beginners, children, experienced players, CPU fighters, and competitive play. It will not divide players into “First Bell,” “Club Fighter,” “Contender,” or similar gameplay systems.

Learning will occur through a dedicated training mode that breaks mechanics into concise, coherent parts. Each module will focus attention and develop skills in manageable chunks while preserving the same underlying mechanics used in ordinary and competitive matches.

Career mode and every career-related system are deferred to the next version and assigned its lowest priority.

## Rationale

- CPU vs. CPU simulation proves combat rules, tactics, judging, balance, and explainability before human inputs complicate diagnosis.
- Human vs. CPU can then reuse a tested simulation rather than defining a second combat path.
- One system gives beginners a genuine route toward advanced and competitive play without artificial classifications or outcome entitlement.
- Modular training reduces cognitive load through instruction and focused practice rather than simplified or incompatible rules.
- Deferring career prevents progression, scheduling, economy, narrative, and long-term state from distracting from the core boxing system.

## Training-mode requirements

Every training module should contain:

1. A concise objective
2. A short explanation
3. A visual or interactive demonstration
4. Focused guided practice
5. A measurable execution condition
6. Immediate and truthful feedback
7. Optional repetition
8. A clear connection to live-fight application

Training may adjust drill conditions, repetition, prompts, opponent cooperation, and presentation. It must not create a separate physics model, damage system, scoring system, move set, or competitive ruleset.

## Consequences

- CPU policies, observable-state boundaries, event logs, simulation determinism, and batch telemetry become immediate engineering priorities.
- The first human-facing work includes Human vs. CPU controls and training modules built on the same simulation contract.
- Career-specific designs, schemas, user interface, progression, economy, records, injuries, scheduling, and narrative work do not enter the Version 1 critical path.
- Documentation or code implying separate beginner combat tiers must be removed or marked superseded.
