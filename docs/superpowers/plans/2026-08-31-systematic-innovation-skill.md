# Systematic Innovation Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and behaviorally validate the provider-neutral `systematic-innovation` Agent Skill from a preserved no-skill baseline.

**Architecture:** The installable skill lives under `skills/systematic-innovation/` and contains a concise router plus four conditional references. A small standard-library validator checks structure and portability. Behavioral RED and GREEN outputs are preserved separately from the skill so the instructions are written in response to observed failures rather than intuition alone.

**Tech Stack:** Open Agent Skills Markdown, CPython 3.13 standard library with 3.11-3.14 compatibility, `unittest`, JSON, Git

**Spec:** `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md` and `docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md`

**Contract Alignment:** Both specifications are approved and authoritative within their scopes. This plan executes them and does not amend or supersede either contract.

## Global Constraints

1. The canonical skill name is `systematic-innovation`.
2. The skill must follow the open Agent Skills specification.
3. The skill must work without web access, subagents, structured input tools, or proprietary commands.
4. Quick mode targets 10 to 15 distinct possibilities; Deep mode targets 15 to 24 and asks no more than seven questions.
5. Outputs are called innovation possibilities, not completed innovations.
6. The Perspective Council is a user-facing label; its behavior is implemented through explicit Reasoning Cells.
7. The skill provides light decision support but no winner, roadmap, tasks, experiments, budgets, or rollout unless explicitly requested.
8. Verified principles, adapted methods, and original AI mechanisms remain distinct.
9. No copyrighted book text or unverified Rickards framework names may be shipped.
10. No skill content is written before the no-skill baseline has been run and reviewed.
11. Behavioral tests score observable output, not hidden reasoning or exact prose.
12. Deep scenarios use a fixed multi-turn disclosure script shared by baseline and treatment; Quick scenarios remain single-turn.
13. A mechanism is counted as useful only after minimum relevance, constraint alignment, causal clarity, plausibility, and safety gates pass.
14. Every task uses RED, GREEN, REFACTOR and ends in a focused commit.

---

## Planned File Map

| File | Responsibility |
| --- | --- |
| `evals/pilot/cases.json` | Twelve realistic baseline and treatment scenarios |
| `evals/pilot/rubric.md` | Observable behavior rubric shared by RED and GREEN runs |
| `evals/pilot/runbook.md` | Fresh-context execution and result-capture procedure |
| `evals/pilot/results/baseline.jsonl` | Append-only no-skill outputs |
| `evals/pilot/results/treatment.jsonl` | Append-only skill-enabled outputs |
| `evals/pilot/baseline-analysis.md` | Observed failures that justify skill guidance |
| `evals/triggers/cases.json` | Should-trigger, should-not-trigger, and boundary prompts |
| `skills/systematic-innovation/SKILL.md` | Discovery metadata, routing, core loop, and invariants |
| `skills/systematic-innovation/references/innovation-lenses.md` | Reasoning Cells, operators, and mechanism ledger |
| `skills/systematic-innovation/references/deep-mode.md` | Progressive questioning and Deep mode behavior |
| `skills/systematic-innovation/references/output-contract.md` | Portfolio, saturation, receptivity, and decision support |
| `skills/systematic-innovation/references/evidence.md` | Provenance classes, verified claims, limitations, and sources |
| `tools/validate_skill.py` | Structure, frontmatter, reference, and portability validation |
| `tests/__init__.py` | Makes standard-library test modules directly importable |
| `tests/test_pilot_manifest.py` | Pilot corpus validation |
| `tests/test_skill_structure.py` | Skill package and frontmatter validation |
| `tests/test_skill_references.py` | Relative-reference and evidence checks |
| `tests/test_skill_portability.py` | Proprietary dependency and executable-script checks |
| `README.md` | Public value proposition, local installation, usage, and evidence limits |
| `SECURITY.md` | Skill review and reporting guidance |
| `LICENSE` | MIT license |

### Task 1: Create and Validate the RED Pilot Corpus

**Files:**

1. Create: `evals/pilot/cases.json`
2. Create: `evals/pilot/rubric.md`
3. Create: `evals/pilot/runbook.md`
4. Create: `tests/__init__.py`
5. Create: `tests/test_pilot_manifest.py`

**Interfaces:**

1. Consumes: The domains, modes, boundaries, and failure modes in the approved specification.
2. Produces: `cases.json` containing objects with `id`, `domain`, `prompt`, `expected_mode`, `interaction_mode`, `user_turns`, `should_trigger`, and `target_failures`.

- [ ] **Step 1: Write the failing pilot-manifest test**

```python
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PilotManifestTests(unittest.TestCase):
    def test_pilot_has_twelve_unique_cross_domain_cases(self):
        path = ROOT / "evals/pilot/cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        self.assertEqual(len(cases), 12)
        self.assertEqual(len({case["id"] for case in cases}), 12)
        self.assertGreaterEqual(len({case["domain"] for case in cases}), 7)
        self.assertTrue(any(case["expected_mode"] == "quick" for case in cases))
        self.assertTrue(any(case["expected_mode"] == "deep" for case in cases))
        self.assertTrue(any(not case["should_trigger"] for case in cases))

    def test_every_case_declares_observable_failure_targets(self):
        path = ROOT / "evals/pilot/cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        for case in cases:
            self.assertTrue(case["prompt"].strip(), case["id"])
            self.assertGreaterEqual(len(case["target_failures"]), 2, case["id"])

    def test_deep_cases_have_controlled_multi_turn_scripts(self):
        path = ROOT / "evals/pilot/cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        for case in cases:
            if case["expected_mode"] == "deep":
                self.assertEqual(case["interaction_mode"], "controlled-multi-turn")
                self.assertEqual(len(case["user_turns"]), 2)
                self.assertIn("Produce your final portfolio", case["user_turns"][-1])
            else:
                self.assertEqual(case["interaction_mode"], "single-turn")
                self.assertEqual(case["user_turns"], [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify RED**

Run: `python -m unittest tests.test_pilot_manifest -v`

Expected: `ERROR` because `evals/pilot/cases.json` does not exist.

- [ ] **Step 3: Create the twelve cases**

Use these exact scenario intents and natural-language prompts:

1. `retail-retention`: “Our furniture store sells well, but strong salespeople stop sharing information because commission rewards individual performance. Help me find innovative ways to improve teamwork without removing commission.” Expected mode: Deep.
2. `permit-wait`: “A city wants to reduce small-business permit wait times while preserving safety review and public accountability. Generate meaningfully different approaches.” Expected mode: Deep.
3. `ignored-reminders`: “Users keep ignoring our medication reminder app. Give me fresh ideas that are not just more notifications, badges, or AI personalization.” Expected mode: Quick with high-stakes restraint.
4. `release-bottleneck`: “A software team releases once every eight weeks because testing, compliance, and operations sign-off happen sequentially. Brainstorm systemic alternatives.” Expected mode: Deep.
5. `teacher-fatigue`: “Teachers are exhausted by disconnected innovation initiatives. How could a school district improve student support without launching another burdensome program?” Expected mode: Deep with preservation.
6. `food-bank-mismatch`: “Our food bank receives plenty of donations, but not the items families need when they need them. We have almost no technology budget.” Expected mode: Quick.
7. `meal-planning`: “I keep buying groceries with good intentions and wasting food by the end of the week. Help me invent a better personal system.” Expected mode: Quick.
8. `warehouse-returns`: “Returned products sit for weeks before anyone decides whether to restock, repair, discount, or discard them. Find non-obvious operational models.” Expected mode: Quick.
9. `library-access`: “A rural library wants to expand access for people who cannot visit during opening hours, but it cannot hire more staff or weaken privacy.” Expected mode: Deep.
10. `provocation`: “Use Provocation mode on the assumption that a customer-support department must answer every customer question itself.” Expected mode: Quick plus Contrarian and Boundary Reframing.
11. `fact-lookup`: “What is the difference between sustaining and disruptive innovation?” Expected mode: none; should not trigger.
12. `implementation-only`: “We selected a self-service returns portal. Create the implementation tickets and database schema.” Expected mode: none; should not trigger.

Assign at least two `target_failures` per case from: `genericity`, `duplicate_mechanisms`, `missing_preservation`, `missing_system_map`, `premature_winner`, `implementation_drift`, `unsafe_provocation`, `question_overload`, `false_attribution`, and `incorrect_trigger`.

Set Quick and trigger-negative cases to `interaction_mode: single-turn` with an empty `user_turns` array. Set the five Deep cases to `interaction_mode: controlled-multi-turn` and use these exact two follow-up disclosures after the first and second assistant turns, regardless of whether the assistant asks questions:

1. `retail-retention`: “Additional context: customer ownership and individual accountability are valuable and must remain. The main failures are hoarded product knowledge, weak handoffs on days off, and resentment when one person helps another close.” Then: “Final context: managers can change team routines and recognition, but cannot remove commission or add substantial payroll. Produce your final portfolio now using all available information.”
2. `permit-wait`: “Additional context: applicants repeat the same information across departments, while reviewers discover missing evidence late. Safety specialists are scarce and elected officials require an auditable decision trail.” Then: “Final context: the city can change sequencing, intake, triage, and information flow, but statutory reviews and public records must remain. Produce your final portfolio now using all available information.”
3. `release-bottleneck`: “Additional context: the same evidence is recreated for testing, compliance, and operations. Most releases are low risk, but every release follows the process designed for the highest-risk change.” Then: “Final context: the team may redesign evidence, sequencing, ownership, and release boundaries, but cannot bypass mandatory controls. Produce your final portfolio now using all available information.”
4. `teacher-fatigue`: “Additional context: teachers value peer support and local discretion. Previous programs added reporting and meetings but rarely removed older work.” Then: “Final context: the district has no new permanent staff budget and must preserve safeguarding and equitable student access. Produce your final portfolio now using all available information.”
5. `library-access`: “Additional context: many affected residents have unreliable internet, limited transport, or shift work. Staff already handle outreach informally, which creates inconsistent service and burnout.” Then: “Final context: the library can change partnerships, scheduling, service boundaries, and circulation models, but cannot weaken patron privacy or add permanent staff. Produce your final portfolio now using all available information.”

- [ ] **Step 4: Write the rubric and runbook**

The rubric must define 0-to-3 anchored ratings for mechanism diversity, domain specificity, constraint relevance, system awareness, preservation awareness, uncertainty honesty, decision restraint, and usability. It must define a duplicate as the same causal mechanism presented with changed nouns or surface features. Before a mechanism contributes to any useful-mechanism count, require relevance at least 2, constraint alignment at least 2, causal clarity at least 2, plausibility at least 1, and no critical safety or rights violation. Preserve raw distinct-mechanism count separately.

The runbook must require fresh contexts, identical prompt and follow-up sequences, raw turn-by-turn preservation, no skill or creativity preamble in RED, model and host metadata, and two pilot repetitions per trigger-positive case. Trigger-negative cases run once. For controlled multi-turn cases, send the two scripted user disclosures after the first two assistant turns even if the assistant already proposes ideas; score the final assistant portfolio, but record total assistant output tokens across every turn.

- [ ] **Step 5: Run the test and verify GREEN**

Run: `python -m unittest tests.test_pilot_manifest -v`

Expected: three tests pass.

- [ ] **Step 6: Commit the corpus**

```bash
git add evals/pilot tests/__init__.py tests/test_pilot_manifest.py
git commit -m "test: define systematic innovation pilot cases"
```

### Task 2: Run and Preserve the No-Skill RED Baseline

**Files:**

1. Create: `evals/pilot/results/baseline.jsonl`
2. Create: `evals/pilot/baseline-analysis.md`

**Interfaces:**

1. Consumes: `evals/pilot/cases.json`, `evals/pilot/rubric.md`, and `evals/pilot/runbook.md`.
2. Produces: One JSON object per run with `case_id`, `condition`, `replicate`, `host`, `model`, `interaction_mode`, ordered `turns`, `final_response`, `total_assistant_output_tokens`, `ratings`, and `notes`.

- [ ] **Step 1: Add an empty-result validation test**

Extend `tests/test_pilot_manifest.py` with a test requiring every trigger-positive case to have two `vanilla` baseline records and every trigger-negative case to have one activation observation.

- [ ] **Step 2: Run the test and verify RED**

Run: `python -m unittest tests.test_pilot_manifest.PilotManifestTests.test_baseline_results_cover_all_cases -v`

Expected: `FAIL` because `baseline.jsonl` is absent.

- [ ] **Step 3: Run the baseline in fresh contexts**

For each trigger-positive case, dispatch two fresh no-skill runs using exactly the declared single-turn or controlled multi-turn script. For each trigger-negative case, record whether the host attempted to invoke an innovation workflow without explicitly installing this skill. Do not provide the rubric, gates, or intended answer to generators.

- [ ] **Step 4: Score observable behavior**

Read each complete transcript and assign rubric ratings with evidence excerpts no longer than one sentence. Extract mechanisms from the final portfolio, apply the minimum quality gates to each candidate mechanism, and then deduplicate qualifying mechanisms by causal family. Record raw and qualifying counts separately.

- [ ] **Step 5: Write the failure analysis**

`baseline-analysis.md` must report observed failures by case and aggregate category. It must quote the actual rationalizations or generic patterns that the skill needs to correct. Do not add hypothetical rules for failures that did not occur.

- [ ] **Step 6: Run the coverage test and verify GREEN**

Run: `python -m unittest tests.test_pilot_manifest -v`

Expected: all pilot tests pass.

- [ ] **Step 7: Commit the RED evidence**

```bash
git add evals/pilot/results/baseline.jsonl evals/pilot/baseline-analysis.md tests/test_pilot_manifest.py
git commit -m "test: capture no-skill ideation baseline"
```

### Task 3: Build the Skill Package Validator

**Files:**

1. Create: `tools/validate_skill.py`
2. Create: `tests/test_skill_structure.py`
3. Create: `tests/test_skill_references.py`
4. Create: `tests/test_skill_portability.py`

**Interfaces:**

1. Produces: `validate_skill(path: Path) -> list[str]` and a CLI returning zero only when no errors exist.
2. Consumes later: `skills/systematic-innovation/`.

- [ ] **Step 1: Write failing structure tests**

Test that the package contains `SKILL.md`, exactly the four specified references, valid YAML-like frontmatter with `name` and `description`, a lowercase hyphenated name no longer than 64 characters, and a description no longer than 1,024 characters.

- [ ] **Step 2: Write failing reference and portability tests**

Test that every Markdown link to `references/*.md` resolves, no reference escapes the skill folder, there are no executable files inside the skill, and required behavior does not mention provider-specific commands such as `claude`, `codex`, `cursor`, `antigravity`, or `pi`.

- [ ] **Step 3: Run tests and verify RED**

Run: `python -m unittest tests.test_skill_structure tests.test_skill_references tests.test_skill_portability -v`

Expected: failures because the validator and skill package do not exist.

- [ ] **Step 4: Implement the minimal validator**

```python
from pathlib import Path
import re
import sys


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    _, block, _ = text.split("---\n", 2)
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    skill_md = path / "SKILL.md"
    if not skill_md.is_file():
        return ["SKILL.md is missing"]
    text = skill_md.read_text(encoding="utf-8")
    fields = parse_frontmatter(text)
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append("invalid skill name")
    if not description or len(description) > 1024:
        errors.append("invalid description")
    return errors


def main(argv: list[str]) -> int:
    errors = validate_skill(Path(argv[1]))
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

Extend this implementation only enough to satisfy the written reference and portability tests.

- [ ] **Step 5: Run the tests**

Run: `python -m unittest tests.test_skill_structure tests.test_skill_references tests.test_skill_portability -v`

Expected: validator unit tests pass; package-presence tests still fail for the expected missing package.

- [ ] **Step 6: Commit the validator**

```bash
git add tools/validate_skill.py tests/test_skill_structure.py tests/test_skill_references.py tests/test_skill_portability.py
git commit -m "test: add portable skill package validator"
```

### Task 4: Write the Minimal Skill from Observed Baseline Failures

**Files:**

1. Create: `skills/systematic-innovation/SKILL.md`
2. Create: `skills/systematic-innovation/references/innovation-lenses.md`
3. Create: `skills/systematic-innovation/references/deep-mode.md`
4. Create: `skills/systematic-innovation/references/output-contract.md`
5. Create: `skills/systematic-innovation/references/evidence.md`

**Interfaces:**

1. Consumes: `evals/pilot/baseline-analysis.md` and the approved specification.
2. Produces: A standards-compliant skill with relative reference links and no runtime dependencies.

- [ ] **Step 1: Run the package tests and confirm RED**

Run: `python -m unittest tests.test_skill_structure tests.test_skill_references tests.test_skill_portability -v`

Expected: package-presence and content tests fail.

- [ ] **Step 2: Write `SKILL.md`**

Use frontmatter with `name: systematic-innovation`. Write a concise trigger description based on user intent, not workflow summary. The body must contain:

1. The core principle that possibilities must differ by mechanism and connect to meaningful change.
2. Quick versus Deep observable routing.
3. User overrides.
4. The Innovation Brief fields.
5. The system and preservation scan.
6. Reasoning Cell selection rules.
7. Mechanism-ledger distinctiveness rules.
8. Saturation behavior.
9. Ideation-only and high-stakes boundaries.
10. Conditional links to each reference explaining when to read it.

Keep detailed cell operators, Deep questions, portfolio templates, and evidence tables in references. Add explicit counters only for failures documented in `baseline-analysis.md`.

- [ ] **Step 3: Write `innovation-lenses.md`**

Define the seven Reasoning Cells, ten lenses (including multiple redefinition across analytic, empathic, motivational, metaphorical, and boundary-relaxed modes, and synectic excursions), initial fluency depletion (discarding top-of-mind memory-dump tropes before ledger entry), cell output contract, parallel and sequential fallback, mechanism-ledger fields, structural dimensions, duplicate test, cross-pollination, and Provocation boundaries.

- [ ] **Step 4: Write `deep-mode.md`**

Define the question-value test, up-to-seven limit, contrasting provisional seeds, stopping rule, ambiguous and contested challenge handling, and no-question behavior when the user says to skip questions.

- [ ] **Step 5: Write `output-contract.md`**

Define the six disclosure layers, Quick and Deep quantity targets, saturation stop, portfolio tags as non-quotas, spotlight signals, receptivity notes (including Rickards's three problem-owner questions, mission-orientated versus negotiative versus participative boundary modes, and *Yes-but* inoculation), and prohibited implementation drift.

- [ ] **Step 6: Write `evidence.md`**

Create separate tables for verified principles, adapted methods, and original AI mechanisms. Include the verified nine-chapter bibliographic structure and figures of Rickards (1985), *Stimulating Innovation: A Systems Approach* (Frances Pinter, London, `pp. xi + 221`, ISBN `0-86187-512-5`), and source links from section 31 of the specification. Explicitly mark reconstructed Rickards framework names and the twelve-chapter table as unverified and excluded.

- [ ] **Step 7: Run validation and verify GREEN**

Run:

```bash
python tools/validate_skill.py skills/systematic-innovation
python -m unittest tests.test_skill_structure tests.test_skill_references tests.test_skill_portability -v
```

Expected: exit zero and all tests pass.

- [ ] **Step 8: Commit the minimal skill**

```bash
git add skills/systematic-innovation
git commit -m "feat: add systematic innovation skill"
```

### Task 5: Run GREEN Behavioral Scenarios and Refine Narrowly

**Files:**

1. Create: `evals/pilot/results/treatment.jsonl`
2. Create: `evals/pilot/treatment-analysis.md`
3. Modify only as evidence requires: `skills/systematic-innovation/*.md`

**Interfaces:**

1. Consumes: The same cases, models, hosts, and rubric as RED.
2. Produces: Paired baseline/treatment evidence and documented skill corrections.

- [ ] **Step 1: Run every positive case with the skill**

Use fresh contexts, identical scripted user turns, and the same replicate counts. Explicitly invoke the skill so this task measures behavior rather than discovery.

- [ ] **Step 2: Run negative cases without explicit invocation**

Record whether the installed skill activates incorrectly.

- [ ] **Step 3: Score and compare**

Use the original rubric. Record mechanism families, genericity, preservation, system awareness, implementation drift, question count, output length, and observed failures.

- [ ] **Step 4: Write treatment analysis**

For every skill change proposed, cite the failing case and observed behavior. If a baseline failure disappeared, do not add more guidance for it.

- [ ] **Step 5: Apply the smallest supported corrections**

Modify only the sections associated with observed treatment failures. Re-run the affected cases at least twice in fresh contexts and preserve the new records with a revision identifier.

- [ ] **Step 6: Run structural tests**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 7: Commit behavioral evidence and corrections**

```bash
git add evals/pilot skills/systematic-innovation
git commit -m "test: refine skill from behavioral evaluations"
```

### Task 6: Optimize Automatic Triggering

**Files:**

1. Create: `evals/triggers/cases.json`
2. Create: `evals/triggers/results.jsonl`
3. Modify: `skills/systematic-innovation/SKILL.md`
4. Create: `tests/test_trigger_manifest.py`

**Interfaces:**

1. Produces: 20 should-trigger, 20 should-not-trigger, and at least 10 boundary cases.
2. Consumes: Automatic discovery behavior from the current host and later host-integration studies.

- [ ] **Step 1: Write the trigger-manifest test**

Require unique IDs, at least 50 cases, balanced positive and negative classes, at least 10 boundary cases, and prompts that include both explicit innovation language and indirect user intent.

- [ ] **Step 2: Run the test and verify RED**

Run: `python -m unittest tests.test_trigger_manifest -v`

Expected: failure because the manifest is absent.

- [ ] **Step 3: Write the trigger cases**

Cover ideation, opportunity discovery, persistent problems, assumption challenge, selected-solution implementation, debugging, fact lookup, writing variation, option comparison, and roadmap execution. Include near-boundary prompts such as “Improve this architecture” where ideation intent depends on context.

- [ ] **Step 4: Run a no-guidance control and five fresh samples per description variant**

Record automatic activation. Test the current description, one narrower variant, and one broader variant. Randomize case order and preserve every observation.

- [ ] **Step 5: Select the shortest description meeting the evidence**

Prefer the description with the best held-out balance. Do not include workflow steps in frontmatter. The release study later requires at least 0.90 precision and 0.85 recall per behavior-tested host.

- [ ] **Step 6: Run all tests and commit**

```bash
python -m unittest discover -s tests -v
git add evals/triggers skills/systematic-innovation/SKILL.md tests/test_trigger_manifest.py
git commit -m "test: optimize systematic innovation discovery"
```

### Task 7: Add Public Documentation and Local Installation Checks

**Files:**

1. Create: `README.md`
2. Create: `SECURITY.md`
3. Create: `LICENSE`
4. Modify: `tests/test_skill_portability.py`

**Interfaces:**

1. Produces: Public project explanation and verified local installation instructions.
2. Does not publish a remote installation command until a repository URL exists and is tested.

- [ ] **Step 1: Add failing documentation tests**

Require README sections for value proposition, Quick and Deep examples, installation from the local repository, supported standard, methodology, evidence limits, and benchmarking status. Require MIT license text and a security-reporting document.

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_skill_portability -v`

Expected: documentation tests fail.

- [ ] **Step 3: Write README**

Lead with: ordinary AI brainstorming often produces variations of the obvious; this skill uses system mapping, explicit reasoning transformations, and mechanism tracking to produce a diverse possibility portfolio. Document local installation using the current Skills CLI only after verifying the exact command against `.`. Include direct Markdown loading as the fallback.

- [ ] **Step 4: Add license and security guidance**

Use the MIT license. `SECURITY.md` must tell users to inspect third-party skill content before installation, report false attribution and unsafe behavior, and avoid placing credentials in prompts or benchmark results.

- [ ] **Step 5: Verify local installation**

Run the current Skills CLI in dry-run or local-source mode against this repository. Record the exact successful command in README. Verify that only `skills/systematic-innovation/` is installed.

- [ ] **Step 6: Run tests and commit**

```bash
python -m unittest discover -s tests -v
git add README.md SECURITY.md LICENSE tests/test_skill_portability.py
git commit -m "docs: document portable skill installation"
```

### Task 8: Candidate Skill Verification Gate

**Files:**

1. Create: `evals/pilot/candidate-report.md`
2. Modify only if verification fails: skill, tests, or pilot evidence files.

**Interfaces:**

1. Produces: A candidate skill ready for the benchmark-runner plan.
2. Does not claim final release validation before the audited study plan passes.

- [ ] **Step 1: Run all deterministic checks**

```bash
python tools/validate_skill.py skills/systematic-innovation
python -m unittest discover -s tests -v
git diff --check
```

Expected: all commands exit zero with no warnings.

- [ ] **Step 2: Review behavioral invariants**

Confirm from preserved outputs that the skill uses mechanism distinctions, respects preservation, obeys mode overrides, stops at saturation, avoids forced winners, and does not drift into implementation.

- [ ] **Step 3: Run one fresh portability sample without subagents or web access**

Use a pilot case not used for the latest correction. Confirm the skill still produces a usable portfolio and labels assumptions.

- [ ] **Step 4: Write the candidate report**

Report skill commit, models and hosts tested, structural results, RED-to-GREEN changes, known failures, and claims that remain unverified pending the full benchmark.

- [ ] **Step 5: Commit the candidate report**

```bash
git add evals/pilot/candidate-report.md
git commit -m "docs: record candidate skill verification"
```
