# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:33 UTC | START ]
"""Deterministic reference simulation of a CPU-vs-CPU bout.

Executes the canonical models: the collision pipeline's stage order, the punch
model's commitment and outcome recovery, the condition model's stamina and
knockdown rules, the guard model's posture extents, and the crowd model's
novelty and risk gating. Emits fight_event records.

Determinism: one seeded stream, fighters resolved in fixed index order, no
wall-clock read anywhere. Same seed and same canon reproduce the same log.

The score firewall is enforced by construction: policies receive an Observation
built only from observable state, and the round cards live in a private
structure the Observation has no path to.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field

from . import canon

TICKS_PER_SECOND = 60


@dataclass
class Fighter:
    name: str
    profile: str
    stamina: float
    crowd: float = 0.0
    knockdowns: int = 0
    condition: dict = field(default_factory=dict)
    committed: int = 0
    posture: str = "high_guard"
    last_move: str = ""
    repeats: int = 0
    landed: int = 0
    thrown: int = 0
    # Range and clinch state, so running and clinch abuse are testable rather
    # than assumed. Distance is shared but each fighter records its own intent.
    retreats: int = 0
    clinch_entries: int = 0
    out_of_range_attempts: int = 0
    blocked_taken: int = 0
    # Per-round accumulators, reset at each bell. Cards score the round in front
    # of the judges, not the bout to date - see _score_round.
    round_force: float = 0.0
    round_knockdowns_suffered: int = 0
    effective_force: float = 0.0
    # The repetition economy (punch_model.repetition_economy), which was declared
    # in canon and executed nowhere until 2026-08-03. arm_work is per hand;
    # reads is what THIS fighter has learned about the other one's patterns.
    arm_work: dict = field(default_factory=lambda: {"lead": 0.0, "rear": 0.0})
    reads: dict = field(default_factory=dict)
    threw_without_stepping: int = 0
    # Crowd bookkeeping the crowd model has declared all along: gains decay by
    # sameness whoever earns them (blocking the fortieth jab thrills nobody),
    # and the bar drains after a grace window so it cannot be banked and coasted
    # on (crowd_model.bar.decay_per_tick_idle - declared, and inert until
    # 2026-08-03).
    last_gain_source: str = ""
    gain_repeats: int = 0
    last_gain_tick: int = 0
    # Chaining (punch_model.chaining), declared at step 6 and inert until
    # 2026-08-03: a link is a punch that starts inside the previous punch's late
    # recovery. Combinations exist because recovery overlaps the next windup,
    # which is also why 'combinations' is a crowd source nobody could earn.
    # The fighter's card. Empty means every attribute is zero, which multiplies every
    # effect by exactly one - so a fighter with no card fights the baseline model and
    # any difference between two fighters is attributable to their cards (Rule 10).
    attrs: dict = field(default_factory=dict)
    last_hand: str = ""
    last_move_category: str = ""
    link_open_until: int = 0
    combo_length: int = 0
    # Rule 19 evidence: an input degraded by exhaustion is still an input. This
    # counts throws made below the low-stamina threshold, so a check can prove
    # the gate degrades rather than blocks.
    degraded_throws: int = 0

    def alive(self) -> bool:
        return self.knockdowns < canon.condition()["knockdown"]["max_per_bout"]


class Bout:
    """One CPU-vs-CPU bout. Nothing here reads a scorecard."""

    def __init__(self, seed: int, profile_a: str, profile_b: str,
                 rounds: int = 3, round_seconds: int = 180):
        self.seed = seed
        self.rng = random.Random(seed)
        self.rounds = rounds
        self.round_ticks = round_seconds * TICKS_PER_SECOND
        cm = canon.condition()
        self.fighters = [
            Fighter(name="A", profile=profile_a, stamina=cm["stamina"]["max"]),
            Fighter(name="B", profile=profile_b, stamina=cm["stamina"]["max"]),
        ]
        from . import policy as _policy      # local: policy imports canon, not engine
        for f in self.fighters:
            f.condition = {d["region"]: 0.0 for d in cm["damage_regions"]}
            f.attrs = dict(_policy.attributes_for(f.profile))
            # The tank is attribute-scaled, so a fighter starts full of THEIR
            # pool rather than of the canon baseline (stamina.start_fraction).
            f.stamina = self._stamina_max(f) * cm["stamina"]["start_fraction"]
        self.log: list = []
        self.seq = 0
        self.tick = 0
        self.round = 0
        # Shared separation in reach units, resolved into a canonical band with
        # hysteresis - the same rule proved byte-reproducible in-engine (Phase D).
        mvd = canon.movement()
        mv = mvd["range_bands"]
        self._bands = mv["bands"]
        self._hyst = float(mv["hysteresis_ru"])
        # The ring, as a bound rather than as scenery. Two positions on a track of
        # ring-side length; separation is their difference. This is what makes
        # excessive running finite (data/movement_model.json ring.track).
        self._track = mvd["ring"]["track"]
        self._dirmul = mvd["locomotion"]["directional"]
        self._axis = float(self._track["axis_length_ru"])
        self._ropes = float(self._track["back_to_ropes_ru"])
        self._min_sep = float(mvd["separation"]["min_center_distance_ru"])
        self._count_ticks = cm["knockdown"]["count_ticks_per_number"]
        mid = self._axis / 2.0
        self.pos = [mid - 0.45, mid + 0.45]
        self.distance = self.pos[1] - self.pos[0]
        self.band = 2
        self.at_ropes = [False, False]
        self.clinched = False
        self.clinch_ticks = 0
        # Sealed. The Observation has no reference to this object (Rule 3).
        self._cards: dict = {f.name: 0.0 for f in self.fighters}
        self.stopped = False
        self.stop_reason = ""

    # ---- event emission -------------------------------------------------
    def emit(self, etype: str, actor: str = "", target: str = "",
             payload: dict | None = None, explains: list | None = None,
             visibility: str = "observable") -> int:
        ev = {
            "seq": self.seq,
            "tick": self.tick,
            "clock": {"round": self.round,
                      "display_ms": int(self.tick * 1000 / TICKS_PER_SECOND),
                      "real_ms": int(self.tick * 1000 / TICKS_PER_SECOND)},
            "type": etype,
            "visibility": visibility,
        }
        if actor:
            ev["actor"] = actor
        if target:
            ev["target"] = target
        if payload:
            ev["payload"] = payload
        if explains:
            ev["explains"] = explains
        self.log.append(ev)
        self.seq += 1
        return ev["seq"]

    # ---- observation (the firewall) -------------------------------------
    def observe(self, me: Fighter, opp: Fighter) -> dict:
        """Everything a fighter may see. Deliberately excludes opponent internals
        and has no path to self._cards."""
        cm = canon.condition()
        return {
            "own_stamina_fraction": me.stamina / self._stamina_max(me),
            "own_crowd_fraction": me.crowd / canon.crowd()["bar"]["max"],
            "own_knockdowns": me.knockdowns,
            "opponent_knockdowns": opp.knockdowns,
            "opponent_visible_posture": opp.posture,
            "opponent_recent_thrown": opp.thrown,
            "my_last_move": me.last_move,
            "my_repeats": me.repeats,
            "band": self.band,
            "band_key": self._bands[self.band]["key"],
            # Ringcraft. Both flags are things a fighter can plainly see - where
            # the ropes are, and whether the other one has run out of ring. They
            # carry no score information, so Rule 3 is untouched.
            "own_back_to_ropes": self.at_ropes[self.fighters.index(me)],
            "opponent_back_to_ropes": self.at_ropes[self.fighters.index(opp)],
            # A fighter mid-punch, mid-step or mid-count is VISIBLY so - this is
            # the distillation of observable punch_thrown/step/knockdown events
            # plus authored frame data, not a read of hidden state. It is the
            # entire trade of the counterpuncher, whose canon win condition is
            # "exploiting blocked, dodged and whiffed recovery windows".
            "opponent_committed_ticks": opp.committed,
            "clinched": self.clinched,
            "round": self.round,
            "total_rounds": self.rounds,
            "tick_in_round": self.tick % self.round_ticks,
        }

    # ---- range, movement and clinch -------------------------------------
    def _resolve_band(self) -> None:
        """Hysteresis: leaving the current band costs the extra Hyst either way.
        Identical rule to the one BP_RangeWalker executes in the engine."""
        b = self._bands[self.band]
        lo = float(b["min_ru"]) - self._hyst
        hi = (99.0 if b.get("max_ru") is None else float(b["max_ru"])) + self._hyst
        prev = self.band
        if self.distance < lo:
            self.band = max(0, self.band - 1)
        elif self.distance > hi:
            self.band = min(len(self._bands) - 1, self.band + 1)
        if self.band != prev:
            self.emit("range_change", "", "",
                      {"from": self._bands[prev]["key"], "to": self._bands[self.band]["key"],
                       "distance_ru": round(self.distance, 4)})

    def step(self, f: Fighter, direction: str) -> None:
        """Footwork on the ring track (data/movement_model.json ring.track).

        Retreating is legal, damage-free and never blocked. What it is not is
        free: it covers less ground than an advance, it costs more of it when the
        legs are gone, and it ends at the ropes. That is the whole answer to
        Rule 4's 'excessive running' - the runner loses ground more slowly than
        it is taken and eventually has none left to give, without the simulation
        ever refusing the input.

        The earlier version moved a scalar separation by a fixed +/-0.09 with no
        ring at all, which let a retreating fighter open distance against a
        pressure fighter forever at exactly matched rates. That was found by the
        abuse-list check, not reasoned about in advance.
        """
        moves = canon.moves()
        mid = {"in": "step_in", "out": "step_out", "lateral": "step_lateral"}[direction]
        m = moves[mid]
        f.stamina = max(0.0, f.stamina - m["stamina_cost"])
        f.committed = m["recovery_frames"]

        i = self.fighters.index(f)
        toward = 1 if i == 0 else -1          # +x is B's side of the track
        # The authored stride for the boxing-steps mode, rather than a constant
        # the engine invented beside it (movement_model.locomotion.modes).
        base = next(m["stride_length_ru"] for m in canon.movement()["locomotion"]["modes"]
                    if m["posture_mode"] == "boxing_steps")
        mul = {"in": self._dirmul["advance_stride_multiplier"],
               "out": self._dirmul["retreat_stride_multiplier"],
               "lateral": self._dirmul["lateral_stride_multiplier"]}[direction]
        # A guard is a body structure, and a tight one does not move as freely
        # (posture mobility_multiplier, declared at step 7 and inert until now).
        mul *= self._posture(f)["mobility_multiplier"] * self._attr(f, "stride_length")
        cm = canon.condition()
        if f.stamina / self._stamina_max(f) < cm["stamina"]["exhausted_threshold_fraction"]:
            mul *= self._dirmul["exhausted_stride_multiplier"]

        payload = {"direction": direction}
        on_ropes = min(self.pos[i], self._axis - self.pos[i]) <= self._ropes
        if direction == "lateral":
            # Circling costs the step and changes the angle, not the separation.
            # On the ropes it is the one thing still fully available - and the
            # multiplier that says so is read rather than assumed, because a
            # constant of 1.0 written in the engine is not the same promise as
            # a 1.0 the data can be inspected for.
            if on_ropes:
                mul *= self._track["rope_lateral_multiplier"]
            payload["lateral"] = True
        else:
            sign = toward if direction == "in" else -toward
            # The ropes: a backward step into them buys what the track says it
            # buys, which is nothing. Authored as rope_retreat_multiplier and
            # previously enforced by a positional clamp that happened to agree
            # with it - the same behaviour, but unfalsifiable, and it would not
            # have changed if the number had.
            if on_ropes and direction == "out":
                mul *= self._track["rope_retreat_multiplier"]
                payload["rope_blocked"] = True
            want = base * mul * sign
            new = min(max(self.pos[i] + want, 0.0), self._axis)
            self.pos[i] = new
            # Bodies do not overlap (movement_model separation.min_center_distance_ru).
            if self.pos[1] - self.pos[0] < self._min_sep:
                if i == 0:
                    self.pos[0] = self.pos[1] - self._min_sep
                else:
                    self.pos[1] = self.pos[0] + self._min_sep
                self.pos[0] = max(0.0, self.pos[0])
                self.pos[1] = min(self._axis, self.pos[1])
        if direction == "out":
            f.retreats += 1
        # The feet reset, which is what position_cost is measured against.
        f.threw_without_stepping = 0

        self.distance = self.pos[1] - self.pos[0]
        payload["distance_ru"] = round(self.distance, 4)
        payload["ring_position_ru"] = round(self.pos[i], 4)
        self.emit("step", f.name, "", payload)
        self._check_ropes()
        self._resolve_band()

    def _check_ropes(self) -> None:
        """Ringcraft observables. Emitted on entry only - a fighter pinned on the
        ropes for ten seconds is one event and a lasting state, not a hundred
        events."""
        for i, f in enumerate(self.fighters):
            edge = min(self.pos[i], self._axis - self.pos[i])
            now = edge <= self._ropes
            if now and not self.at_ropes[i]:
                self.emit("ropes_reached", f.name, "", {"edge_ru": round(edge, 4)})
                if edge <= float(self._track["cornered_ru"]) * 0.5:
                    self.emit("cornered", f.name, "", {"edge_ru": round(edge, 4)})
            self.at_ropes[i] = now

    def clinch(self, f: Fighter, opp: Fighter) -> None:
        """Clinch halts the exchange. Repeated use is referee-dependent and counts
        toward clinch-abuse recognition - the move table already says so."""
        m = canon.moves()["clinch_entry"]
        f.stamina = max(0.0, f.stamina - m["stamina_cost"])
        f.committed = m["recovery_frames"]
        f.clinch_entries += 1
        if self.band > 0:
            self.emit("clinch_start", f.name, opp.name, {"refused": True,
                                                         "reason": "out_of_clinch_range"})
            f.out_of_range_attempts += 1
            return
        self.clinched = True
        self.clinch_ticks = 90
        cs = self.emit("clinch_start", f.name, opp.name, {"entries": f.clinch_entries})
        if f.clinch_entries >= 6:
            self.emit("referee_warning", "referee", f.name,
                      {"reason": "clinch_abuse", "entries": f.clinch_entries}, [cs])

    # ---- the canonical collision pipeline -------------------------------
    def resolve(self, atk: Fighter, dfn: Fighter, move: dict, decision_seq: int,
                amp: dict | None = None) -> str:
        """Stage order exactly as data/collision_model.json declares it. `amp`
        carries the instrument Ultimate's multipliers; everything else about an
        Ultimate is an ordinary punch in this pipeline, which is precisely what
        makes it legal (ability_model.reference_instruments)."""
        col = canon.collision()
        ge = canon.guard_evasion()
        qthr = canon.quality_thresholds()
        postures = {p["id"]: p for p in ge["postures"]}

        r_sweep = self.rng.random()
        r_evade = self.rng.random()
        r_guard = self.rng.random()
        align = self.rng.random()
        # Accuracy nudges the grade of contact, never whether contact happens -
        # the band is narrow for exactly that reason (attribute_effects).
        align = min(1.0, align * self._attr(atk, "alignment"))
        # Exhaustion lands worse (punch_model.stamina_gate): the alignment
        # penalty is subtracted here, before the quality bands read it, so a
        # tired fighter's punches grade lower without any of them being refused.
        _, align_penalty, degraded = self._fatigue_degradation(atk)
        align = max(0.0, align - align_penalty)
        if degraded:
            atk.degraded_throws += 1

        # Rule 12 range gate, ahead of the pipeline: a punch thrown from the wrong
        # band travels its full arc into empty air. No magnetic correction, and no
        # invisible lunge closes the distance for it (data/punch_model.json).
        band_keys = [b["key"] for b in self._bands]
        if move["range_band"] != band_keys[self.band]:
            atk.out_of_range_attempts += 1
            return self._apply(atk, dfn, move, "whiffed", align, decision_seq, amp=amp)

        # Stage 0, inverted: no overlap terminates at whiffed.
        if r_sweep < 0.15:
            return self._apply(atk, dfn, move, "whiffed", align, decision_seq, amp=amp)
        # The read (repetition_economy.opponent_read): the defender's evasion and
        # guard arrive earlier against a pattern they have now seen more than
        # once. This belongs to the DEFENDER's observation - it is stored on the
        # defender, it needs sightings to exist, and it decays the moment the
        # pattern stops. Nothing here counts the thrower's repeats.
        read = self._read_gain(dfn, move["id"])
        # The telegraph (guard_evasion_model.telegraph): the loading tell the
        # move table has described in prose since step 6, made mechanical. A
        # punch is dodgeable in proportion to how long it spends being visibly
        # on its way - the defender is not buffed, the slow punch is seen.
        tg = ge["telegraph"]
        tele = min(tg["max_multiplier"],
                   1.0 + max(0, move["startup_frames"] - tg["reference_startup_frames"])
                   * tg["evasion_gain_per_startup_frame"])
        # A committed defender defends worse (guard_evasion_model.
        # committed_defense): mid-punch you cannot slip and cannot fully cover.
        # This is what makes counter_window_ticks a window rather than a number,
        # and overcommitment the liability the rusher's canon names.
        cd = ge["committed_defense"]
        ev_commit = cd["evasion_multiplier_while_committed"] if dfn.committed > 0 else 1.0
        gd_commit = cd["guard_extent_multiplier_while_committed"] if dfn.committed > 0 else 1.0
        # Stage 1: active evasion, ranked above guard on purpose.
        evade_chance = (0.10 + 0.10 * postures[dfn.posture]["counter_readiness"]) \
            * (1.0 + read) * tele * ev_commit * self._attr(dfn, "evasion_chance")
        if r_evade < evade_chance:
            return self._apply(atk, dfn, move, "dodged", align, decision_seq, amp=amp)
        # Stage 2: guard interception - which volume is permitted, and does its
        # coverage extent actually reach (Decision 0010). The reach is impaired
        # by accumulated arm condition: damage_regions declare that arms impair
        # guard_integrity, and a guard that has absorbed force all night rises
        # slower and covers less (condition_model.impairment).
        gi = col["guard_interception"]
        volumes = gi.get(move["guard_interaction"], [])
        extent = max((postures[dfn.posture]["extents"].get(v, 0.0) for v in volumes),
                     default=0.0)
        # Guard structure multiplies the posture's own extent - it cannot create
        # coverage the posture does not have, so a shell still sells the body.
        extent *= self._guard_integrity(dfn) * gd_commit \
            * self._attr(dfn, "guard_coverage_extent")
        if r_guard < extent * 0.55 * (1.0 + read):
            return self._apply(atk, dfn, move, "blocked", align, decision_seq, amp=amp)
        # Stage 3: quality dispatch.
        qc = sum(1 for t in qthr if align >= t)
        cls = ["brushed", "grazed", "solid", "clean"][qc]
        # The extent travels with the outcome: interception failing is not the
        # same as the lane being open, and the knockdown model reads which.
        return self._apply(atk, dfn, move, cls, align, decision_seq, extent, amp=amp)

    def _guard_integrity(self, f: Fighter) -> float:
        """Arms impair guard_integrity (condition_model.impairment): linear from
        1.0 at fresh arms to the authored floor at full arm condition."""
        cm = canon.condition()
        imp = cm["impairment"]
        cap = {d["region"]: d["capacity"] for d in cm["damage_regions"]}
        avg = (f.condition.get("arm_left", 0.0) / cap["arm_left"]
               + f.condition.get("arm_right", 0.0) / cap["arm_right"]) / 2.0
        floor = imp["guard_extent_multiplier_at_full_arms"]
        return 1.0 - (1.0 - floor) * avg

    def _torso_fatigue(self, f: Fighter) -> float:
        """Torso condition as a fraction 0..1, the body-work meter both stamina
        impairments read."""
        cap = {d["region"]: d["capacity"] for d in canon.condition()["damage_regions"]}
        return ((f.condition.get("torso_upper", 0.0) / cap["torso_upper"]
                 + f.condition.get("torso_lower", 0.0) / cap["torso_lower"]) / 2.0)

    # ---- the posture as a trade (guard_evasion_model.posture_economy) --------
    def _stamina_max(self, f: Fighter) -> float:
        """This fighter's tank. Deliberately separate from recovery: how much you
        have and how fast you get it back are different fighters' virtues."""
        return canon.condition()["stamina"]["max"] * self._attr(f, "stamina_maximum")

    # ---- attributes reaching the fight (data/attribute_effects.json) --------
    def _attr(self, f: Fighter, scales: str) -> float:
        """The multiplier this fighter's card contributes to a named mechanic.

        Looked up by the mechanic being scaled rather than by attribute name, so a
        call site says what it is scaling and the data says which attribute does the
        scaling. Returns 1.0 for a mechanic no effect targets and for a fighter whose
        card is silent on it, which is what makes an empty card the baseline (Rule 10).
        """
        for e in canon.attribute_effects()["effects"]:
            if e["scales"] != scales:
                continue
            v = f.attrs.get(e["attribute"])
            if v is None:
                return 1.0
            lo, hi = e["multiplier_at_minus_100"], e["multiplier_at_plus_100"]
            t = (max(-100.0, min(100.0, float(v))) + 100.0) / 200.0
            return lo + (hi - lo) * t
        return 1.0

    def _posture(self, f: Fighter) -> dict:
        return {p["id"]: p for p in canon.guard_evasion()["postures"]}[f.posture]

    def _offense_price(self, f: Fighter, move: dict) -> tuple:
        """What this punch costs from inside THIS guard, in stamina and startup.

        The core combat rule states that a guard 'changes what offense is
        available from inside it'. Every posture has named offense_cheap and
        offense_expensive by move CATEGORY since step 7 and nothing read either,
        so every punch cost the same from every structure. Pricing by category
        rather than by move id is deliberate: it is where the elbows are and
        where the weight sits that makes an uppercut expensive out of a
        cross-arm guard, and that is geometry rather than a tax.
        """
        pe = canon.guard_evasion()["posture_economy"]
        p = self._posture(f)
        cat = move.get("category", "")
        if cat in p.get("offense_cheap", []):
            return pe["offense_cheap_stamina_multiplier"], 1.0
        if cat in p.get("offense_expensive", []):
            return (pe["offense_expensive_stamina_multiplier"],
                    pe["offense_expensive_startup_multiplier"])
        return 1.0, 1.0

    def _fatigue_degradation(self, f: Fighter) -> tuple:
        """punch_model.stamina_gate: below the low-stamina threshold a punch
        arrives later and worse aligned. It always arrives.

        Both coefficients were authored at step 6 and read by nothing, and the
        POLICY was refusing to throw below the exhausted threshold - which is an
        input being eaten, exactly what `input_ever_ignored: false` forbids. The
        gate belongs here, as degradation, not there as a refusal.
        """
        cm = canon.condition()["stamina"]
        sg = canon.punch_model()["stamina_gate"]
        frac = f.stamina / cm["max"]
        lo, hi = cm["exhausted_threshold_fraction"], cm["low_threshold_fraction"]
        if frac >= hi:
            return 1.0, 0.0, False
        t = 1.0 if frac <= lo else (hi - frac) / (hi - lo)
        return (1.0 + (sg["low_stamina_startup_multiplier_max"] - 1.0) * t,
                sg["low_stamina_alignment_penalty_max"] * t,
                True)

    def _apply(self, atk: Fighter, dfn: Fighter, move: dict, cls: str,
               align: float, decision_seq: int, extent: float = 0.0,
               amp: dict | None = None) -> str:
        cm = canon.condition()
        rec = canon.outcome_recovery()[cls]
        bands = {b["class"]: b for b in canon.collision()["quality_bands"]}
        # The Ultimate's amplification, or unity. Force up, recovery up, full
        # stamina - the bar buys force, never safety (ability_model law).
        a_imp = amp["impact_multiplier"] if amp else 1.0
        a_rec = amp["recovery_multiplier"] if amp else 1.0
        a_sta = amp["stamina_cost_multiplier"] if amp else 1.0

        # repetition_economy.arm_fatigue: the arm doing the work pays more for
        # each throw, in stamina and in startup. It recovers whenever that arm
        # rests, so a fighter who mixes hands never accumulates it - the tax is
        # on doing one thing, not on throwing punches.
        hand = move.get("hand", "lead")
        armmul = self._arm_multiplier(atk, hand)
        af = self._mech("arm_fatigue")

        # What this punch costs from inside this guard, and what exhaustion adds
        # to its startup. Both were authored long before anything read them.
        st_mul, start_mul = self._offense_price(atk, move)
        fatigue_start, _, _ = self._fatigue_degradation(atk)

        # Chaining (punch_model.chaining): a link is a punch begun inside the
        # previous punch's late recovery. Opposite-hand links are free because
        # the other hand was already loaded; the same hand pays retraction, and
        # the same POWER hand pays a weight reset. No free cancels - the window
        # opens partway through recovery and never during active contact.
        ch = canon.punch_model()["chaining"]
        linked = self.tick <= atk.link_open_until
        if linked:
            if hand != atk.last_hand:
                link_cost = ch["opposite_hand_link_startup_multiplier"]
            elif move.get("category") in ("cross", "hook", "uppercut", "overhand"):
                link_cost = ch["power_repeat_same_hand_startup_multiplier"]
            else:
                link_cost = ch["same_hand_link_startup_multiplier"]
            # Fluency makes combinations cheaper and never free: it scales the
            # SURPLUS above 1.0, so a perfectly fluent fighter still pays the base
            # cost and link_earliest_recovery_fraction still gates when a link may
            # begin at all.
            link_cost = 1.0 + (link_cost - 1.0) * self._attr(atk, "chain_link_cost")
            start_mul *= link_cost
            atk.combo_length += 1
        else:
            atk.combo_length = 1

        atk.stamina = max(0.0, atk.stamina
                          - move["stamina_cost"] * armmul * a_sta * st_mul)
        # Hand speed shortens startup, which shortens the telegraph the defender
        # reads. It does not touch recovery: commitment is what a punch costs
        # after it is thrown, and speed does not buy a way out of it.
        startup = move["startup_frames"] * start_mul * fatigue_start \
            * self._attr(atk, "punch_startup")
        recovery = move["recovery_frames"] * rec["recovery_multiplier"] * a_rec
        atk.committed = int(recovery + move["startup_frames"] * (armmul - 1.0)
                            + (startup - move["startup_frames"]))
        # The next link may begin once recovery is far enough along.
        atk.link_open_until = self.tick + atk.committed + int(
            recovery * (1.0 - ch["link_earliest_recovery_fraction"]))
        atk.last_hand = hand
        atk.last_move_category = move.get("category", "")
        atk.thrown += 1
        atk.arm_work[hand] = atk.arm_work.get(hand, 0.0) + af["per_throw_same_arm"]

        # repetition_economy.position_cost: throwing without resetting the feet
        # cedes ground. The thrower ends up where the opponent put them.
        pc = self._mech("position_cost")
        atk.threw_without_stepping += 1
        i = self.fighters.index(atk)
        away = -1 if i == 0 else 1
        self.pos[i] = min(max(self.pos[i] + away * pc["ru_ceded_per_throw_without_step"],
                              0.0), self._axis)
        self.distance = abs(self.pos[1] - self.pos[0])

        # The offer is what the defender observes - made before the outcome, so a
        # pattern is read for having been shown, not for having worked.
        self._observe_offer(dfn, move["id"])

        thrown_seq = self.emit("punch_thrown", atk.name, dfn.name,
                               {"move": move["id"], "posture": dfn.posture,
                                "arm_fatigue_multiplier": round(armmul, 3)},
                               [decision_seq])
        landed = cls in bands
        # repetition_economy.counter_window_growth: the same punch from the same
        # timing becomes easier to time. Expressed in the same tick currency as
        # outcome_recovery so the two cannot drift apart.
        cw = self._mech("counter_window_growth")
        seen = max(0, dfn.reads.get(move["id"], 0) - 1)
        payload = {"move": move["id"], "class": cls,
                   "counter_window_ticks": rec["counter_window_ticks"]
                   + min(cw["max_added_ticks"], seen * cw["ticks_per_sighting"])}
        if landed:
            # Quality says how well it landed; impact says how much there was to
            # land. Both, or a clean jab hits like a clean overhand - which is
            # exactly what the repetition-abuse check caught (punch_model
            # delivered_impact).
            force = bands[cls]["delivered_force_fraction"] * self._impact(move) * a_imp \
                * self._attr(atk, "delivered_impact")
            region = move["target_regions"][0]
            # Body work is a distinct competence rather than a target choice: it
            # scales force delivered downstairs only.
            if region.startswith("torso"):
                force *= self._attr(atk, "body_shot_force")
            if region in dfn.condition:
                cap = {d["region"]: d["capacity"] for d in cm["damage_regions"]}[region]
                # Durability decides how fast the night catches up with you; chin
                # decides the knockdown. Two different attributes, two different
                # sites, exactly as attribute_effects declares them.
                dfn.condition[region] = min(cap, dfn.condition[region] + force * 6.0
                                            * self._attr(dfn, "condition_accumulation"))
            payload["region"] = region
            payload["force"] = round(force, 4)
            atk.landed += 1
            atk.round_force += force
            atk.effective_force += force
        if cls == "blocked":
            dfn.blocked_taken += 1
            # Blocking is not free (condition_model.impairment): a blocked punch
            # delivers a fraction of its force into the guarding arms, and arm
            # condition is what erodes coverage extents. This is how sustained
            # pressure opens a guard that never drops - the passive blocker's
            # answer arrives through boxing rather than a rule (Rule 4).
            imp = cm["impairment"]
            # No engine-side multiplier on top of the authored fraction. An
            # earlier version tripled it here, which pegged both arms at full
            # condition by the second round of any busy fight and turned the
            # guard off entirely - a number the data could not be inspected for.
            absorbed = self._impact(move) * a_imp * imp["arm_damage_fraction_of_blocked_force"]
            caps = {d["region"]: d["capacity"] for d in cm["damage_regions"]}
            for arm in ("arm_left", "arm_right"):
                if arm in dfn.condition:
                    dfn.condition[arm] = min(caps[arm], dfn.condition[arm] + absorbed)
        out_seq = self.emit("punch_outcome", atk.name, dfn.name, payload, [thrown_seq])

        self._crowd_gain(atk, dfn, move, cls, out_seq)
        if landed:
            self._knockdown_check(atk, dfn, move, cls, out_seq, extent, a_imp)
        return cls

    def _crowd_gain(self, atk: Fighter, dfn: Fighter, move: dict, cls: str,
                    out_seq: int) -> None:
        """Rule 12: crowd goes to whoever did the thing the crowd saw.

        The earlier version paid every outcome to the ATTACKER - including
        'defense' when the attacker's punch was blocked and 'evasions' when it
        was dodged, so a fighter earned crowd for punching into a guard and the
        defender's work earned nothing. That is why every defensive style ran
        bottom-of-table on crowd while pinned at a full bar it could not use.
        Recipients now follow the crowd_model gain sources as written: landed
        offence pays the puncher ('counters' at its higher rate when the target
        was caught inside their own commitment - the counterpuncher's canon win
        condition); a block pays the blocker; a dodge pays the evader; a whiff
        pays nobody. Novelty decays per RECIPIENT by sameness of what the crowd
        keeps seeing - the fortieth identical block thrills nobody either.
        """
        cr = canon.crowd()
        if move["id"] == atk.last_move:
            atk.repeats += 1
        else:
            atk.repeats = 0
        atk.last_move = move["id"]

        if cls == "whiffed":
            return
        if cls == "blocked":
            earner, src, key = dfn, "defense", "block"
        elif cls == "dodged":
            earner, src, key = dfn, "evasions", "dodge"
        else:
            earner = atk
            # 'combinations' is the second-richest source in the crowd model and
            # was unreachable until chaining executed - a punch landed inside a
            # link is what the crowd is actually cheering.
            if dfn.committed > 0:
                src = "counters"
            elif atk.combo_length > 1:
                src = "combinations"
            else:
                src = "clean_offense"
            key = move["id"]

        source = next((g for g in cr["gain_sources"] if g["id"] == src), None)
        if source is None:
            return
        base = source["base_gain"]
        if key == earner.last_gain_source:
            earner.gain_repeats += 1
        else:
            earner.gain_repeats = 0
        earner.last_gain_source = key
        # novelty_gated is authored per source and was ignored: every source
        # decayed. A source the crowd model exempts must actually be exempt, or
        # the flag is decoration.
        mult = 1.0
        if source.get("novelty_gated", True):
            mult = max(cr["novelty"]["floor_multiplier"],
                       cr["novelty"]["repeat_multiplier"] ** max(0, earner.gain_repeats))
        gain = base * mult
        earner.crowd = min(cr["bar"]["max"], earner.crowd + gain)
        earner.last_gain_tick = self.tick
        self.emit("crowd_gain", earner.name, "", {"source": src, "amount": round(gain, 4),
                                                  "novelty_multiplier": round(mult, 4)},
                  [out_seq])
        if earner.crowd >= cr["bar"]["max"]:
            self.emit("crowd_full", earner.name, "", {}, [out_seq])

    # ---- the fighter_action machine, finally consulted --------------------
    def _action_state(self, f: Fighter) -> str:
        """Which fighter_action state this fighter is in, derived from state the
        engine already tracks. combat_states.json has declared an availability
        block per state - can_punch, can_guard, can_move, can_evade - since step
        1, and nothing ever read it: legality came from a bare `committed > 0`
        counter, so the machine was a document rather than a rule."""
        if self.stopped:
            return "stopped"
        if f.knockdowns and f.committed > self._count_ticks:
            return "knocked_down"
        if f.committed > 0:
            return "move_recovery"
        if self.clinched:
            return "clinch"
        return "idle"

    def _may(self, f: Fighter, capability: str) -> bool:
        states = {s["id"]: s for s in
                  canon.combat_states()["machines"]["fighter_action"]["states"]}
        av = states[self._action_state(f)].get("availability")
        return True if av is None else bool(av.get(capability, False))

    def _mech(self, mid: str) -> dict:
        for m in canon.punch_model()["repetition_economy"]["mechanisms"]:
            if m["id"] == mid:
                return m["coefficients"]
        raise KeyError(f"repetition mechanism '{mid}' has no coefficients in canon")

    def _read_gain(self, dfn: Fighter, move_id: str) -> float:
        """repetition_economy.opponent_read, as the canon states it: fires on a
        pattern the DEFENDER has seen more than once, and gives the defender an
        earlier arrival against that specific pattern.

        Deliberately not a repeat counter on the thrower. It is keyed to the
        defender, it needs sightings to exist at all, and _observe_offer decays
        it against every pattern that is not currently being offered - so a
        fighter who varies is never carrying something they cannot shed. That
        distinction is the whole of Rule 4's prohibited_mechanisms list.
        """
        c = self._mech("opponent_read")
        seen = dfn.reads.get(move_id, 0)
        if seen < c["sightings_before_effect"]:
            return 0.0
        return min(c["max_gain"], (seen - c["sightings_before_effect"] + 1) * c["gain_per_sighting"])

    def _observe_offer(self, dfn: Fighter, move_id: str) -> None:
        """The defender sees this pattern once more, and forgets a little of
        every other one. Forgetting is what keeps the read honest."""
        c = self._mech("opponent_read")
        dfn.reads[move_id] = dfn.reads.get(move_id, 0) + 1
        for k in list(dfn.reads):
            if k != move_id:
                dfn.reads[k] = max(0, dfn.reads[k] - c["decay_per_unseen_offer"])

    def _arm_multiplier(self, f: Fighter, hand: str) -> float:
        c = self._mech("arm_fatigue")
        return min(c["max_multiplier"], 1.0 + f.arm_work.get(hand, 0.0))

    def _impact(self, move: dict) -> float:
        """Rule 14: a punch's power is what it cost to throw, normalized over the
        punch table's own range. No per-move power field exists to read, and the
        punch model's schema forbids adding one - a punch that is cheap, fast and
        heavy is the thing commitment exists to prevent."""
        di = canon.punch_model()["delivered_impact"]
        costs = [m["stamina_cost"] for m in canon.punches().values()]
        lo, hi = min(costs), max(costs)
        if hi <= lo:
            return di["max_impact_scalar"]
        t = (move["stamina_cost"] - lo) / (hi - lo)
        return di["min_impact_scalar"] + t * (di["max_impact_scalar"] - di["min_impact_scalar"])

    def _knockdown_check(self, atk: Fighter, dfn: Fighter, move: dict, cls: str,
                         out_seq: int, extent: float = 0.0,
                         a_imp: float = 1.0) -> None:
        """Rule 14: observable force, quality and accumulated condition. No dice
        roll attached to the punch - the threshold is a function of state."""
        cm = canon.condition()
        if cls not in ("solid", "clean"):
            return
        jaw = dfn.condition.get("jaw_chin", 0.0)
        head = dfn.condition.get("head", 0.0)
        force = {"solid": 0.75, "clean": 1.0}[cls] * self._impact(move) * a_imp
        accumulated = (jaw * 0.6 + head * 0.4) / 100.0
        stamina_frac = dfn.stamina / self._stamina_max(dfn)
        kdm = cm["knockdown"]
        pm = kdm["pressure_modifiers"]
        # balance and guard_state: two inputs canon has listed since step 8 that
        # nothing was reading. Being caught inside your own recovery is the
        # counter-punch knockdown; an open lane lands heavier than a covered one.
        balance = pm["caught_committed_multiplier"] if dfn.committed > 0 \
            else pm["balanced_multiplier"]
        if dfn.committed > 0:
            # Counter timing is how much of an opponent's commitment this fighter
            # actually converts - it scales the SURPLUS over a balanced target, so
            # it can never make catching someone worth less than not catching them.
            balance = pm["balanced_multiplier"] + (balance - pm["balanced_multiplier"]) \
                * self._attr(atk, "counter_window_exploitation")
        guard = 1.0 + pm["unguarded_lane_bonus"] * (1.0 - max(0.0, min(1.0, extent)))
        pressure = (force * (pm["undamaged_baseline"] + accumulated)
                    * (1.4 - stamina_frac) * balance * guard)
        # Chin raises the line pressure must cross. Bounded above by
        # attribute_effects precisely because condition_model.chin says maximum
        # resistance is never immunity: +100 Chin is the most authored resistance
        # in the game and still loses to enough evidence (Rule 14).
        threshold = kdm["pressure_threshold"] * self._attr(dfn, "knockdown_pressure_threshold")
        if pressure < threshold \
                or move["target_regions"][0] not in ("jaw_chin", "head"):
            return
        dfn.knockdowns += 1
        dfn.round_knockdowns_suffered += 1
        # The mandatory eight count, which canon has declared since step 8 and
        # which nothing was executing: the man who was down loses the time as
        # well as the point.
        count_ticks = kdm["count_ticks_per_number"]
        dfn.committed = count_ticks * (8 if kdm.get("mandatory_eight_count") else 3)
        kd = self.emit("knockdown", atk.name, dfn.name,
                       {"pressure": round(pressure, 4),
                        "accumulated_condition": round(accumulated, 4),
                        "count": dfn.knockdowns}, [out_seq])
        # Rule 16: the count arithmetic is identical for every referee.
        for n in range(1, (8 if kdm.get("mandatory_eight_count") else 3) + 1):
            self.emit("count_tick", "referee", dfn.name, {"number": n}, [kd])
        # Rising is a partial recovery, which is the entire point of the count.
        # Without it accumulated condition only ever climbs, so the first
        # knockdown guarantees the rest and no bout survives to the cards.
        rel = min(0.95, kdm["count_condition_relief_fraction"]
                  * self._attr(dfn, "between_rounds_recovery"))
        for region in ("jaw_chin", "head"):
            if region in dfn.condition:
                dfn.condition[region] *= (1.0 - rel)
        deficit = self._stamina_max(dfn) - dfn.stamina
        dfn.stamina += deficit * kdm["count_stamina_relief_fraction"]
        self.emit("rise", dfn.name, "", {"after_count": 8,
                                         "condition_relief": rel,
                                         "stamina_after": round(dfn.stamina, 3)}, [kd])
        if dfn.round_knockdowns_suffered >= kdm["max_per_round"]:
            self.stopped = True
            self.stop_reason = "three_knockdown_rule"
            self.emit("stoppage", "referee", dfn.name,
                      {"condition": "three_knockdown_rule"}, [kd])
        elif dfn.knockdowns >= kdm["max_per_bout"]:
            self.stopped = True
            self.stop_reason = "knockdown_limit"
            self.emit("stoppage", "referee", dfn.name,
                      {"condition": "knockdown_limit"}, [kd])

    # ---- the loop -------------------------------------------------------
    def run(self) -> list:
        from . import policy
        cm = canon.condition()
        cpu = canon.cpu()
        interval = cpu["reaction"]["decision_interval_ticks"]
        for f in self.fighters:
            f.posture = policy.posture_for(f.profile)
        self.emit("bout_start", "", "", {"seed": self.seed,
                                         "profiles": [f.profile for f in self.fighters]})
        for rnd in range(1, self.rounds + 1):
            if self.stopped:
                break
            self.round = rnd
            self.emit("round_start", "", "", {"round": rnd})
            self._run_round()
            self.emit("round_end", "", "", {"round": rnd})
            self._score_round()          # sealed
            if not self.stopped and rnd < self.rounds:
                self._between_rounds()
        self.emit("bout_end", "", "", {"stopped": self.stopped,
                                       "reason": self.stop_reason})
        self._final_card()               # sealed
        return self.log

    def _run_round(self) -> None:
        from . import policy
        cm = canon.condition()
        cpu = canon.cpu()
        interval = cpu["reaction"]["decision_interval_ticks"]
        punches = canon.punches()
        start = self.tick
        while self.tick - start < self.round_ticks and not self.stopped:
            self.tick += 1
            for i, f in enumerate(self.fighters):          # fixed order
                opp = self.fighters[1 - i]
                if f.committed > 0:
                    f.committed -= 1
                    f.stamina = min(self._stamina_max(f), f.stamina)
                    continue
                # Idle regeneration, never faster than resting (Rule 14) - and
                # scaled by body work: torso regions impair stamina
                # (condition_model.impairment). A worked body refills slower,
                # which is the entire point of investing downstairs.
                imp = cm["impairment"]
                torso = self._torso_fatigue(f)
                regen_mult = 1.0 - (1.0 - imp["stamina_regen_multiplier_at_full_torso"]) * torso
                f.stamina = min(self._stamina_max(f),
                                f.stamina + cm["stamina"]["regen_per_tick_idle"] * regen_mult)
                # Holding the guard costs (guard_evasion_model posture
                # stamina_per_tick, declared at step 7 and read by nothing until
                # now). Charged only while not committed - you are not holding a
                # guard mid-punch, you are punching. This is the third clause of
                # the core combat rule: a guard costs resources to hold.
                f.stamina = max(0.0, f.stamina - self._posture(f)["stamina_per_tick"])
                # Arm fatigue drains while the arm is not working. A fighter who
                # mixes hands sheds it as fast as they build it, which is why
                # this taxes a loop and not a workrate.
                arec = self._mech("arm_fatigue")["recovery_per_idle_tick"]
                for h in f.arm_work:
                    f.arm_work[h] = max(0.0, f.arm_work[h] - arec)
                # The bar drains after its grace window (crowd_model.bar) -
                # declared idle decay, finally executed. Banking a bar and
                # coasting is what this exists to prevent.
                bar = canon.crowd()["bar"]
                if f.crowd > 0 and (self.tick - f.last_gain_tick) > bar["decay_grace_ticks"]:
                    f.crowd = max(0.0, f.crowd - bar["decay_per_tick_idle"])
                if (self.tick % interval) != 0:
                    continue
                if self.clinched:
                    self.clinch_ticks -= 1
                    if self.clinch_ticks <= 0:
                        self.clinched = False
                        # The referee breaks them where they stand: separation
                        # opens, ring position does not teleport (Rule 13).
                        centre = (self.pos[0] + self.pos[1]) / 2.0
                        centre = min(max(centre, 0.25), self._axis - 0.25)
                        self.pos = [centre - 0.25, centre + 0.25]
                        self.distance = self.pos[1] - self.pos[0]
                        self.emit("clinch_end", "", "",
                                  {"distance_ru": round(self.distance, 4)})
                        self._check_ropes()
                        self._resolve_band()
                    continue
                obs = self.observe(f, opp)
                action = policy.decide(f.profile, obs, self.rng)
                if action is None:
                    continue
                dseq = self.emit("cpu_decision", f.name, "",
                                 {"chosen_action": action,
                                  "confidence": 0.5,
                                  "observed_keys": sorted(obs)})
                # Legality comes from the fighter_action machine's availability
                # block, not from a bare committed counter. A refused action is
                # emitted, never silently dropped: Rule 19 is about the input
                # being heard, not about it always succeeding.
                if action in ("step_in", "step_out", "step_lateral"):
                    if not self._may(f, "can_move"):
                        self.emit("cpu_decision", f.name, "",
                                  {"chosen_action": action, "refused_by_state":
                                   self._action_state(f)}, [dseq])
                        continue
                    self.step(f, {"step_in": "in", "step_out": "out",
                                  "step_lateral": "lateral"}[action])
                    continue
                if action == "clinch_entry":
                    self.clinch(f, opp)
                    continue
                if action == "ultimate":
                    # The full-bar conversion (ability_model.reference_instruments):
                    # the Ultimate rides the heaviest punch this band permits,
                    # through the ordinary pipeline - blockable, dodgeable,
                    # whiffable, counterable - and the bar empties on the swing,
                    # hit or miss, because the crowd paid for the attempt.
                    cr = canon.crowd()
                    if f.crowd < cr["bar"]["max"]:
                        continue          # a policy asking early gets nothing
                    band_key = self._bands[self.band]["key"]
                    rides = [m for m in punches.values() if m["range_band"] == band_key]
                    if not rides:
                        continue
                    move = max(rides, key=lambda m: m["stamina_cost"])
                    u = canon.ability()["reference_instruments"]["instrument_ultimate"]
                    useq = self.emit("ultimate_activated", f.name, opp.name,
                                     {"rides": move["id"],
                                      "impact_multiplier": u["impact_multiplier"],
                                      "recovery_multiplier": u["recovery_multiplier"]},
                                     [dseq])
                    f.crowd = 0.0          # crowd_model.bar.resets_on_full_spend
                    f.last_gain_tick = self.tick
                    self.resolve(f, opp, move, useq, amp=u)
                    if self.stopped:
                        break
                    continue
                if action not in punches:
                    continue
                if not self._may(f, "can_punch"):
                    self.emit("cpu_decision", f.name, "",
                              {"chosen_action": action, "refused_by_state":
                               self._action_state(f)}, [dseq])
                    continue
                self.resolve(f, opp, punches[action], dseq)
                if self.stopped:
                    break

    def _between_rounds(self) -> None:
        cm = canon.condition()
        bs = self.emit("break_start", "", "", {"ticks": cm["recovery"]["between_rounds_break_ticks"]})
        for f in self.fighters:
            deficit = self._stamina_max(f) - f.stamina
            # The corner cannot fully mend a worked body (condition_model.
            # impairment): body investment carries into the next round, which is
            # the whole reason bodywork is named in two canon win conditions.
            imp = cm["impairment"]
            torso = self._torso_fatigue(f)
            rec_mult = 1.0 - (1.0 - imp["between_rounds_recovery_multiplier_at_full_torso"]) \
                * torso
            f.stamina += deficit * cm["stamina"]["between_rounds_recovery_fraction"] * rec_mult
            for d in cm["damage_regions"]:
                f.condition[d["region"]] *= (1.0 - d["recovers_between_rounds"])
        self.emit("break_end", "", "", {}, [bs])

    # ---- sealed judging -------------------------------------------------
    def _score_round(self) -> None:
        """Ten-point-must on the round in front of the judges (Rule 3: sealed).

        Two corrections were forced by the style-viability and abuse-list checks,
        and both are logged here so a later edit does not silently undo them:

        1. The round is scored on THIS round's work. The previous version summed
           bout-to-date landings, so an early lead re-won every subsequent round.
        2. The round is scored on effective offence - the sum of delivered force
           fractions - not on a raw count of contacts. Counting contacts made a
           brushed jab (0.15 force) worth exactly as much as a clean cross (1.0),
           which is what let a single-jab loop out-point a varied fighter it was
           visibly losing to. Quality already exists in canon as the collision
           model's `delivered_force_fraction`; the card now reads it rather than
           inventing a volume proxy beside it. This is the judging analogue of
           Rule 14: what lands, and how well, decides - never a flat tally.

        Knockdowns are deducted the way a real card deducts them: one point per
        knockdown suffered in the round, on top of losing it.
        """
        a, b = self.fighters
        if a.round_force > b.round_force:
            win = a
        elif b.round_force > a.round_force:
            win = b
        else:
            win = None
        for f in self.fighters:
            base = 10.0 if (win is None or f is win) else 9.0
            self._cards[f.name] += base - f.round_knockdowns_suffered
        self.emit("judge_round_card", "", "", {"round": self.round},
                  visibility="sealed")
        for f in self.fighters:
            f.round_force = 0.0
            f.round_knockdowns_suffered = 0

    def _final_card(self) -> None:
        self.emit("judge_final_card", "", "", {"rounds": self.round},
                  visibility="sealed")

    def decision(self) -> str:
        """The bout's outcome, as an official would read it: a stoppage first,
        otherwise the cards. Not reachable from an Observation - policies receive
        the dict from observe(), never the Bout - so Rule 3 still holds. This is
        the referee's-eye view the evidence harness is entitled to.
        """
        a, b = self.fighters
        if self.stopped:
            if a.knockdowns != b.knockdowns:
                return b.name if a.knockdowns > b.knockdowns else a.name
        ca, cb = self._cards[a.name], self._cards[b.name]
        if ca != cb:
            return a.name if ca > cb else b.name
        return ""

    def result(self) -> dict:
        return {
            "seed": self.seed,
            "stopped": self.stopped,
            "reason": self.stop_reason,
            "fighters": [
                {"name": f.name, "profile": f.profile, "thrown": f.thrown,
                 "landed": f.landed, "effective_force": round(f.effective_force, 3),
                 "knockdowns": f.knockdowns,
                 "crowd": round(f.crowd, 3),
                 "stamina": round(f.stamina, 3)}
                for f in self.fighters
            ],
        }
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:33 UTC | END ]
