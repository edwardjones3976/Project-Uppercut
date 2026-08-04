<!-- Claude Fable 5 (claude-fable-5) - 2026-08-03 05:04 UTC - boxing_guard_matchups.md start -->

# Boxing Guard Types and Style Matchups Under Queensberry Rules

**Project Uppercut — combat system design reference**

> Scope: developer-side reference for guard modeling, punch-vs-guard matchups,
> offense economy per guard, and CPU decision logic. When
> `docs/architecture/COMBAT_SYSTEM_ARCHITECTURE.md` exists, this document feeds
> its guard/defense subsystem; do not duplicate content there — link here.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:33 UTC | START edit: canon-integration notes added at landing. The original author's tag lines above and below are left untouched per CONTRIBUTION_TAGGING.md. ] -->

> **Status (Rule 18): DESIGN REFERENCE — not canon data, not implemented.**
> This document proposes structures and fields. It creates no schema and changes
> no behaviour. Promotion to canonical data requires Director ratification plus a
> validator and fixtures, matching the pattern used for combat states, movement,
> camera and collision. Every value here is a tuning hypothesis.
>
> **Rule 1 boundary — historical exemplars.** Real practitioners are named below
> purely as technique shorthand, which Rule 2 supports: real boxing knowledge is
> meant to be functional. Rule 1 governs *shipped* identities, and these names
> must never migrate into fighter identities, bios, commentary lines, trait text,
> or any other player-facing content. They are research references only, and they
> stop at this file.
>
> **Integration contract with `data/collision_model.json`.** That file defines the
> physical primitives — two guard volumes (`guard_high`, `guard_body`, each
> absorbing into arms, guard integrity and stamina) and `guard_interception`,
> which maps a move's `guard_interaction` onto the volumes that intercept it. The
> ten structures below are *postures*: named configurations of those same two
> volumes plus an offensive profile. The collision pipeline remains the sole
> authority on whether an attempt resolves as blocked, and `guard_interception`
> remains the sole authority on which volume intercepts which punch path.
>
> **Amended 2026-08-03 06:31 UTC (Claude Opus 5, claude-opus-5).** The clause
> here originally read that any entry contradicting `guard_interception` is
> "wrong by construction." That was drawn too tight. The conditional rows below
> — cross-arm bar low or high, shell roll timed or late — are state-dependent
> *geometry*, which a fixed `guard_interaction` → volume map cannot express, so
> the clause condemned the most boxing-truthful content in the document.
> Resolved per Decision 0010: posture and alignment states modulate the
> **coverage extents** of the same two volumes. `guard_interception` still
> decides which volume is *permitted* to intercept a given path; the extents
> decide whether it actually reaches. The collision pipeline remains the sole
> authority and never reads a posture's identity. An entry here is wrong only
> if it claims an interception the resulting extents cannot produce.
>
> Worth recording: the "Core rule" stated below — a guard protects the
> interception *path*, not the final target — was reached independently in this
> document and by the collision validator on 2026-08-03, which rejected an
> uppercut model built on target region instead of travel path. Two passes, same
> conclusion.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:33 UTC | END edit ] -->

Historical framing worth keeping in mind: these guards exist *because* of
Queensberry rules. Padded gloves make blocking with the hands and forearms
viable, which is why the bare-knuckle era used a completely different upright,
arms-extended stance. Guard design in-game should reflect glove-era mechanics.

---

## Design Principle

A guard is not "high defense" or "low defense." It is a **body structure** that
protects some lines while exposing others, and that also shapes what offense is
cheap or awkward to launch from it.

Every guard defines:

```text
guard_type
protected_zones
weak_zones
best_against
vulnerable_to
counter_options
offense_effective      # punches cheap/natural to throw FROM this guard
offense_awkward        # punches that force abandoning the structure
stamina_cost
mobility_cost
visibility_cost
```

Every punch defines:

```text
target_region
trajectory
entry_angle
range
guard_intercept_zone
counter_exposure
```

### Core rule (blueprint-level)

> **A guard protects the interception path, not merely the final target.
> Punches define both target region and travel path; guards define protected
> planes and exposed lanes.**

This single rule prevents most future modeling errors — e.g., an uppercut
targets the jaw, but the best interception is usually a low/mid forearm
structure, not a hand parked at the chin.

---

## Guard Catalog

Each guard entry: structure, defensive matchups (both directions), offense
economy from the guard, best guard responses, and game-logic summary.

### 1. High Guard / Basic Shell

**Structure:** Both gloves held high near the temples and cheeks, chin down,
elbows tucked against the ribs. The amateur and pressure-fighter staple.

**Defends well against**

| Punch | Why |
| --- | --- |
| Jab to head | Gloves already occupy the center/head lane |
| Straight right / cross | Forearms and gloves absorb direct head shots |
| Lead hook to head | Side glove can catch or absorb |
| Overhand | High hands cover looping head shots |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Uppercut | Travels upward under/through the guard line |
| Body hooks | Elbows may not stay tight enough |
| Body jab / body straight | Center body can remain open |
| Angled shots | A static shell can be turned or split |

**Offense from this guard**

- *Effective:* fast straight jabs, right crosses, short lead hooks — hands are
  already in launch position on the head line.
- *Awkward:* looping body shots and wide uppercuts — throwing them forces the
  fighter to fully drop the shell and expose the head.

**Best guard responses:** catch jabs, absorb straights, roll with hooks, drop
elbow vs body shots, step back vs uppercuts.

```text
strong_head_protection
body_coverage_from_guard_body_extent   # 0.55, under the 0.6 interception
                                       # threshold: the body lane is OPEN
weak_vs_upward_centerline_attacks
offense_favors_straight_punching
can_become_passive_if_overused
moderate_arm_condition_damage
```

### 2. Peek-a-Boo Guard

**Structure:** Gloves firmly against the lower cheeks/chin, elbows tucked,
torso compact and squared, paired with constant rhythmic slipping, bobbing, and
explosive entries. A full style, not just a hand position (D'Amato / Tyson /
Patterson).

**Defends well against**

| Punch | Why |
| --- | --- |
| Jab | Tight guard plus head movement disrupts straight entries |
| Cross / 1-2 combinations | Compact structure absorbs or slips; a moving head is a poor linear target |
| Hook | Gloves and forearms sit close to the temples |
| Uppercut | Better than an ordinary high guard when elbows stay tucked; gloves sit in front of the chin lane |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Long body jab | Compact stance allows outside body touches |
| Wide body hook | If elbows rise during an entry |
| Check hook | Aggressive entries run into angles |
| Rear uppercut timed on entry | The Douglas-vs-Tyson failure mode: punches timed as the fighter dips in |

**Offense from this guard**

- *Effective:* devastating hooks to head and body, and inside uppercuts — the
  torque generated by slips loads them for free.
- *Awkward:* long-range straight punching — the style must close distance and
  fight inside to function.

**Best guard responses:** slip inside, bob and weave, counter hook, explosive
body-head combination.

```text
strong_all_around_close_range_defense
rewards_movement_and_timing
offense_favors_hooks_and_uppercuts_off_slips
weak_if_entries_become_predictable
high_stamina_demand   # collapses when conditioning fades
```

### 3. Philly Shell / Shoulder Roll

**Structure:** Lead arm draped low across the torso, rear glove glued to the
rear cheek/chin, lead shoulder raised to protect the lead side of the jaw
(Mayweather, James Toney). Built for deflection and instant counters.

**Defends well against**

| Punch | Why |
| --- | --- |
| Straight right / cross | Rolled off the raised lead shoulder |
| Predictable-line head shots | Rolls turn clean hits into glances |
| Lead-side body hooks | The draped lead forearm shields that flank |
| Single committed power shots | Excellent counter platform |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Jab | The lead hand is down; jabs must be shoulder-checked or rear-hand parried |
| Lead hook around the guard | Can wrap the shoulder position |
| Center / rear-side body straights | Torso center remains targetable |
| Overhand — *roll late or shoulder misaligned* | Arcs over the shoulder line. A timed roll turns it instead — conditional by design (reconciliation item 4) |
| Fast combinations | Multiple angles stress the shell |
| Southpaw straight left | Travels down the open side and breaks the roll rhythm; shell fighters historically switch to a conventional guard vs southpaws |

**Offense from this guard**

- *Effective:* counter right crosses, check hooks, fast flicking jabs from the
  hip.
- *Awkward:* stiff driving power jabs and lead uppercuts — the low-hanging lead
  arm offers no loading path, so both carry a very high `offense_launch_cost`.
  Neither is unavailable: elite shell fighters land the lead uppercut routinely,
  so ringcraft buys the cost down rather than gating the punch out
  (reconciliation item 5).

**Best guard responses:** shoulder roll, pull counter, check hook, rear-hand
counter, pivot away.

```text
excellent_vs_predictable_straight_power
high_counter_readiness
offense_favors_counters_over_pressure
weak_vs_volume_bodywork_hooks_around_shell_and_southpaw_angles
overhand_coverage_depends_on_roll_alignment_state
lead_uppercut_available_at_high_launch_cost_scaling_with_ringcraft
requires_high_ringcraft   # high skill guard
```

### 4. Cross-Arm Guard

**Structure:** Forearms stacked/crossed horizontally over the face and upper
chest, elbows angled slightly forward (Archie Moore, comeback-era Foreman,
elements in Frazier). Very sturdy, hard to split cleanly, but limits offense
and vision.

**Defends well against**

| Punch | Why |
| --- | --- |
| Hooks to head | Crossed arms absorb looping attacks |
| Overhands | The forearm structure catches impact |
| Straight shots to the face | Dense barrier in front of the head |
| Short-range flurries | Strong absorption guard |
| Chin-line uppercuts — *conditional* | Only when the forearm bar is seated low and aligned across the centerline (see reconciliation log) |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Body shots | Lower torso opens depending on elbow placement |
| Uppercuts — *conditional* | Split upward through the middle when the arms ride high or separate under pressure |
| Angled body hooks | Wrap under the guard |
| Sustained volume to the arms | Arm condition degrades |

**Offense from this guard**

- *Effective:* wide hooks, sweeping overhand rights, backhand/flip-style jabs
  thrown off the crossed position.
- *Awkward:* quick straight jabs and crosses — the crossed forearms are a
  physical barrier that slows linear extension.

**Best guard responses:** smother pressure, walk the opponent down slowly,
counter after absorption, clinch/reset if overwhelmed.

```text
high_absorption
low_counter_speed
reduced_visibility
arm_damage_risk
uppercut_coverage_depends_on_guard_alignment_state
offense_favors_looping_power
good_for_durable_fighters
```

### 5. Long Guard

**Structure:** Lead arm extended toward the opponent's face to measure, frame,
blind, and jam, rear hand protecting the chin (Klitschko's pawing lead, Hearns
at range). A distance-control tool for tall/reach fighters.

**Defends well against**

| Punch | Why |
| --- | --- |
| Jab | The lead hand contests the jab lane |
| Straight entries | The extended frame disrupts the approach |
| Wide hooks | Smothered before they build arc / kept outside hook range |
| Rushes and inside pressure | Frames the opponent out and stalls forward momentum |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Overhand | Loops over the extended arm |
| Body shots underneath | The extended arm exposes the ribs |
| Inside hooks | Once the opponent gets past the frame |
| Counter right over the jab | The extended hand can be timed, trapped, or parried |

**Offense from this guard**

- *Effective:* stiff long jabs, straight right hands, pull-counters.
- *Awkward:* short inside hooks and tight uppercuts — the stance keeps the
  fighter at extreme range.

**Best guard responses:** frame, parry, step back, jab intercept, pivot out.

```text
excellent_distance_control
weak_once_opponent_is_inside
counterable_by_overhands_and_body_entries
offense_favors_long_straight_punching
suits_tall_reach_fighters
```

### 6. Low Lead Hand / Bait Guard

**Structure:** Lead hand carried low to invite attacks, improve vision, create
rhythm, and prepare counters (Ali, Roy Jones Jr., Hamed). Reflex-based; trusts
reads, pull-backs, and footwork rather than blocking.

**Defends well against**

| Punch | Why |
| --- | --- |
| Predictable jab | Slipped/parried from the relaxed position |
| Lunging attacks | The bait creates the counter opportunity |
| Overcommitted straights | Pull counter becomes available |
| Slow entries | Seen early with unobstructed vision |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Fast jab | The low hand arrives late |
| Lead hook | Side of the head is exposed |
| Overhand | The high line is open |
| Quick combinations | Guard recovery lags |

Nothing here is mechanically protected — value comes from baiting and vision,
and it is the structure that ages worst as reflex attributes decay.

**Offense from this guard**

- *Effective:* up-jabs from below the eyeline, lead hooks from unexpected
  angles, pull-counter rights.
- *Awkward:* sustained blocking-position exchanges and tight defensive-frame
  counters — the hand has to travel to get home.

**Best guard responses:** pull counter, slip jab, step-back counter, lead hook
trap.

```text
high_counter_potential
high_exposure
requires_timing_and_reflex_attributes
offense_favors_unseen_angles
dangerous_for_low_skill_cpu_or_player_behavior
degrades_hard_with_reflex_stat_decay
```

### 7. Tight Elbow Guard / Body Guard

**Structure:** Elbows tucked tight to ribs and centerline; hands moderate or
high, but body protection is the priority.

**Defends well against**

| Punch | Why |
| --- | --- |
| Body hooks | Elbows shield the ribs |
| Body jab | Center body line is covered |
| Uppercut | Dropped forearms intercept the upward path — the correct intercept structure for chin-target uppercuts |
| Inside combinations | Compact structure absorbs body pressure |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Hooks to head | Hands may sit too low/tight |
| Overhands | The high head lane opens |
| High jabs | The headline can be touched |
| Wide-angle shots | The compact guard can be turned |

**Offense from this guard**

- *Effective:* short counter uppercuts, shovel hooks, compact inside
  combinations — the frame is pre-loaded for them.
- *Awkward:* long straight punching — pinned elbows shorten reach and leverage.

**Best guard responses:** elbow block, forearm wedge, short counter uppercut,
step-in smother.

```text
strong_vs_bodywork_and_uppercuts
weaker_vs_high_hooks_and_overhands
good_against_pressure_fighters
offense_favors_short_inside_work
reduced_offensive_freedom_at_range
```

### 8. Double Forearm / Ear-Muff Guard

**Structure:** Both gloves/forearms clamp tightly over the sides of the head.
Primarily an emergency posture to survive flurries.

**Defends well against**

| Punch | Why |
| --- | --- |
| Hooks to head | Side coverage is strong |
| Overhands | Forearms absorb looping shots |
| Wild combinations | Compact coverage survives chaos |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Straight body shots | The body center opens |
| Uppercuts | Split underneath the clamped arms |
| Body hooks | Elbows lift away from the ribs |
| Jabs to body | Easy scoring touches |

**Offense from this guard**

- *Effective:* short 2-3 counters fired the instant the storm passes.
- *Awkward:* initiating almost anything while covered — opening the clamp is
  the price of offense; this is a survival posture, not a platform.

**Best guard responses:** cover up, wait out the storm, step back, counter when
the opponent overthrows.

```text
emergency_survival_guard
bad_for_scoring_and_visibility
loses_ring_position
vulnerable_to_bodywork_and_uppercuts
offense_limited_to_post_storm_counters
```

### 9. High Elbow / Forearm Frame Guard

**Structure:** One or both forearms frame across the opponent's line to control
space at close range or against pressure.

**Defends well against**

| Punch | Why |
| --- | --- |
| Inside hooks | The frame disrupts shoulder rotation |
| Head entries | The forearm blocks the entry path |
| Clinch attempts | Creates space |
| Short flurries | Interrupts rhythm |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Body shots | The framing arm exposes the torso |
| Overhand around the frame | Loops around it |
| Straight down the center | If the frame is misaligned |
| Uppercut under the frame | Rises beneath it |

**Offense from this guard**

- *Effective:* free-hand short hooks and uppercuts thrown off the frame;
  frame-pivot-counter exits.
- *Awkward:* long-range punching and committed rear-hand power while the frame
  is engaged.

**Best guard responses:** frame and pivot, smother, create an exit angle, short
counter.

```text
strong_inside_control_tool
not_a_pure_block
beaten_by_bodywork_and_angle_changes
offense_favors_free_hand_short_shots
```

### 10. Open Guard / Active Hands Guard

**Structure:** Hands stay mobile — parrying, touching, probing, disrupting —
rather than fixed.

**Defends well against**

| Punch | Why |
| --- | --- |
| Jab | Parry/catch disrupts rhythm |
| Straight | The active hand redirects |
| Single shots | Reads and responds well |
| Range entries | Touch control interrupts the setup |

**Vulnerable to**

| Punch | Why |
| --- | --- |
| Fast combinations | Too many threats to parry |
| Feints | Draws bad reactions |
| Hooks | Wide attacks bypass center parries |
| Body attacks | High hand activity exposes the torso |

**Offense from this guard**

- *Effective:* parry-and-return jabs and straights, hand-trap entries into the
  cross.
- *Awkward:* fully loaded power shots — active hands are rarely in a loaded
  position.

**Best guard responses:** parry, hand trap, touch-and-counter, jab disruption.

```text
high_skill_active_defense
strong_vs_predictable_singles
weak_vs_feints_layered_combinations_and_bodywork
offense_favors_touch_counters
```

---

## Master Tables

### Punch Effectiveness by Guard Type

| Guard | Strong Against | Weak Against |
| --- | --- | --- |
| High Guard | Jabs, crosses, head hooks, overhands | Uppercuts, body shots, angles |
| Peek-a-Boo | Jabs, crosses, 1-2s, hooks, some uppercuts | Check hooks, body jabs, punches timed on entry |
| Philly Shell | Crosses, lead-side body hooks, single shots; overhands *when the roll is timed and the shoulder aligned* | Jabs, lead hooks around the shell, center bodywork, southpaw angles; overhands *when the roll is late or misaligned* |
| Cross-Arm | Hooks, overhands, face straights, flurries; chin-line uppercuts *if bar is low/aligned* | Body shots, uppercuts *when arms ride high*, arm damage |
| Long Guard | Jabs, rushes, wide hooks, long entries | Overhands, body entries, inside hooks |
| Low Lead Hand | Predictable jabs, lunges | Fast jabs, lead hooks, overhands |
| Tight Elbow Guard | Body shots, uppercuts, inside pressure | High hooks, overhands, head jabs |
| Ear-Muff Guard | Head hooks, overhands, wild flurries | Body shots, uppercuts, straight body attacks |
| Forearm Frame | Inside hooks, clinch entries | Body shots, overhands, uppercuts underneath |
| Active Hands | Jabs, straights, single shots | Feints, hooks, combinations, body attacks |

### Best Punches Against Each Guard

| Opponent Guard | Better Punch Choices | Worse Punch Choices |
| --- | --- | --- |
| High Guard | Uppercut, body hook, body jab, angle hook | Repeated head jab, straights into gloves |
| Peek-a-Boo | Check hook, body jab, step-back straight, uppercut timed on entry | Lazy straights, predictable single jab |
| Philly Shell | Jab, lead hook, body straight, southpaw straight; overhand *against a late or misaligned roll* | Naked rear cross, predictable jab-cross; overhand *into a timed roll* |
| Cross-Arm | Body hook, angled body shot, volume to arms; uppercut split *only when arms ride high* | Single head hook, slow overhand, straights into the bar |
| Long Guard | Overhand, body entry, slip-inside hook, angle change | Long straight down the same line |
| Low Lead Hand | Fast jab, lead hook, overhand, double jab | Slow lunging straight |
| Tight Elbow Guard | High hook, overhand, high jab, angle shot | Body spam, unset low uppercut |
| Ear-Muff Guard | Body jab, body hook, uppercut, ring pressure | Wild head hooks into cover |
| Forearm Frame | Body hook, step-around hook, overhand, uppercut under frame | Smothered inside hooks |
| Active Hands | Feint-to-hook, body shot, layered combinations | Single predictable jab or cross |

### Best Guards Against Each Punch

| Incoming Punch | Best Guard Responses | Weaker Guard Responses |
| --- | --- | --- |
| Jab to head | High Guard, Long Guard, Peek-a-Boo, Active Hands | Philly Shell (lead hand down), Low Lead Hand if late |
| Cross / straight | High Guard, Philly Shell, Cross-Arm, Peek-a-Boo | Low/open guards |
| Lead hook | High Guard, Ear-Muff, Peek-a-Boo | Philly Shell if the shoulder is misaligned |
| Rear hook | High Guard, Ear-Muff, Cross-Arm | Long Guard once the opponent is inside |
| Uppercut | Tight Elbow Guard, Peek-a-Boo, low/mid forearm catch; Cross-Arm *only with a low, aligned bar* | Loose High Guard, Ear-Muff, Cross-Arm with high-riding arms |
| Body hook | Tight Elbow Guard, Peek-a-Boo, Philly Shell (lead side only) | Long Guard, Low Lead Hand, High Guard |
| Body jab / straight | Tight Elbow Guard, elbow drop, active parry | Ear-Muff, loose High Guard, Cross-Arm |
| Overhand | High Guard, Ear-Muff, Cross-Arm, Philly Shell *with a timed roll* | Long Guard, Low Lead Hand, Philly Shell *with a late or misaligned roll* |
| Flurry / combination | Peek-a-Boo, Ear-Muff, Cross-Arm | Active Hands if overwhelmed |
| Feint-to-punch | Disciplined High Guard, compact guards, patience | Active Hands, Low Lead Hand, overreactive shell |

### Offense From Each Guard (summary)

| Guard | Cheap / Natural Offense | Awkward Offense (breaks the structure) |
| --- | --- | --- |
| High Guard | Fast jabs, crosses, short lead hooks | Looping body shots, wide uppercuts |
| Peek-a-Boo | Hooks head/body, inside uppercuts off slips | Long-range straight boxing |
| Philly Shell | Counter rights, check hooks, flicker jabs | Driving power jabs; lead uppercuts (very high cost, not unavailable — scales with ringcraft) |
| Cross-Arm | Wide hooks, overhand rights, flip jabs | Quick straight jabs and crosses |
| Long Guard | Stiff long jabs, straight rights, pull counters | Short inside hooks, tight uppercuts |
| Low Lead Hand | Up-jabs, unseen lead hooks, pull counters | Sustained blocking-position exchanges |
| Tight Elbow Guard | Short uppercuts, shovel hooks, inside combos | Long straight punching |
| Ear-Muff | Post-storm short counters | Initiating anything while covered |
| Forearm Frame | Free-hand short hooks/uppercuts, pivot exits | Long-range or committed rear-hand power |
| Active Hands | Parry-and-return straights, hand-trap crosses | Fully loaded power shots |

---

## Punch Effectiveness (system-wide baselines)

- **Highest percentage:** the jab (safest, most thrown, sets up everything);
  the cross (most reliable power shot); the lead hook (mid-range finisher from
  outside the eyeline). **Body shots deserve special weighting:** no guard
  covers head and body simultaneously, so body investment pays against nearly
  every defense.
- **Situational:** uppercuts (devastating, but require close range and a
  specific opening; from distance they expose the thrower badly); overhand
  (high risk, high reward).
- **Lowest percentage:** wide haymakers, bolo punches, lead uppercuts from
  range, arm punches thrown from outside reach.

---

## Game Implementation Notes

Guard choice should modify more than damage:

```text
damage_reduction
stamina_cost
visibility
counter_readiness
movement_speed
ring_position_loss
guard_integrity        # degrades under volume; governs alignment states
arm_condition_damage
counter_window_access
offense_launch_cost    # per-punch cost modifier from offense_effective/awkward
```

Examples:

```text
# High Guard
strong_head_damage_reduction
moderate_arm_condition_damage
weak_body_coverage
moderate_counter_readiness
low_launch_cost_straights / high_launch_cost_body_loops

# Philly Shell
strong_vs_straights
high_counter_readiness
weak_vs_hooks_and_bodywork
requires_high_ringcraft
low_launch_cost_counters / high_launch_cost_power_jab
guard_alignment_state: {roll_timed_aligned, roll_late_or_misaligned}
overhand_intercept: strong when roll_timed_aligned, weak when roll_late_or_misaligned
lead_uppercut_launch_cost: very_high, reduced_by_ringcraft

# Tight Elbow Guard
strong_vs_body_and_uppercut
reduced_head_coverage
strong_inside_survival
reduced_mobility
low_launch_cost_inside_work / high_launch_cost_long_straights

# Cross-Arm
guard_alignment_state: {bar_low_aligned, bar_high_or_split}
uppercut_intercept: strong when bar_low_aligned, weak when bar_high_or_split
```

## Guard Matchup Rules for CPU Logic

CPU fighters reason from observable evidence, not omniscience:

```text
Opponent using high shell repeatedly.
Recent head jabs blocked.
Body lane open.
Uppercut intercept risk depends on elbow position.
Switch to body jab, body hook, feint-to-uppercut, or angle step.
```

```text
Opponent using long guard.
Outside entries failing.
Try overhand over frame, step-inside body hook, or slip past lead hand.
```

```text
Opponent in cross-arm.
Bar currently riding high under my body volume.
Uppercut split window is open; head hooks remain wasted.
```

This makes boxing knowledge functional, not decorative.

---

## Reconciliation Log (deliberate design decisions)

Items 1–3 record disagreements between two source references. Items 4–6 record
contradictions this document produced internally, caught by later review passes.
All resolutions are intentional — do not "fix" them back without a design
discussion.

1. **Cross-arm vs uppercuts.** One source listed uppercuts as a cross-arm
   weakness (split up the middle); another listed the cross-arm as the *best*
   uppercut defense (forearms block the middle channel). Both are true
   conditionally: a low, aligned forearm bar intercepts chin-line uppercuts; a
   bar that rides high or splits under body-volume pressure is opened by them.
   Modeled via a `guard_alignment_state` on the cross-arm guard, which also
   gives CPU logic a readable exploit trigger.
2. **Philly shell vs body shots.** Resolved by splitting the zone: lead-side
   body hooks are a shell *strength* (draped forearm shield); center and
   rear-side body straights remain a shell *weakness*.
3. **Peek-a-boo vs uppercuts.** Kept as "better than an ordinary high guard"
   for uppercuts arriving at the chin lane, while the rear uppercut *timed on
   entry* stays a headline vulnerability — the two are different situations
   (static coverage vs punished movement).
4. **Philly shell vs the overhand.** This document contradicted itself in four
   places: the guard entry called the overhand a shell weakness, the strength
   table called it a shell strength, the punch-selection table recommended it
   *against* the shell, and the best-response table named the shoulder roll a
   best answer *to* it. Resolved the same way as item 1, because it is the same
   kind of fact: a roll that is timed and aligned turns the overhand off the
   shoulder, and a roll that is late or misaligned lets it arc over the
   shoulder line. Formalized as a shell `guard_alignment_state`
   {roll_timed_aligned, roll_late_or_misaligned}, which also delivers the guard
   state the charter already promised. Do not flatten it back to a single
   verdict in either direction.
5. **Philly shell lead uppercut.** An earlier draft treated this as skill-gated;
   the landed text called it "mechanically hard to generate," which reads as
   unavailable. Resolved as expensive rather than absent: a very high
   `offense_launch_cost` that ringcraft reduces. Elite shell fighters do land
   it, so removing the punch outright would fail the coach test, while making
   it cheap would erase the structural cost of carrying the lead hand low.
6. **High Guard "moderate body protection".** Caught by an external review pass,
   2026-08-04. The High Guard summary block asserted `moderate_body_protection`
   as a flat property, which contradicts the model twice over: `collision_model`
   gives `guard_high` only head, jaw and the eyes — the torso belongs to
   `guard_body` — and `pose_geometry` gives high_guard a guard_body extent of
   0.55 against an interception threshold of 0.6, so the body lane is **open**,
   not moderately covered. That opening is load-bearing: it is the whole reason
   "body shots pay off against a high guard" emerges from posture data and one
   threshold instead of being written down as a rule (Rule 4's counterplay
   against passive high blocking). A flat "moderate" line quietly re-hardcodes
   what Decision 0010 made emergent. Resolved by stating the extent and its
   consequence rather than a verdict. If the tucked-elbow reading is wanted —
   that a high guard buys *some* body coverage — the way to get it is to raise
   that posture's guard_body extent in canon and let the threshold decide, not
   to describe coverage the geometry does not produce.

---

## Final Takeaway

Every guard is a trade: protection in one zone is bought by selling another,
and offense economy is part of the price. Elite defense in the sim should
ultimately come from head movement, footwork, and distance — the guard is the
last line, not the whole system. That keeps the core promise intact:

> **Arcade boxing with real boxing bones.**

<!-- Claude Fable 5 (claude-fable-5) - 2026-08-03 05:04 UTC - boxing_guard_matchups.md end -->
