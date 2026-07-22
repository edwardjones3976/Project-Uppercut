# Project Uppercut Roadmap

## Current state

**Phase 0 — Preproduction and requirements consolidation: in progress**

The 13-response planning review has been consolidated into project rules and an initial development order. No playable build is claimed.

## Phase 0 — Foundation

### Deliverables

- Confirm engine and supported tool versions.
- Establish repository conventions and contribution guidance.
- Define canonical data schemas for fighter attributes, attribute families, boxing lore, observable fight events, commentary profiles, commentator relationships, clock settings, and match results.
- Define the two original vertical-slice fighters without borrowed likenesses.
- Define automated validators before balancing roster content.

### Quality gate

- Originality rules documented.
- Scorecard access boundaries documented and testable.
- One canonical attribute-budget formula chosen.
- Legal and illegal fighter-build fixtures specified.
- Vertical-slice acceptance criteria approved.

## Phase 1 — CPU vs. CPU simulation foundation

This is the first functional priority. It establishes the authoritative combat system before human controls are layered onto it.

### Minimum scope

- Two original reference fighters with contrasting styles.
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

### Quality gate

- Complete CPU vs. CPU matches run from selection through post-fight flow.
- CPU fighters use no hidden score, opponent input, or privileged state knowledge.
- No known infinite stun, clinch, running, meter, or safe-animation exploit.
- Replay/event log can explain major combat and judging events.
- Style matchups create varied but explainable outcomes.
- Balance reports identify dominant loops and ineffective traits.

## Phase 2 — Human vs. CPU and modular training

### Deliverables

- Human controls layered onto the Phase 1 combat system.
- One CPU opponent governed by the same simulation rules proven in Phase 1.
- A dedicated training mode using the same mechanics as live matches.
- Concise training modules for movement, range, jab use, combinations, defense, counters, body work, stamina, ropes, clinches, knockdowns, scoring awareness, and tactical adaptation.
- Demonstration, guided practice, measurable execution checks, immediate feedback, and repeatable drills.
- Minimal original arena and commentary presentation required for a complete playable match.
- Advice reward cap and stacking tests.
- Controller, readability, and accessibility validation.

### Quality gate

- A human can complete training modules and a full Human vs. CPU match.
- Training instruction changes guidance rather than underlying combat rules.
- CPU behavior remains free of score access, input-reading, and hidden advantages.
- Beginner guidance can be disabled without changing fighter capabilities or match rules.
- Advanced mechanics remain available in the unified system.

## Phase 3 — Human vs. Human

### Deliverables

- Local Human vs. Human play.
- Symmetric input and simulation rules.
- Dual-consent between-round skip.
- Competitive pause/menu behavior.
- Controller and accessibility validation for both players.

### Quality gate

- Identical rules and timing for both players.
- No player can force the other to skip a break.
- Match results are deterministic from the authoritative event record.
- No training assistance produces a competitive advantage.

## Phase 4 — Online mode

Online work begins only after local Human vs. Human combat and deterministic match flow are stable.

### Quality gate

- Network authority and rollback/synchronization strategy validated.
- Clock, scoring, break consent, results, and replays remain consistent under latency.
- Disconnect and dispute behavior is defined.

## Phase 5 — Version 1 content and polish

Potential Version 1 work includes expanded fighters, arenas, commentary crews, themed broadcasts, rulesets, accessibility, training modules, performance work, and presentation improvements. All content must obey the same originality, unified-system, score-isolation, anti-spam, timing, and attribute rules.

## Deferred next version — Career mode

Career mode and every career-specific system are deliberately excluded from Version 1. They are assigned to the next version at its lowest priority. Version 1 architecture should remain compatible with future expansion, but current implementation, scheduling, and acceptance gates must not depend on career features.
