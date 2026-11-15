from datetime import UTC, datetime

import pytest

from systematic_innovation_bench.conversation import (
    accept_turn,
    complete_conversation,
    next_turn_job,
    resume_conversation,
    start_conversation,
)
from systematic_innovation_bench.models import (
    BenchmarkCase,
    Condition,
    ConversationScript,
    InteractionMode,
    Job,
    TurnResponse,
)
from systematic_innovation_bench.store import read_records


def case(deep=True):
    return BenchmarkCase(
        id="c",
        family="open-ended-systemic",
        domain="operations",
        split="development",
        prompt="Initial challenge",
        strata={"mode": "deep" if deep else "quick"},
        interaction_mode=InteractionMode.CONTROLLED_MULTI_TURN
        if deep
        else InteractionMode.SINGLE_TURN,
        conversation_script=ConversationScript(
            user_turns=("Stakeholders and safeguards.", "Resources and final portfolio request.")
        )
        if deep
        else None,
    )


def job(condition=Condition.VANILLA, deep=True):
    c = case(deep)
    return Job(
        run_id="r",
        case_id=c.id,
        condition=condition,
        replicate=0,
        model="m",
        host="inbox",
        prompt=c.prompt,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        interaction_mode=c.interaction_mode,
        conversation_script=c.conversation_script,
    )


def response(turn_job, tokens=20, **updates):
    return TurnResponse(
        **(
            {
                "job_id": turn_job.job_id,
                "turn_index": turn_job.assistant_turn_index,
                "content": "Portfolio or questions?",
                "output_tokens": tokens,
                "cost": 0.1,
                "latency_seconds": 1.0,
            }
            | updates
        )
    )


def test_every_condition_receives_identical_disclosures_and_all_tokens_count(tmp_path):
    transcripts = []
    for condition in Condition:
        state = start_conversation(
            job(condition), case(), responses_path=tmp_path / f"{condition}.jsonl"
        )
        old = state
        with pytest.raises(ValueError):
            complete_conversation(state)
        for tokens in (20, 30, 120):
            turn = next_turn_job(state)
            assert turn is not None
            state = accept_turn(state, turn, response(turn, tokens))
        assert old.turns == ()
        assert next_turn_job(state) is None
        record = complete_conversation(state)
        assert record.final_response_output_tokens == 120
        assert record.total_assistant_output_tokens == 170
        assert record.total_cost == pytest.approx(0.3)
        assert record.total_latency_seconds == 3.0
        assert [t.role for t in state.turns] == ["user", "assistant"] * 3
        assert len(read_records(tmp_path / f"{condition}.jsonl", TurnResponse)) == 3
        transcripts.append([t.content for t in state.turns if t.role == "user"])
    assert all(
        transcript
        == [
            "Initial challenge",
            "Stakeholders and safeguards.",
            "Resources and final portfolio request.",
        ]
        for transcript in transcripts
    )


def test_resume_after_every_turn_reconstructs_immutable_state():
    state = start_conversation(job(), case())
    responses = []
    for _ in range(3):
        turn = next_turn_job(state)
        accepted = response(turn)
        state = accept_turn(state, turn, accepted)
        responses.append(accepted)
        restored = resume_conversation(job(), case(), responses)
        assert restored == state


def test_protocol_mismatch_and_replaying_a_turn_are_rejected():
    state = start_conversation(job(), case())
    turn = next_turn_job(state)
    with pytest.raises(ValueError):
        accept_turn(
            state, turn.model_copy(update={"system_instructions": "changed"}), response(turn)
        )
    with pytest.raises(ValueError):
        accept_turn(state, turn, response(turn, job_id="other"))
    advanced = accept_turn(state, turn, response(turn))
    with pytest.raises(ValueError):
        accept_turn(advanced, turn, response(turn))


def test_single_turn_and_missing_usage_are_preserved():
    state = start_conversation(job(deep=False), case(False))
    turn = next_turn_job(state)
    state = accept_turn(state, turn, response(turn, tokens=None))
    assert complete_conversation(state).total_assistant_output_tokens is None
    assert next_turn_job(state) is None


def test_retry_attempt_outputs_count_toward_efficiency_without_changing_disclosures():
    state = start_conversation(job(deep=False), case(False))
    turn = next_turn_job(state)
    state = accept_turn(state, turn, response(turn, tokens=7, status="failed"))
    pending = next_turn_job(state)
    assert pending.attempt == 1
    assert [t.content for t in pending.transcript] == ["Initial challenge"]
    state = accept_turn(state, pending, response(pending, tokens=13, attempt=1))
    assert complete_conversation(state).total_assistant_output_tokens == 20
