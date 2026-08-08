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

**The honest limit of that measurement.** It extracts field *names* from
`Get*Field(TEXT("..."))` calls. It shows which names each file mentions. It does
**not** show that two files interpret the same name identically, and that is
exactly where a silent disagreement would live.

## So the interpretation was checked too, and it found one

The parsing sites were pulled and compared field by field against the extracted
`UppercutRangeCanonLoader` — the reader Phase Q's chain already went through
this exercise to produce.

The result is reassuring in the way that matters: the six are **copy-paste
descendants of one reader**, not independent interpretations. For shared fields
the parsing is textually identical modulo variable names. `rope_retreat_multiplier`,
`axis_length_ru`, `back_to_ropes_ru`, `min_center_distance_ru` and the band
walk all read the same way in all seven files. The fixed-point conversion

```cpp
int64 Q(double V) { return (int64)FMath::RoundToDouble(V * 10000.0); }
```

is byte-identical in all five private copies and in the reference;
`CoreProbeCommandlet` has no `Q()` and inlines the same expression.

**One real divergence exists**, and it is representational:

| | unbounded top band (`out_of_range` authors no `max_ru`) |
|---|---|
| the six inline readers | `(int64)990000` — a ceiling at 99.0 ru |
| `UppercutRangeCanonLoader` | `FUppercutRangeCanon::Unbounded == -1` — no ceiling |

Those are different statements. They agree on every fight *only* because the
ring caps separation: `ring.track.axis_length_ru` is **4.92**, so `Sep < 990000`
always holds and both resolve the top band identically. Verified against canon
rather than assumed.

Two consequences.

The equivalence is presently an **accident of the ring being small**, and
nothing stated it. A canon edit growing the ring — or shrinking
`reference_reach_span_m`, which is the same thing in reach units — would make
five phases disagree with Phase Q about which band a fighter is in, silently.
`test_the_two_unbounded_band_sentinels_still_agree` now pins that invariant, so
the coupling fails loudly instead.

And the unified loader has to **choose**. Picking `-1` is the better statement
of what canon means, and it requires auditing every arithmetic use of `BandHi`
across all six: `BandHi[i] - BandLo[i]` yields a sensible width under the 990000
sentinel and nonsense under `-1` unless guarded, which is exactly why
`UppercutRangeCore.cpp` guards it today and the six do not have to.

That is the whole decision content of step 1. One sentinel, one audit.

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
   proven by every phase reproducing its existing hash. Its only real decision
   is the unbounded-band sentinel, and the audit that choice implies.
2. One seeded RNG with named substreams, replacing the eight private copies,
   which **will** move every stream by construction — new integrated pins, per
   Decision 0022's re-blessing policy, never a re-bless of the unit pins.
3. The integrated contract on top of both.

Step 1 is provably inert and can be done first. Step 2 cannot be, and that is
the point at which the new evidence begins.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 17:15 UTC | END ] -->
