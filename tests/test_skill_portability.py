from pathlib import Path
import os
import tempfile
import unittest

from tools.validate_skill import validate_skill
from tests.test_skill_structure import SKILL_DIR, _create_valid_temp_skill


class SkillPortabilityUnitTests(unittest.TestCase):
    def test_rejects_executable_files_and_provider_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = _create_valid_temp_skill(Path(tmp))
            script = skill / "helper.sh"
            script.write_text("#!/bin/sh\necho hi\n", encoding="utf-8")
            os.chmod(script, 0o755)
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            (skill / "SKILL.md").write_text(
                text + "\nRun `claude` or `codex` or `antigravity` to execute this skill.\n",
                encoding="utf-8",
            )
            errors = validate_skill(skill)
            self.assertTrue(any("executable or non-markdown" in err for err in errors))
            self.assertTrue(any("provider-specific" in err for err in errors))


class CanonicalSkillPortabilityTests(unittest.TestCase):
    def test_canonical_skill_is_portable_and_markdown_only(self) -> None:
        self.assertTrue(SKILL_DIR.is_dir(), "skills/systematic-innovation directory is missing")
        errors = validate_skill(SKILL_DIR)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
