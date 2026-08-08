# Decision 0030 — Defensive purity, non-engagement, and boxing-lore registry

**Status:** Accepted  
**Date:** 2026-08-08  
**Authority:** Director  
**Trigger:** Correction report `defensive_purity_and_non_engagement.md`

## 1. Terminology is corrected

The phrase **anti-running rule** is retired as normative Project Uppercut language.

The project distinguishes:

- **Defensive purity:** landing meaningful offense while denying return fire. This includes mobile out-boxing, circling, slipping, countering, hitting-and-moving, and other boxing in which the fighter is difficult to hit but still produces effective work.
- **Non-engagement:** sustained periods in which a fighter neither lands meaningful offense nor meaningfully contests the opponent, using avoidance/passivity primarily to prevent a fight from occurring rather than to box effectively.

Movement alone is not the discriminator. The discriminator is **effective output and contest participation over time**.

> **Hitting without being hit is mastery. Neither hitting nor being hit for long periods is non-engagement.**

## 2. Movement and stamina may not punish defensive success

No movement, stamina, damage, contact, or hidden resource rule may charge a fighter merely for:

- not being hit;
- moving while landing;
- circling;
- retreating in open ring;
- using defense successfully;
- denying an opponent clean contact.

Movement remains priced by actual authoritative displacement and its declared basis. Ring geometry may bound straight-line retreat. Lateral escape and ordinary back-foot boxing remain legitimate.

The existing defensive-purity validator is accepted as a regression guard.

## 3. No movement-model repin for prose alone

The proposed `defensive_purity_is_never_penalised` invariant is **not added to `data/movement_model.json` now**.

Reason: the principle is already protected by this accepted Decision plus the validator, while editing the hashed movement canon solely to restate the rule would move historical O/Q identities and require a re-pin with no gameplay benefit.

Historical pins are not churned for documentation placement.

If a later planned movement-canon revision already requires O/Q re-proof, the invariant may be embedded then without reopening this decision.

## 4. Where non-engagement belongs

The primary discriminator belongs in the systems that already evaluate boxing:

1. **Scoring:** clean punching, effective aggression, ring generalship, and defense determine who won the round. Defensive purity can win. Empty avoidance earns no special credit.
2. **Referee behavior:** once referee logic exists, profiles may prompt or warn repeated observable non-engagement under the shared rules. A referee may not alter punch truth, stamina, or judging criteria.
3. **Audience presentation:** observable inactivity may cool presentation intensity, while clean defensive mastery may earn crowd reaction. Presentation may not change authority.
4. **Crowd resource:** inactivity simply fails to earn the kinds of observable achievements that generate Crowd. No hidden anti-movement drain is introduced.

A future rolling engagement observation may be recorded for telemetry, refereeing, commentary, and post-fight explanation. It is **not** a direct movement/stamina penalty and may not become a hidden combat debuff.

## 5. Boxing-lore families become canonical design vocabulary

The following five families are accepted as Project Uppercut boxing-ideology IDs:

- `jab_control`
- `defensive_purity`
- `body_investment`
- `initiative_and_exit`
- `preparation`

They are not five new mechanics. They are a data-driven interpretive layer connecting existing mechanics and observable evidence to CPU strategy, training, commentary, corners, judging interpretation, and post-fight analysis.

The registry must eventually define, for each family:

- canonical ID;
- principle statement;
- observable triggers/evidence;
- systems allowed to consume it;
- systems forbidden to consume it;
- underlying mechanical authority it references;
- presentation phrases/idioms as non-authoritative aliases.

No lore entry may duplicate or override a combat formula.

## 6. Sequencing

Do **not** detour First Bell to build the complete lore system now.

Before sealed scoring/judging is pinned, add the minimal registry structure and wire `defensive_purity` and `body_investment` to the evidence those subsystems already produce. Add other family consumers as their owning systems become live.

The registry exists to prevent phrases from mutating into mechanics without authority.

> **Boxing language may explain the fight. It may not secretly rewrite it.**
