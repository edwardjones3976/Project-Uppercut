# Decision 0004 — Style Viability and Polar-Opposite Stress Testing

**Date:** 2026-08-02  
**Status:** Accepted

## Decision

Project Uppercut must allow polar-opposite boxing styles to win without allowing either extreme to become the only correct strategy.

Two explicit stress cases are required:

1. a fighter who begins with pure, effective aggression and can still win;
2. a low-action fighter who extends the contest, controls tempo, creates misses, and drains an opponent’s stamina.

Neither style is automatically punished for existing. Neither style receives automatic success merely for reaching an extreme. Every major style must retain a fair route to victory when matched with skill, mechanical execution, adaptation, and the game’s boxing logic.

> **The game punishes reckless aggression, not aggression; empty avoidance, not patience.**

## Style contract

Every major style must define:

- **win condition:** how skilled execution produces victory;
- **risk condition:** how poor execution creates vulnerability;
- **counterplay:** how the opponent can answer it through shared mechanics;
- **readable signals:** how players, CPUs, spectators, replay, and commentary understand the result.

Equal viability does not require every matchup to become exactly 50/50. It requires every style to have a legitimate, explainable route to victory rather than being invalidated by system preference.

## Aggression

Effective aggression may win through pace, volume discipline, ring cutting, bodywork, corner pressure, momentum, and forced mistakes.

Aggression becomes risky when it is inaccurate, repetitive, poorly spaced, overcommitted, stamina-wasteful, or tactically unresponsive.

Aggressive fighters must not lose extra stamina merely because they are aggressive. Consequence follows observable behavior such as misses, blocked commitment, repeated heavy attacks, poor recovery, and failure to reset.

## Patience and stamina control

Patient or low-action fighting may win through distance, composure, created misses, counters, body attacks, recovery, ring control, and rhythm disruption.

Avoidance alone does not win. It must create measurable advantage through clean defense, counters, position, stamina efficiency, scoring events, or forced mistakes.

Movement should create positional tradeoffs rather than receiving a universal stamina tax. Retreat may gain space while surrendering ring position; lateral movement may create angles while remaining vulnerable to ring cutting and prediction.

## Universal balance mechanics

Style balance should emerge from reusable shared systems rather than hidden character-specific exceptions.

Universal systems include:

- attack startup, active contact, and recovery;
- range and positional consequence;
- stamina cost and regeneration delay;
- clean, blocked, dodged, grazed, and whiffed outcomes;
- repetition recognition;
- guard integrity and guard fatigue;
- bodywork and recovery effects;
- ring position, ropes, and corners;
- counter windows and whiff punishment;
- crowd rewards for effective and varied boxing;
- judging based on observable boxing events behind the score firewall.

Avoid lazy balancing such as automatic aggression penalties, automatic crowd loss for patience, universal weakness assigned to speed or power, or hidden bonuses created only to rescue one named fighter.

## Required generic CPU stress profiles

Before named fighters are treated as balanced, the technical sandbox should support generic CPU profiles including:

1. **Rusher** — immediate pressure, volume, body/head variation, and ring cutting;
2. **Drainer** — low output, evasive movement, created misses, stamina control, and body counters;
3. **Technician** — range, jab structure, balanced defense, and clean scoring;
4. **Counterpuncher** — pattern recognition, whiff punishment, and disciplined waiting;
5. **Showman** — calculated taunts, crowd-oriented risks, and momentum bursts;
6. **Power Threat** — lower volume, high consequence, trap construction, and knockdown danger.

These are simulation instruments, not permanent roster classes or mandatory player labels.

## Polar-opposite acceptance tests

### First Bell Firestorm

The aggressive profile should:

- threaten passive or unprepared opposition;
- create meaningful early-fight victory potential;
- remain vulnerable to disciplined counters, movement, bodywork, and stamina consequences;
- avoid unavoidable stun loops or volume-only dominance.

### The Long Drain

The patient profile should:

- punish reckless pursuit;
- create advantage through misses, counters, bodywork, recovery, and positioning;
- remain vulnerable to effective ring cutting, clean scoring pressure, and purposeful body attacks;
- fail to win merely by refusing interaction.

## Simulation evidence

CPU vs. CPU reports should track enough evidence to explain style outcomes, including:

- aggression and passivity indicators;
- punches thrown, landed, blocked, dodged, grazed, and missed;
- repeated-pattern triggers;
- clean-hit and counter rates;
- stamina expenditure, recovery, and body damage;
- guard fatigue;
- ring-control and corner time;
- knockdowns and stoppages;
- crowd events;
- tactical adaptations;
- decision and stoppage rationale.

## Governing law

> **No style wins because the game favors the style. A style wins because the player or CPU executes its boxing logic better than the opponent solves it.**

## Consequences

- Balance changes should first adjust shared mechanics or transparent authored attributes before introducing fighter-specific exceptions.
- Dominant extremes and ineffective styles become quality-gate failures during CPU simulation.
- Style stress tests must be reusable as fighters, abilities, referees, arenas, and online systems expand.
