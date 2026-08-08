<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 18:40 UTC | START ] -->
# Three-lens panel review — the game, and the process that is producing it

**Date:** 2026-08-08 · **Requested by:** the Director · **Head at time of review:**
`a7a38db` on `feat/integrated-bout-tick`, `b1ca3ab` on `main`

## What this document is, and what it is not

**This is a harness. It may not conclude anything.**

The panel below is three subagents, written and briefed by one model, arguing in
two rounds. They are not user research. They did not play the game, because
there is nothing to play; they read a specification. Their cultural and
professional backgrounds are constructed, and constructed viewpoints reproduce
the assumptions of whoever constructed them — which in this case is the same
agent that wrote much of the code under review. That is a conflict of interest
and it is stated here rather than buried.

What a device like this is genuinely good for: **generating the questions a real
test should ask, before the real test is expensive.** Section 8 is the part of
this document with a claim on the project's time. Everything above it is
material.

Nothing here is evidence. No pin, no hash, no canon value.

## 1. The panel

| | Who | Lens |
|---|---|---|
| **AN** | Adaeze Nwankwo, 41, Lagos — executive producer at a mobile-first studio; ran a regional fighting-game circuit for six years | Reach and shipping. Device economics, data cost, interrupted power, shoulder-to-shoulder play, comedy as mass-reach |
| **KM** | Kenji Muraoka, 58, Osaka — 22 years designing arcade cabinets and running location tests; accessibility consultant since a hand injury took most of his left grip | The hand, the eye, and the first ninety seconds. Location-test discipline; a super-aged player base; execution depth |
| **RS** | Rocío Salazar-Ibáñez, 47, Mexico City — 15 years a boxing broadcast producer, ringside; long-form columnist | Spectacle, respect, and the audience in the room. Multigenerational family viewing; showmanship that never mocks the athlete |

Round one: independent evaluation on effectiveness, ease of use, comprehension
and direction, over two passes — the game as specified, and the process. Round
two: each read the other two and answered a rotating prompt aimed at their own
most exposed position.

## 2. Effectiveness

All three rate the mechanical specification highly and the project's output
poorly, and they arrive there by different routes.

RS: *"the best-argued boxing model I have read from a game team."* She singles
out Wind over Reserve — the reason a body attack in round three pays in round
nine — and the anti-running rule, which she recognises as *cortar el ring*
written as physics. AN singles out the guard-as-structure model as "correct
boxing, and more importantly correct game design, because it turns defence into
a choice with a shape instead of a slider." KM protects punch commitment above
everything: *"Every playtest will produce someone asking to cancel a whiff.
Refuse them. That rule is the game."*

Against output, all three converge on the same number and none of them was
prompted to. RS: *"a facility with every camera calibrated, every audio path
verified, redundant everything, and no show has ever gone to air."* KM: *"a
cabinet with a beautifully documented coin mechanism and no screen."* AN: *"one
week in, the artefact is a physiologically defensible fatigue model with no
bell, no face, no joke and no button."*

Two of them make the same technical argument about the recurring units defect.
KM: *"tests written from the same misreading agree with the misreading."* RS:
*"That class of bug is invisible to a unit test and unmissable to an eye… They
are catching with instruments what they could catch with a screen, three times
over, and calling the catch a success."*

## 3. Ease of use

This is the section where the panel is harshest, and it is unanimous: there is
no control scheme, so the second clause of the design promise — *if a player has
to read a manual to enjoy it, it doesn't ship* — has **no evidence at all**, not
weak evidence, while the first clause has 1,298 tests.

KM answers from his own hand: *"Ten guards implies either a modifier held
continuously or a stance-cycle. A held modifier plus a directional plus a punch
button is a three-point grip. I cannot make that shape."* He notes committed
animation punishes mis-inputs at maximum severity — correct for a healthy
twenty-five-year-old in Nipponbashi, and the reason a sixty-eight-year-old
regular does not insert a second coin.

AN puts the over-55 case concretely: her uncle knows more boxing than the panel
and has presbyopia and stiff fingers. *"He will not fail because he lacks boxing
knowledge; he will fail because the knowledge cannot get from his eye to his
thumb fast enough."*

RS points at who actually buys boxing: *"three generations on one sofa. The
person most likely to buy a boxing game is very often the person least able to
hold a quarter-circle input for thirty-six minutes."*

Their specific asks, merged: guard as a **latched** state rather than held;
input buffering; commit windows adjustable as a first-class setting rather than
a difficulty tier, and **asymmetric** — recovery may be shortened for the
player, startup and telegraph never may, because shortening startup deletes the
read; guard readable by silhouette, never by colour; difficulty expressed as
counter-window width, which the no-adaptive-difficulty rule already makes the
only honest lever; and RS's catch, which nobody else saw — a guard's declared
**visibility cost must never be expressed as a smaller or dimmer picture**, or
the mechanic penalises low-vision players twice.

Every one of these is a schema decision. All of them are cheap this month and
expensive after the input layer exists.

## 4. Comprehension

KM's standard is ninety seconds and three plays. He cannot apply it — the
operating surface does not exist — but he can weigh the load: *"Five range
bands, ten guards, two stamina pools, counter windows, seven referees with
different thresholds, sealed scorecards. Every one of those is defensible in
isolation and correct as simulation. Together they are a manual."*

All three independently reach the same resolution: **the manual has to be the
animation.** RS: *"Reserve depletion must show on the body — hands drop, feet go
flat, the mouth opens — before it shows on any bar."* AN: a fighter who gasps,
drops his hands and gets walked onto the ropes teaches `RECOVERY_DENIED` in one
second with no text. KM: *"boxing is legible from the body… That is the asset.
It only works if the animation and silhouette carry it, which is exactly the
unjudged gate."*

On the process, comprehension is rated high with one specific failure. KM would
onboard faster here than on most projects he consults for — contract-first,
reason codes, 26 numbered decisions, drift logged rather than hidden — *"But I
would also, within a week, notice that six frozen components each read the
movement data their own way, and I would not know which reading was canon."* AN
names the same thing as the cause of the three-times units defect and proposes
the cure: not another guard after each catch, but **one typed representation of
rates and distances that makes the wrong reading impossible to express.**

## 5. Direction, and how far it has strayed

The charter says arcade boxing with real bones, comedy-first. The panel's
finding is that the project has drifted into being **a boxing simulation kernel
of high quality with an arcade game hypothesised on top of it**, and that the
drift is measurable rather than a matter of taste:

- one week in, eleven phase legs proven and zero fights;
- balance values unfitted and tuning forbidden until cadence looks plausible —
  but cadence cannot look like anything until a fight runs;
- comedy-first with no joke, no art direction, no character direction, no
  commentary line, no roster, no faces, no voices;
- no control scheme, no tutorial, no accessibility, no platform decision, no
  business model, no localisation plan.

RS puts the show-business version: *"They have built the referee's rulebook and
forgotten to book the show."* KM puts the design version: *"The players I have
watched do not buy correctness. They buy the moment the tall man's chin comes
up. The project has spent its first week proving that the tall man's chin can be
modelled."*

On comedy-first specifically, RS refused diplomacy: *"it does not exist. Not one
specified system is funny. Comedy-first is a label on an empty room, and the
room has 1,298 tests next door."* Under cross-examination AN — the panellist
most invested in humour, who had argued the reason codes were a comedy engine
built by accident — conceded the point: *"Material is not a joke. I withdraw the
implication that the funny part is handled. It is not scoped, not budgeted, and
not staffed."*

## 6. Points of agreement

1. **Stop and run one complete fight before anything else.** All three reached
   this independently, in round one, unprompted, and all three restated it after
   reading each other. It is the panel's only unanimous action item.
2. **The reason-code stream, plus the rule that the CPU sees only what a fighter
   could see, is this project's unique asset.** AN: *"That single constraint is
   the competitive truth, the comedy, the tutorial and the spectator layer at
   once. Nothing else in this project pays four times."* RS wants it as the
   broadcast layer, paired with sealed scorecards. Protect it.
3. **Wind over Reserve is the best idea in the design** and must not be traded
   away for shorter sessions.
4. **Punch commitment with declared telegraphs and locked frame data is the
   game.** Two of three named it unprompted; the third did not dispute it.
5. **Ten guards is wrong, and it is a readability defect, not a technical gap.**
6. **The comedy is a label today**, and will be bolted on late and cheap if it
   is not scoped now. Conceded by the panellist who argued against this.
7. **Accessibility must be decided this month**, while there is no input layer to
   retrofit.
8. **A charter rule against caricature belongs in the charter now.** RS and AN
   independently named the same risk for their own regions' fighters. AN added a
   rule neither of the others had: *"the loser is usually sitting beside you on
   the same couch. If the joke only works because someone is humiliated, it will
   not survive shoulder-to-shoulder play."*
9. **The recurring units defect is a systemic signal, not bad luck**, and the fix
   is a single typed representation, not another guard.
10. **The platform decision is blocking everything else** — the panel's own final
    position. Framing sets silhouette size, which sets viewing distance, which
    sets the number of guards.

## 7. Points of disagreement

**7.1 Where the game lives — the deepest split, partially resolved.** AN wants
mid-range Android primary *"not because a phone is the best place to box, but
because it is the hardest box, and the hard box is the only one you can design
outward from."* KM is thinking about a cabinet and a lever; RS about a
television. AN named the costs herself: KM loses analogue distance and a
three-point grip, forcing the guard system down to a stance plus two attack
inputs; RS loses screen, and a phone-framed camera crops the fight to two
torsos. RS, on her own territory, largely conceded: *"a boxing exchange is
watchable on a phone. Ring geography is not."* What dies in the crop is
everything the anti-running rule exists to produce, and it must then be carried
non-spatially. The panel landed on **phone frame as the constraint, television as
the full expression** — with KM's input fidelity the genuine, unrecovered loss.

**7.2 The byte-identity gate — unresolved, and the panel is least qualified
here.** KM alone would demote it: *"equivalence is not correctness"* — byte
parity would have reproduced the units defect faithfully in both languages and
reported green. His narrowed proposal: a **release gate, not a phase door**,
permitting a Python-only arena build that may be watched and may never ship,
with byte-identity re-proved once the numbers stop moving. His argument is about
tempo: if every observation must be paid in Python, then C++, then re-proved
before the next fight can be watched, the loop collapses to one observation per
cycle. The other two did not ask for this and their recommendation costs the
Director no rule at all. **Recorded as a divergence, not a recommendation** — it
proposes softening the discipline that has caught every defect this project has
found, on the say-so of a panel that has never had to live with a silent
divergence between two builds.

**7.3 Round length — raised, then withdrawn.** AN would have killed twelve
rounds of 180 seconds as the shipping unit. Under cross-examination she withdrew
it as *"a market and distribution argument I dressed as an accessibility one"*
and conceded the design point: *"a three-round game does not need Wind and
Reserve at all, and if I cut the fight to fit a bus ride I delete the smartest
idea on the page."* Settled position: three and six rounds as first-class
options, twelve as the full expression. Her surviving addition, uncontested:
**every round boundary is a save point**, because in her market a session ends
when the power does.

**7.4 The Crowd Bar — killed, with the underlying need conceded.** RS: *"eleven
declared gain sources and a novelty floor is a spreadsheet where a roar should
be, and it turns the audience into currency."* She holds the kill and grants
AN's point beneath it: the crowd reaction *is* the shareable clip. Her
replacement is not a meter — sustained roar earns **presentation**: the camera
drops, the replay fires between rounds, the crowd is on its feet at the final
bell, the corner and commentary pick up what the room already said. Plus a hard
rule: **the crowd never touches the scorecards.** KM did not defend the bar.

**7.5 What the silhouette test measures.** KM proposed five guards decided by a
forced-choice silhouette test — *"any pair confused above 20% collapses into one
guard"* — with the constraint that each surviving guard must own a *different
exposed lane*. RS accepted five as the ceiling and priced his test as narrower
than her argument in four ways: it tests a **stance at rest**, where the moment
that decides comprehension is the **interception frame**, arms in motion; at
1.2 m on flat white, where her audience is at three metres with ring lighting
and a corner post; on a clean source, where the clip that reaches people has
been through a messaging app at 480p; and it asks *which one is it* rather than
*what does it do to me*.

## 8. Recommendations

Sequenced. Items 1–3 are the panel's unanimous position; the rest follow from it.

**1. Run one complete fight, and watch it.** First bell to sealed card, ugly,
unfitted, capsules, no animation. All three panellists ended both rounds here.
RS would sit through all twelve rounds; AN would watch the plain-text version
first and only then build her thirty seconds; KM would put it in front of five
people who owe him nothing. This is also the project's own blocker — tuning is
forbidden until integrated cadence exists, and cadence cannot exist until a
fight runs. It requires contact quality, condition, knockdown, count, stoppage
and judging: substantial work, and the only work that unlocks anything else.

**2. Decide the platform, this week.** Everything downstream waits on it —
camera framing sets silhouette size, which sets viewing distance, which sets the
guard count, which sets the collision volumes. "Unreal 5.8 on Windows" is a
default, not a decision, and the panel's compromise is testable: **frame for a
phone, express on a television.**

**3. Decide the input surface and the accessibility floor before either
exists.** Latched guard rather than held; input buffering; asymmetric commit
window as a first-class setting (recovery shortenable, startup and telegraph
never); full remapping; one-handed viability; commitment attached to the
decision and never to the surface — *"once a punch is live it cannot be
cancelled, but a touch that lands slightly off must resolve to the punch the
player meant."* All cheap now.

**4. Write the two charter rules the panel asked for.** (a) The joke is never a
fighter's competence, never their origin, and never a humiliation the loser has
to sit next to. Comedy comes from physics and situation. (b) The crowd never
touches the scorecards.

**5. Replace the Crowd Bar resource with earned presentation.** Keep the
reaction, delete the currency, and let sustained roar buy camera, replay and
commentary rather than a spendable meter.

**6. Scope the comedy, or stop calling it comedy-first.** Both are honest; the
current position is not. If it stays a label for another month it will be bolted
on late, cheap, and written by whoever is free.

**7. Collapse ten guards to the number that survives the readability test**, with
the constraint that each must own a different exposed lane. Keep the other
authored postures in canon as animation flavour within a family, so no research
is burned. This also resolves the standing ten-guards-over-two-volumes drift on
readability grounds rather than engineering convenience.

**8. Replace the recurring units guards with one typed representation** of rates
and distances that makes the wrong reading impossible to express. The basis
declaration added under Decision 0026 is the right half of this; the missing
half is a type that carries its basis.

**9. Add round-boundary save points** to the twelve-round mode.

**10. Recorded but not recommended:** demoting byte-identity from a phase door to
a release gate (§7.2). It is the panel's one proposal to weaken the discipline
that has caught every defect the project has found, and it is a Director call
rather than a panel one.

## 9. The pilot test the panel designed

Kenji Muraoka's protocol, with Rocío Salazar-Ibáñez's additions. Under thirty
minutes, five participants, runnable the day a fight exists.

**Part A — the guard count.** Participants at 1.2 m from a monitor. Flat black
silhouettes of each candidate guard on white, no textures, no colour, no fighter
art. Sixty flashes, 200 ms each; participant presses which one they saw.
Measure the confusion matrix and response time. **Any pair confused above 20%
collapses into one guard.** One participant over sixty-five; one asked to remove
their glasses.

*RS's additions, which change what the test is measuring:* a second pass over the
same silhouettes asking only **"where would you hit him?"** — a posture that is
discriminable but does not communicate its exposed lane is decorative. A motion
pass at real animation speed, over a real ring background, at three metres,
**after a messaging-app compression round-trip**. And one participant on a
phone-sized viewport, which brings the platform question forward for free.

**Part B — does the simulation communicate without text.** Ten minutes. Pads
down. The ugly unfitted integrated fight, capsules, three rounds, reason-code
stream hidden from participants. At each stoppage, one question: **"what just
happened to him?"** Measure how often the answer is unprompted and in the family
of *he's tired*, *he's stuck on the ropes*, *he can't get away*. Also watch where
the eyes go at the instant of a punch — **at the arm, or at the head.** If nobody
looks at the arm, the interception-path model is invisible, and the design
promise dies on screen rather than in the code.

**Cultural pilots, per the brief.** Before any wider launch, run Part B
unchanged in at least two markets with real boxing audiences and different device
realities — the panel's own three would do. The variable worth measuring is not
preference but **whether the same fight produces the same explanation**. If a
round reads as *he's exhausted* in one room and *he's scared* in another, the
animation is ambiguous, not the audience.

## 10. What the panel could not judge, and said so

Every panellist opened by flagging it. There is no build. Nobody has seen a
round. KM: *"in twenty-two years I have never once correctly predicted, from
paper, how long a stranger would stay at a cabinet."* Everything in sections 3
and 4 about how this game *plays* is inference from a specification and should be
retired the moment a real player touches it.

The one finding that does not depend on inference is the one all three reached
anyway: **zero complete integrated fights.**
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 18:40 UTC | END ] -->
