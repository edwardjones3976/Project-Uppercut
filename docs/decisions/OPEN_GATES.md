<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 19:00 UTC | START ] -->

# Open decision gates

One place where every decision that is blocking work is listed with an owner and
a closure state. A decision packet is evidence; a gate is a thing that can be
*closed*. A closed decision gate may leave implementation work, but it may no
longer be used as a reason to postpone choosing a direction.

**Rules for this file.** A gate is added when work stops on a Director call. It is
closed only by a Decision record in `docs/decisions/`, and closing it means
editing the row to `CLOSED` with a decision number — never deleting it.

## Status

| # | Gate | Blocks | State | Authority |
|---|---|---|---|---|
| G1 | **Normal-step cost authority** | stamina economy and every footwork-dependent result | **CLOSED** | Decision 0014: displacement-scaled `0.60/ru`; normal 0.22-ru step = `0.132` |
| G2 | **Rest / no-action semantics** | action cadence and stamina equilibrium | **CLOSED** | Decision 0014: `Observe`, `HoldPosition`, `Rest`, and `MicroAdjust` are distinct authoritative outcomes |
| G3 | **`aggression_bias` semantics** | CPU policy and style analysis | **CLOSED** | Decision 0014: offensive-initiative tendency after opportunity filtering, not per-tick throw probability |
| G4 | **Lateral guard geometry with simple controls** | hooks and side-specific exposure | **CLOSED** | Decision 0013, ratified by Decision 0014: lateral model, discrete controller, sequenced after live generic bout integration |
| G5 | **Declare the default ruleset** | valid stoppage and decision-path interpretation | **CLOSED** | Decision 0014: Project Uppercut Professional Rules v1; no automatic three-knockdown default; optional disclosed arcade modifier |
| G6 | **Guard lanes authored exactly on the interception threshold** | stable guard semantics | **CLOSED** | Decision 0014: Philly shell body `0.55`; Active Hands head `0.65`; exact-threshold values prohibited without explicit decision |

## Implementation obligations created by closure

Closing these gates does not claim the engineering work is complete. It removes
ambiguity so the work can proceed.

### G1 implementation

- remove the flat generic-step charge;
- use actual displacement multiplied by `0.60/ru`;
- reserve higher costs for separately named explosive movement;
- re-run affected stamina and Phase O evidence.

### G2 implementation

- add first-class no-action outcomes to policy and C++;
- separate decision frequency from physical-action frequency;
- preserve observable risk for Rest and positional cost for passivity.

### G3 implementation

- split CPU reasoning into strategic, tactical, and execution layers;
- filter offensive opportunities before selecting a punch;
- emit reason codes;
- keep style-balance conclusions quarantined until the corrected policy runs in C++.

### G4 implementation

- finish per-hand behavior and live policy first;
- complete the generic live bout;
- then implement lateral geometry as a new frozen phase before named fighters.

### G5 implementation

- version the ruleset in every bout and replay;
- remove the silent three-knockdown default from the professional path;
- retain an explicit selectable arcade modifier;
- re-run stoppage and decision-path evidence.

### G6 implementation

- update `data/guard_evasion_model.json`;
- add an exact-threshold validator;
- re-run guard and dependent validation.

## Closed gates

All six initial Director gates were closed on 2026-08-06 by Decisions 0013 and
0014.

Future implementation defects should be tracked as engineering issues. They must
not be reopened as undecided product questions unless new evidence directly
contradicts the accepted rulings.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 19:00 UTC | END ] -->

<!-- [ OpenAI Director | GPT-5.6 Thinking | 2026-08-06 12:27 PDT | closure update ] -->
