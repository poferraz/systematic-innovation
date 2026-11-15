import json

from systematic_innovation_bench.adapters.inbox import ingest_turn_responses
from systematic_innovation_bench.models import ConversationTurn, TurnJob, TurnResponse
from systematic_innovation_bench.redaction import redact_text
from systematic_innovation_bench.store import append_record


def test_credentials_headers_urls_and_known_values_are_redacted():
    secret = "test" + "-credential-value"
    leaked = secret in redact_text(f"Data {secret}", [secret])
    assert not leaked
    for text in (
        f"Authorization: Bearer {secret}",
        f"Authorization: Basic {secret}",
        f"https://user:{secret}@example.invalid/a",
        f'api_key="{secret}"',
    ):
        leaked = secret in redact_text(text, [])
        assert not leaked
    assert redact_text("unchanged ordinary text", []) == "unchanged ordinary text"


def test_store_is_an_unavoidable_redaction_boundary(tmp_path):
    secret = "test" + "-credential-value"
    path = tmp_path / "raw.jsonl"
    append_record(
        path, TurnResponse(job_id="j", turn_index=2, content=f"Authorization: Bearer {secret}")
    )
    leaked = secret in path.read_text()
    assert not leaked


def test_inbox_redacts_before_canonical_append_and_is_idempotent(tmp_path):
    secret = "fixture" + "-opaque-credential"
    path = tmp_path / "inbox.jsonl"
    canonical = tmp_path / "canonical.jsonl"
    response = TurnResponse(
        job_id="j", turn_index=2, content=secret, raw_response=json.dumps({"text": secret})
    )
    path.write_text(response.model_dump_json() + "\n")
    pending = TurnJob(
        job_id="j",
        assistant_turn_index=2,
        transcript=(ConversationTurn(turn_index=1, role="user", content="context"),),
    )
    result = ingest_turn_responses(
        path, jobs=[pending], canonical_path=canonical, secret_values=[secret]
    )
    ingest_turn_responses(path, jobs=[pending], canonical_path=canonical, secret_values=[secret])
    leaked = secret in canonical.read_text()
    assert not leaked
    assert result[0].content == "[REDACTED]"


def test_json_credential_assignments_and_username_only_urls_are_redacted():
    secret = "fixture" + "-json-credential"
    leaked = secret in redact_text(json.dumps({"api_key": secret}))
    assert not leaked
    leaked = secret in redact_text(f"https://{secret}@example.invalid")
    assert not leaked


def test_basic_prose_and_frozen_skill_are_not_changed_by_redaction():
    from pathlib import Path

    from systematic_innovation_bench.planner import load_skill_pack

    assert redact_text("Basic system understanding") == "Basic system understanding"
    pack = load_skill_pack(Path(__file__).parents[2] / "skills/systematic-innovation")
    assert redact_text(pack) == pack


def test_credential_named_object_values_and_secret_keys_are_redacted():
    from systematic_innovation_bench.redaction import redact_object

    secret = "fixture" + "-object-credential"
    redacted = redact_object({"authorization": secret, "access_token": secret, "ordinary": "fine"})
    leaked = secret in json.dumps(redacted)
    assert not leaked
    assert redacted["ordinary"] == "fine"
    leaked = secret in json.dumps(redact_object({secret: "ordinary"}, [secret]))
    assert not leaked


def test_case_prompt_redaction_does_not_invent_job_digest_fields():
    from systematic_innovation_bench.models import BenchmarkCase
    from systematic_innovation_bench.redaction import redact_model

    secret = "fixture" + "-case-credential"
    case = BenchmarkCase(
        id="c",
        family="open-ended-systemic",
        domain="operations",
        split="development",
        prompt=secret,
        strata={"mode": "quick"},
    )
    assert redact_model(case, [secret]).prompt == "[REDACTED]"
