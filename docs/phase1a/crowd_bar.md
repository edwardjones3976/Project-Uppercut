<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:54 UTC | START ] -->

# Crowd Bar — ROADMAP Phase 1A step 11

Canon: `data/crowd_model.json` · Schema: `schemas/crowd_model.schema.json` ·
Validator: `tools/uppercut_validate/crowd.py` · Tests: `tests/test_crowd.py`

**Rule 18.** Definitions only; every number is a tuning hypothesis.

## Contract, then mechanism

`data/crowd_contract.json` has stated Rule 12 as law since Phase 0: eleven rewardable behaviours,
three explicitly insufficient ones, and a prohibition list covering scores, judging criteria and
every flavour of hidden generic multiplier. What it never provided was a mechanism.

This step supplies one, and the validator's main job is making sure the mechanism obeys the contract
rather than restating it. Every gain source must be a behaviour the contract declares rewardable;
none may be one it declares insufficient; and every rewardable behaviour must actually pay
something, so the mechanism cannot silently drop half the law.

## Two devices stop farming, and only one of them is obvious

**The risk gate** is the obvious one. Sources that require risk pay nothing when the action carried
no counter exposure — landing on a fighter who is down, stunned beyond response, or out of range to
answer earns no crowd. The validator additionally requires the three highest-paying sources to all
require risk, because a safe action paying top rate makes the gate decorative.

**Novelty** is the subtle one, and it is where Rule 4 and Rule 12 pull against each other. Repetition
must stop being a meter engine, but Rule 4 explicitly protects legitimate repetition — a jab that
keeps working because nobody answered it is not spam. So the multiplier decays toward a floor that
is **strictly above zero**, and the validator fails a floor of zero with that reasoning attached. A
meter that zeroes a repeated action has prohibited it rather than de-emphasised it.

The crowd's decline is also observable: the reaction to the fourth identical hook is visibly smaller
than to the first. That matters because Rule 4 requires the punishment to arrive through something a
spectator can see, not through bookkeeping.

## Holding a full bar is a decision

The bar decays after a grace window, and a full bar expires after 3600 ticks. Without those, banking
a bar early and coasting is free, and a permanently-full bar is a threat with no decision attached.
It carries between rounds because the crowd remembers the fight rather than the bell.

At full, the choice is the Ultimate **or** the Full-Crowd Trait, never both from one bar — Rule 12,
cross-checked here and again in the ability model, because that is the rule a later contributor is
most likely to break by accident.

## What the crowd may never touch

Scores, judging criteria, contact truth, condition truth, stamina truth, and any hidden generic
damage, defense, speed, stamina or comeback multiplier. All seven are schema constants pinned to
`false`. The Crowd Bar is loud, and it is earned, and it is not a judge and not a rubber band.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:54 UTC | END ] -->
