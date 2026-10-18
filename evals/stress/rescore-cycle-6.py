# Reproduce the Cycle 6 exploratory measurement from immutable Cycle 5 generations.
import hashlib
import json
import platform
import subprocess
from pathlib import Path
from tools.score_eval_results import summarize_results

root = Path(__file__).resolve().parents[2]
conditions = ['baseline_clean', 'control_creative', 'skill_treatment']
cohorts = {
    'stress': ('evals/stress/cases.json', 'cycle-5-stress-controls', 'cycle-5-stress-treatment'),
    'pilot': ('evals/pilot/cases.json', 'cycle-5-pilot-controls', 'cycle-5-pilot-treatment'),
}
all_results = {}
integrity = []
pending = []
for corpus, (case_file, control_dir, treatment_dir) in cohorts.items():
    cases = json.loads((root / case_file).read_text())['cases']
    case_map = {case['id']: case for case in cases}
    wanted = sum(int(case.get('replicates', 2 if case['should_trigger'] else 1)) for case in cases)
    summaries = {}
    for condition in conditions:
        source = root / 'evals/stress/results' / (treatment_dir if condition == 'skill_treatment' else control_dir) / f'{condition}.jsonl'
        rows = [json.loads(line) for line in source.read_text().splitlines()] if source.exists() else []
        if len(rows) != wanted:
            pending.append(f'{corpus}/{condition}: {len(rows)}/{wanted}')
            continue
        keys = [(row['case_id'], row['replicate']) for row in rows]
        if len(set(keys)) != wanted:
            raise ValueError('Duplicate keys in ' + str(source))
        expected_keys = {(case['id'], rep) for case in cases for rep in range(1, int(case.get('replicates', 2 if case['should_trigger'] else 1)) + 1)}
        if set(keys) != expected_keys:
            raise ValueError('Missing/unexpected case replicate keys')
        for row in rows:
            case = case_map[row['case_id']]
            if row['condition'] != condition or row['model'] != 'gpt-5.6-luna':
                raise ValueError('Condition/model mismatch')
            turns = row['turns']
            if len(turns) != 1 + len(case['user_turns']):
                raise ValueError('Turn-count mismatch')
            if not turns[0]['user'].endswith(case['prompt']) or [turn['user'] for turn in turns[1:]] != case['user_turns']:
                raise ValueError('Disclosure mismatch')
            if row['final_response'] != turns[-1]['assistant']:
                raise ValueError('Final-response mismatch')
        modes = {row.get('token_accounting') for row in rows}
        if len(modes) != 1:
            raise ValueError('Mixed accounting semantics; inspect instead of guessing')
        legacy_cumulative = modes == {'provider'}
        if not legacy_cumulative and modes != {'provider_cumulative_differenced'}:
            raise ValueError('Unknown token accounting')
        summary = summarize_results(rows, cases, provider_usage_cumulative=legacy_cumulative)
        summary['source'] = str(source.relative_to(root))
        summary['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        summary['all_assistant_output_tokens'] = sum(row['total_assistant_output_tokens'] for row in summary['records'])
        summary['legacy_cumulative_correction'] = legacy_cumulative
        summaries[condition] = summary
        integrity.append({'corpus': corpus, 'condition': condition, 'records': wanted, 'assistant_turns': sum(len(row['turns']) for row in rows),
                          'exact_keys_and_disclosures': True, 'source_sha256': summary['source_sha256']})
    all_results[corpus] = summaries
if pending:
    print('Pending: ' + '; '.join(pending))
    raise SystemExit(2)

old = json.loads((root / 'evals/stress/results/cycle-5-comparison.json').read_text())
for row in integrity:
    original = next(r for r in old['integrity'] if (r['corpus'], r['condition']) == (row['corpus'], row['condition']))
    assert row == original, 'Raw source or integrity changed'
output = root / 'evals/stress/results/cycle-6-comparison.json'
output.write_text(json.dumps({'measurement_source_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [root / 'tools/pilot_metrics.py', root / 'tools/score_eval_results.py']}, 'analysis_python': platform.python_version(), 'candidate_base_revision': '6f3acb9', 'analysis_base_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(), 'supersedes_measurement': 'cycle-5-comparison.json', 'monetary_cost': None, 'latency': None, 'scope': 'Exploratory public development diagnostics; same raw generations as Cycle 5; no calibrated semantic quality scores or primary endpoint', 'integrity': integrity, 'cohorts': all_results}, indent=2) + '\n')
print('Validated unchanged 192 conversations / 333 turns; saved Cycle 6 measurement')
