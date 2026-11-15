"""Content-free structural and scientific checks for study preregistration."""
from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

PRIMARY = "qualified_useful_distinct_mechanisms_per_1000_total_assistant_output_tokens"
CONDITIONS = ["vanilla", "generic-brainstorm", "format-matched", "established-method", "full-skill"]
STAGES = ["six_case_feasibility", "twelve_case_rehearsal", "development_60", "validation_20",
          "cross_agent_validation", "sealed_20", "report", "stop"]
QUALITY = {"relevance_min": 2, "constraint_alignment_min": 2, "causal_clarity_min": 2,
           "plausibility_min": 1, "critical_safety_violation": False,
           "application_order": "gate_candidates_then_deduplicate"}
REQUIRED = {
    "study_id", "status", "candidate_commit", "runner_commit", "corpus_digests", "primary_endpoint",
    "quality_gate", "interaction_protocol", "stage_gates", "secondary_endpoints", "conditions",
    "analysis_unit", "bootstrap", "missingness", "exclusions", "pilot_rule", "judge_acceptance",
    "budgets", "sealed_test_policy", "primary_contrast", "ablations", "pilot_values",
    "measurement_freeze", "validation_policy", "stopping_rules", "multiplicity",
}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _number(value: Any, minimum: float, *, strict: bool = False) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and (value > minimum if strict else value >= minimum))


def validate_preregistration(document: object) -> list[str]:
    """Return rule identifiers only, never supplied text or protected values.

    A valid draft describes a protocol, not permission to execute. Freeze adds
    immutable identifiers, observed pilot quantities and accepted measurement
    evidence. Stage authorization and restricted preflight remain separate gates.
    """
    if not isinstance(document, Mapping):
        return ["PREREG_REQUIRED_FIELDS"]
    errors = []
    if not REQUIRED <= document.keys() or document.get("status") not in ("draft", "frozen"):
        errors.append("PREREG_REQUIRED_FIELDS")
    if (document.get("primary_endpoint") != PRIMARY
            or document.get("primary_contrast") != {"treatment": "full-skill", "control": "format-matched"}
            or document.get("conditions") != CONDITIONS
            or document.get("analysis_unit") != "case"):
        errors.append("PREREG_PRIMARY_CONTRACT")
    if document.get("quality_gate") != QUALITY:
        errors.append("PREREG_QUALITY_GATE")
    protocol = _mapping(document.get("interaction_protocol"))
    if (protocol.get("candidate_source") != "final_portfolio"
            or protocol.get("token_denominator") != "all_assistant_turns"
            or protocol.get("deep_disclosures") != 2
            or protocol.get("disclosure_parity") != "byte_identical_across_conditions"):
        errors.append("PREREG_INFORMATION_PARITY")
    if document.get("stage_gates") != STAGES:
        errors.append("PREREG_STAGE_ORDER")
    if _mapping(document.get("ablations")).get("split") != "development":
        errors.append("PREREG_ABLATION_SPLIT")
    bootstrap = _mapping(document.get("bootstrap"))
    if (bootstrap.get("unit") != "case" or bootstrap.get("methods") != ["percentile", "BCa"]
            or document.get("multiplicity") != "Holm_step_down_secondary_contrasts"):
        errors.append("PREREG_ANALYSIS_UNIT")
    judge = _mapping(document.get("judge_acceptance"))
    if (judge.get("pairwise_agreement_min") != 0.75
            or judge.get("krippendorff_alpha_min") != 0.67
            or not _number(judge.get("minimum_trained_annotators"), 2)
            or not _number(judge.get("minimum_stratified_pairs_per_round"), 40)
            or judge.get("maximum_prompt_revisions") != 3
            or judge.get("blinding") != "out_of_repo_seed_or_isolated_exported_packet"
            or judge.get("fallback") != "human_primary_LLM_exploratory"):
        errors.append("PREREG_CALIBRATION")
    sealed = _mapping(document.get("sealed_test_policy"))
    validation = _mapping(document.get("validation_policy"))
    if (sealed.get("maximum_executions") != 1
            or sealed.get("candidate_unchanged") is not True
            or sealed.get("analysis_frozen") is not True
            or sealed.get("operator_approval_required") is not True
            or sealed.get("terminal_transition") != "report_then_stop_no_candidate_revision"
            or validation.get("operator_approval_required") is not True
            or validation.get("feedback_to_development") != "release_eligibility_decision_only"):
        errors.append("PREREG_RESTRICTED_FEEDBACK")
    if document.get("status") != "frozen":
        return errors
    if any(not isinstance(document.get(name), str)
           or re.fullmatch(r"[a-f0-9]{40}", document[name]) is None
           for name in ("candidate_commit", "runner_commit")):
        errors.append("FREEZE_REVISIONS")
    digests = _mapping(document.get("corpus_digests"))
    if (set(digests) != {"public", "validation", "test"}
            or any(not isinstance(value, str) or re.fullmatch(r"[a-f0-9]{64}", value) is None
                   for value in digests.values())):
        errors.append("FREEZE_DIGESTS")
    values = _mapping(document.get("pilot_values"))
    if (not _number(values.get("variance"), 0)
            or not _number(values.get("reliability"), 0)
            or not _number(values.get("practical_effect"), 0, strict=True)
            or not _number(values.get("equivalence_margin"), 0)
            or type(values.get("repetitions")) is not int
            or values.get("repetitions", 0) < 1):
        errors.append("FREEZE_PILOT_VALUES")
    measurement = _mapping(document.get("measurement_freeze"))
    if (any(not isinstance(measurement.get(name), str) or not measurement[name].strip()
            for name in ("extraction_version", "judge_version", "conversation_protocol"))
            or not isinstance(measurement.get("rehearsal_run_digest"), str)
            or re.fullmatch(r"[a-f0-9]{64}", measurement.get("rehearsal_run_digest", "")) is None
            or judge.get("status") not in ("accepted", "human-primary")):
        errors.append("FREEZE_MEASUREMENT")
    budgets = _mapping(document.get("budgets"))
    if (type(budgets.get("max_calls")) is not int or budgets.get("max_calls", 0) < 1
            or not _number(budgets.get("max_cost"), 0, strict=True)
            or type(budgets.get("max_concurrency")) is not int
            or budgets.get("max_concurrency", 0) < 1):
        errors.append("FREEZE_BUDGET")
    return errors
