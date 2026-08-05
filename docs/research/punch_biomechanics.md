<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 05:00 UTC | START ] -->

# Punch biomechanics and contact quality

**Collection state: 7 sources, 6 read, 1 discovered. Nothing is accepted into
canon.** Accepting evidence takes a Decision record, and none has been written
for this lane. Everything below is what the sources say, not what the game does.

Harvested 2026-08-05 from OpenAlex; queries in `research/queries/`, records in
`research/metadata/`, index in `research/citations/INDEX.md`.

## What the collection currently supports

**The three punch families are different actions, not one action at different
speeds.** Fifteen amateur boxers under 3D capture with force plates under both
legs differed significantly across straight, hook and uppercut on every measured
variable except elbow angular velocity. The lead hook carried the highest peak
fist velocity; the jab arrived fastest. *(Stanley, Thomson, Smith & Lamb, 2018,
International Journal of Performance Analysis in Sport.)*

That distinction is worth holding onto, because it separates two quantities this
project currently derives from one another: **how fast a hand moves** and **how
soon a punch arrives**. Our move table has startup frames and a tip-extension
ramp; this says they are describing two real and different things and should not
be tuned as if one implied the other.

**Skill shows up as where the punch comes from, not how hard the arm is thrown.**
Fifteen potential Olympic medallists against eight trained juniors, in a
17-sensor inertial suit: elites produced more force at higher velocity across
cross, hook and uppercut, and juniors leaned significantly more on the
**shoulder** for all three. *(Dinu & Louis, 2020, Frontiers in Sports and Active
Living.)*

This is the more interesting finding for us. Attributes in this project scale
output. The measured difference between levels is a **shape** difference in the
kinetic chain, and a fighter profile that wanted to model "trained" honestly
would reach for the chain rather than for a damage multiplier.

**Effective mass and impulse are the measured quantities, not peak force alone.**
A forensic study of 50 untrained volunteers on a 10 kHz force plate with 2 kHz
video reports impulse, impact duration and effective mass — the ratio of impulse
to velocity — alongside peak force. *(Adamec, Höfer, Pittner, Monticelli, Graw &
Schöpfer, 2020, International Journal of Legal Medicine.)*

Our impact model derives delivered force from what a punch cost to throw. That is
internally consistent and unvalidated. Effective mass and impulse are the
handles that would let it be checked against something measured. **Impact
duration we do not model at all**, and the animation currently implies one.

**The same named punch is a different force-time curve in a different trained
population.** Eleven boxers against sixteen Sanda athletes on a Vicon rig with
two Kistler platforms differed significantly in peak and contact velocity, peak
impulse, relative strength and rate of force development — for the lead straight
alone. *(Liu, Li, Yan, He & Zhao, 2023, Frontiers in Physiology.)*

Evidence that style is expressible without inventing per-style damage numbers.

**Punch measurement has left the laboratory.** A wearable punch-performance
system validated against force plate and motion capture at R² 0.97–0.99.
*(Menzel & Potthast, 2021, Sensors.)* Not a boxing finding — an instrument
finding, and it matters
for how future evidence in this lane can arrive.

## What the collection does NOT support, stated plainly

- **Nothing here measures a punch against a moving, defending opponent.** Every
  study is bag work, pad work or an instrumented target at maximal effort on
  command. Our whole contact pipeline is about interception, and this lane says
  nothing about it yet.
- **Nothing here is under fatigue.** Every measurement is fresh. The fatigue lane
  is a separate collection for exactly this reason.
- **Nothing here supports a knockdown model.** Force is not outcome, and the
  step from impact to consequence belongs to `knockdowns_and_stoppages`.
- **Nothing here supports our stamina-cost-to-impact derivation.** It is not
  contradicted either; it is simply unexamined.

## Open questions this lane should answer next

1. Does impact force fall with fatigue, and does it fall differently for the
   three families? (Crosses into `fatigue_and_recovery`.)
2. Is there measured evidence on **guard return time** after a punch — the
   quantity our per-hand vacated-lane model asserts?
3. What does stance change, measurably? One harvested source asks precisely this
   (orthodox versus southpaw straight punch) and has been read only as far as its
   aims. It bears directly on Decision 0013's lateral geometry, where stance in
   this project is currently a label rather than a geometry.
4. Is impact duration a quantity a fighting game should model, or one that
   animation legitimately stands in for?

## Rejected from this lane, with reasons

Four sources were harvested and set aside: a Taekwondo cohort whose punch data
cannot be read across a kicking-dominant kinetic chain; a supplementation study;
an acute warm-up potentiation study; and a football-versus-boxing head impact
comparison that belongs in `knockdowns_and_stoppages` and will be re-harvested
there. Records are in `research/rejected/`, each with its reason, so they are not
rediscovered next month.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 05:00 UTC | END ] -->
