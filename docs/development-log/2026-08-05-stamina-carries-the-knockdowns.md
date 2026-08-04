<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 00:35 UTC | START ] -->

# Measured: stamina carries the knockdowns, and the guard is what drains it

**2026-08-05.** Having been wrong four times in a row about what was holding the
decision path shut, the last entry promised a measurement instead of a fifth
prediction. It also offered a hypothesis — that saturated head and jaw condition
was inflating pressure. **That hypothesis is wrong too.** The measurement says so
in one table.

## The measurement

Canon's pressure is a product, and the K row already carried every term, so no
new instrumentation was needed. Each factor below is its inflation over a fresh,
balanced, fully covered target — the opponent for whom the product is smallest.
93 knockdowns across 24 seeds:

| term | median | min | max | |
|---|---|---|---|---|
| **stamina** | **2.74** | 1.71 | 3.50 | **carries it** |
| balance | 1.25 | 1.00 | 1.25 | |
| condition | 1.17 | 1.03 | 1.34 | |
| guard | 1.16 | 1.15 | 1.24 | |

Combined median inflation: **4.58×**.

Accumulated condition — my hypothesis — contributes 1.17×. It is the *smallest*
term but one. The stamina term contributes 2.74× and ranges to 3.50, which is its
arithmetic maximum: `(1.4 − stamina_frac) / 0.4` reaches 3.5 only at zero
stamina.

A median of 2.74 means that **at the moment of a knockdown a fighter is typically
at 30% stamina**. They are not being knocked out by damage. They are being
knocked out by exhaustion, and canon's formula multiplies a punch's pressure by
up to three and a half times when a man is empty.

## Why the tier experiment came out flat, explained

The previous entry recorded knockdowns flat at ~104 across a 3.3× range of
decision cadence and could not explain it. This does.

**The posture hold cost is charged per tick, not per action.** A fighter pays
`stamina_per_tick` for holding his guard on every one of a round's 10,800 ticks,
whether he throws sixty punches or six. Punching costs stamina too, but the
constant drain dominates — which is exactly why slowing a fighter to a novice's
twenty-tick reaction changed his work rate by two thirds and his knockdown rate
by nothing at all. He arrives at the same empty tank either way, and the stamina
term does the rest.

Two findings that looked unrelated are the same finding.

## What this does and does not license

It does **not** license changing a number. The stamina term is canon's, the hold
cost is canon's, and the interaction between them is a design statement about
what carrying a guard should cost across three minutes. It may be exactly right.

What it does license is a properly framed question for the Director, which the
last four attempts could not produce because they were aimed at the wrong
subsystem:

> Should a fighter who holds his guard for a full round, without throwing much,
> arrive at the third minute close to empty — and therefore three times easier to
> drop?

If yes, the model is working and the knockdown threshold should be swept against
*that* fighter. If no, the lever is `posture_economy`'s per-tick hold cost or
stamina's regeneration rate, not the 0.57 threshold and not the pressure formula.

Either answer is reachable now. That is the difference between this entry and the
four before it.

## Tally, updated

Five wrong diagnoses today, each corrected within seconds by a sweep: the debug
floor, z-fighting, grading-as-blocker, guard-as-blocker, policy-as-blocker, and
condition-saturation. The instrument found in one run what prediction missed five
times, which is the argument for instrumenting first, stated as plainly as it can
be stated.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 00:35 UTC | END ] -->
