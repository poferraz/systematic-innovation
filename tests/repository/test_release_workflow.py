from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", re.MULTILINE)
PINNED_ACTION_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$")


class ReleaseWorkflowTests(unittest.TestCase):
    def test_release_workflow_enforces_tag_only_attestation_and_reproducibility_gates(self) -> None:
        workflow_path = ROOT / ".github/workflows/release.yml"
        self.assertTrue(workflow_path.is_file(), "Expected .github/workflows/release.yml to exist")
        text = workflow_path.read_text(encoding="utf-8")

        # Tag-only execution
        self.assertIn("tags:", text)
        self.assertIn("v[0-9]+.[0-9]+.[0-9]+", text)
        self.assertNotIn("pull_request", text)
        self.assertNotIn("workflow_dispatch", text)

        # Least-privilege permissions, checkout hardening, and timeout
        self.assertIn("contents: write", text)
        self.assertIn("id-token: write", text)
        self.assertIn("attestations: write", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("timeout-minutes: 15", text)

        # Every action must be pinned to a full 40-char SHA, including actions/attest
        uses_targets = USES_RE.findall(text)
        self.assertGreaterEqual(len(uses_targets), 3)
        for target in uses_targets:
            self.assertRegex(
                target,
                PINNED_ACTION_RE,
                f"Expected full 40-char SHA pin in release.yml, got: {target}",
            )
        self.assertIn("actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26", uses_targets)

        # Required verification and dual-build reproducibility gates in order
        val_idx = text.find("python3 -m tools.repository validate")
        build_a_idx = text.find("build-a/systematic-innovation.zip")
        build_b_idx = text.find("build-b/systematic-innovation.zip")
        cmp_idx = text.find("cmp -s")
        verify_idx = text.find("python3 -m tools.repository verify-artifact")
        attest_idx = text.find("actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26")
        publish_idx = text.find("gh release create")

        for name, idx in (
            ("validate", val_idx),
            ("build-a", build_a_idx),
            ("build-b", build_b_idx),
            ("cmp -s", cmp_idx),
            ("verify-artifact", verify_idx),
            ("actions/attest", attest_idx),
            ("gh release create", publish_idx),
        ):
            self.assertNotEqual(idx, -1, f"Missing required release gate in release.yml: {name}")

        self.assertLess(val_idx, build_a_idx)
        self.assertLess(build_a_idx, cmp_idx)
        self.assertLess(build_b_idx, cmp_idx)
        self.assertLess(cmp_idx, verify_idx)
        self.assertLess(verify_idx, attest_idx, "Artifact verification must precede attestation")
        self.assertLess(attest_idx, publish_idx, "Attestation must precede GitHub Release publication")

    def test_release_documentation_covers_attestation_integrity_rotation_and_revocation(self) -> None:
        release_doc = ROOT / "docs/release.md"
        self.assertTrue(release_doc.is_file(), "Expected docs/release.md to exist")
        text = release_doc.read_text(encoding="utf-8")

        self.assertIn("gh attestation verify", text)
        self.assertIn("--repo poferraz/systematic-innovation", text)
        self.assertIn(".github/workflows/release.yml", text)
        self.assertIn("release/revocations.json", text)
        self.assertIn("python3 -m tools.repository verify-artifact", text)
        self.assertIn("identity rotation", text.lower())
        self.assertIn("security advisory", text.lower())


if __name__ == "__main__":
    unittest.main()
