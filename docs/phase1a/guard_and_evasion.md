<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:40 UTC | START ] -->

# Guard and Evasion — ROADMAP Phase 1A step 7

Canon: `data/guard_evasion_model.json` · Schema: `schemas/guard_evasion_model.schema.json` ·
Validator: `tools/uppercut_validate/guard.py` · Tests: `tests/test_guard.py`

**Rule 18.** Definitions only. No guard has been held in the engine, and every number is a tuning
hypothesis.

## The promise this step keeps

Decision 0010 closed the pinned "10 guards vs. 2 guard volumes" drift on mechanism: a posture
modulates the *coverage extent* of the two collision volumes rather than adding volumes or branching
the pipeline on a name. It shipped with four illustrative examples and an explicit note that the
authored posture set was step 7 content.

This is step 7. All ten named guards from `docs/design/boxing_guard_matchups.md` are now data —
high guard, peek-a-boo, Philly shell, cross-arm, long guard, low lead hand, tight elbow, ear-muff,
forearm frame, active hands — each supplying an extent for `guard_high` and `guard_body` plus the
costs it pays to hold. The validator checks every extent against the collision model's own
`min_modulated` / `max_modulated` bounds, so a posture cannot quietly exceed the geometry the
collision layer declared.

## Every guard is a trade, enforced rather than asserted

The design principle says a guard protects some lanes while exposing others. Two checks make that
structural instead of aspirational. A posture covering both volumes at 0.95 or above is rejected —
that is not a guard, it is an off switch. A posture covering neither meaningfully is rejected too;
that is a stance.

The subtler one is pricing. The ear-muff cover is the maximum-head-coverage posture in the set and
it lists **no** cheap offense, because opening the clamp is the price of throwing anything. A model
where that posture also kept full mobility, full vision and cheap stamina would be strictly best,
and the fighter holding it would never have a reason to leave — which is exactly the "indefinitely
safe state" Rule 4 prohibits. So the validator requires any posture with no cheap offense to pay in
mobility, vision or stamina. The ear-muff pays in all three.

## The two reconciled conditionals are locked to their state ids

Cross-arm and Philly shell are the postures whose coverage canon resolves *conditionally* — the
cross-arm bar low-aligned or high-and-split, the shell roll timed or late. Those exact state ids ship
in the collision model as worked examples, and the validator now requires this file to declare the
same ones. A rename here would silently unhook the conditional coverage that the reconciliation log
and Decision 0010 were both written to protect. It fails loudly instead.

## Evasion outranks covering, and the claim is checked against the files that pay it

`evasion_economy.outranks_guard` is a claim, and claims are cheap. The validator cross-checks it in
two places rather than trusting it: the collision pipeline must still resolve `active_evasion` before
`guard_intercept`, and the punch model must still give a dodge a larger counter window than a block.
If either changed, this file's claim would be unbacked, and the check says so in those words.

The cost side matters as much. A mistimed evasion carries a six-tick penalty, because an evasion that
is free when it fails makes covering pointless. Slipping is better than blocking when it works and
worse when it does not — that asymmetry is what makes it a decision rather than a default.

Four defensive answers are authored, split by kind. `slip_lead` and `roll_under` are **active-window**
evasions: they vacate real hurtbox-backed regions, and their active ticks are frame-locked to the
move table exactly, the same lock the animation model uses. `step_out` and `pivot_lead` are
**positional** answers — they remove the fighter from reach or change the angle rather than clearing
a lane, so they vacate nothing and carry no window. Collapsing those two kinds together would have
let a step register as a dodge, which is a different thing and pays a different price.

Every evasion declares what beats it. `roll_under` is beaten by the uppercut, because the uppercut
rises into where the head is going.

## Guard integrity: earned, not counted

Blocking costs something (Rule 14) and a guard break is earned through intelligent varied pressure,
never through repetition count (Rule 4). `degrades_from_repetition_alone` is a const `false` the
validator enforces.

An opened guard is deliberately *not* a stun. It moves the posture to its weaker alignment state,
which the collision model reads as reduced coverage extents — the fighter keeps acting, keeps
inputting, and is simply covering less. The validator rejects any `opened_state` describing a
disable or a stun, for the same reason the punch model refuses to eat a tired fighter's input.

## What step 7 leaves open

Which posture a fighter chooses, and when, is step 9 (CPU decision-making from observable
information). What the accumulated damage does is step 8 (stamina, condition, knockdowns). The
matchup tables stay in `boxing_guard_matchups.md`, which this file names as authoritative and the
validator confirms — one table, one home.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:40 UTC | END ] -->
