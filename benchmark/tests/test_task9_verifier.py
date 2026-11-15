from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from systematic_innovation_bench.models import TurnResponse
from systematic_innovation_bench.runtime import (
    RunDirectory,
    canonical_digest,
    load_config,
    prepare,
    public_cases,
)

ROOT = Path(__file__).resolve().parents[1]
CASES = ('syn-dev-001', 'red-dev-001', 'sys-dev-001', 'pre-dev-001',
         'tri-dev-001', 'adv-dev-001')
SENTINEL = 'PRIVATE_FIXTURE_NEVER_IN_TECHNICAL_SUMMARY'


def _receipt(ledger, event, turn, response_path=None, response_sha256=None):
    from task9.worker import build_payload

    request_hash = canonical_digest(build_payload(turn))
    path = ledger / 'attempts.jsonl'
    prior = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    value = {
        'seq': len(prior) + 1, 'event': event, 'turn_id': turn.turn_id,
        'request_sha256': request_hash, 'reserved_micro_usd': 50000,
        'charged_micro_usd': 240 if event == 'completed' else None,
        'response_path': response_path, 'response_sha256': response_sha256,
        'error': None, 'timestamp': '2026-11-15T00:00:00Z',
        'previous_sha256': prior[-1]['sha256'] if prior else '0' * 64,
    }
    value['sha256'] = canonical_digest(value)
    with path.open('a') as stream:
        stream.write(json.dumps(value, separators=(',', ':')) + '\n')


def _make_run(tmp_path):
    config = load_config(ROOT / 'configs/feasibility-six.proposed.yaml')
    config = config.model_copy(update={'run_id': 'offline-verifier', 'dry_run': False})
    jobs, manifest = prepare(config, public_cases(ROOT / 'cases/development', CASES))
    run = RunDirectory(tmp_path / 'run')
    with run.lock():
        run.create(jobs, manifest)
    ledger = run.inside('worker')
    ledger.mkdir()
    return run, ledger


def _accept(run, ledger, index, *, status='succeeded', output_tokens=20):
    assert run.export(run.inside(f'exchange/request-{index}.jsonl')) == 1
    pending = run.pending()[0]
    turn = run.opaque(pending)
    raw = {
        'id': f'resp_fixture_{index}', 'model': 'gpt-5.4-mini-2026-03-17',
        'service_tier': 'default', 'status': 'completed',
        'usage': {'input_tokens': 200, 'output_tokens': output_tokens,
                  'input_tokens_details': {'cached_tokens': 0},
                  'output_tokens_details': {'reasoning_tokens': 0}},
        'output': [{'type': 'message', 'role': 'assistant', 'status': 'completed',
                    'content': ([{'type': 'refusal', 'refusal': SENTINEL + f' turn {turn.assistant_turn_index} final answer'}]
                                if status == 'refused' else
                                [{'type': 'output_text', 'text': SENTINEL + f' turn {turn.assistant_turn_index} final answer'}])}],
    }
    raw = {'provider_response': raw, 'request_id': f'req_fixture_{index}',
           'http_status': 200, 'cost_provenance': {
               'kind': 'calculated-token-rate-upper-bound', 'currency': 'USD',
               'input_rate_usd_per_million': '0.75', 'output_rate_usd_per_million': '4.50',
               'basis': 'provider-total-tokens; uncached input rate; reasoning not added again'}}
    response = TurnResponse(
        job_id=turn.job_id, turn_index=turn.assistant_turn_index,
        content=SENTINEL + f' turn {turn.assistant_turn_index} final answer', status=status, input_tokens=200,
        output_tokens=output_tokens, cost=0.00024, latency_seconds=0.01,
        raw_response=json.dumps(raw),
    )
    target = ledger / ('responses/' + hashlib.sha256(turn.turn_id.encode()).hexdigest() + '.json')
    target.parent.mkdir(exist_ok=True)
    from task9.worker import build_payload

    claims = ledger / 'claims'
    claims.mkdir(exist_ok=True)
    (claims / (hashlib.sha256(turn.turn_id.encode()).hexdigest() + '.json')).write_text(
        json.dumps({'turn_id': turn.turn_id, 'request_sha256': canonical_digest(build_payload(turn))}))
    target.write_text(response.model_dump_json() + '\n')
    for event in ('reserved', 'dispatched'):
        _receipt(ledger, event, turn)
    _receipt(ledger, 'completed', turn, target.relative_to(ledger).as_posix(),
             hashlib.sha256(target.read_bytes()).hexdigest())
    incoming = run.inside(f'exchange/response-{index}.jsonl')
    incoming.write_text(response.model_dump_json() + '\n')
    run.ingest(incoming)


def _resume_in_fresh_process(run, ledger, checkpoint):
    code = ('from pathlib import Path; from systematic_innovation_bench.runtime import RunDirectory; '
            'from task9.verifier import record_resume; '
            f'record_resume(RunDirectory(Path({str(run.path)!r})), '
            f'worker_ledger=Path({str(ledger)!r}), checkpoint=Path({str(checkpoint)!r}))')
    result = subprocess.run([sys.executable, '-c', code], cwd=ROOT,
                            env={**os.environ, 'PYTHONPATH': f'{ROOT / "src"}:{ROOT}'},
                            capture_output=True, check=False)
    assert result.returncode == 0


@pytest.fixture(scope="module")
def complete_template(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("template")
    from task9.verifier import create_resume_checkpoint, generate_isolated_reports

    run, ledger = _make_run(tmp_path)
    _accept(run, ledger, 0, status='refused')
    checkpoint = run.inside('technical/checkpoint.json')
    create_resume_checkpoint(run, worker_ledger=ledger, output=checkpoint)
    _resume_in_fresh_process(run, ledger, checkpoint)
    for index in range(1, 70):
        _accept(run, ledger, index)
    generate_isolated_reports(run)
    return run, ledger, checkpoint


@pytest.fixture
def complete_run(complete_template, tmp_path):
    original, _, _ = complete_template
    target = tmp_path / "run"
    shutil.copytree(original.path, target)
    return RunDirectory(target), target / "worker", target / "technical/checkpoint.json"


def test_offline_complete_run_is_content_free_and_never_advances_science(complete_run):
    from task9.verifier import verify_technical_run, write_technical_report

    run, ledger, checkpoint = complete_run
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert report.decision == 'offline-rehearsal-complete', report.diagnostics
    assert report.scientific_gate_passed is False
    assert report.live_execution_authorized is False
    assert report.coverage.parent_jobs == 30
    assert report.coverage.accepted_turns == 70
    assert report.resources.input_tokens == 14000
    assert report.resources.output_tokens == 1400
    assert report.resources.calculated_upper_bound_usd == '0.016800'
    assert report.resources.reserved_upper_bound_usd == '3.500000'
    assert report.statuses.refused == 1
    assert report.statuses.succeeded == 29
    assert report.metadata.complete_attempts == 70
    assert report.packets.count == 12
    assert report.packets.integrity_verified
    assert report.checks.resume_verified
    result = write_technical_report(report, run.inside('technical/decision.md'),
                                    run.inside('technical/decision.json'))
    payload = run.inside('technical/decision.json').read_text()
    assert len(result) == 2
    for forbidden in (SENTINEL, str(run.path), 'primary_effect', 'qualified',
                      'case_effects', 'strata', 'candidate_a', 'win_tie_loss'):
        assert forbidden not in payload
    with pytest.raises(ValueError, match='REPORT_PATH_REFUSED'):
        write_technical_report(report, ROOT / 'study/stage-gates.yaml',
                               run.inside('technical/invalid.json'))


def test_checkpoint_requires_fresh_process_not_supplied_boolean(tmp_path):
    from task9.verifier import create_resume_checkpoint, record_resume, verify_technical_run

    run, ledger = _make_run(tmp_path)
    _accept(run, ledger, 0)
    checkpoint = run.inside('technical/checkpoint.json')
    create_resume_checkpoint(run, worker_ledger=ledger, output=checkpoint)
    with pytest.raises(ValueError, match='FRESH_PROCESS_REQUIRED'):
        record_resume(run, worker_ledger=ledger, checkpoint=checkpoint)
    checkpoint.write_text(json.dumps({'resumed': True, 'verified': True, 'secret': SENTINEL}))
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert 'RESUME_INVALID' in report.diagnostics
    assert SENTINEL not in report.model_dump_json()
    assert report.decision == 'stopped-incomplete'


def test_unknown_metadata_is_missing_and_diagnostics_never_echo_values(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    target = run.inside('records/turns.jsonl')
    rows = target.read_text().splitlines()
    row = json.loads(rows[0])
    row['input_tokens'] = None
    rows[0] = json.dumps(row)
    target.write_text('\n'.join(rows) + '\n')
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert report.decision == 'stopped-incomplete'
    assert report.resources.input_tokens is None
    assert report.metadata.complete_attempts == 69
    assert 'METADATA_INCOMPLETE' in report.diagnostics
    assert SENTINEL not in report.model_dump_json()


def test_refusal_with_full_coverage_is_valid_and_failed_retains_counts(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    response_path = run.inside('records/responses.jsonl')
    rows = [json.loads(line) for line in response_path.read_text().splitlines()]
    rows[0]['status'] = 'failed'
    response_path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert report.coverage.parent_jobs == 30
    assert report.statuses.failed == 1
    assert report.resources.output_tokens == 1400
    assert report.decision == 'stopped-incomplete'


def test_packets_use_final_only_complete_context_and_hide_identity(complete_run):
    from task9.verifier import build_protocol_packets

    run, _, _ = complete_run
    packets = build_protocol_packets(run, seed=17)
    assert len(packets) == 12
    assert {packet.criterion for packet in packets} == {'constraint_alignment'}
    assert {packet.private_assignment.judge_family for packet in packets} == {'protocol-check'}
    assert sorted(len(packet.user_transcript) for packet in packets) == [1] * 4 + [3] * 8
    for packet in packets:
        serialized = packet.model_dump_json()
        assert 'private_assignment' not in serialized
        assert 'full-skill' not in serialized
        assert 'format-matched' not in serialized
        assert 'input_tokens' not in serialized
        assert 'cost' not in serialized
        expected_index = 6 if len(packet.user_transcript) == 3 else 2
        assert packet.candidate_a.endswith(f'turn {expected_index} final answer')
        assert packet.candidate_b.endswith(f'turn {expected_index} final answer')


def test_resume_rejects_altered_accepted_prefix(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    path = run.inside('records/turns.jsonl')
    path.write_bytes(path.read_bytes().replace(b'final answer', b'other answer', 1))
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert not report.checks.resume_verified
    assert 'RESUME_INVALID' in report.diagnostics
    assert not report.checks.integrity_verified


def test_full_quality_packet_construction_is_synthetic_only():
    from task9.verifier import synthetic_quality_packet_check

    assert synthetic_quality_packet_check() == 5


@pytest.mark.parametrize('kind', ['usage-bool', 'usage-string', 'provider-model',
                                  'provider-tier', 'oversized-output', 'duplicate-turn'])
def test_untrusted_attempt_mutations_stop_without_exposing_payload(complete_run, kind):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    path = run.inside('records/turns.jsonl')
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if kind in {'usage-bool', 'usage-string'}:
        rows[0]['input_tokens'] = True if kind == 'usage-bool' else '200'
    elif kind in {'provider-model', 'provider-tier'}:
        raw = json.loads(rows[0]['raw_response'])
        field = 'model' if kind == 'provider-model' else 'service_tier'
        raw['provider_response'][field] = SENTINEL
        rows[0]['raw_response'] = json.dumps(raw)
    elif kind == 'oversized-output':
        rows[0]['output_tokens'] = 4097
    else:
        rows.append(rows[0])
    path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert report.decision == 'stopped-incomplete'
    assert SENTINEL not in report.model_dump_json()
    if kind in {'usage-bool', 'usage-string'}:
        assert report.coverage.parent_jobs == 30
        assert report.coverage.terminal_jobs == 30
        assert report.statuses.refused == 1
    if kind == 'oversized-output':
        assert 'BUDGET_INVALID' in report.diagnostics
    elif kind.startswith('provider'):
        assert 'PROVIDER_METADATA_INVALID' in report.diagnostics


def test_worker_receipt_provenance_is_required_not_self_reported_booleans(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    (ledger / 'attempts.jsonl').write_text(json.dumps({'verified': True, 'secret': SENTINEL}) + '\n')
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert not report.checks.ledger_verified
    assert 'LEDGER_INVALID' in report.diagnostics
    assert report.coverage.accepted_turns == 70
    assert report.decision == 'stopped-incomplete'
    assert SENTINEL not in report.model_dump_json()


def test_byte_different_disclosures_across_conditions_fail_parity(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    path = run.inside('records/jobs.jsonl')
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[0]['conversation_script']['user_turns'][0] += ' '
    path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert not report.checks.disclosure_parity_verified
    assert 'DISCLOSURE_PARITY_INVALID' in report.diagnostics


def test_verification_hashes_standard_reports_without_reading_effect_text(complete_run, monkeypatch):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    original = Path.read_text

    def safe_read(path, *args, **kwargs):
        if path.name in {'report.md', 'report.json'}:
            raise AssertionError('effect-bearing report text was opened')
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'read_text', safe_read)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert report.checks.standard_reports_verified
    assert report.decision == 'offline-rehearsal-complete'


def test_supplied_offline_approval_must_match_current_source(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    approval = run.inside('technical/approval.json')
    approval.write_text(json.dumps({'approved': True, 'secret': SENTINEL}))
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint,
                                  approval=approval)
    assert report.decision == 'stopped-incomplete'
    assert 'APPROVAL_INVALID' in report.diagnostics
    assert report.live_execution_authorized is False
    assert SENTINEL not in report.model_dump_json()


def _rewrite_receipts(ledger, rows):
    original_lines = (ledger / 'attempts.jsonl').read_text().splitlines(keepends=True)
    previous = '0' * 64
    for index, row in enumerate(rows, 1):
        row['seq'] = index
        row['previous_sha256'] = previous
        row.pop('sha256', None)
        row['sha256'] = canonical_digest(row)
        previous = row['sha256']
    (ledger / 'attempts.jsonl').write_text(''.join(
        original_lines[i] if i < len(original_lines) and json.loads(original_lines[i]) == row
        else json.dumps(row) + '\n' for i, row in enumerate(rows)))


def test_overlapping_reservations_are_rejected_even_with_valid_hash_chain(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    rows = [json.loads(line) for line in (ledger / 'attempts.jsonl').read_text().splitlines()]
    rows[3:9] = [rows[3], rows[6], rows[4], rows[5], rows[7], rows[8]]
    _rewrite_receipts(ledger, rows)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert 'BUDGET_INVALID' in report.diagnostics
    assert report.decision == 'stopped-incomplete'


def test_transport_deadline_excess_in_receipts_is_incomplete(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    rows = [json.loads(line) for line in (ledger / 'attempts.jsonl').read_text().splitlines()]
    rows[5]['timestamp'] = '2026-11-15T00:02:01Z'
    _rewrite_receipts(ledger, rows)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert 'BUDGET_INVALID' in report.diagnostics
    assert report.decision == 'stopped-incomplete'


def test_receipt_request_digest_must_match_actual_reconstructed_transcript(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    rows = [json.loads(line) for line in (ledger / 'attempts.jsonl').read_text().splitlines()]
    turn_id = rows[3]['turn_id']
    for row in rows[3:6]:
        row['request_sha256'] = 'b' * 64
    claim = ledger / ('claims/' + hashlib.sha256(turn_id.encode()).hexdigest() + '.json')
    claim.write_text(json.dumps({'turn_id': turn_id, 'request_sha256': 'b' * 64}))
    _rewrite_receipts(ledger, rows)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert 'LEDGER_CORRELATION_INVALID' in report.diagnostics
    assert report.decision == 'stopped-incomplete'


def test_verifier_refuses_noncanonical_skill_path_before_opening_it(complete_run, monkeypatch):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    unapproved = run.inside('unapproved-skill')
    unapproved.mkdir()
    (unapproved / 'SKILL.md').write_text(SENTINEL)
    manifest = run.manifest.model_dump(mode='json')
    manifest['config']['skill_path'] = str(unapproved)
    run.inside('manifest.json').write_text(json.dumps(manifest))
    original = Path.open

    def allowed_open(path, *args, **kwargs):
        if path.is_relative_to(unapproved):
            raise AssertionError('noncanonical source opened')
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', allowed_open)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert 'SOURCE_INVALID' in report.diagnostics
    assert report.decision == 'stopped-incomplete'


def test_isolated_report_child_failures_have_code_only_diagnostics(tmp_path, monkeypatch):
    from task9.verifier import generate_isolated_reports

    run, _ = _make_run(tmp_path)

    def timed_out(*args, **kwargs):
        raise subprocess.TimeoutExpired([SENTINEL], 120, output=SENTINEL, stderr=SENTINEL)

    monkeypatch.setattr(subprocess, 'run', timed_out)
    with pytest.raises(ValueError, match='^STANDARD_REPORT_GENERATION_FAILED$'):
        generate_isolated_reports(run)


def _remove_standard_generation(run):
    journal = run.inside('integrity.jsonl')
    lines = journal.read_bytes().splitlines(keepends=True)
    retained = [index for index, line in enumerate(lines)
                if 'records/scores.jsonl' not in json.loads(line)['digests']]
    assert retained
    journal.write_bytes(b''.join(lines[:retained[-1] + 1]))
    for name in ('reports/report.md', 'reports/report.json',
                 'reports/standard-report-receipt.json', 'records/scores.jsonl'):
        path = run.inside(name)
        if path.exists():
            path.unlink()


def test_arbitrary_unattested_reports_cannot_pass_technical_gate(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    _remove_standard_generation(run)
    run.inside('reports/report.md').write_text(SENTINEL)
    run.inside('reports/report.json').write_text(json.dumps({'untrusted': SENTINEL}))
    run.verify()
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert report.decision == 'stopped-incomplete'
    assert not report.checks.standard_reports_verified
    assert 'STANDARD_REPORTS_MISSING' in report.diagnostics
    assert SENTINEL not in report.model_dump_json()


def test_changed_scores_after_generation_invalidate_standard_report_receipt(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    scores = run.inside('records/scores.jsonl')
    first_line = scores.read_bytes().splitlines(keepends=True)[0]
    with scores.open('ab') as stream:
        stream.write(first_line)
    run.verify()
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert report.decision == 'stopped-incomplete'
    assert not report.checks.standard_reports_verified
    assert 'STANDARD_REPORTS_INVALID' in report.diagnostics


def test_report_generation_receipt_tampering_fails_closed(complete_run):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    receipt = run.inside('reports/standard-report-receipt.json')
    assert receipt.is_file()
    content = json.loads(receipt.read_bytes())
    content['runner_source_sha256'] = '0' * 64
    receipt.write_text(json.dumps(content))
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert not report.checks.standard_reports_verified
    assert 'STANDARD_REPORTS_INVALID' in report.diagnostics
    assert report.decision == 'stopped-incomplete'


def test_report_generation_receipt_cannot_traverse_symlink(complete_run, tmp_path, monkeypatch):
    from task9.verifier import verify_technical_run

    run, ledger, checkpoint = complete_run
    outside = tmp_path / 'outside-receipt.json'
    outside.write_text(SENTINEL)
    receipt = run.inside('reports/standard-report-receipt.json')
    if receipt.exists():
        receipt.unlink()
    receipt.symlink_to(outside)
    original = Path.open

    def confined_open(path, *args, **kwargs):
        if path == outside:
            raise AssertionError('outside receipt opened')
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, 'open', confined_open)
    report = verify_technical_run(run, worker_ledger=ledger, checkpoint=checkpoint)
    assert not report.checks.standard_reports_verified
    assert report.decision == 'stopped-incomplete'
