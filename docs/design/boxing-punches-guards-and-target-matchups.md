# Project Uppercut — Boxing Punches, Target Zones, Angles, and Guard Matchups

**Status:** Developer-side design reference  
**Rules context:** Modern gloved boxing descended from the Marquess of Queensberry rules  
**Purpose:** Support strike data, guard interception, CPU reasoning, Training Mode, commentary, telemetry, and balance tests  

> **A punch's intended landing zone is not necessarily the guard plane that intercepts it.**

This document provides a boxing-informed vocabulary for Project Uppercut. It is not a claim that one punch or guard always defeats another. Effectiveness depends on range, stance relationship, timing, setup, angle, posture, movement, fatigue, guard integrity, contact quality, and the fighter's attributes.

The original Queensberry rules established the broad form of modern gloved stand-up boxing. Current commissions and sanctioning bodies provide the detailed legal target and foul rules used today. For Project Uppercut, legal punches use the knuckle surface of a closed glove and target the front or sides of the opponent above the belt. The back of the head or neck, kidneys, spine, groin, and an opponent who is down are not legal targets.

## 1. Required strike-model separation

Every strike definition should separate at least:

```yaml
strike_family: jab | straight | hook | uppercut | overhand | shovel_hook
lead_or_rear: lead | rear
level: head | body
intended_target_region: jaw | temple | cheek | nose | forehead | sternum | solar_plexus | liver | ribs | guard_arm
trajectory: linear | horizontal_arc | rising_arc | descending_arc | diagonal_rising_arc
entry_angle: center | inside | outside | over | under
primary_intercept_plane: high_center | high_side | mid_center | mid_side | low_center | low_side | extended_frame
secondary_intercept_planes: []
range_band: outside | long | mid | close | inside
startup: prototype_value
active_contact: prototype_value
recovery: prototype_value
stamina_cost: prototype_value
counter_exposure: prototype_value
```

`intended_target_region` describes where the punch seeks to land. `primary_intercept_plane` describes where an effective guard usually meets its path.

Example:

```yaml
strike_family: uppercut
level: head
intended_target_region: jaw
trajectory: rising_arc
primary_intercept_plane: low_center
secondary_intercept_planes:
  - mid_center
```

An uppercut may finish at the jaw while being stopped lower by a dropped forearm, elbow frame, or compact centerline structure.

---

# 2. Core punch catalog

## 2.1 Lead jab

**Path:** Fast linear lead-hand strike.  
**Typical angles:** Centerline, slight outside step, upward jab, downward jab, body jab.  
**Primary uses:** Measure distance, interrupt, score, obscure vision, establish rhythm, force guard reactions, prepare combinations.

### Common legal targets

- Nose and center face
- Forehead when posture or height creates that line
- Jaw or cheek from an angle
- Sternum or upper abdomen with a body jab
- Guard gloves or forearms to occupy or disrupt them

### More effective when

- Used at long range
- Timed during an opponent's entry
- Doubled or varied in rhythm
- Paired with an outside step or angle change
- Used to expose the body or rear-hand lane

### Less effective when

- Repeated at one rhythm without variation
- Thrown from hook range with no frame or exit
- Sent directly into an established high-center guard
- Overextended against a prepared slip-and-counter fighter

### Strong guard answers

- High guard catch
- Long-guard interception
- Active-hand parry
- Rear-hand catch
- Slip with responsible rear-hand protection

### Guard structures the jab can challenge

- Low lead-hand guards
- Loose shoulder-roll positions before the shoulder is set
- Static guards when the jab is used to blind, occupy, or redirect rather than force damage

---

## 2.2 Rear straight / cross

**Path:** Linear rear-hand power strike through the center or an angle created by foot position.  
**Typical angles:** Centerline, outside-angle cross, split-guard straight, straight to body.

### Common legal targets

- Jaw and chin
- Nose and center face
- Cheek
- Sternum and solar plexus
- Ribs when stance and angle permit

### More effective when

- Set up by the jab, feint, or lead-hand control
- Thrown after gaining outside foot position in open-stance matchups
- Timed against a returning jab
- Delivered into an opponent moving toward it
- Used after the guard has been displaced

### Less effective when

- Thrown naked from too far away
- Repeated into a settled shoulder roll
- Used at cramped inside range
- Overcommitted against lateral movement

### Strong guard answers

- High-center guard
- Rear-hand catch or parry
- Shoulder roll when aligned correctly
- Cross-arm structure
- Step-back or outside slip

### Guard structures the cross can challenge

- Open or low guards
- Long guards after the lead frame has been cleared
- Guards displaced by a jab, hook, or hand trap

---

## 2.3 Lead hook

**Path:** Horizontal or slightly rising arc from the lead side.  
**Typical angles:** Head hook, body hook, check hook, pivot hook, short inside hook.

### Common legal targets

- Jaw and cheek
- Temple and side of head
- Liver region from the orthodox lead side against an orthodox opponent
- Ribs and side of torso
- Guard arm when deliberately damaging or moving the shell

### More effective when

- The opponent is focused on centerline straights
- Thrown after a jab or rear straight shifts the guard
- Used as a check hook against forward pressure
- Delivered from an outside angle
- Mixed between head and body

### Less effective when

- Thrown from outside its range
- Looped widely without setup
- Sent repeatedly into a tight ear-muff guard
- Used while square and unable to recover position

### Strong guard answers

- High-side glove and forearm
- Ear-muff cover
- Peek-a-boo shell
- Cross-arm guard
- Roll-under or step-away when timed

### Guard structures the lead hook can challenge

- Philly shell, especially around or above the lead shoulder
- Long guard after entering past the extended arm
- Tight-elbow body guard when directed high

---

## 2.4 Rear hook

**Path:** Horizontal rear-side arc, usually from mid or close range.  
**Typical angles:** Rear head hook, rear body hook, hook after pivot or stance shift.

### Common legal targets

- Jaw and opposite cheek
- Temple and side of head
- Ribs and side of torso
- Guard arm

### More effective when

- The opponent has rotated toward the rear side
- A lead hook, jab, or body shot has shifted the guard
- Used at close range after entering safely
- Thrown during a stance-switch sequence with stable balance

### Less effective when

- Thrown from long range
- Loaded visibly
- Used while the fighter's feet are crossed or square
- Repeated against a compact side-covering shell

### Strong guard answers

- High-side guard
- Cross-arm guard
- Ear-muff cover
- Roll-under or angle exit

### Guard structures the rear hook can challenge

- Open guards
- Long guards once the range has collapsed
- Tight body guards when directed high

---

## 2.5 Lead uppercut

**Path:** Short rising arc from the lead side, usually close or inside.  
**Typical angles:** Center uppercut, slight outside-angle uppercut, body-to-head uppercut.

### Common legal targets

- Jaw and chin
- Center face at close range
- Solar plexus or upper abdomen when aimed to the body

### More effective when

- The opponent uses a high shell with lifted elbows
- The opponent leans forward or enters upright
- Set up by body hooks, jabs, or a frame
- Thrown inside a wide hook
- Used after a slip creates a short center lane

### Less effective when

- Thrown from long range
- Used against a compact guard with elbows and forearms protecting the center
- Telegraphed by a deep dip
- Thrown while the opponent is already exiting laterally

### Strong guard answers

- Dropped forearm
- Tight-elbow or compact mid/low-center guard
- Peek-a-boo structure with elbows connected
- Step-back
- Short framing hand or jab interruption before launch

### Guard structures the uppercut can challenge

- Loose high guard
- Ear-muff guard held too high
- Cross-arm guard when the center gap opens
- Upright passive shell

> **Modeling rule:** The head uppercut targets the jaw but is principally intercepted at the low or mid centerline because its path rises into the target.

---

## 2.6 Rear uppercut

**Path:** More powerful rising rear-hand arc, generally from close range.  
**Typical angles:** Center rear uppercut, rear uppercut after slip, rear uppercut to body.

### Common legal targets

- Jaw and chin
- Center face
- Solar plexus and upper abdomen

### More effective when

- The opponent shells high or bends forward
- Timed after a slip inside the jab or cross
- Used after lead-hand framing or body work
- The opponent's elbows separate during combinations

### Less effective when

- Launched from outside range
- Overcommitted against a step-back
- Used against tight centerline forearm and elbow structure
- Thrown without protecting against the counter hook

### Strong guard answers

- Tight-elbow guard
- Dropped forearm or compact center block
- Step-back
- Angle exit
- Early jab or short hook interruption

### Guard structures the rear uppercut can challenge

- Loose high guard
- Elevated ear-muff guard
- Static cross-arm structure with an exposed center seam

---

## 2.7 Overhand

**Path:** Descending arc over an opponent's lead hand or guard line.  
**Typical angles:** Rear overhand over the jab, overhand from outside angle, looping lead overhand.

### Common legal targets

- Temple and side of head
- Jaw and cheek
- Forehead when the opponent ducks or changes level

### More effective when

- Timed over a jab or extended long guard
- Used against a low lead hand
- Thrown from an outside angle
- The opponent's head remains on the centerline

### Less effective when

- Thrown without setup
- Used against a compact high-side guard
- Repeated predictably
- Attempted from crowded inside range

### Strong guard answers

- High-side guard
- Ear-muff cover
- Cross-arm guard
- Step under, roll, or angle exit

### Guard structures the overhand can challenge

- Long guard
- Low lead-hand guard
- Shoulder roll when the arc clears the shoulder alignment

---

## 2.8 Shovel hook

**Path:** Diagonal rising arc between a hook and uppercut.  
**Typical angles:** Lead shovel hook to liver or solar plexus, rear shovel hook to body, diagonal head shot at close range.

### Common legal targets

- Liver region
- Solar plexus
- Ribs
- Jaw at close range when the line rises high enough

### More effective when

- Thrown under a high elbow
- Mixed with head hooks or uppercuts
- Used after the opponent braces for a straight
- Delivered from a small outside angle

### Less effective when

- Thrown from too far away
- Sent into a compact elbow shield
- Repeated without head-level variation
- Used while standing square with no exit

### Strong guard answers

- Tight-elbow body guard
- Dropped elbow and forearm wedge
- Pivot away from the striking side
- Step-back when range allows

### Guard structures the shovel hook can challenge

- Loose high guard
- Long guard with exposed ribs
- Ear-muff shell with elevated elbows

---

## 2.9 Body jab and body straight

These are level variants of the jab and cross rather than separate punch families, but they require their own tactical treatment.

### Common legal targets

- Sternum
- Solar plexus
- Upper abdomen
- Front-side ribs when the angle is legal

### More effective when

- The opponent holds a high static guard
- Used to alter level and prepare head attacks
- Timed during a reset or upright posture
- Thrown with an exit so the head is not left exposed

### Less effective when

- The attacker bends excessively and loses vision
- Repeated at one rhythm
- Used from too close to recover safely
- Directed below the legal belt line

### Strong guard answers

- Tight-elbow guard
- Elbow drop
- Active downward parry
- Step-back or pivot

---

# 3. Legal body-region effectiveness matrix

The following is a game-design effectiveness guide, not a medical prediction table. Effectiveness is contextual and should be produced by contact quality, force, angle, movement, accumulated condition, and defensive state rather than a flat target multiplier alone.

| Legal target region | Punches commonly effective | Punches commonly less efficient | Intended gameplay consequence |
|---|---|---|---|
| Jaw / chin | Straight, cross, hook, uppercut, shovel hook | Long body-focused shots, poorly ranged overhand | Balance disruption, knockdown risk, jaw condition |
| Temple / side of head | Lead/rear hook, overhand, angle cross | Centerline body shots, short uppercut without angle | Head condition, tracking/composure pressure |
| Nose / center face | Jab, straight, short uppercut | Wide hook from wrong range | Accuracy disruption, visible damage, head condition |
| Forehead / upper guard line | Jab, straight, overhand when posture creates line | Uppercut from excessive range | Usually reduced clean effect; may damage attacking hand/guard in deeper simulation |
| Cheek / side face | Hook, cross from angle, overhand | Body jab | Head condition, side-specific facial damage |
| Sternum | Body jab, straight to body | Wide head hook | Posture and breathing pressure, body condition |
| Solar plexus | Straight to body, rear uppercut to body, shovel hook | Long looping head punch | Stamina interruption, body condition, temporary recovery delay |
| Liver-side body | Lead body hook or shovel hook from orthodox-vs-orthodox geometry; mirrored by stance relationship | Straight head jab | Strong body-condition and stamina consequence when clean |
| Ribs / side torso | Body hooks, shovel hooks | Centerline uppercut without angle | Body condition, movement and breathing pressure |
| Guard arms / forearms | Varied hooks and straights deliberately working the guard | Repeating one weak safe strike | Arm condition, guard integrity, positional pressure |

## Target-model safeguards

- No region produces an automatic knockout.
- Chin or temple contact may create high consequence only when force, placement, movement, balance, awareness, accumulated condition, and defense support it.
- Body targets should influence stamina and posture without becoming guaranteed stun buttons.
- The liver-side designation must follow fighter orientation and stance, not a fixed screen-left rule.
- Contact to guard arms is not a clean scoring punch to the target beneath it, but can create arm-condition and guard-integrity consequences.
- Legal target logic must reject back-of-head, neck, spine, kidney, groin, below-belt, and downed-opponent contacts.

---

# 4. Guard catalog

## 4.1 Conventional high guard / basic shell

**Structure:** Gloves high near cheeks and temples; forearms protect center; elbows provide partial body coverage.

**Best against:**

- Head jab
- Rear straight / cross
- Head hooks when the side glove and forearm are positioned correctly
- Overhands when the shell remains compact

**More vulnerable to:**

- Body jab and body straight
- Body hooks and shovel hooks when elbows rise
- Uppercuts through a loose center
- Angle changes that turn the shell

**Tradeoffs:** Reliable and teachable; can become passive; absorbs arm and guard damage; may reduce vision.

---

## 4.2 Peek-a-boo guard

**Structure:** Compact high hands, tucked elbows, hidden chin, active slips, weaves, and explosive entries.

**Best against:**

- Jabs and crosses when combined with head movement
- Hooks to head
- Uppercuts when elbows remain connected
- Short combinations at close range

**More vulnerable to:**

- Check hooks against predictable entries
- Long body jabs
- Angled body hooks when elbows lift
- Opponents who force repeated entries and exits

**Tradeoffs:** Strong compact coverage and counter entry; demanding on stamina, movement, timing, and CPU discipline.

---

## 4.3 Shoulder roll / Philly shell

**Structure:** Lead shoulder shields chin, rear hand covers opposite side, lead hand rests lower for parries and body coverage.

**Best against:**

- Rear straight / cross
- Predictable jabs
- Committed single centerline punches
- Shots that can be rolled into glancing contact

**More vulnerable to:**

- Lead hook around the shoulder
- Body combinations
- Overhands clearing the shoulder line
- Open-stance rear straights and changed angles
- Layered combinations that prevent a single clean roll

**Tradeoffs:** High counter readiness and efficiency; high Ringcraft requirement; orientation-sensitive rather than universally strong.

---

## 4.4 Cross-arm guard

**Structure:** Forearms cross before the face and upper torso to create a dense impact barrier.

**Best against:**

- Head hooks
- Overhands
- Straight head shots
- Short flurries

**More vulnerable to:**

- Body hooks and shovel hooks
- Uppercuts through an opened center seam
- Sustained work to arms and guard integrity
- Reduced visibility and slower immediate counters

**Tradeoffs:** Strong absorption and durability expression; limits offense, visibility, and rapid counter selection.

---

## 4.5 Long guard

**Structure:** Lead arm extends to measure, frame, blind, occupy, or intercept while the rear hand protects.

**Best against:**

- Jabs
- Straight-line entries
- Rushes from outside range
- Hooks launched from too far away

**More vulnerable to:**

- Overhands over the lead frame
- Body attacks beneath the extended arm
- Inside hooks after the frame is cleared
- Timing attacks against the returning lead hand

**Tradeoffs:** Excellent range management; deteriorates sharply if the opponent establishes inside position.

---

## 4.6 Low lead-hand / bait guard

**Structure:** Lead hand carried low for vision, rhythm, baiting, parrying, and counter launching.

**Best against:**

- Predictable jabs
- Lunging single shots
- Slow entries
- Overcommitted straights that can be pulled or slipped

**More vulnerable to:**

- Fast jabs
- Lead hooks
- Overhands
- Rapid layered combinations

**Tradeoffs:** High counter potential and visual freedom; substantial exposure; should require timing, awareness, reflex, and composure rather than grant passive evasion.

---

## 4.7 Tight-elbow / body guard

**Structure:** Elbows connected to ribs and centerline; forearms positioned to intercept body attacks and rising punches.

**Best against:**

- Body hooks
- Body jab and straight
- Uppercuts intercepted on their rising path
- Inside body combinations

**More vulnerable to:**

- High hooks
- Overhands
- Head jabs and straights when the hands settle too low
- Angles that turn the compact structure

**Tradeoffs:** Strong body and centerline protection; may sacrifice head coverage, mobility, and offensive freedom.

---

## 4.8 Ear-muff / double-forearm cover

**Structure:** Gloves and forearms press tightly around the sides and front of the head, commonly used to survive a burst.

**Best against:**

- Head hooks
- Overhands
- Wild head combinations
- Emergency flurry survival

**More vulnerable to:**

- Body jab and straight
- Body hooks
- Uppercuts under an elevated cover
- Ring-position loss and passive guard pressure

**Tradeoffs:** Strong emergency head protection; low visibility and counter readiness; should not become an indefinite safe state.

---

## 4.9 Forearm frame

**Structure:** One or both forearms actively frame the opponent's shoulder, head line, or entry path rather than forming a static shell.

**Best against:**

- Inside hooks
- Forward entries
- Clinch attempts
- Short flurries that require shoulder rotation

**More vulnerable to:**

- Body hooks beneath the frame
- Overhands around it
- Uppercuts underneath
- Step-around attacks

**Tradeoffs:** Strong space-management tool; not a universal block; position and referee tolerance matter.

---

## 4.10 Active-hands / open guard

**Structure:** Mobile hands parry, catch, touch, occupy, and disrupt rather than remaining fixed.

**Best against:**

- Jabs
- Straights
- Predictable single shots
- Measured entries

**More vulnerable to:**

- Feints that draw false reactions
- Hooks around centerline parries
- Layered combinations
- Body attacks during high hand activity

**Tradeoffs:** Flexible and counter-ready; cognition-heavy; can fail dramatically against feints and volume.

---

# 5. Punch-to-guard matchup matrix

`Strong` means the guard naturally occupies or controls the punch's common path. `Conditional` means timing, compactness, angle, and stance determine the result. `Weak` means the punch naturally attacks an exposed lane, not that it automatically lands.

| Incoming punch | Strong guard answers | Conditional answers | Guards commonly challenged |
|---|---|---|---|
| Head jab | High guard, long guard, active hands | Peek-a-boo, shoulder roll | Low lead-hand guard, loose open guard |
| Rear straight / cross | High guard, shoulder roll, cross-arm | Active hands, peek-a-boo | Low/open guard, displaced long guard |
| Lead head hook | High-side guard, ear-muff, peek-a-boo | Cross-arm, roll-under | Shoulder roll, long guard after entry |
| Rear head hook | High-side guard, ear-muff, cross-arm | Peek-a-boo, angle exit | Long guard at collapsed range, low guard |
| Lead uppercut | Tight-elbow guard, dropped forearm, compact peek-a-boo | Cross-arm with closed center | Loose high guard, elevated ear-muff |
| Rear uppercut | Tight-elbow guard, compact center forearms, step-back | Peek-a-boo, cross-arm | Loose high shell, static high cover |
| Body jab / straight | Tight-elbow guard, downward parry | High guard with timely elbow drop | Ear-muff, high shell with floating elbows |
| Lead body hook | Tight-elbow guard, compact peek-a-boo | Cross-arm when lowered correctly | Long guard, elevated high guard |
| Rear body hook | Tight-elbow guard, compact body shell | Cross-arm, pivot exit | Long guard, low lead-hand stance with open rear ribs |
| Overhand | High-side guard, ear-muff, cross-arm | Roll-under, angle exit | Long guard, low lead hand, misaligned shoulder roll |
| Shovel hook | Tight-elbow guard, forearm wedge | Step-back, pivot | Loose high guard, long guard, elevated ear-muff |
| Multi-angle flurry | Peek-a-boo, cross-arm, temporary ear-muff | High guard with active exits | Low guard, active hands overwhelmed by volume |

---

# 6. Guard-to-punch tactical summary

| Defender's guard | Punches usually less efficient against it | Punches and setups commonly more effective against it |
|---|---|---|
| Conventional high guard | Naked head jab, straight into settled gloves, predictable head hook | Body jab, body straight, body hook, shovel hook, uppercut through loose center, angle changes |
| Peek-a-boo | Predictable single jabs/crosses, unprepared head hooks | Check hook, long body jab, entry uppercut, lateral exits, feint-and-angle sequences |
| Shoulder roll | Naked rear cross, predictable jab-cross, single centerline power | Lead hook, body work, overhand, open-stance rear straight, multi-angle combinations |
| Cross-arm | Single head hook, slow overhand, simple straight | Body hooks, shovel hooks, uppercut through seam, sustained arm/guard work |
| Long guard | Long straight launched on same line, outside hooks | Overhand, body entry, slip-inside hook, step-around attack |
| Low lead hand | Slow lunging single shots it can bait | Fast jab, double jab, lead hook, overhand, layered combination |
| Tight-elbow guard | Repeated body hooks, obvious body uppercuts | High jab, high hook, overhand, angle changes |
| Ear-muff | Wild head hooks and overhands into cover | Body jab, body hook, uppercut under cover, ring-pressure sequences |
| Forearm frame | Smothered short hooks thrown into the frame | Body hook, step-around hook, overhand around frame, uppercut underneath |
| Active hands | Predictable single jab or cross | Feint-to-hook, layered combinations, body attacks, rhythm changes |

---

# 7. CPU decision examples

```yaml
observation:
  opponent_guard: conventional_high
  recent_head_jabs_blocked: 4
  opponent_elbows: elevated
  range: mid
candidate_adjustments:
  - increase: body_jab
  - increase: lead_body_hook
  - increase: feint_to_uppercut
  - decrease: naked_head_jab
reason: high shell protects head center but exposes body and rising centerline when loose
```

```yaml
observation:
  opponent_guard: long_guard
  outside_entries_stopped: 3
  opponent_lead_arm_extended: true
candidate_adjustments:
  - increase: overhand_over_frame
  - increase: slip_inside_body_hook
  - increase: step_around_lead_side
  - decrease: long_straight_same_line
reason: extended frame controls linear entry but exposes over, under, and inside routes
```

```yaml
observation:
  opponent_guard: tight_elbow
  body_hooks_blocked: 5
  head_side_coverage: reduced
candidate_adjustments:
  - increase: lead_head_hook
  - increase: overhand
  - increase: high_jab_to_angle
  - decrease: repeated_body_hook
reason: compact body protection concedes some high-line access
```

CPU logic must use observable guard posture, recent outcomes, range, stance, and pattern evidence. It must not receive hidden knowledge that a human player could not infer.

---

# 8. Training Mode applications

Recommended modules:

1. **Target versus intercept plane** — stop an uppercut low even though it targets the jaw.
2. **Opening a high shell** — use level changes and body work rather than repeating head shots.
3. **Beating the long guard** — attack over, under, or around the frame.
4. **Shoulder-roll orientation** — understand why stance relationship and angle matter.
5. **Guard transitions** — move between high, tight-elbow, active-hands, and emergency cover without changing the unified combat rules.
6. **Punch selection by range** — prevent long-range uppercuts and outside hooks from behaving like magnetic attacks.
7. **Combination layering** — use one punch to move the guard and the next to attack the exposed lane.
8. **Defense is not immunity** — demonstrate arm condition, guard fatigue, position loss, and counter opportunities.

---

# 9. Validation requirements

The validator should reject or flag:

- a head uppercut whose only intercept plane is `high_center`;
- a body hook with no side-body trajectory or legal target;
- an overhand classified as a purely linear strike;
- a legal strike targeting back of head, neck, spine, kidney, groin, or below belt;
- a guard that provides strong coverage against every punch family;
- a punch with no startup, active contact, recovery, range, stamina, guard interaction, or counter exposure;
- a guard matchup expressed as guaranteed success rather than contextual effectiveness;
- a fixed left/right liver target that ignores stance and orientation;
- blocked glove/forearm contact scored as clean contact to the protected target;
- punch effectiveness determined by target region alone without trajectory and intercept-plane logic.

Recommended invariant:

> **No punch is universally effective, no guard is universally complete, and every authored advantage creates an observable lane, cost, or counter opportunity.**

---

# 10. Sources and scope notes

This document distinguishes the historical Queensberry framework from modern detailed competition rules. The original Queensberry code established gloved stand-up boxing, timed rounds, knockdown counts, and prohibitions on wrestling. Modern commission and amateur rulebooks define detailed fouls and legal conduct.

Primary and official references consulted:

- USA Boxing, **2026 USA Boxing Rule Book** and official rulebook page: https://www.usaboxing.org/usa-boxing-rulebook
- Ohio Administrative Code, **Rule 3773-2-02**, adopting Association of Boxing Commissions uniform championship rules and listing modern boxing fouls: https://codes.ohio.gov/ohio-administrative-code/rule-3773-2-02

Historical reference:

- Public-domain text of the **Marquess of Queensberry Rules**: https://en.wikisource.org/wiki/Marquess_of_Queensberry_rules

The punch-versus-guard effectiveness tables are Project Uppercut design guidance grounded in common boxing mechanics. They must be validated through boxing-expert review, animation/collision testing, CPU simulation, player testing, and telemetry before numerical tuning is treated as final.
