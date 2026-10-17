import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PilotManifestTests(unittest.TestCase):
    def test_pilot_has_twelve_unique_cross_domain_cases(self) -> None:
        path = ROOT / "evals/pilot/cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        self.assertEqual(len(cases), 12)
        self.assertEqual(len({case["id"] for case in cases}), 12)
        self.assertGreaterEqual(len({case["domain"] for case in cases}), 7)
        self.assertTrue(any(case["expected_mode"] == "quick" for case in cases))
        self.assertTrue(any(case["expected_mode"] == "deep" for case in cases))
        self.assertTrue(any(not case["should_trigger"] for case in cases))

    def test_every_case_declares_observable_failure_targets(self) -> None:
        path = ROOT / "evals/pilot/cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        for case in cases:
            self.assertTrue(case["prompt"].strip(), case["id"])
            self.assertGreaterEqual(len(case["target_failures"]), 2, case["id"])

    def test_deep_cases_have_controlled_multi_turn_scripts(self) -> None:
        path = ROOT / "evals/pilot/cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        for case in cases:
            if case["expected_mode"] == "deep":
                self.assertEqual(case["interaction_mode"], "controlled-multi-turn")
                self.assertEqual(len(case["user_turns"]), 2)
                self.assertIn("Produce your final portfolio", case["user_turns"][-1])
            else:
                self.assertEqual(case["interaction_mode"], "single-turn")
                self.assertEqual(case["user_turns"], [])

    def test_baseline_results_cover_all_cases(self) -> None:
        cases_path = ROOT / "evals/pilot/cases.json"
        results_path = ROOT / "evals/pilot/results/baseline.jsonl"
        self.assertTrue(results_path.is_file(), "evals/pilot/results/baseline.jsonl is missing")
        cases = json.loads(cases_path.read_text(encoding="utf-8"))["cases"]
        records = [
            json.loads(line)
            for line in results_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        required_keys = {
            "case_id",
            "condition",
            "replicate",
            "host",
            "model",
            "interaction_mode",
            "turns",
            "final_response",
            "total_assistant_output_tokens",
            "ratings",
            "notes",
        }
        for record in records:
            self.assertTrue(required_keys.issubset(record.keys()), record.get("case_id"))

        for case in cases:
            vanilla_records = [
                r
                for r in records
                if r["case_id"] == case["id"] and r["condition"] == "vanilla"
            ]
            if case["should_trigger"]:
                self.assertEqual(
                    len(vanilla_records),
                    2,
                    f"Expected 2 vanilla baseline records for positive case {case['id']}",
                )
                self.assertEqual({r["replicate"] for r in vanilla_records}, {1, 2})
            else:
                self.assertEqual(
                    len(vanilla_records),
                    1,
                    f"Expected 1 vanilla baseline observation for negative case {case['id']}",
                )

    def test_treatment_results_cover_all_cases(self) -> None:
        cases_path = ROOT / "evals/pilot/cases.json"
        results_path = ROOT / "evals/pilot/results/treatment.jsonl"
        self.assertTrue(results_path.is_file(), "evals/pilot/results/treatment.jsonl is missing")
        cases = json.loads(cases_path.read_text(encoding="utf-8"))["cases"]
        records = [
            json.loads(line)
            for line in results_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        required_keys = {
            "case_id",
            "condition",
            "replicate",
            "host",
            "model",
            "interaction_mode",
            "turns",
            "final_response",
            "total_assistant_output_tokens",
            "ratings",
            "notes",
        }
        for record in records:
            self.assertTrue(required_keys.issubset(record.keys()), record.get("case_id"))

        for case in cases:
            treatment_records = [
                r
                for r in records
                if r["case_id"] == case["id"] and r["condition"] == "treatment"
            ]
            if case["should_trigger"]:
                self.assertEqual(
                    len(treatment_records),
                    2,
                    f"Expected 2 treatment records for positive case {case['id']}",
                )
                self.assertEqual({r["replicate"] for r in treatment_records}, {1, 2})
            else:
                self.assertEqual(
                    len(treatment_records),
                    1,
                    f"Expected 1 treatment observation for negative case {case['id']}",
                )


if __name__ == "__main__":
    unittest.main()


