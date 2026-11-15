# Task 9 readiness tooling

This external inbox worker implements the approved [six-case plan](../../docs/superpowers/plans/2026-11-14-study-task9-six-case-feasibility.md). The owner approved **70 requests, US$5 maximum, no retries**, implementation and offline tests. [The decision record](../study/task9-readiness-approval.yaml) keeps live execution unauthorized and the scientific stage pending. The canonical skill remains frozen.

The provider-neutral package remains under `../src/`. This directory runs from the benchmark checkout with `uv run --locked python -m task9`; it is not included in the `sib` distribution. Use Python 3.11–3.14, uv 0.12.8 and the locked development environment. `uv sync --locked --group task9` installs the optional tokenizer dependency; root repository tools remain standard-library only.

## Offline verification

From `benchmark/`:

```bash
uv run --offline --locked pytest -q
uv run --offline --locked ruff check .
uv run --offline --locked mypy src task9
uv run --offline --locked python -m task9 --help
```

`tests/test_task9_integration.py` prepares the six actual public cases and five conditions, exchanges 70 synthetic request-bound replies, proves a fresh-process resume after the first Deep turn, checks cached replay without another attempt, generates standard reports in an isolated child, and emits only technical evidence. Every Task 9 test denies DNS and socket connections. Fake token counts, costs, IDs and answers are synthetic; they establish neither API compatibility nor scientific feasibility.

## Component boundaries

- `contracts.py` and `guards.py` validate exact scope, policy, source/corpus/skill/config/lock digests, approval expiry and independent transport identity. A process lock, exclusive claims and fsynced hash-chained receipts precede dispatch. Unknown outcomes stop the run; completed matching requests return retained evidence without sending again.
- `transport.py` makes one direct TLS request with a 120-second total deadline and a 1 MiB body limit. It reads the credential only inside the guarded send callback. It has no SDK retry, redirect or proxy path. Fake connections exercise it offline.
- `worker.py` sends the complete instructions and transcript with fixed model parameters, validates response identity, status and usage, retains redacted provider evidence, and calculates an upper-bound cost from total usage. Reasoning tokens are included in output usage once.
- `tokens.py` requires explicit local vocabulary bytes matching its pinned hash. It never downloads tokenizer resources. Its framing allowance is **unreviewed and cannot certify live dispatch**; local counts never replace provider usage.
- `verifier.py` checks 30 jobs / 70 turns, disclosure parity, all-turn accounting, receipts, resume prefixes and report provenance. It constructs 12 blinded protocol packets without rating them. Technical outputs exclude answers, candidates, condition effects, rankings and strata. Offline success never passes a scientific gate.

The worker reserves US$0.05 per request, uses integer microdollars, stops at US$4.50 including unresolved reservations, and also enforces the US$5 cap, 70-attempt ceiling, serial execution, zero retries, 32,768 input tokens, 4,096 output tokens and three-hour wall limit. The plan's conservative token-price bound is US$3.01056; these are declared limits, not measured charges.

## Explicit run-local operations

`python -m task9 COMMAND --help` documents each command:

| Command | Purpose |
| --- | --- |
| `bindings` | Read actual immutable input digests; creates no approval. |
| `process` | Consume one exported opaque TurnJob and an independently supplied approval; offline mode requires an exact request-bound replay fixture. Write only a response exchange file, then use `sib ingest` for canonical evidence. |
| `checkpoint` | Retain the first accepted Deep turn and evidence prefixes. |
| `resume-proof` | Prove unchanged prefixes from a fresh process before continuing. |
| `verify` | Optionally generate isolated standard reports, then write technical JSON/Markdown and return the technical decision. |

Approvals, replay fixtures, response exchanges, receipts, checkpoints and reports belong inside ignored run storage, never public Git. The offline approval format is `ExecutionApproval`; tests show a complete example. An approval must match the actual run, sources, input profile and separately selected account/project. Editing inputs invalidates it.

## Live launch remains blocked

The proposed config retains `dry_run: true`. Preregistration remains draft, `stage-gates.yaml` retains `execution_authorized: false`, Task 9 remains pending, and the readiness record has no live authorization. Live mode refuses before reading run inputs or credentials; guards independently enforce the pause. The production counter also refuses live certification.

A later launch needs separate owner authorization, reviewed provider-framing evidence, an immutable clean reviewed checkout, exact account/project and enforcing budget controls, refreshed price/model access evidence, and the independent filesystem/egress controls in the plan. Local hashes detect corruption, not an adversary able to rewrite the entire evidence directory. This implementation does not install those operating-system controls or authorize private packs, human labeling, judge calls, study advancement, merge or push.
