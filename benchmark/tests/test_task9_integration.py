"""Complete Task 9 execution plumbing with request-bound offline HTTP fixtures only."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

from systematic_innovation_bench.conversation import accept_turn, next_turn_job, start_conversation
from systematic_innovation_bench.models import RunConfig, TurnJob, TurnResponse
from systematic_innovation_bench.runtime import (
    RunDirectory,
    canonical_digest,
    prepare,
    public_cases,
)
from systematic_innovation_bench.store import read_records
from task9.contracts import CASE_IDS, MODEL, ExecutionApproval
from task9.guards import Task9Guard, approval_bindings
from task9.replay import ReplayBundle
from task9.worker import Worker, build_payload

BENCH=Path(__file__).resolve().parents[1]


def cli(*args):
    env={k:v for k,v in os.environ.items() if k in {'PATH','SYSTEMROOT','TMPDIR','LANG','LC_ALL'}}
    env['PYTHONPATH']=os.pathsep.join((str(BENCH/'src'),str(BENCH)))
    return subprocess.run([sys.executable,'-m','task9',*map(str,args)],cwd=BENCH,
                          capture_output=True,text=True,env=env,check=False)


def response_body(sequence):
    return {'id':f'resp_offline_{sequence}','model':MODEL,'service_tier':'default','status':'completed',
            'metadata':{'api_key':'offline'+'-synthetic-credential'},
            'output':[{'type':'message','role':'assistant','status':'completed','content':[
                {'type':'output_text','text':'Synthetic offline portfolio. No measurement claim.'}]}],
            'usage':{'input_tokens':200,'output_tokens':20,'total_tokens':220,
                     'output_tokens_details':{'reasoning_tokens':0},'input_tokens_details':{'cached_tokens':0}}}


@pytest.fixture
def prepared(tmp_path):
    values=yaml.safe_load((BENCH/'configs/feasibility-six.proposed.yaml').read_text())
    values.update(run_id='offline-task9-integration',dry_run=False)
    config=RunConfig.model_validate(values)
    cases=public_cases(BENCH/'cases/development',CASE_IDS)
    jobs,manifest=prepare(config,cases)
    run=RunDirectory(tmp_path/'run')
    with run.lock():
        run.create(jobs,manifest)
    rows=[]
    for job in jobs:
        case=next(c for c in cases if c.id==job.case_id)
        state=start_conversation(job,case)
        while pending:=next_turn_job(state):
            external=run.opaque(pending)
            rows.append({'request_sha256':canonical_digest(build_payload(external)),
                'input_bound_tokens':1000,'status':200,'request_id':f'req_offline_{len(rows)}',
                'body':response_body(len(rows))})
            state=accept_turn(state,pending,TurnResponse(job_id=job.job_id,
                turn_index=pending.assistant_turn_index,content='Synthetic offline portfolio. No measurement claim.',
                input_tokens=200,output_tokens=20,cost=.00024,latency_seconds=.001))
    fixture=run.inside('worker/replay.json')
    fixture.parent.mkdir(parents=True)
    fixture.write_text(json.dumps({'responses':rows}))
    replay=ReplayBundle.load(fixture)
    approval=ExecutionApproval(approved=True,mode='offline',run_id=config.run_id,
        account_id='offline-account',project_id='offline-project',expires_at=datetime.now(UTC)+timedelta(hours=1),
        budget_override_approved=True,bindings=approval_bindings(run),input_profile_sha256=replay.profile_sha256)
    approval_file=run.inside('worker/approval.json')
    approval_file.write_text(approval.model_dump_json())
    guard=Task9Guard(run,approval,transport_account_id='offline-account',transport_project_id='offline-project')
    return run,approval_file,fixture,replay,guard


def test_seventy_request_offline_rehearsal_resumes_and_emits_only_technical_evidence(prepared):
    from task9.verifier import (
        create_resume_checkpoint,
        generate_isolated_reports,
        verify_technical_run,
        write_technical_report,
    )
    run,approval_path,_fixture,replay,guard=prepared
    worker=Worker(guard,replay,replay)
    checkpoint=run.inside('worker/checkpoint.json')
    turns=0
    while run.pending():
        outgoing=run.inside(f'exchange/out-{turns:03d}.jsonl')
        assert run.export(outgoing)==1
        job=read_records(outgoing,TurnJob)[0]
        result=worker.process(job)
        incoming=run.inside(f'exchange/in-{turns:03d}.jsonl')
        incoming.write_text(result.model_dump_json()+'\n')
        assert run.ingest(incoming)==1
        turns+=1
        if turns==1:
            prior=run.inside('records/turns.jsonl').read_bytes()
            create_resume_checkpoint(run,worker_ledger=run.inside('worker'),output=checkpoint)
            resumed=cli('resume-proof','--run-dir',run.path,'--checkpoint',checkpoint)
            assert resumed.returncode==0,resumed.stdout+resumed.stderr
            assert run.inside('records/turns.jsonl').read_bytes()==prior
            worker=Worker(Task9Guard(run,guard.approval,transport_account_id='offline-account',
                transport_project_id='offline-project'),replay,replay)
    assert turns==70 and len(run.responses)==30
    leaked = ('offline'+'-synthetic-credential') in run.inside('records/turns.jsonl').read_text()
    assert not leaked
    assert json.loads(run.turns[0].raw_response)['provider_response']['metadata'] == {
        'api_key':'[REDACTED]',
    }
    generate_isolated_reports(run)
    report=verify_technical_run(run,worker_ledger=run.inside('worker'),checkpoint=checkpoint,
                                mode='offline',approval=approval_path)
    assert report.technical_checks_passed,report.diagnostics
    assert report.scientific_gate_passed is False
    assert report.live_execution_authorized is False
    assert report.coverage.provider_attempts==70
    output=report.model_dump_json()
    for forbidden in ('Synthetic offline portfolio','case_effects','win_tie_loss','qualified_distinct','primary_effect'):
        assert forbidden not in output
    written=write_technical_report(report,run.inside('reports/technical.md'),run.inside('reports/technical.json'))
    assert len(written)==2
    assert json.loads(run.inside('reports/technical.json').read_text())['mode']=='offline'
    run.snapshot()
    assert run.verify()['jobs']==30
    assert yaml.safe_load((BENCH/'study/stage-gates.yaml').read_text())['execution_authorized'] is False


def test_cli_offline_process_identity_and_cached_replay(prepared):
    run,approval_path,fixture,_replay,guard=prepared
    outgoing=run.inside('exchange/out-first.jsonl')
    run.export(outgoing)
    output=run.inside('exchange/response.jsonl')
    base=('process','--run-dir',run.path,'--approval',approval_path,'--outbox',outgoing,
          '--output',output,'--fixtures',fixture,'--mode','offline','--project-id','offline-project')
    wrong=cli(*base,'--account-id','other-account')
    assert wrong.returncode!=0
    assert not output.exists()
    assert guard.records()==[]
    good=cli(*base,'--account-id','offline-account')
    assert good.returncode==0,good.stdout+good.stderr
    before=output.read_bytes()
    repeat=cli(*base,'--account-id','offline-account')
    assert repeat.returncode==0,repeat.stdout+repeat.stderr
    assert output.read_bytes()==before
    assert guard.verify()['attempts']==1
