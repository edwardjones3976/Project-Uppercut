<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 15:35 UTC | Decision 0036 start ] -->
# Decision 0036 — The count was eating the round, and volume is still not governed

**Status:** ACCEPTED (delegated).
**Authority:** the owner's standing in-session delegation, 2026-08-09.
**Gated on:** Decision 0035, which froze `pressure_threshold` until volume was
governed and said the sweep would be re-run once it was.

## The ruling

**`pressure_threshold` stays at 0.57. Again.** And a claim this project made
one commit ago is withdrawn: **volume is not governed.** It looked governed,
and the appearance was a measurement artifact this decision exists to correct.

## The correction, stated plainly

The guard commit reported *"landed punches per round: ~150 → 26.8"*. That
comparison was invalid. The 26.8 was measured at the CURRENT threshold, where
knockdowns are so frequent that the count consumes most of the round: at 0.57
the fight produces ~20 knockdowns per round, each running an eight-second
count, which is roughly 160 seconds of counting inside a 180-second round.
**The round was not quiet because the guard was working. It was quiet because
almost nobody was allowed to fight in it.**

Raise the threshold so the counts stop, and the real volume appears:

| threshold | kd per landed punch | kd per round | **landed per round** | stops | decisions |
|---|---|---|---|---|---|
| 5700 (current) | 0.753 | 20.26 | **26.9** | 4 | 6 |
| 8000 | 0.411 | 17.62 | 42.9 | 6 | 4 |
| 11000 | 0.171 | 14.19 | 83.0 | 6 | 4 |
| 14000 | 0.099 | 11.07 | 111.8 | 8 | 2 |
| 15500 | 0.097 | 12.29 | **127.0** | 3 | 7 |

Total landed punches across the ten-seed population rise from 2,206 to 11,907
— **5.4× more punching happens once the counting stops.**

**What the guard actually bought.** Pre-guard, Decision 0035 measured ~156
knockdown-capable landed punches per round. Post-guard, with counts out of the
way, 127. That is a real ~19% reduction and the mechanism is right, but it is
not the five-fold change the earlier number implied. The guard was necessary
and is not sufficient.

## Why the threshold is still refused

It behaves correctly on the axis it owns — knockdowns per landed punch falls
0.753 → 0.097, monotonically, exactly as a threshold should. And knockdowns
per round still sits at **12.3 at the top of the range**, because 127 landed
punches a round against a 9.7% knockdown rate is twelve knockdowns however the
threshold is set. Choosing a value here would once again fit a number to a
volume nobody intends to keep.

Both result paths stay busy across the entire range (stops 3–8, decisions
2–7), so canon's stated criterion cannot discriminate between candidates
either. There is no evidence-supported choice available, and inventing one is
what this project calls fitting.

## The real question, named

**Throw rate.** Roughly 127 landed punches per round implies something near
270 thrown; a real round is 40–70 thrown and 15–25 landed for both fighters
combined. The fight throws about four times too much, and every defensive
mechanism added so far has trimmed the edges of that rather than touched it.

The mechanisms canon authors that could govern it, and their state:

- `posture_economy` hold costs — **now read** (this session), and evidently
  not enough on their own.
- `punch_model.outcome_recovery` — **now read**, blocked/dodged/whiffed
  recovery multipliers. Also not enough on its own, and worth noting why: the
  multiplier is applied to the recovery *remaining* when a punch resolves,
  which is the tail rather than the whole commitment.
- `punch_model.repetition_economy` and `chaining` — **unread.** These are the
  authored answers to throwing the same thing forever and to what a
  combination costs.
- `stamina_gate` on `punch_model` — **unread.**
- The policy's own attack branch: `PUNISH_RECOVERY` produced 674 of 677
  punches in the Section 2 simulation, so aggression bias barely reaches throw
  rate at all and the fight is essentially one branch firing whenever an
  opponent is recovering — which, with everyone always recovering, is always.

## Consequences

1. `pressure_threshold` remains frozen. Two decisions have now refused it on
   evidence; a third refusal is not expected to be needed, because the next
   measurement should finally be taken on a fight with a boxing-plausible
   work rate.
2. **Throw rate becomes the critical path**, ahead of the body knockdown and
   ahead of C++ parity. The candidates are canon's unread economies —
   `repetition_economy`, `chaining`, `stamina_gate` — and the policy's
   single-branch offence.
3. The claim "volume is governed" is withdrawn from the record. The guard's
   own numbers stand: it blocks, it is byte-identical to Phase L, and it cut
   volume by about a fifth.

## On the measurement mistake itself

This is the second time in two decisions that a statistic chosen without care
pointed the wrong way — first knockdowns-per-fight conflating rate with
duration, now landed-per-round conflating volume with fighting time. Both were
caught by continuing to measure rather than by reasoning, and both are on the
record. The lesson is cheap to state and apparently expensive to learn: **in a
fight that stops itself constantly, every per-round statistic is really a
statement about how much of the round was a fight.**

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 15:35 UTC | Decision 0036 end ] -->
