# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""COMPLIANT sample: CPU policy reading observable evidence only (Rule 3).

Not simulation code. This exists so the score-isolation checker has a known-good
input and cannot pass merely because a real tree is empty.
"""


def choose_action(observable_events, fighter_state):
    guard_impacts = [e for e in observable_events if e["type"] == "guard_impact"]
    belief = "opponent guard structure weakening on the lead side"
    confidence = min(0.9, 0.15 * len(guard_impacts))
    return {
        "chosen_action": "body_hook_lead",
        "observed_evidence": [e["seq"] for e in guard_impacts],
        "estimate": {"belief": belief, "confidence": confidence,
                     "uncertainty_note": "inference from visible guard reactions only"},
        "alternatives_considered": ["reset_to_mid_range", "double_jab"],
        "forbidden_inputs_assertion": "no_official_score_no_opponent_input_no_privileged_state",
    }
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
