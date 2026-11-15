"""Allowlisted argument-array subprocess adapter with bounded pipe capture."""

import os
import selectors
import shutil
import signal
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path

from ..models import TurnJob, TurnResponse
from ..redaction import redact_model, redact_text
from ..store import append_record


def _executable(name: str) -> str:
    resolved = shutil.which(name) if not os.path.isabs(name) else name
    if not resolved or not Path(resolved).is_file():
        raise ValueError("adapter executable is unavailable")
    return str(Path(resolved).resolve())


class SubprocessAdapter:
    def __init__(
        self,
        command: tuple[str, ...],
        allowed_executables: frozenset[str],
        timeout_seconds: float,
        *,
        environment_allowlist: frozenset[str] = frozenset(),
        secret_values: Sequence[str] = (),
        max_output_bytes: int = 1048576,
        canonical_path: Path | None = None,
    ) -> None:
        if not command or timeout_seconds <= 0 or max_output_bytes < 1:
            raise ValueError("invalid subprocess boundaries")
        executable = _executable(command[0])
        if executable not in {_executable(item) for item in allowed_executables}:
            raise ValueError("adapter executable is outside allowlist")
        self.command = (executable, *command[1:])
        self.timeout_seconds = timeout_seconds
        self.environment_allowlist = environment_allowlist
        self.secret_values = tuple(secret_values)
        self.max_output_bytes = max_output_bytes
        self.canonical_path = canonical_path

    def _capture(self, payload: bytes) -> tuple[int, bytes, bytes, str | None, float]:
        started = time.monotonic()
        environment = {
            key: os.environ[key] for key in self.environment_allowlist if key in os.environ
        }
        process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=environment,
            start_new_session=True,
        )
        assert (
            process.stdin is not None and process.stdout is not None and process.stderr is not None
        )
        output = bytearray()
        errors = bytearray()
        offset = 0
        failure = None
        try:
            with selectors.DefaultSelector() as selector:
                for pipe, label, event in (
                    (process.stdin, "input", selectors.EVENT_WRITE),
                    (process.stdout, "output", selectors.EVENT_READ),
                    (process.stderr, "error", selectors.EVENT_READ),
                ):
                    os.set_blocking(pipe.fileno(), False)
                    selector.register(pipe, event, label)
                while selector.get_map():
                    remaining = self.timeout_seconds - (time.monotonic() - started)
                    if remaining <= 0:
                        failure = "adapter timeout"
                        break
                    for key, _ in selector.select(min(remaining, 0.1)):
                        if key.data == "input":
                            try:
                                offset += os.write(key.fd, payload[offset : offset + 65536])
                            except BrokenPipeError:
                                offset = len(payload)
                            if offset >= len(payload):
                                selector.unregister(key.fileobj)
                                process.stdin.close()
                        else:
                            chunk = os.read(key.fd, 65536)
                            if not chunk:
                                selector.unregister(key.fileobj)
                                continue
                            available = self.max_output_bytes - len(output) - len(errors)
                            target = output if key.data == "output" else errors
                            target.extend(chunk[:available])
                            if len(chunk) > available:
                                failure = "adapter output limit exceeded"
                                break
                    if failure:
                        break
            if failure:
                os.killpg(process.pid, signal.SIGKILL)
            try:
                code = process.wait(
                    timeout=max(0.01, self.timeout_seconds - (time.monotonic() - started))
                )
            except subprocess.TimeoutExpired:
                failure = "adapter timeout"
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
            return code, bytes(output), bytes(errors), failure, time.monotonic() - started
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            for pipe in (process.stdin, process.stdout, process.stderr):
                pipe.close()

    def run_turn(self, job: TurnJob) -> TurnResponse:
        safe_job = redact_model(job, self.secret_values)
        try:
            code, output, errors, failure, latency = self._capture(
                safe_job.model_dump_json().encode()
            )
            raw = redact_text(
                (output + errors).decode("utf-8", errors="replace"), self.secret_values
            )
            raw = raw.encode()[: self.max_output_bytes].decode("utf-8", errors="ignore")
            if failure or code:
                result = TurnResponse(
                    job_id=job.job_id,
                    turn_index=job.assistant_turn_index,
                    attempt=job.attempt,
                    content="",
                    status="failed",
                    raw_response=raw,
                    error=failure or "adapter exited nonzero",
                    latency_seconds=latency,
                )
            else:
                try:
                    result = TurnResponse.model_validate_json(output)
                    if (
                        result.job_id != job.job_id
                        or result.turn_index != job.assistant_turn_index
                        or result.attempt != job.attempt
                    ):
                        raise ValueError("adapter response correlation mismatch")
                    if result.status == "succeeded" and not result.content.strip():
                        raise ValueError("empty adapter response")
                    result = TurnResponse.model_validate(
                        result.model_dump()
                        | {
                            "raw_response": raw,
                            "latency_seconds": result.latency_seconds
                            if result.latency_seconds is not None
                            else latency,
                        }
                    )
                except ValueError:
                    result = TurnResponse(
                        job_id=job.job_id,
                        turn_index=job.assistant_turn_index,
                        attempt=job.attempt,
                        content="",
                        status="failed",
                        raw_response=raw,
                        error="invalid adapter response",
                        latency_seconds=latency,
                    )
        except OSError:
            result = TurnResponse(
                job_id=job.job_id,
                turn_index=job.assistant_turn_index,
                attempt=job.attempt,
                content="",
                status="failed",
                error="adapter launch failed",
            )
        result = redact_model(result, self.secret_values)
        if self.canonical_path is not None:
            append_record(self.canonical_path, result, secret_values=self.secret_values)
        return result
