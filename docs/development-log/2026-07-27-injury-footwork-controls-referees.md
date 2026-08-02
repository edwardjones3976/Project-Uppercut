# Project Uppercut — Injury, Footwork, Controls, Stances, and Referees

**Date:** 2026-07-27 (America/Los_Angeles)  
**Status:** Preproduction design record  
**Scope:** An improvised consolidation of the ten Project Uppercut design responses produced after the previous GitHub entry.

> This document records accepted direction and prototype hypotheses. It does not claim that any combat system, animation, referee logic, CPU behavior, visual injury model, controller command, balance value, or playable build has been implemented or validated.

## Executive direction

This design pass adds five connected layers to the unified combat system:

1. rare but explainable stoppage vulnerability for every fighter;
2. visible, localized facial damage with meaningful accuracy consequences;
3. one continuous threat-responsive footwork model;
4. tactical stance switching and motion-command Specials;
5. a referee system that is fair, readable, strategically meaningful, and capable of changing a fight without arbitrarily deciding it.

The governing principle is:

> Project Uppercut should preserve visible boxing truth while allowing attributes, injuries, movement choices, command execution, and officiating philosophy to create meaningful strategic consequences.

## 1. Maximum Chin is resistance, not immunity

A fighter with a Chin rating of 100 has the strongest authored resistance in the roster. That rating does not create absolute immunity to an early knockdown, knockout, or referee stoppage.

A rare early stoppage remains possible when qualifying evidence supports it, including:

- exceptional delivered force;
- clean jaw placement;
- high contact quality;
- the defender moving into the punch;
- poor balance or foot placement;
- lack of bracing or visual awareness;
- a precisely timed counter;
- a dangerous accumulated sequence;
- an inability to defend intelligently after being hurt.

The initial design hypothesis may target an approximately one-percent early-stoppage frequency for maximum-Chin fighters at the population or simulation level, but this must not become a flat one-percent roll on every punch. A per-punch lottery would compound rapidly, reward volume spam, and produce unexplained outcomes.

The authoritative stoppage model should evaluate delivered force, location, movement, balance, awareness, fatigue, accumulated condition, Chin, Recovery, Composure, and follow-up defense. Rare does not mean arbitrary.

> A maximum rating guarantees exceptional resistance, not supernatural invulnerability.

Simulation calibration must distinguish:

- percentage of fights ending early;
- percentage of qualifying clean impacts producing a severe reaction;
- opponent Power distribution;
- contact location and quality;
- fatigue and accumulated damage;
- follow-up sequence;
- referee profile;
- recovery success.

## 2. Facial regions and visible eye damage

The head cannot operate as one undifferentiated damage volume. The minimum facial target model includes:

- **General Head**
- **Jaw/Chin**
- **Left Eye/Orbital**
- **Right Eye/Orbital**

The wider body model continues to include Upper Torso, Lower Torso, Left Arm/Guard, and Right Arm/Guard.

Jaw contact primarily influences shock, stun, knockdown vulnerability, and stoppage risk. Eye and orbital contact primarily influences swelling, cuts, visual tracking, defensive recognition, accuracy, corner treatment, commentary, and doctor-stoppage risk. One punch can affect more than one condition only when its actual contact geometry supports that classification.

### Eye-condition stages

| Condition | Intended presentation |
|---|---|
| Fresh | No meaningful impairment |
| Irritated | Redness, blinking, and minor discomfort |
| Swollen | Visible swelling and measurable functional loss |
| Compromised | Restricted opening, tracking difficulty, and elevated medical concern |
| Critical | Severe impairment and substantial doctor-stoppage risk |

Each eye is tracked separately. Visual presentation should agree with the authoritative injury state through swelling, cuts, blinking, facial animation, corner treatment, and commentary. Damage to the left eye cannot silently appear on the right.

### Accuracy must be affected

Swollen-eye damage directly reduces accuracy. The effect is physical, readable, and side-specific rather than an unexplained forced-miss roll.

Preliminary tuning ranges are:

| Eye condition | Accuracy reduction target |
|---|---:|
| Fresh | 0% |
| Irritated | 1–2% |
| Swollen | 4–6% |
| Compromised | 8–12% |
| Critical | 12–18% |

These values are prototypes, not final balance commitments.

The strongest impairment occurs when:

- attacks approach through the damaged side;
- the opponent pivots or exits toward the impaired side;
- the fighter attempts a side-specific counter;
- the fighter must reacquire a moving target;
- both eyes are damaged;
- fatigue, stun, poor balance, or low Composure compounds the injury.

Eye damage may:

- reduce target tracking;
- narrow placement precision;
- weaken distance judgment;
- delay attack recognition from the impaired side;
- reduce defensive confidence;
- degrade side-specific counter timing;
- turn marginal clean contact into solid contact;
- turn solid contact into a graze;
- cause a narrowly placed punch to pass a moving target;
- influence CPU targeting, movement, and risk assessment;
- prompt tactical corner advice;
- raise doctor-stoppage scrutiny.

It must not reverse controls, discard a correctly timed input, bend a visibly centered punch away from its target, create extreme screen blur, or apply an unexplained global miss chance. If the glove trajectory is physically centered, properly ranged, and unobstructed, it still connects.

Corner treatment may reduce swelling between rounds without completely erasing accumulated injury. Fighters and CPUs may also respond by changing guard orientation, stance, circling direction, preferred counters, head position, or engagement distance.

> Eye damage reduces what the fighter can accurately see, track, and target; it does not override what visibly happens in the ring.

## 3. Elastic Footwork System

Project Uppercut should not divide movement into slow binary locomotion engines such as free movement and engaged movement. Those terms may describe circumstances, but the fighter remains inside one continuous system.

> Distance changes the shape of movement, not responsiveness.

The Elastic Footwork System continuously adjusts stride length, urgency, weight transfer, defensive readiness, and directional commitment according to a threat field.

The threat field considers:

- opponent position and distance;
- opponent stance and lead side;
- glove and shoulder orientation;
- forward momentum;
- active and anticipated attacks;
- angles and escape lanes;
- ropes and corners;
- both fighters’ balance, stamina, and speed;
- current guard and vulnerable regions.

At safe distance, fighters use longer responsive navigation and believable acceleration. As threat rises, steps compress naturally into shorter boxing movement. During an active exchange, the fighter cannot freely sprint around committed punches, but direction changes remain responsive when the feet and balance support them.

The system requires:

- immediate recognition of movement intent;
- believable foot completion;
- branchable steps;
- planted pivots;
- explicit acceleration and deceleration;
- no artificial transition tax;
- no magnetic range correction;
- no invisible attack lunges;
- no rotation without meaningful footwork;
- no slow, obvious mode-change animation that creates unrelated vulnerability.

Free, Threatened, Committed, and Unbalanced may be useful telemetry descriptors. They are not separate control schemes.

Motion matching, inertial blending, stride warping, distance warping, orientation warping, and procedural foot placement may support presentation, but none may invent range or contradict authoritative position.

## 4. Stance switching and ambidextrous fighters

Every fighter may switch between orthodox and southpaw. Each non-ambidextrous fighter has a stated primary stance and loses some familiarity when operating outside it.

Secondary stance remains useful for:

- changing the lead-hand matchup;
- protecting an injured eye or arm;
- creating a new attack angle;
- escaping poor positioning;
- changing the lead-foot relationship;
- disrupting an opponent’s timing;
- altering jab and rear-hand responsibilities.

Typical prototype penalties for a non-ambidextrous fighter in the secondary stance may include:

| Mechanic | Preliminary range |
|---|---:|
| Accuracy | −5% to −10% |
| Power transfer | −4% to −8% |
| Guard stability | −5% to −10% |
| Combination speed | −3% to −7% |
| Defensive reaction | 3% to 8% slower |
| Stamina consumption | 5% to 10% higher |
| Miss recovery | 5% to 12% longer |

The actual package is authored per fighter. One fighter may preserve accuracy but lose power transfer; another may retain force but become less coordinated defensively.

A small, exclusive group of ambidextrous fighters receives no stance-familiarity penalty in either orientation. They preserve authored accuracy, defense, combination fluency, and power transfer when changing stance.

Ambidexterity does not grant:

- higher universal attributes;
- free damage;
- superior stamina;
- faster movement by default;
- recovery cancellation;
- immunity to bad positioning;
- protection while crossing the feet;
- automatic matchup superiority.

Stance versatility consumes part of the fighter’s overall design economy. A specialist may possess greater one-stance mastery, power, durability, stamina, pressure, crowd influence, or ability strength. Ambidextrous fighters gain adaptability, not a best-in-roster classification.

Switching should emerge from believable steps, pivots, pullbacks, angle exits, direction changes, and combination endings. The input is responsive, but a careless switch remains vulnerable because of visible balance and position rather than an artificial delay.

CPU fighters should switch for observable tactical reasons rather than random variety.

> Every fighter may change stance. Specialists sacrifice familiarity; ambidextrous fighters do not, but everyone remains bound by timing, balance, and position.

## 5. Left-stick motion commands for Specials

Motion-command activation is accepted as a promising control direction because it can reward deliberate execution while incorporating Specials into actual boxing movement.

Candidate universal command families include:

- Down → Down-Forward → Forward + Special;
- Forward → Down → Down-Forward + Special;
- Down → Down-Back → Back + Special;
- Back → Forward + Special;
- Forward → Forward + Special.

Commands are opponent-relative:

- Forward means toward the opponent.
- Back means away from the opponent.
- Side changes update the command frame automatically.
- Orthodox/southpaw switching does not reverse the player’s command language.

A dedicated Special button is the preferred confirmation because ordinary movement and power punches occur constantly. Directional preparation plus explicit confirmation reduces accidental activation. If controller capacity requires it, Special may serve as a modifier with Lead Punch and Rear Punch selecting between the two abilities.

Initial recognition targets may permit:

- approximately 350–500 milliseconds to complete a command;
- small neutral gaps;
- forgiving but consistent directional sectors;
- equivalent D-pad and left-stick entry;
- remapping;
- identical competitive tolerance for all players.

Training Mode should display input history and identify the missing or incorrect direction. This is structured preparation, not an easier competitive control system.

Directional inputs remain legitimate movement. A forward input advances, a down input compresses or changes level, and a diagonal creates an angle when physically valid. The fighter should not freeze while entering the command.

Motion commands cannot bypass:

- recovery;
- stun;
- severe imbalance;
- authored range;
- tracking limits;
- stamina cost;
- Crowd requirements;
- cooldowns;
- counterable startup and recovery.

Execution difficulty is never permission for an unavoidable move.

> Directional preparation establishes intent; the Special button confirms it; authored boxing consequences govern the result.

## 6. The competitive referee crew

Six serious referees provide different enforcement philosophies under the same authoritative boxing rules.

Their independent behavioral axes include:

- intervention frequency;
- clinch tolerance;
- inside-work allowance;
- foul strictness;
- warning patience;
- deduction readiness;
- safety sensitivity;
- stoppage urgency;
- communication;
- positioning.

### Prototype profiles

| Referee | Philosophy | Intervention | Clinch | Inside | Foul strictness | Warning patience | Deduction | Safety | Stoppage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Raymond Whitaker | Patient Observer | 2 | 8 | 7 | 4 | 8 | 2 | 5 | 4 |
| Celeste Navarro | Authority | 9 | 2 | 3 | 9 | 3 | 9 | 7 | 7 |
| Hana Mori | Technician | 6 | 5 | 5 | 8 | 5 | 7 | 7 | 6 |
| Darius Cole | Inside-Work Referee | 3 | 7 | 10 | 5 | 7 | 4 | 6 | 5 |
| Nkiru Okafor | Safety Specialist | 7 | 4 | 4 | 7 | 5 | 6 | 10 | 10 |
| Thomas Baines | Communicator | 6 | 5 | 6 | 6 | 10 | 5 | 7 | 6 |

Ratings are relative prototype tendencies on a 1–10 scale, not implementation claims.

Their philosophies are:

1. **Whitaker:** Fighters should resolve most legitimate situations themselves.
2. **Navarro:** Clean structure and immediate obedience preserve the contest.
3. **Mori:** Repeatable technical consistency should govern enforcement.
4. **Cole:** Legal inside work deserves time to develop.
5. **Okafor:** Continued punishment must remain medically and defensively justifiable.
6. **Baines:** Clear communication can preserve action without surrendering control.

### Shared authoritative rules

Referee personality may never alter:

- contact or collision classification;
- punch damage;
- stamina calculations;
- knockdown physics;
- the authoritative knockdown-count clock;
- input responsiveness;
- fighter attributes;
- Crowd gains;
- official judging criteria;
- access to hidden health values, opponent inputs, or live scorecards.

Every referee uses observable evidence. The count clock is identical even when voice cadence and animation differ. All officials obey a universal medical and incapacitation floor.

## 7. Referees must be meaningful without ruining matches

Referees are active matchup conditions, not cosmetic presets. A permissive referee may favor infighters, clinch workers, physical pressure fighters, body punchers, and fighters skilled at borderline tactics. A stern referee may favor outboxers, mobile counterpunchers, clean combination punchers, and disciplined fighters who require space. A safety-focused referee may disadvantage slow starters or comeback specialists by intervening sooner when observable defense collapses.

That influence is legitimate within reason.

> A referee may influence how the fight develops, but should rarely determine the winner without the fighters’ conduct creating that result.

The project should not automatically tighten a referee merely because a matchup win rate changes. Testing must ask whether the shift is logical, disclosed, consistent, and adaptable.

A profile requires investigation when:

- the advantage has no understandable boxing explanation;
- it favors the same fighter across nearly every matchup;
- opponents lack meaningful adaptation;
- similar incidents receive inconsistent calls;
- hidden information determines decisions;
- the official invalidates an entire style;
- the optimal strategy becomes exploiting the official rather than boxing;
- referee influence regularly overwhelms fighter execution.

Ranked referee testing should examine style-conditioned results rather than only global averages. A meaningful shift in a particular infighter-versus-outboxer matchup may be desirable even when the overall roster remains balanced.

The assigned referee and three concise tendencies should be disclosed before final fighter selection or before a locked competitive set. Players and CPUs can then adapt clinching, inside work, foul risk, rope tactics, guard recovery, pressure, and injury management.

Every major action should be replay-explainable through:

- detected infraction or injury;
- observable severity;
- referee view and distance;
- prior warnings;
- command issued;
- fighter compliance;
- reason for separation, warning, deduction, doctor consultation, or stoppage.

The corrected governing law is:

> Referees shape the boundaries of the contest without becoming the contest.

## 8. Elliot “Eventually” Ames

Elliot Ames is a seventh, deliberately noncompetitive comic-relief referee for Exhibition, Casual, Local, Custom, Party, and selected CPU-simulation matches. He is excluded from Ranked.

His official identity is simply an unhurried referee of uncertain botanical origin. Nothing in canon, dialogue, commentary, interface text, asset naming visible to players, or marketing confirms any interpretation beyond “leaf referee.”

### Visual direction

- humanoid botanical body;
- a familiar serrated-leaf silhouette;
- eight uneven leaflets, including one conspicuously extra leaflet;
- relaxed half-lowered eyes;
- slightly oversized striped referee shirt;
- off-center bow tie;
- slow, loose gestures;
- no smoke, paraphernalia, drug terminology, explicit symbolism, or direct explanation.

Younger players should be able to read him as a strange sleepy plant. Older players may recognize an unconfirmed layer of the joke.

### Prototype profile

| Axis | Rating |
|---|---:|
| Intervention | 1/10 |
| Clinch tolerance | 10/10 |
| Inside allowance | 9/10 |
| Foul strictness | 2/10 |
| Warning patience | 10/10 |
| Deduction readiness | 1/10 |
| Safety sensitivity | 5/10 |
| Stoppage urgency | 3/10 |

His ordinary behavior includes:

- extended benefit of the doubt;
- unusually patient clinch observation;
- delayed but eventually enforceable warnings;
- slow approaches to routine separations;
- generous tolerance of messy legal inside work;
- cosmetic moments of delayed realization.

The decision system must register authoritative events correctly even when his animation delivers the joke late. He remains bound by the universal count, doctor, incapacitation, serious-foul, and intelligent-defense standards.

> Elliot is late to manage disorder, but never late to recognize genuine danger.

His humor concerns patience, distraction, paperwork, and unusual timing. It never directly names or confirms the underlying implication.

Candidate lines include:

- “I was getting to that.”
- “Break. Yes, I mean now.”
- “I saw it. I was considering it.”
- “Let’s not turn this into paperwork.”
- “Continue—but perhaps more thoughtfully.”

Commentary may say:

- “Eventually is taking the scenic route again.”
- “That warning had a very long introduction.”
- “Nobody has ever accused Ames of rushing to judgment.”

His match card must clearly disclose:

- extremely tolerant of clinching;
- very slow to deduct;
- allows prolonged inside fighting;
- unavailable in Ranked.

## 9. CPU simulation and validation requirements

The CPU-first foundation should test these systems together rather than in isolation.

### Injury telemetry

Record:

- impact region and side;
- contact quality;
- delivered force;
- eye-condition change;
- accuracy effect;
- reaction and target-reacquisition time;
- corner treatment;
- doctor observation;
- knockdown and stoppage chain.

### Footwork and stance telemetry

Record:

- threat value;
- stride length and acceleration;
- planted foot;
- stance before and after movement;
- reason for stance switch;
- active familiarity penalties;
- balance and recovery;
- whether animation agrees with authoritative position.

### Special-command telemetry

Record:

- directional history;
- command-recognition result;
- confirmation input;
- fighter state;
- resource cost;
- startup, contact, block, dodge, whiff, and recovery;
- rejected-activation reason.

### Referee telemetry

Record:

- clinch duration;
- legal inside-work duration;
- breaks;
- warnings;
- deductions;
- fouls by type and severity;
- doctor consultations;
- stoppage evidence;
- style-conditioned and fighter-conditioned win rates;
- player or CPU adaptation after disclosed tendencies.

Simulation should identify arbitrary or dominant interactions without flattening intentional boxing-style differences.

## Consolidated status

| Area | Disposition |
|---|---|
| Maximum Chin without immunity | Accepted direction |
| Approximately 1% rare early-stoppage hypothesis | Simulation target; never a flat per-punch roll |
| Separate Head, Jaw, Left Eye, and Right Eye regions | Accepted direction |
| Visible side-specific eye injury | Accepted direction |
| Eye-driven accuracy reduction | Required; numerical ranges remain tuning targets |
| Elastic threat-responsive footwork | Accepted system direction |
| Universal stance switching | Accepted direction |
| Exclusive penalty-free ambidextrous fighters | Accepted direction; not a superiority class |
| Left-stick motion-command Specials | Accepted prototype direction |
| Dedicated Special confirmation | Preferred control hypothesis |
| Six serious referee philosophies | Accepted roster direction |
| Fair but meaningful referee influence | Binding balance philosophy |
| Elliot “Eventually” Ames | Accepted non-Ranked comic-relief direction |
| Replay-explainable referee decisions | Mandatory competitive standard |

## Immediate documentation consequences

1. Extend the observable combat-event model with facial region, affected side, eye condition, tracking effect, stance, familiarity state, motion-command history, and referee evidence.
2. Treat all numerical values in this entry as prototype targets until CPU simulation and human playtesting validate them.
3. Build validation cases for maximum-Chin early stoppages, side-specific eye impairment, physically centered punches under injury, threat-responsive stride compression, stance changes during pivots and exchanges, command recognition during real movement, and referee-style matchup shifts.
4. Disclose referee tendencies before competitive selection and exclude Elliot Ames from Ranked.
5. Preserve one combat system for CPU and human participants. CPU agents receive no hidden access to command inputs, scorecards, or authoritative values that their fighter could not observe.
6. Keep referee influence meaningful, consistent, explainable, and responsive to fighter conduct.

## Evidence limitation

This entry is an improvised design consolidation created from the latest Project Uppercut planning responses. It documents intended behavior and balance hypotheses; it does not establish implementation, testing, licensing, asset completion, engine integration, or production readiness.
