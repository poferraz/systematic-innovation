from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.repository.isolation import Violation, scan_public_tree
from tests.repository.test_authority import _create_minimal_valid_repo

ROOT = Path(__file__).resolve().parents[2]


def _create_minimal_valid_skill(tmp_root: Path) -> None:
    skill_dir = tmp_root / "skills/systematic-innovation"
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)
    for name in ("deep-mode.md", "evidence.md", "innovation-lenses.md", "output-contract.md"):
        (refs_dir / name).write_text(f"# {name}\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: systematic-innovation\n"
        "description: Use when the user wants distinct options.\n"
        "---\n\n"
        "# Systematic Innovation\n\n"
        "See [deep-mode.md](references/deep-mode.md), "
        "[evidence.md](references/evidence.md), "
        "[innovation-lenses.md](references/innovation-lenses.md), and "
        "[output-contract.md](references/output-contract.md).\n",
        encoding="utf-8",
    )


class IsolationTests(unittest.TestCase):
    def test_safe_repository_passes_public_isolation_scan(self) -> None:
        violations = scan_public_tree(ROOT)
        self.assertEqual(violations, [], f"Expected zero violations on ROOT, got: {violations}")

    def test_synthetic_leaking_tree_fixture_fails_with_restricted_path_and_never_echoes_content(self) -> None:
        fixture_root = ROOT / "tests/repository/fixtures/leaking-tree"
        violations = scan_public_tree(fixture_root)
        codes = {v.code for v in violations}
        self.assertIn("RESTRICTED_PATH", codes)
        paths = {v.path for v in violations if v.code == "RESTRICTED_PATH"}
        self.assertIn("restricted/validation.yaml", paths)
        for v in violations:
            self.assertIsInstance(v, Violation)
            self.assertNotIn("SYNTHETIC_RESTRICTED_CONTENT_DO_NOT_ECHO", v.message)

    def test_credential_names_and_secret_assignments_fail_without_echoing_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _create_minimal_valid_repo(tmp_root)
            _create_minimal_valid_skill(tmp_root)

            secret_val = "SuperSecretValue_" + "DoNotEcho987654321"
            openai_key = "OPENAI_" + "API_KEY"
            config_file = tmp_root / "config.env"
            config_file.write_text(f"{openai_key}={secret_val}\n", encoding="utf-8")

            violations = scan_public_tree(tmp_root)
            secret_violations = [v for v in violations if v.code == "SECRET_KEY_NAME"]
            self.assertTrue(
                len(secret_violations) >= 1,
                f"Expected SECRET_KEY_NAME violation, got: {violations}",
            )
            self.assertEqual(secret_violations[0].path, "config.env")
            for v in violations:
                self.assertNotIn(secret_val, v.message)
                self.assertNotIn(secret_val, repr(v))

    def test_shadow_canonical_behavior_outside_skill_directory_fails_with_shadow_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _create_minimal_valid_repo(tmp_root)
            _create_minimal_valid_skill(tmp_root)

            shadow = tmp_root / "adapters/other-host/SKILL.md"
            shadow.parent.mkdir(parents=True, exist_ok=True)
            shadow.write_text("---\nname: systematic-innovation\n---\n", encoding="utf-8")

            violations = scan_public_tree(tmp_root)
            codes = {v.code for v in violations}
            self.assertIn("SHADOW_AUTHORITY", codes)

    def test_generated_archive_and_undeclared_release_source_and_broken_reference_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _create_minimal_valid_repo(tmp_root)
            _create_minimal_valid_skill(tmp_root)

            # 1. Generated archive in tracked tree
            (tmp_root / "artifact.zip").write_bytes(b"PK\x05\x06" + b"\x00" * 18)
            # 2. Undeclared file inside skills/systematic-innovation/
            (tmp_root / "skills/systematic-innovation/extra.py").write_text("print(1)\n", encoding="utf-8")
            # 3. Broken relative link inside skills/systematic-innovation/SKILL.md
            skill_md = tmp_root / "skills/systematic-innovation/SKILL.md"
            skill_md.write_text(
                skill_md.read_text(encoding="utf-8") + "\nBroken [missing](references/missing.md)\n",
                encoding="utf-8",
            )

            violations = scan_public_tree(tmp_root)
            codes = {v.code for v in violations}
            self.assertIn("GENERATED_ARCHIVE", codes)
            self.assertIn("UNDECLARED_RELEASE_SOURCE", codes)
            self.assertIn("BROKEN_CANONICAL_REFERENCE", codes)

    def test_git_ls_files_is_used_for_git_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _create_minimal_valid_repo(tmp_root)
            _create_minimal_valid_skill(tmp_root)
            subprocess.run(["git", "init", "-q"], cwd=str(tmp_root), check=True)
            subprocess.run(["git", "add", "."], cwd=str(tmp_root), check=True)

            # An untracked file outside skills/ that is ignored by git ls-files should not trigger if only tracked files are scanned
            (tmp_root / ".gitignore").write_text("ignored_local.zip\n", encoding="utf-8")
            subprocess.run(["git", "add", ".gitignore"], cwd=str(tmp_root), check=True)
            (tmp_root / "ignored_local.zip").write_bytes(b"PK\x05\x06" + b"\x00" * 18)

            violations = scan_public_tree(tmp_root)
            self.assertEqual(violations, [], f"Expected clean git-tracked scan, got: {violations}")

            # Once force-tracked in git index, git ls-files reports it and scan_public_tree catches it
            subprocess.run(["git", "add", "-f", "ignored_local.zip"], cwd=str(tmp_root), check=True)
            violations_after = scan_public_tree(tmp_root)
            self.assertIn("GENERATED_ARCHIVE", {v.code for v in violations_after})

    def test_cli_validate_command_passes_on_root_and_fails_on_leaking_tree(self) -> None:
        res_ok = subprocess.run(
            [sys.executable, "-m", "tools.repository", "validate"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            res_ok.returncode,
            0,
            f"Expected exit code 0 on ROOT; stdout={res_ok.stdout!r}, stderr={res_ok.stderr!r}",
        )

        fixture_root = ROOT / "tests/repository/fixtures/leaking-tree"
        res_bad = subprocess.run(
            [sys.executable, "-m", "tools.repository", "validate", str(fixture_root)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(res_bad.returncode, 0)
        combined = res_bad.stdout + res_bad.stderr
        self.assertIn("RESTRICTED_PATH", combined)
        self.assertNotIn("SYNTHETIC_RESTRICTED_CONTENT_DO_NOT_ECHO", combined)


if __name__ == "__main__":
    unittest.main()
