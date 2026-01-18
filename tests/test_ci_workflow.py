"""Tests for CI/CD workflow configuration."""

import pytest
from pathlib import Path

import yaml


class TestGitHubWorkflow:
    """Tests to validate GitHub Actions workflow configuration."""

    @pytest.fixture
    def workflow_path(self) -> Path:
        """Path to the test.yml workflow file."""
        return Path(__file__).parent.parent / ".github" / "workflows" / "test.yml"

    @pytest.fixture
    def workflow(self, workflow_path) -> dict:
        """Load and parse the workflow file."""
        if not workflow_path.exists():
            pytest.skip("Workflow file not found")
        return yaml.safe_load(workflow_path.read_text())

    def test_workflow_file_exists(self, workflow_path):
        """Verify the workflow file exists."""
        assert workflow_path.exists(), "GitHub Actions workflow file should exist"

    def test_workflow_is_valid_yaml(self, workflow_path):
        """Verify the workflow file is valid YAML."""
        content = workflow_path.read_text()
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            pytest.fail(f"Workflow file is not valid YAML: {e}")

    def test_workflow_has_name(self, workflow):
        """Verify workflow has a name."""
        assert "name" in workflow, "Workflow should have a name"
        assert workflow["name"] == "Tests"

    def test_workflow_has_triggers(self, workflow):
        """Verify workflow has trigger events.

        Note: YAML parses 'on:' as the boolean True, so we check for True key.
        """
        # YAML parses 'on:' as True (boolean), not the string 'on'
        assert True in workflow or "on" in workflow, "Workflow should have trigger events"
        triggers = workflow.get(True) or workflow.get("on")
        assert "push" in triggers or "pull_request" in triggers

    def test_workflow_has_unit_tests_job(self, workflow):
        """Verify unit-tests job exists."""
        assert "jobs" in workflow
        assert "unit-tests" in workflow["jobs"]

    def test_workflow_has_integration_tests_job(self, workflow):
        """Verify integration-tests job exists."""
        assert "jobs" in workflow
        assert "integration-tests" in workflow["jobs"]

    def test_unit_tests_runs_on_matrix(self, workflow):
        """Verify unit tests run on multiple platforms."""
        job = workflow["jobs"]["unit-tests"]
        assert "strategy" in job
        assert "matrix" in job["strategy"]
        matrix = job["strategy"]["matrix"]
        assert "os" in matrix
        # Should include at least ubuntu and macos
        os_list = matrix["os"]
        assert any("ubuntu" in os for os in os_list)
        assert any("macos" in os for os in os_list)

    def test_integration_tests_runs_on_macos(self, workflow):
        """Verify integration tests run on macOS."""
        job = workflow["jobs"]["integration-tests"]
        assert "runs-on" in job
        assert "macos" in job["runs-on"]

    def test_integration_tests_has_model_caching(self, workflow):
        """Verify integration tests cache the whisper model."""
        job = workflow["jobs"]["integration-tests"]
        steps = job.get("steps", [])
        cache_steps = [s for s in steps if s.get("uses", "").startswith("actions/cache")]
        assert len(cache_steps) >= 1, "Should have at least one cache step"

        # Check for whisper model cache
        whisper_cache = any(
            "whisper" in str(s.get("with", {}))
            for s in cache_steps
        )
        assert whisper_cache, "Should cache whisper model"

    def test_workflow_uploads_test_artifacts(self, workflow):
        """Verify workflow uploads test results as artifacts."""
        for job_name, job in workflow["jobs"].items():
            steps = job.get("steps", [])
            upload_steps = [s for s in steps if "upload-artifact" in s.get("uses", "")]
            # At least some jobs should upload artifacts
            if job_name in ["unit-tests", "integration-tests"]:
                assert len(upload_steps) >= 1, f"{job_name} should upload artifacts"

    def test_integration_tests_skips_microphone_tests(self, workflow):
        """Verify CI skips microphone-dependent tests."""
        job = workflow["jobs"]["integration-tests"]
        steps = job.get("steps", [])

        # Find the pytest run step
        pytest_steps = [s for s in steps if "pytest" in str(s.get("run", ""))]
        assert len(pytest_steps) >= 1

        # Check that it excludes microphone tests
        pytest_cmd = pytest_steps[0].get("run", "")
        assert "not requires_microphone" in pytest_cmd or "requires_microphone" not in pytest_cmd

    def test_workflow_has_python_setup(self, workflow):
        """Verify all jobs set up Python."""
        for job_name, job in workflow["jobs"].items():
            if job_name == "test-summary":
                continue  # Summary job doesn't need Python
            steps = job.get("steps", [])
            python_steps = [s for s in steps if "setup-python" in s.get("uses", "")]
            assert len(python_steps) >= 1, f"{job_name} should set up Python"


class TestWorkflowMarkerConsistency:
    """Tests to verify pytest markers are consistent with workflow."""

    @pytest.fixture
    def pyproject_path(self) -> Path:
        """Path to pyproject.toml."""
        return Path(__file__).parent.parent / "pyproject.toml"

    def test_integration_marker_defined(self, pyproject_path):
        """Verify integration marker is defined in pyproject.toml."""
        content = pyproject_path.read_text()
        assert "integration" in content
        assert "marks tests as integration tests" in content

    def test_requires_microphone_marker_defined(self, pyproject_path):
        """Verify requires_microphone marker is defined."""
        content = pyproject_path.read_text()
        assert "requires_microphone" in content

    def test_requires_whisper_marker_defined(self, pyproject_path):
        """Verify requires_whisper marker is defined."""
        content = pyproject_path.read_text()
        assert "requires_whisper" in content

    def test_requires_macos_marker_defined(self, pyproject_path):
        """Verify requires_macos marker is defined."""
        content = pyproject_path.read_text()
        assert "requires_macos" in content
