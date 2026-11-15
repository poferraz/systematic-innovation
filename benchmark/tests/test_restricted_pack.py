"""Only synthetic private packs are used; no protected content is retained in Git."""
import json
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

from systematic_innovation_bench.restricted import (
    PackValidationError,
    validate_restricted_pack,
)

ALLOCATIONS = {
    "synthetic-mechanism": 5, "counterfactual-rediscovery": 3,
    "open-ended-systemic": 6, "preservation-no-change": 2,
    "trigger-scope": 2, "adversarial-high-stakes": 2,
}


@pytest.fixture
def pack():
    with tempfile.TemporaryDirectory(prefix="sib-private-fixture-") as directory:
        path = Path(directory).resolve()
        notes = []
        for split in ("validation", "test"):
            cases = []
            for family, count in ALLOCATIONS.items():
                for index in range(count):
                    case_id = f"{split}-{family}-{index}"
                    cases.append({
                        "id": case_id, "family": family, "domain": "fictional",
                        "split": split, "prompt": "Explore this invented scheduling system.",
                        "strata": {"mode": "deep"}, "expected_mode": "deep",
                        "interaction_mode": "controlled-multi-turn",
                        "conversation_script": {"user_turns": [
                            "Preserve fair access.", "Use existing resources. Give the final portfolio.",
                        ]},
                        "hidden_mechanisms": ["fictional causal family"],
                    })
                    notes.append({
                        "case_id": case_id,
                        "gold_mechanisms": ["fictional causal family"],
                        "acceptable_functional_equivalents": ["equivalent fictional family"],
                        "unsafe_outputs": ["exclusion"],
                        "deterministic_checks": ["complete transcript"],
                        "provenance_notes": "Invented fixture, never a study case.",
                        "reviewer_approvals": [
                            {"reviewer": "reviewer-one", "approved": True},
                            {"reviewer": "reviewer-two", "approved": True},
                        ],
                    })
            (path / f"{split}.yaml").write_text(yaml.safe_dump({"cases": cases}))
        (path / "scoring.yaml").write_text(yaml.safe_dump({"schema_version": "1.0", "cases": notes}))
        yield path


def test_pack_exact_allocation_digest_and_content_free_summary(pack):
    from systematic_innovation_bench.restricted_preflight import digest_path

    summary = validate_restricted_pack(pack)
    assert summary.validation_count == 20
    assert summary.test_count == 20
    assert summary.family_counts == {family: count * 2 for family, count in ALLOCATIONS.items()}
    assert len(summary.digest) == 64
    serialized = json.dumps(summary.model_dump())
    assert "fictional causal" not in serialized
    assert str(pack) not in serialized
    assert validate_restricted_pack(pack).digest == summary.digest
    assert digest_path(pack) == summary.digest


def test_pack_refuses_unvalidated_extra_entries(pack):
    (pack / "undeclared.txt").write_text("unreviewed input")
    with pytest.raises(PackValidationError):
        validate_restricted_pack(pack)


@pytest.mark.parametrize("marker_kind", ["directory", "file"])
def test_pack_refuses_ignored_location_in_unrelated_git_worktree(pack, tmp_path, marker_kind):
    repository = tmp_path / "unrelated-public-worktree"
    repository.mkdir()
    if marker_kind == "directory":
        subprocess.run(["git", "-C", str(repository), "init", "-q"], check=True)
    else:
        (repository / ".git").write_text("gitdir: external-metadata\n")
    (repository / ".gitignore").write_text("ignored-pack/\n")
    relocated = repository / "ignored-pack"
    pack.rename(relocated)
    if marker_kind == "directory":
        ignored = subprocess.run(
            ["git", "-C", str(repository), "check-ignore", "ignored-pack/"],
            capture_output=True, check=False,
        )
        assert ignored.returncode == 0
    with pytest.raises(PackValidationError, match="PACK_INSIDE_GIT_WORKTREE"):
        validate_restricted_pack(relocated)


@pytest.mark.parametrize("fault", ["count", "duplicate", "split", "deep_script", "gold", "reviewer", "unknown_scoring", "schema"])
def test_pack_rejects_structural_faults_without_echoing_values(pack, fault, capsys):
    sentinel = "private" + "-fixture-" + "sentinel"
    data = yaml.safe_load((pack / "validation.yaml").read_text())
    scoring = yaml.safe_load((pack / "scoring.yaml").read_text())
    data["cases"][0]["prompt"] = sentinel
    if fault == "count":
        data["cases"].pop()
    elif fault == "duplicate":
        data["cases"][1]["id"] = data["cases"][0]["id"]
    elif fault == "split":
        data["cases"][0]["split"] = "development"
    elif fault == "deep_script":
        data["cases"][0]["conversation_script"]["user_turns"].pop()
    elif fault == "gold":
        scoring["cases"][0]["gold_mechanisms"] = []
    elif fault == "reviewer":
        scoring["cases"][0]["reviewer_approvals"][1]["reviewer"] = "reviewer-one"
    elif fault == "unknown_scoring":
        scoring["cases"][0]["case_id"] = "absent"
    elif fault == "schema":
        data["cases"][0]["unexpected"] = sentinel
    (pack / "validation.yaml").write_text(yaml.safe_dump(data))
    (pack / "scoring.yaml").write_text(yaml.safe_dump(scoring))
    with pytest.raises(PackValidationError) as error:
        validate_restricted_pack(pack)
    output = capsys.readouterr()
    leaked = sentinel in str(error.value) + output.out + output.err
    assert not leaked


def test_pack_refuses_worktree_paths_and_symlinked_files(pack, tmp_path):
    root = Path(__file__).resolve().parents[2]
    with pytest.raises(PackValidationError):
        validate_restricted_pack(root / "benchmark")
    original = pack / "validation.yaml"
    replacement = pack / "payload.yaml"
    original.rename(replacement)
    original.symlink_to(replacement)
    with pytest.raises(PackValidationError):
        validate_restricted_pack(pack)


def test_pack_rejects_malformed_yaml_without_content_in_error(pack):
    sentinel = "private" + "-syntax-" + "sentinel"
    (pack / "scoring.yaml").write_text("cases: [" + sentinel)
    with pytest.raises(PackValidationError) as error:
        validate_restricted_pack(pack)
    leaked = sentinel in str(error.value)
    assert not leaked


def test_external_private_schema_matches_wire_contract(pack):
    from jsonschema import Draft202012Validator

    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "study/restricted-pack.schema.json").read_text())
    payload = {name: yaml.safe_load((pack / f"{name}.yaml").read_text())
               for name in ("validation", "test", "scoring")}
    validator = Draft202012Validator(schema)
    validator.validate(payload)
    payload["scoring"]["cases"][0]["reviewer_approvals"] = []
    assert not validator.is_valid(payload)
