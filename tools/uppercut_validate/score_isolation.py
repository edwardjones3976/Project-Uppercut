# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""Score Isolation Principle checker (PROJECT_RULES.md Rule 3).

Satisfies the ROADMAP Phase 0 gate item "Scorecard access boundaries documented
and testable" by making the boundary executable in two directions:

  1. SOURCE  - no forbidden consumer may reference a sealed score symbol.
  2. EVIDENCE - in a recorded event log, official cards must be sealed, and no
     CPU decision may cite a sealed event as observed evidence.

Honesty note (Rule 18): no engine or simulation source exists yet, so check (1)
currently has nothing to police in a real tree. Its non-vacuity is proved by
tests/isolation_samples/violation_sample, which the checker must flag.
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
import re
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCANNABLE = {".py", ".cpp", ".h", ".hpp", ".cs", ".txt", ".md", ".json", ".yaml", ".yml"}


@dataclass
class Violation:
    kind: str
    where: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.kind}] {self.where}: {self.detail}"


def load_contract(path: Path | None = None) -> dict:
    path = path or REPO / "data" / "score_isolation_contract.json"
    return json.loads(path.read_text())


def scan_source(root: Path, contract: dict | None = None) -> list:
    """Flag any sealed-symbol reference inside a forbidden consumer path."""
    contract = contract or load_contract()
    idents = contract["sealed_symbols"]["identifiers"]
    pattern = re.compile(r"\b(" + "|".join(re.escape(i) for i in idents) + r")\b")
    out: list = []
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 22:00 UTC | F3: containment | START edit ]
    # The consumer paths are DATA, and data must not be able to point this
    # scanner outside the tree it was asked to police. A path that resolves
    # outside `root` ('..', an absolute path, a junction) is refused loudly,
    # not skipped: skipping would mean a forbidden consumer silently went
    # unscanned, which is fail-open.
    root_resolved = root.resolve()
    for consumer in contract["forbidden_consumers"]:
        for rel in consumer["paths"]:
            base = root / rel
            resolved = base.resolve()
            if not resolved.is_relative_to(root_resolved):
                raise ValueError(
                    "score-isolation contract: consumer %r path %r resolves to "
                    "%s, outside the scanned root %s - refusing to scan"
                    % (consumer.get("id"), rel, resolved, root_resolved))
            if not base.exists():
                continue
    # [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 22:00 UTC | F3: containment | END edit ]
            # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | START edit ]
            # A consumer path may name a single file: the reference simulator
            # keeps its CPU logic in one module (tools/uppercut_sim/policy.py),
            # and the contract now names it, which is what made this scan
            # load-bearing rather than provisioned.
            files = [base] if base.is_file() else sorted(base.rglob("*"))
            # [ Claude (Cowork) | Claude Fable 5 (claude-fable-5) | 2026-08-04 02:13 UTC | END edit ]
            for f in files:
                if not f.is_file() or f.suffix not in SCANNABLE:
                    continue
                for n, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
                    m = pattern.search(line)
                    if m:
                        out.append(Violation(
                            "score_access", f"{f.relative_to(root)}:{n}",
                            f"forbidden consumer '{consumer['id']}' references sealed symbol '{m.group(1)}'"))
    return out


def check_event_log(events: list, contract: dict | None = None) -> list:
    """Structural firewall checks over a recorded event log."""
    contract = contract or load_contract()
    sealed_types = set(contract["sealed_symbols"]["event_types"])
    out: list = []

    sealed_seqs = set()
    for e in events:
        if e.get("type") in sealed_types:
            if e.get("visibility") != "sealed":
                out.append(Violation("unsealed_card", f"seq={e.get('seq')}",
                                     f"event '{e.get('type')}' must carry visibility 'sealed'"))
            sealed_seqs.add(e.get("seq"))
        elif e.get("visibility") == "sealed":
            sealed_seqs.add(e.get("seq"))

    for e in events:
        if e.get("type") != "cpu_decision":
            continue
        cited = set((e.get("payload") or {}).get("observed_evidence", []))
        leaked = cited & sealed_seqs
        if leaked:
            out.append(Violation("evidence_leak", f"seq={e.get('seq')}",
                                 f"CPU decision cites sealed event(s) {sorted(leaked)} as observed evidence"))
        assertion = (e.get("payload") or {}).get("forbidden_inputs_assertion")
        if assertion != "no_official_score_no_opponent_input_no_privileged_state":
            out.append(Violation("missing_assertion", f"seq={e.get('seq')}",
                                 "CPU decision lacks the forbidden-inputs assertion"))
    return out
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
