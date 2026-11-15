"""Transparent aggregate reports, with no inferred semantic quality ratings."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Sequence
from pathlib import Path
from statistics import mean, median
from typing import Any

from .models import Job, ResponseRecord, ScoreRecord
from .scoring.mechanisms import (
    distinct_mechanism_count,
    gate_failures,
    qualified_distinct_mechanism_count,
    validate_semantic_equivalences,
)
from .statistics import (
    PRIMARY_ENDPOINT,
    AnalysisRecord,
    bootstrap_case_ci,
    paired_case_effects,
    win_tie_loss,
)

CONFIRMATORY = ('total_distinct_mechanisms', 'vendi_score', 'duplicate_collapse_ratio',
                'useful_mechanism_proportion', 'duplicate_reduction', 'genericity_reduction',
                'constraint_responsiveness', 'system_awareness', 'preservation_awareness',
                'ideation_scope_compliance', 'hidden_mechanism_recovery',
                'human_pairwise_preference', 'length_controlled_pairwise_preference')


def build_report_data(jobs: Sequence[Job], responses: Sequence[ResponseRecord], scores: Sequence[ScoreRecord],
                      *, skill_revision: str, runner_revision: str, benchmark_version: str = '0.1.0',
                      calibration_status: str = 'not-assessed', human_primary: bool = False,
                      headline_automated_claim: bool = False, bootstrap_repetitions: int = 2000,
                      seed: int = 0, equivalence_margin: float = 0.0,
                      confirmatory_metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    calibrated = calibration_status == 'passed'
    if headline_automated_claim and not calibrated:
        raise ValueError('human calibration required for headline automated claim')
    jobmap, responsemap, scoremap = {j.job_id: j for j in jobs}, {r.job_id: r for r in responses}, {s.job_id: s for s in scores}
    if len(jobmap) != len(jobs) or len(responsemap) != len(responses) or len(scoremap) != len(scores):
        raise ValueError('duplicate report identifiers')
    if not set(responsemap) <= set(jobmap) or not set(scoremap) <= set(jobmap):
        raise ValueError('uncorrelated report records')
    records = []
    lower_records = []
    upper_records = []
    rating_job_bounds: list[dict[str, Any]] = []
    semantic_decisions: dict[str, object] = {}
    rejections: Counter[str] = Counter()
    counts: Counter[str] = Counter(raw_extracted_candidates=0, raw_distinct_families=0,
                                  qualified_candidates=0, qualified_distinct_families=0,
                                  total_assistant_output_tokens=0, final_response_output_tokens=0,
                                  missing_token_records=0, failures=0, pending_jobs=0,
                                  unscored_jobs=0, incompletely_rated_jobs=0, unrated_candidates=0)
    strata: dict[str, dict[str, Any]] = {name: {} for name in ('model', 'host', 'interaction_mode', 'family')}
    for job in jobs:
        response, score = responsemap.get(job.job_id), scoremap.get(job.job_id)
        if response is None:
            counts['pending_jobs'] += 1
        if score is None:
            counts['unscored_jobs'] += 1
        mechanisms = score.mechanisms if score else ()
        unrated = sum(mechanism.quality is None for mechanism in mechanisms)
        retained_equivalences = score.metrics.get('semantic_equivalences', []) if score else []
        semantic_pairs = validate_semantic_equivalences(mechanisms, retained_equivalences)
        if semantic_pairs:
            semantic_decisions[job.job_id] = retained_equivalences
        tokens = response.total_assistant_output_tokens if response else None
        status = response.status if response else 'pending'
        incomplete_ratings = status == 'succeeded' and score is not None and unrated > 0
        counts['unrated_candidates'] += unrated
        counts['incompletely_rated_jobs'] += incomplete_ratings
        qualified = qualified_distinct_mechanism_count(mechanisms, semantic_pairs) if status == 'succeeded' else 0
        raw = distinct_mechanism_count(mechanisms, semantic_pairs)
        counts['raw_extracted_candidates'] += len(mechanisms)
        counts['raw_distinct_families'] += raw
        counts['qualified_distinct_families'] += qualified
        counts['qualified_candidates'] += sum(not gate_failures(m.quality) for m in mechanisms)
        for mechanism in mechanisms:
            rejections.update(gate_failures(mechanism.quality))
        counts['total_assistant_output_tokens'] += tokens or 0
        final_tokens = (response.conversation.final_response_output_tokens if response and response.conversation
                        else response.output_tokens if response else None)
        counts['final_response_output_tokens'] += final_tokens or 0
        counts['missing_token_records'] += tokens is None
        counts['failures'] += status not in ('succeeded', 'pending')
        record = AnalysisRecord(case_id=job.case_id, condition=job.condition.value, qualified=qualified,
                                raw_distinct=raw, total_assistant_output_tokens=tokens,
                                cost=response.cost if response else None,
                                latency_seconds=response.latency_seconds if response else None, status=status,
                                measured=response is not None and (
                                    status != 'succeeded' or (score is not None and not incomplete_ratings)),
                                model=job.model, host=job.host, interaction_mode=job.interaction_mode.value,
                                family=str(score.metrics.get('family', 'unspecified')) if score else 'unspecified')
        records.append(record)
        # Sensitivity scenarios use the observed extraction without declaring an
        # unrated mechanism a measured failure. Known failed candidates stay out
        # of the possible-qualification set; retained semantic decisions apply
        # before counting its possible families.
        possible = [m for m in mechanisms if m.quality is None or not gate_failures(m.quality)]
        possible_ids = {m.id for m in possible}
        possible_pairs = [pair for pair in semantic_pairs if set(pair) <= possible_ids]
        upper_qualified = (max(qualified, distinct_mechanism_count(possible, possible_pairs))
                           if status == 'succeeded' else 0)
        bound_known = response is not None and (status != 'succeeded' or score is not None)
        unavailable_reason = ('generation_pending' if response is None else
                              'missing_scored_extraction' if not bound_known else
                              'missing_or_nonpositive_total_assistant_tokens' if not tokens else None)
        available = unavailable_reason is None
        rating_job_bounds.append({
            'job_id': job.job_id,
            'qualified_distinct_lower': qualified if bound_known else None,
            'qualified_distinct_upper': upper_qualified if bound_known else None,
            'primary_rate_lower': 1000 * qualified / tokens if available and tokens else None,
            'primary_rate_upper': 1000 * upper_qualified / tokens if available and tokens else None,
            'unrated_candidates': unrated,
            'unavailable_reason': unavailable_reason,
        })
        lower_records.append(record.model_copy(update={'measured': bound_known}))
        upper_records.append(record.model_copy(update={'qualified': upper_qualified, 'measured': bound_known}))
    effects = paired_case_effects(records, 'full-skill', 'format-matched')
    def intervals(rows: Sequence[AnalysisRecord]) -> dict[str, Any]:
        paired = paired_case_effects(rows, 'full-skill', 'format-matched')
        if not any(e.difference is not None for e in paired):
            return {'percentile': None, 'bca': None, 'median_percentile': None, 'median_bca': None,
                    'paired_cases': len(paired), 'missing_cases': len(paired)}
        result: dict[str, Any] = {}
        for statistic in ('mean', 'median'):
            for method in ('percentile', 'bca'):
                key = method if statistic == 'mean' else f'median_{method}'
                result[key] = bootstrap_case_ci(paired, bootstrap_repetitions, seed,
                                                method=method, statistic=statistic).model_dump()
        result.update(paired_cases=len(paired), missing_cases=sum(e.difference is None for e in paired))
        return result
    for dimension in strata:
        grouped: dict[str, list[AnalysisRecord]] = defaultdict(list)
        for row in records:
            grouped[getattr(row, dimension)].append(row)
        strata[dimension] = {label: {'n_records': len(rows), 'primary_effect': intervals(rows)}
                             for label, rows in sorted(grouped.items())}
    primary_effect = intervals(records)
    def sensitivity_contrast(optimistic: bool) -> dict[str, Any]:
        treatment_rows = upper_records if optimistic else lower_records
        control_rows = lower_records if optimistic else upper_records
        rows = ([row for row in treatment_rows if row.condition == 'full-skill']
                + [row for row in control_rows if row.condition == 'format-matched'])
        paired = paired_case_effects(rows, 'full-skill', 'format-matched')
        values = [effect.difference for effect in paired if effect.difference is not None]
        missing = sum(effect.difference is None for effect in paired)
        available = bool(values) and missing == 0
        return {'mean': mean(values) if available else None,
                'median': median(values) if available else None,
                'paired_cases': len(paired), 'missing_cases': missing,
                'unavailable_reason': None if available else 'incomplete_paired_rating_or_token_bounds',
                'case_effects': [effect.model_dump() for effect in paired]}

    rating_sensitivity = {
        'scope': 'Observed extracted candidates and retained family equivalences only; not confidence intervals.',
        'lower_assumption': 'Only candidates already passing every quality gate qualify.',
        'upper_assumption': 'Unrated candidates may qualify; known gate failures remain excluded, then families are deduplicated.',
        'job_bounds': rating_job_bounds,
        'pessimistic_contrast': sensitivity_contrast(False),
        'optimistic_contrast': sensitivity_contrast(True),
    }
    eligible = bool(
        calibrated and counts['unscored_jobs'] == 0 and counts['pending_jobs'] == 0
        and counts['missing_token_records'] == 0 and counts['incompletely_rated_jobs'] == 0
        and primary_effect['percentile'] is not None and primary_effect['missing_cases'] == 0
    )
    if headline_automated_claim and not eligible:
        raise ValueError('complete paired measurements required for headline automated claim')
    limitations = ['Measures systematic ideation performance; realized innovation and global novelty are untested.',
                   'Lexical structural clustering is an aid; retained human or LLM semantic equivalence evidence is required for ambiguous paraphrases.',
                   'Missing provider metadata stays missing; no token estimates are substituted.',
                   'Unrated candidates make primary measurements incomplete; qualified counts remain lower bounds until ratings are complete. Public draft study gates have not been executed.']
    if primary_effect['percentile'] and primary_effect['percentile']['degenerate']:
        limitations.append(
            'The primary bootstrap interval is degenerate: ' +
            primary_effect['percentile']['degeneracy_reason'] +
            '. A zero-width resampling interval does not establish population precision.')
    if not calibrated:
        limitations.append('Automated judging is uncalibrated; no headline automated claim is allowed.')
    count_data: dict[str, Any] = dict(counts)
    count_data['rejections'] = dict(rejections)
    count_data['sample_jobs'] = len(jobs)
    return {'primary_endpoint': PRIMARY_ENDPOINT, 'primary_contrast': 'full-skill minus format-matched',
                'primary_effect': primary_effect, 'win_tie_loss': win_tie_loss(effects, equivalence_margin).model_dump(),
                'counts': count_data, 'quality_gate': {'relevance': 2, 'constraint_alignment': 2, 'causal_clarity': 2,
                                                    'plausibility': 1, 'critical_safety_violation': False},
                'confirmatory_endpoints': {k: (confirmatory_metrics or {}).get(k, 'not-assessed') for k in CONFIRMATORY},
                'exploratory_endpoints': {'receptivity': 'not-assessed', 'cross_domain_transfer': 'not-assessed',
                                           'provocation_quality': 'not-assessed', 'combination_quality': 'not-assessed',
                                           'question_usefulness': 'not-assessed'},
                'efficiency': {'tokens': 'all assistant turns', 'total_cost': sum(r.cost or 0 for r in responses),
                                'missing_cost_records': sum(r.cost is None for r in responses),
                                'total_latency_seconds': sum(r.latency_seconds or 0 for r in responses),
                                'missing_latency_records': sum(r.latency_seconds is None for r in responses)},
                'strata': strata, 'judge_calibration_status': calibration_status, 'human_primary': human_primary,
                'headline_automated_claim_allowed': eligible,
                'case_effects': [effect.model_dump() for effect in effects],
                'rating_sensitivity': rating_sensitivity,
                'semantic_equivalence_decisions': semantic_decisions,
                'revisions': {'skill': skill_revision, 'runner': runner_revision, 'benchmark': benchmark_version},
                'exclusions': [], 'deviations': [], 'limitations': limitations}


def write_json_report(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')


def write_markdown_report(data: dict[str, Any], path: Path) -> None:
    effect = data['primary_effect']['percentile']
    lead = (f"{effect['estimate']:.4g} (95% CI {effect['lower']:.4g} to {effect['upper']:.4g}; "
            f"{effect['n_cases']} paired cases)" if effect else 'unavailable: incomplete paired measurements or token accounting')
    counts = data['counts']
    text = (f"# Systematic ideation performance\n\nPrimary paired effect: {lead}.\n\n"
            f"Endpoint: `{data['primary_endpoint']}`. Contrast: {data['primary_contrast']}.\n\n"
            f"Raw extracted candidates: {counts['raw_extracted_candidates']}; raw distinct families: {counts['raw_distinct_families']}; "
            f"qualified candidates: {counts['qualified_candidates']}; qualified distinct families: {counts['qualified_distinct_families']}.\n\n"
            f"Total assistant output tokens: {counts['total_assistant_output_tokens']}; final response tokens: {counts['final_response_output_tokens']}; "
            f"missing token records: {counts['missing_token_records']}; failures: {counts['failures']}; "
            f"pending jobs: {counts['pending_jobs']}; unscored jobs: {counts['unscored_jobs']}; "
            f"incompletely rated jobs: {counts['incompletely_rated_jobs']}; unrated candidates: {counts['unrated_candidates']}.\n\n"
            f"Qualification thresholds: {json.dumps(data['quality_gate'], sort_keys=True)}.\n\n"
            f"Rejections by criterion (overlapping): {json.dumps(counts['rejections'], sort_keys=True)}.\n\n"
            f"Win/tie/loss and missing: {json.dumps(data['win_tie_loss'], sort_keys=True)}.\n\n"
            f"Calibration: {data['judge_calibration_status']}.\n\n")
    for name in ('confirmatory_endpoints', 'exploratory_endpoints', 'efficiency', 'strata', 'case_effects', 'rating_sensitivity', 'semantic_equivalence_decisions', 'revisions', 'exclusions', 'deviations'):
        text += f"## {name.replace('_', ' ').capitalize()}\n\n```json\n{json.dumps(data[name], indent=2, sort_keys=True)}\n```\n\n"
    text += '## Limitations\n\n' + '\n'.join(f'- {item}' for item in data['limitations']) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
