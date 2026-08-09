# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 15:38 UTC | START ]
"""Validator for data/attribute_effects.json - how attributes reach the fight.

The file exists because attribute_families.json declared twenty-four attributes in
Phase 0, fighter fixtures carried them, a budget validator policed them, and the
reference bout read none of them. This validator's job is to stop that recurring in the
one place it could: an attribute that is declared, scaled by nothing, and therefore
still decorative.

Three laws, each of which has already been violated somewhere in this project:

  Rule 10 - a zeroed attribute multiplies by exactly one. Without it an empty fighter
      card would not fight the baseline model, and no difference between two cards
      would be attributable to the cards.
  Rule 18 - no attribute is inert. Every attribute is either given an effect or named
      in `not_yet_expressed`; a degenerate multiplier band counts as inert.
  Rule 11 - extremes stay playable from both sides. No multiplier reaches zero, so a
      minimum attribute never makes an outcome impossible, and no band is wide enough
      for a maximum attribute to decide an outcome by itself.
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from pathlib import Path

from . import schema_check

REPO = Path(__file__).resolve().parents[2]


def load() -> dict:
    return json.loads((REPO / "data" / "attribute_effects.json").read_text(encoding="utf-8"))


def _families() -> list:
    fam = json.loads((REPO / "data" / "attribute_families.json").read_text(encoding="utf-8"))
    return [a for f in fam["families"].values() for a in f["attributes"]]


def check_schema(doc: dict) -> list:
    return schema_check.validate(doc, "attribute_effects.schema.json")


def check_curve(doc: dict) -> list:
    c = doc["curve"]
    errs = []
    if c["centre_multiplier"] != 1.0:
        errs.append("Rule 10: a zeroed attribute must multiply by exactly one, or an empty "
                    "fighter card does not fight the baseline model")
    if c["domain"] != [-100, 100]:
        errs.append(f"curve domain {c['domain']} does not match the attribute range declared in "
                    f"attribute_families.json")
    fam = json.loads((REPO / "data" / "attribute_families.json").read_text(encoding="utf-8"))
    rng = fam["range"]
    if [rng["min"], rng["max"]] != c["domain"] or rng["center"] != 0:
        errs.append("the curve domain and attribute_families.range disagree - two scales by "
                    "another name")
    return errs


def check_effects(doc: dict) -> list:
    """Rule 18: every attribute either acts or is named as not acting."""
    errs = []
    declared = set(_families())
    scaled = {}
    for e in doc["effects"]:
        if e["attribute"] not in declared:
            errs.append(f"effect scales '{e['attribute']}', which attribute_families.json does "
                        f"not declare")
        scaled.setdefault(e["attribute"], []).append(e["scales"])
        lo, hi = e["multiplier_at_minus_100"], e["multiplier_at_plus_100"]
        if lo == hi:
            errs.append(f"'{e['attribute']}' has a flat multiplier band - it is declared, scaled "
                        f"by nothing, and therefore still decorative")
        want_up = e["direction"] == "higher_is_stronger"
        # 'higher_is_weaker' means the multiplier falls as the attribute rises: fast
        # hands SHORTEN startup, so its band runs downward while still being a buff.
        if want_up and hi < lo:
            errs.append(f"'{e['attribute']}' is declared higher_is_stronger but its multiplier "
                        f"falls as the attribute rises")
        if not want_up and hi > lo:
            errs.append(f"'{e['attribute']}' is declared higher_is_weaker but its multiplier "
                        f"rises as the attribute rises")
    for a in sorted(scaled):
        if len(scaled[a]) > 1:
            errs.append(f"'{a}' scales {scaled[a]} - one attribute reaching several mechanics "
                        f"makes its influence impossible to read off a single row")
    named = set(doc.get("unexpressed_attributes", {}).get("not_yet_expressed", []))
    for a in sorted(declared - set(scaled) - named):
        errs.append(f"attribute '{a}' is declared by a family, has no effect, and is not named as "
                    f"not_yet_expressed - the silent third state")
    for a in sorted(named & set(scaled)):
        errs.append(f"attribute '{a}' is named not_yet_expressed while an effect scales it - the "
                    f"registry is wrong in the flattering direction")
    for a in sorted(named - declared):
        errs.append(f"'{a}' is named not_yet_expressed but no family declares it - a dead entry")
    return errs


def check_bounds(doc: dict) -> list:
    """Rule 11 from both sides: a maximum attribute may not make an outcome certain and
    a minimum one may not make it impossible."""
    b = doc["bounds"]
    errs = []
    for e in doc["effects"]:
        lo, hi = sorted((e["multiplier_at_minus_100"], e["multiplier_at_plus_100"]))
        if lo < b["min_multiplier"]:
            errs.append(f"'{e['attribute']}' bottoms out at {lo}, below the floor "
                        f"{b['min_multiplier']} - a minimum attribute would make "
                        f"'{e['scales']}' effectively impossible (Rule 11)")
        if hi > b["max_multiplier"]:
            errs.append(f"'{e['attribute']}' tops out at {hi}, above the ceiling "
                        f"{b['max_multiplier']} - a maximum attribute would decide "
                        f"'{e['scales']}' by itself (Rule 11)")
        width = hi - lo
        if width > b["max_band_width"]:
            errs.append(f"'{e['attribute']}' spans {width:.2f}, wider than the permitted "
                        f"{b['max_band_width']} - the attribute would dominate the term it scales")
        if width < b["min_band_width"]:
            errs.append(f"'{e['attribute']}' spans only {width:.2f}, under the minimum "
                        f"{b['min_band_width']} - too narrow to be worth spending points on, "
                        f"which is inert by another name")
    if b["min_multiplier"] <= 0:
        errs.append("the multiplier floor is at or below zero - some attribute value would "
                    "switch a mechanic off entirely")
    return errs


def check_chin_is_not_immunity(doc: dict) -> list:
    """Rule 14, cross-checked against the file that states it.

    condition_model.chin.max_resistance_confers_immunity is a const false enforced by
    the condition validator. That is a claim about DATA; this is the claim about
    ARITHMETIC, and they can drift apart. A chin multiplier without a ceiling would
    make +100 Chin unfalsifiable no matter what the other file promises.
    """
    errs = []
    chin = [e for e in doc["effects"] if e["attribute"] == "chin"]
    if not chin:
        named = doc.get("unexpressed_attributes", {}).get("not_yet_expressed", [])
        if "chin" not in named:
            errs.append("chin has no effect and is not named as unexpressed, while Rule 14 and "
                        "condition_model.chin both describe what it does")
        return errs
    e = chin[0]
    if e["scales"] != "knockdown_pressure_threshold":
        errs.append(f"chin scales '{e['scales']}'; Rule 14 and condition_model.chin describe it "
                    f"as knockdown resistance")
    cond = json.loads((REPO / "data" / "condition_model.json").read_text(encoding="utf-8"))
    if cond["chin"]["max_resistance_confers_immunity"]:
        errs.append("condition_model says maximum Chin confers immunity; this file cannot make "
                    "that safe")
    if e["multiplier_at_plus_100"] > doc["bounds"]["max_multiplier"]:
        errs.append("the Chin ceiling exceeds the global bound - +100 Chin would approach "
                    "immunity, which Rule 14 forbids in the words 'maximum authored resistance, "
                    "never absolute immunity'")
    return errs


def check_prohibitions(doc: dict) -> list:
    blob = " ".join(doc["prohibitions"]).lower()
    needed = ("not declared in this file", "certain", "impossible", "declared multiplier")
    return [f"missing required prohibition covering '{p}'" for p in needed if p not in blob]


def check_invariants(doc: dict) -> list:
    present = {i["id"] for i in doc["invariants"]}
    required = ("zero_is_the_baseline", "no_attribute_is_inert", "extremes_stay_playable")
    return [f"missing required invariant '{r}'" for r in required if r not in present]


ALL_CHECKS = [
    ("schema", check_schema),
    ("curve_rule10", check_curve),
    ("effects_rule18", check_effects),
    ("bounds_rule11", check_bounds),
    ("chin_is_not_immunity_rule14", check_chin_is_not_immunity),
    ("prohibitions", check_prohibitions),
    ("invariants_declared", check_invariants),
]


def run_all(doc: dict | None = None) -> list:
    doc = load() if doc is None else doc
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(doc))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 15:38 UTC | END ]
