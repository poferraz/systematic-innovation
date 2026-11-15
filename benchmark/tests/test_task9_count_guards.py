"""Hermetic regressions for approval before every lazy counter invocation."""
import fcntl
import json
import time
from datetime import UTC, datetime, timedelta

import pytest
from test_task9_guards import accept_without_environment_reads, payload_and_bound, request, response
from test_task9_guards import setup_run as original_setup_run

from task9.guards import Task9Error

setup_run = original_setup_run


def test_expired_approval_refuses_before_any_lazy_counter(setup_run):
    _run, _approval, guard = setup_run
    job = request(setup_run)
    payload, _bound = payload_and_bound(job)
    guard.approval = guard.approval.model_copy(update={
        "expires_at": datetime.now(UTC) - timedelta(seconds=1),
    })

    class ForbiddenCounter:
        def bound(self, payload):
            pytest.fail("counter invoked before approval")

    with pytest.raises(Task9Error, match="^TASK9_APPROVAL_MISMATCH$"):
        guard.process_with_counter(job, payload, ForbiddenCounter(),
                                   lambda: pytest.fail("generation forbidden"),
                                   transport_live=False)


class FixtureTransport:
    is_live = False
    account_id = "offline-account"
    project_id = "offline-project"

    def __init__(self, *, tokens=100, callback=None):
        self.tokens = tokens
        self.callback = callback
        self.requests = 0

    def send(self, payload, *, timeout_seconds, max_output_bytes):
        from task9.transport import HTTPReply
        self.requests += 1
        assert timeout_seconds == 10 and max_output_bytes == 4096
        if self.callback:
            self.callback()
        return HTTPReply(status=200, request_id="fixture-count",
                         body=json.dumps({"object": "response.input_tokens",
                                          "input_tokens": self.tokens}).encode())


def provider(setup_run, *, tokens=100, callback=None):
    from task9.counting import ProviderInputCounter
    _run, _approval, guard = setup_run
    job = request(setup_run)
    payload, _bound = payload_and_bound(job)
    transport = FixtureTransport(tokens=tokens, callback=callback)
    counter = ProviderInputCounter(transport)
    guard.approval = guard.approval.model_copy(update={
        "token_counting_authorized": True, "max_token_count_requests": 70,
        "input_profile_sha256": counter.profile_sha256,
    })
    return guard, job, payload, counter, transport


def generation(job, incoming=100):
    result = response(job, input_tokens=incoming, cost=(incoming * 0.75 + 90) / 1000000)
    raw = json.loads(result.raw_response)
    raw["provider_response"]["usage"]["input_tokens"] = incoming
    return result.model_copy(update={"raw_response": json.dumps(raw)})


def test_counting_is_separately_default_denied(setup_run):
    guard, job, payload, counter, transport = provider(setup_run)
    guard.approval = guard.approval.model_copy(update={
        "token_counting_authorized": False, "max_token_count_requests": 0,
    })
    with pytest.raises(Task9Error, match="^TASK9_COUNT_NOT_AUTHORIZED$"):
        guard.process_with_counter(job, payload, counter,
                                   lambda: pytest.fail("unapproved generation"),
                                   transport_live=False)
    assert transport.requests == 0 and guard.records() == []


def test_count_is_durable_before_transport_and_does_not_increase_generation_attempts(setup_run):
    from task9.count_ledger import read_count_receipts
    run, _approval, _guard = setup_run

    def during_count():
        assert [row.event for row in read_count_receipts(run.inside("worker"))] == ["started"]
        assert _guard.verify()["attempts"] == 0

    guard, job, payload, counter, transport = provider(setup_run, callback=during_count)
    result = guard.process_with_counter(job, payload, counter, lambda: generation(job),
                                        transport_live=False)
    assert result.status == "succeeded"
    assert transport.requests == 1 and guard.verify()["attempts"] == 1
    rows = read_count_receipts(run.inside("worker"))
    assert [row.event for row in rows] == ["started", "completed"]
    assert rows[-1].input_bound.provider_evidence.request_id == "fixture-count"


def test_completed_generation_replay_invokes_neither_counter_nor_generation(setup_run):
    guard, job, payload, counter, transport = provider(setup_run)
    first = guard.process_with_counter(job, payload, counter, lambda: generation(job),
                                       transport_live=False)
    before = {p: p.read_bytes() for p in guard.ledger_root.rglob("*") if p.is_file()}

    class Forbidden:
        def bound(self, payload):
            pytest.fail("completed generation must not count again")

    assert guard.process_with_counter(job, payload, Forbidden(),
                                      lambda: pytest.fail("must not regenerate"),
                                      transport_live=False) == first
    assert transport.requests == 1
    assert {p: p.read_bytes() for p in guard.ledger_root.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize("damage", ["expired", "project", "request", "profile", "live", "source"])
def test_prechecks_precede_any_provider_count(setup_run, monkeypatch, damage):
    guard, job, payload, counter, transport = provider(setup_run)
    if damage == "expired":
        guard.approval = guard.approval.model_copy(update={
            "expires_at": datetime.now(UTC) - timedelta(seconds=1)})
    elif damage == "project":
        guard.transport_project_id = "wrong"
    elif damage == "request":
        payload["instructions"] += "changed"
    elif damage == "profile":
        guard.approval = guard.approval.model_copy(update={"input_profile_sha256": "a" * 64})
    elif damage == "source":
        guard.approval = guard.approval.model_copy(update={"bindings": {}})
    with pytest.raises(Task9Error):
        guard.process_with_counter(job, payload, counter,
                                   lambda: pytest.fail("generation forbidden"),
                                   transport_live=damage == "live")
    assert transport.requests == 0 and guard.records() == []


def test_worker_lock_precedes_metadata_traffic(setup_run):
    guard, job, payload, counter, transport = provider(setup_run)
    guard.ledger_root.mkdir(parents=True)
    with (guard.ledger_root / ".worker.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(Task9Error, match="^TASK9_CONCURRENCY$"):
            guard.process_with_counter(job, payload, counter,
                                       lambda: pytest.fail("generation forbidden"),
                                       transport_live=False)
    assert transport.requests == 0


@pytest.mark.parametrize("tokens,allowed", [(32768, True), (32769, False)])
def test_authoritative_input_boundary_precedes_generation(setup_run, tokens, allowed):
    guard, job, payload, counter, transport = provider(setup_run, tokens=tokens)
    sends = []

    def send():
        sends.append(True)
        return generation(job, tokens)

    if allowed:
        assert guard.process_with_counter(job, payload, counter, send,
                                          transport_live=False).input_tokens == 32768
    else:
        with pytest.raises(Task9Error, match="^TASK9_COUNT_UNRESOLVED$"):
            guard.process_with_counter(job, payload, counter, send, transport_live=False)
    assert len(sends) == int(allowed) and transport.requests == 1


def test_authoritative_usage_must_equal_count(setup_run):
    guard, job, payload, counter, transport = provider(setup_run, tokens=101)
    with pytest.raises(Task9Error, match="^TASK9_ATTEMPT_UNRESOLVED$"):
        guard.process_with_counter(job, payload, counter, lambda: generation(job, 100),
                                   transport_live=False)
    assert transport.requests == 1
    assert guard.records()[-1].event == "error"


def test_ambiguous_count_is_retained_and_never_retried_after_restart(setup_run):
    from task9.count_ledger import read_count_receipts
    from task9.guards import Task9Guard

    def interrupted():
        raise TimeoutError("fixture-sensitive-value")

    guard, job, payload, counter, transport = provider(setup_run, callback=interrupted)
    with pytest.raises(Task9Error, match="^TASK9_COUNT_UNRESOLVED$"):
        guard.process_with_counter(job, payload, counter,
                                   lambda: pytest.fail("generation forbidden"),
                                   transport_live=False)
    restart = Task9Guard(guard.run, guard.approval,
                         transport_account_id=guard.transport_account_id,
                         transport_project_id=guard.transport_project_id)
    with pytest.raises(Task9Error, match="^TASK9_COUNT_UNRESOLVED$"):
        restart.process_with_counter(job, payload, counter,
                                     lambda: pytest.fail("generation forbidden"),
                                     transport_live=False)
    assert transport.requests == 1 and guard.records() == []
    assert [row.event for row in read_count_receipts(guard.ledger_root)] == ["started", "error"]


def test_count_success_can_be_reused_after_pre_generation_crash(setup_run):
    from task9.guards import Task9Guard
    guard, job, payload, counter, transport = provider(setup_run)
    # Simulate a process death after count receipt durability and before generation claim.
    with guard._lock():
        _records, request_hash, _cached = guard._before_count(job, payload, transport_live=False)
        guard._count(job, payload, counter, transport_live=False, request_hash=request_hash)
    restart = Task9Guard(guard.run, guard.approval,
                         transport_account_id=guard.transport_account_id,
                         transport_project_id=guard.transport_project_id)
    assert restart.process_with_counter(job, payload, counter, lambda: generation(job),
                                        transport_live=False).status == "succeeded"
    assert transport.requests == 1 and restart.verify()["attempts"] == 1


def test_live_direct_bound_cannot_self_certify(setup_run):
    _run, _approval, guard = setup_run
    job = request(setup_run)
    payload, bound = payload_and_bound(job, certified_for_live=True)
    with pytest.raises(Task9Error, match="^TASK9_RETAINED_COUNT_REQUIRED$"):
        guard.process(job, payload, bound, lambda: pytest.fail("generation forbidden"),
                      transport_live=True)


@pytest.mark.parametrize("self_certified", [False, True])
def test_local_counter_cannot_inject_unretained_provider_evidence(setup_run, self_certified):
    from test_task9_count_ledger import bound as invented_bound

    from task9.contracts import InputBound
    _run, _approval, guard = setup_run
    job = request(setup_run)
    payload, original = payload_and_bound(job)
    injected = InputBound(**(original.model_dump() | {
        "provider_evidence": invented_bound().provider_evidence,
        "certified_for_live": self_certified,
    }))
    with pytest.raises(Task9Error, match="^TASK9_RETAINED_COUNT_REQUIRED$"):
        guard.process(job, payload, injected, lambda: generation(job), transport_live=False)
    assert guard.records() == []


def test_over_deadline_count_never_reaches_generation(setup_run, monkeypatch):
    guard, job, payload, counter, transport = provider(setup_run)
    ticks = iter((0.0, 10.01))
    monkeypatch.setattr(time, "monotonic", lambda: next(ticks))
    with pytest.raises(Task9Error, match="^TASK9_COUNT_UNRESOLVED$"):
        guard.process_with_counter(job, payload, counter,
                                   lambda: pytest.fail("late count cannot authorize generation"),
                                   transport_live=False)
    assert transport.requests == 1 and guard.records() == []


@pytest.mark.parametrize("damage", ["request", "projection", "profile", "account", "hash", "tokens"])
def test_counter_evidence_must_match_request_identity_and_raw_reply(setup_run, damage):
    guard, job, payload, original, transport = provider(setup_run)

    class ForgedCounter:
        provider_counting = True
        is_live = False
        account_id = original.account_id
        project_id = original.project_id
        profile_sha256 = original.profile_sha256

        def bound(self, payload):
            bound = original.bound(payload)
            if damage == "request":
                return bound.model_copy(update={"request_sha256": "0" * 64})
            if damage == "profile":
                return bound.model_copy(update={"profile_sha256": "0" * 64})
            field, value = {
                "projection": ("count_request_sha256", "0" * 64),
                "account": ("account_id", "different-account"),
                "hash": ("response_sha256", "0" * 64),
                "tokens": ("response_json", '{"object":"response.input_tokens","input_tokens":99}'),
            }[damage]
            return bound.model_copy(update={
                "provider_evidence": bound.provider_evidence.model_copy(update={field: value}),
            })

    with pytest.raises(Task9Error, match="^TASK9_COUNT_UNRESOLVED$"):
        guard.process_with_counter(job, payload, ForgedCounter(),
                                   lambda: pytest.fail("mismatched count cannot authorize generation"),
                                   transport_live=False)
    assert transport.requests == 1 and guard.records() == []


def advance_guard_clock(guard, monkeypatch, *, remaining):
    from task9 import guards
    from task9.count_ledger import read_count_receipts
    rows = guard.records()
    counts = read_count_receipts(guard.ledger_root)
    first = min(items[0].timestamp for items in (rows, counts) if items)
    later = first + timedelta(seconds=10800 - remaining)
    guard.approval = guard.approval.model_copy(update={
        "expires_at": later + timedelta(hours=5),
    })

    class Later:
        @staticmethod
        def now(zone):
            return later

    monkeypatch.setattr(guards, "datetime", Later)


def next_turn(guard, first, result):
    from systematic_innovation_bench.models import TurnJob
    from systematic_innovation_bench.store import read_records
    accept_without_environment_reads(guard.run, first, result)
    outgoing = guard.run.inside("wall-next.jsonl")
    guard.run.export(outgoing)
    return read_records(outgoing, TurnJob)[0]


@pytest.mark.parametrize("remaining,allowed", [(130, False), (131, True)])
def test_wall_room_reserved_before_fresh_count_claim(setup_run, monkeypatch, remaining, allowed):
    from task9.count_ledger import read_count_receipts
    guard, first, payload, counter, transport = provider(setup_run)
    result = guard.process_with_counter(first, payload, counter, lambda: generation(first),
                                        transport_live=False)
    job = next_turn(guard, first, result)
    payload, _bound = payload_and_bound(job)
    advance_guard_clock(guard, monkeypatch, remaining=remaining)
    before = len(read_count_receipts(guard.ledger_root))
    if allowed:
        assert guard.process_with_counter(job, payload, counter, lambda: generation(job),
                                          transport_live=False).status == "succeeded"
    else:
        with pytest.raises(Task9Error, match="^TASK9_WALL_LIMIT$"):
            guard.process_with_counter(job, payload, counter,
                                       lambda: pytest.fail("generation cannot fit"),
                                       transport_live=False)
        assert len(read_count_receipts(guard.ledger_root)) == before
    assert transport.requests == 1 + int(allowed)


@pytest.mark.parametrize("remaining,allowed", [(120, False), (125, True)])
def test_cached_count_needs_only_generation_wall_room(setup_run, monkeypatch, remaining, allowed):
    guard, job, payload, counter, transport = provider(setup_run)
    with guard._lock():
        _rows, request_hash, _cached = guard._before_count(job, payload, transport_live=False)
        guard._count(job, payload, counter, transport_live=False, request_hash=request_hash)
    advance_guard_clock(guard, monkeypatch, remaining=remaining)
    if allowed:
        assert guard.process_with_counter(job, payload, counter, lambda: generation(job),
                                          transport_live=False).status == "succeeded"
    else:
        with pytest.raises(Task9Error, match="^TASK9_WALL_LIMIT$"):
            guard.process_with_counter(job, payload, counter,
                                       lambda: pytest.fail("generation cannot fit"),
                                       transport_live=False)
        assert guard.records() == []
    assert transport.requests == 1


@pytest.mark.parametrize("remaining,allowed", [(120, False), (121, True)])
def test_local_offline_generation_reserves_full_wall_deadline(setup_run, monkeypatch,
                                                             remaining, allowed):
    _run, _approval, guard = setup_run
    first = request(setup_run)
    payload, bound = payload_and_bound(first)
    result = guard.process(first, payload, bound, lambda: generation(first), transport_live=False)
    job = next_turn(guard, first, result)
    payload, bound = payload_and_bound(job)
    advance_guard_clock(guard, monkeypatch, remaining=remaining)
    before = len(guard.records())
    if allowed:
        assert guard.process(job, payload, bound, lambda: generation(job),
                             transport_live=False).status == "succeeded"
    else:
        with pytest.raises(Task9Error, match="^TASK9_WALL_LIMIT$"):
            guard.process(job, payload, bound, lambda: pytest.fail("generation cannot fit"),
                          transport_live=False)
        assert len(guard.records()) == before


def test_wall_limit_does_not_block_completed_generation_cache(setup_run, monkeypatch):
    guard, job, payload, counter, transport = provider(setup_run)
    result = guard.process_with_counter(job, payload, counter, lambda: generation(job),
                                        transport_live=False)
    advance_guard_clock(guard, monkeypatch, remaining=-1)
    before = {path: path.read_bytes() for path in guard.ledger_root.rglob("*") if path.is_file()}

    class ForbiddenCounter:
        def bound(self, payload):
            pytest.fail("completed cache must bypass counting")

    assert guard.process_with_counter(job, payload, ForbiddenCounter(),
                                      lambda: pytest.fail("completed cache must bypass generation"),
                                      transport_live=False) == result
    assert transport.requests == 1
    assert {path: path.read_bytes() for path in guard.ledger_root.rglob("*") if path.is_file()} == before
