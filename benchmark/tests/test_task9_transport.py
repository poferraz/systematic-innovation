"""Offline HTTPS boundary tests: no real sockets or credential lookup."""
import json
import ssl
import time
from typing import ClassVar

import pytest

from task9.transport import HTTPTransport, TransportError


@pytest.fixture(autouse=True)
def no_real_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("network forbidden in offline tests")
    monkeypatch.setattr("socket.create_connection", forbidden)


class Reply:
    status = 200
    def __init__(self, body=b'{"output": "fixture-secret"}', *, delay=0):
        self.body = body
        self.delay = delay
    def getheader(self, key):
        return "request-123" if key == "x-request-id" else None
    def read(self, count):
        if self.delay:
            time.sleep(self.delay)
        result, self.body = self.body[:count], self.body[count:]
        return result


class Connection:
    instances: ClassVar[list] = []
    next_reply = None
    def __init__(self, host, port, *, timeout, context):
        self.host, self.port, self.timeout, self.context = host, port, timeout, context
        self.closed = False
        self.requests = []
        self.instances.append(self)
    def request(self, method, path, body, headers):
        self.requests.append((method, path, body, headers))
    def getresponse(self):
        return self.next_reply or Reply()
    def close(self):
        self.closed = True


def transport(monkeypatch, *, reply=None):
    Connection.instances.clear()
    Connection.next_reply = reply
    monkeypatch.setattr("http.client.HTTPSConnection", Connection)
    monkeypatch.setenv("OPENAI_API_KEY", "fixture-secret")
    return HTTPTransport(account_id="account-a", project_id="proj_a")


def test_https_route_tls_no_redirect_no_retry_and_ephemeral_redaction(monkeypatch):
    client = transport(monkeypatch)
    response = client.send({"model": "fixture"}, timeout_seconds=120, max_output_bytes=1024)
    assert client.is_live is True
    assert response.status == 200
    assert response.request_id == "request-123"
    assert response.redact(json.loads(response.body)) == {"output": "[REDACTED]"}
    assert "fixture-secret" not in repr(response)
    connection = Connection.instances[0]
    assert (connection.host, connection.port) == ("api.openai.com", 443)
    assert connection.context.verify_mode == ssl.CERT_REQUIRED
    assert connection.context.check_hostname is True
    assert connection.requests[0][0:2] == ("POST", "/v1/responses")
    assert connection.requests[0][3]["Authorization"] == "Bearer fixture-secret"
    assert connection.requests[0][3]["OpenAI-Project"] == "proj_a"
    assert len(Connection.instances) == 1
    assert connection.closed


@pytest.mark.parametrize("status", [301, 401, 429, 503])
def test_non_200_is_returned_once_for_worker_to_retain_failure(monkeypatch, status):
    reply = Reply()
    reply.status = status
    response = transport(monkeypatch, reply=reply).send({}, timeout_seconds=1, max_output_bytes=128)
    assert response.status == status
    assert len(Connection.instances) == 1
    assert Connection.instances[0].closed


def test_response_cap_is_enforced_while_reading(monkeypatch):
    with pytest.raises(TransportError, match="^response-too-large$"):
        transport(monkeypatch, reply=Reply(b"x" * 1025)).send(
            {}, timeout_seconds=1, max_output_bytes=1024
        )
    assert len(Connection.instances) == 1
    assert Connection.instances[0].closed


def test_total_deadline_interrupts_a_slow_read_without_retry(monkeypatch):
    before = time.monotonic()
    with pytest.raises(TransportError, match="^request-timeout$"):
        transport(monkeypatch, reply=Reply(delay=1)).send(
            {}, timeout_seconds=0.02, max_output_bytes=1024
        )
    assert time.monotonic() - before < 0.5
    assert len(Connection.instances) == 1
    assert Connection.instances[0].closed


def test_missing_credential_and_invalid_limits_never_open_connection(monkeypatch):
    client = transport(monkeypatch)
    monkeypatch.delenv("OPENAI_API_KEY")
    with pytest.raises(TransportError, match="^credential-unavailable$"):
        client.send({}, timeout_seconds=1, max_output_bytes=128)
    with pytest.raises(TransportError, match="^transport-limits-invalid$"):
        client.send({}, timeout_seconds=121, max_output_bytes=128)
    assert Connection.instances == []


def test_connection_close_failure_is_code_only(monkeypatch):
    client = transport(monkeypatch)
    def broken_close(self):
        raise RuntimeError("secret-close-detail")
    monkeypatch.setattr(Connection, "close", broken_close)
    with pytest.raises(TransportError, match="^transport-failed$"):
        client.send({}, timeout_seconds=1, max_output_bytes=128)


def test_non_main_thread_refuses_before_credential_or_connection(monkeypatch):
    import threading
    client = transport(monkeypatch)
    results = []
    def run():
        try:
            client.send({}, timeout_seconds=1, max_output_bytes=128)
        except TransportError as error:
            results.append(str(error))
    thread = threading.Thread(target=run)
    thread.start()
    thread.join()
    assert results == ["deadline-unavailable"]
    assert Connection.instances == []


def test_production_transport_live_mode_and_identity_cannot_be_overridden(monkeypatch):
    client = transport(monkeypatch)
    for name, replacement in (("is_live", False), ("account_id", "other"),
                              ("project_id", "proj_other")):
        with pytest.raises(AttributeError):
            setattr(client, name, replacement)
    assert client.is_live is True
    assert client.account_id == "account-a"
    assert client.project_id == "proj_a"
