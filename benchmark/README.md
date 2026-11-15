# Provider-neutral benchmark laboratory

This isolated Python package measures **systematic ideation performance**. It does not establish realized innovation or global novelty. The canonical skill remains in `../skills/systematic-innovation/`; full-treatment planning reads the complete pack at runtime. The root repository tools remain standard-library Python.

Use CPython 3.13 for development (3.11–3.14 supported) and uv **0.12.8**:

```bash
cd benchmark
uv sync --locked
uv run --locked sib --help
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked mypy src task9
```

`src/` owns strict versioned records, loaders, planning, immutable conversation state, append-only storage, adapters, scoring, statistics, reports, and CLI orchestration. `schemas/` supports external producers. `cases/development/` contains the 60 public cases; `study/` contains draft scientific contracts. `runs/` is ignored generated evidence. No provider SDK is required. Provider integrations belong outside this core unless independently reviewed.

## Complete offline example

From the `benchmark` directory, these commands use only the bundled fake subprocess fixture and the six public feasibility case IDs. The fake's tokens/cost are synthetic protocol metadata, not measurements of a model. This does not execute or pass the scientific feasibility study.

```bash
uv run --locked sib validate --config configs/fake.yaml
uv run --locked sib plan --config configs/fake.yaml --cases cases/development --case-ids syn-dev-001,red-dev-001,sys-dev-001,pre-dev-001,tri-dev-001,adv-dev-001 --run-dir runs/offline-example --dry-run
uv run --locked sib run --config configs/fake.yaml --cases cases/development --case-ids syn-dev-001,red-dev-001,sys-dev-001,pre-dev-001,tri-dev-001,adv-dev-001 --run-dir runs/offline-example
uv run --locked sib resume --run-dir runs/offline-example
uv run --locked sib score --run-dir runs/offline-example
uv run --locked sib report --run-dir runs/offline-example
uv run --locked sib verify-run --run-dir runs/offline-example
uv run --locked sib compare --baseline runs/offline-example --candidate runs/offline-example
```

Use a fresh run ID and fresh results directory for another execution. Evidence cannot be overwritten. `--dry-run` on mutating commands validates and describes work without writing or invoking an adapter; `dry_run: true` in configuration also prevents plan/run mutation.

## Turn-level inbox exchange

For an inbox host, first `plan` with explicit `--config`, `--cases`, and `--run-dir`. Export a batch with `sib export --run-dir RUN --output RUN/outbox-1.jsonl`. Give only that file to the external generator. Each `TurnJob` contains an opaque job ID, next assistant index, immutable transcript ending in a user disclosure, model parameters, and condition-rendered instructions. Do not give the generator the manifest, scoring criteria, source identity mappings, hidden labels, another condition's output, or judge annotations.

Return one `TurnResponse` JSON object per line, with the same `job_id`, requested `turn_index`, and `attempt`; include exactly one assistant answer, observed token counts, cost, latency, and status. Preserve unknown metadata as null. Run `sib ingest --run-dir RUN --input RETURNED_JSONL`, then export the next pending batch to a fresh output file. Execute no more than the configured outstanding concurrency. Deduplicate external processing by opaque turn ID; do not execute a previously processed turn twice. Successful assistant turns are never regenerated.

Deep cases disclose exactly the fixed user turns in order regardless of assistant questions. Every condition receives byte-identical disclosures. The final portfolio alone supplies mechanisms; **all** assistant output, including earlier questions and failed attempts, supplies efficiency tokens/cost/latency. Resume reconstructs from accepted turn records. A dispatch interrupted before its response is known remains unresolved until the operator supplies correlated evidence; automatic duplicate spending is refused.

## Security and measurements

Subprocess adapters require an exact executable allowlist, argument arrays without a shell, filtered environments, timeouts, bounded output capture, and configured per-turn cost ceilings. They do not create an OS filesystem or network sandbox. Run untrusted executables within an independently configured platform sandbox. Configurations contain environment **names**, never credential values. Known values and common credential forms are redacted before canonical persistence; diagnostic errors contain rule codes, never matched payloads.

Writes stay inside the configured results directory, with repository-local results limited to `benchmark/runs/`. Evidence uses process locks and durable append-only JSONL. Manifests identify executable source and dirty-worktree status; mutation refuses changed runner source. Integrity snapshots verify input provenance and evidence digests; valid durable log tails can be recovered after interruption. These local hashes detect accidental corruption, not a malicious actor able to rewrite the complete run directory.

`score` extracts explicit structured or compact candidates without trusting model-supplied quality ratings. Generic prose requires a separate reviewed structured extraction. Supply criterion judgments through `score --judgments SCORE_JSONL` in a fresh scoring run; every quality criterion needs evidence. Gate candidates conjunctively before causal deduplication: relevance ≥2/3, constraint alignment ≥2/3, causal clarity ≥2/3, plausibility ≥1/3, no critical safety/rights violation. Judge failures/abstentions leave the primary measurement missing, with sensitivity bounds; unrated candidates never become observed failures. Lexical structural equivalence is a disclosed fallback; reviewed semantic equivalence requires retained evidence. Recovery uses optimal one-to-one Hungarian assignment; Vendi uses a positive semidefinite structural similarity kernel.

Reports expose raw candidates/families, qualified candidates/families, overlapping rejection counts, final and total tokens, missingness, cost, latency, failures, and strata. The primary contrast is full skill minus format-matched control; repetitions average within matched case/model/host cells before case bootstrap. Percentile/BCa intervals and Holm secondary adjustment are available. Unmeasured semantic endpoints are explicitly not assessed. Uncalibrated automated ratings never support headline claims.

Restricted-pack validation is content-free and refuses in-repository packs. `sib restricted-preflight --declaration DECLARATION --output AUTHORIZATION` checks a frozen reviewed external execution declaration and records authorization only; it launches no adapter. Public run commands are development-only. Read [restricted custody](../docs/security/restricted-execution.md) before any private-pack access. Live model studies, human calibration, validation, sealed access, cross-agent results, and publication remain pending.

Follow [HANDOFF.md](HANDOFF.md) for operations and [runner-verification.md](runner-verification.md) for retained offline evidence.

The approved Task 9 budget is 70 requests / US$5 / no retries. Its external API worker, spending/approval guards and technical verifier are in [task9/](task9/README.md), with synthetic offline integration tests. Live execution remains paused and the canonical skill remains frozen; see the [readiness decision](study/task9-readiness-approval.yaml).
