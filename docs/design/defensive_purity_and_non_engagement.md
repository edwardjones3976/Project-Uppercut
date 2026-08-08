<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 19:35 UTC | START ] -->
# Swimming without getting wet — and the thing that is actually the abuse

**Director correction, 2026-08-08.** There is no anti-running rule in Project
Uppercut. There never was one, and the Director never asked for one.

## The correction

The phrase "the anti-running rule" was invented in this repository's comments
and spread to six files, including a public C++ header and the shared range
runtime. It is not in `PROJECT_RULES.md`. It is not in any Decision. It is not
in `data/movement_model.json`, whose own note says the opposite in plainer
words. It was mine, and it is retired.

What it displaced is a distinction the project is built on:

| | |
|---|---|
| **The abuse** | Not hitting **and** not getting hit, for long periods. Non-engagement. |
| **Not the abuse** | Hitting **without** getting hit. Defensive mastery. *"Swimming without getting wet."* |

A single phrase — "anti-running" — collapses those two into one, because it
names the *symptom they share* (a fighter moving, not being hit) instead of the
thing that separates them (whether he is landing). Once the phrase existed, the
mechanism it labelled looked like a penalty on movement. It is not. It is a
ring.

## What canon actually says, in canon's own words

Rule 4 is titled **"Fair anti-spam behavior."** It lists seven targeted abuses,
and "excessive running" appears in the same breath as "passive blocking abuse" —
both of them non-engagement, neither of them movement. Rule 4's own closing
sentence is the governing one:

> A predictable action becomes punishable because of observable pattern
> recognition, stamina, position, commitment, defense, and counterplay — not
> because the game secretly decides that repetition is prohibited.

`data/movement_model.json` says it again, twice, without ever using the word
"anti-running":

> Excessive running is answered by **geometry** rather than by a rule that
> forbids it.

> `rope_retreat_multiplier` of zero is the point: with your back on the ropes a
> backward step buys nothing. It does not forbid the input, it does not freeze
> the fighter, and **lateral movement stays fully available at full rate —
> circling off the ropes is the boxing answer and it remains open.** What ends
> is free retreat in a straight line.

And the exploit harness had the right definition all along:

> Excessive running: retreat whenever possible, **engage almost never.**

The definition was never lost. Only the name went wrong, and the name travelled.

## The mechanism is not the problem

Worth stating plainly, because the natural next move after a correction like
this is to go and change numbers, and that would be wrong here.

- `rope_retreat_multiplier: 0.0` bites **only** with your back on the ropes,
  and **only** on straight-line retreat. Lateral is untouched at `1.0`.
- `retreat_stride_multiplier: 0.78` against `advance 1.0` is why pressure can
  close and why the ring ends. It is geometry, not a fine.
- Movement is priced by **distance travelled and by nothing else** (Decision
  0014, re-affirmed by Decision 0026 Ruling C). A fighter who covers no ground
  pays nothing.

None of that charges a fighter for hitting without being hit. An out-boxer who
circles, slips and lands is treated by this model exactly like an out-boxer who
circles, slips and lands — which is to say, not charged for it at all. The model
was already right. The commentary on top of it was wrong, and commentary is what
the next engineer reads.

## The lore family that never made it into canon

`docs/development-log/2026-07-21-fun-python-coding-ideas-boxing-review.md`
records an **Expanded Boxing Lore Registry** of five families, each intended to
connect to mechanics, CPU strategy, corner advice, commentary, judging, career,
post-fight analysis and presentation:

1. **Jab control** — "establish the jab", "everything comes off the jab"
2. **Defensive purity** — *"hit and don't get hit"*, ***"swim without getting
   wet"***, "you can't hit what you can't catch"
3. **Body investment** — "kill the body and the head will fall", body-as-a-bank
4. **Initiative and exit** — "get off first", "hit and move", "be first, be
   sharp, be gone"
5. **Preparation** — "fights are won in the gym", "roadwork wins fights"

**Body investment shipped.** It is Wind over Reserve, and the body-as-a-bank
principle is implemented exactly as written: bodywork costs conditioning rather
than breath, so an investment in round three pays in round nine.

**Defensive purity did not.** There is nothing in `data/` that rewards hitting
without being hit, and no registry of any of the five families exists.

The pattern in that gap is worth naming, because it will repeat: **the family
that got built is the one expressible as arithmetic. The family that got lost is
the one that can only pay out on a scorecard.** Body investment could be a
resource; defensive purity has to be *judged*. Scoring does not exist yet, so
the ideology had nowhere to land, and instead of being scheduled it quietly
became its own opposite in six code comments.

The 2026-07-21 review's own note still stands as the right next step: the
registry needs canonical IDs and data-driven rules with explainable triggers,
not scattered sayings.

## Where the discriminator actually belongs

The abuse is non-engagement. The discriminator between it and defensive mastery
is **output over time**, and nothing in the model measures that today.

The wrong place to put it is the locomotion table or the stamina economy. A
movement or stamina term keyed on "not landing" or "not being hit" would charge
a fighter for defensive success, and would hit the out-boxer hardest — the
exact fighter this correction exists to protect.

The right place is the one boxing already uses: **the scorecard.** Clean
punching, effective aggression, ring generalship, defence. A fighter who hits
without being hit *wins rounds*. A fighter who neither hits nor is hit wins
nothing, loses the round to whoever did more, and — with one of the seven
referees — gets warned for it. That is Rule 4's "punishable because of
observable pattern recognition, stamina, position, commitment, defense, and
counterplay," and it needs no new mechanism, only the judging that is already
sequenced.

Second place, if the Director wants a live consequence rather than a
retrospective one: the crowd and the referee, both of which are observable, both
of which already exist as models, and neither of which may touch the cards.

## What changed in the repository

1. The phrase "anti-running rule" is gone from every live code path, comment,
   docstring and test:
   `sandbox/Source/UppercutCore/Public/UppercutRangeCore.h`,
   `tools/uppercut_range/core.py`,
   `tools/uppercut_integrated/bout.py`,
   `tools/engine/analyze_core_round.py`,
   `tests/test_core_range.py`,
   `tests/test_movement_cost_is_displacement.py`.
   Comments only — no stream moved, and the golden streams for O, Q and R still
   match.

2. **Development-log entries are left exactly as written.** Two of them use the
   retired phrase. They are records of what was believed on the day and they are
   not rewritten; this document is the correction beside them. The same applies
   to the 2026-08-08 panel review, where a panellist used the phrase because the
   brief handed it to her — a good illustration of how far a wrong name travels
   once it is in the source material.

3. A new validator, `tools/uppercut_validate/movement.py::check_defensive_purity_is_not_penalised`,
   runs in `cli all` and fails if:
   - `rope_lateral_multiplier` is ever anything but `1.0` — circling off the
     ropes must stay free;
   - retreat or lateral stride ever reaches zero — a fighter must be able to box
     on the back foot;
   - the locomotion table or ring track ever grows a **field** named for output,
     engagement, inactivity, passivity, damage taken, or avoidance.

   Its first version failed on arrival, and correctly: it read the whole block
   as text and tripped on the word "engagement" inside a `$comment` explaining
   that the reference model resolves engagement along one axis. Prose, not a
   term. It now reads key names only. A test written too broadly tempts you to
   widen its exemption; the right move is to narrow the claim.

## Two things for the Director

**1. A canon invariant, proposed and not taken.** The natural home for this rule
is an invariant in `data/movement_model.json` pointing at the new validator:

> `defensive_purity_is_never_penalised` — Nothing in this model charges a
> fighter for hitting without being hit. Movement is priced by distance
> travelled and by nothing else; the ring bounds retreat in a straight line and
> never scales lateral movement. Rule 4's "excessive running" means neither
> hitting nor being hit for long periods, and it is answered by the scorecard
> and by the ring, never by taxing movement or defensive success.

It was written, and then reverted, because it is a canon edit and canon is a
Director call. Its cost is not zero: `data/movement_model.json` is hashed by the
phase contracts, so adding the invariant moves phases **O** and **Q** and
requires both to be re-run and re-pinned in the same commit. That is the
documented procedure and it is about twenty minutes of Unreal time. Say the word
and it happens; the validator runs either way.

**2. The lore registry.** "Swim without getting wet" belongs in the charter's
ideology list, and the other four families with it. That is a charter edit and
also yours. The registry itself — canonical IDs, explainable triggers,
data-driven rather than scattered sayings — is the shape the 2026-07-21 review
already asked for, and it is the thing that would have prevented this.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 19:35 UTC | END ] -->
