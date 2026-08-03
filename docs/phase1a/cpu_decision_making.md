<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:54 UTC | START ] -->

# CPU Decision-Making — ROADMAP Phase 1A step 9

Canon: `data/cpu_decision_model.json` · Schema: `schemas/cpu_decision_model.schema.json` ·
Validator: `tools/uppercut_validate/cpu.py` · Tests: `tests/test_cpu.py`

**Rule 18.** Definitions only. No CPU fighter has made a decision in this engine.

## The problem this step exists to solve

The Phase 1A quality gate asks for something unusual: that CPU fighters use "no hidden score, no
opponent input, and no privileged state knowledge." That is an **absence**, and absences are close to
untestable by watching behaviour. A CPU that reads the scorecards looks exactly like a CPU with good
judgement, right up until someone reads the code.

So the firewall is proven structurally instead. The CPU declares the event types it may read; the
validator checks that set is a subset of the simulation's event vocabulary, and that every sealed
symbol named by `data/score_isolation_contract.json` is absent from it. The gate item becomes a set
relation that fails loudly at validation time rather than a property somebody has to keep remembering.

Thirty-three observable event types are readable — footwork, range changes, punches thrown and their
outcomes, guard impacts, evasions, condition and stamina and balance and composure changes,
knockdowns and counts, referee instructions, crowd events, showmanship. The two judge events are not
among them, and cannot be added without the build going red.

## The blindness loophole, closed

A subset check has an obvious cheat: an empty input set satisfies it perfectly. A CPU that sees
nothing is trivially compliant and useless, and worse, it would let the firewall be "passed" by
deleting inputs rather than by respecting the boundary. So the validator also requires the observable
set to be substantial. That check exists specifically so the firewall cannot be satisfied by
blindness.

## Five named privileges, each with its reason

Official cards, the opponent's input buffer, the RNG state, hidden attributes, and future ticks.
Every entry carries a `why`, and the validator rejects a rationale shorter than a sentence — a ban
without a reason is a ban somebody removes in six months because it looked arbitrary.

The opponent input buffer is the one worth naming twice. Reading pending input is the classic
fighting-game cheat: it produces reactions no human could earn, and it feels arbitrary rather than
unfair, which makes it hard to report and easy to ship.

## Estimates stay estimates

Rule 3 permits the CPU to form beliefs from observable evidence with explicit uncertainty. It does
not permit certainty. `max_confidence` is bounded strictly below 1.0 by the schema, and the reasoning
is in the file: a CPU that is ever certain has stopped estimating and started knowing, and that
difference is precisely what the firewall protects. Beliefs below 0.6 confidence must carry an
uncertainty note, and every belief must cite the observed events that produced it.

## Fast is allowed. Instant is not.

The reaction floor is six ticks — 100ms at 60Hz, fast but inside what a trained human reaches. It is
a hard minimum at every difficulty, and the validator checks every tier against it, because a
zero-tick reaction is input reading by another name even when the code never touches the input
buffer.

Commitment binds the CPU exactly as it binds a human. `may_cancel_own_commitment` is a const `false`:
when the estimate changes mid-punch, the punch still finishes. That privilege — reacting to your own
mistake faster than the rules allow — is the one commitment exists to deny.

## Difficulty changes perception, never physics

Four tiers, from novice at 20-tick reactions and a 35% error rate to champion at 6 ticks and 5%.
What may change: reaction speed, read depth, aggression bias, error rate. What may **never** change:
damage dealt or taken, stamina cost or regeneration, attribute values, contact classification,
knockdown resistance, crowd gain, input responsiveness, judging criteria, referee behaviour.

The validator enforces the boundary three ways. The two lists may not intersect. Five specific
entries must appear in the never-list, because a CPU that hits harder on a higher setting is a hidden
advantage rather than a better opponent. And the tiers must order coherently — a deeper-reading tier
that reacts slower or errs more is not harder, just noisier — with a final check that difficulty is
not inert.

## What step 9 leaves open

Which *specific* action a policy picks from an observed situation is tuning, and belongs with the six
stress profiles the evidence rig will drive. The event log that would let a spectator audit these
decisions is step 10. Nothing here has run.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:54 UTC | END ] -->
