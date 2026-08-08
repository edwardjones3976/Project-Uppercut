# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 07:40 UTC | START ]
"""Decision 0021's two-tier stamina economy, enforced.

WHY THIS FILE EXISTS AT ALL. `data/stamina_economy.json` declares five
invariants and names `tools/uppercut_validate/stamina.py::<fn>` as the enforcer
of each one. That file did not exist. Five rules were therefore documented as
checked and were checked by nothing - which is worse than not claiming
enforcement, because a reader who looks at the canon sees an `enforced_by` and
stops looking.

The function names below match those `enforced_by` strings exactly, and
tests/test_enforced_by_resolves.py now fails if any canon file names an
enforcer that cannot be imported. The gap is closed and the class of gap is
closed with it.
"""
from __future__ import annotations
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

ECONOMY = "data/stamina_economy.json"
EFFORT = "data/moves/generic_sandbox_effort.json"

# Decision 0014's G2 action families.
ACTIONS = ("observe", "hold_position", "rest", "micro_adjust", "move", "guard",
           "evade", "attack")

# The families that buy no Wind back at all (Decision 0021).
NO_RECOVERY = ("move", "guard", "evade", "attack")

ROUND_TICKS = 180 * 60


def load() -> dict:
    return {
        "economy": json.loads((REPO / ECONOMY).read_text(encoding="utf-8")),
        "effort": json.loads((REPO / EFFORT).read_text(encoding="utf-8")),
    }


def check_layers(docs: dict) -> list:
    """Wind and Reserve are separate authoritative values with separate rules.

    The failure this guards against is not that someone deletes a layer; it is
    that the two quietly become the same number wearing two names, at which
    point Decision 0021 is decorative.
    """
    e = docs["economy"]
    errs = []
    for tier in ("wind", "reserve"):
        if tier not in e:
            errs.append("the %s layer is absent - Decision 0021 requires two "
                        "authoritative layers" % tier)
    if errs:
        return errs

    wind, reserve = e["wind"], e["reserve"]
    if "recovery_per_tick_by_action" not in wind:
        errs.append("Wind declares no per-action recovery, so it is not the "
                    "acute resource Decision 0021 describes")
    if "drains" not in reserve:
        errs.append("Reserve declares no drains, so nothing spends it and the "
                    "second layer is inert")

    # The two must not be the same scale AND the same rules, which is how a
    # two-tier model collapses back into one without anybody editing a word.
    same_scale = wind.get("max") == reserve.get("max")
    same_start = wind.get("start_fraction") == reserve.get("start_fraction")
    if same_scale and same_start and reserve.get("in_round_recovery_per_tick") \
            == wind.get("recovery_per_tick_by_action", {}).get("rest"):
        errs.append("Wind and Reserve share scale, start and recovery - they "
                    "have collapsed into one resource with two names")
    return errs


def check_reserve(docs: dict) -> list:
    """Reserve's in-round recovery is EXACTLY zero.

    Not "small". A fighter who gets his legs back by waiting has no reason to
    pace a fight, and the whole late-round texture Decision 0021 is buying
    disappears.
    """
    r = docs["economy"]["reserve"]
    errs = []
    if r.get("in_round_recovery_per_tick") != 0:
        errs.append("Decision 0021: reserve.in_round_recovery_per_tick is %r "
                    "and must be exactly 0 - Reserve does not come back inside "
                    "a round" % r.get("in_round_recovery_per_tick"))
    between = r.get("between_rounds_recovery")
    if not isinstance(between, (int, float)) or between <= 0:
        errs.append("Reserve has no between-rounds recovery, so a corner does "
                    "nothing and conditioning is a one-way ratchet")
    elif between >= r.get("max", 0):
        errs.append("the corner restores the entire Reserve pool, which erases "
                    "the history of the fight between rounds")
    return errs


def check_recovery_ordering(docs: dict) -> list:
    """No state recovers Wind faster than Rest, and working recovers none.

    Also carries THE UNITS GUARD. The 2026-08-03 error was repeated on
    2026-08-07 inside a block whose own comment cited the correction: rates
    authored as small per-tick decimals that actually carry per-second
    magnitude. They look innocent until multiplied by the round length, and a
    pool that refills inside one round means no fighter ever tires at any work
    rate. That is not a tuning problem, it is a silent deletion of the
    mechanic, so it fails here rather than being noticed in a probe.
    """
    wind = docs["economy"]["wind"]
    rates = wind.get("recovery_per_tick_by_action", {})
    pool = wind.get("max", 0)
    errs = []

    for a in ACTIONS:
        if a not in rates:
            errs.append("no Wind recovery rate declared for %r - silence is "
                        "not a rate" % a)
    if errs:
        return errs

    rest = rates["rest"]
    for a in ACTIONS:
        if rates[a] > rest:
            errs.append("Decision 0021: %r recovers Wind faster than rest" % a)
        if a in NO_RECOVERY and rates[a] != 0:
            errs.append("Decision 0021: %r recovers Wind, but working buys "
                        "none back" % a)

    for a in ACTIONS:
        per_round = rates[a] * ROUND_TICKS
        if per_round > pool:
            errs.append(
                "%r recovers %.1f Wind per %d-tick round against a pool of "
                "%.1f - a rate that can refill the pool inside one round means "
                "nobody ever tires. This is the units error, twice made."
                % (a, per_round, ROUND_TICKS, pool))
    return errs


def check_indirect_only(docs: dict) -> list:
    """Reserve reaches vulnerability through Wind, never as a direct term.

    Decision 0021 refuses a second direct multiplier until the indirect path is
    proven insufficient, because a direct term would count deep fatigue twice -
    once in the Wind a fighter has and again in what that Wind is worth.

    HONEST SCOPE. This checks that both indirect paths are declared and
    complete, and that the prohibition is on the record. It cannot prove that
    no consumer anywhere reads Reserve directly; that is what the prohibition
    and review are for, and pretending otherwise would be the same overclaim
    this validator exists to prevent.
    """
    wind = docs["economy"]["wind"]
    errs = []

    ceiling = wind.get("ceiling_from_reserve")
    recovery = wind.get("recovery_from_reserve")
    if not ceiling:
        errs.append("the Wind ceiling no longer depends on Reserve - indirect "
                    "path one is gone, and Reserve reaches nothing")
    if not recovery:
        errs.append("Wind recovery no longer depends on Reserve - indirect "
                    "path two is gone")
    if errs:
        return errs

    floor, span = ceiling.get("floor_fraction"), ceiling.get("span_fraction")
    if floor is None or span is None:
        errs.append("the Wind ceiling declares no floor/span pair")
    elif abs((floor + span) - 1.0) > 1e-9:
        errs.append("ceiling floor %.4f + span %.4f != 1.0, so a fighter at "
                    "full Reserve could never hold a full pool and a fresh "
                    "fighter could never be fresh" % (floor, span))
    elif floor <= 0:
        errs.append("the Wind ceiling floor is %.4f - at zero Reserve a "
                    "fighter would hold no Wind at all, which is a direct "
                    "knockout by conditioning and exactly the second direct "
                    "term Decision 0021 refuses" % floor)

    rfloor, rspan = recovery.get("floor_multiplier"), recovery.get("span_multiplier")
    if rfloor is None or rspan is None:
        errs.append("Wind recovery from Reserve declares no floor/span pair")
    elif rfloor <= 0:
        errs.append("the recovery floor multiplier is %.4f - a drained fighter "
                    "would recover nothing ever, which is a direct term in "
                    "disguise" % rfloor)

    declared = " ".join(docs["economy"].get("prohibitions", []))
    if "direct multiplier" not in declared:
        errs.append("the prohibition on a second direct multiplier is no "
                    "longer declared in the file it governs")
    return errs


def check_effort_is_decoupled(docs: dict) -> list:
    """effort, wind_cost and reserve_load are separately authored.

    The test is not that the three differ somewhere - a constant multiple
    differs everywhere and is still one number wearing three names. The test is
    that the RATIOS vary, and specifically that the body-shot inversion holds:
    body work of equal effort costs LESS breath and MORE conditioning than head
    work. A scaled copy cannot express that, so if it ever stops being true the
    decoupling has quietly collapsed.
    """
    moves = docs["effort"].get("moves", [])
    errs = []
    if not moves:
        return ["the effort table declares no moves"]

    authored = [m for m in moves if m.get("cost_model") != "displacement"]
    for m in authored:
        for field in ("effort", "wind_cost", "reserve_load"):
            if m.get(field) is None:
                errs.append("move %r declares no %s, and a missing cost is not "
                            "a free one" % (m.get("move_id"), field))
    if errs:
        return errs

    ratios = {round(m["wind_cost"] / m["effort"], 9) for m in authored
              if m["effort"]}
    if len(ratios) <= 1:
        errs.append("every authored move has the same wind_cost/effort ratio, "
                    "so wind_cost is effort scaled by a constant - Decision "
                    "0021's decoupling is decorative")

    by_id = {m["move_id"]: m for m in authored}
    head, body = by_id.get("hook_lead"), by_id.get("body_hook_lead")
    if head and body:
        if head["effort"] != body["effort"]:
            errs.append("hook_lead and body_hook_lead no longer share an "
                        "effort, so the inversion can no longer be read off "
                        "them - point the check at a matched pair")
        elif not (body["wind_cost"] < head["wind_cost"]
                  and body["reserve_load"] > head["reserve_load"]):
            errs.append(
                "body and head work of equal effort no longer differ in the "
                "two tiers: body wind %.4f vs head %.4f, body reserve %.4f vs "
                "head %.4f. The three-value model has collapsed."
                % (body["wind_cost"], head["wind_cost"],
                   body["reserve_load"], head["reserve_load"]))

    disp = [m for m in moves if m.get("cost_model") == "displacement"]
    for m in disp:
        if m.get("wind_cost") is not None or m.get("reserve_load") is not None:
            errs.append("displacement-priced move %r also authors a flat cost, "
                        "so it has two prices and the reader picks one"
                        % m["move_id"])
    if disp:
        rates = docs["effort"].get("displacement_movement", {})
        for key in ("wind_per_ru", "reserve_per_ru"):
            if rates.get(key) is None:
                errs.append("moves are displacement-priced but %s is not "
                            "declared - null means 'ask the locomotion model', "
                            "and the model has no answer" % key)
    return errs


def check_calibration_is_not_claimed(docs: dict) -> list:
    """Nothing here is fitted, and the file must keep saying so.

    Decision 0021 step 7 forbids calibration until the integrated policy
    produces boxing-like cadence, and Decision 0024 reduced the 66/120/200
    punch counts to sanity probes. A `values_are_fitted: true` appearing
    without a `fitted_against` is how tuning gets cited as evidence.
    """
    errs = []
    for name, doc in (("stamina_economy", docs["economy"]),
                      ("generic_sandbox_effort", docs["effort"])):
        cal = doc.get("calibration_status")
        if not cal:
            errs.append("%s declares no calibration_status, so a reader cannot "
                        "tell a hypothesis from a fitted value" % name)
            continue
        if cal.get("values_are_fitted") and not cal.get("fitted_against"):
            errs.append("%s claims its values are fitted but names nothing "
                        "they were fitted against" % name)
    return errs


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 09:45 UTC | START edit: Decision 0026 ]
def check_recovery_hysteresis(docs: dict) -> list:
    """Recovery-seeking enters and exits on different declared thresholds.

    Ruling B: "entering recovery intent must use hysteresis: one
    threshold/condition enters recovery-seeking behavior and a separate
    recovered condition exits it, preventing one-tick oscillation."

    One threshold means a fighter crosses it, stops recovering, spends, crosses
    back and recovers again - on alternate ticks, forever. The first integrated
    round did a coarser version of exactly that, and its Wind trace was a flat
    line at the entry threshold for 165 seconds.
    """
    errs = []
    wind = docs["economy"].get("wind", {})
    low = wind.get("low_threshold_fraction")
    exit_at = wind.get("recovery_exit_fraction")
    exhausted = wind.get("exhausted_threshold_fraction")
    if exit_at is None:
        return ["wind declares no recovery_exit_fraction, so recovery intent "
                "has a single threshold and no hysteresis (Decision 0026 B)"]
    if low is None:
        return ["wind declares no low_threshold_fraction to enter recovery on"]
    if not exit_at > low:
        errs.append("recovery exits at %s and enters at %s: the exit must be "
                    "strictly above the entry or the two conditions are one "
                    "condition" % (exit_at, low))
    if exit_at > 1.0:
        errs.append("recovery exits at %s of the pool, which is above full - a "
                    "fighter could never stop seeking recovery" % exit_at)
    if exhausted is not None and not low > exhausted:
        errs.append("the low threshold %s is not above the exhausted threshold "
                    "%s, so the two crisis lines have collapsed"
                    % (low, exhausted))
    return errs


def check_source_basis(docs: dict) -> list:
    """Every stamina source declares the unit it is charged in.

    Ruling D, and the reason for it is three repetitions of one mistake: twice
    a per-second recovery rate consumed as per-tick, once a per-step distance
    consumed as per-tick. All three passed review because every number involved
    looks like a small decimal.

    This checks the declaration is complete and honest against the files it
    describes. It cannot by itself stop a reader misusing a correctly declared
    number - `tests/test_stamina_units.py` carries the five behavioural proofs
    Ruling D also requires.
    """
    errs = []
    econ = docs["economy"]
    basis = econ.get("source_basis")
    if not basis:
        return ["stamina_economy declares no source_basis block, so no stamina "
                "source states whether it is per tick, per second, per "
                "reach-unit, per action or per round break (Decision 0026 D)"]
    allowed = set(basis.get("allowed", ()))
    if not allowed:
        errs.append("source_basis declares no allowed bases, so any string "
                    "would satisfy it")
    sources = basis.get("sources") or {}
    for key, unit in sorted(sources.items()):
        if unit not in allowed:
            errs.append("source %r declares basis %r, which is not one of %s"
                        % (key, unit, ", ".join(sorted(allowed))))

    # The declaration must actually cover what the economy contains. A basis
    # block that names four of nine sources is worse than none: it reads as
    # complete.
    required = [
        ("wind.recovery_per_tick_by_action.*",
         econ.get("wind", {}).get("recovery_per_tick_by_action")),
        ("wind.between_rounds_recovery_fraction",
         econ.get("wind", {}).get("between_rounds_recovery_fraction")),
        ("reserve.in_round_recovery_per_tick",
         econ.get("reserve", {}).get("in_round_recovery_per_tick")),
        ("reserve.between_rounds_recovery",
         econ.get("reserve", {}).get("between_rounds_recovery")),
        ("reserve.drains.sustained_exertion_per_tick_below_low_wind.value",
         econ.get("reserve", {}).get("drains", {})
             .get("sustained_exertion_per_tick_below_low_wind", {}).get("value")),
        ("displacement_movement.wind_per_ru",
         docs["effort"].get("displacement_movement", {}).get("wind_per_ru")),
        ("displacement_movement.reserve_per_ru",
         docs["effort"].get("displacement_movement", {}).get("reserve_per_ru")),
    ]
    for key, present in required:
        if present is not None and key not in sources:
            errs.append("%s exists in canon and declares no basis" % key)

    if any(m.get("wind_cost") is not None for m in docs["effort"].get("moves", ())):
        if "moves[].wind_cost" not in sources:
            errs.append("moves author wind_cost and it declares no basis")

    # The step length is the number that caused the defect. It must be named
    # here as NOT a stamina source, so the next reader meets the warning before
    # meeting the number.
    not_a_source = basis.get("not_a_stamina_source") or {}
    for key in ("movement_model.locomotion.modes[].stride_length_ru",
                "movement_model.locomotion.max_frame_displacement_ru"):
        if key not in not_a_source:
            errs.append("%s is not declared as 'not a stamina source', and it "
                        "is precisely the number that was billed as one on "
                        "2026-08-08" % key)
    return errs
# [ ... | 2026-08-08 09:45 UTC | END edit ]


ALL_CHECKS = (
    ("two layers are distinct", check_layers),
    ("recovery intent has hysteresis", check_recovery_hysteresis),
    ("every stamina source declares its basis", check_source_basis),
    ("Reserve does not regenerate in round", check_reserve),
    ("work never pays better than rest (and the units guard)",
     check_recovery_ordering),
    ("Reserve reaches vulnerability only indirectly", check_indirect_only),
    ("effort is not wind cost", check_effort_is_decoupled),
    ("calibration is not claimed", check_calibration_is_not_claimed),
)
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-07 07:40 UTC | END ]
