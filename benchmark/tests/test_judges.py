"""Blinding and evidence protocols exercise real packet and aggregation boundaries."""
from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from systematic_innovation_bench.models import Mechanism, ResponseRecord, ScoreRecord
from systematic_innovation_bench.scoring.judges import (
    MechanismQualityJudgment,
    PairwiseJudgment,
    aggregate_pairwise,
    assemble_mechanism_quality,
    build_mechanism_quality_jobs,
    build_pairwise_jobs,
    validate_quality_judgment,
)


def answers():
    return (
        ResponseRecord(job_id="run:case:full-skill:0:GENERATOR-X:HOST-X", status="succeeded",
                       content="Model: GENERATOR-X\nCondition: full-skill\nPool unused capacity."),
        ResponseRecord(job_id="run:case:format-matched:0:GENERATOR-X:HOST-X", status="succeeded",
                       content="Skill: systematic-innovation\nFile: private-name.md\nMove work earlier."),
    )


def jobs(judge_families=("judge-one",)):
    left, right = answers()
    return build_pairwise_jobs(
        left, right, user_transcript=("Initial user context", "Fixed disclosure one", "Final disclosure"),
        criterion="causal-diversity", seed=17, judge_families=judge_families,
        generator_families=("GENERATOR-X",),
        identity_labels=("GENERATOR-X", "HOST-X", "private-name.md"),
    )


def judgment(job, preference="left"):
    assignment = job.private_assignment
    winner = ("A" if assignment.a_source == assignment.left_source else "B")
    if preference == "right":
        winner = "B" if winner == "A" else "A"
    elif preference in ("tie", "abstain"):
        winner = preference
    return PairwiseJudgment(
        job_id=job.job_id, criterion="causal-diversity", winner=winner,
        evidence={"causal-diversity": "Different timing changes the operational causal path."},
    )


def test_public_pairwise_packets_strip_identity_and_keep_full_user_transcript():
    batch = jobs()
    assert len(batch) == 2
    for job in batch:
        public = job.model_dump_json()
        for label in ("GENERATOR-X", "HOST-X", "full-skill", "format-matched",
                      "systematic-innovation", "private-name.md", "judge-one"):
            assert label not in public
        assert "private_assignment" not in json.loads(public)
        assert job.user_transcript == (
            "Initial user context", "Fixed disclosure one", "Final disclosure",
        )
        assert job.candidate_a in ("Pool unused capacity.", "Move work earlier.")
        assert job.candidate_b in ("Pool unused capacity.", "Move work earlier.")
        assert job.candidate_a != job.candidate_b
        assert all(text in job.prompt for text in job.user_transcript)


def test_seeded_pairwise_packets_preserve_both_orders():
    first = jobs()
    assert [j.model_dump_json() for j in first] == [j.model_dump_json() for j in jobs()]
    assert {(j.candidate_a, j.candidate_b) for j in first} == {
        ("Pool unused capacity.", "Move work earlier."),
        ("Move work earlier.", "Pool unused capacity."),
    }
    assert len({j.job_id for j in first}) == 2


def test_consistent_order_swaps_count_one_win_per_judge_family():
    batch = jobs()
    result = aggregate_pairwise([judgment(j) for j in batch], [j.private_assignment for j in batch])
    assert (result.wins, result.ties, result.losses) == (1, 0, 0)
    assert result.order_consistency == 1.0
    assert result.inconsistent_orders == 0
    assert len(result.evidence) == 2


def test_position_bias_remains_inconsistent_without_a_confident_winner():
    batch = jobs()
    scores = [judgment(j).model_copy(update={"winner": "A"}) for j in batch]
    result = aggregate_pairwise(scores, [j.private_assignment for j in batch])
    assert (result.wins, result.ties, result.losses) == (0, 0, 0)
    assert result.inconsistent_orders == 1
    assert result.order_consistency == 0.0


def test_incomplete_unknown_and_duplicate_pair_scores_are_rejected():
    batch = jobs()
    assignments = [j.private_assignment for j in batch]
    with pytest.raises(ValueError, match="incomplete"):
        aggregate_pairwise([judgment(batch[0])], assignments)
    with pytest.raises(ValueError, match="duplicate"):
        aggregate_pairwise([judgment(batch[0]), judgment(batch[0])], assignments)
    with pytest.raises(ValueError, match="unknown"):
        aggregate_pairwise([judgment(batch[0]).model_copy(update={"job_id": "unknown"}),
                            judgment(batch[1])], assignments)


def test_judge_family_disagreement_and_abstention_are_preserved():
    batch = jobs(("family-one", "family-two"))
    scores = [judgment(j, "left" if j.private_assignment.judge_family == "family-one" else "right")
              for j in batch]
    result = aggregate_pairwise(scores, [j.private_assignment for j in batch])
    assert result.judge_family_disagreement is True
    assert (result.wins, result.losses) == (1, 1)
    abstentions = [judgment(j, "abstain") for j in batch]
    abstained = aggregate_pairwise(abstentions, [j.private_assignment for j in batch])
    assert abstained.abstentions == 2
    assert abstained.wins == abstained.ties == abstained.losses == 0


def test_ties_and_same_generator_family_warning_are_explicit():
    batch = jobs(("GENERATOR-X",))
    result = aggregate_pairwise([judgment(j, "tie") for j in batch],
                                [j.private_assignment for j in batch])
    assert result.ties == 1
    assert result.warnings == ("same-family-judge",)


def test_pairwise_ratings_require_criterion_specific_evidence():
    with pytest.raises(ValidationError, match="criterion-specific evidence"):
        PairwiseJudgment(job_id="opaque", criterion="relevance", winner="A", evidence={})
    batch = jobs()
    score = judgment(batch[0]).model_copy(update={"criterion": "irrelevant-criterion"})
    with pytest.raises(ValueError, match="criterion"):
        aggregate_pairwise([score, judgment(batch[1])], [j.private_assignment for j in batch])


def test_score_records_can_supply_pairwise_judgments_without_losing_evidence():
    batch = jobs()
    scores = [ScoreRecord(job_id=j.job_id,
                          metrics={"criterion": "causal-diversity", "winner": judgment(j).winner},
                          evidence=judgment(j).evidence) for j in batch]
    result = aggregate_pairwise(scores, [j.private_assignment for j in batch])
    assert result.wins == 1
    assert all(item.evidence for item in result.evidence)


def mechanisms():
    return [Mechanism(id="original-mechanism-label", intervention_point="capacity",
                      actor="operator", changed_flow="unused slots",
                      causal_operation="pool capacity", intended_effect="lower delay")]


def quality_jobs():
    return build_mechanism_quality_jobs(
        mechanisms(), final_portfolio="Pool unused capacity to lower delay.",
        user_transcript=("Initial context", "Final disclosure"), seed=23,
    )


def quality_judgment(job, rating=None):
    value = (False if job.criterion == "critical_safety_violation" else 2) if rating is None else rating
    return MechanismQualityJudgment(
        job_id=job.job_id, criterion=job.criterion, rating=value,
        evidence="The quoted intervention directly addresses the stated delay.",
        evidence_span="Pool unused capacity",
    )


def test_quality_packets_use_five_anchored_criteria_without_threshold_or_identity():
    batch = quality_jobs()
    assert {job.criterion for job in batch} == {
        "relevance", "constraint_alignment", "causal_clarity", "plausibility",
        "critical_safety_violation",
    }
    for job in batch:
        public = job.model_dump_json()
        assert "original-mechanism-label" not in public
        assert job.user_transcript == ("Initial context", "Final disclosure")
        assert "evidence" in job.prompt.lower()
        for hidden in ("per_1000", "threshold", "primary numerator", "passes_quality_gate"):
            assert hidden not in job.prompt
        if job.criterion != "critical_safety_violation":
            assert all(f"{n}:" in job.rubric for n in range(4))
        else:
            assert "true" in job.rubric and "false" in job.rubric


def test_complete_mechanism_quality_requires_all_five_observed_evidence_spans():
    batch = quality_jobs()
    observations = [validate_quality_judgment(job, quality_judgment(job)) for job in batch]
    result = assemble_mechanism_quality(observations, batch)
    quality = result["original-mechanism-label"]
    assert quality.relevance == quality.constraint_alignment == quality.causal_clarity == 2
    assert quality.plausibility == 2
    assert quality.critical_safety_violation is False
    assert set(quality.evidence) == {job.criterion for job in batch}
    with pytest.raises(ValueError, match="incomplete"):
        assemble_mechanism_quality(observations[:-1], batch)


def test_quality_validation_refuses_fabricated_spans_and_out_of_range_ratings():
    job = next(j for j in quality_jobs() if j.criterion == "causal_clarity")
    with pytest.raises(ValueError, match="evidence span"):
        validate_quality_judgment(job, quality_judgment(job).model_copy(update={"evidence_span": "invented"}))
    with pytest.raises(ValidationError):
        quality_judgment(job, 4)
    with pytest.raises(ValidationError):
        quality_judgment(job, True)
    safety = next(j for j in quality_jobs() if j.criterion == "critical_safety_violation")
    with pytest.raises(ValidationError):
        quality_judgment(safety, 1)
    with pytest.raises(ValidationError):
        MechanismQualityJudgment(job_id=job.job_id, criterion=job.criterion, rating=2,
                                 evidence="", evidence_span="Pool unused capacity")


def test_quality_packet_ids_do_not_collide_across_portfolios_with_the_same_seed():
    first = quality_jobs()
    second = build_mechanism_quality_jobs(
        mechanisms(), final_portfolio="Move work earlier to reduce delay.",
        user_transcript=("Initial context", "Final disclosure"), seed=23,
    )
    assert not {job.job_id for job in first} & {job.job_id for job in second}


def test_quality_abstention_is_preserved_without_inventing_a_rating():
    batch = quality_jobs()
    job = next(item for item in batch if item.criterion == "plausibility")
    observation = MechanismQualityJudgment(
        job_id=job.job_id, criterion=job.criterion, rating=None, abstained=True,
        evidence="The final answer does not establish the local feasibility assumption.",
        evidence_span="Pool unused capacity", abstention_reason="Insufficient domain knowledge",
    )
    assert validate_quality_judgment(job, observation).rating is None
    observations = [quality_judgment(item) if item != job else observation for item in batch]
    with pytest.raises(ValueError, match="abstention"):
        assemble_mechanism_quality(observations, batch)
