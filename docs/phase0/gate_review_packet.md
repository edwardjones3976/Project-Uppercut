<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 20:23 UTC | START ] -->

# Phase 0 Gate Review Packet

Sprint B preparation per PROJECT_PLAN.md §5 and §8, and risk mitigation R2/R8: every outstanding
decision arrives here with a written default, so one short Director sitting can close the whole gate.
The Sprint B target is Aug 23; gates govern, so closing early is permitted and closing late is
reported, never absorbed.

Two kinds of items below. **Explicit** items are ROADMAP gate items — silence cannot pass them.
**Default-adopting** items are interpretation choices already implemented behind a configurable
default — silence keeps the default, and the default becomes canonical at gate close.

## Gate snapshot

| # | Gate item | Status |
|---|---|---|
| 1 | Originality rules documented | met |
| 2 | Scorecard access boundaries documented and testable | met (checker proven non-vacuous) |
| 3 | One canonical attribute-budget formula chosen | **awaits D-1** |
| 4 | Legal/illegal fighter-build fixtures specified | met (3 legal / 13 illegal, clause-mapped) |
| 5 | Sandbox acceptance criteria approved | **awaits D-2** |
| 6 | Vertical-slice acceptance criteria approved separately | **awaits D-3** |
| 7 | Game-feel and style-viability laws accepted | met |

## Decision queue

### D-1 — Attribute-budget formula *(explicit — gate item 3)*
**Default proposed:** Curve **C, tiered marginal** (1× on 0–40, 2× on 41–70, 3× on 71–100 — tier
boundaries match Rule 10's own thresholds) with **refund rate 0.5** for negatives; the cap set after a
first calibration pass against real builds.
**Why:** measured at full refund, the most polarised legal build costs *less* than the moderate ones
under every curve — negatives refund more than elite positives cost, which is the exact stacking
loophole Rule 10 forbids. The refund rate, not the curve, closes it.
**Evidence:** `docs/phase0/attribute_budget_candidates.md`; reproduce with
`python3 -m tools.uppercut_validate.cli budget`.

### D-2 — Sandbox acceptance criteria *(explicit — gate item 5)*
**Default proposed:** approve `docs/phase0/sandbox_acceptance_criteria.md` as drafted (27 criteria in
six sections, each traceable to a rule or ROADMAP clause). Edits welcome; the document is structured so
a struck or added criterion doesn't disturb the rest.

### D-3 — Vertical-slice acceptance criteria *(explicit — gate item 6)*
**Default proposed:** approve `docs/phase0/vertical_slice_acceptance_criteria.md` as drafted —
separately from D-2, per prototype separation. Character identity content stays Director-owned; the
document sets the acceptance bar only.

### D-4 — Attribute vocabulary and families *(default-adopting; OQ-5, OQ-6)*
**Default:** the proposed 25-key, three-family taxonomy in `data/attribute_families.json`, with
*mental* exempt from the all-negative prohibition (Rule 10 names only physical and technical).
**Silence:** taxonomy becomes canonical at gate close; extending it later is additive, renaming later
is a migration.

### D-5 — Compensation binding *(default-adopting; OQ-1)*
**Default:** **exclusive** — one positive attribute is spent once; two severe negatives need two
qualifying positives. The stricter reading of give-and-take.
**Consequence made visible:** under the *shared* reading, `illegal_shared_compensation.json` becomes a
legal build; a test asserts both behaviours so the fork is inspectable.

### D-6 — Remaining Rule 10/14 interpretations *(default-adopting; OQ-2, OQ-3, OQ-4, OQ-7)*
**Defaults:** a +100 counts toward the two->+70 allowance (stricter); all-negative checks run over
*declared* attributes for generic fixtures, with full declaration expected of roster characters;
Chin/Durability/Recovery/Composure exist as both authored attribute and governed runtime condition
(the Rule 10 / Rule 14 split in `attribute_families.json` + `condition_regions.json`); no per-attribute
range caps beyond Rule 10's global ones.

### D-7 — Unreal and Blender version pins *(cannot default — needs your installed versions)*
`docs/phase0/technical_baseline.md` has blank version fields on purpose: pinning a version you don't
run would be a Rule 18 violation. Reply with the UE and Blender versions to pin.

### D-8 — Agent ownership and team governance *(cannot default — Decision 0005 rejected the imported
split; Decision 0006 deliberately did not adopt one on inference)*
Options when ready: per-task assignment as now; a workstream-level split recorded as Decision 0007; or
the earlier Ed-final-authority / coordinating-strategist / parallel-teams model, which needs its own
canonical decision before it controls assignments.

### D-9 — Referee schema depth for Phase 0 *(default-adopting; T1.4)*
**Default:** the built minimum contract plus all seven authored profiles satisfies Phase 0; deeper
behavioural parameters land during Phase 1A as the sandbox matures. The referee *system* is canonical
and was never pending.

### D-10 — Confirm Decision 0006 as written *(explicit — it records your override)*
`docs/decisions/0006-contribution-tagging-and-schedule-adoption.md` adopts tagging, the schedule and
the objectives, supersedes exactly two sections of Decision 0005, and deliberately leaves ownership
open (D-8). Confirm the record matches your intent, or mark it up.

## After the rulings

Close-out is mechanical: apply any changed defaults (each is one configuration line or one data file),
re-run the two commands below, record the rulings in `docs/decisions/` via the decision-log template,
and mark gate items 3/5/6 met in `phase0_status.md`. Phase 1A work is unblocked the same day.

```
python3 -m pytest -q                        # 95 tests
python3 -m tools.uppercut_validate.cli all
```

**Precondition for the gate review itself:** the foundation must be in the repository — a gate closed
against files that exist only on one disk would violate Rule 18. See `_to_delete/PUSH_FOUNDATION.md`
for the one-minute push procedure (T0.1).

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 20:23 UTC | END ] -->
