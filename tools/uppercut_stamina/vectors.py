# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 10:30 UTC | START ]
"""Shared Wind/Reserve trajectories. Decision 0021, runtime step 5.

    python -m tools.uppercut_stamina.vectors

The C++ runtime must reproduce every checkpoint below EXACTLY, in q10000
integers. Not approximately, and not "within a tick": the whole reason this
economy is integer fixed-point is that a float port drifts silently and only
shows up as a fight that ends differently three rounds later.

The scenarios are chosen for the seams where a port goes wrong, not for
coverage of ordinary play:

  - recovery that would overflow the pool, so the ceiling clamp is exercised;
  - a fighter working below the low-Wind line, where Reserve starts paying;
  - displacement pricing, where FloorDiv's rounding shows;
  - the corner, which is the only place Reserve moves at all;
  - a low-Reserve fighter, where BOTH indirect paths bite at once.

This mints no integrated evidence. It is a unit contract for one subsystem, in
the same shape as the canon-hash vectors, and it exists so the C++ can be
checked rather than read.
"""
import io
import json
import os

from tools.uppercut_stamina import economy as E

OUT = os.path.join(E.REPO, "tests", "fixtures", "stamina_vectors.json")

ROUND_TICKS = 180 * 60


def _case(c, name, script, wind=None, reserve=None, checkpoints=(),
          between_rounds_after=False):
    """Run a script and emit a self-contained vector.

    The SCRIPT travels in the fixture. The C++ replays it rather than
    re-declaring the scenario, because two copies of a scenario is the same
    defect as two copies of a rule - they agree until one is edited, and the
    edit that matters is the one nobody mirrors.

    `script` is a list of (repeat, action, move_id, displacement_ru).
    `checkpoints` are tick numbers, 1-based, counted over the FLATTENED script,
    so a checkpoint means the same tick in both languages regardless of how the
    repeats were grouped.
    """
    w = c["wind_start"] if wind is None else wind
    r = c["reserve_start"] if reserve is None else reserve
    start_w, start_r = w, r
    marks = []
    tick = 0
    for repeat, action, move_id, disp in script:
        for _ in range(repeat):
            w, r = E.step(c, w, r, action, move_id=move_id,
                          displacement_ru=disp)
            tick += 1
            if tick in checkpoints:
                marks.append({"tick": tick, "wind": w, "reserve": r})

    missed = sorted(set(checkpoints) - {m["tick"] for m in marks})
    if missed:
        raise ValueError(
            "%s declares checkpoints %s that its script never reaches. A "
            "checkpoint the generator silently drops is a comparison the C++ "
            "is never asked to make." % (name, missed))

    if between_rounds_after:
        w, r = E.between_rounds(c, w, r)

    return {
        "name": name,
        "start_wind": start_w,
        "start_reserve": start_r,
        "script": [{"repeat": rep, "action": act, "move": mv, "disp": d}
                   for rep, act, mv, d in script],
        "between_rounds_after": between_rounds_after,
        "wind": w, "reserve": r,
        "checkpoints": marks,
    }


def build():
    c = E.economy_pack()
    # Canon that the economy itself calls impossible must never be frozen into
    # a vector. A fixture generated from broken canon does not report the
    # breakage - it PROMOTES it, by handing the C++ a trajectory to match.
    if c["errors"]:
        raise ValueError(
            "the stamina canon does not satisfy its own contract, so no "
            "trajectory generated from it is evidence of anything:\n  - %s"
            % "\n  - ".join(c["errors"]))
    cases = []

    # 1. Pure rest from empty. Exercises the ceiling clamp on every tick once
    #    the pool fills, which is where an off-by-one shows.
    cases.append(_case(
        c, "rest_from_empty",
        [(ROUND_TICKS, "rest", None, 0)],
        wind=0,
        checkpoints={1, 100, 5000, ROUND_TICKS}))

    # 2. A professional-ish round: one cross every 166 ticks, observing between.
    #    A sanity probe for cadence, NOT calibration evidence - Decision 0024 is
    #    explicit that punch-count numbers prove nothing until observable CPU
    #    policy exists.
    round_script = []
    for _ in range(ROUND_TICKS // 166):
        round_script.append((1, "attack", "cross_rear", 0))
        round_script.append((165, "observe", None, 0))
    cases.append(_case(
        c, "round_at_65_punches", round_script,
        checkpoints={166, 1660, 9960}))

    # 3. Working below the low-Wind line. The ONLY place sustained exertion
    #    charges Reserve, so a port that forgot it looks fine until round eight.
    cases.append(_case(
        c, "grinding_below_low_wind",
        [(600, "attack", "jab_lead", 0)],
        wind=c["wind_low"] - 1,
        checkpoints={1, 300, 600}))

    # 4. Displacement pricing: the ru -> cost conversion, and the
    #    zero-displacement step that must cost nothing, which is what stops a
    #    fighter paying a fee to stand still.
    #
    #    CORRECTION, 2026-08-07. An earlier draft of this comment claimed these
    #    integers were "chosen so the two would differ if the port used '/'".
    #    They are not, and cannot be: every operand on this path is positive,
    #    and floor and truncation agree on positive operands. The claim was
    #    wrong and the case proved less than it said. Case 9 is the vector that
    #    actually discriminates; see the note there.
    cases.append(_case(
        c, "displacement_pricing",
        [(1, "move", "step_in", 2200),
         (1, "move", "step_out", 1717),
         (1, "move", "step_lateral", 3),
         (1, "move", "step_in", 0)],
        checkpoints={1, 2, 3, 4}))

    # 5. The corner. The only place Reserve moves upward. An empty script with
    #    the between-rounds flag set: the vector carries the whole scenario, so
    #    the C++ has no separate branch to write and therefore none to get
    #    wrong.
    cases.append(_case(
        c, "between_rounds", [],
        wind=c["wind_max"] // 4, reserve=c["reserve_max"] // 2,
        between_rounds_after=True))

    # 6. A drained fighter. Ceiling AND recovery multiplier both bite, which is
    #    the compounding a single-path port gets wrong.
    cases.append(_case(
        c, "rest_on_low_reserve",
        [(ROUND_TICKS, "rest", None, 0)],
        wind=0, reserve=c["reserve_max"] // 5,
        checkpoints={1, 1000, ROUND_TICKS}))

    # 7. Spend and rest on the SAME tick. Step order is a rule, not a detail:
    #    pay first, then recover. A port that recovers first refunds a fighter
    #    before he has paid, and the difference is invisible in every scenario
    #    where the two never coincide.
    cases.append(_case(
        c, "spend_and_recover_same_tick",
        [(1, "rest", "jab_lead", 0),
         (1, "observe", "cross_rear", 0),
         (1, "hold_position", "step_in", 1500),
         (1, "micro_adjust", "jab_lead", 0)],
        checkpoints={1, 2, 3, 4}))

    # 8. The floor. Spending past empty must clamp at zero and stay there
    #    rather than going negative and then "recovering" back into credit.
    cases.append(_case(
        c, "spent_past_empty",
        [(400, "attack", "cross_rear", 0)],
        wind=c["wind_exhausted"], reserve=c["reserve_max"] // 10,
        checkpoints={1, 50, 200, 400}))

    # 9. THE FLOOR-VERSUS-TRUNCATE VECTOR, and the only one in this file that
    #    discriminates the two.
    #
    #    `step` computes the recovery multiplier from Reserve BEFORE Reserve is
    #    clamped at zero, so a tick that spends past empty divides a NEGATIVE
    #    numerator - the one place in this economy where Python's // and C++'s
    #    / disagree. Measured, not assumed: over reserve in [-199, -1] the two
    #    give 23 and 24 units of rest recovery respectively, so a port that
    #    used '/' would gain one unit of Wind per such tick and read correct
    #    everywhere else in this file.
    #
    #    Reserve 450 minus overhand_rear's load of 600 lands at -150, inside
    #    that window. Wind starts far below the ceiling so the difference is
    #    not swallowed by the clamp - which is how this seam stayed invisible:
    #    at a full pool the clamp erases the evidence.
    #
    #    This vector pins CURRENT behaviour. Whether reading recovery off an
    #    unclamped negative Reserve is correct at all is a contract question,
    #    raised separately - see docs/plans. The parity requirement holds
    #    either way.
    cases.append(_case(
        c, "negative_intermediate_reserve",
        [(1, "rest", "overhand_rear", 0)],
        wind=100000, reserve=450,
        checkpoints={1}))

    return {
        "$comment": ("Wind/Reserve trajectories for Decision 0021 runtime "
                     "parity. Every value is q10000 and must match EXACTLY - "
                     "an integer economy that agrees approximately has already "
                     "failed. Regenerate with "
                     "python -m tools.uppercut_stamina.vectors."),
        "round_ticks": ROUND_TICKS,
        "canon": {
            "wind_max": c["wind_max"], "wind_low": c["wind_low"],
            "wind_exhausted": c["wind_exhausted"],
            "wind_start": c["wind_start"], "reserve_start": c["reserve_start"],
            "reserve_max": c["reserve_max"],
            "sustained_exertion": c["sustained_exertion"],
            "wind_per_ru": c["wind_per_ru"], "reserve_per_ru": c["reserve_per_ru"],
            "wind_between_rounds": c["wind_between_rounds"],
            "reserve_between_rounds": c["reserve_between_rounds"],
            "ceiling_floor": c["ceiling_floor"], "ceiling_span": c["ceiling_span"],
            "recovery_floor": c["recovery_floor"],
            "recovery_span": c["recovery_span"],
        },
        "cases": cases,
    }


def main():
    data = build()
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, indent=2) + "\n")
    print("wrote %s" % OUT)
    for case in data["cases"]:
        print("  %-26s wind=%-10d reserve=%-10d"
              % (case["name"], case["wind"], case["reserve"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 10:30 UTC | END ]
