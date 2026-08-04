# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START ]
"""Rule 3 as a module boundary, checked on source (Decision 0012 slice item 1).

`tools/uppercut_sim/judge.py` holds the cards. These checks hold the line, in
both directions, as relations over the two source files rather than habits:

  1. judge_imports_nothing   - the Judge may import only __future__. A module
                               that cannot name Fighter, Bout, canon, policy or
                               random cannot read ring internals or the stream.
  2. judge_names_no_ring     - and it never references them anyway: no
                               forbidden identifier appears in its AST.
  3. witness_vocabulary      - every fact the engine shows the judge is a dict
                               literal with constant string keys drawn from
                               judge.FACT_KEYS, and a constant "type" from
                               judge.FACT_TYPES. Widening what the judge sees
                               is a visible, reviewable act.
  4. cards_read_in_decision  - sealed_cards() is called from exactly one place
                               in the engine: Bout.decision(). Nothing else
                               holds a card.
  5. judge_stays_private     - outside its module the judge object is touched
                               only through its public bells and the official
                               reading; it is never aliased or passed on.

Every check takes source text as input, so tests prove non-vacuity by feeding
synthetic violations - the same discipline as scan_source's violation_sample.
"""
from __future__ import annotations
import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

ALLOWED_IMPORTS = {"__future__"}
FORBIDDEN_IN_JUDGE = {
    "Fighter", "Bout", "canon", "policy", "random", "engine", "checks",
    "observe", "resolve", "stamina", "condition", "attrs", "posture", "rng",
}
JUDGE_PUBLIC = {"witness", "seal_round", "seal_final", "sealed_cards"}


def load() -> dict:
    return {
        "judge_source": (REPO / "tools/uppercut_sim/judge.py").read_text(encoding="utf-8"),
        "engine_source": (REPO / "tools/uppercut_sim/engine.py").read_text(encoding="utf-8"),
    }


def _fact_vocabulary() -> tuple:
    from ..uppercut_sim import judge as _judge
    return set(_judge.FACT_KEYS), set(_judge.FACT_TYPES)


def check_judge_imports(doc: dict) -> list:
    """Check 1: the import allowlist IS the firewall's strongest form."""
    errs = []
    tree = ast.parse(doc["judge_source"])
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in ALLOWED_IMPORTS:
                    errs.append(f"judge imports '{a.name}' - the Judge may import nothing")
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if node.level or mod not in ALLOWED_IMPORTS:
                errs.append(f"judge imports from '{'.' * node.level}{node.module}' - "
                            "the Judge may import nothing")
    return errs


def check_judge_names(doc: dict) -> list:
    """Check 2: no ring-state identifier appears anywhere in the judge's AST.
    Identifiers, not text - a docstring may say 'stamina', code may not."""
    errs = []
    tree = ast.parse(doc["judge_source"])
    for node in ast.walk(tree):
        name = None
        if isinstance(node, ast.Name):
            name = node.id
        elif isinstance(node, ast.Attribute):
            name = node.attr
        elif isinstance(node, ast.arg):
            name = node.arg
        if name in FORBIDDEN_IN_JUDGE:
            errs.append(f"judge references forbidden identifier '{name}'")
    return errs


def _witness_calls(tree: ast.AST):
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "witness"):
            yield node


def check_witness_vocabulary(doc: dict) -> list:
    """Check 3: facts are dict literals, keys and type from the vocabulary."""
    keys_ok, types_ok = _fact_vocabulary()
    errs = []
    tree = ast.parse(doc["engine_source"])
    count = 0
    for call in _witness_calls(tree):
        count += 1
        where = f"line {call.lineno}"
        if len(call.args) != 1 or call.keywords:
            errs.append(f"{where}: witness() takes exactly one positional fact")
            continue
        fact = call.args[0]
        if not isinstance(fact, ast.Dict):
            errs.append(f"{where}: the fact must be a dict literal, so its shape "
                        "is auditable at the call site")
            continue
        kv = {}
        for k, v in zip(fact.keys, fact.values):
            if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                errs.append(f"{where}: fact keys must be constant strings")
                continue
            kv[k.value] = v
        bad = set(kv) - keys_ok
        if bad:
            errs.append(f"{where}: fact key(s) {sorted(bad)} outside judge.FACT_KEYS")
        t = kv.get("type")
        if t is None:
            errs.append(f"{where}: fact carries no 'type'")
        elif not (isinstance(t, ast.Constant) and t.value in types_ok):
            errs.append(f"{where}: fact type must be a constant from judge.FACT_TYPES")
    if count == 0:
        errs.append("engine shows the judge nothing - the boundary checks would "
                    "pass vacuously")
    return errs


def check_sealed_reads(doc: dict) -> list:
    """Check 4: sealed_cards() is read in decision() and nowhere else."""
    errs = []
    tree = ast.parse(doc["engine_source"])
    reads = 0
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "sealed_cards"):
                reads += 1
                if fn.name != "decision":
                    errs.append(f"line {node.lineno}: sealed_cards() read inside "
                                f"'{fn.name}' - only decision() may hold the reading")
    if reads == 0:
        errs.append("nothing reads the sealed cards - the bout would have no verdict "
                    "and the check would pass vacuously")
    return errs


def check_judge_privacy(doc: dict) -> list:
    """Check 5: outside its module, the judge is its public surface and nothing
    else. No private reach-in, no aliasing, no passing it onward."""
    errs = []
    tree = ast.parse(doc["engine_source"])

    def is_judge(node) -> bool:
        return (isinstance(node, ast.Attribute) and node.attr == "_judge"
                and isinstance(node.value, ast.Name) and node.value.id == "self")

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and is_judge(node.value):
            if node.attr not in JUDGE_PUBLIC:
                errs.append(f"line {node.lineno}: engine touches judge attribute "
                            f"'{node.attr}' outside its public surface")
        elif isinstance(node, ast.Assign) and is_judge(node.value):
            errs.append(f"line {node.lineno}: the judge is aliased - the boundary "
                        "must stay a single named object")
        elif isinstance(node, ast.Call):
            for a in list(node.args) + [k.value for k in node.keywords]:
                if is_judge(a):
                    errs.append(f"line {node.lineno}: the judge is passed as an "
                                "argument - it does not travel")
    return errs


ALL_CHECKS = [
    ("the Judge imports nothing", check_judge_imports),
    ("the Judge names no ring state", check_judge_names),
    ("witnessed facts use the vocabulary", check_witness_vocabulary),
    ("sealed cards are read in decision() only", check_sealed_reads),
    ("the judge object stays private", check_judge_privacy),
]
# [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | END ]
