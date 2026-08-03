# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:36 UTC | START ]
"""Stress-profile policies.

data/stress_profiles/*.json declare each instrument qualitatively - its win
condition, its risk condition, its counterplay and its readable signals. This
maps those statements onto numeric biases so the reference simulator can run
them. The mapping is a tuning hypothesis (Rule 18); the profiles themselves are
canon and are not edited here.

Every policy takes an Observation dict and nothing else. It has no reference to
the Bout, so it has no path to the sealed round cards - the Rule 3 firewall is a
property of the call signature rather than of anyone's restraint.
"""
from __future__ import annotations

from . import canon

# profile id -> (aggression, guard_preference, variety, risk_appetite)
# Derived from each profile's declared win_condition and risk_condition.
BIAS = {
    "rusher":         (0.80, "high_guard",   0.35, 0.80),
    "drainer":        (0.42, "tight_elbow",  0.55, 0.30),
    "technician":     (0.55, "high_guard",   0.85, 0.45),
    "counterpuncher": (0.35, "philly_shell", 0.60, 0.35),
    "showman":        (0.62, "low_lead",     0.90, 0.85),
    "power_threat":   (0.50, "cross_arm",    0.40, 0.70),
}

# How hard each profile hunts the counter window - the chance of throwing when
# the opponent is visibly inside their own commitment. Read straight off each
# profile's canon: the counterpuncher's entire win_condition is "exploiting
# blocked, dodged and whiffed recovery windows"; the drainer lists "counters";
# power_threat's counterplay row is "counters into the loading window"; the
# rusher's canon warns of overcommitment, so its own counter drive is modest.
COUNTER_DRIVE = {
    "counterpuncher": 0.90,
    "drainer":        0.65,
    "power_threat":   0.55,
    "technician":     0.45,
    "showman":        0.45,
    "rusher":         0.25,
}

# Round pacing (early multiplier -> late multiplier on aggression), linear over
# the bout. Only profiles whose canon states a pacing identity carry one: the
# drainer's win_condition is recovery, rhythm and "ring control that punishes
# waste" - conserve early, cash late against a body-worked, arm-heavy opponent.
PACING = {
    "drainer": (0.65, 1.55),
}

# Share of offence aimed downstairs. Bodywork is named in the drainer's and the
# rusher's canon win conditions; everyone else keeps the default mix.
BODY_SHARE = {
    "drainer": 0.50,
    "rusher":  0.40,
}
DEFAULT_BODY_SHARE = 0.25

POWER = ("cross_rear", "hook_rear", "uppercut_rear", "overhand_rear")
QUICK = ("jab_lead", "hook_lead", "uppercut_lead")
BODY = ("body_hook_lead", "body_straight_rear")


def bias_for(profile: str):
    if profile not in BIAS:
        raise KeyError(f"no policy mapping for stress profile '{profile}'")
    return BIAS[profile]


def posture_for(profile: str) -> str:
    from . import exploits
    if profile in exploits.POSTURES:
        return exploits.POSTURES[profile]
    return bias_for(profile)[1]


def decide(profile: str, obs: dict, rng) -> str | None:
    """Return an action id, or None to hold. Observable inputs only.

    Exploit policies are dispatched first so the exploit hunt can drive the same
    engine as the balance instruments - an abuse tested against a different
    simulator would prove nothing about this one."""
    from . import exploits
    if profile in exploits.EXPLOITS:
        return exploits.EXPLOITS[profile](obs, rng)
    aggression, _, variety, risk = bias_for(profile)
    punches = canon.punches()

    # Range discipline: close when out of range rather than throwing into air.
    # A profile that ignored this would fail the Rule 12 gate by whiffing forever.
    band = obs.get("band_key", "mid")
    if band in ("outside", "out_of_range"):
        return "step_in"
    if band == "clinch" and rng.random() < 0.6:
        return "step_out"
    # Ringcraft, one branch only. On the reference model's single axis there is
    # no ring to cut, so the pressure fighter gets no special behaviour here -
    # it closes because advance beats retreat, which is the mechanism, not a
    # bonus. What a backed-up fighter does have is the circle-off, and a boxer
    # with gas left takes it rather than staying pinned. Reads only where the
    # ropes are, so Rule 3 is untouched.
    if obs.get("own_back_to_ropes") and obs["own_stamina_fraction"] > 0.2 \
            and rng.random() < (1.0 - aggression) * 0.7:
        return "step_lateral"

    # Rule 4: a tired fighter throws less. This reads the fighter's OWN stamina,
    # which is not privileged information about anyone else.
    stamina = obs["own_stamina_fraction"]
    if stamina < 0.08:
        return None

    # The full-bar conversion. Every fighter has the mechanism (Rule 12); the
    # showman is simply built around how fast it refills the bar.
    if obs.get("own_crowd_fraction", 0.0) >= 1.0 \
            and any(punches[m]["range_band"] == band for m in punches):
        return "ultimate"

    # Round pacing, for the profiles whose canon declares one. Reads only the
    # fight card (round number and scheduled length), which the building knows.
    pace = 1.0
    if profile in PACING:
        early, late = PACING[profile]
        total = max(2, obs.get("total_rounds", 3))
        t = (max(1, obs.get("round", 1)) - 1) / (total - 1)
        pace = early + (late - early) * t

    # The counter window: the opponent is visibly inside their own commitment
    # - mid-punch, mid-step or mid-count, all observable events. Profiles hunt
    # it exactly as hard as their canon says they do. The counter pool is every
    # in-band punch that arrives fast enough to beat the window - not just the
    # jab, or every counter in the building is the same punch and the style
    # sweep grows a dominant loop (which is exactly what its first version did:
    # jab_lead at 63% of all landed offence).
    if obs.get("opponent_committed_ticks", 0) > 0 \
            and rng.random() < COUNTER_DRIVE.get(profile, 0.3):
        in_band = [m for m in punches.values() if m["range_band"] == band]
        if in_band:
            fastest = min(m["startup_frames"] for m in in_band)
            window_pool = [m["id"] for m in in_band
                           if m["startup_frames"] <= fastest + 4]
            if window_pool:
                return window_pool[rng.randrange(len(window_pool))]

    throw_chance = aggression * pace * (0.35 + 0.65 * stamina)
    if rng.random() > throw_chance:
        return None

    # Variety bias: a high-variety profile avoids repeating its last move, which
    # is also what keeps its crowd novelty multiplier alive.
    pool = list(punches)
    if obs["my_last_move"] and rng.random() < variety:
        pool = [m for m in pool if m != obs["my_last_move"]] or pool

    body_share = BODY_SHARE.get(profile, DEFAULT_BODY_SHARE)
    roll = rng.random()
    if roll < body_share:
        pref = [m for m in pool if m in BODY]
    elif roll < body_share + risk * 0.45:
        pref = [m for m in pool if m in POWER]
    else:
        pref = [m for m in pool if m in QUICK]
    pool = pref or pool
    # Only throw what this band actually permits (Rule 12).
    in_band = [m for m in pool if punches[m]["range_band"] == band]
    pool = in_band or [m for m in punches if punches[m]["range_band"] == band]
    if not pool:
        return "step_in"
    return pool[rng.randrange(len(pool))]


def available_profiles() -> list:
    """Canon profiles that this mapping covers - a profile with no mapping is a
    loud failure rather than a silent omission."""
    names = canon.stress_profile_names()
    missing = [n for n in names if n not in BIAS]
    if missing:
        raise KeyError(f"stress profiles with no policy mapping: {missing}")
    return names
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 09:36 UTC | END ]
