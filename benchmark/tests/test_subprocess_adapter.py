import sys

import pytest

from systematic_innovation_bench.adapters.subprocess import SubprocessAdapter
from systematic_innovation_bench.models import ConversationTurn, TurnJob


def job():
    return TurnJob(
        job_id="j",
        assistant_turn_index=2,
        transcript=(ConversationTurn(turn_index=1, role="user", content="request"),),
    )


def adapter(code, **updates):
    return SubprocessAdapter(
        (sys.executable, "-c", code),
        frozenset({sys.executable}),
        **({"timeout_seconds": 2} | updates),
    )


def test_allowlist_is_checked_before_execution(tmp_path):
    marker = tmp_path / "should-not-exist"
    with pytest.raises(ValueError):
        SubprocessAdapter(
            (sys.executable, "-c", f"open({str(marker)!r},'w').close()"), frozenset(), 2
        )
    assert not marker.exists()


def test_argument_array_json_roundtrip_and_environment_filtering(monkeypatch):
    secret = "fixture" + "-env-credential"
    monkeypatch.setenv("UNDECLARED_VALUE", secret)
    code = 'import json,sys,os; j=json.load(sys.stdin); print(json.dumps({"job_id":j["job_id"],"turn_index":j["assistant_turn_index"],"content":str("UNDECLARED_VALUE" in os.environ),"output_tokens":1}))'
    result = adapter(code).run_turn(job())
    assert result.content == "False"
    assert result.output_tokens == 1


def test_nonzero_timeout_and_output_limits_are_bounded_and_redacted():
    secret = "fixture" + "-subprocess-credential"
    failed = adapter(
        f"import sys; print({secret!r},file=sys.stderr); sys.exit(2)", secret_values=[secret]
    ).run_turn(job())
    assert failed.status == "failed"
    leaked = secret in failed.model_dump_json()
    assert not leaked
    timed = adapter("import time; time.sleep(5)", timeout_seconds=0.05).run_turn(job())
    assert timed.status == "failed"
    assert "timeout" in timed.error
    limited = adapter('import sys; sys.stdout.write("x"*1000000)', max_output_bytes=128).run_turn(
        job()
    )
    assert limited.status == "failed"
    assert len(limited.raw_response.encode()) <= 128


def test_subprocess_redacts_response_before_optional_canonical_write(tmp_path):
    secret = "fixture" + "-subprocess-credential"
    code = (
        'import json,sys; j=json.load(sys.stdin); print(json.dumps({"job_id":j["job_id"],"turn_index":j["assistant_turn_index"],"content":'
        + repr(secret)
        + ',"output_tokens":1}))'
    )
    path = tmp_path / "canonical.jsonl"
    result = adapter(code, secret_values=[secret], canonical_path=path).run_turn(job())
    assert result.content == "[REDACTED]"
    leaked = secret in path.read_text()
    assert not leaked
