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
    # Both result states, or one of them is unimplemented wearing a passing test.
    # This half was missing until 2026-08-03, and while it was missing the model
    # spent a whole sweep stopping 100% of bouts with the entire judging path -
    # round scoring, the cards, every style that wins on points - dead code.
    if stopped == 30:
        errs.append("every one of 30 bouts ended in a stoppage - no fight reaches the cards, so "
                    "round scoring and every points-based style are unreachable")
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


# ---- 9. accelerated-clock synchronization ----------------------------------
def check_accelerated_clock() -> list:
    """The ninth required check, unblocked by data/clock_model.json.

    The Accelerated Clock is a display mapping. Every system must stay on one
    clock, and nothing about the simulation may change when it is toggled - so
    the test is that the authoritative log is IDENTICAL either way, while the
    displayed time is the only thing that moves.
    """
    errs = []
    cl = json.loads((canon.REPO / "data" / "clock_model.json").read_text(encoding="utf-8"))
    ac = cl["accelerated_clock"]

    for k in ("affects_simulation_tick_rate", "affects_authored_frame_data",
              "affects_stamina_per_tick", "affects_knockdown_count_clock"):
        if ac[k]:
            errs.append(f"acceleration reaches the simulation via {k}")

    # Every event must carry both times, and they must agree on the tick.
    bt = _bout(31337)
    hz = cl["authority"]["tick_rate_hz"]
    ratio = ac["on_display_seconds"] / ac["on_real_seconds"]
    for ev in bt.log:
        c = ev.get("clock")
        if not c:
            errs.append(f"seq {ev['seq']}: event carries no clock - Rule 9 needs one clock read "
                        f"by everything, which means every record stamps it")
            break
        if c["real_ms"] != int(ev["tick"] * 1000 / hz):
            errs.append(f"seq {ev['seq']}: real_ms disagrees with the authoritative tick")
            break

    # Accelerated display advances faster than real time, and only that.
    if ratio <= 1.0:
        errs.append("the accelerated ratio does not accelerate anything")
    accel_display = int(1000 * ratio)
    if accel_display <= 1000:
        errs.append("one real second of accelerated play must display more than one second")
    if cl["between_rounds_break_seconds"] * hz != canon.condition()["recovery"][
            "between_rounds_break_ticks"]:
        errs.append("the clock model and the condition model disagree on the break length - two "
                    "clocks by another name")
    return errs


# ---- 10. style viability and dominant-loop detection ------------------------
def _winner(bt) -> str:
    """The bout's official outcome, read from the engine rather than restated.

    An earlier version of this helper computed its own verdict from knockdowns
    and raw landed count. That was wrong twice over: it duplicated an authority
    that already exists (the sealed cards), and its volume tiebreak disagreed
    with them, so the harness could call a bout for a fighter the judges scored
    against. `Bout.decision()` is the single reading. Rule 3 is untouched - the
    firewall stops POLICIES seeing the cards, and a policy never holds a Bout.
    """
    return bt.decision()


def style_balance(seeds: int = 8, base: int = 41000) -> dict:
    """Win counts per style over an all-pairs sweep at canonical bout length.

    Separated from the gate check on purpose. The gate is 'can this style win at
    all' - a binary the project can hold itself to today. The rates this returns
    are tuning evidence, and they are lopsided right now: reported in
    docs/phase1a/exploit_hunt.md rather than converted into a red test, because
    a check that fails for a known, named, unresolved tuning question stops being
    read after the second week.
    """
    names = policy.available_profiles()
    wins = {n: 0 for n in names}
    played = {n: 0 for n in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for s in range(seeds):
                bt = _bout(base + s, a, b, rounds=3, round_seconds=180)
                played[a] += 1
                played[b] += 1
                w = _winner(bt)
                if w:
                    wins[bt.fighters[0].profile if w == "A" else bt.fighters[1].profile] += 1
    return {n: (wins[n], played[n]) for n in names}


def check_style_viability(seeds: int = 8) -> list:
    """Rule 21: every major style keeps a legitimate route to victory, and no
    style is a dominant extreme. Lopsided is a finding; zero and total are gate
    failures, and this reports which."""
    names = policy.available_profiles()
    wins = {n: 0 for n in names}
    played = {n: 0 for n in names}
    move_landed = {}
    errs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for s in range(seeds):
                # Canonical bout length, not a short one. This check ran at two
                # ninety-second rounds until 2026-08-03 and passed while the
                # showman style won none of twenty bouts at three-by-three -
                # a viability check that only holds at a length nobody fights at
                # is measuring the harness, not the game.
                bt = _bout(41000 + s, a, b, rounds=3, round_seconds=180)
                played[a] += 1
                played[b] += 1
                w = _winner(bt)
                if w:
                    wins[bt.fighters[0].profile if w == "A" else bt.fighters[1].profile] += 1
                for ev in bt.log:
                    if ev["type"] == "punch_outcome" and "region" in ev.get("payload", {}):
                        m = ev["payload"]["move"]
                        move_landed[m] = move_landed.get(m, 0) + 1
    for n in names:
        if played[n] and wins[n] == 0:
            errs.append(f"style '{n}' never won in {played[n]} bouts - absent counterplay is a "
                        f"gate failure under Rule 21, not a tuning note")
        if played[n] and wins[n] == played[n]:
            errs.append(f"style '{n}' won every one of {played[n]} bouts - dominant extreme")
    # Dominant loop: one move carrying an implausible share of all landed offence.
    total = sum(move_landed.values())
    if total:
        top, n_top = max(move_landed.items(), key=lambda kv: kv[1])
        if n_top / total > 0.6:
            errs.append(f"dominant loop: '{top}' accounts for {n_top / total:.0%} of all landed "
                        f"offence across the sweep")
        if len(move_landed) < 4:
            errs.append(f"only {len(move_landed)} distinct moves ever landed - the sweep is too "
                        f"narrow to detect a dominant loop at all")
    else:
        errs.append("no offence landed in the entire sweep - the check is vacuous")
    return errs


# ---- 11. the repetition abuse list -----------------------------------------
def check_repetition_abuse_list() -> list:
    """Rule 4's named abuses, each played as hard as a policy can play it.

    Two assertions per abuse, and the second is the one that matters: the abuse
    must not dominate, AND it must never have been forbidden. A spammer stopped
    by a rule rather than beaten by a fighter fails this suite exactly as loudly
    as one that wins.
    """
    from . import exploits
    errs = []
    baselines = ("technician", "counterpuncher", "rusher")
    for xid in exploits.EXPLOITS:
        abuse_wins = 0
        bouts = 0
        acted = 0
        for base in baselines:
            for s in range(4):
                bt = _bout(52000 + s, base, xid, rounds=2, round_seconds=90)
                bouts += 1
                if _winner(bt) == "B":
                    abuse_wins += 1
                abuser = bt.fighters[1]
                acted += abuser.thrown + abuser.retreats + abuser.clinch_entries
        if abuse_wins == bouts:
            errs.append(f"abuse '{xid}' won every one of {bouts} bouts - it is not an abuse, it is "
                        f"the optimal strategy")
        if xid != "_x_passive_blocker" and acted == 0:
            errs.append(f"abuse '{xid}' never acted at all - it was prohibited rather than "
                        f"punished, which Rule 4 explicitly forbids")

    # Crowd farming must be answered by novelty, not by a lockout. Compared on
    # CUMULATIVE earnings, not the residual bar: once full-bar spending exists,
    # the bar at the final bell is whatever is left after ultimates, and an
    # end-of-bout comparison of residues measures spending schedules rather
    # than income. This check briefly failed for exactly that reason.
    farm = _bout(52100, "technician", "_x_meter_farmer", rounds=2, round_seconds=90)
    farmer, varied = farm.fighters[1], farm.fighters[0]
    earned = {f.name: 0.0 for f in farm.fighters}
    for e in farm.log:
        if e["type"] == "crowd_gain":
            earned[e["actor"]] += e["payload"]["amount"]
    if earned[farmer.name] > earned[varied.name]:
        errs.append(f"the meter farmer out-earned a varied fighter on cumulative crowd "
                    f"({earned[farmer.name]:.1f} vs {earned[varied.name]:.1f}) - novelty decay "
                    f"is not answering low-risk farming")
    gains = [e for e in farm.log if e["type"] == "crowd_gain" and e["actor"] == farmer.name]
    if gains and all(g["payload"]["amount"] <= 0 for g in gains):
        errs.append("the farmer's crowd gain was zeroed outright rather than decayed - Rule 4 "
                    "protects legitimate repetition")

    # Clinch abuse must be recognised observably, by the referee.
    cl = _bout(52200, "rusher", "_x_clincher", rounds=2, round_seconds=90)
    warns = [e for e in cl.log if e["type"] == "referee_warning"
             and e.get("payload", {}).get("reason") == "clinch_abuse"]
    if cl.fighters[1].clinch_entries >= 6 and not warns:
        errs.append("repeated clinching drew no referee warning - clinch abuse must be recognised "
                    "through officiating rather than silently ignored")

    # Excessive running must lose on evidence rather than be blocked.
    run = _bout(52300, "rusher", "_x_runner", rounds=2, round_seconds=90)
    runner = run.fighters[1]
    if runner.retreats == 0:
        errs.append("the runner never retreated - running was prevented rather than made "
                    "unprofitable")
    if runner.effective_force > run.fighters[0].effective_force:
        errs.append("empty avoidance out-scored a pressure fighter on effective offence - Rule 21's "
                    "Long Drain condition says patience must be earned, not free")

    # Passive blocking must not be an indefinitely safe state.
    pas = _bout(52400, "power_threat", "_x_passive_blocker", rounds=2, round_seconds=90)
    blocker = pas.fighters[1]
    if blocker.blocked_taken == 0 and pas.fighters[0].landed == 0:
        errs.append("the passive blocker was never even pressured - the check is vacuous")
    if _winner(pas) == "B":
        errs.append("pure passivity won the bout - blocking has become an indefinitely safe state, "
                    "which Rule 4 prohibits")
    return errs


ALL_CHECKS = [
    ("score_access_denial", check_score_access_denial),
    ("accelerated_clock_synchronization", check_accelerated_clock),
    ("style_viability_and_dominant_loops", check_style_viability),
    ("repetition_abuse_list", check_repetition_abuse_list),
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
