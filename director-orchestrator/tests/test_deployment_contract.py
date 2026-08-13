# [ Codex | GPT-5 | 2026-08-13 23:47 UTC | START ]
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeploymentContractTests(unittest.TestCase):
    def test_n8n_preserves_the_callers_bearer_header(self):
        workflow = json.loads(
            (ROOT / "n8n" / "workflows" / "director-intake.json").read_text(
                encoding="utf-8"
            )
        )
        request_node = next(
            node for node in workflow["nodes"] if node["name"] == "Create Director Task"
        )
        headers = {
            item["name"]: item["value"]
            for item in request_node["parameters"]["headerParameters"]["parameters"]
        }

        self.assertIn("$json.headers", headers["Authorization"])
        self.assertNotIn("ORCHESTRATOR_SHARED_SECRET", headers["Authorization"])

    def test_n8n_container_does_not_receive_the_orchestrator_secret(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertNotIn("ORCHESTRATOR_SHARED_SECRET:", compose)

    def test_bootstrap_forces_dry_run_and_checks_native_exit_codes(self):
        bootstrap = (ROOT / "scripts" / "windows-bootstrap.ps1").read_text(
            encoding="utf-8"
        )

        self.assertIn("ALLOW_PAID_RUNS=false", bootstrap)
        self.assertGreaterEqual(bootstrap.count("$LASTEXITCODE -ne 0"), 2)

    def test_deployment_service_images_are_digest_pinned(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        env_example = (ROOT / ".env.example").read_text(encoding="utf-8")

        self.assertRegex(
            dockerfile,
            r"FROM python:3\.12-slim@sha256:[0-9a-f]{64}",
        )
        self.assertRegex(compose, r"image: postgres:17-alpine@sha256:[0-9a-f]{64}")
        self.assertRegex(
            env_example,
            r"N8N_IMAGE=docker\.n8n\.io/n8nio/n8n@sha256:[0-9a-f]{64}",
        )

    def test_direct_orchestrator_intake_is_the_default(self):
        env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
        main_source = (
            ROOT / "src" / "director_orchestrator" / "main.py"
        ).read_text(encoding="utf-8")

        self.assertRegex(env_example, r"(?m)^N8N_DIRECTOR_WEBHOOK_URL=$")
        self.assertIn("if not settings.slack_channel_id", main_source)
        self.assertIn("if not settings.slack_owner_user_id", main_source)


if __name__ == "__main__":
    unittest.main()
# [ Codex | GPT-5 | 2026-08-13 23:47 UTC | END ]
