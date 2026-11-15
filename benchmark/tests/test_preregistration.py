"""Draft study contracts and deterministic advancement/freeze checks."""
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ["vanilla", "generic-brainstorm", "format-matched", "established-method", "full-skill"]
PRIMARY = "qualified_useful_distinct_mechanisms_per_1000_total_assistant_output_tokens"


def document(filename):
    return yaml.safe_load((ROOT / "study" / filename).read_text())


def test_preregistration_complete_and_primary_contract():
    p = document("preregistration.yaml")
    assert {"study_id", "status", "candidate_commit", "runner_commit", "corpus_digests",
            "primary_endpoint", "quality_gate", "interaction_protocol", "stage_gates",
            "secondary_endpoints", "conditions", "analysis_unit", "bootstrap", "missingness",
            "exclusions", "pilot_rule", "judge_acceptance", "budgets", "sealed_test_policy"} <= p.keys()
    assert p["status"] == "draft"
    assert p["primary_endpoint"] == PRIMARY
    assert p["primary_contrast"] == {"treatment": "full-skill", "control": "format-matched"}
    assert p["conditions"] == CONDITIONS
    assert p["analysis_unit"] == "case"
    assert p["quality_gate"] == {
        "relevance_min": 2, "constraint_alignment_min": 2, "causal_clarity_min": 2,
        "plausibility_min": 1, "critical_safety_violation": False,
        "application_order": "gate_candidates_then_deduplicate",
    }
    assert p["interaction_protocol"]["candidate_source"] == "final_portfolio"
    assert p["interaction_protocol"]["token_denominator"] == "all_assistant_turns"
    assert p["bootstrap"]["unit"] == "case"
    assert p["bootstrap"]["methods"] == ["percentile", "BCa"]
    assert p["multiplicity"] == "Holm_step_down_secondary_contrasts"
    assert p["ablations"]["split"] == "development"
    assert p["sealed_test_policy"]["maximum_executions"] == 1


def test_freeze_rejects_missing_pilot_values_and_digests():
    from systematic_innovation_bench.study_contracts import validate_preregistration

    draft = document("preregistration.yaml")
    assert validate_preregistration(draft) == []
    frozen = deepcopy(draft)
    frozen["status"] = "frozen"
    assert validate_preregistration(frozen)
    frozen["candidate_commit"] = "a" * 40
    frozen["runner_commit"] = "b" * 40
    frozen["corpus_digests"] = {"public": "c" * 64, "validation": "d" * 64, "test": "e" * 64}
    frozen["pilot_values"] = {"variance": 0.5, "reliability": 0.8, "practical_effect": 0.3,
                             "equivalence_margin": 0.1, "repetitions": 4}
    frozen["measurement_freeze"] = {
        "extraction_version": "1", "judge_version": "human-primary-v1",
        "conversation_protocol": "fixed-two-disclosures-v1",
        "rehearsal_run_digest": "f" * 64,
    }
    frozen["budgets"] = {"max_calls": 1000, "max_cost": 20.0, "max_concurrency": 2,
                         "retry_limit": 1, "failure_threshold": 0.2}
    frozen["judge_acceptance"]["status"] = "human-primary"
    assert validate_preregistration(frozen) == []
    for field in frozen["pilot_values"]:
        invalid = deepcopy(frozen)
        invalid["pilot_values"][field] = None
        assert validate_preregistration(invalid)


def test_judge_acceptance_and_human_blinding_contract():
    judge = document("preregistration.yaml")["judge_acceptance"]
    assert judge["pairwise_agreement_min"] == 0.75
    assert judge["krippendorff_alpha_min"] == 0.67
    assert judge["minimum_trained_annotators"] >= 2
    assert judge["minimum_stratified_pairs_per_round"] >= 40
    assert judge["maximum_prompt_revisions"] == 3
    assert judge["blinding"] == "out_of_repo_seed_or_isolated_exported_packet"
    assert judge["abstention_label"] == "abstain"
    assert set(judge["separate_agreement"]) == {
        "mechanism_identity", "relevance", "constraint_alignment", "causal_clarity",
        "plausibility", "critical_safety_violation",
    }


def test_six_case_and_twelve_case_gates_are_exact_and_pending():
    gates = document("stage-gates.yaml")
    six = gates["six_case_feasibility"]
    assert six["case_ids"] == [f"{prefix}-dev-001" for prefix in ("syn", "red", "sys", "pre", "tri", "adv")]
    assert six["conditions"] == CONDITIONS
    assert six["replicates"] == 1
    assert six["allow_effect_claims"] is False
    assert six["status"] == "pending"
    assert set(six["zero_tolerance_checks"]) == {
        "job_correlation", "transcript_equality", "append_only_turns", "mid_conversation_resume",
        "secret_redaction", "complete_token_accounting", "budget_enforcement", "report_generation",
    }
    twelve = gates["twelve_case_rehearsal"]
    assert twelve["case_ids"] == [f"{prefix}-dev-{n:03d}" for prefix in ("syn", "red", "sys", "pre", "tri", "adv") for n in (1, 2)]
    assert twelve["conditions"] == CONDITIONS
    assert twelve["replicates"] == 2
    assert twelve["requires"] == ["six_case_feasibility"]
    assert twelve["allow_effect_claims"] is False
    assert twelve["status"] == "pending"
    assert gates["development_60"]["requires"] == ["six_case_feasibility", "twelve_case_rehearsal"]
    assert gates["validation_20"]["feedback_to_development"] == "release_eligibility_decision_only"
    assert gates["sealed_20"]["next_states"] == ["report", "stop"]
    assert gates["final_report_allowed"] is False


@pytest.mark.parametrize("mutation", ["primary", "gate", "token", "stage", "sealed", "calibration"])
def test_contract_validation_rejects_scientific_boundary_drift(mutation):
    from systematic_innovation_bench.study_contracts import validate_preregistration

    p = document("preregistration.yaml")
    if mutation == "primary":
        p["primary_endpoint"] = "raw_count"
    elif mutation == "gate":
        p["quality_gate"]["relevance_min"] = 1
    elif mutation == "token":
        p["interaction_protocol"]["token_denominator"] = "final_response_only"
    elif mutation == "stage":
        p["stage_gates"] = ["development_60"]
    elif mutation == "sealed":
        p["sealed_test_policy"]["maximum_executions"] = 2
    else:
        p["judge_acceptance"]["pairwise_agreement_min"] = 0.5
    assert validate_preregistration(p)


@pytest.mark.parametrize("payload", [None, [], "untrusted document", 123])
def test_preregistration_non_mapping_returns_content_free_failure(payload):
    from systematic_innovation_bench.study_contracts import validate_preregistration

    assert validate_preregistration(payload) == ["PREREG_REQUIRED_FIELDS"]
