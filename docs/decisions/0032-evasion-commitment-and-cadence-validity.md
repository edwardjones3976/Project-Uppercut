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
