from pathlib import Path
import tempfile
import unittest

from tools.validate_skill import parse_frontmatter, validate_skill


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "systematic-innovation"
REQUIRED_REFERENCES = (
    "innovation-lenses.md",
    "deep-mode.md",
    "output-contract.md",
    "evidence.md",
)


def _create_valid_temp_skill(base: Path) -> Path:
    skill = base / "systematic-innovation"
    refs = skill / "references"
    refs.mkdir(parents=True, exist_ok=True)
    for ref in REQUIRED_REFERENCES:
        (refs / ref).write_text(f"# {ref}\n\nPortable reference content.\n", encoding="utf-8")
    links = "\n".join(f"- [{ref}](references/{ref})" for ref in REQUIRED_REFERENCES)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: systematic-innovation\n"
        "description: Use when the user needs non-obvious, causally distinct innovation possibilities.\n"
        "---\n\n"
        "# Systematic Innovation\n\n"
        f"{links}\n",
        encoding="utf-8",
    )
    return skill


class SkillValidatorStructureUnitTests(unittest.TestCase):
    def test_valid_temp_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = _create_valid_temp_skill(Path(tmp))
            self.assertEqual(validate_skill(skill), [])

    def test_rejects_invalid_frontmatter_and_missing_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = _create_valid_temp_skill(Path(tmp))
            (skill / "SKILL.md").write_text(
                "---\nname: Invalid_Name\ndescription: \"\"\n---\n",
                encoding="utf-8",
            )
            (skill / "references" / "evidence.md").unlink()
            errors = validate_skill(skill)
            self.assertIn("invalid skill name", errors)
            self.assertIn("invalid description", errors)
            self.assertTrue(any("evidence.md" in err for err in errors))


class CanonicalSkillStructureTests(unittest.TestCase):
    def test_canonical_skill_package_structure(self) -> None:
        self.assertTrue((SKILL_DIR / "SKILL.md").is_file(), "skills/systematic-innovation/SKILL.md is missing")
        errors = validate_skill(SKILL_DIR)
        self.assertEqual(errors, [])
        fields = parse_frontmatter((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual(fields.get("name"), "systematic-innovation")
        self.assertLessEqual(len(fields.get("name", "")), 64)
        self.assertTrue(0 < len(fields.get("description", "")) <= 1024)
        ref_files = sorted(p.name for p in (SKILL_DIR / "references").glob("*.md"))
        self.assertEqual(ref_files, sorted(REQUIRED_REFERENCES))

    def test_skill_frontmatter_meets_v2_metadata_and_concise_trigger_contract(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        fields = parse_frontmatter(text)
        self.assertTrue(fields.get("version"), "SKILL.md frontmatter must declare version")
        self.assertEqual(fields.get("license"), "MIT")
        desc = fields.get("description", "")
        self.assertGreaterEqual(len(desc), 50)
        self.assertLessEqual(len(desc), 150, f"Description too long ({len(desc)} > 150)")
        frontmatter_block = text.split("---\n", 2)[1]
        self.assertIn("metadata:", frontmatter_block)
        self.assertIn("author:", frontmatter_block)
        self.assertIn("tags:", frontmatter_block)


if __name__ == "__main__":
    unittest.main()
