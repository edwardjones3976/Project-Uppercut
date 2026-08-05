<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 23:10 UTC | START ] -->
# Phase Q is proven, and the band does nearly all the work

**2026-08-05.** The editor was closed, so the port that had been waiting on it
happened. `UppercutCoreRangeCommandlet` now reproduces
`analyze_core_range.expected_stream` byte for byte at 4242/5400, 777/5400 and
4242/900. That is what proven means here, and Phase Q is the first phase past N
to earn the word.

## What had to be built first, and why it was not obvious

Phase Q's analyzer was written this morning as a rule set: canon read into the
integer contract, four properties stated so they could be mutation-proven, and no
clock. That was enough to prove the rules and **not** enough to prove an
implementation, because an implementation is only proven against a marker stream
and there was no marker stream to prove it against.

So the first half of "port Phase Q" was writing the artifact the port had to
reproduce. Nine actions drawn flat from the shared LCG, two fighters on canon's
ring axis, and eleven row kinds — the movement delivered each tick, the band
transitions, the punches with their verdict AND their reason, the decisions, the
properties, and a trailer carrying the FNV-1a 64 self-hash of everything above
it. Then the C++, then the comparison.

The C++ matched on the first run. That is worth one sentence of suspicion rather
than any celebration: it matched because both sides were written from the same
written-down rules within an hour of each other, which is the good case, and the
three-run check across two seeds and two lengths is what stops it being an
accident.

## What this slice deliberately does not contain

No stamina, no guard, no condition, no damage. Two reasons, and the second is
the load-bearing one.

The first is that those belong to N, L and O, which are already proven, and a
contract that re-implements a proven phase is a second place for it to be wrong.

The second is **G1**. The step cost is priced twice in canon, 4.55× apart, and
that is a Director call nobody has made yet. A Phase Q stream that spent stamina
would have to be re-blessed the day G1 is ruled on — for a reason having nothing
to do with range. A port proven against a stream that moves for unrelated
reasons is not really proven. This one does not move, which means the ruling on
G1, whenever it comes, cannot quietly invalidate the range port.

## The finding: the band gate is doing nearly all of the work

Phase Q applies two tests to a punch. The band gate — Rule 12, the authored
intent, checked at throw time — and the geometric tip-versus-surface test that
survived from Phase K. The module docstring says both are required and that
where they disagree the disagreement is information.

The stream says the band is by far the tighter of the two. In 5400 ticks at seed
4242: 343 punches, 111 landed, **231 whiffed on the band, and exactly one whiffed
on reach**.

    P|1104|1|cross_rear|whiffed|reach|11|19860|19120|mid|1

A rear cross, thrown legally from mid, whose fist finished 0.074 ru short of the
opponent's surface. At seed 777 over the same 5400 ticks the count is zero.

Canon explains it in `pose_geometry.fist.profile_note`: extensions are authored
to sit just under each move's band ceiling plus body reach. The two tests are
*meant* to agree almost everywhere, and where they part company the geometry is
the stricter one, at the top of a band.

The tempting conclusion is that the geometric test is redundant and could go. It
should not go, and the number is the argument for keeping it rather than against
it: a port that checked only the band would be right 342 times out of 343 and
wrong in the one case that matters — a fighter at the far edge of a legal band,
which is exactly where a boxer's judgement of distance is supposed to be tested.
A rule that fires once in five thousand ticks is not a rule that does not
matter; it is a rule that fires when the fight is at the edge of something.

## The other number: two thirds of all punches are thrown from the wrong band

231 of 343. Every one travels its full arc into empty air and pays the whiff,
which is canon's sentence made executable — no invisible lunge closes the gap and
no magnetic correction shortens it.

That is not a defect this phase introduces. It is the defect this phase makes
**visible**, and it is the same thing measured this morning as `uppercut_rear`:
532 thrown, 0 landed, all night, from a stance frozen at one separation since
Phase H. A flat nine-way draw has no idea where it is standing.

What happens to that number when something that can read the band chooses
instead is Phase S's business. Both contracts now exist, on the same integer
model, and can be pointed at each other.

## Two things about tooling, recorded because they cost time

**A PowerShell runner that silently does nothing is worse than one that fails.**
The Phase Q parity runner was first written as a `.ps1` in the shape of Phase N's,
and driven from an agent's spawn context it produced no output twice. Two
independent causes: a mandatory `param()` that fails to bind **prompts on stdin
and waits forever**, and `Write-Host` writes to the information stream, which
`>` from `cmd` does not capture. Both look identical from outside — "the run
produced nothing" — which is the worst available failure mode for evidence
tooling, because it is indistinguishable from a run that found nothing. It is now
`tools/engine/prove_core_range.py`: no shell in the middle, output on stdout,
and it has actually been run end to end rather than assumed to work.

**Floor division is a porting hazard and was closed before it bit.** Python's
`//` floors toward negative infinity; C++ `/` truncates toward zero. Every scaled
quantity in the commandlet goes through an explicit `FloorDiv`. Only one call
site can currently see a negative numerator — the rope retreat scaling — and
canon's `rope_retreat_multiplier` is 0.0, so today the two agree by luck. The
helper is what makes them agree on purpose, and it costs four lines.

## State after this

- **Phase Q: PROVEN.** `STATUS.md` regenerated and now names it.
- Two golden streams pinned: O (held) and Q (proven). Q's pin is what makes the
  parity proof keep meaning something without an engine — a contract edit that
  would break the port is now caught by the ordinary suite.
- 733 tests green; validators green.
- Unchanged: **G1–G6 are still the Director's, and R and S still have no C++.**

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 23:10 UTC | END ] -->
