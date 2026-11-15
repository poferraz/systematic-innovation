# External Baseline Audit: NVIDIA SkillEvaluator Tier 1 & Quality Gate

**Audit Date:** 2026-11-14  
**Target:** `skills/systematic-innovation/` (canonical skill pack authority)  
**Target Git Revision:** `2e1bce9af0a361036d9db5ca44a3589b8c9cdf95` (branch: `stress-test/five-cycle-refinement`)  
**Evaluator Tool:** NVIDIA SkillEvaluator `0.9.0` (commit `0d5e356583fee63c3d12e4930581c7dfb3352911`)  
**Security Scanners:** SkillSpector `2.13.4` (checksum-verified), Gitleaks `8.30.1` (`gitleaks`)  
**Environment Status:** Python 3.13.12 (CPython via `uv 0.10.9`); `docker` not found / not used (static Tier 1 execution); `--no-llm` keyless mode  
**Artifact Archive:** `evals/audits/2026-11-14-skillevaluator-tier1-baseline.json` (fully path-redacted)

---

## Executive Summary

The pre-v2 canonical skill pack (`skills/systematic-innovation/`) underwent a full external baseline evaluation using NVIDIA's `SkillEvaluator` suite (Tier 1 Keyless Validation and Static Quality Gates).

- **Tier 1 Validation Result:** **PASS** (CLI reported 9 of 9 applicable checks passed, 0 failed, 0 incomplete, 0 skipped, 4 N/A; JSON records 13 validators with status `passed`, `overall_passed: true`).
- **Deterministic Quality Score:** **86.0 / 100 (Grade: B)** (passing threshold: 70).
- **Skill Type Detected:** `guide-only` (5 markdown files, 0 scripts, 0 code files).
- **Security & Hygiene Status:** **Clean** (0 secrets, 0 PII findings, 0 injection vulnerabilities, 0 invisible Unicode smuggling characters, 0 broken relative markdown links).
- **Non-blocking Findings:** 15 total occurrences (5 medium-severity schema/quality suggestions, 8 low-severity style/structure suggestions, 2 advisory harness compatibility notes).

---

## 1. Security, Prompt Injection, PII & Secret Checks

### 1.1 SkillSpector AST & Vulnerability Scan
- **Check Name:** `security_scan` (via SkillSpector `2.13.4`)
- **Status:** **PASS** (`[OK] skillspector: No security vulnerabilities detected (secrets, API keys, credentials)`)
- **Findings:** 0 critical, 0 high, 0 medium, 0 low.
- **Verification:** SkillSpector verified that instruction prompts and reference markdown files contain no unconstrained tool invocation primitives, no indirect prompt injection attack vectors, and no hardcoded credentials.

### 1.2 Gitleaks Secrets Detection
- **Check Name:** `secrets_detection` (via `gitleaks` `8.30.1`)
- **Status:** **PASS** (`[OK] gitleaks: No secrets detected by Gitleaks`)
- **Findings:** 0 secrets detected across skill files.

### 1.3 PII Detection Scan
- **Check Name:** `pii_scan`
- **Status:** **PASS** (`[OK] pii_detection: No PII detected in 5 files (emails, SSNs, phone numbers, paths)`)
- **Files Scanned:** 5 markdown files (`SKILL.md`, `references/deep-mode.md`, `references/evidence.md`, `references/innovation-lenses.md`, `references/output-contract.md`).
- **Findings:** 0 PII occurrences.

### 1.4 Unicode Smuggling Detection
- **Check Name:** `unicode_smuggling`
- **Status:** **PASS** (`[OK] unicode_scan: No invisible Unicode characters detected in 5 file(s)`)
- **Findings:** 0 zero-width or homoglyphic smuggling characters.

### 1.5 Optional Tool Status
- **Gitleaks:** Present and executed directly (`gitleaks 8.30.1`).
- **Docker:** Absent (`docker not found`). Not required for Tier 1 static validation; required only for Tier 3 live sandboxed agent execution.
- **Semgrep / Bandit / Pip-Audit:** Python code risk analysis (`Code Risk Analysis`) and dependency scanning (`Dependency Vulnerability Audit`) reported as `N/A` because `skills/systematic-innovation/` is a pure guide skill with zero Python source files or package dependency manifests.

---

## 2. Metadata, Trigger & Agent Skills Spec Compliance

SkillEvaluator evaluated the skill folder structure and YAML frontmatter against the [Agent Skills Specification](https://agentskills.io/) and repository governance rules.

### 2.1 Governance Checks
- `manifest_exists`: Found skill manifest `SKILL.md` (96 lines; well within the 500-line recommended limit).
- `folder_hierarchy`: Valid general skill structure (`skills/systematic-innovation/`).
- `naming_convention`: Folder name `systematic-innovation` follows kebab-case convention.
- `name_consistency`: Folder name matches frontmatter `name: systematic-innovation`.
- `body_heading`: SKILL.md body contains a valid top-level heading (`# Systematic Innovation`).
- `optional_files`: Found supporting `references/` directory with 4 modular reference guides (`deep-mode.md`, `evidence.md`, `innovation-lenses.md`, `output-contract.md`).

### 2.2 Spec Discrepancies & Warnings
SkillEvaluator flagged 3 schema-level recommendations:
1. **`[SCHEMA-MEDIUM] Missing recommended section: '## Instructions'`**
   - *Observation:* The skill organizes its body under `## Core Principle`, `## When Not to Trigger`, `## Mode Routing (Quick vs. Deep)`, `## The Innovation Brief & Preservation Scan`, `## Reasoning Cell Selection & Mechanism Ledger`, `## Ideation-Only & High-Stakes Guardrails`, and `## Reference Navigation` (lacks a section literally titled `## Instructions` or `## Usage`).
   - *Evaluator Guidance:* AgentSkills.io specification leaves body format unrestricted; however, adding an explicit `## Instructions` or `## Usage` heading provides a stable anchor for automated static analyzers.
2. **`[SCHEMA-MEDIUM] Missing recommended section: '## Examples'`**
   - *Observation:* The canonical skill body points to operational layers without embedded end-to-end user session examples in `SKILL.md`.
   - *Evaluator Guidance:* Suggests adding concrete input/output example blocks to assist agents with few-shot calibration.
3. **`[SCHEMA-LOW] Author not specified in metadata`**
   - *Observation:* Frontmatter contains `name` and `description`, but lacks `metadata.author`.
   - *Evaluator Guidance:* Add `metadata.author` indicating team or organization.

### 2.3 Agent Harness Compatibility (Advisory)
SkillEvaluator tested behavioral loading patterns across agent harnesses:
- **GitHub Copilot CLI:** Advisory notice (`CP-RELOAD`): New skills appear after `/skills reload` or session restart.
- **OpenCode:** Advisory notice (`OC-RELOAD`): Skill metadata and instructions are cached at startup; edits require session restart.
- **Status:** **PASS** (`status: "passed"` in JSON; zero harness errors or degraded modes emitted, with the two advisory notifications noted above).

---

## 3. Instruction Clarity, Length, Structure & Overlap Warnings

The deterministic quality scorer rated `skills/systematic-innovation/` across 4 weighted dimensions:

| Dimension | Weight | Score | Deductions | Grade |
| :--- | :---: | :---: | :---: | :---: |
| **Correctness** | 35% | 80.0 / 100 | -20 pts (4 issues × 5 pts) | B |
| **Discoverability** | 25% | 90.0 / 100 | -10 pts (2 issues × 5 pts) | A |
| **Reliability** | 25% | 85.0 / 100 | -15 pts (3 issues × 5 pts) | B |
| **Efficiency** | 15% | 95.0 / 100 | -5 pts (1 issue × 5 pts) | A |
| **Overall** | **100%** | **86.0 / 100** | **-50 pts raw (-14.0 pts weighted: 0.35×20 + 0.25×10 + 0.25×15 + 0.15×5 = 14.0 → Score 86.0)** | **B** |

### 3.1 Token & Efficiency Metrics
- **Total Estimated Tokens:** 2,565 tokens (~10,260 characters).
- **Frontmatter Tokens:** 74 tokens.
- **Instruction Tokens:** 2,488 tokens (well below the 5,000 recommended maximum budget; `recommended_max_tokens: 5000` in JSON metrics).
- **Progressive Disclosure:** References split into `references/` sub-files, keeping the root manifest concise and focused.

### 3.2 Specific Quality Deductions & Warnings
1. **Description Length (`[QUALITY-LOW]`):**
   - *Observed:* Frontmatter description is 258 characters (verbatim):  
     `"Use when a user wants non-obvious ideas, systemic alternatives, assumption challenges, or ways out of a persistent tradeoff without breaking what already works. Do not use for factual lookup, debugging a known bug, or implementing an already-chosen solution."`
   - *Benchmark Recommendation:* Recommend 50–150 characters for top-level routing for progressive disclosure, deferring trigger exclusions to the body.
2. **Missing Purpose / Limitations / Troubleshooting Sections (`[QUALITY-LOW]`):**
   - Skill lacks dedicated Markdown section headers `## Purpose`, `## Prerequisites`, `## Limitations`, and `## Troubleshooting`.
   - *Impact:* Evaluator reliability heuristics look for explicit error/recovery and failure boundary headings.
3. **Language Complexity (`[QUALITY-LOW]`):**
   - Flaggable word choices flagged by readability heuristic (e.g., preference for "use" over "utilize" or dense domain vocabulary).
4. **License Compliance Notice:**
   - In `License Compliance`, check `license_compliance` completed with `status: "passed"` and message `"License compliance scan completed (not detected)"` (`license_status: "not_detected"`). SkillEvaluator emitted an advisory notice: `"No license information found - manual review required. Add a LICENSE file or 'license' field in frontmatter."` (The repository has a root `LICENSE` file, but `skills/systematic-innovation/` does not include a separate `LICENSE` file or frontmatter `license:` field).

---

## 4. Actionable Gap Triage & Phase C / Post-Baseline Recommendations

### 4.1 Summary of Gaps vs. Architectural Intent

| Evaluator Finding | Severity | Systematic Innovation Architecture Intent | Recommended Action |
| :--- | :---: | :--- | :--- |
| **Missing frontmatter version / author / tags** | Medium | Frontmatter currently has minimal fields (`name`, `description`). Adding `version: "2.0.0"`, `metadata.author`, and domain tags (`innovation`, `system-dynamics`, `triz`) improves catalog discoverability. | **Adopt in Phase E:** Add structured metadata fields during v2 skill packaging. |
| **Description length (258 chars vs 50–150)** | Low | The 258-char description concisely defines both positive and negative trigger boundaries. A tighter trigger summary helps LLM router models avoid context dilution. | **Adopt in Phase E:** Tighten trigger summary to ~120 chars; move negative triggers into `## When Not to Trigger`. |
| **Missing `## Instructions`, `## Purpose`, `## Limitations` headings** | Medium / Low | The current body uses domain headings (`## Core Principle`, `## Mode Routing`, `## The Innovation Brief & Preservation Scan`, etc.). Standardizing or augmenting section anchors aligns with agent skill heuristics without losing behavioral rigor. | **Adopt in Phase E:** Reorganize sections into standard headings with preserved behavioral text. |
| **No inline code block examples in SKILL.md** | Medium | The skill references methodology but does not provide an end-to-end worked example in the root manifest. | **Triage:** Retain worked examples in reference files or add a compact example block in `references/evidence.md` / `output-contract.md` to prevent token bloat in `SKILL.md`. |

### 4.2 Owner Decision Checkpoint: Optional Tier 1 LLM Rubric & Tier 3 Live Skill Lift

NVIDIA SkillEvaluator offers two optional higher-tier evaluation capabilities:
1. **Tier 1 LLM-as-Judge Rubric (`skillevaluator rubric-eval`):**
   - Requires API provider access (e.g., NVIDIA Build API key or OpenAI/Anthropic keys).
   - Evaluates subjective instruction clarity, completeness, and edge-case handling against synthetic user queries.
2. **Tier 3 Live Agent Skill Lift (`skillevaluator tier3`):**
   - Requires Docker runtime + LLM provider keys.
   - Evaluates delta agent task performance with skill vs. baseline without skill in sandboxed execution.

**Recommendation:**  
Proceed directly to **Phase C (Deep Research & Probabilistic Creativity Loop)** with this clean **86.0/B** keyless baseline established. Running LLM-backed rubric checks or live agent lift is most informative **after** Phase C research produces the v2 probabilistic engine enhancements (Task 8–11) and the v2 skill is authored (Phase E), allowing a direct before-and-after comparison of v1 baseline vs. v2 candidate.
