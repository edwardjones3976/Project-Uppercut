# Project Uppercut: Critical State Review

**Review date:** 2026-08-06  
**Repository:** `edwardjones3976/Project-Uppercut`  
**Reviewed head:** `926fafc00eecc629094b1b0f44a4a9fa786ad5d3`  
**Review type:** Independent product, architecture, engineering-process, and game-development critique

> This review is intentionally severe. Project Uppercut has accumulated enough evidence, documentation, and technical machinery that polite ambiguity would now be harmful.

---

## Executive verdict

Project Uppercut is currently an **excellent simulation-research repository, a strong deterministic-systems laboratory, and an underdeveloped videogame project**.

Its greatest strength is epistemic discipline: the repository attempts to prove claims, preserve corrections, distinguish contracts from implementations, pin evidence, and prevent presentation from changing combat truth. That discipline is rare and valuable.

Its greatest weakness is that the project has repeatedly converted the absence of a playable game into more analyzers, more phase records, more commandlets, more golden streams, and more explanatory prose. The machinery for knowing whether a subsystem is correct is becoming more mature than the system a player or spectator can actually experience.

The project is no longer mainly at risk of being technically wrong. It is at risk of becoming **technically impeccable scaffolding around a game that remains perpetually one phase away**.

### Overall grade: **B- as an engineering project; D+ as a playable game project**

| Area | Grade | Judgment |
|---|---:|---|
| Creative direction | A- | Distinctive, coherent, original, and unusually well articulated. |
| Boxing-system reasoning | A- | Strong separation of target, trajectory, interception, condition, range, and authority. |
| Determinism and evidence | A | The strongest part of the repository. |
| C++ implementation architecture | C+ | Proven pieces exist, but are still commandlet-shaped islands rather than one runtime. |
| Unreal integration | D | There is no normal map a Director can open and play as a game. |
| CPU behavior | D+ | Contracts exist; the current proven range stream still uses a flat action draw that throws most punches from the wrong band. |
| Game feel | D | Responsiveness, comedy, impact, pacing, and repeated-match enjoyment remain mostly prose. |
| Project management | C- | Six blocking gates, no closed gates, no open issues, and a stale draft PR. |
| Documentation quality | A- | Individually strong, candid, and traceable. |
| Documentation economy | D+ | The document forest is now large enough to obstruct execution. |
| Reproducibility | C+ | Python evidence is strong; Unreal/vendor-asset reproduction and remote CI evidence remain weak. |
| Product readiness | D | No playable complete boxing match, no ordinary game loop, no external testable build. |

---

## What is genuinely excellent

A hard critique should not erase the project’s real accomplishments.

### 1. The repository has unusually strong intellectual honesty

The development history records false diagnoses instead of rewriting them away. The correction that a harness had been measured as though it were the contract is exactly the kind of failure many projects conceal. Here, the mistake became a rule:

> A harness may explore; only the contract may conclude.

That principle is excellent. It should survive the project even if much of the current evidence infrastructure is later simplified.

### 2. Determinism is treated as product infrastructure

The project does not use “same seed” as decorative language. It pins streams, compares Python and C++, records hashes, checks cold re-analysis, and distinguishes authoritative events from presentation. Phase Q now reproduces its Python marker stream byte for byte in C++ across multiple seeds and lengths.

That is a legitimate achievement and a credible future foundation for:

- reproducible replays;
- rollback networking;
- match disputes;
- batch balance analysis;
- deterministic CPU-versus-CPU cards;
- and post-fight explanation.

### 3. The core design boundaries are strong

The following boundaries are well chosen:

- C++ owns authoritative simulation.
- Blueprints and rendering own presentation.
- Python owns validation, analysis, and reference behavior.
- Animation follows combat rather than deciding it.
- Crowd, commentary, camera, and comedy may amplify facts but not alter them.
- Judges remain isolated.
- CPU behavior may not read hidden scores, future actions, or player inputs.

These are exactly the kinds of rules that prevent an arcade game from becoming arbitrary.

### 4. The creative identity is clearer than most early independent projects

“Arcade boxing with real boxing bones” is not empty branding. The repository has already translated it into concrete principles:

- accessible surface, hidden depth;
- spectacle without authority;
- preparation rather than beginner protection;
- aggression and patience both valid when intelligently executed;
- boxing idioms as mechanics before commentary;
- comedy through consequence rather than dishonest physics;
- CPU-versus-CPU as a first-class experience.

The project knows what it wants to become. The problem is no longer vision.

---

## The central failure: the repository is not organized around a playable vertical slice

The most important fact in the repository is still this:

> There is no level that a user opens and plays as Project Uppercut.

`docs/SEE_AND_TEST.md` is commendably honest: the existing levels are evidence harnesses, not a game. The current one-command view produces screenshots from a rendered slice, but it does not produce a normal interactive development arena with a complete authoritative match.

This should be treated as a product emergency, not an ordinary backlog item.

### Why this matters

A game project can survive incomplete AI, placeholder art, limited moves, ugly UI, and poor balance. It cannot survive indefinitely without an end-to-end playable loop because the missing loop hides the interactions that matter most:

- whether movement looks and feels responsive;
- whether punches read correctly at real speed;
- whether recovery and commitment create rhythm;
- whether animation conceals or clarifies authority;
- whether two systems that pass separately become absurd together;
- whether a spectator can follow an exchange;
- whether the game is funny rather than merely documented as funny;
- whether a second bout is desirable.

The repository currently proves components more readily than it proves experience.

---

## Architecture critique: commandlet islands are not yet a game runtime

Phase Q is proven in C++, but the form of that proof exposes the next architectural danger.

`UppercutCoreRangeCommandlet.cpp` is a large, self-contained evidence program. It loads canon files, implements hashing, parses JSON, owns simulation-specific structures, runs a tick loop, emits rows, and verifies a contract. This is valuable as a proof artifact. It is not the architecture that should own live gameplay.

### Current pattern

The project is tending toward:

```text
phase contract
→ phase-specific Python analyzer
→ phase-specific C++ commandlet
→ phase-specific marker stream
→ phase-specific proof record
```

That pattern is excellent for validating a small rule set and dangerous as the dominant production architecture.

If every phase becomes a separate mini-simulation, later integration will require one of two bad outcomes:

1. duplicating rules into a new live runtime after proving them elsewhere; or
2. welding commandlet implementations together into a monolith never designed for real-time play.

### Required correction

The next architectural milestone must introduce a shared runtime object, not merely another commandlet.

A suitable target is conceptually:

```text
FUppercutSimulation
  owns authoritative state
  owns the fixed tick
  consumes versioned data
  emits authoritative events
  supports save/load/resimulation
  has no rendering dependency

UUppercutFightSubsystem
  owns a live Unreal session
  advances FUppercutSimulation
  exposes read-only snapshots/events

AUppercutMatchDirector
  translates events into presentation
```

Commandlets should become clients of the same simulation runtime used by Play-in-Editor, not alternate implementations of it.

### Hard rule proposed by this review

> No phase after Q should be considered strategically successful unless its code is reusable by the live simulation without copying its rules.

Byte parity is necessary. Runtime convergence is now equally necessary.

---

## The project is overcounting tests and undercounting experiences

The repository reports 733 passing tests at the reviewed head. That number reflects meaningful discipline, but it is becoming a seductive metric.

A project can have 1,500 green tests and still fail the most important test:

> Can a person launch the game, watch or play a complete fight, understand what happened, and want another one?

Current test growth is not matched by growth in:

- playable maps;
- human input paths;
- full-match integration;
- presentation reviews;
- accessibility checks;
- external playtests;
- performance captures;
- user-facing failure reports;
- build artifacts.

### Correction

Add a second status ledger called **Experience Evidence**, with milestones such as:

- development arena opens;
- Play begins a live fight;
- full round completes;
- knockdown and count visible;
- bout reaches decision or stoppage;
- pause/restart/seed controls work;
- one non-developer completes the flow;
- one spectator correctly explains the decisive exchange;
- one Director review approves readability;
- one Director review approves comedy/impact;
- one external build launches on a clean machine.

Test counts should remain, but they must stop serving as a proxy for product progress.

---

## Open gates are being documented instead of decided

`docs/decisions/OPEN_GATES.md` contains six unresolved gates:

- G1: normal-step cost;
- G2: rest/no-action semantics;
- G3: aggression-bias semantics;
- G4: lateral guard decision ratification;
- G5: default ruleset;
- G6: exact-threshold guard values.

None is closed.

The gate file is a good correction to scattered decision packets. It is not enough. Three of these gates block the stamina economy and CPU policy. One blocks the meaning of a valid ending. One is described as a fix rather than a judgment.

Continuing to build around them increases rework and creates a strange inversion: the repository can prove a new C++ phase while foundational product choices remain undecided.

### Required correction

Close G1, G2, G3, G5, and G6 before adding another analytical phase.

G4 may be ratified and deferred in implementation, but its authority should stop floating.

The project already has enough evidence to make these decisions. More measurement is now likely to become avoidance disguised as rigor.

---

## CPU behavior is still a laboratory placeholder

Phase Q’s proven stream uses a flat action draw. The result is that roughly two thirds of punches are thrown from the wrong range band. The commit correctly states that Phase S is supposed to change this.

That finding is useful, but it also reveals that the current C++ proof is not yet “a boxer with distance.” It is “a deterministic action generator with distance consequences.”

A boxer is not defined merely by legal actions. A boxer needs:

- intent;
- restraint;
- preferred range;
- tactical memory;
- fear and confidence boundaries;
- hurt-state behavior;
- rest behavior;
- pattern recognition;
- characteristic mistakes;
- adaptation.

### Required correction

The first live CPU policy should be deliberately small and visibly purposeful:

- seek preferred range;
- do not throw an unavailable punch;
- rest when no useful action exists;
- protect a visibly damaged region;
- pressure ropes;
- reset after inefficient exchanges;
- punish one repeated pattern;
- emit a reason code for every decision.

Do not attempt “smart AI” before this. Do not keep using random legal action selection as a stand-in for boxing intelligence after the live arena exists.

---

## Game feel is the project’s least proven pillar

The stated priority order begins with responsiveness, visual speed, fun, and humor. The repository has not yet proven any of those in the way a player experiences them.

There is no evidence yet for:

- input-to-action latency;
- animation acknowledgement latency;
- buffer behavior;
- visual contact clarity at full speed;
- hit pause quality;
- camera stability;
- impact audio;
- crowd rhythm;
- comedic timing;
- repeated-match fatigue;
- spectator comprehension.

The project’s strongest philosophical pillar is therefore its weakest implemented pillar.

### Required correction

The first playable arena must include a thin “soul proof,” not wait for final polish:

- one clean impact package;
- one original crowd swell;
- one concise commentary line;
- one deliberate silence after a knockdown;
- one truthful comic reaction;
- one replay that explains the decisive exchange.

This is not scope creep. It is validation of the product identity.

---

## Documentation has become both strength and drag

The repository’s documents are generally thoughtful, specific, and candid. The problem is quantity, overlap, and narrative density.

The README alone functions as product pitch, status report, architecture summary, historical index, design manifesto, and documentation directory. Development logs routinely contain essay-length forensic narratives. Commit messages can be longer than the code changes they explain.

This creates several costs:

- new contributors must reconstruct authority from many files;
- current actions are buried under historical reasoning;
- stale statements remain semantically plausible;
- agents can spend entire sessions reading explanations rather than building;
- every correction adds another layer rather than reducing complexity.

### Required correction

Adopt a documentation hierarchy with explicit retention rules:

1. **Current truth**
   - `README.md`
   - `STATUS.md`
   - `OPEN_GATES.md`
   - `ROADMAP.md`
   - accepted decisions
2. **Active implementation**
   - one current slice plan
   - one live integration runbook
3. **Reference**
   - boxing and design references
4. **Historical evidence**
   - archived development logs and superseded investigations

Create a generated index that marks each document:

- authoritative;
- active;
- reference;
- historical;
- superseded.

Do not delete the forensic history. Stop making every reader traverse it by default.

---

## Project management is weaker than the engineering discipline

The repository has no open GitHub issues, despite six formal blocking gates and multiple implementation phases. It has one stale draft pull request, PR #5, based on an old head and reporting 559 tests while main has advanced far beyond it.

This is a serious mismatch.

The project has built an intricate internal decision system but is not using ordinary work-tracking tools to make ownership, priority, and closure visible.

### Required correction

Create GitHub issues for:

- each open gate;
- live Unreal integration;
- shared runtime extraction;
- Phase R C++ parity;
- Phase S C++ parity;
- full-round Phase O integration;
- game-feel review;
- external-build reproducibility.

Close or rebase PR #5. Leaving a stale environment PR open is repository litter and a misleading signal.

Use milestones:

- **M1: Play-ready developer arena**
- **M2: Complete generic CPU bout**
- **M3: Human-vs-CPU technical input**
- **M4: Adewale vs. Calvin vertical slice**

The repository needs fewer invisible obligations and more explicit closure.

---

## CI and reproducibility are not yet strong enough

The reviewed head has no visible combined status checks or workflow runs through GitHub. Local commit messages report clean tests and validators, but remote independent evidence is absent.

This matters because the project places extraordinary weight on proof.

### Current reproducibility split

**Strong:**

- Python tests;
- validators;
- golden streams;
- deterministic hashes;
- documented local commands.

**Weak or incomplete:**

- GitHub-visible CI status;
- Unreal C++ compilation on a clean machine;
- automatic Unreal commandlet parity;
- restoration of gitignored Fab assets;
- external packaged-build launch;
- artifact retention.

### Required correction

At minimum:

- run Python tests and validators on every pull request;
- publish test artifacts and generated status;
- require status checks before merge;
- use a self-hosted Windows runner for Unreal build/parity when practical;
- produce a machine-readable vendor-asset manifest with IDs, versions, hashes, and restoration instructions;
- create a clean-machine verification checklist;
- retain a packaged development build at major milestones.

A private repository cannot call itself evidence-first while its strongest evidence exists only in local commit prose.

---

## Asset handling is operationally fragile

The repository intentionally ignores the licensed boxing and arena assets. That is legally sensible. It also means a fresh clone does not contain the visual project described in screenshots.

The current documentation explains this, but explanation is not restoration.

### Required correction

Add a non-secret asset manifest containing:

- marketplace/Fab asset identifier;
- expected package name;
- expected version;
- required engine version;
- expected destination path;
- license/receipt storage location outside Git;
- optional local checksum;
- whether a placeholder fallback exists.

Add an audit command that reports:

- present and correct;
- missing;
- wrong version;
- wrong path;
- fallback active.

The project must remain buildable as a gray-box experience without paid assets.

---

## The current roadmap is phase-centric rather than player-centric

The phase naming system has value, but it encourages internal progress to masquerade as product progress.

“Phase Q proven” sounds larger than what it currently means: one isolated range contract has C++ parity. That is good engineering evidence. It is not a player milestone.

### Required correction

Keep phase labels for engineering evidence, but report product progress separately:

| Product milestone | Current state |
|---|---|
| Open a game map and press Play | Not available |
| Watch one live authoritative exchange | Not available as a normal game loop |
| Complete one authoritative round | Not available |
| Complete one authoritative bout | Not available |
| Pause/restart/change seed in a live arena | Not available |
| Human input through the shared core | Not available |
| Director-approved game feel | Not evaluated |
| External tester flow | Not available |

This table is harsh because it is useful.

---

## Non-negotiable corrective program

The following program should supersede broad exploratory work until completed.

### Step 1: Close the Director gates

Close G1, G2, G3, G5, and G6 with accepted decision records. Ratify G4 and schedule its implementation.

No further tuning conclusions should be accepted until those decisions are reflected in canon and the Phase O golden stream is intentionally re-blessed.

### Step 2: Extract one shared authoritative runtime

Create a reusable simulation runtime consumed by:

- commandlets;
- Python/C++ parity runners;
- Play-in-Editor;
- standalone development builds;
- future replay and rollback systems.

Do not create separate gameplay logic for the development arena.

### Step 3: Build the play-ready developer arena

The Unreal project must open into an obvious map where the Director can:

- press Play;
- watch two generic fighters;
- pause/resume;
- single-step;
- restart a seed;
- change speed;
- see range, state, stamina, condition, hand availability, and CPU reason codes.

### Step 4: Integrate, do not merely port

Bring N, Q, then R and S into the same live state machine. Resume O only after the integrated runtime can execute the complete chain:

```text
bell → decisions → movement → contact → condition → knockdown → count
→ recovery/stoppage → card → next round/verdict
```

### Step 5: Prove one complete generic CPU bout

The bout must reach both kinds of valid ending across a seed set:

- stoppage;
- decision.

The same seed must reproduce. A different seed must produce a different but explainable contest.

### Step 6: Prove the product’s soul

Add one small package of impact, crowd, commentary, silence, humor, replay, and post-fight explanation. Conduct a Director review.

### Step 7: Only then author named fighters

Adewale and Calvin should be the first character-complete vertical slice only after generic combat can complete a believable fight.

---

## What the project should stop doing immediately

Until the live arena and full generic bout exist, stop or sharply limit:

- new large design documents;
- additional guard catalogs;
- new fighter concepts;
- broad roster balance claims;
- more isolated phase commandlets without shared-runtime reuse;
- tuning against flat-random CPU behavior;
- essays that do not close a gate or unblock code;
- screenshots presented as game progress without an interactive path;
- test-count celebration without an experience milestone;
- new future-mode planning.

The project does not need more possibility. It needs convergence.

---

## Final assessment

Project Uppercut is not failing. It is succeeding at the wrong level of abstraction.

It has proven that the team can reason, measure, correct itself, formalize boxing logic, and reproduce deterministic computations. Those are major capabilities.

It has not yet proven that those capabilities combine into a videogame.

The project’s next victory should not be another phase letter, another 100 tests, or another meticulous postmortem. It should be this sentence becoming literally true:

> Two visible fighters enter one Unreal ring, think for observable reasons, move and defend with the bodies they visibly possess, complete a truthful fight under a declared ruleset, and leave behind a replay that explains the result while the presentation makes the Director want to run another seed.

Until then, the repository remains a remarkable boxing laboratory with a game trapped inside it.

---

## Review acknowledgment checklist

The project should treat this review as acknowledged when:

- [ ] The review is merged into `main`.
- [ ] Each open gate has an issue or accepted closure record.
- [ ] PR #5 is closed, superseded, or rebased.
- [ ] A shared live-runtime issue is active.
- [ ] A play-ready development-arena issue is active.
- [ ] The next status report includes both engineering evidence and experience evidence.
- [ ] No new phase is declared complete solely through an isolated commandlet.
- [ ] The Director has reviewed the first complete live bout in Unreal.
