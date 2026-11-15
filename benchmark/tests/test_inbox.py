import pytest

from systematic_innovation_bench.adapters.inbox import (
    export_turn_jobs,
    ingest_turn_responses,
    validate_turn_correlation,
)
from systematic_innovation_bench.models import ConversationTurn, TurnJob, TurnResponse
from systematic_innovation_bench.store import read_records


def job(id="j", index=2, attempt=0):
    transcript = tuple(
        ConversationTurn(turn_index=i, role="user" if i % 2 else "assistant", content=str(i))
        for i in range(1, index)
    )
    return TurnJob(job_id=id, assistant_turn_index=index, transcript=transcript, attempt=attempt)


def test_export_ingest_and_safe_reingestion(tmp_path):
    jobs = [job("a"), job("b")]
    out = tmp_path / "out.jsonl"
    export_turn_jobs(jobs, out)
    export_turn_jobs(jobs, out)
    assert len(read_records(out, TurnJob)) == 2
    inbox = tmp_path / "in.jsonl"
    inbox.write_text(
        "\n".join(
            TurnResponse(
                job_id=j.job_id, turn_index=2, content="response", raw_response="raw"
            ).model_dump_json()
            for j in jobs
        )
        + "\n"
    )
    canonical = tmp_path / "canonical.jsonl"
    responses = ingest_turn_responses(inbox, jobs=jobs, canonical_path=canonical)
    assert len(responses) == 2
    ingest_turn_responses(inbox, jobs=jobs, canonical_path=canonical)
    assert len(read_records(canonical, TurnResponse)) == 2


@pytest.mark.parametrize(
    "responses",
    [
        [TurnResponse(job_id="unknown", turn_index=2, content="text")],
        [TurnResponse(job_id="j", turn_index=4, content="text")],
        [TurnResponse(job_id="j", turn_index=2, content="text", attempt=1)],
        [TurnResponse(job_id="j", turn_index=2, content="text")] * 2,
        [TurnResponse(job_id="j", turn_index=2, content="")],
    ],
)
def test_correlation_rejects_unknown_out_of_order_duplicate_and_empty(responses):
    with pytest.raises(ValueError):
        validate_turn_correlation([job()], responses)


def test_malformed_nonterminal_and_missing_content_leave_no_canonical_writes(tmp_path):
    path = tmp_path / "input.jsonl"
    canonical = tmp_path / "canonical.jsonl"
    for line in (
        "bad",
        '{"job_id":"j","turn_index":2,"content":"x","status":"pending"}',
        '{"job_id":"j","turn_index":2}',
    ):
        path.write_text(line + "\n")
        with pytest.raises(ValueError):
            ingest_turn_responses(path, jobs=[job()], canonical_path=canonical)
        assert not canonical.exists()
