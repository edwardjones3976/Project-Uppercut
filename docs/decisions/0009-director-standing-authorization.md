<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 23:17 UTC | START ] -->

# Decision 0009 — Director Standing Execution Authorization

**Status:** accepted (Director grant, recorded verbatim)
**Date:** 2026-08-02
**Supersedes:** narrows nothing; extends Decision 0008's per-task assignment with a standing grant.

## The grant, verbatim

> "You will do it! You won't need to walk me through anything but what you completed!
> Under this project, you have full authorization."

— Director, 2026-08-02, immediately following the UE 5.8.1 install and the runbook hand-off.

## What it means in practice

Agents execute Project Uppercut work end-to-end — implementation, tooling, installs, repository
operations, engine work — without pausing for per-step walkthroughs, and report **completed work with
evidence** rather than asking permission at each step. Recorded per the visible-rulings pattern of
Decision 0007: authority is written down, attributable, and reversible, never assumed.

## What it does not change

1. **The session safety contract.** Credentials, account sign-ins, legal acceptances (EULAs),
   payments and permanent deletions stay with the Director regardless of authorization — which is
   why the Epic sign-in was his and the project creation was ours.
2. **Rule 18.** Authorization to act is not authorization to claim. Every completion still ships with
   repository evidence; unverified work is reported as unverified.
3. **Canon precedence.** PROJECT_NOTES.md and PROJECT_RULES.md still outrank any plan or agent
   convenience. This grant authorizes execution, not reinterpretation.
4. **Director-owned calls.** Gate passes stay evidence-driven; product-identity and canon changes
   remain his.

## Revocation

One Director line narrows or revokes this at any time; the change lands here as an amendment, not a
silent behavior shift.

## First act under this grant

Runbook step 5 executed by agent: `sandbox/UppercutSandbox.uproject` created Blueprint-first from the
engine's own TP_Blank template (per its TemplateDefs.ini rules), fresh ProjectID, headless editor
acceptance run as verification — evidence in the commit that carries this decision.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 23:17 UTC | END ] -->
