"""Hermetic Task 9 tests never connect to a network or perform DNS lookup."""
from __future__ import annotations

import socket

import pytest


@pytest.fixture(autouse=True)
def task9_network_is_disabled(request, monkeypatch):
    if not request.node.path.name.startswith("test_task9"):
        yield
        return
    attempts = []

    def denied(*args, **kwargs):
        attempts.append(True)
        raise AssertionError("OFFLINE_TEST_NETWORK_FORBIDDEN")

    monkeypatch.setattr(socket, "getaddrinfo", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket.socket, "connect_ex", denied)
    yield
    assert not attempts, "OFFLINE_TEST_NETWORK_ATTEMPTED"
