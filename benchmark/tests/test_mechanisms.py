import pytest

from systematic_innovation_bench.models import Mechanism, MechanismQuality
from systematic_innovation_bench.scoring.mechanisms import (
    bipartite_mechanism_recovery,
    distinct_mechanism_count,
    extract_mechanisms,
    hungarian_maximum_weight,
    passes_quality_gate,
    qualified_distinct_mechanism_count,
    vendi_score,
)


def mechanism(**changes):
    data = {'id': 'a', 'intervention_point': 'queue', 'actor': 'staff', 'changed_flow': 'jobs',
                'causal_operation': 'pool demand', 'intended_effect': 'reduce delay'}
    return Mechanism(**(data | changes))


def quality(**changes):
    return MechanismQuality(**({'relevance': 2, 'constraint_alignment': 2, 'causal_clarity': 2,
                                    'plausibility': 1, 'critical_safety_violation': False} | changes))


def test_gate_is_conjunctive_and_unrated_never_qualifies():
    assert passes_quality_gate(quality())
    for field, value in [('relevance', 1), ('constraint_alignment', 1), ('causal_clarity', 1),
                         ('plausibility', 0), ('critical_safety_violation', True)]:
        assert not passes_quality_gate(quality(**{field: value}))
    assert qualified_distinct_mechanism_count([mechanism()]) == 0


def test_gate_precedes_clustering_and_actor_alone_is_variant():
    items = [mechanism(quality=quality(relevance=1)),
             mechanism(id='b', actor='volunteers', quality=quality()),
             mechanism(id='c', changed_flow='money', causal_operation='escrow payment', quality=quality())]
    assert distinct_mechanism_count(items) == 2
    assert qualified_distinct_mechanism_count(items) == 2


def test_paraphrases_merge_but_different_causal_flow_does_not():
    a = mechanism(changed_flow='tasks', causal_operation='pool requests', intended_effect='reduce waiting')
    b = mechanism(id='b', changed_flow='jobs', causal_operation='combine demand', intended_effect='cut delay')
    c = mechanism(id='c', changed_flow='payment', causal_operation='pool requests')
    assert distinct_mechanism_count([a, b]) == 1
    assert distinct_mechanism_count([a, c]) == 2


def test_hungarian_is_global_optimum_and_one_to_one():
    # Greedy 0.9 at (0,0) would yield only 1.0, optimal assignment yields 1.65.
    pairs = hungarian_maximum_weight([[0.9, 0.8], [0.85, 0.1]])
    assert set(pairs) == {(0, 1), (1, 0)}
    assert hungarian_maximum_weight([]) == []
    assert len(hungarian_maximum_weight([[1], [0.9], [0.8]])) == 1
    with pytest.raises(ValueError):
        hungarian_maximum_weight([[1, 2], [1]])


def test_recovery_deduplicates_gold_matches():
    result = bipartite_mechanism_recovery([mechanism(), mechanism(id='b')], ['pool demand'])
    assert result['matched'] == 1
    assert result['recall'] == 1
    assert result['precision'] == 0.5
    assert bipartite_mechanism_recovery([], [])['matched'] == 0


def test_vendi_identical_and_orthogonal_endpoints():
    assert vendi_score([mechanism(), mechanism(id='b')]) == pytest.approx(1)
    assert vendi_score([mechanism(intervention_point='alpha', changed_flow='beta',
                                  causal_operation='gamma', intended_effect='delta'),
                        mechanism(id='b', intervention_point='epsilon', changed_flow='zeta',
                                  causal_operation='eta', intended_effect='theta')]) == pytest.approx(2)
    assert vendi_score([]) == 0


def test_extraction_reads_final_structured_portfolio_without_fabricating_quality():
    text = 'P1: Shared queue | Intervention: reception | Lever: pool demand | Chain: arrivals -> shared slots -> less delay | Preserve: access'
    extracted = extract_mechanisms(text)
    assert len(extracted) == 1
    assert extracted[0].quality is None
    assert qualified_distinct_mechanism_count(extracted) == 0
    assert extract_mechanisms('What resources do you have?') == []


def test_reviewed_semantic_equivalence_flows_to_raw_and_gated_counts():
    from systematic_innovation_bench.scoring.mechanisms import validate_semantic_equivalences
    items = [mechanism(quality=quality()),
             mechanism(id='b', intervention_point='intake capacity', changed_flow='unclaimed slots',
                       causal_operation='share unused appointments', intended_effect='shorten time to service',
                       quality=quality())]
    evidence = [{'left': 'a', 'right': 'b', 'evidence': 'Both change unused-slot allocation before intake.'}]
    pairs = validate_semantic_equivalences(items, evidence)
    assert distinct_mechanism_count(items, pairs) == 1
    assert qualified_distinct_mechanism_count(items, pairs) == 1
    items[0] = items[0].model_copy(update={'quality': quality(relevance=1)})
    assert qualified_distinct_mechanism_count(items, pairs) == 1


@pytest.mark.parametrize('evidence', [
    [{'left': 'a', 'right': 'b', 'evidence': ''}],
    [{'left': 'a', 'right': 'unknown', 'evidence': 'observed'}],
    [{'left': 'a', 'right': 'a', 'evidence': 'observed'}],
    [['a', 'b']],
])
def test_semantic_equivalence_requires_retained_evidence_and_known_distinct_ids(evidence):
    from systematic_innovation_bench.scoring.mechanisms import validate_semantic_equivalences
    with pytest.raises(ValueError):
        validate_semantic_equivalences([mechanism(), mechanism(id='b')], evidence)
