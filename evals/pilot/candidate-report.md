# Systematic Innovation: Candidate Skill Verification Gate Report

> **Superseded assessment — 2026-10-17 stress recovery:** The historical efficiency/quality claims below are not current validated claims. Legacy token counts were unverified estimates, some single-turn outputs stalled at discovery, and no calibrated mechanism-quality, safety, or human evaluation established the approved primary endpoint. Raw outputs remain unchanged. See the [audited stress report](../stress/five-cycle-report.md) and [contract findings](../stress/contract-findings.md).
>
> **Pilot Errata & Audit Findings (`F-08`, `F-18`, `F-30`):**
> 1. *Turn-Count Asymmetry:* Historical treatment records in `evals/pilot/results/treatment.jsonl` captured only 2 assistant turns for Deep cases rather than the 3 turns recorded in baseline records, introducing conversational turn asymmetry.
> 2. *Cross-Arm Numerator Mismatch (+162% Withdrawn):* The reported +162% causal density surge compared distinct mechanism families in treatment against uncollapsed raw candidate counts in baseline, invalidating the historical efficiency claim.
> 3. *Hardcoded Question Counts:* Historical analysis scripts relied on hardcoded `turn_1_question_count` constants rather than dynamic parser extraction from transcript turns.
> 4. *Scope & Paraphrase Caveats:* Automatic activation and trigger precision were evaluated on a small 12-case pilot rather than an independent held-out benchmark; compliance with Rickards's Three Problem-Owner Questions relied on prompt paraphrasing rather than structural verification.

## 1. Executive Summary & Gate Decision

- **Original Reported Status:** **APPROVED (PASSED)** — superseded; empirical gate not substantiated
- **Candidate Skill Authority:** `skills/systematic-innovation/`
- **Candidate Skill Commit:** `1549a7c`
- **Date:** 2026-10-17
- **Target Milestone:** Completion of Skill Plan Phase 1 (Core Skill Authoring & Empirical Pilot Verification). Ready for Phase 2 (`systematic-innovation-benchmark-runner`).

The original assessment asserted improved causal density, reduced conversational churn, complete restraint, and trigger precision. Those headline claims are superseded by the recovery audit. Passing structural tests does not establish qualified mechanism quality, automatic activation, approved-spec conformance, or release readiness.

---

## 2. Deterministic & Structural Verification

| Check | Specification Requirement | Result | Evidence |
| :--- | :--- | :---: | :--- |
| **Package Validator** | `tools/validate_skill.py` exit zero, pure Markdown, zero binary scripts | **PASS** | `validate_skill.py skills/systematic-innovation` exited 0 with 0 errors |
| **Link Integrity** | All internal markdown links must resolve without escaping root | **PASS** | `test_canonical_skill_references_resolve` passed |
| **Authority Architecture** | Single declared authority in `skills/systematic-innovation/` | **PASS** | `test_repository_has_one_declared_behavioral_authority` passed |
| **Unit Test Suite** | 100% pass across repository, pilot manifest, portability, and triggers | **PASS** | 22/22 unit tests passed in 0.040s |
| **Git Tree Integrity** | `git diff --check` clean, zero whitespace/merge artifacts | **PASS** | Exited 0 with no warnings |

---

## 3. Evaluated Environments & Models

- **Host Architecture:** Provider-neutral Agent Skills Standard, evaluated using isolated subagents (`antigravity-subagent-with-canonical-skill` vs. `antigravity-subagent-clean-context`).
- **Underlying LLM:** Advanced agentic coding / reasoning foundation model (`inherit-default`).
- **Corpus:** 12 cross-domain pilot cases (`evals/pilot/cases.json`):
  - 5 Deep controlled multi-turn cases (retail, municipal permitting, DevOps release pipelines, education staffing, rural library access).
  - 5 Quick single-turn cases (meal planning, medication adherence, food bank mismatch, warehouse returns triage, customer support provocation).
  - 2 Negative trigger controls (Clayton Christensen fact lookup, PostgreSQL task app schema).
- **Total Preserved Runs:** 44 runs (22 baseline runs in `evals/pilot/results/baseline.jsonl` + 22 treatment runs in `evals/pilot/results/treatment.jsonl`).

---

## 4. Historical RED-to-GREEN Contrast (Not Validated)

| Dimension | RED Baseline (`vanilla`) | GREEN Treatment (`skill`) | Transformation Impact |
| :--- | :---: | :---: | :--- |
| **Primary Efficiency** | 0.897 mechanisms / 1k tok | **2.352 mechanisms / 1k tok** | **+162% causal information density** |
| **Deep Turn-1 Restraint** | 0 / 10 runs (0%) | **10 / 10 runs (100%)** | Zero premature solution dumping; asks 4 targeted questions + 3 provisional seeds under 450 tokens |
| **Deep Dialogue Churn** | 6,422 mean output tokens | **4,170 mean output tokens** | **-35% conversational overhead** |
| **Duplicate Collapse** | 0.55 mean collapse ratio | **Controlled Mechanism Ledger** | Candidates guaranteed distinct across 5 structural dimensions |
| **Implementation Drift** | 18 / 20 positive runs (90% fail) | **0 / 20 positive runs (0% fail)** | Eliminated 30/60/90-day roadmaps; replaced with Spotlight Signals and 1–2 week low-cost learning probes |
| **System & Preservation Scan**| 0 / 20 positive runs (0%) | **20 / 20 positive runs (100%)** | Explicitly preserves non-negotiable anchors and maps socio-technical boundaries |
| **Stakeholder Receptivity** | 0 / 20 positive runs (0%) | **20 / 20 positive runs (100%)** | Evaluates Rickards (1985) Ch. 8 Problem-Owner Questions and *Yes-But* hearing inoculation |
| **Negative Trigger Precision**| 100% (0 false triggers) | **100% (0 false triggers)** | Zero unwanted systematic innovation ceremony on factual lookups or routine code tasks |

---

## 5. Original Behavioral Audit (Not Recalibrated)

All preserved runs were audited against the core behavioral invariants:
1. **Initial Fluency Depletion:** Observed in 20/20 positive runs. Top-of-mind tropes (e.g. generic inventory apps, 2-2-2 meal rules, NFC pill caps) were explicitly identified and quarantined before ledger entry.
2. **Mechanism Ledger Tracking:** Every candidate portfolio item explicitly declared its causal lever, principal actor, and intended feedback loop, preventing surface relabeling of single mechanisms.
3. **Preservation Floor:** In complex regulated cases (`permit-wait`, `release-bottleneck`), existing safety and compliance baselines were strictly protected rather than waived.
4. **Spotlight Signals over Forced Winners:** Final outputs preserved decision agency for the problem owner by highlighting tension trade-offs rather than prescribing a single choice.
5. **No Hallucinated Effect Sizes:** Quantified claims were restricted to verifiable structural logic; empirical effect sizes were deferred to local validation via 1–2 week learning probes.

---

## 6. Known Scope Limitations & Remaining Release Claims

The following claims remain intentionally unverified pending the full benchmark execution:
1. **Multi-Model Universality:** While verified on the primary agentic foundation model, behavioral invariance across external model families (Claude 3.5 Sonnet, GPT-4o, DeepSeek-R1, and local open-weights models) will be formally measured in Phase 2/3 using the automated benchmark runner.
2. **50-Case Automatic Discovery:** While the 50-case trigger corpus is authored and tested (`evals/triggers/cases.json`), large-scale cross-host trigger matrix runs (5 replicates across 3 prompt variants) will be executed during the multi-host evaluation study.
3. **External Packaging:** Public remote installation (e.g. from GitHub URL) will be validated upon pushing the repository to GitHub.

---

## 7. Gate Conclusion

The original candidate certification is superseded for empirical and behavioral-conformance claims. The current development candidate requires the contract decision and evaluation gates documented in the stress report; no universal non-hallucination claim is made.
