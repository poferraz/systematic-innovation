"""Request-bound offline replay of explicitly supplied synthetic HTTP fixtures."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import Field, StrictInt

from systematic_innovation_bench.runtime import canonical_digest

from .contracts import Contract, InputBound, Sha256
from .transport import HTTPReply


def request_digest(payload: dict[str, Any]) -> str:
    return canonical_digest(payload)


class ReplayRecord(Contract):
    request_sha256: Sha256
    input_bound_tokens: StrictInt = Field(ge=1, le=32768)
    status: StrictInt = Field(ge=100, le=599)
    request_id: str = Field(min_length=1, max_length=200)
    body: dict[str, Any]


class ReplayFile(Contract):
    responses: tuple[ReplayRecord, ...] = Field(min_length=1, max_length=70)


class ReplayBundle:
    """An offline counter/transport pair. It cannot certify or use a live endpoint."""
    is_live = False
    profile_sha256 = hashlib.sha256(b"task9-request-bound-offline-fixtures-v1").hexdigest()

    def __init__(self, records: tuple[ReplayRecord, ...]) -> None:
        self.records = {row.request_sha256: row for row in records}
        if len(self.records) != len(records):
            raise ValueError("TASK9_DUPLICATE_REPLAY")

    @classmethod
    def load(cls, path: Path) -> ReplayBundle:
        if path.is_symlink() or path.stat().st_size > 16 * 1048576:
            raise ValueError("TASK9_REPLAY_INVALID")
        return cls(ReplayFile.model_validate_json(path.read_bytes()).responses)

    def _record(self, payload: dict[str, Any]) -> ReplayRecord:
        row = self.records.get(request_digest(payload))
        if row is None:
            raise ValueError("TASK9_REPLAY_REQUEST_UNKNOWN")
        return row

    def bound(self, payload: dict[str, Any]) -> InputBound:
        return InputBound(tokens=self._record(payload).input_bound_tokens,
                          profile_sha256=self.profile_sha256,
                          request_sha256=request_digest(payload), certified_for_live=False)

    def send(self, payload: dict[str, Any], *, timeout_seconds: float,
             max_output_bytes: int) -> HTTPReply:
        if timeout_seconds <= 0 or max_output_bytes <= 0:
            raise ValueError("TASK9_REPLAY_LIMIT_INVALID")
        row = self._record(payload)
        body = json.dumps(row.body, sort_keys=True, allow_nan=False).encode()
        if len(body) > max_output_bytes:
            raise ValueError("TASK9_REPLAY_RESPONSE_TOO_LARGE")
        return HTTPReply(status=row.status, body=body, request_id=row.request_id)
