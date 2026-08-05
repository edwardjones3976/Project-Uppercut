<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 00:10 UTC | START ] -->

# The CPU policy is not the blocker either — I was wrong, four times running

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 02:21 UTC | QA: superseded in part START ] -->
> **QA correction, added after the fact.** A confound found later the same night
> invalidates the *conclusion* below, though not its measurements. Every sweep in
> this entry compared TOTALS across bouts that all end on the three-knockdown
> rule, so bout length was set by the outcome being measured. Totals were
> therefore normalised by their own result, and any claim here of the form
> "pacing is not the driver" is unsafe.
> Read `2026-08-05-the-sweeps-were-measuring-the-wrong-thing.md` before acting on
> anything in this entry. The original text below is left unedited on purpose.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 02:21 UTC | QA: superseded in part END ] -->

**2026-08-05.** Since the first Phase O sweep I have said, in three commits and a
decision record, that the dead decision path would come back once fighters
stopped choosing uniformly at random. Canon's own note supported it: the 0.57
knockdown threshold was swept against a *policy*, and a coin does not pace
itself. It was a good hypothesis. It is wrong.

## What was measured

`cpu_decision_model.difficulty_tiers` authors both pacing dials, so no invention
was needed. Two real gaps existed and both were closed:

**Cadence.** The core decided every `decision_interval_ticks` = 4. Canon's
*slowest* tier reacts every 20 and its fastest every 6 — the slice had been
deciding five times faster than a novice and 1.5× faster than a champion.

**Aggression.** Uniform choice over eleven actions throws 5/11 = 0.4545 of the
time, between club and contender, while reacting faster than a champion.

All four authored tiers, 24 seeds, three rounds, per-hand guard in place:

| tier | cadence | aggression | blocks | landed | knockdowns | stopped | decisions |
|---|---|---|---|---|---|---|---|
| novice | 20 | 0.35 | 1093 | 1283 | 104 | 24/24 | **0** |
| club | 14 | 0.45 | 1046 | 1330 | 106 | 24/24 | **0** |
| contender | 10 | 0.55 | 986 | 1421 | 103 | 24/24 | **0** |
| champion | 6 | 0.60 | 979 | 1376 | 105 | 24/24 | **0** |

## The result

**Knockdowns are flat at ~104 across a 3.3× range of decision cadence and a 1.7×
range of aggression.** Slowing a fighter to a novice's twenty-tick reaction — a
third of the work rate — does not change how often he goes down. Every bout still
ends inside the limits.

That is not a small correction to the hypothesis. It kills it. Pacing is not the
driver, which means the remaining excess is in the **pressure arithmetic itself**,
not in how often it is invoked.

## Where it probably is, stated as a hypothesis this time

Canon's pressure is a product:

    force × (undamaged_baseline + accumulated) × (1.4 − stamina_frac) × balance × guard

Of those, `accumulated` is the term that does not care how often anyone punches:
it is jaw and head condition as a fraction of capacity, and Phase N already
recorded that head and jaw **saturate within ninety seconds** because nothing
consumed them. At saturation `(0.55 + 1.0)` nearly triples pressure, and the
count's 45% relief is recovered within a few more landings. A flat knockdown rate
across every cadence is exactly what a saturation-driven term looks like: the
fighters arrive at the same condition ceiling regardless of how fast they got
there.

**The next measurement is to instrument the four terms of the product** at each
knockdown and report which one carries it — not to adjust anything. Four
consecutive wrong diagnoses is enough to stop guessing and read the numbers.

## The honest tally

Today's wrong calls, in order: the canvas artefact was the debug floor (no), then
z-fighting (no, it was painted artwork); grading was the Phase O blocker (half —
necessary, not sufficient); the guard stage was the blocker (partly — it fixed
blocks and not the fight); the CPU policy was the blocker (no). Each cost a
Python sweep of a few seconds because the contract came first, which is the
method working — but the pattern is a person reasoning ahead of his evidence, and
the correction is to instrument before predicting.

What the four wrong calls did buy: contact quality, per-hand defence, a working
guard where there was none, and now a measured elimination of pacing. Nothing
built on them is invalid. The diagnoses were wrong; the mechanics they produced
were each independently correct and are each independently proven.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 00:10 UTC | END ] -->
