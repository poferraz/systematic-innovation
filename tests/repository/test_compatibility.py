import copy
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from typing import Any

from tools.repository.compatibility import (
    ALLOWED_DIMENSION_STATES,
    DIMENSIONS,
    ClaimResult,
    effective_dimension_states,
    evaluate_claim,
    validate_host_record,
)

ROOT = Path(__file__).resolve().parents[2]


def _make_valid_record(
    *,
    agent_family: str = "family-alpha",
    host: str = "alpha-cli",
    host_version: str = "1.2.0",
    model_family: str = "alpha-model-v1",
    tested_at: str = "2026-11-01",
    review_after: str = "2026-12-31",
    format_conformance: str = "passed",
    installation: str = "passed",
    discovery: str = "passed",
    explicit_activation: str = "passed",
    automatic_activation: str = "not-claimed",
    behavioral_conformance: str = "passed",
    claim_profiles: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "agent_family": agent_family,
        "host": host,
        "host_version": host_version,
        "model_family": model_family,
        "skill_revision": "a" * 40,
        "artifact_digest": "b" * 64,
        "format_version": "1.0",
        "format_conformance": format_conformance,
        "installation": installation,
        "discovery": discovery,
        "explicit_activation": explicit_activation,
        "automatic_activation": automatic_activation,
        "behavioral_conformance": behavioral_conformance,
        "installation_procedure": "Copy skills/systematic-innovation into host skills directory",
        "invocation_mode": "explicit",
        "test_scenario": "Controlled single-turn and multi-turn conformance suite",
        "tested_at": tested_at,
        "review_after": review_after,
        "run_ids": [f"run-{agent_family}-001"],
        "claim_profiles": claim_profiles if claim_profiles is not None else ["explicit-invocation", "broad-cross-agent"],
        "limitations": ["Automatic discovery not claimed on this host."],
    }


class CompatibilityTests(unittest.TestCase):
    def test_all_six_dimensions_and_every_allowed_state_are_accepted(self) -> None:
        self.assertEqual(
            DIMENSIONS,
            (
                "format_conformance",
                "installation",
                "discovery",
                "explicit_activation",
                "automatic_activation",
                "behavioral_conformance",
            ),
        )
        for dim in DIMENSIONS:
            for state in ALLOWED_DIMENSION_STATES[dim]:
                rec = _make_valid_record()
                rec[dim] = state
                violations = validate_host_record(rec, as_of=date(2026, 11, 14))
                self.assertEqual(
                    violations,
                    [],
                    f"Expected {dim}={state!r} to be valid, got: {violations}",
                )

    def test_not_claimed_is_legal_only_for_automatic_activation(self) -> None:
        for dim in DIMENSIONS:
            rec = _make_valid_record()
            rec[dim] = "not-claimed"
            violations = validate_host_record(rec, as_of=date(2026, 11, 14))
            if dim == "automatic_activation":
                self.assertEqual(violations, [])
            else:
                codes = {v.code for v in violations}
                self.assertIn(
                    "INVALID_DIMENSION_STATE",
                    codes,
                    f"Expected INVALID_DIMENSION_STATE when {dim}='not-claimed'",
                )

    def test_installation_does_not_imply_discovery_and_explicit_does_not_imply_automatic(self) -> None:
        rec = _make_valid_record(
            installation="passed",
            discovery="not-assessed",
            explicit_activation="passed",
            automatic_activation="not-assessed",
            behavioral_conformance="passed",
        )
        original = copy.deepcopy(rec)
        states = effective_dimension_states(rec, as_of=date(2026, 11, 14))
        self.assertEqual(rec, original, "Evaluation must never mutate input records")
        self.assertEqual(states["installation"], "passed")
        self.assertEqual(states["discovery"], "not-assessed")
        self.assertEqual(states["explicit_activation"], "passed")
        self.assertEqual(states["automatic_activation"], "not-assessed")

        # Evaluating a profile that requires discovery=passed must fail even though installation=passed
        disc_result = evaluate_claim("discovered-explicit", [rec], as_of=date(2026, 11, 14))
        self.assertIsInstance(disc_result, ClaimResult)
        self.assertFalse(disc_result.passed)

        # Evaluating a profile that requires automatic_activation=passed must fail even though explicit_activation=passed
        auto_result = evaluate_claim("automatic-invocation", [rec], as_of=date(2026, 11, 14))
        self.assertFalse(auto_result.passed)

    def test_overdue_evidence_becomes_stale_and_fails_claims(self) -> None:
        rec = _make_valid_record(
            tested_at="2026-09-01",
            review_after="2026-10-15",
            installation="passed",
            explicit_activation="passed",
            behavioral_conformance="passed",
        )
        states_before = effective_dimension_states(rec, as_of="2026-10-15")
        self.assertEqual(states_before["behavioral_conformance"], "passed")

        states_after = effective_dimension_states(rec, as_of="2026-10-16")
        self.assertEqual(states_after["behavioral_conformance"], "stale")
        self.assertEqual(states_after["installation"], "stale")
        self.assertEqual(states_after["explicit_activation"], "stale")
        self.assertEqual(states_after["automatic_activation"], "not-claimed")

        claim_after = evaluate_claim("explicit-invocation", [rec], as_of="2026-10-16")
        self.assertFalse(claim_after.passed)
        self.assertTrue(any(v.code == "STALE_EVIDENCE" for v in claim_after.violations))

    def test_broad_claim_requires_three_distinct_families_with_behavioral_conformance_passed(self) -> None:
        r1 = _make_valid_record(agent_family="family-alpha", host="alpha-cli")
        r2 = _make_valid_record(agent_family="family-beta", host="beta-cli")
        r3_dup = _make_valid_record(agent_family="family-beta", host="beta-ide")

        # Only 2 distinct families -> must fail broad-cross-agent
        res_two = evaluate_claim("broad-cross-agent", [r1, r2, r3_dup], as_of="2026-11-14")
        self.assertFalse(res_two.passed)
        self.assertEqual(res_two.qualifying_families, ("family-alpha", "family-beta"))

        # Third distinct family with behavioral_conformance='not-assessed' -> still fails
        r3_unassessed = _make_valid_record(
            agent_family="family-gamma",
            host="gamma-cli",
            behavioral_conformance="not-assessed",
        )
        res_unassessed = evaluate_claim("broad-cross-agent", [r1, r2, r3_unassessed], as_of="2026-11-14")
        self.assertFalse(res_unassessed.passed)

        # Third distinct family with behavioral_conformance='passed' -> passes!
        r3_passed = _make_valid_record(
            agent_family="family-gamma",
            host="gamma-cli",
            behavioral_conformance="passed",
        )
        res_three = evaluate_claim("broad-cross-agent", [r1, r2, r3_passed], as_of="2026-11-14")
        self.assertTrue(res_three.passed, f"Expected broad claim to pass, got: {res_three.violations}")
        self.assertEqual(res_three.qualifying_families, ("family-alpha", "family-beta", "family-gamma"))

    def test_unsupported_adapter_is_rejected_without_complete_host_delta_evidence(self) -> None:
        rec = _make_valid_record()
        rec["adapter_used"] = True
        violations = validate_host_record(rec, as_of="2026-11-14")
        self.assertIn("UNSUPPORTED_ADAPTER", {v.code for v in violations})

        rec["adapter_evidence"] = {
            "host": "alpha-cli",
            "host_version": "1.2.0",
            "demonstrated_incompatibility": "Host requires YAML manifest wrapper in .host-plugin/",
            "why_docs_insufficient": "Host loader ignores bare SKILL.md without wrapper file",
            "minimal_translation": "Single metadata pointer file to canonical SKILL.md",
            "preservation_test": "tests/repository/test_authority.py",
        }
        violations_with_evidence = validate_host_record(rec, as_of="2026-11-14")
        self.assertEqual(violations_with_evidence, [])

    def test_automatic_activation_and_behavioral_thresholds_are_enforced_when_present(self) -> None:
        rec = _make_valid_record(
            automatic_activation="passed",
            claim_profiles=["automatic-invocation"],
        )
        rec["automatic_activation_metrics"] = {"precision": 0.85, "recall": 0.80}
        violations = validate_host_record(rec, as_of="2026-11-14")
        self.assertIn("THRESHOLD_FAILED", {v.code for v in violations})

        rec["automatic_activation_metrics"] = {"precision": 0.92, "recall": 0.88}
        self.assertEqual(validate_host_record(rec, as_of="2026-11-14"), [])

    def test_verify_compatibility_cli_subcommand_accepts_valid_matrix_and_rejects_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            valid_matrix = tmp_path / "integration-matrix.yaml"
            records = [
                _make_valid_record(agent_family="family-alpha", host="alpha-cli"),
                _make_valid_record(agent_family="family-beta", host="beta-cli"),
                _make_valid_record(agent_family="family-gamma", host="gamma-cli"),
            ]
            # Write JSON-compatible YAML
            valid_matrix.write_text(json.dumps({"records": records}, indent=2) + "\n", encoding="utf-8")

            res_ok = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.repository",
                    "verify-compatibility",
                    str(valid_matrix),
                    "--profile",
                    "broad-cross-agent",
                    "--as-of",
                    "2026-11-14",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_ok.returncode, 0, res_ok.stdout + res_ok.stderr)

            # Now test with only 2 families -> must fail broad-cross-agent
            insufficient_matrix = tmp_path / "insufficient-matrix.yaml"
            insufficient_matrix.write_text(json.dumps({"records": records[:2]}, indent=2) + "\n", encoding="utf-8")
            res_bad = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.repository",
                    "verify-compatibility",
                    str(insufficient_matrix),
                    "--profile",
                    "broad-cross-agent",
                    "--as-of",
                    "2026-11-14",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res_bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
