"""Explicit Task 9 readiness operations; no command creates a live approval."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Literal

import yaml

from systematic_innovation_bench.models import TurnJob, TurnResponse
from systematic_innovation_bench.runtime import REPOSITORY_ROOT, RunDirectory
from systematic_innovation_bench.store import read_records


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="python -m task9", description="Paused Task 9 readiness tools")
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("bindings", "process", "checkpoint", "resume-proof", "verify"):
        item = sub.add_parser(name)
        item.add_argument("--run-dir", type=Path, required=True)
        if name != "bindings":
            item.add_argument("--mode", choices=("offline", "live"), default="offline")
        if name in ("process", "verify"):
            item.add_argument("--approval", type=Path, required=True)
        if name == "process":
            item.add_argument("--outbox", type=Path, required=True)
            item.add_argument("--output", type=Path, required=True)
            item.add_argument("--fixtures", type=Path)
            item.add_argument("--tokenizer-resource", type=Path)
            item.add_argument("--account-id")
            item.add_argument("--project-id")
        if name in ("checkpoint", "resume-proof", "verify"):
            item.add_argument("--checkpoint", type=Path, required=True)
        if name == "verify":
            item.add_argument("--markdown", type=Path, required=True)
            item.add_argument("--json", type=Path, required=True)
            item.add_argument("--generate-standard-reports", action="store_true")
    return root


def _check_live_pause(mode: str) -> None:
    if mode != "live":
        return
    path = REPOSITORY_ROOT / "benchmark/study/stage-gates.yaml"
    gates = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(gates, dict) or gates.get("execution_authorized") is not True:
        raise ValueError("LIVE_EXECUTION_PAUSED")


def _response_output(run: RunDirectory, args: argparse.Namespace) -> Path:
    output = run.inside(args.output)
    exchange = run.inside("exchange")
    inputs = [run.inside(args.outbox), run.inside(args.approval)]
    inputs.extend(Path(value).resolve() for value in (args.fixtures, args.tokenizer_resource)
                  if value is not None)
    if (output == exchange or not output.is_relative_to(exchange)
            or any(output == item or (output.exists() and item.exists()
                                      and output.samefile(item)) for item in inputs)):
        raise ValueError("TASK9_OUTPUT_PATH_INVALID")
    ancestor = output.parent
    while ancestor != run.path:
        if ancestor.exists() and not ancestor.is_dir():
            raise ValueError("TASK9_OUTPUT_PATH_INVALID")
        ancestor = ancestor.parent
    return output


def _preflight_response_output(output: Path, guard: Any, job: TurnJob) -> None:
    """An existing response is reusable only through verified completed receipts."""
    if not output.exists():
        return
    records = guard.records()  # Verifies receipt chain and cached response digests.
    matching = [record for record in records if record.turn_id == job.turn_id]
    if not matching or matching[-1].event != "completed" or matching[-1].response_path is None:
        raise ValueError("TASK9_OUTPUT_REPLACEMENT_REFUSED")
    cached_path = guard.run.inside(guard.ledger_root / matching[-1].response_path)
    cached = TurnResponse.model_validate_json(cached_path.read_bytes())
    expected = (cached.model_dump_json() + "\n").encode()
    if output.read_bytes() != expected:
        raise ValueError("TASK9_OUTPUT_REPLACEMENT_REFUSED")


def _exclusive_response(path: Path, payload: bytes) -> None:
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError("TASK9_OUTPUT_REPLACEMENT_REFUSED")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def dispatch(args: argparse.Namespace) -> dict[str, Any]:
    from .contracts import ExecutionApproval
    from .guards import Task9Guard, approval_bindings

    raw_mode = getattr(args, "mode", "offline")
    mode: Literal["offline", "live"]
    if raw_mode == "offline":
        mode = "offline"
    elif raw_mode == "live":
        mode = "live"
    else:
        raise ValueError("TASK9_EXECUTION_MODE_INVALID")
    _check_live_pause(mode)  # Before reading an approval, run, input, fixture or credential.
    run = RunDirectory(args.run_dir)
    run.verify()
    if args.command == "bindings":
        return {"bindings": approval_bindings(run), "live_execution_authorized": False}
    ledger = run.inside("worker")
    if args.command == "process":
        from .worker import Worker

        output = _response_output(run, args)
        approval = ExecutionApproval.model_validate_json(run.inside(args.approval).read_bytes())
        if approval.mode != mode:
            raise ValueError("TASK9_EXECUTION_MODE_MISMATCH")
        if not args.account_id or not args.project_id:
            raise ValueError("TASK9_TRANSPORT_IDENTITY_REQUIRED")
        jobs = read_records(run.inside(args.outbox), TurnJob)
        if len(jobs) != 1:
            raise ValueError("TASK9_ONE_REQUEST_REQUIRED")
        guard = Task9Guard(run, approval, ledger_root=ledger,
                           transport_account_id=args.account_id,
                           transport_project_id=args.project_id)
        _preflight_response_output(output, guard, jobs[0])
        if mode == "offline":
            from .replay import ReplayBundle

            if args.fixtures is None or args.tokenizer_resource is not None:
                raise ValueError("TASK9_OFFLINE_REPLAY_REQUIRED")
            replay = ReplayBundle.load(args.fixtures)
            worker = Worker(guard, replay, replay)
        else:
            from .tokens import LocalInputCounter
            from .transport import HTTPTransport

            if args.tokenizer_resource is None or args.fixtures is not None:
                raise ValueError("TASK9_LIVE_COUNTER_REQUIRED")
            worker = Worker(guard, HTTPTransport(account_id=args.account_id,
                            project_id=args.project_id), LocalInputCounter(args.tokenizer_resource))
        response = worker.process(jobs[0])
        _exclusive_response(output, (response.model_dump_json()+"\n").encode())
        return {"mode": mode, "responses": 1, "live_execution_authorized": False}
    from .verifier import create_resume_checkpoint, record_resume

    checkpoint = run.inside(args.checkpoint)
    if args.command == "checkpoint":
        create_resume_checkpoint(run, worker_ledger=ledger, output=checkpoint)
        return {"mode": mode, "checkpoint_created": True}
    if args.command == "resume-proof":
        record_resume(run, worker_ledger=ledger, checkpoint=checkpoint)
        return {"mode": mode, "resume_recorded": True}
    from .verifier import generate_isolated_reports, verify_technical_run, write_technical_report

    if args.generate_standard_reports:
        generate_isolated_reports(run)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint,
                                  mode=mode, approval=args.approval)
    digests = write_technical_report(report, run.inside(args.markdown), run.inside(args.json))
    run.snapshot()
    return {"mode": mode, "report_digests": digests, "decision": report.decision,
            "technical_checks_passed": report.technical_checks_passed,
            "scientific_gate_passed": False, "live_execution_authorized": False}


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = dispatch(args)
    except (ValueError, OSError, KeyError, TypeError, RuntimeError, yaml.YAMLError) as error:
        from .guards import Task9Error

        code = error.code if isinstance(error, Task9Error) else "TASK9_OPERATION_REFUSED"
        if isinstance(error, ValueError) and error.args == ("LIVE_EXECUTION_PAUSED",):
            code = "LIVE_EXECUTION_PAUSED"
        print(json.dumps({"error": code}))
        return 1
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 1 if result.get("technical_checks_passed") is False else 0
