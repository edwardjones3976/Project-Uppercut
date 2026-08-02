<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 20:42 UTC | START ] -->

# Decision 0007 — Phase 0 Gate Rulings

**Date:** 2026-08-02
**Status:** Accepted under explicit Director delegation ("You have permission to do all of it")
**Scope:** the decision queue D-1 through D-10 in `docs/phase0/gate_review_packet.md`, excluding D-8
(team governance), which is recorded separately as Decision 0008.

## Standing note on authority

PROJECT_RULES.md and Decision 0005 reserve objectives and gate approvals to the Director. The Director
delegated these rulings explicitly. They are recorded here rather than applied silently so that every
one remains visible, attributable and reversible: **each ruling below is one configuration line or one
data file away from being changed**, and a Director reversal supersedes this record without needing to
unpick any code.

## D-1 — Attribute budget formula *(gate item: one canonical formula chosen)*

**Ruled:** curve **C, tiered marginal** (1x on magnitude 0–40, 2x on 41–70, 3x on 71–100);
**refund rate 0.5**; **cap 1000**, applying only to complete declarations. Canonical form:
`data/attribute_budget.json`.

**Why curve C:** its tier boundaries are the same 40 and 70 thresholds Rule 10 already uses for its caps
and compensation ladder, so authors reason about one set of numbers rather than two. It also escalates
hardest at the extremes, which is what Rule 10's escalation clause asks for.

**Why refund 0.5, and why this was the real finding:** measured at full refund, the most polarised legal
build cost *less* than a moderate one under **every** candidate curve — severe negatives refunded more
than elite positives cost. That is precisely the "unrestricted upward stacking" Rule 10 forbids, and it
was a property of the refund rate, not of any curve. Halving the refund restores the intended ordering:
net 100 for a broad-modest build, 180 for two elite attributes plus mild negatives, 230 for the
polarised build.

**Why the cap is scoped:** cost scales with how many attributes a build declares. A 7-attribute sandbox
fixture nets 230 where a complete 24-attribute build nets 869. One absolute cap cannot span both, so the
cap binds only builds declaring every attribute in the taxonomy. Partial fixtures are balance
instruments; their cost is reported, not enforced.

**Confidence, stated honestly:** the cap rests on **one** modelled build
(`fixtures/fighters/legal/reference_complete_shape.json`, deliberately sitting near several Rule 10
caps at once). That is evidence, but not much of it. The config carries
`tuning_status: hypothesis` and a recalibration trigger for when real roster characters exist.

## D-2 — Generic technical sandbox acceptance criteria *(gate item)*

**Ruled:** `docs/phase0/sandbox_acceptance_criteria.md` adopted as drafted — 27 criteria across combat
foundation, CPU behaviour, officiating and clock, Crowd and abilities, evidence, and readability and
balance. Each traces to a rule or ROADMAP clause, and criteria can be struck or added individually
without disturbing the rest.

## D-3 — Character vertical-slice acceptance criteria *(gate item)*

**Ruled:** `docs/phase0/vertical_slice_acceptance_criteria.md` adopted as drafted, **separately** from
D-2, preserving prototype separation. It sets the acceptance bar only; the identity, personality,
appearance and dialogue of Adewale "The Fine Print" Balogun and Calvin "The Host" Givens remain
Director-owned content and are not authored here.

## D-4 — Attribute vocabulary and families

**Ruled:** the 24-key, three-family taxonomy in `data/attribute_families.json` becomes canonical —
9 physical, 8 technical, 7 mental. *Mental* carries no all-negative prohibition, because Rule 10 names
only physical and technical. `corner_chemistry` stays out of fighter attributes: Rule 6 frames it as a
relationship between a fighter and a corner, not a property of the fighter. Extending the vocabulary
later is additive; renaming later is a migration.

## D-5 — Compensation binding *(OQ-1)*

**Ruled: exclusive.** A compensating positive is spent once; two severe negatives require two qualifying
positives. This is the stricter reading and the one consistent with "the model is give-and-take and must
not permit unrestricted upward stacking." The alternative *shared* reading would make
`illegal_shared_compensation.json` a legal build; a test asserts both behaviours so the fork stays
inspectable.

## D-6 — Remaining Rule 10 and Rule 14 interpretations

**Ruled:** a +100 **counts** toward the two-above-+70 allowance (OQ-2, stricter reading). All-negative
family checks evaluate over *declared* attributes, with complete declaration expected of roster
characters (OQ-3). Chin, Durability, Recovery and Composure exist as **both** an authored attribute and a
governed runtime condition — the Rule 10 / Rule 14 split across `attribute_families.json` and
`condition_regions.json`, which drops nothing from Rule 14's list (OQ-4). No per-attribute range caps
beyond Rule 10's global ones (OQ-7); notably Chin remains authorable to +100, which Rule 14 already
qualifies as maximum resistance rather than immunity.

## D-7 — Unreal and Blender version pins

**Ruled on procedure, not on numbers.** Naming a version the Director does not run would be exactly the
unevidenced claim Rule 18 prohibits, and this session cannot see the Windows toolchain. The ruling is
therefore: `docs/phase0/technical_baseline.md` keeps its version fields open, and they are filled from
the **actual installed build** at first engine setup, recorded in the same commit that creates the Unreal
project. Until then no tooling, CI job or document may assume a version. Decision 0002's engine choice is
unaffected; only the literal build number is outstanding.

## D-9 — Referee schema depth for Phase 0 *(T1.4)*

**Ruled:** the minimum contract plus all seven authored profiles satisfies Phase 0. Deeper behavioural
parameters land during Phase 1A as the sandbox matures and gives them something to act on. The referee
*system* was never pending; only the timing of profile depth was.

## D-10 — Decision 0006

**Ruled:** confirmed as written. Contribution tagging, the execution schedule and the objectives are
adopted; Decision 0005 is superseded in exactly two sections and stands otherwise.

## Consequences

- `data/attribute_budget.json` is created and enforced by `tools/uppercut_validate/attributes.py`.
- `fixtures/fighters/legal/reference_complete_shape.json` and
  `fixtures/fighters/illegal/illegal_over_budget_cap.json` are added; the suite is 100 tests.
- Phase 0 gate items 3, 5 and 6 are satisfied **pending repository evidence** — the gate is not closed
  until the foundation is pushed, because closing a gate against files on one disk would violate Rule 18.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 20:42 UTC | END ] -->
