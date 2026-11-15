# Compatibility Evidence Contract

This directory defines the schema and claim-profile contracts for evaluating host compatibility of [`skills/systematic-innovation/`](../skills/systematic-innovation/SKILL.md) under [`docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md`](../docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md) (§9).

## Six Independent Dimensions

Compatibility is evaluated across six independent dimensions rather than a single badge or linear ladder:

1. `format_conformance`: `passed`, `failed`, `not-assessed`
2. `installation`: `passed`, `failed`, `not-supported`, `not-assessed`
3. `discovery`: `passed`, `failed`, `not-supported`, `not-assessed`
4. `explicit_activation`: `passed`, `failed`, `not-supported`, `not-assessed`
5. `automatic_activation`: `passed`, `failed`, `not-supported`, `not-claimed`, `not-assessed`
6. `behavioral_conformance`: `passed`, `failed`, `not-assessed`

Passing one dimension never implies that another dimension passed. Evidence whose `review_after` date has elapsed (`as_of > review_after`) or that is marked with an unassessed material change is evaluated as `stale` and cannot satisfy a `"passed"` requirement in any claim profile.

## Validation Command

```bash
python3 -m tools.repository verify-compatibility benchmark/study/integration-matrix.yaml --profile broad-cross-agent
```
