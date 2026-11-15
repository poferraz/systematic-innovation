import json
from datetime import UTC, datetime

import pytest

from systematic_innovation_bench.models import (
    BenchmarkCase,
    Condition,
    ConversationScript,
    InteractionMode,
    Job,
    MechanismQuality,
    RunConfig,
    TurnResponse,
)


def case_data(**updates):
    data = {
        "id": "case-001",
        "family": "synthetic-mechanism",
        "domain": "operations",
        "split": "development",
        "prompt": "Improve this system",
        "strata": {"mode": "quick"},
    }
    return data | updates


def test_case_rejects_sealed_content_in_public_split():
    with pytest.raises(ValueError, match="hidden mechanisms"):
        BenchmarkCase(**case_data(hidden_mechanisms=["pooled demand"]))


def test_job_has_stable_roundtrip_identity():
    job = Job(
        run_id="run-001",
        case_id="case-001",
        condition=Condition.FULL_SKILL,
        replicate=0,
        model="example-model",
        host="inbox",
        prompt="Prompt",
        created_at=datetime(2026, 8, 31, tzinfo=UTC),
    )
    assert job.job_id == "run-001:case-001:full-skill:0:example-model:inbox"
    assert Job.model_validate_json(job.model_dump_json()) == job
    assert len(job.prompt_sha256) == 64


def test_multi_turn_case_requires_a_fixed_disclosure_script():
    with pytest.raises(ValueError, match="conversation script"):
        BenchmarkCase(**case_data(interaction_mode=InteractionMode.CONTROLLED_MULTI_TURN))
    script = ConversationScript(user_turns=("Shared context.", "Produce final portfolio now."))
    assert script.maximum_assistant_turns == 3
    assert ConversationScript.model_validate_json(script.model_dump_json()) == script
    with pytest.raises(ValueError):
        BenchmarkCase(**case_data(conversation_script=script))


@pytest.mark.parametrize("field,value", [("relevance", 4), ("plausibility", -1)])
def test_quality_ratings_are_anchored(field, value):
    data = {
        "relevance": 2,
        "constraint_alignment": 2,
        "causal_clarity": 2,
        "plausibility": 1,
        "critical_safety_violation": False,
    }
    with pytest.raises(ValueError):
        MechanismQuality(**(data | {field: value}))


def test_response_and_config_validate_boundaries():
    with pytest.raises(ValueError):
        TurnResponse(job_id="j", turn_index=1, content="bad index")
    with pytest.raises(ValueError):
        RunConfig(run_id="r", models=("m",), model_allowlist=("m",), max_calls=0)
    with pytest.raises(ValueError):
        BenchmarkCase(**case_data(strata={}))
    assert "additionalProperties" in json.dumps(BenchmarkCase.model_json_schema())


def test_subprocess_configuration_is_explicit_and_bounded():
    cfg = RunConfig(
        run_id="r",
        models=("m",),
        model_allowlist=("m",),
        adapter_command=("python",),
        allowed_executables=("python",),
        environment_allowlist=("LANG",),
        secret_environment_keys=("RUN_CREDENTIAL",),
        timeout_seconds=2,
        max_output_bytes=100,
    )
    assert cfg.adapter_command == ("python",)
    with pytest.raises(ValueError):
        RunConfig(run_id="r", models=("m",), model_allowlist=("m",), timeout_seconds=0)


def test_conversation_and_response_reject_corrupt_final_text_and_identity():
    from systematic_innovation_bench.models import (
        ConversationRecord,
        ConversationTurn,
        ResponseRecord,
    )

    turns = (
        ConversationTurn(turn_index=1, role="user", content="request"),
        ConversationTurn(turn_index=2, role="assistant", content="actual final", output_tokens=20),
    )
    data = {
        "job_id": "j",
        "turns": turns,
        "turn_response_ids": ("j:2:0",),
        "final_response": "actual final",
        "final_response_output_tokens": 20,
        "total_assistant_output_tokens": 20,
    }
    record = ConversationRecord(**data)
    for update in (
        {"final_response": "forged"},
        {"final_response_output_tokens": 10},
        {"total_assistant_output_tokens": 10},
    ):
        with pytest.raises(ValueError):
            ConversationRecord(**(data | update))
    with pytest.raises(ValueError):
        ResponseRecord(job_id="other", status="succeeded", conversation=record)


def test_empty_causal_dimensions_and_response_identity_are_rejected():
    from systematic_innovation_bench.models import Mechanism, ResponseRecord

    data = {
        "id": "m",
        "intervention_point": "queue",
        "actor": "staff",
        "changed_flow": "requests",
        "causal_operation": "pool",
        "intended_effect": "less delay",
    }
    for field in data:
        with pytest.raises(ValueError):
            Mechanism(**(data | {field: ""}))
    with pytest.raises(ValueError):
        ResponseRecord(job_id="", status="failed")


@pytest.mark.parametrize("value", [True, "123", 12.5])
def test_protocol_token_counts_reject_coercible_noninteger_scalars(value):
    with pytest.raises(ValueError):
        TurnResponse(job_id="j", turn_index=2, content="text", output_tokens=value)


@pytest.mark.parametrize(
    "field,value",
    [
        ("relevance", True),
        ("causal_clarity", "2"),
        ("plausibility", 1.5),
        ("critical_safety_violation", "false"),
    ],
)
def test_quality_judgments_reject_scalar_coercion(field, value):
    data = {
        "relevance": 2,
        "constraint_alignment": 2,
        "causal_clarity": 2,
        "plausibility": 1,
        "critical_safety_violation": False,
    }
    with pytest.raises(ValueError):
        MechanismQuality(**(data | {field: value}))


@pytest.mark.parametrize(
    "field,value",
    [
        ("max_calls", "50"),
        ("max_concurrency", True),
        ("dry_run", "false"),
        ("max_cost", "5.0"),
        ("max_cost", True),
    ],
)
def test_configuration_limits_reject_scalar_coercion(field, value):
    with pytest.raises(ValueError):
        RunConfig(**({"run_id": "r", "models": ["m"], "model_allowlist": ["m"]} | {field: value}))
