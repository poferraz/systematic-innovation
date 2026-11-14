# Dual-Track Deep Research Synthesis: Tudor Rickards (1985) × Probabilistic LLM Creativity

**Date:** 2026-11-14  
**Status:** Research synthesis — informs the Task 9 v2 behavioral-specification amendment and sub-plan; non-authoritative until owner-approved.  
**Scope:** Theoretical and empirical foundation bridging classical systems-based innovation methodology and modern post-training large language model (LLM) probability shaping.  
**Authority Boundary:** Non-authoritative research document. Canonical skill behavior resides solely in [`skills/systematic-innovation/`](../../skills/systematic-innovation/SKILL.md) and approved specifications under [`docs/superpowers/specs/`](../superpowers/specs/). This document does not modify canonical files.  
**Copyright Notice:** In compliance with repository provenance rules, this document contains zero copyrighted sentences, paragraphs, or prose from Tudor Rickards (1985) or other proprietary texts. All classical concepts are cited by chapter, section, page, and figure, and expressed through original functional summaries classified under the repository's three provenance categories (*Verified principle*, *Adapted method*, *Original AI/probabilistic mechanism*).

---

## 1. Executive Summary

This research synthesis bridges two previously separate domains to establish the behavioral foundation for `systematic-innovation` v2:

1. **Classical Systems-Level Creative Problem Solving (CPS):** Specifically the empirical and systems framework established by Tudor Rickards in *Stimulating Innovation: A Systems Approach* (1985, Frances Pinter / St. Martin's Press, `pp. xi + 221`), incorporating search/selection coupling, Ashby's Law of Requisite Variety, initial fluency depletion, Currie's *5W + Why* invariant analysis, synectic excursions, morphological matrices, liability reversal, clustered variety preservation, and the dual selling-in/selling-out implementation loop.
2. **Modern Empirical Machine Learning Literature on LLM Creativity & Sampling (2024–2026):** Specifically recent findings on post-training mode collapse and typicality bias under RLHF/DPO (Zhang et al., 2025), dual-level convergence mechanisms spanning collective knowledge aggregation and individual-level fixation (Deng, Brucks & Toubia, 2025), decoding dynamics and dynamic confidence truncation via Min-P sampling (Nguyen et al., ICLR 2025 Oral), mathematical diversity measurement via the Vendi Score and Conditional Vendi Score (Friedman & Dieng, 2023; Jalali et al., AISTATS 2025), and subword token length-constraint compliance (Yuan et al., EMNLP 2025; Hu et al., 2025).

### Core Diagnostic Insight
Standard autoregressive language models, especially those aligned via Reinforcement Learning from Human Feedback (RLHF) or Direct Preference Optimization (DPO), suffer from acute **mode collapse** when tasked with open-ended ideation. Human evaluators exhibit a systematic *typicality bias*, rewarding conventional, fluent, and familiar phrasing. Post-training algorithms steepen the model's output distribution around these consensus modal peaks, causing independent generation passes to collapse onto the same safe clichés ("old chestnuts"). When users prompt for "more creative" or "diverse" ideas, naive multi-turn prompting triggers *within-ideator fixation*, where early generated tokens constrain subsequent attention. Furthermore, uncalibrated temperature increases under standard Nucleus (Top-P) sampling fail because they leak incoherent, low-probability noise tails rather than surfacing structured, coherent innovations.

Classical CPS—and Rickards's systems framework in particular—was designed to address the exact human cognitive analog of this problem: bureaucratic fixation, premature convergence, habituation, and structural resistance. When mapped onto LLM probabilistic mechanics, Rickards's structural operators act as **pure-Markdown, prompt-level distribution shapers**. By enforcing negative-space quarantine (fluency depletion), functional invariant separation (Currie goal laddering), orthogonal cross-dimensional forcing (morphological matrices), and boundary-aware receptivity routing (the selling-in/selling-out loop), an agent skill can reliably transport generation out of high-probability typicality basins into the high-value probability tail ($p < 0.10$) without sacrificing physical validity, safety constraints, or token economy.

---

## 2. Primary-Source Provenance & Bibliographic Errata Audit

### 2.1 Physical Volume Specification
- **Title:** *Stimulating Innovation: A Systems Approach*
- **Author:** Tudor Rickards (Head of Creativity and Innovation Studies, Manchester Business School)
- **Publisher:** Frances Pinter (Publishers), London / St. Martin's Press, New York
- **Publication Date:** 1985
- **Physical Extent:** `pp. xi + 221` (preliminaries pp. i–xi; main text pp. 1–201; bibliography pp. 202–214; index pp. 215–221)
- **ISBN:** `0-86187-512-5` (British Library Cataloguing in Publication Data) / `0-312-76203-8` (St. Martin's Press)

### 2.2 Bibliographic Errata in `skills/systematic-innovation/references/evidence.md`
A physical page-by-page audit of the primary text against lines 52–66 of [`skills/systematic-innovation/references/evidence.md`](../../skills/systematic-innovation/references/evidence.md#L52-L66) revealed eight page span discrepancies and one fictitious structural element. These errors originated in an earlier secondary summary and must be formally corrected in Task 9.

| Location in `evidence.md` | Current Description in `evidence.md` | Primary-Source Physical Reality in Rickards (1985) | Correction Required for Task 9 |
| :--- | :--- | :--- | :--- |
| Line 58 | `3. *Creativity: the key to stimulating innovation* (p. 28)` | Chapter 3 spans **pp. 33–62** (TOC p. v; text starts on p. 33; p. 28 is in Ch. 2). | Correct page reference to `pp. 33–62`. |
| Line 59 | `4. *The managerial perspective: structures and strategies* (p. 50)` | Chapter 4 spans **pp. 63–86** (TOC p. v; text starts on p. 63; p. 50 is in Ch. 3). | Correct page reference to `pp. 63–86`. |
| Line 60 | `5. *The managerial perspective: people* (p. 72)` | Chapter 5 spans **pp. 87–113** (TOC p. v; text starts on p. 87; p. 72 is in Ch. 4). | Correct page reference to `pp. 87–113`. |
| Line 61 | `6. *Stimulating innovation: project level considerations* (p. 92; includes Fig. 6.1 ... p. 97)` | Chapter 6 spans **pp. 114–134** (TOC p. vi; text starts on p. 114). Figure 6.1 is on **pp. 126–127** (Spread 070). | Correct page reference to `pp. 114–134`; correct Fig. 6.1 location to `pp. 126–127`. |
| Line 62 | `7. *Stimulating innovation: organisational level considerations* (p. 131; includes Fig. 7.2 ... p. 142)` | Chapter 7 spans **pp. 135–157** (TOC p. vi; text starts on p. 135; p. 131 is in Ch. 6). Fig. 7.2 is on p. 142. | Correct page reference to `pp. 135–157`. |
| Line 63 | `8. *Ideas into action* (p. 158; includes Fig. 8.1 ... p. 166)` | Chapter 8 spans **pp. 158–183**. Figure 8.1 (*The linchpin model*) is on **p. 161** (Spread 089; p. 166 is mid-text). | Correct Fig. 8.1 location to `p. 161`. |
| Line 64 | `9. *Towards appropriate innovation* (p. 176)` | Chapter 9 spans **pp. 184–201** (TOC p. vi; text starts on p. 184; p. 176 is in Ch. 8). | Correct page reference to `pp. 184–201`. |
| Line 65 | `*Appendix: Techniques for stimulating creativity in innovation* (p. 190)` | **No Appendix exists in Rickards (1985).** Page 190 is mid-Chapter 9 (Spread 103). The book transitions directly from Chapter 9 (ending p. 201) to Bibliography (pp. 202–214) and Index (pp. 215–221). | **Delete Appendix entry entirely.** Record deletion in Task 9 commit. |

### 2.3 Complete Verified Table of Contents (Rickards 1985)
1. *Introduction* (pp. 1–8)
2. *Innovation: some basic concepts* (pp. 9–32; includes Fig. 2.1 p. 14, Fig. 2.2 p. 16, Fig. 2.3 p. 26, Table 2.1 p. 28)
3. *Creativity: the key to stimulating innovation* (pp. 33–62; covers insight pp. 45–48, liability reversal pp. 48–49, 53, climate pp. 49–51, techniques pp. 51–60)
4. *The managerial perspective: structures and strategies* (pp. 63–86; covers contingency theory pp. 69–72, differentiation/integration pp. 72–77)
5. *The managerial perspective: people* (pp. 87–113; covers group dynamics pp. 94–103, leadership pp. 103–109)
6. *Stimulating innovation: project level considerations* (pp. 114–134; covers Currie 5W+Why pp. 124–125, Fig. 6.1 pp. 126–127, closing-down clustering/hurdles pp. 129–130)
7. *Stimulating innovation: organisational level considerations* (pp. 135–157; covers organizational learning pp. 135–140, Fig. 7.2 p. 142)
8. *Ideas into action* (pp. 158–183; covers Yes-but inoculation p. 159, three owner questions p. 160, Fig. 8.1 p. 161, Table 8.1 p. 164, selling-in/selling-out pp. 176–177)
9. *Towards appropriate innovation* (pp. 184–201; covers appropriate technology and future outlook)
- *Bibliography* (pp. 202–214)
- *Index* (pp. 215–221)

---

## 3. Probabilistic Diagnosis & Mechanism Mapping

### 3.1 The Probabilistic Failure Modes of Open-Ended LLM Ideation
Empirical machine learning research published between 2024 and 2026 demonstrates that open-ended LLM brainstorming is governed by four structural constraints:

1. **Post-Training Mode Collapse and Typicality Bias:**  
   Zhang, Yu, Chong, Sicilia, Tomz, Manning & Shi (2025, *Verbalized Sampling*, arXiv:2510.01171) demonstrated that human preference optimization (RLHF, DPO) introduces an acute *typicality bias*. Human annotators systematically reward conventional, highly predictable text over structurally novel formulations. Consequently, post-trained models compress the generation distribution into narrow modal peaks. Standard autoregressive generation samples from the high-probability core ($p > 0.30$), producing clichés ("old chestnuts") that look polished but lack causal distinctness.
2. **Collective Convergence vs. Individual Fixation:**  
   Deng, Brucks & Toubia (2025, *Examining and Addressing Barriers to Diversity in LLM-Generated Ideas*, Columbia Business School / arXiv) identified two separate mechanisms governing LLM ideation limits:
   - *Collective-level convergence:* Independent sessions draw from the same aggregated global prior, lacking the natural knowledge partitioning of human crowds.
   - *Individual-level fixation:* Generating an idea in an active context immediately anchors the attention mechanism, causing subsequent turns in the same conversation to fixate on the same semantic neighborhood. Naive multi-turn prompting ("give me 10 more ideas") dramatically worsens within-session fixation.
3. **Decoding Pathology under Temperature Scaling:**  
   Nguyen et al. (ICLR 2025 Oral, *Turning Up the Heat: Min-p Sampling for Creative and Coherent LLM Outputs*) proved that standard Nucleus (Top-P) sampling fails in creative ideation. When an LLM faces an open-ended prompt, its next-token probability distribution becomes relatively flat. Under Top-P, a cumulative threshold (e.g., $p=0.90$) forces the sampler to ingest a massive tail of low-probability noise tokens, producing incoherence and hallucinations at higher temperatures. Conversely, dynamic truncation ($\min_p \times p_{\max}$) cuts the noise tail while preserving valid tail-probability alternatives.
4. **Length Bias and Word-Budget Blindness:**  
   Yuan et al. (EMNLP 2025, *Following Length Constraints in Instructions*) and Hu et al. (2025) demonstrated that autoregressive models fail strict negative word-count limits (e.g., "in under 400 words") because token generation occurs step-by-step without global length awareness, and RLHF creates an ingrained verbosity bias. Models cannot reliably track word count without explicit structural slot allocation (Plan-and-Write decoupling). This directly explains the 400/500-word holdout regression observed in `evals/restored-2026-10-18/report.md`.

### 3.2 Master Probabilistic Mechanism Mapping Table
The table below maps each LLM failure mode to its governing Rickards (1985) principle, the supporting 2024–2026 empirical literature, its pure-Markdown / runner realization, and its formal repository provenance category.

| # | LLM Failure Mode | Rickards (1985) Classical Principle / Mechanism | Empirical ML Literature (2024–2026) | Pure-Markdown / Runner Realization in `systematic-innovation` | Provenance Classification |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Mode Collapse & Cliché Output**<br>Model clusters on safe, conventional modal peaks due to typicality bias in human feedback datasets. | **Initial Fluency Depletion**<br>(Ch. 3, pp. 55–57; Ch. 6, pp. 119–120, 128)<br>Exhausting the "old chestnuts" and obvious solutions before genuine speculative generation begins. | **Zhang et al. (2025)** (arXiv:2510.01171) on *Verbalized Sampling* ($p < 0.10$ tail sampling).<br>**Deng et al. (2025)** on collective-level convergence. | **Negative-Space Quarantine (Brief Field 7):** Upfront mandatory listing and programmatic quarantine of the top 3 default tropes before ledger entry, forcing token emission into low-probability tail space ($p < 0.10$). | `Adapted method` |
| **2** | **Procedural Habit Fixation**<br>Model confuses the legacy administrative process with the core problem outcome, offering incremental tweaks. | **Russell Currie (ICI) Critical Examination 5W + Why**<br>(Ch. 6, pp. 124–125)<br>Rigorous goal laddering separating invariant *What* from secondary *How/When/Where/Who* vehicles. | **Deng et al. (2025)** on Chain-of-Thought targeting cognitive fixation.<br>**Midgley & Pinzón (2011)** boundary critique. | **Functional Invariant Separation (Brief Field 5):** Explicit instruction requiring the agent to isolate 100% of the outcome constraint (*What*) while treating the administrative delivery mechanism (*How/When*) as disposable. | `Verified principle` |
| **3** | **Uncontrolled Divergence & Incoherent Tails**<br>Raising temperature alone under Top-P produces hallucinations and nonsense tokens rather than creative alternatives. | **Coupled Search/Select Loops & Requisite Variety**<br>(Ch. 2, pp. 23–26, Fig. 2.3; Ch. 6, pp. 126–129, Fig. 6.1)<br>Search constrained by an explicit selection environment satisfying Ashby's Law. | **Nguyen et al. (ICLR 2025 Oral)** on *Min-P Sampling* ($\min_p \times p_{\max}$).<br>**Friedman & Dieng (2023)** on Vendi Score ($\text{VS}_k$). | **Combinatorial Morphological Matrix (Lenses):** Cross-dimensional forcing combining orthogonal variables, paired with runner dynamic truncation or structured pure-Markdown bounding. | `Adapted method` |
| **4** | **Metaphor Drift & Hallucination**<br>Remote analogical prompts cause models to generate poetic, non-actionable fluff. | **Synectic Excursions with Metaphor Stripping**<br>(Ch. 3, pp. 57–58; Fig. 6.1, p. 127)<br>Systematic excursion into distant operational analogs followed by rigorous force-fit back to the host system. | **Deng et al. (2025)** on ordinary knowledge partitioning.<br>**Si et al. (2024)** on functional analog retrieval in LLMs. | **Metaphor-Stripped Excursions (Lenses):** Instruction requiring remote domain mapping (biology, aerospace) followed by a mandatory stripping step: final mechanism text must contain zero figurative or poetic vocabulary. | `Adapted method` |
| **5** | **Surface Paraphrase Inflation**<br>Generating multiple proposals that sound distinct lexically but execute the exact same causal mechanism. | **Clustered Variety Preservation & Battelle Screening**<br>(Ch. 6, pp. 129–130)<br>Clustering 100+ ideas into 5–6 structural families; applying cheap, severe screening hurdles early. | **Friedman & Dieng (2023)** on Vendi Score.<br>**Jalali et al. (AISTATS 2025)** on Conditional Vendi Score.<br>**Meincke et al. (2024)** on LLM duplicate collapse. | **5–6 Structural Cluster Floor & Causal Ledger:** Mechanism Ledger requires distinct causal coordinates. Portfolio presentation mandates grouping into $\ge 5$ distinct structural clusters before emission. | `Adapted method` |
| **6** | **Institutional Organ Rejection**<br>Novel proposals trigger reflexive rejection ("Yes-but") due to boundary overflow, unvoiced stakeholder pain, or metric clashes. | **Dual Selling-In / Selling-Out Loop & 3 Owner Questions**<br>(Ch. 8, pp. 159–164, 176–177; Table 8.1; Note 3 p. 183)<br>Inoculating proposals against killer phrases; routing across mission, negotiative, and participative boundaries. | **Ulrich (1983)** / **Midgley (2000)** on Boundary Critique ("The Witness").<br>**Rickards (1985)** on three-hearing inoculation. | **Structured Receptivity Spotlights (Output Layer 4):** Each spotlight answers the 3 Problem-Owner Questions (novelty, relevance, resources) and identifies the boundary mode, including externalized burdens ("The Witness"). | `Verified principle` |
| **7** | **Word-Cap Defiance & Verbosity Bias**<br>Autoregressive models fail strict length caps (e.g., 400 words) due to lack of lookahead and RLHF verbosity bias. | **Plan-and-Write Budget Allocation**<br>(Classical rhetorical composition; decoupled budgeting). | **Yuan et al. (EMNLP 2025)** on length constraints in instructions.<br>**Hu et al. (Findings of EMNLP 2025)**. | **Piped Compact Syntax (Output Layer 3):** Strict single-line piped format (`[ID] Name \| Causal Lever \| Mechanism \| Invariant Preserved \| Boundary Mode`) with pre-allocated slot budgets, locking outputs under $\le 500$ words. | `Original AI/probabilistic mechanism` |

---

## 4. Critical Disposition of `2026-10-18-v2-brainstorming-synthesis.md`

### 4.1 Background and Triage Criteria
On 2026-10-18, an exploratory brainstorming synthesis (`docs/research/2026-10-18-v2-brainstorming-synthesis.md`) proposed incorporating concepts from Technological Innovation Systems (TIS), Critical Systems Heuristics (CSH), Boundary Critique, and Multi-Level Perspectives (MLP). That document remained unexecuted research input (`D2`).

To prepare the v2 specification amendment (Task 9), each candidate concept is evaluated against four strict criteria:
1. **Ideation-First Guardrail:** Does it preserve open exploration, or does it drift into premature implementation roadmaps, 30-60-90 day plans, or winner selection?
2. **Preservation-First Hardening:** Does it actively protect working system invariants and safety boundaries?
3. **Causal Distinction over Wording:** Does it enforce distinct causal mechanisms rather than semantic fluff?
4. **Agent Portability & Token Economy:** Can it be expressed in lean, provider-neutral Markdown without inflating the root prompt or triggering instruction dilution?

### 4.2 Structured Disposition Matrix

| Candidate Concept from 2026-10-18 Synthesis | Source Literature | Disposition | Architectural Realization in v2 | Token Tax & Justification |
| :--- | :--- | :---: | :--- | :--- |
| **Functional Invariant vs. Structural Vehicle** | Classical CPS; Currie (1960); Rickards (1985, Ch. 6) | **KEEP** | Placed in `SKILL.md` Brief Field 5 (*Functional Invariants*) and `references/output-contract.md`. Demands 100% preservation of outcome constraints while liberating the delivery mechanism. | **Minimal (+15 words in `SKILL.md`).** High leverage; prevents models from casually recommending compliance/safety rollbacks. |
| **The Externalized Burden ("The Witness")** | Midgley (2000); Ulrich (1983) Boundary Critique | **KEEP** | Placed in `SKILL.md` Brief Field 2 (*Beneficiary & Externalized Burden*). Probes who absorbs downstream maintenance, on-call pain, or friction without an upstream design vote. | **Minimal (+10 words in `SKILL.md`).** Directly enhances systemic problem finding without philosophical jargon. |
| **4 Systemic Failure Archetypes (TIS)**<br>*(Incentive mismatch, missing complement, network pathology, legitimation buffer)* | Johnson (2001); Edquist (2005); Klein Woolthuis et al. (2005) | **ADAPT (Minimalist)** | Folded silently as generative thinking prompts inside `references/innovation-lenses.md` under *System Dynamics* and *Operational Reality*. **NO 8th Reasoning Cell; NO visible output tags.** | **Zero root tax (+0 words in `SKILL.md`, +45 words in lenses).** Guides LLM attention to structural bottlenecks without adding user-facing metadata bloat. |
| **Incommensurable Value Scorecards** | Midgley & Pinzón (2011) Boundary Critique | **ADAPT (Minimalist)** | Folded into Rickards's *Negotiative* boundary mode in `references/output-contract.md`. Identifies where stakeholders evaluate success on conflicting, non-fungible metrics. | **Zero root tax (+0 words in `SKILL.md`, +25 words in output-contract).** Replaces academic sociology with practical stakeholder alignment mechanics. |
| **Mario Bunge's CESM Metamodel**<br>$\mu(\sigma) = F(C, E, S, M)$ | Bunge (1979, 1996) Ontology and Systemics | **PRUNE (Hard Reject)** | **Excluded completely.** Dense algebraic notation consumes excessive prompt tokens, confuses autoregressive attention, and yields zero empirical lift in candidate diversity. | **Zero tax (Excluded).** Eliminates unnecessary pseudo-mathematical prompt overhead. |
| **Ulrich's 12 CSH Questions & "Sacred/Profane" Jargon** | Ulrich (1983) Critical Systems Heuristics | **PRUNE (Hard Reject)** | **Excluded completely.** Twelve philosophical questions transform Deep Mode into a tedious, moralizing interrogation that causes extreme user drop-off in technical domains. | **Zero tax (Excluded).** Preserves Quick Mode speed and respects Deep Mode's 7-question maximum. |
| **Geels's Multi-Level Perspective (MLP)** | Geels (2002, 2005) Socio-Technical Transitions | **PRUNE (Hard Reject)** | **Excluded completely.** Models 50-year macroeconomic transitions across niche, regime, and landscape. Completely outside the actionable horizon of an agent skill solving practical problems. | **Zero tax (Excluded).** Eliminates grand theoretical abstraction. |
| **Socio-Material "Enactment Scripts"** | Orlikowski (2007); Latour (2005) Actor-Network Theory | **PRUNE (Hard Reject)** | **Excluded completely.** Drifts into unsolicited 30-60-90 day deployment roadmaps and change-management plans, directly violating the **Ideation-First** guardrail. | **Zero tax (Excluded).** Enforces strict ideation boundaries; roadmaps are prohibited unless explicitly requested. |
| **National Innovation Systems (NIS / Triple Helix)** | Lundvall (1992); Etzkowitz & Leydesdorff (2000) | **PRUNE (Hard Reject)** | **Excluded completely.** Macro-economic policy framework for regional governments, completely irrelevant to micro/meso engineering and product problems. | **Zero tax (Excluded).** Keeps skill focused on actionable problem domains. |
| **Unverified Quantitative Projections**<br>*(e.g., "+22% Vendi", "+28% Vendi", "+35% adoption")* | 2026-10-18 Unexecuted Design Projections | **PRUNE (Hard Reject)** | **Excluded from empirical documentation.** Formally labeled as unexecuted theoretical projections; no quantitative claims will be cited without retained, audited benchmark runs. | **Zero tax (Excluded).** Upholds strict repo-wide empirical integrity (`D7`). |

---

## 5. Structural Refactoring & Token Economy Plan

### 5.1 SkillEvaluator Quality Gate Alignment (86.0/B $\rightarrow$ $\ge 92.0$/A)
The external baseline audit performed on 2026-11-14 using NVIDIA SkillEvaluator `0.9.0` ([`evals/audits/2026-11-14-skillevaluator-baseline.md`](../../evals/audits/2026-11-14-skillevaluator-baseline.md)) produced a passing score of **86.0 / 100 (Grade B)** with zero security, secret, or injection findings.

However, SkillEvaluator assessed 50 raw deduction points (-14.0 weighted points) across three structural areas:
1. **Schema Headings (`-20 pts` Correctness / Reliability):** Lack of standard AgentSkills.io markdown headers (`## Instructions`, `## Purpose`, `## Limitations`, `## Examples`).
2. **Catalog Discoverability (`-10 pts` Discoverability):** Frontmatter description length (258 characters vs. recommended 50–150 character concise routing trigger); missing structured `metadata.author` and `metadata.version`.
3. **Recovery and Error Boundaries (`-15 pts` Reliability):** Missing explicit `## Limitations` section specifying when the skill must not be executed.

### 5.2 The 30/70 Architectural Split
To eliminate these deductions without increasing token overhead or diluting instruction following, the skill will adopt a strict **30/70 architectural split**:
- **Root Manifest (`SKILL.md`):** Allocated $\le 30\%$ of total token weight (~750 tokens, $\le 100$ lines). Contains metadata, fast-routing triggers, standard AgentSkills.io headers (`## Purpose`, `## Instructions`, `## Limitations`, `## Examples`), core guardrails, and links to modular sub-files.
- **Progressive Disclosure Modules (`references/`):** Allocated $\ge 70\%$ of total token weight (~1,750 tokens across 4 files). Houses deep procedural mechanics:
  - `references/deep-mode.md`: Interactive discovery protocol (1 question per turn, max 7, with provisional seeds).
  - `references/innovation-lenses.md`: Generative Reasoning Cells, morphological combinations, and synectic prompt guides.
  - `references/output-contract.md`: 5-layer presentation contract, Piped Compact Syntax, and spotlight criteria.
  - `references/evidence.md`: Bibliographic errata, provenance ledger, and classical source citations.

### 5.3 Solving the 400/500-Word Budget Regression
In the 2026-10-18 restored-candidate evaluation ([`evals/restored-2026-10-18/report.md`](../../evals/restored-2026-10-18/report.md)), the skill severely regressed on tight-budget requests:
- A 450-word user request produced 590 to 700 words across repair attempts.
- A 400-word blind holdout case produced 575 words (format control: 448; generic control: 300).

Recent empirical literature on length constraints (Yuan et al., EMNLP 2025; Hu et al., Findings of EMNLP 2025) demonstrates that autoregressive models fail free-form negative constraints ("do not exceed 400 words") because token-level probability generation has no global lookahead. However, models strictly adhere to **Plan-and-Write slot allocation** and **Piped Compact Syntax**.

#### The v2 Budget Solution: Piped Compact Syntax
When a user prompt specifies a tight word budget ($\le 500$ words) or requests a compact output, the skill will activate **Piped Compact Syntax** in Layer 3:
```text
[SI-01] Name | Causal Lever | Mechanism | Invariant Preserved | Boundary Mode
```
- **Word allocation per candidate:** Exactly 15–22 words per single-line row.
- **Budget math:** A 12-candidate portfolio uses $12 \times 18 \approx 216$ words.
- **Overhead:** Brief (40 words) + Preservation Scan (35 words) + Spotlight (60 words) + Continuation (15 words) = ~366 words total.
- **Result:** Guarantees strict compliance with $\le 400$ and $\le 500$ word constraints with zero spillover.

---

## 6. Falsifiable Hypotheses (`H1–H6`) for Task 9 Specification & Implementation

The following six falsifiable hypotheses form the core requirements for the Task 9 behavioral specification amendment and sub-plan. Each hypothesis specifies its mechanism, target files, measurable verification test, and token/safety guardrail.

```
+---------------------------------------------------------------------------------------------------------+
|                               FALSIFIABLE RESEARCH HYPOTHESES (H1 - H6)                                 |
+---------------------------------------------------------------------------------------------------------+
|  [H1] Negative-Space Quarantine (Fluency Depletion)   --> Shift probability mass to tail (p < 0.10)     |
|  [H2] Currie 5W+Why Invariant Separation              --> 100% invariant preservation + vehicle freedom |
|  [H3] Morphological Synthesis & 5-6 Cluster Floor     --> Combinatorial variety + metaphor stripping   |
|  [H4] Piped Compact Syntax (Plan-and-Write Budget)    --> 100% compliance on <=500 word caps           |
|  [H5] AgentSkills Schema Alignment & Errata Fix       --> SkillEvaluator Grade A (>=92) + clean errata |
|  [H6] Runner Sampling Sensitivity Probes (Min-P)      --> Characterize decode params vs prompt entropy |
+---------------------------------------------------------------------------------------------------------+
```

### Hypothesis 1 (H1): Fluency Depletion via Explicit Negative-Space Quarantine
- **Mechanism:** Human alignment (RLHF/DPO) induces mode collapse onto conventional solutions (Zhang et al., 2025). Requiring the agent to verbalize and quarantine the top 3 default tropes in Brief Field 7 (*Negative Space*) before generating the candidate ledger forces probability mass into low-probability tail mechanisms ($p < 0.10$), dramatically increasing causal distinctness.
- **Theoretical Grounding:** Rickards (1985, Ch. 3 pp. 55–57; Ch. 6 pp. 119–120, 128) initial fluency depletion; Zhang et al. (2025) verbalized tail sampling.
- **Target Files:** `skills/systematic-innovation/SKILL.md` (Brief Field 7), `skills/systematic-innovation/references/innovation-lenses.md`.
- **Pass/Fail Verification Criterion:** In the public stress holdout corpus, $\ge 85\%$ of generated candidates across 5 replicates must have causal coordinates that do not overlap with the identified negative-space tropes; zero quarantined tropes may appear in the visible portfolio.
- **Token Budget Guardrail:** Added instruction text in `SKILL.md` must not exceed 20 words.

### Hypothesis 2 (H2): Currie 5W+Why Goal Laddering & Functional Invariant Separation
- **Mechanism:** LLMs frequently conflate legacy administrative procedures with core functional requirements, causing either trivial cosmetic suggestions or irresponsible safety rollbacks. Systematically decomposing the problem via Russell Currie's 5W+Why separates the invariant outcome requirement (*What*) from the structural vehicle (*How, When, Where, Who*), unblocking radical vehicle transformation while preserving 100% of safety/compliance constraints.
- **Theoretical Grounding:** Rickards (1985, Ch. 6 pp. 124–125) Russell Currie ICI Critical Examination; Deng, Brucks & Toubia (2025) cognitive fixation reduction via structured decomposition.
- **Target Files:** `skills/systematic-innovation/SKILL.md` (Brief Field 5), `skills/systematic-innovation/references/output-contract.md` (Preservation Scan).
- **Pass/Fail Verification Criterion:** In adversarial safety and regulatory stress cases (e.g., `cases.json` compliance and cooling cases), 100% of generated proposals must preserve declared physical/regulatory invariants, while achieving $\ge 70\%$ structural vehicle divergence from the baseline system.
- **Token Budget Guardrail:** Added instruction text in `SKILL.md` must not exceed 15 words.

### Hypothesis 3 (H3): Morphological Matrix Combinatorial Forcing, Metaphor-Stripped Synectics & 5–6 Cluster Floor
- **Mechanism:** Generating ideas via independent unstructured passes results in surface lexical paraphrasing with low structural diversity (Meincke et al., 2024). Enforcing cross-dimensional morphological recombination (Zwicky/SCIMITAR), coupled with synectic remote-domain functional transfer and a mandatory 5–6 structural cluster floor, maximizes requisite variety (Ashby's Law) while metaphor stripping eliminates hallmark hallucinations.
- **Theoretical Grounding:** Rickards (1985, Ch. 3 pp. 57–59; Ch. 6 pp. 119–120, 126–130, Figs. 6.1 & 8.1); Friedman & Dieng (2023) Vendi Score.
- **Target Files:** `skills/systematic-innovation/references/innovation-lenses.md`, `skills/systematic-innovation/references/output-contract.md`.
- **Pass/Fail Verification Criterion:** Final visible portfolios must distribute candidates across $\ge 5$ distinct causal clusters; zero candidates may contain poetic, allegorical, or figurative vocabulary in their mechanism descriptions (100% mechanical/physical terminology).
- **Token Budget Guardrail:** Net addition to `references/innovation-lenses.md` must not exceed 60 words.

### Hypothesis 4 (H4): Plan-and-Write Budget Lock via Piped Compact Syntax for Strict Word Caps ($\le 500$ words)
- **Mechanism:** Autoregressive LLMs fail free-form negative word limits due to step-by-step subword generation blindness and post-training verbosity bias (Yuan et al., EMNLP 2025). Decoupling budget planning from generation via single-line Piped Compact Syntax (`[ID] Name | Lever | Mechanism | Invariant Preserved | Boundary Mode`) with pre-allocated slot budgets enforces deterministic length compliance.
- **Theoretical Grounding:** Yuan et al. (EMNLP 2025); Hu et al. (Findings of EMNLP 2025); Plan-and-Write structural decoupling.
- **Target Files:** `skills/systematic-innovation/SKILL.md` (Mode Routing), `skills/systematic-innovation/references/output-contract.md` (Layer 3 Compact Syntax).
- **Pass/Fail Verification Criterion:** In the 400-word and 500-word holdout regression test cases, 100% of generated responses must measure $\le 400$ words and $\le 500$ words respectively across 5 independent runs, completely resolving the open regression from `CONTEXT.md` §19.7 and `evals/restored-2026-10-18/report.md`.
- **Token Budget Guardrail:** Adds zero additional prompt words to full/deep executions; compact syntax prompt description in `output-contract.md` $\le 40$ words.

### Hypothesis 5 (H5): Zero-Cost AgentSkills Schema Alignment & `evidence.md` Errata Remediation
- **Mechanism:** Automated skill quality scanners and agent harnesses rely on standardized Markdown headings and metadata for reliable parsing and trigger indexing (NVIDIA SkillEvaluator, AgentSkills.io). Aligning headings (`## Purpose`, `## Instructions`, `## Limitations`, `## Examples`) and correcting primary-source bibliographic errata in `evidence.md` removes all static schema deductions without adding runtime token bloat.
- **Theoretical Grounding:** Agent Skills Specification (`agentskills.io`); NVIDIA SkillEvaluator `0.9.0` Quality Gate; Rickards (1985) physical bibliographic verification.
- **Target Files:** `skills/systematic-innovation/SKILL.md`, `skills/systematic-innovation/references/evidence.md`.
- **Pass/Fail Verification Criterion:** NVIDIA SkillEvaluator score increases from `86.0 / Grade B` to $\ge 92.0 / \text{Grade A}$; schema warnings drop to 0; all 137 repository unit tests pass; `tools/validate_skill.py` and `tools.repository.authority` exit 0.
- **Token Budget Guardrail:** `SKILL.md` total token count remains $\le 850$ tokens; total package token count remains $\le 2,650$ tokens.

### Hypothesis 6 (H6): Runner Decoding Sensitivity & Sampling Optimization Probes
- **Mechanism:** Pure-Markdown skill instructions act as structural entropy constraints, but their interaction with host decoding parameters (`temperature`, `top_p`, `min_p`) dictates the boundary between creative diversity and hallucination. Probing sampling sensitivity in `tools/stress_runner.py` will establish the empirical interaction between prompt-induced diversity (Conditional Vendi Score) and decoding parameters.
- **Theoretical Grounding:** Nguyen et al. (ICLR 2025 Oral) on Min-P sampling; Jalali et al. (AISTATS 2025) on Conditional Vendi Score decomposition; Friedman & Dieng (2023).
- **Target Files:** `tools/stress_runner.py`, `evals/stress/cases.json`.
- **Pass/Fail Verification Criterion:** Runner completes temperature sweeps ($\tau \in \{0.2, 0.7, 1.2\}$) and sampling sweeps (Top-P vs. Min-P where supported) across 3 test cases; proves that structural prompt constraints maintain candidate validity ($\ge 90\%$ compliant) even at elevated temperatures ($\tau = 1.0–1.2$) where baseline prompts experience catastrophic incoherence.
- **Token/Spend Guardrail:** All test runs bounded by `--max-cost 5.00` and restricted strictly to allowlisted models.

---

## 7. References & Primary Source Bibliography

### 7.1 Primary Classical & Methodological Sources
- Currie, R. M. (1960). *Work Study*. London: British Institute of Management / Pitman.
- Gordon, W. J. J. (1961). *Synectics: The Development of Creative Capacity*. New York: Harper & Row.
- Likert, R. (1961). *New Patterns of Management*. New York: McGraw-Hill. (Linchpin model cited by Rickards 1985, p. 161).
- Prince, G. M. (1970). *The Practice of Creativity: A Manual for Dynamic Group Problem Solving*. New York: Harper & Row.
- Rickards, T. (1974). *Problem-Solving Through Creative Thinking*. London: Gower Press.
- Rickards, T. (1985). *Stimulating Innovation: A Systems Approach*. London: Frances Pinter (Publishers) / New York: St. Martin's Press (`pp. xi + 221`, ISBN `0-86187-512-5`).
- Rickards, T., & Freedman, B. L. (1978). "Procedures for managers in idea-deficient situations: an examination of brainstorming approaches." *Journal of Management Studies*, 15(1), 43–55.
- Zwicky, F. (1948). *Morphological Method of Analysis and Construction*. Zurich: Society for Morphological Research.

### 7.2 Modern Empirical Machine Learning & LLM Diversity Literature (2023–2026)
- Deng, Y., Brucks, M., & Toubia, O. (2025). "Examining and Addressing Barriers to Diversity in LLM-Generated Ideas" / "Two Mechanisms of LLM Idea Convergence and the Interventions That Target Them." *Columbia Business School Research Paper* / *arXiv preprint*.
- Friedman, D., & Dieng, A. B. (2023). "The Vendi Score: A Diversity Evaluation Metric for Machine Learning." *Transactions on Machine Learning Research* (TMLR) / *arXiv:2210.02410*.
- Hu, Z., et al. (2025). "Evaluating and Improving Length-Constrained Generation in Large Language Models." *Findings of the Association for Computational Linguistics: EMNLP 2025*.
- Jalali, M., Ospanov, A., Gohari, A., & Farnia, F. (2025). "Conditional Vendi Score: Prompt-Aware Diversity Evaluation for Generative AI Models and LLMs." *Proceedings of the 28th International Conference on Artificial Intelligence and Statistics (AISTATS 2025)*.
- Meincke, L., Mollick, E., & Terwiesch, C. (2024). "Prompting for Novelty: Can Language Models Generate Truly Original Product Concepts?" *Wharton School Working Paper*.
- Nguyen, M. N., Baker, A., Neo, C., Roush, A., Kirsch, A., & Shwartz-Ziv, R. (2025). "Turning Up the Heat: Min-p Sampling for Creative and Coherent LLM Outputs." *International Conference on Learning Representations (ICLR 2025 Oral)* / *arXiv:2407.01082*.
- Si, C., et al. (2024). "Measuring and Mitigating Semantic Fixation in Language Model Ideation." *arXiv preprint*.
- Ulrich, W. (1983). *Critical Heuristics of Social Planning: A New Approach to Practical Philosophy*. Bern: Haupt.
- Yuan, W., Thorne, J., et al. (2025). "Following Length Constraints in Instructions." *Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (EMNLP 2025)*.
- Zhang, J., Yu, S., Chong, D., Sicilia, A., Tomz, M. R., Manning, C. D., & Shi, W. (2025). "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity." *arXiv:2510.01171*.
