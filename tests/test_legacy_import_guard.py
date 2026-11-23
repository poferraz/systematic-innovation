from pathlib import Path
import unittest
from unittest.mock import patch

from tools import compile_treatment_results


class LegacyImportGuardTests(unittest.TestCase):
    def test_unverified_historical_import_cannot_write_new_quality_claims(self):
        with patch.object(Path, "open") as file_access:
            with self.assertRaisesRegex(RuntimeError, "historical importer is disabled"):
                compile_treatment_results.main()
            file_access.assert_not_called()
