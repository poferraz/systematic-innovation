"""Content-free Task 9 verification. No network, credentials, judging, or advancement.

Answer-bearing objects stay inside this library. Only TechnicalReport is printable.
Standard effect-bearing reports are produced by a credential-free, network-disabled
child and are subsequently inspected as bytes for integrity only.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import uuid
from collections import Counter
from collections.abc import Callable
from decimal import ROUND_CEILING, Decimal
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, PrivateAttr, StrictBool, StrictInt

from systematic_innovation_bench.conversation import (
    accept_turn,
    next_turn_job,
    start_conversation,
)
from systematic_innovation_bench.models import (
    Condition,
    Job,
    Mechanism,
    ResponseRecord,
    StrictModel,
    TurnResponse,
)
from systematic_innovation_bench.runtime import (
    REPOSITORY_ROOT,
    Dispatch,
    RunDirectory,
    Snapshot,
    canonical_digest,
    current_source_digest,
    digest,
)
from systematic_innovation_bench.scoring.judges import (
    PairwiseJudgeJob,
    build_mechanism_quality_jobs,
    build_pairwise_jobs,
)
from systematic_innovation_bench.store import read_records

from .contracts import AttemptReceipt, CountReceipt, ExecutionApproval, Sha256

CASE_IDS = ('adv-dev-001', 'pre-dev-001', 'red-dev-001', 'syn-dev-001',
            'sys-dev-001', 'tri-dev-001')
DEEP_IDS = frozenset(('adv-dev-001', 'red-dev-001', 'syn-dev-001', 'sys-dev-001'))
MODEL = 'gpt-5.4-mini-2026-03-17'
SKILL_SHA256 = 'd5971f6e3e646916e2a287c5a8fde96a93b811ed071c362526c605ef222a890b'
PROCESS_INSTANCE = uuid.uuid4().hex
CONDITIONS = frozenset(Condition) - {Condition.ABLATION}
PARAMETERS = {'reasoning': {'effort': 'none'}, 'text': {'verbosity': 'medium'},
              'service_tier': 'default', 'store': False, 'tools': [],
              'tool_choice': 'none', 'truncation': 'disabled'}
Diagnostic = Literal[
    'EVIDENCE_INVALID', 'SCOPE_INVALID', 'INTEGRITY_INVALID', 'SOURCE_INVALID',
    'DISCLOSURE_PARITY_INVALID', 'COVERAGE_INCOMPLETE', 'TERMINAL_INCOMPLETE',
    'METADATA_INCOMPLETE', 'PROVIDER_METADATA_INVALID', 'LEDGER_INVALID',
    'LEDGER_CORRELATION_INVALID', 'BUDGET_INVALID', 'RESUME_INVALID',
    'PACKET_INVALID', 'STANDARD_REPORTS_MISSING', 'STANDARD_REPORTS_INVALID', 'APPROVAL_INVALID',
    'COUNT_EVIDENCE_INVALID',
]


class Coverage(StrictModel):
    expected_parent_jobs: Literal[30] = 30
    expected_assistant_turns: Literal[70] = 70
    parent_jobs: StrictInt = 0
    terminal_jobs: StrictInt = 0
    accepted_turns: StrictInt = 0
    provider_attempts: StrictInt = 0
    deep_cases: StrictInt = 0
    quick_cases: StrictInt = 0
    complete: StrictBool = False


class StatusCounts(StrictModel):
    succeeded: StrictInt = 0
    refused: StrictInt = 0
    failed: StrictInt = 0
    budget_stopped: StrictInt = 0
    pending: StrictInt = 0


class Resources(StrictModel):
    input_tokens: StrictInt | None = None
    output_tokens: StrictInt | None = None
    calculated_upper_bound_usd: str | None = Field(default=None, pattern=r'^\d+\.\d{6}$')
    reserved_upper_bound_usd: str | None = Field(default=None, pattern=r'^\d+\.\d{6}$')
    cost_provenance: Literal['provider-token-rate-calculated-upper-bound'] = (
        'provider-token-rate-calculated-upper-bound'
    )
    cost_is_invoice: Literal[False] = False
    request_limit: Literal[70] = 70
    retry_limit: Literal[0] = 0
    usage_cap_usd: Literal['5.00'] = '5.00'
    operational_stop_usd: Literal['4.50'] = '4.50'
    reservation_per_request_usd: Literal['0.05'] = '0.05'


class Metadata(StrictModel):
    actual_attempts: StrictInt = 0
    complete_attempts: StrictInt = 0
    missing_attempts: StrictInt = 0
    provider_metadata_verified: StrictBool = False
    count_requests: StrictInt = 0
    count_complete_requests: StrictInt = 0
    accounting_method: Literal['offline-local-uncertified', 'provider-input-tokens', 'unverified'] = (
        'offline-local-uncertified'
    )


class Checks(StrictModel):
    scope_verified: StrictBool = False
    integrity_verified: StrictBool = False
    source_verified: StrictBool = False
    disclosure_parity_verified: StrictBool = False
    final_portfolio_boundary_verified: StrictBool = False
    resume_verified: StrictBool = False
    ledger_verified: StrictBool = False
    budget_verified: StrictBool = False
    approval_verified: StrictBool = False
    standard_reports_verified: StrictBool = False
    count_accounting_verified: StrictBool = False


class PacketSummary(StrictModel):
    count: StrictInt = 0
    criterion: Literal['constraint_alignment'] = 'constraint_alignment'
    protocol_family_count: Literal[1] = 1
    integrity_verified: StrictBool = False
    synthetic_quality_criteria_exercised: StrictInt = 0
    judge_requests: Literal[0] = 0
    human_labels: Literal[0] = 0


class EvidenceDigests(StrictModel):
    manifest: str | None = None
    jobs: str | None = None
    corpus: str | None = None
    runner_source: str | None = None
    worker_source: str | None = None
    lock: str | None = None
    skill_tree: str | None = None
    skill_entry: str | None = None
    integrity: str | None = None
    worker_ledger: str | None = None
    count_ledger: str | None = None
    checkpoint: str | None = None
    resume: str | None = None
    packets: str | None = None
    standard_json: str | None = None
    standard_markdown: str | None = None
    standard_receipt: str | None = None
    approval: str | None = None


class TechnicalReport(StrictModel):
    schema_version: Literal['task9-technical-v1'] = 'task9-technical-v1'
    stage: Literal['six-case-feasibility'] = 'six-case-feasibility'
    scope: Literal['technical-plumbing-only'] = 'technical-plumbing-only'
    mode: Literal['offline', 'live']
    decision: Literal['offline-rehearsal-complete', 'technical-review-required', 'stopped-incomplete']
    technical_checks_passed: StrictBool
    scientific_gate_passed: Literal[False] = False
    live_execution_authorized: StrictBool = False
    later_stages_authorized: Literal[False] = False
    empirical_claims_authorized: Literal[False] = False
    coverage: Coverage
    statuses: StatusCounts
    resources: Resources
    metadata: Metadata
    checks: Checks
    packets: PacketSummary
    digests: EvidenceDigests
    diagnostics: tuple[Diagnostic, ...] = ()
    _run_path: Path = PrivateAttr()


class Prefix(StrictModel):
    size: StrictInt = Field(ge=1)
    sha256: str = Field(pattern=r'^[0-9a-f]{64}$')


class ReportInputDigests(StrictModel):
    manifest: Sha256
    jobs: Sha256
    dispatches: Sha256
    turns: Sha256
    responses: Sha256


class ReportOutputDigests(StrictModel):
    standard_json: Sha256
    standard_markdown: Sha256


class ReportSourceDigests(StrictModel):
    runner_source_sha256: Sha256
    task9_source_sha256: Sha256
    dependency_lock_sha256: Sha256


class StandardReportReceipt(StrictModel):
    version: Literal['task9-isolated-standard-reports-v1'] = 'task9-isolated-standard-reports-v1'
    generation_source_sha256: Sha256
    runner_source_sha256: Sha256
    task9_source_sha256: Sha256
    dependency_lock_sha256: Sha256
    inputs: ReportInputDigests
    scores: Prefix
    outputs: ReportOutputDigests
    input_integrity: Prefix
    generation_integrity: Prefix


class ResumeCheckpoint(StrictModel):
    version: Literal['task9-resume-v1'] = 'task9-resume-v1'
    process_id: StrictInt
    process_instance: str
    accepted_turn_id: str
    accepted_turn_index: Literal[2] = 2
    next_assistant_index: Literal[4] = 4
    turns: Prefix
    dispatches: Prefix
    worker_ledger: Prefix
    receipt_count: StrictInt
    count_ledger: Prefix | None = None
    count_receipt_count: StrictInt = Field(default=0, ge=0)
    count_marker_sha256: Sha256 | None = None


class ResumeReceipt(StrictModel):
    version: Literal['task9-resume-receipt-v1'] = 'task9-resume-receipt-v1'
    process_id: StrictInt
    process_instance: str
    checkpoint_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    next_turn_id: str
    next_assistant_index: Literal[4] = 4
    receipt_count: StrictInt
    turns: Prefix
    dispatches: Prefix
    worker_ledger: Prefix
    count_ledger: Prefix | None = None
    count_receipt_count: StrictInt = Field(default=0, ge=0)
    count_marker_sha256: Sha256 | None = None


def _inside_ledger(run: RunDirectory, ledger: Path) -> Path:
    root = run.inside(ledger)
    if not root.is_dir():
        raise ValueError('LEDGER_INVALID')
    return root


def _prefix(path: Path) -> Prefix:
    return Prefix(size=path.stat().st_size, sha256=digest(path))


def _verify_prefix(path: Path, prefix: Prefix, *, exact: bool = False) -> None:
    if path.is_symlink() or path.stat().st_size < prefix.size:
        raise ValueError('PREFIX_INVALID')
    if exact and path.stat().st_size != prefix.size:
        raise ValueError('PREFIX_INVALID')
    with path.open('rb') as stream:
        value = hashlib.sha256(stream.read(prefix.size)).hexdigest()
    if value != prefix.sha256:
        raise ValueError('PREFIX_INVALID')


def _exclusive_json(run: RunDirectory, path: Path, value: StrictModel) -> None:
    target = run.inside(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as stream:
        stream.write(value.model_dump_json(indent=2) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def _resume_path(checkpoint: Path) -> Path:
    return checkpoint.with_name(checkpoint.name + '.resume.json')


def _counts_present(ledger: Path) -> bool:
    return any(path.exists() or path.is_symlink()
               for path in (ledger / 'counts', ledger / 'counting.json'))


def _count_prefix_verified(ledger: Path, saved: ResumeCheckpoint, *, exact: bool) -> None:
    from .count_ledger import read_count_receipts

    if saved.count_ledger is None:
        if (saved.count_receipt_count != 0 or saved.count_marker_sha256 is not None
                or _counts_present(ledger)):
            raise ValueError('RESUME_INVALID')
        return
    # Validate safe paths before hashing or opening the marker/journal ourselves.
    counts = read_count_receipts(ledger)
    if (saved.count_receipt_count != 2 or saved.count_marker_sha256 is None
            or not _counts_present(ledger)
            or digest(ledger / 'counting.json') != saved.count_marker_sha256):
        raise ValueError('RESUME_INVALID')
    _verify_prefix(ledger / 'counts/attempts.jsonl', saved.count_ledger, exact=exact)
    with (ledger / 'counts/attempts.jsonl').open('rb') as stream:
        prefix_bytes = stream.read(saved.count_ledger.size)
    if not prefix_bytes.endswith(b'\n') or len(prefix_bytes.splitlines()) != 2:
        raise ValueError('RESUME_INVALID')
    first_turn = saved.accepted_turn_id.rsplit(':', 2)[0]
    opaque_first = hashlib.sha256(first_turn.encode()).hexdigest() + ':2:0'
    if (len(counts) < 2 or (exact and len(counts) != 2)
            or [row.event for row in counts[:2]] != ['started', 'completed']
            or any(row.turn_id != opaque_first for row in counts[:2])):
        raise ValueError('RESUME_INVALID')


def create_resume_checkpoint(run: RunDirectory, *, worker_ledger: Path, output: Path) -> None:
    """Checkpoint one accepted first Deep turn before any second export."""
    from .guards import read_receipts

    try:
        run.verify()
        ledger = _inside_ledger(run, worker_ledger)
        receipts = read_receipts(ledger)
        turns, dispatches = run.turns, run._dispatches()
        first = run.jobs[0]
        pending = run.pending()[0]
        if (first.case_id != 'adv-dev-001' or len(turns) != 1 or len(dispatches) != 1
                or turns[0].job_id != first.job_id or turns[0].turn_index != 2
                or turns[0].status not in {'succeeded', 'refused'}
                or pending.job_id != first.job_id or pending.assistant_turn_index != 4
                or [r.event for r in receipts] != ['reserved', 'dispatched', 'completed']
                or receipts[-1].turn_id != run.opaque(pending).turn_id.rsplit(':', 2)[0] + ':2:0'):
            raise ValueError('CHECKPOINT_INVALID')
        count_fields: dict[str, Any] = {}
        if _counts_present(ledger):
            counts = _verified_counts(run, ledger, receipts, turns)
            if len(counts) != 2:
                raise ValueError('CHECKPOINT_INVALID')
            count_fields = {
                'count_ledger': _prefix(ledger / 'counts/attempts.jsonl'),
                'count_receipt_count': len(counts),
                'count_marker_sha256': digest(ledger / 'counting.json'),
            }
        value = ResumeCheckpoint(
            process_id=os.getpid(), process_instance=PROCESS_INSTANCE,
            accepted_turn_id=turns[0].turn_id,
            turns=_prefix(run.inside('records/turns.jsonl')),
            dispatches=_prefix(run.inside('records/dispatches.jsonl')),
            worker_ledger=_prefix(ledger / 'attempts.jsonl'), receipt_count=len(receipts),
            **count_fields,
        )
        _exclusive_json(run, output, value)
    except (ValueError, OSError, KeyError, IndexError, TypeError):
        raise ValueError('CHECKPOINT_INVALID') from None


def record_resume(run: RunDirectory, *, worker_ledger: Path, checkpoint: Path) -> None:
    """Called only from a fresh process, before exporting the resumed continuation."""
    from .guards import read_receipts

    try:
        target = run.inside(checkpoint)
        saved = ResumeCheckpoint.model_validate_json(target.read_bytes())
        if saved.process_id == os.getpid() or saved.process_instance == PROCESS_INSTANCE:
            raise ValueError('FRESH_PROCESS_REQUIRED')
        ledger = _inside_ledger(run, worker_ledger)
        receipts = read_receipts(ledger)
        for path, prefix in ((run.inside('records/turns.jsonl'), saved.turns),
                             (run.inside('records/dispatches.jsonl'), saved.dispatches),
                             (ledger / 'attempts.jsonl', saved.worker_ledger)):
            _verify_prefix(path, prefix, exact=True)
        _count_prefix_verified(ledger, saved, exact=True)
        run.verify()
        turn = run.pending()[0]
        if (turn.assistant_turn_index != 4 or turn.job_id != saved.accepted_turn_id.rsplit(':', 2)[0]
                or len(receipts) != saved.receipt_count):
            raise ValueError('RESUME_INVALID')
        value = ResumeReceipt(
            process_id=os.getpid(), process_instance=PROCESS_INSTANCE,
            checkpoint_sha256=digest(target), next_turn_id=turn.turn_id,
            receipt_count=len(receipts), turns=saved.turns, dispatches=saved.dispatches,
            worker_ledger=saved.worker_ledger,
            count_ledger=saved.count_ledger, count_receipt_count=saved.count_receipt_count,
            count_marker_sha256=saved.count_marker_sha256,
        )
        _exclusive_json(run, _resume_path(target), value)
    except ValueError as exc:
        code = 'FRESH_PROCESS_REQUIRED' if str(exc) == 'FRESH_PROCESS_REQUIRED' else 'RESUME_INVALID'
        raise ValueError(code) from None
    except (OSError, KeyError, IndexError, TypeError):
        raise ValueError('RESUME_INVALID') from None


def _resume_verified(run: RunDirectory, ledger: Path, checkpoint: Path) -> bool:
    saved = ResumeCheckpoint.model_validate_json(checkpoint.read_bytes())
    resumed = ResumeReceipt.model_validate_json(run.inside(_resume_path(checkpoint)).read_bytes())
    if (resumed.process_id == saved.process_id
            or resumed.process_instance == saved.process_instance
            or resumed.checkpoint_sha256 != digest(checkpoint)
            or resumed.receipt_count != saved.receipt_count or saved.receipt_count != 3
            or resumed.turns != saved.turns or resumed.dispatches != saved.dispatches
            or resumed.worker_ledger != saved.worker_ledger
            or resumed.count_ledger != saved.count_ledger
            or resumed.count_receipt_count != saved.count_receipt_count
            or resumed.count_marker_sha256 != saved.count_marker_sha256):
        return False
    for path, prefix in ((run.inside('records/turns.jsonl'), saved.turns),
                         (run.inside('records/dispatches.jsonl'), saved.dispatches),
                         (ledger / 'attempts.jsonl', saved.worker_ledger)):
        _verify_prefix(path, prefix)
    _count_prefix_verified(ledger, saved, exact=False)
    turns, dispatches = run.turns, run._dispatches()
    if not turns or turns[0].turn_id != saved.accepted_turn_id or turns[0].turn_index != 2:
        return False
    first_job = next(j for j in run.jobs if j.job_id == turns[0].job_id)
    if first_job.case_id != 'adv-dev-001' or len(turns) < 2 or len(dispatches) < 2:
        return False
    return (turns[1].turn_id == resumed.next_turn_id
            and dispatches[1].turn_id == resumed.next_turn_id
            and turns[1].job_id == first_job.job_id and turns[1].turn_index == 4)


def build_protocol_packets(run: RunDirectory, *, seed: int) -> list[PairwiseJudgeJob]:
    """Library-only answer-bearing result. Never print it or its private mapping."""
    jobs = run.jobs
    responses = {response.job_id: response for response in run.responses}
    result: list[PairwiseJudgeJob] = []
    for case_id in CASE_IDS:
        selected = {job.condition: job for job in jobs if job.case_id == case_id}
        left, right = selected[Condition.FULL_SKILL], selected[Condition.FORMAT_MATCHED]
        context = (left.prompt, *(left.conversation_script.user_turns
                                 if left.conversation_script else ()))
        result.extend(build_pairwise_jobs(
            responses[left.job_id], responses[right.job_id], user_transcript=context,
            criterion='constraint_alignment', seed=seed, judge_families=('protocol-check',),
            identity_labels=(MODEL, 'inbox'),
        ))
    return result


def _packet_check(run: RunDirectory) -> PacketSummary:
    packets = build_protocol_packets(run, seed=0)
    groups: dict[str, list[PairwiseJudgeJob]] = {}
    for packet in packets:
        groups.setdefault(packet.comparison_id, []).append(packet)
        data = packet.model_dump_json()
        forbidden = ('private_assignment', 'full-skill', 'format-matched', MODEL,
                     'input_tokens', 'output_tokens', 'reserved_cost')
        if (any(value in data for value in forbidden) or packet.criterion != 'constraint_alignment'
                or packet.private_assignment.judge_family != 'protocol-check'):
            raise ValueError('PACKET_INVALID')
    if len(groups) != 6 or len(packets) != 12 or len({p.job_id for p in packets}) != 12:
        raise ValueError('PACKET_INVALID')
    for pair in groups.values():
        if (len(pair) != 2 or pair[0].candidate_a != pair[1].candidate_b
                or pair[0].candidate_b != pair[1].candidate_a
                or pair[0].user_transcript != pair[1].user_transcript
                or pair[0].private_assignment.a_source != pair[1].private_assignment.b_source):
            raise ValueError('PACKET_INVALID')
    return PacketSummary(count=12, integrity_verified=True,
                         synthetic_quality_criteria_exercised=synthetic_quality_packet_check())


def synthetic_quality_packet_check() -> int:
    """Exercise five criterion construction using an explicitly synthetic candidate."""
    candidate = Mechanism(id='synthetic-only', intervention_point='queue', actor='coordinator',
                          changed_flow='slots', causal_operation='reserve capacity',
                          intended_effect='reduce waiting', principal_constraint='fixed capacity')
    packets = build_mechanism_quality_jobs(
        [candidate], final_portfolio='A coordinator reserves slots to reduce waiting.',
        user_transcript=('Synthetic fixture: preserve fixed capacity.',), seed=0,
    )
    if len(packets) != 5 or len({p.criterion for p in packets}) != 5:
        raise ValueError('PACKET_INVALID')
    if any('private_assignment' in p.model_dump_json() for p in packets):
        raise ValueError('PACKET_INVALID')
    return 5


STANDARD_REPORT_RECEIPT = 'reports/standard-report-receipt.json'
_REPORT_INPUT_PATHS = {
    'manifest': 'manifest.json', 'jobs': 'records/jobs.jsonl',
    'dispatches': 'records/dispatches.jsonl', 'turns': 'records/turns.jsonl',
    'responses': 'records/responses.jsonl',
}
_REPORT_CHILD_PROGRAM = '''import socket, sys
socket.socket = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("NETWORK_DISABLED"))
socket.create_connection = socket.socket
from pathlib import Path
from task9.verifier import _generate_standard_reports_in_child
from systematic_innovation_bench.runtime import RunDirectory
_generate_standard_reports_in_child(RunDirectory(Path(sys.argv[1])))
'''


def _report_inputs(run: RunDirectory) -> ReportInputDigests:
    return ReportInputDigests(**{key: digest(run.inside(name))
                                for key, name in _REPORT_INPUT_PATHS.items()})


def _report_sources(run: RunDirectory) -> ReportSourceDigests:
    valid, source = _source(run)
    if not valid:
        raise ValueError('STANDARD_REPORTS_INVALID')
    return ReportSourceDigests(runner_source_sha256=source['runner_source'],
                               task9_source_sha256=source['worker_source'],
                               dependency_lock_sha256=source['lock'])


def _report_outputs(run: RunDirectory) -> ReportOutputDigests:
    return ReportOutputDigests(
        standard_json=digest(run.inside('reports/report.json')),
        standard_markdown=digest(run.inside('reports/report.md')),
    )


def _report_targets_absent(run: RunDirectory) -> None:
    for name in ('reports/report.md', 'reports/report.json', STANDARD_REPORT_RECEIPT):
        if run.inside(name).exists():
            raise ValueError('STANDARD_REPORTS_EXIST')


def _generate_standard_reports_in_child(run: RunDirectory) -> None:
    """The isolated child alone creates the content-free generation receipt.

    This is local process provenance, not a signature or an operating-system
    custody guarantee against a party able to rewrite the whole evidence tree.
    """
    from systematic_innovation_bench.cli import dispatch, parser

    _report_targets_absent(run)
    run.require_current_source()
    _history(run)
    inputs, source = _report_inputs(run), _report_sources(run)
    before = _prefix(run.inside('integrity.jsonl'))
    for command in ('score', 'report'):
        dispatch(parser().parse_args([command, '--run-dir', str(run.path)]))
    _history(run)
    if inputs != _report_inputs(run) or source != _report_sources(run):
        raise ValueError('STANDARD_REPORTS_INVALID')
    receipt = StandardReportReceipt(
        generation_source_sha256=hashlib.sha256(_REPORT_CHILD_PROGRAM.encode()).hexdigest(),
        **source.model_dump(), inputs=inputs,
        scores=_prefix(run.inside('records/scores.jsonl')),
        outputs=_report_outputs(run), input_integrity=before,
        generation_integrity=_prefix(run.inside('integrity.jsonl')),
    )
    _exclusive_json(run, run.inside(STANDARD_REPORT_RECEIPT), receipt)
    # The next durable snapshot seals the receipt without a circular digest:
    # its receipt refers only to the preceding, report-producing snapshot prefix.
    run.snapshot()


def _verify_standard_reports(run: RunDirectory) -> dict[str, str]:
    receipt_path = run.inside(STANDARD_REPORT_RECEIPT)
    receipt = StandardReportReceipt.model_validate_json(receipt_path.read_bytes())
    source = _report_sources(run)
    if (receipt.generation_source_sha256 != hashlib.sha256(_REPORT_CHILD_PROGRAM.encode()).hexdigest()
            or receipt.runner_source_sha256 != source.runner_source_sha256
            or receipt.task9_source_sha256 != source.task9_source_sha256
            or receipt.dependency_lock_sha256 != source.dependency_lock_sha256
            or receipt.inputs != _report_inputs(run)
            or receipt.outputs != _report_outputs(run)):
        raise ValueError('STANDARD_REPORTS_INVALID')
    _verify_prefix(run.inside('records/scores.jsonl'), receipt.scores, exact=True)
    journal = run.inside('integrity.jsonl')
    _verify_prefix(journal, receipt.input_integrity)
    _verify_prefix(journal, receipt.generation_integrity)
    if receipt.input_integrity.size >= receipt.generation_integrity.size:
        raise ValueError('STANDARD_REPORTS_INVALID')
    with journal.open('rb') as stream:
        generation_bytes = stream.read(receipt.generation_integrity.size)
    if not generation_bytes.endswith(b'\n'):
        raise ValueError('STANDARD_REPORTS_INVALID')
    generated = Snapshot.model_validate_json(generation_bytes.splitlines()[-1])
    expected = {name: getattr(receipt.inputs, key) for key, name in _REPORT_INPUT_PATHS.items()}
    expected.update({
        'records/scores.jsonl': receipt.scores.sha256,
        'reports/report.json': receipt.outputs.standard_json,
        'reports/report.md': receipt.outputs.standard_markdown,
    })
    if (any(generated.digests.get(name) != value for name, value in expected.items())
            or generated.sizes.get('records/scores.jsonl') != receipt.scores.size):
        raise ValueError('STANDARD_REPORTS_INVALID')
    receipt_sha = digest(receipt_path)
    snapshots = read_records(journal, Snapshot)
    if not any(snapshot.digests.get(STANDARD_REPORT_RECEIPT) == receipt_sha
               and all(snapshot.digests.get(name) == value for name, value in expected.items())
               for snapshot in snapshots):
        raise ValueError('STANDARD_REPORTS_INVALID')
    _history(run)
    return {**receipt.outputs.model_dump(), 'standard_receipt': receipt_sha,
            'integrity': digest(journal)}


def generate_isolated_reports(run: RunDirectory) -> dict[str, str]:
    """Generate outputs and a durable provenance receipt in an isolated child."""
    _report_targets_absent(run)
    env = {'PYTHONPATH': os.pathsep.join((str(REPOSITORY_ROOT / 'benchmark/src'),
                                        str(REPOSITORY_ROOT / 'benchmark'))),
           'PYTHONDONTWRITEBYTECODE': '1'}
    try:
        result = subprocess.run([sys.executable, '-c', _REPORT_CHILD_PROGRAM, str(run.path)], env=env,
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, timeout=120, check=False)
        if result.returncode:
            raise ValueError('STANDARD_REPORT_GENERATION_FAILED')
        verified = _verify_standard_reports(run)
        return {key: verified[key] for key in ('standard_markdown', 'standard_json')}
    except (ValueError, OSError, subprocess.TimeoutExpired):
        raise ValueError('STANDARD_REPORT_GENERATION_FAILED') from None


def _history(run: RunDirectory) -> bool:
    run.verify()
    for snapshot in read_records(run.inside('integrity.jsonl'), Snapshot):
        for name, expected in snapshot.digests.items():
            path = run.inside(name)
            if name.startswith('records/') and name.endswith('.jsonl'):
                size = snapshot.sizes.get(name)
                if size is None:
                    raise ValueError('INTEGRITY_INVALID')
                _verify_prefix(path, Prefix(size=size, sha256=expected))
            elif digest(path) != expected:
                raise ValueError('INTEGRITY_INVALID')
    return True


def _scope(jobs: list[Job], run: RunDirectory) -> bool:
    config = run.manifest.config
    expected = {(case, condition, 0) for case in CASE_IDS for condition in CONDITIONS}
    actual = {(job.case_id, job.condition, job.replicate) for job in jobs}
    return bool(
        len(jobs) == 30 and len({job.job_id for job in jobs}) == 30 and actual == expected
        and tuple(case.id for case in run.manifest.cases) == CASE_IDS
        and config.models == (MODEL,) and config.model_allowlist == (MODEL,)
        and config.hosts == ('inbox',) and frozenset(config.conditions) == CONDITIONS
        and config.replicates == 1 and config.max_calls == 70 and config.retry_limit == 0
        and config.max_concurrency == 1 and config.failure_threshold == 0
        and config.max_output_tokens == 4096 and config.max_cost == 5
        and config.cost_per_turn == {MODEL: 0.05} and config.model_parameters == PARAMETERS
        and config.timeout_seconds == 120 and config.max_output_bytes == 1048576
        and all(job.model == MODEL and job.host == 'inbox' and job.split == 'development'
                and job.model_parameters == PARAMETERS | {'max_output_tokens': 4096} for job in jobs)
    )


def _parity(jobs: list[Job], responses: list[ResponseRecord]) -> bool:
    response_map = {response.job_id: response for response in responses}
    for case_id in CASE_IDS:
        selected = [job for job in jobs if job.case_id == case_id]
        if len(selected) != 5:
            return False
        contexts = [(job.prompt, *(job.conversation_script.user_turns
                                  if job.conversation_script else ())) for job in selected]
        required = 3 if case_id in DEEP_IDS else 1
        if len(set(contexts)) != 1 or len(contexts[0]) != required:
            return False
        for job in selected:
            response = response_map.get(job.job_id)
            if response is None or response.conversation is None:
                return False
            conversation = response.conversation
            users = tuple(turn.content for turn in conversation.turns if turn.role == 'user')
            if (users != contexts[0] or response.content != conversation.final_response
                    or response.content != conversation.turns[-1].content
                    or response.output_tokens != conversation.final_response_output_tokens):
                return False
    return True


def _source(run: RunDirectory) -> tuple[bool, dict[str, str]]:
    manifest = run.manifest
    skill = REPOSITORY_ROOT / 'skills/systematic-innovation'
    requested = manifest.config.skill_path
    if skill.is_symlink() or (requested is not None and requested.resolve() != skill.resolve()):
        raise ValueError('SOURCE_INVALID')
    paths = sorted(skill.rglob('*'))
    worker_paths = sorted(Path(__file__).parent.glob('*.py'))
    if any(path.is_symlink() for path in (*paths, *worker_paths)):
        raise ValueError('SOURCE_INVALID')
    files = [path for path in paths if path.is_file()]
    tree = canonical_digest({path.relative_to(skill).as_posix(): digest(path) for path in files})
    worker = canonical_digest({path.name: digest(path) for path in worker_paths})
    lock = digest(REPOSITORY_ROOT / 'benchmark/uv.lock')
    values = {'runner_source': current_source_digest(), 'worker_source': worker, 'lock': lock,
              'skill_tree': tree, 'skill_entry': digest(skill / 'SKILL.md')}
    valid = (values['runner_source'] == manifest.runner_source_sha256
             and lock == manifest.artifact_digests.get('dependency_lock')
             and tree == manifest.skill_revision and values['skill_entry'] == SKILL_SHA256)
    return valid, values


def _provider_metadata(turn: TurnResponse) -> bool:
    try:
        envelope = json.loads(turn.raw_response or '')
        raw = envelope['provider_response']
        usage = raw['usage']
        provenance = {
            'kind': 'calculated-token-rate-upper-bound', 'currency': 'USD',
            'input_rate_usd_per_million': '0.75', 'output_rate_usd_per_million': '4.50',
            'basis': 'provider-total-tokens; uncached input rate; reasoning not added again',
        }
        pieces: list[str] = []
        refused = False
        for item in raw['output']:
            if item['type'] == 'reasoning':
                continue
            if (item['type'] != 'message' or item['role'] != 'assistant'
                    or item['status'] != 'completed'):
                return False
            for part in item['content']:
                if part['type'] == 'output_text' and isinstance(part['text'], str):
                    pieces.append(part['text'])
                elif part['type'] == 'refusal' and isinstance(part['refusal'], str):
                    pieces.append(part['refusal'])
                    refused = True
                else:
                    return False
        return bool(
            raw['model'] == MODEL and raw['service_tier'] == 'default'
            and raw['status'] == 'completed' and isinstance(raw['id'], str) and raw['id']
            and envelope['http_status'] == 200 and isinstance(envelope['request_id'], str)
            and envelope['request_id'] and envelope['cost_provenance'] == provenance
            and type(usage['input_tokens']) is int and type(usage['output_tokens']) is int
            and usage['input_tokens'] == turn.input_tokens
            and usage['output_tokens'] == turn.output_tokens
            and pieces and '\n'.join(pieces) == turn.content
            and turn.status == ('refused' if refused else 'succeeded')
        )
    except (ValueError, KeyError, TypeError):
        return False


def _request_payloads(run: RunDirectory) -> dict[str, dict[str, Any]]:
    from .worker import build_payload

    result: dict[str, dict[str, Any]] = {}
    cases = {case.id: case for case in run.manifest.cases}
    turns = run.turns
    for job in run.jobs:
        state = start_conversation(job, cases[job.case_id])
        for response in [turn for turn in turns if turn.job_id == job.job_id]:
            request = next_turn_job(state)
            if request is None:
                raise ValueError('LEDGER_CORRELATION_INVALID')
            opaque = run.opaque(request)
            result[opaque.turn_id] = build_payload(opaque)
            state = accept_turn(state, request, response)
    return result


def _request_digests(run: RunDirectory) -> dict[str, str]:
    return {turn_id: canonical_digest(payload)
            for turn_id, payload in _request_payloads(run).items()}


def _verified_counts(
    run: RunDirectory, ledger: Path, receipts: list[AttemptReceipt], turns: list[TurnResponse], *,
    transport_live: bool | None = None, approved: ExecutionApproval | None = None,
) -> list[CountReceipt]:
    """Correlate separately retained count attempts with exact generation inputs."""
    from .count_ledger import read_count_receipts, validate_provider_bound
    from .counting import counting_profile

    rows = read_count_receipts(ledger)
    starts = rows[::2]
    completed = rows[1::2]
    dispatched = [row for row in receipts if row.event == 'dispatched']
    reserved = {row.turn_id: row for row in receipts if row.event == 'reserved'}
    generated = {row.turn_id: row for row in receipts if row.event == 'completed'}
    accepted = {hashlib.sha256(turn.job_id.encode()).hexdigest()
                + f':{turn.turn_index}:{turn.attempt}': turn for turn in turns}
    profile = canonical_digest(counting_profile())
    if (not rows or len(rows) != len(starts) * 2 or len(starts) > 70
            or len(starts) != len(dispatched) or len(generated) != len(accepted)
            or len(starts) != len(accepted)
            or any(row.event != 'started' for row in starts)
            or any(row.event != 'completed' for row in completed)
            or [row.turn_id for row in starts] != [row.turn_id for row in dispatched]):
        raise ValueError('COUNT_EVIDENCE_INVALID')
    account_id, project_id = starts[0].account_id, starts[0].project_id
    if approved is not None:
        if (not approved.token_counting_authorized or approved.max_token_count_requests != 70
                or approved.input_profile_sha256 != profile):
            raise ValueError('COUNT_EVIDENCE_INVALID')
        account_id, project_id = approved.account_id, approved.project_id
    payloads = _request_payloads(run)
    prior_generation: AttemptReceipt | None = None
    for start, completion in zip(starts, completed, strict=True):
        bound = completion.input_bound
        if bound is None or start.turn_id != completion.turn_id:
            raise ValueError('COUNT_EVIDENCE_INVALID')
        validate_provider_bound(
            bound, payloads[start.turn_id], account_id=account_id, project_id=project_id,
            profile_sha256=profile,
            transport_live=bound.certified_for_live if transport_live is None else transport_live,
        )
        if (start.account_id != account_id or start.project_id != project_id
                or start.profile_sha256 != profile
                or completion.request_sha256 != generated[start.turn_id].request_sha256
                or bound.tokens != accepted[start.turn_id].input_tokens
                or not 0 < bound.tokens <= 32768
                or completion.timestamp < start.timestamp
                or (completion.timestamp - start.timestamp).total_seconds() > 10
                or completion.timestamp > reserved[start.turn_id].timestamp
                or (prior_generation is not None
                    and start.timestamp < prior_generation.timestamp)):
            raise ValueError('COUNT_EVIDENCE_INVALID')
        prior_generation = generated[start.turn_id]
    first_event = min(min(row.timestamp for row in starts),
                      min(row.timestamp for row in receipts))
    final_generation = max(row.timestamp for row in generated.values())
    if (final_generation - first_event).total_seconds() >= 10800:
        raise ValueError('COUNT_EVIDENCE_INVALID')
    return rows


def _ledger_limits(receipts: list[AttemptReceipt]) -> bool:
    active: str | None = None
    prior_event: str | None = None
    dispatch_time = None
    previous_time = None
    if not receipts:
        return False
    for receipt in receipts:
        if previous_time is not None and receipt.timestamp < previous_time:
            return False
        previous_time = receipt.timestamp
        if receipt.event == 'reserved':
            if active is not None:
                return False
            active = receipt.turn_id
        elif receipt.event == 'dispatched':
            if active != receipt.turn_id or prior_event != 'reserved':
                return False
            dispatch_time = receipt.timestamp
        elif receipt.event == 'completed':
            if (active != receipt.turn_id or prior_event != 'dispatched'
                    or dispatch_time is None
                    or (receipt.timestamp - dispatch_time).total_seconds() > 120):
                return False
            active = None
        else:
            return False
        prior_event = receipt.event
    return active is None and (receipts[-1].timestamp - receipts[0].timestamp).total_seconds() < 10800


def verify_technical_run(
    run: RunDirectory, *, worker_ledger: Path, checkpoint: Path,
    mode: Literal['offline', 'live'] = 'offline', approval: Path | None = None,
) -> TechnicalReport:
    """Verify retained technical facts; diagnostics never interpolate input values."""
    from .guards import read_receipts

    if mode not in {'offline', 'live'}:
        raise ValueError('MODE_INVALID')
    diagnostics: list[Diagnostic] = []
    checks: dict[str, bool] = {}
    digests: dict[str, str] = {}
    packets = PacketSummary()
    jobs: list[Job] = []
    turns: list[TurnResponse] = []
    responses: list[ResponseRecord] = []
    dispatches: list[Dispatch] = []
    receipts = []
    counts: list[CountReceipt] = []
    approved: ExecutionApproval | None = None
    accounting_method: Literal[
        'offline-local-uncertified', 'provider-input-tokens', 'unverified'
    ] = 'offline-local-uncertified' if mode == 'offline' else 'unverified'
    ledger: Path | None = None
    try:
        jobs = run.jobs
    except (ValueError, OSError, KeyError, TypeError):
        diagnostics.append('EVIDENCE_INVALID')
    try:
        responses = run.responses
    except (ValueError, OSError, KeyError, TypeError):
        diagnostics.append('EVIDENCE_INVALID')
    try:
        payload = run.inside('records/turns.jsonl').read_bytes()
        if payload and not payload.endswith(b'\n'):
            diagnostics.append('EVIDENCE_INVALID')
        for line in payload.splitlines():
            try:
                turns.append(TurnResponse.model_validate_json(line))
            except ValueError:
                diagnostics.append('EVIDENCE_INVALID')
    except OSError:
        diagnostics.append('EVIDENCE_INVALID')
    try:
        dispatches = read_records(run.inside('records/dispatches.jsonl'), Dispatch)
        digests.update(manifest=digest(run.inside('manifest.json')),
                       jobs=digest(run.inside('records/jobs.jsonl')),
                       corpus=canonical_digest([c.model_dump(mode='json') for c in run.manifest.cases]))
    except (ValueError, OSError, KeyError, TypeError):
        diagnostics.append('EVIDENCE_INVALID')
    operations: tuple[tuple[str, Diagnostic, Callable[[], bool]], ...] = (
        ('scope_verified', 'SCOPE_INVALID', lambda: _scope(jobs, run)),
        ('integrity_verified', 'INTEGRITY_INVALID', lambda: _history(run)),
        ('disclosure_parity_verified', 'DISCLOSURE_PARITY_INVALID', lambda: _parity(jobs, responses)),
    )
    for name, code, operation in operations:
        try:
            checks[name] = bool(operation())
        except (ValueError, OSError, KeyError, TypeError, IndexError):
            checks[name] = False
        if not checks[name]:
            diagnostics.append(code)
    checks['final_portfolio_boundary_verified'] = checks['disclosure_parity_verified']
    try:
        checks['source_verified'], source = _source(run)
        digests.update(source)
        if not checks['source_verified']:
            diagnostics.append('SOURCE_INVALID')
    except (ValueError, OSError, KeyError, TypeError):
        diagnostics.append('SOURCE_INVALID')
    try:
        ledger = _inside_ledger(run, worker_ledger)
        receipts = read_receipts(ledger)
        digests['worker_ledger'] = digest(ledger / 'attempts.jsonl')
        checks['ledger_verified'] = True
    except (ValueError, OSError, KeyError, TypeError):
        diagnostics.append('LEDGER_INVALID')
    dispatched = [receipt for receipt in receipts if receipt.event == 'dispatched']
    completed = [receipt for receipt in receipts if receipt.event == 'completed']
    by_opaque = {hashlib.sha256(t.job_id.encode()).hexdigest() + f':{t.turn_index}:{t.attempt}': t
                 for t in turns}
    expected_dispatches = [hashlib.sha256(d.turn_id.rsplit(':', 2)[0].encode()).hexdigest()
                           + ':' + ':'.join(d.turn_id.rsplit(':', 2)[1:]) for d in dispatches]
    correlation = bool(receipts) and ([r.turn_id for r in dispatched] == expected_dispatches
        and len(dispatched) == len(by_opaque) == len(turns) == len(completed)
        and [r.turn_id for r in completed] == [r.turn_id for r in dispatched])
    try:
        requests = _request_digests(run)
        if any(receipt.request_sha256 != requests.get(receipt.turn_id) for receipt in receipts):
            correlation = False
        for receipt in completed:
            if ledger is None or receipt.response_path is None:
                raise ValueError('LEDGER_INVALID')
            response_path = run.inside(ledger / receipt.response_path)
            if not response_path.is_relative_to(ledger):
                raise ValueError('LEDGER_INVALID')
            observed = TurnResponse.model_validate_json(response_path.read_bytes())
            accepted = by_opaque[receipt.turn_id]
            if (observed.model_dump(exclude={'job_id', 'turn_id'})
                    != accepted.model_dump(exclude={'job_id', 'turn_id'})):
                correlation = False
    except (ValueError, OSError, KeyError, TypeError):
        correlation = False
    if not correlation:
        diagnostics.append('LEDGER_CORRELATION_INVALID')
        checks['ledger_verified'] = False
    try:
        from .count_ledger import read_count_receipts

        if approval is not None:
            approved = ExecutionApproval.model_validate_json(run.inside(approval).read_bytes())
        if ledger is None:
            if mode == 'live':
                raise ValueError('COUNT_EVIDENCE_INVALID')
        elif _counts_present(ledger):
            accounting_method = 'unverified'
            counts = read_count_receipts(ledger)
            _verified_counts(run, ledger, receipts, turns,
                             transport_live=mode == 'live', approved=approved)
            digests['count_ledger'] = digest(ledger / 'counts/attempts.jsonl')
            checks['count_accounting_verified'] = True
            accounting_method = 'provider-input-tokens'
        elif mode == 'live' or (approved is not None and approved.token_counting_authorized):
            raise ValueError('COUNT_EVIDENCE_INVALID')
    except (ValueError, OSError, KeyError, TypeError, IndexError):
        checks['count_accounting_verified'] = False
        accounting_method = 'unverified'
        diagnostics.append('COUNT_EVIDENCE_INVALID')
    known = [turn for turn in turns if type(turn.input_tokens) is int
             and type(turn.output_tokens) is int and turn.cost is not None]
    metadata_complete = len(known) == len(turns) == len(dispatched) and bool(turns)
    if not metadata_complete:
        diagnostics.append('METADATA_INCOMPLETE')
    provider_metadata = bool(turns) and all(_provider_metadata(turn) for turn in turns)
    if not provider_metadata:
        diagnostics.append('PROVIDER_METADATA_INVALID')
    input_tokens = sum(t.input_tokens for t in known if t.input_tokens is not None)
    output_tokens = sum(t.output_tokens for t in known if t.output_tokens is not None)
    calculated = (Decimal(input_tokens) * Decimal('0.75')
                  + Decimal(output_tokens) * Decimal('4.50')) / Decimal(1000000)
    reserved = Decimal(len(dispatched)) * Decimal('0.05')
    budget = (correlation and metadata_complete and len(dispatched) <= 70
              and reserved < Decimal('4.50') and reserved <= Decimal('5.00')
              and all(turn.attempt == 0 and turn.input_tokens is not None
                      and 0 <= turn.input_tokens <= 32768 and turn.output_tokens is not None
                      and 0 <= turn.output_tokens <= 4096
                      and turn.cost is not None
                      and abs(Decimal(str(turn.cost)) - (
                          Decimal(turn.input_tokens) * Decimal('0.75')
                          + Decimal(turn.output_tokens) * Decimal('4.50')) / 1000000)
                      <= Decimal('0.000000000001') for turn in turns)
              and _ledger_limits(receipts)
              and all(r.reserved_micro_usd == 50000 for r in receipts)
              and all(r.charged_micro_usd is not None
                      and Decimal(r.charged_micro_usd) == (Decimal(str(by_opaque[r.turn_id].cost))
                      * 1000000).to_integral_value(rounding=ROUND_CEILING) for r in completed))
    checks['budget_verified'] = bool(budget)
    if not budget:
        diagnostics.append('BUDGET_INVALID')
    try:
        target = run.inside(checkpoint)
        checks['resume_verified'] = ledger is not None and _resume_verified(run, ledger, target)
        digests.update(checkpoint=digest(target), resume=digest(run.inside(_resume_path(target))))
    except (ValueError, OSError, KeyError, IndexError, TypeError):
        checks['resume_verified'] = False
    if not checks['resume_verified']:
        diagnostics.append('RESUME_INVALID')
    try:
        packets = _packet_check(run)
        digests['packets'] = canonical_digest([p.model_dump(mode='json') for p in build_protocol_packets(run, seed=0)])
    except (ValueError, OSError, KeyError, IndexError, TypeError):
        diagnostics.append('PACKET_INVALID')
    try:
        digests.update(_verify_standard_reports(run))
        checks['standard_reports_verified'] = True
    except FileNotFoundError:
        diagnostics.append('STANDARD_REPORTS_MISSING')
    except (ValueError, OSError, KeyError, TypeError):
        diagnostics.append('STANDARD_REPORTS_INVALID')
    if mode == 'live' or approval is not None:
        # A report never grants authorization. Live authorization is an input,
        # verified by the same guard that binds the run before any provider send.
        try:
            from .guards import validate_approval
            if approval is None or ledger is None:
                raise ValueError('APPROVAL_INVALID')
            if approved is None:
                raise ValueError('APPROVAL_INVALID')
            representative = next((row.input_bound for row in reversed(counts)
                                   if row.event == 'completed'), None)
            validate_approval(run, approved, transport_live=mode == 'live',
                              transport_account_id=approved.account_id,
                              transport_project_id=approved.project_id,
                              input_bound=representative)
            checks['approval_verified'] = True
            digests['approval'] = digest(run.inside(approval))
        except (ValueError, OSError, KeyError, TypeError):
            diagnostics.append('APPROVAL_INVALID')
    statuses = Counter(response.status for response in responses)
    expected_turns = {f'{job.job_id}:{index}:0' for job in jobs
                      for index in ((2, 4, 6) if job.case_id in DEEP_IDS else (2,))}
    coverage_complete = (len(jobs) == len(responses) == 30 and len(turns) == 70
                         and len({r.job_id for r in responses}) == 30
                         and {turn.turn_id for turn in turns} == expected_turns)
    if not coverage_complete:
        diagnostics.append('COVERAGE_INCOMPLETE')
    if statuses['failed'] or statuses['budget-stopped'] or any(
        turn.status not in {'succeeded', 'refused'} for turn in turns
    ):
        diagnostics.append('TERMINAL_INCOMPLETE')
    passed = not diagnostics
    report = TechnicalReport(
        mode=mode, decision=('offline-rehearsal-complete' if mode == 'offline' else
                            'technical-review-required') if passed else 'stopped-incomplete',
        technical_checks_passed=passed,
        live_execution_authorized=mode == 'live' and checks.get('approval_verified', False),
        coverage=Coverage(parent_jobs=len(jobs), terminal_jobs=len(responses),
                          accepted_turns=len(turns), provider_attempts=len(dispatched),
                          deep_cases=len({j.case_id for j in jobs if j.case_id in DEEP_IDS}),
                          quick_cases=len({j.case_id for j in jobs if j.case_id not in DEEP_IDS}),
                          complete=coverage_complete),
        statuses=StatusCounts(succeeded=statuses['succeeded'], refused=statuses['refused'],
                              failed=statuses['failed'], budget_stopped=statuses['budget-stopped'],
                              pending=max(0, len(jobs) - len(responses))),
        resources=Resources(input_tokens=input_tokens if metadata_complete else None,
                            output_tokens=output_tokens if metadata_complete else None,
                            calculated_upper_bound_usd=f'{calculated:.6f}' if metadata_complete else None,
                            reserved_upper_bound_usd=f'{reserved:.6f}'),
        metadata=Metadata(actual_attempts=len(dispatched), complete_attempts=len(known),
                          missing_attempts=max(len(dispatched), len(turns)) - len(known),
                          provider_metadata_verified=provider_metadata,
                          count_requests=sum(row.event == 'started' for row in counts),
                          count_complete_requests=sum(row.event == 'completed' for row in counts),
                          accounting_method=accounting_method),
        checks=Checks(**checks), packets=packets, digests=EvidenceDigests(**digests),
        diagnostics=tuple(sorted(set(diagnostics))),
    )
    report._run_path = run.path
    return report


def write_technical_report(report: TechnicalReport, output_md: Path, output_json: Path) -> dict[str, str]:
    """Exclusive writes inside this report's generated run directory only."""
    try:
        run = RunDirectory(report._run_path)
        md, js = run.inside(output_md), run.inside(output_json)
        if md == js or md.suffix != '.md' or js.suffix != '.json' or md.exists() or js.exists():
            raise ValueError('REPORT_PATH_REFUSED')
        serialized = report.model_dump_json(indent=2) + '\n'
        # Markdown is deliberately generated from the same whitelisted record.
        markdown = '# Task 9 technical verification\n\n' + '```json\n' + serialized + '```\n'
        md.parent.mkdir(parents=True, exist_ok=True)
        js.parent.mkdir(parents=True, exist_ok=True)
        with js.open('x', encoding='utf-8') as stream:
            stream.write(serialized)
        with md.open('x', encoding='utf-8') as stream:
            stream.write(markdown)
        return {'technical_json': digest(js), 'technical_markdown': digest(md)}
    except (ValueError, OSError, AttributeError):
        raise ValueError('REPORT_PATH_REFUSED') from None
