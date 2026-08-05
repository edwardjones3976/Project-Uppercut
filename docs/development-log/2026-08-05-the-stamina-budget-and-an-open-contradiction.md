<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:00 UTC | START ] -->

# The stamina budget — and an open contradiction I could not close

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 02:21 UTC | QA: superseded in part START ] -->
> **QA correction, added after the fact.** A confound found later the same night
> invalidates the *conclusion* below, though not its measurements. Every sweep in
> this entry compared TOTALS across bouts that all end on the three-knockdown
> rule, so bout length was set by the outcome being measured. Totals were
> therefore normalised by their own result, and any claim here of the form
> "the hold cost is 11% of the story, so the driver is volume" is unsafe.
> Read `2026-08-05-the-sweeps-were-measuring-the-wrong-thing.md` before acting on
> anything in this entry. The original text below is left unedited on purpose.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 02:21 UTC | QA: superseded in part END ] -->

**2026-08-05.** The last entry established that stamina carries the knockdowns
(2.74× median inflation, fighters at ~30% when they go down) and blamed the
per-tick posture hold cost. **That blame was wrong.** Measured:

| per full round (10,800 ticks, pool 100) | stamina | × pool |
|---|---|---|
| hold high_guard the whole round | 10.8 | 0.11 |
| hold tight_elbow the whole round | 10.8 | 0.11 |
| idle regeneration, whole round | 43.2 | 0.43 |
| **punch spend, canonical round (68 thrown)** | **155.7** | **1.56** |

**Punching costs 14× what holding the guard costs.** The hold is 11% of the pool
across three minutes; the punches are one and a half pools. Canon's per-punch
costs run 1.0 (jab) to 3.0 (uppercut) against a pool of 100 that regenerates 43
per round, so a round of 68 thrown punches spends about three and a half times
what it recovers. Fighters empty out because they punch, which is not a defect —
it is a boxing-shaped statement — and the knockdown formula then multiplies
pressure by up to 3.5× against an empty man.

## The contradiction, stated rather than smoothed over

This does not fit the tier result, and I could not reconcile them before running
out of session.

If punch volume is what empties the tank, then the novice tier — deciding every
20 ticks instead of every 4 — should have spent far less stamina and produced
noticeably fewer knockdowns. It produced 104 against the champion's 105. Either
the tier harness is not reducing volume the way its cadence implies, or something
else pins stamina low regardless of volume.

**That is the next measurement**, and it is a small one: report punches thrown and
end-of-round stamina per tier, from the same harness that produced the flat
result. Whichever way it lands, one of two things is true and both are worth
knowing — the harness has a bug, or stamina has a floor that volume cannot lift.

I am recording this as an open contradiction rather than picking whichever story
sounds better. Six wrong diagnoses today were each cheap because they were
falsified fast; a seventh dressed up as a conclusion would not be.

## Where the Director's question stands

Unchanged and still the right question, but now with the split attached:

> Should a fighter arrive at the third minute close to empty — and therefore
> three times easier to drop?

The measurement says he gets there by **throwing**, not by guarding. So the levers
are per-punch `stamina_cost`, the regeneration rate, or the pressure formula's
stamina weighting — and explicitly **not** `posture_economy`'s hold cost, which
the last entry wrongly nominated and which turns out to be 11% of the story.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:00 UTC | END ] -->
