<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:55 UTC | START ] -->

# Ability Architecture — ROADMAP Phase 1A step 12

Canon: `data/ability_model.json` · Schema: `schemas/ability_model.schema.json` ·
Validator: `tools/uppercut_validate/ability.py` · Tests: `tests/test_ability.py`

**Rule 18.** Architecture only. No fighter-specific ability is authored here, and none has run.

## The rule this step exists to protect

Rule 11 says no attack is unblockable by design. An ability system is precisely where that gets
quietly broken, because the temptation is to make the climactic move *feel* climactic by removing the
answer — invulnerability during the animation, a startup nobody can react to, a command input that
skips recovery. Every one of those is a small, reasonable-looking change that ends counterplay.

So they are schema constants rather than conventions. `counterable` is const `true`,
`grants_invulnerability` and `bypasses_commitment` are const `false`, for all three ability classes,
and the validator restates each failure in terms of what it costs: an ability that grants
invulnerability "removes the answer rather than raising the stakes."

## Abilities answer the same nine questions

Every ability must define startup, active contact, recovery, range band, resource cost, guard
interaction, hit reaction, counter vulnerability and positional consequence — the same nine
properties ROADMAP line 51 requires from every ordinary attack. An ability that skips them has left
the combat system rather than extended it.

Two floors back that up: a minimum startup, because an Ultimate that arrives faster than a jab is a
coin flip rather than a climax, and a recovery floor above the startup floor, because the whole point
of a big option is that missing with it costs something. A whiffed ability is punishable.

## Command entry is a way to ask, never a way to skip

Rule 15 permits motion inputs with explicit confirmation, and requires recognition to be trainable,
remappable, forgiving and consistent. It also forbids that entry bypassing stun, recovery, range,
resource cost, startup, tracking limits or whiff punishment. All six bypass flags are const `false`
and each is individually tested — recognition is forgiving; the fight is not.

## The shape of the set

Two Specials per fighter at roughly a third of a bar each, then one Ultimate and one Full-Crowd Trait,
both costing the entire bar and exclusive with each other. The Special must cost strictly less than a
full-bar ability. The full-bar choice is cross-checked against `crowd_model.json`, which owns the
bar — this file spends it, and the two disagreeing would be the exact drift the cross-lock exists to
catch.

The Full-Crowd Trait is deliberately not a strike: it is a fighter-defining state, which is what makes
the full-bar choice a real decision rather than a damage calculation.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:55 UTC | END ] -->
