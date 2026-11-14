# Systematic Innovation — Security, SkillEvaluator, Probabilistic Creativity & Visual Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute the five-phase remediation, external evaluation (`NVIDIA/SkillEvaluator`), probabilistic creativity R&D loop, README/SVG/PNG overhaul, and release-readiness gate defined in [`2026-11-14-systematic-innovation-v2-loop-design.md`](../specs/2026-11-14-systematic-innovation-v2-loop-design.md).

**Architecture:** `skills/systematic-innovation/` remains the sole editable authority for public skill behavior (`AGENTS.md`). Phases A and B remediate the 32 findings from the 2026-10-29 audit and capture a clean `NVIDIA/SkillEvaluator` Tier 1 baseline outside the repository tree (`../SkillEvaluator`). Phase C runs a bounded, test-first research-and-evaluation loop pairing Tudor Rickards (1985) with probabilistic LLM creativity science before Phase D overhauls `README.md`/SVGs/PNGs and Phase E verifies and merges to `main`.

**Tech Stack:** Python 3.11–3.14 standard library (`unittest`, `json`, `hashlib`, `re`, `pathlib`, `subprocess`), `uv`, Playwright (dev-only PNG rasterization), SVG, GitHub Actions, external `NVIDIA/SkillEvaluator` (`../SkillEvaluator`).

**Contract Alignment:** This plan executes [`2026-11-14-systematic-innovation-v2-loop-design.md`](../specs/2026-11-14-systematic-innovation-v2-loop-design.md), [`2026-08-31-systematic-innovation-design.md`](../specs/2026-08-31-systematic-innovation-design.md), and [`2026-09-01-systematic-innovation-repository-architecture-design.md`](../specs/2026-09-01-systematic-innovation-repository-architecture-design.md). It does not amend or supersede any specification; Task 3 and Task 9 submit explicit specification amendments for owner approval before modifying contracted behavior.

## Global Constraints

1. `skills/systematic-innovation/` is the sole editable behavioral authority and must remain 100% portable, pure Markdown, zero runtime dependencies, zero network calls, and zero executable scripts.
2. No copyrighted book text (`stimulating-innovation-tudor-rickards.md`), untriaged third-party PDFs, credentials, or restricted evaluation packs (`restricted/`, `*.restricted.*`, `*.validation.yaml`, `*.sealed.yaml`) may enter Git history, ordinary CI, generated distributions, or automatic agent context.
3. No push to any remote and no merge to `main` occurs until Phase A clears `0ebddfe` and Phase E verification completes.
4. Existing 116+ unit tests (`python3 -m unittest discover tests -v`) and `python3 tools/validate_skill.py skills/systematic-innovation` must stay green after every code/skill commit.
5. Every code or skill-contract change follows strict RED → GREEN → REFACTOR test-first discipline.
6. Withdrawn `+162%` / `8.2x` pilot efficiency headlines and historical pilot records must never be presented as validated performance claims or overwritten; errata are appended, raw evidence stays intact.

---

## Phase A — Security, Provenance & Audit Remediation

### Task 1: Local Safety Snapshot & Unpushed History Remediation (`F-01`, `F-04`, `F-07`, `F-27`, `D1`, `D2`, `D6`)

**Files:**
- Modify: `.gitignore`
- Move out of Git to gitignored `sources/`: `docs/references/stimulating-innovation-tudor-rickards.md`, `docs/references/*.pdf`, `docs/research/*.pdf`
- Create: `docs/research/README.md`
- Modify: `docs/research/2026-10-18-v2-brainstorming-synthesis.md:1-87`
- Commit alongside clean replacement commit: `docs/superpowers/specs/2026-11-14-systematic-innovation-v2-loop-design.md`, `docs/superpowers/plans/2026-11-14-systematic-innovation-v2-loop.md`, `docs/superpowers/plans/2026-10-29-systematic-innovation-audit-remediation.md`, `evals/audits/`

**Interfaces:**
- Produces: clean branch tip with zero copyrighted book text or untriaged PDFs in `HEAD`, local `sources/` retained untracked for Phase C research, and `backup/pre-remediation-2026-11-14` local ref until Phase E cleanup.

- [ ] **Step 1: Verify unpushed window and create local backup ref**

Run:
```bash
git branch -r --contains 0ebddfe
git rev-parse HEAD
git branch backup/pre-remediation-2026-11-14 HEAD
```
Expected: `git branch -r --contains 0ebddfe` prints nothing (empty); `HEAD` matches `0ebddfe...`.

- [ ] **Step 2: Soft-reset `0ebddfe` and relocate copyrighted book text & PDFs to `sources/`**

Run:
```bash
git reset --soft HEAD~1
mkdir -p sources/references sources/research
git rm --cached docs/references/stimulating-innovation-tudor-rickards.md
mv docs/references/stimulating-innovation-tudor-rickards.md sources/references/
git rm --cached docs/references/*.pdf
mv docs/references/*.pdf sources/references/
git rm --cached docs/research/*.pdf
mv docs/research/*.pdf sources/research/
git rm -r --cached docs/research/Academia.edu_Bundle_-_What_is_systemic_innovation
mv docs/research/Academia.edu_Bundle_-_What_is_systemic_innovation sources/research/
rm -f sources/research/1703Fads3D.pdf
```
Verify md5 deduplication left `sources/research/admin,+The+Systems+Approach+to+Innovation+Studies.pdf` intact and check `sources/` is clean.

- [ ] **Step 3: Ignore `sources/` and document `docs/research/` corpus status**

Append `sources/` to `.gitignore`:
```gitignore
sources/
```

Create `docs/research/README.md`:
```markdown
# Research Inputs

This directory holds non-authoritative background syntheses and research notes used to inform hypothesis generation for `systematic-innovation`.

- **Not behavioral authority:** Canonical skill behavior lives solely in [`skills/systematic-innovation/`](../../skills/systematic-innovation/SKILL.md) and approved specifications under [`docs/superpowers/specs/`](../superpowers/specs/).
- **Copyright and distribution boundary:** Copyrighted primary sources and untriaged third-party PDFs belong strictly in the gitignored local `sources/` directory and never enter Git history, distributions, or automatic agent discovery.
- **Unverified projections:** Exploratory estimates inside research notes are hypotheses until supported by approved specifications and retained evaluation runs.
```

- [ ] **Step 4: Relabel `docs/research/2026-10-18-v2-brainstorming-synthesis.md` (`F-07`, `D2`)**

Edit `docs/research/2026-10-18-v2-brainstorming-synthesis.md`:
- Change line 4 `**Status:** Approved Brainstorming & Architecture Synthesis` to:
  `**Status:** Research input — unexecuted synthesis; no v2 specification exists`
- Update lines 63–70 so the `+22% Vendi`, `+35% adoption`, and `+28% Vendi` labels explicitly state they are **unexecuted design projections (not measured runs)**.
- Update line 83 so `docs/superpowers/specs/2026-10-18-systematic-innovation-v2-design.md` is marked **never authored; superseded as a future workstream by `2026-11-14-systematic-innovation-v2-loop-design.md`**.

- [ ] **Step 5: Stage, verify history isolation, and commit clean replacement commit**

Run:
```bash
git add .gitignore docs/research/README.md docs/research/2026-10-18-v2-brainstorming-synthesis.md \
  docs/superpowers/specs/2026-11-14-systematic-innovation-v2-loop-design.md \
  docs/superpowers/plans/2026-11-14-systematic-innovation-v2-loop.md \
  docs/superpowers/plans/2026-10-29-systematic-innovation-audit-remediation.md \
  evals/audits/
git log HEAD --oneline -- docs/references/stimulating-innovation-tudor-rickards.md
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
git commit -m "chore: remove copyrighted sources from branch and record v2 loop spec"
```
Expected: `git log HEAD` shows 0 commits for the book text; 116 tests pass; validator prints `OK`.

---

### Task 2: Branding Claim Regression Test, Safe Baseline PNG/README & Pilot Addendum (`F-02`, `F-03`, `F-11`, `F-20`, `F-29`, `D7`)

**Files:**
- Create: `tests/test_branding_claims.py`
- Modify: `tools/build_branding.py:184-198,349-388,521-533,651-675`
- Regenerate: `assets/banner.png`, `assets/comparison.png`, `assets/system-architecture.png`, `assets/quick-demo.png`
- Modify: `README.md:10-79,117-128`
- Modify: `evals/stress/five-cycle-report.md:5`, `evals/stress/contract-findings.md:3`, `evals/pilot/baseline-analysis.md:1-5`

**Interfaces:**
- Produces: deterministic `tests/test_branding_claims.py` asserting zero withdrawn metrics or pre-restoration rule strings in `tools/build_branding.py` and `README.md`, plus claim-accurate baseline PNGs and README links.

- [ ] **Step 1: Write failing branding-claim regression test (RED)**

Create `tests/test_branding_claims.py`:
```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_ASSET_STRINGS = (
    "+162%",
    "8.2x",
    "Pilot Lift",
    "Learning Probes",
    "≤ 4 Questions",
    "&le; 4 Questions",
    "4 surgical questions",
    "5 structural dimensions",
    "0.90 MECH / 1K TOK",
    "2.35 MECH / 1K TOK",
    "1–2 Wk Probes",
    "6 DISTINCT LEVERS",
    "1.36 vs 0.17",
)
FORBIDDEN_README_ACTIVE_STRINGS = (
    "still need reconciliation",
    "still require reconciliation",
    "Transforms ordinary AI ideation",
)


class BrandingClaimsRegressionTests(unittest.TestCase):
    def test_build_branding_contains_no_withdrawn_claims_or_superseded_rules(self) -> None:
        source = (ROOT / "tools/build_branding.py").read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_ASSET_STRINGS:
            self.assertNotIn(forbidden, source)

    def test_readme_embeds_no_withdrawn_claims_or_stale_reconciliation_text(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_ASSET_STRINGS + FORBIDDEN_README_ACTIVE_STRINGS:
            self.assertNotIn(forbidden, readme)
        self.assertIn("evals/restored-2026-10-18/report.md", readme)
        self.assertIn("references/innovation-lenses.md", readme)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run RED test to confirm failure**

Run: `python3 -m unittest tests.test_branding_claims -v`
Expected: FAIL on multiple forbidden strings in `tools/build_branding.py` and `README.md`.

- [ ] **Step 3: Strip withdrawn claims and superseded protocols from `tools/build_branding.py`**

Update `tools/build_branding.py`:
- Line 186 (`banner_html`): change `Learning Probes` → `Mechanism Ledger` (or `User Continuation`).
- Line 197 (`banner_html`): change `Pilot Lift: +162% Causal Density · 0% Roadmap Drift` → `Exploratory Design · Ideation-First · Preservation-Safe`.
- Line 350 (`comparison_html`): change `22 Fresh-Context Pilot Runs` → `Conceptual Comparison · Design Goals`.
- Line 356 (`comparison_html`): change `0.90 MECH / 1K TOK` → `DEFAULT MODE`.
- Lines 366–368 (`comparison_html`): replace numeric pilot rates (`0/10`, `55%`, `90%`) with qualitative descriptors: `✕ Skips Discovery`, `✕ Paraphrase Clustering`, `✕ Premature Roadmaps`.
- Line 375 (`comparison_html`): change `2.35 MECH / 1K TOK (+162%)` → `CAUSAL STRUCTURE`.
- Lines 385–387 (`comparison_html`): replace `10/10`, `100%`, `1–2 Wk Probes` with: `✓ Progressive Discovery`, `✓ Preservation Ledger`, `✓ User-Directed Continuation`.
- Line 522 (`arch_html`): change `Enforce 5 structural dimensions` → `Compare causal &amp; structural axes`.
- Line 527 (`arch_html`): change `Ch. 8 Receptivity &amp; 1–2 Wk Probes` → `Ch. 8 Receptivity &amp; Continuation`.
- Line 532 (`arch_html`): change `DEEP MODE: TURN-1 RESTRAINT (&le; 4 Questions + 3 Seeds)` → `DEEP MODE: ONE QUESTION AT A TIME (&le; 7 Max) + 2–3 SEEDS`.
- Line 652 (`demo_html`): change `413 TOKENS` → `TURN 1`.
- Line 657 (`demo_html`): change `4 surgical questions on day-off handoffs &amp; quotes` → `1 high-leverage question on day-off handoffs (one at a time, max 7)`.
- Line 666 (`demo_html`): change `6 DISTINCT LEVERS` → `PORTFOLIO`.
- Line 672 (`demo_html`): change `3 Stakeholder Hearings + 5-day paper card probe` → `Receptivity, Yes-But Safeguards &amp; User Continuation`.
- Line 674 (`demo_html`): change `✓ 8.2x efficiency lift over vanilla baseline (1.36 vs 0.17)` → `✓ Conceptual walkthrough — illustrative structure, not a benchmark claim`.

- [ ] **Step 4: Regenerate baseline PNGs and inspect visually**

Ensure dev Playwright is available in `.venv` (already gitignored):
```bash
uv venv .venv && uv pip install --python .venv/bin/python playwright && .venv/bin/python -m playwright install chromium
.venv/bin/python tools/build_branding.py
```
Inspect all four PNGs (`assets/banner.png`, `assets/comparison.png`, `assets/system-architecture.png`, `assets/quick-demo.png`) with `read_file` to verify clean rendering and zero forbidden text.

- [ ] **Step 5: Update `README.md` (`F-03`, `F-11`, `F-29`, `D7`) and eval report headers (`F-20`)**

Edit `README.md` (preserving all headings required by `tests/test_skill_portability.py`):
- Line 12: link badge to `evals/restored-2026-10-18/report.md` and label `Evidence-Exploratory%20Dev`.
- Line 23: replace `"transforms ordinary AI ideation"` → `"structures AI ideation"`.
- Line 47: reflect resolved 2026-10-17 restoration in `evals/stress/contract-findings.md` (remove `"still need reconciliation"`).
- Lines 72–78: link `evals/restored-2026-10-18/report.md` alongside `evals/stress/five-cycle-report.md`; state accurately that a format-matched control ran in the small uncalibrated diagnostic (`restored-2026-10-18`) and calibrated quality/primary-effect validation remains unestablished.
- Line 86: scope `"Zero Binary Dependencies"` explicitly to the canonical `skills/systematic-innovation/` runtime package (noting repo tooling/branding dev dependencies live separately).
- Lines 117–118 (`D7`): instruct fallback users without automated skill discovery to load `skills/systematic-innovation/SKILL.md` together with all four files under `skills/systematic-innovation/references/` (`innovation-lenses.md`, `deep-mode.md`, `output-contract.md`, `evidence.md`).
- Line 127: note the 2026-10-17 restoration reconciled the attribution classification and link `contract-findings.md` as historical resolution context.

Also update:
- `evals/stress/five-cycle-report.md:5`: replace `"The behavioral-contract decision remains pending."` with `"Addendum (2026-10-17): The owner restored the approved behavioral contract in a36903a; Cycles 1–6 evaluate the pre-restoration candidate and are superseded by evals/restored-2026-10-18/report.md."`
- `evals/stress/contract-findings.md:3`: rewrite `"The owner decision requested during session recovery is pending."` to `"This historical audit recorded discrepancies resolved by the owner's 2026-10-17 restoration decision documented below."`
- `evals/pilot/baseline-analysis.md`: add the same `Superseded assessment — 2026-10-17 stress recovery` banner present in `treatment-analysis.md` and `candidate-report.md`.

- [ ] **Step 6: Verify GREEN and commit**

Run:
```bash
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
git add tests/test_branding_claims.py tools/build_branding.py assets/*.png README.md \
  evals/stress/five-cycle-report.md evals/stress/contract-findings.md evals/pilot/baseline-analysis.md
git commit -m "fix: strip withdrawn claims from branding assets and align README evidence links"
```
Expected: all tests pass (including `test_branding_claims.py` and `test_skill_portability.py`).

---

### Task 3: Behavioral Spec Amendment Draft (`D3` / `F-06`) & Conformance Completions (`F-09`, `F-10`, `F-17`, `F-21`, `F-22`, `F-23`)

**Files:**
- Modify (owner-gated for `D3`): `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md` (§6.4, §12)
- Modify: `tests/test_skill_behavior.py`
- Modify: `skills/systematic-innovation/SKILL.md`, `skills/systematic-innovation/references/innovation-lenses.md`, `skills/systematic-innovation/references/output-contract.md`, `skills/systematic-innovation/references/evidence.md:21`

**Interfaces:**
- Produces: behavioral-spec alignment for execution-channel & hard-budget precedence (`D3`), plus RED/GREEN tests and minimal Markdown clauses closing `F-09`, `F-10`, `F-17`, `F-21`, `F-22`, and `F-23`.

- [ ] **Step 1: Present and confirm the `D3` behavioral-spec amendment before editing the spec**

Present these two targeted additions to `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md` for explicit owner approval (matching the four-corrections precedent):
1. New **§6.4 Execution-channel precedence:** Explicit user overrides hold highest precedence. When the execution channel permits only a single turn (one-shot API, immediate response, or no user reply path), deliver the complete portfolio immediately and record unresolved assumptions in Layer 1 rather than stalling in Deep discovery questions, even if the challenge is complex or Deep mode was requested.
2. Amendment to **§12 User-requested output budgets:** An explicit user word or token ceiling overrides normal candidate breadth and verbosity. Target 80% of the stated ceiling, compress shared context before dropping distinct mechanisms, use a compact plain-text six-layer format for ceilings of 500 words or fewer, and label budget-limited reductions explicitly rather than calling them mechanism saturation.

Once confirmed, insert §6.4 and the §12 clause into `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md`.

- [ ] **Step 2: Write failing conformance tests for `F-09`, `F-10`, `F-17`, `F-21`, `F-22`, `F-23` (RED)**

Append to `tests/test_skill_behavior.py`:
```python
    def test_skill_pack_implements_spec_research_nochg_highstakes_quick_q_and_lenses(self) -> None:
        skill = read("SKILL.md")
        lenses = read("references/innovation-lenses.md")
        contract = read("references/output-contract.md")
        evidence = read("references/evidence.md")

        # F-09: Capability-aware research when host provides tools (§15)
        self.assertIn("host provides", skill.lower())
        self.assertIn("offline", skill.lower())

        # F-10: Valid preservation-first / no-change conclusion (§12)
        self.assertIn("no-change", contract.lower())
        self.assertIn("preservation-first", contract.lower())

        # F-21: High-stakes exploratory + verification needs labeling (§14)
        self.assertIn("exploratory", skill.lower())
        self.assertIn("verification needs", skill.lower())

        # F-22: Quick mode one critical question allowance (§6.1)
        self.assertIn("critical unknown", skill.lower())

        # F-23: Morphological recombination and subtraction operational cues (§10)
        self.assertIn("Morphological recombination", lenses)
        self.assertIn("Subtraction", lenses)

        # F-17: Corrected Lawrence/Lorsch chapter locator in Rickards (1985)
        self.assertIn("Ch. 4", evidence)
        self.assertNotIn("Ch. 7–8", evidence)
```

- [ ] **Step 3: Run RED test to verify failures**

Run: `python3 -m unittest tests.test_skill_behavior -v`
Expected: FAIL on `test_skill_pack_implements_spec_research_nochg_highstakes_quick_q_and_lenses`.

- [ ] **Step 4: Implement minimal spec-grounded skill edits (GREEN)**

1. In `skills/systematic-innovation/SKILL.md`:
   - Quick Mode row (line 26): note `"if an interactive reply is available, ask at most one question only when a critical unknown would make generation meaningless."`
   - High-Stakes Safety Floor (line 87): add `"For medical, legal, financial, security, and other high-stakes topics, label outputs exploratory and state verification needs explicitly."`
   - Under `Core Principle` or capability note: add one concise sentence: `"When the host provides web or workspace research tools and current precedent would materially improve ideation, use them; remain fully functional offline by labeling material assumptions."`
2. In `skills/systematic-innovation/references/output-contract.md`:
   - In Layer 1 / Layer 3 (`### Layer 3: Complete Portfolio`): add `"A preservation-first or no-change conclusion is valid when novelty would add cost or risk without meaningful value."`
3. In `skills/systematic-innovation/references/innovation-lenses.md`:
   - Under `## 2. The Seven Reasoning Cells` (or a brief `Cross-Cell Operators` cue right below it): add compact 1-line operational cues for `Morphological recombination` (decompose into independent causal dimensions and recombine non-obvious pairings) and `Subtraction` (remove a legacy component, rule, or step to reveal whether value improves).
4. In `skills/systematic-innovation/references/evidence.md:21`:
   - Change `Rickards (1985, Ch. 7–8)` → `Rickards (1985, Ch. 4, pp. 70–77)`.

- [ ] **Step 5: Verify GREEN and commit**

Run:
```bash
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
git add docs/superpowers/specs/2026-08-31-systematic-innovation-design.md \
  skills/systematic-innovation/ tests/test_skill_behavior.py
git commit -m "feat: align behavioral spec amendment and complete missing skill conformance clauses"
```
Expected: all tests pass; validator prints `OK`.

---

### Task 4: Security Policy, Root Validation Commands, Packaging Manifest & Public CI (`F-13`, `F-15`, `F-16`, `D4`, `D8`)

**Files:**
- Modify: `AGENTS.md`
- Modify: `SECURITY.md`
- Create: `pyproject.toml`
- Create: `.github/workflows/ci.yml`
- Create: `tests/repository/test_workflows.py`
- Modify: `tests/test_skill_portability.py`

**Interfaces:**
- Produces: documented validation entry points in `AGENTS.md`, trust-zone & GitHub-advisory security policy in `SECURITY.md`, reproducible `pyproject.toml`, and least-privilege CI verified by `tests/repository/test_workflows.py`.

- [ ] **Step 1: Write failing tests for `AGENTS.md`, `SECURITY.md`, `pyproject.toml`, and `.github/workflows/ci.yml` (RED)**

Create `tests/repository/test_workflows.py`:
```python
from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]


class WorkflowAndPackagingTests(unittest.TestCase):
    def test_pyproject_declares_stdlib_runtime_and_playwright_dev_group(self) -> None:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["name"], "systematic-innovation")
        self.assertEqual(data["project"]["dependencies"], [])
        self.assertIn("playwright", " ".join(data["dependency-groups"]["dev"]))

    def test_ci_workflow_is_least_privilege_and_runs_stdlib_checks(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertIn("timeout-minutes: 15", workflow)
        self.assertIn("cancel-in-progress: true", workflow)
        self.assertNotIn("pull_request_target", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertIn("python3 tools/validate_skill.py skills/systematic-innovation", workflow)

    def test_agents_md_lists_validation_commands_and_loop_docs(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("python3 -m unittest discover tests -v", agents)
        self.assertIn("python3 tools/validate_skill.py skills/systematic-innovation", agents)
        self.assertIn("2026-11-14-systematic-innovation-v2-loop-design.md", agents)
        self.assertIn("2026-11-14-systematic-innovation-v2-loop.md", agents)

    def test_security_md_explains_trust_zones_and_uses_advisories(self) -> None:
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertNotIn(".local", security)
        self.assertIn("Trust Zones", security)
        self.assertIn("GitHub Security Advisory", security)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run RED test**

Run: `python3 -m unittest tests.repository.test_workflows -v`
Expected: FAIL because `pyproject.toml`, `.github/workflows/ci.yml`, and updated docs do not exist yet.

- [ ] **Step 3: Implement `AGENTS.md`, `SECURITY.md`, `pyproject.toml`, and `.github/workflows/ci.yml`**

1. Update `AGENTS.md`:
   - Add `docs/superpowers/specs/2026-11-14-systematic-innovation-v2-loop-design.md`, `docs/superpowers/plans/2026-11-14-systematic-innovation-v2-loop.md`, and `docs/superpowers/plans/2026-10-29-systematic-innovation-audit-remediation.md` to the reading order (without introducing any second `skills/<other>/` path).
   - Add `## Validation Commands`:
     ```markdown
     ## Validation Commands

     Repository tests use Python's standard library `unittest` (`pytest` is not used):

     - `python3 -m unittest discover tests -v`
     - `python3 tools/validate_skill.py skills/systematic-innovation`
     - `python3 -m tools.repository.authority`
     ```
2. Update `SECURITY.md`:
   - Add `### Repository Trust Zones`: explicitly distinguish (a) the pure-Markdown public skill (`skills/systematic-innovation/`, zero binaries/dependencies/credentials), (b) executable Python tooling and dev-only Playwright asset generation (`tools/`, `tests/`, never shipped inside the skill directory), and (c) local `sources/` and restricted evaluation packs (`restricted/`, `*.restricted.*`, `*.validation.yaml`, `*.sealed.yaml`, excluded from Git, CI, and distributions).
   - Replace `security@systematic-innovation.local` with private reporting via GitHub Security Advisories only (`D8`).
3. Create `pyproject.toml`:
   ```toml
   [project]
   name = "systematic-innovation"
   version = "0.1.0"
   description = "Provider-neutral Agent Skill and evaluation laboratory for causally distinct, system-aware innovation possibilities."
   requires-python = ">=3.11,<3.15"
   dependencies = []

   [dependency-groups]
   dev = ["playwright>=1.49.0"]
   ```
4. Create `.github/workflows/ci.yml` (resolve current full 40-char commit SHAs for `actions/checkout` v4 and `actions/setup-python` v5 via `git ls-remote https://github.com/actions/checkout` and `git ls-remote https://github.com/actions/setup-python` at creation time; least privilege):
   ```yaml
   name: CI

   on:
     push:
     pull_request:

   permissions:
     contents: read

   concurrency:
     group: ci-${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true

   jobs:
     validate:
       runs-on: ubuntu-latest
       timeout-minutes: 15
       strategy:
         matrix:
           python-version: ["3.11", "3.13", "3.14"]
       steps:
         - uses: actions/checkout@<resolved-40-char-sha>
         - uses: actions/setup-python@<resolved-40-char-sha>
           with:
             python-version: ${{ matrix.python-version }}
         - name: Run unit tests
           run: python3 -m unittest discover -s tests -v
         - name: Validate canonical skill
           run: python3 tools/validate_skill.py skills/systematic-innovation
         - name: Run authority checks
           run: python3 -m tools.repository.authority
   ```
   *(Verify the pinned commit SHAs for `actions/checkout` and `actions/setup-python` or use `gh api` / `git ls-remote` before committing if online.)*

- [ ] **Step 4: Verify GREEN and commit**

Note: Wait until Task 5 implements `python3 -m tools.repository.authority` before expecting the CLI command itself to pass, or update `ci.yml` after Task 5 and run `tests.repository.test_workflows` right now:
```bash
python3 -m unittest tests.repository.test_workflows -v
```
Expected: PASS. Commit after Task 5 or now with Task 4 scope (`AGENTS.md`, `SECURITY.md`, `pyproject.toml`, `.github/workflows/ci.yml`, `tests/repository/test_workflows.py`).

---

### Task 5: Authority Enforcement, Provider-Scan Hardening & Sync Assertions (`F-12`, `F-24`, `F-25`, `F-26`)

**Files:**
- Modify: `tools/repository/authority.py`
- Modify: `tools/validate_skill.py:9,77-80`
- Modify: `tests/repository/test_authority.py`
- Modify: `tests/test_skill_portability.py`
- Modify: `tests/test_stress_runner.py`
- Modify: `CONTEXT.md` (stamp §6 sync note)

**Interfaces:**
- Produces: `python3 -m tools.repository.authority` CLI returning exit code `1` on findings, content-signature shadow detection over an explicit allowlist, broadened supersession phrase checks, broadened `PROVIDER_RE` without `evidence.md` exemption, and `stress_runner` count-drift assertion.

- [ ] **Step 1: Write failing tests (RED)**

1. In `tests/repository/test_authority.py`:
   - Test that a shadow markdown file (even named `README.md` or `guide.md` outside the explicit allowlist) restating the skill's signature rules (`"Quick Mode: 10 to 15"`, `"System Dynamics"`, `"Human Value"`, `"Operational Reality"`, `"Boundary Reframing"`, `"Mechanism Transfer"`, `"never more than seven"`, `"Layer 6: User-Directed Continuation"`) triggers an authority error.
   - Test that plan language containing `"override conflicting specification"` or `"amend the specification"` (outside explicit non-amendment disclaimers) triggers an error.
   - Test `subprocess.run([sys.executable, "-m", "tools.repository.authority"], ...)` returns exit `0` on the repository root.
2. In `tests/test_skill_portability.py`:
   - Test that `validate_skill` rejects `gemini`, `gpt`, `openai`, `anthropic`, and `copilot` inside `references/evidence.md` as well as `SKILL.md` (`F-25`).
3. In `tests/test_stress_runner.py`:
   - Test that `control_format` target strings (`10 to 15` and `15 to 24`) in `tools/stress_runner.py` match the canonical targets declared in `skills/systematic-innovation/SKILL.md` (`F-24`).

- [ ] **Step 2: Run RED tests**

Run: `python3 -m unittest tests.repository.test_authority tests.test_skill_portability tests.test_stress_runner -v`
Expected: FAIL on the new assertions.

- [ ] **Step 3: Implement authority sweep, CLI, and validator hardening (GREEN)**

1. In `tools/repository/authority.py`:
   - Skip `sources` alongside `.git`, `.venv`, `dist`, `fixtures`, `evals`, `docs/superpowers`, `docs/research`, `CONTEXT.md`, `tools`, `tests` in the allowlist for behavioral signatures; for any tracked `.md` outside that allowlist and outside `skills/systematic-innovation/`, flag if `>= 3` distinctive canonical signatures (`"System Dynamics"`, `"Boundary Reframing"`, `"Mechanism Transfer"`, `"10 to 15 distinct possibilities"`, `"15 to 24 distinct possibilities"`, `"Layer 1: Innovation Brief"`, `"Layer 6: User-Directed Continuation"`) co-occur.
   - Broaden plan supersession check to catch `"supersede " + "conflicting"`, `"supersede the specification"`, `"amends the specification"`, or `"overrides the behavioral specification"` unless preceded by `"never "` or `"does not "`.
   - Add `if __name__ == "__main__":` CLI printing errors and returning `1` if errors exist, else `0`.
2. In `tools/validate_skill.py`:
   - Broaden `PROVIDER_RE` to `re.compile(r"\b(?:claude|codex|cursor|antigravity|pi|gemini|gpt|openai|anthropic|copilot)\b", re.IGNORECASE)`.
   - Remove the `if file_path.name != "evidence.md":` exemption (line 77) so all Markdown files in the skill pack are scanned uniformly.
3. In `CONTEXT.md`:
   - Stamp §6 heading note: `"*(Historical summary as of 2026-10-17; `skills/systematic-innovation/` and approved specifications remain authoritative.)*"` (`F-26`).

- [ ] **Step 4: Verify GREEN and commit**

Run:
```bash
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
python3 -m tools.repository.authority
git add tools/repository/authority.py tools/validate_skill.py tests/repository/test_authority.py \
  tests/test_skill_portability.py tests/test_stress_runner.py CONTEXT.md \
  AGENTS.md SECURITY.md pyproject.toml .github/workflows/ci.yml tests/repository/test_workflows.py
git commit -m "feat: harden authority sweeps, skill validator, CI, and security policy"
```
Expected: all tests pass; validator and authority CLI exit 0.

---

### Task 6: Runner Spend/Redaction Safety, Tool Portability & Eval Errata (`F-08`, `F-14`, `F-18`, `F-19`, `F-28`, `F-30`, `F-31`, `F-32`)

**Files:**
- Modify: `tools/stress_runner.py`
- Modify: `tools/compile_treatment_results.py:15`
- Modify: `tools/score_eval_results.py:160-182`
- Modify: `tests/test_stress_runner.py`
- Modify: `tests/test_restored_measurement.py`
- Modify: `evals/pilot/baseline-analysis.md`, `evals/pilot/treatment-analysis.md`, `evals/pilot/candidate-report.md`, `evals/pilot/rubric.md`, `evals/pilot/runbook.md`, `evals/restored-2026-10-18/human-review.md`
- Modify: `CONTEXT.md` (add §19.8)

**Interfaces:**
- Produces: `redact_secrets(text_or_obj)`, `--max-cost`, `--allowed-models`, `--max-failures` in `tools/stress_runner.py`; safe `--output` overwrite guard in `tools/score_eval_results.py`; env/CLI path resolution without hardcoded user home paths; complete pilot errata and `CONTEXT.md` §19.8 record.

- [ ] **Step 1: Write failing runner-safety and tool-portability tests (RED)**

Add tests to `tests/test_stress_runner.py` and `tests/test_restored_measurement.py`:
1. `test_rejects_model_outside_allowlist`: calling `main([... "--model", "unapproved-model"])` raises `ValueError` before spawning any subprocess unless `--allowed-models` explicitly includes it.
2. `test_aborts_when_estimated_or_accumulated_cost_exceeds_max_cost`: `--max-cost 0.50` aborts cleanly before exceeding the configured budget.
3. `test_redacts_credentials_from_transport_events_and_errors`: API-key/bearer patterns (`sk-...`, `Bearer ...`, `AIza...`, `ghp_...`, `NVIDIA_...`) in CLI events or error strings are replaced with `[REDACTED]` before storing in `turns` or raising errors.
4. `test_no_hardcoded_user_home_paths_in_tools`: static check verifying `"/Users/"` is absent from `tools/stress_runner.py` and `tools/compile_treatment_results.py`.
5. `test_score_eval_results_refuses_existing_output_without_force`: running `score_eval_results.main` onto an existing `--output` file fails with `FileExistsError` / nonzero exit unless `--force` is passed.

- [ ] **Step 2: Run RED tests**

Run: `python3 -m unittest tests.test_stress_runner tests.test_restored_measurement -v`
Expected: FAIL on all 5 new tests.

- [ ] **Step 3: Implement runner safety controls and tool fixes (GREEN)**

1. In `tools/stress_runner.py`:
   - Add `redact_text(value: str) -> str` and `redact_obj(obj)` scrubbing OpenAI/Anthropic/Google/GitHub/Bearer token patterns (`sk-[A-Za-z0-9_-]{16,}`, `AIza[0-9A-Za-z_-]{20,}`, `ghp_[A-Za-z0-9]{20,}`, `Bearer\s+\S+`, `(?i)(api[_-]?key|token|secret)\s*[:=]\s*["']?\S+`).
   - Replace `--codex` default `"/Users/poferraz/.local/bin/codex"` with `shutil.which("codex") or "codex"`.
   - Add `--allowed-models` (default `["gpt-5.6-luna"]` or configurable via CLI) and enforce `args.model in args.allowed_models`.
   - Add `--max-cost` (`float | None`), `--cost-per-1k-input` (`float = 0.0`), `--cost-per-1k-output` (`float = 0.0`), and `--max-failures` (`int = 3`) aborting execution if exceeded.
   - Apply `redact_obj` to `events` before storing in `transport` and `redact_text` to raised error excerpts.
2. In `tools/compile_treatment_results.py`:
   - Replace hardcoded `/Users/poferraz/.gemini/antigravity/brain` with `os.environ.get("ANTIGRAVITY_BRAIN_DIR")` or CLI/Path fallback (`Path.home() / ".gemini/antigravity/brain"`).
3. In `tools/score_eval_results.py`:
   - Add `--force` flag; refuse to overwrite an existing `--output` path unless `--force` is supplied.

- [ ] **Step 4: Add pilot errata, rubric boundaries, calibration key rule, and `CONTEXT.md` §19.8 (`F-08`, `F-18`, `F-19`, `F-30`, `F-31`, `F-32`)**

- Append errata to superseded banners in `evals/pilot/baseline-analysis.md`, `treatment-analysis.md`, and `candidate-report.md` documenting: (a) 2-vs-3-turn Deep asymmetry in historical treatment records, (b) cross-arm numerator mismatch (distinct families vs raw candidates) behind the withdrawn `+162%`, (c) hardcoded `turn_1_question_count` constants, and (d) trigger-precision scope and Three Problem-Owner Questions paraphrase caveats (`F-30`).
- Annotate `evals/pilot/rubric.md` §3 and `evals/pilot/runbook.md` §2 explicitly stating the live scorer uses stemmed-cosine lexical clustering (`pilot_metrics.py`) while semantic equivalence clustering and duplicate collapse ratio await calibrated human/LLM scoring (`F-19`).
- Update `evals/restored-2026-10-18/human-review.md` requiring any scheduled 40-pair calibration run to regenerate packets with an out-of-repo random seed/key or export blind copies without `assignment-key.json` (`F-31`).
- Record `CONTEXT.md` §19.8 documenting: clean replacement of `0ebddfe`, relocation of copyrighted book text & 49 PDFs to gitignored `sources/`, relabeling of `2026-10-18-v2-brainstorming-synthesis.md`, `evals/audits/` retention as historical evidence, `D3` behavioral-spec amendment, tracking Hungarian matching (`F-32`) as a formal-benchmark acceptance criterion, and authorization of the 5-phase v2 loop.

- [ ] **Step 5: Verify GREEN and commit**

Run:
```bash
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
python3 -m tools.repository.authority
git add tools/ tests/ evals/pilot/ evals/restored-2026-10-18/human-review.md CONTEXT.md
git commit -m "fix: harden stress runner spend/redaction controls and document pilot errata"
```
Expected: all tests pass; validator and authority CLI exit 0.

---

## Phase B — External Evaluation Baseline (`NVIDIA/SkillEvaluator`)

### Task 7: Run `NVIDIA/SkillEvaluator` Tier 1 Keyless Baseline & Triage Gaps

**Files:**
- External clone (outside repo): `../SkillEvaluator`
- Create: `evals/audits/2026-11-14-skillevaluator-baseline.md`
- Create (path-redacted JSON export): `evals/audits/2026-11-14-skillevaluator-tier1-baseline.json`

**Interfaces:**
- Produces: baseline external static-quality and **SkillSpector** security report for `skills/systematic-innovation/`, plus an owner triage checkpoint deciding whether to also run LLM rubric / Tier 3 Skill Lift before Phase C.

- [ ] **Step 1: Clone `NVIDIA/SkillEvaluator` into sibling directory `../SkillEvaluator`**

Run outside the `systematic-innovation` git tree:
```bash
git clone --depth 1 https://github.com/NVIDIA/SkillEvaluator.git ../SkillEvaluator
```
Inspect `../SkillEvaluator/README.md` and `../SkillEvaluator/pyproject.toml` to verify exact current CLI flags (`quality-check`, `tier1 --no-llm`, report flags).

- [ ] **Step 2: Run Tier 1 keyless `quality-check` and `tier1 --no-llm` (with SkillSpector)**

Run from `../SkillEvaluator` pointing at the absolute path of `skills/systematic-innovation` (outputting to `../SkillEvaluator/reports/` first so no unreviewed raw paths enter this repo):
```bash
cd ../SkillEvaluator
uv run --python 3.13 --extra security skillevaluator quality-check ../systematic-innovation/skills/systematic-innovation -r cli -r json -o reports/si-quality-baseline
uv run --python 3.13 --extra security skillevaluator tier1 ../systematic-innovation/skills/systematic-innovation --no-llm -r cli -r json -o reports/si-tier1-baseline
```
*(Adapt exact subcommand flags if `../SkillEvaluator/README.md` uses slightly updated flag syntax.)*

- [ ] **Step 3: Normalize local paths, archive report in `evals/audits/`, and triage gaps**

Scrub any user-home absolute paths from the JSON report, copy into `evals/audits/2026-11-14-skillevaluator-tier1-baseline.json`, and summarize all pass/warn/fail findings in `evals/audits/2026-11-14-skillevaluator-baseline.md` grouped by:
1. Security / Prompt-Injection / PII / Secret checks (SkillSpector / Gitleaks)
2. Metadata, Trigger & Agent Skills Spec compliance
3. Instruction clarity, length, structure & overlap warnings
4. Recommendations for optional Tier 1 LLM rubric or Tier 3 live Skill Lift (asking the owner whether to run LLM-backed tiers now or after Phase C research).

- [ ] **Step 4: Verify clean git tree & commit Phase B baseline**

Run:
```bash
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
python3 -m tools.repository.authority
git add evals/audits/2026-11-14-skillevaluator-baseline.md evals/audits/2026-11-14-skillevaluator-tier1-baseline.json
git commit -m "docs: record NVIDIA SkillEvaluator Tier 1 baseline report"
```

---

## Phase C — Deep Research & Probabilistic Creativity Loop

### Task 8: Dual-Track Deep Research (`Rickards 1985` × `Probabilistic LLM Creativity`)

**Files:**
- Read-only local reference: `sources/` (strictly never copied or committed)
- Create: `docs/research/2026-11-14-probabilistic-creativity-synthesis.md`

**Interfaces:**
- Produces: provenance-classified synthesis mapping probabilistic LLM mechanisms onto Rickards (1985) systemic innovation principles, plus a critical triage of `2026-10-18-v2-brainstorming-synthesis.md` and concrete falsifiable hypotheses for `skills/systematic-innovation/` and `tools/stress_runner.py`.

- [ ] **Step 1: Audit local `sources/` for underused Rickards (1985) mechanics**

Analyze the book's selection-environment search/select loops, initial fluency depletion, multiple redefinition operators, synectic excursions, morphological synthesis, boundary-overflow modes, and *Yes-but* inoculation without copying copyrighted prose. Record exact chapter/page citations for any verified principle.

- [ ] **Step 2: Research 2024–2026 probabilistic LLM creativity & diversity literature**

Use `search_web` to review primary papers on:
- Verbalized Sampling / tail-probability prompting and distributional diversity in post-trained/RLHF models;
- Mode collapse, typicality bias, and semantic homogenization across repeated samples;
- Orthogonal structural conditioning, negative-space / trope exclusion, and delayed convergence in pure-Markdown instructions;
- Decoding interactions (`temperature`, `top_p`, model family, isolated context vs sequential pass) and word-budget compliance mechanics (targeting the open 400/500-word regression in `CONTEXT.md` §19.7).

- [ ] **Step 3: Synthesize into `docs/research/2026-11-14-probabilistic-creativity-synthesis.md`**

Structure with:
1. Provenance-separated mechanism table (Verified Rickards Principle vs Adapted Method vs Original AI/Probabilistic Mechanism);
2. Critical disposition of the 2026-10-18 TIS/Boundary Critique candidates (keep vs prune based on token economy and mechanism lift);
3. Explicit hypotheses (`H1..Hk`) for skill updates and runner/sampling sensitivity probes, each with a measurable pass/fail test and token-budget guard.

- [ ] **Step 4: Commit research synthesis**

```bash
git add docs/research/2026-11-14-probabilistic-creativity-synthesis.md
git commit -m "docs: synthesize Rickards 1985 and probabilistic LLM creativity research"
```

---

### Task 9: Spec Amendment Gate, Sub-Plan & Iterative Eval Loop (`Phase C Execution`)

**Files (gated on Task 8 + Task 7 findings and owner spec approval):**
- Modify (on owner approval): `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md` (v2 amendment)
- Create (via `writing-plans`): `docs/superpowers/plans/2026-11-XX-systematic-innovation-v2-skill.md`
- Modify: `skills/systematic-innovation/` (`SKILL.md`, `references/*`)
- Modify: `tests/test_skill_behavior.py`, `evals/stress/cases.json` (dev-only expansion if needed)
- Retain runs: `evals/v2-loop/` (append-only JSONLs + scored reports + `SkillEvaluator` re-checks)

**Interfaces:**
- Produces: owner-approved v2 behavioral amendment, RED/GREEN tested pure-Markdown skill upgrades, paired multi-arm evaluation results (`tools/stress_runner.py` + `tools/score_eval_results.py` measuring Vendi Score $\text{VS}_k$, distinct mechanism families, word-budget compliance, and preservation invariants), sampling-interaction diagnostics, and updated `SkillEvaluator` check showing zero regressions.

- [ ] **Step 1: Draft v2 Behavioral Spec Amendment & concrete v2 sub-plan**

Using Task 7 (`SkillEvaluator` gaps) and Task 8 (`2026-11-14-probabilistic-creativity-synthesis.md`), write the exact v2 spec amendment and concrete file-level RED/GREEN sub-plan. Pause for owner approval per `AGENTS.md` before modifying `skills/systematic-innovation/`.

- [ ] **Step 2: Execute RED → GREEN → Eval → Refine loop (bounded cost/calls)**

For each approved hypothesis cycle:
1. Add failing behavioral/budget tests to `tests/test_skill_behavior.py` (including strict 400/500-word ceiling checks).
2. Apply minimal pure-Markdown update to `skills/systematic-innovation/`.
3. Run bounded paired comparisons via `tools/stress_runner.py` with `--max-cost`, `--max-calls`, and `--allowed-models` enforced (comparing `baseline_clean`, `control_format`, prior restored pack, and v2 candidate across target cases and sampling variants).
4. Score via `tools/score_eval_results.py` and re-run `NVIDIA/SkillEvaluator` Tier 1 (plus Tier 2/3 if enabled).
5. Stop when mechanism diversity, budget compliance, preservation safety, and `SkillEvaluator` checks hold without regression.

---

## Phase D & E — README, SVG/PNG Visual Overhaul & Final Merge Gate

### Task 10: README, Custom SVGs & PNG Visual Overhaul (`Phase D`)

**Files:**
- Create / Modify: `assets/*.svg` (e.g., `assets/search-selection-loop.svg`, `assets/reasoning-cells-flow.svg`)
- Modify: `tools/build_branding.py`
- Regenerate: `assets/banner.png`, `assets/comparison.png`, `assets/system-architecture.png`, `assets/quick-demo.png`
- Modify: `README.md`
- Modify: `tests/test_branding_claims.py`, `tests/test_skill_portability.py`

**Interfaces:**
- Produces: redesigned `README.md`, crisp GitHub-compatible vector SVGs, claim-verified PNGs in `#025d9c` buckram blue & `#f5d818` signal yellow, and verified visual inspection of every rendered asset.

- [ ] **Step 1: Author vector SVGs and update `tools/build_branding.py`**

Craft clean SVGs for architectural diagrams (theme-legible in both GitHub light and dark modes, zero embedded claims/drift) and update `tools/build_branding.py` to match the stabilized Phase C workflow and verified metrics only.

- [ ] **Step 2: Regenerate PNGs and inspect every SVG/PNG visually**

Run `.venv/bin/python tools/build_branding.py`, inspect all generated PNGs and SVGs via image inspection / browser preview for clipping, contrast, alignment, and typography, and iterate until crisp.

- [ ] **Step 3: Overhaul `README.md` and run claim/authority guards**

Rewrite `README.md` while keeping `skills/systematic-innovation/` as the sole behavioral authority (no shadow instruction copies) and retaining all required structural sections verified by `tests/test_skill_portability.py`. Run:
```bash
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
python3 -m tools.repository.authority
git add assets/ tools/build_branding.py README.md tests/test_branding_claims.py
git commit -m "docs: overhaul README, SVGs, and PNG visual assets"
```

---

### Task 11: Final Security Audit, `NVIDIA/SkillEvaluator` Gate & Clean Merge (`Phase E`)

**Files:**
- Create: `evals/audits/2026-11-XX-skillevaluator-final.md`
- Modify: `CONTEXT.md` (add §19.9 closure record)

**Interfaces:**
- Produces: passing final `SkillEvaluator` report, clean full-history sweep (including removing the temporary local `backup/pre-remediation-2026-11-14` ref after confirming clean history), green repository verification, and fast-forward merge to `main`.

- [ ] **Step 1: Run final `NVIDIA/SkillEvaluator` verification**

Re-run Tier 1 (and any enabled Tier 2/3) against `skills/systematic-innovation/`, normalize local paths, and save summary in `evals/audits/`.

- [ ] **Step 2: Update `CONTEXT.md` §19.9 and drop local backup ref after verification**

Record Phase A–E outcomes, exact v2 evidence limits, and next phases (human calibration and formal 6/12-case benchmark package) in `CONTEXT.md` §19.9. Remove temporary `backup/pre-remediation-2026-11-14` ref and verify full repository history is clean:
```bash
git branch -D backup/pre-remediation-2026-11-14
git log --all --oneline -- docs/references/stimulating-innovation-tudor-rickards.md
git ls-files | grep -Ei 'restricted|sealed|validation\.yaml|benchmark/private|^dist/|^sources/'
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
python3 -m tools.repository.authority
```
Expected: zero matches in history/tracked-file sweeps; all tests, validator, and authority CLI exit 0.

- [ ] **Step 3: Fast-forward merge to `main` (owner confirmation gate)**

Confirm with the owner before merging and pushing `main`:
```bash
git checkout main
git merge --ff-only stress-test/five-cycle-refinement
```
Expected: clean fast-forward merge with all gates green.

---

## Plan Self-Review

1. **Spec coverage:** Maps 1-to-1 to every section in `2026-11-14-systematic-innovation-v2-loop-design.md` (Phase A Tasks 1–6 cover all 32 Oct 29 audit findings + `D1`–`D9` with `main` held until Phase E; Phase B Task 7 covers `NVIDIA/SkillEvaluator` baseline; Phase C Tasks 8–9 cover dual-track Rickards × probabilistic LLM research + bounded eval loop + spec gate; Phase D Task 10 covers README/SVGs/PNGs; Phase E Task 11 covers final audit & merge).
2. **Placeholder scan:** Tasks 1–7 have exact file paths, line ranges, test code, and CLI commands; Tasks 8–11 specify exact artifact paths, commands, gates, and an explicit sub-plan checkpoint once Phase B & Task 8 empirical findings exist.
3. **Authority & non-supersession check:** Plan explicitly declares non-supersession of approved specs, avoids forbidden contractual-supremacy strings, and leaves `skills/systematic-innovation/` as sole behavioral authority.
