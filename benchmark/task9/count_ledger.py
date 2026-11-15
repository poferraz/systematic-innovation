"""Separate, durable one-shot count receipts; never inference or dollar usage.

The worker holds its process lock around every operation here. A root marker
detects accidental removal of the counts directory; complete malicious rewriting
of every local evidence file remains outside the local hash-chain guarantee.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from systematic_innovation_bench.runtime import canonical_digest

from .contracts import CountReceipt, InputBound
from .guards import ZERO_SHA, Task9Error, _exclusive_file, _fsync_directory, _safe_path

_MARKER = b'{"schema":"task9-count-ledger-v1"}\n'


def validate_count_bound(bound: InputBound, *, request_sha256: str,
                         count_request_sha256: str, profile_sha256: str,
                         account_id: str, project_id: str,
                         live: bool | None = None) -> None:
    """Check retained provider evidence independently of a counter's boolean."""
    try:
        checked = InputBound.model_validate(bound.model_dump())
        evidence = checked.provider_evidence
        if (checked.request_sha256 != request_sha256
                or checked.profile_sha256 != profile_sha256
                or checked.tokens <= 0 or evidence is None
                or evidence.count_request_sha256 != count_request_sha256
                or evidence.account_id != account_id or evidence.project_id != project_id
                or evidence.counted_at > datetime.now(UTC)
                or (live is not None and checked.certified_for_live is not live)
                or hashlib.sha256(evidence.response_json.encode()).hexdigest()
                != evidence.response_sha256):
            raise ValueError("metadata")

        def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate")
                result[key] = value
            return result

        raw = json.loads(evidence.response_json, object_pairs_hook=unique)
        if (not isinstance(raw, dict) or set(raw) != {"object", "input_tokens"}
                or raw["object"] != "response.input_tokens"
                or type(raw["input_tokens"]) is not int
                or raw["input_tokens"] != checked.tokens):
            raise ValueError("response")
    except Exception:  # noqa: BLE001 - count metadata may be provider controlled
        raise Task9Error("TASK9_COUNT_EVIDENCE_INVALID") from None


def _claim_name(turn_id: str) -> str:
    return "claims/" + hashlib.sha256(turn_id.encode()).hexdigest() + ".json"


def validate_provider_bound(bound: InputBound, payload: dict[str, Any], *,
                            account_id: str, project_id: str, profile_sha256: str,
                            transport_live: bool) -> None:
    """Verify the count projection/profile against an actual generation payload."""
    from .counting import build_count_payload, counting_profile

    try:
        if profile_sha256 != canonical_digest(counting_profile()):
            raise ValueError("profile")
        validate_count_bound(
            bound, request_sha256=canonical_digest(payload),
            count_request_sha256=canonical_digest(build_count_payload(payload)),
            profile_sha256=profile_sha256, account_id=account_id, project_id=project_id,
            live=transport_live,
        )
    except Exception:  # noqa: BLE001 - retain only the public rule identifier
        raise Task9Error("TASK9_COUNT_EVIDENCE_INVALID") from None


def _identity(record: CountReceipt) -> dict[str, str]:
    return {name: getattr(record, name) for name in (
        "turn_id", "request_sha256", "count_request_sha256", "profile_sha256",
        "account_id", "project_id",
    )}


def read_count_receipts(ledger_root: Path) -> list[CountReceipt]:
    """Read ``worker/counts`` using the same worker-root convention as receipts."""
    try:
        if ledger_root.is_symlink():
            raise ValueError("path")
        root = _safe_path(ledger_root, "counts")
        marker = _safe_path(ledger_root, "counting.json")
        if not root.exists() and not marker.exists():
            return []
        if not root.is_dir() or not marker.is_file() or marker.read_bytes() != _MARKER:
            raise ValueError("marker")
        journal = _safe_path(root, "attempts.jsonl")
        payload = journal.read_bytes() if journal.exists() else b""
        if payload and not payload.endswith(b"\n"):
            raise ValueError("tail")
        rows = [CountReceipt.model_validate_json(line) for line in payload.splitlines()]
        states: dict[str, CountReceipt] = {}
        starts: dict[str, CountReceipt] = {}
        previous = ZERO_SHA
        for seq, row in enumerate(rows, 1):
            if (row.seq != seq or row.previous_sha256 != previous
                    or row.sha256 != canonical_digest(row.model_dump(
                        mode="json", exclude={"sha256"}))
                    or row.timestamp.tzinfo is None or row.timestamp.utcoffset() is None):
                raise ValueError("hash")
            prior = states.get(row.turn_id)
            if row.event == "started":
                if prior is not None or row.input_bound is not None or row.error is not None:
                    raise ValueError("transition")
                starts[row.turn_id] = row
            elif (prior is None or prior.event != "started"
                  or _identity(prior) != _identity(row) or row.timestamp < prior.timestamp):
                raise ValueError("transition")
            elif row.event == "completed":
                if row.input_bound is None or row.error is not None:
                    raise ValueError("completion")
            elif row.error is None:
                raise ValueError("error")
            if row.input_bound is not None:
                validate_count_bound(
                    row.input_bound, request_sha256=row.request_sha256,
                    count_request_sha256=row.count_request_sha256,
                    profile_sha256=row.profile_sha256, account_id=row.account_id,
                    project_id=row.project_id,
                )
                evidence = row.input_bound.provider_evidence
                assert evidence is not None
                if not starts[row.turn_id].timestamp <= evidence.counted_at <= row.timestamp:
                    raise ValueError("time")
            states[row.turn_id] = row
            previous = row.sha256
        if len(starts) > 70:
            raise ValueError("ceiling")
        claims = _safe_path(root, "claims")
        actual = set(claims.iterdir()) if claims.exists() else set()
        expected = {_safe_path(root, _claim_name(turn_id)) for turn_id in starts}
        if actual != expected:
            raise ValueError("claims")
        for turn_id, row in starts.items():
            claim = _safe_path(root, _claim_name(turn_id))
            if json.loads(claim.read_bytes()) != _identity(row):
                raise ValueError("claim")
        return rows
    except Exception:  # noqa: BLE001 - filesystem/provider metadata stays private
        raise Task9Error("TASK9_COUNT_LEDGER_INTEGRITY") from None


class CountLedger:
    """Mutation helper used only while the enclosing worker lock is held."""

    def __init__(self, ledger_root: Path):
        self.ledger_root = ledger_root
        self.root = _safe_path(ledger_root, "counts")
        self.rows = read_count_receipts(ledger_root)
        self.active: dict[str, str] | None = None

    def _append(self, event: Literal["started", "completed", "error"], *,
                input_bound: InputBound | None = None,
                error: str | None = None) -> None:
        if self.active is None:
            raise Task9Error("TASK9_COUNT_LEDGER_INTEGRITY")
        row = CountReceipt(
            seq=len(self.rows) + 1, event=event,
            **self.active, timestamp=datetime.now(UTC), input_bound=input_bound, error=error,
            previous_sha256=self.rows[-1].sha256 if self.rows else ZERO_SHA, sha256=ZERO_SHA,
        )
        row = row.model_copy(update={"sha256": canonical_digest(row.model_dump(
            mode="json", exclude={"sha256"}))})
        path = _safe_path(self.root, "attempts.jsonl")
        descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "ab") as stream:
            stream.write(row.model_dump_json().encode() + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        _fsync_directory(self.root)
        self.rows.append(row)

    def start(self, **identity: str) -> None:
        if (self.active is not None or any(row.turn_id == identity.get("turn_id")
                                           for row in self.rows)
                or sum(row.event == "started" for row in self.rows) >= 70
                or any(row.event != "completed" for row in {
                    item.turn_id: item for item in self.rows}.values())):
            raise Task9Error("TASK9_COUNT_ATTEMPT_REFUSED")
        self.root.mkdir(parents=True, exist_ok=True)
        marker = _safe_path(self.ledger_root, "counting.json")
        if not marker.exists():
            _exclusive_file(marker, _MARKER)
        self.active = identity
        _exclusive_file(_safe_path(self.root, _claim_name(identity["turn_id"])),
                        json.dumps(identity, sort_keys=True).encode() + b"\n")
        self._append("started")

    def complete(self, bound: InputBound) -> None:
        self._append("completed", input_bound=bound)
        self.active = None

    def fail(self) -> None:
        self._append("error", error="TASK9_COUNT_UNRESOLVED")
        self.active = None
