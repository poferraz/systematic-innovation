"""Fail-closed preflight tests use only freshly created synthetic worktrees."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

import pytest

from systematic_innovation_bench.restricted_preflight import (
    PreflightError,
    RestrictedDeclaration,
    authorize_restricted_run,
    declaration_digest,
    digest_path,
    load_declaration,
)


def test_unrelated_executing_checkout_cannot_authorize_a_clean_declared_runner(approved_declaration):
    with pytest.raises(PreflightError, match="EXECUTING_RUNNER"):
        authorize_restricted_run(approved_declaration)


def test_modified_executing_source_hidden_from_status_is_rejected(approved_declaration):
    relative = "benchmark/src/systematic_innovation_bench/restricted_preflight.py"
    module = approved_declaration.runner_root / relative
    module.write_bytes(module.read_bytes() + b"\n# unreviewed executable source\n")
    git(approved_declaration.runner_root, "update-index", "--assume-unchanged", relative)
    assert git(approved_declaration.runner_root, "status", "--porcelain=v1") == ""
    with pytest.raises(PreflightError, match="EXECUTING_RUNNER"):
        reviewed_authorize(approved_declaration)


def test_directory_digest_uses_sorted_null_delimited_relative_names(tmp_path):
    path = tmp_path / "pack-framing"
    path.mkdir()
    (path / "test.yaml").write_bytes(b"two")
    (path / "scoring.yaml").write_bytes(b"one")
    framed = (b"scoring.yaml\0" + (3).to_bytes(8, "big") + b"one"
              + b"test.yaml\0" + (3).to_bytes(8, "big") + b"two")
    assert digest_path(path) == hashlib.sha256(framed).hexdigest()


LOADED_REVIEWED_MODULES: dict[str, ModuleType] = {}


def reviewed_module(declaration: RestrictedDeclaration) -> ModuleType:
    root = str(declaration.runner_root)
    if root not in LOADED_REVIEWED_MODULES:
        path = declaration.runner_root / "benchmark/src/systematic_innovation_bench/restricted_preflight.py"
        name = "reviewed_fixture_" + hashlib.sha256(root.encode()).hexdigest()
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        previous = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous
        LOADED_REVIEWED_MODULES[root] = module
    return LOADED_REVIEWED_MODULES[root]


def reviewed_authorize(declaration: RestrictedDeclaration):
    module = reviewed_module(declaration)
    try:
        return module.authorize_restricted_run(declaration)
    except module.PreflightError as error:
        # The copied module has its own exception class; compare only its public
        # structural code through the same source-side test assertion type.
        raise PreflightError(error.code) from None


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "-C", str(root), *args], check=True, capture_output=True, text=True,
    ).stdout.strip()


@pytest.fixture
def approved_declaration(tmp_path: Path) -> RestrictedDeclaration:
    runner = tmp_path / "runner"
    runner.mkdir()
    git(runner, "init", "-q")
    git(runner, "config", "user.name", "Synthetic reviewer")
    git(runner, "config", "user.email", "210631651+poferraz@users.noreply.github.com")
    (runner / "benchmark").mkdir()
    copied_module = runner / "benchmark/src/systematic_innovation_bench/restricted_preflight.py"
    copied_module.parent.mkdir(parents=True)
    original_module = Path(__file__).resolve().parents[1] / "src/systematic_innovation_bench/restricted_preflight.py"
    copied_module.write_bytes(original_module.read_bytes())
    lock = runner / "benchmark/uv.lock"
    lock.write_text("synthetic lock\n")
    candidate = runner / "candidate.txt"
    candidate.write_text("synthetic candidate\n")
    git(runner, "add", ".")
    git(runner, "commit", "-qm", "synthetic reviewed inputs")
    pack = tmp_path / "operator-pack"
    pack.mkdir(mode=0o700)
    sentinel = "fixture-" + "sentinel-" + "not-for-output"
    (pack / "pack.yaml").write_text(sentinel)
    results = tmp_path / "controlled-results"
    results.mkdir(mode=0o700)
    identity = {
        "provider": "synthetic-provider", "model": "synthetic-model",
        "account": "synthetic-account", "adapter": "synthetic-adapter",
        "invocation": ["synthetic-executable", "--json"],
    }
    data = {
        "schema_version": "1.0.0", "run_id": "synthetic-rehearsal",
        "runner_root": str(runner), "runner_revision": git(runner, "rev-parse", "HEAD"),
        "lock_path": str(lock), "lock_sha256": digest_path(lock),
        "candidate_path": str(candidate), "candidate_sha256": digest_path(candidate),
        "pack_path": str(pack), "pack_sha256": digest_path(pack), "pack_id": "pack-001",
        "study_stage": "validation", "authorized_stages": ["validation"],
        "execution": identity, "approved_execution": copy.deepcopy(identity),
        "input_paths": [str(runner), str(pack)],
        "allowed_input_paths": [str(runner), str(pack)],
        "output_path": str(results), "allowed_output_paths": [str(results)],
        "egress_endpoints": ["https://models.example.invalid"],
        "allowed_egress_endpoints": ["https://models.example.invalid"],
        "environment_keys": ["LANG"], "allowed_environment_keys": ["LANG"],
        "environment_filtered": True, "credentials_scoped_to_run": True,
        "provider_policy": {
            "retention": "zero retention", "training": "disabled",
            "logging": "metadata only", "regional_processing": "declared region",
            "study_policy_satisfied": True,
        },
        "storage": {
            "access_control": True, "encryption_at_rest": True,
            "backups_excluded": True, "sync_excluded": True, "indexing_excluded": True,
            "temporary_files_controlled": True, "caches_controlled": True,
            "logs_redacted": True, "exports_controlled": True,
            "retention_days": 30, "deletion_policy": "verified deletion after retention",
            "reviewer": "custody-operator", "evidence_sha256": "a" * 64,
        },
        "approval": None,
    }
    declaration = RestrictedDeclaration.model_validate(data)
    data["approval"] = {
        "approver": "study-operator", "timestamp": datetime.now(UTC).isoformat(),
        "study_stage": "validation", "candidate_sha256": data["candidate_sha256"],
        "declaration_sha256": declaration_digest(declaration),
    }
    return RestrictedDeclaration.model_validate(data)


def alter(declaration: RestrictedDeclaration, key: str, value: object) -> RestrictedDeclaration:
    data = declaration.model_dump(mode="json")
    if "." in key:
        parent, field = key.split(".")
        data[parent][field] = value
    else:
        data[key] = value
    return RestrictedDeclaration.model_validate(data)


def resign(declaration: RestrictedDeclaration) -> RestrictedDeclaration:
    data = declaration.model_dump(mode="json")
    data["approval"]["declaration_sha256"] = declaration_digest(declaration)
    data["approval"]["candidate_sha256"] = declaration.candidate_sha256
    data["approval"]["study_stage"] = declaration.study_stage
    return RestrictedDeclaration.model_validate(data)


def test_synthetic_custody_rehearsal_returns_only_content_free_authorization(approved_declaration):
    record = reviewed_authorize(approved_declaration)
    payload = record.model_dump_json()
    assert record.authorized is True
    assert record.runner_revision == approved_declaration.runner_revision
    assert record.pack_sha256 == approved_declaration.pack_sha256
    assert record.declaration_sha256 == declaration_digest(approved_declaration)
    assert record.pack_id == "pack-001"
    assert "sentinel" not in payload
    assert str(approved_declaration.pack_path) not in payload
    assert str(approved_declaration.runner_root) not in payload
    assert str(approved_declaration.output_path) not in payload
    assert list(approved_declaration.output_path.iterdir()) == []


@pytest.mark.parametrize(("key", "value", "code"), [
    ("runner_revision", "f" * 40, "RUNNER_REVISION"),
    ("lock_sha256", "f" * 64, "LOCK_DIGEST"),
    ("pack_sha256", "f" * 64, "PACK_DIGEST"),
    ("candidate_sha256", "f" * 64, "CANDIDATE_DIGEST"),
    ("study_stage", "sealed-test", "STAGE"),
    ("execution.provider", "undeclared", "EXECUTION_IDENTITY"),
    ("execution.model", "undeclared", "EXECUTION_IDENTITY"),
    ("execution.account", "undeclared", "EXECUTION_IDENTITY"),
    ("execution.adapter", "undeclared", "EXECUTION_IDENTITY"),
    ("execution.invocation", ["undeclared"], "EXECUTION_IDENTITY"),
    ("input_paths", ["/"], "INPUT_ACCESS"),
    ("output_path", "/", "OUTPUT_ACCESS"),
    ("egress_endpoints", ["https://undeclared.example.invalid"], "EGRESS"),
    ("environment_keys", ["UNDECLARED_KEY"], "ENVIRONMENT"),
    ("environment_filtered", False, "ENVIRONMENT"),
    ("credentials_scoped_to_run", False, "ENVIRONMENT"),
    ("provider_policy.retention", "", "PROVIDER_POLICY"),
    ("provider_policy.training", "", "PROVIDER_POLICY"),
    ("provider_policy.logging", "", "PROVIDER_POLICY"),
    ("provider_policy.regional_processing", "", "PROVIDER_POLICY"),
    ("provider_policy.study_policy_satisfied", False, "PROVIDER_POLICY"),
    ("storage.access_control", False, "STORAGE"),
    ("storage.encryption_at_rest", False, "STORAGE"),
    ("storage.backups_excluded", False, "STORAGE"),
    ("storage.sync_excluded", False, "STORAGE"),
    ("storage.indexing_excluded", False, "STORAGE"),
    ("storage.temporary_files_controlled", False, "STORAGE"),
    ("storage.caches_controlled", False, "STORAGE"),
    ("storage.logs_redacted", False, "STORAGE"),
    ("storage.exports_controlled", False, "STORAGE"),
    ("storage.deletion_policy", "", "STORAGE"),
    ("approval", None, "OPERATOR_APPROVAL"),
    ("approval.candidate_sha256", "b" * 64, "OPERATOR_APPROVAL"),
    ("approval.study_stage", "sealed-test", "OPERATOR_APPROVAL"),
    ("approval.declaration_sha256", "b" * 64, "OPERATOR_APPROVAL"),
])
def test_every_failed_control_refuses_without_content(approved_declaration, key, value, code, capsys):
    declaration = alter(approved_declaration, key, value)
    if not key.startswith("approval"):
        declaration = resign(declaration)
    with pytest.raises(PreflightError) as error:
        reviewed_authorize(declaration)
    assert error.value.code == code
    assert str(error.value) == code
    assert "sentinel" not in str(error.value) + str(capsys.readouterr())
    assert list(approved_declaration.output_path.iterdir()) == []


@pytest.mark.parametrize("dirty_kind", ["tracked", "untracked"])
def test_actual_dirty_worktree_blocks_before_pack_access(approved_declaration, dirty_kind):
    if dirty_kind == "tracked":
        approved_declaration.lock_path.write_text("changed")
    else:
        (approved_declaration.runner_root / "untracked.txt").write_text("unreviewed")
    with pytest.raises(PreflightError, match="DIRTY_WORKTREE"):
        reviewed_authorize(approved_declaration)


def test_pack_inside_worktree_is_rejected_even_if_ignored(approved_declaration):
    inside = approved_declaration.runner_root / ".git/private-pack"
    inside.mkdir()
    (inside / "pack.yaml").write_text("synthetic only")
    declaration = alter(approved_declaration, "pack_path", str(inside))
    with pytest.raises(PreflightError, match="PACK_LOCATION"):
        reviewed_authorize(declaration)


@pytest.mark.parametrize("marker_kind", ["directory", "file"])
def test_pack_inside_an_unrelated_worktree_is_rejected(approved_declaration, tmp_path, marker_kind):
    repository = tmp_path / "unrelated-public-worktree"
    repository.mkdir()
    if marker_kind == "directory":
        git(repository, "init", "-q")
    else:
        (repository / ".git").write_text("gitdir: external-metadata\n")
    (repository / ".gitignore").write_text("ignored-pack/\n")
    relocated = repository / "ignored-pack"
    approved_declaration.pack_path.rename(relocated)
    declaration = alter(approved_declaration, "pack_path", str(relocated))
    for key in ("input_paths", "allowed_input_paths"):
        declaration = alter(declaration, key, [str(declaration.runner_root), str(relocated)])
    declaration = resign(declaration)
    with pytest.raises(PreflightError, match="PACK_LOCATION"):
        reviewed_authorize(declaration)


def test_permissive_result_directory_is_rejected(approved_declaration):
    approved_declaration.output_path.chmod(0o755)
    with pytest.raises(PreflightError, match="STORAGE"):
        reviewed_authorize(approved_declaration)


def test_signed_declaration_cannot_authorize_broad_filesystem_roots(approved_declaration):
    declaration = resign(alter(approved_declaration, "allowed_input_paths", ["/"]))
    with pytest.raises(PreflightError, match="INPUT_ACCESS"):
        reviewed_authorize(declaration)


def test_signed_declaration_rejects_proxy_environment_bypass(approved_declaration):
    declaration = alter(approved_declaration, "allowed_environment_keys", ["HTTPS_PROXY"])
    declaration = resign(alter(declaration, "environment_keys", ["HTTPS_PROXY"]))
    with pytest.raises(PreflightError, match="ENVIRONMENT"):
        reviewed_authorize(declaration)


def test_approval_binds_every_declaration_field(approved_declaration):
    declaration = alter(approved_declaration, "run_id", "changed-run")
    with pytest.raises(PreflightError, match="OPERATOR_APPROVAL"):
        reviewed_authorize(declaration)


def test_pack_digest_is_order_stable_and_detects_file_name_and_content_changes(tmp_path):
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "b.yaml").write_text("beta")
    (pack / "a.yaml").write_text("alpha")
    original = digest_path(pack)
    (pack / "a.yaml").rename(pack / "c.yaml")
    assert digest_path(pack) != original
    (pack / "c.yaml").rename(pack / "a.yaml")
    assert digest_path(pack) == original
    (pack / "a.yaml").write_text("changed")
    assert digest_path(pack) != original


def test_digest_path_rejects_symlinks(tmp_path):
    target = tmp_path / "data"
    target.write_text("synthetic")
    link = tmp_path / "link"
    link.symlink_to(target)
    with pytest.raises(PreflightError, match="UNSAFE_PATH"):
        digest_path(link)


def test_malformed_declaration_never_echoes_input_values(tmp_path, capsys):
    sentinel = "do-" + "not-echo-" + "fixture"
    declaration = tmp_path / "declaration.yaml"
    declaration.write_text("unexpected: " + sentinel)
    with pytest.raises(PreflightError, match="DECLARATION_INVALID") as error:
        load_declaration(declaration)
    leaked = sentinel in str(error.value) + str(capsys.readouterr())
    assert not leaked


def test_schema_matches_runtime_and_has_no_implicit_permissive_properties():
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/restricted-preflight.schema.json").read_text())
    assert schema == RestrictedDeclaration.model_json_schema()
    assert schema["additionalProperties"] is False
    for definition in schema["$defs"].values():
        if definition.get("type") == "object":
            assert definition["additionalProperties"] is False


def test_digest_of_file_is_plain_sha256(tmp_path):
    path = tmp_path / "lock"
    path.write_bytes(b"lock bytes\n")
    assert digest_path(path) == hashlib.sha256(b"lock bytes\n").hexdigest()


@pytest.mark.parametrize("approval_kind", ["absent", "unbound"])
def test_operator_approval_is_verified_before_pack_bytes_are_read(
    approved_declaration, monkeypatch, approval_kind,
):
    restricted_preflight = reviewed_module(approved_declaration)
    declaration = (alter(approved_declaration, "approval", None) if approval_kind == "absent"
                   else alter(approved_declaration, "run_id", "unapproved-run"))
    original_digest = restricted_preflight.digest_path
    reads = []

    def observe_digest(path):
        if path == approved_declaration.pack_path:
            reads.append(path)
        return original_digest(path)

    monkeypatch.setattr(restricted_preflight, "digest_path", observe_digest)
    with pytest.raises(PreflightError, match="OPERATOR_APPROVAL"):
        reviewed_authorize(declaration)
    assert reads == []
