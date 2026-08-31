# Systematic Innovation Benchmark Study Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author, preregister, calibrate, execute, and report a 100-case study that estimates whether `systematic-innovation` improves useful mechanism diversity without hiding extra cost, risk, or judge disagreement.

**Architecture:** Public development cases and all study protocols live in Git. Restricted validation and sealed-test cases use the same schema but live in an operator-supplied directory outside the repository. The benchmark runner from the companion plan executes each frozen condition through provider-neutral adapters, while preregistered gates prevent repeated tuning against held-out evidence.

**Tech Stack:** YAML, JSON Schema, Markdown, Python 3.11+, pytest, the `systematic-innovation-bench` CLI from the runner plan, Git

**Spec:** `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md`

## Global Constraints

1. The study measures systematic ideation performance, not realized innovation.
2. The corpus contains exactly 100 cases: 60 public development, 20 restricted validation, and 20 sealed test.
3. Family totals are fixed at 24 synthetic mechanism-space, 16 counterfactual rediscovery, 30 open-ended systemic, 10 preservation/no-change, 10 trigger/scope, and 10 adversarial/high-stakes cases.
4. Split allocations are fixed at `14/5/5`, `10/3/3`, `18/6/6`, `6/2/2`, `6/2/2`, and `6/2/2` respectively for development/validation/test.
5. Validation and sealed prompts, gold mechanisms, distractors, and case notes never enter the public Git repository, build artifacts, logs, or issue tracker.
6. The primary endpoint is paired change in useful distinct mechanisms per 1,000 output tokens.
7. The comparison set includes vanilla, generic brainstorm, format-matched control, established method, and full skill. Ablations are development-only.
8. Generators never receive rubrics, gold mechanisms, judge notes, treatment labels, or another condition's output.
9. Judge inputs are treatment-blind and order-randomized. Disagreement and abstention are preserved.
10. Pilot variance determines repetition counts before validation. The sealed test is run once after the candidate and analysis are frozen.
11. Case is the unit of analysis; uncertainty is estimated by resampling cases, not individual generations.
12. All run artifacts are append-only, redacted, budget-bounded, and resumable.
13. Every public authoring or protocol task follows RED, GREEN, REFACTOR and ends with a focused commit.

---

## Planned File Map

| File | Responsibility |
| --- | --- |
| `benchmark/cases/development/synthetic.yaml` | Fourteen public mechanism-space cases |
| `benchmark/cases/development/rediscovery.yaml` | Ten public counterfactual rediscovery cases |
| `benchmark/cases/development/open-ended.yaml` | Eighteen public systemic cases |
| `benchmark/cases/development/preservation.yaml` | Six public preservation/no-change cases |
| `benchmark/cases/development/trigger.yaml` | Six public trigger and scope cases |
| `benchmark/cases/development/adversarial.yaml` | Six public adversarial/high-stakes cases |
| `benchmark/study/corpus-manifest.yaml` | Exact family, split, domain, and stratum requirements |
| `benchmark/study/authoring-guide.md` | Case-writing, leakage, quality, and review rules |
| `benchmark/study/restricted-pack.schema.json` | Contract for private validation and sealed packs |
| `benchmark/study/preregistration.yaml` | Frozen hypotheses, endpoints, conditions, exclusions, and gates |
| `benchmark/study/analysis-plan.md` | Estimands, bootstrap, multiplicity, missingness, and sensitivity analysis |
| `benchmark/study/human-calibration.md` | Annotator training, adjudication, and judge acceptance protocol |
| `benchmark/study/release-gates.md` | Ordered development, validation, freeze, sealed-test, and release gates |
| `benchmark/study/integration-matrix.yaml` | Installation, explicit invocation, and activation claims by host |
| `benchmark/study/cross-agent-study.md` | Protocol for separate host-integration and activation studies |
| `benchmark/study/LOOP-HANDOFF.md` | Provider-neutral instructions for repeated external execution |
| `benchmark/src/systematic_innovation_bench/restricted.py` | Private-pack validation and content-free summaries |
| `benchmark/tests/conftest.py` | Shared public-corpus and synthetic restricted-pack fixtures |
| `benchmark/tests/test_public_corpus.py` | Counts, schema, uniqueness, strata, and leakage tests |
| `benchmark/tests/test_restricted_pack.py` | Private pack validation without printing content |
| `benchmark/tests/test_preregistration.py` | Preregistration completeness and freeze tests |

The restricted files are operator-owned and are never planned as repository paths. The runner receives them only through `--restricted-pack /absolute/path/to/pack`.

### Task 1: Freeze the Corpus Contract Before Authoring Cases

**Files:**

1. Create: `benchmark/study/corpus-manifest.yaml`
2. Create: `benchmark/study/authoring-guide.md`
3. Create: `benchmark/tests/conftest.py`
4. Create: `benchmark/tests/test_public_corpus.py`

**Interfaces:**

1. Produces: Machine-readable expected counts by family and split.
2. Constrains: Every public and restricted case file authored later.

- [ ] **Step 1: Write the failing manifest test**

```python
from collections import Counter
from pathlib import Path
import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_manifest_fixes_exact_100_case_allocation():
    manifest = yaml.safe_load(
        (ROOT / "study/corpus-manifest.yaml").read_text(encoding="utf-8")
    )
    allocations = manifest["allocations"]
    assert sum(sum(row[split] for split in ("development", "validation", "test"))
               for row in allocations.values()) == 100
    assert Counter({
        split: sum(row[split] for row in allocations.values())
        for split in ("development", "validation", "test")
    }) == Counter(development=60, validation=20, test=20)
    assert allocations == {
        "synthetic-mechanism": {"development": 14, "validation": 5, "test": 5},
        "counterfactual-rediscovery": {"development": 10, "validation": 3, "test": 3},
        "open-ended-systemic": {"development": 18, "validation": 6, "test": 6},
        "preservation-no-change": {"development": 6, "validation": 2, "test": 2},
        "trigger-scope": {"development": 6, "validation": 2, "test": 2},
        "adversarial-high-stakes": {"development": 6, "validation": 2, "test": 2},
    }
```

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -v`

Expected: failure because `study/corpus-manifest.yaml` is absent.

- [ ] **Step 3: Create the exact manifest**

Add the allocation above plus required domain strata: public cases span at least eight domains; no single domain exceeds 20% of all cases; at least 20 cases contain hard preservation constraints; at least 15 contain stakeholder conflict; and Quick and Deep intents each appear in at least 20 public cases.

- [ ] **Step 4: Add the shared public-family loader fixture**

```python
from pathlib import Path
import pytest
import yaml
from systematic_innovation_bench.models import BenchmarkCase


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def load_public_family():
    def load(filename: str) -> list[BenchmarkCase]:
        path = ROOT / "cases/development" / filename
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        return [BenchmarkCase.model_validate(item) for item in payload["cases"]]
    return load
```

- [ ] **Step 5: Write the authoring guide**

Define one problem per case, natural prompts, testable constraints, causal-mechanism labeling, acceptable ambiguity, and prohibited leakage. Require an independent review for answerability, domain plausibility, cultural assumptions, harmful framing, accidental solution hints, near-duplicates, and contamination by skill terminology.

- [ ] **Step 6: Run and verify GREEN**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -v`

Expected: manifest test passes.

- [ ] **Step 7: Commit**

```bash
git add benchmark/study/corpus-manifest.yaml benchmark/study/authoring-guide.md benchmark/tests/conftest.py benchmark/tests/test_public_corpus.py
git commit -m "test: freeze benchmark corpus allocation"
```

### Task 2: Author the Fourteen Public Synthetic Mechanism-Space Cases

**Files:**

1. Create: `benchmark/cases/development/synthetic.yaml`
2. Modify: `benchmark/tests/test_public_corpus.py`

**Interfaces:**

1. Produces: Cases `syn-dev-001` through `syn-dev-014`.
2. Each case includes `id`, `family`, `domain`, `split`, `prompt`, `strata`, `expected_mode`, and `should_trigger` only; public files contain no hidden mechanisms.

- [ ] **Step 1: Add the failing family-count test**

```python
def test_synthetic_public_family_has_fourteen_safe_cases(load_public_family):
    cases = load_public_family("synthetic.yaml")
    assert len(cases) == 14
    assert [case.id for case in cases] == [f"syn-dev-{n:03d}" for n in range(1, 15)]
    assert all(case.family == "synthetic-mechanism" for case in cases)
    assert all(not case.hidden_mechanisms for case in cases)
```

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -k synthetic -v`

Expected: failure because the family file is absent.

- [ ] **Step 3: Author controlled mechanism spaces**

Create artificial but coherent systems whose feasible intervention families can be independently enumerated in the restricted scoring pack. Vary bottleneck location, information delay, incentive conflict, resource pooling, sequencing, modularity, feedback, and boundary ownership. Prompts must not name those mechanisms or imply a preferred method.

- [ ] **Step 4: Review for accidental hints and duplicates**

Have a reviewer see prompts without notes and predict likely mechanisms. Rewrite any case where the wording directly reveals more than one intended family or where two cases differ only by domain nouns.

- [ ] **Step 5: Run and verify GREEN**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -k synthetic -v`

Expected: all synthetic tests pass.

- [ ] **Step 6: Commit**

```bash
git add benchmark/cases/development/synthetic.yaml benchmark/tests/test_public_corpus.py
git commit -m "test: add public synthetic mechanism cases"
```

### Task 3: Author the Ten Public Counterfactual Rediscovery Cases

**Files:**

1. Create: `benchmark/cases/development/rediscovery.yaml`
2. Modify: `benchmark/tests/test_public_corpus.py`

**Interfaces:**

1. Produces: Cases `red-dev-001` through `red-dev-010`.
2. Restricted companion notes identify known solution mechanisms and acceptable functional equivalents; generators never receive them.

- [ ] **Step 1: Add a failing count and leakage test**

Require ten IDs, the `counterfactual-rediscovery` family, and reject public keys matching `gold`, `answer`, `known_solution`, `hidden_mechanisms`, or `source_url` with a non-empty value.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -k rediscovery -v`

Expected: failure because `rediscovery.yaml` is absent.

- [ ] **Step 3: Author historically grounded problem abstractions**

Describe the pre-solution state without distinctive names, dates, quotations, patents, or searchable phrasing. Preserve the causal constraints that make the known mechanism useful. Include healthcare only when the prompt asks for conceptual system alternatives and explicitly disallows clinical instructions.

- [ ] **Step 4: Perform an internet-search leakage review**

Search one distinctive sentence from each draft. Rewrite any case whose known solution appears directly in the first page of results. Record only pass/fail and review date publicly, never the hidden answer.

- [ ] **Step 5: Run and verify GREEN**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -k rediscovery -v`

Expected: all rediscovery tests pass.

- [ ] **Step 6: Commit**

```bash
git add benchmark/cases/development/rediscovery.yaml benchmark/tests/test_public_corpus.py
git commit -m "test: add counterfactual rediscovery cases"
```

### Task 4: Author the Eighteen Public Open-Ended Systemic Cases

**Files:**

1. Create: `benchmark/cases/development/open-ended.yaml`
2. Modify: `benchmark/tests/test_public_corpus.py`

**Interfaces:** Produces cases `sys-dev-001` through `sys-dev-018` across organizations, public services, education, software, logistics, sustainability, personal systems, and community settings.

- [ ] **Step 1: Add failing count, domain, and constraint tests**

Require eighteen unique IDs, at least seven domains, at least nine Deep intents, at least six explicit preservation constraints, and no prompt shorter than 35 words.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -k open_ended -v`

Expected: failure because `open-ended.yaml` is absent.

- [ ] **Step 3: Author the cases**

Each case must expose a system tension, at least two affected actors, and one non-negotiable constraint without prescribing a method. Mix process, incentive, information, timing, ownership, access, and trust problems.

- [ ] **Step 4: Conduct mechanism-blind peer review**

Reviewers label the likely intervention families elicited by each prompt. Replace cases that collapse to a single obvious answer or duplicate more than half of another case's predicted families.

- [ ] **Step 5: Run and verify GREEN**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -k open_ended -v`

Expected: all open-ended tests pass.

- [ ] **Step 6: Commit**

```bash
git add benchmark/cases/development/open-ended.yaml benchmark/tests/test_public_corpus.py
git commit -m "test: add open-ended systemic cases"
```

### Task 5: Author Preservation, Trigger, and Adversarial Families

**Files:**

1. Create: `benchmark/cases/development/preservation.yaml`
2. Create: `benchmark/cases/development/trigger.yaml`
3. Create: `benchmark/cases/development/adversarial.yaml`
4. Modify: `benchmark/tests/test_public_corpus.py`

**Interfaces:** Produces six cases per family with IDs `pre-dev-001..006`, `tri-dev-001..006`, and `adv-dev-001..006`.

- [ ] **Step 1: Add failing family and polarity tests**

Require six cases per file. The trigger set must contain two clear activations, two clear non-activations, and two boundary cases. The preservation set must contain at least two cases where “make no change” is a defensible possibility. All adversarial cases require an explicit safety or rights constraint.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -k 'preservation or trigger or adversarial' -v`

Expected: failures because the three files are absent.

- [ ] **Step 3: Author the preservation cases**

Test whether the system identifies what already works, recognizes change fatigue or fragility, and includes maintain, simplify, or stop options without becoming reflexively conservative.

- [ ] **Step 4: Author the trigger cases**

Include direct innovation requests, simple factual questions, implementation-only work, ambiguous “improve this” prompts, a named Provocation request, and a request that begins as ideation but asks for a full roadmap.

- [ ] **Step 5: Author the adversarial cases**

Cover clinical safety, employee surveillance, discriminatory eligibility, vulnerable users, public accountability, and ecological externalities. Score restraint and reframing; never reward instructions that bypass safeguards.

- [ ] **Step 6: Run and verify GREEN**

Run: `cd benchmark && uv run pytest tests/test_public_corpus.py -v`

Expected: all 60 public cases pass schema, allocation, uniqueness, domain, and leakage tests.

- [ ] **Step 7: Commit**

```bash
git add benchmark/cases/development benchmark/tests/test_public_corpus.py
git commit -m "test: complete public development corpus"
```

### Task 6: Define and Validate the Restricted Pack Without Publishing It

**Files:**

1. Create: `benchmark/study/restricted-pack.schema.json`
2. Create: `benchmark/src/systematic_innovation_bench/restricted.py`
3. Create: `benchmark/tests/test_restricted_pack.py`
4. Modify: `benchmark/tests/conftest.py`
5. Modify: `.gitignore`

**Interfaces:**

1. Consumes at run time: An absolute operator path containing `validation.yaml`, `test.yaml`, and `scoring.yaml`.
2. Produces: A content-free validation summary with counts, schema version, SHA-256 digest, and pass/fail status.

- [ ] **Step 1: Write failing private-pack tests with temporary fixtures**

```python
def test_pack_requires_exact_restricted_allocation(valid_restricted_pack):
    summary = validate_restricted_pack(valid_restricted_pack)
    assert summary.validation_count == 20
    assert summary.test_count == 20
    assert summary.family_counts == {
        "synthetic-mechanism": 10,
        "counterfactual-rediscovery": 6,
        "open-ended-systemic": 12,
        "preservation-no-change": 4,
        "trigger-scope": 4,
        "adversarial-high-stakes": 4,
    }


def test_validator_never_echoes_secret_content(invalid_restricted_pack, capsys):
    with pytest.raises(PackValidationError):
        validate_restricted_pack(invalid_restricted_pack)
    output = capsys.readouterr()
    assert "SECRET_PROMPT_SENTINEL" not in output.out + output.err
```

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_restricted_pack.py -v`

Expected: import failure because the schema and validator entry point are absent.

- [ ] **Step 3: Define the private contract**

Require unique IDs; exact split/family counts; prompts; case strata; protected gold mechanisms; acceptable functional equivalents; unsafe outputs; deterministic checks; provenance notes; and two independent reviewer approvals. Store only digests and counts in public run manifests.

- [ ] **Step 4: Implement content-free validation**

`validate_restricted_pack(path: Path) -> RestrictedPackSummary` must resolve the path, reject any location at or below the Git worktree, validate all records, calculate counts and SHA-256 digests from file bytes, and return only schema version, split counts, family counts, and digests. Exceptions may identify a file and structural field path but must never include a prompt, mechanism, note, or source value.

- [ ] **Step 5: Protect likely local paths**

Add `benchmark/private/`, `benchmark/restricted/`, `*.sealed.yaml`, and `*.validation.yaml` to `.gitignore`. Add a preflight that refuses a restricted path located inside the Git worktree, even when ignored.

- [ ] **Step 6: Run tests and a synthetic private-pack smoke test**

Run: `cd benchmark && uv run pytest tests/test_restricted_pack.py -v`

Expected: all tests pass and captured output contains no fixture secrets.

- [ ] **Step 7: Commit public contracts only**

```bash
git add .gitignore benchmark/study/restricted-pack.schema.json benchmark/src/systematic_innovation_bench/restricted.py benchmark/tests/conftest.py benchmark/tests/test_restricted_pack.py
git commit -m "test: protect restricted benchmark packs"
```

### Task 7: Preregister the Experiment and Statistical Decisions

**Files:**

1. Create: `benchmark/study/preregistration.yaml`
2. Create: `benchmark/study/analysis-plan.md`
3. Create: `benchmark/tests/test_preregistration.py`

**Interfaces:**

1. Produces: A machine-readable frozen study contract consumed by the runner.
2. Records: Candidate skill commit, runner commit, corpus digests, conditions, endpoints, exclusions, repetition rule, judge rule, cost ceilings, and release gates.

- [ ] **Step 1: Write the failing completeness test**

Require `study_id`, `status`, `candidate_commit`, `runner_commit`, `corpus_digests`, `primary_endpoint`, `secondary_endpoints`, `conditions`, `analysis_unit`, `bootstrap`, `missingness`, `exclusions`, `pilot_rule`, `judge_acceptance`, `budgets`, and `sealed_test_policy`. Require primary endpoint text to resolve exactly to `useful_distinct_mechanisms_per_1000_output_tokens`.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_preregistration.py -v`

Expected: failure because the preregistration is absent.

- [ ] **Step 3: Write the preregistration in draft status**

Declare the full skill versus format-matched control as the primary contrast. Keep vanilla, generic brainstorm, and established method as secondary contrasts. Limit ablations to development. State exclusions before results: transport failure after bounded retries, empty response, corrupted token accounting, or verified prompt leakage.

- [ ] **Step 4: Specify the analysis**

Aggregate repetitions within case and condition, compute paired case differences, and report median and mean effects with percentile and BCa bootstrap intervals over cases. Report family-level heterogeneity without turning exploratory slices into confirmatory claims. Correct secondary inferential comparisons with Holm's method. Treat judge abstentions and failures as missing with counts plus pessimistic sensitivity bounds.

- [ ] **Step 5: Define pilot-derived quantities without inventing numbers**

The development pilot computes variance, reliability, practical-effect threshold, equivalence margin, and repetitions required for stable case means. Freezing replaces the named derivation rules with their computed numeric values before validation begins; the test rejects `status: frozen` if any numeric value is absent.

- [ ] **Step 6: Run and verify GREEN in draft state**

Run: `cd benchmark && uv run pytest tests/test_preregistration.py -v`

Expected: completeness tests pass; freeze tests remain intentionally skipped until Task 9 produces pilot values.

- [ ] **Step 7: Commit**

```bash
git add benchmark/study/preregistration.yaml benchmark/study/analysis-plan.md benchmark/tests/test_preregistration.py
git commit -m "docs: preregister benchmark analysis"
```

### Task 8: Calibrate Human and LLM Judging Before Treatment Comparison

**Files:**

1. Create: `benchmark/study/human-calibration.md`
2. Modify: `benchmark/study/preregistration.yaml`

**Interfaces:**

1. Produces: An accepted judge prompt/version only if it reaches at least 75% pairwise agreement with humans and Krippendorff's alpha of at least 0.67 on anchored ratings.
2. Consumes: A stratified development-only calibration sample with treatment labels removed and answer order randomized.

- [ ] **Step 1: Add a failing acceptance-gate test**

Extend `test_preregistration.py` so `judge_acceptance` requires `pairwise_agreement_min: 0.75`, `krippendorff_alpha_min: 0.67`, at least two trained human annotators, adjudication rules, and an abstention label.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_preregistration.py -k judge -v`

Expected: failure until the gate and protocol exist.

- [ ] **Step 3: Write the calibration protocol**

Train annotators on mechanism identity versus surface variation, usefulness under constraints, unsafe novelty, and uncertainty. Double-code all calibration items, adjudicate only after independent labels are locked, and revise judge prompts using development items only.

- [ ] **Step 4: Run calibration rounds**

Use a minimum of 40 stratified answer pairs per round. Stop when both thresholds pass on a fresh development calibration slice or after three prompt revisions. If the gate still fails, use human scoring for the primary endpoint and retain LLM scores as exploratory.

- [ ] **Step 5: Preserve the calibration evidence**

Append raw blinded assignments, human labels, judge labels, disagreements, prompt version, and computed reliability to the run directory. Publish aggregate reliability and representative disagreement categories without exposing restricted content.

- [ ] **Step 6: Run and verify GREEN**

Run: `cd benchmark && uv run pytest tests/test_preregistration.py -v`

Expected: judge protocol tests pass.

- [ ] **Step 7: Commit**

```bash
git add benchmark/study/human-calibration.md benchmark/study/preregistration.yaml benchmark/tests/test_preregistration.py
git commit -m "docs: define judge calibration gate"
```

### Task 9: Run the Development Pilot and Freeze the Candidate

**Files:**

1. Create during execution: `benchmark/runs/$SIB_RUN_ID/manifest.json`
2. Create during execution: `benchmark/runs/$SIB_RUN_ID/records/*.jsonl`
3. Create during execution: `benchmark/runs/$SIB_RUN_ID/reports/development.md`
4. Modify: `benchmark/study/preregistration.yaml`

**Interfaces:** Uses all 60 public cases and all five main conditions; development-only ablations may run after the main pilot.

- [ ] **Step 1: Verify clean inputs and budget in dry-run mode**

Run:

```bash
cd benchmark
uv run sib plan --config configs/example.yaml --cases cases/development --preregistration study/preregistration.yaml --dry-run
```

Expected: exactly the preregistered development jobs, no network calls, no restricted paths, and an estimated call/token/cost summary below configured ceilings.

- [ ] **Step 2: Execute a small plumbing smoke test**

Run one case through each condition using the real external adapter. Inspect raw prompt construction, treatment blindness in judging, token counts, redaction, resume behavior, and failure classification. Discard these plumbing records from effect estimation and record their run ID.

- [ ] **Step 3: Execute the 60-case development pilot**

Start with two repetitions per positive-generation case and one activation observation per trigger-negative case. Use identical model version, decoding settings, and budgets across conditions. Resume rather than restart after interruption.

- [ ] **Step 4: Calibrate judging and score the pilot**

Apply Task 8. Cluster outputs into causal mechanisms before usefulness scoring. Preserve raw cluster labels, duplicate decisions, pairwise order, judge versions, and human overrides.

- [ ] **Step 5: Compute pilot-derived design values**

Use case-level variance and between-repetition instability to select the smallest repetition count that makes the median case's endpoint standard error no more than 20% of the preregistered practical-effect threshold, subject to the budget ceiling. Calculate and freeze the practical-effect and equivalence margins from the preregistered development quantiles.

- [ ] **Step 6: Diagnose and revise using development only**

Inspect failures by family, safety, verbosity, duplicate mechanisms, and cost. Skill revisions are allowed only on the candidate branch and require rerunning the full development comparison under a new version. Never inspect validation or sealed outputs while revising.

- [ ] **Step 7: Freeze the candidate and preregistration**

Record immutable Git commit IDs, model identifiers, adapter versions, prompt hashes, corpus digest, numeric repetition count, margins, judge version, and budgets. Set `status: frozen`; tag the candidate `systematic-innovation-benchmark-candidate-v1`.

- [ ] **Step 8: Run freeze verification and commit**

```bash
cd benchmark
uv run pytest tests/test_preregistration.py -v
git add study/preregistration.yaml
git commit -m "docs: freeze benchmark candidate and analysis"
```

Expected: no skipped freeze checks and all tests pass.

### Task 10: Run Restricted Validation as a Single Tuning Gate

**Files:** Runtime artifacts only under `benchmark/runs/$SIB_RUN_ID/`; no restricted case files are added to Git.

**Interfaces:** Consumes the 20-case validation pack by absolute path and the frozen candidate tag.

- [ ] **Step 1: Validate without printing content**

Run: `uv run sib validate-pack --restricted-pack /absolute/operator/path --split validation`

Expected: 20 cases, exact family allocation, digest output, and no prompts or gold mechanisms in stdout, stderr, or logs.

- [ ] **Step 2: Verify the frozen environment**

Checkout the candidate tag in a clean worktree, pin the recorded model and adapter versions, verify no uncommitted changes, and compare all public and private digests with the preregistration.

- [ ] **Step 3: Execute and score validation**

Use the frozen repetition count and judge. Do not expose interim condition effects. Produce the preregistered primary contrast, secondary contrasts, safety counts, cost, latency, failures, and reliability.

- [ ] **Step 4: Apply the release gate**

Proceed only if the primary endpoint interval excludes the preregistered harmful-effect boundary, safety non-inferiority passes, and no critical leakage or execution-integrity event occurred. A failed gate returns development to a new candidate version; it does not authorize repeated probing of the same validation pack.

- [ ] **Step 5: Publish a content-free validation decision**

Record candidate digest, pack digest, run digest, gate outcome, exclusions, and deviations. Do not publish case-level restricted results.

### Task 11: Execute the Sealed Test Once and Write the Final Report

**Files:**

1. Create: `benchmark/runs/$SIB_RUN_ID/reports/final.md`
2. Create: `benchmark/runs/$SIB_RUN_ID/reports/reproducibility.json`
3. Create: `benchmark/study/release-gates.md`

**Interfaces:** Consumes the 20 sealed cases only after validation passes and the candidate remains unchanged.

- [ ] **Step 1: Write the ordered release gates**

Document: public development complete; judge accepted or human-primary fallback declared; preregistration frozen; validation gate passed; candidate digest unchanged; sealed pack digest verified; budget authorized; and operator approval recorded.

- [ ] **Step 2: Validate sealed pack structure without content output**

Run: `uv run sib validate-pack --restricted-pack /absolute/operator/path --split test`

Expected: 20 sealed cases and exact allocation.

- [ ] **Step 3: Execute the sealed study once**

Run the frozen five conditions at the frozen repetition count. If infrastructure fails before 10% of jobs complete, correct infrastructure without inspecting effects and restart under a new run ID. Otherwise resume the same run; do not regenerate successful jobs.

- [ ] **Step 4: Generate the final report**

Lead with the exact construct: systematic ideation performance. Report paired case-level estimates and intervals, raw endpoint distributions, family heterogeneity, activation accuracy, safety/restraint, preservation awareness, verbosity, cost, latency, failures, judge reliability, exclusions, deviations, and negative findings. Never call benchmark success proof of market innovation.

- [ ] **Step 5: Create the reproducibility record**

Include repository commit, candidate tag, Python lock digest, public corpus digest, restricted pack digests, model and host versions, adapter command digest, generation settings, judge prompt/version digest, random seeds, run IDs, and report digest.

- [ ] **Step 6: Verify and commit public report artifacts**

Run:

```bash
cd benchmark
uv run pytest -q
uv run ruff check .
uv run mypy src
uv run sib verify-run "runs/$SIB_RUN_ID"
```

Commit only redacted aggregate reports and reproducibility metadata; keep raw restricted records in controlled storage.

### Task 12: Create the External Loop-Engineering Handoff

**Files:**

1. Create: `benchmark/study/LOOP-HANDOFF.md`
2. Modify: `benchmark/README.md`

**Interfaces:** Gives another coding agent or orchestration tool an exact, provider-neutral protocol for planning, executing, resuming, scoring, comparing, and stopping benchmark iterations.

- [ ] **Step 1: Write a failing documentation-contract test**

Add a test requiring the handoff to contain exact commands for `validate`, `plan --dry-run`, `run`, `resume`, `score`, `report`, `verify-run`, and `compare`; environment inputs; allowed write paths; stop conditions; failure escalation; branch/version rules; and restricted-data prohibitions.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_cli_integration.py -k handoff -v`

Expected: failure because the handoff is absent.

- [ ] **Step 3: Write the loop state machine**

Use these states: `PREFLIGHT`, `DRY_RUN`, `EXECUTE`, `SCORE`, `COMPARE`, `DECIDE`, `FREEZE`, and `STOP`. A development candidate may advance only after complete evidence and tests. Validation can return a decision but never candidate edits. Sealed test always transitions to `STOP`.

- [ ] **Step 4: Define iteration and stop rules**

Each candidate uses a new Git branch, semantic candidate ID, and complete development run. Stop when any of these occurs: candidate meets the frozen practical-effect and safety gates; three consecutive candidates improve less than the equivalence margin; budget reaches 90%; judge calibration fails after three revisions; data leakage occurs; or the maximum of ten development candidates is reached.

- [ ] **Step 5: Define the 100-case execution command sequence**

Document absolute-path parameters without embedding secrets:

```bash
uv run sib validate --config /absolute/path/config.yaml
uv run sib plan --config /absolute/path/config.yaml --cases cases/development --dry-run
uv run sib run --config /absolute/path/config.yaml --cases cases/development
uv run sib resume --run-id "$SIB_RUN_ID"
uv run sib score --run-id "$SIB_RUN_ID"
uv run sib report --run-id "$SIB_RUN_ID"
uv run sib compare --baseline "$SIB_BASELINE_RUN_ID" --candidate "$SIB_CANDIDATE_RUN_ID"
uv run sib verify-run "runs/$SIB_RUN_ID"
```

Define `SIB_RUN_ID`, `SIB_BASELINE_RUN_ID`, and `SIB_CANDIDATE_RUN_ID` from the machine-readable identifiers emitted by immediately preceding commands. The handoff must validate that each variable is non-empty before invoking a mutating command.

- [ ] **Step 6: Define operator checkpoints**

Require explicit human authorization before any restricted validation run, before sealed-test access, and before publication. Infrastructure retries, development resumes, and report regeneration need no checkpoint when they remain within frozen budgets and inputs.

- [ ] **Step 7: Run and verify GREEN**

Run:

```bash
cd benchmark
uv run pytest -q
uv run ruff check .
uv run mypy src
git diff --check
```

Expected: all tests and static checks pass.

- [ ] **Step 8: Commit**

```bash
git add benchmark/study/LOOP-HANDOFF.md benchmark/README.md benchmark/tests/test_cli_integration.py
git commit -m "docs: add benchmark loop handoff"
```

### Task 13: Run Cross-Agent Installation and Activation as Separate Studies

**Files:**

1. Create: `benchmark/study/integration-matrix.yaml`
2. Create: `benchmark/study/cross-agent-study.md`
3. Modify: `benchmark/tests/test_preregistration.py`

**Interfaces:** Separates format compatibility, installation, explicit invocation, automatic activation, and generated-output behavior so success in one cannot be reported as success in another.

- [ ] **Step 1: Write a failing claim-separation test**

Require each matrix entry to contain `agent_family`, `host`, `host_version`, `model_family`, `installation_status`, `explicit_invocation`, `automatic_activation`, `behavior_run_id`, `tested_at`, and `limitations`. Reject the broad claim level unless at least three distinct agent or model families have completed behavior tests.

- [ ] **Step 2: Run and verify RED**

Run: `cd benchmark && uv run pytest tests/test_preregistration.py -k cross_agent -v`

Expected: failure because the matrix and study protocol are absent.

- [ ] **Step 3: Write the separate-study protocol**

For each host, first verify installation without behavior claims. Then test valid explicit invocation cases and require 100% activation. Finally run held-out automatic trigger cases without naming the skill and calculate precision and recall. Only after those studies pass should the same host enter an output-quality behavior sample.

- [ ] **Step 4: Test at least three distinct families**

Select hosts based on actual availability; do not hard-code brand support into the skill. Use the same held-out trigger distribution and record host/model version, settings, availability limitations, and exact result run ID. A format-compatible but unavailable host remains `format-compatible`, not `installation-tested` or `behavior-tested`.

- [ ] **Step 5: Apply claim thresholds**

Per behavior-tested host, require automatic activation precision of at least 0.90, recall of at least 0.85, and correct explicit invocation in every valid case. Report host-specific failures even when pooled performance passes.

- [ ] **Step 6: Keep these results out of the primary effect estimate**

The 100-case primary study uses explicit, controlled condition assignment. Cross-agent installation and activation results receive their own tables and cannot alter the preregistered primary endpoint or sealed-test decision.

- [ ] **Step 7: Verify and commit**

```bash
cd benchmark
uv run pytest tests/test_preregistration.py -v
cd ..
git add benchmark/study/integration-matrix.yaml benchmark/study/cross-agent-study.md benchmark/tests/test_preregistration.py
git commit -m "test: separate cross-agent compatibility claims"
```

---

## Final Study Acceptance Checklist

- [ ] Public development corpus contains exactly 60 schema-valid, non-duplicate cases with the fixed family allocation.
- [ ] Restricted validation and sealed packs contain exactly 20 cases each and remain outside the Git worktree.
- [ ] All five main conditions are frozen; ablations are development-only.
- [ ] The primary endpoint and paired case-level analysis were frozen before validation.
- [ ] Repetition count, practical-effect threshold, and equivalence margin came from the declared development procedure.
- [ ] Judge calibration passed both thresholds or the preregistered human-primary fallback was used.
- [ ] Validation ran once as a gate and the sealed test ran once after candidate freeze.
- [ ] Raw evidence is append-only, redacted, budget-bounded, and resumable.
- [ ] Reports disclose quality, safety, efficiency, failures, disagreement, deviations, and null or negative results.
- [ ] Claims say “systematic ideation performance,” never “proven innovation.”
- [ ] The external handoff can run without provider-specific SDKs or access to hidden repository content.
- [ ] Installation, activation, host integration, and output-quality claims remain separate and at least three families are behavior-tested before any broad cross-agent claim.
