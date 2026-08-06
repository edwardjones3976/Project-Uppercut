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

**G1–G6 were ruled on by the Director on 2026-08-05 and are CLOSED.** The rows
stay, as this file's own rules require; each names the decision that closed it.

**G7 opened 2026-08-06** and is the only gate currently blocking work.

| # | Gate | Blocks | State | Evidence |
|---|---|---|---|---|
| G7 | **The stamina economy cannot pay for a round of boxing** — pool, regeneration and punch costs together buy 19 punches a round against a professional 55–78, a 2.9× shortfall. Fighters sit at 1% stamina for eleven of every twelve minutes, and `1.4 − stamina_fraction` is the ONLY term in the pressure product that discriminates between a landing that knocks a man down and one that does not | Phase O's lethality, and every conversion figure downstream of it | **OPEN** | `docs/plans/2026-08-06-the-stamina-economy-decision-packet.md` |

| # | Gate | Blocks | State | Evidence |
|---|---|---|---|---|
| G1 | **Normal-step cost authority** — `movement_model.locomotion` says 0.132 per step; the move table says 0.600 flat, 4.55× apart, core reads the higher | the whole stamina economy, and every Phase Q/R/S number downstream of footwork | **CLOSED** — movement is priced by displacement; the flat fee is re-homed to named explosive actions | `0014-movement-costs-displacement.md` |
| G2 | **Rest / no-action semantics** — nothing in canon authors doing nothing; four of six non-offensive choices charge stamina | action count, which is the stamina economy's actual problem | **CLOSED** — thinking is free; Observe, HoldPosition and Rest are first-class outcomes | `0015-rest-and-no-action-are-first-class.md` |
| G3 | **`aggression_bias` semantics** — intent, attempt, or throw probability; as read today it produces 175–219 punches per fighter-round against a professional 55–78 | CPU policy, and any style balance conclusion | **CLOSED** — it is intent at the intent stage, not throw rate; the authored numbers stand | `0016-aggression-is-intent-not-throw-rate.md` |
| G4 | **Decision 0013 ratification** — lateral guard geometry in the model, discrete controls at the controller | hooks and side-specific exposure; the ten-guards drift | **CLOSED** — ratified in principle, scheduled after the live round; the ten-guards drift stays open | `0017-ratification-of-0013.md` |
| G5 | **Declare the default ruleset** — the three-knockdown rule is currently canon and is the termination condition in every measurement | what "a bout ended correctly" means; every stoppage figure quoted this week | **CLOSED** — versioned rulesets; professional default, three-knockdown becomes an arcade modifier | `0018-versioned-rulesets-and-the-professional-default.md` |
| G6 | **Guard lanes authored exactly on the interception threshold** — `philly_shell` body and `active_hands` head both sit at 0.60 | two of ten guards open on the first point of arm damage | **CLOSED** — a canon authoring margin, enforced for every posture | `0019-no-coverage-value-sits-on-the-threshold.md` |

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

All six, on 2026-08-05, by Director ruling. Decisions 0014 through 0019. The
rulings and their consequences are in those records; what belongs here is the
one line each that a reader scanning for "is this still blocking anything"
needs, and that is the `State` column above.

Two consequences travel with the closures and are recorded here so they are not
discovered later as surprises:

- **Measurements taken before 2026-08-05 must be re-run rather than re-read**
  wherever they depended on the flat step cost (G1), on a fighter who could not
  stand still (G2), or on the three-knockdown termination (G5).
- **The Phase Q port is unaffected.** Its slice reads no stamina and no ruleset,
  which was the reason for that scope call; the pinned bytes and the proof stand.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 19:00 UTC | END ] -->
