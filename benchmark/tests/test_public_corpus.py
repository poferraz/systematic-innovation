"""Public corpus contracts: fixed allocation, information parity and leakage limits."""
import re
from collections import Counter
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ALLOCATIONS = {
    "synthetic-mechanism": {"development": 14, "validation": 5, "test": 5},
    "counterfactual-rediscovery": {"development": 10, "validation": 3, "test": 3},
    "open-ended-systemic": {"development": 18, "validation": 6, "test": 6},
    "preservation-no-change": {"development": 6, "validation": 2, "test": 2},
    "trigger-scope": {"development": 6, "validation": 2, "test": 2},
    "adversarial-high-stakes": {"development": 6, "validation": 2, "test": 2},
}
FILES = [
    ("synthetic.yaml", "syn", "synthetic-mechanism", 14),
    ("rediscovery.yaml", "red", "counterfactual-rediscovery", 10),
    ("open-ended.yaml", "sys", "open-ended-systemic", 18),
    ("preservation.yaml", "pre", "preservation-no-change", 6),
    ("trigger.yaml", "tri", "trigger-scope", 6),
    ("adversarial.yaml", "adv", "adversarial-high-stakes", 6),
]


def read_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def all_cases():
    return [case for filename, *_ in FILES
            for case in read_yaml(ROOT / "cases/development" / filename)["cases"]]


def test_manifest_fixes_exact_100_case_allocation():
    manifest = read_yaml(ROOT / "study/corpus-manifest.yaml")
    assert manifest["allocations"] == ALLOCATIONS
    assert {split: sum(row[split] for row in manifest["allocations"].values())
            for split in ("development", "validation", "test")} == {
        "development": 60, "validation": 20, "test": 20,
    }


@pytest.mark.parametrize("filename,prefix,family,count", FILES)
def test_family_counts_ids_and_public_contract(filename, prefix, family, count):
    from systematic_innovation_bench.models import BenchmarkCase

    cases = read_yaml(ROOT / "cases/development" / filename)["cases"]
    assert len(cases) == count
    assert [case["id"] for case in cases] == [f"{prefix}-dev-{n:03d}" for n in range(1, count + 1)]
    for case in cases:
        assert case["family"] == family
        assert case["split"] == "development"
        assert not ({"gold", "answer", "known_solution", "hidden_mechanisms", "source_url"} & case.keys())
        BenchmarkCase.model_validate(case)


def test_public_interaction_contract_and_strata():
    cases = all_cases()
    assert len({case["id"] for case in cases}) == 60
    prompts = [re.sub(r"\W+", " ", case["prompt"].lower()).strip() for case in cases]
    assert len(set(prompts)) == 60
    domains = Counter(case["domain"] for case in cases)
    assert len(domains) >= 8
    assert max(domains.values()) <= 12
    assert sum(case["strata"]["preservation"] == "hard" for case in cases) >= 20
    assert sum(case["strata"]["stakeholder_conflict"] == "present" for case in cases) >= 15
    for mode in ("quick", "deep"):
        assert sum(case["expected_mode"] == mode for case in cases) >= 20
    required = {"mode", "ambiguity", "constraint_severity", "stakeholder_complexity",
                "solution_space", "opportunity_type", "domain_knowledge", "preservation",
                "stakeholder_conflict"}
    for case in cases:
        assert required <= case["strata"].keys()
        if case["expected_mode"] == "deep":
            assert case["interaction_mode"] == "controlled-multi-turn"
            turns = case["conversation_script"]["user_turns"]
            assert len(turns) == 2 and all(turn.strip() for turn in turns)
            assert "final portfolio" in turns[-1].lower()
        else:
            assert case["interaction_mode"] == "single-turn"
            assert case.get("conversation_script") is None


def test_open_ended_constraints_and_fair_disclosures():
    cases = read_yaml(ROOT / "cases/development/open-ended.yaml")["cases"]
    assert len({case["domain"] for case in cases}) >= 7
    assert sum(case["expected_mode"] == "deep" for case in cases) >= 9
    assert sum(case["strata"]["preservation"] == "hard" for case in cases) >= 6
    assert all(len(case["prompt"].split()) >= 35 for case in cases)
    for case in all_cases():
        text = case["prompt"] + " ".join(case.get("conversation_script", {}).get("user_turns", []))
        assert not re.search(r"Reasoning Cells|mechanism ledger|saturation detection|full-skill", text, re.IGNORECASE)


def test_preservation_trigger_and_adversarial_polarities():
    preservation = read_yaml(ROOT / "cases/development/preservation.yaml")["cases"]
    assert sum("no change" in case["prompt"].lower() for case in preservation) >= 2
    trigger = read_yaml(ROOT / "cases/development/trigger.yaml")["cases"]
    assert Counter(case["strata"]["trigger_polarity"] for case in trigger) == {
        "positive": 2, "negative": 2, "boundary": 2,
    }
    assert all(case["should_trigger"] is False for case in trigger if case["strata"]["trigger_polarity"] == "negative")
    adversarial = read_yaml(ROOT / "cases/development/adversarial.yaml")["cases"]
    assert all(case["strata"]["safety_constraint"] == "explicit" for case in adversarial)


def test_rediscovery_search_review_is_complete():
    review = read_yaml(ROOT / "study/rediscovery-leakage-review.yaml")
    assert set(review["cases"]) == {f"red-dev-{i:03d}" for i in range(1, 11)}
    assert all(item["result"] == "passed" and item["reviewed_at"] for item in review["cases"].values())
