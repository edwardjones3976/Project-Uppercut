<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:20 UTC | START ] -->

# Wind/Reserve in the shared runtime

Decision 0021, Director order step 13. The two-tier economy now runs in C++ and
reproduces `tools/uppercut_stamina/economy.py` exactly.

## What "proven" means here

The C++ replays sixteen trajectories out of `tests/fixtures/stamina_vectors.json`
and every checkpoint and endpoint matches in q10000 integers. Not approximately
and not "within a tick": a one-unit-per-tick drift reads correct at tick 1 and
is a whole round wrong by the twelfth, and an end-of-run total can hide a
cancelling pair of errors that a mid-run checkpoint cannot.

It also refuses three states that both implementations must refuse, and checks
the two declared floors and the Reserve interval on **every tick of every
case** rather than once each. A floor that holds in the single scenario written
to test it, and is never looked at again across 10800 ticks of the others, is
not a floor.

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
not have to rediscover why the claim went away. The vector that *did*
discriminate is described below, and Decision 0025 has since removed the input
that made it discriminate at all.

**Five invariants enforced by nothing.** `data/stamina_economy.json` named
`tools/uppercut_validate/stamina.py::<fn>` as the enforcer of each of its five
invariants. The module did not exist. That is worse than an unchecked rule with
no claim attached, because `enforced_by` is exactly what a reviewer reads to
decide they need not look further. The validator is written and wired into
`cli.py`, and `tests/test_enforced_by_resolves.py` now fails if any canon file
anywhere names a Python enforcer that cannot be imported.

## Reserve exhaustion: the seam, and how Decision 0025 closed it

**Status: resolved.** The Director ruled on 2026-08-07
(`docs/decisions/0025-reserve-exhaustion-semantics.md`). This section records
what was found, what was ruled, and what now holds it.

### What the first port exposed

`FUppercutStamina::Step` computed the Reserve-derived recovery multiplier
**before** Reserve was clamped at zero. A tick that spent past empty therefore
divided a negative numerator — the one place in this economy where Python's
`//` and C++'s `/` disagree. Measured rather than assumed: across reserve in
`[-199, -1]` the two produced 23 and 24 units of rest recovery respectively. A
port using `/` would have gained one unit of Wind per such tick and read
correct in every other vector in the file.

Worse than the divergence, and the reason it became a Decision rather than a
bug fix: canon declares `recovery_from_reserve.floor_multiplier: 0.40` as a
floor, and a momentarily negative Reserve drove the computed multiplier
**below** it — 3997 against a declared 4000 at the worst reachable value. Small,
bounded, and still a declared bound being crossed by arithmetic nobody
authorised.

### The ruling

Reserve is authoritative on the closed interval `[0, max]`. A fighter **may**
throw the action that empties the tank — the punch is not retroactively
cancelled because its `reserve_load` exceeds the balance — but the stored value
saturates at zero **immediately after the debit**, before any Reserve-derived
formula reads it. The declared floors are therefore true lower bounds rather
than suggestions that disappear when arithmetic underflows.

The Director's reasoning is worth keeping next to the code: cancelling the
punch would introduce an invisible energy-credit check that vetoes an already
legal boxing action. A deeply fatigued fighter can still sling a desperate
right hand. The punishment belongs afterward — a lower Wind ceiling, slower
recovery, worse late-round options — not in a hidden veto. Negative Reserve is
not "extra tired"; it is an invalid state.

Externally supplied state outside the interval is **refused, not normalised**.
Quietly clamping an invalid input would make a corrupt save, a bad fixture or a
mis-wired caller indistinguishable from an exhausted fighter.

### What holds it

Eight proofs, in both languages, plus a Python-only suite so the rules stay
checked on a machine with no engine at all
(`tests/test_reserve_exhaustion.py`, 54 tests).

| # | proof | where it is checked |
|---|---|---|
| 1 | exact spend to zero agrees | `d0025_1_exact_spend_to_zero` |
| 2 | overdraw saturates identically | `d0025_2_overdraw_saturates` |
| 3 | stored Reserve never negative | **every tick of every case** |
| 4 | recovery floor never breached by underflow | **every tick of every case** |
| 5 | Wind ceiling floor never breached | **every tick**, plus `d0025_5_ceiling_holds_at_empty` |
| 6 | negative external Reserve rejected | three `rejection_cases` |
| 7 | corner cannot exceed `reserve.max` | `d0025_7_*`, plus a runtime assert |
| 8 | telemetry keeps the *requested* load | `d0025_8_*`, telemetry per checkpoint |

Proofs 3, 4, 5 and 7 are deliberately continuous rather than one vector each.
An invariant that is only examined in the scenario written to test it is not an
invariant; it is an anecdote.

Proof 8 is the one that is easy to under-build. A fighter holding 0.5 who
throws a 2.0-load punch must not be recorded as having spent 0.5 — he ran out
of tank, and every later reading of what the fight took out of him would
otherwise be a number the economy invented rather than one it charged. The step
therefore reports `requested_reserve_load`, `sustained_exertion`,
`reserve_applied` and `reserve_unpaid` separately, and the C++ must reproduce
all of them.

The vector that used to discriminate `//` from `/` is **kept**, renamed
`overdraw_then_recover`. Its divergent input can no longer occur, so it no
longer discriminates — but it is the exact state that used to be wrong, and an
edit that reintroduced the unclamped read would move its number. Deleting a
regression vector because the regression is fixed is how the regression comes
back.

## Scope

This mints **no integrated evidence**. It is a unit contract for one subsystem,
in the same shape as the canon-hash parity proof. No integrated golden bout, no
stamina calibration, no lateral guard work, no named fighters.
`calibration_status.values_are_fitted` remains `false`, and the 65-punch case is
labelled a sanity probe in the file it lives in — Decision 0024 was explicit
that punch-count numbers prove nothing until observable CPU policy exists.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 08:20 UTC | END ] -->
