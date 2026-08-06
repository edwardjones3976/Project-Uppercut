<!-- [ OpenAI Director | GPT-5.6 Thinking | 2026-08-06 12:27 PDT | START ] -->

# Decision 0014 — Director rulings on the initial open gates

**Status:** accepted  
**Date:** 2026-08-06  
**Authority:** Director  
**Closes:** G1, G2, G3, G5, G6  
**Ratifies by reference:** Decision 0013 closes G4 separately

## Why this decision exists

The project had gathered enough evidence to expose six blocking choices, but the
Director role failed to convert that evidence into rulings. That was a governance
failure, not an evidence shortage.

The correction is immediate:

> Measurements inform a Director decision. They do not replace one.

The following rulings are authoritative unless a later numbered Decision
explicitly supersedes them.

---

## G1 — Normal-step cost authority

### Ruling

Ordinary boxing movement uses displacement-scaled stamina cost:

```text
movement_stamina_cost = distance_moved_in_reach_units × 0.60
```

A normal `0.22 ru` step therefore costs:

```text
0.22 × 0.60 = 0.132 stamina
```

The flat `0.600` value is **not** the cost of an ordinary 0.22-ru adjustment and
must be removed from the generic step path.

A cost near `0.600` may exist only on a separately named explosive movement action,
such as:

- committed lunge;
- emergency rope escape;
- explosive pivot;
- chase burst.

That action must declare its own distance, commitment, recovery, and cost. Zero
displacement costs zero movement stamina.

### Reason

Distance-scaled locomotion is the reusable physical rule. An animation or move name
must not silently price physiology. The prior 4.55× contradiction made every
footwork-dependent stamina conclusion unstable.

### Required implementation

- Change the generic step path to read the locomotion rate.
- Remove or rename the flat generic-step cost.
- Re-run every stamina, cadence, Phase O, and policy measurement affected by G1.
- Re-bless a golden stream only in the same change that updates the accepted canon.

---

## G2 — Rest and no-action semantics

### Ruling

Thinking and acting are separate. A policy decision does not automatically create a
physical action.

The authoritative action family gains these distinct outcomes:

| Outcome | Meaning | Physical cost | Recovery |
|---|---|---:|---|
| `Observe` | Read the opponent and update intent | none | baseline only |
| `HoldPosition` | Maintain stance and range without purposeful movement | negligible or none | baseline only |
| `Rest` | Deliberately lower output and recover | none beyond posture hold | authored recovery benefit |
| `MicroAdjust` | Small balance/range correction | displacement-scaled | baseline only |
| `Move` | Purposeful authored step | displacement-scaled | normal |
| `Guard` | Maintain a declared defensive structure | posture hold cost | normal |
| `Evade` | Commit to an active or positional answer | authored action cost | normal |
| `Attack` | Commit to an authored strike | authored action cost | normal |

`Rest` is not a free invulnerability state. It yields initiative, may concede ring
position, and may be interrupted. `Observe` is not guaranteed recovery beyond the
normal baseline. `MicroAdjust` must use actual displacement rather than a full-step
charge.

### Reason

The project had modeled frequent thought as frequent expenditure. A boxer can watch,
wait, breathe, threaten, and hold space without taking a full stamina-charging action
on every policy tick.

### Required implementation

- Add the new outcomes to the policy contract and C++ action state.
- Separate decision frequency from physical action frequency.
- Emit reason codes for no-action choices.
- Re-run stamina equilibrium and work-rate evidence after the change.

---

## G3 — `aggression_bias` semantics

### Ruling

`aggression_bias` means:

> The fighter's tendency to seek offensive initiative when a plausible opportunity
> exists.

It does **not** mean:

> The probability that every decision tick immediately becomes a punch.

The CPU policy must use a staged process:

```text
observe state
→ select broad intent
→ test for a legal and tactically useful opportunity
→ choose a physical action or continue observing
→ commit
```

An offensive action still requires:

- legal range;
- an available hand;
- acceptable commitment and recovery risk;
- sufficient stamina;
- a visible target lane;
- positional value;
- repetition awareness;
- compatibility with the fighter's current plan and condition.

High aggression should appear through pressure, exit control, feints, jabs, body
investment, purposeful volume, and willingness to exchange. It must not appear as an
impossible punch count.

### Reason

Aggression is strategic appetite, not a second action clock. The previous direct
interpretation produced work rates several times above the intended boxing band and
made style conclusions meaningless.

### Required implementation

- Refactor policy into strategic, tactical, and execution layers.
- Preserve reaction time as a separate concept from decision frequency and attack
  appetite.
- Emit a readable reason code for every committed or deferred action.
- Quarantine roster/style balance conclusions until the corrected policy runs in C++.

---

## G5 — Default ruleset

### Ruling

The default ruleset is:

# Project Uppercut Professional Rules v1

It uses:

- mandatory knockdown count;
- no generic standing eight count;
- no automatic three-knockdown stoppage;
- no saved-by-the-bell rescue;
- referee and medical stoppages from observable evidence;
- disclosed round count, clock mode, referee profile, and event modifiers;
- sealed scoring until the permitted reveal;
- universal medical and incapacitation minimums that presentation cannot override.

The game may also offer an explicit optional modifier:

# Project Uppercut Arcade Three-Knockdown Rule

That modifier must be disclosed before the bout and written into the replay/event
record. It may be used for exhibitions, special events, or faster arcade formats. It
is not the silent default.

A twenty-second out-of-ring count is reserved for the phase in which ring-out
behavior exists. It must not be simulated before an authoritative ring-out state is
implemented.

### Reason

The prior three-knockdown termination rule was an undeclared assumption. Project
Uppercut may use arcade rules deliberately, but it must not present them as universal
professional boxing truth.

### Required implementation

- Version the ruleset in every bout and replay.
- Remove the silent three-knockdown default from the professional path.
- Re-run stoppage and decision-path evidence under Professional Rules v1.
- Preserve the arcade rule as an explicit selectable modifier.

---

## G6 — Guard values on the interception threshold

### Ruling

The current interception threshold remains `0.60` for the simplified two-lane model.
No authored guard may sit exactly on that threshold unless a future Decision names the
knife-edge behavior as intentional.

Set:

```text
philly_shell.guard_body = 0.55
active_hands.guard_high = 0.65
```

These values fix the intended semantics:

- Philly shell body coverage sits on the **exposed** side. Bodywork remains a clear
  answer to the shell.
- Active Hands head coverage sits on the **protected** side when fresh. It can still
  fail under feints, layered combinations, overload, alignment loss, and condition.

The numbers remain tuning hypotheses, but their side of the threshold is now an
authoritative design decision. Future tuning may move them while preserving that
relationship unless a later Decision says otherwise.

### Reason

A value exactly equal to the threshold creates accidental first-damage behavior and
floating-point fragility. Neither posture's identity called for that knife edge.

### Required implementation

- Update `data/guard_evasion_model.json`.
- Add a validator that rejects extents exactly equal to the interception threshold
  unless explicitly allow-listed by a numbered Decision.
- Re-run guard validators and any dependent evidence.

---

## Director sequencing after these rulings

The next authorized order is:

1. implement G1, G2, G3, and G6;
2. port and integrate the accepted range, evasion, and policy behavior into one
   shared C++ runtime;
3. re-run Phase O under Professional Rules v1;
4. create the Play-ready Unreal development arena;
5. complete one generic CPU bout through stoppage and decision paths;
6. add one thin proof of impact, crowd, commentary, humor, silence, and replay;
7. implement Decision 0013 lateral geometry before the named-fighter vertical slice;
8. begin Adewale versus Calvin only after the generic gate passes.

## Governance correction

When evidence presents a bounded choice and the Director has enough information to
understand the trade:

- the Director decides;
- the decision is recorded in the same working cycle;
- implementation and verification become engineering work;
- more measurement is authorized only when it could realistically change the ruling.

“Director call” is not a storage category. It is an obligation.

<!-- [ OpenAI Director | GPT-5.6 Thinking | 2026-08-06 12:27 PDT | END ] -->
