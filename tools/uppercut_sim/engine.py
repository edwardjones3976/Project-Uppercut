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
        for f in self.fighters:
            f.condition = {d["region"]: 0.0 for d in cm["damage_regions"]}
        self.log: list = []
        self.seq = 0
        self.tick = 0
        self.round = 0
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
            "own_stamina_fraction": me.stamina / cm["stamina"]["max"],
            "own_crowd_fraction": me.crowd / canon.crowd()["bar"]["max"],
            "own_knockdowns": me.knockdowns,
            "opponent_knockdowns": opp.knockdowns,
            "opponent_visible_posture": opp.posture,
            "opponent_recent_thrown": opp.thrown,
            "my_last_move": me.last_move,
            "my_repeats": me.repeats,
            "round": self.round,
            "tick_in_round": self.tick % self.round_ticks,
        }

    # ---- the canonical collision pipeline -------------------------------
    def resolve(self, atk: Fighter, dfn: Fighter, move: dict, decision_seq: int) -> str:
        """Stage order exactly as data/collision_model.json declares it."""
        col = canon.collision()
        ge = canon.guard_evasion()
        qthr = canon.quality_thresholds()
        postures = {p["id"]: p for p in ge["postures"]}

        r_sweep = self.rng.random()
        r_evade = self.rng.random()
        r_guard = self.rng.random()
        align = self.rng.random()

        # Stage 0, inverted: no overlap terminates at whiffed.
        if r_sweep < 0.15:
            return self._apply(atk, dfn, move, "whiffed", align, decision_seq)
        # Stage 1: active evasion, ranked above guard on purpose.
        evade_chance = 0.10 + 0.10 * postures[dfn.posture]["counter_readiness"]
        if r_evade < evade_chance:
            return self._apply(atk, dfn, move, "dodged", align, decision_seq)
        # Stage 2: guard interception - which volume is permitted, and does its
        # coverage extent actually reach (Decision 0010).
        gi = col["guard_interception"]
        volumes = gi.get(move["guard_interaction"], [])
        extent = max((postures[dfn.posture]["extents"].get(v, 0.0) for v in volumes),
                     default=0.0)
        if r_guard < extent * 0.55:
            return self._apply(atk, dfn, move, "blocked", align, decision_seq)
        # Stage 3: quality dispatch.
        qc = sum(1 for t in qthr if align >= t)
        cls = ["brushed", "grazed", "solid", "clean"][qc]
        return self._apply(atk, dfn, move, cls, align, decision_seq)

    def _apply(self, atk: Fighter, dfn: Fighter, move: dict, cls: str,
               align: float, decision_seq: int) -> str:
        cm = canon.condition()
        rec = canon.outcome_recovery()[cls]
        bands = {b["class"]: b for b in canon.collision()["quality_bands"]}

        atk.stamina = max(0.0, atk.stamina - move["stamina_cost"])
        atk.committed = int(move["recovery_frames"] * rec["recovery_multiplier"])
        atk.thrown += 1

        thrown_seq = self.emit("punch_thrown", atk.name, dfn.name,
                               {"move": move["id"], "posture": dfn.posture},
                               [decision_seq])
        landed = cls in bands
        payload = {"move": move["id"], "class": cls,
                   "counter_window_ticks": rec["counter_window_ticks"]}
        if landed:
            force = bands[cls]["delivered_force_fraction"]
            region = move["target_regions"][0]
            if region in dfn.condition:
                dfn.condition[region] = min(100.0, dfn.condition[region] + force * 6.0)
            payload["region"] = region
            payload["force"] = force
            atk.landed += 1
        out_seq = self.emit("punch_outcome", atk.name, dfn.name, payload, [thrown_seq])

        self._crowd_gain(atk, move, cls, out_seq)
        if landed:
            self._knockdown_check(atk, dfn, move, cls, out_seq)
        return cls

    def _crowd_gain(self, f: Fighter, move: dict, cls: str, out_seq: int) -> None:
        """Rule 12: novelty decays toward a floor above zero; risk is required."""
        cr = canon.crowd()
        src = {"clean": "clean_offense", "solid": "clean_offense",
               "grazed": "clean_offense", "brushed": "clean_offense",
               "blocked": "defense", "dodged": "evasions", "whiffed": None}[cls]
        if src is None:
            return
        base = next((g["base_gain"] for g in cr["gain_sources"] if g["id"] == src), 0.0)
        if move["id"] == f.last_move:
            f.repeats += 1
        else:
            f.repeats = 0
        mult = max(cr["novelty"]["floor_multiplier"],
                   cr["novelty"]["repeat_multiplier"] ** max(0, f.repeats))
        gain = base * mult
        f.crowd = min(cr["bar"]["max"], f.crowd + gain)
        f.last_move = move["id"]
        self.emit("crowd_gain", f.name, "", {"source": src, "amount": round(gain, 4),
                                             "novelty_multiplier": round(mult, 4)},
                  [out_seq])
        if f.crowd >= cr["bar"]["max"]:
            self.emit("crowd_full", f.name, "", {}, [out_seq])

    def _knockdown_check(self, atk: Fighter, dfn: Fighter, move: dict, cls: str,
                         out_seq: int) -> None:
        """Rule 14: observable force, quality and accumulated condition. No dice
        roll attached to the punch - the threshold is a function of state."""
        cm = canon.condition()
        if cls not in ("solid", "clean"):
            return
        jaw = dfn.condition.get("jaw_chin", 0.0)
        head = dfn.condition.get("head", 0.0)
        force = {"solid": 0.75, "clean": 1.0}[cls]
        accumulated = (jaw * 0.6 + head * 0.4) / 100.0
        stamina_frac = dfn.stamina / cm["stamina"]["max"]
        pressure = force * (0.35 + accumulated) * (1.4 - stamina_frac)
        if pressure < 0.55 or move["target_regions"][0] not in ("jaw_chin", "head"):
            return
        dfn.knockdowns += 1
        dfn.committed = cm["knockdown"]["count_ticks_per_number"] * 3
        kd = self.emit("knockdown", atk.name, dfn.name,
                       {"pressure": round(pressure, 4),
                        "accumulated_condition": round(accumulated, 4),
                        "count": dfn.knockdowns}, [out_seq])
        if dfn.knockdowns >= cm["knockdown"]["max_per_bout"]:
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
                    f.stamina = min(cm["stamina"]["max"], f.stamina)
                    continue
                # Idle regeneration, never faster than resting (Rule 14).
                f.stamina = min(cm["stamina"]["max"],
                                f.stamina + cm["stamina"]["regen_per_tick_idle"])
                if (self.tick % interval) != 0:
                    continue
                obs = self.observe(f, opp)
                move_id = policy.decide(f.profile, obs, self.rng)
                if move_id is None:
                    continue
                dseq = self.emit("cpu_decision", f.name, "",
                                 {"chosen_action": move_id,
                                  "confidence": 0.5,
                                  "observed_keys": sorted(obs)})
                self.resolve(f, opp, punches[move_id], dseq)
                if self.stopped:
                    break

    def _between_rounds(self) -> None:
        cm = canon.condition()
        bs = self.emit("break_start", "", "", {"ticks": cm["recovery"]["between_rounds_break_ticks"]})
        for f in self.fighters:
            deficit = cm["stamina"]["max"] - f.stamina
            f.stamina += deficit * cm["stamina"]["between_rounds_recovery_fraction"]
            for d in cm["damage_regions"]:
                f.condition[d["region"]] *= (1.0 - d["recovers_between_rounds"])
        self.emit("break_end", "", "", {}, [bs])

    # ---- sealed judging -------------------------------------------------
    def _score_round(self) -> None:
        """Rule 3: emitted sealed, and no observable event carries card data."""
        best = max(self.fighters, key=lambda f: f.landed)
        for f in self.fighters:
            self._cards[f.name] += 10.0 if f is best else 9.0
        self.emit("judge_round_card", "", "", {"round": self.round},
                  visibility="sealed")

    def _final_card(self) -> None:
        self.emit("judge_final_card", "", "", {"rounds": self.round},
                  visibility="sealed")

    def result(self) -> dict:
        return {
            "seed": self.seed,
            "stopped": self.stopped,
            "reason": self.stop_reason,
            "fighters": [
                {"name": f.name, "profile": f.profile, "thrown": f.thrown,
                 "landed": f.landed, "knockdowns": f.knockdowns,
                 "crowd": round(f.crowd, 3),
                 "stamina": round(f.stamina, 3)}
                for f in self.fighters
            ],
        }
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:33 UTC | END ]
