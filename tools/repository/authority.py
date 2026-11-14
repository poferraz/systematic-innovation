from __future__ import annotations

from pathlib import Path
import re
import sys

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

IGNORED_DIRS = {".git", ".venv", "dist", "fixtures", ".superpowers", "sources"}

CANONICAL_SIGNATURES = (
    "Quick Mode: 10 to 15",
    "System Dynamics",
    "Human Value",
    "Operational Reality",
    "Boundary Reframing",
    "Mechanism Transfer",
    "never more than seven",
    "10 to 15 distinct possibilities",
    "15 to 24 distinct possibilities",
    "Layer 1: Innovation Brief",
    "Layer 6: User-Directed Continuation",
)

BROADENED_SUPERSEDING_PHRASES = (
    "override conflicting specification",
    "amend the specification",
    "amends the specification",
    "supersede the specification",
    "overrides the behavioral specification",
)

NEGATION_PREFIX_RE = re.compile(
    r"\b(?:never|does not|do not|cannot|must not|nor)\s+[\w\s]{0,25}$",
    re.IGNORECASE,
)


def is_allowlisted_for_behavior(rel: Path) -> bool:
    if rel == Path("CONTEXT.md"):
        return True
    parts = rel.parts
    if parts[0] in {"evals", "tools", "tests"}:
        return True
    if parts[0] == "docs" and len(parts) > 1 and parts[1] in {"superpowers", "research"}:
        return True
    if parts[0] == "skills" and len(parts) > 1 and parts[1] == "systematic-innovation":
        return True
    return False


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
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if rel != CANONICAL_SKILL_REL:
            errors.append(f"shadow behavioral authority outside canonical skill path: {rel.as_posix()}")

    # Content-signature shadow behavioral detection over non-allowlisted markdown files
    for md_file in root.rglob("*.md"):
        rel = md_file.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if is_allowlisted_for_behavior(rel):
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        signature_matches = [sig for sig in CANONICAL_SIGNATURES if sig.lower() in content]
        if len(signature_matches) >= 3:
            errors.append(
                f"shadow behavioral authority detected in non-allowlisted document: {rel.as_posix()} "
                f"({len(signature_matches)} canonical signatures)"
            )

    # Reject plan contractual-supremacy language
    plans_dir = root / "docs/superpowers/plans"
    if plans_dir.is_dir():
        raw_forbidden = "supersede " + "conflicting"
        for plan in sorted(plans_dir.glob("*.md")):
            raw_text = plan.read_text(encoding="utf-8")
            if raw_forbidden in raw_text.lower():
                errors.append(f"plan claims contractual supremacy over specification: {plan.relative_to(root)}")
                continue

            # Check broadened supersession phrases stripping code blocks and respecting negation
            clean_text = re.sub(r"```.*?```", "", raw_text, flags=re.DOTALL)
            clean_text = re.sub(r"`[^`]*`", "", clean_text)
            for phrase in BROADENED_SUPERSEDING_PHRASES:
                for match in re.finditer(re.escape(phrase), clean_text, re.IGNORECASE):
                    start = match.start()
                    prefix = clean_text[max(0, start - 50):start]
                    if not NEGATION_PREFIX_RE.search(prefix):
                        errors.append(
                            f"plan claims contractual supremacy over specification ({phrase}): {plan.relative_to(root)}"
                        )

    return errors


def main(argv: list[str] | None = None) -> int:
    target_root = Path(argv[1]).resolve() if argv and len(argv) > 1 else Path(__file__).resolve().parents[2]
    errors = scan_authority(target_root)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
