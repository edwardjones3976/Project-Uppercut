# [ Codex | GPT-5 | 2026-08-13 23:33 UTC | START: imported from director-orchestrator@110e403 and specialized for Project Uppercut ]
from __future__ import annotations

import re
from copy import deepcopy

from .config import Settings
from .models import Assignment, DirectorPlan, ProviderName, RiskLevel


_GATES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("production deployment or public publishing", re.compile(r"\b(deploy|release|publish|go live|production|prod)\b", re.I)),
    ("merge or protected-branch change", re.compile(r"\b(merge|protected branch|push (?:to )?(?:main|master)|directly to main)\b", re.I)),
    ("destructive action", re.compile(r"\b(delete|destroy|drop database|truncate|purge|wipe|remove account|rewrite history|force push)\b", re.I)),
    ("purchase or paid upgrade", re.compile(r"\b(buy|purchase|subscribe|upgrade plan|charge|payment|spend)\b", re.I)),
    ("external representation", re.compile(r"\b(send|email|message|post|reply|submit)\b.{0,50}\b(customer|client|public|vendor|agency|employer|recipient)\b", re.I | re.S)),
    ("sensitive data", re.compile(r"\b(ssn|social security|passport|medical|health|financial|bank|credit card|identity|genealogy evidence|dna|authentication data)\b", re.I)),
    ("credential or permission change", re.compile(r"\b(api key|token|password|secret|credential|oauth|permission|access scope|administrator|admin access)\b", re.I)),
)


def deterministic_approval_reasons(text: str) -> list[str]:
    return [label for label, pattern in _GATES if pattern.search(text)]


def normalize_repository(repository: str) -> str:
    normalized = repository.strip().rstrip("/")
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized.removeprefix("git@github.com:")
    if normalized.lower().endswith(".git"):
        normalized = normalized[:-4]
    return normalized.lower()


def enforce_plan(plan: DirectorPlan, source_text: str, settings: Settings) -> DirectorPlan:
    safe = deepcopy(plan)
    safe.project = settings.director_project_name
    safe.max_hops = min(safe.max_hops, settings.max_agent_hops)
    safe.max_revisions = min(safe.max_revisions, settings.max_revisions)

    reasons = set(safe.approval_reasons)
    reasons.update(deterministic_approval_reasons(source_text))

    allowed = {
        normalize_repository(repository)
        for repository in settings.director_allowed_repositories
    }
    assignments: list[Assignment] = []
    outside_scope: list[str] = []
    for item in safe.assignments:
        repository = item.repository or settings.director_default_repository
        starting_ref = item.starting_ref or settings.director_default_starting_ref
        if repository and normalize_repository(repository) not in allowed:
            outside_scope.append(repository)
        assignments.append(
            item.model_copy(
                update={"repository": repository, "starting_ref": starting_ref}
            )
        )
    safe.assignments = assignments
    if outside_scope:
        reasons.add("repository outside Project Uppercut allowlist")
        safe.owner_question = (
            "The plan targets a repository outside the Project Uppercut allowlist: "
            + ", ".join(sorted(set(outside_scope)))
            + ". Change the reviewed deployment allowlist before dispatching it."
        )
    if safe.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
        reasons.add(f"{safe.risk_level.value}-risk plan")
    if sum(item.estimated_cost_usd for item in safe.assignments) > settings.max_task_budget_usd:
        reasons.add("estimated cost exceeds task budget")

    safe.approval_reasons = sorted(reasons)
    safe.approval_required = bool(reasons) or safe.approval_required
    if safe.approval_required:
        safe.assignments = [
            item.model_copy(update={"requires_approval": True})
            if item.requires_approval or reasons
            else item
            for item in safe.assignments
        ]
    return safe


def preview_plan(text: str, settings: Settings) -> DirectorPlan:
    lowered = text.lower()
    if any(word in lowered for word in ("research", "sources", "current", "verify facts")):
        provider = ProviderName.PERPLEXITY
    elif any(word in lowered for word in ("prototype", "browser", "visual", "alternate implementation")):
        provider = ProviderName.GEMINI
    elif any(word in lowered for word in ("review", "document", "presentation", "analysis")):
        provider = ProviderName.CLAUDE
    else:
        provider = ProviderName.CURSOR

    project = "unspecified"
    match = re.search(r"(?im)^\s*project\s*:\s*(.+)$", text)
    if match:
        project = match.group(1).strip()[:255]

    assignment = Assignment(
        sequence=1,
        agent=provider,
        task=text.strip(),
        acceptance=["Owner-defined outcome is demonstrably satisfied", "Evidence and unresolved risks are reported"],
        repository=settings.director_default_repository,
        starting_ref=settings.director_default_starting_ref,
        requires_approval=False,
        estimated_cost_usd=0,
    )
    plan = DirectorPlan(
        project=project,
        normalized_outcome=text.strip(),
        risk_level=RiskLevel.LOW,
        approval_required=False,
        approval_reasons=[],
        max_hops=min(3, settings.max_agent_hops),
        max_revisions=min(1, settings.max_revisions),
        assignments=[assignment],
        final_acceptance=["All assignment checks pass", "No approval gate was bypassed"],
        owner_question=None,
    )
    return enforce_plan(plan, text, settings)
# [ Codex | GPT-5 | 2026-08-13 23:37 UTC | END: imported from director-orchestrator@110e403 and specialized for Project Uppercut ]
