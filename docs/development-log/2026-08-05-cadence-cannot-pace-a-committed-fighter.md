<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:25 UTC | START ] -->

# Resolved: decision cadence cannot pace a fighter that commitment already paces

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 02:21 UTC | QA: superseded in part START ] -->
> **QA correction, added after the fact.** A confound found later the same night
> invalidates the *conclusion* below, though not its measurements. Every sweep in
> this entry compared TOTALS across bouts that all end on the three-knockdown
> rule, so bout length was set by the outcome being measured. Totals were
> therefore normalised by their own result, and any claim here of the form
> "reaction_ticks is inert as a pacing control" is unsafe.
> Read `2026-08-05-the-sweeps-were-measuring-the-wrong-thing.md` before acting on
> anything in this entry. The original text below is left unedited on purpose.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 02:21 UTC | QA: superseded in part END ] -->

**2026-08-05.** The previous entry left an open contradiction: punching empties
the tank (155.7 stamina a round against a 100 pool), yet slowing a fighter from a
champion's six-tick reaction to a novice's twenty changed knockdowns not at all.
Either the harness was not reducing volume, or something pinned stamina low
regardless. One table settles it.

| tier | cadence | aggression | punches thrown | end stamina | knockdowns |
|---|---|---|---|---|---|
| novice | 20 | 0.35 | 2,664 | 22.9 | 104 |
| club | 14 | 0.45 | 2,643 | 26.6 | 106 |
| contender | 10 | 0.55 | 2,711 | 27.6 | 103 |
| champion | 6 | 0.60 | 2,651 | 29.7 | 105 |

**Volume is flat.** A 3.3× change in decision cadence and a 1.7× change in
aggression bias produced a 2.6% spread in punches thrown. The dial is not
connected to anything.

## Why — and it is not a bug in the harness

A fighter may only act when `committed[i] == 0`. Punch commitment runs roughly
20–40 ticks. Every one of canon's authored reaction cadences — 6, 10, 14, 20 —
is **shorter than or comparable to the commitment it must wait through**. So the
fighter is not being throttled by how often he is asked; he throws the moment his
recovery ends and the next interval boundary arrives, and at every tier that is
very nearly the same moment.

`reaction.respects_commitment: true` and `may_cancel_own_commitment: false` are
canon's own rules, and they are correct. Their consequence is that
**`reaction_ticks` is inert as a pacing control in this action model.** Making a
fighter "slower to react" cannot make him throw less when commitment already
gates him harder than his reaction does.

This is a model finding rather than a defect. Canon's difficulty tiers were
authored to change *reaction*, and reaction is a real thing — it should govern
how fast a fighter answers something he observes, such as a counter window or a
slip opportunity. It was never a volume control, and using it as one was my
error, not canon's.

## What this means for the Director's question

The question stands and now has no confound:

> Should a fighter arrive at the third minute close to empty — and therefore
> three times easier to drop?

Every tier ends the bout at 23–30 stamina out of 100, and every bout ends by
stoppage. Since cadence cannot change that and the guard hold cost is 11% of the
spend, the only remaining levers are the ones named last entry: per-punch
`stamina_cost`, the regeneration rate, or the pressure formula's stamina
weighting.

And one genuinely new candidate this table surfaces: **commitment frames**. They
are what actually sets work rate, they are authored per move in
`animation_model`, and they have never been examined as an economic control. A
fighter who commits longer throws less and tires less. That is a boxing-shaped
dial nobody has turned.

## Tally

Seven wrong calls today, all cheap. This one was different only in that I named
both possible answers before measuring, and the measurement picked one. That is
the first time today the prediction was structured well enough to be settled
rather than replaced.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:25 UTC | END ] -->
