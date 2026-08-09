# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""Schema validation helpers with a local $ref resolver (no network access)."""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

REPO = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO / "schemas"


def registry() -> Registry:
    reg = Registry()
    for f in sorted(SCHEMA_DIR.glob("*.json")):
        doc = json.loads(f.read_text())
        if "$id" in doc:
            reg = reg.with_resource(doc["$id"], Resource.from_contents(doc))
    return reg


def validator_for(schema_name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMA_DIR / schema_name).read_text())
    return Draft202012Validator(schema, registry=registry())


def validate(instance: dict, schema_name: str) -> list:
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
            for e in validator_for(schema_name).iter_errors(instance)]


def check_crew_rule(assignment: dict) -> list:
    """Rule 8 crew-size law: 4/6 rounds -> 1; 8/10 -> 2; 12 -> 3; championship always 3."""
    rounds = assignment["scheduled_rounds"]
    champ = assignment["championship"]
    expected = 3 if champ else {4: 1, 6: 1, 8: 2, 10: 2, 12: 3}[rounds]
    if assignment["commentator_count"] != expected:
        return [f"Rule 8: {rounds}-round{' championship' if champ else ''} fight requires "
                f"{expected} commentator(s), found {assignment['commentator_count']}"]
    return []


def check_contact_ordering(contact_doc: dict) -> list:
    """Rule 13: blocked < dodged < whiffed commitment consequence."""
    tiers = {c["key"]: c["commitment_tier"] for c in contact_doc["classes"]}
    if not (tiers["blocked"] < tiers["dodged"] < tiers["whiffed"]):
        return ["Rule 13: commitment consequence must strictly increase blocked -> dodged -> whiffed"]
    return []


def check_condition_regions(doc: dict) -> list:
    """Rule 14: the required condition distinctions must all be present."""
    required = {"head", "jaw_chin", "eye_left", "eye_right", "torso_upper", "torso_lower",
                "arm_left", "arm_right", "stamina", "balance", "guard_integrity",
                "composure_state", "chin_state", "durability_state", "recovery_state"}
    present = {r["key"] for r in doc["regions"]}
    missing = required - present
    return [f"Rule 14: missing required condition region(s): {sorted(missing)}"] if missing else []
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
