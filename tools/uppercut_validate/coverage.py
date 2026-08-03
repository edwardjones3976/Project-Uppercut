# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 11:34 UTC | START ]
"""The declared-but-inert check: canon that nothing executes.

Three separate passes over this repository each found the same defect by
accident, and each time it was the largest thing in the pass:

  2026-08-03 (exploit hunt) - punch_model.repetition_economy declared four
      mechanisms with a fires_on, an observable_as and a target apiece, gave
      none of them a number, and so ran entirely inert. The whole of Rule 4's
      answer to repetition existed as four sentences.
  2026-08-03 (balance pass) - crowd recipients, counter windows, the telegraph
      and every region below the neck: four more, each of them a mechanism some
      losing style's canon win condition names.
  2026-08-03 (this pass)  - posture hold cost and offense pricing, the stamina
      gate's degradation, chaining, the fighter_action availability table, and
      a units error in the stamina economy that only surfaced once a policy
      stopped masking it.

Finding the same class three times by luck is not a process. This is the
process: every mechanical key in data/ must be READ by the reference simulator,
or be named in that file's `not_yet_expressed` registry. Prose, provenance and
schema scaffolding are exempt by name. Nothing else is.

The registry is the point. It is not a suppression list - it is the difference
between "we decided not to build this yet" and "we thought we built this".
"""
from __future__ import annotations
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data"
SIM = REPO / "tools" / "uppercut_sim"

# Keys that carry meaning to a reader rather than to the simulation.
EXEMPT_EXACT = {
    "$comment", "$id", "$schema", "schema_version", "tuning_status", "notes",
    "note", "description", "definition", "contribution", "agent", "model",
    "start", "end", "procedure", "id", "label", "status", "display", "rule",
    "statement", "enforced_by", "question", "expresses", "phase", "trigger_detail",
    "invariants", "prohibitions", "prohibited_mechanisms", "fires_on",
    "observable_as", "legitimate_repetition", "hit_reaction",
    "counter_vulnerability", "positional_consequence",
    # The registry's own scaffolding. Exempting it is not a loophole - the
    # registry is a statement ABOUT execution, so requiring it to be executed
    # would be a category error, and check_registry_is_honest is what keeps it
    # from becoming a place to hide things.
    "reference_model_coverage", "not_yet_expressed", "unexpressed_keys", "reason",
    # attribute_effects carries a second registry answering a different question -
    # which ATTRIBUTES have no effect, as opposed to which JSON keys go unread. Its
    # own validator enforces it. Two registries under one name is what the
    # registry_is_honest pass caught the moment that file entered scope.
    "unexpressed_attributes",
}
EXEMPT_SUFFIX = ("_note", "_notes", "_comment", "_rationale", "_definition",
                 "_description", "_derivation", "_source_note")


def _mechanical(key: str) -> bool:
    if key in EXEMPT_EXACT or key.startswith("$"):
        return False
    return not key.endswith(EXEMPT_SUFFIX)


def _keys(obj) -> set:
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if _mechanical(k):
                out.add(k)
            out |= _keys(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= _keys(v)
    return out


def _sim_source() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in SIM.glob("*.py"))


# The files the reference simulator is supposed to EXECUTE. Everything else in
# data/ is either presentation (animation, camera), a meta system the bout does
# not contain (advice, attribute budget, mode configuration), or a contract
# checked structurally elsewhere. Scoping is not an exemption: a file outside
# this set makes no claim that the bout runs it, and a file inside it claims
# exactly that. Moving a file out of this list is a design decision that should
# be argued for, which is why the list is short, explicit, and here rather than
# inferred.
SIMULATED = {
    "punch_model.json",
    "collision_model.json",
    "condition_model.json",
    "guard_evasion_model.json",
    "crowd_model.json",
    "movement_model.json",
    "combat_states.json",
    "ability_model.json",
    # Added 2026-08-03 with the attribute work. The next-steps review found that
    # attribute_families declared twenty-four attributes in Phase 0 and the bout read
    # none of them - the same inert class this checker exists for, sitting one file
    # outside its scope because the original list stopped at combat models. The scope
    # line was the defect, not an oversight in the data.
    "attribute_effects.json",
}


def load() -> dict:
    return {p.name: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(DATA.glob("*.json")) if p.name in SIMULATED}


def unexpressed_registry(doc: dict) -> set:
    """The file's coverage registry, and only that.

    Read from `reference_model_coverage.not_yet_expressed` specifically rather
    than by walking for the name anywhere: condition_model.impairment carries
    its own `not_yet_expressed` list of impairment TARGETS (accuracy, tracking,
    composure), which are capabilities rather than JSON keys. Merging the two
    made the coverage registry silently claim credit for a list that answers a
    different question - caught by check_registry_is_honest on its first run,
    which is the argument for having written that check.
    """
    block = doc.get("reference_model_coverage") or {}
    return set(block.get("not_yet_expressed", []))


def _walk_for(obj, key):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key and isinstance(v, list):
                yield v
            else:
                yield from _walk_for(v, key)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_for(v, key)


def check_no_inert_canon(docs: dict | None = None) -> list:
    """Every mechanical key is read by the simulator or named as unexpressed."""
    docs = load() if docs is None else docs
    blob = _sim_source()
    errs = []
    for name, doc in docs.items():
        named = unexpressed_registry(doc)
        for key in sorted(_keys(doc)):
            if key in named:
                continue
            if re.search(r'["\']' + re.escape(key) + r'["\']', blob):
                continue
            errs.append(
                f"{name}: '{key}' is declared and nothing in the reference simulator reads it. "
                f"Either execute it, or add it to a `not_yet_expressed` list in that file so the "
                f"gap is a decision on the record rather than an assumption nobody checked.")
    return errs


def check_registry_is_honest(docs: dict | None = None) -> list:
    """The escape hatch may not be used as a suppression list.

    Two ways it goes wrong, and both are worse than the disease: naming a key
    unexpressed while the simulator does read it (the registry is then lying in
    the reassuring direction), and naming a key the file does not declare at all
    (dead entries that make the list look longer than the debt).
    """
    docs = load() if docs is None else docs
    blob = _sim_source()
    errs = []
    for name, doc in docs.items():
        declared = _keys(doc)
        for key in sorted(unexpressed_registry(doc)):
            if re.search(r'["\']' + re.escape(key) + r'["\']', blob):
                errs.append(f"{name}: '{key}' is listed as not_yet_expressed but the simulator "
                            f"does read it - the registry is wrong in the flattering direction")
            elif key not in declared and key not in _EXPECTED_ABSTRACT:
                errs.append(f"{name}: '{key}' is listed as not_yet_expressed but the file never "
                            f"declares it - a dead entry inflates the list past the real debt")
    return errs


# Impairment targets name capabilities rather than keys, so they are legitimately
# absent from the declaring file's own key set.
_EXPECTED_ABSTRACT = {"accuracy", "tracking", "composure_state", "balance", "chin_state",
                      "stamina", "guard_integrity"}


def check_rates_are_per_tick(docs: dict | None = None) -> list:
    """A per-tick rate that drains or fills its own pool many times per round is
    a units error, not a tuning choice.

    This is the exact shape of the 2026-08-03 stamina defect: regeneration was
    authored at 0.09 per tick, which is 972 stamina per 180-second round against
    a pool of 100. It survived two steps because a CPU policy refused to throw
    below the exhausted threshold, so the stamina economy never bound anything
    and its numbers were never under test.
    """
    docs = load() if docs is None else docs
    cond = docs["condition_model.json"]
    round_ticks = 180 * 60
    errs = []
    pool = cond["stamina"]["max"]
    for k, v in cond["stamina"].items():
        if k.startswith("regen_per_tick") and v * round_ticks > pool:
            errs.append(f"condition_model: {k}={v} regenerates {v*round_ticks:.0f} over a "
                        f"three-minute round against a pool of {pool} - the pool refills "
                        f"{v*round_ticks/pool:.1f} times per round, which is a per-second rate "
                        f"wearing a per-tick name")
    guard = docs["guard_evasion_model.json"]
    for p in guard["postures"]:
        cost = p["stamina_per_tick"] * round_ticks
        if cost > pool:
            errs.append(f"guard_evasion_model: posture '{p['id']}' costs {cost:.0f} stamina per "
                        f"round to hold against a pool of {pool} - holding a guard cannot cost "
                        f"more than a fighter has")
    bar = docs["crowd_model.json"]["bar"]
    drain = bar["decay_per_tick_idle"] * round_ticks
    if drain > bar["max"]:
        errs.append(f"crowd_model: idle decay empties {drain:.0f} of a {bar['max']} bar per "
                    f"round - the bar would evaporate between exchanges")
    return errs


ALL_CHECKS = [
    ("no_inert_canon", check_no_inert_canon),
    ("registry_is_honest", check_registry_is_honest),
    ("rates_are_per_tick", check_rates_are_per_tick),
]


def run_all(docs: dict | None = None) -> list:
    docs = load() if docs is None else docs
    out = []
    for name, fn in ALL_CHECKS:
        out.extend(f"{name}: {e}" for e in fn(docs))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 11:34 UTC | END ]
