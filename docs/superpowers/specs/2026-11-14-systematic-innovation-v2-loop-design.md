# Systematic Innovation — Security, SkillEvaluator, Probabilistic Creativity & Visual Overhaul Loop Design

**Date:** 2026-11-14  
**Status:** Draft — awaiting owner review  
**Project:** `systematic-innovation`  
**Branch Context:** `stress-test/five-cycle-refinement` (ahead of `main` / `origin/main` at `46ce0b6`)

## 1. Purpose & Authority Alignment

This specification defines the five-phase improvement loop to resume, harden, evaluate, evolve, and visually polish `systematic-innovation` while honoring all existing project invariants:

1. **Non-Supersession:** This document defines the execution-loop architecture and phase gates for the v1-remediation-to-v2-evolution program. It does **not** silently amend or supersede [`2026-08-31-systematic-innovation-design.md`](2026-08-31-systematic-innovation-design.md) or [`2026-09-01-systematic-innovation-repository-architecture-design.md`](2026-09-01-systematic-innovation-repository-architecture-design.md). Any change to the skill's behavioral contract introduced in Phase A (`D3`) or Phase C requires an explicit, owner-approved behavioral-specification amendment recorded in `CONTEXT.md`.
2. **Single Behavioral Authority:** `skills/systematic-innovation/` remains the sole editable authority for public skill behavior (`AGENTS.md`).
3. **Book Provenance Fidelity:** All methodological evolution in Phase C remains grounded in Tudor Rickards (1985), *Stimulating Innovation: A Systems Approach* (Frances Pinter, London, `pp. xi + 221`, ISBN `0-86187-512-5`), preserving the three-class provenance boundary in `CONTEXT.md` §4.4–4.5 (verified principles, adapted methods, original AI mechanisms) and reproducing zero copyrighted source text.
4. **Trust-Zone & History Hygiene:** Copyrighted material, untriaged third-party PDFs, and restricted evaluation packs never enter public Git history, ordinary CI, generated archives, or automatic agent context.

---

## 2. Five-Phase Loop Architecture

The program runs as a gated sequence of five phases (`Phase A` → `Phase B` → `Phase C` → `Phase D` → `Phase E`), where `Phase C` executes a bounded hypothesis-to-measurement loop until gains stabilize.

```text
[Phase A: Security, Provenance & Audit Baseline]
        │  (clean 0ebddfe, runner guards, SECURITY.md, spec conformance)
        ▼
[Phase B: External Gap Baseline via NVIDIA/SkillEvaluator]
        │  (Tier 1 quality-check + SkillSpector security; optional Tier 2/3)
        ▼
[Phase C: Deep Research & Probabilistic Creativity Loop] ◄───┐
        │  (Rickards 1985 × Probabilistic LLM Science → Spec   │ iterate until
        │   → RED tests → Skill edit → Internal + External     │ gains hold &
        │   Evals: Vendi/mechanisms/budget + SkillEvaluator) ──┘ no regressions
        ▼
[Phase D: README, SVG & PNG Visual Overhaul]
        │  (claim-accurate storytelling, crisp SVGs, verified PNGs)
        ▼
[Phase E: Final Audit, Verification & Clean Merge to main]
```

---

## 3. Phase Specifications

### 3.1 Phase A — Security, Provenance & Hygiene Baseline

Phase A resolves all 32 findings from [`evals/audits/2026-10-29-deep-audit-report.md`](../../evals/audits/2026-10-29-deep-audit-report.md) using [`docs/superpowers/plans/2026-10-29-systematic-innovation-audit-remediation.md`](../plans/2026-10-29-systematic-innovation-audit-remediation.md) with the owner-approved defaults (`D1`–`D9`), subject to one branch-timing modification: **hold the fast-forward merge to `main` until Phases C–E complete**.

Key Phase A deliverables and invariants:
- **Unpushed History & Corpus Remediation (`F-01`, `F-04`, `D1`):** Because `0ebddfe` sits on no remote branch, reset `HEAD~1` after creating a local safety ref; relocate `docs/references/stimulating-innovation-tudor-rickards.md` and the 49 PDFs into a gitignored local `sources/` directory (retained locally for Phase C research); deduplicate identical PDFs in `sources/`; add `docs/research/README.md`; keep `docs/research/2026-10-18-v2-brainstorming-synthesis.md` tracked and relabeled as unexecuted research input (`F-07`, `D2`).
- **Immediate Claim-Surface Correction (`F-02`, `F-03`):** Strip withdrawn `+162%` / `8.2x` claims and pre-restoration workflow text from `tools/build_branding.py`, add a deterministic regression test preventing withdrawn strings from re-entering branding sources or `README.md`, regenerate claim-clean baseline PNGs, and fix stale `README.md` badges/links (pointing to `evals/restored-2026-10-18/report.md` and reflecting resolved contract restoration). Full visual/SVG redesign waits for Phase D.
- **Security & Runner Hardening (`F-12`, `F-14`, `F-15`, `F-16`, `F-28`, `D4`, `D8`):**
  - Update `SECURITY.md` with the three trust zones (public skill, public benchmark tooling, restricted evaluation pack) and GitHub Private Security Advisories (replacing the `.local` email).
  - Add `--max-cost`, an explicit model allowlist, failure thresholds/bounded retries, and credential redaction of raw CLI outputs to `tools/stress_runner.py`, plus fix hardcoded absolute paths and unconditional file overwrites in evaluation scripts.
  - Upgrade `tools/repository/authority.py` with content-signature sweeps and a CLI; remove the undocumented `evidence.md` exemption and broaden provider scanning in `tools/validate_skill.py`.
  - Add `pyproject.toml` and a least-privilege stdlib GitHub Actions CI workflow (`.github/workflows/ci.yml`).
- **Behavioral Spec & Skill Conformance (`F-06`, `F-09`, `F-10`, `F-21`–`F-23`, `D3`):** Complete missing existing-spec clauses in `skills/systematic-innovation/` (`research-when-available`, `preservation-first/no-change`, `high-stakes verification labeling`, `Quick-mode single critical question`, `morphological recombination` & `subtraction` cues) test-first; draft and submit for owner sign-off the behavioral-spec amendment grounding `SKILL.md` lines 29–40 (`Execution-Channel Precedence` and `Hard Output Budget Precedence`).
- **Decision & Audit Records (`F-05`, `F-08`, `F-18`, `F-19`, `F-27`, `D5`–`D9`):** Commit `evals/audits/` as historical evidence; record pilot errata and lexical-clustering boundaries; record all decisions in `CONTEXT.md` §19.8.

**Phase A Exit Gate:** `0ebddfe` replaced cleanly (history grep for book text and restricted patterns returns zero matches), all unit tests + `validate_skill.py` + `authority.py` pass, `stress_runner.py` spend/redaction guards pass tests, and nothing has been pushed yet.

---

### 3.2 Phase B — External Evaluation Baseline (`NVIDIA/SkillEvaluator`)

Phase B measures the cleaned canonical skill pack against `https://github.com/NVIDIA/SkillEvaluator` without polluting the repository tree:

1. **Workspace Isolation:** Clone and run `NVIDIA/SkillEvaluator` in a sibling directory outside this repository (`../SkillEvaluator`) using `uv`, never inside `skills/` or tracked project paths.
2. **Tier 1 Keyless Baseline:** Execute `skillevaluator quality-check` and `skillevaluator tier1 --no-llm` (which runs deterministic Agent Skills compliance, secret/PII checks, and **SkillSpector** security/prompt-injection scanning) against `skills/systematic-innovation/`.
3. **Evidence Capture:** Save the clean JSON and CLI summary reports under `evals/audits/` (with any local paths normalized/redacted) as the **Pre-v2 External Baseline**.
4. **Tier 1 LLM / Tier 2 / Tier 3 Triage:** Present the Tier 1 keyless gap findings to the owner and confirm whether to also run Tier 1 LLM rubric checks, Tier 2 overlap checks, or Tier 3 live sandboxed Skill Lift before or during Phase C (depending on available API/local-model/Docker setup).

**Phase B Exit Gate:** Baseline `SkillEvaluator` Tier 1 keyless report captured, reviewed, and triaged into actionable findings (security, instruction clarity, metadata/discovery, or structure).

---

### 3.3 Phase C — Deep Research & Probabilistic Creativity Loop

Phase C investigates how to make LLMs measurably more innovative and less mode-collapsed while staying strictly true to Tudor Rickards's (1985) systemic approach and pure-Markdown portability.

#### Research Track 1: Rickards (1985) Primary Anchor
Verify and map exact book mechanics (using the local `sources/` files only as offline research input—never copying text into repository outputs):
- Coupled **search and selection** inside an organizational selection environment.
- **Initial fluency depletion** (moving past top-of-mind memory dumps before collecting candidates).
- **Structural operators**: multiple redefinition (analytic, empathic, motivational, metaphorical, boundary-relaxed), synectic excursions, morphological synthesis, assumption reversal.
- **Boundary-overflow modes** (mission-orientated, negotiative win-win goal emergence, participative discovery), **three problem-owner questions**, and ***Yes-but* hearing inoculation**.

#### Research Track 2: Probabilistic LLM Creativity Mechanisms
Investigate 2024–2026 empirical and mechanistic literature on LLM creativity, entropy, and sampling behavior—explicitly separating:
1. **Pure-Markdown Distributional Operators (Portable Core):** Inference-time prompting structures that reshape the model's conditional token distribution without API parameter control—for example:
   - *Verbalized distribution / tail-sampling techniques* (prompting explicit coverage across low-probability, high-plausibility regions rather than argmax/mode responses);
   - *Negative-space conditioning* (quarantining default tropes *in-context* so subsequent token generation avoids high-prior semantic basins);
   - *Orthogonal structural forcing* (conditioning each Reasoning Cell on distinct structural coordinates so pass $k+1$ does not collapse onto pass $k$);
   - *Delayed convergence & preservation-first gating* (preventing premature collapse onto a single "best" implementation plan);
   - *Concise, non-bloating enforcement* that also solves the open **400/500-word output-budget regression** recorded in `CONTEXT.md` §19.7.
2. **Runner & Decoding Interactions (Evaluation Lab):** Controlled sweeps in `tools/stress_runner.py` measuring how decoding parameters (e.g., `temperature`, `top_p`, model family, multi-turn vs single-turn, isolated passes vs sequential passes) interact with the pure-Markdown skill.
3. **Prior v2 Synthesis Evaluation:** Critically evaluate the unexecuted hypotheses in `docs/research/2026-10-18-v2-brainstorming-synthesis.md` (TIS failure archetypes, externalized burden, functional invariant vs structural vehicle) alongside the new probabilistic findings—keeping only mechanisms that justify their token cost and pass Rickards provenance alignment.

#### Bounded Iteration Protocol
Each R&D cycle follows strict RED → GREEN → REFACTOR discipline:
1. Write a research memo summarizing verified evidence and candidate hypotheses (`docs/research/`).
2. Propose and get owner approval for a formal **v2 Behavioral Spec Amendment** before changing the skill's core contract.
3. Add failing behavioral/budget/invariant assertions (`tests/`) and targeted eval cases first.
4. Implement the pure-Markdown refinement in `skills/systematic-innovation/`.
5. Run paired evaluations across arms (vanilla, generic brainstorm, format-matched control, prior restored candidate, v2 candidate) measuring:
   - Causal mechanism diversity: **Vendi Score ($\text{VS}_k$)** and distinct mechanism families (with semantic/structural equivalence, explicitly noting measurement limits);
   - Compliance & safety: **word-budget adherence**, preservation invariants, high-stakes safety, no fabricated stats, no premature winner/roadmap drift;
   - External check: re-run **`NVIDIA/SkillEvaluator`** to confirm no regressions in static quality, security, or token efficiency.
6. Stop iterating when hypotheses stabilize with verified gains and zero safety/budget/portability regressions (and stop immediately if `stress_runner.py` budget/failure caps trigger).

**Phase C Exit Gate:** Approved v2 behavioral spec (if amended), green test suite, retained paired comparison evidence (with honest limits, no uncalibrated quality claims presented as calibrated human validation), and clean `SkillEvaluator` pass on the v2 skill candidate.

---

### 3.4 Phase D — README, SVG & PNG Visual Overhaul

Once the skill workflow and verified evidence stabilize:
1. **README Architecture (`README.md`):** Rewrite for clarity, scannability, honest evidence framing, accurate Quick/Deep/Provocation examples, verified installation paths, and zero shadow behavioral specs (`AGENTS.md` / `authority.py` clean).
2. **Vector SVGs (`assets/*.svg`):** Author crisp, theme-resilient SVGs for structural diagrams (e.g., the coupled search/selection loop, Reasoning Cells / distributional expansion flow, or trust-zone architecture) that stay sharp at all screen densities.
3. **Raster PNGs (`assets/*.png` via `tools/build_branding.py`):** Update the Playwright-backed generator to reflect the final v2 architecture, authentic Tudor Rickards (1985) visual identity (`#025d9c` buckram blue and `#f5d818` signal yellow), and strictly claim-verified metrics.
4. **Visual Verification:** Inspect every generated SVG and PNG directly via image-capable inspection (and browser preview if helpful) to confirm typography, contrast, clipping, alignment, and accuracy before committing.

**Phase D Exit Gate:** All `README.md` links, SVGs, PNGs, and `build_branding.py` pass branding-claim regression tests, `authority.py`, and direct visual inspection.

---

### 3.5 Phase E — Final Verification, Security Gate & Merge

1. Run the full verification battery:
   - `python3 -m unittest discover tests -v`
   - `python3 tools/validate_skill.py skills/systematic-innovation`
   - `python3 -m tools.repository.authority`
   - `git log --all` history sweeps verifying zero copyrighted book text, zero untriaged PDFs, zero credentials, and zero restricted-pack paths.
2. Re-run `NVIDIA/SkillEvaluator` (Tier 1 + any configured Tier 2/3 checks) on the final candidate and archive the final summary report in `evals/audits/`.
3. Update `CONTEXT.md` §19 with the complete Phase A–E record, final compatibility/evidence scope, and next steps (such as human calibration and the formal 6/12-case benchmark package).
4. Merge cleanly to `main` (fast-forward or clean PR merge) and verify `main` matches all gates before pushing.

---

## 4. Explicit Out-of-Scope Boundaries

- This loop does **not** touch or weaken restricted/sealed evaluation boundaries (`restricted/`, `*.restricted.*`, `*.validation.yaml`, `*.sealed.yaml`).
- This loop does **not** treat uncalibrated automated runs as calibrated human judgment or claim global novelty/realized commercial innovation.
- This loop does **not** embed Python scripts, credentials, or provider-specific commands inside `skills/systematic-innovation/`.
