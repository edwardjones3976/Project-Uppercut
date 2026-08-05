<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:20 UTC | START ] -->

# Decision 0014 — Movement costs displacement, not a flat fee

**Status:** accepted (Director ruling, 2026-08-05)
**Closes:** gate **G1**
**Date:** 2026-08-05
**Supersedes:** nothing. **Extends:** nothing.
**Packet:** `docs/plans/2026-08-05-three-canon-quantities-decision-packet.md` §Item 1

## Question

A step was priced twice in canon, 4.55× apart, and the core read the higher one.

    movement_model.locomotion.boxing_steps    stamina_cost_per_ru 0.60
                                              stride_length_ru    0.22   -> 0.132
    moves/generic_sandbox_moves.json          step_in/step_out    0.600 flat
                                              step_lateral        0.700 flat

Footwork was 46.7% of all stamina spend in the harness that first surfaced this.
The two numbers cannot both be the price of the same 0.22 ru adjustment.

## Decision

**Ordinary movement is priced by displacement:**

    movement_stamina_cost = distance_travelled_ru × stamina_cost_per_ru

A normal 0.22 ru boxing step at full stride therefore costs **0.132**.

**Zero displacement costs zero movement stamina.** A fighter who thinks without
moving pays nothing for the thought (that is Decision 0015's subject, and this
is the half of it that lives in the movement model).

**The flat 0.600 is not deleted — it is re-homed.** It may be retained only for a
separately *named* explosive movement action: a committed lunge, an emergency
rope escape, an explosive pivot, a chase burst. Those are real boxing actions
with a real price, and the price is what makes them a decision. What the flat fee
may not be is the cost of an ordinary adjustment step.

## How canon expresses it

One authority, one derived echo, and a validator tying them together — because
the defect being closed here is precisely *two authorities disagreeing*.

- `movement_model.locomotion.<mode>.stamina_cost_per_ru` is the authority.
- Distance is the distance the **body travels**, which is
  `stride_length_ru × the directional multiplier in force`. Not the change in
  separation: a lateral step displaces a fighter even in a model whose geometry
  is one axis and cannot represent the angle. Pricing lateral movement off the
  separation delta would make it free, and free movement is an exploit before it
  is a simplification.
- The exhausted multiplier is inside that distance, so a fighter whose legs have
  gone covers less ground and pays less for it. One number drives both.
- Ordinary step moves in the move table carry `"cost_model": "displacement"` and
  a derived `stamina_cost` for readers that expect the field. A validator
  recomputes it from the authority and fails on drift
  (`movement.check_step_cost_authority`), so the echo cannot become a second
  opinion.
- Explosive movement carries `"category": "explosive_step"` and
  `"cost_model": "flat"`, and that is where a flat fee is allowed to live.
  **No such move is authored yet**, and one is not authored by this record:
  the ruling permits the flat fee a home, it does not require the home to be
  built today. What is done today is that 0.600 stops being the price of an
  ordinary 0.22 ru adjustment. The schema and the validator are ready for the
  explosive action when a phase needs one.

Cost is charged at **commitment**, for the displacement intended. A step stopped
early by the body-separation clamp is still a step that was driven off the rear
foot. This is stated rather than assumed because it is the kind of detail two
implementations quietly disagree about.

## Consequences, named before they are measured

- The stamina economy changes materially. Footwork was 46.7% of spend in the
  harness and 14% on the contract; both numbers were computed against the flat
  fee and neither survives this ruling. **They must be re-measured, not
  re-read.**
- The Phase O golden stream moves. It is re-blessed in the same commit as this
  record, which is the rule in `docs/phase1a/golden/README.md`.
- **Phase Q's proof survives, but not untouched, and the difference matters.**
  Its slice spends no stamina, so nothing in its *behaviour* moves. But it reads
  the move table for range bands and hashes that file into its header, so
  repricing three steps changed its stream anyway. The claim written when Phase Q
  was ported — "this pin will survive the open gates" — was therefore too strong,
  and is corrected here rather than quietly left standing: what survives is the
  fight, not the bytes.

  This is the pin working as intended. The Phase Q golden failed the moment canon
  moved underneath it, which is the alarm that says "re-prove the port before you
  re-bless." That was done: `UppercutCoreRangeCommandlet` was re-run against the
  new canon and is still byte-identical to the contract.

- **Phases N and K move for the same reason** — both hash the move table into
  their marker streams. Their pinned hashes were re-proven, not merely updated:
  the C++ was re-run against the new canon and still reproduces the analyzer
  exactly. The old hashes stay in the record with the new ones beside them.
- Every conclusion that rested on "footwork is expensive" is now suspect. The
  three that matter are named in the development log rather than quietly
  dropped.

## What this does not decide

It does not decide how often a fighter steps — that is G2 and G3. A cheaper step
taken every decision tick is still a fighter who never stops moving, and pricing
alone will not produce a boxer.

<!-- [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-06 00:20 UTC | END ] -->
