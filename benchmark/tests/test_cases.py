import json
from pathlib import Path

import pytest
import yaml
from jsonschema import ValidationError, validate

from systematic_innovation_bench.cases import load_cases, summarize_strata


def write_cases(path, ids=("b", "a"), split="development", **updates):
    data = [
        {
            "id": i,
            "family": "synthetic-mechanism",
            "domain": "operations",
            "split": split,
            "prompt": "A safe public fictional system.",
            "strata": {"mode": "quick"},
        }
        | updates
        for i in ids
    ]
    path.write_text(yaml.safe_dump({"cases": data}))
    return path


def test_loading_is_sorted_and_strata_are_counted(tmp_path):
    path = write_cases(tmp_path / "cases.yaml")
    cases = load_cases([path], expected_split="development")
    assert [c.id for c in cases] == ["a", "b"]
    assert summarize_strata(cases) == {"domain": {"operations": 2}, "mode": {"quick": 2}}


@pytest.mark.parametrize(
    "updates", [{"strata": {}}, {"hidden_mechanisms": ["private"]}, {"unknown": True}]
)
def test_loader_rejects_invalid_records_without_content_echo(tmp_path, updates):
    path = write_cases(tmp_path / "cases.yaml", **updates)
    with pytest.raises(ValueError) as caught:
        load_cases([path])
    assert "A safe public" not in str(caught.value)


def test_duplicates_split_mismatch_and_public_restricted_path_are_rejected(tmp_path):
    a = write_cases(tmp_path / "a.yaml", ids=("a",))
    b = write_cases(tmp_path / "b.yaml", ids=("a",))
    with pytest.raises(ValueError, match="duplicate"):
        load_cases([a, b])
    with pytest.raises(ValueError, match="split"):
        load_cases([a], expected_split="validation")
    write_cases(a, split="validation")
    with pytest.raises(ValueError, match="outside"):
        load_cases([a], public_root=tmp_path)


def test_public_case_schema_forbids_hidden_fields_and_checks_scripts(tmp_path):
    schema = json.loads((Path(__file__).parents[1] / "schemas/case.schema.json").read_text())
    path = write_cases(tmp_path / "case.yaml", ids=("a",))
    case = yaml.safe_load(path.read_text())["cases"][0]
    validate(case, schema)
    with pytest.raises(ValidationError):
        validate(case | {"hidden_mechanisms": []}, schema)
    with pytest.raises(ValidationError):
        validate(case | {"interaction_mode": "controlled-multi-turn"}, schema)
