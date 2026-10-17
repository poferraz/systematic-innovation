from pathlib import Path
import tempfile
import unittest

from tools.validate_skill import validate_skill
from tests.test_skill_structure import REQUIRED_REFERENCES, SKILL_DIR, _create_valid_temp_skill


class SkillReferenceValidatorUnitTests(unittest.TestCase):
    def test_rejects_broken_and_escaping_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = _create_valid_temp_skill(Path(tmp))
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            (skill / "SKILL.md").write_text(
                text + "\n- [missing](references/missing.md)\n- [escape](../CONTEXT.md)\n",
                encoding="utf-8",
            )
            errors = validate_skill(skill)
            self.assertTrue(any("missing.md" in err for err in errors))
            self.assertTrue(any("escapes skill directory" in err for err in errors))


class CanonicalSkillReferenceTests(unittest.TestCase):
    def test_canonical_skill_references_resolve(self) -> None:
        self.assertTrue((SKILL_DIR / "SKILL.md").is_file(), "skills/systematic-innovation/SKILL.md is missing")
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        for ref in REQUIRED_REFERENCES:
            self.assertIn(f"references/{ref}", text, f"SKILL.md must link to references/{ref}")
            self.assertTrue((SKILL_DIR / "references" / ref).is_file(), f"Missing reference {ref}")
        self.assertEqual(validate_skill(SKILL_DIR), [])


if __name__ == "__main__":
    unittest.main()
