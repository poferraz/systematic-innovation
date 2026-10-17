from pathlib import Path
import os
import re
import sys


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PROVIDER_RE = re.compile(r"\b(?:claude|codex|cursor|antigravity|pi)\b", re.IGNORECASE)
REQUIRED_REFERENCES = (
    "innovation-lenses.md",
    "deep-mode.md",
    "output-contract.md",
    "evidence.md",
)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}
    block = parts[1]
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def _validate_links(md_file: Path, skill_root: Path, errors: list[str]) -> None:
    text = md_file.read_text(encoding="utf-8")
    for match in LINK_RE.finditer(text):
        raw_target = match.group(1).strip().split("#", 1)[0].strip()
        if not raw_target or raw_target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (md_file.parent / raw_target).resolve()
        try:
            resolved.relative_to(skill_root)
        except ValueError:
            errors.append(f"link escapes skill directory: {raw_target}")
            continue
        if not resolved.is_file():
            errors.append(f"unresolved reference link: {raw_target}")


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    skill_root = path.resolve()
    skill_md = skill_root / "SKILL.md"
    if not skill_md.is_file():
        return ["SKILL.md is missing"]

    text = skill_md.read_text(encoding="utf-8")
    fields = parse_frontmatter(text)
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append("invalid skill name")
    if not description or len(description) > 1024:
        errors.append("invalid description")

    refs_dir = skill_root / "references"
    for ref_name in REQUIRED_REFERENCES:
        if not (refs_dir / ref_name).is_file():
            errors.append(f"missing required reference: {ref_name}")

    for file_path in sorted(skill_root.rglob("*")):
        if file_path.is_dir():
            continue
        if file_path.suffix != ".md" or os.access(file_path, os.X_OK):
            errors.append(f"executable or non-markdown file: {file_path.name}")
            continue
        _validate_links(file_path, skill_root, errors)
        if file_path.name != "evidence.md":
            content = file_path.read_text(encoding="utf-8")
            if PROVIDER_RE.search(content):
                errors.append(f"provider-specific instruction in {file_path.name}")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: validate_skill.py <skill-path>")
        return 1
    errors = validate_skill(Path(argv[1]))
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
