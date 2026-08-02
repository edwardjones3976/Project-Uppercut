# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""Command line entry point: python -m tools.uppercut_validate.cli [all|fighters|isolation|budget]"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from . import attributes, budget, contracts, schema_check, score_isolation

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
    print("\nNo cap is enforced. The canonical curve and cap are a Director decision "
          "(docs/phase0/attribute_budget_candidates.md).")
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
    print(f"RESULT: {'OK' if total == 0 else str(total) + ' FAILURE(S)'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
