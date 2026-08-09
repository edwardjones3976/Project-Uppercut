# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 22:50 UTC | START ]
"""Contact, condition, knockdown, count and stoppage for the integrated bout.

THE CHAIN THAT LETS A FIGHT END. Until this module a punch that arrived was a
row and nothing else; now it is a contact, the contact wears a region down,
the worn region reaches a knockdown, the knockdown starts a count, and the
count - or the referee - can end the bout. Every threshold, pacing value and
limit is read from canon; every structural choice this module makes itself is
named in place and marked as structure, not tuning.

TWO NAMED SIMPLIFICATIONS, both with precedent and both deliberate:

  CONTACT QUALITY IS "solid".  Phase N's own analyzer declares
    `GRADED = "solid"` as "the named simplification, in one place", and the
    integrated bout starts at the same place: an arrived punch is a solid
    contact. The graded pipeline (glancing/partial/clean) belongs to the
    collision model and arrives when it does. Until then, no term here
    pretends to a quality resolution that does not exist.

  CONDITION DAMAGE IS AUTHORED EFFORT.  Decision 0021 separates a move's
    `effort` (the impact-scale number) from its resource costs precisely so
    effort can serve the impact side. No damage coefficient is invented on
    top of it: one point of effort is one point of regional condition, against
    canon's authored capacity of 100 per region. That identity is a structural
    hypothesis like every unfitted number in this project, and it is a READ
    number, not a written one.

WHAT A PUNCH TARGETS IS THE WHOLE LIST, NOT ELEMENT ZERO.
`generic_sandbox_moves.json` authors `target_regions` as an ordered LIST and
canon marks `knockdown_relevant` on regions, not on moves. Reading only
`target_regions[0]` made JSON array position the authority over which punches
can end a fight - `hook_lead` is authored `["head", "jaw_chin"]`, so the hook
already targets the jaw and was being refused the jaw's consequence. Decision
0026: array position is not authority. So:

  * ELIGIBILITY reads every authored region. "Can this punch find the jaw" is
    answerable from canon alone and needs no placement resolution.
  * PLACEMENT keeps one primary region, and that is a DELIBERATE non-change.
    Splitting force across a move's regions would need a distribution this
    module does not have: which region a multi-region punch actually finds is
    contact quality and placement, and contact quality is the named
    simplification directly above. Inventing a split (1/N, or full force to
    each) is inventing the graded-placement resolution under another name, and
    the numbers would not be canon's. Named here so the next reader meets the
    limit deliberately rather than discovering it.

DELIVERED IMPACT IS CANON'S, NOT THIS MODULE'S.  `punch_model.delivered_impact`
authors `derived_from: stamina_cost`, `normalization: linear over the punch
table's own stamina_cost range`, `min_impact_scalar` and `max_impact_scalar`,
and `applies_to: [condition_damage, knockdown_pressure]`. This module used to
compute its own force term as `effort / max(all efforts)`. That was a second
authority on delivered impact and it was the weaker one: the maximum was taken
over EVERY authored move, so `overhand_rear` - which the integrated contract's
punch vocabulary does not contain and which therefore cannot be thrown - set
the scale for every punch that can, and any future high-effort move would have
silently rescaled the whole fight. Canon's normalisation is over the punch
table only and is floored at `min_impact_scalar`, which is what makes canon's
own sentence true: "there is no harmless punch". Canon's reading wins; the
local one is deleted rather than kept beside it.

NO DICE. Canon: "never a dice roll attached to a punch"
(`flat_random_roll_per_punch: false`). Everything below is a deterministic
function of observable state. The `knockdown_recovery` RNG substream exists
and is deliberately not consumed - randomness enters when canon authors a
distribution, not when an implementer wants one.
"""
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ONE = 10000
CONDITION = os.path.join("data", "condition_model.json")
EFFORT = os.path.join("data", "moves", "generic_sandbox_effort.json")
REFEREES = os.path.join("data", "referees")
REF_SEMANTICS = os.path.join("data", "referee_semantics.json")
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: D3 canon paths ]
MOVES = os.path.join("data", "moves", "generic_sandbox_moves.json")
PUNCH_MODEL = os.path.join("data", "punch_model.json")
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: D3 canon paths ]


def _read(rel):
    with io.open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return json.load(fh)


def _q(v):
    return int(round(float(v) * ONE))


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: D3 region reading, delivered_impact, impairment ]
# A region name a move targets that canon's damage_regions never declared.
# It cannot be knockdown-relevant, because knockdown_relevant is a property
# canon writes on a declared region and nowhere else. `guard_high` authors
# `guard_integrity`, which is an attribute rather than a region, so this case
# is real and is answered rather than crashed - but only for moves nobody
# declared a punch. A declared PUNCH targeting an undeclared region is a canon
# error and `condition_pack` says so.
_UNDECLARED_REGION = {"knockdown_relevant": False}


def _impact_scalars(di, punches, costs):
    """canon's `punch_model.delivered_impact`, in q10000.

    "linear over the punch table's own stamina_cost range", onto
    [min_impact_scalar, max_impact_scalar]. Every number here is read; the only
    thing this function decides is the order of the arithmetic, and it is
    ordered to keep the multiply before the divide so the fixed-point result
    does not lose the span to an early floor.
    """
    lo_s, hi_s = _q(di["min_impact_scalar"]), _q(di["max_impact_scalar"])
    span = hi_s - lo_s
    known = [p for p in punches if p in costs]
    if not known:
        return {}, "no declared punch has an authored stamina_cost"
    lo, hi = min(costs[p] for p in known), max(costs[p] for p in known)
    if hi == lo:
        return {}, ("the declared punch vocabulary carries a single "
                    "stamina_cost, so canon's linear normalisation over the "
                    "punch table's range has no range to be linear over")
    return {p: lo_s + (span * (costs[p] - lo)) // (hi - lo) for p in known}, None


def condition_pack(punches=None):
    """Canon's condition, knockdown and count rules, q10000, nothing invented.

    `punches` is the caller's declared punch vocabulary, taken the same way
    `evade_pack(regions)` and `punch_frames(punches)` take theirs and for the
    same reason: canon normalises delivered impact "linear over the PUNCH
    table's own stamina_cost range", which is undefined until something says
    which moves are punches - and punch-ness is declared, never inferred from
    a category string. The default is this package's own contract vocabulary,
    imported inside the function so the module's import graph stays exactly as
    narrow as it was.
    """
    if punches is None:
        from tools.uppercut_integrated import contract as _C
        punches = _C.PUNCHES
    punches = tuple(punches)

    d = _read(CONDITION)
    kd = d["knockdown"]
    mods = kd["pressure_modifiers"]
    regions = {r["region"]: {
        "capacity": _q(r["capacity"]),
        "recovers_between_rounds": _q(r["recovers_between_rounds"]),
        "knockdown_relevant": bool(r.get("knockdown_relevant")),
        # Carried because canon's impairment note says the multipliers read
        # "the mean of the relevant regions", and the relevant regions are the
        # ones canon says an attribute is impaired BY. Reading `impairs` is
        # how that stays canon's list instead of becoming a list written here.
        "impairs": tuple(r.get("impairs", ())),
    } for r in d["damage_regions"]}

    eff = _read(EFFORT)
    efforts = {m["move_id"]: _q(m["effort"]) for m in eff["moves"]}
    if not efforts:
        raise SystemExit("no authored efforts - a contact model with no force "
                         "scale cannot exist")

    # THE D3 FIX'S WHOLE SUBSTANCE: the authored list is read as a list.
    mt = _read(MOVES)
    table = mt["moves"] if isinstance(mt, dict) else mt
    move_regions = {m["id"]: tuple(m.get("target_regions") or ())
                    for m in table}
    # `stamina_cost` must be PRESENT, not defaulted: a punch silently costing
    # 0.0 would become the bottom of canon's normalisation range and shift the
    # impact of every other punch. Absent means absent, and the checks below
    # name the punch rather than inventing a cost for it.
    costs = {m["id"]: _q(m["stamina_cost"]) for m in table
             if "stamina_cost" in m}

    impact, impact_err = _impact_scalars(
        _read(PUNCH_MODEL)["delivered_impact"], punches, costs)

    imp = d.get("impairment") or {}

    def _imp(name):
        return _q(imp[name]) if name in imp else None

    ticks_per = int(kd["count_ticks_per_number"])
    c = {
        "regions": regions,
        "efforts": efforts,
        "punches": punches,
        # move id -> every region canon authors it to target, authored order.
        "move_regions": move_regions,
        # move id -> canon's delivered-impact scalar. Replaces this module's
        # own `effort / max(effort)`, which was a second authority normalised
        # over moves that cannot be thrown. `effort_max` is gone with it
        # rather than left in the pack unread.
        "impact": impact,
        "impairment": {
            "stamina_regen_at_full_torso":
                _imp("stamina_regen_multiplier_at_full_torso"),
            "between_rounds_recovery_at_full_torso":
                _imp("between_rounds_recovery_multiplier_at_full_torso"),
            "guard_extent_at_full_arms":
                _imp("guard_extent_multiplier_at_full_arms"),
            "arm_damage_fraction_of_blocked_force":
                _imp("arm_damage_fraction_of_blocked_force"),
            "expressed": tuple(imp.get("expressed", ())),
            "not_yet_expressed": tuple(imp.get("not_yet_expressed", ())),
        },
        "pressure_threshold": _q(kd["pressure_threshold"]),
        "caught_committed": _q(mods["caught_committed_multiplier"]),
        "balanced": _q(mods["balanced_multiplier"]),
        "unguarded_lane_bonus": _q(mods["unguarded_lane_bonus"]),
        # The floor of the accumulated-condition term. Canon's own note calls
        # the day this was a bare 0.35 inside a simulator a defect; it is read
        # here and refused if absent.
        "undamaged_baseline": _q(mods["undamaged_baseline"])
        if "undamaged_baseline" in mods else None,
        "count_ticks_per_number": int(kd["count_ticks_per_number"]),
        "count_to": int(kd["count_to"]),
        "mandatory_eight": bool(kd["mandatory_eight_count"]),
        "count_condition_relief": _q(kd["count_condition_relief_fraction"]),
        "count_stamina_relief": _q(kd["count_stamina_relief_fraction"]),
        # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09
        #   10:20 UTC | edit: Decision 0033 Ruling 2 ] `max_per_round` and
        # `max_per_bout` are removed from this pack. Decision 0034 Ruling 4 keeps
        # them physically in condition_model.json as validator-bound echoes
        # for frozen Phases N/K - gone from HERE, not from the file.
        # They were contest rules living in the arithmetic file, read by the
        # bout while the authored rulesets - which explicitly switch them off
        # under professional rules - were read by nothing. Knockdown-count
        # stoppage now comes from `ruleset_pack()` exclusively, where null
        # means "no stoppage by that mechanism" and never "use a default".
        "rise_window_ticks": int(kd["rise_window_ticks"]),
        # WHERE THE NUMBER EIGHT COMES FROM. `rise_window_ticks` was loaded
        # and never read, and the count loop carried a literal 8 instead.
        # 480 ticks / 60 ticks per number IS canon's mandatory eight, exactly,
        # so reading it deletes an invented literal and changes no tick. It is
        # NOT a rise-time curve: canon authors no mapping from condition to
        # how long a man takes to get up, and inventing one is a new number.
        "mandatory_count_number":
            (int(kd["rise_window_ticks"]) // ticks_per) if ticks_per else 0,
        "errors": [],
    }
    if c["undamaged_baseline"] is None:
        c["errors"].append(
            "knockdown.pressure_modifiers authors no undamaged_baseline - the "
            "single number deciding whether an early knockout is reachable is "
            "unauthored, which canon's own note names as a defect")
    if c["pressure_threshold"] <= 0:
        c["errors"].append("a zero pressure threshold ends every fight on the "
                           "first contact")
    if not any(r["knockdown_relevant"] for r in regions.values()):
        c["errors"].append("no region is knockdown_relevant, so no fight can "
                           "ever end by knockout")
    if impact_err:
        c["errors"].append("punch_model.delivered_impact cannot be read: %s"
                           % impact_err)
    if c["mandatory_eight"] and c["mandatory_count_number"] != 8:
        c["errors"].append(
            "knockdown authors mandatory_eight_count but rise_window_ticks %d "
            "over count_ticks_per_number %d is %d, not 8. Canon contradicts "
            "itself about when a fighter may rise; refused rather than picking "
            "one." % (c["rise_window_ticks"], ticks_per,
                      c["mandatory_count_number"]))
    if "stamina" in c["impairment"]["expressed"] \
            and c["impairment"]["stamina_regen_at_full_torso"] is None:
        c["errors"].append(
            "condition_model.impairment lists stamina as EXPRESSED and authors "
            "no stamina_regen_multiplier_at_full_torso, so body work would "
            "accumulate against a consequence canon says exists")
    for p in punches:
        targets = move_regions.get(p)
        if not targets:
            c["errors"].append(
                "%r is a declared punch and canon's move table gives it no "
                "target_regions, so it lands nowhere" % (p,))
            continue
        unknown = [r for r in targets if r not in regions]
        if unknown:
            c["errors"].append(
                "%r targets %s, which condition_model.damage_regions does not "
                "declare - a punch cannot land on a region the corner cannot "
                "see" % (p, ", ".join(sorted(unknown))))
        if p not in efforts:
            c["errors"].append(
                "%r is a declared punch with no authored effort, so it would "
                "wear a region by an amount nobody wrote" % (p,))
        if impact and p not in impact:
            c["errors"].append(
                "%r is a declared punch with no authored stamina_cost, so "
                "canon's delivered impact has nothing to derive from" % (p,))
    return c


def contact_regions(pack, move_id):
    """Every region canon authors this move to target, in the authored order.

    Fails closed on an unknown move id. This codebase has never let an
    unrecognised id mean "free", and a punch whose target is unknown is a
    punch whose consequence would have to be invented.
    """
    targets = pack["move_regions"].get(move_id)
    if targets is None:
        raise KeyError(
            "%r is not in canon's move table, so what it targets is unknown. "
            "Refused rather than defaulted." % (move_id,))
    return targets


def primary_region(pack, move_id):
    """The one region a solid contact's force is PLACED in.

    The first authored region canon also declares a damage region. For every
    punch in the table that is `target_regions[0]`, so this is behaviour the
    bout already had - but it is now a stated rule with a stated limit (see
    the module docstring) rather than an array subscript, and it refuses a
    move whose authored regions are all undeclared instead of raising deep
    inside `absorb`.
    """
    for r in contact_regions(pack, move_id):
        if r in pack["regions"]:
            return r
    raise KeyError(
        "%r targets only regions condition_model.damage_regions does not "
        "declare, so a contact from it has nowhere to land" % (move_id,))


def knockdown_regions(pack, move_id):
    """The knockdown-relevant regions this move is authored to target.

    THE D3 FIX. Every authored region is read, not element zero. `hook_lead`
    is authored ["head", "jaw_chin"]; the hook targets the jaw and now carries
    the jaw's consequence. Reordering the JSON array changes nothing here,
    which is Decision 0026 applied where it was being violated.
    """
    return tuple(r for r in contact_regions(pack, move_id)
                 if pack["regions"].get(r, _UNDECLARED_REGION)
                 ["knockdown_relevant"])


def knockdown_capable(pack, move_id):
    """Can this punch put a man down at all. Canon's question, canon's answer."""
    return bool(knockdown_regions(pack, move_id))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: D3 region reading, delivered_impact, impairment ]


def referee_pack(referee_id):
    """One official's profile plus the shared stoppage semantics."""
    prof = _read(os.path.join(REFEREES, "%s.json" % referee_id))
    sem = _read(REF_SEMANTICS)
    disposition = prof["enforcement"]["stoppage_disposition"]
    thresholds = {row["level"]: row["value"]
                  for row in sem["stoppage"]
                  ["unanswered_after_knockdown_by_stoppage_disposition"]}
    if disposition not in thresholds:
        raise SystemExit(
            "referee %r has stoppage disposition %r, which the shared "
            "semantics do not author. Refused rather than defaulted."
            % (referee_id, disposition))
    return {
        "id": prof["id"],
        "display_name": prof["display_name"],
        "disposition": disposition,
        # None means: defer entirely to the count and the knockdown limits.
        "unanswered_stop": thresholds[disposition],
    }


class RegionalCondition(object):
    """One fighter's accumulated damage, per canon's declared regions."""

    __slots__ = ("damage", "pack")

    def __init__(self, pack):
        self.pack = pack
        self.damage = {r: 0 for r in pack["regions"]}

    def absorb(self, region, force):
        """A solid contact wears its region. Returns the region's new fraction."""
        if region not in self.damage:
            raise KeyError(
                "%r is not a declared damage region. An unauthored region "
                "absorbing force is damage the corner cannot see." % (region,))
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: absorb refuses negative force ]
        # Decision 0025's rule again: refused, not normalised. Negative force
        # is unreachable today - force is an authored effort - but it would
        # drive `fraction` below zero, push the accumulated-condition term
        # under canon's baseline, and make a punch HEAL a jaw. Fail closed.
        if force < 0:
            raise ValueError(
                "force %d into %r is negative. A contact cannot undo damage; "
                "recovery is the corner's job and the count's, and both have "
                "their own authored rates." % (force, region))
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: absorb refuses negative force ]
        cap = self.pack["regions"][region]["capacity"]
        self.damage[region] = min(cap, self.damage[region] + force)
        return self.fraction(region)

    def fraction(self, region):
        cap = self.pack["regions"][region]["capacity"]
        return (self.damage[region] * ONE) // cap if cap else 0

    def worst_knockdown_fraction(self):
        return max((self.fraction(r) for r, spec in self.pack["regions"].items()
                    if spec["knockdown_relevant"]), default=0)

    def between_rounds(self):
        """The corner works on damage at canon's authored per-region rates."""
        for r, spec in self.pack["regions"].items():
            relief = (self.damage[r] * spec["recovers_between_rounds"]) // ONE
            self.damage[r] -= relief

    def count_relief(self):
        """What the eight seconds on one knee buy. Partial, per canon: the
        count buys clarity, never a fresh fighter."""
        frac = self.pack["count_condition_relief"]
        for r in self.damage:
            self.damage[r] -= (self.damage[r] * frac) // ONE

    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | START edit: impairment reading ]
    def mean_fraction(self, attribute):
        """The mean condition of the regions canon says impair `attribute`.

        The region list is canon's own `impairs`, not a list of region names
        written here - so "which regions are the torso" is answered by the
        file that declares the torso.
        """
        fracs = [self.fraction(r) for r, spec in self.pack["regions"].items()
                 if attribute in spec["impairs"]]
        return sum(fracs) // len(fracs) if fracs else 0

    def impairment_multiplier(self, attribute, at_full):
        """Canon: "All multipliers interpolate linearly from 1.0 at zero
        condition to the stated value at full capacity, reading the mean of
        the relevant regions." That sentence is the whole of this function;
        no coefficient is chosen here.

        `at_full` of None means canon authors no coefficient for this use, and
        an unauthored impairment is 1.0 - no effect, declared - rather than a
        guess.
        """
        if at_full is None:
            return ONE
        return ONE - ((ONE - at_full) * self.mean_fraction(attribute)) // ONE

    def stamina_regen_multiplier(self):
        """What accumulated body damage does to getting your breath back.

        Canon authors the coefficient (`impairment.stamina_regen_multiplier_at
        _full_torso`) and lists `stamina` as EXPRESSED. THIS MODULE DOES NOT
        APPLY IT: Wind recovery is computed in `uppercut_stamina.economy`,
        which this section does not own. The reading lives here because the
        coefficient and the damage both do; the multiplication has to happen
        where the recovery is. Until a caller uses this, body investment still
        changes nothing - and that is now a wiring gap with a named end, not a
        value nobody read.
        """
        return self.impairment_multiplier(
            "stamina", self.pack["impairment"]["stamina_regen_at_full_torso"])
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 02:05 UTC | END edit: impairment reading ]


def knockdown_pressure(pack, move_id, defender_condition, defender_wind_fraction,
                       defender_committed, defender_evading):
    """The deterministic pressure a solid contact puts on a fighter's legs.

    STRUCTURE, DECLARED ONCE. Canon authors the inputs, the threshold, the
    modifiers and the baseline; canon does not author the combining shape, so
    this module does, in the simplest form that uses every authored term and
    invents no constant:

        force      = punch_model.delivered_impact scalar     (CANON's scale)
        condition  = baseline + (1 - baseline) * worst_knockdown_region
        fatigue    = 1 + (1 - wind_fraction)                 (bounded, x2 max)
        pressure   = force * condition * fatigue * modifiers

    Every term is in [0, ~2]; the threshold that decides how often fights end
    early is canon's 0.57 and stays canon's. When the collision model brings
    graded contact quality and closing velocity, they enter here as factors
    and this docstring is rewritten - that is expected evolution, not drift.

    THE FORCE TERM WAS THIS MODULE'S AND IS NOW CANON'S. It read
    `effort / max(every authored effort)`, which put the scale of every punch
    in the fight under a move the contract's punch vocabulary does not contain
    and which therefore cannot be thrown, and gave the jab no floor. Canon
    authors the derivation, the normalisation, the floor and the ceiling in
    `punch_model.delivered_impact`. Two authorities on one quantity is the
    defect this project has just spent a ruling removing; the local one is
    deleted, not kept beside it.

    CALLER'S NOTE ON `pressure_threshold`. Canon's own threshold note says a
    threshold "is only meaningful against the volume it was measured at". The
    0.57 sweep was run when exactly one authored move could reach a
    knockdown-relevant region. Reading `target_regions` correctly makes four
    of the five contract punches knockdown-capable, so the threshold now faces
    a population it was not measured against. That is a re-sweep and a
    Director disposition (Decision 0033 Ruling 1 fixes the sequence: land the
    fix, MEASURE, then dispose); it is deliberately NOT a number changed here.
    """
    if defender_wind_fraction < 0:
        # Decision 0025's rule, one layer up: an out-of-range input is refused,
        # not normalised. A negative Wind fraction would push `fatigue` past
        # the x2 this docstring promises and quietly uncap the whole model.
        raise ValueError(
            "defender wind fraction %d is negative. Wind is authoritative on "
            "[0, max]; a negative fraction is an invalid state, not a third "
            "exhaustion regime." % (defender_wind_fraction,))
    try:
        force = pack["impact"][move_id]
    except KeyError:
        raise KeyError(
            "%r has no delivered-impact scalar, so how hard it lands is "
            "unauthored. It is either not in the declared punch vocabulary "
            "this pack was built with, or canon's move table gives it no "
            "stamina_cost." % (move_id,))
    baseline = pack["undamaged_baseline"]
    condition = baseline + ((ONE - baseline)
                            * defender_condition.worst_knockdown_fraction()) // ONE
    fatigue = ONE + (ONE - min(ONE, defender_wind_fraction))
    pressure = force * condition // ONE
    pressure = pressure * fatigue // ONE
    if defender_committed:
        pressure = pressure * pack["caught_committed"] // ONE
    else:
        pressure = pressure * pack["balanced"] // ONE
    if defender_evading:
        # The mistimed evasion: the head was moving and the guard was not
        # there. Canon's unguarded-lane bonus, applied to the case Phase R
        # authored it for.
        pressure = pressure + pack["unguarded_lane_bonus"] * force // ONE
    return pressure


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 10:22 UTC | START edit: Decision 0033 Ruling 2 - rulesets rule the contest ]
RULESETS = os.path.join("data", "rulesets")


def ruleset_pack(ruleset_id, count_to=None):
    """The contest rules a bout is fought under. Decision 0019, finally read.

    Decisions 0014/0019 authored versioned rulesets and nothing ever loaded
    one: the bout stopped fights on knockdown limits it read from
    `condition_model.json` - limits the professional ruleset explicitly
    switches OFF - and thirty of thirty measured fights ended on exactly that
    rule while `decision_path_must_survive: true` was contradicted every time.
    Decision 0033 Ruling 2 splits the authority: `condition_model.knockdown`
    keeps the ARITHMETIC (the count clock is identical for every referee,
    Rule 16); the CONTEST RULES live here exclusively.

    NULL MEANS "NO STOPPAGE BY THAT MECHANISM", never "use a default". Under
    `professional` both knockdown counts are null, so no knockdown count ever
    stops a professional bout - a fighter is counted out, the referee stops
    it, or the cards decide it, which is what the sport's own rules say.

    Refusals, all fail-closed: an unknown ruleset id; `three_knockdown_rule:
    true` alongside a null per-round count (the rule's NAME asserting what its
    NUMBER denies is a canon contradiction, not a default opportunity); and a
    mandatory count number at or beyond `count_to`, because a fighter cannot
    rise at a number the count never reaches.
    """
    path = os.path.join(REPO, RULESETS, "%s.json" % ruleset_id)
    if not os.path.exists(path):
        raise SystemExit(
            "%r is not an authored ruleset (no %s). An unauthored contest is "
            "refused, never defaulted - the fight under the wrong rules is "
            "worse than no fight." % (ruleset_id, path))
    d = _read(os.path.join(RULESETS, "%s.json" % ruleset_id))

    def _limit(key):
        v = d[key]
        if v is None:
            return None
        n = int(v)
        if n <= 0:
            raise SystemExit("%s.%s is %r; a non-positive knockdown limit is "
                             "a contradiction, not a rule" % (ruleset_id, key, v))
        return n

    c = {
        "id": d["id"],
        "version": d.get("version"),
        "per_round": _limit("knockdowns_per_round_stoppage"),
        "per_bout": _limit("knockdowns_per_bout_stoppage"),
        "three_knockdown_rule": bool(d["three_knockdown_rule"]),
        "standing_eight_count": bool(d["standing_eight_count"]),
        "saved_by_the_bell": bool(d["saved_by_the_bell"]),
        "mandatory_count_numbers": d["mandatory_count_numbers"],
        "scoring": dict(d["scoring"]),
    }
    if c["id"] != ruleset_id:
        raise SystemExit("ruleset file %s declares id %r; a file that "
                         "disagrees with its own name is refused"
                         % (path, c["id"]))
    if c["three_knockdown_rule"] and c["per_round"] is None:
        raise SystemExit(
            "%s authors three_knockdown_rule: true with a null "
            "knockdowns_per_round_stoppage. The rule's name asserts what its "
            "number denies; refused rather than defaulted to 3." % ruleset_id)
    if count_to is not None and isinstance(c["mandatory_count_numbers"], int) \
            and c["mandatory_count_numbers"] >= int(count_to):
        raise SystemExit(
            "%s authors a mandatory count number (%d) at or beyond count_to "
            "(%d); a fighter cannot rise at a number the count never reaches"
            % (ruleset_id, c["mandatory_count_numbers"], int(count_to)))
    if c["saved_by_the_bell"]:
        raise SystemExit(
            "%s authors saved_by_the_bell: true, and the bout implements only "
            "the false case (a count that straddles the bell completes). "
            "Refused rather than silently ignoring an authored rule."
            % ruleset_id)
    if c["standing_eight_count"]:
        raise SystemExit(
            "%s authors standing_eight_count: true, which the bout does not "
            "model. Refused rather than silently ignoring an authored rule."
            % ruleset_id)
    return c
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09 10:22 UTC | END edit: Decision 0033 Ruling 2 - rulesets rule the contest ]
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 22:50 UTC | END ]
