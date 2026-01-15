"""Integration tests for GitHub Actions workflow validation.

These tests validate the structure and configuration of workflow YAML files
without requiring actual GitHub Actions execution.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml


WORKFLOWS_DIR = Path(__file__).parent.parent.parent / ".github" / "workflows"
DAILY_DIGEST_WORKFLOW = WORKFLOWS_DIR / "daily-digest.yaml"
LINT_WORKFLOW = WORKFLOWS_DIR / "lint-workflow.yaml"


def load_workflow(path: Path) -> dict[str, Any]:
    """Load a workflow YAML file."""
    with open(path, encoding="utf-8") as f:
        result: dict[str, Any] = yaml.safe_load(f)
        return result


class TestDailyDigestWorkflow:
    """Tests for the daily-digest.yaml workflow."""

    @pytest.fixture
    def workflow(self) -> dict[str, Any]:
        """Load the daily digest workflow."""
        if not DAILY_DIGEST_WORKFLOW.exists():
            pytest.skip("daily-digest.yaml not found")
        return load_workflow(DAILY_DIGEST_WORKFLOW)

    def test_workflow_name(self, workflow: dict[str, Any]) -> None:
        """Verify workflow has a descriptive name."""
        assert "name" in workflow
        assert workflow["name"] == "Daily Digest"

    def test_schedule_trigger(self, workflow: dict[str, Any]) -> None:
        """Verify workflow has schedule trigger for UTC 23:00."""
        assert "on" in workflow
        triggers = workflow["on"]
        assert "schedule" in triggers

        schedules = triggers["schedule"]
        assert len(schedules) >= 1

        # Check cron expression: 0 23 * * * (UTC 23:00)
        cron = schedules[0]["cron"]
        assert cron == "0 23 * * *", f"Expected '0 23 * * *', got '{cron}'"

    def test_workflow_dispatch_trigger(self, workflow: dict[str, Any]) -> None:
        """Verify workflow supports manual triggering."""
        assert "on" in workflow
        triggers = workflow["on"]
        assert "workflow_dispatch" in triggers

    def test_required_permissions(self, workflow: dict[str, Any]) -> None:
        """Verify workflow has required permissions (least privilege)."""
        assert "permissions" in workflow
        permissions = workflow["permissions"]

        # Required permissions
        assert permissions.get("contents") == "write", (
            "Need contents:write for state branch"
        )
        assert permissions.get("pages") == "write", "Need pages:write for deployment"
        assert permissions.get("id-token") == "write", "Need id-token:write for OIDC"

    def test_concurrency_configuration(self, workflow: dict[str, Any]) -> None:
        """Verify concurrency is configured to prevent overlapping runs."""
        assert "concurrency" in workflow
        concurrency = workflow["concurrency"]

        # Should have a group
        assert "group" in concurrency
        assert "digest" in concurrency["group"].lower()

        # Should not cancel in progress (serialize instead)
        assert concurrency.get("cancel-in-progress") is False

    def test_environment_variables(self, workflow: dict[str, Any]) -> None:
        """Verify required environment variables are set."""
        assert "env" in workflow
        env = workflow["env"]

        required_vars = ["PYTHON_VERSION", "STATE_BRANCH", "STATE_FILE", "OUTPUT_DIR"]
        for var in required_vars:
            assert var in env, f"Missing environment variable: {var}"

    def test_jobs_structure(self, workflow: dict[str, Any]) -> None:
        """Verify workflow has required jobs."""
        assert "jobs" in workflow
        jobs = workflow["jobs"]

        # Required jobs
        required_jobs = ["digest", "deploy-pages", "persist-state"]
        for job in required_jobs:
            assert job in jobs, f"Missing job: {job}"

    def test_digest_job_steps(self, workflow: dict[str, Any]) -> None:
        """Verify digest job has required steps."""
        jobs = workflow["jobs"]
        digest_job = jobs["digest"]

        assert "steps" in digest_job
        steps = digest_job["steps"]

        # Check for key step names/ids
        step_names = []
        step_ids = []
        for step in steps:
            if "name" in step:
                step_names.append(step["name"].lower())
            if "id" in step:
                step_ids.append(step["id"])

        # Required steps
        assert any("checkout" in name for name in step_names), "Missing checkout step"
        assert any("state" in name for name in step_names), "Missing state restore step"
        assert any("python" in name for name in step_names), "Missing Python setup step"
        assert any("pipeline" in name for name in step_names), "Missing pipeline step"

    def test_deploy_pages_job_depends_on_digest(self, workflow: dict[str, Any]) -> None:
        """Verify deploy-pages job depends on successful digest."""
        jobs = workflow["jobs"]
        deploy_job = jobs["deploy-pages"]

        assert "needs" in deploy_job
        assert "digest" in deploy_job["needs"]

        # Should only run if digest succeeds
        assert deploy_job.get("if") == "success()" or "success()" in str(
            deploy_job.get("if", "")
        )

    def test_persist_state_job_depends_on_digest(
        self, workflow: dict[str, Any]
    ) -> None:
        """Verify persist-state job depends on successful digest."""
        jobs = workflow["jobs"]
        persist_job = jobs["persist-state"]

        assert "needs" in persist_job
        assert "digest" in persist_job["needs"]

        # Should only run if digest succeeds
        assert persist_job.get("if") == "success()" or "success()" in str(
            persist_job.get("if", "")
        )

    def test_no_secrets_in_commands(self, workflow: dict[str, Any]) -> None:
        """Verify no secrets are directly embedded in commands."""
        workflow_text = yaml.dump(workflow)

        # Should not contain set -x (could leak secrets in logs)
        assert "set -x" not in workflow_text, "Found 'set -x' which could leak secrets"

        # Check that secrets are properly referenced via ${{ secrets.* }}
        # and not hardcoded with actual values
        # The pattern "HF_TOKEN: ${{ secrets.HF_TOKEN }}" is acceptable
        import re

        # Look for secret-like patterns that are hardcoded (not via ${{ secrets.* }})
        # Bad pattern: HF_TOKEN: "actual_token_value" or HF_TOKEN: sk-xxx
        hardcoded_pattern = re.compile(
            r"(HF_TOKEN|OPENREVIEW_TOKEN):\s*['\"]?[a-zA-Z0-9_-]{10,}['\"]?"
        )
        matches = hardcoded_pattern.findall(workflow_text)
        # Filter out valid secret references
        for match in matches:
            if f"secrets.{match}" not in workflow_text:
                raise AssertionError(f"Potential hardcoded secret: {match}")

    def test_outputs_defined(self, workflow: dict[str, Any]) -> None:
        """Verify digest job defines required outputs."""
        jobs = workflow["jobs"]
        digest_job = jobs["digest"]

        assert "outputs" in digest_job
        outputs = digest_job["outputs"]

        # Required outputs
        assert "run_id" in outputs, "Missing run_id output"
        assert "state_checksum" in outputs, "Missing state_checksum output"

    def test_state_artifact_upload(self, workflow: dict[str, Any]) -> None:
        """Verify digest job uploads state.sqlite as artifact."""
        jobs = workflow["jobs"]
        digest_job = jobs["digest"]
        steps = digest_job["steps"]

        # Find artifact upload step
        artifact_steps = [
            s
            for s in steps
            if "uses" in s and "upload-artifact" in str(s.get("uses", ""))
        ]

        assert len(artifact_steps) >= 1, "Missing artifact upload step"

        # Verify it uploads state-sqlite
        upload_step = artifact_steps[0]
        assert "with" in upload_step
        assert upload_step["with"].get("name") == "state-sqlite"

    def test_persist_state_downloads_artifact(self, workflow: dict[str, Any]) -> None:
        """Verify persist-state job downloads artifact instead of re-running pipeline."""
        jobs = workflow["jobs"]
        persist_job = jobs["persist-state"]
        steps = persist_job["steps"]

        # Find artifact download step
        download_steps = [
            s
            for s in steps
            if "uses" in s and "download-artifact" in str(s.get("uses", ""))
        ]

        assert len(download_steps) >= 1, "Missing artifact download step"

        # Verify no pipeline re-run (no uv run python main.py run)
        for step in steps:
            if "run" in step:
                run_content = step["run"]
                assert "main.py run" not in run_content, (
                    "persist-state should not re-run pipeline"
                )

    def test_persist_state_no_secrets_needed(self, workflow: dict[str, Any]) -> None:
        """Verify persist-state job does not require API secrets."""
        jobs = workflow["jobs"]
        persist_job = jobs["persist-state"]
        steps = persist_job["steps"]

        # Check no step has HF_TOKEN or OPENREVIEW_TOKEN env
        for step in steps:
            if "env" in step:
                env = step["env"]
                assert "HF_TOKEN" not in env, "persist-state should not need HF_TOKEN"
                assert "OPENREVIEW_TOKEN" not in env, (
                    "persist-state should not need OPENREVIEW_TOKEN"
                )


class TestLintWorkflow:
    """Tests for the lint-workflow.yaml workflow."""

    @pytest.fixture
    def workflow(self) -> dict[str, Any]:
        """Load the lint workflow."""
        if not LINT_WORKFLOW.exists():
            pytest.skip("lint-workflow.yaml not found")
        return load_workflow(LINT_WORKFLOW)

    def test_workflow_name(self, workflow: dict[str, Any]) -> None:
        """Verify workflow has a descriptive name."""
        assert "name" in workflow
        assert "lint" in workflow["name"].lower()

    def test_triggers_on_workflow_changes(self, workflow: dict[str, Any]) -> None:
        """Verify workflow triggers on changes to workflow files."""
        triggers = workflow["on"]

        # Should trigger on push and pull_request to workflow paths
        for trigger_type in ["push", "pull_request"]:
            assert trigger_type in triggers
            trigger = triggers[trigger_type]
            assert "paths" in trigger
            paths = trigger["paths"]
            assert any(".github/workflows" in str(p) for p in paths)

    def test_read_only_permissions(self, workflow: dict[str, Any]) -> None:
        """Verify lint workflow only has read permissions."""
        assert "permissions" in workflow
        permissions = workflow["permissions"]

        # Should only have contents:read
        assert permissions.get("contents") == "read"


class TestWorkflowFilesExist:
    """Tests to verify required workflow files exist."""

    def test_workflows_directory_exists(self) -> None:
        """Verify .github/workflows directory exists."""
        assert WORKFLOWS_DIR.exists(), f"Workflows directory not found: {WORKFLOWS_DIR}"

    def test_daily_digest_workflow_exists(self) -> None:
        """Verify daily-digest.yaml exists."""
        assert DAILY_DIGEST_WORKFLOW.exists(), (
            f"Workflow not found: {DAILY_DIGEST_WORKFLOW}"
        )

    def test_lint_workflow_exists(self) -> None:
        """Verify lint-workflow.yaml exists."""
        assert LINT_WORKFLOW.exists(), f"Workflow not found: {LINT_WORKFLOW}"

    def test_workflow_files_are_valid_yaml(self) -> None:
        """Verify all workflow files are valid YAML."""
        for workflow_file in WORKFLOWS_DIR.glob("*.yaml"):
            try:
                load_workflow(workflow_file)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {workflow_file}: {e}")

        for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
            try:
                load_workflow(workflow_file)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {workflow_file}: {e}")


class TestTemplateFiles:
    """Tests to verify template files follow best practices."""

    TEMPLATES_DIR = (
        Path(__file__).parent.parent.parent / "src" / "renderer" / "templates"
    )

    def test_macros_file_exists(self) -> None:
        """Verify _macros.html exists for DRY template patterns."""
        macros_file = self.TEMPLATES_DIR / "_macros.html"
        assert macros_file.exists(), f"Macros file not found: {macros_file}"

    def test_base_template_has_skip_link(self) -> None:
        """Verify base.html has skip-to-content link for accessibility."""
        base_file = self.TEMPLATES_DIR / "base.html"
        assert base_file.exists()

        content = base_file.read_text()
        assert "skip-link" in content, "Missing skip-link for accessibility"
        assert "#main-content" in content, "Missing main-content anchor"

    def test_base_template_has_aria_current(self) -> None:
        """Verify base.html uses aria-current for current page indicator."""
        base_file = self.TEMPLATES_DIR / "base.html"
        assert base_file.exists()

        content = base_file.read_text()
        assert 'aria-current="page"' in content, "Missing aria-current for nav"

    def test_templates_import_macros(self) -> None:
        """Verify index.html and day.html import and use macros."""
        for template_name in ["index.html", "day.html"]:
            template_file = self.TEMPLATES_DIR / template_name
            assert template_file.exists()

            content = template_file.read_text()
            assert 'from "_macros.html" import' in content, (
                f"{template_name} should import macros"
            )
            assert "story_item" in content, (
                f"{template_name} should use story_item macro"
            )
