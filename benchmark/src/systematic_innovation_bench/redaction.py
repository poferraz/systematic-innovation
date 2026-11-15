"""Credential redaction before any canonical evidence persistence."""

import re
from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
_HEADERS = re.compile(r"(?i)\bauthorization\s*[\"']?\s*:\s*[\"']?(?:bearer|basic)\s+[^\s\"',;]+")
_BEARER = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{16,}={0,2}")
_CREDENTIAL_KEYS = frozenset(
    {
        "authorization",
        "api_key",
        "access_token",
        "auth_token",
        "secret_key",
        "client_secret",
        "password",
        "private_key",
        "bearer_token",
    }
)
_URL_CREDENTIALS = re.compile(r"(?i)(https?://)[^/@\s]+@")
_ASSIGNMENTS = re.compile(
    r"""(?ix)(\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|secret[_-]?key|client[_-]?secret|password)\b[\"']?\s*[=:]\s*)(?:"[^"\n]*"|'[^'\n]*'|[^\s,;}]+)"""
)
_TOKEN = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[po]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})\b"
)
_PEM = re.compile(
    r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----.*?-----END (?:[A-Z ]+ )?PRIVATE KEY-----", re.DOTALL
)


def redact_text(text: str, secret_values: Sequence[str] = ()) -> str:
    for secret in sorted(set(secret_values), key=len, reverse=True):
        if secret:
            text = text.replace(secret, "[REDACTED]")
    text = _PEM.sub("[REDACTED]", text)
    text = _URL_CREDENTIALS.sub(r"\1[REDACTED]@", text)
    text = _HEADERS.sub("[REDACTED]", text)
    text = _BEARER.sub("[REDACTED]", text)
    text = _ASSIGNMENTS.sub(r"\1[REDACTED]", text)
    return _TOKEN.sub("[REDACTED]", text)


def redact_object(value: Any, secret_values: Sequence[str] = ()) -> Any:
    if isinstance(value, str):
        return redact_text(value, secret_values)
    if isinstance(value, dict):
        return {
            redact_text(key, secret_values) if isinstance(key, str) else key: "[REDACTED]"
            if isinstance(key, str) and key.lower().replace("-", "_") in _CREDENTIAL_KEYS
            else redact_object(item, secret_values)
            for key, item in value.items()
        }
    if isinstance(value, (tuple, list)):
        return [redact_object(item, secret_values) for item in value]
    return value


def redact_model(record: T, secret_values: Sequence[str] = ()) -> T:
    payload = redact_object(record.model_dump(mode="json"), secret_values)
    if "prompt_sha256" in type(record).model_fields and payload.get("prompt") != getattr(
        record, "prompt", None
    ):
        payload["prompt_sha256"] = ""
    try:
        return type(record).model_validate(payload)
    except ValueError:
        raise ValueError("credential redaction invalidated record identity") from None
