import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest

from systematic_innovation_bench.models import ResponseRecord, TurnResponse
from systematic_innovation_bench.store import (
    append_record,
    read_records,
    terminal_job_ids,
    turn_responses_for_job,
)


def append_unique(args):
    path, index = args
    append_record(
        Path(path), ResponseRecord(job_id=f"j{index}", status="succeeded", content="text")
    )


def test_append_is_jsonl_fsynced_and_does_not_overwrite(tmp_path):
    path = tmp_path / "records.jsonl"
    first = ResponseRecord(job_id="a", status="succeeded", content="first\nsecond")
    with patch("os.fsync", wraps=__import__("os").fsync) as fsync:
        append_record(path, first)
        assert fsync.call_count == 1
    prefix = path.read_bytes()
    append_record(path, ResponseRecord(job_id="b", status="refused"))
    assert path.read_bytes().startswith(prefix)
    assert len(path.read_text().splitlines()) == 2
    assert read_records(path, ResponseRecord)[0] == first
    assert terminal_job_ids(read_records(path, ResponseRecord)) == frozenset({"a", "b"})


def test_retry_preservation_and_duplicate_terminal_rejection(tmp_path):
    path = tmp_path / "records.jsonl"
    failed = ResponseRecord(job_id="j", status="failed", attempt=0)
    append_record(path, failed)
    append_record(path, ResponseRecord(job_id="j", status="succeeded", attempt=1))
    with pytest.raises(ValueError, match="duplicate"):
        append_record(path, ResponseRecord(job_id="j", status="succeeded", attempt=1))
    with pytest.raises(ValueError):
        append_record(path, ResponseRecord(job_id="j", status="succeeded", attempt=2))
    assert len(read_records(path, ResponseRecord)) == 2


def test_turn_retrieval_preserves_retries_and_orders_by_turn(tmp_path):
    path = tmp_path / "turns.jsonl"
    for job, index, attempt, status in (
        ("a", 2, 0, "failed"),
        ("a", 2, 1, "succeeded"),
        ("b", 2, 0, "succeeded"),
        ("a", 4, 0, "succeeded"),
    ):
        append_record(
            path,
            TurnResponse(job_id=job, turn_index=index, content="x", attempt=attempt, status=status),
        )
    turns = turn_responses_for_job(read_records(path, TurnResponse), "a")
    assert [(t.turn_index, t.attempt) for t in turns] == [(2, 0), (2, 1), (4, 0)]


def test_malformed_records_name_line_but_never_contents(tmp_path):
    path = tmp_path / "bad.jsonl"
    marker = "private" + "-synthetic-marker"
    path.write_text(json.dumps({"job_id": "j", "status": "failed"}) + "\n" + marker)
    with pytest.raises(ValueError, match="line 2") as caught:
        read_records(path, ResponseRecord)
    assert marker not in str(caught.value)


def test_process_writers_are_locked_and_symlink_is_rejected(tmp_path):
    path = tmp_path / "many.jsonl"
    with ProcessPoolExecutor(max_workers=3) as pool:
        list(pool.map(append_unique, [(str(path), index) for index in range(18)]))
    assert len(read_records(path, ResponseRecord)) == 18
    link = tmp_path / "link.jsonl"
    link.symlink_to(path)
    with pytest.raises((ValueError, OSError)):
        append_record(link, ResponseRecord(job_id="symlink", status="succeeded"))
