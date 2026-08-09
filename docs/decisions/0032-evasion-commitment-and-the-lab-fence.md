<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 09:45 UTC | Decision 0032 record start ] -->
# Decision 0032 — Evasion is a commitment, and the lab fence

**Status:** ACCEPTED (Director, 2026-08-08).
**Provenance:** This file is a TRANSCRIPTION. The ruling was issued in the
Director's disposition of the round-three panel review and recorded on Issue
#12 on 2026-08-08; it has been cited across the codebase as "Decision 0032"
since, but no decision file was ever written. The decision-drift test caught
the gap on 2026-08-09 — which is that test doing its job — and this record
closes it. Nothing here is new; wording follows the Director's disposition
note. The tags mark the transcriber, not the author of the ruling.

## The main ruling

Evasion must consume real time and commitment inside the same bout that
already owns policy, movement/range and stamina:

    commit to slip/roll -> startup -> active window
        -> punch reaches that window or does not
        -> vacated lane / authored counter resolves
        -> recovery, or mistime consequence

No dodge percentage. No evasion die. No free defensive twitching. A bad read
still occupies the fighter's body and time.

**Correction to the panel:** the Phase R analyzer already reads startup,
recovery, active timing and `mistime_penalty_ticks`. The gap was that the
integrated bout did not make those timings authoritative combat commitments.

## Disposition of the panel's six asks

1. **Two-contact input cap — accepted, deferred.** First Bell is CPU-first;
   the human input layer inherits the cap later (Decision 0027 carries the
   spirit).
2. **One-week answer deadline on lab findings — deadline rejected; the
   binding rule (§3 below) accepted instead.**
3. **Evasion recovery before trusting cadence — accepted immediately**, on
   the critical path.
4. **Never show Crowd Bar and crowd roar simultaneously — rejected.**
   Presentation may not be *triggered by* Crowd Bar thresholds; causality is
   the fence, coincidence is allowed.
5. **Judges should differ on defence — good question, deferred.** No hidden
   `defence_score` bonus manufactured to force disagreement.
6. **Accessibility depends partly on cadence — accepted**, but no numeric
   cadence target may be established from synthetic data.

## §3 — the lab fence (the clause cited everywhere)

> **No lab observation may be used to change canon, calibration, acceptance
> criteria, or authoritative implementation until it receives an explicit
> Director disposition.**

Until evasion commitment is integrated — and since integration, until the
Director disposes otherwise — cadence and outcome numbers from integrated
runs (punch counts, rest counts, movement counts, stamina fits) remain
**diagnostics, not calibration evidence**.

## Required proofs

Body shot still finds the body during a head slip; the uppercut defeats the
authored roll; a straight can miss a correctly timed slip; a mistimed slip
creates recovery/opportunity cost; presentation RNG changes leave every
evasion outcome unchanged. (All five implemented and passing in
`tests/test_decision_0032.py`.)

## Implementation order the ruling fixed

Phase R extraction as the smallest reusable Python seam, byte-identical
re-prove; then integrated evasion preserving authored startup/active/
recovery/mistime with evasion resolving before guard and a slipped punch
never also blocked; then, without another panel: evasion → guard → contact
quality → regional condition → knockdown eligibility → count/recovery →
referee → sealed scoring → verdict.
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 09:45 UTC | Decision 0032 record end ] -->
