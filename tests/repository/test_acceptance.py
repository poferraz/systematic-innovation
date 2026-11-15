import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.repository.acceptance import (
    EXPECTED_CRITERIA_IDS,
    REPOSITORY_SHELL_CRITERIA_IDS,
    evaluate_acceptance,
    validate_acceptance_inventory,
)

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE_PATH = ROOT / "evidence/architecture/acceptance.json"


class AcceptanceTests(unittest.TestCase):
    def test_acceptance_inventory_has_exact_ar01_through_ar12_and_valid_evidence(self) -> None:
        self.assertTrue(ACCEPTANCE_PATH.is_file(), "Expected evidence/architecture/acceptance.json to exist")
        data = json.loads(ACCEPTANCE_PATH.read_text(encoding="utf-8"))
        violations = validate_acceptance_inventory(data, root=ROOT)
        self.assertEqual(violations, [], f"Expected zero inventory schema violations, got: {violations}")

        rows = {row["id"]: row for row in data["criteria"]}
        self.assertEqual(tuple(rows.keys()), EXPECTED_CRITERIA_IDS)
        for cid in REPOSITORY_SHELL_CRITERIA_IDS:
            self.assertEqual(rows[cid]["status"], "passed", f"Expected {cid} to be 'passed'")
        for cid in ("AR-08", "AR-09"):
            self.assertEqual(
                rows[cid]["status"],
                "not-ready",
                f"Expected {cid} to remain 'not-ready' until benchmark/ package is built",
            )

    def test_rejects_aggregate_scores_invalid_states_and_missing_evidence_files(self) -> None:
        base = json.loads(ACCEPTANCE_PATH.read_text(encoding="utf-8"))

        # 1. Aggregate / composite score fields are forbidden (AR-10)
        with_score = copy.deepcopy(base)
        with_score["overall_score"] = 83.3
        v_score = validate_acceptance_inventory(with_score, root=ROOT)
        self.assertIn("AGGREGATE_SCORE_PROHIBITED", {v.code for v in v_score})

        row_score = copy.deepcopy(base)
        row_score["criteria"][0]["score"] = 100
        v_row_score = validate_acceptance_inventory(row_score, root=ROOT)
        self.assertIn("AGGREGATE_SCORE_PROHIBITED", {v.code for v in v_row_score})

        # 2. Invalid status value is rejected
        bad_status = copy.deepcopy(base)
        bad_status["criteria"][0]["status"] = "mostly-passed"
        v_status = validate_acceptance_inventory(bad_status, root=ROOT)
        self.assertIn("INVALID_STATUS", {v.code for v in v_status})

        # 3. 'passed' with non-existent evidence file is rejected
        missing_ev = copy.deepcopy(base)
        missing_ev["criteria"][0]["evidence"] = ["nonexistent/path/does_not_exist.json"]
        v_ev = validate_acceptance_inventory(missing_ev, root=ROOT)
        self.assertIn("UNRESOLVABLE_EVIDENCE", {v.code for v in v_ev})

        # 4. Missing criterion ID is rejected
        incomplete = copy.deepcopy(base)
        incomplete["criteria"] = incomplete["criteria"][:-1]
        v_inc = validate_acceptance_inventory(incomplete, root=ROOT)
        self.assertIn("CRITERIA_MISMATCH", {v.code for v in v_inc})

    def test_blocking_criteria_cannot_be_offset_and_stage_gating_works(self) -> None:
        base = json.loads(ACCEPTANCE_PATH.read_text(encoding="utf-8"))

        # Full acceptance fails while AR-08 and AR-09 are 'not-ready'
        full_ok, full_blockers = evaluate_acceptance(base, root=ROOT, stage="full")
        self.assertFalse(full_ok)
        self.assertTrue(any("AR-08" in b for b in full_blockers))
        self.assertTrue(any("AR-09" in b for b in full_blockers))

        # Repository-shell stage passes because AR-01..AR-07 and AR-10..AR-12 are passed and none failed
        shell_ok, shell_blockers = evaluate_acceptance(base, root=ROOT, stage="repository-shell")
        self.assertTrue(shell_ok, f"Expected repository-shell stage to pass, got: {shell_blockers}")

        # If all 12 criteria have status='passed' and valid evidence, full stage passes
        all_passed = copy.deepcopy(base)
        for row in all_passed["criteria"]:
            row["status"] = "passed"
        all_ok, all_blockers = evaluate_acceptance(all_passed, root=ROOT, stage="full")
        self.assertTrue(all_ok, f"Expected all-passed inventory to pass full stage, got: {all_blockers}")

    def test_cli_acceptance_subcommand_honors_full_and_repository_shell_stages(self) -> None:
        res_full = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.repository",
                "acceptance",
                "--evidence",
                str(ACCEPTANCE_PATH),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_full.returncode, 1)
        self.assertIn("AR-08", res_full.stdout)
        self.assertIn("AR-09", res_full.stdout)

        res_shell = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.repository",
                "acceptance",
                "--evidence",
                str(ACCEPTANCE_PATH),
                "--stage",
                "repository-shell",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_shell.returncode, 0, res_shell.stdout + res_shell.stderr)

    def test_control_register_documents_active_and_deferred_controls(self) -> None:
        reg_path = ROOT / "docs/governance/control-register.md"
        self.assertTrue(reg_path.is_file(), "Expected docs/governance/control-register.md to exist")
        text = reg_path.read_text(encoding="utf-8")
        self.assertIn("Active Controls", text)
        self.assertIn("Deferred Controls", text)
        self.assertIn("Trigger", text)
        self.assertIn("host adapter", text.lower())


if __name__ == "__main__":
    unittest.main()
