from pathlib import Path
import sys
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ToolchainTests(unittest.TestCase):
    def test_python_version_pin_exists_and_matches_3_13(self) -> None:
        pin_file = ROOT / ".python-version"
        self.assertTrue(pin_file.is_file(), "Expected .python-version at repository root")
        self.assertEqual(pin_file.read_text(encoding="utf-8").strip(), "3.13")

    def test_root_pyproject_declares_supported_python_range_and_stdlib_core(self) -> None:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["requires-python"], ">=3.11,<3.15")
        self.assertEqual(data["project"]["dependencies"], [])

    def test_runtime_python_meets_minimum_floor(self) -> None:
        self.assertGreaterEqual(sys.version_info[:2], (3, 11))


if __name__ == "__main__":
    unittest.main()
