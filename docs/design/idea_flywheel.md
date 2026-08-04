# The Project Uppercut Idea Flywheel

> **Ideas should keep moving even when implementation must stay disciplined.**

Project Uppercut needs two opposite virtues at once:

- a narrow active slice that can actually finish; and
- a wide creative horizon that never goes gray from staring at the same subsystem.

This document protects both. It is a reservoir for ideas, a filter against scope creep,
and a repeatable method for turning research into original design rather than imitation.
It does not authorize implementation. `ROADMAP.md`, accepted decisions, and the active
quality gate control when an idea may enter production.

---

## 1. The anti-stagnation rule

A project stagnates in two different ways:

1. **Mechanical stagnation:** the team repeats the same kind of technical work until it
   loses sight of the player experience.
2. **Conceptual stagnation:** the team protects scope so aggressively that no new image,
   mode, character behavior, training method, or presentation language is allowed to
   form.

The answer is not unrestricted brainstorming. The answer is a creative side-channel:
ideas are continuously collected, argued, classified, and sharpened while only the idea
aligned with the active gate is eligible to become code.

> **Keep the gallery open. Keep only one painting on the easel.**

---

## 2. Six galleries for new ideas

Every idea enters one primary gallery. Cross-links are allowed, but one gallery owns the
question.

### Gallery A — Ring Truth

Questions of boxing mechanics, tactics, consequence, judging, refereeing, stamina,
condition, movement, defense, and adaptation.

Examples:

- per-hand and later lateral guard availability;
- punch trajectory versus interception structure;
- clinch entry, work, break, and referee philosophy;
- feints that alter observable prediction rather than damage;
- bodywork that changes later choices;
- ring-cutting geometry;
- southpaw/orthodox foot-position consequences;
- fatigue changing decision quality before it changes animation speed.

### Gallery B — Character Theater

Questions of personality expressed through behavior, not merely biography or costume.

Examples:

- a fighter who becomes funnier when losing composure;
- a technician whose taunts are tiny corrections rather than dances;
- a Showman whose combinations contain intentional “applause windows” that remain
  punishable;
- rival fighters who interpret the same observable event differently;
- corner chemistry that changes advice confidence, not combat truth;
- entrances that reveal tactical identity before the bell.

### Gallery C — Broadcast Magic

Questions of watchability, camera, sound, commentary, replay, arena, event pacing, and
spectator understanding.

Examples:

- commentary that states confidence levels indirectly through language;
- deliberate silence after a frightening knockdown;
- a “Ringside Desk” that compares style tensions without reading official cards;
- replay overlays that show hand availability, range, and contact quality;
- venue acoustics that make a club fight intimate and a championship fight enormous;
- crowd reactions that split audibly between admiration, concern, and disbelief;
- camera lenses selected by event class while contact readability remains invariant.

### Gallery D — Learning Lab

Questions of Training, replay education, boxing vocabulary, guided practice, and later
Career/Story development.

Examples:

- “Myth versus Ring Truth” drills that test popular boxing sayings;
- a film-room mode that pauses before the mistake and asks for the better answer;
- replay takeover that returns the player to a prior decision point;
- style-recognition drills using generic CPU profiles;
- corner advice exercises where the player must identify which advice is relevant;
- a training module that teaches when *not* to throw;
- tactile minigames that improve understanding without granting competitive stats.

### Gallery E — Competitive Ecology

Questions of local competition, online networking, matchmaking variety, lobbies,
tournaments, spectating, disputes, replays, and community knowledge.

Examples:

- open-challenge rooms where any skill level can voluntarily enter;
- ranked matchmaking with strong similarity preference but occasional style and rating
  variation;
- post-match “run it back with the same seed conditions” exhibitions;
- spectator prediction cards that never affect the fight;
- tournament broadcasts driven by authoritative event records;
- a rematch system that highlights what each fighter adapted between bouts;
- rollback-safe presentation rules for audio, particles, and commentary.

### Gallery F — World and Event

Questions of arenas, fight cards, promoters, referees, commentators, gyms, rivalries,
culture, themed events, and later Career/Story worldbuilding.

Examples:

- club nights whose intimacy changes sound and camera but not physics;
- invitation events where social prestige changes presentation, not fighter power;
- regional commentary traditions;
- referees who become recognizable through fair enforcement philosophy;
- fight-week packages that create narrative from actual matchup tensions;
- a comedy showcase with louder presentation but identical contact truth;
- arenas that remember prior events visually without implying scripted history.

---

## 3. The Idea Card

No idea enters serious discussion until it can answer this card.

```text
IDEA NAME:

GALLERY:

PLAYER PROMISE:
What new feeling, understanding, decision, or story does this create?

BOXING OR GAME TRUTH:
What real principle, proven game-design problem, or product need supports it?

VISIBLE PROOF:
What would a player or spectator actually see, hear, choose, or understand?

AUTHORITATIVE SYSTEMS REUSED:
Which existing systems carry it? What must not be duplicated?

PRESENTATION LAYER:
How does it appear without gaining fight authority?

COUNTERPLAY OR FAILURE:
How can the mechanic be answered, misused, or shown to be a bad idea?

ORIGINALITY LINE:
What principle is inspired by history, and what protected surface is forbidden?

EARLIEST VALID PHASE:
When may this be implemented without violating the roadmap?

CHEAPEST EXPERIMENT:
What is the smallest test that could disprove it?

KILL CRITERION:
What evidence would make us archive it rather than rationalize it?
```

A poetic idea without a visible proof remains a mood. A technical idea without a player
promise remains infrastructure. Project Uppercut needs both halves.

---

## 4. The Blue Corner / Red Corner method

Every promising idea receives two short treatments.

### Blue Corner: the case for it

- What becomes more fun, readable, truthful, funny, or reusable?
- Which existing system becomes more expressive?
- What historical problem does it solve?
- Why would a player remember it?

### Red Corner: the case against it

- Does it duplicate an existing system?
- Does it secretly alter outcomes through presentation?
- Does it create a dominant style, hidden protection, or private rules?
- Does it require content scale before the core is proven?
- Is it merely a recognizable feature from another game wearing new names?
- Could a simpler version deliver the same promise?

An idea that survives both corners earns an experiment. It does not automatically earn a
roadmap slot.

---

## 5. A sustainable creative cadence

### Weekly: one seed, one contradiction

- Add one research or observation seed to a gallery.
- Write one Red Corner objection before celebrating it.
- Do not implement it unless it serves the active objective.

### At every phase gate: Gallery Night

Review the strongest unbuilt cards and ask:

1. Which one solves a newly visible player problem?
2. Which one reuses the most proven systems?
3. Which one demonstrates the product identity fastest?
4. Which one can be disproved cheaply?
5. Which one belongs later even if it is excellent?

Select at most one non-required idea for the next phase's experiment budget.

### Quarterly: repaint the horizon

Review `VISION.md` and this reservoir for:

- ideas now invalidated by evidence;
- ideas whose phase has arrived;
- repeated themes that reveal a missing pillar;
- areas receiving no creative attention;
- and attractive ideas that would pull the game away from its identity.

Archive deliberately. A graveyard of rejected ideas is evidence of judgment, not failure.

---

## 6. Historical research method

The project studies gaming history to understand solved problems, not to harvest
recognizable surfaces.

For each reference title, record:

1. **The production problem:** What constraint or audience need existed?
2. **The design answer:** What principle did the game use?
3. **The cost:** What weakness, limitation, or trade did that answer create?
4. **The Uppercut translation:** How can the principle be re-derived from boxing truth
   and current architecture?
5. **The hard NO:** Which names, characters, UI, audio, animations, wording, likenesses,
   or signature presentation may not cross?

Useful historical poles already in the repository include:

- `ready_2_rumble_design_study.md`: arcade comedy, personality, spectacle currency;
- the Fight Night study: simulation, embodied consequence, narrative ambition;
- the Tactic Boxing intake: CPU spectating and original roster, but a deliberately
  different ragdoll truth model;
- Punch-Out!! history: immediate legibility, simple surface, pattern recognition;
- modern fighting-game training: tutorials, missions, frame and input visibility,
  single-player learning journeys;
- rollback history: determinism as a prerequisite for responsive online play.

---

## 7. Creative seeds worth preserving

These are seeds, not commitments. Each must complete an Idea Card before entering a
phase.

### 7.1 Fight Fingerprint

After every bout, generate a compact visual and textual identity: pace, range, contact
map, bodywork, hand discipline, adaptations, knockdowns, referee events, and defining
moment.

**Why it matters:** One artifact serves spectators, training, rivalries, telemetry, and
future Career/Story.

### 7.2 The Ringside Desk

A pre- and post-fight presentation layer where original analysts discuss style tensions,
observable momentum, and uncertainty without accessing official cards.

**Why it matters:** Turns CPU vs. CPU into a program rather than a simulation window.

### 7.3 Replay Takeover

A training tool that returns a human player to the moment before a mistake and lets them
try another answer under the same authoritative state.

**Why it matters:** Converts explanation into practice while preserving one combat
system.

### 7.4 Boxing Grammar

A data-driven layer connecting phrases such as “stick and move,” “cut off the ring,” or
“work the body” to actual event patterns and training evidence.

**Why it matters:** The game's hidden boxing idioms become teachable without duplicating
combat rules in prose.

### 7.5 Commentary Uncertainty

Commentators carry estimates and confidence, not hidden truth. Their wording changes
based on evidence quality and disagreement.

**Why it matters:** Score isolation becomes audible drama rather than merely a security
boundary.

### 7.6 Intentional Silence

Certain knockdowns, injuries, and stoppages suppress queued comedy and commentary for a
measured beat.

**Why it matters:** Contrast gives both humor and seriousness more power.

### 7.7 Crowd Temperament

Events author crowd tastes: technical appreciation, hometown loyalty, appetite for
aggression, or suspicion of Showmanship. The crowd changes sound and meter opportunities
only through declared observable reward categories; it never changes judging or generic
stats.

**Why it matters:** Arenas gain identity without becoming hidden modifiers.

### 7.8 Referee Weather

Referee philosophy is disclosed before the fight and treated like weather: not destiny,
but a condition intelligent fighters account for.

**Why it matters:** Officials become meaningful and fair rather than random third
fighters.

### 7.9 The One-More-Round Rematch

A quick rematch package highlights what each CPU or human fighter learned from the prior
bout, while the new fight remains unscripted.

**Why it matters:** Rivalry emerges from adaptation and memory rather than cutscenes.

### 7.10 Style Tension Poster

Before a match, generate an original event card showing likely tactical questions rather
than win predictions: Can the Rusher close distance? Can the Drainer make misses pay?
Which hand becomes vulnerable during the jab?

**Why it matters:** Teaches spectators what to watch without revealing or manufacturing
outcomes.

### 7.11 The Honest Highlight Reel

Automated highlight selection uses authoritative event importance: knockdowns, clean
counters, ring escapes, bodywork turning points, referee interventions, and major
adaptations.

**Why it matters:** The same event record powers replays, trailers, and analysis without
hand-authored false drama.

### 7.12 Cornermen with Different Eyes

Corners observe the same fight through different expertise and chemistry. One notices
feet, another condition, another temperament. Advice confidence and relevance vary; no
corner reads official cards.

**Why it matters:** Character and learning systems deepen without violating score
isolation.

### 7.13 Venue as Instrument

Club, regional, championship, international, exclusive, and comedy events use different
camera density, acoustics, lighting, walkouts, crowd scale, and broadcast crews while the
fight core remains identical.

**Why it matters:** Reusable event modules create scale more cheaply than bespoke modes.

### 7.14 The Training Gym That Watches Back

The gym identifies repeated mistakes from event evidence and recommends a focused drill,
not a stat bonus.

**Why it matters:** Training responds personally without protecting the player in
competition.

### 7.15 Comedic Consequence Library

A library of original reactions triggered by truthful situations: a premature pose
interrupted by a jab, a corner stool nearly missed after a dizzy round, a referee's dry
look after repeated warnings.

**Why it matters:** Ready 2 Rumble spirit appears through consequence, not stolen gags or
broken physics.

### 7.16 Spectator Prediction Without Authority

Spectators may predict outcomes or turning points, but predictions are isolated from
judges, CPU, crowd rewards, and match state.

**Why it matters:** Adds social engagement without contaminating the ring.

### 7.17 The Fight as a Dataset and a Tale

Every match produces both machine-readable evidence and a short human-readable account.
The account must be generated from events, not invented over them.

**Why it matters:** Bridges engineering, commentary, accessibility, and future narrative.

### 7.18 Lateral Guard Geometry

The current per-hand mechanic captures vertical exposure. A later 2D body and hook model
can capture which side opened when the lead or rear hand left home.

**Why it matters:** Completes a boxing-truthful mechanic already discovered without
prematurely forcing it into the current one-dimensional slice.

---

## 8. Idea health checks

A healthy reservoir should contain all of the following:

- ideas that improve the next active slice;
- ideas deliberately deferred for later phases;
- ideas about humor, not only combat arithmetic;
- ideas about spectators, not only controllers;
- ideas about learning, not only winning;
- ideas about production reuse, not only features;
- ideas with explicit kill criteria;
- and archived ideas whose rejection teaches the next contributor something.

Warning signs:

- every new idea is another fighter;
- every problem is answered with a new meter;
- every presentation idea requests combat authority;
- every training idea changes competitive rules;
- every historical reference becomes a feature checklist;
- every technical finding triggers broad tuning before dependencies exist;
- or the repository grows faster in prose than the fight grows on screen.

---

## 9. The creative compact

> **Project Uppercut will not confuse discipline with dryness.**
>
> The active build stays narrow. The imagination stays wide. Research enters as a
> question, not a command. History lends principles, not costumes. Every idea must find
> a player promise, a boxing truth, a reusable system, a visible proof, and a reason it
> might deserve to die.

That is how the project keeps moving without becoming a parade of unfinished inventions.
