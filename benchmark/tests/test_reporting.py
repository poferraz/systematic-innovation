import json
from datetime import UTC, datetime

import pytest

from systematic_innovation_bench.models import (
    Condition,
    Job,
    Mechanism,
    MechanismQuality,
    ResponseRecord,
    ScoreRecord,
)
from systematic_innovation_bench.reporting import (
    build_report_data,
    write_json_report,
    write_markdown_report,
)


def sample():
    jobs = [Job(run_id='r', case_id='a', condition=c, replicate=0, model='m', host='inbox',
                prompt='Options?', created_at=datetime(2026, 8, 31, tzinfo=UTC))
            for c in [Condition.FULL_SKILL, Condition.FORMAT_MATCHED]]
    quality = MechanismQuality(relevance=2, constraint_alignment=2, causal_clarity=2,
                               plausibility=1, critical_safety_violation=False)
    m = Mechanism(id='a', intervention_point='queue', actor='staff', changed_flow='tasks',
                  causal_operation='pool', intended_effect='less delay', quality=quality)
    scores = [ScoreRecord(job_id=jobs[0].job_id, mechanisms=(m, m.model_copy(update={'id': 'b', 'quality': None}))),
              ScoreRecord(job_id=jobs[1].job_id)]
    responses = [ResponseRecord(job_id=j.job_id, status='succeeded', content='portfolio', output_tokens=1000)
                 for j in jobs]
    return jobs, responses, scores


def test_report_discloses_primary_numerator_denominator_rejections_and_limits(tmp_path):
    data = build_report_data(*sample(), skill_revision='abc', runner_revision='def')
    assert data['primary_endpoint'].startswith('qualified_useful_distinct')
    assert data['primary_effect']['percentile'] is None
    assert data['primary_effect']['missing_cases'] == 1
    assert data['counts']['raw_extracted_candidates'] == 2
    assert data['counts']['raw_distinct_families'] == 1
    assert data['counts']['qualified_distinct_families'] == 1
    assert data['counts']['rejections']['unrated'] == 1
    assert data['counts']['incompletely_rated_jobs'] == 1
    assert data['counts']['unrated_candidates'] == 1
    assert data['counts']['total_assistant_output_tokens'] == 2000
    assert data['headline_automated_claim_allowed'] is False
    assert set(data['strata']) == {'model', 'host', 'interaction_mode', 'family'}
    assert data['confirmatory_endpoints']['preservation_awareness'] == 'not-assessed'
    write_json_report(data, tmp_path/'r.json')
    write_markdown_report(data, tmp_path/'r.md')
    assert json.loads((tmp_path/'r.json').read_text()) == data
    text = (tmp_path/'r.md').read_text()
    assert text.index('Primary paired effect') < text.index('Raw extracted')
    assert 'uncalibrated' in text.lower()
    assert 'systematic ideation performance' in text


def test_failed_calibration_refuses_headline_automated_claim():
    with pytest.raises(ValueError, match='calibration'):
        build_report_data(*sample(), skill_revision='s', runner_revision='r',
                          calibration_status='failed', headline_automated_claim=True)


def test_missing_tokens_cannot_produce_a_confident_primary_effect():
    jobs, responses, scores = sample()
    responses[0] = responses[0].model_copy(update={'output_tokens': None})
    data = build_report_data(jobs, responses, scores, skill_revision='s', runner_revision='r')
    assert data['primary_effect']['percentile'] is None
    assert data['counts']['missing_token_records'] == 1
    assert data['win_tie_loss']['missing'] == 1


def test_unscored_success_is_missing_measurement_and_blocks_claim():
    jobs, responses, scores = sample()
    # Only the control has an actual measurement; the treatment is unscored.
    data = build_report_data(jobs,responses,scores[1:],skill_revision='s',runner_revision='r',
                             calibration_status='passed')
    assert data['primary_effect']['percentile'] is None
    assert data['win_tie_loss']['missing'] == 1
    assert not data['headline_automated_claim_allowed']


def test_pending_generations_and_missing_tokens_block_calibrated_headline():
    jobs, responses, scores = sample()
    data = build_report_data(jobs,[],scores,skill_revision='s',runner_revision='r',calibration_status='passed')
    assert not data['headline_automated_claim_allowed']
    responses[0] = responses[0].model_copy(update={'output_tokens':None})
    data = build_report_data(jobs,responses,scores,skill_revision='s',runner_revision='r',calibration_status='passed')
    assert not data['headline_automated_claim_allowed']


def test_unscored_success_cannot_produce_a_measured_primary_difference():
    jobs, responses, scores = sample()
    data = build_report_data(jobs, responses, scores[1:], skill_revision='s', runner_revision='r')
    assert data['primary_effect']['percentile'] is None
    assert data['primary_effect']['missing_cases'] == 1
    assert data['win_tie_loss']['missing'] == 1


def test_headline_claim_requires_completed_paired_measurements():
    jobs, responses, scores = sample()
    pending = build_report_data(jobs, [], scores, skill_revision='s', runner_revision='r',
                                calibration_status='passed')
    assert pending['headline_automated_claim_allowed'] is False
    with pytest.raises(ValueError, match='complete paired measurements'):
        build_report_data(jobs, [], scores, skill_revision='s', runner_revision='r',
                          calibration_status='passed', headline_automated_claim=True)
    missing = [responses[0].model_copy(update={'output_tokens': None}), responses[1]]
    data = build_report_data(jobs, missing, scores, skill_revision='s', runner_revision='r',
                             calibration_status='passed')
    assert data['headline_automated_claim_allowed'] is False


def test_report_uses_retained_semantic_equivalences_in_both_numerator_disclosures():
    jobs, responses, scores = sample()
    m = scores[0].mechanisms[0]
    paraphrase = m.model_copy(update={'id': 'paraphrase', 'intervention_point': 'intake capacity',
                                     'changed_flow': 'unclaimed slots',
                                     'causal_operation': 'share unused appointments',
                                     'intended_effect': 'shorten time to service'})
    scores[0] = ScoreRecord(job_id=jobs[0].job_id, mechanisms=(m, paraphrase),
        metrics={'semantic_equivalences': [{'left': m.id, 'right': paraphrase.id,
                                            'evidence': 'Same unused-slot allocation operation.'}]})
    data = build_report_data(jobs, responses, scores, skill_revision='s', runner_revision='r')
    assert data['counts']['raw_distinct_families'] == 1
    assert data['counts']['qualified_distinct_families'] == 1
    assert data['primary_effect']['percentile']['estimate'] == 1
    assert data['semantic_equivalence_decisions'][jobs[0].job_id] == scores[0].metrics['semantic_equivalences']
    assert any('degenerate' in limitation.lower() for limitation in data['limitations'])


def test_unrated_distinct_candidate_retains_lower_bound_counts_but_primary_is_missing():
    jobs, responses, scores = sample()
    rated = scores[0].mechanisms[0]
    unrated = rated.model_copy(update={
        'id': 'unknown-quality', 'intervention_point': 'accountability',
        'changed_flow': 'ownership', 'causal_operation': 'delegate authority',
        'intended_effect': 'fewer approvals', 'quality': None,
    })
    scores[0] = ScoreRecord(job_id=jobs[0].job_id, mechanisms=(rated, unrated))
    data = build_report_data(jobs, responses, scores, skill_revision='s', runner_revision='r',
                             calibration_status='passed')
    assert data['counts']['raw_extracted_candidates'] == 2
    assert data['counts']['raw_distinct_families'] == 2
    assert data['counts']['qualified_distinct_families'] == 1
    assert data['counts']['unrated_candidates'] == 1
    assert data['counts']['incompletely_rated_jobs'] == 1
    assert data['primary_effect']['percentile'] is None
    assert data['case_effects'][0]['difference'] is None
    assert data['case_effects'][0]['treatment_raw'] == 2
    assert data['win_tie_loss']['missing'] == 1
    assert data['headline_automated_claim_allowed'] is False


def test_incomplete_ratings_refuse_requested_headline_even_with_passed_calibration():
    with pytest.raises(ValueError, match='complete paired measurements'):
        build_report_data(*sample(), skill_revision='s', runner_revision='r',
                          calibration_status='passed', headline_automated_claim=True)


def test_explicitly_scored_empty_portfolio_remains_measured_zero():
    jobs, responses, scores = sample()
    scores[0] = ScoreRecord(job_id=jobs[0].job_id, mechanisms=())
    data = build_report_data(jobs, responses, scores, skill_revision='s', runner_revision='r',
                             calibration_status='passed', headline_automated_claim=True)
    assert data['primary_effect']['percentile']['estimate'] == 0
    assert data['primary_effect']['missing_cases'] == 0
    assert data['counts']['unrated_candidates'] == 0
    assert data['counts']['incompletely_rated_jobs'] == 0
    assert data['headline_automated_claim_allowed'] is True


def test_unrated_candidate_sensitivity_pairs_treatment_low_with_control_high():
    jobs, responses, scores = sample()
    rated = scores[0].mechanisms[0]
    unrated = rated.model_copy(update={
        'id': 'unknown-quality', 'intervention_point': 'accountability',
        'changed_flow': 'ownership', 'causal_operation': 'delegate authority',
        'intended_effect': 'fewer approvals', 'quality': None,
    })
    scores[0] = ScoreRecord(job_id=jobs[0].job_id, mechanisms=(rated, unrated))
    scores[1] = ScoreRecord(job_id=jobs[1].job_id, mechanisms=(unrated,))
    data = build_report_data(jobs, responses, scores, skill_revision='s', runner_revision='r')
    sensitivity = data['rating_sensitivity']
    treatment, control = sensitivity['job_bounds']
    assert treatment['qualified_distinct_lower'] == 1
    assert treatment['qualified_distinct_upper'] == 2
    assert treatment['primary_rate_lower'] == 1
    assert treatment['primary_rate_upper'] == 2
    assert control['primary_rate_lower'] == 0
    assert control['primary_rate_upper'] == 1
    assert sensitivity['pessimistic_contrast']['mean'] == 0
    assert sensitivity['optimistic_contrast']['mean'] == 2
    assert sensitivity['pessimistic_contrast']['missing_cases'] == 0
    assert data['primary_effect']['percentile'] is None


def test_rating_sensitivity_deduplicates_unknowns_with_retained_equivalence_evidence():
    jobs, responses, scores = sample()
    rated = scores[0].mechanisms[0]
    unrated = rated.model_copy(update={
        'id': 'other-phrasing', 'intervention_point': 'intake capacity',
        'changed_flow': 'unclaimed slots', 'causal_operation': 'share unused appointments',
        'intended_effect': 'shorten time to service', 'quality': None,
    })
    scores[0] = ScoreRecord(job_id=jobs[0].job_id, mechanisms=(rated, unrated), metrics={
        'semantic_equivalences': [{'left': rated.id, 'right': unrated.id,
                                  'evidence': 'Same unused-slot allocation operation.'}],
    })
    data = build_report_data(jobs, responses, scores, skill_revision='s', runner_revision='r')
    treatment = data['rating_sensitivity']['job_bounds'][0]
    assert treatment['qualified_distinct_lower'] == 1
    assert treatment['qualified_distinct_upper'] == 1


def test_rating_sensitivity_preserves_unavailable_token_bounds_instead_of_zero():
    jobs, responses, scores = sample()
    responses[0] = responses[0].model_copy(update={'output_tokens': None})
    data = build_report_data(jobs, responses, scores, skill_revision='s', runner_revision='r')
    sensitivity = data['rating_sensitivity']
    treatment = sensitivity['job_bounds'][0]
    assert treatment['qualified_distinct_lower'] == 1
    assert treatment['qualified_distinct_upper'] == 1
    assert treatment['primary_rate_lower'] is None
    assert treatment['primary_rate_upper'] is None
    assert treatment['unavailable_reason'] == 'missing_or_nonpositive_total_assistant_tokens'
    assert sensitivity['pessimistic_contrast']['mean'] is None
    assert sensitivity['optimistic_contrast']['mean'] is None
    assert sensitivity['pessimistic_contrast']['missing_cases'] == 1
