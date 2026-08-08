# Director State Review — 2026-08-07

**Review head:** `30a0c2cd314247defe730323d87eb43cc74060ce`  
**Authority:** Director  
**Scope:** current `main`, active roadmap, CI, evidence architecture, live Unreal path, shared fight runtime, and governance.

## Verdict

Project Uppercut has crossed an important line.

It is no longer primarily a collection of design documents and isolated commandlet proofs. It now has:

- a shared authoritative C++ runtime used beyond one commandlet;
- a real Play-in-Editor development arena;
- proven C++ range and evasion paths;
- a cross-language semantic canon identity system with precise dependency scope;
- versioned rulesets and resolved initial Director gates;
- a shared C++ Wind/Reserve runtime with state-dependent recovery and bounded exhaustion semantics;
- GitHub Actions validation on pull requests and `main` pushes;
- preserved unit evidence through the integration work.

The previous review's central architectural criticism has therefore been substantially answered.

The principal project risk has changed.

> **The project no longer needs to prove that its parts can be engineered. It needs to prove that the parts can coexist as one complete, entertaining boxing match.**

No later infrastructure achievement outranks that objective.

---

## Current grades

| Area | Grade | Director assessment |
|---|---:|---|
| Product vision and identity | **A** | Clear, distinct, original, and stable. |
| Boxing-system design | **A-** | Deep and increasingly coherent, but clinch/foul/lateral geometry breadth remains later work. |
| Evidence and determinism | **A** | Now a genuine project strength rather than a collection of ad hoc pins. |
| C++ architecture | **A-** | Shared runtime rule is working; commandlet-island risk is materially reduced. |
| Unreal integration | **B-** | A real Play-ready arena exists, but only a subset of the fight lives there. |
| Stamina architecture | **A-** | Wind/Reserve separation is strong and cross-language proven; values remain intentionally unfitted. |
| CPU boxing intelligence | **C-** | Contracts and policy concepts exist, but the observable policy is not yet integrated into the complete live runtime. |
| Complete fight flow | **D+** | No single authoritative live bout yet reaches knockdown/count/stoppage/decision end to end. |
| Game feel and presentation | **D+** | Rendered proof exists, but responsiveness, impact, humor, crowd rhythm, commentary and replay have not passed a Director feel gate. |
| Product readiness | **D+** | Technically impressive prototype, not yet a playable boxing product. |
| Governance | **B** | Decisions are now made promptly, but active documentation and issue hygiene still lag implementation. |
| CI / clean-machine evidence | **B-** | Linux validation exists. Windows/Unreal remote proof and generated-status freshness remain incomplete. |

### Overall

- **Engineering program:** **B+**
- **Playable videogame:** **C-**
- **Direction:** **A-**

The repository is healthier than the 2026-08-06 review. It is not yet entitled to call Phase 1A nearly complete.

---

## What is now genuinely strong

### 1. The shared-runtime rule is working

The most important architectural correction since the prior review is that new systems are being built for reuse by the live simulation rather than accepted as isolated commandlet success.

The binding rule remains:

> **No phase after Q is strategically successful unless its implementation is reusable by the shared live simulation without copying its rules.**

Wind/Reserve follows this rule. Range and evasion already follow it. This is the architecture the rest of Phase 1A must use.

### 2. Evidence identity is finally precise enough

Decisions 0023–0024 solved a real evidence-design defect:

- raw hashes preserve exact provenance;
- semantic hashes identify authoritative meaning;
- hash-policy identity is global only where policy is truly global;
- per-file role-set identity prevents unrelated canon files from moving together;
- RFC 6901 paths are internally unambiguous;
- Python and C++ compare canonical bytes before hashes;
- historical N/K/O/Q/R event rows survived migration unchanged.

This system is now infrastructure. Do not keep extending it unless a new concrete failure appears.

### 3. Wind/Reserve is a better boxing model than one stamina number

Decision 0021 and the merged runtime correctly distinguish:

- immediate exchange breath and burst capacity (`Wind`);
- deep fight-long conditioning (`Reserve`);
- physical effort from acute cost and long-term load.

Decision 0025 also resolves Reserve underflow correctly: a legal action may empty the tank, but negative Reserve is not a third hidden exhaustion regime.

This is good boxing logic and good software architecture.

### 4. The Unreal project can finally be opened and watched

`L_UppercutDevArena` is a real development surface. The Director can open the project, press Play, pause, step, reseed and inspect the authoritative range/evasion loop.

That is a major improvement over screenshot-only evidence.

But it is a development arena, not yet a boxing game.

---

## Critical deficiencies

## 1. The complete bout is now the only strategic priority

Project Uppercut still lacks one authoritative runtime in which all of these coexist:

`range → evasion → observable policy → Wind/Reserve → contact quality → regional condition → knockdown → count → recovery → referee stoppage → sealed scoring → verdict`

The project has proven many of those nouns separately.

The next proof must be the sentence.

No new broad research lane, fighter, guard study, presentation subsystem, or balance sweep outranks this.

### Director milestone: FIRST BELL INTEGRATION GATE

The next integrated runtime must prove at minimum:

1. one generic three-round bout reaches a valid **decision**;
2. one different seed/configuration reaches a valid **stoppage**;
3. both use the same runtime and ruleset;
4. the live arena and commandlet emit the same authoritative stream;
5. pause, playback speed, camera and rendering do not alter the result;
6. CPU decisions carry observable reason codes;
7. official scorecards remain sealed from policy and presentation until reveal;
8. the post-fight record can explain the decisive exchange.

Three rounds are sufficient for the first integrated gate because this gate proves architecture and flow, not final championship pacing. Configurable longer fights remain required before Phase 1A closes.

## 2. CPU policy is now the main boxing-intelligence gap

The repository has spent enough time proving what happens after an action is chosen.

It now needs fighters who choose actions for boxing reasons.

The integrated policy must distinguish:

- observing from acting;
- seeking pressure from merely throwing;
- resting from refusing engagement;
- preferred range from current range;
- an open lane from a random move opportunity;
- pattern recognition from hidden prediction;
- hurt-state adaptation from generic difficulty scaling.

Every committed or deferred decision should carry a reason code.

No official scores, future inputs, private random draws, or unobservable opponent state may enter policy.

## 3. Game feel remains mostly unproven

The project claims a feel hierarchy that begins with responsiveness, visual speed and fun.

Those remain claims.

The first complete live bout must include only a **thin soul proof**:

- one convincing clean impact package;
- one crowd swell driven by observable action;
- one original commentary beat;
- one deliberate silence after a major knockdown;
- one truthful comedic reaction;
- one replay explanation.

Do not build a broadcast suite. Prove the game's personality can survive contact with the authoritative simulation.

## 4. Active documentation is stale in ways that can misdirect work

Two current-facing files are materially behind the repository:

### `docs/SEE_AND_TEST.md`

It correctly describes `L_UppercutDevArena` near the top, then later still states:

- there is no level to open and press Play;
- Phase O is held on G7;
- G7 still requires a Director ruling;
- Phase O/P/S have no C++ while the stamina runtime now does exist in C++.

That is control-plane drift inside an operational runbook.

### `STATUS.md`

The file is generated, but the generator output currently records a branch-merge commit rather than current `main`, and the workflow does not enforce regeneration. It also reduces the active authority to Decision 0012 and describes the next step too generically.

A generated file that is allowed to be stale is merely hand-maintained drift with extra machinery.

### `docs/implementation/integrated_contract_acceptance.md`

The semantic identity section remains unchecked despite Issue #17 being closed and the implementation merged. Several stamina items are also now proven.

The checklist should reflect repository evidence or explicitly say it is intentionally historical.

## 5. Issue tracking still duplicates authority

Issues #8, #9 and #12 overlap heavily.

Issue #12 already declares itself the single convergence issue. That should become true operationally.

- #8 is a historical acknowledgment of the prior critical review and should close as superseded by #12.
- #9's remaining implementation obligations should be folded into #12 and #9 closed as superseded.
- #14 should remain open for CI/status work.

A project should not need three open issues to remember the same active bout.

## 6. CI is improved but still incomplete

`.github/workflows/validate.yml` correctly runs `pytest` and the canon validators on pull requests and `main` pushes.

Remaining gaps:

- `STATUS.md` freshness is not enforced by CI;
- Unreal C++ build/parity/live-arena evidence remains local rather than GitHub-hosted;
- no Windows clean-machine lane exists yet;
- the Director cannot use GitHub alone to prove that the post-merge Unreal runtime built and ran.

This does not block local integration work. It does block calling the project clean-machine proven.

## 7. Test-count inflation must stop functioning as a product metric

`1100 passed` is useful engineering evidence.

It is not a product milestone.

From this review forward, Director status reports should lead with experience evidence:

- Can a complete fight run?
- Can it reach both cards and stoppage?
- Can a spectator explain why?
- Can the Director press Play and observe it?
- Does it feel responsive and enjoyable?

Test totals may appear underneath those answers.

---

## Director rulings from this review

### R1 — PR #21 is accepted and merged

The Wind/Reserve shared runtime passed its required Decision 0025 correction, branch CI, parity and local Unreal evidence. It is now part of `main`.

### R2 — Issue #12 is the sole Phase 1A convergence issue

Issues #8 and #9 should be closed after their remaining live implementation obligations are represented in #12.

### R3 — No new design gate before the integrated bout

No new numbered Director decision is required merely to continue ordinary implementation of Decisions 0021–0025.

A new gate may be raised only when current accepted authorities genuinely contradict each other or an implementation exposes an unresolved product rule.

### R4 — The next code must create the integrated contract

Immediate order:

1. new versioned integrated schema;
2. deterministic named RNG substreams;
3. observable CPU policy;
4. Wind/Reserve wired into that policy/runtime;
5. contact and regional condition;
6. knockdown/count/recovery/stoppage;
7. sealed scoring and verdict;
8. commandlet/live-arena parity;
9. First Bell Integration Gate;
10. thin soul proof;
11. Director game-feel review.

### R5 — Broad tuning remains frozen

No broad stamina, style, knockdown, guard or roster tuning until the observable integrated policy produces plausible boxing cadence.

Synthetic fixed-volume probes remain structural diagnostics only.

### R6 — Lateral guard geometry and named fighters remain later

Decision 0013 stays accepted but sequenced after the complete generic live-bout gate.

Adewale vs. Calvin begins only after that generic gate proves the shared system can stand on its own.

---

## Definition of the next victory

The next strategic success is not another phase letter.

It is this sentence becoming true:

> **Two generic fighters enter `L_UppercutDevArena`, choose actions for observable boxing reasons, spend and recover Wind and Reserve, land graded contact, accumulate regional consequence, survive or fail an authoritative count, reach either a referee stoppage or sealed decision, and leave behind a replay that explains why — while the presentation remains unable to change one fact.**

When that exists, Project Uppercut will have crossed from a sophisticated boxing engine prototype into the first recognizable version of its actual game.
