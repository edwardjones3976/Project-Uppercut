<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 06:40 UTC | START ] -->

# Decision 0040 — the C++ round is the fight, and neither outcome is authentic yet

**Date:** 2026-08-12
**Authority:** Director ruling on Issue #12, recorded here so the control plane
and the repository say the same thing.
**Status:** in force.

## Why this record exists

The ruling was made on GitHub. `docs/decisions/OPEN_GATES.md` and the decision
index did not know about it. That is control-plane drift: two places that both
claim to say what is decided, disagreeing, with nothing failing. This repository
has already paid for that once — Decision 0038 exists because two branches
numbered decisions independently — so a ruling that lives only in an issue
comment is not yet a ruling this project can act on.

Nothing here is new authority. This is the transcription, and it is numbered so
a later edit cannot silently flip it.

## The rulings

**R1 — The shared C++ `INTEGRATED_1R` session is the combat authority.**
`FUppercutFightSession` and the cores it composes are the fight. What Play runs
is what the evidence is taken against.

**R2 — Python `IntegratedBout` is reference and tooling only.**
It remains valuable as an instrument — fast, inspectable, runnable in CI and on
Linux — and it is not the fight. When the two disagree, C++ is not the one that
is wrong by default; Python is the one that must converge.

**R3 — Neither current outcome is accepted as authentic calibration.**
The C++ round produces **zero** knockdowns (`punches=123 landed=51 kd=0-0`,
seed 4242, 10800 ticks). The Python round produces **17 and 21** across two
seeds. A round in which nobody can be dropped and a round with a knockdown every
ten seconds are both wrong, and the fact that one of them currently scores
better against the authenticity bands does not make it correct. Neither is canon.

**R4 — Waivers remain empty.**
The authenticity scorecard reports what it measures. A metric that fails is a
failure, not an entry in a file. The earlier waiver set — which waived exactly
the four metrics that failed, and attributed Python's numbers to an unfinished
C++ port — is withdrawn and must not return in that shape. If a metric must be
tolerated, that is a Director disposition with its own record, not a JSON entry.

**R5 — `pressure_threshold` remains frozen at 0.57.**
Decisions 0035–0037 stand. Nothing in the divergence above is evidence about the
threshold, because the two implementations do not yet agree on what they are
measuring. Tuning a shared constant to reconcile two disagreeing runtimes would
bury the disagreement instead of resolving it.

**R6 — `feat/authenticity-program` is on HOLD.**
Not merge-ready. Release requires parity, the CI repairs, and broader evidence
than two seeds.

## What must be true before calibration is even discussed

In order. Each one gates the next.

1. **CI blockers repaired** — `STATUS.md` regenerated rather than hand-edited,
   the source-integrity gate green, and no authenticity metric able to pass by
   being absent. A gate that skips a missing measurement is a gate that reports
   the absence of data as success.
2. **The first C++/Python divergence traced.** Not the totals — the first tick
   where the two runtimes make different decisions from the same seed. Totals
   are a symptom and this project has already lost a day to measuring the wrong
   artifact (`docs/development-log/2026-08-05-i-measured-the-wrong-artifact.md`).
3. **UE and live proofs re-run** after the repairs, on the exact tree being
   judged.
4. **A matched 30-seed scorecard**, both runtimes, with opening / middle /
   ending captures. Two seeds cannot carry a claim about authenticity; the
   confound that invalidated four conclusions at once was a normalisation over
   bouts that all ended the same way.

Only then is calibration a conversation. Until then it is a way of making the
numbers agree without finding out why they do not.

## What this decision does not do

It does not rule on which knockdown rate is right. It rules that the question
cannot be answered from the current evidence, and that the answer belongs to the
Director once parity exists. It does not reopen any closed gate. It does not
move a pin, a canon value, or a frozen threshold.

## Consequences

- `OPEN_GATES.md` records this ruling. No new gate is opened: this is a
  disposition, not a question awaiting one.
- `authenticity_waivers.json` must hold no waivers. A future waiver requires a
  numbered decision naming the metric, the seeds, and the expiry condition.
- Any agent proposing a tuning change to `pressure_threshold`, the condition
  model, or the knockdown regions should be pointed at R5 and at Decision 0032
  Ruling 4 before it is measured, not after.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 06:40 UTC | END ] -->
