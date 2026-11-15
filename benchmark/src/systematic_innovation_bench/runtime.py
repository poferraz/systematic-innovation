"""Bounded execution and immutable input provenance for the command interface."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import subprocess
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

from .adapters.inbox import export_turn_jobs, ingest_turn_responses
from .cases import load_cases
from .conversation import accept_turn, complete_conversation, next_turn_job, resume_conversation
from .models import (
    BenchmarkCase,
    Job,
    ResponseRecord,
    RunConfig,
    RunManifest,
    ScoreRecord,
    StrictModel,
    TurnJob,
    TurnResponse,
)
from .planner import plan_jobs, select_cases
from .redaction import redact_model
from .store import append_record, read_records, turn_responses_for_job

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class Snapshot(StrictModel):
    digests: dict[str, str]
    sizes: dict[str, int] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Dispatch(StrictModel):
    turn_id: str
    model: str
    reserved_cost: float = Field(ge=0, allow_inf_nan=False)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def current_source_digest() -> str:
    """Identify the exact current Python implementation independently of Git HEAD."""
    source_root = Path(__file__).resolve().parent
    return canonical_digest(
        {
            path.relative_to(source_root).as_posix(): digest(path)
            for path in sorted(source_root.rglob("*.py"))
        }
    )


def load_config(path: Path) -> RunConfig:
    config = RunConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    secrets = [os.environ[k] for k in config.secret_environment_keys if os.environ.get(k)]
    if redact_model(config, secrets) != config:
        raise ValueError("credential values are forbidden in configuration")
    return config


def public_cases(path: Path, case_ids: Sequence[str] | None = None) -> list[BenchmarkCase]:
    paths = sorted(path.glob("*.yaml")) if path.is_dir() else [path]
    if not paths:
        raise ValueError("empty public case selection")
    return select_cases(
        load_cases(paths, expected_split="development", public_root=REPOSITORY_ROOT), case_ids
    )


def prepare(config: RunConfig, cases: Sequence[BenchmarkCase]) -> tuple[list[Job], RunManifest]:
    if config.split != "development":
        raise ValueError(
            "restricted execution requires a separate operator-controlled reviewed deployment"
        )
    secrets = [os.environ[k] for k in config.secret_environment_keys if os.environ.get(k)]
    cases = [redact_model(case, secrets) for case in cases]
    jobs = [redact_model(job, secrets) for job in plan_jobs(cases, config, datetime.now(UTC))]
    revision = subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    skill_path = config.skill_path or REPOSITORY_ROOT / "skills/systematic-innovation"
    skill_files = [skill_path / "SKILL.md", *sorted((skill_path / "references").glob("*.md"))]
    skill_revision = canonical_digest(
        {p.relative_to(skill_path).as_posix(): digest(p) for p in skill_files}
    )
    runner_source = current_source_digest()
    dirty = bool(
        subprocess.run(
            ["git", "-C", str(REPOSITORY_ROOT), "status", "--porcelain=v1"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    manifest = RunManifest(
        run_id=config.run_id,
        git_revision=revision,
        runner_source_sha256=runner_source,
        runner_worktree_dirty=dirty,
        skill_revision=skill_revision,
        config=config,
        cases=tuple(cases),
        artifact_digests={
            "dependency_lock": digest(REPOSITORY_ROOT / "benchmark/uv.lock"),
            "planned_jobs": canonical_digest([j.model_dump(mode="json") for j in jobs]),
            "public_corpus": canonical_digest([c.model_dump(mode="json") for c in cases]),
        },
    )
    return jobs, manifest


class RunDirectory:
    def __init__(self, path: Path):
        if path.is_symlink():
            raise ValueError("run directory cannot be a symlink")
        self.path = path.resolve()
        if self.path.is_relative_to(REPOSITORY_ROOT) and not self.path.is_relative_to(
            REPOSITORY_ROOT / "benchmark/runs"
        ):
            raise ValueError("repository results must be in generated runs directory")

    def inside(self, path: Path | str) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.path / candidate
        resolved = candidate.resolve()
        if not resolved.is_relative_to(self.path) or resolved == self.path:
            raise ValueError("output must remain inside configured run directory")
        current = candidate
        while current != self.path and current != current.parent:
            if current.is_symlink():
                raise ValueError("run evidence cannot traverse symlinks")
            current = current.parent
        return resolved

    @contextmanager
    def lock(self) -> Iterator[None]:
        self.path.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(
            self.inside(".runner.lock"), os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600
        )
        with os.fdopen(descriptor, "a") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    @property
    def manifest(self) -> RunManifest:
        return RunManifest.model_validate_json(self.inside("manifest.json").read_text())

    @property
    def jobs(self) -> list[Job]:
        return read_records(self.inside("records/jobs.jsonl"), Job)

    @property
    def turns(self) -> list[TurnResponse]:
        return read_records(self.inside("records/turns.jsonl"), TurnResponse)

    @property
    def responses(self) -> list[ResponseRecord]:
        return read_records(self.inside("records/responses.jsonl"), ResponseRecord)

    def require_current_source(self) -> None:
        if self.manifest.runner_source_sha256 != current_source_digest():
            raise ValueError("runner source differs from the planned implementation")

    def create(self, jobs: Sequence[Job], manifest: RunManifest) -> None:
        if manifest.runner_source_sha256 != current_source_digest():
            raise ValueError("runner source differs from the planned implementation")
        if any(p.name != ".runner.lock" for p in self.path.iterdir()):
            raise ValueError("run directory already contains evidence")
        with self.inside("manifest.json").open("x", encoding="utf-8") as stream:
            stream.write(manifest.model_dump_json(indent=2) + "\n")
        for job in jobs:
            append_record(self.inside("records/jobs.jsonl"), job)
        self.snapshot()

    def snapshot(self) -> None:
        self.require_current_source()
        names = ["manifest.json"]
        for directory in ("records", "reports"):
            root = self.path / directory
            if root.exists():
                names.extend(
                    p.relative_to(self.path).as_posix() for p in root.rglob("*") if p.is_file()
                )
        paths = {name: self.inside(name) for name in sorted(names)}
        append_record(
            self.inside("integrity.jsonl"),
            Snapshot(
                digests={name: digest(path) for name, path in paths.items()},
                sizes={name: path.stat().st_size for name, path in paths.items()},
            ),
        )

    def verify(self) -> dict[str, int]:
        snapshots = read_records(self.inside("integrity.jsonl"), Snapshot)
        if not snapshots:
            raise ValueError("missing integrity record")
        # Only declared append-only logs may have a crash-durable suffix after
        # the last checkpoint. Every previously checkpointed byte remains fixed.
        append_models: dict[str, type[BaseModel]] = {
            "records/turns.jsonl": TurnResponse,
            "records/dispatches.jsonl": Dispatch,
            "records/responses.jsonl": ResponseRecord,
            "records/scores.jsonl": ScoreRecord,
        }
        checkpoint = snapshots[-1]
        for name, expected in checkpoint.digests.items():
            path = self.inside(name)
            size = checkpoint.sizes.get(name)
            if name in append_models and size is not None:
                if path.stat().st_size < size:
                    raise ValueError("append-only evidence was truncated")
                with path.open("rb") as stream:
                    prefix = stream.read(size)
                if hashlib.sha256(prefix).hexdigest() != expected:
                    raise ValueError("artifact prefix digest mismatch")
            elif digest(path) != expected:
                raise ValueError("artifact digest mismatch")
        for name, model in append_models.items():
            path = self.inside(name)
            if path.exists():
                payload = path.read_bytes()
                if payload and not payload.endswith(b"\n"):
                    raise ValueError("incomplete append-only evidence")
                read_records(path, model)
        manifest, jobs = self.manifest, self.jobs
        if (
            canonical_digest([j.model_dump(mode="json") for j in jobs])
            != manifest.artifact_digests["planned_jobs"]
        ):
            raise ValueError("job provenance mismatch")
        if (
            canonical_digest([c.model_dump(mode="json") for c in manifest.cases])
            != manifest.artifact_digests["public_corpus"]
        ):
            raise ValueError("corpus provenance mismatch")
        self.pending(finalize=False)
        return {"verified_artifacts": len(checkpoint.digests), "jobs": len(jobs)}

    def _dispatches(self) -> list[Dispatch]:
        dispatches = read_records(self.inside("records/dispatches.jsonl"), Dispatch)
        config = self.manifest.config
        jobs = {job.job_id: job for job in self.jobs}
        if len({item.turn_id for item in dispatches}) != len(dispatches):
            raise ValueError("duplicate dispatch evidence")
        if len(dispatches) > config.max_calls:
            raise ValueError("dispatch call ceiling violated")
        for item in dispatches:
            try:
                job_id, index_text, attempt_text = item.turn_id.rsplit(":", 2)
                job = jobs[job_id]
                index, attempt = int(index_text), int(attempt_text)
                maximum = (
                    job.conversation_script.maximum_assistant_turns
                    if job.conversation_script
                    else 1
                )
            except (ValueError, KeyError):
                raise ValueError("unknown dispatch identity") from None
            if (
                index < 2
                or index % 2
                or index > 2 * maximum
                or attempt < 0
                or attempt > config.retry_limit
                or item.model != job.model
                or item.reserved_cost != config.cost_per_turn.get(job.model)
            ):
                raise ValueError("dispatch does not match declared job or limits")
        return dispatches

    def pending(self, *, finalize: bool = False) -> list[TurnJob]:
        if finalize:
            self.require_current_source()
        manifest, jobs, turns, terminal = self.manifest, self.jobs, self.turns, self.responses
        case_map = {case.id: case for case in manifest.cases}
        job_ids = {job.job_id for job in jobs}
        if len(job_ids) != len(jobs):
            raise ValueError("duplicate planned job")
        if any(turn.job_id not in job_ids for turn in turns) or any(
            r.job_id not in job_ids for r in terminal
        ):
            raise ValueError("uncorrelated stored evidence")
        dispatches = self._dispatches()
        dispatch_ids = {item.turn_id for item in dispatches}
        if any(turn.turn_id not in dispatch_ids for turn in turns):
            raise ValueError("stored response has no declared dispatch")
        completed = {r.job_id: r for r in terminal}
        if len(completed) != len(terminal):
            raise ValueError("duplicate terminal job evidence")
        pending = []
        for job in jobs:
            raw_records = [turn for turn in turns if turn.job_id == job.job_id]
            records = turn_responses_for_job(turns, job.job_id)
            if tuple(raw_records) != records:
                raise ValueError("stored turns are not in execution order")
            state = resume_conversation(job, case_map[job.case_id], records)
            terminal_response = completed.get(job.job_id)
            if state.is_budget_stopped:
                stopped = self._stopped_response(
                    job.job_id, records, "budget-stopped", "ADAPTER_BUDGET_STOP"
                )
                if terminal_response is not None:
                    if (
                        terminal_response.status != stopped.status
                        or terminal_response.error != stopped.error
                        or terminal_response.output_tokens != stopped.output_tokens
                        or terminal_response.cost != stopped.cost
                        or terminal_response.latency_seconds != stopped.latency_seconds
                    ):
                        raise ValueError(
                            "terminal budget stop differs from recorded assistant attempts"
                        )
                elif finalize:
                    append_record(self.inside("records/responses.jsonl"), stopped)
                continue
            if state.is_complete:
                conversation = complete_conversation(state)
                status: Literal["refused", "succeeded"] = (
                    "refused" if any(t.status == "refused" for t in records) else "succeeded"
                )
                if terminal_response is not None:
                    if (
                        terminal_response.status != status
                        or terminal_response.conversation != conversation
                        or terminal_response.content != conversation.final_response
                        or terminal_response.output_tokens
                        != conversation.final_response_output_tokens
                    ):
                        raise ValueError("terminal response differs from completed conversation")
                elif finalize:
                    append_record(
                        self.inside("records/responses.jsonl"),
                        ResponseRecord(
                            job_id=job.job_id,
                            status=status,
                            content=conversation.final_response,
                            conversation=conversation,
                            output_tokens=conversation.final_response_output_tokens,
                            cost=conversation.total_cost,
                            latency_seconds=conversation.total_latency_seconds,
                        ),
                    )
                continue
            next_job = next_turn_job(state)
            if next_job is None:
                raise ValueError("incomplete conversation has no continuation")
            if terminal_response is not None:
                if (
                    terminal_response.status == "failed"
                    and next_job.attempt > manifest.config.retry_limit
                ):
                    continue
                if terminal_response.status == "budget-stopped" and terminal_response.error in {
                    "MAX_CALLS",
                    "MAX_COST",
                    "FAILURE_THRESHOLD",
                    "COST_CEILING_EXCEEDED",
                    "UNKNOWN_COST",
                }:
                    continue
                raise ValueError("terminal response does not match conversation state")
            if next_job.attempt > manifest.config.retry_limit:
                if finalize:
                    append_record(
                        self.inside("records/responses.jsonl"),
                        self._stopped_response(job.job_id, records, "failed", "RETRY_LIMIT"),
                    )
                continue
            pending.append(next_job)
        return pending

    @staticmethod
    def _stopped_response(
        job_id: str,
        records: Sequence[TurnResponse],
        status: Literal["failed", "budget-stopped"],
        error: str,
    ) -> ResponseRecord:
        tokens, costs, latencies = (
            [r.output_tokens for r in records],
            [r.cost for r in records],
            [r.latency_seconds for r in records],
        )
        return ResponseRecord(
            job_id=job_id,
            status=status,
            error=error,
            output_tokens=sum(v for v in tokens if v is not None)
            if all(v is not None for v in tokens)
            else None,
            cost=sum(v for v in costs if v is not None)
            if all(v is not None for v in costs)
            else None,
            latency_seconds=sum(v for v in latencies if v is not None)
            if all(v is not None for v in latencies)
            else None,
        )

    def _reservation_issue(self, candidates: Sequence[TurnJob]) -> str | None:
        config = self.manifest.config
        dispatches = self._dispatches()
        dispatch_ids = {item.turn_id for item in dispatches}
        new = [turn for turn in candidates if turn.turn_id not in dispatch_ids]
        if len({turn.turn_id for turn in candidates}) != len(candidates):
            raise ValueError("duplicate reservation request")
        if any(turn.model not in config.model_allowlist for turn in new):
            raise ValueError("model is outside declared allowlist")
        if any(turn.model not in config.cost_per_turn for turn in new):
            return "UNKNOWN_COST"
        if len(dispatches) + len(new) > config.max_calls:
            return "MAX_CALLS"
        responses = {response.turn_id: response for response in self.turns}
        if any(
            (cost := responses[item.turn_id].cost) is not None and cost > item.reserved_cost + 1e-12
            for item in dispatches
            if item.turn_id in responses
        ):
            return "COST_CEILING_EXCEEDED"
        charged = sum(
            max(item.reserved_cost, responses[item.turn_id].cost or 0)
            if item.turn_id in responses
            else item.reserved_cost
            for item in dispatches
        )
        if (
            charged + sum(config.cost_per_turn[turn.model] for turn in new)
            > config.max_cost + 1e-12
        ):
            return "MAX_COST"
        observed = self.turns
        if (
            observed
            and sum(turn.status == "failed" for turn in observed) / len(observed)
            > config.failure_threshold
        ):
            return "FAILURE_THRESHOLD"
        return None

    def _stop_for_budget(self, issue: str) -> None:
        dispatch_ids = {item.turn_id for item in self._dispatches()}
        for turn in self.pending():
            if turn.turn_id not in dispatch_ids:
                records = turn_responses_for_job(self.turns, turn.job_id)
                append_record(
                    self.inside("records/responses.jsonl"),
                    self._stopped_response(turn.job_id, records, "budget-stopped", issue),
                )
        self.snapshot()

    def reserve(self, turn: TurnJob) -> None:
        self.require_current_source()
        issue = self._reservation_issue([turn])
        if issue:
            raise ValueError(issue)
        if turn.turn_id in {item.turn_id for item in self._dispatches()}:
            return
        append_record(
            self.inside("records/dispatches.jsonl"),
            Dispatch(
                turn_id=turn.turn_id,
                model=turn.model,
                reserved_cost=self.manifest.config.cost_per_turn[turn.model],
            ),
        )

    @staticmethod
    def opaque(turn: TurnJob) -> TurnJob:
        opaque_id = hashlib.sha256(turn.job_id.encode()).hexdigest()
        return TurnJob.model_validate(turn.model_dump() | {"job_id": opaque_id, "turn_id": ""})

    def export(self, output: Path) -> int:
        self.require_current_source()
        target = self.inside(output)  # Refuse invalid paths before reservations or finalization.
        dispatches = self._dispatches()
        response_ids = {turn.turn_id for turn in self.turns}
        unresolved = {item.turn_id for item in dispatches if item.turn_id not in response_ids}
        available = max(0, self.manifest.config.max_concurrency - len(unresolved))
        reserved = {item.turn_id for item in dispatches}
        pending = [turn for turn in self.pending() if turn.turn_id not in reserved][:available]
        if not pending:
            return 0
        if target.exists():
            raise ValueError("export requires a new request artifact")
        issue = self._reservation_issue(pending)
        if issue:
            self._stop_for_budget(issue)
            raise ValueError(issue)
        # Every path and limit is validated before the first durable reservation.
        for turn in pending:
            self.reserve(turn)
        export_turn_jobs([self.opaque(turn) for turn in pending], target)
        self.pending(finalize=True)
        self.snapshot()
        return len(pending)

    @staticmethod
    def _same_response(left: TurnResponse, right: TurnResponse) -> bool:
        # Missing provider timestamps are assigned on first acceptance. Re-reading
        # an unchanged exchange file must not manufacture a conflicting timestamp.
        return left.model_dump(exclude={"created_at"}) == right.model_dump(exclude={"created_at"})

    def ingest(self, incoming: Path) -> int:
        self.require_current_source()
        pending = self.pending()
        config = self.manifest.config
        secrets = [os.environ[key] for key in config.secret_environment_keys if os.environ.get(key)]
        responses = ingest_turn_responses(incoming, secret_values=secrets)
        current = {self.opaque(turn).turn_id: turn for turn in pending}
        accepted = {}
        for response in self.turns:
            opaque_id = hashlib.sha256(response.job_id.encode()).hexdigest()
            accepted_response = TurnResponse.model_validate(
                response.model_dump() | {"job_id": opaque_id, "turn_id": ""}
            )
            accepted[accepted_response.turn_id] = accepted_response
        reserved = {item.turn_id for item in self._dispatches()}
        seen: set[str] = set()
        validated = []
        for response in responses:
            if response.turn_id in seen:
                raise ValueError("duplicate incoming response")
            seen.add(response.turn_id)
            if response.turn_id in accepted:
                if not self._same_response(response, accepted[response.turn_id]):
                    raise ValueError("accepted response cannot be replaced")
                continue
            if response.turn_id not in current:
                raise ValueError("unknown or out-of-order incoming turn")
            turn = current[response.turn_id]
            if turn.turn_id not in reserved:
                raise ValueError("response was never dispatched")
            converted = TurnResponse.model_validate(
                response.model_dump() | {"job_id": turn.job_id, "turn_id": ""}
            )
            job = next(job for job in self.jobs if job.job_id == turn.job_id)
            case = next(case for case in self.manifest.cases if case.id == job.case_id)
            state = resume_conversation(job, case, turn_responses_for_job(self.turns, job.job_id))
            accept_turn(state, turn, converted)
            validated.append(converted)
        # No untrusted row can fail validation after earlier rows have been written.
        for response in validated:
            append_record(self.inside("records/turns.jsonl"), response, secret_values=secrets)
        self.pending(finalize=True)
        self.snapshot()
        return len(validated)

    def execute(self) -> int:
        self.require_current_source()
        from .adapters.subprocess import SubprocessAdapter

        config = self.manifest.config
        if set(config.hosts) != {"subprocess"} or not config.adapter_command:
            raise ValueError(
                "run requires a declared subprocess adapter; use export for inbox jobs"
            )
        if any(model not in config.cost_per_turn for model in config.models):
            raise ValueError("known cost ceiling required before adapter launch")
        secrets = [os.environ[key] for key in config.secret_environment_keys if os.environ.get(key)]
        adapter = SubprocessAdapter(
            tuple(config.adapter_command),
            frozenset(config.allowed_executables),
            config.timeout_seconds,
            environment_allowlist=frozenset(config.environment_allowlist),
            secret_values=secrets,
            max_output_bytes=config.max_output_bytes,
        )
        calls = 0
        while pending := self.pending(finalize=True):
            turn = pending[0]
            if turn.turn_id in {item.turn_id for item in self._dispatches()}:
                raise ValueError("unresolved dispatch requires explicit correlated ingestion")
            issue = self._reservation_issue([turn])
            if issue:
                self._stop_for_budget(issue)
                raise ValueError(issue)
            self.reserve(turn)
            self.snapshot()
            result = adapter.run_turn(self.opaque(turn))
            result = TurnResponse.model_validate(
                result.model_dump() | {"job_id": turn.job_id, "turn_id": ""}
            )
            job = next(job for job in self.jobs if job.job_id == turn.job_id)
            case = next(case for case in self.manifest.cases if case.id == job.case_id)
            state = resume_conversation(job, case, turn_responses_for_job(self.turns, turn.job_id))
            accept_turn(state, turn, result)
            append_record(self.inside("records/turns.jsonl"), result, secret_values=secrets)
            calls += 1
            self.pending(finalize=True)
            self.snapshot()
        self.snapshot()
        return calls
