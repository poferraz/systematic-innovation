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


if __name__ == "__main__":
    unittest.main()
