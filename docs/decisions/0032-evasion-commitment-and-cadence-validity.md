# Decision 0032 — Evasion commitment and cadence validity

**Status:** Accepted
**Date:** 2026-08-08
**Director:** ChatGPT

## Context

The third three-lens constructed panel correctly exposed a risk in the path toward First Bell: cadence measurements are not trustworthy if active evasions can be attempted without carrying their authored startup/active/recovery commitment and mistime consequences into the integrated bout.

This is not a new evasion design. Phase R already establishes the relevant canon, its Python analyzer already reads startup/recovery and the mistime penalty, and the shared C++ evasion core already exposes reusable rules. The current gap is **integration**: the First Bell bout must preserve those commitments rather than treating evasion as a free instantaneous tactical label.

## Ruling

1. **Active evasion is a committed action.** `slip_lead`, `roll_under`, and any later active-window evasion must preserve authored timing semantics in the integrated bout. Startup, active window, recovery, and the declared mistime penalty remain authoritative inputs; the integrated runtime may not collapse them into an instantaneous success/failure query.

2. **No evasion success die is introduced.** Resolution remains geometric/temporal: vacated region, authored counters, punch timing, and the active window determine whether a punch finds empty space. Randomness may influence a CPU choice among equivalent legal defensive intentions; it does not roll the defensive outcome after commitment.

3. **Mistimed defence must have opportunity cost.** A committed evasion that catches nothing still consumes its authored commitment/recovery. The opponent need not be mid-punch for an evasion attempt to carry cost. This prevents repeated telegraph-twitching from becoming a free dominant line.

4. **Cadence evidence is provisional until this is integrated.** Punch-rate, rest-rate, movement-rate, accessibility-cadence, and stamina-fit conclusions produced before movement/range, typed stamina, and authoritative evasion commitment coexist in the same bout are diagnostics only. They may identify defects; they may not fit balance values.

5. **Phase R remains frozen evidence.** If Python rules are extracted from `analyze_core_evade.py` into a reusable module for the integrated bout, the historical Phase R analyzer must consume that module and re-prove byte-identically. No historical pin moves for refactoring.

6. **The shared C++ evasion core remains the authority seam.** The integrated C++ runtime must call the existing reusable Phase R core. If a missing live seam is discovered, extract the smallest reusable seam and re-prove Phase R. Do not copy formulas into the bout.

## Required integrated proofs

Before cadence may become fit evidence, prove at minimum:

- an active evasion has a nonzero commitment/recovery path where canon declares one;
- a mistimed evasion cannot be spammed every decision tick without consequence;
- a body shot still defeats a head-vacating slip by region;
- an authored uppercut counter still defeats the roll;
- a straight can be evaded by a correctly timed slip;
- a successful evasion resolves before guard and is not also recorded as a block;
- changing presentation RNG cannot alter any evasion result;
- Python and C++ agree at the integrated evasion boundary.

## Non-rulings

This decision does **not** tune evasion windows, recovery lengths, punch cadence, Wind/Reserve values, or accessibility timing. Those remain unfitted until complete-bout observable evidence exists.

## Director intent

The purpose is not to make defence expensive. It is to make defence **committed**. A good read should buy safety. A bad read should cost time, position, or opportunity because the fighter actually moved their body and must recover from that choice.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 20:35 UTC | appendix start ] -->

---

# Appendix — reconciliation of a duplicate 0032 (2026-08-09)

**Everything above this line is the Director's, unaltered.** This appendix was
appended when a duplicate decision file was found and resolved.

## What happened

On 2026-08-09 the decision-drift test flagged that "Decision 0032" was cited
throughout the codebase with no decision file present *on the working branch*.
A transcription was written from the Director's disposition note and filed as
`0032-evasion-commitment-and-the-lab-fence.md`.

The premise was wrong. **This file already existed on `main`** — the branch
simply predated it. The transcription was a second document bearing the same
decision number, which is precisely the drift the numbering exists to prevent.

Resolved rather than averaged, per the project's working rule: **this file, the
Director's own, is the sole Decision 0032.** The transcription is deleted. The
two additive passages it carried, neither of which contradicted anything above,
are preserved below because code and later decisions refer to them.

## Citation correction — "§3" means Ruling 4

Code comments, `tests/test_decision_0032.py`, and Decisions 0033–0037 cite
**"Decision 0032 §3"** for the lab fence. That section number came from the
transcription's own layout and does not exist in this file. The rule it names
is **Ruling 4 above** — *"Cadence evidence is provisional until this is
integrated."* Both citations point at the same binding rule; **Ruling 4 is the
authoritative reference** and new work should cite it. Existing citations are
left in place rather than rewritten across dozens of files, and this paragraph
is the map between them.

The clause as it has been quoted across the codebase:

> No lab observation may be used to change canon, calibration, acceptance
> criteria, or authoritative implementation until it receives an explicit
> Director disposition.

## Disposition of the round-three panel's six asks

Recorded in the Director's disposition note and nowhere else in `docs/decisions/`:

1. **Two-contact input cap — accepted, deferred.** First Bell is CPU-first; the
   human input layer inherits the cap later (Decision 0027 carries the spirit).
2. **One-week answer deadline on lab findings — deadline rejected**; the binding
   rule (Ruling 4) accepted instead.
3. **Evasion recovery before trusting cadence — accepted immediately**, on the
   critical path.
4. **Never show Crowd Bar and crowd roar simultaneously — rejected.**
   Presentation may not be *triggered by* Crowd Bar thresholds; causality is the
   fence, coincidence is allowed.
5. **Judges should differ on defence — deferred.** No hidden `defence_score`
   bonus manufactured to force disagreement.
6. **Accessibility depends partly on cadence — accepted**, but no numeric
   cadence target may be established from synthetic data.

## Correction the transcription carried

The panel believed the Phase R analyzer did not read evasion timing. It does —
startup, recovery, active timing and `mistime_penalty_ticks` were already read.
The real gap was that the **integrated bout** did not make those timings
authoritative combat commitments. Ruling 1 above is what closed it.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 20:35 UTC | appendix end ] -->
