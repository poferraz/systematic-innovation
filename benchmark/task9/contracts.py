"""Strict, immutable contracts at the Task 9 external-worker boundary."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, model_validator

CASE_IDS = ("adv-dev-001", "pre-dev-001", "red-dev-001", "syn-dev-001", "sys-dev-001",
            "tri-dev-001")
CONDITIONS = ("vanilla", "generic-brainstorm", "format-matched", "established-method",
              "full-skill")
MODEL = "gpt-5.4-mini-2026-03-17"
FROZEN_SKILL_MD = "d5971f6e3e646916e2a287c5a8fde96a93b811ed071c362526c605ef222a890b"
PARAMETERS = {
    "reasoning": {"effort": "none"}, "text": {"verbosity": "medium"},
    "service_tier": "default", "store": False, "tools": [], "tool_choice": "none",
    "truncation": "disabled", "max_output_tokens": 4096,
}
Sha256 = Annotated[str, Field(strict=True, pattern=r"^[a-f0-9]{64}$")]
LogicalId = Annotated[str, Field(strict=True, min_length=1, max_length=200,
                                 pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)


class Task9Policy(Contract):
    max_calls: StrictInt = 70
    max_cost_micro_usd: StrictInt = 5000000
    stop_micro_usd: StrictInt = 4500000
    reserve_micro_usd: StrictInt = 50000
    max_concurrency: StrictInt = 1
    retry_limit: StrictInt = 0
    max_input_tokens: StrictInt = 32768
    max_output_tokens: StrictInt = 4096
    timeout_seconds: StrictInt = 120
    max_response_bytes: StrictInt = 1048576
    wall_seconds: StrictInt = 10800

    @model_validator(mode="after")
    def fixed_envelope(self) -> Self:
        expected = (70, 5000000, 4500000, 50000, 1, 0, 32768, 4096, 120, 1048576, 10800)
        if tuple(self.model_dump().values()) != expected:
            raise ValueError("TASK9_POLICY_MISMATCH")
        return self


class InputBound(Contract):
    tokens: StrictInt = Field(ge=0)
    profile_sha256: Sha256
    request_sha256: Sha256
    certified_for_live: StrictBool = False


class ExecutionApproval(Contract):
    approved: StrictBool
    mode: Literal["offline", "live"]
    run_id: LogicalId
    account_id: LogicalId
    project_id: LogicalId
    expires_at: datetime
    budget_override_approved: StrictBool
    live_execution_authorized: StrictBool = False
    bindings: dict[str, Sha256]
    input_profile_sha256: Sha256
    policy: Task9Policy = Field(default_factory=Task9Policy)

    @model_validator(mode="after")
    def aware_expiration(self) -> Self:
        if self.expires_at.tzinfo is None or self.expires_at.utcoffset() is None:
            raise ValueError("TASK9_APPROVAL_TIME_INVALID")
        return self


class AttemptReceipt(Contract):
    seq: StrictInt = Field(ge=1)
    event: Literal["reserved", "dispatched", "completed", "error"]
    turn_id: str = Field(strict=True, pattern=r"^[a-f0-9]{64}:[246]:0$")
    request_sha256: Sha256
    reserved_micro_usd: StrictInt = Field(ge=0)
    charged_micro_usd: StrictInt | None = Field(default=None, ge=0)
    response_path: str | None = None
    response_sha256: Sha256 | None = None
    error: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    timestamp: datetime
    previous_sha256: Sha256
    sha256: Sha256
