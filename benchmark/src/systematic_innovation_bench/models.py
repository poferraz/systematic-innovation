"""Versioned records shared by all benchmark boundaries."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    model_validator,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Condition(StrEnum):
    VANILLA = "vanilla"
    GENERIC_BRAINSTORM = "generic-brainstorm"
    FORMAT_MATCHED = "format-matched"
    ESTABLISHED_METHOD = "established-method"
    FULL_SKILL = "full-skill"
    ABLATION = "ablation"


class InteractionMode(StrEnum):
    SINGLE_TURN = "single-turn"
    CONTROLLED_MULTI_TURN = "controlled-multi-turn"


Status = Literal["succeeded", "failed", "refused", "budget-stopped"]


class ConversationScript(StrictModel):
    user_turns: tuple[str, ...] = Field(min_length=1)
    maximum_assistant_turns: StrictInt = 0

    @model_validator(mode="after")
    def check_script(self) -> Self:
        if any(not turn.strip() for turn in self.user_turns):
            raise ValueError("conversation script disclosures must be non-empty")
        expected = len(self.user_turns) + 1
        if self.maximum_assistant_turns not in (0, expected):
            raise ValueError("conversation script maximum does not match disclosures")
        object.__setattr__(self, "maximum_assistant_turns", expected)
        return self


class BenchmarkCase(StrictModel):
    id: str = Field(min_length=1)
    family: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    split: Literal["development", "validation", "test"]
    prompt: str = Field(min_length=1)
    strata: dict[str, str] = Field(min_length=1)
    expected_mode: Literal["quick", "deep"] | None = None
    should_trigger: StrictBool | None = None
    interaction_mode: InteractionMode = InteractionMode.SINGLE_TURN
    conversation_script: ConversationScript | None = None
    hidden_mechanisms: tuple[str, ...] = ()

    @model_validator(mode="after")
    def protect_public_cases(self) -> Self:
        if self.split == "development" and self.hidden_mechanisms:
            raise ValueError("hidden mechanisms are forbidden in public development cases")
        if self.interaction_mode is InteractionMode.CONTROLLED_MULTI_TURN:
            if self.conversation_script is None:
                raise ValueError("controlled multi-turn case requires conversation script")
        elif self.conversation_script is not None:
            raise ValueError("single-turn case cannot contain conversation script")
        return self


class Job(StrictModel):
    run_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    condition: Condition
    replicate: StrictInt = Field(ge=0)
    model: str = Field(min_length=1)
    host: str = Field(min_length=1)
    prompt: str
    created_at: datetime
    split: Literal["development", "validation", "test"] = "development"
    interaction_mode: InteractionMode = InteractionMode.SINGLE_TURN
    conversation_script: ConversationScript | None = None
    system_instructions: str = ""
    model_parameters: dict[str, Any] = Field(default_factory=dict)
    job_id: str = ""
    prompt_sha256: str = ""

    @model_validator(mode="after")
    def derive_identity(self) -> Self:
        identity = ":".join(
            (
                self.run_id,
                self.case_id,
                self.condition.value,
                str(self.replicate),
                self.model,
                self.host,
            )
        )
        digest = hashlib.sha256(self.prompt.encode()).hexdigest()
        if self.job_id and self.job_id != identity:
            raise ValueError("job identity mismatch")
        if self.prompt_sha256 and self.prompt_sha256 != digest:
            raise ValueError("job prompt digest mismatch")
        object.__setattr__(self, "job_id", identity)
        object.__setattr__(self, "prompt_sha256", digest)
        if (self.interaction_mode is InteractionMode.CONTROLLED_MULTI_TURN) != (
            self.conversation_script is not None
        ):
            raise ValueError("job conversation script mismatch")
        return self


class ConversationTurn(StrictModel):
    turn_index: StrictInt = Field(ge=1)
    role: Literal["user", "assistant"]
    content: str
    input_tokens: StrictInt | None = Field(default=None, ge=0)
    output_tokens: StrictInt | None = Field(default=None, ge=0)
    cost: StrictFloat | None = Field(default=None, ge=0, allow_inf_nan=False)
    latency_seconds: StrictFloat | None = Field(default=None, ge=0, allow_inf_nan=False)
    timestamp: datetime | None = None

    @model_validator(mode="after")
    def check_role_index(self) -> Self:
        if (self.turn_index % 2 == 1) != (self.role == "user"):
            raise ValueError("conversation roles must alternate from user at index one")
        return self


class TurnJob(StrictModel):
    job_id: str = Field(min_length=1)
    assistant_turn_index: StrictInt = Field(ge=2, multiple_of=2)
    transcript: tuple[ConversationTurn, ...] = Field(min_length=1)
    system_instructions: str = ""
    model: str = ""
    host: str = "inbox"
    model_parameters: dict[str, Any] = Field(default_factory=dict)
    attempt: StrictInt = Field(default=0, ge=0)
    turn_id: str = ""

    @model_validator(mode="after")
    def check_transcript(self) -> Self:
        if self.assistant_turn_index != len(self.transcript) + 1:
            raise ValueError("turn job index does not follow transcript")
        if self.transcript[-1].role != "user":
            raise ValueError("turn job transcript must end with user")
        if tuple(t.turn_index for t in self.transcript) != tuple(
            range(1, len(self.transcript) + 1)
        ):
            raise ValueError("turn job transcript is not contiguous")
        identity = f"{self.job_id}:{self.assistant_turn_index}:{self.attempt}"
        if self.turn_id and self.turn_id != identity:
            raise ValueError("turn identity mismatch")
        object.__setattr__(self, "turn_id", identity)
        return self

    @classmethod
    def from_state(cls, state: Any, transcript: tuple[ConversationTurn, ...]) -> TurnJob:
        return cls(
            job_id=state.job.job_id,
            assistant_turn_index=len(transcript) + 1,
            transcript=transcript,
            system_instructions=state.job.system_instructions,
            model=state.job.model,
            host=state.job.host,
            model_parameters=state.job.model_parameters,
        )


class TurnResponse(StrictModel):
    job_id: str = Field(min_length=1)
    turn_index: StrictInt = Field(ge=2, multiple_of=2)
    content: str
    status: Status = "succeeded"
    input_tokens: StrictInt | None = Field(default=None, ge=0)
    output_tokens: StrictInt | None = Field(default=None, ge=0)
    cost: StrictFloat | None = Field(default=None, ge=0, allow_inf_nan=False)
    latency_seconds: StrictFloat | None = Field(default=None, ge=0, allow_inf_nan=False)
    attempt: StrictInt = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)
    raw_response: str | None = None
    error: str | None = None
    turn_id: str = ""

    @model_validator(mode="after")
    def derive_identity(self) -> Self:
        identity = f"{self.job_id}:{self.turn_index}:{self.attempt}"
        if self.turn_id and self.turn_id != identity:
            raise ValueError("turn response identity mismatch")
        object.__setattr__(self, "turn_id", identity)
        return self


class ConversationRecord(StrictModel):
    job_id: str = Field(min_length=1)
    turns: tuple[ConversationTurn, ...]
    turn_response_ids: tuple[str, ...]
    final_response: str
    final_response_output_tokens: StrictInt | None = Field(default=None, ge=0)
    total_assistant_output_tokens: StrictInt | None = Field(default=None, ge=0)
    total_cost: StrictFloat | None = Field(default=None, ge=0, allow_inf_nan=False)
    total_latency_seconds: StrictFloat | None = Field(default=None, ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def check_conversation_evidence(self) -> Self:
        if (
            not self.turns
            or len(self.turns) % 2
            or tuple(turn.turn_index for turn in self.turns) != tuple(range(1, len(self.turns) + 1))
        ):
            raise ValueError("conversation must contain contiguous complete user/assistant pairs")
        if (
            self.final_response != self.turns[-1].content
            or self.final_response_output_tokens != self.turns[-1].output_tokens
        ):
            raise ValueError("conversation final portfolio does not match last assistant turn")
        assistant_turns = [turn for turn in self.turns if turn.role == "assistant"]
        if len(set(self.turn_response_ids)) != len(self.turn_response_ids) or len(
            self.turn_response_ids
        ) < len(assistant_turns):
            raise ValueError("conversation turn evidence references are incomplete or duplicate")
        known_tokens = [turn.output_tokens for turn in assistant_turns]
        if (
            any(value is None for value in known_tokens)
            and self.total_assistant_output_tokens is not None
        ):
            raise ValueError("conversation total cannot replace missing provider token metadata")
        if (
            self.total_assistant_output_tokens is not None
            and self.total_assistant_output_tokens
            < sum(value for value in known_tokens if value is not None)
        ):
            raise ValueError("conversation total omits assistant output tokens")
        return self


class ResponseRecord(StrictModel):
    job_id: str = Field(min_length=1)
    status: Status
    attempt: StrictInt = Field(default=0, ge=0)
    content: str = ""
    conversation: ConversationRecord | None = None
    output_tokens: StrictInt | None = Field(default=None, ge=0)
    input_tokens: StrictInt | None = Field(default=None, ge=0)
    cost: StrictFloat | None = Field(default=None, ge=0, allow_inf_nan=False)
    latency_seconds: StrictFloat | None = Field(default=None, ge=0, allow_inf_nan=False)
    error: str | None = None
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def check_conversation_identity(self) -> Self:
        if self.conversation is not None and self.conversation.job_id != self.job_id:
            raise ValueError("response conversation identity mismatch")
        return self

    @property
    def total_assistant_output_tokens(self) -> int | None:
        return (
            self.conversation.total_assistant_output_tokens
            if self.conversation
            else self.output_tokens
        )


class MechanismQuality(StrictModel):
    relevance: StrictInt = Field(ge=0, le=3)
    constraint_alignment: StrictInt = Field(ge=0, le=3)
    causal_clarity: StrictInt = Field(ge=0, le=3)
    plausibility: StrictInt = Field(ge=0, le=3)
    critical_safety_violation: StrictBool
    evidence: dict[str, str] = Field(default_factory=dict)


class Mechanism(StrictModel):
    id: str = Field(min_length=1)
    intervention_point: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    changed_flow: str = Field(min_length=1)
    causal_operation: str = Field(min_length=1)
    intended_effect: str = Field(min_length=1)
    principal_constraint: str = ""
    quality: MechanismQuality | None = None
    evidence: dict[str, str] = Field(default_factory=dict)


class ScoreRecord(StrictModel):
    job_id: str = Field(min_length=1)
    mechanisms: tuple[Mechanism, ...] = ()
    criterion_scores: dict[str, StrictFloat | StrictInt | StrictBool | None] = Field(
        default_factory=dict
    )
    evidence: dict[str, str] = Field(default_factory=dict)
    judge_id: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


class RunConfig(StrictModel):
    run_id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    models: tuple[str, ...] = Field(min_length=1)
    model_allowlist: tuple[str, ...] = Field(min_length=1)
    hosts: tuple[str, ...] = ("inbox",)
    conditions: tuple[Condition, ...] = (Condition.VANILLA, Condition.FULL_SKILL)
    replicates: StrictInt = Field(default=1, ge=1)
    split: Literal["development", "validation", "test"] = "development"
    dry_run: StrictBool = True
    max_calls: StrictInt = Field(default=50, ge=1)
    max_cost: StrictFloat = Field(default=10.0, gt=0, allow_inf_nan=False)
    max_concurrency: StrictInt = Field(default=2, ge=1)
    retry_limit: StrictInt = Field(default=1, ge=0)
    failure_threshold: StrictFloat = Field(default=0.20, ge=0, le=1)
    max_output_tokens: StrictInt = Field(default=4096, ge=1)
    model_parameters: dict[str, Any] = Field(default_factory=dict)
    cost_per_turn: dict[str, StrictFloat] = Field(default_factory=dict)
    skill_path: Path | None = None
    ablation: str | None = None
    ablation_skill_path: Path | None = None
    adapter_command: tuple[str, ...] = ()
    allowed_executables: tuple[str, ...] = ()
    environment_allowlist: tuple[str, ...] = ()
    secret_environment_keys: tuple[str, ...] = ()
    timeout_seconds: StrictFloat = Field(default=120, gt=0, allow_inf_nan=False)
    max_output_bytes: StrictInt = Field(default=1048576, ge=1)

    @model_validator(mode="after")
    def check_lists(self) -> Self:
        for values in (self.models, self.model_allowlist, self.hosts, self.conditions):
            if (
                not values
                or len(values) != len(set(values))
                or any(not str(v).strip() for v in values)
            ):
                raise ValueError("run configuration lists must be nonempty and unique")
        if any(not 0 <= cost < float("inf") for cost in self.cost_per_turn.values()):
            raise ValueError("per-turn costs must be finite and nonnegative")
        return self


class RunEstimate(StrictModel):
    parent_jobs: StrictInt
    maximum_calls: StrictInt
    maximum_cost: StrictFloat | None
    maximum_output_tokens: StrictInt


class RunManifest(StrictModel):
    run_id: str
    benchmark_version: str = "0.1.0"
    runner_version: str = "0.1.0"
    skill_version: str = "2.0.0"
    git_revision: str
    runner_source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    runner_worktree_dirty: StrictBool
    skill_revision: str
    config: RunConfig
    cases: tuple[BenchmarkCase, ...]
    artifact_digests: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
