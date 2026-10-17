from __future__ import annotations

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


class TriggerManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest_path = ROOT / "evals/triggers/cases.json"

    def test_trigger_manifest_exists_and_is_valid_json(self) -> None:
        self.assertTrue(self.manifest_path.is_file(), "evals/triggers/cases.json is missing")
        data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertIn("cases", data)
        self.assertIsInstance(data["cases"], list)

    def test_trigger_manifest_has_at_least_50_cases_with_unique_ids(self) -> None:
        if not self.manifest_path.is_file():
            self.skipTest("Manifest missing")
        cases = json.loads(self.manifest_path.read_text(encoding="utf-8"))["cases"]
        self.assertGreaterEqual(len(cases), 50, "Expected at least 50 trigger cases")
        ids = [c["id"] for c in cases]
        self.assertEqual(len(ids), len(set(ids)), "Case IDs must be unique")

    def test_trigger_manifest_has_balanced_classes_and_boundary_cases(self) -> None:
        if not self.manifest_path.is_file():
            self.skipTest("Manifest missing")
        cases = json.loads(self.manifest_path.read_text(encoding="utf-8"))["cases"]
        positives = [c for c in cases if c.get("should_trigger") is True]
        negatives = [c for c in cases if c.get("should_trigger") is False]
        boundaries = [c for c in cases if c.get("category") == "boundary"]

        self.assertGreaterEqual(len(positives), 20, "Expected at least 20 should-trigger cases")
        self.assertGreaterEqual(len(negatives), 20, "Expected at least 20 should-not-trigger cases")
        self.assertGreaterEqual(len(boundaries), 10, "Expected at least 10 boundary cases")

    def test_trigger_case_structure(self) -> None:
        if not self.manifest_path.is_file():
            self.skipTest("Manifest missing")
        cases = json.loads(self.manifest_path.read_text(encoding="utf-8"))["cases"]
        required_keys = {"id", "prompt", "category", "should_trigger", "intent_type"}
        for case in cases:
            self.assertTrue(required_keys.issubset(case.keys()), f"Case {case.get('id')} missing keys")
            self.assertIsInstance(case["prompt"], str)
            self.assertGreater(len(case["prompt"].strip()), 10)
            self.assertIn(case["category"], {"positive", "negative", "boundary"})
            self.assertIsInstance(case["should_trigger"], bool)


if __name__ == "__main__":
    unittest.main()
