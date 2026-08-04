<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START ] -->

# Referee profiles, consumed: seven philosophies that actually officiate

**Date:** 2026-08-04 · **Decision 0012 slice item 2** · next_steps Step B, second half

The 2026-08-03 review's finding 2 said it plainly: "Referee profiles are authored
data — Rule 16's seven philosophies, the stoppage conditions in `condition_model`
— and **nothing consumes them**. Every referee in the model behaves identically."
This records the change that makes the profiles officiate.

## What exists now

`data/referee_semantics.json` is the dictionary that turns a profile's
categorical enforcement levels into executed numbers — authored as
`{level, value}` rows so the coverage checker's key discipline applies to the
table names. `Bout` takes a `referee` parameter (default `hana_mori`), derives
this official's numbers from profile × semantics at construction, and discloses
the official in the `bout_start` payload (Rule 16: disclosed before the fight,
in the record and the replay). Enforcement that now differs by official:

- **The clinch ladder.** Warnings from this official's threshold onward —
  celeste warns from entry 3, hana from 6, elliot from 17 — then a **point
  deduction** each deduction-gap past it, emitted as `referee_deduction` (an
  event type the fight_event schema and the replay model's
  `required_explained_types` had declared all along, inert until now) and
  witnessed by the Judge exactly as a knockdown is: a public ring fact, one
  point off the round, no reason attached to the card.
- **Break patience.** How long the official lets them work before the break:
  60 decision-slots for celeste, 90 (the incumbent constant) for hana, 150 for
  elliot.
- **The `referee_judgement` stoppage** (`condition_model.stoppage_conditions`,
  declared and inert until now), on observable evidence only: a fighter who has
  been down this bout, absorbing solid-or-clean punishment without landing an
  answer. Landing anything resets the ledger; so does the round break, because
  the corner is an answer. Only the protective disposition (nkiru) carries a
  finite threshold; `standard` is deliberately null — the incumbent engine
  stopped only on the count and the limits, and moving that line for every
  official is a tuning act that waits for a rendered fight. A judgement
  stoppage is a TKO: the waved-off fighter loses, whatever the knockdown
  ledger says.

What did **not** move: the count arithmetic (Rule 16 — identical for every
official, one code path), the knockdown-rule stoppages, and the Judge's
boundary (the deduction is a new entry in its published fact vocabulary — a
visible act, checked by the same five boundary relations).

## The laws (cli `refsem`, mirrored in tests)

Four checks keep the pairing honest, each proven non-vacuous by mutation:
every official resolves in every table it feeds (the "referee who maps to
nothing" is the inert class this step closes); the numbers are ordered by what
the level words claim; **the neutral rows are the incumbent constants** —
warning at 6, break patience 90, judgement stoppage off — so the file's
calibration promise is enforced, not prose; and the seven officials derive at
least four distinct enforcement tuples (they derive seven).

## Equivalence and difference, measured

Same 72-bout matrix as the Judge extraction (every ordered stress pairing,
seeds 31 and 4242), against the pre-change baseline:

    hana_mori (default)   72/72 byte-identical once the disclosure key is removed
    nkiru_okafor           2/72 fights change - both referee_judgement TKOs
                           (4242 showman v drainer, 4242 showman v technician;
                           302 knockdowns across the matrix supplied the evidence)
    celeste_navarro        0/72 change
    elliot_ames            0/72 change

The first line is the calibration promise holding exactly: the neutral official
IS the pre-consumption engine, so every recorded balance figure
(`attributes_in_the_loop.md`) remains a true statement about the current build.
The second line is consumption proven in natural play, not just in tests: the
safety specialist genuinely stops fights the other officials let run.

## Named finding: the clinch tendencies are unreachable in natural play

The zeros on lines three and four are not a rounding artifact and are not being
rounded away. `clinch_entry` appears nowhere in `policy.py`: **no stress-style
policy ever chooses to clinch**, so warnings, deductions and break patience —
proven mechanically by direct tests and reachable through the abuse-list
exploit policies — never surface in a natural style-versus-style fight. The
officials differ where fights actually go (knockdowns), and are inert where
fights never go (the clinch). That is a CPU-policy gap, not a referee gap: the
drainer's real-world analogue smothers and clinches, and when step C re-opens
style balance the clinch belongs in its toolkit. Logged here so the next
balance pass inherits it as a question rather than rediscovering it as a
surprise.

Suite after consumption: 504 passed (16 new), `cli all` RESULT: OK including
the four new semantics laws, all eleven gate checks green — see STATUS.md.

<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | END ] -->
