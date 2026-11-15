# Task 9 offline implementation verification

Date: 2026-11-14, America/Vancouver. Baseline: `afe1a36507f0fe6be3f9db1c3a763eaface19d25`; local branch: `codex/study-task9-plan`. Scope: the approved [70-call / US$5 / no-retry plan](../docs/superpowers/plans/2026-11-14-study-task9-six-case-feasibility.md), external readiness tooling and offline tests only.

## Test-first evidence

The baseline passed 180 root standard-library tests and 236 benchmark tests. New component tests first failed for missing guard/worker/transport/tokenizer/verifier modules. Subsequent regression tests demonstrated failures before repair for budget-decision binding, inconsistent core/worker receipts, mutable transport identity, provider metadata, raw-response redaction, request provenance, unsafe source paths and unsanitized child-process errors. The complete synthetic rehearsal also exposed and fixed a Unicode request-digest mismatch.

A separate whole-change review reproduced three integration defects: repeated redaction broke raw JSON during ingest; worker output could bypass canonical ingestion; arbitrary report files lacked trusted generation provenance. Each received a focused failing regression before correction. Re-review then reproduced a duplicate-key credential leak in the generic raw-JSON correction; strict duplicate-key parsing with lexical fallback closed it after a failing regression. CLI verification also exposes its technical decision and returns failure when checks fail.

## Offline scope

The full integration uses the six actual public development cases, all five conditions, four Deep / two Quick cases, 30 parent jobs and 70 assistant turns. Replies, usage and costs are synthetic request-bound fixtures. It proves first-Deep-turn checkpointing, resume in a fresh process, immutable accepted prefixes, cached replay with no second attempt, worker-to-ingest redaction, isolated standard-report generation and technical-only output. It does not rate answers or fabricate calibration judgments.

Task 9 tests block DNS/socket connections and fail if attempted. HTTP transport tests use fake connections. Isolated report generation strips inherited credentials, blocks sockets and suppresses output; the parent verifies provenance and hashes without opening effect-bearing report content. Fixtures, approvals and runtime evidence stay in temporary/ignored directories.

The declared budget uses integer microdollars, US$0.05 reservations, a US$4.50 stop threshold including uncertainty, a US$5 cap, at most 70 attempts, concurrency one and zero retries. Tests cover lock contention, exact replay, changed requests, unresolved outcomes, corruption, approval/source/corpus drift, call/cost/time/input/output bounds and strict provider usage. Local text counting is explicitly **uncertified for live framing**; unknown provider overhead cannot silently authorize a request.

## Reproduction and results

Use uv 0.12.8 and separate locked environments for Python 3.11, 3.13 and 3.14. Dependency installation is a setup step; all test commands below run offline without downloading tokenizer vocabulary or contacting a provider.

```bash
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
python3 -m tools.repository.authority
python3 -m tools.repository validate
python3 -m tools.repository acceptance --evidence evidence/architecture/acceptance.json --stage full
git diff --check
cd benchmark
uv lock --offline --check
uv run --offline --locked pytest -q
uv run --offline --locked ruff check .
uv run --offline --locked mypy src task9
```

Final results on frozen source:

- Root standard-library suite: **181 passed**.
- Benchmark: **418 passed on each of Python 3.11, 3.13 and 3.14**, including the complete 70-turn offline integration on each interpreter.
- Ruff: passed on all three interpreters. Mypy: **32 source files passed** on each.
- Offline lock check: **36 packages resolved**, lock unchanged.
- Skill validation, authority scan, tracked-public-tree validation and whitespace checks: passed. Full architecture acceptance: **AR-01 through AR-12 passed**, retaining implementation/protocol scope rather than empirical study claims.
- Independent scoped re-review: **52 targeted tests passed**, all three original findings, CLI failure signalling and the duplicate-key regression closed; no remaining actionable findings.
- Canonical skill, preregistration and stage-gate files have no diff from baseline. The proposed config remains dry-run; live authorization remains false.

The final matrix used separate locked environments and `--offline`; test runtimes were 171.82 seconds (3.11), 167.17 seconds (3.13) and 179.58 seconds (3.14). No tests were skipped. Generated rehearsal evidence remains temporary/ignored.

## Authorization and limits

The [readiness decision](study/task9-readiness-approval.yaml) approves implementation/offline testing and the fixed budget. It explicitly denies live authorization. The proposed config stays dry-run, preregistration stays draft, every scientific gate stays pending and the canonical skill is unchanged (`SKILL.md` SHA-256 `d5971f6e3e646916e2a287c5a8fde96a93b811ed071c362526c605ef222a890b`). No live generation, human labeling, private-pack access or scientific advancement occurred.

The external worker remains outside the provider-neutral package's runtime dependencies; only the optional `task9`/development group adds pinned tiktoken 0.14.0. The production tokenizer requires separately supplied, hash-checked local vocabulary; its framing profile has no live-certification switch. API access, current provider compatibility and billing identity were not probed. Independent OS custody/egress controls, account/project selection, refreshed prices and a clean reviewed revision remain pre-launch requirements. Local hash chains do not defend against complete malicious evidence rewriting. No merge or push is included in this work.
