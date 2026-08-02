# 2026-08-02 — Modular Production, Game Feel, Player Development, and Style-Balance Consolidation

**Status:** Confirmed planning record  
**Scope:** Consolidates the recent Project Uppercut exchanges and the user’s explicit corrections. Canonical rules and accepted decisions control where wording differs.

## 1. Modular development instead of rebuilding ordinary technology

Project Uppercut should combine legally reusable systems, tools, templates, animation packs, modular character assets, user-interface frameworks, audio libraries, and arena content where doing so improves cost, quality, and schedule.

The game remains an original intellectual property. Ready 2 Rumble and comparable games may inform energy, accessibility, character presentation, and arcade-boxing tone, but protected characters, likenesses, lines, animations, music, user interface, arenas, code, and branding may not be copied.

The accepted production direction is Unreal-first, with Blueprints for early prototyping, Python for tooling and analysis, and C++ introduced later when performance, determinism, networking, or architecture justifies it. C# has no meaningful role unless the project changes to Unity.

Every marketplace or licensed asset requires a compatibility audit covering license, modification rights, skeleton, retargeting, root motion, performance, networking, visual fit, engine support, and maintainability.

## 2. Corrected prototype and mode order

The original generic recommendation incorrectly prioritized player-controlled modes and one Special per fighter.

The confirmed order is:

1. CPU vs. CPU simulation;
2. Human vs. CPU;
3. local Human vs. Human;
4. online after deterministic local combat is stable;
5. Version 1 content and polish.

Career Mode, Story Mode, and career-related systems are deferred to the next version and remain its lowest priority.

The earliest prototype must be separated into:

### Generic technical combat sandbox

- combat states;
- movement and facing;
- camera;
- animation state;
- collision and contact truth;
- basic punches;
- guard and evasion;
- stamina, condition, knockdowns, and recovery;
- CPU decision-making;
- simulation logging;
- Crowd Bar architecture;
- ability architecture.

### First character-complete vertical slice

- Adewale “The Fine Print” Balogun;
- Calvin “The Host” Givens;
- complete attributes and CPU personalities;
- two Specials per fighter;
- one Ultimate per fighter;
- one Full-Crowd Trait per fighter;
- entrances, rivalry presentation, and commentary hooks.

Adewale tests timing, Ringcraft, range, structure, counters, and pattern recognition. Calvin tests speed, Combinations, Showmanship, evasive exits, and crowd generation.

## 3. Counterplay from the first punch

Counterplay cannot be added after a simple punch system is complete. Every attack begins with authored startup, active contact, recovery, range, stamina cost, guard interaction, hit reaction, counter vulnerability, and positional consequence.

The Crowd Bar does not create generic damage, defense, speed, stamina, judging, or comeback bonuses. A completed Crowd Bar creates a strategic choice between the fighter’s Ultimate and Full-Crowd Trait.

Crowd gain should recognize clean offense, combinations, defense, counters, reversals, Ringcraft, Showmanship, variety, and meaningful high-risk success. Raw activity and low-risk meter farming are insufficient.

## 4. Governing game feel

The confirmed feel hierarchy is:

1. impressively responsive;
2. visually fast;
3. fun and funny;
4. accurate in boxing logic;
5. enjoyable across repeated matches;
6. steady-paced;
7. secretly layered with boxing idioms and advanced Ringcraft.

> **Project Uppercut is arcade boxing with real boxing bones: instantly responsive, visually fast, genuinely funny, competitively fair, and much deeper than it initially appears.**

Visual speed must not destroy readable cause and effect. CPU vs. CPU spectators should understand why important exchanges occurred. Accuracy means boxing-logic accuracy: range, foot position, bodywork, predictability, counters, pressure, recovery, and ring position matter even when the presentation is exaggerated.

Fun means immediate excitement, personality, comedy, impact, and memorable moments. Enjoyable means the game remains fair, understandable, and worth playing across several matches.

## 5. Beginners receive preparation, not protection

A prior phrase suggesting that competitive play protects beginners was rejected.

Project Uppercut develops beginners through a thought-provoking, detailed, easy-to-learn, fun-to-use, modern, useful, and reusable training ecosystem. Version 1 relies on Training Mode, CPU sparring, Human vs. CPU, demonstrations, drills, immediate feedback, replay, and fight analysis. Career and Story may deepen this work in the later version where they belong.

Head-to-head and online play use the complete game. There are no hidden beginner damage reductions, rubber-banding, score-driven comeback boosts, secret stamina assistance, restricted advanced mechanics, or selective outcome-changing input forgiveness.

Online matchmaking should not permanently isolate skill groups. Beginners should not receive only hopeless fights, and advanced players should not fight only advanced players. Over time, players should encounter a fair spread of easier, comparable, and harder opposition while the combat rules remain unchanged. Repeated deliberate beginner farming should be discouraged through matchmaking and mode design rather than hidden gameplay assistance.

## 6. Polar-opposite styles and reusable balance

Two explicit polar stress cases were accepted:

- an opening-bell aggressor capable of winning through effective pressure;
- a low-action stamina controller capable of extending the fight and punishing waste.

Neither style should be over-punished, and neither should become the only reliable way to win. All major styles require a win condition, risk condition, counterplay, and readable signals.

The governing distinction is:

- punish reckless aggression, not aggression;
- punish empty avoidance, not patience.

Aggression may win through pace, volume discipline, bodywork, ring cutting, and forced errors. Its risks come from misses, blocked commitment, repetition, poor spacing, and failure to reset.

Patient fighting may win through created misses, counters, bodywork, recovery, distance, rhythm, and ring control. Avoidance alone does not win; it must create observable boxing advantage.

Balance should emerge from universal mechanics rather than hidden character-specific rescue rules. Required reusable systems include commitment, contact classification, stamina, guard fatigue, bodywork, ring position, counter windows, repetition recognition, judging evidence, and Crowd rewards.

Generic CPU stress profiles should include a Rusher, Drainer, Technician, Counterpuncher, Showman, and Power Threat before named roster balance is treated as proven.

> **No style wins because the game favors the style. A style wins because the player or CPU executes its boxing logic better than the opponent solves it.**

## 7. Records and evidence

Early balance and production records should prioritize:

- move tables;
- fighter cards;
- matchup matrices;
- CPU simulation reports;
- playtest sheets;
- decision logs;
- attribute-budget sheets.

Simulation telemetry should explain aggression, passivity, contact results, repetition, counters, stamina, body damage, guard fatigue, ring control, corner time, knockdowns, Crowd events, tactical adaptations, and decision rationale.

No planning statement in this record claims that a playable build, purchased asset, completed model, or validated tuning value already exists.
