<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:30 UTC | START ] -->

# The integrated contract: identity and partitioned randomness

Decision 0022, and R4 items 1 and 2 of the 2026-08-07 Director state review.
This is the foundation the rest of the integrated bout is built on: a versioned
contract that owns its own identity, initial state, canon hashes and
randomness. No combat behaviour is implemented here and none is implied.

## The fork, and the call

The earlier survey framed step one as *unifying the six inline canon readers* —
`BoutDirector`, `CoreCondition`, `CoreGuard`, `CoreLoop`, `CoreProbe`,
`CoreSweep`. Re-reading Decision 0022 against R4, I think that framing was
wrong, and the work here takes the other branch.

**Those six are frozen historical artifacts. The live simulation never runs
them.** The convergence rule says an implementation must be *reusable by the
shared live simulation without copying its rules*. It does not say every
commandlet ever written must be retrofitted. Retrofitting six proven artifacts
buys the live bout nothing, risks six pins, and delays the thing R4 actually
orders.

So: the integrated contract gets **one** implementation, written once, and the
frozen phases are left alone. That is the same reasoning applied to I, J and L
during the 2026-08-08 header repair — they were left untouched precisely
because changing them would have created drift rather than removed it.

The duplication that matters is the duplication the *live* runtime would carry.
There is none: this package imports the existing canon header builder rather
than growing a second one, and a test forbids it from importing phase analyzer
code at all, so an edit here cannot move a unit pin.

## Randomness is partitioned by name

Decision 0022's promise is a negative one:

> A subsystem may consume only its own authoritative stream. Adding a cosmetic
> draw or changing policy cadence may not silently move knockdown, judging, or
> contact outcomes.

Negative promises rot quietly, because nothing fails when they break — the
fight simply becomes a different fight while every existing test still passes.
Against a single shared generator the promise is not merely unenforced, it is
unenforceable: every draw is a side effect on every other subsystem.

So each of the seven substreams is a genuinely separate generator, seeded by

```text
sha256( derivation_version | contract_version | bout_seed | name )
```

over **length-prefixed** fields. The prefixes are not decoration: without them
`("ab","c")` and `("a","bc")` derive the same stream, which is the same
aliasing defect the RFC 6901 canon pointers were bitten by on 2026-08-07.

Derivation takes the **name**, never a position. Decision 0022 says iteration
order may not determine random ownership, and an index is iteration order
wearing a number. A test shuffles the declaration order and asserts every seed
is unchanged.

`BoutRng` deliberately exposes no way to draw without naming an owner — no
`next`, no `random`, no default stream. A test asserts those methods do not
exist, so the shared-cursor habit cannot return one convenience method at a
time.

## What is proven, and what is only started

Decision 0022 lists seven required assertions. Three have real coverage now:

| # | assertion | state |
|---|---|---|
| 1 | same seed and initial state reproduce byte-identically | header layer covered |
| 2 | different seeds create non-vacuous variation | covered, including that the *substreams* differ and not merely the recorded seed line |
| 4 | no system reads another's private draw | partially — authority is declared per stream and visible in the artifact |

Four cannot be tested until their subsystems exist, and they are named in
`tests/test_integrated_contract.py` with a test that keeps them named:
assertion 3 (all event families in one stream), 5 (pause/speed/camera not
altering authority), 6 (one runtime for commandlet and live arena), 7 (a bout
ending by stoppage or decision).

That list is deliberate. "The integrated contract has tests" must never be
read as "the integrated contract is proven", and the only reliable way to stop
that is to make the gap a thing the suite asserts.

## Deliberately absent

No combat rules. No CPU policy. No tuning of anything. `values_are_fitted`
remains false everywhere, and this file introduces no number that a fight
depends on beyond the declared round structure.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 07:30 UTC | END ] -->
