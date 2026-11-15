"""Responses worker tests use synthetic provider objects and no network."""
import copy
import json

import pytest

from systematic_innovation_bench.models import ConversationTurn, TurnJob
from task9.transport import HTTPReply, TransportError
from task9.worker import Worker, WorkerError, build_payload

MODEL = "gpt-5.4-mini-2026-03-17"
PARAMETERS = {
    "reasoning": {"effort": "none"}, "text": {"verbosity": "medium"},
    "service_tier": "default", "store": False, "tools": [], "tool_choice": "none",
    "truncation": "disabled", "max_output_tokens": 4096,
}


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("offline worker cannot use network")
    monkeypatch.setattr("socket.create_connection", forbidden)


def job(**updates):
    return TurnJob(**({
        "job_id": "opaque-job", "assistant_turn_index": 4, "model": MODEL,
        "system_instructions": "instruction  \nverbatim", "model_parameters": copy.deepcopy(PARAMETERS),
        "transcript": (
            ConversationTurn(turn_index=1, role="user", content="request  \n"),
            ConversationTurn(turn_index=2, role="assistant", content="prior reply"),
            ConversationTurn(turn_index=3, role="user", content="fixed disclosure"),
        ),
    } | updates))


def provider(**updates):
    return {
        "id": "resp_1", "object": "response", "model": MODEL, "service_tier": "default",
        "status": "completed", "error": None, "incomplete_details": None,
        "output": [
            {"id": "msg_1", "type": "message", "status": "completed", "role": "assistant",
             "content": [{"type": "output_text", "text": "first", "annotations": []}]},
            {"id": "msg_2", "type": "message", "status": "completed", "role": "assistant",
             "content": [{"type": "output_text", "text": "second", "annotations": []}]},
        ],
        "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120,
                  "input_tokens_details": {"cached_tokens": 10},
                  "output_tokens_details": {"reasoning_tokens": 5}},
    } | updates


class Counter:
    def bound(self, payload):
        return {"fixture_only": True, "payload": copy.deepcopy(payload)}


class Guard:
    def process(self, job, payload, input_bound, send_callback, *, transport_live):
        assert input_bound["payload"] == payload
        assert transport_live is False
        return send_callback()


class Transport:
    is_live = False
    def __init__(self, value, *, status=200, redact=lambda value: value):
        self.value, self.status, self.redact = value, status, redact
        self.payloads = []
    def send(self, payload, *, timeout_seconds, max_output_bytes):
        self.payloads.append(copy.deepcopy(payload))
        assert timeout_seconds == 120
        assert max_output_bytes == 1048576
        if isinstance(self.value, Exception):
            raise self.value
        body = self.value if isinstance(self.value, bytes) else json.dumps(self.value).encode()
        return HTTPReply(body, self.status, "req_1", self.redact)


def run(value, **kwargs):
    transport = Transport(value, **kwargs)
    return Worker(Guard(), transport, Counter()).process(job()), transport


def test_exact_stateless_payload_and_all_text_usage_cost_metadata():
    result, transport = run(provider())
    assert result.status == "succeeded"
    assert result.content == "first\nsecond"
    assert (result.job_id, result.turn_id, result.turn_index, result.attempt) == (
        "opaque-job", "opaque-job:4:0", 4, 0
    )
    assert (result.input_tokens, result.output_tokens) == (100, 20)
    assert result.cost == pytest.approx(0.000165)
    raw = json.loads(result.raw_response)
    assert raw["provider_response"] == provider()
    assert raw["request_id"] == "req_1"
    assert raw["cost_provenance"]["kind"] == "calculated-token-rate-upper-bound"
    assert raw["cost_provenance"]["output_rate_usd_per_million"] == "4.50"
    assert transport.payloads == [{
        "model": MODEL, "instructions": "instruction  \nverbatim",
        "input": [{"role": "user", "content": "request  \n"},
                  {"role": "assistant", "content": "prior reply"},
                  {"role": "user", "content": "fixed disclosure"}],
        **PARAMETERS,
    }]


def test_refusal_and_text_from_every_assistant_item_are_preserved():
    data = provider()
    data["output"][1]["content"] = [{"type": "refusal", "refusal": "cannot comply"}]
    result, _ = run(data)
    assert result.status == "refused"
    assert result.content == "first\ncannot comply"
    assert result.output_tokens == 20


@pytest.mark.parametrize("update,code", [
    ({"model": "alias"}, "provider-model-mismatch"),
    ({"service_tier": "priority"}, "provider-tier-mismatch"),
    ({"status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"}},
     "provider-not-completed"),
    ({"output": [{"type": "function_call", "name": "bad", "arguments": "{}"}]},
     "provider-output-invalid"),
    ({"output": []}, "provider-content-empty"),
    ({"usage": None}, "provider-usage-invalid"),
    ({"usage": {"input_tokens": True, "output_tokens": 20}}, "provider-usage-invalid"),
    ({"usage": {"input_tokens": 10.0, "output_tokens": 20}}, "provider-usage-invalid"),
    ({"usage": {"input_tokens": 32769, "output_tokens": 20}}, "provider-usage-invalid"),
    ({"usage": {"input_tokens": 100, "output_tokens": 4097}}, "provider-usage-invalid"),
    ({"usage": {"input_tokens": 100, "output_tokens": 0}}, "provider-usage-invalid"),
    ({"usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 121}},
     "provider-usage-invalid"),
])
def test_provider_contract_failures_are_terminal_code_only_with_redacted_raw(update, code):
    result, transport = run(provider(**update))
    assert result.status == "failed"
    assert result.error == code
    assert result.content == ""
    assert len(transport.payloads) == 1
    assert json.loads(result.raw_response)["provider_response"] == provider(**update)


@pytest.mark.parametrize("body,code", [
    (b"not-json secret", "provider-json-invalid"),
    (b'{"status":"completed","status":"failed"}', "provider-json-invalid"),
    (b'{"usage":NaN}', "provider-json-invalid"),
    (b'{"usage":Infinity}', "provider-json-invalid"),
    (b"[]", "provider-json-invalid"),
])
def test_malformed_duplicate_and_nonfinite_json_never_retains_unsafe_bytes(body, code):
    result, _ = run(body)
    assert result.status == "failed"
    assert result.error == code
    assert result.raw_response is None


@pytest.mark.parametrize("failure,code", [
    (TransportError("request-timeout"), "request-timeout"),
    (TransportError("response-too-large"), "response-too-large"),
    (RuntimeError("secret-provider-diagnostic"), "transport-failed"),
])
def test_transport_failure_has_no_exception_text_and_no_resubmit(failure, code):
    result, transport = run(failure)
    assert result.status == "failed"
    assert result.error == code
    assert "secret-provider-diagnostic" not in result.model_dump_json()
    assert len(transport.payloads) == 1


def test_non_200_does_not_interpret_success_body():
    result, transport = run(provider(), status=429)
    assert result.status == "failed"
    assert result.error == "provider-http-status"
    assert json.loads(result.raw_response)["http_status"] == 429
    assert len(transport.payloads) == 1


def test_redaction_precedes_return_for_content_raw_and_request_id():
    secret = "fixture-credential-sentinel"
    data = provider()
    data["output"][0]["content"][0]["text"] = secret
    data["metadata"] = {"api_key": secret}
    def redact(value):
        return json.loads(json.dumps(value).replace(secret, "[REDACTED]"))
    result, _ = run(data, redact=redact)
    assert secret not in result.model_dump_json()
    assert result.content == "[REDACTED]\nsecond"
    assert json.loads(result.raw_response)["provider_response"]["metadata"] == {
        "api_key": "[REDACTED]"
    }


@pytest.mark.parametrize("updates", [
    {"model": "other"}, {"attempt": 1}, {"host": "other"},
    {"model_parameters": PARAMETERS | {"temperature": 0.7}},
    {"model_parameters": PARAMETERS | {"max_output_tokens": 4097}},
    {"model_parameters": PARAMETERS | {"store": True}},
])
def test_undeclared_job_or_sampling_changes_fail_before_transport(updates):
    client = Transport(provider())
    with pytest.raises(WorkerError, match="^request-contract-invalid$"):
        Worker(Guard(), client, Counter()).process(job(**updates))
    assert client.payloads == []


def test_payload_builder_returns_an_independent_exact_copy():
    incoming = job()
    payload = build_payload(incoming)
    payload["reasoning"]["effort"] = "high"
    assert incoming.model_parameters["reasoning"]["effort"] == "none"


def test_reasoning_item_before_assistant_does_not_hide_text_or_double_count_tokens():
    data = provider()
    data["output"].insert(0, {"type": "reasoning", "id": "rs_1", "summary": []})
    result, _ = run(data)
    assert result.status == "succeeded"
    assert result.content == "first\nsecond"
    assert result.output_tokens == 20
    assert result.cost == pytest.approx(0.000165)
    assert json.loads(result.raw_response)["provider_response"]["output"][0] == {
        "type": "reasoning", "id": "rs_1", "summary": []
    }


@pytest.mark.parametrize("reasoning", [
    {"type": "reasoning", "summary": "bad"},
    {"type": "reasoning", "summary": [{"type": "tool_call", "text": "bad"}]},
    {"type": "reasoning", "summary": [], "status": "incomplete"},
])
def test_malformed_or_incomplete_reasoning_items_fail_closed(reasoning):
    data = provider()
    data["output"].insert(0, reasoning)
    result, _ = run(data)
    assert result.status == "failed"
    assert result.error == "provider-output-invalid"


@pytest.mark.parametrize("update", [
    {"unknown_billable_count": 20},
    {"output_tokens_details": {"reasoning_tokens": True}},
    {"input_tokens_details": {"cached_tokens": 101}},
    {"input_tokens_details": {"cached_tokens": -1}},
])
def test_usage_unknown_fields_or_invalid_breakdowns_fail_closed(update):
    data = provider()
    data["usage"].update(update)
    result, _ = run(data)
    assert result.status == "failed"
    assert result.error == "provider-usage-invalid"


def test_json_numeric_overflow_is_rejected_without_raw_unsafe_bytes():
    result, _ = run(b'{"usage":1e999}')
    assert result.status == "failed"
    assert result.error == "provider-json-invalid"
    assert result.raw_response is None


@pytest.mark.parametrize("transport_project", ["proj_other", None])
def test_live_transport_identity_must_match_independently_configured_guard(transport_project):
    client = Transport(provider())
    client.is_live = True
    client.account_id = "account-a"
    client.project_id = transport_project
    guard = Guard()
    guard.transport_account_id = "account-a"
    guard.transport_project_id = "proj_approved"
    with pytest.raises(WorkerError, match="^transport-identity-mismatch$"):
        Worker(guard, client, Counter()).process(job())
    assert client.payloads == []


def test_redaction_failure_never_exposes_exception_or_unredacted_response():
    def broken_redaction(value):
        raise RuntimeError("credential-redaction-sentinel")
    result, _ = run(provider(), redact=broken_redaction)
    assert result.status == "failed"
    assert result.error == "response-redaction-failed"
    assert result.raw_response is None
    assert result.content == ""
    assert "credential-redaction-sentinel" not in result.model_dump_json()


@pytest.mark.parametrize("content", ["bad", [{"type": "function_call", "text": "bad"}]])
def test_reasoning_content_cannot_hide_malformed_or_tool_output(content):
    data = provider()
    data["output"].insert(0, {"type": "reasoning", "summary": [], "content": content})
    result, _ = run(data)
    assert result.status == "failed"
    assert result.error == "provider-output-invalid"


@pytest.mark.parametrize("identifier", [None, "", 123])
def test_missing_provider_response_id_fails_closed(identifier):
    result, _ = run(provider(id=identifier))
    assert result.status == "failed"
    assert result.error == "provider-metadata-invalid"


def test_missing_request_id_fails_closed_without_dropping_raw_provider_evidence():
    class NoRequestID(Transport):
        def send(self, payload, **kwargs):
            response = super().send(payload, **kwargs)
            return HTTPReply(response.body, response.status, None, response.redact)
    client = NoRequestID(provider())
    result = Worker(Guard(), client, Counter()).process(job())
    assert result.status == "failed"
    assert result.error == "provider-metadata-invalid"
    assert json.loads(result.raw_response)["provider_response"] == provider()
