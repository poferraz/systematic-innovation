from pathlib import Path
import tempfile
import unittest

from tools.repository.authority import scan_authority

ROOT = Path(__file__).resolve().parents[2]


class AuthorityTests(unittest.TestCase):
    def test_repository_has_one_declared_behavioral_authority(self) -> None:
        self.assertEqual(scan_authority(ROOT), [])

    def test_plans_do_not_claim_contractual_supremacy(self) -> None:
        for plan in (ROOT / "docs/superpowers/plans").glob("*.md"):
            text = plan.read_text(encoding="utf-8").lower()
            forbidden = "supersede " + "conflicting"
            self.assertNotIn(forbidden, text, str(plan))

    def test_scan_authority_rejects_missing_agents_file_and_shadow_copies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            errors = scan_authority(tmp_root)
            self.assertTrue(any("AGENTS.md" in err for err in errors))

            # Populate minimal valid routing then inject a shadow SKILL.md outside canonical path
            (tmp_root / "CONTEXT.md").write_text("# Context\n", encoding="utf-8")
            specs = tmp_root / "docs/superpowers/specs"
            plans = tmp_root / "docs/superpowers/plans"
            specs.mkdir(parents=True)
            plans.mkdir(parents=True)
            (specs / "2026-08-31-systematic-innovation-design.md").write_text("# Spec 1\n", encoding="utf-8")
            (specs / "2026-09-01-systematic-innovation-repository-architecture-design.md").write_text(
                "# Spec 2\n", encoding="utf-8"
            )
            (plans / "2026-09-01-systematic-innovation-coordinated-implementation.md").write_text(
                "# Plan 0\n", encoding="utf-8"
            )
            (plans / "2026-08-31-systematic-innovation-skill.md").write_text("# Plan 1\n", encoding="utf-8")
            (plans / "2026-08-31-systematic-innovation-benchmark-runner.md").write_text(
                "# Plan 2\n", encoding="utf-8"
            )
            (plans / "2026-08-31-systematic-innovation-benchmark-study.md").write_text(
                "# Plan 3\n", encoding="utf-8"
            )
            (tmp_root / "AGENTS.md").write_text(
                (ROOT / "AGENTS.md").read_text(encoding="utf-8")
                if (ROOT / "AGENTS.md").is_file()
                else "skills/systematic-innovation/\nCONTEXT.md\n",
                encoding="utf-8",
            )
            shadow = tmp_root / "adapters/cursor/SKILL.md"
            shadow.parent.mkdir(parents=True)
            shadow.write_text("---\nname: systematic-innovation\n---\n", encoding="utf-8")
            shadow_errors = scan_authority(tmp_root)
            self.assertTrue(any("shadow" in err.lower() for err in shadow_errors))


if __name__ == "__main__":
    unittest.main()
