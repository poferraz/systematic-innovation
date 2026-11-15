"""Immutable controlled disclosures, independent of assistant questions or condition."""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from .models import BenchmarkCase, ConversationRecord, ConversationTurn, Job, TurnJob, TurnResponse
from .redaction import redact_model
from .store import append_record, turn_responses_for_job


@dataclass(frozen=True)
class ConversationState:
    job: Job
    case: BenchmarkCase
    turns: tuple[ConversationTurn, ...] = ()
    responses: tuple[TurnResponse, ...] = ()
    responses_path: Path | None = None
    secret_values: tuple[str, ...] = ()

    @property
    def assistant_turn_count(self) -> int:
        return len(self.turns) // 2

    @property
    def maximum_assistant_turns(self) -> int:
        return (
            self.case.conversation_script.maximum_assistant_turns
            if self.case.conversation_script
            else 1
        )

    @property
    def is_budget_stopped(self) -> bool:
        return any(response.status == "budget-stopped" for response in self.responses)

    @property
    def is_complete(self) -> bool:
        return self.assistant_turn_count == self.maximum_assistant_turns


def start_conversation(
    job: Job,
    case: BenchmarkCase,
    *,
    responses_path: Path | None = None,
    secret_values: Sequence[str] = (),
) -> ConversationState:
    if (
        job.case_id != case.id
        or job.prompt != case.prompt
        or job.conversation_script != case.conversation_script
        or job.interaction_mode != case.interaction_mode
    ):
        raise ValueError("job and case conversation contracts differ")
    return ConversationState(
        job=job, case=case, responses_path=responses_path, secret_values=tuple(secret_values)
    )


def next_turn_job(state: ConversationState) -> TurnJob | None:
    if state.is_complete or state.is_budget_stopped:
        return None
    if not state.turns:
        content = state.case.prompt
    else:
        if state.case.conversation_script is None:
            raise ValueError("single-turn conversation exceeded maximum")
        content = state.case.conversation_script.user_turns[state.assistant_turn_count - 1]
    transcript = (
        *state.turns,
        ConversationTurn(turn_index=len(state.turns) + 1, role="user", content=content),
    )
    pending = TurnJob.from_state(state, transcript)
    attempts = [
        response.attempt
        for response in state.responses
        if response.turn_index == pending.assistant_turn_index
    ]
    if attempts:
        pending = TurnJob.model_validate(
            pending.model_dump() | {"attempt": max(attempts) + 1, "turn_id": ""}
        )
    return pending


def accept_turn(
    state: ConversationState, turn_job: TurnJob, response: TurnResponse
) -> ConversationState:
    response = redact_model(response, state.secret_values)
    expected = next_turn_job(state)
    if expected is None or expected != turn_job:
        raise ValueError("turn job is not the deterministic conversation continuation")
    if (
        response.job_id != turn_job.job_id
        or response.turn_index != turn_job.assistant_turn_index
        or response.attempt != turn_job.attempt
    ):
        raise ValueError("response does not correlate to pending turn")
    if response.status == "succeeded" and not response.content.strip():
        raise ValueError("successful turn requires nonempty assistant text")
    if state.responses_path is not None:
        append_record(state.responses_path, response, secret_values=state.secret_values)
    responses = (*state.responses, response)
    if response.status in ("failed", "budget-stopped"):
        return replace(state, responses=responses)
    assistant = ConversationTurn(
        turn_index=response.turn_index,
        role="assistant",
        content=response.content,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost=response.cost,
        latency_seconds=response.latency_seconds,
        timestamp=response.created_at,
    )
    return replace(state, turns=(*turn_job.transcript, assistant), responses=responses)


def complete_conversation(state: ConversationState) -> ConversationRecord:
    if not state.is_complete:
        raise ValueError("conversation cannot finalize before its last assistant turn")
    tokens = [response.output_tokens for response in state.responses]
    costs = [response.cost for response in state.responses]
    latencies = [response.latency_seconds for response in state.responses]
    return ConversationRecord(
        job_id=state.job.job_id,
        turns=state.turns,
        turn_response_ids=tuple(response.turn_id for response in state.responses),
        final_response=state.turns[-1].content,
        final_response_output_tokens=state.turns[-1].output_tokens,
        total_assistant_output_tokens=sum(value for value in tokens if value is not None)
        if all(value is not None for value in tokens)
        else None,
        total_cost=sum(value for value in costs if value is not None)
        if all(value is not None for value in costs)
        else None,
        total_latency_seconds=sum(value for value in latencies if value is not None)
        if all(value is not None for value in latencies)
        else None,
    )


def resume_conversation(
    job: Job,
    case: BenchmarkCase,
    responses: Sequence[TurnResponse],
    *,
    responses_path: Path | None = None,
    secret_values: Sequence[str] = (),
) -> ConversationState:
    state = start_conversation(job, case, secret_values=secret_values)
    for response in turn_responses_for_job(responses, job.job_id):
        pending = next_turn_job(state)
        if pending is None:
            raise ValueError("persisted response exceeds conversation maximum")
        state = accept_turn(state, pending, response)
    return replace(state, responses_path=responses_path)
