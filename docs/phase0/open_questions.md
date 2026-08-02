<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ] -->

# Phase 0 — Open Questions

Places where PROJECT_RULES.md admits more than one honest reading. Each is implemented with a
default so work continues, and each default is **configurable in code** rather than baked in, so a
Director ruling changes one line instead of a rewrite. None of these is a proposal to change canon;
they are requests to disambiguate it.

## OQ-1 — Can one positive attribute compensate more than one severe negative?

Rule 10 says a value from −41 to −60 "requires a meaningful positive of at least +30", and so on up
the ladder. It does not say whether a single +80 can pay for two separate severe negatives.

- **Exclusive** (implemented default): each compensating positive is spent once. A fighter with two
  severe negatives must field two qualifying positives. This is the stricter reading and the one most
  consistent with "the model is give-and-take and must not permit unrestricted upward stacking."
- **Shared**: one qualifying positive satisfies every negative in its tier.

Impact is large: under *shared*, `illegal_shared_compensation.json` becomes a legal build. The test
suite asserts both behaviours so the consequence of the ruling is visible
(`test_compensation_binding_is_configurable`). Change via `Interpretation.compensation_binding`.

## OQ-2 — Does a +100 count toward "at most two attributes may exceed +70"?

Literally, +100 exceeds +70, so a fighter with +100 has spent one of the two slots. The alternative
reading treats the +100 clause as separate, allowing +100 plus two more above +70 — three elite
attributes total. Default: **it counts** (stricter). Change via
`Interpretation.hundred_counts_toward_over_seventy`.

## OQ-3 — "Every physical trait negative" over which set?

If a fighter declares only three of the nine physical attributes and all three are negative, is that
"every physical trait negative"? Default: **evaluated over declared attributes**, which makes partial
generic fixtures checkable. The alternative requires complete fighters to declare every attribute in
every family — cleaner long-term, heavier for sandbox fixtures. Recommend requiring complete
declaration for `roster_character` and keeping the declared-only rule for
`generic_test_fixture`; that split needs a ruling.

## OQ-4 — Attribute versus condition for Chin, Durability, Recovery, Composure

Rule 14 lists Chin, Durability, Recovery and Composure inside the *combat condition* list, alongside
head, eyes and arms. Rule 10 treats attributes as authored −100…+100 values. These four are plainly
both: an authored rating **and** a live state that degrades during a bout.

Implemented split: `data/attribute_families.json` holds the authored rating; `data/condition_regions.json`
holds the runtime state and names the governing attribute. Nothing from Rule 14's list is dropped.
Confirm the split is intended.

## OQ-5 — Attribute vocabulary is not canonical

Canon names some attributes directly (Power, Chin, Durability, Recovery, Composure, Ring Awareness,
Coachability, Ringcraft, Showmanship, stamina, balance, speed, technique, reach) but never publishes a
closed list. `data/attribute_families.json` proposes a 25-key vocabulary in three families. Rule 10
requires families to be explicit data, so *something* must be chosen before roster authoring.
This file is marked `status: proposed_pending_director_approval`.

Also note: `corner_chemistry` is deliberately **absent** from fighter attributes, because Rule 6 frames
it as a relationship between a fighter and a corner rather than a property of the fighter.

## OQ-6 — Is a third family ("mental") sanctioned?

Rule 10 explicitly protects two families from being all-negative: physical and technical. The proposed
taxonomy adds a third, *mental*, which carries no all-negative prohibition — meaning a fighter could
in principle be mentally negative across the board. Confirm that is acceptable, or extend the
prohibition.

## OQ-7 — Does the ±100 range apply to every attribute equally?

Rule 10's caps are global counts ("at most one attribute may equal +100"). If some attributes should
be range-limited individually — e.g. Chin capped below +100 for safety reasons, given Rule 14's
insistence that +100 Chin is not immunity — that constraint is not currently expressed anywhere.

## OQ-8 — Refund rate for negatives in the budget

Whichever cost curve is chosen, negatives can refund budget at full rate or at a discount. Full-rate
refund is the loophole most likely to permit stacking: build two severe negatives, buy two elite
positives. See `attribute_budget_candidates.md`; the refund rate is part of the same ruling.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ] -->
