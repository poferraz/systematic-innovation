import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StressManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = json.loads(
            (ROOT / "evals/stress/cases.json").read_text(encoding="utf-8")
        )["cases"]

    def test_corpus_covers_required_adversarial_topologies(self) -> None:
        by_topology = {case["topology"]: case for case in self.cases}
        self.assertEqual(len(self.cases), 12)
        self.assertEqual(len({case["id"] for case in self.cases}), 12)
        required = {
            "macgyver_overconstrained",
            "macgyver_recombination",
            "research_ideation_exhaustion",
            "wharton_homogenization",
            "triz_contradiction",
            "ambiguous_mode",
            "regulatory_bypass",
            "deep_multiturn_drift",
            "token_ceiling",
        }
        self.assertEqual(set(by_topology), required)

    def test_cases_declare_research_provenance_and_replicates(self) -> None:
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["prompt"].strip())
                self.assertGreaterEqual(case["replicates"], 3)
                self.assertTrue(case["primary_source"].startswith("https://"))
                self.assertGreaterEqual(len(case["target_failures"]), 3)

    def test_interaction_modes_match_stress_topology(self) -> None:
        by_id = {case["id"]: case for case in self.cases}
        multi = [
            "macgyver-overconstrained",
            "triz-thermal-contradiction",
            "deep-preserve-ledger-drift",
        ]
        for case_id in multi:
            case = by_id[case_id]
            self.assertEqual(case["interaction_mode"], "controlled-multi-turn")
            self.assertEqual(len(case["user_turns"]), 3)
            self.assertIn("Produce your final portfolio", case["user_turns"][-1])
        for case in self.cases:
            if case["id"] not in multi:
                self.assertEqual(case["interaction_mode"], "single-turn")
                self.assertEqual(case["user_turns"], [])

    def test_safety_and_impossible_constraint_cases_declare_expected_boundaries(self) -> None:
        by_id = {case["id"]: case for case in self.cases}
        self.assertFalse(by_id["macgyver-overconstrained"]["must_be_solvable"])
        safety_cases = [case for case in self.cases if case["topology"] == "regulatory_bypass"]
        self.assertEqual({case["id"] for case in safety_cases}, {"gdpr-audit-bypass", "fda-audit-bypass"})
        self.assertTrue(all(case["must_refuse_bypass"] for case in safety_cases))
        for case in self.cases:
            self.assertIn("preserve", case)
            self.assertIsInstance(case["preserve"], list)
            self.assertTrue(case["preserve"])
        self.assertEqual(by_id["token-ceiling-portfolio"]["word_limit"], 350)

    def test_high_replicate_cases_require_five_runs(self) -> None:
        by_id = {case["id"]: case for case in self.cases}
        self.assertGreaterEqual(by_id["startup-homogenization"]["replicates"], 5)
        self.assertGreaterEqual(by_id["research-idea-exhaustion"]["replicates"], 5)


if __name__ == "__main__":
    unittest.main()
