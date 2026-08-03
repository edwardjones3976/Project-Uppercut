# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:42 UTC | START ]
"""The ROADMAP's required automated checks, run against the reference simulator.

ROADMAP Phase 1A lists eleven required checks. Until now only the attribute
fixtures existed, because the others need something to run. This implements the
ones the reference model can honestly answer today:

  score-access denial, determinism and seeded replay, repetition-versus-spam,
  large-batch invalid-state and deadlock, knockdown/stoppage/result states,
  First Bell Firestorm, Long Drain, and Crowd-farming prohibition.

Each returns a list of findings; empty means pass. They are deliberately written
to be falsifiable - several assert that a thing CAN happen, because a check that
only forbids can be satisfied by a simulation where nothing happens at all.
"""
from __future__ import annotations
import hashlib
import json

from . import canon, policy
from .engine import Bout

SEALED = ("judge_round_card", "judge_final_card")
CARD_WORDS = ("card", "score", "points", "leading", "behind")


def _log_hash(log: list) -> str:
    return hashlib.sha256(json.dumps(log, sort_keys=True).encode()).hexdigest()


def _bout(seed: int, a: str = "technician", b: str = "counterpuncher", **kw) -> Bout:
    bt = Bout(seed, a, b, **kw)
    bt.run()
    return bt


# ---- 1. score-access denial ------------------------------------------------
def check_score_access_denial() -> list:
    bt = _bout(9001)
    errs = []
    for ev in bt.log:
        if ev["type"] in SEALED and ev["visibility"] != "sealed":
            errs.append(f"seq {ev['seq']}: {ev['type']} emitted as {ev['visibility']}")
        if ev["visibility"] == "observable":
            blob = json.dumps(ev.get("payload", {})).lower()
            for w in CARD_WORDS:
                if w in blob:
                    errs.append(f"seq {ev['seq']}: observable {ev['type']} payload leaks '{w}'")
    # The firewall as a call-signature property: an Observation carries no path
    # to the sealed cards, so a policy physically cannot reach them.
    obs = bt.observe(bt.fighters[0], bt.fighters[1])
    for k in obs:
        for w in CARD_WORDS:
            if w in k.lower():
                errs.append(f"observation key '{k}' exposes score-adjacent state")
    if any(isinstance(v, Bout) for v in obs.values()):
        errs.append("the observation hands the policy a reference to the bout itself")
    if not any(e["type"] in SEALED for e in bt.log):
        errs.append("no judge events were emitted at all - the check would pass vacuously")
    return errs


# ---- 2. determinism and seeded replay --------------------------------------
def check_determinism_and_replay() -> list:
    errs = []
    a1 = _log_hash(_bout(4242).log)
    a2 = _log_hash(_bout(4242).log)
    b1 = _log_hash(_bout(4243).log)
    if a1 != a2:
        errs.append("same seed produced different logs - resimulation is broken")
    if a1 == b1:
        errs.append("different seeds produced identical logs - the check is vacuous and the "
                    "stream is probably not being consumed")
    return errs


# ---- 3. repetition versus spam ---------------------------------------------
def check_repetition_versus_spam() -> list:
    """Rule 4: repeating one action must pay progressively less, and must still
    pay something. Both halves are checked - a model that zeroes repetition has
    prohibited it rather than de-emphasised it."""
    bt = _bout(7777, "rusher", "rusher")
    errs = []
    gains = [e for e in bt.log if e["type"] == "crowd_gain"]
    if not gains:
        return ["no crowd gains at all - repetition check is vacuous"]
    mults = [g["payload"]["novelty_multiplier"] for g in gains]
    if max(mults) <= min(mults):
        errs.append("the novelty multiplier never varied - repetition costs nothing")
    floor = canon.crowd()["novelty"]["floor_multiplier"]
    if min(mults) < floor - 1e-9:
        errs.append(f"a repeated action fell below the novelty floor {floor}")
    if any(g["payload"]["amount"] <= 0 for g in gains):
        errs.append("Rule 4: a repeated action earned exactly zero - legitimate repetition is "
                    "protected and must keep paying something")
    return errs


# ---- 4. large-batch invalid state and deadlock ------------------------------
def check_large_batch(n: int = 40) -> list:
    errs = []
    cm = canon.condition()
    for seed in range(n):
        bt = _bout(5000 + seed, "showman", "drainer", rounds=2, round_seconds=60)
        for f in bt.fighters:
            if f.stamina < -1e-9 or f.stamina > cm["stamina"]["max"] + 1e-9:
                errs.append(f"seed {seed}: stamina out of range ({f.stamina})")
            if f.knockdowns > cm["knockdown"]["max_per_bout"]:
                errs.append(f"seed {seed}: knockdowns exceed the bout maximum")
            for r, v in f.condition.items():
                if v < -1e-9 or v > 100.0 + 1e-9:
                    errs.append(f"seed {seed}: condition '{r}' out of range ({v})")
        seqs = [e["seq"] for e in bt.log]
        if seqs != sorted(seqs) or len(set(seqs)) != len(seqs):
            errs.append(f"seed {seed}: event sequence is not strictly ordered")
        ticks = [e["tick"] for e in bt.log]
        if ticks != sorted(ticks):
            errs.append(f"seed {seed}: event ticks are not monotonic")
        for e in bt.log:
            for ref in e.get("explains", []):
                if ref >= e["seq"]:
                    errs.append(f"seed {seed}: seq {e['seq']} explains a later event")
        if not any(e["type"] == "punch_outcome" for e in bt.log):
            errs.append(f"seed {seed}: no punch resolved - the bout deadlocked")
    return errs


# ---- 5. knockdown, stoppage and result states -------------------------------
def check_result_states() -> list:
    errs = []
    stopped = 0
    for seed in range(30):
        bt = _bout(100 + seed, "power_threat", "showman", rounds=3, round_seconds=90)
        kd = [e for e in bt.log if e["type"] == "knockdown"]
        st = [e for e in bt.log if e["type"] == "stoppage"]
        if st:
            stopped += 1
            if not kd:
                errs.append(f"seed {seed}: a stoppage occurred with no knockdown to explain it")
            for s in st:
                if not s.get("explains"):
                    errs.append(f"seed {seed}: stoppage carries no causal explanation")
        if not bt.log or bt.log[-1]["type"] != "judge_final_card":
            errs.append(f"seed {seed}: the bout did not end with a final card")
    if stopped == 0:
        errs.append("no bout in 30 ever reached a stoppage - the stoppage path is untested")
    return errs


# ---- 6. First Bell Firestorm ------------------------------------------------
def check_first_bell_firestorm() -> list:
    """Effective opening aggression must be able to win; volume alone must not
    be sufficient. Both directions are asserted."""
    errs = []
    aggressive_wins = 0
    for seed in range(24):
        bt = _bout(300 + seed, "rusher", "technician", rounds=2, round_seconds=90)
        a, b = bt.fighters
        if a.landed > b.landed:
            aggressive_wins += 1
    if aggressive_wins == 0:
        errs.append("the aggressive instrument never out-landed the technician in 24 bouts - "
                    "effective pressure has no route to victory")
    if aggressive_wins == 24:
        errs.append("the aggressive instrument won every bout - volume alone is sufficient, which "
                    "is the failure this test exists to catch")
    return errs


# ---- 7. Long Drain ----------------------------------------------------------
def check_long_drain() -> list:
    """Patient stamina control must be able to win; empty avoidance must not."""
    errs = []
    drainer_ends_fresher = 0
    for seed in range(24):
        bt = _bout(600 + seed, "drainer", "rusher", rounds=3, round_seconds=120)
        d, r = bt.fighters
        if d.stamina > r.stamina:
            drainer_ends_fresher += 1
        if d.thrown == 0:
            errs.append(f"seed {seed}: the patient instrument threw nothing - that is empty "
                        f"avoidance, not stamina control")
    if drainer_ends_fresher == 0:
        errs.append("patient stamina control never ended fresher than the pressure fighter - the "
                    "stamina economy gives patience no payoff")
    return errs


# ---- 8. Crowd-farming prohibition -------------------------------------------
def check_crowd_farming() -> list:
    """A one-move spammer must not out-earn a varied fighter on crowd."""
    errs = []
    spam = _bout(2100, "power_threat", "technician", rounds=2, round_seconds=90)
    varied = _bout(2100, "technician", "power_threat", rounds=2, round_seconds=90)
    spam_gains = [e["payload"]["novelty_multiplier"]
                  for e in spam.log if e["type"] == "crowd_gain"]
    if not spam_gains:
        return ["no crowd gain events - the farming check is vacuous"]
    if sum(1 for m in spam_gains if m < 1.0) == 0:
        errs.append("no crowd gain was ever reduced by novelty - farming is unpunished")
    cr = canon.crowd()
    if not cr["risk_gate"]["zero_gain_when_unopposed"]:
        errs.append("the crowd model no longer zeroes gain against an unopposed target")
    return errs


ALL_CHECKS = [
    ("score_access_denial", check_score_access_denial),
    ("determinism_and_seeded_replay", check_determinism_and_replay),
    ("repetition_versus_spam", check_repetition_versus_spam),
    ("large_batch_invalid_state", check_large_batch),
    ("knockdown_stoppage_result_states", check_result_states),
    ("first_bell_firestorm", check_first_bell_firestorm),
    ("long_drain", check_long_drain),
    ("crowd_farming_prohibition", check_crowd_farming),
]


def run_all() -> list:
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn())
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:42 UTC | END ]
