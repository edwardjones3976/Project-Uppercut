<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:26 UTC | START ] -->

# The matched pair: `generic_pressure_a` vs `generic_range_b`

Two authored generic fixtures, written so that the one-round CPU-vs-CPU test
match has two fighters a viewer can tell apart **from behaviour**, not from a
nameplate.

- `fixtures/fighters/legal/generic_pressure_a.json`
- `fixtures/fighters/legal/generic_range_b.json`

They live under `fixtures/fighters/legal/` and not `data/fighters/`, because
there is deliberately no `data/fighters/` — a roster is Phase 1B and an empty
directory is an invitation. `legal/` is not a euphemism here: the validator
sweeps that folder and asserts every card in it passes Rule 10, so these two
get the whole economy check for free on every run.

## What was wrong before

Every Rule 10 check in the repository judged **one** card in isolation. Nothing
required two cards put in a ring together to differ at all. Two byte-identical
cards were a legal matchup, and the live C++ fighters were exactly that:
identical empty cards, every multiplier 1.0. "Press Play and tell the fighters
apart" was not something the repository could fail at, because it was not
something the repository asserted.

## The two shapes

Neither card is the other with the signs flipped — that would be one axis, not
two fighters.

| | A — pressure/power | B — range/timing |
|---|---|---|
| Wins by | closing distance and making the exchange expensive | banking rounds from the outside |
| Pays with | reach −22, counter timing −28, **defensive technique −42** | **power −45**, durability −30, chin −18 |
| Compensation | `defensive_technique` ← `power` (+45) | `power` ← `reach` (+45) |
| Loses to | someone who will not stand still | being trapped inside |

The matchup has a shape a coach would recognise: A must make it a phone booth,
B must not let him. B is deliberately worse than A at exactly the thing A is
built to force.

**B cannot end the fight.** Power −45 is a severe negative with a declared
visible consequence: clean, correct punches that move nobody. That is the point
— it makes B's route to victory the scorecard, and therefore makes the sealed
one-round decision a real outcome rather than a fallback.

## Why the numbers stay modest

Bands are style-like (roughly ±10…45), not cartoon. No attribute reaches +70,
let alone +100, so neither card spends its budget on a single elite trait:
A nets 304 and B nets 396 against the canonical cap of 1000
(`data/attribute_budget.json`, `C_tiered_marginal`, refund 0.5). There is
deliberate headroom — these are instruments for measuring a one-round ending,
and a pair sitting near several caps at once would make every measurement a
statement about the caps.

## The rule that keeps them different: expressed attributes only

`tools/uppercut_validate/pairing.py` requires the pair to differ by **≥ 20** on
at least **8** of the attributes `data/attribute_effects.json` actually
expresses. The current pair clears it with room: **11 of 14**.

The word *expressed* is load-bearing. Ten of the twenty-four attributes —
`frame`, `inside_work`, `footwork_technique`, `composure`, `ring_awareness`,
`adaptability`, `discipline`, `coachability`, `ringcraft`, `showmanship` — are
named in `attribute_effects.json` as `not_yet_expressed`. They scale nothing.
A pair separated by the full width of the economy on those ten and identical on
everything else would look like the most differentiated pair in the repository
and would produce two fighters who fight **exactly the same**.

So the comparison is taken only over attributes with a declared effect row, and
that set is read from canon rather than listed in the checker — the day
`ringcraft` acquires an effect it joins the comparison automatically. The
counter-example is a test
(`test_a_pair_differing_only_where_the_fight_cannot_see_is_refused`), not a
comment.

A second test enforces the other half of the same idea: no unexpressed
attribute on either card may exceed ±30 in magnitude. −30 is where Rule 10
itself starts treating a negative as consequential, so the bar reads as "never
consequential enough for Rule 10 to demand a story about it." This caught a
real error during authoring — B's severe negative was originally
`inside_work −45`, which would have spent a genuine +45 of reach compensating a
weakness the simulation cannot currently show.

## Running the checks

```
python -m tools.uppercut_validate.cli fighters   # Rule 10, both cards
python -m tools.uppercut_validate.cli pairing    # the pair is a real matchup
python -m pytest tests/test_fighter_pair_uniqueness.py tests/test_authored_cards_reach_the_sim.py -q
```

## Using them

```python
from tools.uppercut_sim.engine import Bout
b = Bout(seed=4242, profile_a="rusher", profile_b="technician",
         rounds=1, round_seconds=60,
         cards=("generic_pressure_a", "generic_range_b"))
```

`cards=` is optional and defaults to `None`, which keeps the stress-profile
loadouts and therefore keeps every measurement taken before this seam existed
exactly as it was. Verified: `python -m tools.engine.golden --diff` reports
phases O, Q and R byte-identical after this change.

A supplied card **replaces** the profile's loadout rather than merging with it.
Two sources adding into one attribute dict would be a second opinion about what
a fighter is, and second opinions in this repository agree right up until one of
them is edited.

## Still open

The C++ side does not read these cards yet. `FUppercutFightSession` — the
integrated session that would apply these multipliers at the same `_attr` sites
the Python engine uses — is not written. Until it is, the live fighters in
`L_UppercutDevArena` remain identical, and this document describes a pair that
exists in the reference simulator only. That gap is the next slice, and it is
named here rather than left for a reader to discover.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-12 03:26 UTC | END ] -->
