from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_task9_integration import prepared as integration_prepared

from task9.cli import dispatch, main, parser
from task9.worker import Worker

# Reuse the real prepared-run fixture without duplicating setup.
prepared = integration_prepared

ROOT = Path(__file__).resolve().parents[1]


def command(*args):
    return subprocess.run([sys.executable,"-m","task9",*args],cwd=ROOT,
                          capture_output=True,text=True,check=False,
                          env={k:v for k,v in os.environ.items() if k in
                               {"PATH","PYTHONPATH","SYSTEMROOT","TMPDIR","LANG","LC_ALL"}})


def test_help_lists_only_explicit_commands_and_does_not_create_evidence(tmp_path):
    result=command("--help")
    assert result.returncode==0
    for name in ("bindings","process","checkpoint","resume-proof","verify"):
        assert name in result.stdout
    assert not list(tmp_path.iterdir())


def test_live_process_fails_closed_with_current_pause_before_files_or_credentials(tmp_path):
    output=tmp_path/"must-not-exist.jsonl"
    result=command("process","--run-dir",str(tmp_path/"absent-run"),"--approval",str(tmp_path/"absent-approval.json"),
                   "--outbox",str(tmp_path/"absent-outbox.jsonl"),"--output",str(output),"--mode","live")
    assert result.returncode!=0
    assert "Traceback" not in result.stderr
    assert "LIVE_EXECUTION_PAUSED" in result.stdout
    assert not output.exists()


def process_args(prepared, output):
    run, approval, fixture, _replay, _guard = prepared
    outgoing = run.inside("exchange/request.jsonl")
    run.export(outgoing)
    values = ["process", "--run-dir", str(run.path), "--approval", str(approval),
              "--outbox", str(outgoing), "--output", str(run.inside(output)),
              "--fixtures", str(fixture), "--account-id", "offline-account",
              "--project-id", "offline-project"]
    return parser().parse_args(values)


def forbid_worker(monkeypatch):
    def unexpected(self, job):
        raise AssertionError("worker reached before output preflight")
    monkeypatch.setattr(Worker, "process", unexpected)


@pytest.mark.parametrize("output", [
    "records/turns.jsonl", "records/responses.jsonl", "manifest.json",
    "worker/attempts.jsonl", "integrity.json",
])
def test_process_output_cannot_bypass_ingest_or_replace_control_files(prepared, monkeypatch, output):
    run, _approval, _fixture, _replay, guard = prepared
    args = process_args(prepared, output)
    before = {path: path.read_bytes() for path in run.path.rglob("*") if path.is_file()}
    forbid_worker(monkeypatch)
    with pytest.raises(ValueError, match="^TASK9_OUTPUT_PATH_INVALID$"):
        dispatch(args)
    assert guard.records() == []
    assert {path: path.read_bytes() for path in run.path.rglob("*") if path.is_file()} == before
    assert run.verify()["jobs"] == 30


def test_conflicting_exchange_output_is_rejected_before_any_attempt(prepared, monkeypatch):
    run, _approval, _fixture, _replay, guard = prepared
    args = process_args(prepared, "exchange/response.jsonl")
    output = run.inside(args.output)
    output.write_text("conflicting existing evidence\n")
    forbid_worker(monkeypatch)
    with pytest.raises(ValueError, match="^TASK9_OUTPUT_REPLACEMENT_REFUSED$"):
        dispatch(args)
    assert output.read_text() == "conflicting existing evidence\n"
    assert guard.records() == []


@pytest.mark.parametrize("source", ["outbox", "approval", "fixtures"])
def test_output_cannot_replace_any_process_input_even_inside_exchange(prepared, monkeypatch, source):
    run, approval, fixture, _replay, guard = prepared
    args = process_args(prepared, "exchange/response.jsonl")
    if source == "outbox":
        args.output = args.outbox
    else:
        original = approval if source == "approval" else fixture
        moved = run.inside("exchange/" + original.name)
        moved.write_bytes(original.read_bytes())
        setattr(args, source, moved)
        args.output = moved
    forbid_worker(monkeypatch)
    with pytest.raises(ValueError, match="^TASK9_OUTPUT_PATH_INVALID$"):
        dispatch(args)
    assert guard.records() == []


@pytest.mark.parametrize("passed,decision,expected_exit", [
    (False, "stopped-incomplete", 1), (True, "offline-rehearsal-complete", 0),
])
def test_verify_summary_exposes_decision_and_returns_failure_for_incomplete(
    prepared, monkeypatch, capsys, passed, decision, expected_exit
):
    run, approval, _fixture, _replay, _guard = prepared
    report = SimpleNamespace(decision=decision, technical_checks_passed=passed)
    monkeypatch.setattr("task9.verifier.verify_technical_run", lambda *args, **kwargs: report)
    monkeypatch.setattr("task9.verifier.write_technical_report", lambda *args: {"json": "a" * 64})
    result = main(["verify", "--run-dir", str(run.path), "--approval", str(approval),
                   "--checkpoint", "worker/checkpoint.json", "--markdown", "reports/technical.md",
                   "--json", "reports/technical.json"])
    assert result == expected_exit
    emitted = json.loads(capsys.readouterr().out)
    assert emitted["decision"] == decision
    assert emitted["technical_checks_passed"] is passed
    assert emitted["scientific_gate_passed"] is False
    assert emitted["live_execution_authorized"] is False


def test_identical_existing_output_is_reused_only_with_verified_completed_receipt(prepared, monkeypatch):
    run, _approval, _fixture, _replay, guard = prepared
    args = process_args(prepared, "exchange/response.jsonl")
    dispatch(args)
    output = run.inside(args.output)
    before = output.read_bytes()
    ledger_before = run.inside("worker/attempts.jsonl").read_bytes()
    def no_send(*args, **kwargs):
        raise AssertionError("cached response resubmitted")
    monkeypatch.setattr("task9.replay.ReplayBundle.send", no_send)
    assert dispatch(args)["responses"] == 1
    assert output.read_bytes() == before
    assert run.inside("worker/attempts.jsonl").read_bytes() == ledger_before
    assert guard.verify()["attempts"] == 1


def test_changed_existing_output_with_valid_receipt_is_refused_before_worker(prepared, monkeypatch):
    run, _approval, _fixture, _replay, guard = prepared
    args = process_args(prepared, "exchange/response.jsonl")
    dispatch(args)
    output = run.inside(args.output)
    output.write_bytes(output.read_bytes() + b"changed")
    forbid_worker(monkeypatch)
    with pytest.raises(ValueError, match="^TASK9_OUTPUT_REPLACEMENT_REFUSED$"):
        dispatch(args)
    assert guard.verify()["attempts"] == 1


def test_existing_file_ancestor_is_rejected_before_worker_or_attempt(prepared, monkeypatch):
    run, _approval, _fixture, _replay, guard = prepared
    args = process_args(prepared, "exchange/request.jsonl/response.jsonl")
    outgoing_before = run.inside(args.outbox).read_bytes()
    forbid_worker(monkeypatch)
    with pytest.raises(ValueError, match="^TASK9_OUTPUT_PATH_INVALID$"):
        dispatch(args)
    assert guard.records() == []
    assert run.inside(args.outbox).read_bytes() == outgoing_before
