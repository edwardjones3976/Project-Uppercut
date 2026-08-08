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

  DELIVERED FORCE IS AUTHORED EFFORT.  Decision 0021 separates a move's
    `effort` (the impact-scale number) from its resource costs precisely so
    effort can serve the impact side. No damage coefficient is invented on
    top of it: one point of effort is one point of regional condition, against
    canon's authored capacity of 100 per region. That identity is a structural
    hypothesis like every unfitted number in this project, and it is a READ
    number, not a written one.

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


def _read(rel):
    with io.open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return json.load(fh)


def _q(v):
    return int(round(float(v) * ONE))


def condition_pack():
    """Canon's condition, knockdown and count rules, q10000, nothing invented."""
    d = _read(CONDITION)
    kd = d["knockdown"]
    mods = kd["pressure_modifiers"]
    regions = {r["region"]: {
        "capacity": _q(r["capacity"]),
        "recovers_between_rounds": _q(r["recovers_between_rounds"]),
        "knockdown_relevant": bool(r.get("knockdown_relevant")),
    } for r in d["damage_regions"]}

    eff = _read(EFFORT)
    efforts = {m["move_id"]: _q(m["effort"]) for m in eff["moves"]}
    if not efforts:
        raise SystemExit("no authored efforts - a contact model with no force "
                         "scale cannot exist")

    c = {
        "regions": regions,
        "efforts": efforts,
        "effort_max": max(efforts.values()),
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
        "max_per_round": int(kd["max_per_round"]),
        "max_per_bout": int(kd["max_per_bout"]),
        "rise_window_ticks": int(kd["rise_window_ticks"]),
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
    return c


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


def knockdown_pressure(pack, move_id, defender_condition, defender_wind_fraction,
                       defender_committed, defender_evading):
    """The deterministic pressure a solid contact puts on a fighter's legs.

    STRUCTURE, DECLARED ONCE. Canon authors the inputs, the threshold, the
    modifiers and the baseline; canon does not author the combining shape, so
    this module does, in the simplest form that uses every authored term and
    invents no constant:

        force      = effort / effort_max                     (authored scale)
        condition  = baseline + (1 - baseline) * worst_knockdown_region
        fatigue    = 1 + (1 - wind_fraction)                 (bounded, x2 max)
        pressure   = force * condition * fatigue * modifiers

    Every term is in [0, ~2]; the threshold that decides how often fights end
    early is canon's 0.57 and stays canon's. When the collision model brings
    graded contact quality and closing velocity, they enter here as factors
    and this docstring is rewritten - that is expected evolution, not drift.
    """
    force = (pack["efforts"][move_id] * ONE) // pack["effort_max"]
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
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 22:50 UTC | END ]
