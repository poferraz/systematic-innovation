# Systematic Innovation Benchmark Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a provider-neutral, resumable benchmark runner that executes controlled single-turn and multi-turn experiments, preserves raw evidence, applies minimum quality gates, and produces statistically honest reports.

**Architecture:** A Python package under `benchmark/` owns typed records, case validation, job planning, controlled conversation state, append-only storage, adapters, scoring, statistics, and reporting. Multi-turn cases replay the same fixed user-disclosure schedule in every condition, and the final portfolio is scored while all assistant tokens count toward efficiency. The default inbox/outbox protocol works with any external tool capable of reading and writing JSONL, while a constrained subprocess adapter supports local coding-agent CLIs without embedding provider-specific logic in the core.

**Tech Stack:** Python 3.11+, Pydantic 2, PyYAML 6, NumPy 2, pytest 8, Ruff, Mypy, JSONL, Markdown

**Spec:** `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md`

**Approved Amendments:** The user's 2026-09-01 direction adds controlled multi-turn benchmarking, minimum mechanism quality gates, six-case and twelve-case feasibility stages, and cross-agent validation before the final release report. These later constraints supersede conflicting benchmark language in the specification.

## Global Constraints

1. The benchmark measures systematic ideation performance, not realized innovation.
2. The primary endpoint is paired change in qualified useful distinct mechanisms per 1,000 total assistant output tokens.
3. Raw prompts and responses are append-only and never replaced.
4. Validation and sealed-test content must not enter the public repository.
5. Model behavior, host integration, and automatic activation are separate studies.
6. The runner must support dry runs, resume, bounded retries, maximum calls, maximum cost, concurrency limits, a model allowlist, and failure thresholds.
7. Credentials must never appear in jobs, results, logs, or reports.
8. LLM judging must be blind to treatment identity, randomize answer order, and preserve disagreement.
9. Repetitions are chosen after pilot variance analysis rather than fixed globally.
10. The benchmark must report tokens, cost, latency, failures, and efficiency alongside quality.
11. The core runner contains no provider SDK dependency.
12. Controlled multi-turn cases give every condition the same ordered user disclosures and maximum number of assistant turns.
13. A mechanism contributes to the primary numerator only after relevance, constraint alignment, causal clarity, plausibility, and safety gates pass.
14. The primary efficiency denominator includes output tokens from every assistant turn, not only the final portfolio.
15. Every implementation task follows TDD and ends with a focused commit.

---

## Planned File Map

```text
benchmark/
├── pyproject.toml
├── README.md
├── src/systematic_innovation_bench/
│   ├── __init__.py
│   ├── cli.py
│   ├── models.py
│   ├── cases.py
│   ├── restricted.py
│   ├── planner.py
│   ├── conversation.py
│   ├── store.py
│   ├── redaction.py
│   ├── adapters/
│   │   ├── base.py
│   │   ├── inbox.py
│   │   └── subprocess.py
│   ├── scoring/
│   │   ├── deterministic.py
│   │   ├── mechanisms.py
│   │   └── judges.py
│   ├── statistics.py
│   └── reporting.py
├── schemas/
│   ├── case.schema.json
│   ├── job.schema.json
│   ├── response.schema.json
│   └── conversation.schema.json
├── configs/example.yaml
├── tests/
│   ├── fixtures/
│   ├── test_models.py
│   ├── test_cases.py
│   ├── test_planner.py
│   ├── test_store.py
│   ├── test_inbox.py
│   ├── test_conversation.py
│   ├── test_subprocess_adapter.py
│   ├── test_redaction.py
│   ├── test_deterministic_scoring.py
│   ├── test_mechanisms.py
│   ├── test_judges.py
│   ├── test_statistics.py
│   ├── test_reporting.py
│   └── test_cli_integration.py
└── HANDOFF.md
```

### Task 1: Create the Package and Typed Record Contract

**Files:**

1. Create: `benchmark/pyproject.toml`
2. Create: `benchmark/src/systematic_innovation_bench/__init__.py`
3. Create: `benchmark/src/systematic_innovation_bench/models.py`
4. Create: `benchmark/tests/test_models.py`

**Interfaces:**

1. Produces: `BenchmarkCase`, `Condition`, `InteractionMode`, `ConversationScript`, `ConversationTurn`, `TurnJob`, `TurnResponse`, `ConversationRecord`, `Job`, `ResponseRecord`, `Mechanism`, `MechanismQuality`, `ScoreRecord`, `RunConfig`, and `RunManifest` Pydantic models.
2. Consumes later: Every runner component serializes through these models.

- [ ] **Step 1: Write failing model tests**

```python
from datetime import datetime, timezone
import pytest
from systematic_innovation_bench.models import (
    BenchmarkCase,
    Condition,
    ConversationScript,
    InteractionMode,
    Job,
)


def test_case_rejects_sealed_content_in_public_split():
    with pytest.raises(ValueError, match="hidden mechanisms"):
        BenchmarkCase(
            id="case-001",
            family="synthetic-mechanism",
            domain="operations",
            split="development",
            prompt="Improve this system",
            hidden_mechanisms=["pooled demand"],
            strata={"mode": "quick"},
        )


def test_job_has_stable_identity():
    job = Job(
        run_id="run-001",
        case_id="case-001",
        condition=Condition.FULL_SKILL,
        replicate=0,
        model="example-model",
        host="inbox",
        prompt="Prompt",
        created_at=datetime(2026, 8, 31, tzinfo=timezone.utc),
    )
    assert job.job_id == "run-001:case-001:full-skill:0:example-model:inbox"


def test_multi_turn_case_requires_a_fixed_disclosure_script():
    with pytest.raises(ValueError, match="conversation script"):
        BenchmarkCase(
            id="case-002",
            family="open-ended-systemic",
            domain="operations",
            split="development",
            prompt="Improve this system",
            strata={"mode": "deep"},
            interaction_mode=InteractionMode.CONTROLLED_MULTI_TURN,
        )

    script = ConversationScript(
        user_turns=(
            "Additional context supplied identically to every condition.",
            "Final context. Produce the final portfolio now.",
        ),
    )
    assert script.maximum_assistant_turns == 3
```

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_models.py -v`

Expected: import failure because the package does not exist.

- [ ] **Step 3: Create package metadata**

Configure Python `>=3.11`, runtime dependencies `pydantic>=2.8,<3`, `PyYAML>=6,<7`, and `numpy>=2,<3`; development dependencies `pytest>=8,<9`, `pytest-cov>=5,<7`, `ruff>=0.6,<1`, and `mypy>=1.11,<2`. Expose console script `sib = systematic_innovation_bench.cli:main`.

- [ ] **Step 4: Implement the models**

```python
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Condition(StrEnum):
    VANILLA = "vanilla"
    GENERIC_BRAINSTORM = "generic-brainstorm"
    FORMAT_MATCHED = "format-matched"
    ESTABLISHED_METHOD = "established-method"
    FULL_SKILL = "full-skill"
    ABLATION = "ablation"


class InteractionMode(StrEnum):
    SINGLE_TURN = "single-turn"
    CONTROLLED_MULTI_TURN = "controlled-multi-turn"


class ConversationScript(StrictModel):
    user_turns: tuple[str, ...] = Field(min_length=1)

    @computed_field
    @property
    def maximum_assistant_turns(self) -> int:
        return len(self.user_turns) + 1


class BenchmarkCase(StrictModel):
    id: str
    family: str
    domain: str
    split: str
    prompt: str
    strata: dict[str, str]
    expected_mode: str | None = None
    should_trigger: bool | None = None
    interaction_mode: InteractionMode = InteractionMode.SINGLE_TURN
    conversation_script: ConversationScript | None = None
    hidden_mechanisms: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def protect_public_cases(self):
        if self.split == "development" and self.hidden_mechanisms:
            raise ValueError("hidden mechanisms are forbidden in public development cases")
        if (self.interaction_mode is InteractionMode.CONTROLLED_MULTI_TURN
                and self.conversation_script is None):
            raise ValueError("controlled multi-turn case requires conversation script")
        if (self.interaction_mode is InteractionMode.SINGLE_TURN
                and self.conversation_script is not None):
            raise ValueError("single-turn case cannot contain conversation script")
        return self


class Job(StrictModel):
    run_id: str
    case_id: str
    condition: Condition
    replicate: int = Field(ge=0)
    model: str
    host: str
    prompt: str
    created_at: datetime

    @computed_field
    @property
    def job_id(self) -> str:
        return ":".join((self.run_id, self.case_id, self.condition.value,
                         str(self.replicate), self.model, self.host))
```

Implement the remaining records with strict fields specified in section 25 of the design. `ConversationTurn` contains `turn_index`, `role`, `content`, tokens, cost, latency, and timestamp. `TurnJob` contains the parent `job_id`, `assistant_turn_index`, immutable transcript ending in a user turn, and condition-rendered system instructions; define `TurnJob.from_state(state, transcript)` to set `assistant_turn_index = len(transcript) + 1`. `TurnResponse` contains exactly one assistant turn at that index. `ConversationRecord` contains the complete ordered transcript, final assistant response, total assistant output tokens, total cost, and total latency. `ResponseRecord` wraps either a single-turn result or a completed `ConversationRecord`. `MechanismQuality` stores 0-to-3 relevance, constraint alignment, causal clarity, and plausibility plus a critical-safety-violation boolean. `ScoreRecord` preserves mechanism-level quality gates, criterion scores, and judge evidence. `RunConfig` contains budgets and allowlists. `RunManifest` contains benchmark, runner, skill, and Git versions.

- [ ] **Step 5: Run and verify GREEN**

Run: `cd benchmark && uv run pytest tests/test_models.py -v`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add benchmark/pyproject.toml benchmark/src benchmark/tests/test_models.py
git commit -m "feat: define benchmark record contracts"
```

### Task 2: Validate and Load Case Packs

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/cases.py`
2. Create: `benchmark/tests/test_cases.py`
3. Create: `benchmark/schemas/case.schema.json`

**Interfaces:**

1. Produces: `load_cases(paths: Sequence[Path], expected_split: str | None = None) -> list[BenchmarkCase]`.
2. Produces: `summarize_strata(cases: Sequence[BenchmarkCase]) -> dict[str, dict[str, int]]`.
3. Reserves: `restricted.py` for the private-pack implementation specified in Task 6 of the benchmark-study plan; the runner CLI imports it lazily so ordinary public runs do not require a restricted pack.

- [ ] **Step 1: Write failing tests**

Test valid YAML loading, duplicate-ID rejection across files, split mismatch rejection, missing strata rejection, deterministic order by case ID, and refusal to load restricted content from a path inside the public repository.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_cases.py -v`

Expected: import failure.

- [ ] **Step 3: Implement the loader**

```python
from pathlib import Path
from collections.abc import Sequence
import yaml
from .models import BenchmarkCase


def load_cases(paths: Sequence[Path], expected_split: str | None = None) -> list[BenchmarkCase]:
    cases: list[BenchmarkCase] = []
    for path in paths:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        cases.extend(BenchmarkCase.model_validate(item) for item in payload["cases"])
    ids = [case.id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case id")
    if expected_split and any(case.split != expected_split for case in cases):
        raise ValueError(f"case split does not match {expected_split}")
    return sorted(cases, key=lambda case: case.id)
```

Add explicit path-boundary checks through a caller-supplied `public_root` rather than assuming a machine-specific path.

- [ ] **Step 4: Add the JSON Schema**

Mirror the strict Pydantic case contract for external tools. Do not include hidden-mechanism fields in the public case schema.

- [ ] **Step 5: Run tests and commit**

```bash
cd benchmark && uv run pytest tests/test_cases.py -v
cd ..
git add benchmark/src/systematic_innovation_bench/cases.py benchmark/tests/test_cases.py benchmark/schemas/case.schema.json
git commit -m "feat: validate benchmark case packs"
```

### Task 3: Plan Reproducible Experimental Jobs

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/planner.py`
2. Create: `benchmark/tests/test_planner.py`
3. Create: `benchmark/configs/example.yaml`

**Interfaces:**

1. Produces: `plan_jobs(cases: Sequence[BenchmarkCase], config: RunConfig, now: datetime) -> list[Job]`.
2. Produces: `estimate_run(jobs: Sequence[Job], config: RunConfig) -> RunEstimate`, where maximum calls and cost include every planned assistant turn in controlled conversations.
3. Produces: `select_cases(cases: Sequence[BenchmarkCase], case_ids: Sequence[str] | None) -> list[BenchmarkCase]` with exact-ID validation for staged runs.

- [ ] **Step 1: Write failing planning tests**

Test stable ordering, exact case-ID subset selection with unknown and duplicate ID rejection, correct factorial expansion across conditions/models/hosts/replicates, maximum-call rejection, model allowlist enforcement, ablations restricted to development, identical initial prompts across treatment arms except condition preambles, and identical user-disclosure schedules across all conditions for the same multi-turn case.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_planner.py -v`

Expected: import failure.

- [ ] **Step 3: Implement condition rendering**

Create explicit preambles for vanilla, generic brainstorming, format-matched, established-method, full-skill, and named ablations. The format-matched condition must request the same output shape and maximum count without mentioning Reasoning Cells, mechanism ledger, system map, preservation, or saturation.

- [ ] **Step 4: Implement job expansion and estimation**

Use a stable nested order of case, condition, model, host, and replicate. A single-turn `Job` estimates one generation call; a controlled multi-turn `Job` estimates `conversation_script.maximum_assistant_turns` calls. Reject plans whose total estimated turn calls exceed `max_calls`. Calculate worst-case configured cost across all planned turns when per-model estimates exist; otherwise mark cost unknown rather than treating it as zero.

- [ ] **Step 5: Add the example configuration**

Include dry run enabled, development split only, explicit model allowlist, maximum 50 calls, maximum concurrency 2, retry limit 1, failure threshold 0.20, and no configured API credentials.

- [ ] **Step 6: Run tests and commit**

```bash
cd benchmark && uv run pytest tests/test_planner.py -v
cd ..
git add benchmark/src/systematic_innovation_bench/planner.py benchmark/tests/test_planner.py benchmark/configs/example.yaml
git commit -m "feat: plan bounded benchmark runs"
```

### Task 4: Preserve Append-Only Results and Resume Safely

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/store.py`
2. Create: `benchmark/tests/test_store.py`
3. Create: `benchmark/schemas/job.schema.json`
4. Create: `benchmark/schemas/response.schema.json`
5. Create: `benchmark/schemas/conversation.schema.json`

**Interfaces:**

1. Produces: `append_record(path: Path, record: BaseModel) -> None`.
2. Produces: `read_records(path: Path, model_type: type[T]) -> list[T]`.
3. Produces: `turn_responses_for_job(responses: Sequence[TurnResponse], job_id: str) -> tuple[TurnResponse, ...]`.
4. Produces: `terminal_job_ids(responses: Sequence[ResponseRecord]) -> frozenset[str]`.
5. Stores: Only records that have passed the redaction boundary defined in Task 7; “raw response” means the complete provider response after credential and authorization-value redaction, not an unredacted secret-bearing payload.

- [ ] **Step 1: Write failing storage tests**

Test one-record-per-line JSONL, flush and `fsync`, malformed-line detection with line number, duplicate terminal response rejection, retry-attempt preservation, ordered partial-conversation preservation, and exact per-job turn retrieval.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_store.py -v`

Expected: import failure.

- [ ] **Step 3: Implement append-only writes**

```python
from pathlib import Path
import os
from pydantic import BaseModel


def append_record(path: Path, record: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = record.model_dump_json(exclude_none=False)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(payload + "\n")
        handle.flush()
        os.fsync(handle.fileno())
```

Never rewrite a raw result file. Derived reports may be regenerated in separate paths.

- [ ] **Step 4: Implement resume semantics and schemas**

Terminal statuses are `succeeded`, `failed`, `refused`, and `budget-stopped`. A retry creates a new response record with an incremented attempt and never erases the earlier failure. Persist every accepted `TurnResponse` before planning the next turn; a completed `ConversationRecord` references the ordered turn-record identifiers and never duplicates or rewrites them. Task 6 reconstructs resume state from `turn_responses_for_job`.

- [ ] **Step 5: Run tests and commit**

```bash
cd benchmark && uv run pytest tests/test_store.py -v
cd ..
git add benchmark/src/systematic_innovation_bench/store.py benchmark/tests/test_store.py benchmark/schemas
git commit -m "feat: preserve resumable benchmark evidence"
```

### Task 5: Implement Inbox and Outbox Exchange

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/adapters/base.py`
2. Create: `benchmark/src/systematic_innovation_bench/adapters/inbox.py`
3. Create: `benchmark/tests/test_inbox.py`

**Interfaces:**

1. Defines: `Adapter.run_turn(job: TurnJob) -> TurnResponse` protocol. Single-turn jobs use the same interface with `assistant_turn_index == 2` after the initial user turn at index 1.
2. Produces: `export_turn_jobs(jobs, path)`, `ingest_turn_responses(path)`, and `validate_turn_correlation(jobs, responses)`.

- [ ] **Step 1: Write failing exchange tests**

Test exact parent-job and turn-index correlation, rejection of unknown job IDs, out-of-order responses, duplicate turn outputs, omitted raw text, nonterminal status, malformed JSONL, and safe re-ingestion of an already ingested file.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_inbox.py -v`

Expected: import failure.

- [ ] **Step 3: Implement the protocol and exchange**

```python
from typing import Protocol
from ..models import TurnJob, TurnResponse


class Adapter(Protocol):
    def run_turn(self, job: TurnJob) -> TurnResponse: ...
```

Export only the next pending turn for each active conversation. Each `TurnJob` contains the immutable transcript through the most recent user turn, so an external tool needs no hidden runner state. Ingestion validates the complete typed response and exact turn correlation before appending it to the canonical raw turn log.

- [ ] **Step 4: Run tests and commit**

```bash
cd benchmark && uv run pytest tests/test_inbox.py -v
cd ..
git add benchmark/src/systematic_innovation_bench/adapters benchmark/tests/test_inbox.py
git commit -m "feat: add provider-neutral benchmark exchange"
```

### Task 6: Execute Controlled Multi-Turn Conversations

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/conversation.py`
2. Create: `benchmark/tests/test_conversation.py`
3. Modify: `benchmark/src/systematic_innovation_bench/store.py`

**Interfaces:**

1. Produces: `start_conversation(job: Job, case: BenchmarkCase) -> ConversationState`.
2. Produces: `next_turn_job(state: ConversationState) -> TurnJob | None`.
3. Produces: `accept_turn(state: ConversationState, turn_job: TurnJob, response: TurnResponse) -> ConversationState`.
4. Produces: `complete_conversation(state: ConversationState) -> ConversationRecord`.

- [ ] **Step 1: Write failing controlled-conversation tests**

```python
def test_every_condition_receives_the_same_fixed_user_disclosures(make_job, deep_case):
    transcripts = []
    for condition in Condition:
        state = start_conversation(make_job(condition), deep_case)
        while (turn_job := next_turn_job(state)) is not None:
            state = accept_turn(state, turn_job, fake_turn_response(turn_job))
        transcripts.append([
            turn.content for turn in state.turns if turn.role == "user"
        ])
    assert all(transcript == transcripts[0] for transcript in transcripts[1:])


def test_final_portfolio_and_total_assistant_tokens_are_separate(make_job, deep_case):
    state = run_scripted_conversation(make_job(Condition.FULL_SKILL), deep_case, [20, 30, 120])
    record = complete_conversation(state)
    assert record.final_response == state.turns[-1].content
    assert record.final_response_output_tokens == 120
    assert record.total_assistant_output_tokens == 170
```

Also test strict alternating roles, immutable prior turns, exact turn indices, refusal to exceed the scripted maximum, resume after each accepted turn, finalization only after the last assistant response, and single-turn compatibility.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_conversation.py -v`

Expected: import failure because `conversation.py` does not exist.

- [ ] **Step 3: Implement deterministic conversation advancement**

```python
def next_turn_job(state: ConversationState) -> TurnJob | None:
    if state.is_complete:
        return None
    if not state.turns:
        user_content = state.initial_prompt
    else:
        disclosure_index = state.assistant_turn_count - 1
        user_content = state.script.user_turns[disclosure_index]
    transcript = (*state.turns, ConversationTurn(
        turn_index=len(state.turns) + 1,
        role="user",
        content=user_content,
    ))
    return TurnJob.from_state(state, transcript=transcript)
```

`accept_turn` must require `response.turn_index == turn_job.assistant_turn_index`, verify that the `TurnJob` transcript is the exact deterministic continuation of state, append that user turn and assistant response to the new immutable state, persist the assistant response append-only, and mark completion only when `assistant_turn_count == script.maximum_assistant_turns`. The controller never interprets the assistant's questions and never changes disclosures by condition. This fixed schedule provides identical information while still observing whether each condition asks, revises, and synthesizes across turns.

- [ ] **Step 4: Define scoring boundaries**

Extract candidate mechanisms only from `ConversationRecord.final_response`. Calculate efficiency with `ConversationRecord.total_assistant_output_tokens`, total assistant cost, and total conversation latency. Preserve question count, revision behavior, and use of newly disclosed information as secondary multi-turn measures.

- [ ] **Step 5: Run and verify GREEN**

Run: `cd benchmark && uv run pytest tests/test_conversation.py tests/test_store.py tests/test_inbox.py -v`

Expected: all conversation, persistence, and exchange tests pass.

- [ ] **Step 6: Commit**

```bash
git add benchmark/src/systematic_innovation_bench/conversation.py benchmark/src/systematic_innovation_bench/store.py benchmark/tests/test_conversation.py
git commit -m "feat: add controlled multi-turn benchmarking"
```

### Task 7: Add Secret Redaction and the Constrained Subprocess Adapter

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/redaction.py`
2. Create: `benchmark/src/systematic_innovation_bench/adapters/subprocess.py`
3. Create: `benchmark/tests/test_redaction.py`
4. Create: `benchmark/tests/test_subprocess_adapter.py`

**Interfaces:**

1. Produces: `redact_text(text: str, secret_values: Sequence[str]) -> str`.
2. Produces: `SubprocessAdapter(command: tuple[str, ...], allowed_executables: frozenset[str], timeout_seconds: int)`.

- [ ] **Step 1: Write failing security tests**

Test redaction of configured secrets, common authorization headers, and URL credentials. Test executable allowlist enforcement, argument-array execution without a shell, timeout, nonzero exit capture, output-size limit, and inherited-environment filtering.
Also test that inbox ingestion and subprocess completion call redaction before `append_record`, using a sentinel secret that must be absent from the canonical JSONL file.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_redaction.py tests/test_subprocess_adapter.py -v`

Expected: import failure.

- [ ] **Step 3: Implement redaction**

Replace exact configured secret values and recognized bearer/basic authorization patterns with `[REDACTED]`. Never print environment variables during error reporting.

- [ ] **Step 4: Implement subprocess execution**

Use `subprocess.run` with a list of arguments, `shell=False`, a filtered environment, text input through stdin, bounded timeout, and bounded captured output. Reject executable paths not in the configured allowlist before launching.

- [ ] **Step 5: Run tests and commit**

```bash
cd benchmark && uv run pytest tests/test_redaction.py tests/test_subprocess_adapter.py -v
cd ..
git add benchmark/src/systematic_innovation_bench/redaction.py benchmark/src/systematic_innovation_bench/adapters/subprocess.py benchmark/tests
git commit -m "feat: secure local benchmark adapters"
```

### Task 8: Add Deterministic and Quality-Gated Mechanism Scoring

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/scoring/deterministic.py`
2. Create: `benchmark/src/systematic_innovation_bench/scoring/mechanisms.py`
3. Create: `benchmark/tests/test_deterministic_scoring.py`
4. Create: `benchmark/tests/test_mechanisms.py`

**Interfaces:**

1. Produces: `score_deterministic(job, response) -> dict[str, float | int | bool]`.
2. Produces: `mechanism_signature(mechanism: Mechanism) -> tuple[str, ...]`.
3. Produces: `passes_quality_gate(quality: MechanismQuality) -> bool`.
4. Produces: `distinct_mechanism_count(mechanisms: Sequence[Mechanism]) -> int` for the disclosed raw count.
5. Produces: `qualified_distinct_mechanism_count(mechanisms: Sequence[Mechanism]) -> int` for the primary numerator.

- [ ] **Step 1: Write failing deterministic tests**

Test status, per-turn and total token counts, latency, output presence, requested count, implementation-drift phrase checks, and question count. Assert that missing provider token metadata remains `None` rather than estimated as fact, and that controlled multi-turn efficiency uses all assistant output tokens.

- [ ] **Step 2: Write failing mechanism tests**

Use fixtures where two differently named ideas share the same intervention, actor, flow, and effect; require one raw mechanism family. Use fixtures with a different causal flow but similar wording; require two raw families. Add exact quality-gate fixtures:

```python
def test_minimum_quality_gate_is_conjunctive():
    passing = MechanismQuality(
        relevance=2,
        constraint_alignment=2,
        causal_clarity=2,
        plausibility=1,
        critical_safety_violation=False,
    )
    assert passes_quality_gate(passing)
    assert not passes_quality_gate(passing.model_copy(update={"relevance": 1}))
    assert not passes_quality_gate(passing.model_copy(update={"constraint_alignment": 1}))
    assert not passes_quality_gate(passing.model_copy(update={"causal_clarity": 1}))
    assert not passes_quality_gate(passing.model_copy(update={"plausibility": 0}))
    assert not passes_quality_gate(passing.model_copy(update={"critical_safety_violation": True}))


def test_only_qualified_mechanisms_enter_primary_numerator(mechanism_fixture):
    mechanisms = mechanism_fixture(qualities=["pass", "fail-relevance", "pass-duplicate"])
    assert distinct_mechanism_count(mechanisms) == 2
    assert qualified_distinct_mechanism_count(mechanisms) == 1
```

- [ ] **Step 3: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_deterministic_scoring.py tests/test_mechanisms.py -v`

Expected: import failure.

- [ ] **Step 4: Implement objective checks and structured signatures**

Mechanism identity uses normalized intervention point, changed flow, causal operation, and intended effect. Actor changes alone create variants unless a second structural dimension changes. `passes_quality_gate` returns true only for relevance at least 2 of 3, constraint alignment at least 2 of 3, causal clarity at least 2 of 3, plausibility at least 1 of 3, and no critical safety or rights violation. Preserve every extracted candidate and raw family before filtering. Apply the gate to candidates, then deduplicate the qualifying candidates by causal signature. Keep the semantic ratings outside deterministic extraction and preserve their judge evidence.

- [ ] **Step 5: Run tests and commit**

```bash
cd benchmark && uv run pytest tests/test_deterministic_scoring.py tests/test_mechanisms.py -v
cd ..
git add benchmark/src/systematic_innovation_bench/scoring benchmark/tests
git commit -m "feat: score benchmark structure and mechanisms"
```

### Task 9: Orchestrate Blind Pairwise Judges

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/scoring/judges.py`
2. Create: `benchmark/tests/test_judges.py`

**Interfaces:**

1. Produces: `build_pairwise_jobs(...) -> list[Job]` with both answer orders.
2. Produces: `aggregate_pairwise(scores: Sequence[ScoreRecord]) -> PairwiseResult`.

- [ ] **Step 1: Write failing judge tests**

Test removal of condition and model labels, stable seeded randomization, both presentation orders, criterion-specific evidence requirement, disagreement preservation, incomplete judge-pair rejection, same-family judge warnings, and mechanism-level 0-to-3 anchored judgments for relevance, constraint alignment, causal clarity, and plausibility plus critical safety violation.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_judges.py -v`

Expected: import failure.

- [ ] **Step 3: Implement pair construction**

Judge prompts include the complete user transcript, rubric criterion, normalized candidate labels `A` and `B`, and final portfolios. They do not include treatment, host, model, skill, or file names. Generate an order-swapped pair for every comparison. Create separate blinded mechanism-quality jobs that return one anchored rating and one evidence span per criterion; they cannot see the efficiency formula or acceptance threshold.

- [ ] **Step 4: Implement aggregation**

Return win, tie, loss, order consistency, judge-family disagreement, and evidence. Do not collapse inconsistent order judgments into a confident winner.

- [ ] **Step 5: Run tests and commit**

```bash
cd benchmark && uv run pytest tests/test_judges.py -v
cd ..
git add benchmark/src/systematic_innovation_bench/scoring/judges.py benchmark/tests/test_judges.py
git commit -m "feat: add bias-aware blind judging"
```

### Task 10: Compute Case-Level Statistics and Efficiency

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/statistics.py`
2. Create: `benchmark/tests/test_statistics.py`

**Interfaces:**

1. Produces: `paired_case_effects(records, treatment, control, metric) -> list[CaseEffect]`.
2. Produces: `bootstrap_case_ci(effects, repetitions, seed) -> ConfidenceInterval`.
3. Produces: `win_tie_loss(effects, equivalence_margin) -> WinTieLoss`.

- [ ] **Step 1: Write failing statistical tests**

Use a fixed synthetic dataset with hand-calculated paired differences. Test case-level averaging before bootstrap, reproducible seeded confidence intervals, failures retained as zero qualified mechanisms, equivalence-margin ties, and efficiency normalization by total assistant tokens, cost, and latency. Assert that a multi-turn record with 4 qualified distinct mechanisms and 2,000 total assistant output tokens scores exactly 2.0 even when its final response contains only 1,200 tokens.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_statistics.py -v`

Expected: import failure.

- [ ] **Step 3: Implement paired analysis**

Never treat stochastic replicates from one case as independent cases. Aggregate within case and condition first, then bootstrap cases with replacement. Define the primary per-run metric as `1000 * qualified_distinct_mechanisms / total_assistant_output_tokens`; reject a primary score when token accounting is missing instead of substituting final-response tokens. Return effect size, interval, sample size, missingness, and the parallel raw distinct-mechanism count.

- [ ] **Step 4: Run tests and commit**

```bash
cd benchmark && uv run pytest tests/test_statistics.py -v
cd ..
git add benchmark/src/systematic_innovation_bench/statistics.py benchmark/tests/test_statistics.py
git commit -m "feat: analyze paired benchmark effects"
```

### Task 11: Generate Transparent Reports

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/reporting.py`
2. Create: `benchmark/tests/test_reporting.py`

**Interfaces:**

1. Produces: `build_report_data(...) -> dict[str, object]`.
2. Produces: `write_markdown_report(data, path) -> None` and `write_json_report(data, path) -> None`.

- [ ] **Step 1: Write failing report tests**

Require primary endpoint, confidence interval, win/tie/loss, qualified and raw distinct-mechanism counts, mechanism gate pass and failure counts by criterion, total conversation tokens, every confirmatory and efficiency metric, failures, sample counts, model/host strata, single-turn versus multi-turn strata, judge calibration status, limitations, and skill/benchmark commit hashes. Require reports to refuse a headline automated claim when human calibration failed.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_reporting.py -v`

Expected: import failure.

- [ ] **Step 3: Implement Markdown and JSON reports**

The report begins with the primary paired effect, not an optional composite. It shows the qualifying threshold, raw extracted mechanisms, raw distinct families, qualified candidates, qualified distinct families, and total assistant tokens so terse-output gaming is visible. It separates confirmatory and exploratory endpoints and reports controlled multi-turn results separately from single-turn results. An optional composite appears only when the run manifest contains preregistered weights and sensitivity results.

- [ ] **Step 4: Run tests and commit**

```bash
cd benchmark && uv run pytest tests/test_reporting.py -v
cd ..
git add benchmark/src/systematic_innovation_bench/reporting.py benchmark/tests/test_reporting.py
git commit -m "feat: report benchmark effects transparently"
```

### Task 12: Expose the CLI and End-to-End Fake-Adapter Test

**Files:**

1. Create: `benchmark/src/systematic_innovation_bench/cli.py`
2. Create: `benchmark/tests/fixtures/fake_agent.py`
3. Create: `benchmark/tests/test_cli_integration.py`
4. Create: `benchmark/README.md`

**Interfaces:**

1. Produces CLI commands: `validate`, `validate-pack`, `plan`, `export`, `ingest`, `run`, `resume`, `score`, `report`, `compare`, and `verify-run`.
2. Consumes: All runner modules.

- [ ] **Step 1: Write the failing end-to-end test**

The test creates one single-turn and one controlled multi-turn case, plans vanilla and full-skill jobs, exports one turn at a time, has the fake agent return standardized responses, verifies identical multi-turn user disclosures across conditions, ingests every response, scores only the final portfolios using all assistant tokens, resumes with zero pending turns, compares two run manifests, generates Markdown and JSON reports, and verifies all artifact digests. A separate temporary fixture exercises `validate-pack` without printing its prompt sentinel.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_cli_integration.py -v`

Expected: CLI import or command failure.

- [ ] **Step 3: Implement CLI dispatch**

Use `argparse`. Every mutating command supports `--dry-run`. `plan` and `run` accept an optional comma-separated `--case-ids` list and reject unknown, repeated, or empty IDs. Require explicit paths for cases, config, run directory, and restricted pack. Print concise summaries and return nonzero on validation, budget, correlation, conversation-protocol, or security errors.

- [ ] **Step 4: Write benchmark README**

Document installation with `uv sync`, the turn-level inbox/outbox workflow, controlled disclosure scripts, subprocess safety, dry run, mid-conversation resume, quality gates, directory layout, and a complete fake-adapter example. State that provider adapters belong outside the core unless independently reviewed.

- [ ] **Step 5: Run the complete suite**

```bash
cd benchmark
uv run pytest -q
uv run ruff check .
uv run mypy src
```

Expected: all commands pass without warnings.

- [ ] **Step 6: Commit**

```bash
git add benchmark
git commit -m "feat: complete provider-neutral benchmark runner"
```

### Task 13: Add the External-Agent Handoff and Runner Verification Gate

**Files:**

1. Create: `benchmark/HANDOFF.md`
2. Create: `benchmark/runner-verification.md`

**Interfaces:**

1. Produces: A self-contained operating brief for another coding agent.
2. Depends on: All CLI commands and safety limits from earlier tasks.

- [ ] **Step 1: Write the handoff**

Include exact steps to validate the environment, run a dry plan, export only pending turns, process JSONL without modifying transcripts or disclosure order, ingest results, resume interrupted conversations, apply mechanism quality gates, run judges, generate reports, protect restricted cases, enforce budgets, and stop after configured limits. Require the external agent to propose candidate skill changes on a separate branch and never overwrite a released version.

- [ ] **Step 2: Execute the handoff using the fake adapter**

Follow `HANDOFF.md` from a fresh shell without relying on unstated knowledge. Record every command and expected artifact in `runner-verification.md`.

- [ ] **Step 3: Run final verification**

```bash
cd benchmark
uv run pytest -q
uv run ruff check .
uv run mypy src
uv run sib --help
cd ..
git diff --check
```

Expected: all checks pass and help lists all eleven commands.

- [ ] **Step 4: Commit**

```bash
git add benchmark/HANDOFF.md benchmark/runner-verification.md
git commit -m "docs: add benchmark runner handoff"
```
