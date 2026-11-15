"""Append-only, process-locked JSONL evidence storage."""

import fcntl
import os
from collections.abc import Sequence
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .models import ResponseRecord, TurnResponse
from .redaction import redact_model

T = TypeVar("T", bound=BaseModel)


def _parse_lines(payload: str, model_type: type[T]) -> list[T]:
    records: list[T] = []
    for index, line in enumerate(payload.splitlines(), 1):
        try:
            records.append(model_type.model_validate_json(line))
        except ValueError:
            raise ValueError(f"invalid JSONL record at line {index}") from None
    return records


def append_record(path: Path, record: BaseModel, *, secret_values: Sequence[str] = ()) -> None:
    record = redact_model(record, secret_values)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("evidence path cannot be a symlink")
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            handle.seek(0)
            payload = handle.read()
            if payload and not payload.endswith("\n"):
                raise ValueError("incomplete JSONL record prevents append")
            existing = _parse_lines(payload, type(record))
            if isinstance(record, ResponseRecord):
                related = [
                    item
                    for item in existing
                    if isinstance(item, ResponseRecord) and item.job_id == record.job_id
                ]
                if any(item.attempt == record.attempt for item in related):
                    raise ValueError("duplicate terminal response")
                if related and (
                    max(item.attempt for item in related) >= record.attempt
                    or any(item.status != "failed" for item in related)
                ):
                    raise ValueError("terminal response cannot be retried")
            elif isinstance(record, TurnResponse):
                related_turns = [
                    item
                    for item in existing
                    if isinstance(item, TurnResponse)
                    and item.job_id == record.job_id
                    and item.turn_index == record.turn_index
                ]
                if any(item.attempt == record.attempt for item in related_turns):
                    raise ValueError("duplicate turn response")
                if related_turns and (
                    max(item.attempt for item in related_turns) >= record.attempt
                    or any(item.status != "failed" for item in related_turns)
                ):
                    raise ValueError("accepted turn cannot be replaced")
            handle.write(record.model_dump_json(exclude_none=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def read_records(path: Path, model_type: type[T]) -> list[T]:
    if not path.exists():
        return []
    if path.is_symlink():
        raise ValueError("evidence path cannot be a symlink")
    with path.open("r", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
        try:
            return _parse_lines(handle.read(), model_type)
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def turn_responses_for_job(
    responses: Sequence[TurnResponse], job_id: str
) -> tuple[TurnResponse, ...]:
    selected = [response for response in responses if response.job_id == job_id]
    if len({response.turn_id for response in selected}) != len(selected):
        raise ValueError("duplicate turn evidence")
    return tuple(sorted(selected, key=lambda item: (item.turn_index, item.attempt)))


def terminal_job_ids(responses: Sequence[ResponseRecord]) -> frozenset[str]:
    return frozenset(response.job_id for response in responses)
