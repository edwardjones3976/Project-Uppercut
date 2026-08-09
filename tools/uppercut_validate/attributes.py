# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | START ]
"""Rule 10 attribute-economy validator.

Every check below quotes the clause of PROJECT_RULES.md Rule 10 it enforces.
Interpretation choices are surfaced in docs/phase0/open_questions.md and are
configurable here rather than silently baked in.
"""
from __future__ import annotations
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-09 21:58 UTC | F1: strict canon JSON ]
from . import strict_json as json
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Interpretation:
    """Configurable readings of Rule 10 clauses that admit more than one reading."""
    # OQ-1: may one positive attribute pay for more than one severe negative?
    compensation_binding: str = "exclusive"          # "exclusive" | "shared"
    # OQ-2: does a +100 also count toward "at most two attributes may exceed +70"?
    hundred_counts_toward_over_seventy: bool = True
    # OQ-3: "every physical trait negative" evaluated over declared attributes.
    all_negative_over_declared_only: bool = True


@dataclass
class Finding:
    rule: str
    severity: str          # "violation" | "warning"
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.rule}: {self.message}"


@dataclass
class Report:
    fighter_id: str
    findings: list = field(default_factory=list)

    @property
    def legal(self) -> bool:
        return not any(f.severity == "violation" for f in self.findings)

    @property
    def violations(self) -> list:
        return [f for f in self.findings if f.severity == "violation"]


def load_families(path: Path | None = None) -> dict:
    path = path or REPO / "data" / "attribute_families.json"
    return json.loads(path.read_text())


def family_of(attr: str, families: dict) -> str | None:
    for name, spec in families["families"].items():
        if attr in spec["attributes"]:
            return name
    return None


def validate_fighter(fighter: dict, families: dict | None = None,
                     interp: Interpretation | None = None) -> Report:
    families = families or load_families()
    interp = interp or Interpretation()
    rep = Report(fighter_id=fighter.get("id", "<unknown>"))
    attrs: dict = fighter.get("attributes", {})
    add = rep.findings.append

    # --- vocabulary: "families and compensating relationships must be explicit data" ---
    for k in attrs:
        if family_of(k, families) is None:
            add(Finding("R10.families", "violation",
                        f"attribute '{k}' belongs to no declared family in data/attribute_families.json"))

    # --- range ---
    for k, v in attrs.items():
        if not isinstance(v, int) or not (-100 <= v <= 100):
            add(Finding("R10.range", "violation", f"'{k}' = {v!r} outside the -100..+100 economy"))

    # --- positive caps ---
    at_hundred = [k for k, v in attrs.items() if v == 100]
    if len(at_hundred) > 1:
        add(Finding("R10.pos.one_max", "violation",
                    f"at most one attribute may equal +100; found {len(at_hundred)}: {sorted(at_hundred)}"))
    over_seventy = [k for k, v in attrs.items()
                    if v > 70 and (interp.hundred_counts_toward_over_seventy or v != 100)]
    if len(over_seventy) > 2:
        add(Finding("R10.pos.two_over_70", "violation",
                    f"at most two attributes may exceed +70; found {len(over_seventy)}: {sorted(over_seventy)}"))

    # --- negative safeguards ---
    at_minus_hundred = [k for k, v in attrs.items() if v == -100]
    if len(at_minus_hundred) > 1:
        add(Finding("R10.neg.one_max", "violation",
                    f"at most one attribute may equal -100; found {len(at_minus_hundred)}: {sorted(at_minus_hundred)}"))

    below_thirty = [k for k, v in attrs.items() if v < -30]
    by_family: dict = {}
    for k in below_thirty:
        by_family.setdefault(family_of(k, families), []).append(k)
    for fam, keys in by_family.items():
        if fam is not None and len(keys) > 2:
            add(Finding("R10.neg.two_related_under_30", "violation",
                        f"at most two RELATED attributes may fall below -30; family '{fam}' has {len(keys)}: {sorted(keys)}"))

    below_forty = [k for k, v in attrs.items() if v < -40]
    if len(below_forty) > 3:
        add(Finding("R10.neg.three_under_40", "violation",
                    f"at most three attributes may fall below -40 overall; found {len(below_forty)}: {sorted(below_forty)}"))

    # --- no all-negative physical or technical family ---
    for fam, spec in families["families"].items():
        if not spec.get("rule10_all_negative_prohibited"):
            continue
        declared = [k for k in spec["attributes"] if k in attrs]
        pool = declared if interp.all_negative_over_declared_only else spec["attributes"]
        if pool and all(attrs.get(k, 0) < 0 for k in pool):
            add(Finding("R10.neg.family_all_negative", "violation",
                        f"no fighter may have every {fam} trait negative; all {len(pool)} declared {fam} attributes are negative"))

    # --- compensation ladder ---
    def required_positive(v: int) -> int | None:
        if -60 <= v <= -41:
            return 30
        if -80 <= v <= -61:
            return 50
        if -100 <= v <= -81:
            return 70
        return None

    comps = fighter.get("compensations", [])
    used_positives: set = set()
    for k, v in sorted(attrs.items()):
        need = required_positive(v)
        if need is None:
            continue
        linked = [c for c in comps if c.get("negative") == k]
        if not linked:
            add(Finding("R10.compensation", "violation",
                        f"'{k}' = {v} requires a declared compensating positive of at least +{need}; "
                        f"no compensation entry names it (Rule 10 requires explicit data)"))
            continue
        satisfied = False
        for c in linked:
            pos = c.get("positive")
            pval = attrs.get(pos)
            if pval is None:
                add(Finding("R10.compensation", "violation",
                            f"'{k}' compensation names '{pos}', which is not a declared attribute"))
                continue
            if pval < need:
                add(Finding("R10.compensation", "violation",
                            f"'{k}' = {v} requires a compensating positive of at least +{need}; "
                            f"'{pos}' = {pval} is insufficient"))
                continue
            if interp.compensation_binding == "exclusive" and pos in used_positives:
                add(Finding("R10.compensation.exclusive", "violation",
                            f"'{pos}' is already spent compensating another severe negative; "
                            f"give-and-take forbids reusing it for '{k}' (OQ-1)"))
                continue
            used_positives.add(pos)
            satisfied = True
            break
        if not satisfied and not any(f.rule.startswith("R10.compensation") and k in f.message
                                     for f in rep.findings):
            add(Finding("R10.compensation", "violation",
                        f"'{k}' = {v} has no satisfied compensation"))

    # --- severe negatives must cause visible gameplay consequences ---
    declared_consequences = {e["attribute"] for e in fighter.get("severe_negative_consequences", [])}
    for k in below_forty:
        if k not in declared_consequences:
            add(Finding("R10.severe_consequence", "violation",
                        f"'{k}' = {attrs[k]} is a severe negative with no declared visible gameplay consequence"))

    # --- budget cap (Decision 0007) ---
    try:
        from . import budget as _budget
        ev = _budget.evaluate(attrs)
        if ev["over_cap"]:
            add(Finding("R10.budget_cap", "violation",
                        f"complete build nets {ev['net']} against the canonical cap of {ev['cap']} "
                        f"({ev['curve']}, refund {ev['refund_rate']})"))
    except FileNotFoundError:
        pass

    # --- no simplistic overall rating ---
    for banned in ("overall", "overall_rating", "ovr", "rating"):
        if banned in fighter or banned in attrs:
            add(Finding("R10.no_overall", "violation",
                        f"'{banned}' present; Rule 10 forbids one simplistic overall rating standing in for the profile"))

    return rep
# [ Claude (Cowork) | Claude Opus 5 (claude-opus-5) | 2026-08-02 19:34 UTC | END ]
