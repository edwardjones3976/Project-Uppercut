<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 06:20 UTC | START ] -->

# The reference reaches the cards — and the 16.7× gap factorises into three known omissions

**2026-08-05.** Phase O has been held on a conversion rate too high by 19.1×, and
tonight ruled out every volume explanation for it in turn: contact grading, CPU
policy, difficulty tiers, decision cadence, commitment frames, the guard's hold
cost, and finally work rate itself. Slowed to a boxer's 76 punches per round the
gap only falls to 6.0×, and **not one bout in 24 reaches the cards at any swept
interval**. So the question stopped being "which of our numbers is wrong."

Canon's 0.57 threshold was swept against the **reference simulator**, not against
this core. That is a thing we can just run.

## The reference goes to the cards

| | core | reference | ratio |
|---|---|---|---|
| thrown per fighter-round | 236.8 | 40.7 | 5.8× |
| connect % | 53.0 | 42.4 | 1.3× |
| knockdowns per minute | 6.36 | 0.38 | **16.7×** |

**20 of 24 reference bouts went to the cards.** `decision_path_must_survive` is
satisfied there and always has been. The invariant is not aspirational and the
threshold is not mistuned — the reference meets both with canon's own numbers.

## The gap factorises

| factor | ratio | what it is |
|---|---|---|
| volume | 5.8× | punches thrown per fighter per round |
| accuracy | 1.3× | share of them that land |
| lethality | 2.3× | knockdowns per **landed** punch (0.0760 vs 0.0332) |
| product | **16.7×** | |

Three independent factors, multiplying to the whole gap with nothing left over.
And each one lands on something already known.

**Accuracy.** 30.4% of reference punches miss before any guard check ever runs —
14.8% swept for no overlap, 15.6% actively dodged, the dodge amplified by a slow
punch's telegraph and by the defender's read of a repeated pattern. In the core
that figure is **zero**. Geometry replaced the reference's probabilistic guard
stage, which is a real determinism win and the right call; it silently dropped
the sweep and evasion stages standing next to it. Nothing in this core misses.

**Volume.** The reference logs **zero** out-of-range attempts, and that is the
point rather than an absence of the mechanism: its policy only throws what the
current range band permits, so distance shapes punch *selection* itself. Our core
stands at one fixed distance forever, every punch is always available, and the
action set gets thrown flat. It is also, exactly, why `uppercut_rear` landed zero
of 532 — an inside-band punch thrown all night from outside, in a core with no
bands.

**Lethality.** 2.3× per landed punch is what remains after volume and accuracy
are divided out, and it is the size of the stamina inflation measured
independently twice tonight: 2.17× from floor to the median eligible landing,
2.74× median pressure inflation. Fighters here arrive at every landing emptier
than the reference's do — and 28.8% of everything they spend on punching is paid
into the uppercut that cannot connect.

## What this actually says

The three factors are not three problems. **Two of them are the missing range
model, and the third is what the missing range model does to the stamina
economy.** A core with range bands would throw fewer punches (selection is
constrained), land a smaller share of them (distance is a miss mechanism the
guard is not), and stop burning a quarter of its stamina budget on a punch that
is never in range.

Six phases of hypotheses died on the volume side of the pressure formula because
that is where I kept looking. The defect was never in the formula. It is one
stage upstream of everything I was measuring: the core implements the reference's
*resolution* pipeline and skips its *range* pipeline, and every downstream number
is a faithful computation over a fight that has no distance in it.

## For the Director

Nothing here is a tuning proposal and none of it edits canon. Three things worth
a decision:

The range model is authored — `movement_model.range_bands` with hysteresis, and
`punch_model` gives every move its `range_band`. The core reads none of it. That
is a phase, not a patch, and it plausibly resolves Phase O as a side effect
rather than by being aimed at it.

The sweep and evasion stages need a determinism call. Geometry is strictly better
than dice and it is why the marker stream is byte-identical across primitives,
mannequins and the full arena. But a geometric evasion needs a body that can slip,
and today it has neither the geometry nor the dice. Either answer is defensible;
the current state — silently neither — is the one that is not.

Whether `pressure_threshold` and the stamina economy need anything at all should
be re-asked **after** range exists, and not before. On tonight's evidence the
honest expectation is that they need nothing.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 06:20 UTC | END ] -->
