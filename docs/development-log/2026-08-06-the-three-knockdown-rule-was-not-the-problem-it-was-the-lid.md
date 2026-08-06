<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 07:30 UTC | START ] -->
# The three-knockdown rule was not the problem. It was the lid.

**2026-08-06.** Decision 0018 made rulesets named, versioned data and set the
professional rulebook — which has no three-knockdown rule — as the default. The
contract now reaches the cards in **24 of 24 bouts**. It reached them in **0 of
24** before.

That sentence is true and it is the least interesting thing in this entry.

## The measurement

`tools/engine/measure_ruleset_effect.py`. Same contract, same seeds, same code
path; the only difference is which rulebook the bout ran under.

    24 bouts x 3 rounds, seeds 4242..4265

                              professional     arcade
      reached the cards                 24          0
      stopped                            0         24
      knockdowns                      1648         96
      rounds completed                  72         24
      knockdowns per round           22.89        4.0

## What it actually says

**Twenty-three knockdowns per round.** Not three, not five. A fighter is being
put down roughly every eight seconds of round time and getting up each time,
because nothing stops him any more.

`decision_path_must_survive` — the invariant that has held Phase O since
2026-08-04 — is now satisfied, and it is satisfied **for the wrong reason**. The
bout survives to the cards because nothing ends it, not because the fighters
survive it. That is a different thing and it should not be reported as progress.

The two numbers that looked like separate facts all week were always one fact:

> **"0 of 24 reach the cards" and "23 knockdowns per round" are the same
> measurement, seen from either side of the stoppage rule.**

The three-knockdown rule was not causing Phase O's problem. It was the lid on
it. Removing the lid did not fix anything; it made the size of the thing visible.

And the thing was already measured, on 2026-08-05: **conversion at 0.3196
against the reference's 0.1148 — 2.78×.** That number was correct, it was taken
against the contract rather than a harness, and it survives this ruling
untouched. What has changed is that the consequence is now impossible to miss.

## What this ruling did earn

- **A bout can now end by decision.** The scoring path, the sealed cards and the
  verdict row have never executed in a completed bout before today; they now do,
  in every bout of the sweep. Whatever else is wrong, that path is live.
- **Every stream says which rulebook it ran under** (`H|ruleset`,
  `H|ruleset_version`, `H|canon_ruleset`). A replay whose ruleset is unknown is
  not a replay, it is a coincidence.
- **The arcade rule is kept, not deleted.** Decision 0018's point was never that
  three-knockdown is wrong for an arcade boxing game. It was that choosing it
  silently, for every fight, was.
- **Every stoppage figure quoted the week of 2026-08-03 is now re-runnable
  against either rulebook**, which is what those figures needed and could not
  have, because there was only one rulebook.

## An implementation note worth keeping

`condition_model.knockdown.max_per_round` and `max_per_bout` did not move.
Sealed Phases N and K read them and re-proving those phases again for a field
Phase O no longer consults would be pure churn. So they stayed, and a validator
now holds them equal to the **arcade** ruleset — because the arcade rules are
what those two fields were describing all along. Same shape as Decision 0014's
step cost: one authority, one checked echo, and no way for the two to drift
apart quietly.

## What is next, and what it is not

Not another termination rule. The next lever is conversion, and the two rulings
already recorded that bear on it are **G2** (rest and no-action outcomes) and
**G3** (aggression as intent rather than throw rate) — both of which reduce how
often a fighter acts, which is where the stamina economy and therefore the
pressure term actually live.

One thing found while scoping G2 and worth stating before it is rediscovered:
**G2 is not separable from G3.** Canon authors three regeneration rates by
activity (`regen_per_tick_idle` 0.004, `_moving` 0.0018, `_throwing` 0.0) and
the core currently uses one of them; fixing that is real but small. The large
half of G2 — a fighter who reconsiders without acting — only changes a fight if
something *decides* to think rather than act, and that decider is G3's staged
policy. Implementing G2 alone would be close to a no-op dressed as a ruling.

They land together, or they do not land.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 07:30 UTC | END ] -->
