"""Count claims and their receipts cannot disappear into a permitted retry."""
import hashlib
import json
import shutil
from datetime import UTC, datetime

import pytest

from systematic_innovation_bench.runtime import canonical_digest
from task9.contracts import InputBound, ProviderCountEvidence


def bound():
    raw = '{"input_tokens":100,"object":"response.input_tokens"}'
    return InputBound(
        tokens=100, request_sha256="a" * 64, profile_sha256="b" * 64,
        provider_evidence=ProviderCountEvidence(
            count_request_sha256="c" * 64, account_id="account", project_id="project",
            request_id="request-count", response_json=raw,
            response_sha256=hashlib.sha256(raw.encode()).hexdigest(),
            counted_at=datetime.now(UTC),
        ),
    )


def begin(tmp_path):
    from task9.count_ledger import CountLedger
    ledger = CountLedger(tmp_path / "worker")
    values = {"turn_id": "d" * 64 + ":2:0", "request_sha256": "a" * 64,
              "count_request_sha256": "c" * 64, "profile_sha256": "b" * 64,
              "account_id": "account", "project_id": "project"}
    ledger.start(**values)
    return ledger, values


def test_count_start_is_durable_and_completion_binds_exact_evidence(tmp_path):
    from task9.count_ledger import read_count_receipts
    ledger, _values = begin(tmp_path)
    assert [r.event for r in read_count_receipts(tmp_path / "worker")] == ["started"]
    result = bound()
    ledger.complete(result)
    rows = read_count_receipts(tmp_path / "worker")
    assert [r.event for r in rows] == ["started", "completed"]
    assert rows[-1].input_bound == result
    assert rows[-1].previous_sha256 == rows[0].sha256


@pytest.mark.parametrize("damage", ["journal", "claim", "directory", "anchor", "tail", "hash"])
def test_deleted_or_changed_count_evidence_cannot_be_retried(tmp_path, damage):
    from task9.count_ledger import read_count_receipts
    from task9.guards import Task9Error
    ledger, _values = begin(tmp_path)
    ledger.complete(bound())
    root = tmp_path / "worker"
    journal = root / "counts/attempts.jsonl"
    if damage == "journal":
        journal.unlink()
    elif damage == "claim":
        next((root / "counts/claims").glob("*.json")).unlink()
    elif damage == "directory":
        shutil.rmtree(root / "counts")
    elif damage == "anchor":
        (root / "counting.json").unlink()
    elif damage == "tail":
        journal.write_bytes(journal.read_bytes().rstrip(b"\n"))
    else:
        rows = journal.read_text().splitlines()
        changed = json.loads(rows[-1])
        changed["input_bound"]["tokens"] = 99
        changed["sha256"] = canonical_digest({k: v for k, v in changed.items() if k != "sha256"})
        journal.write_text(rows[0] + "\n" + json.dumps(changed) + "\n")
    with pytest.raises(Task9Error, match="^TASK9_COUNT_LEDGER_INTEGRITY$"):
        read_count_receipts(root)


def test_orphan_count_claim_blocks_recovery(tmp_path):
    from task9.count_ledger import read_count_receipts
    from task9.guards import Task9Error
    _ledger, _values = begin(tmp_path)
    (tmp_path / "worker/counts/attempts.jsonl").unlink()
    with pytest.raises(Task9Error, match="^TASK9_COUNT_LEDGER_INTEGRITY$"):
        read_count_receipts(tmp_path / "worker")


def test_seventy_metadata_attempts_do_not_authorize_a_seventy_first(tmp_path):
    from task9.count_ledger import CountLedger, read_count_receipts
    from task9.guards import Task9Error
    ledger = CountLedger(tmp_path / "worker")
    for number in range(70):
        ledger.start(turn_id=f"{number:064x}:2:0", request_sha256="a" * 64,
                     count_request_sha256="c" * 64, profile_sha256="b" * 64,
                     account_id="account", project_id="project")
        ledger.complete(bound())
    before = (tmp_path / "worker/counts/attempts.jsonl").read_bytes()
    with pytest.raises(Task9Error, match="^TASK9_COUNT_ATTEMPT_REFUSED$"):
        ledger.start(turn_id=f"{70:064x}:2:0", request_sha256="a" * 64,
                     count_request_sha256="c" * 64, profile_sha256="b" * 64,
                     account_id="account", project_id="project")
    assert len(read_count_receipts(tmp_path / "worker")) == 140
    assert (tmp_path / "worker/counts/attempts.jsonl").read_bytes() == before
