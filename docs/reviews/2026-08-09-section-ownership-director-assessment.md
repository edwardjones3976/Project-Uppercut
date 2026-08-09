<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 03:40 UTC | director assessment start ] -->
# Overall Project Assessment — section ownership pass

Five sections were established with strict file ownership so specialists could
not collide. Four ran as independent owners; Section 5 (contract, stream,
verification) was retained by the Director, because it owns `bout.py` — the
file where every other section meets — and integration is the coordinating
role's job.

## Project health

**Materially better than it was this morning, and honestly red right now.**

The council's number-one item is fixed and the fix is measured, not asserted:

    whiff_band == 0

Seed 4242, full fight, not one punch refused by the range gate. The same seed
refused 85 before; the twelve-round mirrored-outside fight refused **3,174 —
every punch it threw.** `policy.BY_BAND` is deleted. There is one derivation
of offence legality, canon's, and the chooser and the gate both read it.

The fight changed shape in the direction the whole council pointed:

| | before | after |
|---|---|---|
| punches refused by the gate | 85 | **0** |
| authored counters fired | 0 | **49** |
| punches slipped (vacated) | 5 | **70** |
| punches thrown, whole fight | ~317 in round 1 alone | 268 |

Evasion finally does something. Decision 0032's commitment lifecycle was built
two sessions ago and could not express itself, because the punches it was
meant to answer were being refused before they reached it.

**And the gates are red: 14 genuine failures plus 3 deliberate countdowns.**
The work is preserved on `wip/section-ownership-band-gate` at `927c1d6`,
clearly labelled, pushed, and not merged. `main` and the green tip of
`feat/phase-r-into-the-bout` are untouched.

## Major strengths — protect these

The range module's canon self-checks; `in_band`'s fail-closed posture (now
strengthened — it had a latent `None == None` hole); the policy's
observable-only inputs and entity-scoped streams; `resolution.py`'s refusal to
invent coefficients and its habit of naming simplifications in place; and
`judging.py`'s structural seal, which four specialists were told to improve and
none weakened.

## P0 blockers, current

**B1. Fourteen tests carry expectations of the old grammar.** Preferred bands
that are now correctly refused, `P.BANDS` which no longer exists, and reason
codes that changed when "no legal attack" stopped meaning "pivot on the spot".
Each needs judgment, not a mechanical pass.

**B2. Three countdown tests are firing, exactly as designed.**
`test_council_findings.py` was written so each test fails the day its defect
dies. Three have died. They must be retired and replaced with the invariants
their own docstrings specify — the coherence tautology, no ghosts, and
`whiff_band == 0`.

**B3. The knockdown funnel is still one move id, and it is now BLOCKED on the
Director rather than on engineering.** Section 3's patches are complete and
anchor-verified. Its own owner then found the reason not to land them
unilaterally: reading `target_regions` correctly makes four of five punches
knockdown-capable, and at the current threshold **cross and uppercut clear it
at full wind and zero damage** — every landed one a knockdown. Re-choosing
`pressure_threshold` is fitting a value, which Decision 0032 §3 reserves to
you. So the fix waits on a disposition instead of being smuggled in beside it.

## P1 priorities

Section 4's ten-point-must fix and judging units — complete, anchor-verified,
not yet applied. **D4 is not hypothetical: an illegal card is already on disk.**
Fight A round 1, Tomasz Wojcik's card reads 9-9, a round in which neither
fighter receives ten. Section 4 reproduced it exactly from the recorded
account.

Then: ruleset authority (D6), which decides what "an ending" even is; and the
`thrown` evidence field, without which effective aggression cannot be
expressed.

## Cross-section conflicts, and how they were resolved

**Section 1 vs Section 3, on batching.** Section 1 predicted the band fix would
roughly triple `uppercut_rear`'s selection rate at inside and asked for D3 in
the same batch. Section 3 independently found that D3 in that batch produces
round-one stoppages. Both are right, and the resolution is neither's to make —
it is DD1. **Testing cannot resolve it, because the disagreement is about what
number the fight should be tuned to, and tuning is forbidden.** Escalated.

**Section 1's own answer to its own open question.** Asked whether a punch-less
`outside` band is correct boxing or a canon gap, it argued *correct* from three
independent canon sources — the jab's authored tip extension (1.05 ru) against
the outside floor (1.1 ru), `threat_compression`'s `release_bands`, and
`auto_advance_on_throw: false` — and then made its code correct under **both**
answers and proved it. That is the right shape for a specialist meeting a
Director question.

**Section 4 against the council's own earlier reviewer.** The referee specialist
wanted judges forced off exact ties. Section 4 ruled: a genuine dead heat stays
10-10, because fabricating separation hides an evidence famine behind a
scoreline — but an exact *arithmetic* tie breaks on each judge's own criterion
priority. Even rounds fell 5.0% → 0.4% with no randomness consumed.

## Missing ownership

`fighter.py` and `uppercut_evade/core.py` had no section owner. I took
`fighter.py` as Director to thread legality through the observation. `evade`
was left alone deliberately — Section 3 flagged that its `target_regions[0]`
read is *correct* there (a slip vacates one lane) and must not be "fixed" by
analogy.

## Duplication found

`policy.BY_BAND` (deleted), `policy.BANDS` (deleted), `policy.BY_HAND` (still a
third hand-authored copy of canon's per-move `hand` — flagged, not absorbed,
because hand is not a range property), `resolution`'s own delivered-impact term
competing with `punch_model.delivered_impact`, and `fnv1a64` re-declared in
`bout.py` beside the C++ twin.

## Testing gaps

Everything below is specified as exact assertions in the section reports and
none of it is written yet: the coherence tautology between chooser and gate;
the punch ledger closing; `decision_path_must_survive` as an executable sweep;
every scored round giving the winner ten; judge independence under 95%
agreement; turn-order neutrality; and the reaction-lattice phase test that
would expose whether a hard 4-tick interval makes mid-tier slips read as random.

## Decisions needed — and these are genuinely yours

**DD1 (P0).** Does the knockdown-region fix land, and if so what happens to
`pressure_threshold: 0.57`? It was swept when one move could reach a
knockdown-relevant region. Re-choosing it is fitting a value.

**DD2 (P0).** Ruleset authority: delete `max_per_round`/`max_per_bout` from
`condition_model` and let the ruleset rule, accepting the contract bump to v3?
Under `professional` both stoppage counts are `null`, which means **no
knockdown count stops the bout** — and the decision path finally survives.

**DD3 (P1).** Does `range_band` become a set per move? Section 1 says no and
argues the outfighter's real answer is a step-and-jab composite action, not a
wider band. Everything written is correct either way.

**DD4 (P1).** Do `torso_lower` / `head` become knockdown-relevant? The body
knockdown is currently impossible.

**DD5 (P2).** Is `pressed × landed` accepted as effective aggression until a
`thrown` count exists?

## Final project matrix

| Section | Owner | State | Highest risk | Priority | Next action |
|---|---|---|---|---|---|
| 1 Range & offence legality | S1 | **Applied, verified** | C++ twin not ported | P1 | Port `ThrowableFrom`; sort on string not FName |
| 2 CPU policy & cadence | S2 | **Applied, 14 tests red** | Cadence lattice unmeasured | P0 | Update test expectations; run lattice test |
| 3 Contact & knockdown | S3 | **Patched, not applied** | Blocked on DD1 | P0 | Director disposition, then apply |
| 4 Officiating & judging | S4 | **Patched, not applied** | Illegal card on disk | P1 | Apply; guard `verdict()` on empty card |
| 5 Contract, stream, verification | Director | **Partial** | Gates red | P0 | Retire 3 countdowns; fix 14; re-run sweep |

## Next execution order

1. **Update the 14 test expectations and retire the 3 countdowns** — replacing
   each with the invariant its own docstring specifies. Gates green before
   anything else moves.
2. **Apply Section 4's judging patches** and guard the empty-card read. This is
   independent of the fight's shape and fixes an illegal card already on disk.
3. **Rule DD1**, then apply Section 3 in that same batch, because Section 1's
   throw-rate change and Section 3's eligibility change compound.
4. **Rule DD2** and wire ruleset authority — it decides what an ending is, and
   every sweep run before it must be re-run after it.
5. **Re-run the thirty-seed sweep and look at the fight.** Every diagnostic in
   this document is provisional until then. The contested middle either
   appears or it does not, and *that* is the measurement worth having.
6. Only then: the guard stage, reach-at-contact, the chain window, the clinch.

## What I will not claim

The contested middle has not been observed. What has been established is that
the two mechanical reasons it could not appear — an offence table that
disagreed with the gate, and a fighter with no answer to being unable to punch
— are gone from the code and proven gone by measurement. Whether a watchable
fight follows is a question for step 5, not for this document.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 03:40 UTC | director assessment end ] -->
