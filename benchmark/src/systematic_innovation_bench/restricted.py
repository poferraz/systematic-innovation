"""Validate operator-owned packs without emitting their contents or absolute paths."""
from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Literal, Self

import yaml
from pydantic import Field, ValidationError, model_validator

from .models import BenchmarkCase, InteractionMode, StrictModel

ALLOCATION = {
    "synthetic-mechanism": 5, "counterfactual-rediscovery": 3,
    "open-ended-systemic": 6, "preservation-no-change": 2,
    "trigger-scope": 2, "adversarial-high-stakes": 2,
}
FILES = ("scoring.yaml", "test.yaml", "validation.yaml")


class PackValidationError(ValueError):
    """A content-free failure at the restricted boundary."""


class RestrictedCase(BenchmarkCase):
    expected_mode: Literal["quick", "deep"]
    hidden_mechanisms: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def private_contract(self) -> Self:
        if self.split not in ("validation", "test"):
            raise ValueError("restricted split required")
        if self.expected_mode == "deep":
            if (self.interaction_mode is not InteractionMode.CONTROLLED_MULTI_TURN
                    or self.conversation_script is None
                    or len(self.conversation_script.user_turns) != 2):
                raise ValueError("fixed two-disclosure protocol required")
        elif self.interaction_mode is not InteractionMode.SINGLE_TURN:
            raise ValueError("quick protocol must be single turn")
        if self.should_trigger is False and self.interaction_mode is not InteractionMode.SINGLE_TURN:
            raise ValueError("negative trigger protocol must be single turn")
        return self


class ReviewerApproval(StrictModel):
    reviewer: str = Field(min_length=1)
    approved: Literal[True]


class ProtectedScoring(StrictModel):
    case_id: str = Field(min_length=1)
    gold_mechanisms: tuple[str, ...] = Field(min_length=1)
    acceptable_functional_equivalents: tuple[str, ...] = Field(min_length=1)
    unsafe_outputs: tuple[str, ...] = Field(min_length=1)
    deterministic_checks: tuple[str, ...] = Field(min_length=1)
    provenance_notes: str = Field(min_length=1)
    reviewer_approvals: tuple[ReviewerApproval, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def independent_approvals(self) -> Self:
        if len({item.reviewer for item in self.reviewer_approvals}) < 2:
            raise ValueError("independent reviewer approvals required")
        return self


class RestrictedCasesFile(StrictModel):
    cases: tuple[RestrictedCase, ...] = Field(min_length=20, max_length=20)


class RestrictedScoringFile(StrictModel):
    schema_version: Literal["1.0"]
    cases: tuple[ProtectedScoring, ...] = Field(min_length=40, max_length=40)


class RestrictedPack(StrictModel):
    validation: RestrictedCasesFile
    test: RestrictedCasesFile
    scoring: RestrictedScoringFile


class RestrictedPackSummary(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    status: Literal["passed"] = "passed"
    validation_count: int
    test_count: int
    family_counts: dict[str, int]
    digests: dict[str, str]
    digest: str


def validate_restricted_pack(
    path: Path, *, public_root: Path | None = None,
) -> RestrictedPackSummary:
    """Read only the three declared files; return counts and byte digests.

    Public-root override supports an operator's reviewed checkout. It may only
    make the boundary stricter: the package's own source worktree is also denied.
    Validation errors intentionally omit Pydantic/YAML exceptions, which may
    contain values from protected documents.
    """
    source_root = Path(__file__).resolve().parents[3]
    boundaries = [source_root.resolve()]
    if public_root is not None:
        boundaries.append(public_root.resolve())
    if not path.is_absolute():
        raise PackValidationError("PACK_PATH_NOT_ABSOLUTE")
    resolved = path.resolve()
    if any(resolved.is_relative_to(root) for root in boundaries):
        raise PackValidationError("PACK_INSIDE_PUBLIC_WORKTREE")
    if not resolved.is_dir():
        raise PackValidationError("PACK_DIRECTORY_REQUIRED")
    if any((ancestor / ".git").exists() or (ancestor / ".git").is_symlink()
           for ancestor in (resolved, *resolved.parents)):
        raise PackValidationError("PACK_INSIDE_GIT_WORKTREE")
    try:
        if {entry.name for entry in resolved.iterdir()} != set(FILES):
            raise PackValidationError("PACK_UNDECLARED_ENTRY")
    except OSError:
        raise PackValidationError("PACK_DIRECTORY_UNREADABLE") from None
    digests: dict[str, str] = {}
    contents: dict[str, object] = {}
    combined = hashlib.sha256()
    for filename in FILES:
        candidate = resolved / filename
        if candidate.is_symlink() or not candidate.is_file():
            raise PackValidationError("PACK_REGULAR_FILE_REQUIRED")
        try:
            if candidate.stat().st_size > 16 * 1024 * 1024:
                raise PackValidationError("PACK_FILE_LIMIT")
            data = candidate.read_bytes()
            payload = yaml.safe_load(data)
        except (OSError, UnicodeError, yaml.YAMLError):
            raise PackValidationError("PACK_PARSE_FAILED") from None
        digests[filename] = hashlib.sha256(data).hexdigest()
        combined.update(filename.encode() + b"\0" + len(data).to_bytes(8, "big") + data)
        contents[filename.removesuffix(".yaml")] = payload
    try:
        pack = RestrictedPack.model_validate(contents)
    except (ValidationError, TypeError, ValueError):
        raise PackValidationError("PACK_SCHEMA_FAILED") from None
    cases = (*pack.validation.cases, *pack.test.cases)
    for split, split_cases in (("validation", pack.validation.cases), ("test", pack.test.cases)):
        if any(case.split != split for case in split_cases):
            raise PackValidationError("PACK_SPLIT_MISMATCH")
        if Counter(case.family for case in split_cases) != ALLOCATION:
            raise PackValidationError("PACK_ALLOCATION_MISMATCH")
    ids = [case.id for case in cases]
    scoring_ids = [item.case_id for item in pack.scoring.cases]
    if len(set(ids)) != 40 or len(set(scoring_ids)) != 40 or set(ids) != set(scoring_ids):
        raise PackValidationError("PACK_CASE_CORRELATION_FAILED")
    scoring_by_id = {item.case_id: item for item in pack.scoring.cases}
    if any(set(case.hidden_mechanisms) != set(scoring_by_id[case.id].gold_mechanisms)
           for case in cases):
        raise PackValidationError("PACK_GOLD_MISMATCH")
    return RestrictedPackSummary(
        validation_count=20, test_count=20,
        family_counts=dict(Counter(case.family for case in cases)),
        digests=digests, digest=combined.hexdigest(),
    )
