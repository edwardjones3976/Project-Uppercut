# [ Codex | GPT-5 | 2026-08-13 23:33 UTC | START: imported from director-orchestrator@110e403 and specialized for Project Uppercut ]
from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from director_orchestrator.config import Settings
from director_orchestrator.models import (
    Assignment,
    DirectorPlan,
    ProviderName,
    RiskLevel,
    SlackIntake,
    TaskRecord,
    TaskStatus,
)
from director_orchestrator.policy import (
    deterministic_approval_reasons,
    enforce_plan,
    preview_plan,
)
from director_orchestrator.store import TaskStore


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.settings = replace(Settings(), max_agent_hops=4, max_revisions=1, max_task_budget_usd=1.0)

    def test_merge_and_deploy_require_approval(self):
        reasons = deterministic_approval_reasons("Deploy to production and merge directly to main")
        self.assertIn("production deployment or public publishing", reasons)
        self.assertIn("merge or protected-branch change", reasons)

    def test_dry_run_routes_research_clamps_limits_and_stays_on_uppercut(self):
        plan = preview_plan("Project: RootWitness\nResearch current retention requirements with sources", self.settings)
        self.assertEqual(plan.project, "Project Uppercut")
        self.assertEqual(plan.assignments[0].agent.value, "perplexity")
        self.assertEqual(
            plan.assignments[0].repository,
            "https://github.com/edwardjones3976/Project-Uppercut",
        )
        self.assertLessEqual(plan.max_hops, 4)
        self.assertLessEqual(plan.max_revisions, 1)

    def test_repository_outside_allowlist_stops_for_reviewed_config_change(self):
        plan = DirectorPlan(
            project="anything",
            normalized_outcome="work elsewhere",
            risk_level=RiskLevel.LOW,
            approval_required=False,
            max_hops=1,
            max_revisions=0,
            assignments=[
                Assignment(
                    sequence=1,
                    agent=ProviderName.CURSOR,
                    task="Change another repository",
                    acceptance=["Change exists"],
                    repository="https://github.com/example/other.git",
                )
            ],
            final_acceptance=["Work reviewed"],
        )

        safe = enforce_plan(plan, "Change another repository", self.settings)

        self.assertTrue(safe.approval_required)
        self.assertIn("repository outside Project Uppercut allowlist", safe.approval_reasons)
        self.assertIn("example/other.git", safe.owner_question or "")

    def test_equivalent_uppercut_git_url_is_allowed(self):
        plan = DirectorPlan(
            project="Project Uppercut",
            normalized_outcome="inspect Uppercut",
            risk_level=RiskLevel.LOW,
            approval_required=False,
            max_hops=1,
            max_revisions=0,
            assignments=[
                Assignment(
                    sequence=1,
                    agent=ProviderName.CLAUDE,
                    task="Review the project",
                    acceptance=["Evidence is reported"],
                    repository="git@github.com:edwardjones3976/Project-Uppercut.git",
                )
            ],
            final_acceptance=["Review complete"],
        )

        safe = enforce_plan(plan, "Review the project", self.settings)

        self.assertFalse(safe.approval_required)
        self.assertIsNone(safe.owner_question)


class StoreTests(unittest.TestCase):
    def test_source_event_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            store = TaskStore(str(Path(directory) / "tasks.sqlite3"))
            intake = SlackIntake(
                source_event_id="evt-1",
                channel_id="C123",
                thread_ts="123.45",
                user_id="U123",
                text="DIRECTOR Project: demo Outcome: test",
            )
            first = TaskRecord(task_id="DIR-ONE", status=TaskStatus.QUEUED, intake=intake)
            second = TaskRecord(task_id="DIR-TWO", status=TaskStatus.QUEUED, intake=intake)
            stored_one, created_one = store.create(first)
            stored_two, created_two = store.create(second)
            self.assertTrue(created_one)
            self.assertFalse(created_two)
            self.assertEqual(stored_one.task_id, stored_two.task_id)

    def test_recoverable_tasks_exclude_owner_waits_and_terminal_states(self):
        with tempfile.TemporaryDirectory() as directory:
            store = TaskStore(str(Path(directory) / "tasks.sqlite3"))
            for index, status in enumerate(
                (TaskStatus.QUEUED, TaskStatus.RUNNING, TaskStatus.OWNER_DECISION_REQUIRED, TaskStatus.DONE)
            ):
                intake = SlackIntake(
                    source_event_id=f"evt-{index}",
                    channel_id="C123",
                    thread_ts=f"123.{index}",
                    user_id="U123",
                    text="DIRECTOR Project: demo Outcome: test",
                )
                store.create(TaskRecord(task_id=f"DIR-{index}", status=status, intake=intake))
            self.assertEqual(
                {record.task_id for record in store.list_recoverable()},
                {"DIR-0", "DIR-1"},
            )


if __name__ == "__main__":
    unittest.main()
# [ Codex | GPT-5 | 2026-08-13 23:37 UTC | END: imported from director-orchestrator@110e403 and specialized for Project Uppercut ]
