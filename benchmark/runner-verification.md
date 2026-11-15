# Offline runner verification and contract traceability

Verification date: 2026-11-14. Baseline: `a05c471`; implementation branch: `codex/formal-benchmark`. This record covers public code and synthetic fixtures only. No live model study, human labeling, real restricted pack, host-compatibility study, or scientific stage advancement was executed.

## Test-first execution

Each component was introduced with focused failing tests before implementation. Observed RED boundaries included absent typed records/package, case/planner/store/adapters/conversation modules, missing scoring/statistics/reporting/CLI entry points, absent public corpus/preregistration/preflight contracts, and missing benchmark CI/acceptance evidence. GREEN checks then exercised real typed boundaries and synthetic subprocesses. The initial repository baseline was 178 passing standard-library tests, skill validation OK, repository validation OK, and repository-shell acceptance passing with AR-08/09 not ready.

Review regressions were also demonstrated RED before repair: generator self-grading; unscored successful generations counted as measured zeros; pending/missing results permitting claims; unmatched model/host cells treated as paired; semantic decisions omitted from final counts; undisclosed degenerate intervals; a malformed YAML traceback echoing input; secret-bearing configuration persisted to manifests; missing executable-source provenance; credential-bearing external score imports; partially unrated mechanisms treated as measured; budget-stopped turns being retried; malformed scalar token metadata; unrestricted export batches; partial ingestion; non-idempotent ingestion; and valid durable appends blocking crash recovery. Synthetic Git fixtures demonstrated unrelated executable-checkout refusal, reviewed-source mismatch hidden by assume-unchanged, pack digest disagreement, undeclared pack files, and missing/mismatched authorization.

## Fresh-shell handoff rehearsal

From `benchmark/`, use uv 0.12.8 with the locked environment (CPython 3.13). Follow the complete offline example in README.md. The retained generated example used the six named public IDs, all five conditions, one replicate, and the bundled fake agent: **30 parent jobs, 70 assistant calls** with a synthetic maximum cost of **0.70**. After execution, `resume` returned zero pending turns, `score` wrote 30 score records, `report` wrote Markdown and JSON with headline automated claims disabled, and `verify-run` verified 30 jobs and 8 canonical artifact digests. `compare` reported matching corpus, skill, runner, and parameters for self-comparison. These are protocol checks, not observed model performance or scientific feasibility results. The generated `runs/` records remain ignored; synthetic quality ratings were never invented.

The integration suite separately exercises both single-turn and three-assistant-turn conversations in the inbox protocol, equality of user disclosures across conditions, opaque external job IDs, exact index/attempt correlation, all-turn token sums, final-only extraction, immutable successes on resume, redaction before persistence, dry runs without writes, output-directory confinement, and artifact tamper rejection. Runtime tests exercise prefix-checkpoint recovery, typed durable tails, dispatch correlation, concurrency, whole-batch validation, identical re-ingestion, changed-response refusal, retries, ceilings and failure stops.

## Architecture evidence

| Criterion | Retained contract and deterministic evidence | Scope |
| --- | --- | --- |
| AR-08 | `src/systematic_innovation_bench/restricted_preflight.py`, `schemas/restricted-preflight.schema.json`, `tests/test_restricted_preflight.py`, `../docs/security/restricted-execution.md` | Synthetic controlled rehearsal: actual clean Git checkout/module/revision binding, dependency/candidate/pack digests, stage and execution identity, filesystem/egress/environment declarations, provider policy, storage controls, and bound explicit approval. Every missing/mismatched control refuses authorization with content-free diagnostics before adapter launch. Preflight records authorization only. OS sandbox/firewall and real custody evidence remain operator responsibilities. |
| AR-09 | `study/preregistration.yaml`, `study/stage-gates.yaml`, `study/analysis-plan.md`, `study/human-calibration.md`, `study/public-corpus-review.md`, `tests/test_preregistration.py`, `tests/test_public_corpus.py`, `tests/test_restricted_pack.py` | Approved splits, fixed disclosures, five-criterion gating before deduplication, case-level paired analysis, failure/missingness rules, pilot-derived freeze rules, F-31 blinding, stage order, authorization, contamination retirement/replacement, validation decision-only feedback, and sealed reporting/stop boundary. Draft/pending study contracts are verified; empirical stages are not passed. |

## Implementation decisions and limits

- Reused the current checkout on a local `codex/` branch. Disjoint domains ran in parallel with strict test-first work and independent component/final reviews; integration remained sequential.
- Full treatment reads the sole canonical skill pack; no behavior copy or skill modification was introduced. Named ablations require a separately versioned candidate pack and remain development-only.
- Public run commands are development-only. The restricted CLI validates external packs or records preflight authorization without launching adapters. Executing private stages requires the separately reviewed frozen operator environment described by the custody protocol.
- Per-turn prices are conservative declared ceilings. An unknown estimate remains unknown in planning and refuses automatic dispatch. Actual reported cost breaches stop future work. Subprocess execution is serial, within configured concurrency; inbox exports cap outstanding requests.
- Lexical equivalence is explicitly limited; retained semantic equivalence decisions are required for ambiguous paraphrases and are routed into raw and qualified counts. Generators cannot assign their own quality. Unmeasured semantic endpoints stay not assessed.
- Mypy follows each matrix interpreter and its compatible NumPy stubs; the Python 3.11 job verifies the compatibility floor. A fixed 3.11 target with Python 3.13-only dependency stubs caused a demonstrated parser failure and was removed without widening the supported Python range.
- Public manifests retain Git revision, executable-source digest and dirty-worktree status; mutating operations require the planned source digest. Local artifact hashes identify evidence and corruption; they are not signatures against an adversary able to rewrite the entire run directory. Restricted preflight additionally requires reviewed clean executable bytes.

Final command results are recorded below after the complete gate runs.

## Final gate results

- Root: `python3 -m unittest discover tests -v` — **180 passed**.
- Benchmark: `uv run --locked pytest -q` — **236 passed on each of Python 3.11, 3.13, and 3.14** using separate locked environments.
- `uv lock --check` — **29 packages resolved**, lock unchanged.
- `uv run --locked ruff check .` — **passed on all three matrix interpreters**.
- `uv run --locked mypy src` — **22 source files passed on all three matrix interpreters**.
- Skill validation, authority scan, tracked-public-tree validation, and `git diff --check` — **passed**. The skill SHA-256 is unchanged at `d5971f6e3e646916e2a287c5a8fde96a93b811ed071c362526c605ef222a890b`.
- Full architecture acceptance — **AR-01 through AR-12 passed**. AR-08/09 retain the implementation/protocol scope above; live scientific gates remain pending.
- Fresh whole-branch review identified four defects; one fix wave addressed all four, and scoped re-review found no residual blocker or fix-induced regression. The additional source-continuation gate passed its focused re-review.

Commands used the exact uv 0.12.8 pin; the available system uv 0.10.9 was not substituted. Dependencies and compatibility environments were isolated from root tooling. No origin push or merge was performed.

The handoff was repeated after the four local phase commits from a **clean checkout at `15cd80b915c459d84c2688160edf99336d506af5`**, using a fresh ID (`offline-clean-final`) and an operator copy of the fake configuration. It again completed 30 jobs / 70 turns, resumed with zero pending, scored 30 jobs, generated both reports without a headline claim, and verified 8 artifacts. The manifest recorded `runner_worktree_dirty: false` and a 64-character executable-source digest. The ignored runtime artifacts remain local.
