"""Quality gating, structural equivalence, diversity, and optimal recovery.

The built-in equivalence is a disclosed lexical aid, not a semantic judge.
Reviewed semantic equivalents can be supplied as explicit candidate-ID pairs.
"""
from __future__ import annotations

import json
import math
import re
from collections.abc import Sequence

import numpy as np

from ..models import Mechanism, MechanismQuality

_ALIASES = {
    'tasks': 'job', 'jobs': 'job', 'requests': 'demand', 'request': 'demand',
    'pooling': 'pool', 'pooled': 'pool', 'combine': 'pool', 'combined': 'pool',
    'reduce': 'cut', 'reducing': 'cut', 'waiting': 'delay', 'wait': 'delay',
    'payments': 'payment', 'queues': 'queue', 'delays': 'delay',
}
_STOP = frozenset({'a', 'an', 'the', 'to', 'of', 'and', 'by', 'for', 'in', 'with'})


def _tokens(text: str) -> frozenset[str]:
    return frozenset(_ALIASES.get(w, w) for w in re.findall(r'[a-z0-9]+', text.lower()) if w not in _STOP)


def _normalize(text: str) -> str:
    return ' '.join(sorted(_tokens(text)))


def mechanism_signature(mechanism: Mechanism) -> tuple[str, ...]:
    # Actor substitution alone does not create a causal family.
    return tuple(_normalize(v) for v in (mechanism.intervention_point, mechanism.changed_flow,
                                         mechanism.causal_operation, mechanism.intended_effect))


def passes_quality_gate(quality: MechanismQuality) -> bool:
    return (quality.relevance >= 2 and quality.constraint_alignment >= 2
            and quality.causal_clarity >= 2 and quality.plausibility >= 1
            and not quality.critical_safety_violation)


def gate_failures(quality: MechanismQuality | None) -> list[str]:
    if quality is None:
        return ['unrated']
    failures = [name for name, threshold in [('relevance', 2), ('constraint_alignment', 2),
                                            ('causal_clarity', 2), ('plausibility', 1)]
                if getattr(quality, name) < threshold]
    if quality.critical_safety_violation:
        failures.append('critical_safety_violation')
    return failures


def _jaccard(a: str, b: str) -> float:
    x, y = _tokens(a), _tokens(b)
    return len(x & y) / len(x | y) if x | y else 0.0


def equivalent(a: Mechanism, b: Mechanism) -> bool:
    left, right = mechanism_signature(a), mechanism_signature(b)
    if left == right and all(left):
        return True
    # Require agreement in each structural dimension; pooled words across different
    # flows must not collapse distinct causal structures.
    return all(_jaccard(x, y) >= 0.6 for x, y in zip(left, right, strict=True))


def cluster_mechanisms(mechanisms: Sequence[Mechanism],
                       semantic_equivalences: Sequence[tuple[str, str]] = ()) -> list[list[Mechanism]]:
    ids = {m.id for m in mechanisms}
    if len(ids) != len(mechanisms):
        raise ValueError('duplicate mechanism identifiers')
    approved = {frozenset(pair) for pair in semantic_equivalences}
    if any(not pair <= ids for pair in approved):
        raise ValueError('unknown equivalence identifier')
    clusters: list[list[Mechanism]] = []
    for item in mechanisms:
        for cluster in clusters:
            # Complete-link avoids a chain of weak paraphrases joining unrelated ends.
            if all(equivalent(item, old) or frozenset((item.id, old.id)) in approved for old in cluster):
                cluster.append(item)
                break
        else:
            clusters.append([item])
    return clusters


def validate_semantic_equivalences(
    mechanisms: Sequence[Mechanism], evidence_records: object,
) -> tuple[tuple[str, str], ...]:
    """Validate retained human/judge equivalence decisions before using them.

    ``ScoreRecord.metrics["semantic_equivalences"]`` contains a list of records
    with exactly ``left``, ``right`` and nonempty criterion-specific ``evidence``.
    These are separate measurement-role observations, never generator ratings.
    """
    if not isinstance(evidence_records, list):
        raise ValueError('semantic equivalence evidence must be a list')  # noqa: TRY004 - score validation boundary
    ids = {mechanism.id for mechanism in mechanisms}
    result = []
    seen: set[frozenset[str]] = set()
    for record in evidence_records:
        if not isinstance(record, dict) or set(record) != {'left', 'right', 'evidence'}:
            raise ValueError('invalid semantic equivalence evidence record')
        left, right, evidence = record['left'], record['right'], record['evidence']
        if (not isinstance(left, str) or not isinstance(right, str)
                or left == right or left not in ids or right not in ids
                or not isinstance(evidence, str) or not evidence.strip()):
            raise ValueError('semantic equivalence requires known distinct ids and evidence')
        pair = frozenset((left, right))
        if pair in seen:
            raise ValueError('duplicate semantic equivalence evidence')
        seen.add(pair)
        result.append((left, right))
    return tuple(result)


def distinct_mechanism_count(
    mechanisms: Sequence[Mechanism], semantic_equivalences: Sequence[tuple[str, str]] = (),
) -> int:
    return len(cluster_mechanisms(mechanisms, semantic_equivalences))


def qualified_distinct_mechanism_count(
    mechanisms: Sequence[Mechanism], semantic_equivalences: Sequence[tuple[str, str]] = (),
) -> int:
    ids = {mechanism.id for mechanism in mechanisms}
    if any(len(set(pair)) != 2 or not set(pair) <= ids for pair in semantic_equivalences):
        raise ValueError('invalid semantic equivalence identifier')
    qualified = [m for m in mechanisms if m.quality and passes_quality_gate(m.quality)]
    surviving = {mechanism.id for mechanism in qualified}
    pairs = [pair for pair in semantic_equivalences if set(pair) <= surviving]
    return distinct_mechanism_count(qualified, pairs)


def vendi_score(mechanisms: Sequence[Mechanism]) -> float:
    if not mechanisms:
        return 0.0
    # Cosine Gram kernel is positive semidefinite by construction. Dimension prefixes
    # prevent identical words used as different structural roles becoming equivalent.
    bags = [{f'{i}:{w}' for i, part in enumerate(mechanism_signature(m)) for w in part.split()}
            for m in mechanisms]
    vocabulary = sorted(set().union(*bags))
    if not vocabulary or any(not bag for bag in bags):
        raise ValueError('mechanism has no structural features')
    vectors = np.array([[float(word in bag) for word in vocabulary] for bag in bags])
    vectors /= np.linalg.norm(vectors, axis=1)[:, None]
    eigenvalues = np.linalg.eigvalsh(vectors @ vectors.T / len(mechanisms))
    eigenvalues = eigenvalues[eigenvalues > 1e-12]
    return float(np.exp(-np.sum(eigenvalues * np.log(eigenvalues))))


def hungarian_maximum_weight(weights: Sequence[Sequence[float]]) -> list[tuple[int, int]]:
    """O(n^3) rectangular maximum-weight assignment, including dummy padding."""
    if not weights:
        return []
    rows, columns = len(weights), len(weights[0])
    if any(len(row) != columns for row in weights):
        raise ValueError('ragged matching matrix')
    if columns == 0:
        return []
    if any(not math.isfinite(v) for row in weights for v in row):
        raise ValueError('nonfinite matching weight')
    size = max(rows, columns)
    maximum = max(0.0, max(max(row) for row in weights))
    costs = [[maximum - (weights[i][j] if i < rows and j < columns else 0)
              for j in range(size)] for i in range(size)]
    u, v, p, way = [0.0] * (size + 1), [0.0] * (size + 1), [0] * (size + 1), [0] * (size + 1)
    for i in range(1, size + 1):
        p[0], j0 = i, 0
        minimum, used = [math.inf] * (size + 1), [False] * (size + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], math.inf, 0
            for j in range(1, size + 1):
                if not used[j]:
                    current = costs[i0 - 1][j - 1] - u[i0] - v[j]
                    if current < minimum[j]:
                        minimum[j], way[j] = current, j0
                    if minimum[j] < delta:
                        delta, j1 = minimum[j], j
            for j in range(size + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minimum[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            p[j0] = p[way[j0]]
            j0 = way[j0]
    return sorted((p[j] - 1, j - 1) for j in range(1, size + 1)
                  if p[j] <= rows and j <= columns)


def bipartite_mechanism_recovery(candidates: Sequence[Mechanism], gold_mechanisms: Sequence[str],
                                 threshold: float = 0.5) -> dict[str, float | int]:
    if not 0 <= threshold <= 1:
        raise ValueError('invalid matching threshold')
    weights = [[max(_jaccard(m.causal_operation, gold),
                    _jaccard(' '.join(mechanism_signature(m)), gold)) for gold in gold_mechanisms]
               for m in candidates]
    # Below-threshold edges have zero weight so they cannot displace admissible matches.
    admissible = [[w if w >= threshold else 0.0 for w in row] for row in weights]
    pairs = hungarian_maximum_weight(admissible)
    matches = [(i, j) for i, j in pairs if weights[i][j] >= threshold and weights[i][j] > 0]
    return {'matched': len(matches), 'candidates': len(candidates), 'gold': len(gold_mechanisms),
            'precision': len(matches) / len(candidates) if candidates else 0.0,
            'recall': len(matches) / len(gold_mechanisms) if gold_mechanisms else 0.0,
            'matched_weight': sum(weights[i][j] for i, j in matches)}


def extract_mechanisms(final_response: str) -> list[Mechanism]:
    """Ingest explicit structured extractions or compact candidates, without inventing ratings."""
    try:
        payload = json.loads(final_response)
    except (ValueError, TypeError):
        payload = None
    if isinstance(payload, dict) and isinstance(payload.get('mechanisms'), list):
        return [Mechanism.model_validate(item | {'quality': None, 'evidence': {}})
                for item in payload['mechanisms']]
    result = []
    for line in final_response.splitlines():
        match = re.match(r'^\s*P(\d+):\s*(.+)', line)
        if not match:
            continue
        fields = {key.strip().lower(): value.strip()
                  for part in match[2].split('|')[1:] if ':' in part
                  for key, value in [part.split(':', 1)]}
        chain = fields.get('chain', '')
        if not fields.get('intervention') or not fields.get('lever') or not chain:
            continue
        result.append(Mechanism(id=f'P{match[1]}', intervention_point=fields['intervention'],
                                actor=fields.get('actor', 'unspecified'), changed_flow=chain.split('->')[0].strip(),
                                causal_operation=fields['lever'], intended_effect=chain.split('->')[-1].strip(),
                                principal_constraint=fields.get('preserve', '')))
    return result
