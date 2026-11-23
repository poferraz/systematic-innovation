from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

from tools.repository.authority import scan_authority

ALLOWED_CANONICAL_SKILL_FILES = frozenset(
    {
        "skills/systematic-innovation/SKILL.md",
        "skills/systematic-innovation/references/deep-mode.md",
        "skills/systematic-innovation/references/evidence.md",
        "skills/systematic-innovation/references/innovation-lenses.md",
        "skills/systematic-innovation/references/output-contract.md",
    }
)

RESTRICTED_DIR_NAMES = frozenset({"restricted", "private", "sources"})
RESTRICTED_SUFFIXES = (".validation.yaml", ".sealed.yaml")
SYNTHETIC_FIXTURE_PREFIX = ("tests", "repository", "fixtures")
SYNTHETIC_FIXTURE_SENTINEL = "# SYNTHETIC_ISOLATION_FIXTURE"

FALLBACK_IGNORED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".superpowers",
    }
)

NAMED_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b("
    r"OPENAI_API_KEY|ANTHROPIC_API_KEY|GEMINI_API_KEY|GOOGLE_API_KEY|NVIDIA_API_KEY|"
    r"HF_TOKEN|HUGGINGFACE_TOKEN|GITHUB_TOKEN|GH_TOKEN|AWS_SECRET_ACCESS_KEY|"
    r"AWS_SESSION_TOKEN|AZURE_OPENAI_API_KEY|COHERE_API_KEY|MISTRAL_API_KEY|"
    r"PRIVATE_KEY|SECRET_KEY|CLIENT_SECRET|API_SECRET|BEARER_TOKEN"
    r")\s*[:=]\s*[\"']?(?!\[REDACTED\]|<redacted>|REDACTED|\*{3,}|your_[a-z0-9_]+|none\b|null\b|[\"'][\"'])[A-Za-z0-9_\-\./+=]{8,}[\"']?"
)

GENERIC_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api_key|secret_key|client_secret|access_token|auth_token|private_key|password)"
    r"\s*[:=]\s*[\"'](?!\[REDACTED\]|<redacted>|REDACTED|\*{3,}|your_[a-z0-9_]+|none\b|null\b)[A-Za-z0-9_\-\./+=]{12,}[\"']"
)

PEM_PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"
)

TOKEN_PREFIX_RE = re.compile(
    r"\b(?:"
    r"(?P<openai_sk>sk-[A-Za-z0-9]{20,})|"
    r"(?P<github_pat>gh[po]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})|"
    r"(?P<aws_akia>AKIA[0-9A-Z]{16})|"
    r"(?P<google_aiza>AIza[0-9A-Za-z\-_]{24,})"
    r")\b"
)

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class Violation:
    code: str
    path: str
    message: str


def _collect_candidate_paths(root: Path) -> list[Path]:
    """Return tracked relative paths from git ls-files -z, or deterministic walk for non-git fixtures."""
    git_marker = root / ".git"
    if git_marker.exists():
        res = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True,
            check=False,
        )
        if res.returncode == 0:
            raw_entries = [
                entry.decode("utf-8", errors="replace")
                for entry in res.stdout.split(b"\x00")
                if entry
            ]
            return sorted(Path(entry) for entry in raw_entries)

    paths: list[Path] = []
    for candidate in sorted(root.rglob("*")):
        rel = candidate.relative_to(root)
        if any(part in FALLBACK_IGNORED_DIRS for part in rel.parts):
            continue
        if candidate.is_file() or candidate.is_symlink():
            paths.append(rel)
    return paths


def _is_restricted_path(rel: Path) -> bool:
    parts_lower = [part.lower() for part in rel.parts]
    if any(part in RESTRICTED_DIR_NAMES for part in parts_lower[:-1]):
        return True
    name_lower = rel.name.lower()
    if ".restricted." in name_lower:
        return True
    if name_lower.endswith(RESTRICTED_SUFFIXES):
        return True
    if name_lower == "systematic-innovation-session.bundle":
        return True
    return False


def _is_generated_archive(rel: Path) -> bool:
    parts_lower = [part.lower() for part in rel.parts]
    if parts_lower and parts_lower[0] == "dist":
        return True
    if len(parts_lower) >= 2 and parts_lower[0] == "benchmark" and parts_lower[1] == "runs":
        return True
    name_lower = rel.name.lower()
    if name_lower.endswith(".zip") or name_lower.endswith(".bundle"):
        return True
    return False


def _scan_file_for_secrets(file_path: Path, rel_posix: str) -> list[Violation]:
    violations: list[Violation] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return violations

    named_match = NAMED_SECRET_ASSIGNMENT_RE.search(content)
    if named_match:
        key_name = named_match.group(1).upper()
        violations.append(
            Violation(
                code="SECRET_KEY_NAME",
                path=rel_posix,
                message=f"credential assignment detected for key name {key_name} (value redacted)",
            )
        )
        return violations

    generic_match = GENERIC_SECRET_ASSIGNMENT_RE.search(content)
    if generic_match:
        key_name = generic_match.group(1).lower()
        violations.append(
            Violation(
                code="SECRET_KEY_NAME",
                path=rel_posix,
                message=f"credential assignment detected for field '{key_name}' (value redacted)",
            )
        )
        return violations

    if PEM_PRIVATE_KEY_RE.search(content):
        violations.append(
            Violation(
                code="SECRET_KEY_NAME",
                path=rel_posix,
                message="PEM private key header detected (content redacted)",
            )
        )
        return violations

    token_match = TOKEN_PREFIX_RE.search(content)
    if token_match:
        token_kind = token_match.lastgroup or "token_prefix"
        violations.append(
            Violation(
                code="SECRET_KEY_NAME",
                path=rel_posix,
                message=f"credential token pattern '{token_kind}' detected (value redacted)",
            )
        )

    return violations


def _scan_canonical_skill_sources(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    skill_dir = root / "skills/systematic-innovation"
    if not skill_dir.exists():
        return violations

    resolved_skill_dir = skill_dir.resolve()
    for item in sorted(skill_dir.rglob("*")):
        rel_posix = item.relative_to(root).as_posix()
        if item.is_symlink():
            violations.append(
                Violation(
                    code="UNDECLARED_RELEASE_SOURCE",
                    path=rel_posix,
                    message="symlinks are prohibited inside canonical skill directory",
                )
            )
            continue
        if item.is_dir():
            continue
        if rel_posix not in ALLOWED_CANONICAL_SKILL_FILES:
            violations.append(
                Violation(
                    code="UNDECLARED_RELEASE_SOURCE",
                    path=rel_posix,
                    message="file inside skills/systematic-innovation/ is outside the declared canonical release allowlist",
                )
            )
        if item.suffix.lower() == ".md":
            try:
                text = item.read_text(encoding="utf-8")
            except OSError:
                continue
            for raw_target in MARKDOWN_LINK_RE.findall(text):
                target = raw_target.strip().split("#", 1)[0].strip()
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved_target = (item.parent / target).resolve()
                try:
                    resolved_target.relative_to(resolved_skill_dir)
                except ValueError:
                    violations.append(
                        Violation(
                            code="BROKEN_CANONICAL_REFERENCE",
                            path=rel_posix,
                            message=f"canonical skill reference escapes skills/systematic-innovation/: {target}",
                        )
                    )
                    continue
                if not resolved_target.is_file():
                    violations.append(
                        Violation(
                            code="BROKEN_CANONICAL_REFERENCE",
                            path=rel_posix,
                            message=f"broken relative reference inside canonical skill: {target}",
                        )
                    )

    return violations


def scan_public_tree(root: Path) -> list[Violation]:
    """Deterministically validate public-source isolation, secret hygiene, and single authority."""
    root = root.resolve()
    violations: list[Violation] = []

    candidate_paths = _collect_candidate_paths(root)
    for rel in candidate_paths:
        rel_posix = rel.as_posix()
        abs_path = root / rel

        # Synthetic test fixtures under tests/repository/fixtures/ are allowed to carry
        # synthetic restricted filenames ONLY when marked with the explicit sentinel header,
        # and are still scanned for secrets below.
        if rel.parts[:3] == SYNTHETIC_FIXTURE_PREFIX:
            if _is_restricted_path(Path(*rel.parts[3:])):
                try:
                    header = abs_path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    header = ""
                if not header.startswith(SYNTHETIC_FIXTURE_SENTINEL):
                    violations.append(
                        Violation(
                            code="RESTRICTED_PATH",
                            path=rel_posix,
                            message="fixture in tests/repository/fixtures missing synthetic isolation sentinel",
                        )
                    )
            violations.extend(_scan_file_for_secrets(abs_path, rel_posix))
            continue

        if _is_restricted_path(rel):
            violations.append(
                Violation(
                    code="RESTRICTED_PATH",
                    path=rel_posix,
                    message="restricted evaluation path or private pack extension is prohibited in public tree",
                )
            )

        if _is_generated_archive(rel):
            violations.append(
                Violation(
                    code="GENERATED_ARCHIVE",
                    path=rel_posix,
                    message="generated archive or runtime benchmark output is prohibited in tracked public tree",
                )
            )

        if abs_path.is_file() and not abs_path.is_symlink():
            violations.extend(_scan_file_for_secrets(abs_path, rel_posix))

    violations.extend(_scan_canonical_skill_sources(root))

    # Run authority & shadow-source scan when scanning a repository tree
    has_repo_structure = (
        (root / "AGENTS.md").exists()
        or (root / "skills").exists()
        or (root / "docs/specifications").exists()
    )
    if has_repo_structure:
        for err in scan_authority(root):
            code = "SHADOW_AUTHORITY" if "shadow" in err.lower() else "AUTHORITY_VIOLATION"
            violations.append(
                Violation(
                    code=code,
                    path="AGENTS.md",
                    message=err,
                )
            )

    return violations
