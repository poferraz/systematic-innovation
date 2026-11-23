from pathlib import Path
import re
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", re.MULTILINE)
PINNED_ACTION_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$")


class WorkflowAndPackagingTests(unittest.TestCase):
    def test_pyproject_declares_stdlib_runtime_and_playwright_dev_group(self) -> None:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["name"], "systematic-innovation")
        self.assertEqual(data["project"]["dependencies"], [])
        self.assertIn("playwright", " ".join(data["dependency-groups"]["dev"]))

    def test_ci_workflow_is_least_privilege_pinned_and_runs_stdlib_checks(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertIn("timeout-minutes: 15", workflow)
        self.assertIn("cancel-in-progress: true", workflow)
        self.assertNotIn("pull_request_target", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("write", workflow)
        self.assertNotIn("restricted/", workflow)
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertIn("python3 tools/validate_skill.py skills/systematic-innovation", workflow)
        self.assertIn("python3 -m tools.repository validate", workflow)

        uses_targets = USES_RE.findall(workflow)
        self.assertGreaterEqual(len(uses_targets), 2)
        for target in uses_targets:
            self.assertRegex(
                target,
                PINNED_ACTION_RE,
                f"Expected full 40-char commit SHA pin for GitHub Action: {target}",
            )

    def test_benchmark_ci_uses_locked_isolated_checks_on_supported_matrix(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("  benchmark:", workflow)
        self.assertIn("working-directory: benchmark", workflow)
        self.assertIn('version: "0.12.8"', workflow)
        for version in ("3.11", "3.13", "3.14"):
            self.assertIn('"'+version+'"', workflow)
        for command in ("uv lock --check", "uv run --locked pytest -q", "uv run --locked ruff check .", "uv run --locked mypy src"):
            self.assertIn(command, workflow)
        self.assertIn("--stage full", workflow)

    def test_dependabot_config_exists_and_uses_monthly_reviewable_schedule(self) -> None:
        dependabot_path = ROOT / ".github/dependabot.yml"
        self.assertTrue(dependabot_path.is_file(), "Expected .github/dependabot.yml to exist")
        text = dependabot_path.read_text(encoding="utf-8")
        self.assertIn("version: 2", text)
        self.assertIn('package-ecosystem: "github-actions"', text)
        self.assertIn('package-ecosystem: "pip"', text)
        self.assertIn('interval: "monthly"', text)

    def test_agents_md_lists_validation_commands_and_study_docs(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("python3 -m unittest discover tests -v", agents)
        self.assertIn("python3 tools/validate_skill.py skills/systematic-innovation", agents)
        self.assertIn("python3 -m tools.repository validate", agents)
        self.assertIn("benchmark/study/six-case-protocol.md", agents)
        self.assertIn("evals/v2-loop/report.md", agents)

    def test_security_md_explains_trust_zones_and_uses_advisories(self) -> None:
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertNotIn(".local", security)
        self.assertIn("Trust Zones", security)
        self.assertIn("GitHub Security Advisory", security)


if __name__ == "__main__":
    unittest.main()
