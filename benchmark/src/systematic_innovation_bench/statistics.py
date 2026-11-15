"""Paired case-level estimation. Replicates never become independent cases."""
from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence
from statistics import NormalDist, mean
from typing import Literal

import numpy as np
from pydantic import Field

from .models import StrictModel

PRIMARY_ENDPOINT = 'qualified_useful_distinct_mechanisms_per_1000_total_assistant_output_tokens'


class AnalysisRecord(StrictModel):
    case_id: str
    condition: str
    qualified: int = Field(ge=0)
    raw_distinct: int = Field(ge=0)
    total_assistant_output_tokens: int | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    latency_seconds: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    status: str = 'succeeded'
    measured: bool = True
    model: str = ''
    host: str = ''
    interaction_mode: str = 'single-turn'
    family: str = ''


class CaseEffect(StrictModel):
    case_id: str
    treatment: float | None
    control: float | None
    difference: float | None
    treatment_replicates: int
    control_replicates: int
    treatment_raw: float | None
    control_raw: float | None
    missing: int = 0
    paired_configurations: int = 0
    missing_configurations: int = 0


class ConfidenceInterval(StrictModel):
    estimate: float
    median: float
    lower: float
    upper: float
    n_cases: int
    missing_cases: int
    method: str
    repetitions: int
    seed: int
    statistic: str
    confidence: float
    degenerate: bool = False
    degeneracy_reason: str | None = None


class WinTieLoss(StrictModel):
    wins: int
    ties: int
    losses: int
    missing: int


def efficiency(qualified: int, total_assistant_output_tokens: int | None) -> float:
    if total_assistant_output_tokens is None or total_assistant_output_tokens <= 0:
        raise ValueError('complete positive total assistant token accounting required')
    return 1000 * qualified / total_assistant_output_tokens


def _metric(row: AnalysisRecord, metric: str) -> float | None:
    if not row.measured:
        return None
    numerator = row.qualified if row.status == 'succeeded' else 0
    if metric == PRIMARY_ENDPOINT:
        if not row.total_assistant_output_tokens:
            return None
        return efficiency(numerator, row.total_assistant_output_tokens)
    if metric == 'qualified':
        return float(numerator)
    if metric == 'raw_distinct':
        return float(row.raw_distinct if row.status == 'succeeded' else 0)
    if metric == 'qualified_per_dollar':
        return numerator / row.cost if row.cost else None
    if metric == 'qualified_per_minute':
        return numerator * 60 / row.latency_seconds if row.latency_seconds else None
    raise ValueError('unknown analysis metric')


def paired_case_effects(records: Sequence[AnalysisRecord], treatment: str, control: str,
                        metric: str = PRIMARY_ENDPOINT) -> list[CaseEffect]:
    if treatment == control:
        raise ValueError('contrast requires different conditions')
    grouped: dict[str, dict[str, dict[tuple[str, str], list[AnalysisRecord]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list)))
    for row in records:
        if row.condition in (treatment, control):
            grouped[row.case_id][row.condition][(row.model, row.host)].append(row)
    effects = []
    for case_id, arms in sorted(grouped.items()):
        t_configs, c_configs = arms[treatment], arms[control]
        configurations = sorted(set(t_configs) | set(c_configs))
        t_means, c_means, t_raw, c_raw = [], [], [], []
        missing = missing_configurations = paired_configurations = 0
        for configuration in configurations:
            trows, crows = t_configs.get(configuration, []), c_configs.get(configuration, [])
            tv, cv = [_metric(row, metric) for row in trows], [_metric(row, metric) for row in crows]
            missing += sum(value is None for value in tv + cv) + int(not tv) + int(not cv)
            if trows:
                t_raw.append(mean(row.raw_distinct if row.status == 'succeeded' else 0 for row in trows))
            if crows:
                c_raw.append(mean(row.raw_distinct if row.status == 'succeeded' else 0 for row in crows))
            if not tv or not cv or any(value is None for value in tv + cv):
                missing_configurations += 1
                continue
            paired_configurations += 1
            t_means.append(mean(value for value in tv if value is not None))
            c_means.append(mean(value for value in cv if value is not None))
        # Give each paired model/host cell equal weight within the case, after
        # averaging its stochastic repetitions. An incomplete cell makes the case
        # incomplete rather than substituting a different generating configuration.
        tmean = mean(t_means) if not missing_configurations and t_means else None
        cmean = mean(c_means) if not missing_configurations and c_means else None
        effects.append(CaseEffect(
            case_id=case_id, treatment=tmean, control=cmean,
            difference=tmean-cmean if tmean is not None and cmean is not None else None,
            treatment_replicates=sum(len(rows) for rows in t_configs.values()),
            control_replicates=sum(len(rows) for rows in c_configs.values()), missing=missing,
            treatment_raw=mean(t_raw) if t_raw else None, control_raw=mean(c_raw) if c_raw else None,
            paired_configurations=paired_configurations, missing_configurations=missing_configurations,
        ))
    return effects


def bootstrap_case_ci(effects: Sequence[CaseEffect], repetitions: int, seed: int,
                      method: Literal['percentile', 'bca'] = 'percentile', confidence: float = 0.95,
                      statistic: Literal['mean', 'median'] = 'mean') -> ConfidenceInterval:
    if repetitions < 1 or not 0 < confidence < 1 or method not in ('percentile', 'bca') or statistic not in ('mean', 'median'):
        raise ValueError('invalid bootstrap configuration')
    values = np.array([e.difference for e in effects if e.difference is not None], dtype=float)
    n = len(values)
    if not n or not np.all(np.isfinite(values)):
        raise ValueError('no finite complete paired cases')
    estimator = np.mean if statistic == 'mean' else np.median
    estimate = float(estimator(values))
    rng = np.random.default_rng(seed)
    # Bounded batches rather than repetitions*n unbounded memory.
    draws = np.concatenate([estimator(values[rng.integers(0, n, size=(min(1000, repetitions-i), n))], axis=1)
                            for i in range(0, repetitions, 1000)])
    alpha = (1-confidence)/2
    quantiles = [alpha, 1-alpha]
    if method == 'bca' and n > 1 and float(np.ptp(values)) > 0:
        normal = NormalDist()
        proportion = (float(np.sum(draws < estimate)) + 0.5*float(np.sum(draws == estimate))) / repetitions
        z0 = normal.inv_cdf(min(1-0.5/repetitions, max(0.5/repetitions, proportion)))
        jack = np.array([estimator(np.delete(values, i)) for i in range(n)])
        centered = np.mean(jack)-jack
        denom = 6*float(np.sum(centered**2))**1.5
        acceleration = float(np.sum(centered**3))/denom if denom else 0.0
        adjusted = []
        for q in quantiles:
            z = normal.inv_cdf(q)
            divisor = 1-acceleration*(z0+z)
            adjusted.append(normal.cdf(z0+(z0+z)/divisor) if divisor else q)
        quantiles = sorted(adjusted)
    lower, upper = np.quantile(draws, quantiles)
    degeneracy_reason = ('fewer-than-two-complete-cases' if n < 2 else
                         'constant-case-effects' if float(np.ptp(values)) == 0 else None)
    return ConfidenceInterval(estimate=estimate, median=float(np.median(values)), lower=float(lower),
                              upper=float(upper), n_cases=n, missing_cases=len(effects)-n, method=method,
                              repetitions=repetitions, seed=seed, statistic=statistic, confidence=confidence,
                              degenerate=degeneracy_reason is not None, degeneracy_reason=degeneracy_reason)


def win_tie_loss(effects: Sequence[CaseEffect], equivalence_margin: float) -> WinTieLoss:
    if not math.isfinite(equivalence_margin) or equivalence_margin < 0:
        raise ValueError('invalid equivalence margin')
    differences = [e.difference for e in effects if e.difference is not None]
    return WinTieLoss(wins=sum(d > equivalence_margin for d in differences),
                     losses=sum(d < -equivalence_margin for d in differences),
                     ties=sum(abs(d) <= equivalence_margin for d in differences),
                     missing=len(effects)-len(differences))


def holm_adjust(pvalues: Sequence[float]) -> list[float]:
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in pvalues):
        raise ValueError('invalid p-value')
    ordered = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, previous = [0.0]*len(pvalues), 0.0
    for rank, i in enumerate(ordered):
        previous = max(previous, min(1.0, (len(pvalues)-rank)*pvalues[i]))
        adjusted[i] = previous
    return adjusted
