from __future__ import annotations

from datetime import UTC, datetime

import pytest

from systematic_innovation_bench.models import (
    BenchmarkCase,
    Condition,
    ConversationScript,
    InteractionMode,
    RunConfig,
    TurnResponse,
)
from systematic_innovation_bench.runtime import Dispatch, RunDirectory, prepare
from systematic_innovation_bench.store import append_record, read_records


def make_run(tmp_path, *, count=3, concurrency=1, deep=False, **updates):
    config = RunConfig(
        **(
            {
                "run_id": "runtime",
                "models": ("fake",),
                "model_allowlist": ("fake",),
                "hosts": ("inbox",),
                "conditions": (Condition.VANILLA,),
                "max_calls": 100,
                "max_cost": 10.0,
                "max_concurrency": concurrency,
                "cost_per_turn": {"fake": 0.1},
                "failure_threshold": 1.0,
                "dry_run": False,
            }
            | updates
        )
    )
    cases = [
        BenchmarkCase(
            id=f"c{i}",
            family="open-ended-systemic",
            domain="operations",
            split="development",
            prompt="Shared challenge",
            strata={"mode": "deep" if deep else "quick"},
            interaction_mode=InteractionMode.CONTROLLED_MULTI_TURN
            if deep
            else InteractionMode.SINGLE_TURN,
            conversation_script=ConversationScript(
                user_turns=("Stakeholder constraints", "Resources and final portfolio")
            )
            if deep
            else None,
        )
        for i in range(count)
    ]
    jobs, manifest = prepare(config, cases)
    run = RunDirectory(tmp_path / "run")
    with run.lock():
        run.create(jobs, manifest)
    return run


def packet(turn, **updates):
    return TurnResponse(
        **(
            {
                "job_id": turn.job_id,
                "turn_index": turn.assistant_turn_index,
                "attempt": turn.attempt,
                "content": "Final answer",
                "output_tokens": 10,
                "input_tokens": 2,
                "cost": 0.1,
                "latency_seconds": 0.01,
                "created_at": datetime(2026, 1, 1, tzinfo=UTC),
            }
            | updates
        )
    )


def write_incoming(tmp_path, responses):
    path = tmp_path / "incoming.jsonl"
    path.write_text("".join(response.model_dump_json() + "\n" for response in responses))
    return path


def test_export_caps_outstanding_concurrency_and_does_not_redispatch(tmp_path):
    run = make_run(tmp_path, count=3, concurrency=1)
    assert run.export(run.path / "outgoing-0.jsonl") == 1
    assert len(read_records(run.inside("records/dispatches.jsonl"), Dispatch)) == 1
    assert run.export(run.path / "outgoing-1.jsonl") == 0
    assert not (run.path / "outgoing-1.jsonl").exists()


def test_failed_export_path_does_not_consume_dispatches(tmp_path):
    run = make_run(tmp_path)
    with pytest.raises(ValueError):
        run.export(tmp_path / "outside.jsonl")
    assert not run.inside("records/dispatches.jsonl").exists()
    run.verify()


def test_valid_durable_tail_after_crash_resumes_but_old_bytes_cannot_change(tmp_path):
    run = make_run(tmp_path, count=1, deep=True)
    run.export(run.path / "first.jsonl")
    first = run.pending()[0]
    run.ingest(write_incoming(tmp_path, [packet(run.opaque(first))]))
    run.export(run.path / "second.jsonl")
    second = run.pending()[0]
    append_record(run.inside("records/turns.jsonl"), packet(second))  # Crash before next snapshot.
    run.verify()
    assert run.pending()[0].assistant_turn_index == 6
    path = run.inside("records/turns.jsonl")
    path.write_bytes(path.read_bytes().replace(b"Final answer", b"Wrong answer", 1))
    with pytest.raises(ValueError):
        run.verify()


def test_ingest_is_idempotent_and_changed_accepted_response_is_rejected(tmp_path):
    run = make_run(tmp_path, count=1)
    run.export(run.path / "outgoing.jsonl")
    original = packet(run.opaque(run.pending()[0]))
    incoming = write_incoming(tmp_path, [original])
    assert run.ingest(incoming) == 1
    before = run.inside("records/turns.jsonl").read_bytes()
    assert run.ingest(incoming) == 0
    assert run.inside("records/turns.jsonl").read_bytes() == before
    with pytest.raises(ValueError):
        run.ingest(write_incoming(tmp_path, [original.model_copy(update={"content": "altered"})]))
    assert run.inside("records/turns.jsonl").read_bytes() == before


def test_entire_ingest_batch_is_validated_before_any_append(tmp_path):
    run = make_run(tmp_path, count=3, concurrency=2)
    run.export(run.path / "outgoing.jsonl")
    pending = run.pending()
    incoming = write_incoming(
        tmp_path, [packet(run.opaque(pending[0])), packet(run.opaque(pending[2]))]
    )
    with pytest.raises(ValueError):
        run.ingest(incoming)
    assert not run.inside("records/turns.jsonl").exists()
    run.verify()


def test_unsnapshotted_turn_without_dispatch_is_never_accepted_as_crash_recovery(tmp_path):
    run = make_run(tmp_path, count=1)
    append_record(run.inside("records/turns.jsonl"), packet(run.pending()[0]))
    with pytest.raises(ValueError):
        run.verify()


def test_malformed_appended_tail_is_rejected(tmp_path):
    run = make_run(tmp_path, count=1)
    run.export(run.path / "outgoing.jsonl")
    path = run.inside("records/turns.jsonl")
    path.write_text("{}\n")
    with pytest.raises(ValueError):
        run.verify()


def test_reported_cost_ceiling_breach_stops_future_calls_and_records_budget_status(tmp_path):
    run = make_run(tmp_path, count=2)
    run.export(run.path / "outgoing.jsonl")
    turn = run.pending()[0]
    run.ingest(write_incoming(tmp_path, [packet(run.opaque(turn), cost=0.2)]))
    before = run.inside("records/dispatches.jsonl").read_bytes()
    with pytest.raises(ValueError, match="COST_CEILING_EXCEEDED"):
        run.export(run.path / "blocked.jsonl")
    assert run.inside("records/dispatches.jsonl").read_bytes() == before
    assert [(r.status, r.error) for r in run.responses] == [
        ("succeeded", None),
        ("budget-stopped", "COST_CEILING_EXCEEDED"),
    ]
    assert run.pending() == []
    run.verify()


def test_failure_threshold_stops_retries_and_all_future_calls(tmp_path):
    run = make_run(tmp_path, count=2, failure_threshold=0.2)
    run.export(run.path / "first.jsonl")
    run.ingest(write_incoming(tmp_path, [packet(run.opaque(run.pending()[0]), status="failed")]))
    with pytest.raises(ValueError, match="FAILURE_THRESHOLD"):
        run.export(run.path / "blocked.jsonl")
    assert len(read_records(run.inside("records/dispatches.jsonl"), Dispatch)) == 1
    assert all(
        r.status == "budget-stopped" and r.error == "FAILURE_THRESHOLD" for r in run.responses
    )
    run.verify()


def test_retry_exhaustion_preserves_every_attempt_and_total_tokens(tmp_path):
    run = make_run(tmp_path, count=1, retry_limit=1)
    for index in range(2):
        assert run.export(run.path / f"attempt-{index}.jsonl") == 1
        turn = run.pending()[0]
        assert turn.attempt == index
        run.ingest(write_incoming(tmp_path, [packet(run.opaque(turn), status="failed")]))
    assert run.pending() == []
    assert len(run.turns) == 2
    assert len(run.responses) == 1
    assert run.responses[0].status == "failed"
    assert run.responses[0].output_tokens == 20
    run.verify()


def test_adapter_budget_stop_is_terminal_and_preserves_all_attempt_accounting(tmp_path):
    run = make_run(tmp_path, count=1, deep=True, retry_limit=1)
    run.export(run.path / "first.jsonl")
    run.ingest(write_incoming(tmp_path, [packet(run.opaque(run.pending()[0]))]))
    run.export(run.path / "second.jsonl")
    turn = run.pending()[0]
    run.ingest(
        write_incoming(
            tmp_path, [packet(run.opaque(turn), status="budget-stopped", output_tokens=7)]
        )
    )
    assert run.pending() == []
    before = run.inside("records/dispatches.jsonl").read_bytes()
    assert run.export(run.path / "after-stop.jsonl") == 0
    assert run.inside("records/dispatches.jsonl").read_bytes() == before
    assert len(run.turns) == 2
    assert len(run.responses) == 1
    assert run.responses[0].status == "budget-stopped"
    assert run.responses[0].output_tokens == 17
    run.verify()


@pytest.mark.parametrize("operation", ["export", "ingest", "execute", "reserve", "finalize"])
def test_changed_runner_source_stops_mutation_before_new_dispatch(tmp_path, monkeypatch, operation):
    from systematic_innovation_bench import runtime

    run = make_run(tmp_path, count=1)
    turn = run.pending()[0]
    incoming = write_incoming(tmp_path, [packet(run.opaque(turn))])
    monkeypatch.setattr(runtime, "current_source_digest", lambda: "0" * 64)
    with pytest.raises(ValueError, match="source"):
        if operation == "export":
            run.export(run.path / "blocked.jsonl")
        elif operation == "ingest":
            run.ingest(incoming)
        elif operation == "execute":
            run.execute()
        elif operation == "reserve":
            run.reserve(turn)
        else:
            run.pending(finalize=True)
    assert not run.inside("records/dispatches.jsonl").exists()
    assert not run.inside("records/turns.jsonl").exists()
