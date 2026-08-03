<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:52 UTC | START ] -->

# Basic Punches — ROADMAP Phase 1A step 6

Canon: `data/punch_model.json` · Schema: `schemas/punch_model.schema.json` ·
Validator: `tools/uppercut_validate/punches.py` · Tests: `tests/test_punches.py`

**Rule 18.** Definitions only. No punch has been thrown in the engine, and every number below is a
tuning hypothesis.

## What this step is not

The move table already answers what each punch *is*. `data/moves/generic_sandbox_moves.json` carries
all nine properties ROADMAP line 51 requires from every attack — startup, active contact, recovery,
range, stamina cost, guard interaction, hit reaction, counter vulnerability, positional consequence —
across seventeen entries. Restating that here would create a second source of truth for the same
facts, which is how two documents start disagreeing.

So step 6 answers the other half: not what a punch is, but what **throwing** one costs.

## Commitment

A thrower can never take a punch back. `thrower_cancelable_phases` is empty by construction and the
schema pins it at zero length, because the moment a fighter can cancel a windup on reaction, every
counter in the game becomes a guess about whether the opponent meant it. Only being struck interrupts
a punch, which is the same fact the animation interrupt tiers already encode from the other side — a
struck fighter never finishes throwing.

The input buffer is two ticks and the schema caps it at four. A buffer is a responsiveness feature
(Rule 19: the game must feel immediate), but an unbounded one is a commitment loophole: a punch
queued eight ticks ago executes on a read that has since stopped being true.

## The recovery differential — where blocked < dodged < whiffed becomes real

`data/contact_classes.json` declares the ordering as `commitment_tier`: blocked 1, dodged 2,
whiffed 3. Until now that was a number in a file with nothing downstream of it. This step turns it
into frames a fighter can feel:

| Outcome | Recovery multiplier | Counter window (ticks) |
|---|---|---|
| clean / solid | 1.0 | 0 |
| grazed | 1.0 | 1 |
| brushed | 1.0 | 2 |
| blocked | 1.15 | 4 |
| dodged | 1.3 | 7 |
| whiffed | 1.5 | 10 |

Two boxing facts are load-bearing here. **Landing is never punished for landing** — every landed
class keeps a 1.0 multiplier, and the validator rejects any canon that gives a connecting punch a
worse recovery than a missing one. And **brushing costs more exposure than connecting cleanly**, not
because glancing hits are bad, but because the arm travelled further past its target.

The gap between blocked and dodged is the mechanical statement that the defender who *moved* earns
more than the defender who *covered*. The validator enforces both orderings: non-decreasing across
the canonical tiers, strictly increasing across the three miss classes.

## The gates: nothing is rescued, nothing is eaten

Two prohibitions that pull in opposite directions and both matter.

**Range (Rule 12).** A punch thrown outside its authored band whiffs. Full stop — no auto-advance on
throw, no distance edit, no magnetic correction. The bands come from `data/movement_model.json`
rather than being restated here, so there is exactly one geometry.

**Stamina (Rule 19).** An exhausted fighter still throws. `input_ever_ignored` is a const `false`.
Low stamina raises startup by up to 1.35× and costs up to 0.25 of contact alignment, which the
collision model's quality bands then read — so exhaustion arrives as visibly sloppier boxing rather
than as a controller that stopped responding. Punishing tiredness by eating inputs is the single
fastest way to make a fighting game feel broken.

## The repetition economy — the hard one

Rule 4 is unusually specific: a predictable action becomes punishable "because of observable pattern
recognition, stamina, position, commitment, defense, and counterplay — not because the game secretly
decides that repetition is prohibited." Writing "spam is punished" is easy. Writing it so it is
*true* takes four mechanisms, each declaring what it fires on and how you can see it:

- **arm_fatigue** — the throwing arm accumulates work; arm condition and guard integrity visibly
  degrade on the side doing it. *Costs the thrower.*
- **position_cost** — throwing without resetting the feet cedes ring position. *Costs the thrower.*
- **opponent_read** — a pattern seen more than once arrives against earlier guard and evasion.
  *Helps the defender.*
- **counter_window_growth** — the same punch from the same timing becomes easier to time. *Helps the
  defender.*

None fires on a repeat count. The validator scans `fires_on` and `observable_as` for bookkeeping
language — "repeat count", "the Nth", "after N" — and fails the model if it finds any, because a
mechanism described in counter terms will be implemented in counter terms.

The check that took the longest to get right is the two-sided one. A model where every mechanism
targets the thrower passes every obvious test and is still wrong: the spammer gets tired, but the
opponent never gets a better chance to make them pay. That is punishment without counterplay, and
Rule 4 asks for both. The validator now requires at least one mechanism on each side.

And the inverse guard: **unanswered repetition stays legitimate.** A jab that keeps working because
nobody answered it is not spam and takes no penalty. Every mechanism above requires the opponent to
have done something — fatigue requires the work, the read requires the observation, the counter
window requires the offer.

## Chaining

Combinations exist because recovery overlaps the next windup, not because a combo table permits them.
A link may begin no earlier than halfway through recovery and never during active contact. Opposite
hand links at 1.0× startup — the other hand was already loaded, which is why the one-two is the first
combination anyone learns. The same hand costs 1.4× because it has to retract first, and the same
*power* hand costs 1.8× because the weight has to come back. Nobody throws two right hands back to
back and keeps their balance.

`free_cancel_permitted` is const `false` here too, so chaining cannot reintroduce through the back
door what commitment closed at the front.

## Cross-file locks

- Every contact class in `contact_classes.json` has exactly one recovery row, and no others exist.
- Every offensive move's `range_band` exists in the movement model.
- Every offensive move has non-zero startup, active, recovery and stamina cost — a free punch is a
  spam engine, and a punch with no startup has no counterplay.

## What step 6 deliberately leaves open

The stamina *pool* and its recovery curve are step 8. Guard and evasion as chosen actions are step 7.
Which punch a CPU fighter picks, and why, is step 9. This file defines what any of them costs the
moment it is thrown.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:52 UTC | END ] -->
