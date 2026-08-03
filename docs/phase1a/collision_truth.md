<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | START ] -->

# Collision Truth - Semantics (ROADMAP Phase 1A, step 5)

**Canonical data:** `data/collision_model.json` - **Schema:** `schemas/collision_model.schema.json`
**Validator:** `tools/uppercut_validate/collision.py` (`python -m tools.uppercut_validate.cli collision`)
**Status:** definitions committed and validated. No engine implementation is claimed (Rule 18).

> **Order note.** This step was taken ahead of step 4 (animation states) by Director instruction on
> 2026-08-03. At the definitions level that is coherent - collision geometry does not depend on
> animation. At the *implementation* level it does: hitboxes and hurtboxes ultimately attach to
> animated skeletons, so step 4 remains a prerequisite for building this in the engine. Step 4 is
> still not started and nothing here claims otherwise.

## Why this layer exists

Rule 13 is the reason: *visible action and authoritative result must agree.* Every other honesty
guarantee in the project routes through this file. If a whiffed punch can be classified as a clean
landing, then the event log lies, the replay lies, the judging evidence lies, and the CPU learns from
fiction. So collision is defined as a **total ordered function** rather than a bag of heuristics.

## The pipeline: four stages, seven outcomes, no ambiguity

Every attack enters one pipeline and leaves with exactly one of the seven contact classes.

**Stage 0, sweep overlap.** Did the swept hitbox intersect anything at all? If not, the attempt
terminates immediately as **whiffed**. Ruling out non-intersection *first* is what makes "a visible
miss is never a clean hit" structural rather than aspirational. The sweep is continuous between
ticks, because discrete sampling would let a fast punch tunnel straight through a hurtbox - a visible
hit reported as a miss, the same lie in the other direction. And the model may never nudge distance
to rescue a wrong-range punch; that is magnetic correction, and it is prohibited by name.

**Stage 1, active evasion → dodged.** Ranked deliberately *above* the guard check. If a defender's
authored evasion window vacated the region, the result is a dodge even if the punch also passed near
the guard. That ordering is a value judgement with mechanical teeth: `data/contact_classes.json`
gives dodged a higher commitment tier than blocked, so the active defensive choice punishes the
attacker more than the passive one. Slipping should beat covering up.

**Stage 2, guard interception → blocked.** A guard volume covering the region must intercept *first
along the swept path*. That phrase is what makes a guard a physical object rather than a status flag.
Blocked force does not vanish: every guard volume declares what it absorbs into - the arms, guard
integrity, stamina - because Rule 14 says blocking reduces clean damage without erasing consequence,
and because that accumulation is how a passive blocker eventually gets opened by intelligent varied
pressure rather than by a hidden anti-spam rule.

**Stage 3, quality dispatch → clean | solid | grazed | brushed.** Contact reached a hurtbox; the four
landed classes are then selected by alignment bands that tile [0,1] with no gap or overlap, with
delivered force increasing strictly across them. Brushed contact is reduced but never zero. Closing
velocity modulates on top, bounded so that moving into a punch raises consequence and moving away
lowers it without either dominating the classification.

## What the validator caught - and why the fix is better boxing

The first run failed on the move table: uppercuts target the jaw (a high region) yet are authored
`blockable_low`, and my model rejected that as missing counterplay.

The move table was right and the model was wrong. **Interception follows the punch's path, not its
target region.** An uppercut travels *upward* into the guard: a dropped forearm stops it, and a high
shell does not - which is exactly why the uppercut is the punch that punishes a fighter hiding behind
a high guard. I had conflated "where it lands" with "what stops it." The model now maps each
`guard_interaction` value onto the guard *volumes* that intercept it, and the high/low guard choice
becomes a real trade-off instead of a label: high guard covers the head cluster and eats uppercuts
and body work, body guard covers the torso and eats hooks and straights upstairs. A regression test
pins the uppercut case so the correction cannot be quietly undone.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:44 UTC | START: coverage extents ] -->

## Ten guards over two volumes

The design reference names ten guards. This model declares two guard volumes. That count mismatch
sat pinned in the execution plan until a review pass forced the sharper question: the reference's
best content is *conditional* — a cross-arm bar riding low intercepts a chin-line uppercut and the
same bar riding high gets split by it; a shell roll that is timed turns an overhand and the same
roll arriving late lets it over the shoulder. A fixed `guard_interaction` → volume map cannot say
any of that. It knows which volume may block a path, not whether the volume is currently *there*.

Decision 0010 resolves it without adding volumes or branches. Each guard volume carries a
`coverage_extent` — how much of its nominal structure is actually presented this tick — and a
posture's alignment state moves that number. `guard_interception` still decides which volume is
permitted to intercept a given path; the extent decides whether it reaches. A posture is therefore
geometry, and the pipeline never learns its name.

Two bounds keep this from becoming a free parameter. No alignment may take an extent to zero, since
a guard covering nothing is a different posture rather than a misaligned one; and none may exceed
1.0, since anything above that would let an alignment cover more than the structure it belongs to —
the moment a guard stops being a trade. A third check earns its keep: the validator rejects a canon
in which every posture holds identical extents across its states, because that model would satisfy
the schema while expressing nothing, and the drift would be documented rather than closed.

The four worked examples shipped in the data are illustrative under Rule 18, present to prove the
mechanism can express the two contested rows. Authoring the real posture set is step 7.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:44 UTC | END: coverage extents ] -->

## Region truth and determinism

Eight hurtboxes map one-to-one onto the physically strikeable condition regions of
`data/condition_regions.json`, with side declared for the eyes and arms so eye damage stays
attributable to the side that took it. There is no generic health volume, and the validator refuses
to let two hurtboxes share a region or a guard configuration cover everything.

Determinism is fixed by three schema constants: swept volumes, a pre-tick snapshot so simultaneous
attacks resolve symmetrically (a genuine trade stays a trade, with neither landing silently
cancelling the other), and a declared evaluation order so container layout cannot reach the
authoritative log.

## Reproduce

```
python -m pytest -q tests/test_collision.py
python -m tools.uppercut_validate.cli collision
```

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | END ] -->
