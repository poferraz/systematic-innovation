from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
import tempfile
from typing import Any
import zipfile

from tools.validate_skill import validate_skill

SKILL_NAME = "systematic-innovation"
TOP_LEVEL_PREFIX = f"{SKILL_NAME}/"
SCHEMA_VERSION = "1.0.0"
BUILD_TOOL_VERSION = "1.0.0"
FIXED_ZIP_DATETIME = (1980, 1, 1, 0, 0, 0)
FIXED_UNIX_MODE = 0o100644
UTF8_FLAG_BIT = 0x800

ALLOWED_RELATIVE_SKILL_FILES = (
    "SKILL.md",
    "references/deep-mode.md",
    "references/evidence.md",
    "references/innovation-lenses.md",
    "references/output-contract.md",
)

EXPECTED_ARCHIVE_PATHS = tuple(f"{TOP_LEVEL_PREFIX}{rel}" for rel in sorted(ALLOWED_RELATIVE_SKILL_FILES))

SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

NORMALIZATION_SPEC: dict[str, Any] = {
    "archive_format": "zip",
    "compression": "deflate",
    "compresslevel": 9,
    "mtime_utc": list(FIXED_ZIP_DATETIME),
    "file_mode": "0644",
    "path_order": "lexicographic-posix",
    "line_endings": "lf",
    "top_level_prefix": TOP_LEVEL_PREFIX,
}


@dataclass(frozen=True)
class ManifestFileEntry:
    path: str
    sha256: str
    size_bytes: int
    mode: str = "0644"


@dataclass(frozen=True)
class ReleaseManifest:
    schema_version: str
    skill_name: str
    version: str
    source_revision: str
    build_tool_version: str
    archive_sha256: str
    payload_sha256: str
    files: tuple[ManifestFileEntry, ...]
    normalization: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["files"] = [asdict(f) for f in self.files]
        return data


def _compute_payload_digest(entries: list[ManifestFileEntry]) -> str:
    hasher = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: item.path):
        hasher.update(f"{entry.mode} {entry.size_bytes} {entry.sha256} {entry.path}\n".encode("utf-8"))
    return hasher.hexdigest()


def _validate_source_directory(source: Path) -> list[Path]:
    if not source.is_dir():
        raise ValueError(f"Canonical skill directory does not exist: {source}")

    discovered: list[str] = []
    for item in sorted(source.rglob("*")):
        rel_posix = item.relative_to(source).as_posix()
        if item.is_symlink():
            raise ValueError(f"Symlink prohibited in canonical skill source: {rel_posix}")
        if item.is_dir():
            continue
        discovered.append(rel_posix)

    expected = sorted(ALLOWED_RELATIVE_SKILL_FILES)
    if sorted(discovered) != expected:
        raise ValueError(
            f"Canonical skill source files do not match allowlist: expected {expected}, found {sorted(discovered)}"
        )

    skill_errors = validate_skill(source)
    if skill_errors:
        raise ValueError(f"Canonical skill validation failed before packaging: {skill_errors}")

    return [source / rel for rel in expected]


def build_skill(
    source: Path,
    output: Path,
    version: str,
    revision: str,
) -> ReleaseManifest:
    """Build a deterministic, byte-reproducible canonical skill ZIP archive and return its manifest."""
    if not SEMVER_RE.match(version):
        raise ValueError(f"Invalid semantic version '{version}'; expected X.Y.Z")
    revision_norm = revision.strip().lower()
    if not REVISION_RE.match(revision_norm):
        raise ValueError(f"Invalid source revision '{revision}'; expected 40-char lowercase hex SHA")

    source_files = _validate_source_directory(source.resolve())
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    manifest_entries: list[ManifestFileEntry] = []

    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as zf:
        for abs_file in source_files:
            rel_posix = abs_file.relative_to(source.resolve()).as_posix()
            arcname = f"{TOP_LEVEL_PREFIX}{rel_posix}"
            raw_text = abs_file.read_text(encoding="utf-8")
            normalized_bytes = raw_text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
            file_sha256 = hashlib.sha256(normalized_bytes).hexdigest()

            info = zipfile.ZipInfo(filename=arcname, date_time=FIXED_ZIP_DATETIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # Unix
            info.external_attr = (FIXED_UNIX_MODE & 0xFFFF) << 16
            info.flag_bits |= UTF8_FLAG_BIT
            info.extra = b""
            info.comment = b""

            zf.writestr(info, normalized_bytes, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            manifest_entries.append(
                ManifestFileEntry(
                    path=arcname,
                    sha256=file_sha256,
                    size_bytes=len(normalized_bytes),
                    mode="0644",
                )
            )

    archive_bytes = output.read_bytes()
    archive_sha256 = hashlib.sha256(archive_bytes).hexdigest()
    payload_sha256 = _compute_payload_digest(manifest_entries)

    return ReleaseManifest(
        schema_version=SCHEMA_VERSION,
        skill_name=SKILL_NAME,
        version=version,
        source_revision=revision_norm,
        build_tool_version=BUILD_TOOL_VERSION,
        archive_sha256=archive_sha256,
        payload_sha256=payload_sha256,
        files=tuple(manifest_entries),
        normalization=dict(NORMALIZATION_SPEC),
    )


def write_manifest(manifest: ReleaseManifest, path: Path) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _check_revocations(
    archive_sha256: str,
    payload_sha256: str | None,
    revocations_path: Path,
) -> list[str]:
    errors: list[str] = []
    if not revocations_path.is_file():
        return [f"revocations file missing: {revocations_path}"]
    try:
        data = json.loads(revocations_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"failed to parse revocations file {revocations_path}: {exc}"]

    revoked_list = data.get("revoked_artifacts", [])
    if not isinstance(revoked_list, list):
        return [f"invalid revoked_artifacts list in {revocations_path}"]

    for item in revoked_list:
        if not isinstance(item, dict):
            continue
        rev_sha = str(item.get("sha256", "")).lower()
        reason = item.get("reason", "unspecified")
        if rev_sha and rev_sha in {archive_sha256.lower(), (payload_sha256 or "").lower()}:
            errors.append(f"REVOKED_ARTIFACT: digest {rev_sha} is revoked in {revocations_path.name} ({reason})")
    return errors


def verify_artifact(
    archive_path: Path,
    manifest_path: Path | None = None,
    source_dir: Path | None = None,
    revocations_path: Path | None = None,
    policy_path: Path | None = None,
) -> list[str]:
    """Verify a canonical skill release ZIP, optional manifest, revocation denylist, and post-extract install smoke test."""
    errors: list[str] = []
    if not archive_path.is_file():
        return [f"archive does not exist: {archive_path}"]

    archive_bytes = archive_path.read_bytes()
    archive_sha256 = hashlib.sha256(archive_bytes).hexdigest()

    allowed_files = list(EXPECTED_ARCHIVE_PATHS)
    if policy_path is not None:
        if not policy_path.is_file():
            errors.append(f"policy file missing: {policy_path}")
        else:
            try:
                policy = json.loads(policy_path.read_text(encoding="utf-8"))
                if "allowed_archive_files" in policy:
                    allowed_files = sorted(policy["allowed_archive_files"])
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"invalid policy file {policy_path}: {exc}")

    extracted_entries: list[ManifestFileEntry] = []
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            infos = zf.infolist()
            names = [info.filename for info in infos]
            if names != sorted(names):
                errors.append("archive entries are not in lexicographic POSIX order")
            if names != allowed_files:
                errors.append(
                    f"archive member list does not match canonical allowlist: expected {allowed_files}, found {names}"
                )

            for info in infos:
                name = info.filename
                if not name.startswith(TOP_LEVEL_PREFIX) or ".." in name or "\\" in name or name.startswith("/"):
                    errors.append(f"invalid or unsafe archive path: {name}")
                if info.date_time != FIXED_ZIP_DATETIME:
                    errors.append(f"non-normalized timestamp on {name}: {info.date_time}")
                unix_mode = (info.external_attr >> 16) & 0o177777
                if (unix_mode & 0o170000) == 0o120000:
                    errors.append(f"symlink entry prohibited in archive: {name}")
                if unix_mode != FIXED_UNIX_MODE:
                    errors.append(f"non-normalized file mode on {name}: {oct(unix_mode)}")
                if info.compress_type != zipfile.ZIP_DEFLATED:
                    errors.append(f"non-deflated compression type on {name}: {info.compress_type}")

                data = zf.read(name)
                if b"\r" in data:
                    errors.append(f"non-LF line endings found in archive member: {name}")
                extracted_entries.append(
                    ManifestFileEntry(
                        path=name,
                        sha256=hashlib.sha256(data).hexdigest(),
                        size_bytes=len(data),
                        mode="0644",
                    )
                )

            # Post-extraction installation smoke validation (AR-04)
            with tempfile.TemporaryDirectory() as extract_tmp:
                extract_root = Path(extract_tmp)
                zf.extractall(extract_root)
                installed_skill_dir = extract_root / SKILL_NAME
                if not installed_skill_dir.is_dir():
                    errors.append("extracted archive missing top-level systematic-innovation/ directory")
                else:
                    for val_err in validate_skill(installed_skill_dir):
                        errors.append(f"post-extraction skill validation failed: {val_err}")
    except zipfile.BadZipFile as exc:
        errors.append(f"corrupt ZIP archive: {exc}")
        return errors

    computed_payload_sha256 = _compute_payload_digest(extracted_entries)

    if revocations_path is not None:
        errors.extend(_check_revocations(archive_sha256, computed_payload_sha256, revocations_path))

    manifest_data: dict[str, Any] | None = None
    if manifest_path is not None:
        if not manifest_path.is_file():
            errors.append(f"manifest file does not exist: {manifest_path}")
        else:
            try:
                manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"invalid manifest JSON: {exc}")

    if manifest_data is not None:
        if manifest_data.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"unexpected manifest schema_version: {manifest_data.get('schema_version')}")
        if manifest_data.get("skill_name") != SKILL_NAME:
            errors.append(f"unexpected manifest skill_name: {manifest_data.get('skill_name')}")
        if not SEMVER_RE.match(str(manifest_data.get("version", ""))):
            errors.append(f"invalid manifest version: {manifest_data.get('version')}")
        if not REVISION_RE.match(str(manifest_data.get("source_revision", ""))):
            errors.append(f"invalid manifest source_revision: {manifest_data.get('source_revision')}")
        if manifest_data.get("archive_sha256") != archive_sha256:
            errors.append(
                f"manifest archive_sha256 mismatch: expected {archive_sha256}, got {manifest_data.get('archive_sha256')}"
            )
        if manifest_data.get("payload_sha256") != computed_payload_sha256:
            errors.append(
                f"manifest payload_sha256 mismatch: expected {computed_payload_sha256}, got {manifest_data.get('payload_sha256')}"
            )
        if manifest_data.get("normalization") != NORMALIZATION_SPEC:
            errors.append("manifest normalization object does not match canonical specification")
        expected_files_dicts = [asdict(entry) for entry in extracted_entries]
        if manifest_data.get("files") != expected_files_dicts:
            errors.append("manifest per-file entries do not match archive contents")

    if source_dir is not None:
        with tempfile.TemporaryDirectory() as rebuild_tmp:
            rebuild_zip = Path(rebuild_tmp) / "rebuild.zip"
            rev = str((manifest_data or {}).get("source_revision", "0" * 40))
            ver = str((manifest_data or {}).get("version", "0.1.0"))
            try:
                rebuilt = build_skill(source_dir, rebuild_zip, version=ver, revision=rev)
                if rebuilt.archive_sha256 != archive_sha256 or rebuild_zip.read_bytes() != archive_bytes:
                    errors.append("archive bytes drift from canonical source directory rebuild")
            except ValueError as exc:
                errors.append(f"canonical source rebuild failed: {exc}")

    return errors
