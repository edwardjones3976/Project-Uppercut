# Project Uppercut — The Living Ring

> **Project Uppercut is arcade boxing with real boxing bones: instantly responsive,
> visually fast, genuinely funny, competitively truthful, and deep enough that a
> spectator can become a student without noticing the lesson begin.**

This document is the project's north-star painting. It does not replace
`PROJECT_RULES.md`, `PROJECT_NOTES.md`, accepted decisions, `ROADMAP.md`, or the
generated `STATUS.md`. It gives those instruments a horizon: what the finished
experience should feel like, what history taught this project, what makes it worth
building, and what must remain visible when technical work becomes dense.

Current volatile progress belongs in `STATUS.md`. This file describes the durable end
state.

---

## 1. The picture on the wall

The finished game should be understandable in ten seconds and interesting after ten
thousand exchanges.

A player chooses an original fighter whose posture, rhythm, humor, strengths,
liabilities, entrance, corner, and CPU behavior all describe the same person. The arena
announces importance before the bell without secretly changing the contest. The first
jab lands because feet created range, range created contact, and contact created
consequence. A missed hook leaves a visible debt. A blocked cross bruises the arms
without becoming phantom damage. A slip is not an invincibility spell; it is a timed
answer that can lose to the body. The crowd recognizes drama, not scorecards. The
announcers estimate, argue, and sometimes remain silent because certainty would be a
lie.

The fight looks faster than it mechanically is. Impacts have snap, sound, recoil,
reaction, and comic punctuation, while the underlying windows remain readable. A child
can understand that the tall fighter wants space. A boxing fan can see why the lead foot
matters. An experienced player can notice that the opponent's rear hand has left home.
A spectator can explain the knockdown after watching the replay. None of them receives
a different combat engine.

When the fight ends, the game does not merely show a winner. It shows the shape of the
fight:

- where control changed hands;
- which body regions deteriorated;
- which habits became readable;
- what the referee observed;
- what the judges were permitted to score;
- what each corner believed, with uncertainty;
- which boxing principle decided the final exchange;
- and which moment became the story people repeat afterward.

That is the living ring: a contest, a comedy stage, a teaching instrument, a simulation
laboratory, and a story generator sharing one truth.

---

## 2. The four experiences that must coexist

Project Uppercut is not one mode surrounded by optional furniture. It is four connected
experiences built on one authoritative fight.

### 2.1 Watch

CPU vs. CPU is a first-class product, not only a test harness.

A watchable bout must provide:

- distinct tactical personalities visible without debug overlays;
- broadcast framing that protects contact readability;
- round rhythm with pressure, resets, adaptation, and escalation;
- commentary that reacts to observable evidence and admits uncertainty;
- event presentation that amplifies stakes without voting on outcomes;
- replay and post-fight explanation strong enough to answer, “Why did that happen?”;
- enough variation that two bouts between the same fighters can tell different but
  mechanically defensible stories.

### 2.2 Learn

Training is preparation, not protection.

The training program should feel like a modern boxing gym translated into an inviting
interactive language:

1. show the idea;
2. name the boxing principle;
3. demonstrate the visible cue;
4. let the player perform it;
5. measure the attempt truthfully;
6. replay the result;
7. place the skill inside a live tactical problem;
8. remove the scaffolding without changing the rules.

Career and Story may later deepen this education through relationships, consequences,
and repeated application, but they must never replace the unified combat system with a
scripted substitute.

### 2.3 Compete

Human vs. CPU, local head-to-head, and later online play use the same combat truth.
Mastery comes from timing, spacing, pattern recognition, stamina judgment, ring control,
matchup knowledge, composure, and adaptation.

The game should permit a frightening opening aggressor and a patient stamina drainer to
win, while refusing to make either extreme the only sensible answer. The system does not
punish aggression; it punishes inaccurate, predictable, poorly spaced aggression. It
does not punish patience; it punishes empty avoidance that creates no advantage.

### 2.4 Remember

Every bout should leave a useful memory.

The event log, replay, statistics, commentary, and post-fight presentation should
produce a compact “fight fingerprint”:

- pace by round;
- preferred range;
- clean-contact map;
- guard and evasion choices;
- bodywork effect;
- repeated patterns and successful adaptations;
- knockdown causes;
- referee interventions;
- score uncertainty before the reveal;
- and one or two defining moments.

This is not decoration. Fight memory powers training, rivalries, spectator discussion,
future Career/Story systems, and balance analysis.

---

## 3. The historical lineage: principles, not borrowed paint

Project Uppercut learns from boxing-game history without copying protected identity,
content, or presentation.

| Historical lesson | What the field demonstrated | Project Uppercut's answer |
|---|---|---|
| **Punch-Out!! — immediate legibility** | Nintendo's creators described the arcade original as a simple experience that had to show its fun quickly; its development also turned hardware limits into a clear one-opponent spectacle. | Every exchange must be readable quickly. Simplicity at the surface is not shallowness; it is a doorway. |
| **Ready 2 Rumble — personality and arcade confidence** | The project's internal design study identifies the durable spirit: theatrical fighters, humor, showmanship as currency, tactile training, visible injury, and exaggerated motion. | Original characters, original comedy, the Crowd Bar, counterable Ultimates, and spectacle that never overrides boxing truth. |
| **Fight Night — consequence and embodied boxing** | EA described locomotion, punching, stamina, accessible controls, regional damage, angle, and contact quality as central advances, while Champion Mode showed that a sports game could carry cinematic drama. | Located condition, per-hand and per-region consequence, readable commitment, accessible control surfaces, and later story built from unscripted fights. |
| **Modern fighting games — one core with several doors** | Street Fighter 6 separated competitive fighting, a teaching-oriented single-player journey, and a social hub while retaining one recognizable combat identity. | CPU simulation, focused Training, later Career/Story, local competition, and online spaces become different doors into one ring. |
| **Rollback-era fighting games — determinism is product infrastructure** | GGPO's model depends on saving state, loading state, executing frames without rendering, and deterministic resimulation. | The C++ fixed-tick fight core, sealed authoritative state, event logs, and rendering-without-authority are not laboratory luxuries; they are future online foundations. |

The historical rule is simple:

> **Borrow the problem a successful game solved, never the protected surface it used.**

### Research notes

Primary and official references used for this vision:

- Nintendo, *Iwata Asks: Punch-Out!!*, especially “Now Featuring a Multiplayer
  Mode” and “The Root of What Makes Videogames Fun”:
  https://iwataasks.nintendo.com/interviews/wii/punchout/0/4/
  https://iwataasks.nintendo.com/interviews/wii/punchout/0/5/
- EA, *Fight Night Champion* announcement and launch materials:
  https://www.ea.com/news/ea-announces-fight-night-champion
  https://www.ea.com/en-gb/news/fight-night-champion-out-now
- EA, *Fight Night Champion Art Blog*:
  https://www.ea.com/news/fight-night-champion-art-blog
- Capcom, *Street Fighter 6 Redefines the Genre* and World Tour/Battle Hub
  materials:
  https://news.capcomusa.com/2022/06/02/street-fighter-6-redefines-the-genre-in-2023/
  https://news.capcomusa.com/2022/09/15/details-on-street-fighter-6s-world-tour-battle-hub-four-world-warriors-and-a-closed-beta/
- GGPO, official rollback networking explanation:
  https://www.ggpo.net/
- Project Uppercut's internal reference study:
  `docs/design/ready_2_rumble_design_study.md`

---

## 4. The seven-part feel hierarchy, made visible

The production feel order remains binding. This section describes what success looks
like on screen and in the hands.

### 4.1 Impressively responsive

- Inputs or CPU decisions receive immediate acknowledgement.
- Basic actions do not hide behind ornamental animation delay.
- Recovery is clear and consistent.
- Buffering forgives human timing within authored limits without manufacturing success.
- A player can distinguish “I was late” from “the game was late.”

### 4.2 Visually fast

- Animation, camera, audio, effects, and crowd energy create velocity.
- The authoritative reaction window remains readable.
- Impact emphasis may stretch perception for a moment but never moves collision truth.
- Spectators can reconstruct the exchange afterward.

### 4.3 Fun and funny

- Comedy grows from character, timing, confidence, consequence, commentary, entrances,
  corners, referees, and arena culture.
- A boast becomes funnier when the next jab interrupts it.
- A defensive genius can be amusing without becoming a joke fighter.
- Humor never requires inaccurate contact, humiliating identity, or scripted outcomes.

### 4.4 Boxing-logic accurate

- Range, stance, foot position, guard structure, hand position, fatigue, and recovery
  matter.
- The target of a punch and the structure that intercepts its path remain separate
  concepts.
- Bodywork changes later choices.
- Pressure is effective only when it creates position and contact.
- Defense is useful only when it creates survival, position, or an answer.

### 4.5 Enjoyable

- Losses remain understandable.
- Matches avoid exhausting monotony.
- The user can return for another bout without feeling processed by a machine.
- The game supports serious competition and relaxed experimentation without changing
  combat truth.

### 4.6 Steady-paced

The natural match sentence is:

`read → enter → exchange → consequence → reset or pursue → adapt → escalate`

Constant fireworks flatten drama. Constant caution starves it. The best pace creates
contrast.

### 4.7 Secretly layered with boxing idioms

“Stick and move,” “work the body,” “cut off the ring,” “styles make fights,”
“protect yourself at all times,” and similar principles should exist as observable
mechanical relationships before commentary ever says them.

The player first feels the truth, then learns its name.

---

## 5. What makes Project Uppercut distinct

### 5.1 Explainable boxing, not opaque spectacle

Every major result should have a causal trail. The event record should explain contact,
condition, knockdowns, stoppages, and cards without exposing information prohibited by
the score firewall.

### 5.2 Personality expressed through decisions

A fighter is not a skin over a move list. Identity appears in:

- preferred range;
- opening temperament;
- risk tolerance;
- recovery habits;
- hand discipline;
- guard choices;
- combination grammar;
- Showmanship;
- adaptation speed;
- corner relationship;
- referee interaction;
- and the way confidence changes after success or failure.

### 5.3 Spectacle that buys attention, not authority

The crowd, camera, commentary, entrance, arena, music, lighting, and Ultimate
presentation may enlarge a moment. They may not rewrite it.

### 5.4 A match that teaches itself

Readable cues, truthful replays, useful statistics, commentary uncertainty, and
post-fight explanation make ordinary play educational without turning every match into
a lecture.

### 5.5 A reusable boxing platform

The same systems should support:

- generic balance profiles;
- named fighters;
- CPU bouts;
- human control;
- training drills;
- local competition;
- online rollback;
- commentary and broadcast packages;
- event classes;
- later Career and Story;
- and development telemetry.

A new fighter should remix proven systems more often than invent a private engine.

---

## 6. The end-state product silhouette

The completed Version 1 should feel coherent before it feels large.

### Core fight experience

- Complete CPU vs. CPU, Human vs. CPU, and local Human vs. Human matches.
- Original fighters with authored styles, traits, vulnerabilities, two Specials, one
  Ultimate, and one Full-Crowd Trait.
- Full round, knockdown, count, recovery, stoppage, decision, statistics, replay, and
  post-fight flow.
- Referees with disclosed philosophies under common rules.
- Judges behind a real score firewall.
- Event classes ranging from intimate club cards to championship spectacles.
- Commentary crews that scale with fight importance.

### Learning experience

- Focused Training modules using the live combat engine.
- Demonstrations, drills, measurable goals, replay, and fight-film analysis.
- Boxing idioms connected to mechanics.
- Character and matchup guides derived from actual data rather than marketing prose.

### Competitive experience

- Symmetric local competition first.
- Online only after deterministic local play is stable.
- Ranked, casual, event, and open-challenge spaces later, with varied challenge rather
  than permanent skill quarantine.
- No hidden beginner protection and no special elite rule set.

### Spectator experience

- CPU cards worth watching without developer overlays.
- Broadcast cameras, replay packages, event pacing, entrances, crowd reactions, and
  post-fight summaries.
- Optional “Ringside Desk” tools for comparing tendencies, predicted style tensions,
  and observable momentum without revealing official scores.

### Future version compatibility

Career and Story remain deferred and low priority, but the architecture should later
support:

- gyms, trainers, rivals, promoters, event tiers, injuries, recovery, reputation, and
  fighter relationships;
- a beginner's development through repeated truthful fights;
- drama produced by consequences rather than scripted winners;
- and a world that remembers what actually happened in the ring.

---

## 7. The first undeniable demonstration

Before roster size, career breadth, or online reach, Project Uppercut needs one compact
proof that contains its soul.

A strong first undeniable demonstration is:

1. choose two generic tactical profiles;
2. disclose the referee and event context;
3. watch one complete rendered bout or compact multi-round contest;
4. see readable movement, guard, slip, bodywork, fatigue, knockdown, count, recovery or
   stoppage, and a decision path that survives;
5. hear one original commentary voice and one intentionally placed silence;
6. witness one funny character-neutral reaction that does not alter the outcome;
7. review a fight fingerprint that explains the decisive exchange;
8. rerun the same seed and receive the same authoritative fight beneath presentation;
9. change the seed and receive a different but explainable contest.

That demonstration is the bridge from impressive engineering to an unmistakable game.

---

## 8. Anti-goals

Project Uppercut must not become:

- a physics slapstick game whose humor depends on dishonest outcomes;
- a solemn simulation that forgets personality and delight;
- a hero fighter where abilities replace boxing;
- a one-health-bar damage race;
- a cinematic story that scripts winners;
- a beginner mode with hidden protection;
- an elite mode with exclusive mechanics;
- a CPU showcase that reads inputs, scores, or future actions;
- a content pile built faster than its systems can explain;
- a museum of design documents without a living fight;
- or a technically immaculate engine that nobody wants to watch twice.

---

## 9. The final promise

> **Build the boxing truth once. Let fighters, crowds, jokes, rivalries, arenas,
> training, broadcasts, and future stories reveal different faces of it.**

Project Uppercut succeeds when a newcomer laughs, a boxing fan nods, a competitor sees
a deeper answer, a spectator understands the turning point, and the engine can prove
that none of them watched a lie.
