"""Offline integration tests for the independent Task 9 send boundary."""

from __future__ import annotations

import fcntl
import importlib
import json
import shutil
from datetime import UTC, datetime, timedelta

import pytest
import yaml

from systematic_innovation_bench.models import RunConfig, RunManifest, TurnResponse
from systematic_innovation_bench.planner import plan_jobs
from systematic_innovation_bench.runtime import (
    REPOSITORY_ROOT,
    RunDirectory,
    canonical_digest,
    current_source_digest,
    digest,
    public_cases,
)
from systematic_innovation_bench.store import append_record, read_records


def api():
    return importlib.import_module("task9.guards"), importlib.import_module("task9.contracts")


@pytest.fixture
def setup_run(tmp_path):
    guards, contracts = api()
    values = yaml.safe_load(
        (REPOSITORY_ROOT / "benchmark/configs/feasibility-six.proposed.yaml").read_text()
    )
    values.update(run_id="offline-task9", dry_run=False)
    config = RunConfig.model_validate(values)
    cases = public_cases(REPOSITORY_ROOT / "benchmark/cases/development", contracts.CASE_IDS)
    jobs = plan_jobs(cases, config, datetime.now(UTC))
    manifest = RunManifest(
        run_id=config.run_id,
        git_revision="0" * 40,
        runner_source_sha256=current_source_digest(),
        runner_worktree_dirty=True,
        skill_revision="0" * 64,
        config=config,
        cases=tuple(cases),
        artifact_digests={
            "dependency_lock": digest(REPOSITORY_ROOT / "benchmark/uv.lock"),
            "planned_jobs": canonical_digest([j.model_dump(mode="json") for j in jobs]),
            "public_corpus": canonical_digest([c.model_dump(mode="json") for c in cases]),
        },
    )
    run = RunDirectory(tmp_path / "run")
    with run.lock():
        run.create(jobs, manifest)
    # Test fixture records canonical skill identity; the guard independently recomputes it.
    manifest_path = run.inside("manifest.json")
    manifest = manifest.model_copy(update={"skill_revision": guards.skill_tree_digest()})
    manifest_path.write_text(manifest.model_dump_json(indent=2) + "\n")
    run.snapshot()
    approval = contracts.ExecutionApproval(
        approved=True,
        mode="offline",
        run_id=config.run_id,
        account_id="offline-account",
        project_id="offline-project",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        budget_override_approved=True,
        bindings=guards.approval_bindings(run),
        input_profile_sha256="a" * 64,
    )
    guard = guards.Task9Guard(
        run, approval,
        transport_account_id="offline-account", transport_project_id="offline-project",
    )
    return run, approval, guard


def request(setup_run, *, reserve=True):
    run, _, _ = setup_run
    if reserve:
        run.export(run.path / "outbox.jsonl")
        return read_records(run.path / "outbox.jsonl", importlib.import_module(
            "systematic_innovation_bench.models").TurnJob)[0]
    return run.opaque(run.pending()[0])


def payload_and_bound(job, **updates):
    _, contracts = api()
    payload = {
        "model": job.model,
        "instructions": job.system_instructions,
        "input": [{"role": t.role, "content": t.content} for t in job.transcript],
        **job.model_parameters,
    }
    bound = contracts.InputBound(
        tokens=100, profile_sha256="a" * 64,
        request_sha256=canonical_digest(payload), **updates,
    )
    return payload, bound


def response(job, **updates):
    return TurnResponse(**({
        "job_id": job.job_id, "turn_index": job.assistant_turn_index,
        "attempt": 0, "content": "Synthetic offline answer", "input_tokens": 100,
        "output_tokens": 20, "cost": 0.000165, "latency_seconds": 0.01,
        "raw_response": json.dumps({
            "provider_response": {"id": "offline-response", "model": job.model,
                                  "service_tier": "default", "status": "completed",
                                  "usage": {"input_tokens": 100, "output_tokens": 20}},
            "request_id": "offline-request", "http_status": 200,
            "cost_provenance": {
                "kind": "calculated-token-rate-upper-bound", "currency": "USD",
                "input_rate_usd_per_million": "0.75",
                "output_rate_usd_per_million": "4.50",
                "basis": "provider-total-tokens; uncached input rate; reasoning not added again",
            },
        }),
    } | updates))


def process(setup_run, job=None, *, result=None, **kwargs):
    _, _, guard = setup_run
    job = job or request(setup_run)
    payload, bound = payload_and_bound(job)
    return guard.process(job, payload, bound, lambda: result or response(job),
                         transport_live=False, **kwargs)


def test_reserved_send_is_durable_and_identical_replay_returns_cached_response(setup_run):
    guards, _ = api()
    run, _, guard = setup_run
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    def send():
        assert [r.event for r in guards.read_receipts(run.path / "worker")] == [
            "reserved", "dispatched"]
        return response(job)
    first = guard.process(job, payload, bound, send, transport_live=False)
    before = (run.path / "worker/attempts.jsonl").read_bytes()
    def forbidden():
        pytest.fail("a completed attempt must never be sent twice")
    assert guard.process(job, payload, bound, forbidden, transport_live=False) == first
    assert (run.path / "worker/attempts.jsonl").read_bytes() == before
    receipts = guards.read_receipts(run.path / "worker")
    assert [r.event for r in receipts] == ["reserved", "dispatched", "completed"]
    assert receipts[-1].charged_micro_usd == 165
    assert receipts[-1].reserved_micro_usd == 50000
    assert guard.verify()["attempts"] == 1


@pytest.mark.parametrize("changes", [
    {"approved": False}, {"expires_at": datetime(2020, 1, 1, tzinfo=UTC)},
    {"run_id": "other"}, {"budget_override_approved": False},
    {"account_id": "other"}, {"project_id": "other"},
    {"bindings": {"unknown": "f" * 64}},
])
def test_approval_mismatch_blocks_before_send(setup_run, changes):
    guards, _ = api()
    run, approval, _ = setup_run
    job = request(setup_run)
    guard = guards.Task9Guard(run, approval.model_copy(update=changes),
                             transport_account_id="offline-account",
                             transport_project_id="offline-project")
    payload, bound = payload_and_bound(job)
    with pytest.raises(guards.Task9Error):
        guard.process(job, payload, bound, lambda: pytest.fail("send forbidden"),
                      transport_live=False)


@pytest.mark.parametrize("mode,live", [("offline", True), ("live", False), ("live", True)])
def test_mode_mismatch_or_unapproved_live_stage_never_sends(setup_run, mode, live):
    guards, _ = api()
    run, approval, _ = setup_run
    guard = guards.Task9Guard(run, approval.model_copy(update={
        "mode": mode, "live_execution_authorized": True,
    }), transport_account_id="offline-account", transport_project_id="offline-project")
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    with pytest.raises(guards.Task9Error):
        guard.process(job, payload, bound, lambda: pytest.fail("live send forbidden"),
                      transport_live=live)


def test_unreserved_or_changed_pending_turn_never_sends(setup_run):
    guards, _ = api()
    job = request(setup_run, reserve=False)
    with pytest.raises(guards.Task9Error):
        process(setup_run, job)
    run, _, _ = setup_run
    run.export(run.path / "outbox.jsonl")
    altered = job.model_copy(update={"system_instructions": "changed"})
    with pytest.raises(guards.Task9Error):
        process(setup_run, altered)


@pytest.mark.parametrize("tokens,profile,request_hash", [
    (32769, "a" * 64, None), (100, "b" * 64, None), (100, "a" * 64, "b" * 64),
])
def test_input_bound_is_strict_and_bound_to_payload(setup_run, tokens, profile, request_hash):
    guards, _ = api()
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    bound = bound.model_copy(update={"tokens": tokens, "profile_sha256": profile,
                                    "request_sha256": request_hash or bound.request_sha256})
    with pytest.raises(guards.Task9Error):
        setup_run[2].process(job, payload, bound, lambda: pytest.fail("send forbidden"),
                             transport_live=False)


def test_changed_request_replay_is_rejected(setup_run):
    guards, _ = api()
    job = request(setup_run)
    process(setup_run, job)
    payload, bound = payload_and_bound(job)
    payload["instructions"] = "different request"
    bound = bound.model_copy(update={"request_sha256": canonical_digest(payload)})
    with pytest.raises(guards.Task9Error):
        setup_run[2].process(job, payload, bound, lambda: pytest.fail("retry forbidden"),
                             transport_live=False)


@pytest.mark.parametrize("updates", [
    {"input_tokens": None}, {"output_tokens": None}, {"input_tokens": 32769},
    {"output_tokens": 4097}, {"cost": 0.06}, {"cost": 0.0},
    {"status": "failed", "error": "PROVIDER_FAILURE"}, {"content": ""},
    {"job_id": "wrong"},
])
def test_invalid_return_latches_run_and_does_not_retry(setup_run, updates):
    guards, _ = api()
    run, _, guard = setup_run
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    bad = response(job, **updates)
    with pytest.raises(guards.Task9Error):
        guard.process(job, payload, bound, lambda: bad, transport_live=False)
    with pytest.raises(guards.Task9Error):
        guard.process(job, payload, bound, lambda: pytest.fail("retry forbidden"),
                      transport_live=False)
    assert guard.verify()["stopped"] is True
    assert len([r for r in guards.read_receipts(run.path / "worker")
                if r.event == "dispatched"]) == 1


def test_transport_exception_is_code_only_and_restart_cannot_retry(setup_run):
    guards, _ = api()
    run, approval, guard = setup_run
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    sentinel = "synthetic-secret-sentinel-never-persist"
    def ambiguous():
        raise TimeoutError(sentinel)
    with pytest.raises(guards.Task9Error) as caught:
        guard.process(job, payload, bound, ambiguous, transport_live=False)
    leaked = sentinel in str(caught.value) or sentinel.encode() in (
        run.path / "worker/attempts.jsonl").read_bytes()
    assert leaked is False
    restarted = guards.Task9Guard(run, approval, transport_account_id="offline-account",
                                  transport_project_id="offline-project")
    with pytest.raises(guards.Task9Error):
        restarted.process(job, payload, bound, lambda: pytest.fail("retry forbidden"),
                          transport_live=False)


def test_process_lock_is_nonblocking_and_held_through_callback(setup_run):
    guards, _ = api()
    run, _, guard = setup_run
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    def send():
        with (run.path / "worker/.worker.lock").open("a") as stream, \
                pytest.raises(BlockingIOError):
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(guards.Task9Error):
            guard.process(job, payload, bound, lambda: pytest.fail("concurrent send"),
                          transport_live=False)
        return response(job)
    guard.process(job, payload, bound, send, transport_live=False)


@pytest.mark.parametrize("artifact", ["journal", "response", "truncate"])
def test_corrupt_or_truncated_worker_evidence_fails_closed(setup_run, artifact):
    guards, _ = api()
    run, _, guard = setup_run
    job = request(setup_run)
    process(setup_run, job)
    records = guards.read_receipts(run.path / "worker")
    if artifact == "response":
        (run.path / "worker" / records[-1].response_path).write_text("{}")
    else:
        journal = run.path / "worker/attempts.jsonl"
        journal.write_bytes(b"" if artifact == "truncate" else
                            journal.read_bytes().replace(b'"reserved"', b'"tampered"', 1))
    payload, bound = payload_and_bound(job)
    with pytest.raises(guards.Task9Error):
        guard.process(job, payload, bound, lambda: pytest.fail("send forbidden"),
                      transport_live=False)


def test_ledger_must_stay_inside_worker_directory(setup_run, tmp_path):
    guards, _ = api()
    run, approval, _ = setup_run
    with pytest.raises(guards.Task9Error):
        guards.Task9Guard(run, approval, ledger_root=tmp_path / "elsewhere",
                          transport_account_id="offline-account",
                          transport_project_id="offline-project")


@pytest.mark.parametrize("bad", [True, "70", 70.0])
def test_policy_rejects_coerced_call_limits(bad):
    _, contracts = api()
    with pytest.raises(ValueError):
        contracts.Task9Policy(max_calls=bad)


def test_policy_cannot_expand_the_approved_limits():
    _, contracts = api()
    for updates in ({"max_calls": 71}, {"max_cost_micro_usd": 5000001},
                    {"max_concurrency": 2}, {"retry_limit": 1}):
        with pytest.raises(ValueError):
            contracts.Task9Policy(**updates)


def test_owner_budget_decision_is_bound_to_approval(setup_run):
    _, approval, _ = setup_run
    assert "readiness_approval" in approval.bindings


@pytest.mark.parametrize("field,value", [("budget_approved", False),
                                          ("offline_tests_authorized", False),
                                          ("canonical_skill_frozen", False)])
def test_actual_owner_decision_must_authorize_offline_work(setup_run, tmp_path, monkeypatch,
                                                        field, value):
    guards, _ = api()
    decision = yaml.safe_load((REPOSITORY_ROOT /
                              "benchmark/study/task9-readiness-approval.yaml").read_text())
    decision[field] = value
    path = tmp_path / "owner-decision.yaml"
    path.write_text(yaml.safe_dump(decision))
    monkeypatch.setattr(guards, "READINESS_PATH", path, raising=False)
    run, approval, _ = setup_run
    approval = approval.model_copy(update={"bindings": guards.approval_bindings(run)})
    guard = guards.Task9Guard(run, approval, transport_account_id="offline-account",
                              transport_project_id="offline-project")
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    with pytest.raises(guards.Task9Error):
        guard.process(job, payload, bound, lambda: pytest.fail("send forbidden"),
                      transport_live=False)


def test_failed_correlated_provider_packet_is_retained_for_technical_review(setup_run):
    guards, _ = api()
    run, _, guard = setup_run
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    failed = response(job, status="failed", error="PROVIDER_FAILURE")
    with pytest.raises(guards.Task9Error):
        guard.process(job, payload, bound, lambda: failed, transport_live=False)
    receipt = guards.read_receipts(run.path / "worker")[-1]
    assert receipt.event == "error"
    assert receipt.response_path is not None
    retained = TurnResponse.model_validate_json(
        (run.path / "worker" / receipt.response_path).read_bytes())
    assert retained == failed


@pytest.mark.parametrize("provider_updates", [
    {"model": "wrong-model"}, {"service_tier": "priority"}, {"status": "incomplete"},
    {"usage": {"input_tokens": True, "output_tokens": 20}},
    {"usage": {"input_tokens": 100, "output_tokens": 21}}, {"id": None},
    {"output": [{"type": "function_call", "name": "unexpected_tool"}]},
])
def test_guard_independently_checks_retained_provider_metadata(setup_run, provider_updates):
    guards, _ = api()
    job = request(setup_run)
    result = response(job)
    raw = json.loads(result.raw_response)
    raw["provider_response"].update(provider_updates)
    result = result.model_copy(update={"raw_response": json.dumps(raw)})
    with pytest.raises(guards.Task9Error):
        process(setup_run, job, result=result)


@pytest.mark.parametrize("updates", [
    {"raw_response": "x" * 1048577}, {"latency_seconds": 120.001},
    {"latency_seconds": None}, {"raw_response": None},
])
def test_guard_rejects_oversized_missing_or_late_provider_evidence(setup_run, updates):
    guards, _ = api()
    job = request(setup_run)
    with pytest.raises(guards.Task9Error):
        process(setup_run, job, result=response(job, **updates))


@pytest.mark.parametrize("attempts,spent", [
    (70, 3500000), (71, 0), (69, 4500000), (1, 4450000), (1, 4999999),
])
def test_budget_boundaries_stop_before_the_next_attempt(attempts, spent):
    guards, _ = api()
    with pytest.raises(guards.Task9Error):
        guards.check_envelope(attempts, spent, 50000)


def test_last_allowed_attempt_and_outward_budget_rounding_are_accepted():
    guards, _ = api()
    guards.check_envelope(69, 3450000, 50000)
    guards.check_envelope(1, 4449999, 50000)


def test_crash_after_dispatch_latches_without_saving_an_exception_string(setup_run):
    guards, _ = api()
    run, approval, guard = setup_run
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    def interrupted():
        raise KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        guard.process(job, payload, bound, interrupted, transport_live=False)
    assert [r.event for r in guards.read_receipts(run.path / "worker")] == [
        "reserved", "dispatched"]
    restarted = guards.Task9Guard(run, approval, transport_account_id="offline-account",
                                  transport_project_id="offline-project")
    with pytest.raises(guards.Task9Error):
        restarted.process(job, payload, bound, lambda: pytest.fail("retry forbidden"),
                          transport_live=False)


def test_request_boolean_parameters_cannot_be_replaced_with_integers(setup_run):
    guards, _ = api()
    job = request(setup_run)
    payload, bound = payload_and_bound(job)
    payload["store"] = 0
    bound = bound.model_copy(update={"request_sha256": canonical_digest(payload)})
    with pytest.raises(guards.Task9Error):
        setup_run[2].process(job, payload, bound, lambda: pytest.fail("send forbidden"),
                             transport_live=False)


def test_raw_corpus_bytes_are_frozen_even_when_parsed_cases_are_unchanged(setup_run, tmp_path,
                                                                       monkeypatch):
    guards, _ = api()
    corpus = tmp_path / "public-corpus"
    shutil.copytree(REPOSITORY_ROOT / "benchmark/cases/development", corpus)
    monkeypatch.setattr(guards, "CORPUS_PATH", corpus, raising=False)
    run, approval, _ = setup_run
    approval = approval.model_copy(update={"bindings": guards.approval_bindings(run)})
    guard = guards.Task9Guard(run, approval, transport_account_id="offline-account",
                              transport_project_id="offline-project")
    job = request(setup_run)
    path = corpus / "adversarial.yaml"
    path.write_bytes(path.read_bytes() + b"\n# changed after approval\n")
    payload, bound = payload_and_bound(job)
    with pytest.raises(guards.Task9Error):
        guard.process(job, payload, bound, lambda: pytest.fail("send forbidden"),
                      transport_live=False)


def accept_without_environment_reads(run, job, result):
    canonical = next(turn for turn in run.pending() if run.opaque(turn).turn_id == job.turn_id)
    accepted = TurnResponse.model_validate(result.model_dump() | {
        "job_id": canonical.job_id, "turn_id": "",
    })
    append_record(run.inside("records/turns.jsonl"), accepted)
    run.pending(finalize=True)
    run.snapshot()


def test_accepted_core_turn_without_matching_worker_receipt_blocks_further_sends(setup_run):
    guards, _ = api()
    run, _, guard = setup_run
    first = request(setup_run)
    accept_without_environment_reads(run, first, response(first))
    run.export(run.path / "next.jsonl")
    job = read_records(run.path / "next.jsonl", importlib.import_module(
        "systematic_innovation_bench.models").TurnJob)[0]
    payload, bound = payload_and_bound(job)
    with pytest.raises(guards.Task9Error):
        guard.process(job, payload, bound, lambda: pytest.fail("send forbidden"),
                      transport_live=False)


def test_three_hour_wall_limit_blocks_a_fresh_turn_after_clean_acceptance(setup_run, monkeypatch):
    guards, _ = api()
    run, approval, guard = setup_run
    first = request(setup_run)
    result = process(setup_run, first)
    accept_without_environment_reads(run, first, result)
    run.export(run.path / "next.jsonl")
    job = read_records(run.path / "next.jsonl", importlib.import_module(
        "systematic_innovation_bench.models").TurnJob)[0]
    approval = approval.model_copy(update={"expires_at": datetime.now(UTC) + timedelta(hours=5)})
    guard = guards.Task9Guard(run, approval, transport_account_id="offline-account",
                              transport_project_id="offline-project")
    future = datetime.now(UTC) + timedelta(hours=3, seconds=1)
    class Later:
        @staticmethod
        def now(zone):
            return future
    monkeypatch.setattr(guards, "datetime", Later)
    payload, bound = payload_and_bound(job)
    with pytest.raises(guards.Task9Error, match="TASK9_WALL_LIMIT"):
        guard.process(job, payload, bound, lambda: pytest.fail("send forbidden"),
                      transport_live=False)
