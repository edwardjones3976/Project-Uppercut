<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 23:40 UTC | START ] -->

# Decision 0013 — Guard geometry: nuance in the model, simplicity at the controller

**Status:** accepted; ratified by the Director in Decision 0014  
**Date:** 2026-08-04  
**Ratified:** 2026-08-06  
**Supersedes:** nothing. **Extends:** Decision 0010 (guard postures are coverage extents)

## Question

Should blocking become continuous and rotational — guard coverage as an angular
function rather than two height lanes?

The question arrived bundled. It is really two, and they have different answers.

## Decision

**A. The model gains a lateral axis. Yes.**

Coverage becomes angular rather than two-valued. Named postures do not disappear:
they become special cases — points on the coverage surface — so Decision 0010
stands and every emergent result Phase L proved still falls out.

Three things force it, none of them a reference game:

1. The Director's per-hand mechanic is only half-implementable without it. "Open
   on the side you punched from" needs a side; today's high/low lanes express
   only "open where your hand went."
2. `pose_geometry` already carries the hook as a **named simplification**
   (`blockable_either` → high) explicitly pending 2D lateral geometry. Hooks are
   a large part of what makes boxing read as boxing, and they are currently
   approximated.
3. The project's own core design rule is angular in spirit — a guard protects the
   interception *path*, not the target. High/low is a two-value approximation of
   something the rule already describes as continuous.

**B. The controller does not gain analog guard steering. No.**

Nearly-continuous rotational blocking is a simulation-pole mechanic. Our own
reference study (`docs/design/fight_night_design_study.md`) placed that pole
deliberately opposite where this project sits, and the charter's promise is
mechanics a coach would recognise "in a package that plays fast and reads
clearly," with depth in decisions rather than finger gymnastics.

So: the simulation carries angular coverage, per-hand commitment and interception
paths. The player expresses defence through legible choices — which posture,
which hand to commit, when to spend commitment — and the angular consequences
resolve automatically. A coach watching sees correct boxing; a player is not
steering a guard with a thumbstick.

This is also the honest answer to the external review's C+ on game feel. A larger
continuous input surface makes the truth deeper and the game harder to read,
which is the direction that grade warned about.

## Sequencing, which is the part with a real cost

The Director ratifies this order:

1. **Phase P — the hand is the unit.** Per-hand guard, then per-hand chaining and
   arm fatigue, both of which canon authors and the C++ core must share.
2. **CPU decision policy from observable evidence.** The roadmap's own step 9,
   including the rest and aggression semantics decided in Decision 0014.
3. **Complete live generic round and bout integration.** The current high/low
   geometry must function end to end before a new axis is judged.
4. **Lateral geometry.** Land it as a new phase with its own contract and pin,
   before the Adewale-versus-Calvin named-fighter vertical slice.

The reason lateral geometry is later is not that it matters least. It is that
blocks must be judged inside a fight that behaves like a fight. Building angular
coverage before policy and the live bout would measure it against an incomplete
organism, repeating the trap seen in earlier erosion and stoppage work.

## Consequences

- `pose_geometry` gains a lateral coordinate for guard volumes and punch paths;
  the hook's named simplification is retired rather than carried.
- Posture extents become angular functions. This **extends what a posture's
  extents mean** rather than merely reading them — which is why this is a
  decision record and not a quiet edit.
- Any phase whose PASS depends on the current two-lane geometry stays frozen.
  Lateral geometry lands in a NEW phase with its own contract and its own pin.
- Discrete postures remain the authoring surface, so guard catalogs, CPU
  reasoning and commentary vocabulary do not have to be re-expressed.

## What this decision does not do

It does not adopt any mechanic from a named product. Real boxing is the source;
the reference studies are guidance and motivation only, per the standing Director
directive, and no protected content, naming or presentation enters this project.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 23:40 UTC | END ] -->

<!-- [ OpenAI Director | GPT-5.6 Thinking | 2026-08-06 12:27 PDT | ratification and sequencing amendment ] -->
