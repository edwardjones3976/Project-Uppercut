# Project Uppercut — Canonical Project Notes

**Status:** Authoritative operating brief (preproduction closed 2026-08-02; Phase 1A in progress)  
**Last synchronized:** 2026-08-02 (America/Los_Angeles)  
**Project shape:** **Product — Game / interactive software**  
**Closest genre shape:** **Competitive character-based arcade-boxing simulation**

## What it does and who it is for

> **Project Uppercut is a comedy-first, character-based arcade-boxing game for children, beginners, boxing fans, spectators, and experienced competitive players, using one skill-based combat system to simulate CPU-controlled fights, teach boxing mechanics in focused training modules, and support progressively deeper human competition without weakening advanced play.**

This sentence defines the product and provides the seed for the future objectives section. It is not itself a list of objectives.

## Product identity

Project Uppercut is an original arcade boxing game with exaggerated personalities, dramatic entrances, rivalries, crowd energy, special abilities, tactical humor, and recognizably authentic boxing logic beneath the spectacle.

The game is:

- **comedy-first**, without treating the combat as mechanically meaningless;
- **arcade-readable**, without becoming shallow or random;
- **boxing-informed**, without restricting itself to pure simulation;
- **beginner-teachable**, without protecting beginners through hidden competitive assistance;
- **competitive and skill-based**, without isolating advanced players in a separate combat system;
- **character-driven**, without copying existing fighters, games, likenesses, animations, commentary, branding, or protected intellectual property.

The governing feel statement is:

> **Project Uppercut is arcade boxing with real boxing bones: instantly responsive, visually fast, genuinely funny, competitively fair, and much deeper than it initially appears.**

The production feel priority is fixed:

1. impressively responsive;
2. visually fast;
3. fun and funny;
4. accurate in boxing logic;
5. enjoyable across repeated matches;
6. steady-paced;
7. secretly layered with boxing idioms and advanced Ringcraft.

Responsiveness means inputs, movement, defense, attacks, commitment, and return of control remain consistent and understandable. Visual speed may come from animation, camera, effects, audio, crowd energy, and presentation, but it may not erase readable cause and effect. Fun means immediate excitement, personality, comedy, impact, and memorable moments. Enjoyable means the game remains worth playing across several matches without unfairness, exhaustion, or unexplained failure. Accuracy means boxing-logic accuracy: range, foot position, bodywork, predictability, counters, pressure, recovery, and ring position matter even when the presentation is exaggerated. Steady pacing means fights breathe through observation, engagement, exchange, reset, pressure, punishment, and momentum change rather than permanent chaos.

## First-class operating model

Project Uppercut begins with complete **CPU vs. CPU simulation**. This is both the first development priority and a first-class way to experience the game—not merely a hidden developer test.

A CPU vs. CPU match should eventually support:

- fighter and arena selection;
- referee assignment;
- complete entrances and presentation;
- movement, offense, defense, stamina, injuries, knockdowns, recovery, and stoppages;
- distinct fighter personalities and tactical plans;
- observable adaptation without input reading;
- crowd behavior and commentary;
- official judging behind a score firewall;
- match statistics, replay, and explainable event logs;
- batch simulation for balance testing.

The fixed development order is:

1. CPU vs. CPU simulation foundation
2. Human vs. CPU
3. Human vs. Human
4. Online play only after deterministic local competition is stable
5. Version 1 content, presentation, accessibility, and polish

Career Mode, Story Mode, and every career-related system are deferred to the next version and remain its lowest priority. Version 1 must not depend on them.

## Prototype separation

The first technical sandbox and first character-complete vertical slice are separate milestones.

The generic technical sandbox validates combat states, movement and facing, camera behavior, animation state, collision truth, basic punches, guard and evasion, stamina and condition, knockdowns and recovery, CPU decision-making, deterministic simulation logging, Crowd Bar architecture, and ability architecture.

Counterplay exists from the first punch. Every attack defines startup, active contact, recovery, range, stamina cost, guard interaction, hit reaction, counter vulnerability, and positional consequence before character-specific abilities are added.

After the generic sandbox passes its quality gate, the first character-complete vertical slice uses:

- **Adewale “The Fine Print” Balogun**, testing timing, Ringcraft, range, structure, counters, and pattern recognition;
- **Calvin “The Host” Givens**, testing speed, Combinations, Showmanship, evasive exits, and crowd generation.

This separation allows the project to distinguish shared-system faults from character-specific faults.

## One system for everyone

Project Uppercut uses one underlying combat system for:

- CPU fighters;
- children;
- beginners;
- experienced players;
- competitive players;
- local and future online matches.

There are no separate “First Bell,” “Club Fighter,” beginner, intermediate, or elite combat engines.

> **Beginners receive preparation, not protection.**

Training Mode breaks mechanics into concise, coherent chunks. It may adjust prompts, demonstration, repetition, drill conditions, opponent cooperation, and feedback, but it does not create different physics, damage, scoring, move availability, or competitive rules.

Version 1 develops players through Training Mode, CPU sparring, Human vs. CPU, demonstrations, drills, truthful feedback, replay, and fight analysis. Career Mode and Story Mode may deepen player development in the later version where they belong.

Once a player enters head-to-head or online competition, the complete game is active. Competitive play has no hidden beginner damage reduction, rubber-banding, secret stamina help, score-based comeback assistance, restricted advanced mechanics, or selective input forgiveness that changes outcomes.

Universal remapping, readable feedback, consistent input buffering, and accessibility options remain valid when equally available and competitively truthful.

## Competitive challenge distribution

Online matchmaking should provide a fair spread of challenges rather than permanently isolating players by skill.

Beginners should not be abandoned to endless hopeless fights, and advanced players should not be quarantined into facing only advanced players. Over time, players should encounter easier, comparable, and harder opposition while the combat rules remain unchanged.

Matchmaking and mode design may reduce repeated extreme mismatches and deliberate beginner farming. They may not grant hidden gameplay advantages, alter the unified combat system, or guarantee equal ratings in every match.

Advanced players succeed through knowledge, timing, spacing, mechanical execution, adaptation, stamina management, matchup understanding, and Ringcraft. Beginners are expected to develop those same abilities through the game’s training and CPU systems.

## Roster and fighter structure

The roster is coed. There are no separate male and female divisions and no weight divisions. Balance comes from the authored attribute economy, tactical strengths, weaknesses, abilities, matchup interactions, and visible consequences—not demographic assumptions.

Each complete fighter is intended to have:

- an original identity, visual design, background, personality, entrance, and rivalry network;
- a stated primary stance;
- authored attributes and a distinctive tactical style;
- at least fifteen meaningful traits selected from the project’s training and trait vocabulary;
- two counterable Special abilities;
- one powerful but counterable Ultimate that cannot automatically end a match;
- one distinctive Full-Crowd Trait;
- vulnerabilities that preserve matchup counterplay.

Fighters may share some traits, but duplication should be limited enough for each fighter to remain mechanically and personally distinct. Uniqueness must not depend on obscenity, cultural caricature, intentional ugliness, random weirdness, or confusion.

The attribute system remains centered from -100 to +100, with zero representing balance. Advantages require meaningful costs or disadvantages. No single overall number replaces the fighter’s actual profile.

## Style viability

Project Uppercut must allow polar-opposite styles to win without allowing either extreme to become the only correct strategy.

Two explicit stress cases are required:

- an opening-bell aggressor capable of winning through effective pressure;
- a low-action stamina controller capable of extending the fight and punishing waste.

> **The game punishes reckless aggression, not aggression; empty avoidance, not patience.**

Every major style requires a win condition, risk condition, counterplay, and readable signals. Equal viability does not require every matchup to become exactly 50/50; it requires every style to retain a legitimate route to victory when executed with skill, mechanics, adaptation, and boxing logic.

Aggression may win through pace, volume discipline, ring cutting, bodywork, corner pressure, momentum, and forced mistakes. Its risks come from inaccuracy, repetition, poor spacing, overcommitment, wasted stamina, and failure to reset.

Patient or low-action fighting may win through distance, composure, created misses, counters, bodywork, recovery, rhythm disruption, and ring control. Avoidance alone does not win; it must create observable boxing advantage.

Balance should emerge from reusable universal systems—commitment, contact classification, stamina, guard fatigue, bodywork, ring position, counter windows, repetition recognition, judging evidence, and Crowd rewards—rather than hidden character-specific rescue rules.

Generic CPU stress profiles should include a Rusher, Drainer, Technician, Counterpuncher, Showman, and Power Threat before named roster balance is treated as proven.

> **No style wins because the game favors the style. A style wins because the player or CPU executes its boxing logic better than the opponent solves it.**

## Crowd system

The Crowd Bar rewards expressive and effective boxing, including:

- clean offense;
- defense and evasions;
- counters;
- reversals;
- combinations and variety;
- Ringcraft;
- appropriate Showmanship;
- high-risk success;
- momentum-changing sequences.

At a full Crowd Bar, the fighter chooses between the Ultimate and the Full-Crowd Trait. The same completed bar cannot stack both.

The crowd cannot read or alter official scorecards and cannot provide a generic hidden damage, speed, defense, stamina, judging, or comeback multiplier. Crowd behavior is presentation and an earned character resource—not a secret judge or rubber-band system.

Raw activity, repeated safe actions, and low-risk meter farming are not sufficient Crowd behavior.

## Combat truth

Visible events and authoritative outcomes must agree.

> **Feet establish position; position establishes range; range establishes contact; contact establishes consequence.**

Project Uppercut requires:

- responsive, grounded, threat-aware footwork;
- believable acceleration, deceleration, pivots, and weight transfer;
- no ice skating, magnetic range correction, invisible lunges, or uncontrolled body overlap;
- authoritative strike, guard, and vulnerable-region collision;
- clean, solid, grazed, brushed, blocked, dodged, and whiffed outcomes;
- meaningful stamina, balance, recovery, and counter-exposure consequences;
- replay logs capable of explaining major exchanges.

The Elastic Footwork System is continuous. Safe distance permits longer responsive navigation; threatening range naturally compresses movement into shorter boxing steps. Direction changes remain responsive when balance allows them, but fighters cannot sprint freely through active committed exchanges.

Punch commitment has consequence:

- clean landed punches use the ordinary authored recovery and stamina cost;
- blocked punches create more recovery exposure and Arm Condition damage;
- successfully dodged punches punish commitment more than blocked punches;
- empty-space whiffs create the greatest stamina and counter vulnerability.

Numerical multipliers remain prototype tuning targets and must be validated rather than treated as final implementation facts.

## Damage, defense, and stoppages

Combat condition is not one generic health bar. Relevant systems include:

- head condition;
- body condition;
- jaw vulnerability;
- left-eye and right-eye condition;
- left-arm and right-arm condition;
- guard integrity;
- stamina;
- balance;
- composure;
- Chin;
- Durability;
- Recovery.

Blocking prevents clean contact but does not erase consequence. Repeated intelligent pressure can damage the arms, weaken guard structure, and temporarily open a passive blocker. Repeating one predictable blocked punch does not automatically earn a guard break; varied placement, timing, angles, and stamina matter.

Eye damage is visual, side-specific, and mechanically meaningful. Swelling can reduce accuracy, tracking, side-specific recognition, distance judgment, defensive confidence, counter timing, CPU decision-making, and doctor confidence. It must not reverse controls, manufacture impossible misses, or use extreme blur.

A Chin rating of 100 means maximum authored resistance, not invulnerability. Rare early stoppages remain possible when force, placement, contact quality, movement, balance, awareness, accumulated condition, and failed defense explain them. The game does not use a flat random knockout roll on every punch.

## Stances and controls

Every fighter may switch between orthodox and southpaw.

A non-ambidextrous fighter operating outside the stated stance may lose some accuracy, power transfer, defensive familiarity, combination fluency, stamina efficiency, or recovery quality. The precise penalty is authored per fighter.

A small, exclusive group of ambidextrous fighters has no stance-familiarity penalty in either orientation. Ambidexterity is a tactical advantage, not a best-fighter classification. It does not grant superior universal attributes, cancel bad balance, or remove normal commitment.

Special abilities may use opponent-relative left-stick or D-pad motion commands followed by an explicit Special-button confirmation. Motion recognition should be forgiving but consistent, trainable, remappable, and identical in competitive play. A difficult command never justifies an unavoidable ability.

## Referees

Six serious referees use the same authoritative rules while applying meaningfully different enforcement philosophies across clinches, inside work, fouls, warnings, deductions, injuries, communication, and stoppages.

Referees may influence matchups within reason. They can affect how a fight develops, but should rarely determine the winner without fighter conduct creating the result.

A competitive referee must be:

- disclosed before the fight;
- internally consistent;
- equally applicable to both fighters;
- explainable from observable evidence;
- strategically adaptable;
- subject to the same count, medical, collision, damage, and scoring boundaries.

A referee may not alter punch damage, collision classification, stamina, Crowd gains, fighter attributes, input responsiveness, scorecard criteria, or the authoritative knockdown-count clock.

The six serious officials are:

1. Raymond Whitaker — patient observer
2. Celeste Navarro — stern authority
3. Hana Mori — technical consistency
4. Darius Cole — inside-work tolerance
5. Nkiru Okafor — safety specialist
6. Thomas Baines — communication-centered official

Elliot “Eventually” Ames is a seventh, extremely lax comic-relief botanical referee for non-Ranked modes. His visual and behavioral joke is implied but never canonically identified or directly stated. He may be unusually tolerant of clinching and slow to warn or deduct, but he still obeys the universal medical, incapacitation, serious-foul, and knockdown-count standards.

> **Referees shape the boundaries of the contest without becoming the contest.**

## Score and information boundaries

Official scorecards belong to the Judge subsystem and authoritative Match Controller. Fighters, CPU policies, corners, commentary, crowd systems, difficulty systems, live replay presentation, and referees do not read live cards.

Those systems may estimate who is winning only from observable events and should express uncertainty where appropriate. No score knowledge may drive rubber-banding, CPU decisions, crowd bonuses, advice, commentary certainty, or referee intervention.

## Comedy and tone

Comedy is the highest presentation priority, but it must coexist with competitive trust.

Humor should come from:

- personalities;
- entrances;
- rivalries;
- commentary;
- crowd reactions;
- timing;
- exaggerated but readable abilities;
- consequences;
- arena presentation;
- situational contrast.

Comedy must not require cultural disrespect, demographic stereotypes, protected-property imitation, obscene design, or mechanics that lie to the player.

## Technical and production position

Project Uppercut uses a modular, original, Unreal-first strategy.

The accepted default production baseline is:

- Unreal Engine;
- Blueprints for early prototyping and rapid iteration;
- Python for data generation, validation, simulation analysis, telemetry, balance reports, asset utilities, and automation;
- C++ later for performance-critical, deterministic, networking, or architecture-heavy systems when justified;
- GitHub for version control;
- Blender and properly licensed assets for content production and modification.

C# has no meaningful role unless the project changes to Unity.

Reusable tools and licensed assets may accelerate development. Every asset requires a compatibility audit covering license, modification rights, skeleton, retargeting, root motion, performance, network suitability, visual consistency, engine support, and maintainability.

Project Uppercut’s characters, mechanics, tuning, branding, writing, finished presentation, and project-specific code remain original.

Current repository status: preproduction closed with the Phase 0 quality gate passed on repository
evidence; the validation toolchain (284 tests in CI) and Phase 1A definitions for ROADMAP steps 1–7
(combat states, movement/facing, camera, animation states, collision truth, basic punches, guard and
evasion) are in place; a verified
Unreal Engine 5.8.1 sandbox exists, and deterministic fixed-tick resimulation is validated in-engine
at three levels (docs/phase1a/determinism_probe_results.md). Design documentation is still not
evidence of implemented gameplay, finished assets, or a playable build — no playable boxing match is
claimed.
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 06:12 UTC | edit: status sync only, no identity change ] -->

## Document authority and maintenance

Repository documents serve different purposes:

- **PROJECT_RULES.md:** binding constraints and non-negotiable laws;
- **PROJECT_NOTES.md:** current product identity and operating brief;
- **docs/decisions/:** accepted architectural and production decisions;
- **ROADMAP.md:** fixed development order, deliverables, and quality gates;
- **docs/development-log/:** historical design record and tuning rationale.

When documents conflict, the latest explicit user correction controls and the canonical files must be synchronized promptly. Historical development logs may preserve superseded material only when clearly labeled.

These notes must remain concise enough to orient a new contributor before they read detailed tuning documents. Future objectives should be derived from the product sentence and operating model rather than replacing them.
