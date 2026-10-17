from __future__ import annotations

from pathlib import Path
import re

REQUIRED_LINKS = (
    "CONTEXT.md",
    "docs/superpowers/specs/2026-08-31-systematic-innovation-design.md",
    "docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md",
    "docs/superpowers/plans/2026-09-01-systematic-innovation-coordinated-implementation.md",
    "docs/superpowers/plans/2026-08-31-systematic-innovation-skill.md",
    "docs/superpowers/plans/2026-08-31-systematic-innovation-benchmark-runner.md",
    "docs/superpowers/plans/2026-08-31-systematic-innovation-benchmark-study.md",
)

CANONICAL_SKILL_PATH = "skills/systematic-innovation/"
CANONICAL_SKILL_REL = Path("skills/systematic-innovation/SKILL.md")
SKILL_PATH_RE = re.compile(r"\bskills/[a-z0-9-]+/?")


def scan_authority(root: Path) -> list[str]:
    """Validate single behavioral authority, root routing links, and plan subordination."""
    errors: list[str] = []
    agents_file = root / "AGENTS.md"
    if not agents_file.is_file():
        return ["missing AGENTS.md at repository root"]

    agents_text = agents_file.read_text(encoding="utf-8")

    for rel_path in REQUIRED_LINKS:
        if rel_path not in agents_text:
            errors.append(f"AGENTS.md missing required routing link: {rel_path}")
        if not (root / rel_path).is_file():
            errors.append(f"authoritative document missing on disk: {rel_path}")

    declared_skill_paths = {match.rstrip("/") + "/" for match in SKILL_PATH_RE.findall(agents_text)}
    if declared_skill_paths != {CANONICAL_SKILL_PATH}:
        errors.append(
            f"AGENTS.md must declare exactly one canonical skill path ({CANONICAL_SKILL_PATH}); "
            f"found {sorted(declared_skill_paths)}"
        )

    for boundary_term in ("dist/", "restricted", "host"):
        if boundary_term not in agents_text.lower():
            errors.append(f"AGENTS.md missing required boundary declaration for '{boundary_term}'")

    # Reject shadow SKILL.md copies outside skills/systematic-innovation/SKILL.md
    for candidate in root.rglob("SKILL.md"):
        rel = candidate.relative_to(root)
        if any(part in {".git", ".venv", "dist", "fixtures"} for part in rel.parts):
            continue
        if rel != CANONICAL_SKILL_REL:
            errors.append(f"shadow behavioral authority outside canonical skill path: {rel.as_posix()}")

    # Reject plan contractual-supremacy language
    plans_dir = root / "docs/superpowers/plans"
    if plans_dir.is_dir():
        forbidden = "supersede " + "conflicting"
        for plan in sorted(plans_dir.glob("*.md")):
            text = plan.read_text(encoding="utf-8").lower()
            if forbidden in text:
                errors.append(f"plan claims contractual supremacy over specification: {plan.relative_to(root)}")

    return errors
