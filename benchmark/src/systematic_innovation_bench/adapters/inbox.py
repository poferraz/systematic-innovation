"""Typed inbox/outbox exchange with exact turn correlation."""

from collections.abc import Sequence
from pathlib import Path

from ..models import TurnJob, TurnResponse
from ..redaction import redact_model
from ..store import append_record, read_records


def export_turn_jobs(jobs: Sequence[TurnJob], path: Path) -> None:
    existing = {item.turn_id: item for item in read_records(path, TurnJob)}
    if len({item.turn_id for item in jobs}) != len(jobs):
        raise ValueError("duplicate exported turn job")
    for job in jobs:
        if job.turn_id in existing:
            if existing[job.turn_id] != job:
                raise ValueError("exported transcript cannot be replaced")
        else:
            append_record(path, job)


def validate_turn_correlation(jobs: Sequence[TurnJob], responses: Sequence[TurnResponse]) -> None:
    pending = {(job.job_id, job.assistant_turn_index, job.attempt): job for job in jobs}
    if len(pending) != len(jobs):
        raise ValueError("duplicate pending turn job")
    observed: set[tuple[str, int, int]] = set()
    for response in responses:
        key = (response.job_id, response.turn_index, response.attempt)
        if key not in pending:
            raise ValueError("unknown, out-of-order, or unrequested turn response")
        if key in observed:
            raise ValueError("duplicate turn response")
        if response.status == "succeeded" and not response.content.strip():
            raise ValueError("successful turn response requires raw text")
        observed.add(key)


def ingest_turn_responses(
    path: Path,
    *,
    jobs: Sequence[TurnJob] | None = None,
    canonical_path: Path | None = None,
    secret_values: Sequence[str] = (),
) -> list[TurnResponse]:
    responses = [
        redact_model(response, secret_values) for response in read_records(path, TurnResponse)
    ]
    if jobs is not None:
        validate_turn_correlation(jobs, responses)
    if canonical_path is not None:
        if jobs is None:
            raise ValueError("canonical ingestion requires pending turn correlation")
        existing = {item.turn_id: item for item in read_records(canonical_path, TurnResponse)}
        for response in responses:
            if response.turn_id in existing:
                if existing[response.turn_id] != response:
                    raise ValueError("accepted response cannot be replaced")
            else:
                append_record(canonical_path, response)
    return responses
