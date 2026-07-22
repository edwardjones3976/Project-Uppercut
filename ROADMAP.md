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

## Phase 1 — Human vs. CPU MVP

### Minimum scope

- Two original fighters.
- One original arena.
- Core movement, offense, defense, stamina, guard, balance, composure, head/body condition, knockdowns, recovery, and early stoppages.
- One CPU opponent using observable information only.
- Deterministic Judge subsystem behind the score firewall.
- Authoritative fight clock and 30-second between-round flow.
- Minimal original commentary crew.
- Match result, quick menu, statistics, and replay/event log.

### Required automated checks

- Official-score access-denial tests.
- Accelerated-clock synchronization tests.
- Advice bonus cap and stacking tests.
- Repetition-versus-spam behavior tests.
- Legal/illegal fighter attribute fixtures.
- Knockdown, stoppage, and result-state tests.

### Quality gate

- A complete match can be played from selection through post-fight flow.
- CPU uses no hidden score or input knowledge.
- No known infinite stun, clinch, running, meter, or safe-animation exploit.
- Replay/event log can explain major combat and judging events.

## Phase 2 — Human vs. Human

### Deliverables

- Local Human vs. Human play.
- Symmetric input and simulation rules.
- Dual-consent between-round skip.
- Competitive pause/menu behavior.
- Controller and accessibility validation.

### Quality gate

- Identical rules and timing for both players.
- No player can force the other to skip a break.
- Match results are deterministic from the authoritative event record.

## Phase 3 — Complete CPU vs. CPU simulation

### Deliverables

- Full-match simulation using the same combat rules as playable modes.
- Distinct fighter tendencies and adaptive behavior.
- Batch simulation and telemetry tooling.
- Explainable outcomes tied to attributes, tactics, fatigue, and events.

### Quality gate

- Large simulation batches complete without deadlocks or invalid states.
- Style matchups create varied but explainable outcomes.
- CPU behavior passes score-isolation and anti-input-reading tests.
- Balance reports identify dominant loops and unusable traits.

## Phase 4 — Career mode

Career begins only after CPU vs. CPU simulation is complete enough to support trustworthy opponents, training effects, scheduling, records, injuries, development, and judging histories.

### Quality gate

- Career progression cannot bypass attribute-budget rules.
- Training and coaching changes are explainable and auditable.
- Simulated fights and playable fights share one results contract.

## Phase 5 — Online mode

Online work begins only after local Human vs. Human combat and deterministic match flow are stable.

### Quality gate

- Network authority and rollback/synchronization strategy validated.
- Clock, scoring, break consent, results, and replays remain consistent under latency.
- Disconnect and dispute behavior is defined.

## Phase 6 — Future updates

Potential future work includes expanded fighters, arenas, commentary crews, themed broadcasts, rulesets, career depth, accessibility, and presentation improvements. Future content must obey the same originality, score isolation, anti-spam, timing, and attribute rules.

