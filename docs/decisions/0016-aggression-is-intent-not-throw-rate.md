<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:40 UTC | START ] -->

# Decision 0016 — `aggression_bias` is intent, not throw rate

**Status:** accepted (Director ruling, 2026-08-05)
**Closes:** gate **G3**
**Date:** 2026-08-05
**Packet:** `docs/plans/2026-08-05-three-canon-quantities-decision-packet.md` §Item 2

## Question

`aggression_bias` sits at 0.35–0.60 in canon. Read as "the share of decision
ticks that become a punch," it produces **175–219 punches per fighter-round**
against a professional 55–78 — roughly 7× too high. Neither reading of the
decision clock rescued the authored values, so the number was either wrong or the
reading was.

## Decision

**The reading was wrong.** `aggression_bias` means *the tendency to seek
offensive initiative when a plausible opportunity exists.* It does not mean the
percentage of thought cycles that become a punch.

Policy is staged, and the bias applies at the intent stage only:

    observe state
      -> choose broad intent          <- aggression_bias lives here
      -> identify a legal opportunity
      -> choose an action
      -> commit, or continue observing

A high-aggression fighter expresses it as pressure, not as volume for its own
sake: advancing, controlling exits, feinting, jabbing, attacking open lanes,
forcing defensive reactions, sustaining purposeful volume. An intent to attack
that finds no legal opportunity produces `Observe`, not a punch into empty air.

Every attack must still satisfy, at the opportunity stage: legal range, hand
availability, recovery state, stamina, target availability, tactical value,
repetition awareness, positional risk.

## Why this is a semantic ruling and not a re-tune

The alternative was to divide the authored numbers by seven and carry on. That
would have preserved a model in which a fighter throws at a fixed rate regardless
of whether anything is in front of him — which is the thing that made the volume
wrong in the first place, and it would have made every style read the same at
different speeds. Canon's 0.35–0.60 is kept **unchanged**; what changes is the
stage of the pipeline that reads it.

The consequence worth stating: with this ruling, punch volume becomes an
*emergent* number rather than an authored one. It falls out of how often
opportunity and intent coincide, which is exactly the repository's standing
preference (emergent over hardcoded). It also means volume is now a measurement
that can be wrong, and it will be measured against the professional 55–78 rather
than asserted.

## Reason codes

Every decision emits a readable reason code, so a policy that is behaving oddly
can be read rather than inferred. The initial vocabulary:

`SEEK_PREFERRED_RANGE`, `CUT_OFF_EXIT`, `PUNISH_OPEN_LEAD_SIDE`,
`PROTECT_DAMAGED_BODY`, `RECOVER_STAMINA`, `RESET_AFTER_WHIFF`,
`PUNISH_REPEATED_JAB`, `EXIT_BAD_ANGLE`, `PRESSURE_ROPES`, `HOLD_AND_OBSERVE`.

## The observability rule, restated because it is easy to lose

CPU policy may never read human input before it becomes observable action, future
actions, official scorecards, hidden random draws, or private opponent state a
boxer could not observe. A policy that reads the die is not difficulty, it is
cheating, and it will read as cheating.

## Consequences

- Depends on Decision 0015: a staged policy needs somewhere to put "intent
  without opportunity," and that place is `Observe`.
- Phase S's contract is rewritten around the stages. Its pinned evidence moves.
- Style balance conclusions taken before this ruling were taken against a flat
  throw rate and are withdrawn rather than adjusted.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:40 UTC | END ] -->
