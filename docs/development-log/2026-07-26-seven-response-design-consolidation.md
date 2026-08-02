# Project Uppercut — Seven-Response Design Consolidation

**Date:** 2026-07-26 (America/Los_Angeles)  
**Status:** Preproduction design record  
**Scope:** A consolidated rendition of seven recent Project Uppercut responses covering production strategy, game-feel priorities, competitive learning, punch outcomes, Arm Condition, contact quality, Chin vulnerability, footwork, and collision truth.

> This document records design direction only. It is not evidence of implemented combat, validated numerical balance, completed assets, tests, or a playable build. Numerical modifiers are prototype tuning targets and remain subject to deterministic simulation, human playtesting, and revision.

## Executive direction

Project Uppercut should be an original, modular arcade-boxing game with real boxing logic underneath its accessible presentation. The project should reuse legally licensed general-purpose technology and assets where appropriate while keeping its characters, mechanics, writing, branding, signature presentation, and code original.

The first functional priority remains CPU vs. CPU simulation. That simulation is the laboratory for footwork, distance, collision, contact quality, stamina, defense, anti-spam behavior, judging isolation, explainability, and fighter balance. Human vs. CPU follows; Human vs. Human follows that; online begins only after deterministic local competition is stable. Career and Story remain deferred to a later version and are not required for Version 1.

The governing feel statement is:

> **Project Uppercut is arcade boxing with real boxing bones: instantly responsive, visually fast, genuinely funny, competitively honest, and much deeper than it initially appears.**

## 1. Modular production without borrowed identity

Project Uppercut should not begin from an empty project merely to prove that ordinary systems can be rebuilt. It should be assembled from modular, replaceable components whose licenses, compatibility, provenance, and performance are known.

Appropriate reusable foundations may include:

- Unreal Engine combat or locomotion templates;
- legally licensed boxing and fighting animations;
- modular character and clothing systems;
- arena-environment assets;
- user-interface frameworks;
- licensed impact, crowd, bell, ambience, and menu audio;
- Blueprint prototypes;
- Python-based validation, telemetry, content, and balancing tools.

Reusable assets provide production acceleration, not creative identity. The following remain original Project Uppercut work:

- fighters and their likenesses;
- names, nicknames, biographies, personalities, and rivalries;
- Specials, Ultimates, and Full-Crowd Traits;
- combat tuning and outcome rules;
- Crowd Bar behavior;
- commentary writing and voices;
- arenas as finished branded locations;
- music and signature audio presentation;
- user-interface identity;
- boxing-lore implementation;
- source code unique to the game.

Every marketplace candidate requires an asset audit covering:

- commercial license and modification rights;
- skeleton and retargeting compatibility;
- root-motion behavior;
- stance and foot-placement quality;
- animation completeness;
- engine-version support;
- visual consistency;
- performance;
- network suitability;
- provenance and replacement risk.

The proposed technical division remains:

- **Blueprints:** early gameplay and presentation prototypes;
- **Python:** content tooling, validators, batch simulation, telemetry analysis, and production automation;
- **C++:** later architecture, determinism, performance-critical systems, and engine integration proven to need it;
- **C#:** no planned role while Unreal remains the engine.

## 2. Prototype order and player-facing priorities

The earliest technical sandbox and the first character-complete vertical slice are separate milestones.

### Technical combat sandbox

Use generic test fighters to validate:

1. authoritative combat states;
2. movement, facing, and camera behavior;
3. animation states and foot planting;
4. hitboxes, hurtboxes, and guard volumes;
5. basic punches;
6. blocking, slipping, rolling, ducking, pivoting, and separation;
7. health, stamina, balance, head/body condition, and knockdowns;
8. CPU decision-making using observable information only;
9. deterministic event logging and replay;
10. contact-quality and outcome classification.

### First character-complete vertical slice

After the generic foundation is explainable, use:

- **Adewale “The Fine Print” Balogun:** Ringcraft, timing, distance, structure, and pattern-based control;
- **Calvin “The Host” Givens:** speed, Combinations, Showmanship, evasive exits, and crowd engagement.

The vertical slice may then add:

- final reference attributes;
- two Specials per fighter;
- one Ultimate per fighter;
- one Full-Crowd Trait per fighter;
- distinct CPU personalities;
- prototype entrances;
- rivalry commentary;
- one original arena.

The Crowd Bar rewards clean, varied, expressive boxing, including offense, defense, counters, reversals, Ringcraft, and appropriate Showmanship. Full Crowd creates a choice between an Ultimate and the fighter’s Full-Crowd Trait; the two cannot be stacked from the same bar. Crowd behavior cannot read or alter official scorecards and cannot provide a generic damage, defense, speed, or comeback multiplier.

## 3. Game-feel hierarchy and competitive learning

The experience hierarchy is:

1. impressively responsive;
2. visually fast;
3. fun and funny;
4. accurate to boxing logic;
5. enjoyable across sustained play;
6. steady-paced rather than chaotic or stalled;
7. secretly layered with boxing knowledge.

These terms have distinct meanings:

- **Responsive:** inputs, transitions, feedback, and recovery feel immediate and dependable.
- **Visually fast:** animation, camera, audio, crowd, and effects create energy without deleting readable reaction windows.
- **Fun and funny:** personality, spectacle, commentary, rivalry, and consequences generate memorable moments without making fighters cultural caricatures.
- **Accurate:** distance, timing, leverage, positioning, stamina, countering, body work, defense, and Ringcraft behave according to recognizable boxing logic.
- **Enjoyable:** players remain willing to continue across multiple matches without unreliable mechanics or manufactured unfairness.
- **Steady-paced:** the fight naturally alternates between engagement, defense, pressure, separation, recovery, and tactical adjustment.
- **Deep:** advanced players discover layered consequences and strategic interactions inside the same system taught to everyone else.

### Preparation without protection

Project Uppercut does not secretly protect beginners inside competition. It prepares them outside competition.

> **The game does not lower the ring for beginners. It teaches them how to climb into it.**

Version 1 preparation comes through:

- modular Training Mode;
- CPU sparring;
- CPU simulation;
- replay lessons;
- fight breakdowns;
- style tutorials;
- matchup education;
- boxing-logic explanations.

Career and Story may expand this educational ecosystem in a later version, but they remain outside the Version 1 critical path.

Competitive play uses the full shared ruleset. It must not include beginner-only damage reduction, hidden comeback boosts, rubber-banding, secret stamina support, altered scoring, restricted advanced mechanics, or input assistance that selectively changes competitive outcomes.

Universal input buffering, remapping, accessibility options, and deterministic control forgiveness remain acceptable when they are visible, consistent, and equally available.

### Matchmaking modes

- **Ranked:** prioritizes rating proximity, connection quality, and meaningful competitive results. Search may widen gradually, but it should not intentionally feed unwilling beginners to elite players.
- **Casual:** retains the complete combat system with broader opponent variety and lower consequences.
- **Open Challenge:** permits unrestricted matchups by mutual choice.
- **Mentorship/Sparring:** permits voluntary instructional matches without creating a ranked farming mechanism.

The supporting pillars are **Preparation Without Protection**, **One Ring, Full Rules**, **Depth Without Isolation**, and **Mastery Without Manipulation**.

## 4. Punch-outcome consequence model

Punch outcomes should penalize unsupported commitment more than meaningful contact. The governing law is:

> **Clean contact preserves structure. Guard contact delays recovery. Active evasion exposes commitment. Empty space produces maximum vulnerability.**

The preliminary outcome targets are:

| Primary result | Counter-exposure target | Total stamina-cost target | Defender consequence |
|---|---:|---:|---|
| Clean landed | 1.0× | 1.0× | Health, stun, balance, or position |
| Blocked | 2.0× | 1.25× | Arm Condition and guard fatigue |
| Dodged | 2.5× | 1.5× | None when completely successful |
| Whiffed | 3.5× | 2.25× | None |

These modifiers must apply to the punch’s authored commitment rather than making every attack identical. A whiffed jab remains safer than a whiffed loaded hook or uppercut.

Every punch pays its normal base stamina cost when thrown. The outcome adds a surcharge:

- clean contact: no surcharge;
- blocked: approximately 25% additional cost;
- dodged: approximately 50% additional cost;
- whiffed: approximately 125% additional cost.

Each punch receives one primary outcome. A dodged punch is not also charged as a whiff. Feints are not whiffs.

Consecutive misses may create additional readable balance and retraction problems, but their penalties must not compound exponentially. Repeated offense remains legal when tactically earned; predictable unsupported repetition becomes easier to counter through shared rules rather than hidden nerfs.

## 5. Arm Condition, guard pressure, and blocking abuse

Blocking prevents clean damage; it does not erase consequence.

> **The attacker sacrifices recovery for striking the guard. The defender sacrifices Arm Condition for absorbing the strike.**

Arm Condition represents:

- arm fatigue;
- shoulder and elbow strain;
- repeated impact;
- guard stability;
- the ability to preserve defensive structure.

One readable meter may contain:

- a bright, recoverable portion representing temporary guard fatigue;
- a dark, slower-recovering portion representing accumulated arm damage.

### Proposed Arm Condition stages

| Condition | Defensive state |
|---|---|
| 100–76% — Fresh | Properly aligned blocks prevent nearly all clean damage |
| 75–41% — Strained | Slower transitions and modest impact leakage |
| 40–1% — Compromised | Greater penetration, displacement, and block stun |
| 0% — Broken | Guard is forced open briefly and cannot immediately return at full strength |

A guard break is a short earned opening, not a prolonged helpless state. Movement, slipping, clinching, framing, or a desperate counter may remain available when physically coherent.

Arm recovery pauses or slows while the defender remains crowded, stationary behind the guard, trapped at the ropes, low on stamina, or under repeated impact. Recovery resumes after earned separation, a pivot, a successful clinch, a counter that forces space, a return to center, safely lowering the guard, or the end of the round.

Guard destruction must require intelligent pressure:

- head/body variation;
- left/right variation;
- angles;
- timing changes;
- power placement;
- guard manipulation;
- combinations;
- Ringcraft;
- sufficient stamina.

Repeating the same blocked attack should become more predictable and counterable, not automatically break the guard. A defender who uses the attacker’s 2.0× blocked-punch exposure can counter or escape; a defender who only holds Block eventually loses Arm Condition.

Blocked punches are not recorded as clean landed punches for judging. Physical consequence and official scoring classification remain separate.

## 6. Contact quality, relative movement, and Chin vulnerability

Contact is a spectrum rather than a binary hit flag.

> **Contact quality determines how much force arrives. Power determines its potential. Target vulnerability determines its consequence.**

### Preliminary contact-quality targets

| Contact quality | Damage target | Counter-exposure target |
|---|---:|---:|
| Clean | 1.0× | 1.0× |
| Solid | 0.8–0.9× | approximately 1.1× |
| Grazed | 0.45–0.65× | approximately 1.5× |
| Brushed | 0.15–0.35× | approximately 2.0× |
| Whiffed | 0× | 3.5× |

Delivered consequence should consider:

- fist velocity;
- punch alignment;
- remaining extension;
- shoulder and hip transfer;
- fighter balance;
- contact location;
- relative movement;
- opponent awareness and bracing;
- Power;
- Chin;
- Durability;
- Recovery;
- Composure;
- accumulated condition.

A punch near maximum extension is usually less leveraged, but it is not automatically harmless. A top-tier puncher may retain enough velocity and snap for marginal contact to remain dangerous, especially against an exhausted, unbraced, poorly moving, or low-Chin target.

### Dodge-direction consequences

- Moving away late may reduce a hit to approximately 0.75–0.9× impact.
- A neutral failed dodge produces the ordinary contact result.
- Moving into the attack may raise impact to approximately 1.2–1.35× while increasing stun, guard displacement, Arm Condition damage, and knockdown vulnerability.

Dodging moves vulnerable areas; it never turns them off.

### Distinct durability concepts

- **Power:** force delivered by the attacker.
- **Chin:** susceptibility to head-impact shock, stunning, and knockdowns.
- **Durability:** resistance to accumulated punishment.
- **Recovery:** ability to stabilize and rise.
- **Composure:** decision quality after being hurt.

A low Chin does not mean universally low health. A fighter may be easier to drop yet recover quickly, or resist accumulated damage while remaining vulnerable to sudden clean head contact. Gender, nationality, visible size, and demographic identity provide no hidden Chin or durability modifier.

Project Uppercut should not use unexplained random critical knockouts. A surprising knockdown or stoppage must be explainable through power, placement, contact quality, movement, stamina, balance, accumulated damage, bracing, and fighter attributes.

## 7. Footwork, range, collision, and replay truth

Inaccurate footwork, slippery positioning, unreliable collision, and animation/gameplay disagreement are negative benchmarks for Project Uppercut. The goal is the opposite:

> **The feet establish position, position establishes range, range establishes contact, and contact establishes consequence. Animation, collision, and visible result must agree.**

### Foot truth

The locomotion model must support planting, weight transfer, pivots around a planted foot, directional stepping, acceleration, deceleration, lateral movement, stance switching, rope/corner positioning, and recovery after overcommitment.

Fighters must not:

- ice-skate;
- rotate without meaningful foot movement;
- snap or magnetically slide toward opponents;
- drift during planted attacks;
- change direction without transferring weight;
- receive hidden lunge distance merely because a target is nearby.

### Range truth

The system must distinguish outside range, maximum extension, proper striking range, crowded range, inside fighting, and clinch range. Lunging or advancing strikes must use explicit, readable movement with corresponding counterplay.

### Collision truth

Damage occurs only when an active strike volume intersects a valid guard or vulnerable region. The classifier must distinguish clean, solid, grazed, brushed, blocked, partially blocked, guard-penetrating, dodged, whiffed, dodged-into, and counter contact.

Meaningful regions should include head, jaw area, upper torso, lower torso, left arm/guard, and right arm/guard. A single general character capsule cannot be the authoritative boxing-contact model.

Fighter bodies must not overlap outside defined crowding, framing, smothering, inside fighting, turning, separation, or clinching states.

### Commitment and defensive truth

Punch recovery depends on type, stance, feet, movement, loading, combination position, contact, and stamina. Blocking is not immunity. Dodging is not invulnerability. Defensive success creates a possible answer; it does not automatically perform one.

### Replay truth

The authoritative event record should make major exchanges reproducible and explainable by preserving:

- fighter position and movement;
- planted foot and stance;
- active strike;
- glove trajectory;
- contacted guard or vulnerable region;
- contact quality;
- relative movement;
- damage and stun result;
- Arm Condition effect;
- stamina cost;
- counter exposure;
- resulting position.

If a visible replay shows a miss, the engine cannot classify a clean hit. If a visible glove connects, the record must explain why it was clean, guarded, or marginal.

### Prototype acceptance standards

The combat foundation should not pass its quality gate until:

- visible misses cause no clean damage;
- visible clean contact is recognized consistently;
- grazes and brushes produce reduced impact;
- blocks contact the correct guard region;
- feet remain grounded during planted actions;
- pivots visibly use a planted foot;
- fighters do not magnetically enter range;
- dodges move vulnerable regions rather than granting immunity;
- movement into punches changes collision consequence;
- bodies do not overlap outside legitimate inside states;
- identical seeded combat states produce consistent results;
- replay classification agrees with live presentation;
- CPU fighters navigate ropes, corners, and inside range without collision failure.

## Consolidated status

| Area | Disposition |
|---|---|
| Modular Unreal-first production | Accepted direction; tool and engine versions still require validation |
| CPU vs. CPU first | Binding development priority |
| One unified combat system | Binding project rule |
| Preparation without protection | Accepted competitive-learning philosophy |
| Career and Story | Deferred beyond Version 1 |
| Crowd Bar | Ultimate-or-Trait resource; no judging access or generic stat boost |
| Punch-outcome multipliers | Prototype tuning targets |
| Arm Condition | Accepted system direction; detailed tuning pending |
| Contact-quality multipliers | Prototype tuning targets |
| Chin, Durability, Recovery, Composure separation | Accepted attribute direction |
| Grounded footwork and collision truth | Mandatory technical quality standard |
| Replay explainability | Mandatory simulation and debugging requirement |

## Immediate documentation consequences

1. Add contact outcome, contact quality, Arm Condition, relative movement, and counter exposure to the canonical observable-event model.
2. Keep outcome classification deterministic and available to CPU, training, commentary, replay, and telemetry through observable events—not hidden opponent inputs or official scores.
3. Create test specifications for foot planting, range, body overlap, guard-region contact, grazing, brushing, dodging into attacks, whiff recovery, Arm Condition depletion/recovery, and replay agreement.
4. Preserve the distinction between accepted design laws and numerical tuning targets.
5. Do not advance from the generic CPU combat sandbox to the character-complete vertical slice until footwork, range, collision, and replay truth satisfy measurable gates.

## Evidence limitation

This document consolidates accepted direction and candidate tuning from design conversation. It does not claim that Unreal systems, combat logic, fighter assets, CPU behavior, telemetry, or tests currently exist.
