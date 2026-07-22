# Project Uppercut — Binding Project Rules

These rules consolidate the decisions accepted during the initial Project Uppercut planning conversation. Later explicit corrections supersede earlier suggestions.

## 1. Originality

Project Uppercut is an original spiritual successor, not a remake or literal clone. Do not copy protected characters, names, likenesses, voice performances, music, arenas, artwork, animations, user-interface presentation, announcer lines, story material, or source code.

Every fighter, commentator, trainer, arena, asset, line, mechanic presentation, and brand element must have original provenance and remain distinguishable from real people and existing games.

## 2. Boxing knowledge is functional

Boxing idioms and principles must connect observable fight events to mechanics, CPU strategy, corner advice, commentary, judging interpretation, training, career development, and post-fight analysis.

Lore must be stored as canonical data-driven rules. Multiple sayings may reference one canonical tactical principle; presentation text must not duplicate the underlying combat rule.

## 3. Score Isolation Principle

Official scorecards are private to the Judge subsystem, Match Controller, and the Referee only when required.

During the fight and immediate post-fight flow, official cards must not be readable by:

- human-facing fighter logic;
- CPU fighter logic;
- trainers or corners;
- commentary;
- crowd systems;
- difficulty or adaptive systems;
- live replay presentation;
- advice or bonus systems.

These systems may form imperfect estimates only from observable events, with explicit confidence and uncertainty. Early stoppages terminate scoring. Partial cards remain sealed during the immediate result, quick-menu, and statistics flow, with an optional later archival reveal.

No rubber-banding may use official scores.

## 4. Fair anti-spam behavior

Legitimate repetition remains valid when tactically earned and unanswered. Repetitive low-skill or exploitative behavior must become readable, tiring, positionally costly, and counterable through shared boxing logic.

The same recognition and consequence rules apply to human and CPU-controlled fighters. Do not use hidden punishment, impossible reaction speed, privileged inputs, or official-score knowledge.

Targeted abuse includes one-move loops, safe-animation abuse, stun loops, clinch abuse, excessive running, and meter farming.

## 5. Advice rewards

Bonuses for successfully following valid corner, commentary, or crowd advice must remain small, bounded, non-stackable, and resistant to farming.

Reliability order:

1. Corner
2. Commentary
3. Crowd

Ring Awareness, Coachability, and Corner Chemistry may influence eligibility. Direct combat benefit must not exceed approximately 2%–3% per round and must never use official-score information.

## 6. Development order

The phase order is fixed:

1. Human vs. CPU MVP
2. Human vs. Human
3. Complete CPU vs. CPU simulation
4. Career mode
5. Online mode
6. Future updates

Each phase requires measurable exit criteria and a passed quality gate.

## 7. Commentary crews

- Four- and six-round fights use one commentator.
- Eight- and ten-round fights use two commentators.
- Twelve-round fights use three commentators.
- Championship fights always use three commentators, even when scheduled for fewer than twelve rounds.
- Any original commentator may work with any other; chemistry affects presentation but does not create hard identity-based restrictions.
- During knockdowns and stoppages, event clarity and intentional silence take priority over queued dialogue.

Themed events may guide selection and editorial emphasis without tokenizing or restricting commentators by identity.

## 8. Fight clock and breaks

The menu exposes an **Accelerated Clock** toggle:

- **ON:** display 3:00 while 1:45 passes in real time.
- **OFF:** choose only 1 minute, 2 minutes, or authentic 3 minutes.

There is no free-form clock customization.

All gameplay systems read one synchronized authoritative fight clock. Between-round breaks last 30 real seconds; menu and statistics access do not pause the countdown. Break skipping is an in-match choice, not a pre-match setting. Human vs. Human requires both players to approve the skip.

## 9. Fighter attribute economy

- Internal attributes range from -100 to +100.
- Zero represents balance.
- Positive values represent advantages; negative values represent disadvantages.
- The model is give-and-take and must not permit unrestricted upward stacking.
- Avoid presenting one simplistic overall rating as the authoritative description of a fighter.
- Extreme values have escalating budget costs, and synergy/friction between traits affects real performance.

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

Attribute families and compensating relationships must be explicit data, not inferred from display names.

## 10. Evidence and status honesty

Design documents are not implementation evidence. Do not claim that a feature, test, asset, or playable build exists unless the repository contains verifiable evidence.

