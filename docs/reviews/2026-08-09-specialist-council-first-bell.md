<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:19 UTC | specialist council report start ] -->
# The Specialist Council — First Bell pressure test

**Convened** 2026-08-09 on the Director's brief. Eight composite specialist
personas: elite boxing conditioning; hero-combat systems; veteran boxing-game
combat; modern game feel; boxing biomechanics; professional referee and judge;
modernised arcade art direction; Unreal/technical combat architecture. Each
studied the repository, canon, accepted decisions and the two measured fights
before proposing anything. A cross-examination round followed, in the pairings
the Director named.

## The harness disclaimer, which is not a formality

**These specialists are constructed reviewers, not user research and not
evidence.** None of them has ever thrown a punch, refereed a fight, shipped a
boxing game or watched Project Uppercut play. They are a way of aiming
attention, and their output has exactly the authority of a well-argued
paragraph and no more. They do not get the steering wheel.

What follows was therefore filtered. **Every load-bearing claim in this report
was mechanically re-verified against the code before it was written down.** The
verification is reproducible: `_verify_council.py`-style checks against
`policy.BY_BAND`, `RANGE.range_pack()`, `C.PUNCHES`, `RES.condition_pack()`,
`C.CANON`, `FighterState`, `JudgingPanel` and twenty full fights. Claims that
survived are marked **A** and carry their observed value. **One specialist
claim was falsified by that pass and is recorded as dead in §4** — which is the
point of running the pass at all.

Findings are labelled: **A** repository fact · **B** strong domain principle ·
**C** expert recommendation · **D** hypothesis with a falsifying test · **E**
Director decision required. Nothing below A is canon. Decision 0032 §3 remains
in force: every number from these runs is a diagnostic until the Director
disposes of it, and nothing in this report proposes fitting a value.

---

## 1. Critical findings

### 1.1 There are two authorities on which punches are legal from which range, and they disagree (A)

This is the finding. Five of eight specialists reached it independently from
different directions — the mechanics critic by reading the decision grammar,
the game-feel designer by tracing why 3,174 punches produced no contact, the
architect by looking for duplicated authority on principle, the hero designer
by trying to price a crowd meter, the referee by asking why a scoring vector
was all zeros.

`policy.BY_BAND` is a hand-authored Python table of which punches a fighter may
choose from which band. `data/moves/generic_sandbox_moves.json` authors each
move's `range_band`, and `uppercut_range.core.in_band()` gates on exact
equality. **Verified: seven mismatches.**

| Band | Punches offered | Punches actually legal |
|---|---|---|
| outside | 2 | **0** |
| clinch | 3 | **0** |
| mid | 4 | 3 |
| inside | 6 | 5 |

From two of the four fighting bands, **every punch a fighter can choose is
refused by the range gate.** That is the mechanical cause of the twelve-round
stalemate: two fighters preferring `outside` stepped into a band where offence
does not exist, threw 3,174 punches that were legal to the policy and illegal
to the resolver, and drew 120-120. It is also half the cause of the slugfest:
the `inside` band is the only one where nearly everything lands.

The mechanics critic put the design consequence better than a defect report
would: *"the outside band is not hitting without getting hit — it is a band in
which offence does not exist for either man. Swimming without getting wet
requires water."* The owner's protected art is not currently possible, and
Decision 0030 is not what stands in its way.

**This is the same class of defect the project has already deleted twice** —
the eight copies of the LCG constants, and the phase formulas the integrated
contract was forbidden to copy. Canon has already named the single authority:
`data/punch_model.json` `range_gate` declares `band_source:
"data/movement_model.json"`. `BY_BAND` is an unauthored second opinion about a
rule canon says has one source.

The architect's fix, and he defends both halves as inseparable **(C)**: canon's
`range_band` becomes a *set* per move — because a jab is legal at mid and
outside, and a hook at inside and mid, and one-band-per-punch is bad boxing
before it is bad engineering — **and** `policy.legal_attacks()` stops owning a
table and calls the range pack. Set-ify without deleting `BY_BAND` and the
second table survives to be ported to C++; derive without set-ifying and the
human input layer writes its own legality predicate to give input feedback,
which is where the second table gets rewritten in another language. **(E)**
Whether `range_band` becomes a set is the Director's, because it is a canon
shape.

### 1.2 Three punches the fighter throws never enter the world (A)

**Verified:** the policy can select eight punches; `contract.PUNCHES` declares
five; `body_hook_lead`, `hook_rear` and `uppercut_lead` are charged their
stamina, increment `punches_thrown`, receive a hardcoded 14-tick commitment —
and are never assigned to `me.punch`, so they never fly, never resolve, never
whiff and never void. In a codebase that fails closed everywhere else, an
unknown move gets an invented window instead of an exception. At `inside`,
half the offered offence is either a ghost or band-illegal.

### 1.3 One punch in the game can knock anyone down (A)

**Verified:** `jaw_chin` is the only region canon marks `knockdown_relevant`,
and of the five punches in the bout only `uppercut_rear` targets it. Every jab,
cross, hook and body shot contributes exactly zero accumulated knockdown
pressure. Every one of the ~150 knockdowns across thirty fights came from one
move id.

Worse, the region is read as `target_regions[0]` — **the first element of a
JSON array**. Reordering `hook_lead`'s `["head", "jaw_chin"]` would change which
punches can end a fight. Authority is sitting in array order, which Decision
0026 spent a whole ruling removing from RNG ownership.

The biomechanist's objection is independent and harder: **(B)** concussive
knockdown is a rotational-acceleration event, and the hook and overhand are the
archetypal rotational-acceleration punches. Making the mandible the sole
knockdown lane while the hook lands on an inert region is a taxonomy problem,
not a tuning problem. **(E)** Whether `torso_lower` (the body knockdown — a
top-three knockdown type in the professional sport, and the payoff the drainer
archetype's win condition names) and `head` become knockdown-relevant is a
Director call on canon.

### 1.4 Every fight so far has ended on a rule the declared ruleset switches off (A)

**Verified:** `data/rulesets/professional.json` authors `three_knockdown_rule:
false`, `knockdowns_per_round_stoppage: null`, `knockdowns_per_bout_stoppage:
null`. **No ruleset file appears in the integrated contract's `CANON` tuple.**
The bout instead reads `max_per_round: 3` / `max_per_bout: 4` from
`condition_model.json`. Thirty of thirty fights ended on `knockdown_limit`.

So 100% of observed endings used a stoppage mechanism the ruleset they were
nominally fought under explicitly disables; `arcade_three_knockdown.json` can
never take effect; Decision 0019 (versioned rulesets) is currently decorative;
and `condition_model.knockdown.decision_path_must_survive: true` is violated
thirty times out of thirty.

The referee adds two rulings **(B)**: the three-knockdown rule is real but is a
commission and sanctioning-body *option*, usually waived in championship bouts,
and where it applies the fight ends **on** the third knockdown of the round —
this code tests after incrementing, so it stops on the fourth of a round and
the fifth of a bout. A four-knockdown round is a thing a referee does not
permit. And **there is no per-bout knockdown limit anywhere in professional
boxing.**

He also finds the KO — boxing's defining outcome — currently near-unreachable:
a fighter is only counted out if a knockdown-relevant region is at *full*
damage or Wind is exactly zero, and `count_expired` fired zero times in thirty
fights. **An arcade rule is doing a real rule's job.**

### 1.5 Two of three judges score walking forward roughly ninety times harder than punching (A)

**Verified in a real fight.** `evidence["pressed"]` accumulates q10000 reach
units; `landed` is a punch count; `judging.score_round` sums them with weights
as if they were commensurate. Measured peak in one round of seed 4245:
`landed` 116, `pressed` 4,200. At the stop: red 35 landed / 2,800 pressed, blue
31 landed / 7,000 pressed.

One landed punch is worth **1** to every judge. One capped advancing tick is
worth **140** to Bello and **560** to Reyes. In that measured round, Reyes
scored blue's footwork 2,800 against red's punching 31 — about **90:1**.

The docstring advertises 10000 for clean punching. The arithmetic delivers the
opposite. The panel is not three readings of one fight; it is two footwork
judges and one punching judge, with one degree of freedom.

The referee's separate ruling is that even a *correct* implementation of
`pressed` would be wrong **(B)**: effective aggression's defining word is
*effective*, and every judging seminar in the sport teaches that a fighter who
walks forward and misses is scored **against**. `pressed` is a proxy for
walking forward, which is the one thing judges are trained not to reward.

### 1.6 The scorecards can be illegal under the ten-point must (A)

**Verified by direct construction.** A fighter who wins a round on evidence 20
landed to 1, having been dropped twice, scores **8** — against the loser's
**9**. `pa = max(7, pa - knockdowns[a])` is applied to both fighters, including
the round winner.

The "must" in ten-point-must is precisely the rule that the round winner must
receive ten. A 9-8-to-the-loser round is not a legal card. This has never
fired only because no fight has yet reached the cards with a knockdown in it —
and First Bell's other half is a valid decision. The `max(7, …)` floor is
invented; no canon file authors it.

### 1.7 The fight has no negative feedback loop, and its only brake is dead code (A)

**Verified:** `consecutive_failed_attacks >= 2` — the sole mechanism by which
any fighter reconsiders anything — peaks at **1** over 12,000 ticks and can
never reach 2, because `committed_to()` zeroes the counter on every throw and a
fighter can hold only one punch. `R_AVOID_OVERCOMMIT` has never fired.

Alongside it, also verified: `FighterState.hurt` and `damaged_regions` are
initialised and **never written in a complete fight**, so the policy branch
that reads them is dead and a fighter cannot know he is hurt; `step_lateral`
has a step delta of **0**, so the pivot moves nobody; and `retreat_mult` is
**0**, so a fighter on the ropes has no action that changes his position —
the mechanics critic's "the ropes are an absorbing state" is confirmed by
construction rather than by observation.

### 1.8 Canon that is hashed, declared, and never read (A)

The integrated contract hashes `data/cpu_decision_model.json`, which authors
`reaction.decision_interval_ticks: 4` and `floor_ticks: 6` with the note *"a
CPU may be fast; it may not be instant."* The bout calls `P.decide()` every
tick for both fighters with zero latency. `punch_model.outcome_recovery`
authors per-outcome recovery multipliers and counter windows (whiffed ×1.5 /
10 ticks) — unread, so a whiff costs the same recovery as a landed punch and
the counterpuncher's authored win condition does not exist.
`condition_model.impairment` authors `stamina_regen_multiplier_at_full_torso:
0.35` — unread, so body investment accumulates and changes nothing.
`rise_window_ticks` — unread, so everyone rises at exactly eight, always.
`input_buffer_ticks: 2` — unread.

The architect's ruling is the useful one **(C)**: *implementing the authored
reaction interval is not tuning — it is reading canon the header already
claims.* The same is true of `outcome_recovery` and the torso impairment. None
of these needs a Director disposition under 0032 §3, because none of them
proposes a number: they propose reading numbers canon already fixed.

---

## 2. First Bell blockers

First Bell is *one complete authoritative generic fight capable of ending by
valid decision or valid stoppage.* Both endings now execute. The council was
told to be strict, and the strict test is: **does this prevent the fight from
being authoritative, or from being a fight?** Six survive.

**B1. The band-gate duplicate authority, including the five-versus-eight punch
vocabulary (§1.1, §1.2).** A fight in which two of four bands cannot produce a
punch, and three selectable punches never enter the world, is not authoritative
— and it is the direct cause of one of the two failure modes. *If only one
thing is done before the next fight is run, the whole council says this.*

**B2. The ruleset authority conflict (§1.4).** Until it is resolved, the game's
rules are whatever `condition_model.json` says, canon's rules files are inert,
and every ending on record contradicts the declared ruleset.

**B3. The illegal ten-point-must construction (§1.6).** First Bell's deliverable
includes a valid decision; a card containing a 9-8-to-the-loser round is not a
valid decision.

**B4. The judging unit mismatch (§1.5).** A decision ending exists. A decision
*worth reaching* does not, and cannot while footwork outscores punching 90:1.

**B5. The single-move knockdown funnel (§1.3).** Not because the number is
wrong — that is 0032 §3 territory — but because knockdown authority currently
rests on `target_regions[0]`, an array index, which the project has ruled is
not authority.

**B6. The unread `reaction` block (§1.8).** Zero-latency, every-tick decisions
by both fighters are implicated in both failure modes, and canon already
authors the fix.

**Explicitly NOT blockers**, and the council was unanimous: guards and postures,
clinches, fouls and point deductions, feints, abilities, the Crowd Bar,
combinations, per-hand tracking, graded contact quality, hitstop, the human
input layer, any art or renderer work, and the 10-guards-vs-2-volumes drift.
All post-First-Bell. Several are large; none of them stops a fight happening.

---

## 3. Post-First-Bell improvements

Ranked by the council's own priority and explicitly forbidden from delaying the
milestone.

**The guard does not exist in the fight (A).** `GUARD` sets `move_id = None`,
so a guard costs nothing, and there is no guard stage in `_resolve_punches`.
The ten postures, `posture_economy`, `guard_integrity`, and the
`guard_extent_multiplier_while_committed: 0.6` are all authored and inert. The
project's stated core rule — *a guard is a body structure that protects some
lanes while exposing others* — is currently not a mechanic. It is the largest
single piece of authored design not yet in the fight, and the pinned
10-guards-vs-2-volumes drift sits directly on top of it.

**Reach-at-contact instead of throw-time band legality (C).** `me.punch =
(move, t, me.band)` freezes legality at throw time, so stepping back after a
punch is thrown cannot make it miss and stepping in behind a jab cannot make it
land. Distance is not yet a live defence.

**No combination is expressible (A).** Policy returns `OBSERVE` for every tick
of recovery, nothing may cancel, so the minimum gap between two punches is the
full authored recovery of the first. **A one-two cannot currently be thrown.**

**The clinch (B).** Canon has the band, the moves file has `clinch_entry`,
`referee_semantics.json` has a clinch block, and the policy's own comment admits
tying up is the missing answer. A boxing game where a hurt fighter cannot hold
is visibly not boxing.

**Body work reaching conditioning (C).** The cheapest high-value change on the
biomechanist's list, and canon already authored the mechanism: body damage
attenuates Wind *recovery*, not capacity — *"a fighter who has been dug to can
still throw the next punch; what he cannot do is get his breath back between
exchanges."* One multiplication in `recovery_rate()` and one in
`between_rounds()`.

**Officiating between "nothing" and "stopped" (B).** Warnings, cautions, point
deductions, low blows, holding, head clashes, cuts, the doctor, the corner's
authority and the towel. `cpu_decision_model.observable_inputs` already declares
`referee_warning`, `referee_deduction`, `referee_instruction`, `doctor_check`,
`clinch_start` and `break_start` — and implements none. The round break is also
one tick long, so between-rounds officiating has nowhere to live. The
technical decision is unreachable because `_stop` closes the panel without
scoring the partial round.

**Feints (C).** `slip_lead.beaten_by` names `feint_then_commit`, and the policy
explicitly declines to implement feints. Decision 0032 made evasion a
prediction mechanic with a real penalty for guessing wrong, while the mechanic
that makes prediction *fair* does not exist. Two specialists flagged that
coupling independently.

**Hitstop, ruled on and deferred (C/E).** The game-feel designer made the case
for authoritative, tick-counted hitstop — inserted non-decision ticks, no RNG
consumed, one `H|` row in the stream, ~3% of a twelve-round fight spent on the
fight's best moments. The architect ruled **no, not for First Bell**: the
fairness problem it solves is caused by a renderer holding a clock the
simulation does not have, which is presentation acquiring authority and is
rejected on its own; canon's unread `input_buffer_ticks` already owns the input
answer; and the human input layer is deferred by Decision 0027, so the problem
does not yet exist. If it is still wanted when that layer is built, the
determinism-safe shape is specified: a single global freeze counter owned by
`step()`, never inside the frozen cores.

**The `Z` snapshot row (C).** `between_rounds()` and `count_relief()` mutate
per-region damage and emit nothing, so any renderer, scrubber or resimulator
must re-implement canon's recovery fractions — a fork. The art director asked
for a row; the architect ruled it is the *same* row as his keyframe and
specified it once: all participants, all declared regions in `contract.REGIONS`
order, emitted after the mutation from one method, at bout start, after the
corner, and after a rise. **Cheap now — the integrated trailer hash is not yet
pinned. A re-prove later.**

---

## 4. Contradictions, and one death

Disagreement was preserved rather than averaged, per the working rule.

**Fatigue and force — resolved, productively.** The conditioning specialist
asked the Director whether fatigue should reduce output, not merely resistance.
The biomechanist refused the framing: force loss under fatigue is not uniform —
what degrades first is repeatability, leg contribution and shot selection,
while *"a tired fighter throws fewer good punches, not uniformly weaker ones"*
— and proposed attenuating only the leg-driven component, weighted by each
move's already-authored `reserve_load`. The corner professional accepted the
correction and then improved on it from experience: `reserve_load` ranks by how
much leg drive a punch *demands*, but what dies late is ranked by **transit
distance and weight transfer**. The short hook off a slip survives exhaustion
and would be faded wrongly; the long straight right is ranked durable and is
exactly the punch that becomes an arm punch in round ten; the body attack dies
*last*, because a tired man can still bend and dig — what he loses is the
ability to get out afterwards. His compression is the best sentence in the
council's output: **fatigue does not weaken punches, it shrinks the range at
which a punch is still a punch.** And the piece neither had said aloud: *"it is
not the punches, it is the guard between them. The elbows come off the ribs
first. The chin comes up second. Punches third. A model where fatigue reaches
offense before it reaches structure has the sequence backwards."*

He withdrew his own E1 as badly shaped and refiled it: **(E1′) does fatigue
reach offense through shot selection and effective range, or through delivered
force?** He then refused to withdraw the underlying asymmetry, and it survives
verification: `knockdown_pressure` reads the defender's Wind and never the
attacker's, so **fatigue makes a fighter twice as easy to drop and not one
percent less able to drop you** — positive feedback with no damper, and the
best available explanation for thirty consecutive knockdown-limit endings.

**Where the biomechanist defended the design against himself.** He was convened
to challenge experiential claims and reported that the lab agrees with the
corner: Wind-over-Reserve is a coarse critical-power model, `in_round_recovery
_per_tick: 0.0` is defensible for glycogen and peripheral fatigue, and *"the
game's error, if any, is in the opposite direction from the one I was set up to
attack."* He was equally clear about the limits of his own field — the body-shot
literature is thin, the liver-shot mechanism is *"plausible and essentially
unevidenced — it is boxing wisdom"*, and the classic leg-drive study is *"old,
small, and badly over-cited."* He also identified which of two structures to
cut if one must go: keep the Reserve→recovery multiplier (measurable), cut the
Wind ceiling (a readable proxy with no physiological correlate).

**Abilities: a headline withdrawn.** The hero-systems designer had computed that
the twelve-round stalemate might earn *eight full crowd bars per round by
punching air*. Confronted with the ghost-punch and band-gate findings, he
withdrew it: those 3,174 whiffs are an artefact of the defect and cease to
exist once the tables unify — *"my permissive-reading disaster was a bug's
shadow, and I should not have hung a headline on it."* He held the other half:
saturation is real and gets *worse* after the fix, because unification raises
contact per attack. And he sharpened something better — unification is what
turns eleven weighted gain sources into a *table* rather than a multiplier,
because combinations, counters and body work currently cannot express
themselves at all.

**Anti-stalling: the officials win.** Asked whether a meter beats a referee at
punishing non-engagement, the hero designer conceded without hedging: *"a
systemic answer cannot tell the staller from the man out-boxing at range — a
referee can, because a referee applies a bona-fide-effort standard."* Officials
own stalling; the crowd owns spectacle. He then filed **(E)** whether the Crowd
Bar's idle-decay term should exist at all once the foul chain is live, since
expiry already solves banking and decay is the term most likely to collide with
defensive purity.

**Retiming: withdrawn under two constraints.** The game-feel designer proposed
doubling power-punch startups so slips become reactable. He withdrew it to a
conditional post-First-Bell hypothesis after the art director's ruling that
exaggeration must live in amplitude and secondary motion — never retiming,
because the three-point stylization experiment requires byte-identical fights —
and the architect's finding that punch timing, evasion startup and evasion
active window come from **three different authoring surfaces with fields not
even spelled the same.** *"You do not retime across three unreconciled
surfaces."* He re-ranked `outcome_recovery` first and his own proposal third.

**And the death.** The architect hypothesised that a stoppage could be
overwritten by a second `F` row, because `_resolve_punches` does not break when
`self.result` is set. **Verified across twenty full fights: every fight emits
exactly one `F` row. REFUTED.** The claim was plausible, well-reasoned, and
wrong. It is recorded here because a review that reports only its confirmed
findings is not a review.

---

## 5. Exploit map

Strategies likely to become disproportionately dominant, all verified unless
marked.

**The ropes are terminal (A).** `retreat_mult` is 0 and `step_lateral`'s delta
is 0, and the policy's rope-escape branch returns the pivot. A fighter whose
back touches the ropes has no action available that changes his position, ever
again. Rope trapping is not dominant; it is absorbing.

**One punch, one band, one fight (A).** `uppercut_rear` from `inside` against a
defender with any recovery ticks clears the pressure threshold essentially on
contact. Every fight measured resolves to that loop.

**Free defence (A).** Guarding costs nothing and intercepts nothing. Pivoting
costs nothing and pays stamina recovery, making `MICRO_ADJUST` strictly
dominant over `HOLD_POSITION`. A mistimed evasion buys six extra recovering
ticks. Recovery-frame farming: throw a long-tailed punch from a band where it
is illegal, pay one charge, collect twenty-plus recovering ticks.

**Going down is efficient (A/B).** Count relief returns 45% of region damage and
25% of the wind deficit in eight seconds; the validator's own units guard caps
in-round recovery far below that. Taking a knee is currently the most efficient
recovery in the game. Directionally true to boxing; the ratio is unearned.

**Turn order (D).** The per-participant loop gives the second fighter a
one-tick information advantage every tick, and `contract.py`'s claim that
participant order "decides who acts first within a tick and nothing else" is
false as written. Falsifying test: swap `DEFAULT_PARTICIPANTS` and re-run the
mirrored profiles; if the winner follows array index rather than corner
identity, tick order is authoritative. The architect's fix is a pre-tick
snapshot for all participants — which is also the shape resimulation needs.

**`variety` is the one ungated crowd source (A).** The only gain source with
both `novelty_gated: false` and `requires_risk: false`. Post-fix the farm is
not air-punching but the knockdown window, where `variety` keeps paying while
the risk gate zeroes everything else.

---

## 6. Missing boxing behaviour

Things real boxing permits that Project Uppercut cannot yet express, drawn from
the eleven situations the conditioning brief named and the referee's rule set.

A fighter catching his breath while remaining dangerous — unreachable as a
distinguishable state, because output never degrades, so "still dangerous"
carries no information. Legs going while the lungs return — correct structure,
zero expression: `exhausted_stride_multiplier` is authored and unread, so the
one place an audience would *see* it is inert. A pressure fighter exhausting
himself through failed pursuit — failed pursuit costs exactly what successful
pursuit costs, and futility leaves no residue. Conserving without abstaining —
every conserving verb is non-engagement; there is no branch that uses the jab
the way canon's own note describes it, *"how a boxer occupies an opponent while
breathing."* A hurt fighter becoming temporarily inefficient — dead code. Body
investment paying off later — accumulates, changes nothing. A one-two. Holding.
A body knockdown. A flash knockdown, or a man up at three: everyone rises at
exactly eight, having recovered an identical fraction of everything, which is
the one fighter the corner professional says he never sees. Rise time — *"the
most informative signal a real fight produces"* — is computed away.

And the foul chain, which matters more than its size suggests: professional
boxing already owns the twelve-round non-engagement case. Failing to make a
bona fide effort is a foul, with a remedy chain of instruction, caution,
warning, point deduction, disqualification. **It punishes non-engagement
without ever touching the man who is hitting and not being hit.** That is the
owner's distinction, enforced by the sport's own machinery rather than by a
movement tax Decision 0030 forbids or a scoring hack nobody wants.

---

## 7. Missing game behaviour

Things a modern arcade game needs that boxing realism alone will not supply.

No hitstop, no impact vocabulary, no camera impulse: `animation_model.json` and
`camera_model.json` contain no impact, shake, kick, freeze or emphasis keys at
all. No input buffer in practice (2 ticks = 33ms is smaller than one frame of
display-latency jitter; modern action games buffer 100–150ms). One telegraph
for every punch — a binary "a punch is in the air" available from startup frame
0, identical across the move table, so there is no per-punch readability
gradient for a human to learn. No hurt-state vocabulary of any kind. No
comeback-adjacent tension: the fight has no state between "nothing" and
"stopped".

And the sharpest one, from the game-feel specialist: **the twelve-round
stalemate is the more dangerous of the two failures**, because it is a 100%
acknowledgement failure. *"You press, the fighter throws, and nothing in the
world answers you. Three thousand times."* Against a priority order whose first
item is "impressively responsive," that is the top-of-list defect — and its
cause is the worst class of feel bug: **the game says yes to an input and then
throws it away.**

---

## 8. 2026–2029 modernisation opportunities

Places where the project is thinking like an older game, with the old creative
intent separated from the old limitation.

**Damage as threshold texture swaps** was a memory limitation; the intent was
*the fight leaves marks*. The modern equivalent is eight continuous,
asymmetric, region-driven channels — which this canon already authored and
which nothing yet renders. Eye damage is per-side, so swelling is asymmetric
and the fighter turns away from the closed side: that asymmetry is
simultaneously the truth and the comedy engine.

**Bright fighters on dark arenas** was partly a lighting limitation; the intent
was focal control. The modern equivalent is an enforced value/chroma budget
validated on materials rather than faked in lighting.

**The locked side-on camera** was a limitation; the intent was that the audience
always sees the geometry of the exchange. The modern equivalent is a camera
contractually forbidden from hiding the range band or the guard structure —
and `camera_model.json` already has `readability` and `observable_inputs` keys,
which is exactly where that contract belongs.

**Canned taunts** were a limitation; the intent was personality continuing after
the bell. The modern equivalent is already sitting in the stream: the bout emits
a `D` row every tick for every fighter carrying strategic aim, tactic, execution
and a reason code in boxing's own words — `SEEK_RECOVERY_SPACE`,
`PUNISH_RECOVERY`, `AVOID_OVERCOMMIT`. **Intent is in the stream. A renderer
never has to guess what a fighter is trying to do.** That is a gift the
lineage never had.

**Simulation tick as input tick.** Keep the authoritative sim at 60Hz; sample
and timestamp input at 240–1000Hz. Eight milliseconds of free latency and a
2026 baseline.

**And the one thing explicitly not to transplant (C):** that lineage used
caricature as national and ethnic shorthand. The modern route to instant
identity is silhouette, costume *geometry* and motion signature — and the
coed, no-division roster makes body architecture the natural axis anyway.

---

## 9. Reusability risks

Systems most likely to become one-off implementations rather than shared
architecture, in the architect's order.

**Highest: `policy.BY_BAND`, `policy.BY_HAND` and `judging.JUDGE_STYLES`** —
hand-authored gameplay tables inside runtime Python, with no canon file and no
C++ twin. `BY_HAND` duplicates canon's `hand` field *correctly today*, which is
precisely how these rot.

**`resolution.knockdown_pressure`** — a combining shape invented in the
integrated package, competing with `punch_model.delivered_impact`, which
authors `derived_from: stamina_cost`. **(E)** Which file is authoritative for
delivered impact.

**`effort_max = max(efforts.values())`** — a global normaliser over the whole
effort table that any future high-effort move silently rescales. The hero
designer found the same hazard from the other end: authoring an Ultimate with a
`stamina_cost` above the punch table's maximum would re-normalise delivered
impact for every punch in the game. **(D)** Falsifying test: author a throwaway
ability at `stamina_cost: 8.0`, re-run the impact vector, see whether
`overhand_rear` moves.

**`fnv1a64` re-declared in `bout.py`** alongside `UppercutFnv1a64`. **The
count/rise/referee logic inlined as `IntegratedBout` methods** rather than a
core with a C++ twin. **`data/replay_model.json` is not in `contract.CANON`** —
the integrated stream does not declare the replay contract it exists to satisfy.

**Three authoring surfaces for move timing (A).** Punch resolution reads
`animation_model.json`; evasion startup/recovery reads the moves table;
evasion active window reads `guard_evasion_model.json`. One fight, three
clocks, fields not spelled alike. The correct relationship: authored animation
frames are *presentation of* authoritative timing, never the source of it, and
a validator should assert equality rather than the runtime reading whichever
file it imported.

**One latent port hazard (A).** Exactly one site divides a possibly-negative
value — `rope_scaled`'s `(delta * retreat_mult) // 10000`, with `delta`
negative for the left-side fighter. Python floors; C++ truncates. It is masked
only because `retreat_mult` is currently 0 (**verified**). Any ringcraft work
that makes it non-zero silently forks the two runtimes. Route it through an
explicit `floordiv()` now.

---

## 10. Proposed tests

Falsifiable scenarios, not opinions. Each states what the stream must show.

1. **Band legality.** For every band and every move the policy can offer,
   `RANGE.in_band()` must return true. Today: 7 failures. *(Now written as a
   standing check — see §12.)*
2. **Punch ledger.** `sum(punches_thrown) == resolved + whiff_band + voided +
   in-flight` over a full fight. Today: fails by the ghost count.
3. **Decision path survives.** A seed sweep under the `professional` ruleset
   must reach the cards at least once — the executable form of
   `decision_path_must_survive: true`. Today: 0 of 30.
4. **Ten-point must.** For every scored round on every card, the round winner
   receives exactly 10. Today: falsifiable by construction.
5. **Judge independence.** Print the three per-round evidence sums beside the
   cards in a contested fight. Prediction: the two `pressed`-weighted judges
   agree with each other on essentially every round and disagree with the third
   whenever anyone advanced — a panel with one degree of freedom, not three.
6. **Body investment.** A throws only body shots for rounds 1–4; B throws head
   shots at equal count and effort. From round 6, B's wind gain per resting tick
   must be strictly below A's at equal Reserve. Today: identical.
7. **Denied recovery.** A below the low-wind line; B advances for 600 ticks then
   stops. The stream must show `RECOVERY_DENIED` with wind flat or falling, then
   `REST_WHEN_SAFE` and rising wind within a bounded number of ticks.
8. **Pursuit tax.** A pressure fighter advancing all round must end the round
   with strictly lower wind than the retreater. If not, movement billing is
   broken.
9. **Free-action audit.** A fighter choosing `MICRO_ADJUST` every tick must not
   end a round with more wind than the same fighter choosing `REST`.
10. **Legs.** Below the exhausted Reserve threshold, `X` rows must show smaller
    applied displacement per movement tick than at full Reserve.
11. **Attacker fatigue.** The same punch against the same defender state,
    thrown at 90% and 12% wind, must not produce identical knockdown pressure.
    Today it does.
12. **Reaction-lattice phase.** With the authored 4-tick decision interval,
    sweep commit offsets 0–3 and count slips per punch per phase. If bimodal,
    the interval must not be a hard lattice — otherwise mid-tier slips will read
    as random, which is the failure the feel specialist exists to prevent.
13. **Turn order.** Swap `DEFAULT_PARTICIPANTS` and re-run mirrored profiles.
    If the winner follows array index, tick order is authoritative.
14. **Silhouette CI.** Normalised shape-context distance between every new
    fighter silhouette and every existing one at matched pose and angle, with a
    floor. Machine pre-check before any human hour is spent.

---

## 11. Proposed Director decisions

Only questions that genuinely require authority. Nothing here is a preference
seeking a blessing.

**E1. Range-band shape.** Does canon's `range_band` become a *set* per move? A
jab is legal at mid and outside; a hook at inside and mid. One band per punch
is a canon shape question, and the fix to B1 depends on the answer.

**E2. Stoppage authority.** Which file rules stoppage-by-knockdown-count —
`condition_model.knockdown` or `data/rulesets/*`? The architect's implementable
proposal: `condition_model` keeps the arithmetic (thresholds, count clock,
relief fractions, identical for every referee per Rule 16); the *contest rules*
move to the ruleset exclusively; `max_per_round`/`max_per_bout` are **deleted**
from `condition_model` rather than left as fallbacks, because a value only
sometimes read is the same defect one layer down; `null` means "no stoppage by
that mechanism" and never "use a default". `IntegratedBout(ruleset=...)`,
`CANON` gains the ruleset actually fought under, contract bumps to v3 — free
today, a re-prove later.

**E3. Knockdown-relevant regions.** Does `torso_lower` (the body knockdown) and
possibly `head` become knockdown-relevant, and does the knockdown region become
explicitly authored rather than `target_regions[0]`?

**E1′. Fatigue and offence.** Does fatigue reach offence through *shot selection
and effective range*, or through delivered force? The council's answer is
selection and range — and that the structure must be authored before any number
is fitted. Related and separable: does fatigue reach *structure* (the guard)
before it reaches offence?

**E4. Observability of fatigue.** `cpu_decision_model.observable_inputs`
declares `stamina_change`; `Observable.__slots__` has no field for it. Both
cannot stand, and the answer gates whether recovery denial can ever be
deliberate rather than incidental.

**E5. Committed-action recovery frames.** Do they pay wind recovery? Today they
do, which makes punching, evading and *mistiming* partly self-funding.

**E6. Delivered-impact authority.** `punch_model.delivered_impact` or
`generic_sandbox_effort.effort`?

**E7. Crowd Bar idle decay.** Does it survive once the foul chain owns stalling,
given that expiry already solves banking and decay is the term most likely to
collide with defensive purity?

**E8. Hitstop.** Presentation-only with an input-fairness rule at the input
layer (the architect's ruling, and the council's recommendation), or
authoritative tick-counted (the shape is specified and determinism-safe if it
never enters the frozen cores)? Not needed before the human input layer exists.

**E9. Definition of a burst.** `acceptance_bands.burst_wind_low/high` (15–35) is
inert until "burst" is defined; at authored costs that band is twenty to fifty
punches, which is a round, not a burst. A definition problem, not a value
problem.

---

## 12. Recommended order

Strict priority. The council's ordering, with the architect's reasoning and the
Director's own prohibition on research detours applied.

**First, and alone if only one thing is done: unify the band gate (B1/B2).**
Delete `policy.BY_BAND`; derive legal attacks from the range pack; reconcile the
punch vocabulary so the policy cannot select a move the bout cannot fly. It is
the mechanical cause of one failure mode, and **every measurement taken before
it is a measurement of a fight that cannot land from half its bands.**

**Second, resolve ruleset authority (B2/E2).** It decides what "an ending" *is*.
Any sweep run before it must be re-run after it.

**Third, read the canon already hashed (B6).** `reaction.floor_ticks` and
`decision_interval_ticks`; `outcome_recovery`'s multipliers and counter windows;
the torso→stamina impairment. None is tuning; all three are reading numbers the
contract already claims. The feel specialist re-ranked `outcome_recovery` to
first in his own discipline: it costs no canon change, it creates the only
human-reactable window in the game, and **whiffing has to hurt before throwing
becomes a decision.**

**Fourth, fix the cards (B3/B4).** The ten-point-must construction, and the
`pressed` unit mismatch — with the referee's caveat that a *correct* `pressed`
is still the wrong proxy, so effective aggression should be conditional on the
ground advanced ending in a landed punch or forcing the ropes, and ring
generalship should get a channel at all. The bout already computes `_on_ropes`,
`band` and `preferred_band`.

**Fifth, the knockdown funnel (B5).** Author the knockdown-relevant region
explicitly rather than reading an array index.

**Sixth — and only now — re-run the sweep and look at the fight.** Every
diagnostic in this report and in the fight artifacts is provisional until then.
The contested middle either appears or it does not, and *that* is the
measurement worth having.

**Then, and not before:** the guard stage, reach-at-contact, the chain window,
the clinch, the foul chain, feints, and the two art tasks worth doing early
because doing them late is expensive — writing down that animation timing is
canon, and locking reach as an art input before any character exists, since
arm length is a combat input and not a free caricature dial.

---

## What the council did not get to decide

The number is now:

    complete integrated fights = 1 (stoppage), 1 (decision)

and the honest gloss is that one of those two is a fight and the other is
thirty-six minutes of two men missing. None of these eight has watched Project
Uppercut fight. Now, for the first time, somebody can — and the first thing the
fight said, unprompted, was that a table in the policy disagrees with canon.

That is the review working. The knives were sharp; the fight was sharper.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 00:19 UTC | specialist council report end ] -->
