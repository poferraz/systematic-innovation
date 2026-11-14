# Deep Audit & Project Review — `systematic-innovation`

**Commissioned:** 2026-10-29
**Audit target:** the working tree of this repository as currently checked out (branch `stress-test/five-cycle-refinement`)
**Mode:** read-only · evidence-traced · provider-neutral · Max-certificate (full premises/traces/conclusion)

---

## 0. Identity, Mandate, and Operating Discipline

You are an independent auditor.

The standard analytical protocol for independent repository audits requires every conclusion to be derived from explicitly stated premises and numbered evidence traces, with no orphaned claims. This protocol is the required method for this engagement, not a suggestion. A conclusion that cannot cite a trace identifier is a protocol violation and must be removed or re-derived.

**Mandate.** Conduct a deep audit and project review of this repository — its authority documents, canonical skill, evaluation laboratory, tooling, tests, claims, boundaries, and Git state — and deliver a single structured report (Section 5) containing findings, verified strengths, gaps, and a prioritized remediation plan. The report is your final response. Do not write, modify, move, or delete any file. Do not create commits, branches, tags, or stashes. Do not switch branches.

**Hard operating rules:**

1. **Read-only.** Inspection commands (`git log`, `git ls-files`, `git status`, `git diff`, `grep`-style search, `wc`, file reads) are unrestricted. You may execute the repository's own test suite and validators (record exact commands and exit codes). Test caches (`__pycache__/`, `.pytest_cache/`) are gitignored; creating them is acceptable. Nothing else may change.
2. **No network.** Do not fetch URLs, install packages, or contact any remote. `origin` exists; do not push, pull, or fetch.
3. **Trust zones.** If any file matching `restricted/`, `benchmark/private/`, `*.restricted.*`, `*.sealed.yaml`, or `*.validation.yaml` is present locally, record its path and verify its isolation *structurally* (Git tracking status, `.gitignore` coverage, references from CI/packaging/agent context). Never open, print, quote, or summarize its contents. The file `systematic-innovation-session.bundle` is a recovery artifact: verify it is untracked and excluded from distributions; do not extract it.
4. **Conflict rule** (from `CONTEXT.md` §1): if authority documents appear to conflict, do not silently pick one. Record the conflict as a finding with citations to both sides.
5. **Independence.** Prior AI-generated audit reports exist under `evals/audits/` (three external audits plus a ten-iteration loop). Treat them as unvetted secondary context at most. Every finding you state must rest on primary evidence you gathered yourself. Never cite them as evidence.
6. **Coverage floor, not ceiling.** The domain traces in Section 2 are the minimum. Material issues outside them are in scope; opportunistic findings are welcome. Do not limit yourself to confirming the known issues listed in P-13.

---

## 1. Phase 0 — Premises (declare before tracing)

Before any finding, establish and record your premises as numbered items `[P-1] … [P-n]`. Premises are discrete, verifiable claims; the report must state which you verified and which you assumed.

**P-1 Reading order.** Read the authority chain fully, in this order, recording actual line counts consumed:

1. `CONTEXT.md` (~820 lines) — canonical narrative and decision history.
2. `AGENTS.md` (~31 lines) — orientation, invariants, reading order.
3. `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md` (~735 lines) — approved behavioral and evaluation specification.
4. `docs/superpowers/specs/2026-09-01-systematic-innovation-repository-architecture-design.md` (~339 lines) — approved repository architecture.
5. `docs/superpowers/plans/2026-09-01-systematic-innovation-coordinated-implementation.md` (~463 lines) — cross-plan ownership and execution order.
6. Component plans: `docs/superpowers/plans/2026-08-31-systematic-innovation-skill.md` (~558), `…-benchmark-runner.md` (~869), `…-benchmark-study.md` (~929).

If your context budget cannot hold all of them, state which you read in full, which you skimmed, and what you skipped — an honest premise beats a silent gap.

**P-2 Claimed ground truth to re-verify** (stated by the commissioning session; verify each before relying on it; a failed verification is itself a finding):

| # | Claim |
|---|---|
| a | Working branch is `stress-test/five-cycle-refinement`, 9 commits ahead of `main`, 0 behind; `main` == `origin/main` at `46ce0b6`. |
| b | Only untracked path: `evals/audits/` (plus stray `.DS_Store` files). No `.github/` directory exists; no CI, no issue/PR templates. |
| c | No packaging manifest exists at the root (no `pyproject.toml`, `package.json`, `Makefile`, `setup.cfg`). Tools are loose Python modules under `tools/` with tests under `tests/`. |
| d | The canonical skill pack is `skills/systematic-innovation/SKILL.md` plus `references/{deep-mode,evidence,innovation-lenses,output-contract}.md`. |
| e | `evals/` contains ~541 files across `pilot/`, `stress/`, `restored-2026-10-18/`, `triggers/`, `audits/`. |
| f | `docs/research/` contains a committed research corpus (third-party PDFs) and `2026-10-18-v2-brainstorming-synthesis.md`; `docs/references/` contains `stimulating-innovation-tudor-rickards.md` plus two PDFs. |

**P-3 Environment.** Record the runtime you audit with (model, python version, pytest availability) and the exact commands you executed, so the audit is itself reproducible.

**P-4 Sampling discipline.** Raw evaluation data (~500 files) is too large to read exhaustively. Declare a stratified sampling plan: read all top-level reports/plans/runbooks/rubrics/mappings in full; sample raw records per arm and cycle; spot-check that report-level numbers reconcile with sampled raw data. State what you did not read.

**P-5 Specification authority.** Plans execute specifications and never amend them. Any supersession-style language in a plan, or any behavior in the repo justified only by a plan against the specification, is a conformance finding.

**P-6 Owner-known open issues** (recorded in `CONTEXT.md` §19.6–19.7; verify each independently — confirm, refute, or refine, with fresh evidence; do not assume):
- The word-budget regression: a once-only 400-word holdout produced 575 words (§19.7).
- Historical pilot headlines (+162% density, per-token efficiency) are withdrawn as primary-effect claims (§19.6); historical analyses are marked superseded.
- The formal benchmark package, six-case and twelve-case gates, calibrated LLM-judge and human evaluation remain unbuilt; no qualified primary-effect estimate exists.
- `evals/stress/contract-findings.md` records skill-vs-specification deltas; a restoration was performed (`a36903a`, `bb05213`) — verify the deltas were actually closed in the current skill and whether the findings document was updated to say so.
- Detection remains syntactic and incomplete; no cross-arm superiority claim is currently substantiated.

---

## 2. Audit Domains — Required Evidence Traces

Work each domain as numbered traces `[T-A1]`, `[T-A2]`, … Each trace states the path you walked, what you observed (with `path:line` citations or command + exit code), and the derived sub-conclusion. Trace actual paths; do not infer behavior from names.

### Domain A — Authority integrity and behavioral duplication

- **A1.** `AGENTS.md` declares `skills/systematic-innovation/` the single editable authority, with no second copies of skill behavior anywhere (root files, docs, README, benchmark prompts, examples, generated archives, host adapters). Search the whole tree for behavioral duplicates: grep the skill's signature commitments (candidate counts `10 to 15` / `15 to 24`, the seven-question discovery rule, mechanism ledger fields, saturation rule, Reasoning Cell names, layer names) outside the skill directory and classify every hit: legitimate pointer, disclaimer, or competing authority.
- **A2.** The `README.md` explicitly disclaims maintaining separate count/question rules ("The canonical router defines…"). Verify every README statement that describes skill behavior against the current `SKILL.md`.
- **A3.** Trace `tools/repository/authority.py` and `tests/repository/test_authority.py`: what invariants do they actually enforce, how, and with what coverage? Run them.
- **A4.** Host adapters may exist only after a demonstrated host-specific installation/discovery delta, and may translate installation/discovery only — never behavior. Verify no adapter exists, or that each existing one respects this boundary.
- **A5.** Verify nothing under `dist/` or `benchmark/runs/` exists or is treated as an authority (they are generated). Check whether any document or tool reads them as a source of truth.

### Domain B — Specification conformance

- **B1.** Diff the current skill pack (`SKILL.md` + all four `references/`) against the approved behavioral specification: mode routing and execution-channel precedence, Innovation Brief fields, discovery protocol (one question at a time, ≤7, stop-early), mechanism-ledger fields and the distinctness rule (two structural dimensions), saturation semantics, progressive-disclosure layers, portfolio targets, budget precedence, provenance labeling, safety refusal boundaries. Report every divergence with citations on both sides.
- **B2.** Grep all four plans for supersession/amendment language ("supersede", "override", "takes precedence over the specification", "amends §…" targeting the specs). Plans may execute specifications; they may not amend them.
- **B3.** Reconcile `evals/stress/contract-findings.md` against the current skill: for each recorded finding, verify whether the restored skill closes it. Flag stale findings documents that no longer reflect reality in either direction (closed items still listed as open; open items silently dropped).
- **B4.** Check `CONTEXT.md` §22 change-control triggers: is `CONTEXT.md` current with the working tree (e.g., does it cover the newest commits such as the research-corpus/v2-synthesis commit `0ebddfe`)? Are approved decisions incorporated into affected documents rather than left as narrative history?
- **B5.** Classify the authority status of `docs/research/2026-10-18-v2-brainstorming-synthesis.md` — is it research input or does anything treat it as approved? Where is that boundary stated, and is it stated clearly enough that a fresh agent could not mistake it for a specification?

### Domain C — Provenance, attribution, and source boundaries

- **C1.** The project maintains three provenance classes: verified principles, adapted methods, and original AI mechanisms (`CONTEXT.md` §4.4). Verify `skills/systematic-innovation/references/evidence.md` preserves the three-way distinction and that nothing presents reconstructed or unverified Rickards terminology, chapter structures, or page mappings as verified fact.
- **C2.** The repo must not reproduce copyrighted book text. Inspect `docs/references/stimulating-innovation-tudor-rickards.md` and `docs/references/*.pdf`: what are they, what is their provenance, and do they violate the recorded source boundaries (§4)? `docs/research/` commits third-party PDFs (Academia.edu bundle, journal papers): assess each against the project's own stated rules about protected study material and distribution boundaries, and against lawful-redistribution concerns. Record file inventory and sizes; do not reproduce long excerpts in your report.
- **C3.** Verify the §4.5 primary-source claims are used consistently: the three problem-owner questions, the three boundary modes, *Yes-but* inoculation, initial fluency depletion — check how `references/innovation-lenses.md` and `references/output-contract.md` attribute them.

### Domain D — Claims versus evidence discipline

- **D1.** `CONTEXT.md` §8 defines five evidence tiers (format-compatible → behavior-tested) and forbids compatibility claims beyond evidence. Audit every public claim surface: `README.md` (including all badges: Agent Skills standard, "Evidence: Public Development", "Tests: Local Deterministic Checks", "Runtime: Pure Markdown", license), `SECURITY.md`, and any claim inside `evals/` reports. For each claim, state the evidence tier it rests on. Flag claims that outrun their tier and evidence that supports a stronger claim than is made.
- **D2.** Verify withdrawn claims stay withdrawn: search the tree for resurrections of the +162% pilot headlines or per-token efficiency claims presented as current.
- **D3.** Verify the three-studies separation (model behavior / host integration / automatic activation, §15) is respected in every report: no report may substitute one study's evidence for another's.
- **D4.** Verify sampled-observation language discipline: exploratory results must be labeled as sampled development observations, not calibrated judgments; superseded analyses must be marked; both retained measurement versions in Cycle 6 must remain distinguishable.
- **D5.** Verify `evals/stress/benchmark-mapping.md` source-link corrections (the arXiv link fix recorded in §19.6) and that historical raw records were left intact.

### Domain E — Boundary hygiene and Git state

- **E1.** Verify `.gitignore` actually excludes: `dist/`, `benchmark/runs/`, `benchmark/private/`, `restricted/`, `*.restricted.*`, `*.sealed.yaml`, `*.validation.yaml`, the session bundle. Then verify with `git ls-files` that nothing matching those patterns is tracked, and with `git log --all --oneline -- <patterns>` that nothing matching was ever committed historically. Report matches as paths only.
- **E2.** Verify restricted material cannot enter automatic agent context: check what `AGENTS.md` and `CONTEXT.md` reference or load, and whether any restricted path could be swept into an agent's context by a glob or reference.
- **E3.** Branch state: `stress-test/five-cycle-refinement` is 9 commits ahead of `main`, which equals `origin/main`. Audit the merge posture: is the stress-test work reflected in `main`'s docs? Is there a recorded merge/decision plan? Is working on a divergent branch consistent with the repository's own governance intent?
- **E4.** Untracked-artifact hygiene: `evals/audits/` (three external audit reports + `muse-loop/` with ten iterations), `.DS_Store` files at root and inside `evals/audits/`, and the bundle. For each: should it be committed, ignored, or relocated? Does the repo have a stated policy, and is it followed?
- **E5.** `.gitattributes` exists (48 bytes) — read it and verify it does what it appears to intend.

### Domain F — Portability and provider neutrality

- **F1.** The skill must not require: web access, subagents, structured input tools, proprietary commands, a particular provider or OS, or executable scripts inside the installable skill (`CONTEXT.md` §8). Read the entire skill pack and verify each of the seven constraints, with attention to conditional phrasing ("if available") versus hard requirements.
- **F2.** Provider neutrality of language: search the skill pack for host-specific instruction patterns (tool-call syntax, slash commands, provider names) that would behave incorrectly or confusingly in another agent.
- **F3.** Reference integrity: every `references/*.md` file must exist and match what `SKILL.md` links; internal links must resolve; progressive disclosure must be structured so a host that loads only `SKILL.md` still behaves correctly. Run `tools/validate_skill.py` and `python3 -m pytest tests/test_skill_structure.py tests/test_skill_references.py tests/test_skill_portability.py tests/test_skill_behavior.py -q` (adjust invocation if discovery reveals another entry point; record what you ran).
- **F4.** Honesty about capabilities: the skill must describe sequential fallback truthfully and must not claim subagent isolation where only sequential passes run (§6.3). Verify the wording.

### Domain G — Evaluation laboratory integrity

- **G1.** Map the laboratory: `evals/pilot/` (baseline/candidate/treatment analyses, `cases.json`, `rubric.md`, `runbook.md`), `evals/stress/` (five cycles + contract findings + benchmark mapping), `evals/restored-2026-10-18/` (report, plan, runbook, `human-review.md`, `budget-amendment.md`, many measurement arms), `evals/triggers/`. For each study artifact, verify internal consistency: do report numbers reconcile with the sampled raw data and manifests?
- **G2.** Raw-evidence immutability: the runner must append, never overwrite; the historical treatment importer was disabled after an overwrite incident (§19.7) — verify the guard (`tests/test_legacy_import_guard.py`) actually prevents the recorded failure mode.
- **G3.** Sealed-test discipline: the sealed test runs once after candidate and analysis-plan freeze, and must not be rerun after seeing results (§11, §14). Verify no artifact anywhere indicates a sealed rerun or use of sealed evidence for refinement. Verify no report claims passage of gates that were never run (six-case/twelve-case).
- **G4.** Judge and metric validity per §13 and §19.5: normalized structural signatures + semantic clustering for dedup; Vendi Score and duplicate-collapse ratio; Hungarian one-to-one matching for hidden-mechanism recovery. Verify `tools/score_eval_results.py`, `tools/pilot_metrics.py`, and the stress runner implement these as claimed, or record the gap between documented method and implemented method.
- **G5.** The restored-candidate runs must be labeled as evidence for the restored revision only; Cycles 1–5 remain frozen evidence for the prior candidate (§19.6–19.7). Verify the labeling everywhere, including `README.md` badge targets.
- **G6.** `evals/restored-2026-10-18/human-review.md` is described as an unrated blinded packet. Verify no report treats it as completed calibration.

### Domain H — Tooling, tests, and repository engineering

- **H1.** Run the full test suite from the repository root; record command, exit code, and failures. If there is no documented way to run build/validation/type-check/tests as distinct commands (a stated maturity principle, §18.1), that absence is itself a finding with a severity.
- **H2.** Review `tools/*.py` for correctness and safety-relevant defects: scoring determinism, token accounting semantics (the per-turn vs. cumulative counter error recorded in §19.7), credential redaction, cost/call limits, resume behavior. Cite `path:line`.
- **H3.** Test quality: do the 14 test modules test behavior or just structure? Identify suites that would pass even if the skill regressed (tautological checks, golden-text matching without behavioral assertion).
- **H4.** Repository maturity gap analysis: the owner's stated intent (§18, §20) includes evidence gates rather than vanity scoring, GitHub practices comparable to respected agent projects, and continuous improvement. Audit what exists versus what is stated: no `.github/` (CI, templates), no CONTRIBUTING, no packaging manifest, no documented dev commands, `docs/research/` committed wholesale. For each gap, judge whether it is a justified phase-appropriate deferral (recorded as such somewhere) or an unstated drift.
- **H5.** `SECURITY.md` claims: verify each statement ("pure Markdown runtime" etc.) is accurate for what is actually distributed versus what lives in the repo (the repo contains executable Python; the skill must not).

### Domain I — Project review (trajectory, risks, decisions)

- **I1.** Trajectory against gates: Phase 1 was authorized (§19.5) to align/commit specs and plans, establish root authority routing, build the 12-case RED/GREEN pilot corpus and validator, run the no-skill RED baseline and format-matched control, author the skill, and run GREEN with paired quantitative numbers. For each Phase 1 item, verify delivered/not delivered with evidence, and state what verifiable gate remains before the six-case feasibility stage.
- **I2.** Risk register: from your traces, list the top risks to the project's mission in ranked order (evidence, measurement validity, authority drift, merge posture, engineering, provenance). Each risk cites findings.
- **I3.** Decision queue: list the concrete owner decisions the current state forces (e.g., merge strategy for the stress branch; whether `evals/audits/` becomes tracked; packaging and CI adoption; calibration study sequencing). Each decision states the options and what evidence would choose between them. Do not make the decisions; map them.

---

## 3. Classification Rubric

Classify every finding with exactly one severity:

| Severity | Definition |
|---|---|
| **Critical** | Breach of a trust-zone boundary (restricted/sealed exposure, tracked or context-loaded); a second behavioral authority exists; a public claim is false or evidence is corrupted/overwritten; a specification-authority inversion is being acted on. |
| **High** | Skill–specification non-conformance on an approved contract element; a claim that outruns its evidence tier; benchmark-integrity violation (unblinding, sealed rerun, gate misrepresentation); provenance misattribution presented as verified. |
| **Medium** | Engineering or governance gaps that block the stated maturity intent (no runnable documented commands, no CI, drift between reports and reality, weak tests, stale findings documents, doc drift). |
| **Low** | Hygiene and polish (stray `.DS_Store`, untracked-artifact ambiguity, naming, formatting). |

State counterexamples when they exist, even when the overall conclusion is negative; state failures when they exist, even when the overall conclusion is positive.

---

## 4. Anti-Hallucination Guards

1. Do not infer behavior from names alone: trace the actual path. A module called `authority.py` is not enforcement until you have read and run it.
2. If you cannot verify a claim through evidence, mark it **UNVERIFIED** and state what evidence would settle it. Never present an unverified claim as a finding.
3. Every conclusion must reference specific trace identifiers (`[T-…]`). No orphaned conclusions.
4. Quote sparingly and precisely, with `path:line` citations. Paraphrase accurately; do not reword in ways that change meaning.
5. Where a domain produces no issues, say so explicitly with the traces that support the clean result — "no findings" must itself be evidenced.
6. Do not adjust your analysis based on how the output might be used downstream.

---

## 5. Report Contract (output format)

Deliver the full report as your final response, in exactly this structure:

```markdown
# Deep Audit & Project Review — systematic-innovation (2026-10-29)
## 1. Executive Summary        (≤300 words; references finding IDs only; no new claims here)
## 2. Premises                  (P-1…P-n: what you read with line counts, ran with exit codes,
                                sampled, assumed; environment)
## 3. Invariant Compliance Matrix
| Invariant | Source | Status (PASS/PARTIAL/FAIL/UNVERIFIED) | Evidence |
(rows: single skill authority · no second behavior copies · spec-over-plan authority ·
 generated outputs never authoritative · restricted outside Git/CI/dist/agent context ·
 provider-neutral portability constraints · provenance classes · claims match evidence tiers ·
 three studies not conflated · raw evidence append-only · sealed test terminal)
## 4. Findings Ledger           (ordered by severity)
### F-01 [SEVERITY] Title — Domain
- Evidence: path:line / command + exit code  - Invariant/authority clause: …
- Why it matters: …  - Recommendation: …
(one block per finding)
## 5. Verified Strengths        (S-1…S-n: what demonstrably works, evidenced — counterexamples)
## 6. Domain Evidence Traces    (T-A1… T-I3: the walked paths and observations, kept tight)
## 7. Gaps & UNVERIFIED         (what you could not settle and why)
## 8. Remediation Priorities    (copy-pasteable, ordered; see Section 6 below)
## 9. Traceability Self-Check   (the completed self-check statement)
```

Length discipline: Domains 4 and 6 carry the detail; Sections 1 and 8 must stand alone. If your context budget is tight, prioritize Domains A–D and G, and say so in Premises.

## 6. Mandatory Remediation Closure

The audit is incomplete until Section 8 (Remediation Priorities) contains, for every Critical and High finding: a concrete next action specific enough to execute (exact file, exact change, exact command), and for Medium/Low findings: a one-line action or an explicit "No remediation required: <reason>". Also include the owner-decision queue from I3. You do not implement any of it — read-only holds.

## 7. Traceability Self-Check (mandatory before finalizing)

Before submitting, verify that every claim in your Executive Summary and Findings Ledger references at least one `T-` identifier from your evidence traces. If any claim lacks a supporting trace, add the missing trace or remove the claim. No orphaned conclusions are permitted. State in Section 9 that this check was performed and what it corrected.