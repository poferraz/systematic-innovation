"""Durable, fail-closed authorization and spending guards for one opaque turn.

Only ``process`` can cross the injected send boundary. It holds a nonblocking
process lock, consumes a durable exclusive claim and fsyncs two journal events
before invoking the callback. An uncertain result is never sent again.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import subprocess
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from decimal import ROUND_CEILING, Decimal
from pathlib import Path
from typing import Any

import yaml

from systematic_innovation_bench.models import TurnJob, TurnResponse
from systematic_innovation_bench.planner import plan_jobs
from systematic_innovation_bench.runtime import (
    REPOSITORY_ROOT,
    Dispatch,
    RunDirectory,
    canonical_digest,
    current_source_digest,
    digest,
    public_cases,
)
from systematic_innovation_bench.store import read_records

from .contracts import (
    CASE_IDS,
    CONDITIONS,
    FROZEN_SKILL_MD,
    MODEL,
    PARAMETERS,
    AttemptReceipt,
    ExecutionApproval,
    InputBound,
)

PLAN_PATH = REPOSITORY_ROOT / (
    "docs/superpowers/plans/2026-11-14-study-task9-six-case-feasibility.md"
)
STAGE_PATH = REPOSITORY_ROOT / "benchmark/study/stage-gates.yaml"
READINESS_PATH = REPOSITORY_ROOT / "benchmark/study/task9-readiness-approval.yaml"
SKILL_PATH = REPOSITORY_ROOT / "skills/systematic-innovation"
CORPUS_PATH = REPOSITORY_ROOT / "benchmark/cases/development"
ZERO_SHA = "0" * 64


class Task9Error(ValueError):
    """Public exceptions contain a constant rule identifier only."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _tree_digest(root: Path, pattern: str) -> str:
    if root.is_symlink():
        raise Task9Error("TASK9_SOURCE_UNSAFE")
    paths = sorted(root.rglob(pattern))
    if any(p.is_symlink() for p in paths):
        raise Task9Error("TASK9_SOURCE_UNSAFE")
    return canonical_digest({p.relative_to(root).as_posix(): digest(p)
                             for p in paths if p.is_file()})


def skill_tree_digest() -> str:
    return _tree_digest(SKILL_PATH, "*")


def approval_bindings(run: RunDirectory) -> dict[str, str]:
    """Collect actual fixed-path identities for an independently supplied approval.

    This read-only function creates no approval and changes no stage flag.
    Paths and observed digests are deliberately not caller parameters.
    """
    cases = public_cases(CORPUS_PATH, CASE_IDS)
    return {
        "plan": digest(PLAN_PATH),
        "config": canonical_digest(run.manifest.config.model_dump(mode="json")),
        "runner_source": current_source_digest(),
        "worker_source": _tree_digest(Path(__file__).parent, "*.py"),
        "dependency_lock": digest(REPOSITORY_ROOT / "benchmark/uv.lock"),
        "public_corpus": canonical_digest([c.model_dump(mode="json") for c in cases]),
        "public_corpus_files": _tree_digest(CORPUS_PATH, "*.yaml"),
        "skill_tree": skill_tree_digest(),
        "skill_md": digest(SKILL_PATH / "SKILL.md"),
        "stage_contract": digest(STAGE_PATH),
        "readiness_approval": digest(READINESS_PATH),
        "manifest": digest(run.inside("manifest.json")),
    }


def validate_approval(
    run: RunDirectory,
    approval: ExecutionApproval,
    *,
    transport_live: bool,
    transport_account_id: str,
    transport_project_id: str,
    input_bound: InputBound | None = None,
) -> None:
    """Validate separate owner approval against actual source and transport mode."""
    try:
        checked = ExecutionApproval.model_validate(approval.model_dump())
        if (not checked.approved or not checked.budget_override_approved
                or checked.run_id != run.manifest.run_id
                or checked.expires_at <= datetime.now(UTC)
                or type(transport_live) is not bool
                or (checked.mode == "live") != transport_live
                or checked.account_id != transport_account_id
                or checked.project_id != transport_project_id):
            raise Task9Error("TASK9_APPROVAL_MISMATCH")
        if checked.bindings != approval_bindings(run):
            raise Task9Error("TASK9_FREEZE_MISMATCH")
        if checked.bindings["skill_md"] != FROZEN_SKILL_MD:
            raise Task9Error("TASK9_SKILL_FROZEN")
        decision = yaml.safe_load(READINESS_PATH.read_text(encoding="utf-8"))
        expected_budget = {
            "currency": "USD", "max_calls": 70, "max_cost": 5.0,
            "per_turn_reservation": 0.05, "stop_at_cost": 4.5, "retry_limit": 0,
            "max_concurrency": 1, "max_input_tokens": 32768, "max_output_tokens": 4096,
            "request_timeout_seconds": 120.0, "max_output_bytes": 1048576,
            "max_wall_seconds": 10800,
        }
        budget = decision.get("budget")
        if (decision.get("stage") != "six_case_feasibility"
                or decision.get("budget_approved") is not True
                or decision.get("implementation_authorized") is not True
                or decision.get("offline_tests_authorized") is not True
                or decision.get("canonical_skill_frozen") is not True
                or decision.get("scientific_stage_status") != "pending"
                or not isinstance(budget, dict) or budget != expected_budget
                or any(type(budget[key]) is not type(value)
                       for key, value in expected_budget.items())):
            raise Task9Error("TASK9_OWNER_DECISION_REQUIRED")
        if input_bound is not None:
            InputBound.model_validate(input_bound.model_dump())
            if (input_bound.profile_sha256 != checked.input_profile_sha256
                    or input_bound.tokens > checked.policy.max_input_tokens):
                raise Task9Error("TASK9_INPUT_BOUND")
        if transport_live:
            stage = yaml.safe_load(STAGE_PATH.read_text(encoding="utf-8"))
            if (not checked.live_execution_authorized
                    or decision.get("live_execution_authorized") is not True
                    or stage.get("execution_authorized") is not True
                    or stage.get("six_case_feasibility", {}).get("status") != "pending"
                    or input_bound is None or not input_bound.certified_for_live
                    or run.manifest.config.dry_run
                    or run.manifest.runner_worktree_dirty):
                raise Task9Error("TASK9_LIVE_NOT_AUTHORIZED")
            state = subprocess.run(
                ["git", "-C", str(REPOSITORY_ROOT), "status", "--porcelain=v1"],
                capture_output=True, text=True, check=True,
            )
            revision = subprocess.run(
                ["git", "-C", str(REPOSITORY_ROOT), "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True,
            )
            if state.stdout or revision.stdout.strip() != run.manifest.git_revision:
                raise Task9Error("TASK9_REVIEWED_CHECKOUT_REQUIRED")
    except Task9Error:
        raise
    except Exception as exc:  # noqa: BLE001 - redact every boundary exception
        del exc  # Never expose exception text or provider-controlled details.
        raise Task9Error("TASK9_APPROVAL_INVALID") from None


def _safe_path(root: Path, name: str) -> Path:
    candidate = root / name
    resolved = candidate.resolve()
    if resolved == root.resolve() or not resolved.is_relative_to(root.resolve()):
        raise Task9Error("TASK9_LEDGER_PATH")
    for path in (candidate, *candidate.parents):
        if path.is_symlink():
            raise Task9Error("TASK9_LEDGER_PATH")
        if path == root:
            break
    return resolved


def _claim_name(turn_id: str) -> str:
    return "claims/" + hashlib.sha256(turn_id.encode()).hexdigest() + ".json"


def _response_name(turn_id: str) -> str:
    return "responses/" + hashlib.sha256(turn_id.encode()).hexdigest() + ".json"


def read_receipts(ledger_root: Path) -> list[AttemptReceipt]:
    """Verify chain, state transitions, exclusive claims and response pointers."""
    try:
        if ledger_root.is_symlink():
            raise Task9Error("TASK9_LEDGER_PATH")
        journal = _safe_path(ledger_root, "attempts.jsonl")
        payload = journal.read_bytes() if journal.exists() else b""
        if payload and not payload.endswith(b"\n"):
            raise Task9Error("TASK9_LEDGER_INTEGRITY")
        records = [AttemptReceipt.model_validate_json(line) for line in payload.splitlines()]
        states: dict[str, str] = {}
        requests: dict[str, str] = {}
        previous = ZERO_SHA
        for seq, record in enumerate(records, 1):
            if (record.seq != seq or record.previous_sha256 != previous
                    or record.sha256 != canonical_digest(record.model_dump(
                        mode="json", exclude={"sha256"}))
                    or record.reserved_micro_usd != 50000
                    or record.timestamp.tzinfo is None):
                raise Task9Error("TASK9_LEDGER_INTEGRITY")
            prior = states.get(record.turn_id)
            valid = ((record.event == "reserved" and prior is None)
                     or (record.event == "dispatched" and prior == "reserved")
                     or (record.event in {"completed", "error"} and prior == "dispatched"))
            if (not valid or (record.turn_id in requests
                              and requests[record.turn_id] != record.request_sha256)):
                raise Task9Error("TASK9_LEDGER_INTEGRITY")
            if record.event == "completed" and (
                record.charged_micro_usd is None or record.response_path is None
                or record.response_sha256 is None or record.error is not None
            ):
                raise Task9Error("TASK9_LEDGER_INTEGRITY")
            if (record.response_path is None) != (record.response_sha256 is None):
                raise Task9Error("TASK9_LEDGER_INTEGRITY")
            if record.response_path is not None:
                if record.response_path != _response_name(record.turn_id):
                    raise Task9Error("TASK9_LEDGER_INTEGRITY")
                path = _safe_path(ledger_root, record.response_path)
                if digest(path) != record.response_sha256:
                    raise Task9Error("TASK9_LEDGER_INTEGRITY")
                response = TurnResponse.model_validate_json(path.read_bytes())
                if response.turn_id != record.turn_id:
                    raise Task9Error("TASK9_LEDGER_INTEGRITY")
            states[record.turn_id] = record.event
            requests[record.turn_id] = record.request_sha256
            previous = record.sha256
        claims_root = _safe_path(ledger_root, "claims")
        actual_claims = set(claims_root.glob("*.json")) if claims_root.exists() else set()
        expected_claims = {_safe_path(ledger_root, _claim_name(turn_id)) for turn_id in states}
        if actual_claims != expected_claims:
            raise Task9Error("TASK9_LEDGER_INTEGRITY")
        for turn_id, request_hash in requests.items():
            claim = json.loads(_safe_path(ledger_root, _claim_name(turn_id)).read_bytes())
            if claim != {"turn_id": turn_id, "request_sha256": request_hash}:
                raise Task9Error("TASK9_LEDGER_INTEGRITY")
        return records
    except Task9Error:
        raise
    except Exception as exc:  # noqa: BLE001 - redact malformed evidence details
        del exc  # Evidence errors are code-only at the external boundary.
        raise Task9Error("TASK9_LEDGER_INTEGRITY") from None


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _exclusive_file(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    _fsync_directory(path.parent)


def check_envelope(attempts: int, accounted_micro_usd: int, next_reserve_micro_usd: int) -> None:
    """Check integer accounting before an additional generation attempt."""
    if (any(type(value) is not int or value < 0
            for value in (attempts, accounted_micro_usd, next_reserve_micro_usd))
            or next_reserve_micro_usd != 50000):
        raise Task9Error("TASK9_BUDGET_INVALID")
    if attempts >= 70:
        raise Task9Error("TASK9_CALL_LIMIT")
    if accounted_micro_usd >= 4500000:
        raise Task9Error("TASK9_OPERATIONAL_STOP")
    if accounted_micro_usd + next_reserve_micro_usd > 5000000:
        raise Task9Error("TASK9_COST_LIMIT")
    if accounted_micro_usd + next_reserve_micro_usd >= 4500000:
        raise Task9Error("TASK9_OPERATIONAL_STOP")


class Task9Guard:
    def __init__(self, run: RunDirectory, approval: ExecutionApproval, *,
                 ledger_root: Path | None = None, transport_account_id: str,
                 transport_project_id: str):
        self.run = run
        self.approval = approval
        self.transport_account_id = transport_account_id
        self.transport_project_id = transport_project_id
        try:
            expected = run.inside("worker")
            selected = expected if ledger_root is None else run.inside(ledger_root)
            if selected != expected:
                raise Task9Error("TASK9_LEDGER_PATH")
            self.ledger_root = selected
        except Task9Error:
            raise
        except Exception as exc:  # noqa: BLE001 - paths may contain protected data
            del exc
            raise Task9Error("TASK9_LEDGER_PATH") from None

    @contextmanager
    def _lock(self) -> Iterator[None]:
        self.ledger_root.mkdir(parents=True, exist_ok=True)
        path = _safe_path(self.ledger_root, ".worker.lock")
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "a") as stream:
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Task9Error("TASK9_CONCURRENCY") from None
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)

    def records(self) -> list[AttemptReceipt]:
        return read_receipts(self.ledger_root)

    def verify(self) -> dict[str, int | bool]:
        records = self.records()
        final = {r.turn_id: r for r in records}
        return {
            "attempts": sum(r.event == "dispatched" for r in records),
            "completed": sum(r.event == "completed" for r in records),
            "reserved_micro_usd": sum(r.reserved_micro_usd for r in final.values()),
            "charged_micro_usd": sum(r.charged_micro_usd or 0 for r in final.values()),
            "unresolved": sum(r.event in {"reserved", "dispatched"} for r in final.values()),
            "stopped": any(r.event in {"error", "reserved", "dispatched"}
                           for r in final.values()),
        }

    def _append(self, records: list[AttemptReceipt], **values: Any) -> AttemptReceipt:
        data = {
            "seq": len(records) + 1, "timestamp": datetime.now(UTC),
            "previous_sha256": records[-1].sha256 if records else ZERO_SHA,
            "charged_micro_usd": None, "response_path": None, "response_sha256": None,
            "error": None, **values,
        }
        # Round trip before hashing so datetime serialization is canonical.
        record = AttemptReceipt(**data, sha256=ZERO_SHA)
        record = record.model_copy(update={"sha256": canonical_digest(record.model_dump(
            mode="json", exclude={"sha256"}))})
        path = _safe_path(self.ledger_root, "attempts.jsonl")
        descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "ab") as stream:
            stream.write(record.model_dump_json().encode() + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        _fsync_directory(path.parent)
        records.append(record)
        return record

    def _scope(self) -> list[Dispatch]:
        self.run.require_current_source()
        self.run.verify()
        config, manifest, jobs = self.run.manifest.config, self.run.manifest, self.run.jobs
        if (config.models != (MODEL,) or config.model_allowlist != (MODEL,)
                or config.hosts != ("inbox",) or tuple(config.conditions) != CONDITIONS
                or config.replicates != 1 or config.split != "development"
                or config.max_calls != 70 or config.max_cost != 5.0
                or config.max_concurrency != 1 or config.retry_limit != 0
                or config.failure_threshold != 0.0 or config.max_output_tokens != 4096
                or config.timeout_seconds != 120.0 or config.max_output_bytes != 1048576
                or config.cost_per_turn != {MODEL: 0.05}
                or canonical_digest(config.model_parameters) != canonical_digest(
                    {k: v for k, v in PARAMETERS.items() if k != "max_output_tokens"})
                or config.skill_path is not None or config.ablation is not None
                or config.ablation_skill_path is not None or config.adapter_command
                or config.allowed_executables or config.environment_allowlist
                or config.secret_environment_keys != ("OPENAI_API_KEY",)
                or tuple(c.id for c in manifest.cases) != CASE_IDS or len(jobs) != 30
                or manifest.skill_revision != skill_tree_digest()
                or manifest.artifact_digests.get("dependency_lock")
                != digest(REPOSITORY_ROOT / "benchmark/uv.lock")):
            raise Task9Error("TASK9_SCOPE_MISMATCH")
        actual_cases = public_cases(CORPUS_PATH, CASE_IDS)
        if tuple(actual_cases) != manifest.cases:
            raise Task9Error("TASK9_CORPUS_MISMATCH")
        expected_jobs = plan_jobs(actual_cases, config, jobs[0].created_at)
        if [j.model_dump(exclude={"created_at"}) for j in jobs] != [
            j.model_dump(exclude={"created_at"}) for j in expected_jobs
        ]:
            raise Task9Error("TASK9_JOB_MISMATCH")
        return read_records(self.run.inside("records/dispatches.jsonl"), Dispatch)

    def _reconcile(self, records: list[AttemptReceipt], dispatches: list[Dispatch]) -> None:
        final = {record.turn_id: record for record in records}
        opaque_dispatches = set()
        for dispatch in dispatches:
            job_id, index, attempt = dispatch.turn_id.rsplit(":", 2)
            opaque_dispatches.add(f"{hashlib.sha256(job_id.encode()).hexdigest()}:{index}:{attempt}")
        if not set(final).issubset(opaque_dispatches):
            raise Task9Error("TASK9_LEDGER_CORRELATION")
        for accepted in self.run.turns:
            opaque = TurnResponse.model_validate(accepted.model_dump() | {
                "job_id": hashlib.sha256(accepted.job_id.encode()).hexdigest(), "turn_id": "",
            })
            receipt = final.get(opaque.turn_id)
            if receipt is None or receipt.event != "completed" or receipt.response_path is None:
                raise Task9Error("TASK9_LEDGER_CORRELATION")
            cached = TurnResponse.model_validate_json(
                _safe_path(self.ledger_root, receipt.response_path).read_bytes())
            if opaque.model_dump(exclude={"created_at"}) != cached.model_dump(
                exclude={"created_at"}
            ):
                raise Task9Error("TASK9_LEDGER_CORRELATION")

    @staticmethod
    def _validate_response(job: TurnJob, result: TurnResponse, bound: InputBound) -> int:
        # Charge quarter-microdollars outward to whole microdollars.
        if (result.turn_id != job.turn_id or result.attempt != 0
                or result.status not in {"succeeded", "refused"}
                or (not result.content.strip() and result.status != "refused")
                or result.input_tokens is None or result.output_tokens is None
                or result.input_tokens > 32768 or result.input_tokens > bound.tokens
                or result.output_tokens > 4096 or result.cost is None
                or result.raw_response is None
                or len(result.raw_response.encode()) > 1048576
                or result.latency_seconds is None or result.latency_seconds > 120):
            raise Task9Error("TASK9_RESPONSE_INVALID")
        envelope = json.loads(result.raw_response)
        if (not isinstance(envelope, dict) or set(envelope) != {
            "provider_response", "request_id", "http_status", "cost_provenance"
        } or type(envelope.get("http_status")) is not int or envelope["http_status"] != 200
                or not isinstance(envelope.get("request_id"), str)
                or not envelope["request_id"].strip()
                or envelope.get("cost_provenance") != {
                    "kind": "calculated-token-rate-upper-bound", "currency": "USD",
                    "input_rate_usd_per_million": "0.75", "output_rate_usd_per_million": "4.50",
                    "basis": "provider-total-tokens; uncached input rate; reasoning not added again",
                }):
            raise Task9Error("TASK9_PROVIDER_METADATA")
        provider = envelope.get("provider_response")
        if not isinstance(provider, dict):
            raise Task9Error("TASK9_PROVIDER_METADATA")
        usage = provider.get("usage")
        outputs = provider.get("output", [])
        if (provider.get("model") != MODEL or provider.get("service_tier") != "default"
                or provider.get("status") != "completed"
                or provider.get("error") is not None or provider.get("incomplete_details") is not None
                or not isinstance(provider.get("id"), str) or not provider["id"].strip()
                or not isinstance(usage, dict)
                or type(usage.get("input_tokens")) is not int
                or type(usage.get("output_tokens")) is not int
                or usage["input_tokens"] != result.input_tokens
                or usage["output_tokens"] != result.output_tokens
                or not isinstance(outputs, list)
                or any(not isinstance(item, dict) or item.get("type") not in {"message", "reasoning"}
                       for item in outputs)):
            raise Task9Error("TASK9_PROVIDER_METADATA")
        exact = Decimal(result.input_tokens) * Decimal("0.75") + (
            Decimal(result.output_tokens) * Decimal("4.50"))
        if abs(Decimal(str(result.cost)) * 1000000 - exact) > Decimal("0.000001"):
            raise Task9Error("TASK9_COST_METADATA")
        micro = int(exact.to_integral_value(rounding=ROUND_CEILING))
        if micro > 50000:
            raise Task9Error("TASK9_TURN_COST_LIMIT")
        return micro

    def process(self, turn_job: TurnJob, payload: dict[str, Any], input_bound: InputBound,
                send: Callable[[], TurnResponse], *, transport_live: bool) -> TurnResponse:
        """Send once, or recover byte-identical completed evidence without sending."""
        try:
            with self._lock():
                validate_approval(
                    self.run, self.approval, transport_live=transport_live,
                    transport_account_id=self.transport_account_id,
                    transport_project_id=self.transport_project_id, input_bound=input_bound,
                )
                json.dumps(payload, allow_nan=False)
                expected_payload = {
                    "model": turn_job.model, "instructions": turn_job.system_instructions,
                    "input": [{"role": t.role, "content": t.content}
                              for t in turn_job.transcript], **PARAMETERS,
                }
                request_hash = canonical_digest(payload)
                if (request_hash != canonical_digest(expected_payload)
                        or input_bound.request_sha256 != request_hash):
                    raise Task9Error("TASK9_REQUEST_MISMATCH")
                records = self.records()
                same = [r for r in records if r.turn_id == turn_job.turn_id]
                if same and same[0].request_sha256 != request_hash:
                    raise Task9Error("TASK9_REPLAY_MISMATCH")
                final = {r.turn_id: r for r in records}
                if any(r.event != "completed" for r in final.values()):
                    raise Task9Error("TASK9_RUN_STOPPED")
                dispatches = self._scope()
                self._reconcile(records, dispatches)
                if same:
                    path = _safe_path(self.ledger_root, same[-1].response_path or "invalid")
                    return TurnResponse.model_validate_json(path.read_bytes())
                pending = {self.run.opaque(j).turn_id: j for j in self.run.pending()}
                canonical = pending.get(turn_job.turn_id)
                if canonical is None or self.run.opaque(canonical) != turn_job:
                    raise Task9Error("TASK9_PENDING_MISMATCH")
                core_dispatches = {d.turn_id: d for d in dispatches}
                if canonical.turn_id not in core_dispatches or turn_job.attempt != 0:
                    raise Task9Error("TASK9_RESERVATION_REQUIRED")
                core_responses = {r.turn_id: r for r in self.run.turns}
                unresolved = {d.turn_id for d in dispatches if d.turn_id not in core_responses}
                if unresolved != {canonical.turn_id}:
                    raise Task9Error("TASK9_CONCURRENCY")
                accounted = 0
                for dispatch in dispatches:
                    if dispatch.turn_id == canonical.turn_id:
                        continue
                    observed = core_responses.get(dispatch.turn_id)
                    observed_micro = int((Decimal(str(observed.cost or 0)) * 1000000)
                                         .to_integral_value(rounding=ROUND_CEILING)) if observed else 0
                    accounted += max(50000, observed_micro)
                check_envelope(sum(r.event == "dispatched" for r in records), accounted, 50000)
                if records and (datetime.now(UTC) - records[0].timestamp).total_seconds() >= 10800:
                    raise Task9Error("TASK9_WALL_LIMIT")
                _exclusive_file(_safe_path(self.ledger_root, _claim_name(turn_job.turn_id)),
                                json.dumps({"turn_id": turn_job.turn_id,
                                            "request_sha256": request_hash},
                                           sort_keys=True).encode() + b"\n")
                base = {"turn_id": turn_job.turn_id, "request_sha256": request_hash,
                        "reserved_micro_usd": 50000}
                self._append(records, event="reserved", **base)
                self._append(records, event="dispatched", **base)
                response_pointer: dict[str, str] = {}
                try:
                    result = send()
                    result = TurnResponse.model_validate(result.model_dump())
                    if result.turn_id == turn_job.turn_id:
                        response_name = _response_name(turn_job.turn_id)
                        response_path = _safe_path(self.ledger_root, response_name)
                        _exclusive_file(response_path, result.model_dump_json().encode() + b"\n")
                        response_pointer = {"response_path": response_name,
                                            "response_sha256": digest(response_path)}
                    charged = self._validate_response(turn_job, result, input_bound)
                    self._append(records, event="completed", charged_micro_usd=charged,
                                 **response_pointer, **base)
                    return result
                except Exception as exc:  # noqa: BLE001 - provider exceptions may contain secrets
                    del exc  # A callback may raise a credential-bearing exception.
                    self._append(records, event="error", error="TASK9_ATTEMPT_UNRESOLVED",
                                 **response_pointer, **base)
                    raise Task9Error("TASK9_ATTEMPT_UNRESOLVED") from None
        except Task9Error:
            raise
        except Exception as exc:  # noqa: BLE001 - external boundary is code-only
            del exc
            raise Task9Error("TASK9_GUARD_REJECTED") from None
