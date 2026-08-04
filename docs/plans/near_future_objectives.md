# Near-Future Objectives — From Proven Machinery to a Living Bout

This is an outcome ladder, not a dated forecast and not a second status file.

- Current volatile facts belong in `/STATUS.md`.
- Binding constraints belong in `/PROJECT_RULES.md`.
- Phase order and quality gates belong in `/ROADMAP.md`.
- Accepted architecture belongs in `/docs/decisions/`.
- The end-state picture belongs in `/VISION.md`.

This document answers one narrower question:

> **What are the next visible outcomes that turn the present combat machinery into
> the first complete, watchable Project Uppercut experience?**

The objectives are dependency-ordered. A later objective may be prepared, but it does
not become the active implementation priority until the earlier evidence gate closes.

---

## 1. The current crossing

The project has already proven a deterministic C++ fight core, movement and range,
punch geometry, rendered animation, guard and slip, regional condition, audited assets,
and presentation with no authority over the result. The current crossing is harder and
more valuable:

`exchange simulation → complete boxing contest`

The gap is not another punch type or another reference document. It is the connected
chain from tactical choice to contact quality to accumulated condition to knockdown,
count, recovery, stoppage or cards, and post-fight explanation.

The latest design work also exposed three facts that control the order:

1. **Defense is per hand.** A committed fighter may vacate one defensive lane while the
   other hand remains home. Treating commitment as a whole-body switch erased that
   distinction.
2. **Contact quality is necessary but not sufficient.** Brushed, grazed, solid, and
   clean contact restore the force spectrum, but random action selection still produces
   non-boxing work rates and invalid balance conclusions.
3. **CPU decision policy must precede final knockdown tuning.** Thresholds calibrated
   against fighters who pace, protect themselves, reset, and respond to hurt states
   cannot be judged against fighters choosing uniformly from an action list.

These are not detours. They are the narrow bridge to a truthful round.

---

## 2. Horizon One — Make defense and decision-making real

### Objective 1: Land per-hand guard truth in the authoritative core

**Product statement:** A fighter caught mid-punch is exposed where the committed hand
left, while the free hand may still catch or degrade the incoming shot.

**Required implementation proof**

- Per-hand defensive availability derives from existing move-hand and punch-height data.
- No posture-name branching enters collision authority.
- No new random guard roll is required.
- Free-hand coverage retains its authored extent.
- Vacated-hand coverage uses the committed-defense consequence already in canon.
- Same seed and initial state remain byte-identical across processes and rebuilds.
- A frozen-phase evidence pin prevents historical analyzers from being silently changed.

**Player-visible proof**

- A jabber can throw while keeping the rear hand meaningfully useful.
- A fighter who sends the covering hand away creates a readable counter lane.
- The replay can identify which hand was committed and which hand intercepted.

**Failure conditions**

- Commitment removes all defense regardless of hand position.
- Both hands defend at full strength while one is visibly punching.
- Guard success is restored only by hidden probability without geometric explanation.
- Per-hand logic becomes a character-specific exception rather than a reusable rule.

### Objective 2: Put an observable CPU policy into the rendered core

**Product statement:** Fighters stop behaving like dice with gloves and begin behaving
like tactical personalities.

The minimum policy does not need final intelligence. It needs visible boxing purpose.

**Observable inputs only**

- current and recent range;
- stamina and regional condition;
- guard posture and hand availability;
- opponent's recent actions and repeated patterns;
- rope and corner position;
- current commitment and recovery;
- visible knockdown or hurt state;
- referee warnings and disclosed tendencies;
- remaining authoritative round time;
- Crowd state without official scores.

**Minimum tactical behaviors**

- approach or hold range with purpose;
- protect a hurt region;
- stop throwing when recovery is required;
- pressure an opponent on the ropes;
- reset after an inefficient exchange;
- attack an observable open lane;
- vary repeated offense when the opponent demonstrates a read;
- respond differently to fresh, tired, hurt, and desperate situations;
- preserve the six generic stress-profile identities without hardcoding outcomes.

**Engineering proof**

- Policy decisions carry a reason code into the event stream.
- Policies cannot import or receive sealed scorecards.
- A same-seed run reproduces decisions and outcomes.
- Batch reports distinguish tactical causes from raw action frequency.

**Player-visible proof**

A spectator can watch two generic profiles and describe their plans without reading their
labels.

**Failure conditions**

- The CPU reads human inputs, future actions, random draws, or official cards.
- Difficulty changes damage, collision, stamina, or timing truth.
- Every profile converges on the same highest-frequency move loop.
- “Adaptation” is merely a hidden anti-spam penalty.

---

## 3. Horizon Two — Complete the first truthful round

### Objective 3: Resume and pass the held full-round contract

**Product statement:** Accumulated condition finally has somewhere to go.

The complete round chain must include:

1. bell and authoritative clock;
2. tactical decisions;
3. movement, range, and contact;
4. contact-quality grading;
5. per-region consequence;
6. hurt and knockdown pressure;
7. knockdown animation and authoritative count;
8. mandatory recovery rules;
9. partial relief without magical restoration;
10. referee judgment and rule-based stoppage;
11. round closure and sealed card;
12. between-round partial recovery;
13. continuation, decision, or stoppage verdict.

**Required invariant**

The decision path must survive. A valid model may produce early stoppages, but it may not
turn every representative bout into a first-round stoppage.

**Engineering proof**

- Knockdowns emerge from observable force, placement, balance, awareness, and condition,
  never a flat knockout roll.
- Count timing uses one authoritative clock.
- Three-in-a-round and bout-level knockdown limits behave as declared.
- Referee stoppages consume visible evidence and shared rules.
- Judges receive only witnessed facts through the score firewall.
- Cards remain sealed until the permitted reveal.
- The Python reference and C++ core agree at the phase's declared evidence boundary.

**Player-visible proof**

A spectator can distinguish:

- a flash knockdown from accumulated deterioration;
- a fighter rising hurt from a fighter recovering cleanly;
- a referee stoppage from a count-out;
- a close round from a dominant one;
- and a decision from a failure of the knockout system.

**Failure conditions**

- Every landing is treated as full-quality contact.
- Every bout stops before tactical adaptation can matter.
- Recovery erases the fight's history.
- Presentation timing disagrees with the authoritative count.
- A dramatic camera or animation changes the underlying result.

### Objective 4: Add one controlled proof of the game's soul

The first complete round should not wait for final polish to test the project's identity.
Add only a thin presentation layer sufficient to answer whether truthful boxing can also
be lively.

**Minimum soul proof**

- one original commentary voice;
- one deliberate silence during a decisive event;
- one crowd escalation driven by observable action;
- one character-neutral comic reaction or arena beat;
- one impact presentation package with audio, pose, camera, and pause aligned to the
  authoritative contact;
- one replay explanation of the decisive exchange.

**Boundary**

None of these may change collision, force, condition, cards, CPU knowledge, or outcome.

**Director review questions**

- Did the exchange feel immediate?
- Did it look faster than it mechanically was?
- Could the decisive contact be read?
- Did the comedy sharpen the moment rather than interrupt it?
- Did the round breathe?
- Would someone willingly watch another seed?

Automated checks can protect truth. This review protects taste.

---

## 4. Horizon Three — Turn the round into a product loop

### Objective 5: Complete the smallest end-to-end CPU bout experience

**Entry**

- choose two generic stress profiles;
- choose or disclose event class, referee, round count, and clock mode;
- show style tensions without revealing outcomes or official-score information.

**Fight**

- complete match flow;
- round transitions;
- knockdowns, counts, recovery, stoppages, and decisions;
- readable broadcast camera;
- basic crowd and commentary behavior;
- deterministic event record.

**Exit**

- result presentation;
- statistics;
- fight fingerprint;
- replay access;
- event explanation;
- quick rematch, new seed, or new matchup.

**Product proof**

A person who did not build the engine can launch the experience, select a matchup, watch
a complete contest, understand the result, and choose to watch another without opening a
debug console.

### Objective 6: Pass the Phase 1A gate honestly

The gate is not passed because the underlying systems exist separately. It is passed when
the complete experience meets the `ROADMAP.md` criteria together.

Before declaring Phase 1A complete, require:

- complete selection-to-post-fight flow;
- no hidden CPU knowledge;
- no known dominant exploit loop;
- explainable replay and judging events;
- Director-approved visual readability;
- viable aggression and viable patient stamina control;
- legitimate routes for all six stress profiles;
- telemetry that names weak, dominant, or inert mechanisms;
- status generated from current evidence;
- and no rule, decision, or phase record contradicted by stable documents.

---

## 5. Horizon Four — The first character-complete painting

### Objective 7: Begin Adewale vs. Calvin only after the generic gate

The first named pairing should prove that character identity can inhabit shared boxing
truth without hiding system faults.

### Adewale “The Fine Print” Balogun should reveal

- timing;
- structure;
- Ringcraft;
- disciplined pressure;
- range accounting;
- pattern recognition;
- efficient counters;
- and the feeling that every exchange has terms and conditions.

### Calvin “The Host” Givens should reveal

- speed;
- combination flow;
- Showmanship;
- evasive exits;
- crowd fluency;
- rhythm disruption;
- social command of the arena;
- and the danger of entertaining himself into an opening.

### Character-complete proof

Each receives:

- authored attributes and at least fifteen meaningful traits;
- distinct CPU policy parameters;
- two counterable Specials;
- one counterable Ultimate;
- one Full-Crowd Trait;
- entrance and commentary hooks;
- visible liabilities;
- and a fight fingerprint recognizably different from the other's.

The shared core must explain their differences. Private physics or hidden exemptions are
a failure.

---

## 6. The near-future “not now” wall

Ideas are welcome. Implementation remains gated.

Do not divert the active slice into:

- a larger roster;
- Career or Story systems;
- online networking before local combat is complete;
- final matchmaking policy;
- economy, scheduling, or progression;
- additional reference studies with no active design question;
- cosmetic quantity before one presentation package is readable;
- new guard names before current guard geometry works end to end;
- broad tuning against random-action CPU behavior;
- or status prose that duplicates generated facts.

New ideas belong in `docs/design/idea_flywheel.md` until their earliest valid phase
arrives.

---

## 7. Definition of near-future success

The project has crossed the near-future bridge when the following sentence is true:

> **Two generic fighters can enter a real ring, choose actions for observable boxing
> reasons, defend with the hands they visibly have available, exchange graded contact,
> accumulate localized consequence, survive or fail a truthful count, reach either a
> stoppage or sealed decision, and leave behind a replay that explains the story — all
> while the presentation makes someone smile and never changes a single fact.**

That is the next canvas. Everything after it has somewhere solid to stand.
