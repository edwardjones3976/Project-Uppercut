<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 04:11 UTC | Decision 0033 start ] -->
# Decision 0033 — Delegated dispositions: knockdown regions, ruleset authority, and the measurement gate

**Status:** ACCEPTED (delegated).
**Authority:** The owner, in-session, 2026-08-09: *"You rule on them using the
logic we have used throughout the project."* These dispositions were made under
that delegation by the coordinating agent, applying the project's own recorded
principles. Any of them may be countermanded by a later Director ruling; each
states the principle it was derived from so a countermand knows exactly what it
is disagreeing with.

**The five questions** are the ones escalated by the section-ownership pass
(docs/reviews/2026-08-09-section-ownership-director-assessment.md, DD1–DD5).

**The logic applied**, as this project has stated it repeatedly: reading canon
correctly is a bug fix and changing what canon says is a decision; one
authority per rule, and second opinions are deleted rather than kept as
fallbacks; array position is not authority (Decision 0026); fail closed —
unknown ids and null values never mean "free" or "use a default"; no value is
fitted and no structure is invented from synthetic evidence — structure before
numbers, and numbers only after the real integrated fight is measured
(Decision 0021 step 7, Decision 0032 §3); emergent over hardcoded; and the
frozen phases stay byte-identical while the unpinned integrated contract may
still move freely.

---

## Ruling 1 (DD1) — the knockdown-region fix LANDS; the threshold DOES NOT MOVE

Section 3's patches are **accepted and will be applied**. Reading every region
in a move's authored `target_regions` instead of element zero is a correction
of a misread — `hook_lead` is authored `["head", "jaw_chin"]`, so canon already
says the hook targets the jaw and the code was throwing that away. Knockdown
authority stops living in JSON array order, which is Decision 0026's own rule
applied where it was being violated. Damage placement deliberately keeps one
primary region: splitting force across regions would invent a placement
distribution canon does not author.

`pressure_threshold: 0.57` is **explicitly not re-chosen now**, even though
Section 3 verified that the fixed reading lets `cross_rear` and `uppercut_rear`
clear it at full wind and zero damage. Canon's own threshold note supplies the
principle: *"a threshold is only meaningful against the volume it was measured
at."* Re-choosing it before the post-fix sweep exists would be fitting a value
to a fight nobody has seen — the exact thing 0032 §3 forbids. **The sequence is
therefore: land the fix, run the thirty-seed sweep, and dispose of the
threshold as its own numbered decision informed by the measured knockdown
distribution.** An interim sweep that is too violent is evidence, not a defect.

## Ruling 2 (DD2) — rulesets rule the contest; the duplicate is deleted

Accepted in full, in the shape Sections 3 and 4 and the architect converged on
independently:

- `condition_model.knockdown` keeps the **arithmetic** — pressure threshold and
  modifiers, count clock, count-to, mandatory eight, relief fractions —
  because canon already says the count is identical for every referee.
- The **contest rules** live in `data/rulesets/*` exclusively:
  `knockdowns_per_round_stoppage`, `knockdowns_per_bout_stoppage`,
  `three_knockdown_rule`, `saved_by_the_bell`, `standing_eight_count`,
  `mandatory_count_numbers`, `scoring`.
- **`max_per_round` and `max_per_bout` are DELETED from the integrated
  condition pack**, so the integrated runtime cannot reach them at all.
  *AMENDED IN IMPLEMENTATION, 2026-08-09 10:25 UTC:* the keys themselves
  REMAIN in `condition_model.json`, because Phase O's frozen analyzer reads
  them as its named `legacy_max_per_*` echo and the condition validator pins
  them against the arcade ruleset's numbers — deleting them breaks a frozen
  phase's loader, and frozen phases stay byte-identical. The ruling's intent
  is preserved in the stronger form: the integrated bout's pack does not
  carry the keys, so there is no fallback to sometimes-read — the values are
  unreachable from the runtime rather than merely deprecated. Full deletion
  waits for the day Phase O is deliberately re-pinned, and this note is the
  record so the deferral cannot silently become the decision.
- **`null` means "no stoppage by that mechanism", never "use a default."**
  Fail closed. Under `professional` both counts are null, so no knockdown
  count stops a professional bout — which is what
  `decision_path_must_survive: true` has been asking for while being
  contradicted thirty times out of thirty.
- The off-by-one is corrected: where a limit applies, the fight ends **on**
  the Nth knockdown (`>=`, tested after the increment). A four-knockdown round
  is a thing a referee does not permit.
- `three_knockdown_rule: true` alongside a null round count is a canon
  contradiction and is **refused at load**, never defaulted to 3.
- `IntegratedBout` takes a `ruleset` id; the ruleset file actually fought
  under enters `contract.CANON` and the header records it; the contract bumps
  to v3. This is free today because no integrated artifact is pinned, and the
  frozen phases read no ruleset and do not move.
- **The default ruleset for the generic First Bell fight is `professional`**,
  because First Bell's definition requires both endings to be reachable and
  professional is the ruleset under which the decision path survives.
  `arcade_three_knockdown` remains authored, selectable, and is the identity
  ruleset for the arcade product later — it is not being demoted, it is being
  made real, since today no ruleset file is read at all.

## Ruling 3 (DD3) — `range_band` stays one band per move; `outside` stays punch-less

Section 1's argument is accepted because canon corroborates it three
independent ways: the jab's authored tip extension (1.05 ru) ends before the
`outside` band begins (1.1 ru); `threat_compression` declares offence exists in
`inside` and `mid` and releases in `outside` and beyond; and
`auto_advance_on_throw: false` already rules that no invisible lunge closes a
gap. Widening the jab's band would fix a symptom by lying about the authored
geometry. The outfighter's art is closing to mid and leaving again — which the
policy can now do, since a fighter with no legal punch seeks a working range
instead of standing still. **The eventual step-and-jab composite action is
acknowledged as the right future answer for outfighting feel and goes to the
backlog as its own decision; it is not smuggled in here.**

## Ruling 4 (DD4) — the body knockdown WAITS ONE MEASUREMENT

That boxing has body knockdowns is not in dispute — the biomechanist, the
referee and the boxing-memory specialist all said so, and the drainer's
authored win condition implies it. But making `torso_lower` knockdown-relevant
is a change to what canon says, layered on top of Ruling 1's change to how
canon is read. **Two population changes at once make the measurement
uninterpretable.** The project's rule is structure before numbers and
measurement before structure-on-structure: land Ruling 1, measure, then author
the body knockdown as its own decision with the threshold disposition it will
inevitably interact with. Deferral here is sequencing, not doubt.

## Ruling 5 (DD5) — `pressed × landed` is accepted as effective aggression, until `thrown` exists

Section 4's implementation is accepted: ground advanced that bought clean
punching, with a fighter who marches forward and misses scoring zero — which
is the seminar's own teaching, expressed with no invented conversion constant.
It is the honest maximum available from today's evidence vector. `thrown` is
added to the bout's per-round evidence (a one-line increment where an attack
commits), and when it exists the aggression term is re-ruled on accuracy —
that re-ruling is expected and does not need a new decision number unless the
shape changes.

---

## What this decision deliberately does not do

It does not touch `pressure_threshold`, does not add knockdown-relevant
regions, does not define `hurt`, does not choose a difficulty tier for the
generic fighter (the tier-free reading — latency = canon's floor — stands
until tiers are wired deliberately), and does not change any authored number
anywhere. Every one of those waits on the same gate: **the re-measured
thirty-seed sweep under these rulings.** That sweep is the next evidence this
project produces, and everything in it remains a diagnostic under Decision
0032 §3 until disposed.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 04:11 UTC | Decision 0033 end ] -->
