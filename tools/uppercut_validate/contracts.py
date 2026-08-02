# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:52 UTC | START ]
"""Checkable forms of Rules 4, 5, 6, 12 and 16.

Each function turns a rule that is normally enforced by code review into one that
fails a test. Nothing here simulates anything; these are contract checks over data.
"""
from __future__ import annotations
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((REPO / rel).read_text())


# ---------------------------------------------------------------- Rule 12 Crowd
def check_crowd_event(event: dict, contract: dict | None = None) -> list:
    """Rule 12: the Crowd rewards expressive AND effective boxing, never low-risk farming."""
    contract = contract or _load("data/crowd_contract.json")
    out = []
    if event["earned_by"] not in contract["rewardable_behaviour"]:
        out.append(f"Rule 12: '{event['earned_by']}' is not a rewardable Crowd behaviour")
    if event["delta"] > 0 and not event["risk_taken"]:
        out.append("Rule 12: positive Crowd gain without risk is low-risk meter farming")
    if event["delta"] > 0 and not event.get("observed_evidence"):
        out.append("Rule 12: Crowd gain must cite the observable events that earned it")
    return out


def check_full_crowd_spend(spend: dict, contract: dict | None = None) -> list:
    """Rule 12: one completed bar activates the Ultimate OR the Full-Crowd Trait, never both."""
    contract = contract or _load("data/crowd_contract.json")
    used = [k for k in contract["full_bar"]["choice"] if spend.get(k)]
    if len(used) > 1:
        return ["Rule 12: one completed Crowd Bar cannot activate both the Ultimate and the "
                "Full-Crowd Trait"]
    return []


# ------------------------------------------------------------- Rule 5 mode config
def check_mode_configuration(mode: dict, contract: dict | None = None) -> list:
    """Rule 5: a mode is a declared configuration over one combat system, never a second engine."""
    contract = contract or _load("data/mode_configurations.json")
    permitted = set(contract["permitted_configuration_surfaces"])
    prohibited = set(contract["prohibited_configuration_surfaces"])
    out = []
    for surface in mode.get("configures", []):
        if surface in prohibited:
            out.append(f"Rule 5: mode '{mode['id']}' may not configure '{surface}' — "
                       f"that would be a separate combat engine or a hidden player-tier rule")
        elif surface not in permitted:
            out.append(f"Rule 5: mode '{mode['id']}' declares unknown surface '{surface}'")
    return out


# ------------------------------------------------------------------ Rule 6 advice
def check_advice_award(award: dict, contract: dict | None = None) -> list:
    """Rule 6: small, bounded, non-stackable, farming-resistant, never score-driven."""
    contract = contract or _load("data/advice_contract.json")
    out = []
    if award.get("benefit_pct", 0) > contract["max_direct_combat_benefit_per_round_pct"]:
        out.append(f"Rule 6: direct combat benefit {award['benefit_pct']}% exceeds the "
                   f"{contract['max_direct_combat_benefit_per_round_pct']}% per-round ceiling")
    if len(award.get("sources", [])) > 1 and not contract["stackable"]:
        out.append(f"Rule 6: advice bonuses are non-stackable; {award['sources']} awarded together")
    for s in award.get("sources", []):
        if s not in contract["reliability_order"]:
            out.append(f"Rule 6: '{s}' is not a recognised advice source")
    if award.get("used_official_score"):
        out.append("Rule 3 / Rule 6: advice may never use official-score information")
    return out


# --------------------------------------------------------------- Rule 4 anti-spam
def check_spam_ruling(ruling: dict, contract: dict | None = None) -> list:
    """Rule 4: repetition is punished by observable boxing logic, never by a hidden decision."""
    contract = contract or _load("data/anti_spam_contract.json")
    out = []
    mech = ruling.get("mechanism")
    if mech in contract["prohibited_punishment_mechanisms"]:
        out.append(f"Rule 4: '{mech}' is a prohibited punishment mechanism; a predictable action "
                   f"becomes punishable through observable boxing logic, not a secret rule")
    elif mech not in contract["permitted_punishment_mechanisms"]:
        out.append(f"Rule 4: unknown punishment mechanism '{mech}'")
    if ruling.get("applies_to") not in ("both", None):
        out.append("Rule 4: the same recognition and consequence rules apply to human and CPU fighters")
    return out


# ------------------------------------------------------------------ Rule 16 referee
REFEREE_PROHIBITIONS = {"punch_damage", "stamina", "collision_classification", "crowd_gain",
                        "fighter_attributes", "input_responsiveness", "judging_criteria",
                        "official_scores"}


def check_referee_profile(profile: dict) -> list:
    """Rule 16: universal minimums bind every official, including the comic-relief one."""
    out = []
    missing = REFEREE_PROHIBITIONS - set(profile.get("prohibitions_acknowledged", []))
    if missing:
        out.append(f"Rule 16: profile does not acknowledge prohibitions {sorted(missing)}")
    for k, v in profile.get("universal_minimums", {}).items():
        if v is not True:
            out.append(f"Rule 16: universal minimum '{k}' must hold for every official")
    if not profile.get("disclosed_before_match"):
        out.append("Rule 16: every competitive referee must be disclosed before the fight")
    if profile.get("competitive") and not profile.get("ranked_eligible"):
        out.append("Rule 16: a competitive official should be Ranked-eligible")
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:52 UTC | END ]
