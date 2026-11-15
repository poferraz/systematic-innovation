from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]


class WorkflowAndPackagingTests(unittest.TestCase):
    def test_pyproject_declares_stdlib_runtime_and_playwright_dev_group(self) -> None:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["name"], "systematic-innovation")
        self.assertEqual(data["project"]["dependencies"], [])
        self.assertIn("playwright", " ".join(data["dependency-groups"]["dev"]))

    def test_ci_workflow_is_least_privilege_and_runs_stdlib_checks(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertIn("timeout-minutes: 15", workflow)
        self.assertIn("cancel-in-progress: true", workflow)
        self.assertNotIn("pull_request_target", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertIn("python3 tools/validate_skill.py skills/systematic-innovation", workflow)
        self.assertIn("python3 -m tools.repository validate", workflow)

    def test_agents_md_lists_validation_commands_and_loop_docs(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("python3 -m unittest discover tests -v", agents)
        self.assertIn("python3 tools/validate_skill.py skills/systematic-innovation", agents)
        self.assertIn("2026-11-14-systematic-innovation-v2-loop-design.md", agents)
        self.assertIn("2026-11-14-systematic-innovation-v2-loop.md", agents)

    def test_security_md_explains_trust_zones_and_uses_advisories(self) -> None:
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertNotIn(".local", security)
        self.assertIn("Trust Zones", security)
        self.assertIn("GitHub Security Advisory", security)


if __name__ == "__main__":
    unittest.main()
