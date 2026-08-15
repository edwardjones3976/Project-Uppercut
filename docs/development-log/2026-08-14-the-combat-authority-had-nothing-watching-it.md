<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 10:40 UTC | START ] -->

# 2026-08-14 — the combat authority had nothing watching it

**Head:** `main` @ `86d3ef1`
**Binary:** `UnrealEditor-UppercutCore.dll` built 2026-08-12 23:05 UTC. Not
rebuilt for this work — the Director's editor was open. The only commit newer
than the binary (`6f82f6c`) touches `UppercutMatchDirector` and
`UppercutFighterBase` pose-capture presentation; `UppercutFightSession.cpp` is
current with the build.

## What was found

Decision 0040 R1 made the shared C++ `INTEGRATED_1R` session the combat
authority. It was the only artifact in this repository with no pin, no
analyzer and no test:

- `prove_live_arena` passes `-integrated=0` — deliberately, because it pins the
  Phase Q distance contract;
- `tools/engine/golden.py` covers phases O, Q and R;
- `tests/test_integrated_arena_analyzer.py` and `tests/test_thin_policy_mirror.py`
  appear in `tests/__pycache__/` as `.pyc` files with no `.py` beside them.

That last point was initially read here as "the tests were deleted". It is not
what happened, and the truth is worse. Both tests exist — on
`feat/authenticity-program`, the branch Decision 0040 R6 put on **HOLD** as not
merge-ready. The `.pyc` files are leakage from an earlier checkout of it. So the
integrated arena did have a checker written for it, on a branch nobody reviewing
`main` would find, which is the failure mode this project already wrote down:
*work on an unmerged branch does not exist to anyone reviewing the project.*

The cost was already on the record, unnoticed. Decision 0040 quotes the C++
round at `punches=123 landed=51 kd=0-0` for seed 4242 over 10800 ticks. The same
configuration on this head produces:

    S|rows=9106|fnv=90a660783330ee69|ticks=10800|punches=153|landed=153|result=decision|cards=10-9|kd=0-0

Whether that is a build difference or a behaviour change is not established
here. What is established is that no gate could have reported it.

## What the fights say

Three runs of the authority, now pinned:

| seed | ticks | punches | landed | slipped | wrong band | kd | result |
|---:|---:|---:|---:|---:|---:|---:|---|
| 4242 | 10800 | 153 | 153 | 0 | 0 | 0–0 | decision 10–9 |
| 777 | 10800 | 166 | 166 | 0 | 0 | 0–0 | decision 10–9 |
| 4242 | 1200 | 80 (+1 in flight) | 80 | 0 | 0 | 0–0 | decision 10–9 |

**399 punches thrown across 22,800 ticks and 399 of them landed.** Not one miss,
not one slip, not one punch from the wrong band. Two independent lines of
evidence explain it:

1. `FUppercutFightSession::ResolvePunches` only consults the evade core when the
   defender's last action begins with `slip` or `roll`
   (`UppercutFightSession.cpp:217`). The action vocabulary the thin policy
   actually emits across all three streams is `observe`, `rest`, `hold`,
   `step_in`, `step_out` and punches — nothing else. The `evaded` branch is
   unreachable through this policy rather than rare.
2. `trace_integrated_divergence` confirms it from the other side: the C++ policy
   never emits the `Evade` tactic in a full round. Python does.

Guard is not consulted at all, and `force` is a per-fighter constant (5650 and
4962) with no variance across a whole round.

**The round is also over long before the bell.** After the first minute, 3446 of
3478 decisions are `RECOVER_WIND`; across the round both fighters rest or
observe 93% of ticks. Punches land 108 in the first 30 seconds and 6 in the
last 30.

None of this is asserted to be wrong. Decision 0040 R3 already holds that
neither runtime's outcome is authentic, and Issue #12 owns the integration work
that would change it. It is recorded so that the next change to the round is
made against a written starting point instead of a memory.

## Decision 0040 prerequisite #2, answered

> The first C++/Python divergence traced. Not the totals — the first tick where
> the two runtimes make different decisions from the same seed.

At seed 4242 over one round:

- C++ emits 4476 decisions, Python 5730. Python decides for both fighters every
  tick from tick 1; C++ decides for one fighter roughly every other tick from
  tick 0.
- **1038 decisions land on the same (tick, fighter) and can be compared.**
- **Zero of the 1038 are identical.** The first is at tick 4: C++ has
  `red_corner` throwing `uppercut_rear` on `PUNISH_RECOVERY`; Python has the
  same fighter retreating `step_out` on `EXIT_BAD_RANGE`.

The vocabularies are not the same vocabulary. C++ uses 4 reason codes in a full
round; Python uses 8, of which it shares 3. C++'s dominant code — `RECOVER_WIND`,
94% of its decisions — is one Python never emits at all. Python's `Evade` tactic
has no C++ counterpart in practice.

So the answer to prerequisite #2 is not a tick number. **The two runtimes never
agree once, and they are not the same policy with different tuning.** Any plan
that treats convergence as calibration is mis-scoped, which is what R5's freeze
on `pressure_threshold` was protecting against.

## What was built

| Path | What it is |
|---|---|
| `tools/engine/analyze_integrated_arena.py` | reads an `INTEGRATED_1R` stream back and checks it cannot be lying to itself — grammar, tick order, punches that were thrown before they resolved, trailer against rows, verdict against knockdowns, 10-point-must arithmetic |
| `tools/engine/prove_integrated_arena.py` | runs the authority headless at three configurations and diffs against the pins, rendering drift as a fight |
| `tools/engine/trace_integrated_divergence.py` | the projection above, aligned on `(tick, fighter)` |
| `docs/phase1a/golden/integrated_1r_*.stream` | the three recordings |
| `tests/test_integrated_arena_analyzer.py` | 37 tests; every check the analyzer makes is mutation-proven |
| `tests/test_integrated_divergence_trace.py` | 5 tests holding the tracer's alignment honest |

**This pin is weaker than the O/Q/R pins and says so in its own docstring.**
Those are pins on an analyzer that predicts the bytes, so they check without an
engine. Decision 0040 R2 forbids the equivalent here: a Python module that could
predict these bytes would be the second implementation of the rules that the
convergence rule exists to prevent. These are recordings. They prove the
authority still produces the fight it produced, and that the fight is internally
coherent. They cannot prove it is good boxing, and nothing here encodes an
opinion that it is.

**The guard was verified rather than assumed**, the way the Phase Q guard was:
one pinned row was changed from `landed` to `evaded`, `prove_integrated_arena`
was re-run and reported

    DRIFT  seed=4242  ticks=1200   first difference at line 356
        arena  tick 1195: fighter 0 LANDS hook_lead (force=5650)
        pin    tick 1195: fighter 0 throws hook_lead and it is slipped

exiting non-zero; the row was restored and the pin proved again at
`sha256=fc67e039…`. Note which layer caught it: an `evaded` row is perfectly
coherent, so the coherence checker passed it and only the bytes objected. That
is why both layers exist.

## A collision, found after the work was written — needs a Director call

`feat/authenticity-program` already carries files with **three of the same
names**: `tools/engine/analyze_integrated_arena.py`,
`tools/engine/prove_integrated_arena.py`, and its own pinned streams under
`tools/engine/golden_integrated_arena/`. This was discovered after the versions
above were written, not before, and it is recorded that way round on purpose.

They are not the same thing, and the difference is checkable:

| | held branch (`4da11ba`) | here |
|---|---|---|
| `analyse()` | 7 shallow checks: header phase, cards row, trailer present and keyed, result in a known set, body non-empty | grammar and arity, tick order, punch thrown before it resolved, action authorised by a decision, trailer against rows, verdict against the knockdown rows, count sequence, 10-point-must arithmetic |
| proven to catch anything | no mutation tests | 37 tests, one per check |
| goldens | `tools/engine/golden_integrated_arena/` | `docs/phase1a/golden/`, beside O, Q and R |
| `repo=` normalisation | rewritten to the **local** path — portable "across checkouts on the same machine layout" | rewritten to a fixed `<repo>` token — portable across machines, including the runner in Issue #14 |
| divergence trace | none | `trace_integrated_divergence.py` |

Despite the name, the held branch's `expected_stream()` does not predict
anything either — it reads its golden back. Both versions are recordings; this
one checks far more of what it records and is portable off this laptop.

**This is not merged away.** Two implementations of one rule that agree until
one is edited is the defect this repository spends most of its discipline
avoiding, and it has already paid for the governance version of it once
(Decision 0038, and the twice-numbered 0014). Whoever takes
`feat/authenticity-program` off HOLD should **delete its three files rather than
merge them**, and the two concrete things not to carry across are the
`golden_integrated_arena/` location and the machine-local normalisation. If the
Director prefers the branch's versions instead, then these three should go — but
one of the two must, and by a decision rather than by whichever lands first.

## Two defects found in passing, not fixed here

Both are in C++ and this work did not rebuild, so neither was touched.

1. **`UppercutRoundCore.cpp:126` — `SealDecision` sets `bCardsSealed = false`.**
   The flag initialises to `true` and is set `true` on reset, so sealing a
   decision is the one thing that unsets it. Nothing reads it today, which is
   the only reason it is harmless.
2. **`SealDecision` scores a drawn round 9–9.** In the 10-point-must system an
   even round is 10–10; knockdowns are then subtracted. Scoring it 9–9 also
   changes what a knockdown costs on a drawn round. The path is untaken in all
   three pinned runs, so `analyze_integrated_arena` does not fail on it — it
   checks that the winner of a round scored 10 minus knockdowns against, which
   is the invariant the taken path does satisfy.

A third is an evidence-lane defect rather than a rules one: **the authoritative
header carries `repo=<absolute path>`**, so the same fight produces different
bytes in a different checkout. `prove_integrated_arena` normalises that one
field and declares the normalisation; the durable fix belongs to whoever owns
the header, and it matters for the self-hosted Windows runner in Issue #14.

## Gates

    python -m pytest -q                          1479 passed
    python -m tools.uppercut_validate.cli all     RESULT: OK
    python -m tools.engine.golden --diff          O, Q, R all match
    python -m tools.engine.prove_integrated_arena PROVEN x3

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-14 10:40 UTC | END ] -->
