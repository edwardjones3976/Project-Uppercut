<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 19:40 UTC | START ] -->

# I measured the wrong artifact

**2026-08-05.** Every measurement I took today after the confound was taken on
`experiment_per_hand_guard.run_with` — a measurement harness — and reported as if
it described **the Phase O contract**. It does not. The contract is a
substantially fuller simulation, and several of today's headline findings are
findings about the harness only.

This is the ninth corrected diagnosis today and much the largest. It is written
before any further work because everything downstream of it needs re-reading.

## What the contract actually contains

`analyze_core_round.expected_stream` — the artifact a C++ port must reproduce
byte-for-byte, and the thing "Phase O" means — already has:

- **positions and footwork.** `step_in` / `step_out` move fighters along a track,
  with band resolution and canon's hysteresis. 1,535 steps across 24 bouts.
- **evasion.** `slip_lead` sets a slip window and a high punch arriving inside it
  is `dodged`. 449 slips, 20 dodges.
- **misses.** A punch whose tip never reaches the surface resolves `whiffed`.
  969 whiffs, 37.7% of everything thrown.

Measured on the contract, 24 seeds × 3 rounds:

| | contract | harness | reference sim |
|---|---|---|---|
| punches | 2,567 | 2,457 | 3,909 |
| connect | **42.5%** | 53.0% | 42.4% |
| whiffed | 969 | 0 | — |
| steps | 1,535 | 0 | — |
| slips | 449 | 0 | — |
| uppercut_rear landed | **180** | **0** | — |

**The contract's connect rate is 42.5% against the reference's 42.4%.**

## What that means for today's findings

**Withdrawn.** The claims that the core has no range model, that footwork has
been inert since Phase H, that nothing ever misses, and that `uppercut_rear`
landed zero of 532 — all true of the harness, none true of the contract. The
uppercut lands 180 times in the contract.

**Withdrawn.** The 16.7× factorisation into volume 5.8× / accuracy 1.3× /
lethality 2.3×. It compared the harness against the reference. Against the
contract the accuracy factor is **1.00**, so Phase R's headline — "closed the
accuracy factor, 60% connect down to 41–46%" — closed a gap that existed only in
the harness.

**Withdrawn.** Every stamina figure quoted today: footwork at 46.7% of spend, 231
per round out against 10.6 in, the 4.6× lethality residual, the recovery
candidates. All harness measurements. They may hold on the contract; nobody has
checked.

**Still standing, and re-verified on the contract just now:**

- **Phase O is held.** 24 of 24 bouts stop, all in round one. Unchanged since
  2026-08-04 and confirmed here on the contract itself.
- **The confound.** Bout totals compared across bouts that all end on a knockdown
  count. Independent of which artifact was measured.
- **The step-cost contradiction (G1).** 0.132 against 0.600 in two canon files.
  A canon defect; no simulation involved.
- **Ten guards, two volumes, four behaviours (G6).** Read from canon directly.
- **The ABC ruleset gap (G5).** Read from a primary source.
- **Phase Q, R and S as contracts.** They encode canon rules correctly and their
  tests pass. What is wrong is the claim that they *added* range and evasion to a
  core that lacked both.

## How it happened, stated plainly

The harness was the thing I had instrumented. It had `run_with`, hooks were easy
to add, and it ran in a second. The contract emits a marker stream and is
awkward to instrument. So I measured what was easy to measure and wrote up the
results as though they described the phase.

The tell was there the whole time and I read past it: the Phase O stream's
trailer has counted `whiffed`, `dodged`, `steps` and `slips` since it was
written. I quoted that trailer in this log on 2026-08-05 without noticing that a
core with "no evasion and nothing that misses" was reporting both.

The rule I should have followed, and the one that goes in CONTRIBUTING: **a
finding about a phase must be measured on that phase's contract.** A harness may
explore; only the contract may conclude.

## What happens next

Nothing further should be built on today's stamina numbers. The honest position
is that Phase O is held, the reason is not established, and the three canon
quantities in the decision packet remain worth deciding on their own merits —
G1 and G6 because they are defects in canon rather than in any simulation, G5
because it is a declaration the project has not made.

Re-running the conversion and stamina work against the contract is the first job,
and it is a real job rather than a re-read: the contract has no `on_eligible`
hook, no per-term decomposition, and a stream-shaped output. Instrumenting it
without changing a single byte of its stream is the constraint that makes it
worth doing carefully.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 19:40 UTC | END ] -->
