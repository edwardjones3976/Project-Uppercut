<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:20 UTC | START ] -->

# Wind/Reserve in the shared runtime

Decision 0021, Director order step 13. The two-tier economy now runs in C++ and
reproduces `tools/uppercut_stamina/economy.py` exactly.

## What "proven" means here

The C++ replays nine trajectories out of `tests/fixtures/stamina_vectors.json`
and every checkpoint and endpoint matches in q10000 integers. Not approximately
and not "within a tick": a one-unit-per-tick drift reads correct at tick 1 and
is a whole round wrong by the twelfth, and an end-of-run total can hide a
cancelling pair of errors that a mid-run checkpoint cannot.

The scenario scripts travel **in the fixture**. The commandlet replays what it
is handed rather than re-declaring what "a professional round" or "the corner"
means, because two copies of a scenario is the same defect as two copies of a
rule: they agree until one is edited, and the edit that matters is the one
nobody mirrors.

Run it with `python -m tools.engine.prove_stamina_parity`. That script also
recomputes every case from the contract before it starts, so a fixture
hand-edited to match a broken implementation still fails — the fixture is a
cache of the contract's answers, not a second authority.

## Three things found on the way

**Case-insensitive move ids.** `TMap<FString, ...>::Find` compares and hashes
case-insensitively in Unreal; Python's `dict` does not. `Jab_Lead` collected
`jab_lead`'s price, which means the two implementations disagreed about which
ids canon declares. The move's authored spelling is now carried in the value
and the lookup confirms the case the map actually matched, and two ids
colliding case-insensitively fail at load rather than silently sharing a row.
This is the same operator that bit the canonicalizer on 2026-08-07, caught the
second time before it cost anything.

**An overclaim, corrected in place.** The displacement vector's comment claimed
its integers were chosen so the two languages would differ if the port used
`/`. They cannot be: every operand on that path is positive, and floor and
truncation agree on positive operands. The case proved less than it said it
did. Recorded in the file rather than quietly deleted, so a later reader does
not have to rediscover why the claim went away.

**Five invariants enforced by nothing.** `data/stamina_economy.json` named
`tools/uppercut_validate/stamina.py::<fn>` as the enforcer of each of its five
invariants. The module did not exist. That is worse than an unchecked rule with
no claim attached, because `enforced_by` is exactly what a reviewer reads to
decide they need not look further. The validator is written and wired into
`cli.py`, and `tests/test_enforced_by_resolves.py` now fails if any canon file
anywhere names a Python enforcer that cannot be imported.

## The floor-versus-truncate seam, and an open contract question

`FUppercutStamina::Step` computes the Reserve-derived recovery multiplier
**before** Reserve is clamped at zero. A tick that spends past empty therefore
divides a negative numerator, which is the one place in this economy where
Python's `//` and C++'s `/` disagree. Measured rather than assumed: across
reserve in `[-199, -1]` the two produce 23 and 24 units of rest recovery
respectively. A port using `/` would gain one unit of Wind per such tick and
read correct in every other vector in the file. `negative_intermediate_reserve`
pins it.

That seam is closed. The question it exposes is not:

> Should recovery be read off an unclamped negative Reserve at all?

Canon declares `recovery_from_reserve.floor_multiplier: 0.40` as a floor. When
Reserve is momentarily negative the computed multiplier drops **below** that
floor — to 3997 against a declared 4000 at the worst reachable value, since the
largest authored `reserve_load` is 0.060 against a pool of 100. The breach is
small and bounded, and it is still a declared bound being crossed.

Three readings, and the choice is the Director's because it is a canon call,
not an implementation detail:

1. **Clamp Reserve before computing recovery.** The floor means what it says.
   Costs: the vector moves, and a fighter who spends past empty gets a
   fractionally better tick than he does today.
2. **Leave it.** Overdraft is real: a man who spent more than he had is worse
   off than a man who spent exactly what he had. Then the floor is documented
   as a floor *on non-negative Reserve*, and canon says so.
3. **Refuse the overdraft.** A move that cannot be paid for is not thrown.
   Largest consequence, and it belongs to the policy layer rather than here.

Nothing is being changed on my own authority; the current behaviour is pinned
and the question is raised rather than averaged away.

## Scope

This mints **no integrated evidence**. It is a unit contract for one subsystem,
in the same shape as the canon-hash parity proof. No integrated golden bout, no
stamina calibration, no lateral guard work, no named fighters.
`calibration_status.values_are_fitted` remains `false`, and the 65-punch case is
labelled a sanity probe in the file it lives in — Decision 0024 was explicit
that punch-count numbers prove nothing until observable CPU policy exists.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:20 UTC | END ] -->
