# Project Uppercut — 90-Day Execution Plan

**Quarter:** Monday 2026-08-03 → Sunday 2026-11-01 (13 weeks)
**Plan status:** v0.3 — committed at the Director's request as a corrected execution proposal. Supersedes v0.1 and v0.2 in full; proposed objectives and calendar targets still require Director ratification.
**Scope of authority:** none. This is a dated execution schedule, not doctrine.

> **Authority stack (per PROJECT_NOTES.md, "Document authority and maintenance"):**
> `PROJECT_RULES.md` (binding constraints) → `PROJECT_NOTES.md` (canonical operating brief) → `docs/decisions/` (accepted decisions 0001–0005) → `ROADMAP.md` (fixed development order, deliverables, quality gates) → **this plan** (calendar forecast and task breakdown for the next 90 days).
> Where this plan conflicts with anything above it, the plan is wrong and gets amended. The latest explicit Director correction controls.

---

## 1. Current state — facts as of 2026-08-02

- The repository `edwardjones3976/Project-Uppercut` is live on `main` (private) with the canonical documents in place: `PROJECT_NOTES.md` (authoritative operating brief), `PROJECT_RULES.md` (binding rules), `README.md`, `ROADMAP.md` (Phases 0–5 with quality gates), decisions 0001–0005, and the development-log consolidations. The current repository documents were verified by remote readback on 2026-08-02 while preparing this revision; individual historical commit hashes are intentionally not treated as a permanent statement of repository head.
- **ROADMAP.md Phase 0 — Preproduction and requirements consolidation: in progress.** That is the project's true current phase, and this plan schedules work accordingly.
- Per Rule 18, design documentation is not implementation evidence: **no Unreal project, playable build, combat code, or test suite exists yet, and none is claimed.**
- The intended local working folder is `C:\Users\edwar\project-uppercut`. This plan does not claim that folder is already a verified clone; cloning and remote-state verification are scheduled in Week 1 (T0.1).
- Plan v0.1 was reviewed at roughly 70% alignment and is retracted. Its imported assumptions — a non-canonical meter name, scorecard-aware CPU logic, a four-archetype launch roster, a hard numeric balance band, a language-first tech recommendation, presumed ownership splits, and a presumed tagging rule — are all withdrawn. Appendix A records the disposition of every review finding.

## 2. What this quarter is

This quarter executes the ROADMAP, in its fixed order, against the calendar:

1. **Finish Phase 0 (Foundation) and pass its quality gate.**
2. **Build Phase 1A (generic CPU vs. CPU combat sandbox) and drive it to its quality gate.**
3. **Enter Phase 1B (Adewale vs. Calvin vertical slice) only if the 1A gate passes**, and only with preparation work that does not outrun the gate.

Phase 1A and Phase 1B are execution-plan subdivisions of canonical ROADMAP Phase 1. They do not amend the fixed development order.

Phase boundaries are governed by quality gates, not dates. The calendar in §5 is a forecast for planning Director time; **when evidence and the calendar disagree, the gate wins and the dates move** (Rule 18: no claimed progress without repository evidence).

CPU vs. CPU is both the first engineering laboratory and a first-class way to experience the game. The quarter's end state, if the forecast holds: complete, deterministic, explainable, watchable CPU-vs-CPU matches between generic test fighters, with batch telemetry and balance evidence — the foundation the entire product sentence stands on.

## 3. Objective candidates for Director development

PROJECT_NOTES.md states the product sentence "provides the seed for the future objectives section." The objectives below are **derived from that sentence and the operating model; they are a proposal, not doctrine, until the Director ratifies or rewrites them.**

The sentence commits the product to: a comedy-first, character-based arcade-boxing game; five audiences (children, beginners, boxing fans, spectators, experienced competitive players); one skill-based combat system; and three uses of that system — CPU-controlled fights, focused training modules, progressively deeper human competition without weakening advanced play. This quarter serves the first use directly and protects the other two structurally.

| # | Proposed objective | Serves (sentence / roadmap) | Measurable exit |
|----|--------------------|------------------------------|-----------------|
| PO1 | **Phase 0 gate passed** | Foundation for every clause | All Phase 0 quality-gate items checked: originality rules documented; scorecard-access boundaries documented and testable; one canonical attribute-budget formula chosen; legal/illegal fighter-build fixtures specified; sandbox and vertical-slice acceptance criteria approved separately; game-feel and style-viability laws accepted |
| PO2 | **Phase 1A minimum scope running** | "simulate CPU-controlled fights" | Complete CPU vs. CPU matches from selection through post-fight flow; two CPU fighters using observable information only; deterministic Judge subsystem behind the score firewall; authoritative clock with 30-second breaks; results, statistics, replay/event log; batch simulation and telemetry tooling |
| PO3 | **Evidence rig green** | competitive fairness; "resistant to spam or hidden CPU advantages" | The ROADMAP's required automated checks all run and pass: score-access denial, accelerated-clock sync, repetition-vs-spam, attribute fixtures, knockdown/stoppage/result states, determinism and seeded replay, large-batch invalid-state and deadlock, First Bell Firestorm, Long Drain, style-viability and dominant-loop, Crowd-farming prohibition |
| PO4 | **Watchable and explainable** | spectators; comedy-first identity's foundation | A spectator can watch a sandbox bout and understand decisive exchanges (game-feel hierarchy holds even in sandbox visuals); replay/event logs explain major combat and judging events; fighter personality and tactical tendency are visible in observable events, giving later comedy and commentary truthful material to build on |
| PO5 | **One-system law future-proofed** | training modules; deeper human competition | Phase 0 schemas and 1A architecture permit declared mode configurations, accessibility presentation, and training conditions while prohibiting separate combat engines, hidden player-tier rules, or incompatible physics, damage, scoring, and move systems — proven by schema design and validator coverage, not by building Phase 2 early |

## 4. Workstreams

Owners are **deliberately unassigned**: the canonical documents establish no contributor division of labor, so per-task assignment is the Director's call (§9, open item 2). Task IDs carry ROADMAP traceability.

### WS0 — Repository and working environment *(Phase 0)*

- **T0.1** Clone the repo into the local working folder and verify the root `PROJECT_PLAN.md` plus canonical documents against remote `main` before implementation begins.
- **T0.2** Repository conventions and contribution guidance (Phase 0 deliverable): branch model, issue labels per workstream, decision-log workflow in `docs/decisions/`, evidence-artifact conventions (where batch reports and replay logs live so gate reviews cite commits, not claims).
- **T0.3** Confirm Unreal Engine and supported tool versions as the default technical baseline (Phase 0 deliverable); record as a pinned-versions doc. Decision 0002 stands: Unreal-first, Blueprints for early prototyping, Python for tools/analysis, C++ later where performance, determinism, networking, or architecture justifies it; C# has no role unless the engine changes.
- **T0.4** Continuous checks for what CI can honestly cover now: GitHub Actions running the Python-side validators, schema tests, and fixture suites on every push. In-engine automation initially runs as scripted local batch runs whose output artifacts are committed as evidence; hosted UE automation is revisited when C++ modules justify the infrastructure.

### WS1 — Canonical data schemas *(Phase 0)*

- **T1.1** Schemas for: fighter attributes and attribute families (centered −100…+100 economy); boxing lore (canonical data-driven rules; sayings reference principles, never duplicate combat rules — Rule 2); move startup, active contact, recovery, guard interaction, counter exposure, and positional consequence; clean, solid, grazed, brushed, blocked, dodged, and whiffed contact; localized target and condition state; stance familiarity and ambidexterity; Specials, Ultimates, Full-Crowd Traits, and Crowd events; observable fight events; referee evidence and decisions; commentary profiles and commentator relationships; clock settings; match results; CPU decision reasons; and style stress profiles.
- **T1.2** Attribute-budget validator implementing Rule 10 exactly: give-and-take economy; positive caps (one +100 max, two >+70 max); negative safeguards (one −100 max, two related <−30 max, no all-negative physical or technical family, three <−40 max, compensation ladder −41/−60→+30, −61/−80→+50, −81/−100→+70); escalating budget costs; explicit attribute families and compensating relationships as data.
- **T1.3** Legal and illegal fighter-build fixtures (Phase 0 gate item) exercising every cap and safeguard above.
- **T1.4** *Phase-timing decision for Director approval:* the referee system itself is already canonical. Decide whether its full profile schema—enforcement-philosophy parameters for the six serious officials and the non-Ranked comic-relief official—must be completed in Phase 0 or whether Phase 0 defines only the minimum contract needed for Phase 1A provisioning.

### WS2 — Validators and templates *(Phase 0)*

- **T2.1** Automated validators before any roster balancing (Phase 0 deliverable).
- **T2.2** Templates: move-table, fighter-card, matchup-matrix, simulation-report, playtest, decision-log, attribute-budget.
- **T2.3** Asset compatibility audit checklist: license, modification rights, skeleton, retargeting, root motion, performance, network suitability, visual consistency, engine support, maintainability (Rule 22 — required before any licensed asset enters).

### WS3 — Acceptance criteria and Phase 0 gate *(Phase 0, Director-approval-heavy)*

- **T3.1** Generic technical sandbox acceptance criteria, drafted for Director approval.
- **T3.2** Character vertical-slice acceptance criteria for Adewale "The Fine Print" Balogun and Calvin "The Host" Givens, approved **separately** (prototype-separation principle: shared-system faults must stay distinguishable from character-specific faults).
- **T3.3** Phase 0 quality-gate review session; every gate item closed with linked evidence.

### WS4 — Phase 1A combat core *(Phase 1A)*

Built in the ROADMAP's required implementation order, in-engine, prototyped Blueprints-first:

1. combat-state definitions
2. movement and facing
3. camera behavior
4. animation states
5. hitboxes, hurtboxes, guard regions, and collision truth
6. basic punches
7. guard and evasion
8. stamina, health, body/head condition, knockdowns, and recovery
9. CPU decision-making using observable information only
10. deterministic simulation logging and replay evidence
11. Crowd Bar architecture
12. Special, Full-Crowd Trait, and Ultimate architecture

Standing constraints from the canon, binding on every step: counterplay from the first punch (every attack defines startup, active contact, recovery, range, stamina cost, guard interaction, hit reaction, counter vulnerability, positional consequence); the Elastic Footwork System as one continuous threat-responsive model — no ice skating, magnetic range correction, invisible lunges, or body overlap; feet → position → range → contact → consequence; contact classification (clean, solid, grazed, brushed, blocked, dodged, whiffed) with blocked < dodged < whiffed commitment cost; condition modeled per region (head, jaw/chin, per-eye, torso, per-arm/guard, stamina, balance, guard, Composure, Chin, Durability, Recovery) — no single generic health bar; Chin +100 = maximum authored resistance, never invulnerability, and no flat per-punch knockout roll; stance switching for every fighter with authored non-ambidextrous penalties and a small exclusive ambidextrous set; at a full Crowd Bar the fighter chooses Ultimate **or** Full-Crowd Trait, never both from one bar; numerical multipliers remain tuning hypotheses until validated (Rule 18).

- **T4.A** Determinism approach in Unreal validated early (this is the load-bearing technical-sandbox question): authoritative fixed-tick simulation state, a single seeded RNG service, and event-sourced logs. Deterministic resimulation means the same seed and authoritative initial state reproduce the same authoritative event log. Replay means the saved event log reproduces the recorded presentation without rerunning uncertain CPU or judging decisions. If Blueprint-tick behavior cannot hold deterministic resimulation, C++ enters for the sim core earlier than otherwise planned—an accepted Rule 22 trigger, to be evidenced rather than assumed.
- **T4.B** Judge subsystem and Match Controller behind the score firewall (Rule 3): during the fight and immediate post-fight flow, official cards unreadable by fighter logic, CPU logic, referees, corners, commentary, crowd, difficulty, live replay presentation, and advice systems; those systems form estimates from observable events only, with explicit uncertainty; early stoppages terminate scoring; partial cards sealed through the immediate result flow.
- **T4.C** Authoritative fight clock: one synchronized clock read by all systems; Accelerated Clock toggle semantics (ON: display 3:00 over 1:45 real; OFF: 1, 2, or authentic 3 minutes only — no free-form customization); 30-second real between-round breaks that menus don't pause.
- **T4.D** Referee architecture provisioning (scope-honest): assignment slot, disclosure-before-fight, enforcement-philosophy hooks around clinches, fouls, warnings, deductions, injuries, and stoppages, bound by the universal knockdown-count clock and medical minimums, with no access to scores and no power to alter damage, stamina, collision classification, Crowd gain, attributes, input responsiveness, or judging criteria. Full six-official behavioral depth and the non-Ranked comic-relief official (Elliot "Eventually" Ames — implication implied, never canonically stated) are content that lands as the sandbox and vertical slice mature; the architecture lands now.

### WS5 — Evidence rig and balance instruments *(Phase 1A)*

- **T5.1** Batch simulation and telemetry tooling (Python): N×N stress-profile round-robins across seed sweeps; simulation-report generation from the Phase 0 template.
- **T5.2** The six generic CPU stress profiles as balance instruments, not roster classes: Rusher, Drainer, Technician, Counterpuncher, Showman, Power Threat.
- **T5.3** The ROADMAP's required automated checks, wired to run on every meaningful change: score-access denial; accelerated-clock synchronization; repetition-versus-spam behavior (targeted abuse list: one-move loops, safe-animation abuse, stun loops, clinch abuse, excessive running, passive blocking abuse, meter farming — punished through observable boxing logic, never hidden rules); legal/illegal attribute fixtures; knockdown, stoppage, and result states; determinism and seeded replay; large-batch invalid-state and deadlock; **First Bell Firestorm** (effective opening aggression can win; volume-only dominance cannot); **Long Drain** (patient stamina control can win; empty avoidance cannot); style-viability and dominant-loop detection; Crowd-farming and generic-boost prohibition.
- **T5.4** Balance evidence standard (per Rule 21 — replaces v0.1's numeric band): every major style keeps a legitimate, executable route to victory; reports flag **inexplicable dominance** (outcomes not explainable from observable mechanics), **absent counterplay**, dominant loops, and ineffective traits. Lopsided win rates are findings to explain, not automatically failures: asymmetry earned through style, stance, condition, or referee context is legitimate. Dominant extremes and nonviable styles are Phase 1A gate failures.

### WS6 — Watchability *(Phase 1A)*

- **T6.1** Sandbox presentation sufficient for a spectator to follow a bout and understand decisive exchanges — the gate's readability item, honored with sandbox-grade visuals (generic fighters, minimal arena; entrances, commentary crews, and full presentation belong to later phases).
- **T6.2** Observable personality: tactical tendencies, Showmanship, composure, and adaptation visible in events and logs — the truthful substrate that later comedy, commentary, and crowd presentation build on (comedy is the highest presentation priority of the product; this quarter lays its mechanical foundation rather than its content).

## 5. Calendar forecast — 13 weeks

**Forecast, not commitment: gates govern.** Sized so one zero-touch week does not break the quarter.

| Sprint | Weeks | Dates | Focus | Target evidence at exit |
|--------|-------|-------|-------|-------------------------|
| **A — Foundation build** | W1–W2 | Aug 3 – Aug 16 | T0.1–T0.4; schema drafts (T1.1); budget-formula candidates (T1.2); fixture specs (T1.3); templates (T2.2); audit checklist (T2.3); acceptance-criteria drafts (T3.1, T3.2); referee-schema proposal decision (T1.4) | Repo cloned and conventions live; validators running in Actions; drafts ready for Director review |
| **B — Phase 0 gate** | W3 | Aug 17 – Aug 23 | Director review week: budget formula chosen; fixtures approved; both acceptance-criteria sets approved separately; gate checklist closed (T3.3) | **Phase 0 quality gate: PASS target Aug 23** |
| **C — Sandbox core** | W4–W8 | Aug 24 – Sep 27 | WS4 in required order; determinism validation first (T4.A); firewall + clock (T4.B, T4.C); referee provisioning (T4.D); evidence rig grows alongside (T5.1, T5.3 subset) | First complete deterministic CPU vs. CPU match with replay (forecast: ~Sep 13); batch runner producing reports by Sep 27 |
| **D — Evidence and balance** | W9–W11 | Sep 28 – Oct 18 | Six stress profiles (T5.2); full check suite green (T5.3); balance reports and explainability passes (T5.4); watchability pass (WS6); exploit hunts | **Phase 1A quality gate: review target Oct 18** |
| **E — Gate remediation / 1B prep** | W12–W13 | Oct 19 – Nov 1 | Fix gate findings. Only if 1A passes: Phase 1B preparation that respects prototype separation — authored data for Adewale and Calvin run against validators; no character combat code ahead of the gate | Quarter review Nov 1: gates status, evidence index, next-quarter proposal (1B build) |

**Honesty note:** a passed 1A gate in 13 weeks, including Unreal bootstrap and a determinism proof, is ambitious. If T4.A validation or the Phase 0 approval week slips, Sprint D compresses and the 1A gate review moves into next quarter — reported plainly, per Rule 18, rather than absorbed silently.

## 6. Resources

| Resource | Position |
|----------|----------|
| **People** | Director (vision, doctrine, approvals, gate sign-off — the scarce resource this plan budgets around) plus contributing agents. Per-task assignment: Director's call, recorded in the issue tracker (§9, item 2). Weekly review cadence with decisions batched; explicit numbered waiting-lists on every handoff. |
| **Engine & languages** | Unreal Engine (default baseline, version pinned in T0.3, subject to technical-sandbox validation); Blueprints for early prototyping; Python for data generation, validation, simulation analysis, telemetry, balance reports, asset utilities, automation; C++ later where performance, determinism, networking, or architecture justifies it. |
| **Version control & CI** | GitHub, private repo, `main` protected by convention; GitHub Actions for Python-side validation from Week 1; in-engine batch evidence via scripted local runs with committed artifacts until heavier CI is justified. |
| **Content tooling** | Blender plus properly licensed assets — every asset through the T2.3 compatibility audit before entering the project. Characters, mechanics, tuning, branding, writing, presentation, and project-specific code remain original (Rule 1). |
| **Budget** | $0 external spend assumed for the quarter. Any licensed-asset or tooling purchase is a Director decision with the audit attached. |
| **Working environment** | Local folder `C:\Users\edwar\project-uppercut` as the clone; agent sessions work against the repo with evidence-linked reporting. |

## 7. Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | **Determinism in Unreal harder than expected** (Blueprint tick order, float drift) — threatens replay truth, seeded tests, and the 1A gate | T4.A validates this first, in Sprint C's opening; accepted fallback is C++ for the sim core per Rule 22; finding reported with evidence either way |
| R2 | **Phase 0 approval bottleneck** — the gate is Director-decision-heavy | All drafts land before the Sprint B review week; decisions batched; defaults proposed in writing so a short review session can close many items |
| R3 | **Scope creep past the gates** (character work, presentation, input, roster growth before 1A passes) | Fixed development order is law; Sprint E's 1B work is data-and-validators only; parking lot below |
| R4 | **Originality drift** — inspiration sliding toward imitation in names, moves, presentation, or terminology | Rule 1 audit habit at every review; canonical vocabulary only (Crowd Bar, Specials, Ultimate, Full-Crowd Trait, Ringcraft, Showmanship); asset audits mandatory; no protected-property terminology in code, data, or docs |
| R5 | **Score-isolation leakage** — a convenient read of official cards during CPU, crowd, referee, difficulty, or replay work | Firewall built as architecture (T4.B), not discipline; score-access denial tests run continuously from the first Judge commit |
| R6 | **Evidence dishonesty by momentum** — status claims outrunning repository evidence | Rule 18 as reporting law: weekly status cites commits and artifacts or says "not started"; prototype numbers labeled hypotheses until promoted |
| R7 | **Comedy foundation neglected in a systems quarter** — a sandbox that proves mechanics but gives the comedy-first identity nothing to stand on | WS6/T6.2 keeps personality observable in events and logs; commentary-profile and lore schemas (T1.1) land this quarter so presentation phases inherit truthful hooks |
| R8 | **Director bandwidth** — solo decision-maker across a decision-heavy quarter | Weekly scope survives a zero-touch week; every request for decision arrives with a written default |

## 8. Reporting and cadence

Weekly Director review with three artifacts: evidence-linked status (commits, reports, replay logs — or explicit "not started"), the decision queue with proposed defaults, and an updated numbered waiting-list. Gate reviews (Sprint B, Sprint D) are dedicated sessions walking the ROADMAP checklist item by item. Every accepted decision lands in `docs/decisions/`; canonical files synchronize promptly when the Director issues corrections, per PROJECT_NOTES.md maintenance rules.

## 9. Pending Director decisions (not assumed by this plan)

1. **Author, ratify, rewrite, or discard §3 objective candidates** — the objectives section belongs to the Director; this plan supplies derivation material, not a decision.
2. **Ownership assignments and team governance** — no Claude-primary/Codex-presentation split is assumed. Earlier discussion contemplated Ed as final authority, ChatGPT coordinating strategy and arbitration, and Codex-led and Claude-led teams working in parallel; that model requires a separate canonical governance decision before it controls workstream assignments. Until then, assignments are made explicitly per task.
3. **Contribution tagging** — the model/timestamp tagging convention used in the Director's other projects is **not an adopted Project Uppercut rule**. This file carries the author's attribution tags in comments; whether tagging becomes project law here is the Director's call.
4. **Referee-profile schema timing** (T1.4) — approve the full schema for Phase 0 or approve a minimum Phase 0 contract with detailed profiles following during Phase 1A. The canonical referee system itself is not pending.

**Parking lot (excluded this quarter, per the fixed order):** human controls and Human vs. CPU (Phase 2), training-module content (Phase 2), Human vs. Human (Phase 3), online and matchmaking (Phase 4), Version 1 content and presentation breadth (Phase 5), Career and Story systems (deferred next version, its lowest priority), roster beyond the two named vertical-slice fighters, arenas, entrances, commentary content, branding, and distribution decisions.

---

## Appendix A — Disposition of the 2026-08-02 review findings

| Review finding on v0.1 | v0.3 disposition |
|-------------------------|------------------|
| Non-canonical meter name; one signature move | Canonical Crowd system throughout: Crowd Bar; two counterable Specials per fighter; full-bar choice between Ultimate and Full-Crowd Trait, never both (WS4 item 11–12) |
| CPU read scorecards / reacted to being "behind on cards" | Score Isolation implemented as architecture and tested continuously; CPU estimates come from observable events with explicit uncertainty (T4.B, T5.3, R5) |
| Four generic launch fighters, one per archetype | Generic **test fighters** and six stress **profiles** as balance instruments in 1A; the character slice is Adewale "The Fine Print" Balogun vs. Calvin "The Host" Givens, gated behind 1A (WS5, Sprint E) |
| Hard 35–65% balance band | Replaced by Rule 21 evidence standard: legitimate routes to victory, inexplicable-dominance and absent-counterplay detection; no numeric law (T5.4) |
| Legacy-title framing | Plan grounds identity in the canonical originality position: original spiritual successor to classic arcade boxing; no protected-property terminology anywhere in the plan (R4) |
| Comedy underweighted | Comedy-first identity carried as PO4/T6.2/R7: this quarter builds its truthful mechanical substrate; content lands in presentation phases |
| Training Mode absent | One-system law protected structurally now (PO5, schema design); training-module content correctly scheduled in Phase 2, not this quarter |
| Coed / no-divisions roster absent | Carried in WS1 schemas and Rule 10/11 validator work; roster philosophy affects attribute economy from Phase 0 onward |
| Referee system absent | Referee architecture provisioned in 1A (T4.D) with the six serious officials and the non-Ranked comic-relief official as maturing content; only the timing and depth of the Phase 0 profile schema remain pending (T1.4) |
| Damage model oversimplified | Full per-region condition model from the canon adopted as a WS4 standing constraint (head, jaw/chin, per-eye, torso, per-arm/guard, stamina, balance, guard, Composure, Chin, Durability, Recovery) |
| Footwork reduced to range/spacing | Elastic Footwork System, planted movement, threat-responsive stride compression, collision truth, and replay truth adopted as WS4 standing constraints (items 2, 5) |
| TypeScript recommended as core | Withdrawn. Unreal-first per Decision 0002: Blueprints prototyping, Python tooling, C++ when justified; determinism validated in-engine first (T0.3, T4.A) |
| Claude/Codex ownership assumed | Withdrawn; ownership is a pending Director decision (§9.2) |
| Tagging treated as project doctrine | Withdrawn as doctrine; contribution tags removed from this committed plan; any future convention remains a pending Director decision (§9.3) |
| Factually stale (repo "to be created", O1/T1.1/T1.3, kickoff list) | §1 restates current state; all completed governance work removed from the task set; kickoff checklist replaced by WS0 |
| Objectives declared as doctrine | §3 contains objective candidates for Director development and carries no authority until the Director authors, ratifies, or rewrites them (§9.1) |

*Plan v0.3 — subordinate by construction. PROJECT_RULES.md, PROJECT_NOTES.md, accepted decisions, and ROADMAP.md control.*

---

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 06:13 UTC | PROJECT_PLAN synchronization addendum START ] -->

## Appendix B — Synchronization addendum (2026-08-03, subordinate)

Recorded under the plan's own laws (§8: canonical files synchronize promptly; Rule 18: status claims
track repository evidence). The Director's v0.3 text above is untouched; this appendix only notes
where §1's "facts as of 2026-08-02" and §9's pending list have since been overtaken by committed
evidence and accepted decisions, so the plan reads against current truth instead of silently drifting:

- **Phase 0 is complete.** The quality gate passed on repository evidence on 2026-08-02
  (`docs/phase0/phase0_status.md`, Decision 0007). §1's "Phase 0 in progress" described the pre-gate
  state at the moment v0.3 was written.
- **A test suite and toolchain now exist.** Schemas, contracts, validators, and fixtures — 242 tests
  green in GitHub Actions on every push (T0.4 live). §1's "no test suite exists yet" is superseded.
- **An Unreal project now exists.** `sandbox/UppercutSandbox.uproject` on Unreal Engine 5.8.1
  (CL 56057345), pinned in `docs/phase0/technical_baseline.md` (T0.3 done). Still true, still
  claimed: no playable build and no completed combat gameplay (Rule 18).
- **T0.1 is done.** `C:\Users\edwar\project-uppercut` is the verified working clone; local and remote
  `main` parity is checked at every push.
- **T4.A — the load-bearing determinism question — is validated, not merely scheduled.** Engine
  runtime, Blueprint actor tick, and the canonical state machine executing in the Blueprint VM each
  hold byte-identical same-seed evidence with different-seed divergence
  (`docs/phase1a/determinism_probe_results.md`). The Rule 22 C++ trigger did **not** fire; it stays
  armed for scale, not correctness.
- **Phase 1A steps 1–5 are defined** (combat states, movement/facing, camera, animation states,
  collision truth) with validators, tests, and semantics docs — `docs/phase1a/phase1a_status.md`.
  Step 6 (basic punches) is next in the fixed order.
- **§9's four pending decisions have been ruled.** Decision 0006 adopted the §3 objectives, the §5
  schedule, and contribution tagging (items 1 and 3 — tagging is now project law, codified in
  `CONTRIBUTION_TAGGING.md`); Decision 0008 set team governance (item 2); Decision 0007's D-9 ruled
  referee schema depth for Phase 0 (item 4 / T1.4). Decisions now run 0001–0010.
- **The pinned "10 guards vs. 2 guard volumes" drift is closed on mechanism**, not on wording:
  Decision 0010 makes a guard posture modulate the coverage extents of the two declared collision
  volumes, so the collision pipeline stays the sole authority and ten named guards need neither ten
  volumes nor ten branches. The authored posture set remains ROADMAP step 7 work.

Live status is tracked in `docs/phase0/phase0_status.md` and `docs/phase1a/phase1a_status.md`. This
plan remains what it declares itself to be: a calendar forecast subordinate to gates and canon.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-03 06:13 UTC | PROJECT_PLAN synchronization addendum END ] -->
