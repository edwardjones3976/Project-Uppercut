<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:45 UTC | START ] -->

# The sweeps were measuring the wrong thing — a confound that invalidates the framing

**2026-08-05.** Commitment frames were the last candidate: the thing that
actually sets work rate, authored per move, never examined as an economic
control. Swept as a sensitivity test, 24 seeds, three rounds:

| commitment | thrown | blocks | end stamina | knockdowns | decisions |
|---|---|---|---|---|---|
| ×1.0 (canon) | 2,457 | 853 | 28.7 | 99 | 0 |
| ×1.5 | 2,452 | 862 | 27.1 | 103 | 0 |
| ×2.0 | 2,392 | 775 | 29.3 | 106 | 0 |
| ×3.0 | 2,243 | 730 | 26.2 | 102 | 0 |

**Tripling commitment reduced punches thrown by 8.7%.** That is not a connected
dial either — and three inert dials in a row is not three coincidences. It is a
sign the instrument is wrong.

## The confound

Every bout in every one of these sweeps **ends inside round one on the
three-knockdown rule.** Bout length is therefore not fixed: it is however long it
takes to produce three knockdowns. And since the knockdown conversion rate per
landing is roughly constant across all these variations, every bout ends after
roughly the same number of landed punches.

So the totals I have been comparing — punches thrown, blocks, knockdowns — are
not measuring what each dial does to a fighter. They are measuring **how many
punches fit into a bout that always ends at the same place.** Turn any dial and
the bout simply takes more or less wall-clock time to reach the same three
knockdowns, while the totals barely move.

That explains cadence being flat. It explains commitment being flat. It probably
explains part of the tier result too. Three "the dial is inert" findings collapse
into one "the measurement was normalised by its own outcome" finding.

## What the correct metrics are

Not totals. Per-opportunity rates and elapsed time:

- **knockdown conversion**: knockdowns ÷ landings eligible to cause one
  (solid or clean, to jaw or head). This is the number the 0.57 threshold
  actually governs.
- **ticks to first knockdown** and **ticks to stoppage** — how long the fight
  lasts, which is what a dial should change.
- **stamina at a fixed tick**, not at bout end, so bouts of different lengths are
  comparable at all.

The last of those is the one that hurts most in hindsight: "end stamina 23–30
across every tier" looked like a floor, and it may simply have been every bout
ending at the same *point in its own arc*.

## Status, honestly

The measurements taken today are not wrong, but several of the **conclusions
drawn from them are unsafe**, specifically every claim of the form "dial X is
inert." The correct statement is weaker: dial X does not change the totals in a
bout that terminates on a knockdown count. Whether it changes the fight is
untested.

The one finding that survives intact is the pressure decomposition, because it
measured per-knockdown terms rather than totals: stamina contributes 2.74×
median inflation and condition 1.17×, and those are ratios at the moment of the
event, immune to this confound.

**Next session starts here:** re-run the tier and commitment sweeps against
conversion rate and ticks-to-stoppage, and re-read the "inert dial" conclusions
against the results. I would not act on any of them until that is done.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 03:10 UTC | resolution START ] -->
**RESOLVED, same night.** The re-run is done, in
`2026-08-05-the-dials-were-never-inert-and-the-blocker-has-a-number.md`. Three of
the four "inert dial" conclusions were artifacts: cadence spans 1.88× and
commitment 2.18× in ticks-to-stoppage. What is actually flat across every sweep
is `kd/eligible`, which is why no volume dial could ever have reached the cards —
the bout needs a conversion of 0.0139 and the model produces 0.2654.
<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 03:10 UTC | resolution END ] -->

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 01:45 UTC | END ] -->
