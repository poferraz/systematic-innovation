"""Offline-only input accounting; current framing is explicitly uncertified.

The pinned local tokenizer counts text exactly for its encoding. Provider framing
is not publicly proven for the selected Responses snapshot: the provisional
framing allowance is an estimate, never provider usage or a live-safe guarantee.
There is deliberately no API to certify this profile by supplying a boolean.
"""
from __future__ import annotations

import base64
import hashlib
import importlib.metadata
import json
from pathlib import Path
from typing import Any

from systematic_innovation_bench.runtime import canonical_digest

from .contracts import InputBound

RESOURCE_SHA256 = "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d"
# Exact o200k_base pattern from OpenAI tiktoken0.14.0 openai_public.py.
# https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py
_PATTERN = "|".join([  # noqa: FLY002 - preserve the pinned official regex fragments
    r"[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]*[\p{Ll}\p{Lm}\p{Lo}\p{M}]+(?i:'s|'t|'re|'ve|'m|'ll|'d)?",
    r"[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]+[\p{Ll}\p{Lm}\p{Lo}\p{M}]*(?i:'s|'t|'re|'ve|'m|'ll|'d)?",
    r"\p{N}{1,3}", r" ?[^\s\p{L}\p{N}]+[\r\n/]*", r"\s*[\r\n]+", r"\s+(?!\S)", r"\s+",
])


class TokenCountError(ValueError):
    """No exception text from resource paths, input text, or dependencies escapes."""


def input_profile() -> dict[str, Any]:
    return {
        "id": "task9-o200k-responses-unreviewed-v1",
        "model": "gpt-5.4-mini-2026-03-17", "tokenizer": "tiktoken", "version": "0.14.0",
        "encoding": "o200k_base", "encoding_resource_sha256": RESOURCE_SHA256,
        "encoding_pattern_sha256": hashlib.sha256(_PATTERN.encode()).hexdigest(),
        "counted_text": "instructions + every transcript role and content + parameter JSON",
        "framing_status": "unreviewed-no-live-certification",
        "fixed_framing_allowance": 256, "per_message_framing_allowance": 64,
        "certified_for_live": False, "local_count_is_provider_usage": False,
    }


def _load_local_encoding(resource_path: Path) -> Any:
    # Read and hash bytes ourselves. tiktoken.get_encoding/load_tiktoken_bpe can
    # fetch missing or corrupt caches, so neither is used here.
    try:
        with resource_path.open("rb") as handle:
            data = handle.read(8 * 1024 * 1024 + 1)
    except OSError:
        raise TokenCountError("tokenizer-resource-unavailable") from None
    if len(data) > 8 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != RESOURCE_SHA256:
        raise TokenCountError("tokenizer-resource-mismatch")
    try:
        if importlib.metadata.version("tiktoken") != "0.14.0":
            raise TokenCountError("tokenizer-version-mismatch")
        import tiktoken

        ranks = {}
        for line in data.splitlines():
            token, rank = line.split()
            ranks[base64.b64decode(token, validate=True)] = int(rank)
        return tiktoken.Encoding(
            name="o200k_base", pat_str=_PATTERN, mergeable_ranks=ranks,
            special_tokens={"<|endoftext|>": 199999, "<|endofprompt|>": 200018},
        )
    except TokenCountError:
        raise
    except Exception:  # noqa: BLE001 - sanitize untrusted boundary exceptions
        raise TokenCountError("tokenizer-unavailable") from None


class LocalInputCounter:
    """Pinned offline tokenizer plus an explicitly unreviewed framing estimate."""

    certified_for_live = False

    def __init__(self, resource_path: Path) -> None:
        self._encoding = _load_local_encoding(resource_path)
        self.profile_sha256 = canonical_digest(input_profile())

    def bound(self, payload: dict[str, Any]) -> InputBound:
        try:
            instructions = payload["instructions"]
            messages = payload["input"]
            if not isinstance(instructions, str) or not isinstance(messages, list) or not messages:
                raise ValueError("input")
            texts = [instructions]
            for message in messages:
                if (
                    not isinstance(message, dict) or set(message) != {"role", "content"}
                    or message["role"] not in ("user", "assistant")
                    or not isinstance(message["content"], str)
                ):
                    raise ValueError("message")
                texts.extend((message["role"], message["content"]))
            metadata = {key: value for key, value in payload.items()
                        if key not in ("instructions", "input")}
            texts.append(json.dumps(metadata, sort_keys=True, separators=(",", ":"), allow_nan=False))
            for text in texts:
                text.encode("utf-8")
            tokens = 256 + 64 * len(messages)
            tokens += sum(len(self._encoding.encode_ordinary(text)) for text in texts)
            return InputBound(
                tokens=tokens, profile_sha256=self.profile_sha256, certified_for_live=False,
                request_sha256=canonical_digest(payload),
            )
        except Exception:  # noqa: BLE001 - sanitize untrusted boundary exceptions
            raise TokenCountError("input-count-invalid") from None
