"""Pinned direct HTTPS transport; no SDK, redirects, proxies, or retries.

The total deadline uses POSIX interval timers, including DNS and headers. A host
without that facility, a non-main thread, or an existing alarm is refused.
"""
from __future__ import annotations

import http.client
import json
import math
import os
import re
import signal
import ssl
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Protocol

from systematic_innovation_bench.redaction import redact_object


class TransportError(ValueError):
    """A deliberately code-only transport failure."""


@dataclass(frozen=True)
class HTTPReply:
    body: bytes = field(repr=False)
    status: int
    request_id: str | None = None
    redact: Callable[[Any], Any] = field(default=redact_object, repr=False, compare=False)


class Transport(Protocol):
    @property
    def is_live(self) -> bool: ...

    def send(
        self, payload: dict[str, Any], *, timeout_seconds: float, max_output_bytes: int
    ) -> HTTPReply: ...


@contextmanager
def _deadline(seconds: float) -> Iterator[None]:
    if (
        threading.current_thread() is not threading.main_thread()
        or not hasattr(signal, "setitimer")
        or signal.getitimer(signal.ITIMER_REAL) != (0.0, 0.0)
    ):
        raise TransportError("deadline-unavailable")
    old = signal.getsignal(signal.SIGALRM)

    def expired(signum: int, frame: Any) -> None:
        raise TransportError("request-timeout")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


class HTTPTransport:
    """One POST to the approved endpoint, with an ephemeral scoped credential."""

    __slots__ = ("_account_id", "_project_id")

    @property
    def is_live(self) -> bool:
        return True

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def project_id(self) -> str:
        return self._project_id

    def __init__(self, *, account_id: str, project_id: str) -> None:
        if not all(re.fullmatch(r"[A-Za-z0-9_-]{1,100}", v) for v in (account_id, project_id)):
            raise TransportError("transport-identity-invalid")
        self._account_id = account_id
        self._project_id = project_id

    def send(
        self, payload: dict[str, Any], *, timeout_seconds: float, max_output_bytes: int
    ) -> HTTPReply:
        if (
            type(timeout_seconds) not in (int, float)
            or not math.isfinite(timeout_seconds)
            or not 0 < timeout_seconds <= 120
            or type(max_output_bytes) is not int
            or not 0 < max_output_bytes <= 1048576
        ):
            raise TransportError("transport-limits-invalid")
        connection = None
        try:
            body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
            context = ssl.create_default_context()
            with _deadline(float(timeout_seconds)):
                # This function is called only inside the durable approval guard.
                secret = os.environ.get("OPENAI_API_KEY", "")
                if not secret or any(c in secret for c in "\r\n"):
                    raise TransportError("credential-unavailable")
                connection = http.client.HTTPSConnection(
                    "api.openai.com", 443, timeout=timeout_seconds, context=context
                )
                started = time.monotonic()
                connection.request(
                    "POST", "/v1/responses", body,
                    {"Authorization": "Bearer " + secret, "OpenAI-Project": self.project_id,
                     "Content-Type": "application/json", "Accept": "application/json"},
                )
                response = connection.getresponse()
                chunks = bytearray()
                while True:
                    if time.monotonic() - started >= timeout_seconds:
                        raise TransportError("request-timeout")
                    chunk = response.read(min(65536, max_output_bytes + 1 - len(chunks)))
                    if not chunk:
                        break
                    chunks.extend(chunk)
                    if len(chunks) > max_output_bytes:
                        raise TransportError("response-too-large")
                request_id = response.getheader("x-request-id")
                if request_id is not None:
                    request_id = redact_object(str(request_id)[:256], (secret,))
                return HTTPReply(
                    body=bytes(chunks), status=response.status, request_id=request_id,
                    redact=lambda value: redact_object(value, (secret,)),
                )
        except TransportError:
            raise
        except TimeoutError:
            raise TransportError("request-timeout") from None
        except Exception:  # noqa: BLE001 - sanitize untrusted boundary exceptions
            raise TransportError("transport-failed") from None
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:  # noqa: BLE001 - sanitize cleanup errors as well
                    raise TransportError("transport-failed") from None
