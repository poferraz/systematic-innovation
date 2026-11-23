import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.repository.authority import REQUIRED_LINKS, scan_authority

ROOT = Path(__file__).resolve().parents[2]


def _create_minimal_valid_repo(tmp_root: Path) -> None:
    for relative in REQUIRED_LINKS:
        document = tmp_root / relative
        document.parent.mkdir(parents=True, exist_ok=True)
        document.write_text("# Fixture\n", encoding="utf-8")
    (tmp_root / "AGENTS.md").write_text(
        (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        if (ROOT / "AGENTS.md").is_file()
        else "skills/systematic-innovation/\nCONTEXT.md\n",
        encoding="utf-8",
    )


class AuthorityTests(unittest.TestCase):
    def test_repository_has_one_declared_behavioral_authority(self) -> None:
        self.assertEqual(scan_authority(ROOT), [])

    def test_missing_canonical_skill_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_minimal_valid_repo(root)
            (root / "skills/systematic-innovation/SKILL.md").unlink()
            self.assertTrue(any("document missing" in err for err in scan_authority(root)))

    def test_retired_plan_directory_cannot_be_reintroduced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_minimal_valid_repo(root)
            plan = root / "docs/superpowers/plans/draft.md"
            plan.parent.mkdir(parents=True)
            plan.write_text("Development notes", encoding="utf-8")
            self.assertTrue(any("development plan" in err for err in scan_authority(root)))

    def test_scan_authority_rejects_missing_agents_file_and_shadow_copies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            errors = scan_authority(tmp_root)
            self.assertTrue(any("AGENTS.md" in err for err in errors))

            # Populate minimal valid routing then inject a shadow SKILL.md outside canonical path
            _create_minimal_valid_repo(tmp_root)
            shadow = tmp_root / "adapters/cursor/SKILL.md"
            shadow.parent.mkdir(parents=True)
            shadow.write_text("---\nname: systematic-innovation\n---\n", encoding="utf-8")
            shadow_errors = scan_authority(tmp_root)
            self.assertTrue(any("shadow" in err.lower() for err in shadow_errors))

    def test_shadow_markdown_content_triggers_authority_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _create_minimal_valid_repo(tmp_root)

            # A non-allowlisted markdown file (even named guide.md or README.md in a subfolder)
            # restating canonical signatures triggers an authority error
            guide = tmp_root / "adapters/cursor/guide.md"
            guide.parent.mkdir(parents=True, exist_ok=True)
            guide.write_text(
                "# Guide\n"
                "Quick Mode: 10 to 15\n"
                "System Dynamics\n"
                "Human Value\n"
                "Operational Reality\n"
                "Boundary Reframing\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            self.assertTrue(
                any("shadow behavioral authority" in err.lower() for err in errors),
                f"Expected shadow behavioral authority error, got: {errors}",
            )

    def test_authority_cli_subprocess_exits_zero_on_root(self) -> None:
        res = subprocess.run(
            [sys.executable, "-m", "tools.repository.authority"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            res.returncode,
            0,
            f"authority CLI exited {res.returncode}; stdout={res.stdout!r}, stderr={res.stderr!r}",
        )

    def test_authority_cli_subprocess_exits_one_on_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            res = subprocess.run(
                [sys.executable, "-m", "tools.repository.authority", str(tmp_root)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                res.returncode,
                1,
                f"Expected exit code 1 on findings; stdout={res.stdout!r}, stderr={res.stderr!r}",
            )
            self.assertTrue(
                "missing agents.md" in (res.stdout + res.stderr).lower(),
                f"Expected missing AGENTS.md message, got: stdout={res.stdout!r}, stderr={res.stderr!r}",
            )

if __name__ == "__main__":
    unittest.main()

