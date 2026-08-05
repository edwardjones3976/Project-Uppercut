<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 09:30 UTC | START ] -->

# Phase R — evasion without dice, and the two clocks nobody had separated

**2026-08-05.** Phase Q delivered the volume factor and most of the accuracy
factor. What remained of the reference gap was the evasion stage — the reference
dodges 15.6% of everything thrown and this core dodged nothing — and the
lethality residual. This builds evasion. It closes the accuracy factor completely,
it uncovers an architectural conflation nobody had noticed, and it leaves the
lethality residual standing, larger than before and for a reason that makes sense.

## Canon had already made evasion geometric

The happy discovery: no die was needed, so none was added.
`guard_evasion_model.evasions` authors each evasion as a *kind*, a set of regions
it **vacates**, an active window in ticks, and the things it is **beaten by**:

    slip_lead    active_window   vacates head, jaw_chin   5 ticks
                 beaten_by feint_then_commit, body_shot
    roll_under   active_window   vacates head, jaw_chin   6 ticks
                 beaten_by uppercut, body_shot
    step_out     positional      vacates nothing — "range denial rather than
    pivot_lead   positional       evasion... and scores nothing"

So the rule is one sentence and it is canon's: during an evasion's active window
a punch aimed at a vacated region finds nothing there, unless the punch is one the
evasion is authored to be beaten by, in which case it lands into the movement.

That second clause is not an exception bolted on to rescue a model. It is this
project's core design rule applied one level out — a guard is not "high defence"
but a structure that protects some lanes and exposes others, and **an evasion is
the same object in motion**. Canon says it plainly: *the uppercut is the
punishment because it rises into where the head is going*. A roll that beat the
uppercut would be a strictly better guard rather than a different one, and the
contract refuses any evasion with no counter for exactly that reason.

**The telegraph falls out unpriced.** The reference needs a multiplier to make
slow punches more dodgeable, because its evasion is a die rolled at contact. Here
a slip is five ticks of real time, so an 11-frame overhand is far likelier than a
4-frame jab to still be in the air when the window is open. Nothing computes it.
The defender is not buffed; the slow punch is seen, which is what canon says the
telegraph is *for*.

**The price is authored too.** `mistime_penalty_ticks: 6` — a window that closes
having caught nothing leaves the defender in recovery. And `outranks_guard: true`
fixes the stage order, so a slipped punch is never also a blocked punch.

## The two clocks

Then the measurement refused to behave, and the reason turned out to be the
interesting part.

A timed slip and an untimed slip produced **identical** results. At the slow
decision clock a boxing-plausible throw rate requires, a fighter essentially never
gets a decision tick during an opponent's 4-to-10-frame startup — so he cannot
react, and "reacting" and "slipping at random" are the same policy.

The core has one clock doing two jobs. `decision_interval_ticks` sets both how
often a fighter *thinks* and how often he *throws*. Those are different things and
canon already knows it: `cpu_decision_model` authors `reaction_ticks` **and**
`aggression_bias` as separate dials, and this core has only ever used the first as
if it were both. That is also why the difficulty tiers measured flat back at the
start of the night — with one clock, and no distance and no evasion to react to,
there was nothing for a reaction rate to be a rate *of*.

Separate them — decide every 6 ticks, throw on an aggression roll — and the fight
becomes recognisable:

| configuration | thrown/f-rd | evaded | connect | kd/min | gap | cards |
|---|---|---|---|---|---|---|
| Phase O | 236.8 | 0 | 53.0% | 6.36 | 19.1× | 0/24 |
| Phase Q, a fighter | 187.2 | 0 | 60.1% | 6.70 | 20.1× | 0/24 |
| + evasion, one clock | 50.0 | 614 | 38.0% | 1.43 | 4.3× | 0/24 |
| react 6, aggression 0.06 | 11.9 | 165 | 42.8% | 0.55 | 1.6× | **14/24** |
| react 6, aggression 0.15 | 28.6 | 134 | 46.0% | 1.54 | 4.6× | 1/24 |
| react 6, aggression 0.30 | 51.8 | 133 | 45.7% | 2.38 | 7.1× | 0/24 |
| react 6, aggression 0.45 | 70.2 | 148 | 44.3% | 2.91 | 8.7× | 0/24 |
| *reference simulator* | *40.7* | *610* | *42.4%* | *0.38* | — | *20/24* |

Connect rate now sits at **41–46% across every configuration**, against the
reference's 42.4% and CompuBox's 36.9% power-punch average. The accuracy factor is
closed. It was the evasion stage, exactly as the factorisation predicted.

## What is left, stated precisely

At `react 6, aggression 0.30` the core throws 51.8 punches per fighter per round
against the reference's 40.7 and connects 45.7% against 42.4% — both within a
quarter of the reference. And it still drops men **6.3× as often**. Dividing out
volume (1.27×) and accuracy (1.08×) leaves a **4.6× lethality residual**.

That is *larger* than the 2.3× measured before this phase, and the reason is
sound rather than alarming: the core now delivers its most dangerous punch. The
uppercut is the highest-impact move in the set and it landed zero times in every
measurement taken before Phase Q. A model that finally throws the uppercut
properly gets more knockdowns from the same number of landings.

So the whole night reduces to one sentence. **Volume was range, accuracy was
evasion, and lethality is the stamina economy — and only the third is still
open.** Every measurement tonight has pointed at the same term from a different
direction: 2.17× floor-to-median, 2.74× median pressure inflation, 2.3× then 4.6×
per landed punch against the reference. A fighter who never tires is never knocked
down in 373 eligible landings.

## For the Director

Three things, and none of them is a tuning proposal.

**The two clocks should be separated in canon, not just in an experiment.**
`reaction_ticks` and `aggression_bias` are both authored and the core reads one of
them as if it were both. Fixing that is small, it is canon-faithful, and it makes
the difficulty tiers mean something for the first time.

**The stamina economy is the last open term** and it should now be examined on its
own, with range and evasion in place, because every earlier attempt to examine it
was reading a fight with no distance in it.

**The evasion policy is deliberately dumb** and should stay that way until the
above is settled. It slips when it sees a punch and otherwise slips at random; it
does not read the punch's height, its own guard, or the counter it could throw. A
smarter defender would move these numbers and would tell us nothing about the
model, which is the trap the whole night has been about.

Phase R adds no coefficient, draws no die, and edits no canon. 628 tests pass. The
C++ core reads none of it yet; the contract and its 14 tests are the deliverable,
in the same analyzer-first order as every phase before it.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-05 09:30 UTC | END ] -->
