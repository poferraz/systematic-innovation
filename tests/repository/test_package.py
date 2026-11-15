import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from tools.repository.package import (
    ReleaseManifest,
    build_skill,
    verify_artifact,
    write_manifest,
)
from tools.validate_skill import validate_skill

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SKILL_DIR = ROOT / "skills/systematic-innovation"


class PackageTests(unittest.TestCase):
    def test_two_builds_in_different_temp_dirs_are_byte_identical_and_valid_after_extraction(self) -> None:
        revision = "a" * 40
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            zip1 = Path(tmp1) / "build-a/systematic-innovation.zip"
            zip2 = Path(tmp2) / "nested/build-b/systematic-innovation.zip"
            manifest1_path = Path(tmp1) / "build-a/manifest.json"

            m1 = build_skill(CANONICAL_SKILL_DIR, zip1, version="0.1.0", revision=revision)
            m2 = build_skill(CANONICAL_SKILL_DIR, zip2, version="0.1.0", revision=revision)
            write_manifest(m1, manifest1_path)

            self.assertIsInstance(m1, ReleaseManifest)
            bytes1 = zip1.read_bytes()
            bytes2 = zip2.read_bytes()
            self.assertEqual(bytes1, bytes2, "Expected two independent builds to be byte-for-byte identical")

            sha1 = hashlib.sha256(bytes1).hexdigest()
            self.assertEqual(m1.archive_sha256, sha1)
            self.assertEqual(m2.archive_sha256, sha1)
            self.assertEqual(m1.payload_sha256, m2.payload_sha256)

            with zipfile.ZipFile(zip1, "r") as zf:
                infos = zf.infolist()
                names = [info.filename for info in infos]
                self.assertEqual(names, sorted(names), "Archive entries must be in sorted POSIX order")
                self.assertEqual(
                    names,
                    [
                        "systematic-innovation/SKILL.md",
                        "systematic-innovation/references/deep-mode.md",
                        "systematic-innovation/references/evidence.md",
                        "systematic-innovation/references/innovation-lenses.md",
                        "systematic-innovation/references/output-contract.md",
                    ],
                )
                for info in infos:
                    self.assertTrue(info.filename.startswith("systematic-innovation/"))
                    self.assertNotIn("..", info.filename)
                    self.assertNotIn("\\", info.filename)
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    unix_mode = (info.external_attr >> 16) & 0o177777
                    self.assertEqual(unix_mode, 0o100644)

                extract_dir = Path(tmp1) / "extracted"
                zf.extractall(extract_dir)
                self.assertEqual(validate_skill(extract_dir / "systematic-innovation"), [])

            errors = verify_artifact(
                archive_path=zip1,
                manifest_path=manifest1_path,
                source_dir=CANONICAL_SKILL_DIR,
                revocations_path=ROOT / "release/revocations.json",
                policy_path=ROOT / "release/policy.json",
            )
            self.assertEqual(errors, [], f"Expected zero verification errors, got: {errors}")

    def test_build_skill_rejects_symlinks_and_non_canonical_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src_copy = Path(tmp) / "skill"
            shutil.copytree(CANONICAL_SKILL_DIR, src_copy)
            (src_copy / "README.md").write_text("# Extra\n", encoding="utf-8")

            out_zip = Path(tmp) / "out.zip"
            with self.assertRaises(ValueError):
                build_skill(src_copy, out_zip, version="0.1.0", revision="b" * 40)

            (src_copy / "README.md").unlink()
            symlink_path = src_copy / "references/link.md"
            symlink_path.symlink_to(src_copy / "SKILL.md")
            with self.assertRaises(ValueError):
                build_skill(src_copy, out_zip, version="0.1.0", revision="b" * 40)

    def test_verify_artifact_rejects_revoked_digest_and_tampered_zip(self) -> None:
        revision = "c" * 40
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            zip_path = tmp_path / "systematic-innovation.zip"
            manifest_path = tmp_path / "manifest.json"
            manifest = build_skill(CANONICAL_SKILL_DIR, zip_path, version="0.1.0", revision=revision)
            write_manifest(manifest, manifest_path)

            # 1. Revoked archive digest must be rejected even when archive & manifest are valid
            revocations_file = tmp_path / "revocations.json"
            revocations_file.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0.0",
                        "revoked_artifacts": [
                            {
                                "sha256": manifest.archive_sha256,
                                "reason": "Synthetic revocation test",
                                "revoked_at": "2026-11-14",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rev_errors = verify_artifact(
                archive_path=zip_path,
                manifest_path=manifest_path,
                revocations_path=revocations_file,
            )
            self.assertTrue(
                any("revoked" in err.lower() for err in rev_errors),
                f"Expected revoked artifact error, got: {rev_errors}",
            )

            # 2. Archive containing non-normalized timestamp or extra file must fail verification
            bad_zip = tmp_path / "bad.zip"
            with zipfile.ZipFile(bad_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("systematic-innovation/SKILL.md", "---\nname: systematic-innovation\n---\n")
            bad_errors = verify_artifact(archive_path=bad_zip)
            self.assertNotEqual(bad_errors, [])

    def test_release_policy_and_schema_files_exist_and_are_valid_json(self) -> None:
        policy = json.loads((ROOT / "release/policy.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "release/manifest.schema.json").read_text(encoding="utf-8"))
        revocations = json.loads((ROOT / "release/revocations.json").read_text(encoding="utf-8"))

        self.assertEqual(policy["release_channel"], "github-releases")
        self.assertEqual(policy["tag_pattern"], "^v[0-9]+\\.[0-9]+\\.[0-9]+$")
        self.assertEqual(policy["archive_policy"], "release-only")
        self.assertEqual(policy["trusted_workflow"], ".github/workflows/release.yml")
        self.assertIn("payload_sha256", schema["required"])
        self.assertIn("revoked_artifacts", revocations)

    def test_package_and_verify_artifact_cli_subcommands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            zip_out = tmp_path / "systematic-innovation.zip"
            manifest_out = tmp_path / "manifest.json"
            res_pkg = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.repository",
                    "package",
                    "--output",
                    str(zip_out),
                    "--manifest",
                    str(manifest_out),
                    "--version",
                    "0.1.0",
                    "--revision",
                    "d" * 40,
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_pkg.returncode, 0, res_pkg.stderr)
            self.assertTrue(zip_out.is_file())
            self.assertTrue(manifest_out.is_file())

            res_ver = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.repository",
                    "verify-artifact",
                    str(zip_out),
                    "--manifest",
                    str(manifest_out),
                    "--source",
                    str(CANONICAL_SKILL_DIR),
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_ver.returncode, 0, res_ver.stdout + res_ver.stderr)


if __name__ == "__main__":
    unittest.main()
