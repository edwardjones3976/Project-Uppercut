# Project Uppercut — “Fun Python Coding Ideas” Response Review

**Review date:** 2026-07-21 (America/Los_Angeles)  
**Conversation window:** 2026-07-22 01:29:47–06:36:29 UTC  
**Scope:** The latest 13 assistant responses concerning the boxing video game only. Unrelated boxing betting and settlement material is excluded.

> **Superseded on 2026-07-22:** The original phase order recorded below is retained as conversation history, but it is no longer authoritative. CPU vs. CPU simulation is now first, Human vs. CPU second, and career mode plus all related systems are deferred to the next version at its lowest priority. Project Uppercut uses one unified combat system; beginners and children learn through concise modular training rather than named player tiers or separate beginner systems. See [Decision 0001](../decisions/0001-simulation-first-unified-training.md).

## Executive review

The 13 responses form a coherent preproduction requirements baseline for an original arcade-boxing game currently called **Project Uppercut**. The strongest through-line is that boxing knowledge should be implemented as game logic rather than decorative flavor: the lore system, advice system, score isolation, anti-spam rules, commentary, time model, and attribute economy all reinforce that goal.

No implementation evidence was found. These responses describe proposed requirements and architecture, not completed code, assets, tests, or a playable build. The dedicated Project Uppercut repository now exists and preserves the evolving requirements.

The latest corrections supersede earlier flexibility in two areas:

1. The clock menu is now a simple **Accelerated Clock ON/OFF** control. ON means 3:00 displayed / 1:45 real; OFF exposes only 1 minute, 2 minutes, or authentic 3 minutes. There is no free-form time customization. Break skipping is chosen during each break, not configured before the match.
2. The attribute model retains the centered -100 to +100 give-and-take economy, but now also has explicit negative-trait safeguards and compensating-positive thresholds.

## Chronological response record

### 01 — Originality boundary and production foundation

**Timestamp:** 2026-07-22 01:29:47 UTC

- Framed the game as an original **spiritual successor**, not a literal Ready 2 Rumble clone.
- Required original characters, names, music, arenas, UI, announcer lines, artwork, assets, and code while preserving an arcade-boxing feel.
- Recommended Unreal Engine 5.8, Blueprints for prototyping, C++ for combat architecture, Python for tools/automation, GitHub as source of truth, and Blender for original assets.
- Proposed responsibilities: Ed as director; Codex for repo-wide implementation; Claude for architecture/review; Cursor for pair programming/debugging; Perplexity for research; Gemini for visual ideation; Virtual Desk for controlled GUI work.

**Review:** The legal/originality boundary is essential and should become a repository-level rule. The engine/tool selection is a proposal, not a verified setup.

### 02 — Detailed Project Uppercut foundation

**Timestamp:** 2026-07-22 01:32:09 UTC

- Named the working project **Project Uppercut**.
- Proposed a two-fighter vertical slice, data-driven combat, a Showtime/Crowd Heat meter, and styles-make-fights logic.
- Separated vitality, head, body, guard, balance, composure, and stamina rather than reducing combat to a single health bar.
- Included knockdowns/recovery, human-like CPU personalities, Arcade/Competitive/Party Chaos rulesets, and modular repo structure with `AGENTS.md`.
- Suggested Unreal systems including Gameplay Ability System, StateTree, Motion Matching, and Control Rig.

**Review:** This is a broad vision document. The vertical slice is the correct anchor, but the number of advanced engine systems should be reduced to only what the first playable slice proves it needs.

### 03 — Boxing Lore Engine

**Timestamp:** 2026-07-22 01:58:47 UTC

- Made boxing idioms operational inputs to combat logic, commentary, corner advice, CPU adaptation, judging, career development, and post-fight analysis.
- Defined a loop: live match event → tactical interpretation → relevant boxing principle → system response.
- Mapped idioms to gameplay rules, tactical-truth scores, and commentary categories.

**Review:** This is the project’s clearest differentiator. It should be a data-driven rules registry with explainable triggers, not scattered hard-coded sayings.

### 04 — Expanded Boxing Lore Registry

**Timestamp:** 2026-07-22 02:10:02 UTC

- Expanded canonical lore families:
  - **Jab control:** “Establish the jab,” “When in doubt, jab,” “The jab is the boss of the ring,” and “Everything comes off the jab.”
  - **Defensive purity:** “Hit and don’t get hit,” “Swim without getting wet,” and “You can’t hit what you can’t catch/find.”
  - **Body investment:** “Kill the body and the head will fall/die” and the body-as-a-bank principle.
  - **Initiative and exit:** “Get off first,” “Hit and move,” “Stick and move,” and “Be first, be sharp, be gone.”
  - **Preparation:** “Fights are won in the gym,” “Train hard, fight easy,” and “Roadwork wins fights.”
- Connected each family to mechanics, CPU strategy, corner advice, commentary, judging, career/training, post-fight analysis, fighter personality, and visual presentation.

**Review:** The registry needs canonical IDs and paraphrased/original presentation text so multiple sayings can point to one deterministic rule without duplicating logic.

### 05 — Tiny listening bonuses

**Timestamp:** 2026-07-22 02:20:49 UTC

- Allowed only minuscule rewards when a player correctly acts on valid live advice.
- Reliability order: corner is most trustworthy, commentary is indirect, crowd is least reliable.
- Named **Ring Awareness**, **Coachability**, and **Corner Chemistry** as governing traits.
- Capped direct combat benefit at roughly 2%–3% per round, with no farming, spam stacking, or official-score knowledge.

**Review:** Reward recognition and learning, but avoid invisible stat manipulation. The preferred implementation is bounded readiness/composure feedback with clear eligibility windows and telemetry.

### 06 — Original commentator ensemble

**Timestamp:** 2026-07-22 02:37:38 UTC

- Defined a rotating fictional broadcast organization rather than direct reproductions of real commentators.
- Required distinct facial structure, voice, biography, boxing background, commentary philosophy, humor, and emotional temperament.
- Proposed commentators including Martin Kessler, Walter “Walt” Keene, Elijah “Coach Eli” Booker, Graham Pike, Darnell “D-Price” Price, Rafael Rosario-De León, Tomás “Tomo” Salazar, Denise “D.J.” Jordan, Vivian Hart, Noah Adler, Mason Reed, Nia Franklin, Marisol “Mari” Rosario, Diego Valdés, Talia Brooks, and Jules “The Unicorn” Avery.
- Included Jules as a subtle LGBTQ-inclusive comic-relief personality while calling for respectful characterization rather than caricature.

**Review:** The ensemble is unusually deep for an MVP and presents major writing, casting, recording, localization, memory, and line-collision costs. Build the roster data model now, but produce only a minimal crew for the vertical slice.

### 07 — Score Isolation Principle / Judge Firewall

**Timestamp:** 2026-07-22 02:47:34 UTC

- Established **Rule 001 / Engine Law 004**: official scorecards remain inaccessible to fighters, CPU, trainers, commentators, crowd, replay, difficulty, and adaptive AI during the contest and immediate post-fight flow.
- Limited live official-score access to Judge AI, the Referee when required, and the Match Controller.
- Required CPU fighters and presentation systems to use observable events and imperfect estimates containing score, confidence, and uncertainty.
- Early stoppages terminate scoring; the result appears first, while partial cards remain sealed through the quick-menu/stats flow and may be revealed later in an archive/replay context.
- Prohibited score-driven rubber-banding.

**Review:** This should be enforced by module/API boundaries and automated access tests, not merely by convention. The wording about replay access needs a lifecycle distinction: live replay presentation cannot read cards; post-fight archival review may after the reveal gate.

### 08 — Locked development order

**Timestamp:** 2026-07-22 03:11:48 UTC

- Locked the order: **Human vs. CPU MVP → Human vs. Human → complete CPU vs. CPU simulation → Career → Online → Future updates**.
- Required quality gates between phases.
- Identified shared foundations: deterministic combat, judge subsystem, score firewall, commentary bus, replay logs, and automated combat tests.
- Kept early stoppages, post-fight quick menu, and match statistics in the early MVP scope.

**Review:** This order is coherent, especially requiring complete CPU-vs.-CPU simulation before career. “Complete” needs measurable exit criteria so that career mode is not blocked indefinitely.

### 09 — Anti-spam and exploit law

**Timestamp:** 2026-07-22 03:29:59 UTC

- Distinguished strategically earned repetition from spam. Repeated jabs, body work, pressure, or counters remain legitimate when the opponent fails to answer them.
- Targeted one-move loops, safe-animation abuse, stun loops, clinch abuse, running, and meter farming.
- Proposed pattern tracking for attack frequency, entries/exits, favorite combos, target preference, defensive reactions, dodge direction, rope behavior, clinch frequency, signature use, and timing.
- Made predictable play increasingly readable, tiring, positionally costly, and counterable through shared boxing logic rather than hidden nerfs.
- Required CPU and human players to obey the same rules; corner/commentary should recognize repeated patterns.

**Review:** This is compatible with the lore and AI systems. Pattern confidence and counter availability need deterministic telemetry tests to prevent unfair input-reading or sudden difficulty spikes.

### 10 — Commentary crew scaling and themes

**Timestamp:** 2026-07-22 03:53:08 UTC

- Crew size: 4/6-round fights = one commentator; 8/10-round fights = two; 12-round or championship fights = three. Championships always receive three even when scheduled below 12 rounds.
- Allowed any commentator pairing, guided by chemistry/relationship values rather than hard incompatibilities.
- Proposed Latin Fight Night, Black History Month, Championship Crew, Technician’s Table, Pure Entertainment Crew, Rules and Controversy Desk, Next Generation Crew, and Women in Boxing events.
- Suggested auto, manual, random, or career-promoter selection while accounting for expertise, freshness, role relevance, relationship value, timing, and silence priority during knockdowns/stoppages.

**Review:** Crew scaling is clear. Themed crews should influence selection and editorial focus without restricting individuals to identity-based events or creating tokenized presentation.

### 11 — Accelerated fight clock and between-round flow

**Timestamp:** 2026-07-22 04:27:37 UTC

- Defined the default clock as 3:00 displayed while 1:45 elapses in real time, a scale of 180 / 105 = 1.7142857.
- Required all match systems to read one synchronized authoritative fight clock.
- Set breaks to 30 real seconds; menu/stat access does not pause the break countdown.
- Allowed break skipping; Human vs. Human requires both users to approve.

**Review:** The single authoritative clock is correct. Presentation, stamina, judging windows, commentary cooldowns, replay timestamps, and online synchronization must all distinguish displayed fight time from wall-clock time.

### 12 — Centered give-and-take fighter attributes

**Timestamp:** 2026-07-22 04:35:32 UTC

- Proposed internal attributes from -100 to +100, with 0 as balanced, positive values as advantages, and negative values as disadvantages.
- Set the ordinary roster’s total attribute budget at 0 and discouraged a single overall rating.
- Added escalating costs for extremes: 0–25 = 1.0, 26–50 = 1.2, 51–75 = 1.5, and 76–100 = 2.0.
- Suggested at most one +100 attribute and at most two attributes above +70.
- Made synergy and friction between physical/technical traits part of effectiveness.

**Review:** The concept is strong, but a raw arithmetic sum and a weighted nonlinear budget are different rules. The schema needs one canonical budget formula plus validation fixtures showing legal and illegal fighter builds.

### 13 — Final clock and negative-attribute corrections

**Timestamp:** 2026-07-22 06:36:29 UTC

- Superseded broad clock customization:
  - Accelerated Clock **ON** = displayed 3:00 / real 1:45.
  - Accelerated Clock **OFF** = dropdown containing only 1 minute, 2 minutes, or authentic 3 minutes.
  - No custom time values.
  - Break skipping is an in-match choice, not a pre-match setting.
- Added negative-attribute safeguards:
  - No more than one attribute at -100.
  - No more than two related attributes below -30.
  - No fighter may have every physical trait negative.
  - No fighter may have every technical trait negative.
  - No more than three attributes below -40 overall.
  - Every attribute below -40 needs a meaningful compensating positive.
  - -41 to -60 requires at least +30; -61 to -80 requires at least +50; -81 to -100 requires at least +70.
  - Severe negatives must create visible gameplay consequences.

**Review:** These corrections are now authoritative. “Related attributes,” “physical,” “technical,” and the link between a negative and its compensating positive must be explicit data, not inferred from names.

## Consolidated requirement status

| Area | Status after response 13 | Review disposition |
|---|---|---|
| Originality | Original spiritual successor; no copied audiovisual package | Binding project rule |
| Engine/tooling | UE 5.8 + Blueprint/C++ + Python proposed | Validate before scaffolding |
| First functional priority | CPU-vs.-CPU simulation foundation | Supersedes the original H-v-CPU-first plan |
| Lore | Data-driven boxing principles affect mechanics and presentation | Core differentiator |
| Advice rewards | Tiny, valid-action-only, non-stackable | Needs visible/telemetric rules |
| Scorecards | Strict live isolation with gated later reveal | Binding engine law |
| Anti-spam | Shared, readable pattern adaptation; no hidden punishment | Binding combat law |
| Phase order | CPU-v-CPU → H-v-CPU → H-v-H → Online/polish | Career deferred to the next version at lowest priority |
| Learning model | One unified combat system with concise modular training | No named player tiers or separate beginner engine |
| Commentary | Scaled 1/2/3-person crews; broad original ensemble | Data model now; content later |
| Clock | Accelerated toggle or fixed 1/2/authentic options | Latest response supersedes prior flexibility |
| Breaks | 30 real seconds; live menu/stats; per-break skip; dual consent in PvP | Binding flow rule |
| Attributes | Centered -100…+100, nonlinear budget, caps and compensation | Needs canonical validator |

## Main risks and contradictions to resolve

1. **Design scope exceeds MVP production capacity.** The full commentary cast, themed crews, lore breadth, multiple modes, motion systems, and career/online ideas should remain data-model compatible but outside the initial content budget.
2. **The attribute budget is not fully specified.** A total raw sum of zero can conflict with weighted extreme costs. Adopt one explicit formula and test examples.
3. **Advice bonuses may feel hidden or unfair.** Keep them small, observable in telemetry, non-stackable, and unable to overcome poor execution.
4. **Score isolation must be architectural.** Direct references to the Judge subsystem should be impossible from CPU, commentary, crowd, difficulty, and live replay modules.
5. **Anti-spam must not become input reading.** Recognition must use observable history, confidence thresholds, reaction latency, and shared rules.
6. **Time has two representations.** Every subsystem must declare whether it consumes authoritative fight time, displayed time, or wall-clock time.
7. **Originality requires ongoing review.** Fictional fighters, commentators, dialogue, presentation, likeness, music, and arenas need provenance and similarity checks.

## Recommended next repository actions

1. Add data schemas for lore rules, fighter attributes/families, commentator profiles/relationships, match clock configuration, observable fight events, CPU policies, and training modules.
2. Add validator/test specifications before gameplay code:
   - official-score access denial tests;
   - legal/illegal fighter-build fixtures;
   - accelerated-clock synchronization tests;
   - dual-consent break-skip tests;
   - repetition-versus-spam behavior tests;
   - advice bonus cap/stacking tests.
3. Define CPU-vs.-CPU simulation exit criteria before Human-vs.-CPU work.
4. Define modular training acceptance criteria alongside Human-vs.-CPU controls.
5. Keep all career-mode work out of Version 1 planning and implementation.

## Evidence limitation

This document is a faithful reconstruction of the 13 retrieved response records and their binding decisions. It is a review of conversation history, not proof that any proposed implementation exists.
