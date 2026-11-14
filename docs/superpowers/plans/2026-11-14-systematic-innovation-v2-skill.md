# Systematic Innovation v2 Skill Enhancement Plan & Behavioral Spec Amendment

> **Status:** Completed — approved by owner on 2026-11-14 (**Part I A1–A9** + **Part II** + bounded `codex exec` paired evaluation scope); verified in [`evals/v2-loop/report.md`](../../../evals/v2-loop/report.md).

**Goal:** Upgrade the canonical markdown skill (`skills/systematic-innovation/`) to counter RLHF/DPO typicality collapse, lock tight output-budget adherence (`<= 500` words), eliminate Rickards (1985) primary-source pagination errors, achieve `SkillEvaluator` Grade A (`>= 92/100`), and verify gains empirically via bounded paired evaluations (`evals/v2-loop/`).

**Grounded Evidence:**
- [Phase B SkillEvaluator Baseline](../../../evals/audits/2026-11-14-skillevaluator-baseline.md) (`86.0 / Grade B`, 15 findings, 0 security findings).
- [Phase C Dual-Track Synthesis](../../research/2026-11-14-probabilistic-creativity-synthesis.md) (Tudor Rickards 1985 physical scan verification + peer-reviewed 2023–2025 probabilistic diversity literature; verified citations only).

---

## Part I: Proposed v2 Behavioral Spec Amendment

**Target Document:** [`docs/superpowers/specs/2026-08-31-systematic-innovation-design.md`](../specs/2026-08-31-systematic-innovation-design.md)  
**Context Ledger Entry:** Record owner approval as **`§19.9 V2 Behavioral Spec Amendment (2026-11-14)`** in [`CONTEXT.md`](../../../CONTEXT.md).

All approved contracts remain intact unless refined below: **Layer 1–6 disclosure headings**, **Quick (10–15) and Deep (15–24) targets (not quotas)**, **Execution-Channel Precedence (§6.4)**, **Preservation-First & Cumulative Preserve Ledger**, **Ideation-Only & No-Fake-Compliance guardrails**, **High-Stakes safety floor**, and **Provider-Neutral markdown-only packaging (§16)**.

### A1. Amend §5 Step 5 & §10 — Two-Stage Anti-Typicality Tail Sampling (`H1`)
Add to **§10 (Innovation Lenses)** after the existing initial-fluency sentence (line 229):

> **Anti-Typicality Two-Stage Protocol:** Before recording entries in the Mechanism Ledger, explicitly articulate and quarantine the 2–3 highest-probability modal tropes in Layer 1 (*Negative-Space Trope Quarantine*). Do not allow any numbered portfolio candidate to share a core causal mechanism or verb-object dynamic with a quarantined trope. Sample candidate generation across distinct regions of the conditional outcome space (tail-distribution exploration) rather than paraphrases around the mode, keeping verbalized diversity cues implicit or lightweight in user-facing formatting unless requested.

### A2. Amend §8 & §11 — Currie `5W+Why` Invariant/Vehicle Separation (`H3`)
Add to **§8 (System and Stuckness Map)** and **§11 (Mechanism Ledger)** right after the preservation and causal-difference rules:

> **Invariant vs. Legacy-Vehicle Separation:** Distinguish each preserved system invariant (*what* function, safeguard, value, or constraint must remain intact) from its incidental delivery vehicle (*which* habit, form, role, or artifact currently carries it). Preserving an invariant never requires preserving a broken delivery vehicle, and every candidate `Preserve check` must verify compliance at the underlying invariant and resource-demand level.

### A3. Amend §9 & §10 — Metaphor-Stripped Excursions & Combinatorial Forcing (`H2`)
Add to **§10 (Innovation Lenses)**:

> **Metaphor-Stripped Mechanism Transfer:** Any synectic or outside-domain transfer must map an explicit two-node abstract causal or dependency structure (actors, flow, bottleneck, feedback) between source and target domains and strip source-domain jargon before generating the candidate. Domain labels without structural isomorphism are invalid transfers.
>
> **Morphological 2x2 Forcing & Liability-to-Asset Reversal:** When contrasting dimensions stagnate or constraints tighten, cross at least two independent structural axes (e.g., intervention stage × incentive/burden carrier) to force non-default cells, and test reversing stated bottlenecks or liabilities into operational signals or buffers inside the safe constraint envelope.

### A4. Amend §12 — Clustered Variety Preservation Floor (`H3`)
Add to **§12 (Saturation and Portfolio Balance)** before `§12.1`:

> **Clustered Variety Floor:** For standard non-budget-limited runs, cells should avoid premature stopping before exploring at least five distinct causal clusters across at least two Reasoning Cells (or until genuine domain saturation is demonstrated and explained). Within distinct clusters, retain promising rough variants until the duplicate test confirms whether two mechanisms are structurally identical. Under explicit hard user budgets (`§12.1`), budget ceilings still take precedence over cluster floors.

### A5. Amend §12.1 & §13.3 — Deterministic Piped Compact Syntax (`H5`)
Refine **§12.1 (User-requested output budgets)** and **§13.3 (Layer 3: Complete Portfolio)**:

> **Piped Compact Portfolio Format (`<= 500` words):** When an explicit ceiling of 500 words or fewer applies, render `L1:`, `L2:`, `P1:`..`Pn:`, `L4:`, `L5:`, and `L6:` as compact plain-text lines targeting 80% of the ceiling. Each compact candidate line uses colon-keyed piped fields (`P1: <Name> | Lever: <...> | Intervention: <...> | Chain: <X -> Y -> Z> | Preserve: <all L1 invariants / delta> | Failure: <...> | Fit: <mode + safeguard>`) with pre-allocated slot budgets (`L1+L2 <= 15%`, `P1..Pn <= 50%`, `L4+L5+L6 <= 15%`, 20% safety reserve) so deterministic metrics and preservation checks still parse cleanly without exceeding the word limit.

### A6. Amend §14 — Dual Selling-In / Selling-Out Receptivity (`H4`)
Refine **§14 (Receptivity and Light Decision Support)** paragraph 2:

> **Dual Selling-In / Selling-Out & *Yes-But* Safeguards:** Each spotlighted possibility evaluates both **Selling-In** (what internal champion, governance gate, or resource holder gets protected or gained to permit trial) and **Selling-Out** (what end-beneficiary, partner, or external stakeholder experiences as immediate legible value), paired with the Three Problem-Owner Questions (*new to owner*, *mission relevant*, *resource actionable*) and a specific structural safeguard answering the strongest *Yes-but* rejection reflex.

### A7. Amend §16 — Standard Section Headings & 30/70 Progressive Disclosure (`Task 7 + H5`)
Add to **§16 (Discovery and Portability)**:

> **Package Structure & Progressive Disclosure:** `skills/systematic-innovation/SKILL.md` declares recommended open-standard frontmatter (`name`, `version`, concise 50–150 character trigger `description`, `license`, and `metadata.author` / `metadata.tags`), organizes the core operational contract into clear top-level sections (`Purpose`, `Prerequisites`, `Instructions`, `Examples`, `Limitations`, `Troubleshooting`, and conditional `Reference Navigation`), uses direct provider-neutral wording without corporate filler terms, and keeps deep worked taxonomy, discovery mechanics, full six-layer contracts, and bibliographic records in `references/` so initial context load stays lean (~30/70 split).

### A8. Amend §18 — Measurement-Only Runner Sampling Instrumentation (`H6`)
Add to **§18 (Benchmark Experimental Conditions)**:

> **Harness-Only Configuration Sensitivity Probes:** The local benchmark adapter (`tools/stress_runner.py`) may pass optional invocation configuration flags (such as reasoning effort or sampling overrides via CLI passthrough) strictly for controlled paired measurement comparisons. No CLI flags, provider names, or model-specific tuning directives belong inside `skills/systematic-innovation/`.

### A9. Primary-Source Bibliographic Errata Closure
Correct Rickards (1985) chapter and figure pagination in `references/evidence.md` against the verified physical volume scan (`Ch. 3 p. 33`, `Ch. 4 p. 63`, `Ch. 5 p. 87`, `Ch. 6 p. 114`, `Fig. 6.1 pp. 126–127`, `Ch. 7 p. 135`, `Fig. 7.2 p. 142`, `Ch. 8 p. 158`, `Fig. 8.1 p. 161`, `Ch. 9 pp. 184–201`), remove the non-existent `Appendix (p. 190)` entry (replacing with verified `Bibliography pp. 202–214` and `Index pp. 215–221`), and add only directly verified 2023–2025 academic citations (`Zhang et al. 2025`, `Deng, Brucks & Toubia 2025`, `Friedman & Dieng 2023`, `Nguyen et al. ICLR 2025`, `Yuan et al. EMNLP 2025`, `Hu et al. EMNLP 2025 Findings`) without copying source prose.

---

## Part II: Concrete File-Level Implementation Sub-Plan (TDD)

**Architectural Invariants to Preserve Across All Existing Tests (`137` passing):**
- `tests/test_stress_runner.py` regexes in `SKILL.md`: preserve literal phrases `**10 to 15 distinct possibilities** in one turn` and `synthesize **15 to 24 distinct possibilities**`.
- `tests/test_skill_behavior.py`: preserve all tested anchors (`Execution-Channel Precedence`, `Hard Output Budget Precedence`, `80% of the requested ceiling`, all 8 Brief fields, all 7 Reasoning Cells, `### Layer 1: Innovation Brief` .. `### Layer 6: User-Directed Continuation`, `Contradiction & Boundary Re-Anchor`, `Quantitative disconfirmation threshold` / `Only when the user explicitly requests experiments`, `Ch. 4`, `offline`, `exploratory`, `verification needs`, `critical unknown`, etc.).
- `tools/validate_skill.py`: zero provider tokens (`claude|codex|cursor|antigravity|pi|gemini|gpt|openai|anthropic|copilot`) anywhere in `skills/systematic-innovation/`.
- `tools/pilot_metrics.py`: compact piped template MUST use `P1:` + `FIELD_ALIASES` keys (`Lever:`, `Intervention:`, `Chain:`, `Preserve:`) so `_extract_p_candidate_blocks` / `_extract_compact_candidates` and `detect_preservation_violations` parse without code breakage.

### Milestone 1: Spec & Governance Sign-Off *(after owner approves Part I)*
- **Files:** `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md`, `CONTEXT.md`
- **Action:** Apply Amendments `A1`–`A9` to the approved behavioral spec and append `§19.9` record to `CONTEXT.md`.

### Milestone 2: Failing Tests First (`RED`)
- **Files:** `tests/test_skill_structure.py`, `tests/test_skill_behavior.py`, `tests/test_stress_runner.py`
- **New Tests (must fail before Milestone 3/4 edits):**
  1. `test_skill_frontmatter_meets_v2_metadata_and_concise_trigger_contract` (`tests/test_skill_structure.py`): verifies `version`, `license`, `metadata` author/tags presence, and `50 <= len(description) <= 150`.
  2. `test_skill_v2_probabilistic_and_skillevaluator_sections` (`tests/test_skill_behavior.py`): checks `SKILL.md` contains `## Purpose`, `## Prerequisites`, `## Instructions`, `## Examples`, `## Limitations`, `## Troubleshooting`, fenced code block example, zero SkillEvaluator corporate filler tokens (`utilize`, `facilitate`, `leverage`, `paradigm`, `synergy`), Negative-Space Trope Quarantine + tail-distribution cue (`H1`), Currie invariant/vehicle split (`H3`), and Selling-In/Selling-Out (`H4`).
  3. `test_output_contract_and_lenses_v2_mechanisms` (`tests/test_skill_behavior.py`): verifies metaphor-stripped 2-node transfer & 2x2 morphological forcing (`H2`), `>= 5` clustered variety floor (`H3`), piped compact syntax (`Lever:` / `Intervention:` / `Chain:` / `Preserve:`) parsed cleanly by `tools/pilot_metrics.py` (`H5`), and dual Selling-In/Selling-Out spotlight fields (`H4`).
  4. `test_evidence_rickards_1985_pagination_and_no_fabricated_appendix` (`tests/test_skill_behavior.py`): asserts verified chapter page starts (`p. 33`, `p. 63`, `p. 87`, `p. 114`, `Fig. 8.1` `p. 161`, `Ch. 9` `p. 184`) and absence of the fabricated `Appendix: Techniques` (`p. 190`) and inaccurate legacy start pages (`p. 28`, `p. 92`, `p. 131`, `p. 166`, `p. 176`).
  5. `test_stress_runner_supports_codex_config_passthrough` (`tests/test_stress_runner.py`): verifies optional `--codex-config` / `-c` passthrough in `build_initial_command` and resume commands (`H6`).
- **Verification (`RED`):** Run `python3 -m unittest discover tests` and confirm the 5 new tests fail for the expected missing v2 features.

### Milestone 3: Canonical Skill & Reference Upgrades (`GREEN`)
- **File 1: `skills/systematic-innovation/SKILL.md`** (target ~1,150–1,350 words; <= 150-char description):
  - Frontmatter: add `version: "2.0.0"`, concise `<= 150`-char `description`, `license: MIT`, `metadata.author`, `metadata.tags`.
  - Sections aligned to both operational flow and `SkillEvaluator`:
    - `## Purpose` (Core Principle + Anti-Typicality + When Not to Trigger).
    - `## Prerequisites` (host research/subagent awareness vs full `offline` zero-dependency mode).
    - `## Instructions` (Mode Routing table preserving exact regex strings; Execution-Channel Precedence; Hard Output Budget Precedence + Piped Compact Syntax trigger; Innovation Brief + Currie `what`/vehicle separation + Negative-Space Default-Trope Quarantine `H1`; Cumulative `Preserve:` ledger; 7 Reasoning Cells + Metaphor-Stripped Transfer & 2x2 Morphological / Liability-to-Asset cues `H2`; Clustered Variety `5–6` cluster floor `H3`; `Reference Navigation` links).
    - `## Examples` (compact fenced ```text Piped Compact Syntax `L1:`/`L2:`/`P1:`/`P2:`/`L4:`/`L5:`/`L6:` exemplar + Deep Turn-1 1-question + 2-seed exemplar, zero fake stats).
    - `## Limitations` (Ideation-Only, No Fabricated Stats, High-Stakes `exploratory` + `verification needs`, measurement scope).
    - `## Troubleshooting` (Error/Cause/Solution table for Contrasting Impossibility, Budget Ceiling Overrun, Single-Turn Deep Conflict, Premature Mode Collapse).
  - Replace all occurrences of `"leverage"` / corporate buzzwords in `SKILL.md` with clear active phrasing (`"control points"`, `"high-impact points"`, `"use"`).
- **File 2: `skills/systematic-innovation/references/innovation-lenses.md`** (~650 words):
  - Upgrade §1 to Two-Stage Anti-Typicality Protocol (`H1`: verbalized tail-space exploration + strict rejection of variants reusing any quarantined verb+mechanism).
  - Add 2-node abstract dependency mapping rule for `Mechanism Transfer` (`H2`), explicit 2x2 independent-axis morphological matrix & `Liability-to-Asset Reversal` (`H2`), Currie `5W+Why` invariant vs legacy-vehicle audit inside §5 (`H3`), and clustered `>= 5` cluster saturation rule inside §4 (`H3`).
- **File 3: `skills/systematic-innovation/references/output-contract.md`** (~950–1,050 words):
  - Upgrade `Compact Portfolio Template` (`<= 500` words) to strict colon-keyed Piped Compact Syntax (`P1: <Name> | Lever: <...> | Intervention: <...> | Chain: <X -> Y -> Z> | Preserve: <...> | Failure: <...> | Fit: <...>`) compatible with `tools/pilot_metrics.py` + `<= 15%/50%/15%/20%` slot allocation (`H5`).
  - Keep all `Layer 1`–`Layer 6` headings intact; integrate **Dual Selling-In / Selling-Out** + Three Problem-Owner Questions + stronger *Yes-but* causal safeguard inside `Layer 4` (`H4`).
- **File 4: `skills/systematic-innovation/references/deep-mode.md`** (~500 words):
  - Add Currie invariant-vs-vehicle probe phrasing to Target Four High-Leverage Unknowns (`H3`) and ensure Turn-1/2 contrast seeds span non-overlapping mechanisms (`H1`/`H2`).
- **File 5: `skills/systematic-innovation/references/evidence.md`** (~750 words):
  - Fix all Rickards (1985) TOC chapter/figure pagination and delete the fabricated `Appendix (p. 190)` (`pp. 184–201` Ch. 9, `pp. 202–214` Bibliography, `pp. 215–221` Index).
  - Add verified Rickards (1985) page citations (`pp. 48–49, 53, 55–59, 119–120, 124–125, 128–130, 160–164, 176–177`) and verified Table D/E academic entries (`Zhang et al. 2025`, `Deng, Brucks & Toubia 2025`, `Nguyen et al. ICLR 2025`, `Yuan et al. EMNLP 2025`, `Hu et al. EMNLP 2025 Findings`) clearly marked under the Three-Class Provenance Boundary.

### Milestone 4: Measurement-Only `H6` Runner Support (`GREEN`)
- **File:** `tools/stress_runner.py`
- **Action:** Add repeatable `--codex-config key=value` CLI argument forwarded via `-c key=value` on initial and resume `codex exec` invocations (default empty = unchanged behavior). Zero provider tokens or CLI details enter `skills/systematic-innovation/`.
- **Verification (`GREEN`):**
  - `python3 -m unittest discover tests -v` -> all pass cleanly.
  - `python3 tools/validate_skill.py skills/systematic-innovation` -> `OK`.
  - `python3 -m tools.repository.authority` -> exit `0`.
  - Run `../SkillEvaluator` `quality-check` and `tier1 --no-llm` on `skills/systematic-innovation` -> verify score reaches **Grade A (`>= 92/100`)** with zero security/critical/medium schema issues (aside from unavoidable keyless Tier 2–3 advisories). If any deterministic deduction remains, refine `SKILL.md` cleanly and re-verify before live LLM runs.

### Milestone 5: Bounded Paired Evaluation & Convergence Loop *(only with owner budget sign-off)*
- **Output Directory:** `evals/v2-loop/` (separate from historical `evals/stress/results/` and `evals/restored-2026-10-18/`).
- **Bounded Paired Evaluation Protocol (respecting `--max-calls` and `--max-cost`):**
  - Subset of diagnostic stress cases testing each hypothesis:
    - `token-ceiling-portfolio` (`<= 350` words) & `holdout-budget` (`<= 400` words) $\rightarrow$ validates `H5` strict word-limit compliance & nonzero parsed candidates.
    - `startup-homogenization` & `startup-default-audit` $\rightarrow$ validates `H1` trope quarantine & higher `distinct_mechanism_clusters` / `VS_1.0` vs `control_creative` / `control_format`.
    - `triz-thermal-contradiction` or `cross-domain-recombination` + `macgyver-overconstrained` $\rightarrow$ validates `H2`/`H3` Currie invariant preservation & impossibility re-anchoring.
    - Optional bounded `H6` check on 1 case (`--codex-config model_reasoning_effort=low` vs `high` if supported by host model) paired across identical prompts.
  - Score every condition separately via `python3 -m tools.score_eval_results` (`--output-path` per condition, no pooled comparisons) and record a concise, honest metrics table + failure analysis in `evals/v2-loop/report.md`.
  - If any regression appears (word overrun, preservation violation, cluster drop, or Discovery stall), iterate back through TDD fix -> `validate_skill.py` -> `SkillEvaluator` -> focused retest until clean.
