"""Request-bound provider counting, invoked only inside Task 9's durable guard.

The provider documents full input counts, including message framing. A fixture
reply remains offline evidence; this adapter never certifies the local tokenizer.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from datetime import UTC, datetime
from typing import Any

from systematic_innovation_bench.redaction import redact_object
from systematic_innovation_bench.runtime import canonical_digest

from .contracts import MODEL, InputBound, ProviderCountEvidence
from .transport import HTTPCountTransport, HTTPTransport, Transport, TransportError

_COUNT_FIELDS = ("model", "instructions", "input", "reasoning", "text", "tools",
                 "tool_choice", "truncation")
_GENERATION_FIELDS = ("max_output_tokens", "service_tier", "store")
_TRANSPORT_CODES = frozenset({
    "request-timeout", "response-too-large", "credential-unavailable", "deadline-unavailable",
    "transport-limits-invalid", "transport-failed",
})


class ProviderCountError(ValueError):
    """Count boundary errors contain codes, never input or provider diagnostics."""


def _parameters() -> dict[str, Any]:
    # Return a fresh fixed contract; caller mutation cannot redefine the profile.
    return {
        "reasoning": {"effort": "none"}, "text": {"verbosity": "medium"},
        "service_tier": "default", "store": False, "tools": [], "tool_choice": "none",
        "truncation": "disabled", "max_output_tokens": 4096,
    }


def counting_profile() -> dict[str, Any]:
    return {
        "id": "task9-openai-responses-input-tokens-v1", "model": MODEL,
        "endpoint": "https://api.openai.com/v1/responses/input_tokens", "method": "POST",
        "counted_fields": list(_COUNT_FIELDS),
        "omitted_generation_fields": list(_GENERATION_FIELDS),
        "fixed_generation_parameters": _parameters(),
        "framing_status": "documented-provider-count-includes-roles-and-boundaries",
        "certification": "request-bound-live-transport-evidence-required",
        "count_is_generation_usage": False,
        "timeout_seconds": 10, "max_response_bytes": 4096, "retry_limit": 0,
        "sources": [
            "https://developers.openai.com/api/docs/guides/token-counting",
            ("https://developers.openai.com/api/reference/resources/responses/subresources/"
             "input_tokens/methods/count"),
            "https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens",
        ],
    }


def build_count_payload(full_generation_payload: dict[str, Any]) -> dict[str, Any]:
    """Project the exact fixed Task 9 request, refusing unknown or changed fields."""
    try:
        if (
            type(full_generation_payload) is not dict
            or set(full_generation_payload) != set(_COUNT_FIELDS + _GENERATION_FIELDS)
            or type(full_generation_payload["model"]) is not str
            or full_generation_payload["model"] != MODEL
            or type(full_generation_payload["instructions"]) is not str
            or type(full_generation_payload["input"]) is not list
            or not full_generation_payload["input"]
        ):
            raise ValueError("shape")
        full_generation_payload["instructions"].encode("utf-8")
        for message in full_generation_payload["input"]:
            if (
                type(message) is not dict or set(message) != {"role", "content"}
                or type(message["role"]) is not str
                or message["role"] not in ("user", "assistant")
                or type(message["content"]) is not str
            ):
                raise ValueError("message")
            message["content"].encode("utf-8")
        for key, expected in _parameters().items():
            value = full_generation_payload[key]
            if type(value) is not type(expected) or json.dumps(
                value, sort_keys=True, allow_nan=False
            ) != json.dumps(expected, sort_keys=True, allow_nan=False):
                raise ValueError("parameter")
        return {key: copy.deepcopy(full_generation_payload[key]) for key in _COUNT_FIELDS}
    except Exception:  # noqa: BLE001 - request values must not enter diagnostics
        raise ProviderCountError("count-request-invalid") from None


def _identity(transport: Transport) -> tuple[bool, str, str]:
    try:
        mode = transport.is_live
        account, project = (getattr(transport, name) for name in ("account_id", "project_id"))
        if type(mode) is not bool or any(
            type(value) is not str
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}", value) is None
            or redact_object(value) != value for value in (account, project)
        ):
            raise ValueError("identity")
        return mode, account, project
    except Exception:  # noqa: BLE001 - independent transport metadata is untrusted
        raise ProviderCountError("count-identity-invalid") from None


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


def _valid_response(value: Any) -> bool:
    return (
        type(value) is dict and set(value) == {"object", "input_tokens"}
        and value["object"] == "response.input_tokens"
        and type(value["input_tokens"]) is int and value["input_tokens"] > 0
    )


def _valid_request_id(value: Any) -> bool:
    return (type(value) is str and bool(value.strip()) and len(value) <= 256
            and not any(ord(character) < 32 or ord(character) == 127 for character in value))


class ProviderInputCounter:
    """Count a strict request once; the guard owns authorization and attempt limits."""

    __slots__ = ("_identity", "_profile_sha256", "_transport")
    _transport: Transport
    _identity: tuple[bool, str, str]
    _profile_sha256: str

    def __init__(self, transport: Transport) -> None:
        if isinstance(transport, HTTPTransport) and not isinstance(transport, HTTPCountTransport):
            raise ProviderCountError("count-identity-invalid")
        object.__setattr__(self, "_transport", transport)
        object.__setattr__(self, "_identity", _identity(transport))
        object.__setattr__(self, "_profile_sha256", canonical_digest(counting_profile()))

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("counter-configuration-immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("counter-configuration-immutable")

    @property
    def provider_counting(self) -> bool:
        return True

    @property
    def is_live(self) -> bool:
        return self._identity[0]

    @property
    def account_id(self) -> str:
        return self._identity[1]

    @property
    def project_id(self) -> str:
        return self._identity[2]

    @property
    def profile_sha256(self) -> str:
        return self._profile_sha256

    def bound(self, payload: dict[str, Any]) -> InputBound:
        count_payload = build_count_payload(payload)
        if _identity(self._transport) != self._identity:
            raise ProviderCountError("count-identity-invalid")
        request_sha256 = canonical_digest(payload)
        count_request_sha256 = canonical_digest(count_payload)
        try:
            reply = self._transport.send(count_payload, timeout_seconds=10, max_output_bytes=4096)
            if (canonical_digest(payload) != request_sha256
                    or canonical_digest(count_payload) != count_request_sha256):
                raise ProviderCountError("count-request-invalid")
            if _identity(self._transport) != self._identity:
                raise ProviderCountError("count-identity-invalid")
            if type(reply.status) is not int or reply.status != 200:
                raise ProviderCountError("count-http-status")
            if type(reply.body) is not bytes:
                raise ProviderCountError("count-json-invalid")
            if len(reply.body) > 4096:
                raise ProviderCountError("count-response-too-large")
            if not _valid_request_id(reply.request_id):
                raise ProviderCountError("count-metadata-invalid")
            try:
                data = json.loads(
                    reply.body.decode("utf-8"), object_pairs_hook=_unique_object,
                    parse_float=_finite_float, parse_constant=_invalid_constant,
                )
            except (ValueError, TypeError, UnicodeError, RecursionError):
                raise ProviderCountError("count-json-invalid") from None
            if not _valid_response(data):
                raise ProviderCountError("count-response-invalid")
            redacted = redact_object(reply.redact(data))
            request_id = redact_object(reply.redact(reply.request_id))
            if not _valid_response(redacted) or redacted != data:
                raise ProviderCountError("count-response-invalid")
            if not _valid_request_id(request_id):
                raise ProviderCountError("count-metadata-invalid")
            response_json = json.dumps(redacted, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=False, allow_nan=False)
            evidence = ProviderCountEvidence(
                requested_model=MODEL, count_request_sha256=count_request_sha256,
                account_id=self.account_id, project_id=self.project_id, request_id=request_id,
                http_status=200, response_json=response_json,
                response_sha256=hashlib.sha256(response_json.encode("utf-8")).hexdigest(),
                counted_at=datetime.now(UTC),
            )
            return InputBound(
                tokens=data["input_tokens"], request_sha256=request_sha256,
                profile_sha256=self.profile_sha256, certified_for_live=self.is_live,
                provider_evidence=evidence,
            )
        except ProviderCountError:
            raise
        except TransportError as error:
            code = str(error) if str(error) in _TRANSPORT_CODES else "transport-failed"
            raise ProviderCountError(code) from None
        except Exception:  # noqa: BLE001 - never expose provider/transport exception values
            raise ProviderCountError("transport-failed") from None
