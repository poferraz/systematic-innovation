"""Provider counting uses synthetic replies and never calls the provider."""
from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
from datetime import timedelta

import pytest

from systematic_innovation_bench.runtime import canonical_digest
from task9.transport import HTTPReply, HTTPTransport, TransportError

MODEL = "gpt-5.4-mini-2026-03-17"


def api():
    assert importlib.util.find_spec("task9.counting") is not None, "count-only adapter missing"
    return importlib.import_module("task9.counting")


def payload():
    return {
        "model": MODEL, "instructions": "all instructions  \nincluding café and 漢字",
        "input": [
            {"role": "user", "content": "initial request  \n"},
            {"role": "assistant", "content": "all prior assistant output"},
            {"role": "user", "content": "every fixed disclosure  \n"},
        ],
        "reasoning": {"effort": "none"}, "text": {"verbosity": "medium"},
        "service_tier": "default", "store": False, "tools": [], "tool_choice": "none",
        "truncation": "disabled", "max_output_tokens": 4096,
    }


class FixtureTransport:
    is_live = False
    account_id = "account-a"
    project_id = "proj_a"

    def __init__(self, body=b'{"object":"response.input_tokens","input_tokens":123}',
                 *, status=200, request_id="req_count_1", redact=lambda value: value):
        self.body, self.status, self.request_id = body, status, request_id
        self.redact = redact
        self.payloads = []

    def send(self, request, *, timeout_seconds, max_output_bytes):
        self.payloads.append(copy.deepcopy(request))
        assert (timeout_seconds, max_output_bytes) == (10, 4096)
        if isinstance(self.body, Exception):
            raise self.body
        return HTTPReply(self.body, self.status, self.request_id, self.redact)


def test_projection_preserves_all_input_and_omits_only_fixed_generation_fields():
    original = payload()
    projected = api().build_count_payload(original)
    assert projected == {
        "model": MODEL, "instructions": "all instructions  \nincluding café and 漢字",
        "input": [
            {"role": "user", "content": "initial request  \n"},
            {"role": "assistant", "content": "all prior assistant output"},
            {"role": "user", "content": "every fixed disclosure  \n"},
        ],
        "reasoning": {"effort": "none"}, "text": {"verbosity": "medium"},
        "tools": [], "tool_choice": "none", "truncation": "disabled",
    }
    projected["input"][0]["content"] = "caller mutation"
    projected["reasoning"]["effort"] = "high"
    assert original == payload()


@pytest.mark.parametrize("update", [
    {"model": "gpt-5.4-mini"}, {"instructions": None}, {"instructions": "\ud800"},
    {"input": []}, {"input": "request"}, {"input": [{"role": "system", "content": "x"}]},
    {"input": [{"role": "user", "content": 1}]},
    {"input": [{"role": "user", "content": "x", "phase": "final_answer"}]},
    {"input": [{"role": "assistant", "content": [{"type": "input_text", "text": "x"}]}]},
    {"reasoning": {"effort": "low"}}, {"reasoning": {"effort": "none", "summary": "auto"}},
    {"text": {"verbosity": "high"}}, {"text": {"verbosity": "medium", "format": {"type": "text"}}},
    {"tools": [{"type": "web_search"}]}, {"tools": ()}, {"tool_choice": "auto"},
    {"truncation": "auto"}, {"store": True}, {"store": 0}, {"service_tier": "priority"},
    {"max_output_tokens": 4096.0}, {"max_output_tokens": 4097},
    {"temperature": 0}, {"previous_response_id": "resp_1"}, {"conversation": "conv_1"},
    {"unsafe": float("nan")},
])
def test_changed_or_unknown_fields_fail_before_count_transport(update):
    transport = FixtureTransport()
    counter = api().ProviderInputCounter(transport)
    with pytest.raises(api().ProviderCountError, match="^count-request-invalid$"):
        counter.bound(payload() | update)
    assert transport.payloads == []


@pytest.mark.parametrize("missing", list(payload()))
def test_missing_payload_fields_cannot_silently_disappear(missing):
    request = payload()
    del request[missing]
    with pytest.raises(api().ProviderCountError, match="^count-request-invalid$"):
        api().build_count_payload(request)


def test_fixture_count_binds_both_requests_and_retains_canonical_provider_evidence():
    transport = FixtureTransport()
    counter = api().ProviderInputCounter(transport)
    bound = counter.bound(payload())
    assert bound.tokens == 123
    assert bound.certified_for_live is False
    assert bound.request_sha256 == canonical_digest(payload())
    assert bound.profile_sha256 == counter.profile_sha256 == canonical_digest(api().counting_profile())
    evidence = bound.provider_evidence
    assert evidence is not None
    assert evidence.requested_model == MODEL
    assert evidence.count_request_sha256 == canonical_digest(transport.payloads[0])
    assert evidence.count_request_sha256 != bound.request_sha256
    assert (evidence.account_id, evidence.project_id) == ("account-a", "proj_a")
    assert evidence.request_id == "req_count_1"
    assert evidence.http_status == 200
    assert evidence.response_json == '{"input_tokens":123,"object":"response.input_tokens"}'
    assert evidence.response_sha256 == hashlib.sha256(evidence.response_json.encode()).hexdigest()
    assert evidence.counted_at.utcoffset() == timedelta(0)
    assert len(transport.payloads) == 1
    assert counter.provider_counting is True
    assert counter.is_live is False


def test_counter_mode_and_identity_come_only_from_independent_transport():
    transport = FixtureTransport()
    transport.is_live = True  # A synthetic mode test: send still uses only this in-memory fixture.
    counter = api().ProviderInputCounter(transport)
    assert counter.bound(payload()).certified_for_live is True
    for name, value in (("is_live", False), ("account_id", "other"),
                        ("project_id", "proj_other"), ("provider_counting", False),
                        ("profile_sha256", "0" * 64)):
        with pytest.raises(AttributeError):
            setattr(counter, name, value)
    transport.account_id = "changed-after-configuration"
    with pytest.raises(api().ProviderCountError, match="^count-identity-invalid$"):
        counter.bound(payload())
    assert len(transport.payloads) == 1


@pytest.mark.parametrize("name,value", [("is_live", 1), ("account_id", ""),
                                        ("project_id", "bad\nidentity")])
def test_missing_or_unsafe_transport_identity_fails_without_send(name, value):
    transport = FixtureTransport()
    setattr(transport, name, value)
    with pytest.raises(api().ProviderCountError, match="^count-identity-invalid$"):
        api().ProviderInputCounter(transport)
    assert transport.payloads == []


@pytest.mark.parametrize("body,code", [
    (b"not-json credential-sentinel", "count-json-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":1,"input_tokens":2}',
     "count-json-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":NaN}', "count-json-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":Infinity}', "count-json-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":1e999}', "count-json-invalid"),
    (b"\xff", "count-json-invalid"), (b"[]", "count-response-invalid"),
    (b'{"object":"response","input_tokens":123}', "count-response-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":true}', "count-response-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":123.0}', "count-response-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":0}', "count-response-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":-1}', "count-response-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":123,"id":"resp_1"}',
     "count-response-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":123,"model":"alias"}',
     "count-response-invalid"),
    (b'{"object":"response.input_tokens","input_tokens":123,"api_key":"sentinel"}',
     "count-response-invalid"),
    (b" " * 4097, "count-response-too-large"),
])
def test_malformed_unsafe_or_oversized_responses_stop_with_code_only_errors(body, code):
    transport = FixtureTransport(body)
    with pytest.raises(api().ProviderCountError, match="^" + code + "$"):
        api().ProviderInputCounter(transport).bound(payload())
    assert len(transport.payloads) == 1


@pytest.mark.parametrize("status", [True, 200.0, 201, 301, 401, 429, 503])
def test_count_requires_exact_200_and_never_follows_or_retries(status):
    transport = FixtureTransport(status=status)
    with pytest.raises(api().ProviderCountError, match="^count-http-status$"):
        api().ProviderInputCounter(transport).bound(payload())
    assert len(transport.payloads) == 1


@pytest.mark.parametrize("request_id", [None, "", "  ", "r" * 257, "unsafe\r\nheader"])
def test_count_requires_nonblank_bounded_safe_request_id(request_id):
    transport = FixtureTransport(request_id=request_id)
    with pytest.raises(api().ProviderCountError, match="^count-metadata-invalid$"):
        api().ProviderInputCounter(transport).bound(payload())


def test_transport_secret_redaction_is_applied_before_retaining_request_identity():
    transport = FixtureTransport(request_id="req credential-sentinel", redact=lambda value:
                                 value.replace("credential-sentinel", "[REDACTED]")
                                 if isinstance(value, str) else value)
    evidence = api().ProviderInputCounter(transport).bound(payload()).provider_evidence
    assert evidence.request_id == "req [REDACTED]"
    assert "credential-sentinel" not in evidence.model_dump_json()


@pytest.mark.parametrize("failure,code", [
    (TransportError("request-timeout"), "request-timeout"),
    (TransportError("response-too-large"), "response-too-large"),
    (TransportError("credential-sentinel"), "transport-failed"),
    (RuntimeError("credential-sentinel"), "transport-failed"),
])
def test_transport_exceptions_are_terminal_and_do_not_reveal_details(failure, code):
    transport = FixtureTransport(failure)
    with pytest.raises(api().ProviderCountError, match="^" + code + "$"):
        api().ProviderInputCounter(transport).bound(payload())
    assert len(transport.payloads) == 1


def test_count_above_guard_ceiling_is_preserved_for_guard_to_refuse():
    # The counter proves the count; only the guard owns the 32,768 input ceiling.
    transport = FixtureTransport(b'{"object":"response.input_tokens","input_tokens":32769}')
    assert api().ProviderInputCounter(transport).bound(payload()).tokens == 32769


def test_each_changed_instruction_disclosure_or_prior_turn_changes_both_bindings():
    counter = api().ProviderInputCounter(FixtureTransport())
    baseline = counter.bound(payload())
    for field in ("instructions", "prior", "disclosure"):
        request = payload()
        if field == "instructions":
            request["instructions"] += " changed"
        else:
            request["input"][1 if field == "prior" else 2]["content"] += " changed"
        updated = counter.bound(request)
        assert updated.request_sha256 != baseline.request_sha256
        assert updated.provider_evidence.count_request_sha256 != (
            baseline.provider_evidence.count_request_sha256)


def test_generation_transport_cannot_be_misconfigured_as_the_provider_counter():
    transport = HTTPTransport(account_id="account-a", project_id="proj_a")
    with pytest.raises(api().ProviderCountError, match="^count-identity-invalid$"):
        api().ProviderInputCounter(transport)


@pytest.mark.parametrize("changed", ["count_projection", "generation_request"])
def test_mutation_during_send_cannot_bind_a_count_to_different_input(changed):
    original = payload()

    class MutatingTransport(FixtureTransport):
        def send(self, request, **kwargs):
            response = super().send(request, **kwargs)
            target = request if changed == "count_projection" else original
            target["input"][0]["content"] = "altered after counting"
            return response

    with pytest.raises(api().ProviderCountError, match="^count-request-invalid$"):
        api().ProviderInputCounter(MutatingTransport()).bound(original)


def test_counter_configuration_cannot_be_deleted():
    counter = api().ProviderInputCounter(FixtureTransport())
    with pytest.raises(AttributeError):
        del counter._identity
    assert (counter.account_id, counter.project_id) == ("account-a", "proj_a")
