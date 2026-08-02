# Decision 0005 — Execution-Plan Authority and Filtered Intake

**Date:** 2026-08-02  
**Status:** Accepted  
**Source:** Latest Project Uppercut submissions recovered from the conversation titled “Career Growth Journey IV,” including review of the draft “Project Uppercut — 90-Day Project Plan”

## Decision

Project Uppercut will not import the draft 90-day plan verbatim. Useful engineering structure may be retained only after it is filtered through the current canonical product ideology.

A time-bound execution plan is subordinate to:

1. the latest explicit Director correction;
2. PROJECT_RULES.md;
3. PROJECT_NOTES.md;
4. accepted decision records;
5. ROADMAP.md;
6. the execution plan;
7. workstream documents and implementation details.

Historical logs preserve rationale but do not override current canonical direction.

The objectives section remains reserved for Director authorship or explicit Director approval. An assistant-generated objective table is a proposal, not project doctrine.

## Accepted planning components

The following ideas from the draft are consistent with Project Uppercut and may inform a future execution plan:

- CPU vs. CPU remains the first functional and playable priority.
- The simulation should be deterministic for a given seed and authoritative starting state.
- Complete bouts should produce explainable event records suitable for replay and analysis.
- Automated tests should protect determinism, state validity, score isolation, and combat rules.
- Batch CPU tournaments and matchup reports should help reveal dominant loops, ineffective systems, and unexplained outcomes.
- A minimal watchable CPU vs. CPU experience may follow the proven simulation foundation.
- Human input remains later than CPU simulation.
- Online, Career, and Story work remain outside the immediate implementation path.
- Evidence gates should control expansion into presentation fidelity, roster growth, and additional modes.
- Early scope should remain small enough to diagnose shared-system faults before expanding content.

These are production structures, not permission to replace the canonical combat or character design.

## Rejected or superseded assumptions

The following draft elements are not accepted and must not enter the repository as current direction:

### Stale repository kickoff

The repository, default branch, canonical notes, README links, project rules, decisions, roadmap, and development logs already exist. Tasks describing them as “to be created” are obsolete.

### “Rumble” meter terminology

Project Uppercut uses the **Crowd Bar**. At Full Crowd, the fighter chooses between the Ultimate and the Full-Crowd Trait; one completed bar cannot activate both. Each complete fighter also has two Specials. Do not collapse these systems into one generic signature move or borrow identity-bearing terminology from another game.

### CPU access to scorecards

CPU decision policy may not read official cards or know that it is “behind on the cards.” CPU fighters, corners, commentary, referees, crowd systems, and difficulty systems use observable fight evidence and uncertain estimates only.

### Rigid four-archetype launch roster

Swarmer, out-boxer, slugger, counterpuncher, Rusher, Drainer, Technician, Showman, and Power Threat labels may serve as generic simulation stress profiles. They are not permanent roster classes or a substitute for original fighter identities.

The technical sandbox uses generic fixtures. The first character-complete vertical slice follows the accepted Adewale “The Fine Print” Balogun and Calvin “The Host” Givens pairing. Any expansion beyond that requires the relevant quality gate.

### Hard universal 35–65 balance band

No fixed matchup band is accepted as a universal pass/fail rule. Polar-opposite styles, referee interpretations, stance interactions, injuries, abilities, and fighter strengths may create intentionally uneven matchups.

Balance testing should identify:

- dominant options without reasonable counterplay;
- styles with no legitimate route to victory;
- unexplained or inconsistent outcome shifts;
- referee influence that overwhelms fighter conduct;
- hidden assistance or information leakage;
- loops that defeat the shared boxing systems.

A numeric band may later be proposed as an alert threshold for a defined test population, but it cannot flatten intentional style differences or substitute for causal analysis.

### Plain TypeScript as the authoritative game core

The accepted default is modular Unreal-first production, using Blueprints for early prototyping, Python for tooling and analysis, and C++ later where architecture or performance requires it.

A TypeScript experiment may not silently become the authoritative combat engine. Any alternate-stack prototype requires an explicit decision explaining how it avoids duplicated rules, divergent simulation behavior, discarded implementation, and a second source of truth.

### Imported agent ownership

The draft assignment of Claude as primary builder and Codex as presentation-only contributor is not canonical. Neither are imported file-ownership rules from another project.

Agent and human responsibilities must be assigned for the actual work in scope and must not conflict with repository state, available tooling, or Director instructions.

### Mandatory contribution tags

Mandatory assistant/model/timestamp start-and-end tags on every file are not an accepted Project Uppercut rule. Git already records authorship and history. Any additional contribution-tagging convention requires separate approval and must avoid polluting source files, generated data, or user-facing content.

### Premature schedules and objectives

The August 3–November 1 quarter, milestone dates, four-fighter objective, zero-touch-week assumptions, 48-hour Director response expectation, and assistant-authored objectives are not approved merely because they appear in a draft plan.

Dates, objectives, workload, ownership, and acceptance thresholds require Director approval after the objectives section is authored.

### Incomplete system scope

A future execution plan cannot reduce the simulation to health, stamina, guard, range, generic archetypes, and one meter. Its architecture must anticipate the accepted systems relevant to the selected milestone, including:

- Elastic Footwork and collision truth;
- clean, blocked, dodged, grazed, brushed, and whiffed contact;
- counter exposure and stamina consequences;
- head, jaw, eye, torso, arm, guard, balance, and recovery conditions;
- stance switching and ambidexterity;
- two Specials, one Ultimate, and one Full-Crowd Trait per complete fighter;
- the Crowd Bar;
- meaningful but fair referee behavior;
- score isolation;
- replay explainability;
- unified Training Mode compatibility;
- comedy-first presentation and original character identity.

Not every system must be finished in the first sandbox, but early data contracts and event models must not make them impossible or require a separate combat engine later.

## Future plan requirements

Any replacement PROJECT_PLAN.md should:

1. begin from the repository’s actual current state;
2. link PROJECT_NOTES.md and PROJECT_RULES.md;
3. preserve CPU-first development and the generic-sandbox/character-slice separation;
4. leave objectives explicitly pending until the Director authors or approves them;
5. use Unreal-first production unless a later accepted decision changes it;
6. describe Crowd, ability, score-isolation, style-viability, and referee boundaries correctly;
7. distinguish generic CPU stress profiles from named roster characters;
8. use measurable quality gates without treating one win-rate range as universal truth;
9. avoid importing Edge Engine governance or agent assignments without approval;
10. state honestly that documentation is not implementation evidence.

## Consequences

- The draft 90-day plan remains an external planning artifact and is not canonical.
- Its accepted engineering ideas are preserved here without importing its stale or conflicting assumptions.
- PROJECT_NOTES.md, PROJECT_RULES.md, Decisions 0001–0004, and ROADMAP.md remain authoritative.
- A future plan may reuse the accepted components in this decision after the Director defines the objectives.
