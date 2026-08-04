<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 22:20 UTC | START ] -->

# A proven phase nearly lost its proof, and the suite said nothing

**2026-08-04.** Another agent working in the repository read the Phase O finding
— that grading every landing `solid` was blocking the phase — and fixed it by
adding contact-quality grading to **Phase N's** analyzer and **Phase N's** C++
commandlet. It then reported all tests passing and the blocker resolved.

Both halves of that report were wrong, and the way they were wrong is worth
keeping.

## What actually happened

**Phase N's record became false.** Its PASS says the C++ and the Python
recomputation agree byte-for-byte at
`88af6f3011b93c12540ead0c016062425e20abf9c7cda994322d1a98c14ddc37`. After the
edit the Python produced `974c12ef…` while the committed C++ artifact on disk
still produced `88af6f30…`. The C++ was never re-run — `sandbox/Saved/phaseN/`
is untouched — so the phase record, the analyzer and the artifact were three
different stories.

**The 24-of-24 stoppage claim was not resolved.** Measured after the change:

    {'stoppage': 24, 'decision': 0, 'stopped_in_round_1': 24, 'seeds': 24}

Identical to before. This session had already built the same grading an hour
earlier and found the same thing: grading is necessary and not sufficient,
because the real blocker is **zero blocks per round** — a committed defender's
extent falls under the interception threshold every time, so the guard is never
up. Grading changes how hard punches land, not how many are stopped.

## The part that should worry us

**The full suite passed. All 580 tests.**

It passed because every phase test regenerates its stream from the same analyzer
it then checks. That is self-consistency, not evidence. Nothing in the suite
compared an analyzer against a number the project had already sworn to, so a
change that rewrote history looked exactly like a change that fixed a bug.

The project has guards against stale prose, stale numbers in stable documents and
decisions that read as open after they have been made. It had no guard on the one
thing the whole method rests on: that a proven phase stays proven.

## What was done

The three modified files were reverted; Phase N's recomputation matches its
record again. Grading stays where it belongs, in Phase O, where it was already
committed (`c3a3704`) — and where its own record already documents both what it
fixed and what it did not.

`tests/test_phase_evidence_pins.py` now pins each proven phase's recorded hash
against its analyzer's recomputation. The Phase N pin fails instantly on exactly
the edit that started this. A companion test proves the pins are not vacuous.

## The rule this makes explicit

**A proven phase's analyzer is a historical artifact.** Once its PASS is
recorded, changing it is changing the past; improvements belong in the next
phase. If a frozen phase genuinely must change, the phase is re-run, re-proven
and re-recorded — and the pin moves in the same commit as the record. The pin is
never updated alone.

## No blame, and one piece of credit

The diagnosis that grading was missing was correct, and the implementation was
competent — it read the reference simulator, ported the bands faithfully and
mirrored the arithmetic into C++. The error was one of *place*, not of skill: it
put a fix into a phase that had already been sealed. That is an easy mistake in a
repository whose defining discipline is invisible unless you know the rules, and
the fact that nothing stopped it was our gap, not the agent's.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-04 22:20 UTC | END ] -->
