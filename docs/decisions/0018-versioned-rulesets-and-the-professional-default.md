<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:55 UTC | START ] -->

# Decision 0018 — Versioned rulesets, and a professional default

**Status:** accepted (Director ruling, 2026-08-05)
**Closes:** gate **G5**
**Date:** 2026-08-05

## Question

The three-knockdown rule was canon here, and it was the termination condition in
every measurement taken during the week of 2026-08-03. An external review pointed
out that the Association of Boxing Commissions' Unified Rules contain no such
rule; checked against the ABC's own published text, that is correct and explicit
— **Rule 8: "There is NO Three (3) Knockdown Rule."**

That did not make the project wrong. It made an *assumption* stand where a
*declaration* belonged.

## Decision

**Rulesets become explicit, named and versioned data.** No bout runs under an
implicit rulebook, and every bout records which one it ran under.

### Default: `Project Uppercut Professional Rules`

- mandatory knockdown count;
- referee stoppages;
- **no** generic standing eight count;
- **no** automatic three-knockdown stoppage;
- **no** saved-by-the-bell rescue;
- disclosed round count and clock behaviour;
- universal medical and incapacitation minimums;
- authoritative scoring and foul deductions.

### Optional modifier: `Project Uppercut Arcade Three-Knockdown Rule`

The three-knockdown condition stays available for arcade exhibitions and special
events. What it may no longer do is silently define every professional fight.

### Recording

Every replay and event record stores the **ruleset name and version**, alongside
the seed, the commit and the data hashes. A replay whose ruleset is unknown is
not a replay; it is a coincidence.

## The consequence, stated plainly because it is large

`decision_path_must_survive` — the invariant that has held Phase O since
2026-08-04 — is an invariant about bouts reaching the cards. The rule that was
stopping bouts reaching the cards is the three-knockdown stoppage that no
professional ruleset has.

So this ruling changes what "a bout ended correctly" means, and **every stoppage
figure quoted during that week was measured against a termination condition the
project no longer uses by default.** Those figures are re-run, not re-read. The
reference simulator's 20-of-24 was measured under the same three-knockdown rule
and is subject to the same re-run.

This does not retroactively make the stamina findings wrong. The 16.7× gap
factorised into volume, accuracy and lethality under a rule both sides shared,
and a shared rule cancels in a ratio. What it changes is the absolute claim —
"this core reaches the cards in 0 of 24" — which must be re-measured under the
professional default before it is quoted again.

## Measured after (2026-08-06)

Implemented and swept the same day: `tools/engine/measure_ruleset_effect.py`,
24 bouts, 3 rounds, one contract, two rulebooks.

| | professional | arcade |
|---|---|---|
| reached the cards | **24** | 0 |
| stopped | 0 | 24 |
| knockdowns | 1648 | 96 |
| knockdowns per round | **22.89** | 4.0 |

`decision_path_must_survive` is satisfied for the first time — and **for the
wrong reason.** The bout survives to the cards because nothing ends it, not
because the fighters survive it.

The reading that matters: *"0 of 24 reach the cards"* and *"23 knockdowns per
round"* were always the same measurement seen from either side of the stoppage
rule. This ruling did not fix Phase O; it removed the lid and made the size of
the real problem — conversion at 2.78× the reference, measured 2026-08-05 and
unaffected by this — impossible to miss.

Full working: `docs/development-log/2026-08-06-the-three-knockdown-rule-was-not-the-problem-it-was-the-lid.md`.

## What this does not decide

Foul deductions, medical stoppage criteria and the scoring of a fought-even round
are named as provisions of the default ruleset but are not yet authored in
detail. They are data in a versioned file, which is exactly the point: they can
be authored without another decision record, and a bout will record which version
it used.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:55 UTC | END ] -->
