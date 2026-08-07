<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 17:15 UTC | START ] -->

# What the integrated schema has to absorb

Decision 0022 rules that the integrated bout gets its own contract, its own
stream, and **named RNG substreams** derived from the bout seed. This is a
survey of what stands between here and that, measured rather than estimated,
taken before anyone starts integrating.

Nothing here is a proposal. It is a count, and one of the two counts is worse
than the phase-record notes suggest.

## The reader sprawl is smaller than it looks

`tests/test_live_arena_is_one_implementation.py` pins six phases parsing
movement canon inline. Reading that number cold, the natural fear is six
independent opinions about what canon says. The containment says otherwise.

| reader | fields | canon files |
|---|---|---|
| `CoreConditionCommandlet` | 73 | 9 |
| `BoutDirector` | 59 | 8 |
| `CoreGuardCommandlet` | 59 | 8 |
| `CoreSweepCommandlet` | 56 | 8 |
| `CoreLoopCommandlet` | 37 | 5 |
| `CoreProbeCommandlet` | 5 | 0 literal |

Union: **78 field names across 9 canon files.** But the sets are largely
*nested*, not parallel — `CoreCondition` strictly contains Guard, Sweep and
Probe; Guard strictly contains Sweep and Probe; Sweep contains Probe. The
genuinely reader-specific fields are few and nameable:

- `BoutDirector` alone: `hand`, `reference_reach_span_m`, `spatial_units`
- `CoreLoopCommandlet` alone: `key`, `range_band`
- `CoreGuardCommandlet` (vs BoutDirector): `committed_defense`, `evasions`,
  `guard_extent_multiplier_while_committed`

So an integrated loader is one reader over the union, plus a handful of
phase-specific fields — closer to a merge than a reconciliation.

**The honest limit of this measurement.** It extracts field *names* from
`Get*Field(TEXT("..."))` calls. It shows which names each file mentions. It does
**not** show that two files interpret the same name identically, and that is
exactly where a silent disagreement would live — two readers both reading
`stride_length_ru`, one applying a multiplier the other does not. Establishing
that requires reading the six, and it is the work the integrated loader has to
do properly rather than a number this survey can supply.

## The RNG is the real blocker, and it is not counted anywhere

Decision 0022 requires deterministic **named substreams**, one per subsystem,
and states that "a subsystem may consume only its own authoritative stream" and
that adding a cosmetic draw may not silently move knockdown, judging or contact
outcomes.

Against that requirement:

```text
LCG multiplier  1664525        8 files
LCG increment   1013904223     8 files
FNV-1a prime    1099511628211  8 files
```

`BoutDirector`, `CoreConditionCommandlet`, `CoreGuardCommandlet`,
`CoreLoopCommandlet`, `CoreProbeCommandlet`, `CoreSweepCommandlet`,
`EvadeSession`, `RangeCore` each carry their own copy of the decision draw.
Eight independent implementations of "the next random number", each currently
correct about its own phase, and none of them derived from a named substream
because no substream layer exists yet.

This matters more than the reader sprawl for three reasons.

First, **it is the next order item.** Named RNG substreams sit directly after
the integrated schema in the convergence sequence. Eight private draws is the
thing that has to become one seeded, versioned derivation.

Second, **it is the seam Decision 0022 explicitly protects.** The ruling's
prohibition — a cosmetic draw may not move a knockdown — is unenforceable while
eight files each advance their own generator. There is nothing to enforce it
*on*.

Third, **the existing guard is narrower than it reads.**
`test_the_subsystem_does_not_reimplement_the_loop` asserts the LCG constants are
absent from `UppercutFightSubsystem.cpp`. That is a real and useful guard, and
it covers one file. Nothing counts the other eight, so a ninth copy arrives
silently.

That last gap is closed by this change: the counts are now pinned the same way
the reader sprawl is, so growth has to be deliberate.

## What this does not claim

- It does not claim the eight LCG copies currently disagree. Each phase is
  proven against its own contract, so each is right about the fight it
  describes. They are a blocker for *unification*, not evidence of a present
  defect — the same distinction the reader-sprawl test already draws.
- It does not propose a substream derivation. That is Decision 0022's to
  specify and the Director's to approve; deriving one here and letting it
  become fact by being first is precisely what the convergence note warns
  against.
- It measures no gameplay and moves no pin.

## Suggested order, for whenever the integrated schema starts

1. One canon loader over the 78-field union, replacing the six inline readers,
   proven by every phase reproducing its existing hash.
2. One seeded RNG with named substreams, replacing the eight private copies,
   which **will** move every stream by construction — new integrated pins, per
   Decision 0022's re-blessing policy, never a re-bless of the unit pins.
3. The integrated contract on top of both.

Step 1 is provably inert and can be done first. Step 2 cannot be, and that is
the point at which the new evidence begins.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 17:15 UTC | END ] -->
