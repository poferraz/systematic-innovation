"""Local tokenizer tests never fetch a vocabulary or make provider calls."""
import copy
from pathlib import Path

import pytest
import tiktoken

from systematic_innovation_bench.runtime import canonical_digest
from task9.contracts import InputBound
from task9.tokens import LocalInputCounter, TokenCountError, input_profile
from task9.worker import PARAMETERS


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("token counter attempted network")
    monkeypatch.setattr("socket.create_connection", forbidden)


def payload():
    return {"model": "gpt-5.4-mini-2026-03-17", "instructions": "aaaa",
            "input": [{"role": "user", "content": "aaaa"}], **copy.deepcopy(PARAMETERS)}


def tiny_encoding():
    # Actual tiktoken engine, with a tiny local BPE fixture. No provider vocabulary.
    return tiktoken.Encoding(
        name="offline-fixture", pat_str=r"[\s\S]+",
        mergeable_ranks={**{bytes([n]): n for n in range(256)}, b"aa": 256, b"aaaa": 257},
        special_tokens={},
    )


def counter(monkeypatch):
    monkeypatch.setattr("task9.tokens._load_local_encoding", lambda path: tiny_encoding())
    return LocalInputCounter(Path("offline-fixture-vocab"))


def test_bound_counts_all_text_roles_parameters_and_framing_and_binds_request(monkeypatch):
    estimator = counter(monkeypatch)
    bound = estimator.bound(payload())
    assert isinstance(bound, InputBound)
    assert bound.certified_for_live is False
    assert bound.profile_sha256 == canonical_digest(input_profile())
    assert bound.request_sha256 == canonical_digest(payload())
    # 2 content tokens, 4 role bytes, 256 fixed + 64 per-message framing,
    # plus all 215 bytes in the declared parameter metadata for this tiny BPE.
    assert bound.tokens == 541
    assert input_profile()["framing_status"] == "unreviewed-no-live-certification"
    assert input_profile()["local_count_is_provider_usage"] is False


def test_full_pack_sized_text_is_not_rejected_by_a_byte_only_estimate(monkeypatch):
    request = payload()
    request["instructions"] = "a" * 40412
    bound = counter(monkeypatch).bound(request)
    assert len(request["instructions"].encode()) > 32768
    assert bound.tokens < 32768
    assert bound.certified_for_live is False


def test_previous_assistant_and_every_disclosure_change_count_and_digest(monkeypatch):
    estimator = counter(monkeypatch)
    first = estimator.bound(payload())
    changed = payload()
    changed["input"].extend([
        {"role": "assistant", "content": "abcdefgh"},
        {"role": "user", "content": "ijklmnop"},
    ])
    later = estimator.bound(changed)
    assert later.tokens == first.tokens + 157
    assert later.request_sha256 != first.request_sha256


def test_missing_resource_fails_before_any_tiktoken_encoding_lookup(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("get_encoding may download")
    monkeypatch.setattr(tiktoken, "get_encoding", forbidden)
    with pytest.raises(TokenCountError, match="^tokenizer-resource-unavailable$"):
        LocalInputCounter(tmp_path / "missing")


def test_wrong_resource_hash_is_refused_without_loading_or_deleting_it(tmp_path, monkeypatch):
    resource = tmp_path / "vocab"
    resource.write_bytes(b"untrusted fixture encoding")
    def forbidden(*args, **kwargs):
        raise AssertionError("get_encoding may download")
    monkeypatch.setattr(tiktoken, "get_encoding", forbidden)
    with pytest.raises(TokenCountError, match="^tokenizer-resource-mismatch$"):
        LocalInputCounter(resource)
    assert resource.read_bytes() == b"untrusted fixture encoding"


@pytest.mark.parametrize("change", [
    {"instructions": None}, {"input": []},
    {"input": [{"role": "developer", "content": "bad"}]},
    {"input": [{"role": "user", "content": 1}]},
    {"temperature": float("nan")},
])
def test_uncountable_or_malformed_inputs_fail_closed(monkeypatch, change):
    with pytest.raises(TokenCountError, match="^input-count-invalid$"):
        counter(monkeypatch).bound(payload() | change)
