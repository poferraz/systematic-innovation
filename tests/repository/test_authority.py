import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.repository.authority import scan_authority

ROOT = Path(__file__).resolve().parents[2]


def _create_minimal_valid_repo(tmp_root: Path) -> None:
    (tmp_root / "CONTEXT.md").write_text("# Context\n", encoding="utf-8")
    specs = tmp_root / "docs/superpowers/specs"
    plans = tmp_root / "docs/superpowers/plans"
    specs.mkdir(parents=True, exist_ok=True)
    plans.mkdir(parents=True, exist_ok=True)
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

    def test_plans_with_broadened_supersession_language_trigger_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _create_minimal_valid_repo(tmp_root)

            plan = tmp_root / "docs/superpowers/plans/bad_plan.md"
            plan.write_text(
                "# Bad Plan\nThis task will override conflicting specification in Phase 2.\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            self.assertTrue(
                any("contractual supremacy" in err.lower() for err in errors),
                f"Expected supremacy error for 'override conflicting specification', got: {errors}",
            )

            plan.write_text(
                "# Bad Plan\nThis plan amends the specification directly.\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            self.assertTrue(
                any("contractual supremacy" in err.lower() for err in errors),
                f"Expected supremacy error for 'amends the specification', got: {errors}",
            )

            # Negated phrasing and code-quoted phrasing should NOT trigger an error
            plan.write_text(
                "# Good Plan\nPlans execute approved specifications and never amend the specification.\n"
                "We check for `override conflicting specification` in tests.\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            supremacy_errors = [err for err in errors if "contractual supremacy" in err.lower()]
            self.assertEqual(supremacy_errors, [])

            # Unnegated prose "supersede conflicting" triggers error
            plan.write_text(
                "# Bad Plan\nThis task will supersede conflicting architecture directives.\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            self.assertTrue(
                any("contractual supremacy" in err.lower() for err in errors),
                f"Expected supremacy error for 'supersede conflicting', got: {errors}",
            )

            # Negated prose "supersede conflicting" and backtick-quoted example do NOT trigger error
            plan.write_text(
                "# Good Plan\nPlans never supersede conflicting rules or specifications.\n"
                "Example: `supersede conflicting` is a forbidden phrase.\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            supremacy_errors = [err for err in errors if "contractual supremacy" in err.lower()]
            self.assertEqual(supremacy_errors, [], f"Expected no supremacy error, got: {supremacy_errors}")

            # Editorial punctuation in negation is tolerated
            plan.write_text(
                "# Good Plan\nThis document does not, however, amend the specification in any way.\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            supremacy_errors = [err for err in errors if "contractual supremacy" in err.lower()]
            self.assertEqual(supremacy_errors, [], f"Expected no supremacy error with editorial punctuation, got: {supremacy_errors}")

            # Sentence boundary before unnegated supersession MUST trigger an error
            plan.write_text(
                "# Bad Plan\nWe will never do X. This plan will amend the specification.\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            self.assertTrue(
                any("contractual supremacy" in err.lower() for err in errors),
                f"Expected supremacy error across sentence boundary, got: {errors}",
            )

            # Multi-line / newline boundary before unnegated supersession MUST trigger an error
            plan.write_text(
                "# Bad Plan\nWe will never do X\nThis plan will amend the specification.\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            self.assertTrue(
                any("contractual supremacy" in err.lower() for err in errors),
                f"Expected supremacy error across newline boundary, got: {errors}",
            )

            # Tilde code fences (3+ tildes) and 4-backtick fences do NOT trigger false positives
            plan.write_text(
                "# Good Plan\n"
                "~~~markdown\namend the specification\n~~~\n"
                "````\nsupersede conflicting\n````\n",
                encoding="utf-8",
            )
            errors = scan_authority(tmp_root)
            supremacy_errors = [err for err in errors if "contractual supremacy" in err.lower()]
            self.assertEqual(supremacy_errors, [], f"Expected code fences to be stripped cleanly, got: {supremacy_errors}")

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

    def test_context_md_has_section_6_historical_sync_note(self) -> None:
        context_text = (ROOT / "CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn(
            "*(Historical summary as of 2026-10-17; `skills/systematic-innovation/` and approved specifications remain authoritative.)*",
            context_text,
        )


if __name__ == "__main__":
    unittest.main()

