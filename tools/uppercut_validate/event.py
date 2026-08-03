# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:30 UTC | START ]
"""Event presentation validator.

docs/design/event_presentation_reference.md (OpenAI GPT-5.6, merged as a1c900e)
closes with a section titled "Validation requirements" listing eleven things
future validators should reject. This is those validators. A design document
that asks for enforcement and never gets it is how good intentions become
folklore, so the list is implemented rather than admired.

The single idea underneath all of it: presentation may not reach the fight.
Prestige, broadcast, crowd spectacle and venue dressing sit outside the
simulation's authority exactly as the camera does - and for the same reason the
camera is excluded from the determinism hash, they have to be provably outside
it rather than politely outside it.
"""
from __future__ import annotations
import json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]

REQUIRED_ROLES = ("referee", "judge", "timekeeper", "ringside_physician")

REQUIRED_PROHIBITIONS = ("without a referee", "prestige change combat", "read or alter official",
                         "privileged, hidden or future", "silently modify", "hidden fighter stat",
                         "obscure authoritative", "recorded provenance")

REQUIRED_INVARIANTS = (
    "officials_are_required", "prestige_never_reaches_the_fight",
    "broadcast_knows_nothing_privileged", "incidents_do_not_decide_fights",
    "ring_size_is_geometry", "championship_metadata_required",
    "commentary_crew_scales_and_stays_legal", "evidence_stays_visible",
    "licensed_content_has_provenance",
)


def load() -> dict:
    return json.loads((REPO / "data" / "event_model.json").read_text())


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "event_model.schema.json")


def check_officials(doc: dict) -> list:
    by = {o["role"]: o for o in doc["required_officials"]}
    errs = []
    for r in REQUIRED_ROLES:
        if r not in by:
            errs.append(f"an event without a {r} is not a sanctioned bout")
        elif not by[r]["authority"].strip():
            errs.append(f"official '{r}' declares no authority, so nobody knows what they decide")
    if "judge" in by and by["judge"]["min"] < 3:
        errs.append("three judges are the minimum for a scored bout")
    return errs


def check_authority(doc: dict) -> list:
    """The heart of it: presentation is loud and powerless."""
    a = doc["authority"]
    errs = []
    for k, why in (
        ("prestige_alters_combat", "Rule 12: a bigger event does not make a punch land harder"),
        ("prestige_alters_attributes", "Rule 12: prestige is stakes, never statistics"),
        ("crowd_presentation_reads_scores", "Rule 3: the crowd cannot see the cards"),
        ("crowd_presentation_alters_scores", "Rule 3: the crowd cannot touch the cards"),
        ("broadcast_has_privileged_knowledge", "Rule 3: broadcast sees what a spectator sees"),
        ("broadcast_has_future_knowledge", "Rule 3: nothing in presentation reads ahead of the tick"),
        ("dynamic_incidents_alter_outcomes",
         "a dynamic incident that changes a result is a rigged fight with good lighting"),
        ("presentation_may_obscure_evidence",
         "the gate's readability item: spectacle that hides the decisive moment has failed"),
    ):
        if a[k]:
            errs.append(why)
    return errs


def check_venue(doc: dict) -> list:
    v = doc["venue_requirements"]
    errs = []
    if not v["separated_fighter_routes"]:
        errs.append("separated fighter routes are a venue requirement")
    if not v["emergency_access_route"]:
        errs.append("an emergency access route is a venue requirement")
    if v["ring_size_as_hidden_stat_modifier"]:
        errs.append("ring size must be actual space read by footwork, not a hidden stat modifier - "
                    "the same category of error as a rubber-band multiplier")
    if not v["ring_size_is_real_space"]:
        errs.append("ring size must be real geometry")
    return errs


def check_event_classes(doc: dict) -> list:
    errs = []
    ids = [c["id"] for c in doc["event_classes"]]
    if len(set(ids)) != len(ids):
        errs.append("duplicate event class id")
    for c in doc["event_classes"]:
        if not 2 <= c["commentary_crew"] <= 3:
            errs.append(f"event class '{c['id']}' commentary crew {c['commentary_crew']} is outside "
                        f"the canonical bounds")
        if c["prestige"] >= 4 and c["commentary_crew"] < 3:
            errs.append(f"event class '{c['id']}' carries high prestige with a small crew - "
                        f"commentary must scale with fight importance")
    champs = [c for c in doc["event_classes"] if c["requires_championship_metadata"]]
    if not champs:
        errs.append("no event class requires championship metadata, so the requirement is inert")
    for c in champs:
        if c["prestige"] < 3:
            errs.append(f"'{c['id']}' demands championship metadata at low prestige")
    return errs


def check_evidence(doc: dict) -> list:
    must = set(doc["evidence_visibility"]["must_remain_visible"])
    errs = []
    for need in ("knockdown", "stoppage_reason", "contact_classification", "count"):
        if need not in must:
            errs.append(f"'{need}' must remain visible - the gate asks a spectator to understand "
                        f"decisive exchanges, and this is one of them")
    return errs


def check_provenance(doc: dict) -> list:
    need = {"celebrity_appearance", "sponsor_content", "licensed_music"}
    have = set(doc["provenance_required_for"])
    return [f"Rule 1: '{n}' must require recorded provenance before shipping"
            for n in sorted(need - have)]


def check_prohibitions(doc: dict) -> list:
    blob = " ".join(doc["prohibitions"]).lower()
    return [f"missing required prohibition covering '{p}'"
            for p in REQUIRED_PROHIBITIONS if p not in blob]


def check_invariants(doc: dict) -> list:
    present = {i["id"] for i in doc["invariants"]}
    return [f"missing required invariant '{r}'" for r in REQUIRED_INVARIANTS if r not in present]


ALL_CHECKS = [
    ("schema", check_schema),
    ("officials_rule16", check_officials),
    ("authority_rule3_rule12", check_authority),
    ("venue_rule12", check_venue),
    ("event_classes_rule17", check_event_classes),
    ("evidence_visibility_gate", check_evidence),
    ("provenance_rule1", check_provenance),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 10:30 UTC | END ]
