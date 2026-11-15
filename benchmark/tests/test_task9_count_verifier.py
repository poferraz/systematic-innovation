"""Count evidence verification is offline and exposes only technical metadata."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta

import pytest
from test_task9_verifier import (
    SENTINEL,
    _accept,
    _make_run,
    _resume_in_fresh_process,
    _rewrite_receipts,
)
from test_task9_verifier import (
    complete_run as complete_run,  # noqa: PLC0414 - expose the imported pytest fixture
)
from test_task9_verifier import (
    complete_template as complete_template,  # noqa: PLC0414 - dependency of complete_run
)

from systematic_innovation_bench.conversation import (
    accept_turn,
    next_turn_job,
    start_conversation,
)
from systematic_innovation_bench.runtime import canonical_digest, digest
from task9.contracts import InputBound, ProviderCountEvidence
from task9.count_ledger import CountLedger
from task9.counting import build_count_payload, counting_profile
from task9.verifier import verify_technical_run
from task9.worker import build_payload

STAMP = datetime(2026, 11, 15, tzinfo=UTC)


def _requests(run):
    cases = {case.id: case for case in run.manifest.cases}
    result = []
    for job in run.jobs:
        state = start_conversation(job, cases[job.case_id])
        for response in (item for item in run.turns if item.job_id == job.job_id):
            request = next_turn_job(state)
            assert request is not None
            opaque = run.opaque(request)
            result.append((opaque.turn_id, build_payload(opaque)))
            state = accept_turn(state, request, response)
    return result


def _add_counts(run, ledger, monkeypatch, *, number=None):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return STAMP

    monkeypatch.setattr("task9.count_ledger.datetime", Clock)
    journal = CountLedger(ledger)
    profile = canonical_digest(counting_profile())
    for turn_id, request in _requests(run)[:number]:
        count_hash = canonical_digest(build_count_payload(request))
        response = '{"input_tokens":200,"object":"response.input_tokens"}'
        bound = InputBound(
            tokens=200, profile_sha256=profile, request_sha256=canonical_digest(request),
            provider_evidence=ProviderCountEvidence(
                count_request_sha256=count_hash, account_id="fixture-account",
                project_id="fixture-project", request_id="req_count_fixture",
                response_json=response, response_sha256=hashlib.sha256(response.encode()).hexdigest(),
                counted_at=STAMP,
            ),
        )
        journal.start(turn_id=turn_id, request_sha256=bound.request_sha256,
                      count_request_sha256=count_hash, profile_sha256=profile,
                      account_id="fixture-account", project_id="fixture-project")
        journal.complete(bound)


def _bind_count_checkpoint(ledger, checkpoint):
    count_path = ledger / "counts/attempts.jsonl"
    first = b"".join(count_path.read_bytes().splitlines(keepends=True)[:2])
    prefix = {"size": len(first), "sha256": hashlib.sha256(first).hexdigest()}
    values = {"count_ledger": prefix, "count_receipt_count": 2,
              "count_marker_sha256": digest(ledger / "counting.json")}
    saved = json.loads(checkpoint.read_bytes())
    checkpoint.write_text(json.dumps(saved | values))
    receipt = checkpoint.with_name(checkpoint.name + ".resume.json")
    resumed = json.loads(receipt.read_bytes())
    receipt.write_text(json.dumps(resumed | values | {"checkpoint_sha256": digest(checkpoint)}))


def _rewrite_counts(ledger, mutate):
    path = ledger / "counts/attempts.jsonl"
    lines = path.read_bytes().splitlines(keepends=True)
    rows = [json.loads(line) for line in lines]
    mutate(rows)
    previous = "0" * 64
    for index, row in enumerate(rows, 1):
        row.update(seq=index, previous_sha256=previous)
        row.pop("sha256", None)
        row["sha256"] = canonical_digest(row)
        previous = row["sha256"]
    path.write_bytes(b"".join(
        lines[index] if index < len(lines) and json.loads(lines[index]) == row
        else (json.dumps(row) + "\n").encode() for index, row in enumerate(rows)
    ))
    for row in rows:
        if row["event"] == "started":
            claim = ledger / ("counts/claims/" + hashlib.sha256(row["turn_id"].encode()).hexdigest()
                              + ".json")
            claim.write_text(json.dumps({name: row[name] for name in (
                "turn_id", "request_sha256", "count_request_sha256", "profile_sha256",
                "account_id", "project_id",
            )}))


def test_full_counts_are_separate_metadata_and_never_generation_usage(
    complete_run, monkeypatch
):
    run, ledger, checkpoint = complete_run
    _add_counts(run, ledger, monkeypatch)
    _bind_count_checkpoint(ledger, checkpoint)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert report.decision == "offline-rehearsal-complete", report.diagnostics
    assert report.metadata.count_requests == 70
    assert report.metadata.count_complete_requests == 70
    assert report.metadata.accounting_method == "provider-input-tokens"
    assert report.checks.count_accounting_verified
    assert report.digests.count_ledger == digest(ledger / "counts/attempts.jsonl")
    assert report.coverage.provider_attempts == report.metadata.actual_attempts == 70
    assert (report.resources.input_tokens, report.resources.output_tokens) == (14000, 1400)
    assert report.resources.calculated_upper_bound_usd == "0.016800"
    assert report.resources.reserved_upper_bound_usd == "3.500000"
    for private in (SENTINEL, "fixture-account", "fixture-project", "req_count_fixture"):
        assert private not in report.model_dump_json()


def test_local_offline_fixture_remains_explicitly_uncertified(complete_run):
    run, ledger, checkpoint = complete_run
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert report.technical_checks_passed
    assert report.metadata.count_requests == report.metadata.count_complete_requests == 0
    assert report.metadata.accounting_method == "offline-local-uncertified"
    assert not report.checks.count_accounting_verified


def test_live_verification_requires_retained_count_evidence(complete_run):
    run, ledger, checkpoint = complete_run
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint, mode="live")
    assert "COUNT_EVIDENCE_INVALID" in report.diagnostics
    assert report.metadata.accounting_method == "unverified"
    assert not report.checks.count_accounting_verified
    assert report.decision == "stopped-incomplete"


@pytest.mark.parametrize("kind", ["malformed", "marker-only", "partial", "unattested"])
def test_present_invalid_or_incomplete_counts_cannot_be_ignored(
    complete_run, monkeypatch, kind
):
    run, ledger, checkpoint = complete_run
    if kind == "malformed":
        (ledger / "counts").mkdir()
        (ledger / "counts/attempts.jsonl").write_text('{"secret":"' + SENTINEL + '"}\n')
    elif kind == "marker-only":
        (ledger / "counting.json").write_text('{"verified":true}')
    else:
        _add_counts(run, ledger, monkeypatch, number=1)
        if kind == "unattested":
            def mutate(rows):
                rows[-1]["input_bound"]["provider_evidence"] = None
            _rewrite_counts(ledger, mutate)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert "COUNT_EVIDENCE_INVALID" in report.diagnostics
    assert not report.checks.count_accounting_verified
    assert report.decision == "stopped-incomplete"
    assert SENTINEL not in report.model_dump_json()


@pytest.mark.parametrize("kind", ["tokens", "request", "profile", "identity", "deadline",
                                  "overlap", "error"])
def test_count_proof_correlation_and_limits_are_verified_independently(
    complete_run, monkeypatch, kind
):
    run, ledger, checkpoint = complete_run
    _add_counts(run, ledger, monkeypatch)
    _bind_count_checkpoint(ledger, checkpoint)

    def mutate(rows):
        pair = rows[2:4]  # Preserve the checkpoint's first accepted count prefix.
        if kind == "tokens":
            bound = pair[1]["input_bound"]
            bound["tokens"] = 201
            raw = '{"input_tokens":201,"object":"response.input_tokens"}'
            bound["provider_evidence"]["response_json"] = raw
            bound["provider_evidence"]["response_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        elif kind in {"request", "profile", "identity"}:
            field = {"request": "request_sha256", "profile": "profile_sha256",
                     "identity": "account_id"}[kind]
            value = "different-account" if kind == "identity" else "b" * 64
            for row in pair:
                row[field] = value
            if kind == "identity":
                pair[1]["input_bound"]["provider_evidence"][field] = value
            else:
                pair[1]["input_bound"][field] = value
        elif kind == "deadline":
            pair[1]["timestamp"] = (STAMP + timedelta(seconds=11)).isoformat()
        elif kind == "overlap":
            rows[2:6] = [rows[2], rows[4], rows[3], rows[5]]
        else:
            pair[1].update(event="error", input_bound=None, error="TASK9_COUNT_UNRESOLVED")

    _rewrite_counts(ledger, mutate)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert "COUNT_EVIDENCE_INVALID" in report.diagnostics
    assert not report.checks.count_accounting_verified
    assert report.decision == "stopped-incomplete"


def test_supplied_approval_binds_count_identity_and_profile(complete_run, monkeypatch):
    from task9.contracts import ExecutionApproval
    from task9.guards import approval_bindings

    run, ledger, checkpoint = complete_run
    _add_counts(run, ledger, monkeypatch)
    _bind_count_checkpoint(ledger, checkpoint)
    approval = ExecutionApproval(
        approved=True, mode="offline", run_id=run.manifest.run_id,
        account_id="wrong-account", project_id="fixture-project",
        expires_at=datetime.now(UTC) + timedelta(hours=1), budget_override_approved=True,
        token_counting_authorized=True, max_token_count_requests=70,
        bindings=approval_bindings(run), input_profile_sha256=canonical_digest(counting_profile()),
    )
    target = run.inside("technical/count-approval.json")
    target.write_text(approval.model_dump_json())
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint, approval=target)
    assert "COUNT_EVIDENCE_INVALID" in report.diagnostics
    assert not report.checks.count_accounting_verified


def test_checkpoint_binds_count_prefix_and_marker_before_fresh_resume(tmp_path, monkeypatch):
    from task9.verifier import create_resume_checkpoint

    run, ledger = _make_run(tmp_path)
    _accept(run, ledger, 0)
    _add_counts(run, ledger, monkeypatch)
    checkpoint = run.inside("technical/count-checkpoint.json")
    create_resume_checkpoint(run, worker_ledger=ledger, output=checkpoint)
    saved = json.loads(checkpoint.read_bytes())
    assert saved["count_receipt_count"] == 2
    assert saved["count_ledger"] == {
        "size": (ledger / "counts/attempts.jsonl").stat().st_size,
        "sha256": digest(ledger / "counts/attempts.jsonl"),
    }
    assert saved["count_marker_sha256"] == digest(ledger / "counting.json")
    _resume_in_fresh_process(run, ledger, checkpoint)
    resumed = json.loads(checkpoint.with_name(checkpoint.name + ".resume.json").read_bytes())
    assert resumed["count_ledger"] == saved["count_ledger"]
    assert resumed["count_receipt_count"] == 2
    assert resumed["count_marker_sha256"] == saved["count_marker_sha256"]


@pytest.mark.parametrize("kind", ["prefix", "marker", "deleted", "late-count"])
def test_resume_requires_unchanged_count_prefix_and_marker(
    complete_run, monkeypatch, kind
):
    run, ledger, checkpoint = complete_run
    _add_counts(run, ledger, monkeypatch)
    if kind != "late-count":
        _bind_count_checkpoint(ledger, checkpoint)
    if kind == "prefix":
        path = ledger / "counts/attempts.jsonl"
        path.write_bytes(path.read_bytes().replace(b'"seq":1', b'"seq":9', 1))
    elif kind == "marker":
        (ledger / "counting.json").write_text('{"schema":"other"}\n')
    elif kind == "deleted":
        (ledger / "counts/attempts.jsonl").unlink()
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert "RESUME_INVALID" in report.diagnostics
    assert not report.checks.resume_verified


def test_fresh_resume_refuses_appended_count_rows_before_second_export(tmp_path, monkeypatch):
    import subprocess
    import sys

    from task9.verifier import create_resume_checkpoint

    run, ledger = _make_run(tmp_path)
    _accept(run, ledger, 0)
    _add_counts(run, ledger, monkeypatch)
    checkpoint = run.inside("technical/count-checkpoint.json")
    create_resume_checkpoint(run, worker_ledger=ledger, output=checkpoint)
    path = ledger / "counts/attempts.jsonl"
    with path.open("ab") as stream:
        stream.write(path.read_bytes().splitlines(keepends=True)[0])
    code = ('from pathlib import Path; from systematic_innovation_bench.runtime import RunDirectory; '
            'from task9.verifier import record_resume; '
            f'record_resume(RunDirectory(Path({str(run.path)!r})), '
            f'worker_ledger=Path({str(ledger)!r}), checkpoint=Path({str(checkpoint)!r}))')
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, check=False)
    assert result.returncode != 0
    assert b"RESUME_INVALID" in result.stderr
    assert not checkpoint.with_name(checkpoint.name + ".resume.json").exists()


def test_resume_prefix_must_cover_exactly_two_count_events(complete_run, monkeypatch):
    run, ledger, checkpoint = complete_run
    _add_counts(run, ledger, monkeypatch)
    _bind_count_checkpoint(ledger, checkpoint)
    prefix = b"".join((ledger / "counts/attempts.jsonl").read_bytes().splitlines(keepends=True)[:4])
    changed = {"size": len(prefix), "sha256": hashlib.sha256(prefix).hexdigest()}
    saved = json.loads(checkpoint.read_bytes())
    checkpoint.write_text(json.dumps(saved | {"count_ledger": changed}))
    resume = checkpoint.with_name(checkpoint.name + ".resume.json")
    saved_resume = json.loads(resume.read_bytes())
    resume.write_text(json.dumps(saved_resume | {"count_ledger": changed,
                                               "checkpoint_sha256": digest(checkpoint)}))
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert "RESUME_INVALID" in report.diagnostics
    assert not report.checks.resume_verified


def test_marker_symlink_is_refused_before_its_target_is_read(complete_run, monkeypatch):
    from pathlib import Path

    run, ledger, checkpoint = complete_run
    _add_counts(run, ledger, monkeypatch)
    _bind_count_checkpoint(ledger, checkpoint)
    marker = ledger / "counting.json"
    target = run.inside("technical/private-marker-target")
    target.write_text(SENTINEL)
    marker.unlink()
    marker.symlink_to(target)
    original = Path.open

    def protected(path, *args, **kwargs):
        if path == marker:
            raise AssertionError("unsafe marker was opened before validation")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", protected)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert "COUNT_EVIDENCE_INVALID" in report.diagnostics
    assert "RESUME_INVALID" in report.diagnostics


@pytest.mark.parametrize("final_completion", [10790, 10795])
def test_combined_count_and_generation_window_includes_first_count(
    tmp_path, monkeypatch, final_completion
):
    from task9.guards import read_receipts
    from task9.verifier import _ledger_limits, _verified_counts

    run, ledger = _make_run(tmp_path)
    _accept(run, ledger, 0)
    _accept(run, ledger, 1)
    _add_counts(run, ledger, monkeypatch)
    base = STAMP - timedelta(seconds=10800)
    generations = [json.loads(line) for line in (ledger / "attempts.jsonl").read_bytes().splitlines()]
    for index, row in enumerate(generations):
        seconds = (0, 0, 0, 10785, 10785, final_completion)[index]
        row["timestamp"] = (base + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")
    _rewrite_receipts(ledger, generations)

    def span(rows):
        for index, row in enumerate(rows):
            seconds = (-10, 0, 10784, 10784)[index]
            row["timestamp"] = (base + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")
            if row["input_bound"] is not None:
                row["input_bound"]["provider_evidence"]["counted_at"] = row["timestamp"]

    _rewrite_counts(ledger, span)
    receipts = read_receipts(ledger)
    # The initial count adds 10 seconds to an otherwise valid generation window.
    assert _ledger_limits(receipts)
    with pytest.raises(ValueError, match="^COUNT_EVIDENCE_INVALID$"):
        _verified_counts(run, ledger, receipts, run.turns, transport_live=False)
