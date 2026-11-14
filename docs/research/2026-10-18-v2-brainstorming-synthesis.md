# Systematic Innovation v2: Research Synthesis, Critical Triage & Evolution Strategy

**Date:** 2026-10-18  
**Status:** Research input — unexecuted synthesis; no v2 specification exists  
**Scope:** Repository-wide evolution from v1 to v2  

---

## 1. Executive Summary & Context

This document captures the synthesis of new research materials (Tudor Rickards's 1985 *Stimulating Innovation*, NotebookLM research analyses, Technological Innovation Systems [TIS] literature, Critical Systems Heuristics [CSH], and Boundary Critique) evaluated against the canonical `systematic-innovation` agent skill.

The goal is to evolve the skill to **v2** while strictly upholding our non-negotiable project guardrails:
1. **Ideation-First (No Premature Winners):** Keep portfolios open; never output unsolicited roadmaps, sprint backlogs, or Gantt charts.
2. **Preservation-First:** Protect what already works. Novelty must never casually invert safety, statutory compliance, or physical reality.
3. **Causal Distinction over Wording Variants:** An idea is distinct only if its causal mechanism or structural coordinates differ, not surface vocabulary.
4. **Agent Portability & Token Economy:** The skill must remain lightweight, provider-neutral Markdown that installs seamlessly in coding agents without prompt bloat.

---

## 2. Step 1: Critical Triage & Reality Check

We triaged the ingested literature into three clear buckets:

### Bucket 1: High-Leverage Gaps (True Signal)
- **4 Systemic Failure Archetypes (TIS - Johnson, Edquist, Klein Woolthuis):**
  - *Incentive/Rule Mismatch:* Rules/metrics actively punish the desired behavior.
  - *Missing Complement ("Reverse Salient"):* The innovation is trapped because a shared tool, testbed, or standard is missing.
  - *Network/Tie-Strength Pathology:* Broken feedback loops (weak-tie failure) or captive lock-in (over-strong tie failure).
  - *Legitimation & Transition Buffer:* Sunk-cost defenders and threatened incumbents cause organ rejection without a protected transition path.
- **The Externalized Burden ("The Witness" - Ulrich, Midgley):** Probing who bears the downstream friction or on-call pain without having a vote in upstream design.
- **Incommensurable Value Scorecards (Midgley & Pinzón):** Identifying when factions evaluate reality on fundamentally conflicting, non-overlapping scorecards (e.g., audit compliance vs. velocity) to decouple them rather than forcing naive compromises.
- **Functional Invariant vs. Structural Vehicle (Preservation Hardening):** Preserving 100% of the outcome requirement (safety, compliance) while liberating the legacy procedural habit (manual sign-offs).

### Bucket 2: Redundant / Already Handled
- **Initial Fluency Depletion:** Already operationalized via default trope quarantine (Lines 60, 78–82 of `SKILL.md`).
- **Ambidextrous Dual-System Innovation:** Already built into the core identity (Ideation-First + Preservation-First).
- **Three Problem-Owner Questions & Boundary Routing:** Already in `references/output-contract.md`.
- **Causal Mechanism Deduplication:** Already in `SKILL.md`'s Mechanism Ledger and duplicate-filtering rule.

### Bucket 3: Academic Bloat / Out of Scope (The Reject Pile)
- **Mario Bunge's CESM Metamodel ($\mu(\sigma) = F(C, E, S, M)$):** Dense algebraic formalism that wastes tokens and degrades LLM instruction-following.
- **Ulrich's 12 CSH Questions & "Sacred/Profane" Jargon:** Turns Deep Mode into an interrogation; sociological jargon sounds alien and preachy in technical tasks.
- **Geels's Multi-Level Perspective (MLP):** Models 50-year socio-technical macro transitions; irrelevant and hand-wavy for addressable agent horizons.
- **Socio-Material "Enactment Scripts":** Violates Guardrail #1 (Ideation-First) by drifting into unsolicited 30-60-90 day implementation roadmaps.
- **National Innovation Systems (NIS / Triple Helix):** Macro-policy tool for government ministries, not agent problem-solving.

---

## 3. Step 2: Resolving Core Design Tensions

1. **Micro vs. Macro Systems:** 
   - *Resolution:* Anchor to **Micro, Meso, and Local Ecosystems** (the problem-owner's direct span of control and immediate dependency network). Macro concepts are translated into meso mechanics (e.g., public procurement $\rightarrow$ internal chargeback rules; national infrastructure $\rightarrow$ shared platform testbeds).
2. **Boundary Critique & Power (Without Moralizing):**
   - *Resolution:* De-ideologize the mechanics. Translate ethical/emancipatory critiques into **structural causality, negative externalities, and telemetry gaps**. The agent acts as an objective systems engineer, never a moral magistrate.
3. **Diagnostic Burden vs. Quick Mode:**
   - *Resolution:* Decouple internal diagnostics from user interaction:
     - **Quick Mode:** The 4 failure modes run as a silent *generative checklist* to force candidate diversity across coordinates. Zero extra user turns; Layer 1 remains 3–4 concise sentences.
     - **Deep Mode:** Strictly **one question per turn (max 7 total), paired with 2–3 contrasting provisional seeds**. The agent pattern-matches the primary tension and lets the seeds do the cognitive heavy lifting.

---

## 4. Step 3: Five Independent Architectural Iterations & Tradeoff Ledger

We ran five independent architectural passes to stress-test candidate implementations (all percentage metrics below are unexecuted design projections, not measured runs):
1. **Run 1: Micro-Injection (Minimalist):** Ultra-low token tax (+35 words in `SKILL.md`), but risks being missed by mid-tier models.
2. **Run 2: Cognitive Operator (Cell-Centric):** Dedicated `Systemic Architecture` cell. High diversity (+22% Vendi — unexecuted design projection, not a measured run), but crowds out other cells in Quick Mode.
3. **Run 3: Upstream Framing (Diagnostic-First):** Enriches Brief Fields 2, 5, and 8. Strong adoption (+35% adoption — unexecuted design projection, not a measured run), but risks inflating Layer 1.
4. **Run 4: Ledger Coordinate (Deduplication-First):** Highest diversity (+28% Vendi — unexecuted design projection, not a measured run), but printing tags on every candidate causes metadata bloat.
5. **Run 5: Invariant Receptivity (Yes-But Inoculation):** Highest safety and adoption, but risks making the agent overly cautious if over-emphasized.

### The Pareto-Optimal Synthesis
- **Upstream Framing:** Enrich Field 2 (*Beneficiary & Externalized Burden*), Field 5 (*Functional Invariants*), and Field 8 (*Dominant Frame & Untouchable Anchors*) in `SKILL.md` without expanding field count.
- **Generative Operators:** Place the 4 Systemic Failure Generative Prompts inside `references/innovation-lenses.md` under `System Dynamics` and `Operational Reality` (avoids adding an 8th cell).
- **Internal Ledger Enforcement:** Enforce failure-mode coordinates in the internal Mechanism Ledger and duplicate checks, but do not mandate printing heavy metadata tags in the visible portfolio.
- **Preservation Directive:** Place the "Functional Invariant vs. Structural Vehicle" rule in `SKILL.md`'s preservation logic, and add Rickards's "Yes-but" inoculation to Layer 4 Spotlights in `references/output-contract.md`.
- **Root Token Economy:** Total addition to root `SKILL.md` is strictly under 8 lines of text.

---

## 5. Repository Evolution Plan for v2

- **Phase 1: Governance & Spec:** `docs/superpowers/specs/2026-10-18-systematic-innovation-v2-design.md` (never authored; superseded as a future workstream by `2026-11-14-systematic-innovation-v2-loop-design.md`) and `CONTEXT.md`.
- **Phase 2: Test-Driven Contracts:** Add regression and behavior assertions to `tests/test_skill_behavior.py` and `tests/test_skill_portability.py`.
- **Phase 3: Canonical Skill Implementation:** Update `skills/systematic-innovation/` (`SKILL.md` and the four reference modules).
- **Phase 4: Evals, Tooling & Benchmarks:** Add 3 new stress cases to `evals/stress/cases.json`; update `tools/score_eval_results.py` and `tools/pilot_metrics.py`.
- **Phase 5: Verification, Authority Audit & Docs:** Run full test suite, authority scanner, update `README.md`, and verify zero link or provider-name regressions.
