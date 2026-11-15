import pytest

from systematic_innovation_bench.statistics import (
    AnalysisRecord,
    bootstrap_case_ci,
    efficiency,
    holm_adjust,
    paired_case_effects,
    win_tie_loss,
)


def record(case, condition, qualified, **kw):
    return AnalysisRecord(case_id=case, condition=condition, qualified=qualified, raw_distinct=qualified,
                          total_assistant_output_tokens=2000, **kw)


def test_efficiency_uses_all_assistant_tokens_and_missing_never_becomes_estimate():
    assert efficiency(4, 2000) == 2
    with pytest.raises(ValueError):
        efficiency(4, None)
    with pytest.raises(ValueError):
        efficiency(4, 0)


def test_case_is_analysis_unit_replicates_average_and_failure_zero_is_retained():
    rows = [record('a', 't', 4), record('a', 't', 8), record('a', 'c', 2),
            record('b', 't', 9, status='failed'), record('b', 'c', 2)]
    effects = paired_case_effects(rows, 't', 'c')
    assert [e.difference for e in effects] == [2, -1]
    assert [e.case_id for e in effects] == ['a', 'b']
    assert effects[0].treatment_replicates == 2
    assert effects[1].treatment_raw == 0


def test_unpaired_or_unknown_accounting_disclosed_and_not_silently_dropped():
    rows = [record('a', 't', 4)]
    effects = paired_case_effects(rows, 't', 'c')
    assert len(effects) == 1
    assert effects[0].difference is None
    assert effects[0].missing == 1
    with pytest.raises(ValueError):
        bootstrap_case_ci(effects, 100, 1)


def test_seeded_percentile_and_bca_bootstrap_cases():
    effects = paired_case_effects([record(str(i), c, q) for i in range(4)
                                  for c, q in [('t', 2 * (i + 1)), ('c', 0)]], 't', 'c')
    interval = bootstrap_case_ci(effects, 2000, 17)
    assert interval == bootstrap_case_ci(effects, 2000, 17)
    assert interval.estimate == 2.5
    assert interval.n_cases == 4
    assert interval.lower < interval.estimate < interval.upper
    bca = bootstrap_case_ci(effects, 2000, 17, method='bca')
    assert bca.method == 'bca'
    assert bca.lower < bca.upper
    constant = bootstrap_case_ci([e for e in effects[:1]], 100, 4, method='bca')
    assert constant.lower == constant.upper == 1


def test_win_tie_loss_margin_and_holm_monotone_stepdown():
    effects = paired_case_effects([record(str(i), c, q) for i in range(3)
                                  for c, q in [('t', [4, 2, 0][i]), ('c', 2)]], 't', 'c')
    assert win_tie_loss(effects, 0.1).model_dump() == {'wins': 1, 'ties': 1, 'losses': 1, 'missing': 0}
    assert holm_adjust([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    with pytest.raises(ValueError):
        holm_adjust([float('nan')])


def test_unmeasured_success_is_missing_and_never_an_observed_zero():
    rows = [record('a', 't', 0, measured=False), record('a', 'c', 2)]
    effects = paired_case_effects(rows, 't', 'c')
    assert effects[0].difference is None
    assert effects[0].missing == 1


def test_pairing_requires_the_same_model_and_host_configuration():
    rows = [record('a', 't', 8, model='model-one'), record('a', 'c', 2, model='model-two')]
    effect = paired_case_effects(rows, 't', 'c')[0]
    assert effect.difference is None
    assert effect.missing_configurations == 2


def test_case_effect_averages_paired_configuration_means_before_case_mean():
    rows = [record('a', 't', 8, model='model-one'), record('a', 't', 8, model='model-one'),
            record('a', 'c', 2, model='model-one'), record('a', 't', 2, model='model-two'),
            record('a', 'c', 4, model='model-two')]
    effect = paired_case_effects(rows, 't', 'c')[0]
    assert effect.treatment == 2.5
    assert effect.control == 1.5
    assert effect.difference == 1.0
    assert effect.paired_configurations == 2


def test_degenerate_bootstrap_explicitly_discloses_no_estimable_case_variation():
    one = paired_case_effects([record('a', 't', 4), record('a', 'c', 2)], 't', 'c')
    result = bootstrap_case_ci(one, 100, 7, method='bca')
    assert result.degenerate is True
    assert result.degeneracy_reason == 'fewer-than-two-complete-cases'
    constant = paired_case_effects([record(case, arm, q) for case in ('a', 'b')
                                    for arm, q in (('t', 4), ('c', 2))], 't', 'c')
    result = bootstrap_case_ci(constant, 100, 7, method='bca')
    assert result.degenerate is True
    assert result.degeneracy_reason == 'constant-case-effects'
