<!-- Claude Fable 5 (claude-fable-5) - 2026-08-03 07:19 UTC - boxing-punches-guards-and-target-matchups condensed rewrite start -->

# Boxing Punches, Target Regions, and Matchup Pointers (Queensberry Rules)

**Project Uppercut — combat system design reference**
**Path:** `docs/design/boxing-punches-guards-and-target-matchups.md`
**This revision:** condensed rewrite of the 813-line PR #3 version (reported merge `524df30`). What was removed, what was kept, and why: see Provenance at the bottom.

> **Status (Rule 18): DESIGN REFERENCE — not canon data, not implemented.**
> Every value cited here is a tuning hypothesis. Frame, stamina, and
> counter-vulnerability data are owned by `data/moves/generic_sandbox_moves.json`;
> if this file and that file disagree, the data file wins.

## Scope and ownership (anti-drift contract)

This document owns exactly three things: **punch profiles** (trajectory, entry
angle, variants, range), **target-region effectiveness**, and the **legal/foul
boundary**.

It deliberately does **not** contain:

- the ten-guard catalog → `docs/design/boxing_guard_matchups.md`
- the punch-vs-guard and guard-vs-punch matchup tables → same file, Master Tables
- collision and interception truth → `data/collision_model.json` + `docs/phase1a/collision_truth.md` (extent modulation per Decision 0010)
- frame data and costs → `data/moves/generic_sandbox_moves.json`

One table, one home. The PR #3 version reproduced the full guard catalog and
both matchup tables alongside their canonical copies; duplicated tables drift,
and the guard doc's reconciliation log exists precisely because they already
did once. Link, don't copy.

## Core rule (stated once, owned elsewhere)

> **A guard protects the interception path, not merely the final target.**

Canonical statement: `boxing_guard_matchups.md`. Enforced in
`data/collision_model.json`, whose `guard_interception` map was corrected by the
validator on 2026-08-03 for exactly this reason. The uppercut is the showcase:
it targets `jaw_chin` (a high region) yet is authored `blockable_low`, because
it travels **upward** — a dropped forearm bars its path and a raised shell does
not. Per Decision 0010, posture and alignment states then modulate the coverage
*extents* of the two guard volumes; `guard_interception` decides which volume is
permitted to intercept a path, the extents decide whether it actually reaches.

---

## Punch catalog

Per entry: trajectory and entry angle · move-table ids · `guard_interaction` ·
variants · effective targets · poor targets · risk profile. Target names use
`data/condition_regions.json` ids where one exists.

### Jab — `blockable_high` — `jab_lead`

- **Trajectory:** straight line, lead hand, shortest possible path — the only
  punch launched without first opening the guard.
- **Variants:** probing/measuring jab, power jab (weight transfer), double and
  triple jab, up-jab (rising line against taller or crouching opponents), body
  jab (see body shots).
- **Effective targets:** the nose (waters the eyes — momentary blindness and
  disorientation), `jaw_chin` (head snap; rhythm and balance disruption), solar
  plexus as a body jab (breath and stamina tax).
- **Poor targets:** the forehead (thickest bone on the body; more risk to the
  puncher's hand than to the target), chest and shoulders (absorbed harmlessly).
- **Risk:** the lowest in the sport, and the move table agrees — cheapest
  startup, recovery, stamina, and counter exposure in the generic set. Its job
  is volume, range control, and setup, never finishing. Mechanically, it should
  never be the punch that loses an exchange.

### Cross / straight rear — `blockable_high` — `cross_rear`

- **Trajectory:** straight line, rear hand, full rear-foot/hip/torso rotation —
  the highest-leverage straight punch available.
- **Variants:** basic cross, the 1-2 behind a jab, counter-cross off a slip,
  body straight (see body shots).
- **Effective targets:** the point of the chin (`jaw_chin` — maximum rotational
  force through the jaw hinge; top single-shot KO potential), solar plexus
  (drives through center guard gaps and winds the opponent).
- **Poor targets:** the upper skull (glancing contact, hand-injury risk), a
  tight closed guard (wasted energy plus counter exposure).
- **Risk:** moderate — rear-hand commitment opens the lead side and briefly
  costs lateral mobility (move table).

### Hooks — `blockable_either` — `hook_lead`, `hook_rear`

- **Trajectory:** bent arm near 90°, horizontal arc around the guard from
  outside the eyeline. The one punch shape either guard volume can intercept,
  which is why it is authored `blockable_either`.
- **Variants:** lead hook (speed; the mid-range staple), rear hook (more power
  and commitment; longest arc in the generic set), check hook (pivot counter
  against a stepping-in opponent), short/shovel hook (compact ~45° blend of
  hook and uppercut, inside only), body hook (below).
- **Effective targets:** temple and jaw hinge (rotational force disrupts the
  vestibular system — balance, not just the chin), the liver via lead body hook
  (below), floating ribs (mobility and breathing tax).
- **Poor targets:** center of the chest (dense mass, no mechanical advantage),
  the forehead.
- **Risk:** high against anyone who steps inside the arc; wide versions thrown
  from range are visible early and duck-under bait.

### Uppercuts — `blockable_low` — `uppercut_lead`, `uppercut_rear`

- **Trajectory:** near-vertical rise on or near the centerline — the
  design-principle showcase (targets high, intercepted low).
- **Variants:** rear uppercut (the standard; deepest commitment — highest
  counter-vulnerability in the generic set), lead uppercut (rare; high launch
  cost from most guards — from the shell it is skill-gated, not absent, per the
  guard doc's reconciliation log), short/compact inside uppercut, body uppercut
  to the solar plexus.
- **Effective targets:** under the chin (`jaw_chin` — violent upward
  displacement; sets up follow-on hooks), solar plexus between the elbows of a
  standard guard.
- **Poor targets:** the crown of a ducking head (hand-fracture territory), the
  collarbone (a mis-range artifact with no concussive value).
- **Risk:** highest in the set. From any real distance it is slow, telegraphed,
  and leaves the thrower's own chin exposed for the full flight.

### Overhand — `blockable_high` — `overhand_rear`

- **Trajectory:** looping over the top from outside the shoulder line,
  descending diagonal — built to clear a guard rather than pass through it,
  adding the thrower's bodyweight on the way down.
- **Variants:** overhand right (the classic shorter-fighter answer to a taller
  opponent's chin and to the long guard), overhand left (southpaws; surprise
  counters).
- **Effective targets:** behind the ear and the temple (equilibrium disruption
  — spectacular knockdowns), the point of the jaw (downward trajectory
  multiplies force with bodyweight).
- **Poor targets:** the body — mechanically the wrong tool; slow, awkward, and
  the thrower's head is fully exposed on the follow-through.
- **Risk:** slow windup, forward weight commitment, badly exposed after the arc.
- **Authoring gap: closed 2026-08-03.** This flag previously read that
  `move.schema.json` listed `overhand` as a valid category with no `overhand_*`
  entry in the generic set. `overhand_rear` was authored in commit `1675d27` as
  a tuning hypothesis — 11 startup, 3 active, 21 recovery, mid band, 3.2
  stamina, `blockable_high` — carrying the highest counter vulnerability in the
  set, because the looping path telegraphs and the head travels forward with it.
  The animation frame-lock refused the move until `anim_overhand_rear` landed at
  matching ticks, which is that cross-file lock working as designed.

### Body shots — `blockable_low` — `body_hook_lead`, `body_straight_rear` (+ body jab, body uppercut as variants)

- **Cross-cutting category:** every punch above has a body variant. Structurally
  load-bearing: no guard covers the head cluster and the torso at once, so body
  investment pays against nearly every structure — and this must **emerge** from
  zone coverage, never be hardcoded (see the guard doc's design principle).
- **The liver shot:** a lead hook under the opponent's right elbow into the
  right side of the torso. It ends fights through the autonomic nervous
  response, not raw force — the one body punch with genuine single-shot
  stoppage power, often as a delayed drop.
- **Accumulation profile:** stamina drain, breath disruption, hands lowering
  across rounds, and arm/`guard_integrity` damage on blocked volume — the
  mechanism by which passive blocking eventually gets opened.
- **Region-resolution note: ruled by Decision 0011.** The collision model's
  torso hurtboxes (`torso_upper`, `torso_lower`) are declared `side: center`
  while the eyes and arms are side-declared, and the liver's defining property
  is its asymmetry. The torso is **not** side-split: the liver shot is a
  stance-relative *contact-quality outcome* on `torso_lower`, qualified by which
  side of the torso the swept path enters, not a region of its own. The
  collision model already computes entry geometry and stance relationship, so
  the asymmetry falls out of data that exists rather than out of two new
  hurtboxes — and the eight-region model stays eight.

### Low-percentage and showpiece punches

- **Bolo punch:** windmill wind-up; the lowest-percentage legitimate punch in
  the sport, occasionally landing precisely because the trajectory is
  unfamiliar. Natural Showmanship-category material.
- **Wild haymaker:** unstructured, off-balance power swing; all risk, minimal
  technique.
- The correct home for both in Project Uppercut is the comedy and Showmanship
  layer, priced honestly — visible commitment, real whiff punishment, never
  secretly competitive.

---

## Target-region effectiveness (summary)

| Region (condition-model id where one exists) | Best tools | Why | Poor tools |
| --- | --- | --- | --- |
| `jaw_chin` | cross, hooks, overhand, rear uppercut | rotational and upward shock — top single-shot KO potential | jab (snap, not stoppage) |
| `head` — temple / behind the ear | hooks, overhand | arrive outside the eyeline; equilibrium disruption | frontal straight punches |
| `head` — nose | jab, cross | waters the eyes; disorientation | wide arcs |
| `eye_left` / `eye_right` | jab accumulation, clean hooks | cuts and swelling come from repetition, not raw power | single power shots |
| `head` — forehead / crown | none | thickest bone; the puncher's hand is the likelier casualty | everything — a landing to avoid |
| `torso_upper` — solar plexus | body straight, body uppercut, body jab | breath disruption between the elbows | overhand |
| `torso_lower` — liver, right side (see resolution note) | lead body hook | autonomic shutdown; delayed drops | anything center-mass |
| torso — floating ribs | body hooks | mobility and breathing tax | straight center shots |
| `arm_left` / `arm_right` + `guard_integrity` | any blocked volume | passive blocking pays a real, accumulating price | n/a — secondary target by nature |

## Canonical region mapping (Decision 0011)

The anatomical vocabulary above is finer-grained than `data/condition_regions.json`,
which declares eight strikeable regions, and the collision validator rejects any
move targeting a region with no hurtbox. Decision 0011 rules that this vocabulary
stays **design prose** and maps down; it does not become new regions or hurtboxes.

| Prose term | Canonical region |
| --- | --- |
| temple, cheek, nose, forehead, behind the ear, crown | `head` |
| point of the chin, jaw hinge | `jaw_chin` |
| eyes | `eye_left` / `eye_right` |
| sternum, solar plexus | `torso_upper` |
| liver, floating ribs, ribs | `torso_lower` |
| guard arm, blocked volume | `arm_left` / `arm_right` (+ `guard_integrity`) |
| collarbone | none — a mistarget outcome, not a region |

These prose names must not enter move data. `target_regions` in
`data/moves/generic_sandbox_moves.json` takes canonical ids only.

## Legal targets and fouls

**Legal:** front and sides of the head; the torso above the belt line.
**Fouls regardless of contact quality:** back of the head or neck (rabbit
punch), kidneys, spine, anything below the belt.

System hooks, both already real:

1. The Rule 22 collision validator rejects any offensive move targeting a
   region with no hurtbox — foul regions stay un-authored in the generic set by
   design, so a foul cannot exist as an accidental data entry.
2. If deliberate fouls ever become mechanics (comedy or heel identity), they
   route through observable referee evidence and the seven officiating
   profiles — never hidden RNG, never scorecard knowledge (Rule 3).

## Matchups: pointers, not copies

Both matchup tables — best punches against each guard, best guards against each
punch — live **only** in `docs/design/boxing_guard_matchups.md`. Any punch-side
text touching them must respect that file's standing reconciliation-log
rulings:

1. **Cross-arm vs uppercut is conditional** on bar height: a low, aligned
   forearm bar intercepts the chin-line uppercut; high-riding or split arms are
   opened by it. Absolute claims in either direction are wrong.
2. **Long guard vs overhand:** the overhand over the extended arm is that
   guard's signature weakness, not something it smothers.
3. **Shell vs overhand is conditional** on roll timing and shoulder alignment:
   a timed roll deflects it; a static or misaligned shell is arced over.
4. **Shell vs jab:** canon lists the shell among the *weaker* jab responses
   (lead hand down). The rear-hand parry and shoulder catch are real but
   skill-priced nuances, not a structural strength.

## CPU and Training Mode hooks (condensed)

CPU reasoning stays observable-evidence-only; the canonical worked examples
live in the guard doc. Training Mode inherits this file's per-target logic
directly — "why the jab," "find the liver," "when the uppercut" are lessons
that already exist as data above, which is Rule 2 working as intended: boxing
knowledge that is functional, not decorative.

## Everything here is conditional

No matchup in this file is automatic. Range, timing, stance, posture, setup,
movement, fatigue, contact quality, and Ringcraft modulate every claim, and
every number remains a tuning hypothesis until a validated specification or
test promotes it (Rule 18).

## Provenance and conflict handling

Condensed 2026-08-03 from the 813-line PR #3 merge (reported commit `524df30`)
and its two source passes, checked against the guard doc as amended through
Decision 0010 and the 06:31 UTC canon-integration update.

**Removed:** the duplicated ten-guard catalog and both duplicated matchup
tables (now pointers), plus restated collision-truth material owned elsewhere.
**Preserved:** per-target effectiveness detail, the foul boundary, punch
variants, validator hooks, and the overhand authoring gap.
**Corrected rather than averaged**, per the standing reconciliation log: one
source pass claimed the cross-arm guard makes uppercuts "impossible" (ruled
conditional on bar state) and that the long guard smothers overhands (ruled the
opposite — its signature weakness). The same pass's shell-parries-jabs claim is
recorded above as a skill nuance, not a table change. If the merged 813-line
version carried any of those three claims as written, this rewrite supersedes
them; they were already ruled on before PR #3 landed.

<!-- Claude Fable 5 (claude-fable-5) - 2026-08-03 07:19 UTC - boxing-punches-guards-and-target-matchups condensed rewrite end -->
