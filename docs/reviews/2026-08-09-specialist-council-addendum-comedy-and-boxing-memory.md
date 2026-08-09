<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 01:20 UTC | council addendum 9 and 10 start ] -->
# Specialist Council addendum — Subagents 9 and 10

**Convened** 2026-08-09, independently of the technical council, because their
value is cultural instinct, humor, storytelling, audience awareness and boxing
memory rather than engineering authority.

**Subagent 9** — a Foundational Black American man in his late thirties.
Stand-up first, then writing rooms, then producing; now he owns a piece of what
he makes. Married, two kids. He did theater in college and still thinks about
blocking. He is the person in the room who says *"that's a joke, but it's not
HIS joke."*

**Subagent 10** — a Foundational Black American man in his early seventies.
Newspaper, then radio, then network ringside; married forty-one years, a
grandfather. He has sat at title fights and in folding chairs at four-fight club
shows. He has watched what the sport did to men he knew personally, and he is
neither sentimental nor cynical about it.

Both are fictional composite personas. Their demographic profile shapes
perspective and lived context; it does not determine their opinions, and the
brief that convened them forbids reducing either to "the Black guy," "the old
guy," or "the comedian guy." Their age and professions are where the useful
friction lives.

**The harness disclaimer from the main report applies in full.** These are
constructed reviewers, not user research and not evidence.

---

## What they were given, and what it cost the tooling

The elder commentator's brief carries a hard rule: *the commentator knows only
what a credible ringside observer could know.* No hidden RNG, no exact internal
condition values, no future actions, no sealed scores, no invisible CPU
reasoning. He may infer "that right hand looks slower"; he may not report "his
Reserve has dropped to 26.4%."

A rule like that is a promise until something enforces it, so
`tools/uppercut_integrated/ringside.py` was built to be the enforcement: it
projects an exported fight down to the observable and drops everything else —
notably the `D` rows, which carry each fighter's strategic aim, tactic and
reason code in articulate boxing English and are therefore the most seductive
and most dishonest material a broadcast could quote. `tests/test_ringside_fence.py`
holds the projection to that promise, including fail-closed behaviour: an event
family nobody has declared observable does not reach the broadcast by default.

**Then the elder commentator broke the tool three times, and he was right every
time.**

**One (A).** The first transcript was 186 lines of "moves his head to nothing" —
one flinch every half second. A broadcast does not narrate a thing that happens
twice a second; it names the pattern once. Fixed: the mistimed head movement is
now counted per round rather than listed. *And the count is the finding* — 129
in round one.

**Two (A).** The account narrated missed head movement and knockdowns and **not
one landed punch.** His words: *"a fight where you see men fall down but never
see anybody get hit is not a broadcast, it's a rumor."* The fence had been drawn
at the debugger rather than at a ringside seat. Fixed: landed punches are now
narrated the way a broadcast selects them — the first of the round, and anything
breaking a lull.

**And the fix produced a worse finding than the defect.** Round one now contains
exactly **two** narrated landed punches out of 118, because in 173 seconds there
is no eight-second gap between landed punches anywhere. **The broadcast has
nothing to say about round one because nothing in it is distinguishable from
anything else.** His ruling: the tool is telling the truth, and shape in boxing
is not made of landed punches but of *change* — the moment somebody stops
backing up, starts going to the body, gets caught. A gap-based detector will
always find nothing in a round that is uniformly loud. He handed the change-point
problem to the boxing-game designer rather than writing it, which is his
authority boundary working.

**Three (B).** A terminology correction only he would catch. The line read
"both men are feinting at ghosts" — and *a feint is offense*, a lie you tell to
draw a reaction. Two men slipping at punches nobody threw are doing the
opposite. *"In the gym you'd say they're jumpy, or working on air."* Fixed.

**And the clock (A).** A knockdown at 2:54 with the count running past the bell
was printing as 0:02, which reads as the start of the next round. Nobody is
saved by the bell, so the correct broadcast clock says **3:02** — "this is still
round one, and the round should have ended eight seconds ago." Fixed and tested.

---

## The measured convergence

The Director asked that these two agree substantially more than they disagree,
and asked for it measured rather than asserted. **Consensus obtained by
instruction would be worthless** — a harness whose reviewers are told to agree
produces a number about the instruction, not about the fight. So both were put
independently through a 24-proposition ballot drawn from *both* their reviews,
after a genuine exchange round in which each was shown the other's strongest
objections and invited to push back.

| | count | share |
|---|---|---|
| Both rule the same way | 20 / 24 | **83.3%** |
| Divergence in degree (one AGREE, one PARTIAL) | 4 / 24 | 16.7% |
| Direct contradiction (one AGREE, one DISAGREE) | **0 / 24** | **0%** |

**Agreement exceeds divergence by 66.7 percentage points**, clearing the
Director's 65-point threshold. Not one proposition drew a DISAGREE from either
man. That number was reached by exchange, not by decree, and it is reported as
measured.

**The four divergences, all in degree and both men calling them emphasis:**

- **Fight B as comic architecture (§4/§5).** The comedian withdrew it himself,
  on his own grounds rather than the elder's seniority: *"comedy requires
  asymmetry. Fight B is symmetric absence, which is not a comic situation but
  the lack of one."* The elder went the other way and gave him the laugh:
  he withdrew his own reach for the sport's unflattering word for two men who
  will not engage, because *"that word is for a man protecting something. Nobody
  in Fight B is protecting anything. It isn't cowardice, it's absence, and I
  mislabeled it."* They crossed the aisle in opposite directions and met.
  The elder's remaining reservation is the only one he calls real, and he
  reframes it precisely: *"I am content for Fight B's tone to exist and be
  enjoyed; I am not content for the CPU to be permitted to produce a
  thirty-six-minute non-fight because someone found it funny once — and that is
  a Director call about what the policy may do, not a disagreement between me
  and the comedian about whether it is funny."*
- **Showing the round cards after a stoppage (§11).** Both want it; the elder
  adds that it must not weaken the mid-bout seal by one inch. That is a
  condition, not an objection.
- **The most damaging line in the transcripts (§17).** The comedian says
  "unmarked" after 235 landed punches. The elder agrees it is the most damaging
  line about the *simulation*, and adds that "running on empty" over a man
  throwing 141 punches is the most damaging line about the *commentator* —
  *"and that one ends a career."* Two true things.
- **The reaction shot during a count (§4/§13).** Resolved into agreement by
  proposition 14, which both signed: neither man's version is buildable until
  the count has duration. *"We are arguing about how to spend seconds that do
  not exist yet."*

The elder's closing note is worth quoting because it is the opposite of
politeness: *"I want the Director to read it as genuine rather than polite: the
younger man was right about the camera, right about the joke needing nobody to
explain it, and right about the face being the cheapest narrator in the
building. I was right about the uppercut."*

---

## What they found

### The fight has no ordinary, and comedy needs one (C)

The comedian's own verdict on his own discipline, and the sharpest thing in
either review: *"comic timing is negative space. Setup needs a quiet before it;
recognition needs a beat after it. Round one has no before and no after."* The
flinch gag he had proposed — once per fight, held a half-beat too long — is
literally unbuildable in a round of uniform maximum density, because "once" only
reads if the surrounding 172 seconds are calm enough for it to stand out.
**The comedy layer is not merely scheduled after cadence; it is structurally
impossible until cadence exists.**

### The B-story problem (A/B)

The elder's contribution that nobody else in the council could have made. A
professional never announces that a round is dull — he says *less*, word density
drops, pauses lengthen, and the audience reads it without being told. Then he
goes to the B-story: the kid's amateur record, what the trainer said Tuesday,
who is waiting for the winner. *"That is what three minutes of a bad round is
for."* Project Uppercut has no B-story — no names, no records, no stakes, no
corner. **So a shapeless round today is dead air with nothing to put in it,
and that is a bigger hole than the detector.**

### The unmarked face, from two directions (A)

The comedian called "both men finish unmarked after 235 landed punches" the most
horrifying line in either transcript — *"a fight where nothing shows is a fight
where nothing matters, and comedy about nothing is noise."* The elder,
independently, found the mechanism: canon authors `eye_left` and `eye_right`
regions that **no move can reach**, because every move's first target region is
head, jaw or torso. **Cuts and swelling are structurally unreachable, and the
most reliable plain-language hook in the sport — "look at his left eye" — does
not exist.**

The comedian then named what that costs his own department. A changing face is
the only narrator in a fight that costs no dialogue; without it, every callback
must be carried by written lines, *which is exactly what makes sports games
sound written.* **Visible damage is a dialogue-reduction system before it is an
art asset.** And because eye damage impairs tracking, it is a *reason a fighter
starts missing* — comic irony with a mechanical spine, emergent rather than
hardcoded.

### Rendering damage, and a specific foreseeable failure (B/C)

The comedian raised it; the elder had the reference. What people who have only
watched television get wrong is that they think damage is colourful and
symmetrical, and it is neither. Fresh trauma is mostly *architecture and sheen*
— the orbital ridge losing its outline, the cheek losing its plane, tight skin
catching light. On Black skin especially, a purple bruise decal is a costume:
the tell is shape and shine, and later darker rather than redder. Damage is
one-sided, because the other man favours one hand. Nobody remembers the
Vaseline — by round six a face is lacquered, and that is half of what you are
actually seeing. The open mouth is the loudest damage signal at distance. An
eye closing is *a schedule, not a state* — it happens across rounds and changes
what he can see, which changes what he does.

**The caricature failure mode is not colour. It is feature exaggeration** —
reaching for a bigger lip or a broader nose when swelling a face. Swell the
structure that is already there. Reference: ringside stills and post-fight
press-conference photographs, where the swelling has matured and you see the
man. Not broadcast frames.

### Where the comedy actually belongs (C)

Not in dialogue. The comedian's three sources, all already in the stream:
`R_PUNISH_REPEATED_JAB` fires when the game detects predictability — *the corner
notices before the fighter does, the crowd notices before the corner does, and
then the boxing happens*, setup through consequence with no line written.
`SEEK_RECOVERY_SPACE` against `RECOVERY_DENIED` is not a joke but a
*relationship*, and relationships are where jokes come from. And a fighter who
does not need the mandatory eight taking all eight of it anyway, slowly, is
funny *and* correct boxing.

He also named the canon rule he would otherwise have had to ask for:
`appropriate_showmanship` pays 2.0, is novelty-gated, requires risk, and the
risk gate pays **zero when unopposed**. **Canon already refuses to reward
showboating that costs nothing.**

### How people talk about a hurt man (B/C)

The corner never describes the damage; he gives the instruction that follows
from it — *"keep the right hand high," not "your eye is closing."* Description
is the broadcaster's job; instruction is the corner's, and **a man still giving
instructions is a man still in the fight**, which is what keeps it off both the
clinical and the ghoulish rails. The opponent says nothing and starts throwing
to the closing side; the crowd understands before anyone names it. The crowd
goes *lower and thinner*, not louder — the ooh that drops off is more honest
than the roar.

And the bridge between the two specialists' registers, solved by economy rather
than personality: **the same corner man, same voice, same rhythm, fewer words.**
Four bars in round two, two words in round ten. The audience reads the
shortening as gravity because the voice never changed.

### Characters must not share a delivery mechanism (C)

Different lines is not different characters. Seven registers with seven
different *mechanisms*: the deadpan technician (absence), the man who narrates
his own fight in third person and is consistently wrong (self-narration), the
church man who apologises after each knockdown and means it (sincerity), the
wealthy suburban kid who is genuinely talented and insufferable (entitlement),
the veteran who is funny because he is *tired* and never because he is clumsy
(exhaustion), the academic who cites his gameplan and eats a hook mid-citation
(precision), the quiet one whose corner does all the talking (proxy).

The `full_crowd_trait` — *"a fighter-defining state rather than a strike"* — is
the cleanest character hook in canon: a man's whole personality arriving as a
mechanic, once, when the building is with him. Tie the register to the trait,
not to a barks list.

### Commentary levels, ruled on (A/C)

Level 1 — *"he's having trouble getting inside that jab"* — is **reachable
today** and simply is not being surfaced: bands, ground taken, punch identity,
target region, landed/missed and the ropes all exist. Level 2 — *"every time he
steps across that lead foot he's giving up the exit"* — is **not reachable**,
and the blocker is specific: separation is one-dimensional, so there is no lead
foot, no angle, no ring geometry. Level 3 is not reachable and should not be
attempted: feints, chaining and per-hand tracking are authored in canon and not
in the bout. *"A man who does Level 3 badly sounds like a liar; a man who does
Level 1 well sounds like he's been doing this thirty years."*

**Ship Level 1 clean and let Level 2 wait for two-dimensional position.**

### Moments that must stay serious (B)

The count, entirely — from the moment a man is down to the moment he is up or he
is not. Say the number or say nothing. Also: a genuinely hurt man, the tenth
round of a close fight, and the card reveal. The comedian's reasoning is the
load-bearing one: *"comedy needs a floor to stand on,"* and this game currently
has no serious register available at all, because `hurt` is never written.
**Silence during the count buys every laugh in the other eleven minutes.**

Both signed the same fence on the other side: no humour anywhere near a hurt
man, during a count, after a stoppage, over anybody who does not get up on his
own, or over a genuinely close card — *"laugh there and you tell the audience
the result doesn't matter, and everything you built dies with it."* And comedy
comes from behaviour and belief, never from ancestry, body, poverty, disability
or sexuality. Neither man qualified that one.

---

## Director decisions raised

**E-A. Is the comedy diegetic or presentational?** Does humour live inside the
world (fighters, corners, crowd, officials) or on top of it (announcer, UI)?
This decides what the event stream must *emit*, and the stream is being built
now. Worth deciding early because deciding it late is expensive.

**E-B. Does the game have permission to be silent?** An always-on announcer is
an architecture, not a polish pass. If silence is a legal register, say so
before the audio system assumes otherwise.

**E-C. May the presentation layer read the decision stream at all?** It must
never gain combat authority. Read-only access changes everything — and if the
answer is yes, the technical council should know that several of the best comic
and dramatic beats point at codes that never fire in practice.

**E-D. Are the round cards shown after a stoppage?** Both specialists want it;
the elder's condition is that it must not weaken the mid-bout seal.

**E-E. May a judge be forced off an exact tie?** Twelve consecutive 10-10 rounds
from three deliberately-different judges is not a judging outcome.

**E-F. May the CPU be permitted to reach a thirty-six-minute non-fight at all?**
The elder's reframing of the only disagreement he calls real: a question about
what the policy may do, not about whether the result is funny.

**E-G (post-First-Bell).** Is a fighter allowed to be wrong about himself in a
way the player can see and he cannot? Dramatic irony as a system, and the
comedian's candidate for where this game's comedy could be genuinely special.

---

## What neither of them was allowed to do

Neither designed a mechanic. The comedian flagged that his layer is a
*customer* of the damage fix and did not propose one. The elder caught himself
twice and handed off by name — the change-point detector to the boxing-game
designer, the knockdown-lane monopoly to the Director and the referee
specialist. Both signed proposition 24 without qualification.

The comedy serves the fight. The fight does not bend itself into a joke.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 01:20 UTC | council addendum 9 and 10 end ] -->
