from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import compile_treatment_results


class LegacyImportGuardTests(unittest.TestCase):
    def test_unverified_historical_import_cannot_write_new_quality_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / "cases.json"
            cases.write_text('{"cases": []}')
            output = root / "treatment.jsonl"
            output.write_text("retained historical evidence\n")
            with patch.object(compile_treatment_results, "CASES_PATH", cases), \
                 patch.object(compile_treatment_results, "OUTPUT_PATH", output), \
                 patch.object(compile_treatment_results, "CONVERSATIONS", []):
                with self.assertRaisesRegex(RuntimeError, "historical importer is disabled"):
                    compile_treatment_results.main()
            self.assertEqual(output.read_text(), "retained historical evidence\n")
