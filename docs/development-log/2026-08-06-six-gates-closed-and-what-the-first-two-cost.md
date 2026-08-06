<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 03:00 UTC | START ] -->
# Six gates closed, and what implementing the first two actually cost

**2026-08-05/06.** The Director ruled on all six open gates. Decisions 0014
through 0019 record them. Two were implemented the same night; three are recorded
and land with the runtime; one was a ratification with a schedule attached.

The interesting part is not the rulings. It is what happened when a canon number
moved.

## What the rulings say, in one line each

- **0014 (G1)** — movement is priced by displacement. A 0.22 ru step costs 0.132.
  The flat 0.600 is not the price of an ordinary adjustment; it may live under a
  separately named explosive action.
- **0015 (G2)** — thinking is free. `Observe`, `HoldPosition` and `Rest` become
  first-class policy outcomes; a fighter may reconsider without stepping.
- **0016 (G3)** — `aggression_bias` is intent at the intent stage, not the share
  of thought cycles that become a punch. Canon's numbers stand; the reading was
  wrong.
- **0017 (G4)** — Decision 0013 ratified. Lateral guard geometry after the live
  round, not before it.
- **0018 (G5)** — versioned rulesets. `Project Uppercut Professional Rules` is
  the default and has no three-knockdown rule; the three-knockdown condition
  survives as a named arcade modifier.
- **0019 (G6)** — a canon authoring margin of 0.05. No coverage value sits on the
  interception threshold.

## G1 cost three re-proofs, and that is the story

Repricing a step meant editing three entries in
`data/moves/generic_sandbox_moves.json`. Within minutes the suite reported six
failures, and every one was correct:

- Phase O's golden stream — expected, that is what the ruling changes.
- **Phase Q's golden stream** — not expected.
- **Phase N's pinned hash** — not expected.
- **Phase K's pinned hash** — not expected.

Phases K, N and Q all hash the move table into their marker-stream headers. None
of their *fights* changed; Phase Q does not even read a stamina cost. But a file
they hash had moved, so their bytes moved, and three proven phases stopped being
proven until somebody said otherwise.

The choice at that moment is the whole discipline. The cheap option is to edit
four hashes and carry on — the suite goes green, nothing is technically false,
and the evidence quietly becomes a claim about a run nobody did. Instead all
three phases were re-run against the new canon:

    Phase N   UppercutCoreCondition                identical    7b2b9000...
    Phase K   UppercutRenderGameMode               identical    4826e82c...
    Phase Q   UppercutCoreRange, three runs        identical    32fb8185... 02f3832e... b8acb84e...

Each still reproduces its analyzer byte for byte. The old hashes sit beside the
new ones in the pin file and in the phase record, so what was proven when is
still readable.

Total cost: about fifteen minutes of runs. Cost of not doing it: the phrase "the
C++ is proven" would have quietly meant "the C++ was proven, against a canon
that no longer exists."

## A claim I made yesterday that was too strong

When Phase Q was ported I wrote that its pin "will survive the open gates,"
because the slice spends no stamina. It did not survive twelve hours.

The reasoning was half right and the conclusion was wrong, which is the more
useful kind of mistake. A stamina ruling cannot change the Phase Q *fight* — that
part held. But Phase Q reads the move table for range bands and hashes the whole
file, so a change to a field it never reads still changed its stream. The
distinction that actually holds: **a canon ruling on stamina cannot change what
Phase Q does; any edit to a file Phase Q hashes changes what Phase Q emits.**

The correction is written into `0014`, into the phase record, and into the Q port
section, rather than left for someone to trip over.

## Two implementation notes worth keeping

**Zero displacement costs zero, and the ropes case is where that earns its keep.**
`rope_retreat_multiplier` is 0.0 — with your back on the ropes a backward step
buys nothing. Under the old flat fee it still charged full price, so the
anti-running rule doubled as a stamina tax on the fighter already in trouble.
Pricing by distance travelled fixes that without anybody writing a special case,
because the multiplier is now inside the number the price comes off. Both the
movement and its cost resolve from one expression.

**A margin rule written in floats is itself a knife edge.** The first version of
the G6 test failed three lanes authored at exactly 0.55 against a threshold of
0.60 and a margin of 0.05, because in binary floating point `0.6 - 0.55` is
`0.04999999999999999`. It is now compared in the q10000 integer space the whole
core already uses — which is also simply what the simulation sees.

## State

- Six gates closed; `OPEN_GATES.md` shows the closure table and no open rows.
- 745 tests green, validators green.
- Phases K, N and Q re-proven under the new canon. Phase Q is still the latest
  engine phase proven.
- Not yet implemented, and not claimed anywhere: G2's outcome set, G3's staged
  policy, G5's ruleset objects. They land with the runtime subsystem.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 03:00 UTC | END ] -->
