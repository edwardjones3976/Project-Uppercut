# Project Uppercut — Binding Project Rules

These rules consolidate the decisions accepted during Project Uppercut planning. Later explicit corrections supersede earlier suggestions. The [Canonical Project Notes](PROJECT_NOTES.md) define the current product identity and operating model; contributors must read them before proposing implementation, content, objectives, or roadmap changes.

## 0. Product definition

**Project shape:** Product — Game / interactive software  
**Closest genre shape:** Competitive character-based arcade-boxing simulation

> **Project Uppercut is a comedy-first, character-based arcade-boxing game for children, beginners, boxing fans, spectators, and experienced competitive players, using one skill-based combat system to simulate CPU-controlled fights, teach boxing mechanics in focused training modules, and support progressively deeper human competition without weakening advanced play.**

The project is not merely a career game, a beginner boxing tutorial, a pure simulation, or a conventional one-health-bar fighting game. CPU vs. CPU simulation, character expression, authentic boxing consequence, comedy, training, and competitive depth are all parts of the product identity.

## 1. Originality

Project Uppercut is an original spiritual successor, not a remake or literal clone. Do not copy protected characters, names, likenesses, voice performances, music, arenas, artwork, animations, user-interface presentation, announcer lines, story material, or source code.

Every fighter, commentator, trainer, referee, arena, asset, line, mechanic presentation, and brand element must have original provenance and remain distinguishable from real people and existing games.

Legally licensed general-purpose tools and assets may accelerate production, but Project Uppercut’s finished identities, mechanics, tuning, writing, branding, presentation, and project-specific code remain original.

## 2. Boxing knowledge is functional

Boxing idioms and principles must connect observable fight events to mechanics, CPU strategy, corner advice, commentary, judging interpretation, training, and post-fight analysis.

Lore must be stored as canonical data-driven rules. Multiple sayings may reference one canonical tactical principle; presentation text must not duplicate the underlying combat rule.

## 3. Score Isolation Principle

Official scorecards are private to the Judge subsystem and authoritative Match Controller.

During the fight and immediate post-fight flow, official cards must not be readable by:

- human-facing fighter logic;
- CPU fighter logic;
- referees;
- trainers or corners;
- commentary;
- crowd systems;
- difficulty or adaptive systems;
- live replay presentation;
- advice or bonus systems.

These systems may form imperfect estimates only from observable events, with explicit confidence and uncertainty. Early stoppages terminate scoring. Partial cards remain sealed during the immediate result, quick-menu, and statistics flow, with an optional later archival reveal.

No rubber-banding, referee intervention, commentary certainty, CPU decision, advice, Crowd reward, or difficulty adjustment may use official scores.

## 4. Fair anti-spam behavior

Legitimate repetition remains valid when tactically earned and unanswered. Repetitive low-skill or exploitative behavior must become readable, tiring, positionally costly, and counterable through shared boxing logic.

The same recognition and consequence rules apply to human and CPU-controlled fighters. Do not use hidden punishment, impossible reaction speed, privileged inputs, or official-score knowledge.

Targeted abuse includes one-move loops, safe-animation abuse, stun loops, clinch abuse, excessive running, passive blocking abuse, and meter farming.

A predictable action becomes punishable because of observable pattern recognition, stamina, position, commitment, defense, and counterplay—not because the game secretly decides that repetition is prohibited.

## 5. One unified system and modular training

Project Uppercut uses one combat system for every player and mode. Do not create separate beginner, child, intermediate, advanced, or competitive combat engines, progression ladders, or named experience-tier systems.

Beginners and children learn through a dedicated Training Mode that breaks mechanics into concise, coherent, focused chunks.

> **Beginners receive preparation, not protection.**

Training changes instruction, presentation, repetition, and practice conditions—not the underlying rules of boxing or combat.

Training modules should:

- focus on one mechanic or closely related skill group at a time;
- explain the objective concisely;
- demonstrate the mechanic;
- provide guided practice;
- measure successful execution;
- offer immediate, truthful feedback;
- allow repetition without record penalties;
- connect the skill to real match situations;
- support optional review without manufacturing competitive success.

Advanced techniques exist in the unified system rather than being artificially unlocked by experience points. Competitive achievement must be earned through demonstrated skill, decision-making, timing, adaptation, and execution.

Head-to-head and future online competition must not include hidden beginner damage reduction, score-driven comeback boosts, rubber-banding, secret stamina assistance, restricted advanced mechanics, or selective input forgiveness that changes outcomes. Universal accessibility and input-consistency features are valid when equally available and competitively truthful.

## 6. Advice rewards

Bonuses for successfully following valid corner, commentary, or crowd advice must remain small, bounded, non-stackable, and resistant to farming.

Reliability order:

1. Corner
2. Commentary
3. Crowd

Ring Awareness, Coachability, and Corner Chemistry may influence eligibility. Direct combat benefit must not exceed approximately 2%–3% per round and must never use official-score information.

## 7. Development and mode order

The phase order is fixed:

1. Complete CPU vs. CPU simulation foundation
2. Human vs. CPU
3. Human vs. Human
4. Online mode after local competitive play is stable
5. Version 1 content, presentation, accessibility, and polish

CPU vs. CPU is both the first engineering laboratory and a first-class game experience. It must support complete matches and eventually include selection, presentation, referee enforcement, judging, results, statistics, replay, explainable event logs, and batch telemetry.

Each phase requires measurable exit criteria and a passed quality gate.

Career Mode, Story Mode, and all career-related systems are excluded from Version 1. They belong to the next version and remain its lowest priority. Current work must not depend on career progression, scheduling, economy, narrative, or long-term career state.

## 8. Commentary crews

- Four- and six-round fights use one commentator.
- Eight- and ten-round fights use two commentators.
- Twelve-round fights use three commentators.
- Championship fights always use three commentators, even when scheduled for fewer than twelve rounds.
- Any original commentator may work with any other; chemistry affects presentation but does not create hard identity-based restrictions.
- During knockdowns and stoppages, event clarity and intentional silence take priority over queued dialogue.

Themed events may guide selection and editorial emphasis without tokenizing or restricting commentators by identity.

## 9. Fight clock and breaks

The menu exposes an **Accelerated Clock** toggle:

- **ON:** display 3:00 while 1:45 passes in real time.
- **OFF:** choose only 1 minute, 2 minutes, or authentic 3 minutes.

There is no free-form clock customization.

All gameplay systems read one synchronized authoritative fight clock. Between-round breaks last 30 real seconds; menu and statistics access do not pause the countdown. Break skipping is an in-match choice, not a pre-match setting. Human vs. Human requires both players to approve the skip.

## 10. Fighter attribute economy

- Internal attributes range from -100 to +100.
- Zero represents balance.
- Positive values represent advantages; negative values represent disadvantages.
- The model is give-and-take and must not permit unrestricted upward stacking.
- Avoid presenting one simplistic overall rating as the authoritative description of a fighter.
- Extreme values have escalating budget costs, and synergy or friction between traits affects real performance.

Positive caps:

- At most one attribute may equal +100.
- At most two attributes may exceed +70.

Negative safeguards:

- At most one attribute may equal -100.
- At most two related attributes may fall below -30.
- No fighter may have every physical trait negative.
- No fighter may have every technical trait negative.
- At most three attributes may fall below -40 overall.
- A value from -41 to -60 requires a meaningful positive of at least +30.
- A value from -61 to -80 requires a meaningful positive of at least +50.
- A value from -81 to -100 requires a meaningful positive of at least +70.
- Severe negatives must cause visible gameplay consequences.

Attribute families and compensating relationships must be explicit data, not inferred from display names. Demographic identity does not create hidden Power, Chin, Durability, speed, or intelligence modifiers.

## 11. Roster, abilities, and divisions

The roster is coed. There are no male/female divisions and no weight divisions. Differences in visible size, reach, speed, power, durability, movement, technique, and ability design are balanced through the shared attribute economy and counterplay.

Each complete fighter should have:

- an original identity, appearance, cultural grounding, personality, entrance, and rivalry network;
- a primary stance and authored stance familiarity;
- at least fifteen meaningful traits;
- two counterable Special abilities;
- one powerful but counterable Ultimate;
- one distinctive Full-Crowd Trait;
- visible strengths and vulnerabilities.

An Ultimate cannot be an automatic match end, unavoidable sequence, or substitute for boxing execution. Difficult inputs do not justify uncounterable results.

Uniqueness must not rely on obscenity, cultural caricature, intentional ugliness, random weirdness, or confusing mechanics.

## 12. Crowd system

Crowd gain may reward clean offense, defense, counters, reversals, combinations, variety, Ringcraft, appropriate Showmanship, and meaningful momentum changes.

At a full Crowd Bar, the fighter chooses between the Ultimate and the Full-Crowd Trait. One completed bar cannot activate both.

The crowd cannot:

- read or alter official scores;
- change judging criteria;
- provide a hidden generic damage, defense, speed, stamina, or comeback multiplier;
- reward low-risk meter farming;
- override contact, injury, or stamina truth.

## 13. Footwork, collision, and contact truth

Visible action and authoritative result must agree.

> **Feet establish position; position establishes range; range establishes contact; contact establishes consequence.**

The combat system must provide:

- one continuous threat-responsive footwork model;
- responsive navigation at safe distance;
- shorter believable boxing steps inside threatening range;
- planted pivots and visible weight transfer;
- explicit acceleration, deceleration, commitment, and recovery;
- authoritative glove, guard, head, body, arm, and facial-region collision;
- clean, solid, grazed, brushed, blocked, dodged, and whiffed outcomes;
- replay and telemetry capable of explaining major exchanges.

Do not permit ice skating, magnetic range correction, invisible lunges, uncontrolled body overlap, artificial movement-mode transition delays, or a visible miss classified as a clean hit.

Punches that meet the guard remain less costly than punches dodged through active defense, while complete empty-space whiffs receive the greatest recovery and stamina consequence. Numerical ratios remain tuning targets until validated.

## 14. Damage, blocking, and stoppages

Combat condition must distinguish at least:

- head;
- jaw/chin;
- left eye/orbital;
- right eye/orbital;
- upper and lower torso;
- left and right arm/guard;
- stamina;
- balance;
- guard;
- Composure;
- Chin;
- Durability;
- Recovery.

Blocking reduces clean damage but does not erase consequence. Intelligent varied pressure can damage the arms, weaken guard structure, and temporarily open a passive blocker. Predictable single-action spam does not automatically earn a guard break.

Contact quality determines delivered force. Grazed or brushed punches cause reduced but potentially meaningful damage. Movement into a punch may increase consequence; movement away may reduce it.

Eye damage must be visible, side-specific, and capable of reasonably reducing accuracy, tracking, side-specific recognition, counter timing, distance judgment, CPU decisions, and doctor confidence. It must not reverse controls, discard physically correct contact, or rely on extreme visual blur.

A Chin value of +100 represents maximum authored resistance, not absolute immunity. Rare early stoppages remain possible when observable force, placement, contact quality, movement, balance, awareness, accumulated condition, and failed defense support the result. Do not apply a flat random knockout chance to every punch.

## 15. Stance switching and Special inputs

Every fighter may switch between orthodox and southpaw.

Non-ambidextrous fighters receive authored penalties when operating outside their stated stance. Those penalties may affect accuracy, power transfer, defensive familiarity, combination fluency, stamina efficiency, or recovery.

A small, exclusive set of ambidextrous fighters receives no stance-familiarity penalty in either orientation. Ambidexterity is useful versatility, not universal superiority, and does not remove ordinary balance, commitment, or positioning consequences.

Stance switching must remain responsive and emerge through believable steps, pivots, pullbacks, and angle changes rather than a slow artificial transition.

Special abilities may use opponent-relative left-stick or D-pad motion commands followed by explicit confirmation. Recognition must be trainable, remappable, forgiving but consistent, and equally applied. Command entry cannot bypass stun, recovery, resource cost, range, tracking limits, startup, counterplay, or whiff punishment.

## 16. Referee fairness and influence

Six serious referees provide different enforcement philosophies under the same authoritative rules. Their tendencies may meaningfully affect clinches, legal inside work, warnings, deductions, fouls, injury monitoring, communication, and stoppages.

Referees should influence how fights develop without becoming arbitrary third fighters.

Every competitive referee must:

- be disclosed before the match;
- apply one consistent profile to both fighters;
- use observable evidence only;
- permit meaningful tactical adaptation;
- obey the same authoritative knockdown-count clock;
- obey universal medical and incapacitation minimums;
- produce replay-explainable major decisions.

Referees may not alter punch damage, stamina, collision classification, Crowd gain, fighter attributes, input responsiveness, or judging criteria.

Elliot “Eventually” Ames is a seventh, deliberately lax comic-relief botanical referee for non-Ranked play. His visual and behavioral implication is never canonically identified or directly stated. His ordinary enforcement may be unusually permissive, but he remains bound by universal safety, serious-foul, and knockdown-count standards.

> **Referees shape the boundaries of the contest without becoming the contest.**

## 17. Comedy and respectful presentation

Comedy is the highest presentation priority. It should emerge through original personalities, entrances, rivalries, commentary, crowd reactions, timing, spectacle, abilities, consequences, and arena presentation.

Comedy must not require:

- cultural disrespect;
- demographic stereotypes;
- copied characters or protected jokes;
- obscene or hateful presentation;
- intentionally unreadable mechanics;
- collision or outcome dishonesty.

The boxing remains competitively trustworthy even when the presentation is ridiculous.

## 18. Evidence and status honesty

Design documents are not implementation evidence. Do not claim that a feature, test, asset, system, or playable build exists unless the repository contains verifiable evidence.

Prototype numbers are tuning hypotheses unless a validated specification or test promotes them. Historical development logs may preserve earlier or superseded ideas only when their status is explicit.

When canonical files conflict, the latest explicit user correction controls and the repository must be synchronized promptly.
