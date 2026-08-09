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
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.uppercut_range import core as RANGE          # noqa: E402
from tools.uppercut_evade import core as EVADE          # noqa: E402
from tools.uppercut_stamina import economy as E         # noqa: E402
from tools.uppercut_integrated import contract as C     # noqa: E402
from tools.uppercut_integrated import fighter as F      # noqa: E402
from tools.uppercut_integrated import policy as P       # noqa: E402
from tools.uppercut_integrated import rng as R          # noqa: E402
from tools.uppercut_integrated import resolution as RES  # noqa: E402
from tools.uppercut_integrated import judging as J       # noqa: E402
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

    def __init__(self, repo=REPO, seed=4242, rounds=12, round_ticks=180 * 60,
                 profiles=None, start_separation=None,
                 referee="nkiru_okafor", ruleset=C.DEFAULT_RULESET):
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
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) |
        #   2026-08-09 00:40 UTC | START edit: Phase R enters the bout ]
        # The evasion authority, called and not rebuilt. `punch_frames` is what
        # tells the loop WHEN a punch resolves, which is the only thing an
        # evasion window has to be compared against.
        self.evade = EVADE.evade_pack(C.REGIONS)
        if self.evade["canon_errors"]:
            raise SystemExit("the evasion canon fails its own contract: %s"
                             % "; ".join(self.evade["canon_errors"]))
        self.frames = EVADE.punch_frames(C.PUNCHES)
        self.contact = {r: 0 for r in EVADE.REASONS}
        # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09
        #   02:50 UTC | START edit: one authority on offence legality ]
        # THE SECTION-1 FIX, WIRED. `policy.BY_BAND` was a hand-authored second
        # opinion about which punches are legal from which band, and it
        # disagreed with canon seven ways: from `outside` and from `clinch`
        # EVERY punch it offered was refused by the range gate. That is what
        # produced a twelve-round fight with 3,174 punches and zero contacts.
        # There is now one derivation, canon's, and both the chooser and the
        # gate read it. `bands` carries the two facts a fighter genuinely knows
        # about range: which way is closer, and which ranges he cannot work
        # from.
        self.bands = P.Bands(RANGE.band_order(self.range),
                             RANGE.bands_without_offence(self.range, C.PUNCHES))
        # Canon's reaction rules, read at last: how often a fighter
        # reconsiders, and how old the thing he reacts to must be. The file has
        # been hashed into every integrated stream header since the contract
        # existed and nothing ever opened it.
        with io.open(os.path.join(repo, "data", "cpu_decision_model.json"),
                     encoding="utf-8") as fh:
            self.cadence = P.Cadence(json.load(fh)["reaction"])
        self.last_decision = {}
        # [ ... | 2026-08-09 02:50 UTC | END edit ]
        # [ ... | 2026-08-09 00:40 UTC | END edit ]

        # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) |
        #   2026-08-08 23:45 UTC | START edit: the chain that lets a fight end ]
        self.cond_pack = RES.condition_pack()
        if self.cond_pack["errors"]:
            raise SystemExit("the condition canon fails its own contract: %s"
                             % "; ".join(self.cond_pack["errors"]))
        self.referee = RES.referee_pack(referee)
        # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09
        #   10:30 UTC | START edit: Decision 0033 Ruling 2 - the contest has
        #   rules and they are the ruleset's ]
        # Thirty of thirty measured fights ended on a knockdown limit read
        # from condition_model while the authored rulesets - which switch that
        # limit OFF under professional rules - were read by nothing. The
        # contest rules now come from the ruleset exclusively; null means "no
        # stoppage by that mechanism"; and the panel scores under the
        # ruleset's own scoring block rather than a restated default.
        self.rules = RES.ruleset_pack(ruleset,
                                      count_to=self.cond_pack["count_to"])
        # [ ... | 2026-08-09 10:30 UTC | END edit ]
        self.whiff_band = 0
        # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08
        #   23:35 UTC | edit: the punch ledger closes ] A punch can now leave
        #   the world three ways: resolved (contact reasons), whiffed on range
        #   legality (whiff_band), or VOIDED - cleared in flight because a
        #   knockdown stopped the ring or the bell ended the round. The first
        #   loop's lesson (214 thrown, 117 resolved, the rest vanished) is a
        #   ledger rule now: thrown == resolved + whiffed + voided + in-flight,
        #   and tests hold the bout to it.
        self.voided = 0
        self.count = None            # active knockdown count, or None
        self.result = None           # set once, ends the fight
        self._round_end_due = False
        self.round_no = 1
        self.rounds_planned = rounds
        # [ ... | 2026-08-08 23:45 UTC | END edit ]

        self.state, self.rng, self.header_lines = C.new_bout(
            repo, seed, rounds, round_ticks, ruleset=ruleset)

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
        # Per-fighter fight bookkeeping. On the bout rather than the fighter,
        # because it is officiating and judging evidence, not fighter state.
        self.condition = {f.id: RES.RegionalCondition(self.cond_pack)
                          for f in self.fighters}
        # The panel scores under the ruleset actually fought (Decision 0033
        # Ruling 2); `thrown` joins the evidence per Ruling 5, so effective
        # aggression can one day be accuracy rather than ground covered.
        self.panel = J.JudgingPanel([f.id for f in self.fighters],
                                    scoring=self.rules["scoring"])
        self.evidence = {f.id: {"landed": 0, "denied": 0, "pressed": 0,
                                "thrown": 0}
                         for f in self.fighters}
        self.kd_round = {f.id: 0 for f in self.fighters}
        self.kd_bout = {f.id: 0 for f in self.fighters}
        self.unanswered = {f.id: 0 for f in self.fighters}
        self.samples = []
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

    # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:50 UTC | START edit: Decision 0032 - evasion is a commitment ]
    # THE LIFECYCLE THE RULING FIXES:
    #
    #     commit -> startup -> active window -> resolve -> recovery
    #                                                       or mistime
    #
    # A fighter's `evasion` is (id, open_at, close_at, used). During startup
    # the lane is NOT yet vacated - a punch arriving then finds him. The
    # window opens exactly `startup` ticks after commitment, stays open
    # exactly `active` ticks, and if it closes UNUSED the authored mistime
    # penalty extends the recovery: a bad read still occupies the body and
    # the clock. No dodge percentage anywhere in this chain.

    def _commit_evasion(self, me, t, evasion_id):
        spec = self.evade["evasions"].get(evasion_id)
        if spec is None or spec["kind"] != "active_window":
            # A positional action is not a lane-vacating dodge.
            return False
        if me.evasion is not None or me.recovery_ticks > 0:
            return False
        open_at = t + spec["startup"]
        me.evasion = (evasion_id, open_at, open_at + spec["active"], False)
        # The whole commitment occupies the fighter: startup, window, recovery.
        me.recovery_ticks = spec["startup"] + spec["active"] + spec["recovery"]
        return True

    def _evasion_active(self, f, t):
        return (f.evasion is not None
                and f.evasion[1] <= t < f.evasion[2])

    def _tick_evasions(self, t):
        for f in self.fighters:
            if f.evasion is None:
                continue
            ev, open_at, close_at, used = f.evasion
            if t == open_at:
                self.rows.append("W|%d|%s|%s|open|until=%d"
                                 % (t, f.id, ev, close_at))
            if t >= close_at:
                if used:
                    self.rows.append("W|%d|%s|%s|close" % (t, f.id, ev))
                else:
                    # The mistimed evade: the window came and went and nothing
                    # was thrown into it. The read was wrong, and the price is
                    # canon's authored penalty on top of the authored recovery.
                    penalty = self.evade["mistime_ticks"]
                    f.recovery_ticks += penalty
                    self.rows.append("W|%d|%s|%s|mistimed|penalty=%d"
                                     % (t, f.id, ev, penalty))
                f.evasion = None

    def _resolve_punches(self, t):
        """Every punch whose active window ends this tick.

        ORDER, PER THE RULING: range legality first (Rule 12 - a punch thrown
        from a band it is not authored for whiffs whatever the defender did),
        then evasion against whatever window was genuinely open at this
        instant, then - when they exist - guard and contact. `outranks_guard`
        means a dodged punch never reaches the later stages.
        """
        for i, me in enumerate(self.fighters):
            if not me.punch:
                continue
            move, t0, band = me.punch
            span = self.frames[move]["startup"] + self.frames[move]["active"]
            if t - t0 < span:
                continue
            me.punch = None
            foe = self.fighters[1 - i]

            if not RANGE.in_band(self.range, move, band):
                self.whiff_band += 1
                me.failed_attacks += 1
                self.rows.append("P|%d|%s|%s|%s|band=%s|evasion=-|whiffed|band"
                                 % (t, me.id, foe.id, move, band))
                continue

            active = foe.evasion[0] if self._evasion_active(foe, t) else None
            arrived, reason, region = EVADE.resolve(
                self.evade, C.PUNCHES, move, active)
            self.contact[reason] += 1
            if active is not None:
                # The window was USED: something was thrown into it, whatever
                # the outcome. Used windows close quietly; unused ones mistime.
                foe.evasion = (foe.evasion[0], foe.evasion[1],
                               foe.evasion[2], True)
            self.rows.append(
                "P|%d|%s|%s|%s|region=%s|evasion=%s|%s|%s"
                % (t, me.id, foe.id, move, region, active or "-",
                   "arrived" if arrived else "dodged", reason))
            if arrived:
                self._contact(t, me, foe, move, region)
            else:
                me.failed_attacks += 1
                self.evidence[foe.id]["denied"] += 1
    # [ ... | 2026-08-08 23:50 UTC | END edit ]

    # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-08 23:55 UTC | START edit: contact, condition, knockdown, count, stoppage ]
    def _contact(self, t, me, foe, move, region):
        """An arrived punch becomes a solid contact and the fight can change.

        Contact quality is "solid" - Phase N's named simplification, restated
        in `resolution.py` - and delivered force is authored effort. Condition
        accumulates; the knockdown pressure is deterministic; the count and
        the limits are canon's.
        """
        self.evidence[me.id]["landed"] += 1
        self.unanswered[me.id] = 0
        force = self.cond_pack["efforts"][move]
        cond = self.condition[foe.id]
        cond.absorb(region, force)
        self.rows.append("C|%d|%s|%s|%s|%s|solid|dmg=%d"
                         % (t, me.id, foe.id, move, region,
                            cond.fraction(region)))

        # Referee bookkeeping: a fighter who has been down is being watched.
        if self.kd_bout[foe.id] > 0:
            self.unanswered[foe.id] += 1
            stop = self.referee["unanswered_stop"]
            if stop is not None and self.unanswered[foe.id] >= stop:
                self._stop(t, foe, "referee_judgement")
                return

        # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09
        #   10:32 UTC | edit: Section 3's Flag 1, Decision 0033 Ruling 1 ]
        # Eligibility reads EVERY region canon authors this punch to target,
        # not the single region the damage was placed in. The hook is authored
        # ["head", "jaw_chin"]: it targets the jaw, and until this line it was
        # being refused the jaw's consequence by an array subscript.
        if not RES.knockdown_capable(self.cond_pack, move):
            return
        wind_frac = (foe.wind * 10000) // self.econ["wind_max"]
        pressure = RES.knockdown_pressure(
            self.cond_pack, move, cond, wind_frac,
            defender_committed=foe.punch is not None or foe.recovery_ticks > 0,
            defender_evading=self._evasion_active(foe, t))
        if pressure >= self.cond_pack["pressure_threshold"]:
            self._knockdown(t, me, foe, move)

    def _knockdown(self, t, me, foe, move):
        self.kd_round[foe.id] += 1
        self.kd_bout[foe.id] += 1
        self.rows.append("N|%d|%s|down|by=%s|%s|round_kd=%d|bout_kd=%d"
                         % (t, foe.id, me.id, move,
                            self.kd_round[foe.id], self.kd_bout[foe.id]))
        # The ring stops: in-flight punches and windows are void, both corners
        # are neutral, and the count clock - identical for every referee - runs.
        for f in self.fighters:
            if f.punch is not None:
                self.voided += 1
            f.punch = None
            f.evasion = None
        # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-09
        #   10:32 UTC | edit: Decision 0033 Ruling 2 ] The limits are the
        # RULESET'S, null means no stoppage by that mechanism, and where a
        # limit applies the fight ends ON the Nth knockdown (>=, tested after
        # the increment) - the old `>` stopped on the fourth of a
        # three-knockdown round, and a four-knockdown round is a thing a
        # referee does not permit. Under professional rules both limits are
        # null, so a professional bout ends by count, referee, or the cards.
        per_round, per_bout = self.rules["per_round"], self.rules["per_bout"]
        if ((per_round is not None and self.kd_round[foe.id] >= per_round)
                or (per_bout is not None and self.kd_bout[foe.id] >= per_bout)):
            self._stop(t, foe, "knockdown_limit")
            return
        self.count = {"who": foe.id, "start": t, "n": 0}

    def _tick_count(self, t):
        c = self.count
        elapsed = t - c["start"]
        n = elapsed // self.cond_pack["count_ticks_per_number"]
        if n > c["n"]:
            c["n"] = n
            self.rows.append("K|%d|%s|count=%d" % (t, c["who"], n))
            foe = next(f for f in self.fighters if f.id == c["who"])
            if n >= self.cond_pack["count_to"]:
                self._stop(t, foe, "count_expired")
                return
            # Section 3's Flag 3: the eight is READ (rise_window_ticks over
            # the count clock), not written. Same number, no invented literal.
            if (n == self.cond_pack["mandatory_count_number"]
                    and self.cond_pack["mandatory_eight"]):
                # THE RISE RULE, structural and declared: a fighter beaten to
                # the floor of a knockdown-relevant region, or with no breath
                # at all, has nothing to rise WITH. Everyone else gets up at
                # the mandatory eight, having bought exactly what canon says
                # the count buys - partial clarity, never freshness.
                cond = self.condition[c["who"]]
                if (cond.worst_knockdown_fraction() >= 10000
                        or foe.wind <= 0):
                    return          # he stays down; the count runs to ten
                cond.count_relief()
                ceiling = E.wind_ceiling(self.econ, foe.reserve)
                relief = ((ceiling - foe.wind)
                          * self.cond_pack["count_stamina_relief"]) // 10000
                foe.wind = min(ceiling, foe.wind + relief)
                foe.recovery_ticks = 0
                self.rows.append("U|%d|%s|rises|at=%d" % (t, c["who"], n))
                self.count = None

    def _stop(self, t, loser, detail):
        winner = next(f for f in self.fighters if f.id != loser.id)
        method = "KO" if detail == "count_expired" else "TKO"
        self.count = None
        self.panel.close()
        self.result = {"method": method, "winner": winner.id,
                       "round": self.round_no, "tick": t, "detail": detail}
        self.rows.append("F|%d|%s|%s|winner=%s|round=%d"
                         % (t, method, detail, winner.id, self.round_no))

    def _end_round(self, t):
        self.panel.score_round(self.round_no, self.evidence, self.kd_round)
        self.rows.append("B|%d|round_end|%d" % (t, self.round_no))
        if self.round_no >= self.rounds_planned:
            self.panel.close()
            v = self.panel.verdict()
            self.result = {"method": v["method"], "winner": v["winner"],
                           "round": self.round_no, "tick": t,
                           "detail": "decision"}
            self.rows.append("F|%d|%s|decision|winner=%s|round=%d"
                             % (t, v["method"], v["winner"] or "-",
                                self.round_no))
            return
        # The corner. Wind substantially, Reserve barely, damage at canon's
        # per-region rates - and the unanswered ledger resets, because the
        # corner is an answer.
        for f in self.fighters:
            f.between_rounds(self.econ)
            self.condition[f.id].between_rounds()
            if f.punch is not None:
                self.voided += 1
            f.punch = None
            f.evasion = None
            f.recovery_ticks = 0
            self.unanswered[f.id] = 0
        self.evidence = {f.id: {"landed": 0, "denied": 0, "pressed": 0,
                                "thrown": 0}
                         for f in self.fighters}
        self.kd_round = {f.id: 0 for f in self.fighters}
        self.round_no += 1
        self.rows.append("B|%d|round_start|%d" % (t, self.round_no))
    # [ ... | 2026-08-08 23:55 UTC | END edit ]

    def step(self):
        """One tick of the integrated bout, in the order the ruling fixes."""
        if self.result:
            return
        self.tick += 1
        t = self.tick
        left = self.state.round_ticks - (t % self.state.round_ticks)

        if t % 60 == 0:
            self.samples.append({
                "t": t, "r": self.round_no,
                "pos": [f.pos for f in self.fighters],
                "wind": [(f.wind * 10000) // self.econ["wind_max"]
                         for f in self.fighters],
                "reserve": [(f.reserve * 10000) // self.econ["reserve_max"]
                            for f in self.fighters],
                "dmg": [self.condition[f.id].worst_knockdown_fraction()
                        for f in self.fighters]})

        # The bell and the count. The first full fight found the defect here:
        # a count straddled tick 10800, the round-boundary check lived at the
        # bottom of step() where a running count returns early, so the bell
        # never rang and "round 1" ran for 19,356 ticks with the cards empty.
        # The rule, which is boxing's own: NOBODY IS SAVED BY THE BELL - a
        # count that is running when the round expires completes first - but
        # the moment it resolves with the fighter up, the deferred bell rings.
        if t % self.state.round_ticks == 0:
            self._round_end_due = True

        if self.count is not None:
            self._tick_count(t)
            if self.result:
                return
            if self.count is not None:
                return              # the ring is stopped; only the count runs

        if self._round_end_due:
            self._round_end_due = False
            self._end_round(t)
            if self.result:
                return
            return                  # the round break consumed this tick

        # 0. Windows tick before anything resolves against them, and punches
        #    resolve before anyone decides again.
        self._tick_evasions(t)
        self._resolve_punches(t)
        if self.result:
            return

        for i, me in enumerate(self.fighters):
            foe = self.fighters[1 - i]

            # 1. Deliver what movement is already owed, and bill the ground.
            applied, flags = self._deliver_movement(i, me)
            if applied:
                self.rows.append("X|%d|%s|%d|%d|%d|%d|%d|%s"
                                 % (t, me.id, applied, self.fighters[0].pos,
                                    self.fighters[1].pos, self.separation(),
                                    me.pending, flags or "-"))
                if me.advancing:
                    self.evidence[me.id]["pressed"] += abs(applied)
            for who, was, now in self._resolve_bands():
                self.rows.append("R|%d|%s|%s|%s|%d"
                                 % (t, who, was, now, self.separation()))

            # 2. Decide, from what a fighter can see, on his own stream.
            me.on_ropes = self._on_ropes(me)
            me.update_recovery_intent(self.econ)
            # A punch already in the air is observable - the telegraph.
            # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09
            #   02:55 UTC | START edit: legality and cadence reach the decision ]
            # What he may throw FROM WHERE HE IS STANDING, derived from canon
            # by the one authority. Not a table, not a copy, not a default.
            throwable = RANGE.throwable_from(self.range, me.band, C.PUNCHES)
            obs = me.observation(self.econ, foe,
                                 round_number=self.round_no,
                                 ticks_left_in_round=left,
                                 incoming_attack=foe.punch is not None,
                                 throwable_here=throwable,
                                 bands=self.bands)
            d = P.decide(obs, self.streams[me.id], me.profile)
            # [ ... | 2026-08-09 02:55 UTC | END edit ]
            self.rows.append("D|%d|%s|%s|%s|%s|%s|%d"
                             % (t, me.id, d.strategic, d.tactical,
                                d.execution or "-", d.reason, d.initiative))

            # 3. Turn the decision into an intent the range core will price.
            me.advancing = d.tactical == P.ADVANCE
            self._intend(me, d.tactical)

            # 4. Commit. A punch goes in the air; an evasion starts its
            #    startup. Both are charged their authored economy cost, and
            #    both occupy the fighter for their authored spans.
            travelled = abs(applied)
            self.moved_ru += travelled
            self.charged_ru += travelled
            family = FAMILY[d.tactical]
            move_id = None
            if d.tactical == P.ATTACK:
                # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) |
                #   2026-08-09 10:35 UTC | edit: the magic 14 dies ] The
                # policy can no longer select a punch outside the declared
                # vocabulary (it chooses from the range authority's answer
                # over C.PUNCHES), so the `else 14` invented-window branch is
                # unreachable - and an unreachable fail-open branch in a
                # fail-closed codebase is kept as a RAISE, not a default.
                if d.execution not in self.frames:
                    raise AssertionError(
                        "the policy chose %r, which the bout cannot fly - the "
                        "vocabularies have diverged again" % (d.execution,))
                me.committed_to(d.execution,
                                self.frames[d.execution]["frames"])
                move_id = d.execution
                self.evidence[me.id]["thrown"] += 1
                me.punch = (d.execution, t, me.band)
            elif d.tactical == P.EVADE and d.execution:
                if self._commit_evasion(me, t, d.execution):
                    # Evade spam is not free: the authored per-action cost is
                    # charged through the same economy as every punch.
                    move_id = d.execution
            me.tick_recovery()

            travelled_ru = U.displacement(travelled)
            wind_debit = self.rates.movement_wind(travelled_ru)

            before_wind = me.wind
            me.step(self.econ, family, move_id=move_id, travel=travelled_ru)

            applied_wind = before_wind - me.wind
            if move_id is None and family == "move" \
                    and applied_wind != wind_debit.q:
                raise AssertionError(
                    "the typed movement debit (%s) and the economy's (%d) "
                    "disagree at tick %d for %s"
                    % (wind_debit.telemetry("wind"), applied_wind, t, me.id))

            self.rows.append(
                "E|%d|%s|wind=%d|reserve=%d|%s|%s|%s"
                % (t, me.id, me.wind, me.reserve,
                   travelled_ru.telemetry("movement_displacement"),
                   self.rates.wind_per_ru.telemetry("movement_wind_rate"),
                   wind_debit.telemetry("movement_wind_debit")))

    def run(self, ticks):
        for _ in range(ticks):
            if self.result:
                break
            self.step()
        return self

    def run_fight(self):
        """First bell to the end, however it ends."""
        while not self.result:
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
        lines.append("S|ticks=%d|rows=%d|moved_ru=%d|charged_ru=%d|%s"
                     "|whiff_band=%d|voided=%d|fnv=%016x"
                     % (self.tick, len(self.rows), self.moved_ru,
                        self.charged_ru,
                        "|".join("%s=%d" % (r, self.contact[r])
                                 for r in EVADE.REASONS),
                        self.whiff_band, self.voided, h))
        return "\n".join(lines) + "\n"
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-08 14:00 UTC | END ]
