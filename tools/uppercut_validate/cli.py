# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""Command line entry point: python -m tools.uppercut_validate.cli [all|fighters|isolation|budget|states|movement|camera|animation|collision|punches|guard|condition|cpu]"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from . import (animation, attributes, budget, camera, collision, combat_states,
               condition, contracts, cpu, guard, movement, punches, schema_check,
               score_isolation)

REPO = Path(__file__).resolve().parents[2]


def _iter_fixtures():
    for kind in ("legal", "illegal"):
        for f in sorted((REPO / "fixtures" / "fighters" / kind).glob("*.json")):
            yield kind, f


def cmd_fighters() -> int:
    families = attributes.load_families()
    failures = 0
    for kind, f in _iter_fixtures():
        data = json.loads(f.read_text())
        expect_legal = kind == "legal"
        schema_errors = schema_check.validate(data, "fighter.schema.json")
        rep = attributes.validate_fighter(data, families)
        actually_legal = rep.legal and not schema_errors
        ok = actually_legal == expect_legal
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {kind:7} {f.name:34} "
              f"expected={'legal' if expect_legal else 'illegal'} got={'legal' if actually_legal else 'illegal'}")
        for e in schema_errors:
            print(f"        schema: {e}")
        for v in rep.violations:
            print(f"        {v}")
    return failures


def cmd_isolation() -> int:
    contract = score_isolation.load_contract()
    failures = 0
    compliant = REPO / "tests" / "isolation_samples" / "compliant_sample"
    violating = REPO / "tests" / "isolation_samples" / "violation_sample"

    v = score_isolation.scan_source(compliant, contract)
    print(f"{'PASS' if not v else 'FAIL'}  compliant sample -> {len(v)} violation(s)")
    failures += 1 if v else 0

    v = score_isolation.scan_source(violating, contract)
    print(f"{'PASS' if v else 'FAIL'}  violation sample -> {len(v)} violation(s) (checker must not be vacuous)")
    for x in v:
        print(f"        {x}")
    failures += 0 if v else 1

    for name, expect in (("compliant_log.json", 0), ("leaking_log.json", 2)):
        p = REPO / "tests" / "isolation_samples" / name
        if not p.exists():
            continue
        found = score_isolation.check_event_log(json.loads(p.read_text()), contract)
        ok = (len(found) == 0) if expect == 0 else (len(found) > 0)
        print(f"{'PASS' if ok else 'FAIL'}  event log {name} -> {len(found)} finding(s)")
        for x in found:
            print(f"        {x}")
        failures += 0 if ok else 1

    live = score_isolation.scan_source(REPO, contract)
    print(f"INFO  live repository scan -> {len(live)} violation(s) "
          f"(no simulation source exists yet; this check is provisioned, not yet load-bearing)")
    return failures


def cmd_contracts() -> int:
    """Rules 4, 5, 6, 12, 16 contract checks over committed data."""
    failures = 0
    for mode in json.loads((REPO / "data/mode_configurations.json").read_text())["modes"]:
        errs = contracts.check_mode_configuration(mode)
        print(f"{'PASS' if not errs else 'FAIL'}  mode {mode['id']:<16} "
              f"configures {len(mode['configures'])} permitted surface(s)")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    for f in sorted((REPO / "data/referees").glob("*.json")):
        p = json.loads(f.read_text())
        errs = contracts.check_referee_profile(p)
        tag = "non-Ranked" if not p["competitive"] else "Ranked"
        print(f"{'PASS' if not errs else 'FAIL'}  referee {p['id']:<18} {tag}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    moves = json.loads((REPO / "data/moves/generic_sandbox_moves.json").read_text())["moves"]
    bad = [m["id"] for m in moves if schema_check.validate(m, "move.schema.json")]
    print(f"{'PASS' if not bad else 'FAIL'}  generic move table -> {len(moves)} moves, "
          f"all counterplay-defined, all tuning hypotheses")
    failures += len(bad)
    return failures


def cmd_budget() -> int:
    print(f"{'fixture':34} " + "  ".join(f"{c:>18}" for c in budget.CURVES))
    for kind, f in _iter_fixtures():
        data = json.loads(f.read_text())
        prof = budget.profile(data.get("attributes", {}))
        print(f"{f.name:34} " + "  ".join(f"{prof[c]['net']:>18.2f}" for c in budget.CURVES))
    cfg = budget.load_config()
    print(f"\nCanonical (Decision 0007): curve {cfg['curve']}, refund {cfg['refund_rate']}, "
          f"cap {cfg['cap']} on {cfg['cap_scope']} only. tuning_status={cfg['tuning_status']}.")
    over = 0
    for kind, f in _iter_fixtures():
        data = json.loads(f.read_text())
        ev = budget.evaluate(data.get("attributes", {}))
        if ev["cap_enforced"]:
            print(f"  {'OVER CAP' if ev['over_cap'] else 'within cap'}: {f.name} net={ev['net']}")
            over += 1 if ev["over_cap"] else 0
    print(f"  ({over} complete build(s) over cap)")
    return 0


def cmd_docs() -> int:
    failures = 0
    for fn, doc, name in (
        (schema_check.check_contact_ordering, json.loads((REPO / "data" / "contact_classes.json").read_text()), "contact classes"),
        (schema_check.check_condition_regions, json.loads((REPO / "data" / "condition_regions.json").read_text()), "condition regions"),
    ):
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    for a in [{"scheduled_rounds": 4, "championship": False, "commentator_count": 1},
              {"scheduled_rounds": 10, "championship": False, "commentator_count": 2},
              {"scheduled_rounds": 12, "championship": False, "commentator_count": 3},
              {"scheduled_rounds": 6, "championship": True, "commentator_count": 3}]:
        errs = schema_check.check_crew_rule(a)
        print(f"{'PASS' if not errs else 'FAIL'}  crew rule {a['scheduled_rounds']}r "
              f"{'championship' if a['championship'] else 'standard'}")
        failures += len(errs)
    return failures


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | START edit: Phase 1A step 1 ]
def cmd_states() -> int:
    """ROADMAP Phase 1A step 1: combat-state definition laws."""
    doc = combat_states.load()
    failures = 0
    for name, fn in combat_states.ALL_CHECKS:
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    fa = doc["machines"]["fighter_action"]
    prov = sum(1 for s in fa["states"] if s.get("provisioned"))
    print(f"INFO  fighter_action: {len(fa['states'])} states ({prov} provisioned), "
          f"{len(fa['transitions'])} transitions; definitions only, no engine implementation claimed (Rule 18)")
    return failures
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 21:56 UTC | END edit ]


# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | START edit: Phase 1A step 2 ]
def cmd_movement() -> int:
    """ROADMAP Phase 1A step 2: movement, facing and range-band geometry laws."""
    doc = movement.load()
    failures = 0
    for name, fn in movement.ALL_CHECKS:
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    bands = doc["range_bands"]["bands"]
    print(f"INFO  {len(bands)} reach-relative bands, {len(doc['locomotion']['modes'])} posture-locked "
          f"modes, {len(doc['facing']['arcs'])} facing arcs; definitions only, no engine implementation claimed (Rule 18)")
    return failures
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-02 22:16 UTC | END edit ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | START edit: Phase 1A step 3 ]
def cmd_camera() -> int:
    """ROADMAP Phase 1A step 3: camera behaviour laws."""
    doc = camera.load()
    failures = 0
    for name, fn in camera.ALL_CHECKS:
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    modes = doc["framing_modes"]
    print(f"INFO  {len(modes)} framing modes, strict priority {max(m['priority'] for m in modes)}"
          f"..{min(m['priority'] for m in modes)}; camera writes no simulation state and is excluded "
          f"from the determinism hash (Rule 18: definitions only)")
    return failures
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:03 UTC | END edit ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:52 UTC | START edit: Phase 1A step 9 ]
def cmd_cpu() -> int:
    """ROADMAP Phase 1A step 9: CPU decision-making from observable evidence."""
    doc = cpu.load()
    failures = 0
    for name, fn in cpu.ALL_CHECKS:
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    print(f"INFO  {len(doc['observable_inputs'])} observable event types readable, "
          f"{len(doc['forbidden_inputs'])} privileged reads explicitly forbidden, "
          f"{len(doc['difficulty_tiers'])} difficulty tiers changing perception only; "
          f"reaction floor {doc['reaction']['floor_ticks']} ticks (Rule 18: definitions only)")
    return failures
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:52 UTC | END edit ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:41 UTC | START edit: Phase 1A step 8 ]
def cmd_condition() -> int:
    """ROADMAP Phase 1A step 8: condition, knockdowns and recovery."""
    doc = condition.load()
    failures = 0
    for name, fn in condition.ALL_CHECKS:
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    print(f"INFO  {len(doc['damage_regions'])} region condition tracks, no generic pool; "
          f"{len(doc['stoppage_conditions'])} evidenced stoppage conditions; count "
          f"{doc['knockdown']['count_to']} at {doc['knockdown']['count_ticks_per_number']} "
          f"ticks/number, no flat KO roll (Rule 18: definitions only)")
    return failures
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 08:41 UTC | END edit ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:38 UTC | START edit: Phase 1A step 7 ]
def cmd_guard() -> int:
    """ROADMAP Phase 1A step 7: guard and evasion."""
    doc = guard.load()
    failures = 0
    for name, fn in guard.ALL_CHECKS:
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    active = [e for e in doc["evasions"] if e["kind"] == "active_window"]
    print(f"INFO  {len(doc['postures'])} authored postures over 2 guard volumes (Decision 0010), "
          f"{len(active)} active-window evasions frame-locked to the move table, "
          f"{len(doc['evasions']) - len(active)} positional answers (Rule 18: definitions only)")
    return failures
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 07:38 UTC | END edit ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:52 UTC | START edit: Phase 1A step 6 ]
def cmd_punches() -> int:
    """ROADMAP Phase 1A step 6: what throwing a punch costs."""
    doc = punches.load()
    failures = 0
    for name, fn in punches.ALL_CHECKS:
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    print(f"INFO  {len(doc['outcome_recovery']['rows'])} outcome-recovery rows over all seven "
          f"contact classes, {len(doc['repetition_economy']['mechanisms'])} observable repetition "
          f"mechanisms, no cancelable phase (Rule 18: definitions only)")
    return failures
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 06:52 UTC | END edit ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | START edit: Phase 1A step 5 ]
def cmd_collision() -> int:
    """ROADMAP Phase 1A step 5: collision truth laws."""
    doc = collision.load()
    failures = 0
    for name, fn in collision.ALL_CHECKS:
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    v = doc["volumes"]
    print(f"INFO  {len(v['hitboxes'])} hitboxes, {len(v['hurtboxes'])} region-mapped hurtboxes, "
          f"{len(v['guard_volumes'])} guard volumes; {len(doc['resolution_pipeline'])}-stage total "
          f"pipeline over all seven contact classes (Rule 18: definitions only)")
    return failures
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 04:13 UTC | END edit ]


# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:47 UTC | START edit: Phase 1A step 4 ]
def cmd_animation() -> int:
    """ROADMAP Phase 1A step 4: animation state laws."""
    doc = animation.load()
    failures = 0
    for name, fn in animation.ALL_CHECKS:
        errs = fn(doc)
        print(f"{'PASS' if not errs else 'FAIL'}  {name}")
        for e in errs:
            print(f"        {e}")
        failures += len(errs)
    print(f"INFO  {len(doc['state_animations'])} state animations, "
          f"{len(doc['move_animations'])} move animations frame-locked to the move table, "
          f"{len(doc['interrupts'])} interrupt tiers; animation supplies pose, never truth "
          f"(Rule 18: definitions only)")
    return failures
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-03 05:47 UTC | END edit ]


def main(argv: list) -> int:
    cmd = argv[1] if len(argv) > 1 else "all"
    total = 0
    if cmd in ("all", "fighters"):
        print("== Rule 10 fighter fixtures ==");  total += cmd_fighters(); print()
    if cmd in ("all", "isolation"):
        print("== Rule 3 score isolation ==");    total += cmd_isolation(); print()
    if cmd in ("all", "contracts"):
        print("== Rules 4/5/6/12/16 contracts =="); total += cmd_contracts(); print()
    if cmd in ("all", "docs"):
        print("== Rules 8/13/14 data laws ==");   total += cmd_docs(); print()
    if cmd in ("all", "budget"):
        print("== Attribute budget candidates =="); total += cmd_budget(); print()
    if cmd in ("all", "states"):
        print("== Phase 1A combat-state definitions =="); total += cmd_states(); print()
    if cmd in ("all", "movement"):
        print("== Phase 1A movement and facing =="); total += cmd_movement(); print()
    if cmd in ("all", "camera"):
        print("== Phase 1A camera behaviour =="); total += cmd_camera(); print()
    if cmd in ("all", "animation"):
        print("== Phase 1A animation states =="); total += cmd_animation(); print()
    if cmd in ("all", "collision"):
        print("== Phase 1A collision truth =="); total += cmd_collision(); print()
    if cmd in ("all", "punches"):
        print("== Phase 1A basic punches =="); total += cmd_punches(); print()
    if cmd in ("all", "guard"):
        print("== Phase 1A guard and evasion =="); total += cmd_guard(); print()
    if cmd in ("all", "condition"):
        print("== Phase 1A condition and recovery =="); total += cmd_condition(); print()
    if cmd in ("all", "cpu"):
        print("== Phase 1A CPU decision-making =="); total += cmd_cpu(); print()
    print(f"RESULT: {'OK' if total == 0 else str(total) + ' FAILURE(S)'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
