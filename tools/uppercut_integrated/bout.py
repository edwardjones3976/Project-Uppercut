# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 13:50 UTC | START ]
"""One integrated bout tick owner. The first time a policy decision moves a boxer.

WHAT THIS IS. The Director's next punch, stated in his own words: "make a policy
decision physically move a boxer through the existing range core, charge the
exact distance traveled, and record the result inside the integrated
authoritative stream." That sentence is the whole specification and this module
is the whole of it.

WHAT IT REFUSES TO BE. Another interpretation of range. Every rule about where a
fighter is, how far a step carries, what the ropes do to a retreat and which
band a separation belongs to comes from `tools.uppercut_range.core` - the same
rules Phase Q proved and the same rules `UppercutRangeCore` runs in C++.

That module did not exist this morning. Phase Q's Python rules lived inside a
phase analyzer, and the integrated contract may not import phase analyzers, so
integrating range meant importing an analyzer or copying its formulas. The
Director's stop condition names that case exactly and orders the seam extracted
first. It was, and Phase Q re-proved byte-identically afterwards.

WHAT THIS OWNS, and nothing more: the ORDER things happen in. Deliver owed
movement, resolve the band, decide, translate the decision into an intent,
charge what the tick actually cost. The order is a loop; the rules are borrowed.

THE CHARGE IS FROM WHAT MOVED, NOT WHAT WAS INTENDED. Decision 0026 Ruling C:
`movement_wind_cost = actual_authoritative_displacement_ru * 0.60`. A fighter
whose step is cut short by the displacement cap, refused by a body, or zeroed by
the ropes pays for the ground he covered and not a reach unit more. That is the
difference between this and the stand-in probe, and it is why this is the run
that can eventually carry tuning evidence and that one never could.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.uppercut_range import core as RANGE          # noqa: E402
from tools.uppercut_stamina import economy as E         # noqa: E402
from tools.uppercut_integrated import contract as C     # noqa: E402
from tools.uppercut_integrated import fighter as F      # noqa: E402
from tools.uppercut_integrated import policy as P       # noqa: E402
from tools.uppercut_integrated import rng as R          # noqa: E402
from tools.uppercut_units import quantities as U        # noqa: E402
from tools.uppercut_units import rates as RATES         # noqa: E402

# How a tactical answer becomes a movement INTENT the range core can price.
# Advance closes separation, retreat opens it, and a lateral step is the
# knowingly-inert one Phase Q already declares: separation is one number on one
# axis here, and the angle a lateral step changes has no coordinate to change.
INTENT = {
    P.ADVANCE: "step_in",
    P.RETREAT: "step_out",
    P.MICRO_ADJUST: "step_lateral",
}

# The economy's action FAMILY for each tactic. Decision 0024: a family decides
# recovery, a move id decides cost, and they are not interchangeable.
FAMILY = {
    P.OBSERVE: "observe",
    P.HOLD_POSITION: "hold_position",
    P.REST: "rest",
    P.MICRO_ADJUST: "micro_adjust",
    P.ADVANCE: "move",
    P.RETREAT: "move",
    P.GUARD: "guard",
    P.EVADE: "evade",
    P.ATTACK: "attack",
}

FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3


def fnv1a64(running, row):
    """FNV-1a 64 over a row's UTF-8 bytes, folded into a running value.

    The standard constants, and the same fold `UppercutFnv1a64` uses, so a C++
    port reproduces this without a second decision to make.
    """
    for b in row.encode("utf-8"):
        running = ((running ^ b) * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
    return running


class IntegratedBout(object):
    """The bout. One tick owner, one order of operations, borrowed rules."""

    def __init__(self, repo=REPO, seed=4242, rounds=1, round_ticks=180 * 60,
                 profiles=None, start_separation=None):
        self.repo = repo
        self.econ = E.economy_pack()
        if self.econ["errors"]:
            raise SystemExit("the stamina canon fails its own contract: %s"
                             % "; ".join(self.econ["errors"]))
        # Decision 0029: the rates arrive typed, and canon's own declared basis
        # is what types them. A field with no declared basis fails the load
        # rather than reaching a multiplication.
        self.rates = RATES.load()
        self.range = RANGE.range_pack()
        if self.range["canon_errors"]:
            raise SystemExit("the range canon fails its own contract: %s"
                             % "; ".join(self.range["canon_errors"]))

        self.state, self.rng, self.header_lines = C.new_bout(
            repo, seed, rounds, round_ticks)

        profiles = profiles or {
            C.DEFAULT_PARTICIPANTS[0]: P.Profile(6500, "mid"),
            C.DEFAULT_PARTICIPANTS[1]: P.Profile(4000, "inside"),
        }
        # Participants come from the contract's initial state, in the order it
        # declares them. That order decides who acts first within a tick and
        # nothing else - it never reaches a seed, because Decision 0026 derives
        # every fighter-local stream from the identity string alone.
        self.fighters = [F.FighterState(who, self.econ, profiles[who])
                         for who in self.state.participants]
        self.streams = {f.id: self.rng.stream("policy_intent", f.id)
                        for f in self.fighters}

        # The separation every phase before this one was frozen at, so the
        # first integrated round starts where the proven evidence ends.
        half = self.range["axis"] // 2
        gap = (start_separation if start_separation is not None
               else RANGE.q(0.90)) // 2
        self.fighters[0].pos = half - gap
        self.fighters[1].pos = half + gap
        for f in self.fighters:
            f.band = RANGE.band_at(self.range, self.separation())

        self.tick = 0
        self.rows = []
        self.charged_ru = 0          # every reach unit this bout has billed
        self.moved_ru = 0            # every reach unit actually travelled

    # ---------------------------------------------------------------- state --

    def separation(self):
        return self.fighters[1].pos - self.fighters[0].pos

    def _on_ropes(self, me):
        """Whether this fighter's back is against the ropes he is backing to."""
        other = self.fighters[1] if me is self.fighters[0] else self.fighters[0]
        edge = me.pos if me.pos < other.pos else self.range["axis"] - me.pos
        return edge <= self.range["ropes"]
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 13:50 UTC | END ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 14:00 UTC | START ]
    # ----------------------------------------------------------------- tick --

    def _deliver_movement(self, i, me):
        """Pay out displacement already owed, and return what ACTUALLY moved.

        Every rule here is the range core's. This function decides only the
        order: drain the cap, clamp to the ring, refuse to walk through a body,
        then measure. `applied` is read back off the position rather than taken
        from the drain, because the clamp and the ring can both take some of it
        away and the fighter must be billed for the ground he kept.
        """
        if me.pending == 0:
            return 0, ""
        applied, me.pending = RANGE.drain(self.range, me.pending)
        before = me.pos
        me.pos = max(0, min(self.range["axis"], me.pos + applied))

        flags = ""
        if self.separation() < self.range["min_sep"]:
            if i == 0:
                self.fighters[0].pos = self.fighters[1].pos - self.range["min_sep"]
            else:
                self.fighters[1].pos = self.fighters[0].pos + self.range["min_sep"]
            self.fighters[0].pos = max(0, self.fighters[0].pos)
            self.fighters[1].pos = min(self.range["axis"], self.fighters[1].pos)
            # You cannot keep walking into a body. The rest of the stride is not
            # banked for later; it is refused now.
            me.pending = 0
            flags += "m"
        return me.pos - before, flags

    def _resolve_bands(self):
        """Hysteresis is the range core's rule; applying it to both fighters
        after every movement is this loop's job."""
        sep = self.separation()
        moved = []
        for f in self.fighters:
            nb = RANGE.resolve_band(self.range, f.band, sep)
            if nb != f.band:
                moved.append((f.id, f.band, nb))
                f.band = nb
        return moved

    def _intend(self, me, tactic):
        """Turn a tactical answer into displacement owed, through the ropes.

        `step_delta` gives the signed change in SEPARATION the step intends;
        this fighter's own movement is that with the sign his side of the axis
        implies. `rope_scaled` then applies the ring - a retreat with your back
        on the ropes buys nothing - before a single reach unit is owed, so the
        fighter is never billed for a step the ropes refused. It is geometry,
        not a penalty on movement: lateral is untouched.
        """
        action = INTENT.get(tactic)
        if action is None:
            return 0
        delta = RANGE.step_delta(self.range, action)
        if delta == 0:
            return 0
        other = self.fighters[1] if me is self.fighters[0] else self.fighters[0]
        # Separation grows when the fighter on the left moves left, or the
        # fighter on the right moves right.
        own = -delta if me.pos < other.pos else delta
        own = RANGE.rope_scaled(self.range, me.pos, own, other.pos)
        me.pending += own
        return own

    def step(self):
        """One tick of the integrated bout, for every fighter, in order."""
        self.tick += 1
        t = self.tick
        left = self.state.round_ticks - (t % self.state.round_ticks)

        for i, me in enumerate(self.fighters):
            foe = self.fighters[1 - i]

            # 1. Deliver what movement is already owed, and bill the ground.
            applied, flags = self._deliver_movement(i, me)
            if applied:
                self.rows.append("X|%d|%s|%d|%d|%d|%d|%d|%s"
                                 % (t, me.id, applied, self.fighters[0].pos,
                                    self.fighters[1].pos, self.separation(),
                                    me.pending, flags or "-"))
            for who, was, now in self._resolve_bands():
                self.rows.append("R|%d|%s|%s|%s|%d"
                                 % (t, who, was, now, self.separation()))

            # 2. Decide, from what a fighter can see, on his own stream.
            me.on_ropes = self._on_ropes(me)
            me.update_recovery_intent(self.econ)
            d = P.decide(me.observation(self.econ, foe, ticks_left_in_round=left),
                         self.streams[me.id], me.profile)
            self.rows.append("D|%d|%s|%s|%s|%s|%s|%d"
                             % (t, me.id, d.strategic, d.tactical,
                                d.execution or "-", d.reason, d.initiative))

            # 3. Turn the decision into an intent the range core will price.
            me.advancing = d.tactical == P.ADVANCE
            self._intend(me, d.tactical)

            # 4. Charge. THE DISTANCE BILLED IS THE DISTANCE TRAVELLED, which is
            #    `applied` from step 1 - after the cap, the ring and the body
            #    clamp have each had their say. Intent is not charged; ground is.
            travelled = abs(applied)
            self.moved_ru += travelled
            self.charged_ru += travelled
            family = FAMILY[d.tactical]
            move_id = None
            if d.tactical == P.ATTACK:
                me.committed_to(d.execution, 14)
                move_id = d.execution
            me.tick_recovery()

            # `travel_ru` is charged in addition to whatever was committed, so
            # a step taken on the same tick as a punch is still paid for. It is
            # the economy that prices it, not this loop.
            # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
            #   2026-08-08 20:45 UTC | START edit: Decision 0029 ]
            # THE TYPED SEAM, at the exact boundary where three defects landed.
            # `displacement()` refuses a negative and refuses anything that is
            # not an integer count of reach units; the multiplication below is
            # the only declared route from a distance to a Wind debit; and the
            # row records the distance, the RATE and the debit separately,
            # because one opaque `movement_cost` field is precisely the
            # ambiguity that hid all three.
            travelled_ru = U.displacement(travelled)
            wind_debit = self.rates.movement_wind(travelled_ru)

            # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) |
            #   2026-08-08 22:15 UTC | START edit: Decision 0031 ]
            # THE TYPED VALUE IS NOW THE AUTHORITY, not a witness. The Director
            # named the previous shape precisely - "a very sophisticated
            # witness watching an untyped number run the actual fight" - and
            # this is the correction: the ReachUnits object itself is what the
            # fighter is charged from, and the only unwrap to the legacy
            # integer economy happens inside `legacy_economy_travel`, the one
            # named adapter. A raw integer can no longer reach the debit from
            # here at all.
            before_wind = me.wind
            me.step(self.econ, family, move_id=move_id, travel=travelled_ru)
            # [ ... | 2026-08-08 22:15 UTC | END edit ]

            # The typed path and the proven economy must agree about the
            # movement debit. Two roads to one number; the day they disagree is
            # the day one of them was edited alone. Checked only on the ticks
            # where movement is the ONLY charge, because that is the only tick
            # on which the two are computing the same thing.
            applied_wind = before_wind - me.wind
            if move_id is None and family == "move" \
                    and applied_wind != wind_debit.q:
                raise AssertionError(
                    "the typed movement debit (%s) and the economy's (%d) "
                    "disagree at tick %d for %s - one of the two has been "
                    "changed without the other"
                    % (wind_debit.telemetry("wind"), applied_wind, t, me.id))

            self.rows.append(
                "W|%d|%s|wind=%d|reserve=%d|%s|%s|%s"
                % (t, me.id, me.wind, me.reserve,
                   travelled_ru.telemetry("movement_displacement"),
                   self.rates.wind_per_ru.telemetry("movement_wind_rate"),
                   wind_debit.telemetry("movement_wind_debit")))
            # [ ... | 2026-08-08 20:45 UTC | END edit ]

    def run(self, ticks):
        for _ in range(ticks):
            self.step()
        return self

    # --------------------------------------------------------------- stream --

    def stream(self):
        """Header, rows, trailer. The integrated authoritative artifact.

        Decision 0022 assertion 3 - every authoritative event family in ONE
        stream - is not claimed complete by this: contact, condition, knockdown
        and judging do not exist yet, so their rows cannot be here. What IS here
        is one stream carrying every family that DOES exist, which is the only
        honest version of that assertion available today.
        """
        lines = list(self.header_lines) + list(self.rows)
        h = FNV_OFFSET
        for row in lines:
            h = fnv1a64(h, row)
        lines.append("S|ticks=%d|rows=%d|moved_ru=%d|charged_ru=%d|fnv=%016x"
                     % (self.tick, len(self.rows), self.moved_ru,
                        self.charged_ru, h))
        return "\n".join(lines) + "\n"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 14:00 UTC | END ]
