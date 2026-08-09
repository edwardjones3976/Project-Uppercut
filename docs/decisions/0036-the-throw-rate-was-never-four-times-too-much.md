<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 18:50 UTC | Decision 0036 start ] -->
# Decision 0036 — The throw rate was never four times too much

**Status:** ACCEPTED (delegated).
**Authority:** the owner's standing in-session delegation, 2026-08-09.
**Gated on:** Decision 0035, which named throw rate the critical path and
named `punch_model.repetition_economy` as canon's unread answer to it.

## The ruling

Three things, in the order they matter.

1. **`punch_model.repetition_economy` Rule 4 is implemented and lands.** Both
   mechanisms that govern throwing from the thrower's side — `arm_fatigue` and
   `position_cost` — are read from canon and wired into the bout. Neither
   coefficient was chosen here; all four are canon's.
2. **Decision 0035's headline finding is withdrawn.** "The fight throws about
   four times too much" is not true of the fight this project ships. It was
   true of a configuration the project had already refused.
3. **The critical path is renamed.** It is not volume. It is **connect rate**,
   and that is a defence question rather than a throw-rate question.

`pressure_threshold` is untouched by this decision. It remains 0.57.

## The correction, and how it was caught

Decision 0035 wrote: *"Roughly 127 landed punches per round implies something
near 270 thrown; a real round is 40–70 thrown and 15–25 landed."*

The 127 came from its own sweep table — **the `threshold: 14000` row.** The
shipped threshold is 5700, and that row of the same table reads 26.9 landed.
0035 corrected one measurement artifact (the count eating the round) and then
built its closing argument on a different row of the very table it had just
used to expose the first one.

Measured this session, ten seeds (4242–4251), shipped configuration, with the
new block stubbed back off so the numbers describe the tree as it stood at
`6418e3f`:

| | measured | a real round |
|---|---|---|
| thrown per round, both fighters | **42.2** | 40–70 |
| landed per round, both fighters | **26.9** | 15–25 |

The fight was already inside the real band on volume and slightly above it on
landing. **There was no factor of four.** A session that had taken 0035's
premise at face value would have gone looking for a governor to remove three
quarters of a throw rate that did not need removing — which is the precise
failure mode this project calls fitting, arriving through the back door as a
bug fix.

Logged here rather than corrected silently, per the project's working rule
that a resolution lives in the doc so a later edit cannot flip a deliberate
call without meeting the reason for it.

## What the block actually does

Same ten seeds, same shipped configuration, each mechanism switched off and
on at its own module boundary:

| | thrown/round | landed/round | rounds | fights to the cards |
|---|---|---|---|---|
| both off (the tree at `6418e3f`) | 42.2 | 26.9 | 82 | 6/10 |
| `arm_fatigue` only | 42.2 | 26.9 | 82 | 6/10 |
| `position_cost` only | 59.6 | 32.9 | 85 | 6/10 |
| **both on (committed)** | **58.7** | **32.5** | **95** | **7/10** |

Volume went **up**, and that is not a defect. `position_cost` cedes ring
position to the man who stands still and fires, which opens separation, and
separation is answered with more attempts. Canon's sentence is the design:
*"Punching without moving the feet cedes ground. The thrower ends up where the
opponent put them."* It was never authored as a volume brake. It is the reason
a fighter has to walk his man down, and the fight now contains that argument.

58.7 thrown is inside a real round's 40–70. Thirteen more rounds got boxed
across the population and one more fight reached the cards.

## The mechanism that was inert, and why

`arm_fatigue` first measured **bit-identical to being switched off** — the
first two rows above are the same numbers, not similar ones.

The cause was the definition of an idle tick. The first wiring shed an arm's
work on every tick that arm did not *begin* a punch, including the ticks it
spent recovering from one. Canon's ratio is 0.05 gained per throw against
0.004 shed per idle tick: 12.5 idle ticks undo one throw, and a jab occupies
its arm for about fourteen. Under that reading no arm could ever carry work
from one punch to the next, and the ceiling of 1.7 was unreachable by
construction.

**Canon does not author dead coefficients.** A reading that makes an authored
mechanism unable to fire is a misreading, not a finding about the mechanism.
An arm mid-punch is not an idle arm; it sheds on the ticks it is neither
throwing nor recovering from a throw, and the other arm sheds throughout —
which leaves canon's mixing-hands forgiveness exactly intact.

With that fixed, over the same ten fights: 5,577 punches thrown, **1,484
(26.6%) charged anything at all**, the multiplier reaching 1.552 at its worst
and never pinning the 1.70 ceiling. The tail decays smoothly — 652 punches
between 1.05 and 1.10, 216 between 1.10 and 1.15, down to a single punch above
1.55. That is a consequence with a distribution, not a counter with a cap, and
it satisfies canon's own constraint that *"nothing here fires on a repeat
count."*

`tests/test_repetition_economy.py` holds the regression: it asserts the
multiplier is ever anything other than 1.0, because that is the only
observable difference between a live mechanism and a dead one.

## What is not governed, named precisely

58.7 thrown and 32.5 landed is a **55% connect rate**. Professional boxing
runs near 30–35%. Volume is inside the real band; accuracy is not.

Every mechanism that should be taking that number down is a defence mechanism,
and the honest state of each is: the guard is in and blocking (it denies about
a third of what reaches it), evasion is in and firing, and the two of them
together still leave better than half of everything thrown arriving clean.
What is missing is not a brake on the thrower. Candidates, unread or partial,
in canon: `guard_integrity`'s arm condition and guard erosion (the consequence
the block currently names and does not model), hand availability, feints, and
the defender-side half of `repetition_economy` — `opponent_read` and
`counter_window_growth` — which target the man being hit rather than the man
throwing, and which this session deliberately did not touch.

## Consequences

1. **Decision 0035's "four times too much" is withdrawn from the record.**
   Its other findings stand: the count was eating the round, the guard bought
   about a fifth of volume and not five-fold, and the threshold was correctly
   refused twice.
2. **`pressure_threshold` is now measurable.** 0035 said the next threshold
   sweep should be taken on a fight with a boxing-plausible work rate. It now
   is one. The sweep is the next ordered step and is deliberately **not** run
   inside this decision, because a decision that both changes the fight and
   fits a number to the fight it just changed is the thing Decision 0032 §3
   exists to prevent.
3. **Every number in this document is a diagnostic, not calibration
   evidence** (Decision 0032 §3). Nothing in `data/` moved.
4. The critical path is connect rate. Next after the threshold sweep is the
   body knockdown (Decision 0033 Ruling 4), then C++ parity.
<!-- [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 18:50 UTC | Decision 0036 end ] -->
