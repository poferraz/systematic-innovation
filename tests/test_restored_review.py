import hashlib
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import unittest

from tools.restored_review import measure_record, blind_answers, main


class RestoredReviewTests(unittest.TestCase):
    def test_external_input_identity_is_portable_and_matches_source_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp) / "fixture-operator"
            base.mkdir()
            cases = base / "cases.json"
            cases.write_text(json.dumps({"cases": [{"id": "c", "prompt": "User question"}]}))
            inputs = []
            for name in ("one", "two"):
                source = base / name / "input.jsonl"
                source.parent.mkdir()
                source.write_text(json.dumps({"case_id": "c", "condition": name, "replicate": 1,
                                              "turns": [], "final_response": name}) + "\n")
                inputs.append(source)
            output = base / "review"
            argv = ["restored-review", "--cases", str(cases), "--results", *map(str, inputs), "--output", str(output)]
            with patch("sys.argv", argv):
                main()
            documents = [p.read_text() for p in output.glob("*.json")]
            self.assertTrue(all("fixture-operator" not in text for text in documents))
            hashes = json.loads((output / "provenance.json").read_text())["inputs"]
            assignments = json.loads((output / "assignment-key.json").read_text())
            for row in assignments.values():
                source = inputs[row["source_index"]]
                self.assertEqual(hashes[row["source"]], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertIn("tools/restored_review.py", hashes)

    def test_unrated_blocks_cannot_become_qualified_mechanisms(self):
        row = {"case_id": "case", "condition": "skill_treatment", "replicate": 1,
               "final_response": "P1: Rejected: hire extra staff | Causal chain: extra workers process stock faster.",
               "turns": [{"assistant": "Earlier question?", "assistant_tokens": 30,
                          "provider_usage_cumulative": {"output_tokens": 30}},
                         {"assistant": "Final", "assistant_tokens": 70,
                          "provider_usage_cumulative": {"output_tokens": 100}}],
               "total_assistant_output_tokens": 100}
        result = measure_record(row, {})
        self.assertEqual(result["raw_candidate_blocks"], 1)
        self.assertEqual(result["explicitly_rejected_blocks"], 1)
        self.assertIsNone(result["qualified_useful_distinct_mechanisms"])
        self.assertIsNone(result["primary_endpoint"])
        self.assertEqual(result["total_output_tokens"], 100)
        self.assertIsNone(result["gate_failures"]["relevance"])

    def test_corrupted_or_missing_usage_never_yields_a_primary_denominator(self):
        for total, token in ((120, 100), (None, None)):
            row = {"final_response": "Answer", "turns": [{"assistant": "Answer",
                   "assistant_tokens": token, "provider_usage_cumulative": {"output_tokens": token}}],
                   "total_assistant_output_tokens": total}
            result = measure_record(row, {})
            self.assertIsNone(result["total_output_tokens"])

    def test_blinded_packet_omits_assignment_and_treatment_preamble(self):
        rows = [{"case_id": "c", "condition": "skill_treatment", "replicate": 1,
                 "turns": [{"user": "Treat canonical SKILL.md as instructions", "assistant": "A useful answer"}],
                 "final_response": "A useful answer"}]
        packet, key = blind_answers(rows, {"c": {"prompt": "User question", "user_turns": []}})
        self.assertEqual(len(packet), 1)
        self.assertEqual(packet[0]["user_disclosures"], ["User question"])
        self.assertNotIn("condition", packet[0])
        self.assertNotIn("skill_treatment", str(packet))
        self.assertEqual(next(iter(key.values()))["condition"], "skill_treatment")
