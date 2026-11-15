"""Stateless, fail-closed Responses API worker behind the durable guard."""
from __future__ import annotations

import copy
import json
import math
import time
from collections.abc import Callable
from decimal import Decimal
from typing import Any, Protocol

from systematic_innovation_bench.models import TurnJob, TurnResponse
from systematic_innovation_bench.redaction import redact_object

from .contracts import InputBound
from .transport import HTTPReply, Transport, TransportError

MODEL = "gpt-5.4-mini-2026-03-17"
PARAMETERS: dict[str, Any] = {
    "reasoning": {"effort": "none"}, "text": {"verbosity": "medium"},
    "service_tier": "default", "store": False, "tools": [], "tool_choice": "none",
    "truncation": "disabled", "max_output_tokens": 4096,
}
_TRANSPORT_CODES = frozenset({
    "request-timeout", "response-too-large", "credential-unavailable", "deadline-unavailable",
    "transport-limits-invalid", "transport-failed",
})


class WorkerError(ValueError):
    """Code-only pre-dispatch request error."""


class InputCounter(Protocol):
    def bound(self, payload: dict[str, Any]) -> InputBound: ...


class Guard(Protocol):
    def process_with_counter(
        self, job: TurnJob, payload: dict[str, Any], counter: InputCounter,
        send_callback: Callable[[], TurnResponse], *, transport_live: bool,
    ) -> TurnResponse: ...


def build_payload(job: TurnJob) -> dict[str, Any]:
    """Translate only declared instructions/transcript, without host context."""
    if (
        job.model != MODEL or job.host != "inbox" or job.attempt != 0
        or json.dumps(job.model_parameters, sort_keys=True, allow_nan=False)
        != json.dumps(PARAMETERS, sort_keys=True)
    ):
        raise WorkerError("request-contract-invalid")
    return {
        "model": MODEL, "instructions": job.system_instructions,
        "input": [{"role": turn.role, "content": turn.content} for turn in job.transcript],
        **copy.deepcopy(PARAMETERS),
    }


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate")
        result[key] = value
    return result


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite")
    return number


def _invalid_constant(value: str) -> None:
    raise ValueError("nonfinite")


def _decode(body: bytes) -> dict[str, Any]:
    result = json.loads(
        body.decode("utf-8"), object_pairs_hook=_unique_object,
        parse_float=_finite_float, parse_constant=_invalid_constant,
    )
    if not isinstance(result, dict):
        raise TypeError("object-required")
    return result


def _usage(data: dict[str, Any]) -> tuple[int, int]:
    usage = data.get("usage")
    if not isinstance(usage, dict) or set(usage) - {
        "input_tokens", "output_tokens", "total_tokens", "input_tokens_details", "output_tokens_details"
    }:
        raise WorkerError("provider-usage-invalid")
    incoming, outgoing = usage.get("input_tokens"), usage.get("output_tokens")
    if (
        type(incoming) is not int or not 0 < incoming <= 32768
        or type(outgoing) is not int or not 0 < outgoing <= 4096
        or ("total_tokens" in usage and (
            type(usage["total_tokens"]) is not int or usage["total_tokens"] != incoming + outgoing
        ))
    ):
        raise WorkerError("provider-usage-invalid")
    for field, ceiling in (("input_tokens_details", incoming), ("output_tokens_details", outgoing)):
        if field in usage:
            details = usage[field]
            if not isinstance(details, dict) or any(
                type(count) is not int or not 0 <= count <= ceiling for count in details.values()
            ):
                raise WorkerError("provider-usage-invalid")
    return incoming, outgoing


def _content(data: dict[str, Any]) -> tuple[str, bool]:
    output = data.get("output")
    if not isinstance(output, list):
        raise WorkerError("provider-output-invalid")
    pieces: list[str] = []
    refused = False
    for item in output:
        if isinstance(item, dict) and item.get("type") == "reasoning":
            summary = item.get("summary")
            reasoning_content = item.get("content", [])
            if (
                not isinstance(reasoning_content, list)
                or any(not isinstance(part, dict) or part.get("type") != "reasoning_text"
                       or not isinstance(part.get("text"), str) for part in reasoning_content)
                or ("encrypted_content" in item and item["encrypted_content"] is not None
                    and not isinstance(item["encrypted_content"], str))
                or
                not isinstance(summary, list) or item.get("status") not in (None, "completed")
                or any(not isinstance(part, dict) or part.get("type") != "summary_text"
                       or not isinstance(part.get("text"), str) for part in summary)
            ):
                raise WorkerError("provider-output-invalid")
            # Non-visible provider output remains in raw evidence and total usage;
            # only assistant message text/refusals form the benchmark answer.
            continue
        if (
            not isinstance(item, dict) or item.get("type") != "message"
            or item.get("role") != "assistant" or item.get("status") != "completed"
            or not isinstance(item.get("content"), list) or not item["content"]
        ):
            raise WorkerError("provider-output-invalid")
        for part in item["content"]:
            if not isinstance(part, dict):
                raise WorkerError("provider-output-invalid")
            if part.get("type") == "output_text":
                value = part.get("text")
            elif part.get("type") == "refusal":
                value = part.get("refusal")
                refused = True
            else:
                raise WorkerError("provider-output-invalid")
            if not isinstance(value, str) or not value.strip():
                raise WorkerError("provider-output-invalid")
            pieces.append(value)
    if not pieces:
        raise WorkerError("provider-content-empty")
    return "\n".join(pieces), refused


class Worker:
    def __init__(self, guard: Guard, transport: Transport, counter: InputCounter) -> None:
        self.guard = guard
        self.transport = transport
        self.counter = counter

    def process(self, job: TurnJob) -> TurnResponse:
        if self.transport.is_live and any(
            not getattr(self.transport, name, None)
            or getattr(self.transport, name, None) != getattr(self.guard, "transport_" + name, None)
            for name in ("account_id", "project_id")
        ):
            raise WorkerError("transport-identity-mismatch")
        payload = build_payload(job)
        return self.guard.process_with_counter(
            job, payload, self.counter, lambda: self._send(job, payload),
            transport_live=self.transport.is_live,
        )

    def _send(self, job: TurnJob, payload: dict[str, Any]) -> TurnResponse:
        started = time.monotonic()
        common: dict[str, Any] = {
            "job_id": job.job_id, "turn_index": job.assistant_turn_index, "attempt": 0,
            "content": "", "status": "failed",
        }
        raw: str | None = None
        reply: HTTPReply | None = None
        try:
            reply = self.transport.send(payload, timeout_seconds=120, max_output_bytes=1048576)
            if len(reply.body) > 1048576:
                raise WorkerError("response-too-large")
            try:
                data = _decode(reply.body)
            except (UnicodeError, ValueError, TypeError, RecursionError):
                raise WorkerError("provider-json-invalid") from None
            envelope = {
                "provider_response": data, "request_id": reply.request_id,
                "http_status": reply.status,
                "cost_provenance": {
                    "kind": "calculated-token-rate-upper-bound", "currency": "USD",
                    "input_rate_usd_per_million": "0.75",
                    "output_rate_usd_per_million": "4.50",
                    "basis": "provider-total-tokens; uncached input rate; reasoning not added again",
                },
            }
            raw = json.dumps(redact_object(reply.redact(envelope)), allow_nan=False, sort_keys=True)
            if reply.status != 200:
                raise WorkerError("provider-http-status")
            if (
                not isinstance(data.get("id"), str) or not data["id"].strip()
                or not isinstance(reply.request_id, str) or not reply.request_id.strip()
            ):
                raise WorkerError("provider-metadata-invalid")
            if data.get("model") != MODEL:
                raise WorkerError("provider-model-mismatch")
            if data.get("service_tier") != "default":
                raise WorkerError("provider-tier-mismatch")
            if (
                data.get("status") != "completed" or data.get("error") is not None
                or data.get("incomplete_details") is not None
            ):
                raise WorkerError("provider-not-completed")
            incoming, outgoing = _usage(data)
            content, refused = _content(data)
            common.update(
                content=content, status="refused" if refused else "succeeded",
                input_tokens=incoming, output_tokens=outgoing,
                cost=float((Decimal(incoming) * Decimal("0.75")
                            + Decimal(outgoing) * Decimal("4.50")) / Decimal(1000000)),
            )
        except WorkerError as error:
            common["error"] = str(error)
        except TransportError as error:
            common["error"] = str(error) if str(error) in _TRANSPORT_CODES else "transport-failed"
        except Exception:  # noqa: BLE001 - sanitize untrusted boundary exceptions
            common["error"] = "transport-failed"
        common["latency_seconds"] = float(time.monotonic() - started)
        try:
            if reply is not None:
                common = reply.redact(common)
            common = redact_object(common)
            # Redact parsed provider data before serialization. Running regex redaction
            # on this JSON string again can invalidate quoted credential-key values.
            common["raw_response"] = raw
            return TurnResponse(**common)
        except Exception:  # noqa: BLE001 - a failed redactor must never leak response text
            return TurnResponse(
                job_id=job.job_id, turn_index=job.assistant_turn_index, attempt=0,
                status="failed", content="", error="response-redaction-failed",
                latency_seconds=float(time.monotonic() - started),
            )
