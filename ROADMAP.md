# Project Uppercut Roadmap

## Current state

**Phase 0 — Preproduction and requirements consolidation: in progress**

The project’s confirmed planning exchanges have been consolidated into canonical notes, binding rules, accepted decisions, and the fixed development order. No playable build is claimed.

## Phase 0 — Foundation

### Deliverables

- Confirm Unreal Engine and supported tool versions as the default technical baseline.
- Establish repository conventions and contribution guidance.
- Define canonical data schemas for fighter attributes, attribute families, boxing lore, observable fight events, commentary profiles, commentator relationships, clock settings, match results, CPU decision reasons, and style stress profiles.
- Define the generic technical sandbox before character-specific abilities.
- Define Adewale “The Fine Print” Balogun and Calvin “The Host” Givens as the first character-complete vertical slice without borrowed likenesses.
- Define automated validators before balancing roster content.
- Create move-table, fighter-card, matchup-matrix, simulation-report, playtest, decision-log, and attribute-budget templates.
- Establish the asset compatibility audit for license, modification rights, skeleton, retargeting, root motion, performance, network suitability, visual consistency, engine support, and maintainability.

### Quality gate

- Originality rules documented.
- Scorecard access boundaries documented and testable.
- One canonical attribute-budget formula chosen.
- Legal and illegal fighter-build fixtures specified.
- Technical sandbox acceptance criteria approved.
- Character vertical-slice acceptance criteria approved separately.
- Game-feel hierarchy and style-viability laws accepted.

## Phase 1A — Generic CPU vs. CPU combat sandbox

This is the first functional priority. It establishes the authoritative combat system using generic test fighters before named fighter abilities complicate diagnosis.

### Required implementation order

1. combat-state definitions;
2. movement and facing;
3. camera behavior;
4. animation states;
5. hitboxes, hurtboxes, guard regions, and collision truth;
6. basic punches;
7. guard and evasion;
8. stamina, health, body/head condition, knockdowns, and recovery;
9. CPU decision-making using observable information only;
10. deterministic simulation logging and replay evidence;
11. Crowd Bar architecture;
12. Special, Full-Crowd Trait, and Ultimate architecture.

Counterplay is required from the first punch. Every attack must define startup, active contact, recovery, range, stamina cost, guard interaction, hit reaction, counter vulnerability, and positional consequence.

### Generic CPU stress profiles

The sandbox should support reusable profiles for:

- Rusher;
- Drainer;
- Technician;
- Counterpuncher;
- Showman;
- Power Threat.

These are balance instruments, not permanent roster classes.

### Minimum scope

- Core movement, offense, defense, stamina, guard, balance, composure, head/body condition, knockdowns, recovery, and early stoppages.
- Two CPU fighters using observable information only.
- Distinct tendencies, tactical plans, pattern recognition, and adaptation.
- Deterministic Judge subsystem behind the score firewall.
- Authoritative fight clock and 30-second between-round flow.
- Match result, quick menu, statistics, and replay/event log.
- Batch simulation and telemetry tooling.
- Explainable outcomes tied to attributes, tactics, fatigue, positioning, and recorded events.

### Required automated checks

- Official-score access-denial tests.
- Accelerated-clock synchronization tests.
- Repetition-versus-spam behavior tests.
- Legal/illegal fighter attribute fixtures.
- Knockdown, stoppage, and result-state tests.
- Determinism and seeded-replay tests.
- Large-batch invalid-state and deadlock tests.
- First Bell Firestorm aggression tests.
- Long Drain patience/stamina-control tests.
- Style viability and dominant-loop tests.
- Crowd farming and generic-boost prohibition tests.

### Quality gate

- Complete CPU vs. CPU matches run from selection through post-fight flow.
- CPU fighters use no hidden score, opponent input, or privileged state knowledge.
- No known infinite stun, clinch, running, meter, or safe-animation exploit.
- Replay/event log can explain major combat and judging events.
- Visual speed remains readable enough for spectators to understand decisive exchanges.
- Effective aggression can win without volume-only dominance.
- Patient stamina control can win without empty avoidance or refusal to interact.
- Technician, Counterpuncher, Showman, and Power Threat profiles retain legitimate routes to victory.
- Balance reports identify dominant loops and ineffective traits.

## Phase 1B — Adewale vs. Calvin character vertical slice

After the generic sandbox passes its quality gate, implement the first character-complete pairing.

### Adewale “The Fine Print” Balogun

Validate:

- timing;
- Ringcraft;
- range structure;
- counters;
- pattern recognition;
- disciplined pressure and adaptation.

### Calvin “The Host” Givens

Validate:

- speed;
- Combinations;
- Showmanship;
- evasive exits;
- crowd generation;
- rhythm disruption.

### Complete fighter scope

Each fighter includes:

- complete authored attributes and traits;
- primary stance and stance familiarity;
- distinct CPU personality;
- two counterable Specials;
- one counterable Ultimate;
- one Full-Crowd Trait;
- entrances, rivalry hooks, and commentary support;
- visible strengths, liabilities, and matchup counterplay.

### Quality gate

- Both fighters remain distinct without requiring different underlying combat rules.
- Character-specific behavior does not conceal generic system faults.
- One full Crowd Bar creates a choice between Ultimate and Full-Crowd Trait rather than both.
- Neither fighter creates unavoidable ability sequences, hidden stat boosts, or automatic match endings.
- CPU simulation reports explain the pair’s tactical differences and recurring failure modes.

## Phase 2 — Human vs. CPU and modular training

### Deliverables

- Human controls layered onto the Phase 1 combat system.
- One CPU opponent governed by the same simulation rules proven in Phase 1.
- A dedicated training mode using the same mechanics as live matches.
- Concise training modules for movement, range, jab use, combinations, defense, counters, body work, stamina, ropes, clinches, knockdowns, scoring awareness, tactical adaptation, style recognition, and matchup problem-solving.
- Demonstration, guided practice, measurable execution checks, immediate feedback, repeatable drills, replay, and fight analysis.
- Minimal original arena and commentary presentation required for a complete playable match.
- Advice reward cap and stacking tests.
- Controller, readability, and accessibility validation.

### Quality gate

- A human can complete training modules and a full Human vs. CPU match.
- Training instruction changes guidance rather than underlying combat rules.
- CPU behavior remains free of score access, input-reading, and hidden advantages.
- Guidance can be disabled without changing fighter capabilities or match rules.
- Advanced mechanics remain available in the unified system.
- A loss is explainable through observable timing, spacing, stamina, matchup, and decision errors rather than hidden protection or assistance.

## Phase 3 — Human vs. Human

### Deliverables

- Local Human vs. Human play.
- Symmetric input and simulation rules.
- Dual-consent between-round skip.
- Competitive pause/menu behavior.
- Controller and accessibility validation for both players.
- Style-polarity and beginner-versus-advanced playtests without hidden handicaps.

### Quality gate

- Identical rules and timing for both players.
- No player can force the other to skip a break.
- Match results are deterministic from the authoritative event record.
- No training assistance produces a competitive advantage.
- Advanced knowledge wins through timing, mechanics, adaptation, and boxing logic rather than exclusive rules.
- Uneven skill matches remain understandable and mechanically truthful.

## Phase 4 — Online mode

Online work begins only after local Human vs. Human combat and deterministic match flow are stable.

### Deliverables

- Network authority and rollback/synchronization strategy.
- Ranked, casual, event, open-challenge, and future tournament matchmaking requirements.
- Matchmaking that provides a fair spread of easier, comparable, and harder opposition over time without permanently isolating skill groups.
- Systems that reduce repeated extreme mismatches and deliberate beginner farming without changing combat rules or manufacturing outcomes.
- Disconnect, rematch, dispute, replay, and reporting behavior.

### Quality gate

- Clock, scoring, break consent, results, and replays remain consistent under latency.
- Combat rules remain identical across skill levels and online modes.
- Beginners receive no hidden protection, and advanced players are not quarantined into only elite matches.
- Matchmaking variety does not become a license for repeated predatory mismatches.
- Disconnect and dispute behavior is defined and auditable.

## Phase 5 — Version 1 content and polish

Potential Version 1 work includes expanded fighters, arenas, commentary crews, themed broadcasts, rulesets, accessibility, training modules, performance work, and presentation improvements. All content must obey the same originality, unified-system, score-isolation, anti-spam, game-feel, timing, style-viability, and attribute rules.

The production feel order remains:

1. impressively responsive;
2. visually fast;
3. fun and funny;
4. boxing-logic accurate;
5. enjoyable;
6. steady-paced;
7. secretly layered with boxing idioms.

## Deferred next version — Career and Story

Career Mode, Story Mode, and every career-specific system are deliberately excluded from Version 1. They are assigned to the next version at its lowest priority.

They may later deepen beginner and general player development through narrative context, repeated application, CPU opposition, consequences, progression, and fight analysis, but they must use the same unified combat system and may not become hidden competitive protection.

Version 1 architecture should remain compatible with future expansion, but current implementation, scheduling, and acceptance gates must not depend on career or story features.
