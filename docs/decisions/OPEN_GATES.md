<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 19:00 UTC | START ] -->

# Open decision gates

One place where every decision that is blocking work is listed with an owner and
a closure state. A decision packet is evidence; a gate is a thing that can be
*closed*. Without this file the packets live in the document forest and a reader
has to reconstruct which of them are still waiting.

**Rules for this file.** A gate is added when work stops on a Director call. It is
closed only by a Decision record in `docs/decisions/`, and closing it means
editing the row to `CLOSED` with the decision number — never deleting the row.
`tests/test_decision_state_drift.py` already fails when a document reads a
decided thing as open; this file is the inverse and needs the same care.

## Status

| # | Gate | Blocks | State | Evidence |
|---|---|---|---|---|
| G1 | **Normal-step cost authority** — `movement_model.locomotion` says 0.132 per step; the move table says 0.600 flat, 4.55× apart, core reads the higher | the whole stamina economy, and every Phase Q/R/S number downstream of footwork | **OPEN** | packet §Item 1 |
| G2 | **Rest / no-action semantics** — nothing in canon authors doing nothing; four of six non-offensive choices charge stamina | action count, which is the stamina economy's actual problem | **OPEN** | packet §Item 3 |
| G3 | **`aggression_bias` semantics** — intent, attempt, or throw probability; as read today it produces 175–219 punches per fighter-round against a professional 55–78 | CPU policy, and any style balance conclusion | **OPEN** | packet §Item 2 |
| G4 | **Decision 0013 ratification** — lateral guard geometry in the model, discrete controls at the controller | hooks and side-specific exposure; the ten-guards drift | **PROPOSED, awaiting ratification** | `docs/decisions/0013-*.md` |
| G5 | **Declare the default ruleset** — the three-knockdown rule is currently canon and is the termination condition in every measurement | what "a bout ended correctly" means; every stoppage figure quoted this week | **OPEN** | see below |
| G6 | **Guard lanes authored exactly on the interception threshold** — `philly_shell` body and `active_hands` head both sit at 0.60 | two of ten guards open on the first point of arm damage | **OPEN, and a fix rather than a judgement** | `2026-08-05-ten-guards-two-volumes-four-behaviours.md` |

The packet for G1–G3 is
`docs/plans/2026-08-05-three-canon-quantities-decision-packet.md`, with three
options and a consequence for each. Recommended order there: **G1, then G2, then
G3** — G1 is a contradiction rather than a judgement, and G2 and G3 interact, so
deciding G3 first risks deciding it twice.

## G5, stated properly, because it was raised from outside

An external review observed that the Association of Boxing Commissions' Unified
Rules contain no three-knockdown rule. **Checked against the ABC's own published
Unified Rules of Boxing, and it is correct** — the text is explicit rather than
merely silent:

- Rule 8: *"There is NO Three (3) Knockdown Rule."*
- Rule 5: the mandatory eight count after knockdowns is standard in all bouts.
- Rule 7: *"There is NO Standing Eight (8) Count."*
- Rule 10: a boxer who has been knocked down cannot be saved by the bell in any
  round.
- Rule 9: a twenty-second count if a boxer is knocked out of the ring.

This repository treats a three-knockdown stoppage as canon and uses it as the
termination condition in every measurement taken this week. Canon also authors
`max_per_bout: 4`, which has no counterpart in the unified rules either.

That is not automatically wrong — an arcade boxing game may choose the rule
deliberately, and this one is comedy-first with real boxing bones. The gap is
that it is currently an *assumption* rather than a *declaration*. Three ways out:

1. **Declare it.** Name the default ruleset as the project's own, with the
   three-knockdown rule as an authored arcade choice. Cheapest, and honest.
2. **Make it selectable.** A default professional ruleset plus an arcade modifier,
   with the ruleset recorded per bout. More work, and it makes replays need a
   ruleset version.
3. **Drop it.** Adopt unified-rules termination. Note this would change every
   stoppage number measured this week, since the three-knockdown rule is what
   ends the bouts being counted.

Source: the ABC's published Unified Rules of Boxing,
<https://www.abcboxing.com/unified-rules-boxing/>, read 2026-08-05.

Worth noting which way this cuts. `decision_path_must_survive` — the invariant
that has held Phase O all week — is an invariant about bouts reaching the cards,
and the rule making bouts *not* reach the cards is the three-knockdown stoppage
that no professional ruleset has. That does not make the stamina findings wrong;
the reference simulator reaches the cards in 20 of 24 bouts under the same rule.
But if G5 resolves toward unified rules, every stoppage figure quoted this week
is measured against a termination condition the project no longer uses, and they
should be re-run rather than re-read.

## Closed gates

None yet.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 19:00 UTC | END ] -->
