"""Read-only launch review packet; it never authorizes or contacts a provider."""
from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import yaml

from systematic_innovation_bench.conversation import next_turn_job, start_conversation
from systematic_innovation_bench.models import RunConfig
from systematic_innovation_bench.planner import estimate_run, plan_jobs
from systematic_innovation_bench.redaction import redact_model
from systematic_innovation_bench.runtime import (
    REPOSITORY_ROOT,
    canonical_digest,
    current_source_digest,
    digest,
    public_cases,
)

from .contracts import CASE_IDS, CONDITIONS, FROZEN_SKILL_MD, MODEL, PARAMETERS, Contract, Sha256

PROPOSAL = REPOSITORY_ROOT / "benchmark/configs/feasibility-six.proposed.yaml"
GUIDE = "https://developers.openai.com/api/docs/guides/token-counting"
REFERENCE = ("https://developers.openai.com/api/reference/resources/responses/"
             "subresources/input_tokens/methods/count")
BILLING = "https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens"


class PreflightError(ValueError):
    """Only constant codes cross the preflight boundary."""


class LaunchScope(Contract):
    parent_jobs: Literal[30] = 30
    generation_requests: Literal[70] = 70
    count_requests_proposed: Literal[70] = 70
    total_http_requests_proposed: Literal[140] = 140
    initial_count_payloads_prepared: Literal[30] = 30
    usage_cap_usd: Literal["5.00"] = "5.00"
    operational_stop_usd: Literal["4.50"] = "4.50"
    per_generation_reservation_usd: Literal["0.05"] = "0.05"
    calculated_generation_price_bound_usd: Literal["3.010560"] = "3.010560"
    count_price_usd: Literal["0.00"] = "0.00"
    maximum_input_tokens: Literal[32768] = 32768
    maximum_output_tokens: Literal[4096] = 4096
    retries: Literal[0] = 0
    concurrency: Literal[1] = 1
    wall_seconds: Literal[10800] = 10800
    request_timeout_envelope_seconds: Literal[9100] = 9100  # 70 * (120 + 10).


class AccountingReview(Contract):
    method: Literal["provider-exact-input-count"] = "provider-exact-input-count"
    endpoint: Literal["/v1/responses/input_tokens"] = "/v1/responses/input_tokens"
    framing_included_by_documented_contract: Literal[True] = True
    local_framing_certified: Literal[False] = False
    observed_count_requests: Literal[0] = 0
    count_timeout_seconds: Literal[10] = 10
    count_response_limit_bytes: Literal[4096] = 4096
    request_bound_receipts_required: Literal[True] = True
    count_usage_equality_required: Literal[True] = True
    count_endpoint_account_access_verified: Literal[False] = False
    count_zero_retention_claimed: Literal[False] = False
    profile_sha256: Sha256
    initial_projection_sha256: Sha256
    documentation: tuple[str, ...] = (GUIDE, REFERENCE, BILLING)


class OperatorRequirements(Contract):
    account_id: None = None
    project_id: None = None
    model_access_evidence: None = None
    provider_policy_review: None = None
    external_spend_enforcement: None = None
    os_filesystem_enforcement: None = None
    os_egress_enforcement: None = None
    reviewed_clean_revision: None = None
    executable_config_digest: None = None
    execution_approval_digest: None = None
    count_traffic_approval: None = None


class LaunchPreflight(Contract):
    schema_version: Literal["task9-launch-preflight-v1"] = "task9-launch-preflight-v1"
    stage: Literal["six_case_feasibility"] = "six_case_feasibility"
    decision: Literal["blocked-awaiting-operator-review"] = "blocked-awaiting-operator-review"
    launch_ready: Literal[False] = False
    live_execution_authorized: Literal[False] = False
    generation_calls_made: Literal[0] = 0
    provider_requests_made: Literal[0] = 0
    scientific_gate_passed: Literal[False] = False
    prepared_at: datetime
    scope: LaunchScope = LaunchScope()
    accounting: AccountingReview
    operator: OperatorRequirements = OperatorRequirements()
    source_digests: dict[str, Sha256]
    actual_git_revision: str
    actual_worktree_dirty: bool
    blockers: tuple[str, ...]


def _proposal(path: Path) -> RunConfig:
    try:
        config = RunConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        if (not config.dry_run or config.split != "development"
                or config.models != (MODEL,) or config.model_allowlist != (MODEL,)
                or config.hosts != ("inbox",) or tuple(c.value for c in config.conditions) != CONDITIONS
                or config.replicates != 1 or config.max_calls != 70 or config.max_cost != 5.0
                or config.retry_limit != 0 or config.max_concurrency != 1
                or config.failure_threshold != 0 or config.cost_per_turn != {MODEL: 0.05}
                or config.timeout_seconds != 120 or config.max_output_bytes != 1048576
                or config.max_output_tokens != 4096
                or set(config.model_parameters) != set(PARAMETERS) - {"max_output_tokens"}
                or canonical_digest(config.model_parameters | {"max_output_tokens": 4096})
                != canonical_digest(PARAMETERS)
                or config.skill_path is not None or config.ablation is not None
                or config.ablation_skill_path is not None or config.adapter_command
                or config.allowed_executables or config.environment_allowlist
                or config.secret_environment_keys != ("OPENAI_API_KEY",)
                or redact_model(config) != config):
            raise ValueError("scope")
        return config
    except (ValueError, OSError, TypeError, yaml.YAMLError):
        raise PreflightError("TASK9_PREFLIGHT_CONFIG_INVALID") from None


def build_launch_preflight(*, config_path: Path = PROPOSAL) -> LaunchPreflight:
    """Prepare metadata only; operator evidence intentionally remains unfilled."""
    from .counting import build_count_payload, counting_profile
    from .guards import skill_tree_digest
    from .worker import build_payload

    config = _proposal(config_path)
    try:
        cases = public_cases(REPOSITORY_ROOT / "benchmark/cases/development", CASE_IDS)
        jobs = plan_jobs(cases, config, datetime.now(UTC))
        estimate = estimate_run(jobs, config)
        if len(jobs) != 30 or estimate.maximum_calls != 70:
            raise ValueError("scope")
        initial = []
        by_id = {case.id: case for case in cases}
        for job in jobs:
            turn = next_turn_job(start_conversation(job, by_id[job.case_id]))
            if turn is None:
                raise ValueError("scope")
            initial.append(canonical_digest(build_count_payload(build_payload(turn))))
        skill_entry = digest(REPOSITORY_ROOT / "skills/systematic-innovation/SKILL.md")
        if skill_entry != FROZEN_SKILL_MD:
            raise ValueError("skill")
        worker = Path(__file__).parent
        sources = sorted(worker.glob("*.py"))
        if any(path.is_symlink() for path in sources):
            raise ValueError("source")
        stage_path = REPOSITORY_ROOT / "benchmark/study/stage-gates.yaml"
        decision_path = REPOSITORY_ROOT / "benchmark/study/task9-readiness-approval.yaml"
        stages = yaml.safe_load(stage_path.read_text())
        decision = yaml.safe_load(decision_path.read_text())
        blockers = [
            "OWNER_LIVE_AUTHORIZATION_MISSING", "COUNT_TRAFFIC_APPROVAL_MISSING",
            "ACCOUNT_PROJECT_UNSELECTED", "MODEL_ACCESS_UNVERIFIED", "COUNT_ENDPOINT_ACCESS_UNVERIFIED",
            "PROVIDER_POLICY_REVIEW_PENDING", "EXTERNAL_SPEND_ENFORCEMENT_UNVERIFIED",
            "OS_FILESYSTEM_SCOPE_UNVERIFIED", "OS_EGRESS_ENFORCEMENT_UNVERIFIED",
            "CLEAN_REVIEWED_REVISION_REQUIRED", "EXECUTABLE_CONFIG_NOT_FROZEN",
            "EXECUTION_APPROVAL_NOT_BOUND",
        ]
        if stages.get("execution_authorized") is not False or decision.get(
            "live_execution_authorized"
        ) is not False:
            blockers.append("EXPECTED_PAUSE_FLAGS_CHANGED")
        revision = subprocess.run(["git", "-C", str(REPOSITORY_ROOT), "rev-parse", "HEAD"],
                                  capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(REPOSITORY_ROOT), "status", "--porcelain=v1"],
                               capture_output=True, text=True, check=True).stdout
        return LaunchPreflight(
            prepared_at=datetime.now(UTC),
            accounting=AccountingReview(profile_sha256=canonical_digest(counting_profile()),
                                        initial_projection_sha256=canonical_digest(initial)),
            source_digests={
                "config": digest(config_path), "runner": current_source_digest(),
                "worker": canonical_digest({p.name: digest(p) for p in sources}),
                "lock": digest(REPOSITORY_ROOT / "benchmark/uv.lock"),
                "corpus": canonical_digest([case.model_dump(mode="json") for case in cases]),
                "skill_tree": skill_tree_digest(), "skill_entry": skill_entry,
                "stage_contract": digest(stage_path), "readiness_decision": digest(decision_path),
            }, actual_git_revision=revision, actual_worktree_dirty=bool(dirty),
            blockers=tuple(blockers),
        )
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        raise PreflightError("TASK9_PREFLIGHT_EVIDENCE_INVALID") from None
