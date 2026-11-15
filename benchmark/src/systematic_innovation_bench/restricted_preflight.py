"""Content-free authorization checks before restricted execution.

This module verifies local executable inputs and operator-attested custody controls.
It neither launches an adapter nor reads pack records: pack bytes are hashed only.
Detailed declarations belong in controlled operator storage, outside public Git.
"""
from __future__ import annotations

import hashlib
import json
import re
import stat
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import urlsplit

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

Digest = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
Revision = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
LogicalId = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:/@+-]{0,127}$")]
Stage = Literal["validation", "sealed-test"]


class PreflightError(ValueError):
    """A structural rule code, never an input value or exception representation."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class ExecutionIdentity(_StrictModel):
    provider: LogicalId
    model: LogicalId
    account: LogicalId
    adapter: LogicalId
    invocation: tuple[str, ...] = Field(min_length=1)


class ProviderPolicy(_StrictModel):
    retention: str
    training: str
    logging: str
    regional_processing: str
    study_policy_satisfied: bool


class StorageControls(_StrictModel):
    access_control: bool
    encryption_at_rest: bool
    backups_excluded: bool
    sync_excluded: bool
    indexing_excluded: bool
    temporary_files_controlled: bool
    caches_controlled: bool
    logs_redacted: bool
    exports_controlled: bool
    retention_days: int = Field(gt=0)
    deletion_policy: str
    reviewer: LogicalId
    evidence_sha256: Digest


class OperatorApproval(_StrictModel):
    approver: LogicalId
    timestamp: datetime
    study_stage: Stage
    candidate_sha256: Digest
    declaration_sha256: Digest


class RestrictedDeclaration(_StrictModel):
    schema_version: Literal["1.0.0"]
    run_id: LogicalId
    runner_root: Path
    runner_revision: Revision
    lock_path: Path
    lock_sha256: Digest
    candidate_path: Path
    candidate_sha256: Digest
    pack_path: Path
    pack_sha256: Digest
    pack_id: LogicalId
    study_stage: Stage
    authorized_stages: tuple[Stage, ...] = Field(min_length=1)
    execution: ExecutionIdentity
    approved_execution: ExecutionIdentity
    input_paths: tuple[Path, ...] = Field(min_length=1)
    allowed_input_paths: tuple[Path, ...] = Field(min_length=1)
    output_path: Path
    allowed_output_paths: tuple[Path, ...] = Field(min_length=1)
    egress_endpoints: tuple[str, ...]
    allowed_egress_endpoints: tuple[str, ...]
    environment_keys: tuple[str, ...]
    allowed_environment_keys: tuple[str, ...]
    environment_filtered: bool
    credentials_scoped_to_run: bool
    provider_policy: ProviderPolicy
    storage: StorageControls
    approval: OperatorApproval | None


class AuthorizationRecord(_StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    authorized: Literal[True] = True
    run_id: LogicalId
    pack_id: LogicalId
    study_stage: Stage
    runner_revision: Revision
    lock_sha256: Digest
    candidate_sha256: Digest
    pack_sha256: Digest
    declaration_sha256: Digest
    execution_sha256: Digest
    custody_evidence_sha256: Digest
    authorized_at: datetime
    checks: tuple[str, ...]


def load_declaration(path: Path) -> RestrictedDeclaration:
    """Parse an operator-controlled YAML declaration without exposing input errors."""
    try:
        return RestrictedDeclaration.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, yaml.YAMLError, ValidationError, ValueError):
        raise PreflightError("DECLARATION_INVALID") from None


def declaration_digest(declaration: RestrictedDeclaration) -> str:
    """SHA-256 of sorted compact JSON, excluding only the separate approval object."""
    payload = declaration.model_dump(mode="json", exclude={"approval"})
    return _json_digest(payload)


def _json_digest(payload: object) -> str:
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def _safe_path(path: Path) -> Path:
    if not path.is_absolute() or any(part == ".." for part in path.parts):
        raise PreflightError("UNSAFE_PATH")
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise PreflightError("UNSAFE_PATH")
    return path.resolve(strict=True)


def digest_path(path: Path) -> str:
    """Stream SHA-256 of one file, or a sorted length-framed directory tree.

    A file is plain SHA-256. A directory hash frames every POSIX relative file
    name with a NUL terminator, followed by the 8-byte big-endian file size and
    file bytes. Symlinks, non-regular files, empty directories, and unreadable
    inputs fail closed. Directory metadata is deliberately not part of the hash.
    """
    try:
        safe = _safe_path(path)
        if safe.is_file():
            return _file_digest(safe)
        if not safe.is_dir():
            raise PreflightError("UNSAFE_PATH")
        digest = hashlib.sha256()
        files = sorted(safe.rglob("*"), key=lambda item: item.relative_to(safe).as_posix())
        count = 0
        for item in files:
            if item.is_symlink():
                raise PreflightError("UNSAFE_PATH")
            if item.is_dir():
                continue
            if not stat.S_ISREG(item.stat().st_mode):
                raise PreflightError("UNSAFE_PATH")
            name = item.relative_to(safe).as_posix().encode("utf-8")
            digest.update(name + b"\0")
            digest.update(item.stat().st_size.to_bytes(8, "big"))
            with item.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    digest.update(chunk)
            count += 1
        if count == 0:
            raise PreflightError("EMPTY_INPUT")
        return digest.hexdigest()
    except (OSError, RuntimeError, OverflowError, UnicodeError):
        raise PreflightError("INPUT_UNREADABLE") from None


def _file_digest(path: Path) -> str:
    if not stat.S_ISREG(path.stat().st_mode):
        raise PreflightError("UNSAFE_PATH")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments], shell=False, capture_output=True,
            text=True, timeout=15, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        raise PreflightError("RUNNER_UNAVAILABLE") from None
    if result.returncode != 0:
        raise PreflightError("RUNNER_UNAVAILABLE")
    return result.stdout.strip()


def _contained(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _check_executing_runner(runner: Path, revision: str) -> None:
    """Bind this self-contained checker to the reviewed tracked source blob.

    The preflight module imports no other benchmark module: executable library
    dependencies are provisioned from the separately verified lock. Checking
    both location and Git object bytes avoids authorizing an unrelated checkout
    or relying only on status flags that can hide a modified tracked file.
    """
    relative = "benchmark/src/systematic_innovation_bench/restricted_preflight.py"
    executing = _safe_path(Path(__file__))
    if executing != runner / relative:
        raise PreflightError("EXECUTING_RUNNER")
    try:
        reviewed = subprocess.run(
            ["git", "-C", str(runner), "show", f"{revision}:{relative}"],
            shell=False, capture_output=True, timeout=15, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        raise PreflightError("EXECUTING_RUNNER") from None
    if reviewed.returncode != 0 or reviewed.stdout != executing.read_bytes():
        raise PreflightError("EXECUTING_RUNNER")


def _check_inputs(declaration: RestrictedDeclaration, runner: Path, pack: Path) -> None:
    allowed = tuple(_safe_path(path) for path in declaration.allowed_input_paths)
    requested = tuple(_safe_path(path) for path in declaration.input_paths)
    mandatory = (runner, pack, declaration.lock_path.resolve(), declaration.candidate_path.resolve())
    # An approved root may be the frozen runner, exact pack, or another explicit
    # input; it cannot grant an ancestor of either trust zone or the filesystem.
    if any(root == Path(root.anchor) for root in allowed):
        raise PreflightError("INPUT_ACCESS")
    if any(_contained(runner, root) and root != runner for root in allowed):
        raise PreflightError("INPUT_ACCESS")
    if any(_contained(pack, root) and root != pack for root in allowed):
        raise PreflightError("INPUT_ACCESS")
    if any(not any(_contained(path, root) for root in allowed) for path in requested):
        raise PreflightError("INPUT_ACCESS")
    if any(not any(_contained(path, root) for root in requested) for path in mandatory):
        raise PreflightError("INPUT_ACCESS")


def _check_outputs(declaration: RestrictedDeclaration, runner: Path, pack: Path) -> None:
    output = _safe_path(declaration.output_path)
    allowed = tuple(_safe_path(path) for path in declaration.allowed_output_paths)
    if not output.is_dir() or any(not root.is_dir() for root in allowed):
        raise PreflightError("OUTPUT_ACCESS")
    if any(root == Path(root.anchor) for root in allowed):
        raise PreflightError("OUTPUT_ACCESS")
    if not any(_contained(output, root) for root in allowed):
        raise PreflightError("OUTPUT_ACCESS")
    if any(_contained(output, root) or _contained(root, output) for root in (runner, pack)):
        raise PreflightError("OUTPUT_ACCESS")
    if any(_contained(runner, root) or _contained(pack, root) for root in allowed):
        raise PreflightError("OUTPUT_ACCESS")
    if output.stat().st_mode & 0o077:
        raise PreflightError("STORAGE")


def _valid_endpoint(endpoint: str) -> bool:
    try:
        parsed = urlsplit(endpoint)
        return bool(
            parsed.scheme == "https" and parsed.hostname and parsed.username is None
            and parsed.password is None and not parsed.query and not parsed.fragment
            and parsed.path in ("", "/") and parsed.port in (None, 443)
        )
    except ValueError:
        return False


def _check_execution_controls(declaration: RestrictedDeclaration) -> None:
    if declaration.study_stage not in declaration.authorized_stages:
        raise PreflightError("STAGE")
    if declaration.execution != declaration.approved_execution:
        raise PreflightError("EXECUTION_IDENTITY")
    if any(not argument.strip() or "\x00" in argument for argument in declaration.execution.invocation):
        raise PreflightError("EXECUTION_IDENTITY")
    if (any(not _valid_endpoint(item) for item in declaration.allowed_egress_endpoints)
            or any(not _valid_endpoint(item) for item in declaration.egress_endpoints)
            or not set(declaration.egress_endpoints) <= set(declaration.allowed_egress_endpoints)):
        raise PreflightError("EGRESS")
    blocked_environment = {
        "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "FTP_PROXY", "NO_PROXY",
        "PYTHONPATH", "PYTHONHOME", "LD_PRELOAD", "DYLD_INSERT_LIBRARIES",
        "BASH_ENV", "ENV",
    }
    keys = set(declaration.environment_keys)
    if (not declaration.environment_filtered or not declaration.credentials_scoped_to_run
            or not keys <= set(declaration.allowed_environment_keys)
            or any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) for key in keys)
            or any(key.upper() in blocked_environment for key in keys)):
        raise PreflightError("ENVIRONMENT")
    policy = declaration.provider_policy
    if (not policy.study_policy_satisfied or any(
        not value.strip() or value.strip().lower() in {"unknown", "unspecified", "not assessed"}
        for value in (policy.retention, policy.training, policy.logging, policy.regional_processing)
    )):
        raise PreflightError("PROVIDER_POLICY")
    storage = declaration.storage
    if not all((
        storage.access_control, storage.encryption_at_rest, storage.backups_excluded,
        storage.sync_excluded, storage.indexing_excluded, storage.temporary_files_controlled,
        storage.caches_controlled, storage.logs_redacted, storage.exports_controlled,
    )) or not storage.deletion_policy.strip():
        raise PreflightError("STORAGE")


def _check_approval(declaration: RestrictedDeclaration) -> None:
    approval = declaration.approval
    if (approval is None or approval.timestamp.tzinfo is None
            or approval.timestamp > datetime.now(UTC)
            or approval.study_stage != declaration.study_stage
            or approval.candidate_sha256 != declaration.candidate_sha256
            or approval.declaration_sha256 != declaration_digest(declaration)):
        raise PreflightError("OPERATOR_APPROVAL")


def authorize_restricted_run(declaration: RestrictedDeclaration) -> AuthorizationRecord:
    """Fail closed and return a content-free decision; never launch an adapter.

    Call immediately before the separately controlled execution boundary. The
    record attests to the state observed now; it is not a reusable access token.
    """
    try:
        runner = _safe_path(declaration.runner_root)
        if Path(_git(runner, "rev-parse", "--show-toplevel")).resolve() != runner:
            raise PreflightError("RUNNER_LOCATION")
        if _git(runner, "rev-parse", "HEAD") != declaration.runner_revision:
            raise PreflightError("RUNNER_REVISION")
        if _git(runner, "status", "--porcelain=v1", "--untracked-files=all"):
            raise PreflightError("DIRTY_WORKTREE")
        _check_executing_runner(runner, declaration.runner_revision)
        pack = _safe_path(declaration.pack_path)
        if (_contained(pack, runner)
                or any((ancestor / ".git").exists() or (ancestor / ".git").is_symlink()
                       for ancestor in (pack, *pack.parents))):
            raise PreflightError("PACK_LOCATION")
        _check_execution_controls(declaration)
        _check_inputs(declaration, runner, pack)
        _check_outputs(declaration, runner, pack)
        _check_approval(declaration)
        lock = _safe_path(declaration.lock_path)
        if lock != runner / "benchmark/uv.lock":
            raise PreflightError("LOCK_LOCATION")
        _git(runner, "ls-files", "--error-unmatch", "benchmark/uv.lock")
        if digest_path(lock) != declaration.lock_sha256:
            raise PreflightError("LOCK_DIGEST")
        candidate = _safe_path(declaration.candidate_path)
        if not _contained(candidate, runner) or candidate == runner:
            raise PreflightError("CANDIDATE_LOCATION")
        _git(runner, "ls-files", "--error-unmatch", candidate.relative_to(runner).as_posix())
        if digest_path(candidate) != declaration.candidate_sha256:
            raise PreflightError("CANDIDATE_DIGEST")
        if digest_path(pack) != declaration.pack_sha256:
            raise PreflightError("PACK_DIGEST")
        return AuthorizationRecord(
            run_id=declaration.run_id, pack_id=declaration.pack_id,
            study_stage=declaration.study_stage, runner_revision=declaration.runner_revision,
            lock_sha256=declaration.lock_sha256, candidate_sha256=declaration.candidate_sha256,
            pack_sha256=declaration.pack_sha256, declaration_sha256=declaration_digest(declaration),
            execution_sha256=_json_digest(declaration.execution.model_dump(mode="json")),
            custody_evidence_sha256=declaration.storage.evidence_sha256,
            authorized_at=datetime.now(UTC),
            checks=("reviewed-revision", "clean-worktree", "locked-dependencies", "candidate",
                    "external-pack", "stage", "execution-identity", "filesystem", "egress",
                    "environment", "provider-policy", "storage-custody", "operator-approval"),
        )
    except (OSError, UnicodeError, ValueError) as error:
        if isinstance(error, PreflightError):
            raise
        raise PreflightError("PREFLIGHT_INVALID") from None
