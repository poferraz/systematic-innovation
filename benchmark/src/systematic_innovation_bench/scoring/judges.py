"""Treatment-blind judge packets, private assignment keys, and evidence aggregation.

Serialization of a judge job deliberately excludes its private assignment. Store
assignment keys in controlled storage unavailable to raters. Human calibration
uses an operator-supplied out-of-repository seed or an isolated exported packet.
This module builds jobs and validates observations; it makes no model calls.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..models import Condition, Mechanism, MechanismQuality, ResponseRecord, ScoreRecord

QualityCriterion = Literal[
    "relevance", "constraint_alignment", "causal_clarity", "plausibility",
    "critical_safety_violation",
]

QUALITY_RUBRICS: dict[QualityCriterion, str] = {
    "relevance": (
        "0: Unrelated to the stated problem. 1: Tangential or only broadly relevant. "
        "2: Directly addresses a stated need. 3: Directly addresses the central need "
        "and explains its fit to the complete user context."
    ),
    "constraint_alignment": (
        "0: Contradicts a stated non-negotiable constraint. 1: Alignment is unclear "
        "or a material constraint is ignored. 2: Respects the explicit constraints. "
        "3: Explains how all material constraints and preservation requirements remain satisfied."
    ),
    "causal_clarity": (
        "0: No identifiable intervention or causal account. 1: Fragment or assertion "
        "without a causal link. 2: Identifiable intervention with an intelligible causal "
        "path to the intended effect. 3: Explicit causal path with actors, changed "
        "flow, effect and material assumptions."
    ),
    "plausibility": (
        "0: Incoherent or incompatible with known constraints. 1: Plausible under "
        "stated but unverified assumptions. 2: Credible operation within the context. "
        "3: Credible operation with supporting context and explicit limits."
    ),
    "critical_safety_violation": (
        "true: The mechanism entails a critical safety or rights violation in the "
        "supplied context. false: No such critical violation is identified. Explain "
        "uncertainty explicitly; do not invent an assurance of deployment safety."
    ),
}


class _JudgeModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, hide_input_in_errors=True, revalidate_instances="always",
    )


class JudgeAssignment(_JudgeModel):
    """Private mapping: never export this record to a judge or human rater."""

    job_id: str
    comparison_id: str
    criterion: str
    judge_family: str
    left_source: str
    right_source: str
    a_source: str
    b_source: str
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_sources(self) -> Self:
        if self.left_source == self.right_source or {self.a_source, self.b_source} != {
            self.left_source, self.right_source,
        }:
            raise ValueError("invalid private source mapping")
        return self


class PairwiseJudgeJob(_JudgeModel):
    job_id: str
    comparison_id: str
    criterion: str
    user_transcript: tuple[str, ...]
    candidate_a: str
    candidate_b: str
    rubric: str
    prompt: str
    private_assignment: JudgeAssignment = Field(exclude=True, repr=False)


class PairwiseJudgment(_JudgeModel):
    job_id: str
    criterion: str
    winner: Literal["A", "B", "tie", "abstain"]
    evidence: dict[str, str]

    @model_validator(mode="after")
    def require_evidence(self) -> Self:
        if not self.criterion.strip() or not self.evidence.get(self.criterion, "").strip():
            raise ValueError("criterion-specific evidence is required")
        return self


class PairwiseResult(_JudgeModel):
    wins: int
    ties: int
    losses: int
    abstentions: int
    inconsistent_orders: int
    complete_judge_pairs: int
    order_consistency: float | None
    judge_family_disagreement: bool
    family_outcomes: dict[str, dict[str, str]]
    warnings: tuple[str, ...]
    evidence: tuple[PairwiseJudgment, ...]


def _opaque(*parts: object) -> str:
    payload = json.dumps(parts, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def _clean(text: str, identity_labels: Sequence[str]) -> str:
    # Administrative headers are not part of the answer's semantic content.
    text = re.sub(
        r"(?im)^\s*(?:condition|treatment|model|host|skill|file|filename)\s*:\s*.*(?:\n|$)",
        "", text,
    )
    labels = {condition.value for condition in Condition} | {"systematic-innovation"}
    labels.update(label for label in identity_labels if label.strip())
    for label in sorted(labels, key=len, reverse=True):
        text = re.sub(r"(?<!\w)" + re.escape(label) + r"(?!\w)", "[identity removed]", text,
                      flags=re.IGNORECASE)
    return text.strip()


def _user_context(transcript: Sequence[str], labels: Sequence[str]) -> tuple[str, ...]:
    if isinstance(transcript, str) or not transcript or any(not turn.strip() for turn in transcript):
        raise ValueError("complete nonempty user transcript is required")
    return tuple(_clean(turn, labels) for turn in transcript)


def _final(response: ResponseRecord) -> str:
    return response.conversation.final_response if response.conversation else response.content


def build_pairwise_jobs(
    left: ResponseRecord,
    right: ResponseRecord,
    *,
    user_transcript: Sequence[str],
    criterion: str,
    seed: int,
    judge_families: Sequence[str],
    generator_families: Sequence[str] = (),
    identity_labels: Sequence[str] = (),
) -> list[PairwiseJudgeJob]:
    """Create two orders per family; serialize jobs separately from private keys.

    ``seed`` is explicit so calibration can supply an external secret seed. Never
    commit a calibration seed or an assignment key accessible to its raters.
    User disclosures must be supplied in their complete, fixed order. Only final
    portfolios are shown as the two answers; no assistant token/cost data are shown.
    """
    if left.job_id == right.job_id:
        raise ValueError("pairwise sources must differ")
    if not criterion.strip() or not judge_families or len(set(judge_families)) != len(judge_families):
        raise ValueError("criterion and unique judge families are required")
    if any(not family.strip() for family in judge_families):
        raise ValueError("judge family must be nonempty")
    labels = (*identity_labels, left.job_id, right.job_id)
    context = _user_context(user_transcript, labels)
    answers = (_clean(_final(left), labels), _clean(_final(right), labels))
    comparison = _opaque("pair", seed, left.job_id, right.job_id, criterion)
    rng = random.Random(seed)
    result = []
    for family_index, family in enumerate(judge_families):
        orders = [(0, 1), (1, 0)]
        rng.shuffle(orders)
        for a_index, b_index in orders:
            job_id = _opaque(comparison, family_index, a_index)
            sources = (left.job_id, right.job_id)
            warnings = (("same-family-judge",) if family.casefold() in {
                name.casefold() for name in generator_families
            } else ())
            assignment = JudgeAssignment(
                job_id=job_id, comparison_id=comparison, criterion=criterion,
                judge_family=family, left_source=left.job_id, right_source=right.job_id,
                a_source=sources[a_index], b_source=sources[b_index], warnings=warnings,
            )
            rubric = (
                "Assess only the declared criterion using the complete user context. "
                "Do not infer identity from writing style or reward length alone. "
                "Return A, B, tie, or abstain, with criterion-specific evidence. "
                "Abstain when the available context does not support a judgment."
            )
            payload = {
                "criterion": criterion, "user_transcript": context,
                "A": answers[a_index], "B": answers[b_index],
            }
            result.append(PairwiseJudgeJob(
                job_id=job_id, comparison_id=comparison, criterion=criterion,
                user_transcript=context, candidate_a=answers[a_index], candidate_b=answers[b_index],
                rubric=rubric, prompt=rubric + "\n" + json.dumps(payload, ensure_ascii=False),
                private_assignment=assignment,
            ))
    rng.shuffle(result)
    return result


def _pairwise_observation(score: PairwiseJudgment | ScoreRecord) -> PairwiseJudgment:
    if isinstance(score, ScoreRecord):
        return PairwiseJudgment.model_validate({
            "job_id": score.job_id, "criterion": score.metrics.get("criterion"),
            "winner": score.metrics.get("winner"), "evidence": score.evidence,
        })
    return PairwiseJudgment.model_validate(score)


def aggregate_pairwise(
    scores: Sequence[PairwiseJudgment | ScoreRecord], assignments: Sequence[JudgeAssignment],
) -> PairwiseResult:
    """Keep every order judgment and refuse incomplete or uncorrelated pairs."""
    keys = {assignment.job_id: JudgeAssignment.model_validate(assignment) for assignment in assignments}
    if len(keys) != len(assignments):
        raise ValueError("duplicate private assignment")
    observations = [_pairwise_observation(score) for score in scores]
    observed = {score.job_id: score for score in observations}
    if len(observed) != len(observations):
        raise ValueError("duplicate judge observation")
    if not set(observed) <= set(keys):
        raise ValueError("unknown judge job")
    if set(observed) != set(keys) or not keys:
        raise ValueError("incomplete judge pair")
    groups: dict[tuple[str, str], list[JudgeAssignment]] = defaultdict(list)
    for assignment in keys.values():
        if observed[assignment.job_id].criterion != assignment.criterion:
            raise ValueError("judge criterion mismatch")
        groups[(assignment.comparison_id, assignment.judge_family)].append(assignment)
    wins = ties = losses = abstentions = inconsistent = 0
    family_outcomes: dict[str, dict[str, str]] = defaultdict(dict)
    for (comparison, family), pair in groups.items():
        if len(pair) != 2 or len({assignment.a_source for assignment in pair}) != 2:
            raise ValueError("incomplete order-swapped judge pair")
        if len({(assignment.left_source, assignment.right_source, assignment.criterion)
                for assignment in pair}) != 1:
            raise ValueError("inconsistent private judge mapping")
        decisions: list[str] = []
        for assignment in pair:
            winner = observed[assignment.job_id].winner
            if winner in ("tie", "abstain"):
                decisions.append(winner)
            else:
                source = assignment.a_source if winner == "A" else assignment.b_source
                decisions.append("win" if source == assignment.left_source else "loss")
        if "abstain" in decisions:
            abstentions += 1
            family_outcomes[comparison][family] = "abstain"
        elif decisions[0] != decisions[1]:
            inconsistent += 1
            family_outcomes[comparison][family] = "order-inconsistent"
        else:
            outcome = decisions[0]
            family_outcomes[comparison][family] = outcome
            wins += outcome == "win"
            ties += outcome == "tie"
            losses += outcome == "loss"
    informative = len(groups) - abstentions
    disagreement = any(len({outcome for outcome in outcomes.values()
                            if outcome not in {"abstain", "order-inconsistent"}}) > 1
                       for outcomes in family_outcomes.values())
    return PairwiseResult(
        wins=wins, ties=ties, losses=losses, abstentions=abstentions,
        inconsistent_orders=inconsistent, complete_judge_pairs=len(groups),
        order_consistency=(informative - inconsistent) / informative if informative else None,
        judge_family_disagreement=disagreement, family_outcomes=dict(family_outcomes),
        warnings=tuple(sorted({warning for assignment in assignments for warning in assignment.warnings})),
        evidence=tuple(observations),
    )


class QualityAssignment(_JudgeModel):
    job_id: str
    mechanism_id: str
    criterion: QualityCriterion


class MechanismQualityJob(_JudgeModel):
    job_id: str
    criterion: QualityCriterion
    user_transcript: tuple[str, ...]
    final_portfolio: str
    mechanism: dict[str, str]
    rubric: str
    prompt: str
    private_assignment: QualityAssignment = Field(exclude=True, repr=False)


class MechanismQualityJudgment(_JudgeModel):
    job_id: str
    criterion: QualityCriterion
    rating: int | bool | None
    abstained: bool = False
    abstention_reason: str | None = None
    evidence: str = Field(min_length=1)
    evidence_span: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_observation(self) -> Self:
        if not self.evidence.strip() or not self.evidence_span.strip():
            raise ValueError("criterion evidence and observed span are required")
        if self.abstained:
            if self.rating is not None or not (self.abstention_reason or "").strip():
                raise ValueError("abstention requires a reason and no invented rating")
            return self
        if self.abstention_reason is not None:
            raise ValueError("abstention reason requires explicit abstention")
        if self.criterion == "critical_safety_violation":
            if type(self.rating) is not bool:
                raise ValueError("critical safety rating must be boolean")
        elif type(self.rating) is not int or not 0 <= self.rating <= 3:
            raise ValueError("anchored quality rating must be an integer from zero to three")
        return self


def build_mechanism_quality_jobs(
    mechanisms: Sequence[Mechanism],
    *,
    final_portfolio: str,
    user_transcript: Sequence[str],
    seed: int,
    identity_labels: Sequence[str] = (),
) -> list[MechanismQualityJob]:
    """Create one blinded, anchored question per mechanism and quality criterion."""
    if len({mechanism.id for mechanism in mechanisms}) != len(mechanisms):
        raise ValueError("duplicate mechanism identifier")
    labels = (*identity_labels, *(mechanism.id for mechanism in mechanisms))
    context = _user_context(user_transcript, labels)
    final = _clean(final_portfolio, labels)
    result = []
    for index, mechanism in enumerate(mechanisms):
        structure = {
            key: _clean(str(value), labels) for key, value in mechanism.model_dump().items()
            if key not in {"id", "quality", "evidence"}
        }
        for criterion, rubric in QUALITY_RUBRICS.items():
            job_id = _opaque("quality", seed, context, final, structure, index, criterion)
            payload = {
                "criterion": criterion, "user_transcript": context, "final_portfolio": final,
                "candidate": structure,
            }
            prompt = (
                "Rate only this criterion. Return the anchored rating, criterion-specific "
                "evidence, and an exact evidence_span from the final portfolio. "
                "Use the full user context; the candidate is an extraction of the final answer. "
                "If judgment is unsupported, return abstained=true, rating=null and an "
                "abstention_reason rather than inventing a rating.\n"
                + rubric + "\n" + json.dumps(payload, ensure_ascii=False)
            )
            result.append(MechanismQualityJob(
                job_id=job_id, criterion=criterion, user_transcript=context,
                final_portfolio=final, mechanism=structure, rubric=rubric, prompt=prompt,
                private_assignment=QualityAssignment(
                    job_id=job_id, mechanism_id=mechanism.id, criterion=criterion,
                ),
            ))
    random.Random(seed).shuffle(result)
    return result


def validate_quality_judgment(
    job: MechanismQualityJob, payload: MechanismQualityJudgment | Mapping[str, object],
) -> MechanismQualityJudgment:
    observation = MechanismQualityJudgment.model_validate(payload)
    if observation.job_id != job.job_id or observation.criterion != job.criterion:
        raise ValueError("quality judgment correlation mismatch")
    if observation.evidence_span not in job.final_portfolio:
        raise ValueError("quality judgment evidence span is not observed")
    return observation


def assemble_mechanism_quality(
    judgments: Sequence[MechanismQualityJudgment], jobs: Sequence[MechanismQualityJob],
) -> dict[str, MechanismQuality]:
    """Accept quality only after all five criterion observations have real spans."""
    keys = {job.job_id: job for job in jobs}
    scores = {score.job_id: score for score in judgments}
    if len(keys) != len(jobs) or len(scores) != len(judgments):
        raise ValueError("duplicate quality observation or job")
    if not set(scores) <= set(keys):
        raise ValueError("unknown quality judgment")
    if set(scores) != set(keys):
        raise ValueError("incomplete mechanism quality")
    by_mechanism: dict[str, dict[str, MechanismQualityJudgment]] = defaultdict(dict)
    for job_id, job in keys.items():
        score = validate_quality_judgment(job, scores[job_id])
        if score.abstained:
            raise ValueError("mechanism quality contains abstention; retain as missing")
        group = by_mechanism[job.private_assignment.mechanism_id]
        if score.criterion in group:
            raise ValueError("duplicate mechanism quality criterion")
        group[score.criterion] = score
    result = {}
    for mechanism_id, criteria in by_mechanism.items():
        if set(criteria) != set(QUALITY_RUBRICS):
            raise ValueError("incomplete mechanism quality")
        result[mechanism_id] = MechanismQuality.model_validate({
            **{criterion: observation.rating for criterion, observation in criteria.items()},
            "evidence": {criterion: observation.evidence + " [span: " + observation.evidence_span + "]"
                         for criterion, observation in criteria.items()},
        })
    return result
