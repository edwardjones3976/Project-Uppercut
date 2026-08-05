<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 05:10 UTC | START ] -->

# The funnel — I was wrong about eligibility, and there is a punch that cannot land

**2026-08-05.** The conversion measurement left three candidates for Phase O and I
named eligibility as the one I would look at: 373 solid-or-clean head landings
across 24 bouts, roughly 24 per minute of fight, a number nobody had defended.
This counts the funnel stage by stage instead of inferring it, and puts the result
beside what professional boxing actually produces.

The outside benchmark matters here because **canon authors no expected landing
rate anywhere**. `movement_model` mentions punches only to say whether a stance
permits them. There is no internal number to check against, which is precisely why
this went unexamined for so long.

## The funnel

56,036 ticks across 24 bouts — 15.6 minutes of fight, both fighters.

| stage | count | survives | per fighter-round |
|---|---|---|---|
| punches thrown | 2,457 | — | 236.8 |
| reached the plane | 2,455 | 99.9% | 236.6 |
| not blocked | 1,602 | 65.3% | 154.4 |
| landed on the surface | 1,303 | 81.3% | 125.6 |
| landed jaw or head | 1,042 | 80.0% | 100.4 |
| graded solid or clean | 373 | 35.8% | 35.9 |

**Eligibility is not the suspect.** The funnel's own percentages are defensible:
65% of what reaches a guard gets past it, 80% of landings are jaw or head, 29% of
landings grade solid or clean. Those are boxing-shaped ratios. I had the diagnosis
pointed at the wrong stage.

## The top of the funnel is the problem

**237 punches per fighter per round.** Professional boxing runs 55–78, and 30–60
for heavyweights. We are at 3.0× the top of the band, and every downstream number
is a reasonable fraction of an unreasonable input. 35.9 flush head shots per round
is simply what 237 thrown punches buys at honest rates — a fighter in this model
absorbs more clean head shots per round than Roman Gonzalez, the busiest man in
the sport, lands punches of any kind.

The volume is not aggression. It is the decision clock: the core decides every 4
ticks — fifteen decisions per second — and punches are 5 of its 11 actions.
Canon's own slowest difficulty tier reacts every 20 ticks and its fastest every 6.
Measured earlier tonight, cadence was a 1.88× lever on bout length. Read against
boxing it is not a tuning knob at all; it is a constant set to a value no fighter
has ever had.

One more ratio worth noting: **99.9% of thrown punches reach the interception
plane**, and 53% of everything thrown eventually lands. Professional connect rates
run 25–40% overall, with CompuBox's power-punch average at 36.9%. Nothing in this
core misses — there is no distance, no evasion, no range management, so the only
thing between a punch and a body is the guard.

## And a punch that cannot land

| move | peak tip | needs | reaches? |
|---|---|---|---|
| jab_lead | 10,500 | 7,600 | yes |
| cross_rear | 11,000 | 7,600 | yes |
| hook_lead | 8,500 | 7,600 | yes |
| **uppercut_rear** | **7,200** | **7,600** | **NO** |
| body_straight_rear | 11,000 | 7,600 | yes |

`uppercut_rear` was thrown 532 times in the sweep and landed **zero** times. It
peaks 400 units short of a surface it must touch — about 5 cm at canon's scale.

It is not mis-authored. The uppercut is an inside punch and **this core has no
inside**: both fighters stand at a fixed opening distance and never close, so the
one punch in the set that requires closing the range can never be used. That is a
modelling finding, not a number to nudge.

And it is not free. The uppercut is the most expensive move in the set (30,000)
and the highest impact (9,499). Thrown 532 times, it burned **28.8% of every point
of stamina these fighters spent punching**, for nothing. Stamina is the term that
decides every knockdown in this model — a fighter who never tires is never dropped
in 373 eligible landings. So better than a quarter of the punch economy is being
paid into a punch that cannot connect, and the fighters arrive at the knockdown
threshold that much emptier for it.

That is not the whole of Phase O's gap. It is a real, unpriced contribution to it,
found only because the funnel was counted rather than assumed.

## What I would put in front of the Director now

The decision cadence is wrong by a factor of three or more against real boxing,
and it is the input every other number is a fraction of. That is the first thing
to fix, and it is not a balance question — it is a correctness question with an
outside reference.

The uppercut needs range to exist before it can be a punch. Either the core gets
distance and closing (which the movement model already authors and this core does
not read), or the uppercut stays authored-but-unusable and should be named as such
so nobody prices it into a matchup table.

Whether either closes Phase O's 19.1× conversion gap is untested and I am not
going to claim it. Both are defects on their own terms, measured against boxing
rather than against a target.

## Sources

Punch-rate benchmarks are from published CompuBox statistics: the 36.9% power-punch
connect average and 23 jabs thrown per round from Bad Left Hook's CompuBox
breakdown; the 55–78 per-round throw band, 30–60 heavyweight range, and the
Joshua–Ngannou 37.7 thrown / 11.7 landed figures from Infinitude Fight's
statistical review; Roman Gonzalez's 30.1 landed per round from CompuBox's own
career rankings.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 05:10 UTC | END ] -->
